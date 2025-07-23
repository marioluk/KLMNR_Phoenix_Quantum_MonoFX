"""
MultiQuantumTradingSystem - Sistema principale con supporto multi-broker
"""

import time
import logging
from datetime import datetime
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional, Any

from config import ConfigManager
from engine import QuantumEngine
from risk import QuantumRiskManager
from metrics import TradingMetrics
from utils import is_trading_hours
from log_utils.setup import setup_logger, clean_old_logs
from brokers import BrokerManager, MultiBrokerConfigLoader, BrokerConfig

def get_safe_logger():
    l = logging.getLogger('QuantumTradingSystem')
    if l is None or not l.handlers:
        # Fallback: logger console warning
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(formatter)
        l.setLevel(logging.WARNING)
        l.addHandler(ch)
    return l

logger = get_safe_logger()


class MultiQuantumTradingSystem:
    """
    Sistema di trading quantistico con supporto multi-broker
    Gestisce The5ers, FTMO e altri broker simultaneamente
    """
    
    def __init__(self, config_path: str):
        """
        Inizializza il sistema multi-broker
        
        Args:
            config_path: Percorso configurazione principale
        """
        print("🔧 Inizializzazione MultiQuantumTradingSystem...")
        print(f"📁 File configurazione: {config_path}")
        
        # Setup logging
        self._setup_logger(config_path)
        print("✅ Logger configurato")
        
        self._config_path = config_path
        self.running = False
        
        # Carica configurazioni multi-broker
        print("🏢 Caricamento configurazioni broker...")
        self.config_loader = MultiBrokerConfigLoader(config_path)
        self.broker_configs = self.config_loader.load_multi_broker_configs()
        print(f"✅ {len(self.broker_configs)} configurazioni broker caricate")
        
        # Inizializza broker manager
        print("🌐 Inizializzazione BrokerManager...")
        self.broker_manager = BrokerManager(self.broker_configs)
        print("✅ BrokerManager pronto")
        
        # Carica configurazione principale (per retrocompatibilità)
        self.main_config = ConfigManager(config_path)
        
        # Crea engines e risk managers per broker
        print("⚙️ Inizializzazione engines e risk managers...")
        self.engines: Dict[str, QuantumEngine] = {}
        self.risk_managers: Dict[str, QuantumRiskManager] = {}
        
        for broker_config in self.broker_configs:
            # Engine per broker
            broker_engine = QuantumEngine(self.main_config)
            self.engines[broker_config.name] = broker_engine
            
            # Risk manager per broker  
            broker_risk_mgr = QuantumRiskManager(self.main_config, broker_engine, self)
            self.risk_managers[broker_config.name] = broker_risk_mgr
            
            print(f"   ✅ {broker_config.name}: Engine + RiskManager configurati")
        
        # Parametri globali
        self.max_total_positions = 10
        self.max_positions_per_broker = 5
        self.enable_cross_broker_hedging = True
        
        # Metriche e tracking
        self.metrics_lock = Lock()
        self.global_metrics = TradingMetrics()
        self.broker_metrics: Dict[str, TradingMetrics] = {}
        
        for broker_config in self.broker_configs:
            self.broker_metrics[broker_config.name] = TradingMetrics()
        
        # Trade tracking
        self.trade_count = defaultdict(int)
        self.broker_trade_count = defaultdict(lambda: defaultdict(int))
        
        # Timers
        self.last_position_check = time.time()
        self.last_broker_check = time.time()
        self.last_metrics_update = time.time()
        
        print("🚀 MultiQuantumTradingSystem inizializzato con successo!")

    def _setup_logger(self, config_path: str) -> None:
        """Configura il sistema di logging"""
        global logger
        logger = setup_logger(config_path)
        clean_old_logs()

    def start(self) -> None:
        """Avvia il sistema multi-broker"""
        print("🚀 ==> AVVIO MULTI QUANTUM TRADING SYSTEM <== 🚀")
        
        try:
            # Inizializza connessioni broker
            logger.info("🏢 Inizializzazione connessioni broker...")
            connection_results = self.broker_manager.initialize_all_connections()
            
            connected_brokers = sum(1 for success in connection_results.values() if success)
            if connected_brokers == 0:
                raise RuntimeError("Nessun broker connesso")
                
            logger.info(f"✅ {connected_brokers} broker connessi e operativi")
            
            # Avvia loop principale
            self.running = True
            self._main_loop()
            
        except Exception as e:
            logger.critical(f"Errore critico durante l'avvio: {str(e)}", exc_info=True)
            self.running = False
        finally:
            self.stop()

    def stop(self) -> None:
        """Ferma il sistema multi-broker"""
        logger.info("🛑 Fermata sistema multi-broker...")
        
        self.running = False
        
        # Chiudi tutte le posizioni (opzionale)
        try:
            logger.info("📊 Chiusura posizioni aperte...")
            results = self.broker_manager.close_all_positions()
            total_closed = sum(results.values())
            logger.info(f"✅ {total_closed} posizioni chiuse su tutti i broker")
        except Exception as e:
            logger.error(f"Errore chiusura posizioni: {str(e)}")
        
        # Shutdown broker manager
        self.broker_manager.shutdown_all()
        
        logger.info("✅ Sistema multi-broker fermato correttamente")

    def _main_loop(self) -> None:
        """Loop principale multi-broker"""
        logger.info("🔄 Avvio loop principale multi-broker")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Verifica stato broker ogni 30 secondi
                if current_time - self.last_broker_check > 30:
                    self._check_broker_health()
                    self.last_broker_check = current_time
                
                # Monitora posizioni ogni 10 secondi
                if current_time - self.last_position_check > 10:
                    self._monitor_all_positions()
                    self.last_position_check = current_time
                
                # Aggiorna metriche ogni 60 secondi
                if current_time - self.last_metrics_update > 60:
                    self._update_global_metrics()
                    self.last_metrics_update = current_time
                
                # Processa simboli su tutti i broker
                self._process_all_brokers()
                
                # Pausa tra iterazioni
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Interruzione da utente ricevuta")
                break
            except Exception as e:
                logger.error(f"Errore nel loop principale: {str(e)}", exc_info=True)
                time.sleep(5)

    def _check_broker_health(self) -> None:
        """Verifica lo stato di salute di tutti i broker"""
        active_brokers = self.broker_manager.get_active_connections()
        total_brokers = len(self.broker_configs)
        
        logger.info(f"💓 Health check: {len(active_brokers)}/{total_brokers} broker attivi")
        
        for broker_name in [config.name for config in self.broker_configs]:
            if broker_name not in active_brokers:
                logger.warning(f"⚠️ {broker_name} non disponibile")

    def _monitor_all_positions(self) -> None:
        """Monitora posizioni su tutti i broker"""
        try:
            all_positions = self.broker_manager.get_aggregated_positions()
            
            total_positions = sum(len(positions) for positions in all_positions.values())
            
            if total_positions > 0:
                logger.debug(f"📊 Posizioni attive: {total_positions} totali")
                
                for broker_name, positions in all_positions.items():
                    if positions:
                        logger.debug(f"   {broker_name}: {len(positions)} posizioni")
                        
                        # Monitora ogni posizione
                        for position in positions:
                            self._monitor_single_position(broker_name, position)
                            
        except Exception as e:
            logger.error(f"Errore monitoring posizioni: {str(e)}")

    def _monitor_single_position(self, broker_name: str, position) -> None:
        """Monitora una singola posizione"""
        try:
            connection = self.broker_manager.get_connection(broker_name)
            if not connection:
                return
                
            # Ottieni prezzo corrente
            symbol_info = connection.get_symbol_info(position.symbol)
            if not symbol_info:
                return
                
            current_price = symbol_info.ask if position.type == 0 else symbol_info.bid
            
            # Calcola P/L corrente
            if position.type == 0:  # BUY
                pnl = (current_price - position.price_open) * position.volume
            else:  # SELL  
                pnl = (position.price_open - current_price) * position.volume
                
            # Log posizioni in perdita significativa
            if pnl < -100:  # Perdita > $100
                logger.warning(f"⚠️ {broker_name} - {position.symbol} P/L: ${pnl:.2f}")
                
        except Exception as e:
            logger.error(f"Errore monitoring posizione {position.ticket}: {str(e)}")

    def _update_global_metrics(self) -> None:
        """Aggiorna metriche globali aggregate"""
        try:
            status_report = self.broker_manager.get_global_status_report()
            
            logger.info(f"📈 METRICHE GLOBALI:")
            logger.info(f"   Balance totale: ${status_report['total_balance']:.2f}")
            logger.info(f"   Equity totale: ${status_report['total_equity']:.2f}")
            logger.info(f"   P/L totale: ${status_report['total_profit_loss']:.2f}")
            logger.info(f"   Broker attivi: {status_report['active_brokers']}/{status_report['total_brokers']}")
            
        except Exception as e:
            logger.error(f"Errore aggiornamento metriche: {str(e)}")

    def _process_all_brokers(self) -> None:
        """Processa segnali su tutti i broker attivi"""
        active_connections = self.broker_manager.get_active_connections()
        
        for broker_name, connection in active_connections.items():
            try:
                self._process_broker_symbols(broker_name, connection)
            except Exception as e:
                logger.error(f"Errore processing {broker_name}: {str(e)}")

    def _process_broker_symbols(self, broker_name: str, connection) -> None:
        """Processa simboli per un broker specifico"""
        try:
            engine = self.engines[broker_name]
            risk_manager = self.risk_managers[broker_name]
            
            # Simboli configurati per questo broker
            symbols = connection.config.symbols or []
            
            for symbol in symbols:
                # Verifica orari di trading
                if not is_trading_hours(symbol, self.main_config.config):
                    continue
                
                # Ottieni tick
                tick = connection.get_tick(symbol)
                if not tick:
                    continue
                
                # Processa tick nel engine
                mid_price = (tick.ask + tick.bid) / 2
                engine.process_tick(symbol, mid_price)
                
                # Verifica se possiamo tradare
                if not self._can_trade_symbol(broker_name, symbol):
                    continue
                
                # Ottieni segnale
                signal, price = engine.get_signal(symbol, for_trading=False)
                
                if signal in ["BUY", "SELL"]:
                    # Esegui trade se segnale valido
                    self._execute_broker_trade(broker_name, symbol, signal, tick, price)
                    
        except Exception as e:
            logger.error(f"Errore processing simboli {broker_name}: {str(e)}")

    def _can_trade_symbol(self, broker_name: str, symbol: str) -> bool:
        """Verifica se possiamo tradare un simbolo su un broker"""
        try:
            # Verifica engine
            engine = self.engines[broker_name]
            if not engine.can_trade(symbol):
                return False
            
            # Verifica posizioni esistenti per simbolo
            connection = self.broker_manager.get_connection(broker_name)
            existing_positions = connection.get_positions(symbol)
            if existing_positions:
                return False  # Una posizione per simbolo per broker
            
            # Verifica limite posizioni per broker
            all_positions = connection.get_positions()
            if len(all_positions) >= self.max_positions_per_broker:
                return False
            
            # Verifica limite posizioni globali
            global_positions = self.broker_manager.get_aggregated_positions()
            total_positions = sum(len(pos) for pos in global_positions.values())
            if total_positions >= self.max_total_positions:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Errore verifica trading {broker_name}/{symbol}: {str(e)}")
            return False

    def _execute_broker_trade(self, broker_name: str, symbol: str, signal: str, tick, price: float) -> bool:
        """Esegue un trade su un broker specifico"""
        try:
            logger.info(f"🎯 Segnale {signal} per {symbol} su {broker_name}")
            
            # Ottieni risk manager per broker
            risk_manager = self.risk_managers[broker_name]
            engine = self.engines[broker_name]
            
            # Calcola dimensione posizione
            position_size = risk_manager.calculate_position_size(symbol, price, signal)
            if position_size <= 0:
                logger.warning(f"⚠️ Size posizione non valida per {broker_name}/{symbol}")
                return False
            
            # Calcola livelli SL/TP
            order_type = 0 if signal == "BUY" else 1  # MT5 order types
            sl_price, tp_price = risk_manager.calculate_dynamic_levels(symbol, order_type, price)
            
            # Prepara richiesta ordine
            connection = self.broker_manager.get_connection(broker_name)
            symbol_info = connection.get_symbol_info(symbol)
            
            execution_price = symbol_info.ask if signal == "BUY" else symbol_info.bid
            
            request = {
                "action": 1,  # TRADE_ACTION_DEAL
                "symbol": symbol,
                "volume": position_size,
                "type": order_type,
                "price": execution_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 10,
                "magic": connection.config.magic_base,
                "comment": f"QTS-{broker_name}",
                "type_time": 0,  # GTC
                "type_filling": 2,  # FOK
            }
            
            # Esegui ordine
            result = connection.send_order(request)
            
            if result and result.retcode == 0:  # TRADE_RETCODE_DONE
                # Attiva cooldown
                engine.get_signal(symbol, for_trading=True)
                
                # Aggiorna metriche
                self._update_trade_metrics(broker_name, symbol, True, 0.0)
                
                logger.info(f"✅ Trade {signal} {symbol} eseguito su {broker_name}")
                logger.info(f"   Size: {position_size} | Price: {execution_price}")
                logger.info(f"   SL: {sl_price:.5f} | TP: {tp_price:.5f}")
                logger.info(f"   Ticket: {result.order}")
                
                return True
            else:
                logger.error(f"❌ Trade {signal} {symbol} fallito su {broker_name}: {result.retcode if result else 'No result'}")
                return False
                
        except Exception as e:
            logger.error(f"Errore esecuzione trade {broker_name}/{symbol}: {str(e)}", exc_info=True)
            return False

    def _update_trade_metrics(self, broker_name: str, symbol: str, success: bool, profit: float) -> None:
        """Aggiorna metriche per broker e globali"""
        try:
            with self.metrics_lock:
                # Metriche globali
                if success:
                    self.global_metrics.update_trade(symbol, profit)
                
                # Metriche per broker
                if broker_name in self.broker_metrics:
                    self.broker_metrics[broker_name].update_trade(symbol, profit)
                
                # Contatori
                self.trade_count[symbol] += 1
                self.broker_trade_count[broker_name][symbol] += 1
                
                logger.debug(f"📊 Metriche aggiornate: {broker_name}/{symbol}")
                
        except Exception as e:
            logger.error(f"Errore aggiornamento metriche: {str(e)}")

    def get_global_status(self) -> Dict:
        """Ottiene stato completo del sistema multi-broker"""
        try:
            broker_status = self.broker_manager.get_global_status_report()
            
            # Aggiungi statistiche trading
            broker_status['trading_stats'] = {
                'total_trades': sum(self.trade_count.values()),
                'trades_per_broker': dict(self.broker_trade_count),
                'trades_per_symbol': dict(self.trade_count)
            }
            
            # Aggiungi metriche performance
            global_summary = self.global_metrics.get_summary()
            broker_status['performance'] = global_summary
            
            # Aggiungi performance per broker
            broker_status['broker_performance'] = {}
            for broker_name, metrics in self.broker_metrics.items():
                broker_status['broker_performance'][broker_name] = metrics.get_summary()
            
            return broker_status
            
        except Exception as e:
            logger.error(f"Errore status report: {str(e)}")
            return {}

    def force_close_all_positions(self) -> None:
        """Chiude forzatamente tutte le posizioni su tutti i broker"""
        logger.warning("🚨 CHIUSURA FORZATA DI TUTTE LE POSIZIONI")
        
        results = self.broker_manager.close_all_positions()
        
        total_closed = sum(results.values())
        logger.info(f"✅ Chiuse {total_closed} posizioni totali")
        
        for broker_name, count in results.items():
            if count > 0:
                logger.info(f"   {broker_name}: {count} posizioni chiuse")

    def get_best_broker_for_trade(self, symbol: str, signal: str) -> Optional[str]:
        """
        Trova il miglior broker per eseguire un trade
        
        Args:
            symbol: Simbolo da tradare
            signal: Tipo di segnale (BUY/SELL)
            
        Returns:
            Nome del miglior broker o None
        """
        try:
            # 1. Trova broker che supportano il simbolo
            suitable_brokers = []
            
            for broker_name, connection in self.broker_manager.get_active_connections().items():
                if (connection.config.symbols and 
                    symbol in connection.config.symbols and
                    self._can_trade_symbol(broker_name, symbol)):
                    suitable_brokers.append(broker_name)
            
            if not suitable_brokers:
                return None
            
            # 2. Se solo uno disponibile, usalo
            if len(suitable_brokers) == 1:
                return suitable_brokers[0]
            
            # 3. Trova miglior spread
            best_broker = self.broker_manager.get_best_broker_for_symbol(symbol)
            if best_broker in suitable_brokers:
                return best_broker
            
            # 4. Fallback al primo disponibile
            return suitable_brokers[0]
            
        except Exception as e:
            logger.error(f"Errore selezione broker per {symbol}: {str(e)}")
            return None
