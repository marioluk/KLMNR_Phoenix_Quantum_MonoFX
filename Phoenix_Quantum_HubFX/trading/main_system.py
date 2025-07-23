"""
QuantumTradingSystem - Sistema principale di trading algoritmico quantistico
"""

import MetaTrader5 as mt5
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock
from typing import Dict, Any

from config import ConfigManager
from engine import QuantumEngine
from risk import QuantumRiskManager, DailyDrawdownTracker
from metrics import TradingMetrics
from utils import is_trading_hours
from log_utils.setup import setup_logger, clean_old_logs

logger = logging.getLogger('QuantumTradingSystem')


class QuantumTradingSystem:
    """
    Sistema completo di trading algoritmico quantistico che coordina tutti i componenti:
    - ConfigManager per la configurazione
    - QuantumEngine per l'elaborazione dei segnali  
    - QuantumRiskManager per la gestione del rischio
    - TradingMetrics per il monitoraggio delle performance
    """
    
    def __init__(self, config_path: str):
        """
        Inizializza il sistema di trading quantistico
        
        Args:
            config_path: Percorso del file di configurazione JSON
        """
        print(f"🔧 Inizializzazione QuantumTradingSystem...")
        print(f"📁 File configurazione: {config_path}")
        
        # Setup logging
        self._setup_logger(config_path)
        print("✅ Logger configurato")
        
        self._config_path = config_path
        self.running = False
        
        # Caricamento configurazione
        print("📋 Caricamento configurazione...")
        self._load_configuration(config_path)
        print("✅ Configurazione caricata")
        
        # Verifica configurazione minima
        if not hasattr(self.config, 'config') or 'symbols' not in self.config.config:
            logger.error("Configurazione simboli non valida")
            raise ValueError("Sezione symbols mancante nella configurazione")
        
        print(f"🎯 Simboli trovati: {list(self.config.config['symbols'].keys())}")
        
        # Inizializzazione componenti core
        print("🔄 Inizializzazione componenti core...")
        
        # Attiva simboli in MT5
        print("📡 Attivazione simboli in MT5...")
        self._activate_symbols()
        print("✅ Simboli attivati")
        
        # Inizializza motore quantistico
        print("🧠 Inizializzazione Quantum Engine...")
        self.engine = QuantumEngine(self.config)
        print("✅ Quantum Engine pronto")
        
        # Inizializza risk manager
        print("💰 Inizializzazione Risk Manager...")
        self.risk_manager = QuantumRiskManager(self.config, self.engine, self)
        print("✅ Risk Manager pronto")
        
        # Parametri di trading
        self.max_positions = self.config.get_risk_params().get('max_positions', 4)
        self.current_positions = 0
        self.trade_count = defaultdict(int)
        
        # Inizializzazione MT5
        print("📡 Connessione a MetaTrader 5...")
        if not self._initialize_mt5():
            raise RuntimeError("Inizializzazione MT5 fallita")
        print("✅ MT5 connesso")
        
        # Metriche e tracking
        self.metrics_lock = Lock()
        self.position_lock = Lock()
        self.metrics = TradingMetrics()
        
        # Tracking delle performance
        self.trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'symbol_stats': defaultdict(dict)
        }
        
        # Timers per controlli periodici
        self.last_position_check = time.time()
        self.last_connection_check = time.time()
        self.last_account_update = time.time()
        self.last_tick_check = time.time()
        
        # Info account
        self.account_info = None
        
        print("🚀 QuantumTradingSystem inizializzato con successo!")

    def _setup_logger(self, config_path: str) -> None:
        """Configura il sistema di logging"""
        global logger
        logger = setup_logger(config_path)
        clean_old_logs()

    def _load_configuration(self, config_path: str) -> None:
        """Carica il file di configurazione"""
        try:
            self.config = ConfigManager(config_path)
            logger.info(f"Configurazione caricata da {config_path}")
        except Exception as e:
            logger.error(f"Errore caricamento configurazione: {str(e)}")
            raise

    def _activate_symbols(self) -> None:
        """Attiva automaticamente i simboli richiesti in MT5"""
        try:
            symbols = list(self.config.config.get('symbols', {}).keys())
            for symbol in symbols:
                if mt5.symbol_select(symbol, True):
                    logger.info(f"Simbolo {symbol} attivato in MT5")
                else:
                    logger.warning(f"Impossibile attivare simbolo {symbol}")
        except Exception as e:
            logger.error(f"Errore attivazione simboli: {str(e)}")

    def _initialize_mt5(self) -> bool:
        """Connessione a MetaTrader 5"""
        try:
            mt5.shutdown()
            
            config = self.config.config.get('metatrader5', {})
            if not mt5.initialize(
                path=config.get('path'),
                login=int(config.get('login', 0)),
                password=config.get('password', ''),
                server=config.get('server', ''),
                timeout=60000,
                port=int(config.get('port', 18889))
            ):
                logger.error(f"Errore inizializzazione MT5: {mt5.last_error()}")
                return False
                
            logger.info(f"Connesso a {config.get('server', '')} sulla porta {config.get('port', 18889)}")
            return True
            
        except Exception as e:
            logger.error(f"Eccezione durante inizializzazione MT5: {str(e)}")
            return False

    def start(self) -> None:
        """Avvia il sistema di trading"""
        print("🚀 ==> AVVIO QUANTUM TRADING SYSTEM <== 🚀")
        try:
            if not self._verify_connection():
                raise RuntimeError("Connessione MT5 non disponibile")
                
            logger.info("Sistema di trading avviato")
            self.running = True
            self._main_loop()
            
        except Exception as e:
            logger.critical(f"Errore critico durante l'avvio: {str(e)}", exc_info=True)
            self.running = False
        finally:
            self.stop()

    def stop(self) -> None:
        """Ferma il sistema"""
        self.running = False
        
        # Reset timer attributi se esistono
        if hasattr(self, 'last_position_check'):
            del self.last_position_check
        if hasattr(self, 'last_connection_check'):
            del self.last_connection_check
        if hasattr(self, 'last_account_update'):
            del self.last_account_update
        if hasattr(self, 'last_tick_check'):
            del self.last_tick_check
        
        mt5.shutdown()
        logger.info("Sistema arrestato correttamente")

    def _verify_connection(self) -> bool:
        """Verifica/connessione MT5 con ripristino automatico"""
        try:
            # Test connessione
            account_info = mt5.account_info()
            if account_info is None:
                logger.warning("Connessione MT5 persa, tentativo di riconnessione...")
                return self._initialize_mt5()
            return True
        except Exception as e:
            logger.error(f"Errore verifica connessione: {str(e)}")
            return False

    def _main_loop(self) -> None:
        """
        Loop principale di trading con controlli periodici
        """
        logger.info("Avvio loop principale di trading")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Verifica connessione ogni 30 secondi
                if current_time - self.last_connection_check > 30:
                    if not self._verify_connection():
                        logger.error("Connessione MT5 fallita, pausa 60s")
                        time.sleep(60)
                        continue
                    self.last_connection_check = current_time

                # Aggiorna info account ogni 60 secondi
                if current_time - self.last_account_update > 60:
                    self._update_account_info()
                    self._check_drawdown_limits()
                    self.last_account_update = current_time

                # Monitora posizioni ogni 5 secondi
                if current_time - self.last_position_check > 5:
                    self._monitor_open_positions()
                    self.last_position_check = current_time

                # Processa simboli per nuovi segnali
                self._process_symbols()
                
                # Chiusura weekend
                self.close_positions_before_weekend()
                
                # Pausa tra iterazioni
                time.sleep(2)
                
            except KeyboardInterrupt:
                logger.info("Interruzione da utente ricevuta")
                break
            except Exception as e:
                logger.error(f"Errore nel loop principale: {str(e)}", exc_info=True)
                time.sleep(5)

    def _process_symbols(self) -> None:
        """Processa tutti i simboli configurati"""
        current_positions = len(mt5.positions_get() or [])
        
        for symbol in self.config.symbols:
            try:
                # Ottieni tick corrente
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    continue
                    
                # Processa il simbolo
                self._process_single_symbol(symbol, tick, current_positions)
                
            except Exception as e:
                logger.error(f"Errore processo simbolo {symbol}: {str(e)}")

    def _process_single_symbol(self, symbol: str, tick, current_positions: int) -> None:
        """Processa un singolo simbolo per segnali di trading"""
        try:
            # 1. Verifica se possiamo fare trading
            if not self.engine.can_trade(symbol):
                return
                
            # 2. Verifica orari di trading
            if not is_trading_hours(symbol, self.config.config):
                return
                
            # 3. Verifica posizioni esistenti
            existing_positions = mt5.positions_get(symbol=symbol)
            if existing_positions and len(existing_positions) > 0:
                return
                
            # 4. Verifica limite posizioni totali
            if current_positions >= self.max_positions:
                return
            
            # 5. Processa tick nel motore quantistico
            mid_price = (tick.ask + tick.bid) / 2
            self.engine.process_tick(symbol, mid_price)
            
            # 6. Ottieni segnale (senza attivare cooldown)
            signal, price = self.engine.get_signal(symbol, for_trading=False)
            
            logger.debug(f"🔍 Segnale per {symbol}: {signal} (Price: {price})")
            
            if signal in ["BUY", "SELL"]:
                # Calcola dimensione posizione
                size = self.risk_manager.calculate_position_size(symbol, price, signal)
                
                if size > 0:
                    # Attiva cooldown ed esegui trade
                    self.engine.get_signal(symbol, for_trading=True)  # Attiva cooldown
                    success = self._execute_trade(symbol, signal, tick, price, size)
                    
                    if success:
                        logger.info(f"✅ Trade {signal} {symbol} eseguito con successo")
                    else:
                        logger.warning(f"❌ Trade {signal} {symbol} fallito")
                        
        except Exception as e:
            logger.error(f"Errore processo simbolo {symbol}: {str(e)}", exc_info=True)

    def _execute_trade(self, symbol: str, signal: str, tick, price: float, size: float) -> bool:
        """Esegue un trade con gestione completa degli errori"""
        try:
            logger.info(f"🚀 INIZIO ESECUZIONE TRADE: {signal} {symbol} | Size: {size} | Price: {price}")
            
            # Determina tipo ordine
            order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
            
            # Calcola livelli SL/TP
            sl_price, tp_price = self.risk_manager.calculate_dynamic_levels(
                symbol, order_type, price
            )
            
            # Prepara richiesta ordine
            symbol_info = mt5.symbol_info(symbol)
            execution_price = symbol_info.ask if signal == "BUY" else symbol_info.bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": size,
                "type": order_type,
                "price": execution_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 10,
                "magic": self.config.config['risk_parameters']['magic_number'],
                "comment": "QTS-AUTO",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            # Esegui ordine
            logger.info(f"Esecuzione {signal} {symbol}: {size} lots @ {execution_price}")
            result = mt5.order_send(request)
            
            # Se fallisce per filling mode, prova con metodo alternativo
            if result.retcode == 10030:
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                result = mt5.order_send(request)
            
            # Verifica risultato
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Ordine fallito: {result.retcode} - {result.comment}")
                return False
                
            logger.info(f"Trade eseguito {symbol} {size} lots a {execution_price} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")
            logger.info(f"Ticket: {result.order} | Deal: {result.deal}")
            
            # Aggiorna metriche
            try:
                self._update_trade_metrics(success=True, symbol=symbol, profit=0.0)
            except Exception as e:
                logger.error(f"Errore aggiornamento metriche: {str(e)}")
            
            # Pausa di sicurezza post-trade
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Errore esecuzione trade {symbol}: {str(e)}", exc_info=True)
            return False

    def _monitor_open_positions(self) -> None:
        """Monitoraggio avanzato delle posizioni aperte"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
                
            for position in positions:
                try:
                    # Ottieni prezzo corrente
                    symbol_info = mt5.symbol_info(position.symbol)
                    if not symbol_info:
                        continue
                        
                    current_price = symbol_info.ask if position.type == mt5.ORDER_TYPE_BUY else symbol_info.bid
                    
                    # Gestione trailing stop
                    self._manage_trailing_stop(position, current_price)
                    
                    # Controllo timeout posizione
                    self._check_position_timeout(position)
                    
                except Exception as e:
                    logger.error(f"Errore monitoraggio posizione {position.ticket}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Errore critico in _monitor_open_positions: {str(e)}")

    def _manage_trailing_stop(self, position, current_price: float) -> bool:
        """Gestione trailing stop (implementazione semplificata)"""
        try:
            # Implementazione base - da espandere se necessario
            risk_config = self.risk_manager.get_risk_config(position.symbol)
            trailing_config = risk_config.get('trailing_stop', {})
            
            if not trailing_config.get('enable', False):
                return False
                
            # Logica trailing stop qui se necessaria
            return False
            
        except Exception as e:
            logger.error(f"Errore trailing stop posizione {position.ticket}: {str(e)}")
            return False

    def _check_position_timeout(self, position) -> None:
        """Controlla timeout posizione"""
        try:
            risk_config = self.risk_manager.get_risk_config(position.symbol)
            max_hours = risk_config.get('position_timeout_hours', 24)
            
            # Gestione timestamp
            if hasattr(position, 'time_setup'):
                timestamp = position.time_setup
            elif hasattr(position, 'time'):
                timestamp = position.time
            else:
                return
                
            # Converti in datetime
            if isinstance(timestamp, (int, float)):
                if timestamp > 1e10:
                    position_dt = datetime.fromtimestamp(timestamp / 1000)
                else:
                    position_dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, datetime):
                position_dt = timestamp
            else:
                return

            # Calcola durata
            current_dt = datetime.now()
            duration = current_dt - position_dt
            duration_hours = duration.total_seconds() / 3600

            if duration_hours > max_hours:
                logger.info(f"Chiusura posizione {position.ticket} per timeout ({duration_hours:.1f}h > {max_hours}h)")
                self._close_position(position)
                
        except Exception as e:
            logger.error(f"Errore controllo timeout posizione {position.ticket}: {str(e)}")

    def _close_position(self, position) -> bool:
        """Chiude una posizione esistente"""
        try:
            # Verifica che la posizione esista ancora
            existing_positions = mt5.positions_get(ticket=position.ticket)
            if not existing_positions or len(existing_positions) == 0:
                logger.info(f"Posizione {position.ticket} già chiusa")
                return True
            
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                logger.error(f"Simbolo {position.symbol} non trovato")
                return False
                
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": symbol_info.ask if position.type == mt5.ORDER_TYPE_BUY else symbol_info.bid,
                "deviation": 10,
                "magic": self.config.config['risk_parameters']['magic_number'],
                "comment": "QTS-CLOSE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(close_request)
                
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                profit = (position.price_current - position.price_open) * position.volume
                self._update_trade_metrics(
                    success=True, 
                    symbol=position.symbol, 
                    profit=profit
                )
                logger.info(f"Posizione {position.ticket} chiusa con successo")
                return True
            else:
                logger.warning(f"Chiusura posizione {position.ticket} fallita: {result.retcode}")
                return False
            
        except Exception as e:
            logger.error(f"Errore chiusura posizione {position.ticket}: {str(e)}")
            return False

    def _update_account_info(self) -> None:
        """Aggiorna info account"""
        try:
            self.account_info = mt5.account_info()
            if self.account_info and hasattr(self.risk_manager, 'drawdown_tracker'):
                self.risk_manager.drawdown_tracker.update(
                    self.account_info.equity,
                    self.account_info.balance
                )
        except Exception as e:
            logger.error(f"Errore aggiornamento account: {str(e)}")

    def _check_drawdown_limits(self) -> None:
        """Controlla limiti drawdown"""
        if not hasattr(self.risk_manager, 'drawdown_tracker') or not self.account_info:
            return
        
        soft_hit, hard_hit = self.risk_manager.drawdown_tracker.check_limits(self.account_info.equity)
        
        if hard_hit:
            logger.critical("Hard drawdown limit raggiunto!")
            raise RuntimeError("Hard drawdown limit raggiunto")
        
        if soft_hit and not self.risk_manager.drawdown_tracker.protection_active:
            logger.warning("Soft drawdown limit - riduzione esposizione")
            self.risk_manager.drawdown_tracker.protection_active = True
            self.max_positions = max(1, self.max_positions // 2)
            logger.info(f"Max posizioni ridotto a {self.max_positions}")

    def _update_trade_metrics(self, success: bool, symbol: str, profit: float = 0.0) -> None:
        """Aggiorna metriche con controllo del limite giornaliero"""
        try:
            with self.metrics_lock:
                self.trade_metrics['total_trades'] += 1
                
                if success:
                    self.trade_metrics['successful_trades'] += 1
                else:
                    self.trade_metrics['failed_trades'] += 1
                    
                self.trade_metrics['total_profit'] += profit
                
                # Aggiorna statistiche per simbolo
                if symbol not in self.trade_metrics['symbol_stats']:
                    self.trade_metrics['symbol_stats'][symbol] = {
                        'trades': 0,
                        'profit': 0.0,
                        'wins': 0,
                        'losses': 0
                    }
                    
                stats = self.trade_metrics['symbol_stats'][symbol]
                stats['trades'] += 1
                stats['profit'] += profit
                
                if profit > 0:
                    stats['wins'] += 1
                else:
                    stats['losses'] += 1
                    
                logger.info(f"Metriche aggiornate: {symbol} P/L={profit:.2f}")
                
        except Exception as e:
            logger.error(f"Errore aggiornamento metriche: {str(e)}")

    def close_positions_before_weekend(self) -> None:
        """Chiude tutte le posizioni aperte il venerdì sera"""
        now = datetime.now()
        # Venerdì = 4 (lunedì=0), chiusura alle 21:00
        if now.weekday() == 4 and now.hour >= 21:
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    try:
                        self._close_position(pos)
                        logger.info(f"Chiusura automatica posizione {pos.ticket} su {pos.symbol} per fine settimana.")
                    except Exception as e:
                        logger.error(f"Errore chiusura automatica {pos.ticket}: {str(e)}")

    def check_buffers(self) -> None:
        """Controlla lo stato dei buffer di ogni simbolo"""
        for symbol in self.config.symbols:
            buffer = self.engine.tick_buffer.get(symbol, [])
            logger.debug(f"Buffer {symbol}: {len(buffer)} ticks")
