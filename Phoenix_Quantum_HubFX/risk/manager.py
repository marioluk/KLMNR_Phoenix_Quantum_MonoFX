"""
QuantumRiskManager - Gestione del rischio, calcolo dimensioni posizione e livelli SL/TP
"""

import MetaTrader5 as mt5
import numpy as np
import logging
from typing import Dict, Tuple, Any, Optional
from .drawdown_tracker import DailyDrawdownTracker

logger = logging.getLogger('QuantumTradingSystem')


class QuantumRiskManager:
    """
    Gestisce il rischio, calcola dimensioni di posizione e livelli SL/TP
    Dipende da QuantumEngine e dalla configurazione
    """
    
    def __init__(self, config, engine, trading_system=None):
        """
        Inizializza il Risk Manager
        
        Args:
            config: ConfigManager o dizionario di configurazione
            engine: QuantumEngine per calcoli di volatilità
            trading_system: Sistema di trading principale (opzionale)
        """
        # Gestione configurazione
        if hasattr(config, 'get_risk_params'):  # È un ConfigManager
            self._config_manager = config
            self._config = config.config
        else:  # È un dizionario raw
            self._config_manager = None
            self._config = config
        
        self.engine = engine
        self.trading_system = trading_system
        
        # Inizializza drawdown tracker
        account_info = mt5.account_info()
        self.drawdown_tracker = DailyDrawdownTracker(
            account_info.equity if account_info else 10000,
            self._config
        )
        
        self.symbol_data = {}
        
        # Parametri da configurazione
        self.trailing_stop_activation = config.get('risk_management', {}).get('trailing_stop_activation', 0.5)
        self.trailing_step = config.get('risk_management', {}).get('trailing_step', 0.3)
        self.profit_multiplier = config.get('risk_management', {}).get('profit_multiplier', 1.5)
    
    @property
    def config(self) -> Dict:
        """Accesso alla configurazione"""
        return self._config

    def calculate_position_size(self, symbol: str, price: float, signal: str) -> float:
        """
        Calcola dimensione posizione con gestione robusta degli errori
        
        Args:
            symbol: Simbolo da tradare
            price: Prezzo di ingresso
            signal: Tipo di segnale (BUY/SELL)
            
        Returns:
            Dimensione della posizione in lotti
        """
        try:
            # 1. Verifica parametri iniziali
            if not self._load_symbol_data(symbol):
                logger.error(f"Impossibile caricare dati simbolo {symbol}")
                return 0.0
                
            # 2. Ottieni parametri di rischio
            risk_config = self.get_risk_config(symbol)
            account = mt5.account_info()
            
            if not account:
                logger.error("Impossibile ottenere info account")
                return 0.0
            
            # 3. Calcola rischio assoluto in valuta base
            risk_percent = risk_config.get('risk_percent', 0.02)  # 2% default
            risk_amount = account.equity * risk_percent
            
            # 4. Calcola SL in pips con volatilità
            sl_pips = self._calculate_sl_pips(symbol)
            
            # 5. Usa pip value dai dati caricati
            symbol_data = self.symbol_data[symbol]
            pip_value = symbol_data['pip_value']
            
            # 6. Calcola size base
            if sl_pips <= 0 or pip_value <= 0:
                logger.error(f"Valori non validi: sl_pips={sl_pips}, pip_value={pip_value}")
                return 0.0
                
            size = risk_amount / (sl_pips * pip_value)
            
            # SAFETY CHECK: Limite massimo assoluto
            max_size_limit = 0.1  # Massimo 0.1 lotti per sicurezza
            if size > max_size_limit:
                logger.warning(f"Size limitata per {symbol}: {size:.2f} -> {max_size_limit} "
                              f"(Safety limit applicato)")
                size = max_size_limit
            
            # 7. Applica limiti
            size = self._apply_size_limits(symbol, size)
            
            logger.info(
                f"Size calc {symbol}: "
                f"Risk=${risk_amount:.2f}({risk_percent*100:.1f}%) | "
                f"SL={sl_pips:.1f}pips | "
                f"PipValue=${pip_value:.4f} | "
                f"Size={size:.2f}"
            )
            
            return size
            
        except Exception as e:
            logger.error(f"Errore calcolo dimensione {symbol}: {str(e)}", exc_info=True)
            return 0.0

    def _apply_size_limits(self, symbol: str, size: float) -> float:
        """
        Applica limiti di dimensione con controllo margine
        
        Args:
            symbol: Simbolo da verificare
            size: Dimensione proposta
            
        Returns:
            Dimensione corretta entro i limiti
        """
        info = mt5.symbol_info(symbol)
        if not info:
            return 0.0
            
        # Arrotonda al passo corretto
        step = info.volume_step
        size = round(size / step) * step
        
        # Applica minimi/massimi del broker
        size = max(size, info.volume_min)
        size = min(size, info.volume_max)
        
        # CONTROLLO MARGINE
        account = mt5.account_info()
        if account and size > 0:
            # Calcola margine richiesto per la posizione
            margin_required = mt5.order_calc_margin(
                mt5.ORDER_TYPE_BUY,
                symbol,
                size,
                info.ask
            )
            
            # Usa max 80% del margine libero per sicurezza
            max_margin = account.margin_free * 0.8
            
            if margin_required and margin_required > max_margin:
                # Riduci la dimensione per rispettare il margine
                safe_size = size * (max_margin / margin_required)
                safe_size = round(safe_size / step) * step
                safe_size = max(safe_size, info.volume_min)
                
                logger.warning(f"Riduzione size per {symbol}: {size:.2f} -> {safe_size:.2f} "
                             f"(Margine richiesto: ${margin_required:.2f}, disponibile: ${max_margin:.2f})")
                size = safe_size
        
        logger.info(f"Size finale per {symbol}: {size:.2f}")
        
        return size

    def calculate_dynamic_levels(self, symbol: str, position_type: int, entry_price: float) -> Tuple[float, float]:
        """
        Calcola livelli di Stop Loss e Take Profit dinamici
        
        Args:
            symbol: Simbolo di trading
            position_type: Tipo di posizione (mt5.ORDER_TYPE_BUY/SELL)
            entry_price: Prezzo di ingresso
            
        Returns:
            Tupla (sl_price, tp_price)
        """
        try:
            symbol_config = self.get_risk_config(symbol)
            min_sl = symbol_config.get('min_sl_distance_pips', 100)
            base_sl = symbol_config.get('base_sl_pips', 150)
            tp_multiplier = symbol_config.get('profit_multiplier', 2.0)

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Simbolo {symbol} non trovato")
                return 0.0, 0.0

            pip_size = self.engine._get_pip_size(symbol)
            digits = symbol_info.digits

            volatility = self.engine.calculate_quantum_volatility(symbol)

            sl_pips = max(
                min_sl,
                min(
                    base_sl * 2.0,
                    base_sl * (1.0 + 0.5 * volatility)
                )
            )
            tp_pips = sl_pips * tp_multiplier

            if position_type == mt5.ORDER_TYPE_BUY:
                sl_price = entry_price - (sl_pips * pip_size)
                tp_price = entry_price + (tp_pips * pip_size)
            else:
                sl_price = entry_price + (sl_pips * pip_size)
                tp_price = entry_price - (tp_pips * pip_size)

            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)

            logger.info(
                f"Livelli calcolati per {symbol}: SL={sl_pips:.1f}pips TP={tp_pips:.1f}pips "
                f"(Volatility={volatility:.2f}, Config: min_sl={min_sl}, base_sl={base_sl}, multiplier={tp_multiplier})"
            )
            return sl_price, tp_price

        except Exception as e:
            logger.error(f"Errore calcolo livelli per {symbol}: {str(e)}")
            return 0.0, 0.0

    def _get_risk_percent(self, symbol: str) -> float:
        """
        Ottiene la percentuale di rischio con validazione
        
        Args:
            symbol: Simbolo da verificare
            
        Returns:
            Percentuale di rischio limitata tra 0.1% e 5%
        """
        risk_pct = self._get_config(symbol, 'risk_percent', 0.01)
        return np.clip(risk_pct, 0.001, 0.05)  # Min 0.1%, Max 5%

    def _calculate_sl_pips(self, symbol: str) -> float:
        """
        Calcola gli SL pips con volatilità adattiva limitata
        
        Args:
            symbol: Simbolo da analizzare
            
        Returns:
            Stop Loss in pips
        """
        defaults = {'default': 15, 'XAUUSD': 80, 'BTCUSD': 150}
        min_sl = self._get_config(symbol, 'min_sl_distance_pips', defaults.get(symbol, 15))
        
        base_defaults = {'default': 30, 'XAUUSD': 150, 'BTCUSD': 400}
        base_sl = self._get_config(symbol, 'base_sl_pips', base_defaults.get(symbol, 30))
        
        # Ottieni la volatilità quantistica corrente con limitazioni
        volatility = self.engine.calculate_quantum_volatility(symbol)
        
        # Limita l'amplificazione della volatilità
        if symbol in ['XAUUSD', 'XAGUSD', 'SP500', 'NAS100', 'US30']:
            volatility_factor = min(volatility, 1.5)  # Max +50%
        else:  # Forex
            volatility_factor = min(volatility, 1.2)  # Max +20%
        
        adjusted_sl = base_sl * volatility_factor
        final_sl = max(adjusted_sl, min_sl)
        
        logger.debug(f"SL calculation for {symbol}: base={base_sl}, volatility={volatility:.2f}, "
                    f"factor={volatility_factor:.2f}, final={final_sl:.1f} pips")
        
        return final_sl

    def _round_to_step(self, size: float, symbol: str) -> float:
        """
        Arrotonda la dimensione al passo di volume
        
        Args:
            symbol: Simbolo di riferimento
            size: Dimensione da arrotondare
            
        Returns:
            Dimensione arrotondata
        """
        step = self.symbol_data[symbol]['volume_step']
        if step > 0:
            size = round(size / step) * step
        return max(size, self.symbol_data[symbol]['volume_min'])

    def _get_config(self, symbol: str, key: str, default: Any = None) -> Any:
        """
        Helper per ottenere valori dalla configurazione
        
        Args:
            symbol: Simbolo di riferimento
            key: Chiave di configurazione
            default: Valore di default
            
        Returns:
            Valore della configurazione
        """
        # Accesso sicuro alla configurazione
        config = self.config.config if hasattr(self.config, 'config') else self.config
        
        # Cerca prima nelle impostazioni specifiche del simbolo
        symbol_config = config.get('symbols', {}).get(symbol, {})
        if key in symbol_config.get('risk_management', {}):
            return symbol_config['risk_management'][key]
        
        return config.get('risk_parameters', {}).get(key, default)

    def get_risk_config(self, symbol: str) -> Dict:
        """
        Ottiene la configurazione di rischio per un simbolo
        
        Args:
            symbol: Simbolo di trading
            
        Returns:
            Dizionario con la configurazione di rischio
        """
        try:
            # Configurazione base
            base_config = self._config.get('risk_parameters', {})
            
            # Configurazione specifica del simbolo
            symbol_config = self._config.get('symbols', {}).get(symbol, {}).get('risk_management', {})
            
            # Unisci le configurazioni
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
            
            logger.debug(f"Configurazione rischio per {symbol}: {merged_config}")
            
            return merged_config
            
        except Exception as e:
            logger.error(f"Errore in get_risk_config: {str(e)}")
            # Configurazione di fallback
            return {
                'risk_percent': 0.02,
                'base_sl_pips': 150,
                'profit_multiplier': 2.0,
                'trailing_stop': {'enable': False}
            }

    def _load_symbol_data(self, symbol: str) -> bool:
        """
        Carica i dati del simbolo da MetaTrader 5
        
        Args:
            symbol: Simbolo da caricare
            
        Returns:
            True se caricato con successo, False altrimenti
        """
        try:
            if symbol in self.symbol_data:
                return True
                
            info = mt5.symbol_info(symbol)
            if not info:
                logger.error(f"Impossibile ottenere info MT5 per {symbol}")
                return False
            
            # Accesso alla configurazione
            config = self.config.config if hasattr(self.config, 'config') else self.config
            symbol_config = config.get('symbols', {}).get(symbol, {})
            risk_config = symbol_config.get('risk_management', {})
            
            point = info.point
            contract_size = risk_config.get('contract_size', 1.0)
            
            logger.debug(f"Raw data for {symbol}: point={point}, contract_size={contract_size}")
            
            # Calcolo preciso del pip value
            if symbol in ['XAUUSD', 'XAGUSD']:
                # Per oro: 1 lotto = 100 once, 1 pip = $0.01 per oncia
                pip_value = 1.0 * contract_size
            elif symbol in ['SP500', 'NAS100', 'US30']:
                # Per indici: 1 pip = $1.0 per lotto standard
                pip_value = 1.0 * contract_size
            else:  # Forex
                # Per forex: 1 pip = $10 per lotto standard (100,000 unità)
                pip_value = 10.0 * contract_size
            
            self.symbol_data[symbol] = {
                'pip_value': pip_value,
                'volume_step': info.volume_step,
                'digits': info.digits,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'contract_size': contract_size
            }
            
            logger.debug(f"Dati caricati per {symbol}: PipValue=${pip_value:.2f}, ContractSize={contract_size}")
            
            logger.info(f"SYMBOL CONFIG LOADED - {symbol}: "
                       f"Type={'Forex' if symbol not in ['XAUUSD','XAGUSD','SP500','NAS100','US30'] else 'Special'} | "
                       f"ContractSize={contract_size} | "
                       f"PipValue=${pip_value:.4f} | "
                       f"Point={point}")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore critico in _load_symbol_data: {str(e)}")
            return False

    def update_drawdown_tracker(self, current_equity: float, current_balance: float) -> None:
        """
        Aggiorna il tracker del drawdown
        
        Args:
            current_equity: Equity corrente
            current_balance: Balance corrente
        """
        self.drawdown_tracker.update(current_equity, current_balance)

    def check_drawdown_limits(self, current_equity: float) -> Tuple[bool, bool]:
        """
        Verifica i limiti di drawdown
        
        Args:
            current_equity: Equity corrente da verificare
            
        Returns:
            Tupla (soft_limit_hit, hard_limit_hit)
        """
        return self.drawdown_tracker.check_limits(current_equity)
