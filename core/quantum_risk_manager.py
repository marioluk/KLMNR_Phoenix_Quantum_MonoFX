# quantum_risk_manager.py
"""
Modulo QuantumRiskManager: gestisce la logica di risk management per il sistema di trading.
"""
import logging



class QuantumRiskManager:
    def __init__(self, config_manager, engine, parent=None):
        self._config_manager = config_manager
        self.engine = engine
        self.parent = parent
        # ... eventuali altre inizializzazioni ...

    @property
    def symbols(self):
        # Accesso ai simboli tramite _config_manager o direttamente da _config
        if self._config_manager is not None:
            return list(self._config_manager.config.get('symbols', {}).keys())
        elif self._config is not None:
            # _config può essere un dict o avere l'attributo config
            if hasattr(self._config, 'config'):
                return list(self._config.config.get('symbols', {}).keys())
            return list(self._config.get('symbols', {}).keys())
        return []

    # ... qui prosegue la classe con i metodi che ora useranno self.config_manager.symbols invece di self.symbols ...
    """
    1. Inizializzazione
    """
    def __init__(self, config, engine, trading_system=None):
        """Initialize with either ConfigManager or dict, thread-safe runtime"""
        self._lock = threading.Lock()
        if hasattr(config, 'get_risk_params'):
            self._config_manager = config
            self._config = config.config
        else:
            self._config_manager = None
            self._config = config
        self.engine = engine
        self.trading_system = trading_system
        account_info = mt5.account_info()
        config_dict = self._config.config if hasattr(self._config, 'config') else self._config
        self.drawdown_tracker = DailyDrawdownTracker(
            account_info.equity if account_info else 10000,
            config_dict
        )
        self._symbol_data = {}
        # Parametri da config
        self.trailing_stop_activation = config.get('risk_management', {}).get('trailing_stop_activation', 0.5)
        self.trailing_step = config.get('risk_management', {}).get('trailing_step', 0.3)
        self.profit_multiplier = config.get('risk_management', {}).get('profit_multiplier', 1.5)

    # Getter/setter thread-safe per symbol_data
    def get_symbol_data(self, symbol=None):
        with self._lock:
            if symbol is not None:
                return self._symbol_data.get(symbol, None)
            return dict(self._symbol_data)
    def set_symbol_data(self, symbol, value):
        with self._lock:
            self._symbol_data[symbol] = value
    
    @property
    def config(self):
        """Property per accesso alla configurazione"""
        return self._config
        
        
    """
    2. Calcolo Dimensioni Posizione
    """
    def calculate_position_size(self, symbol: str, price: float, signal: str, risk_percent: float = None) -> float:
        """Calcola dimensione posizione normalizzata per rischio e pip value, con limiti di esposizione globale e log dettagliato"""
        try:
            if not self._load_symbol_data(symbol):
                logger.debug(f"[SIZE-DEBUG-TRACE] Blocco su _load_symbol_data({symbol})")
                logger.error(f"Impossibile caricare dati simbolo {symbol}")
                return 0.0

            risk_config = self.get_risk_config(symbol)
            account = mt5.account_info()
            if not account:
                logger.debug(f"[SIZE-DEBUG-TRACE] Blocco su account_info None per {symbol}")
                logger.error("Impossibile ottenere info account")
                return 0.0

            # Parametri base
            if risk_percent is None:
                risk_percent = risk_config.get('risk_percent', 0.02)
            risk_amount = account.equity * risk_percent
            sl_pips = self._calculate_sl_pips(symbol)
            symbol_data = self._symbol_data[symbol]
            pip_size = symbol_data['pip_size']
            contract_size = symbol_data.get('contract_size', 1.0)
            volume_min = symbol_data.get('volume_min', None)
            volume_max = symbol_data.get('volume_max', None)
            volume_step = symbol_data.get('volume_step', None)

            # Calcolo pip_value (pip_size * contract_size)
            pip_value = pip_size * contract_size
            # Target pip value normalizzato (es: 10 USD a pip per tutti i simboli)
            target_pip_value = self._get_config(symbol, 'target_pip_value', 10.0)
            if pip_value <= 0 or sl_pips <= 0:
                logger.error(f"Valori non validi: sl_pips={sl_pips}, pip_value={pip_value}")
                return 0.0

            # Size normalizzata per pip_value: size = (risk_amount / sl_pips) / pip_value
            size = (risk_amount / sl_pips) / pip_value

            # Normalizza per target_pip_value (opzionale, per rendere P&L simile tra simboli)
            size = size * (pip_value / target_pip_value)

            logger.warning(f"[SIZE-DEBUG-TRACE] {symbol} | risk_amount={risk_amount} | sl_pips={sl_pips} | pip_value={pip_value} | size_raw={size} | max_size_limit={self._get_config(symbol, 'max_size_limit', None)} | volume_min={volume_min} | volume_max={volume_max}")

            # Limite massimo assoluto per simbolo
            max_size_limit = self._get_config(symbol, 'max_size_limit', None)
            if max_size_limit is None:
                config = self.config.config if hasattr(self.config, 'config') else self.config
                max_size_limit = config.get('risk_parameters', {}).get('max_size_limit', 0.1)
            if size > max_size_limit:
                logger.warning(f"Size limitata per {symbol}: {size:.2f} -> {max_size_limit} (Safety limit applicato)")
                size = max_size_limit

            # Limite esposizione globale (sommatoria size * contract_size su tutti i simboli)
            max_global_exposure = self._get_config(symbol, 'max_global_exposure', None)
            if max_global_exposure is not None:
                total_exposure = 0.0
                for sym in self.symbols:
                    if sym == symbol:
                        total_exposure += size * contract_size
                    else:
                        # Salta simboli non ancora presenti in _symbol_data per evitare KeyError
                        if sym not in self._symbol_data:
                            continue
                        total_exposure += self._symbol_data[sym].get('last_size', 0.0) * self._symbol_data[sym].get('contract_size', 1.0)
                if total_exposure > max_global_exposure:
                    logger.warning(f"Esposizione globale superata: {total_exposure} > {max_global_exposure}. Size ridotta a zero.")
                    size = 0.0

            # Applica limiti broker e arrotondamenti
            size = self._apply_size_limits(symbol, size)

            # Salva la size calcolata per uso futuro (esposizione globale)
            self._symbol_data[symbol]['last_size'] = size

            symbol_type = 'Metallo' if symbol in ['XAUUSD', 'XAGUSD'] else ('Indice' if symbol in ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225'] else 'Forex')
            logger.debug(
                f"\n-------------------- [SIZE-DEBUG] --------------------\n"
                f"Symbol: {symbol} ({symbol_type})\n"
                f"Risk Config: {risk_config}\n"
                f"Account Equity: {account.equity}\n"
                f"Risk Percent: {risk_percent}\n"
                f"Risk Amount: {risk_amount}\n"
                f"SL Pips: {sl_pips}\n"
                f"Pip Size: {pip_size}\n"
                f"Contract Size: {contract_size}\n"
                f"Pip Value: {pip_value}\n"
                f"Target Pip Value: {target_pip_value}\n"
                f"Volume Min: {volume_min}\n"
                f"Volume Max: {volume_max}\n"
                f"Volume Step: {volume_step}\n"
                f"Size (post-normalizzazione): {size}\n"
                "------------------------------------------------------\n"
            )
            logger.info(
                f"\n==================== [SIZE-DEBUG] ====================\n"
                f"Symbol: {symbol} ({symbol_type})\n"
                f"Risk Amount: ${risk_amount:.2f} ({risk_percent*100:.2f}%)\n"
                f"SL: {sl_pips:.2f} pips\n"
                f"Pip Value: {pip_value}\n"
                f"Target Pip Value: {target_pip_value}\n"
                f"Size: {size:.4f}\n"
                "======================================================\n"
            )
            return size
        except Exception as e:
            logger.error(f"Errore calcolo dimensione {symbol}: {str(e)}", exc_info=True)
            return 0.0
    
       

    def _apply_size_limits(self, symbol: str, size: float) -> float:
        """Applica limiti di dimensione con controllo margine e logging robusto"""
        try:
            info = mt5.symbol_info(symbol)
            if not info:
                logger.error(f"[_apply_size_limits] Info simbolo non disponibile per {symbol}")
                return 0.0
            # Arrotonda al passo corretto
            step = info.volume_step
            size = round(size / step) * step
            # Applica minimi/massimi del broker
            size = max(size, info.volume_min)
            size = min(size, info.volume_max)
            # CONTROLLO MARGINE: Verifica che la posizione sia sostenibile
            account = mt5.account_info()
            if account and size > 0:
                try:
                    margin_required = mt5.order_calc_margin(
                        mt5.ORDER_TYPE_BUY,
                        symbol,
                        size,
                        info.ask
                    )
                    max_margin = account.margin_free * 0.8
                    if margin_required and margin_required > max_margin:
                        safe_size = size * (max_margin / margin_required)
                        safe_size = round(safe_size / step) * step
                        safe_size = max(safe_size, info.volume_min)
                        logger.warning(f"Riduzione size per {symbol}: {size:.2f} -> {safe_size:.2f} "
                                     f"(Margine richiesto: ${margin_required:.2f}, disponibile: ${max_margin:.2f})")
                        size = safe_size
                except Exception as e:
                    logger.error(f"[_apply_size_limits] Errore calcolo margine per {symbol}: {e}", exc_info=True)
            logger.info(
                "\n==================== [SIZE-FINALE] ====================\n"
                f"Symbol: {symbol}\n"
                f"Size finale: {size:.2f}\n"
                "======================================================\n"
            )
            return size
        except Exception as e:
            logger.error(f"[_apply_size_limits] Errore generale per {symbol}: {e}", exc_info=True)
            return 0.0
    

    """
    3. Gestione Stop Loss e Take Profit
    """
    
    def calculate_dynamic_levels(self, symbol: str, position_type: int, entry_price: float) -> Tuple[float, float]:
        try:
            # --- LOG avanzato: mostra da dove vengono i parametri ---
            min_sl = None
            min_sl_source = ''
            # 1. Prova override simbolo (risk_management)
            symbol_config = self._get_config(symbol, 'stop_loss_pips', None)
            if symbol_config is not None:
                min_sl = symbol_config
                min_sl_source = 'override symbol (stop_loss_pips)'
            else:
                # 2. Prova min_sl_distance_pips (mappa per simbolo)
                min_sl_map = self._get_config(symbol, 'min_sl_distance_pips', None)
                if min_sl_map is not None:
                    min_sl = min_sl_map
                    min_sl_source = 'risk_parameters (min_sl_distance_pips)'
            if min_sl is None:
                # 3. Fallback
                min_sl = 30
                min_sl_source = 'fallback (30)'

            base_sl = self._get_config(symbol, 'base_sl_pips', min_sl)
            base_sl_source = 'base_sl_pips (override/symbol/global)' if base_sl != min_sl else min_sl_source
            profit_multiplier = self._get_config(symbol, 'profit_multiplier', 2.2)
            profit_multiplier_source = 'profit_multiplier (override/symbol/global)'

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Simbolo {symbol} non trovato")
                return 0.0, 0.0
            pip_size = self.engine._get_pip_size(symbol)
            digits = symbol_info.digits

            try:
                volatility = float(self.engine.calculate_quantum_volatility(symbol))
            except Exception:
                volatility = 1.0

            oro = ['XAUUSD', 'XAGUSD']
            indici = ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225']
            if symbol in oro + indici:
                volatility_factor = min(volatility, 1.5)
            else:
                volatility_factor = min(volatility, 1.2)

            buffer_factor = 1.15
            adjusted_sl = base_sl * volatility_factor
            if adjusted_sl <= float(min_sl) * 1.05:
                sl_pips = int(round(float(min_sl) * buffer_factor))
            else:
                sl_pips = int(round(max(adjusted_sl, float(min_sl))))
            tp_pips = int(round(sl_pips * profit_multiplier))

            # --- Trailing stop activation mode support ---
            trailing_stop = self._get_config(symbol, 'trailing_stop', {})
            activation_mode = trailing_stop.get('activation_mode', 'fixed')
            activation_pips = trailing_stop.get('activation_pips', 150)
            if activation_mode == 'percent_tp':
                tp_percentage = trailing_stop.get('tp_percentage', 0.5)
                activation_pips = int(round(tp_pips * tp_percentage))
            self._last_trailing_activation_pips = activation_pips  # per debug o uso esterno

            if position_type == mt5.ORDER_TYPE_BUY:
                sl_price = entry_price - (sl_pips * pip_size)
                tp_price = entry_price + (tp_pips * pip_size)
            else:
                sl_price = entry_price + (sl_pips * pip_size)
                tp_price = entry_price - (tp_pips * pip_size)
            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)
            logger.info(
                "\n==================== [LEVELS-DEBUG] ====================\n"
                f"Symbol: {symbol}\n"
                f"SL: {sl_pips} pips\n"
                f"TP: {tp_pips} pips\n"
                f"Entry Price: {entry_price}\n"
                f"SL Price: {sl_price}\n"
                f"TP Price: {tp_price}\n"
                f"Pip Size: {pip_size} (from config: {self.engine._get_pip_size(symbol)})\n"
                f"Digits: {digits}\n"
                f"Volatility: {volatility:.2f}\n"
                f"Min SL: {min_sl} [{min_sl_source}]\n"
                f"Base SL: {base_sl} [{base_sl_source}]\n"
                f"Multiplier: {profit_multiplier} [{profit_multiplier_source}]\n"
                f"Trailing Activation Mode: {activation_mode}\n"
                f"Trailing Activation Pips: {activation_pips}\n"
                "======================================================\n"
            )
            return sl_price, tp_price
        except Exception as e:
            logger.error(f"Errore calcolo livelli per {symbol}: {str(e)}")
            return 0.0, 0.0
                   
    
    """
    4. Utility e Limitatori di Rischio
    """
    
    def _get_risk_percent(self, symbol: str) -> float:
        """Ottiene la percentuale di rischio con validazione"""
        risk_pct = self._get_config(symbol, 'risk_percent', 0.01)
        return np.clip(risk_pct, 0.001, 0.05)  # Min 0.1%, Max 5%
        
        
    def _calculate_sl_pips(self, symbol: str) -> float:
        """Calcola SL pips robusto come nell'optimizer"""
        # min_sl: 1) override simbolo, 2) risk_parameters, 3) fallback
        min_sl = self._get_config(symbol, 'stop_loss_pips', None)
        if min_sl is None:
            min_sl = self._get_config(symbol, 'min_sl_distance_pips', None)
        if min_sl is None:
            forex = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
            indici = ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225']
            oro = ['XAUUSD', 'XAGUSD']
            crypto = ['BTCUSD', 'ETHUSD']
            if symbol in forex:
                min_sl = 250
            elif symbol in indici:
                min_sl = 400
            elif symbol in oro:
                min_sl = 800
            elif symbol in crypto:
                min_sl = 1200
            else:
                min_sl = 300

        base_sl = self._get_config(symbol, 'base_sl_pips', 30)
        try:
            volatility = float(self.engine.calculate_quantum_volatility(symbol))
        except Exception:
            volatility = 1.0
        oro = ['XAUUSD', 'XAGUSD']
        indici = ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225']
        if symbol in oro + indici:
            volatility_factor = min(volatility, 1.5)
        else:
            volatility_factor = min(volatility, 1.2)

        buffer_factor = 1.15
        adjusted_sl = base_sl * volatility_factor
        if adjusted_sl <= float(min_sl) * 1.05:
            final_sl = int(round(float(min_sl) * buffer_factor))
        else:
            final_sl = int(round(max(adjusted_sl, float(min_sl))))

        logger.debug(
            "\n-------------------- [SL-CALC-DEBUG] ------------------\n"
            f"Symbol: {symbol}\n"
            f"Base SL: {base_sl}\n"
            f"Volatility: {volatility:.2f}\n"
            f"Factor: {volatility_factor:.2f}\n"
            f"Min SL: {min_sl}\n"
            f"Final SL: {final_sl} pips\n"
            "------------------------------------------------------\n"
        )
        return final_sl

    
    def _round_to_step(self, size: float, symbol: str) -> float:
        """Arrotonda la dimensione al passo di volume"""
        step = self._symbol_data[symbol]['volume_step']
        if step > 0:
            size = round(size / step) * step
        return max(size, self._symbol_data[symbol]['volume_min'])
        
        
        
    def _get_config(self, symbol: str, key: str, default: Any = None) -> Any:
        """Helper per ottenere valori dalla configurazione, gestendo anche dict per simbolo"""
        config = self.config.config if hasattr(self.config, 'config') else self.config

        # Prima cerca override specifico del simbolo
        symbol_config = config.get('symbols', {}).get(symbol, {})
        if key in symbol_config.get('risk_management', {}):
            return symbol_config['risk_management'][key]

        # Poi cerca nei parametri globali di rischio
        value = config.get('risk_parameters', {}).get(key, default)
        # Se il valore è un dict (mappa per simbolo), estrai quello giusto
        if isinstance(value, dict):
            # Cerca chiave esatta, poi 'default', poi primo valore numerico
            if symbol in value:
                return value[symbol]
            elif 'default' in value:
                return value['default']
            else:
                # fallback: primo valore numerico trovato
                for v in value.values():
                    if isinstance(v, (int, float)):
                        return v
            # Se non trovato, ritorna il dict stesso (comportamento legacy)
            return default
        return value
        

    
    def get_risk_config(self, symbol: str) -> dict:
        """Versione robusta che unisce configurazione globale e specifica del simbolo"""
        try:
            # Configurazione base
            base_config = self._config.get('risk_parameters', {})
            
            # Configurazione specifica del simbolo
            symbol_config = self._config.get('symbols', {}).get(symbol, {}).get('risk_management', {})
            
            # Unisci le configurazioni (i valori specifici del simbolo sovrascrivono quelli globali)
            merged_config = {
                **base_config,
                **symbol_config,
                'trailing_stop': {
                    **base_config.get('trailing_stop', {}),
                    **symbol_config.get('trailing_stop', {})
                }
            }
            
            # Aggiungi valori di default se mancanti
            if 'risk_percent' not in merged_config:
                merged_config['risk_percent'] = 0.02  # 2% default
            if 'base_sl_pips' not in merged_config:
                merged_config['base_sl_pips'] = 150  # 150 pips default
            if 'profit_multiplier' not in merged_config:
                merged_config['profit_multiplier'] = 2.0  # 2:1 default
            
            # Log per debug
            logger.debug(f"Configurazione rischio per {symbol}: {merged_config}")
            
            return merged_config
            
        except Exception as e:
            logger.error(f"Errore in get_risk_config: {str(e)}")
            # Ritorna configurazione di fallback
            return {
                'risk_percent': 0.02,
                'base_sl_pips': 150,
                'profit_multiplier': 2.0,
                'trailing_stop': {'enable': False}
            }
    
    
    """
    5. Validazione e Controlli
    """
    
    def _load_symbol_data(self, symbol: str) -> bool:
        """Calcolo preciso del pip size per tutti i tipi di strumenti, con supporto pip_size_map da config"""
        try:
            if symbol in self._symbol_data:
                return True

            info = mt5.symbol_info(symbol)
            if not info:
                logger.error(f"Impossibile ottenere info MT5 per {symbol}")
                return False

            # Accesso alla configurazione universale
            config = self.config.config if hasattr(self.config, 'config') else self.config
            symbol_config = config.get('symbols', {}).get(symbol, {})
            risk_config = symbol_config.get('risk_management', {})
            contract_size = risk_config.get('contract_size', 1.0)
            point = info.point

            # 1. Cerca pip_size per simbolo in config (override per simbolo)
            pip_size = None
            if 'pip_size' in risk_config:
                pip_size = float(risk_config['pip_size'])
            else:
                # 2. Cerca pip_size_map globale
                pip_map = config.get('pip_size_map', {})
                pip_size = pip_map.get(symbol)
                if pip_size is None:
                    pip_size = pip_map.get('default', 0.0001)
                pip_size = float(pip_size)

            self._symbol_data[symbol] = {
                'pip_size': pip_size,
                'volume_step': info.volume_step,
                'digits': info.digits,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'contract_size': contract_size
            }

            logger.debug(f"Dati caricati per {symbol}: PipSize={pip_size}, ContractSize={contract_size}, Point={point}")
            logger.info(f"SYMBOL CONFIG LOADED - {symbol}: "
                        f"Type={'Forex' if symbol not in ['XAUUSD','XAGUSD','SP500','NAS100','US30'] else 'Special'} | "
                        f"ContractSize={contract_size} | "
                        f"PipSize={pip_size} | "
                        f"Point={point}")
            return True
        except Exception as e:
            logger.error(f"Errore critico in _load_symbol_data: {str(e)}")
            return False
