"""
BrokerManager - Orchestratore centrale per gestire multipli broker MT5
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from .connection import BrokerConnection, BrokerConfig, BrokerStatus

logger = logging.getLogger('QuantumTradingSystem')


class BrokerManager:
    """
    Manager centrale che gestisce multiple connessioni broker MT5
    Coordina The5ers, FTMO e altri broker simultaneamente
    """
    
    def __init__(self, broker_configs: List[BrokerConfig]):
        """
        Inizializza il manager con le configurazioni dei broker
        
        Args:
            broker_configs: Lista delle configurazioni broker
        """
        self.broker_configs = {config.name: config for config in broker_configs}
        self.connections: Dict[str, BrokerConnection] = {}
        self.connection_lock = threading.Lock()
        
        # Thread pool per operazioni parallele
        self.executor = ThreadPoolExecutor(max_workers=len(broker_configs) + 2)
        
        # Statistiche globali
        self.global_stats = {
            'total_brokers': len(broker_configs),
            'connected_brokers': 0,
            'total_trades': 0,
            'total_profit': 0.0,
            'broker_profits': defaultdict(float)
        }
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitor_thread = None
        
        logger.info(f"🏢 BrokerManager inizializzato con {len(broker_configs)} broker")
        for config in broker_configs:
            logger.info(f"   📊 {config.name}: {config.server} ({len(config.symbols or [])} simboli)")

    def initialize_all_connections(self) -> Dict[str, bool]:
        """
        Inizializza tutte le connessioni broker in parallelo
        
        Returns:
            Dizionario con risultati connessione per broker
        """
        logger.info("🚀 Inizializzazione connessioni broker...")
        
        # Crea le connessioni
        for name, config in self.broker_configs.items():
            self.connections[name] = BrokerConnection(config)
        
        # Connetti in parallelo
        connection_results = {}
        futures = {}
        
        for name, connection in self.connections.items():
            future = self.executor.submit(connection.connect)
            futures[future] = name
            
        # Attendi risultati
        for future in as_completed(futures):
            broker_name = futures[future]
            try:
                success = future.result(timeout=60)  # Timeout 60s per connessione
                connection_results[broker_name] = success
                
                if success:
                    self.global_stats['connected_brokers'] += 1
                    logger.info(f"✅ {broker_name} connesso con successo")
                else:
                    logger.error(f"❌ {broker_name} connessione fallita")
                    
            except Exception as e:
                connection_results[broker_name] = False
                logger.error(f"❌ Eccezione connessione {broker_name}: {str(e)}")
        
        # Report finale
        connected = sum(1 for success in connection_results.values() if success)
        total = len(connection_results)
        
        logger.info(f"📊 Connessioni completate: {connected}/{total}")
        
        # Avvia monitoring se ci sono connessioni attive
        if connected > 0:
            self.start_monitoring()
            
        return connection_results

    def start_monitoring(self) -> None:
        """Avvia il thread di monitoring delle connessioni"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 Monitoring connessioni avviato")

    def stop_monitoring(self) -> None:
        """Ferma il monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Monitoring connessioni fermato")

    def _monitor_connections(self) -> None:
        """Thread di monitoring per riconnessioni automatiche"""
        while self.monitoring_active:
            try:
                with self.connection_lock:
                    for name, connection in self.connections.items():
                        if not connection.is_connected():
                            logger.warning(f"⚠️ {name} disconnesso - Tentativo riconnessione")
                            
                            # Riconnessione in background
                            self.executor.submit(connection.auto_reconnect)
                
                # Update statistiche
                self._update_global_stats()
                
                time.sleep(30)  # Check ogni 30 secondi
                
            except Exception as e:
                logger.error(f"Errore monitoring: {str(e)}")
                time.sleep(60)

    def _update_global_stats(self) -> None:
        """Aggiorna statistiche globali"""
        connected = 0
        for connection in self.connections.values():
            if connection.is_connected():
                connected += 1
                
        self.global_stats['connected_brokers'] = connected

    def get_connection(self, broker_name: str) -> Optional[BrokerConnection]:
        """
        Ottiene la connessione per un broker specifico
        
        Args:
            broker_name: Nome del broker
            
        Returns:
            BrokerConnection o None se non trovato
        """
        return self.connections.get(broker_name)

    def get_active_connections(self) -> Dict[str, BrokerConnection]:
        """
        Ottiene tutte le connessioni attive
        
        Returns:
            Dizionario con connessioni attive
        """
        active = {}
        for name, connection in self.connections.items():
            if connection.is_connected():
                active[name] = connection
        return active

    def execute_on_broker(self, broker_name: str, symbol: str, request: Dict) -> Optional[Any]:
        """
        Esegue un ordine su un broker specifico
        
        Args:
            broker_name: Nome del broker
            symbol: Simbolo da tradare
            request: Richiesta ordine
            
        Returns:
            Risultato ordine o None
        """
        connection = self.get_connection(broker_name)
        if not connection or not connection.is_connected():
            logger.error(f"❌ Broker {broker_name} non disponibile per {symbol}")
            return None
            
        return connection.send_order(request)

    def execute_on_all_brokers(self, symbol: str, request_template: Dict) -> Dict[str, Any]:
        """
        Esegue lo stesso ordine su tutti i broker attivi che supportano il simbolo
        
        Args:
            symbol: Simbolo da tradare
            request_template: Template della richiesta ordine
            
        Returns:
            Dizionario con risultati per broker
        """
        results = {}
        futures = {}
        
        for name, connection in self.get_active_connections().items():
            # Verifica se il broker supporta il simbolo
            if (connection.config.symbols and 
                symbol not in connection.config.symbols):
                continue
                
            # Crea richiesta broker-specifica
            request = request_template.copy()
            request['magic'] = connection.config.magic_base
            
            # Esegui in parallelo
            future = self.executor.submit(connection.send_order, request)
            futures[future] = name
            
        # Raccogli risultati
        for future in as_completed(futures):
            broker_name = futures[future]
            try:
                result = future.result(timeout=10)
                results[broker_name] = result
                
                if result and result.retcode == 0:  # MT5.TRADE_RETCODE_DONE
                    logger.info(f"✅ {broker_name} - Ordine {symbol} eseguito")
                else:
                    logger.warning(f"⚠️ {broker_name} - Ordine {symbol} fallito")
                    
            except Exception as e:
                results[broker_name] = None
                logger.error(f"❌ {broker_name} - Eccezione ordine {symbol}: {str(e)}")
                
        return results

    def get_best_broker_for_symbol(self, symbol: str) -> Optional[str]:
        """
        Trova il miglior broker per un simbolo basato su spread e liquidità
        
        Args:
            symbol: Simbolo da analizzare
            
        Returns:
            Nome del miglior broker o None
        """
        best_broker = None
        best_spread = float('inf')
        
        for name, connection in self.get_active_connections().items():
            # Verifica supporto simbolo
            if (connection.config.symbols and 
                symbol not in connection.config.symbols):
                continue
                
            # Ottieni spread corrente
            tick = connection.get_tick(symbol)
            if not tick:
                continue
                
            spread = tick.ask - tick.bid
            
            if spread < best_spread:
                best_spread = spread
                best_broker = name
                
        if best_broker:
            logger.debug(f"💰 Miglior broker per {symbol}: {best_broker} (spread: {best_spread:.5f})")
            
        return best_broker

    def get_aggregated_positions(self) -> Dict[str, List]:
        """
        Ottiene tutte le posizioni da tutti i broker
        
        Returns:
            Dizionario con posizioni per broker
        """
        all_positions = {}
        
        for name, connection in self.get_active_connections().items():
            positions = connection.get_positions()
            all_positions[name] = positions
            
        return all_positions

    def get_total_exposure(self, symbol: str) -> Dict[str, float]:
        """
        Calcola l'esposizione totale per un simbolo su tutti i broker
        
        Args:
            symbol: Simbolo da analizzare
            
        Returns:
            Dizionario con esposizione per broker e totale
        """
        exposure = {'total_long': 0.0, 'total_short': 0.0, 'brokers': {}}
        
        for name, connection in self.get_active_connections().items():
            positions = connection.get_positions(symbol)
            broker_long = broker_short = 0.0
            
            for pos in positions:
                if pos.type == 0:  # BUY
                    broker_long += pos.volume
                else:  # SELL
                    broker_short += pos.volume
                    
            exposure['brokers'][name] = {
                'long': broker_long,
                'short': broker_short,
                'net': broker_long - broker_short
            }
            
            exposure['total_long'] += broker_long
            exposure['total_short'] += broker_short
            
        exposure['net_exposure'] = exposure['total_long'] - exposure['total_short']
        
        return exposure

    def close_all_positions(self, symbol: Optional[str] = None) -> Dict[str, int]:
        """
        Chiude tutte le posizioni su tutti i broker
        
        Args:
            symbol: Simbolo specifico (opzionale, altrimenti tutti)
            
        Returns:
            Dizionario con numero posizioni chiuse per broker
        """
        results = {}
        
        for name, connection in self.get_active_connections().items():
            positions = connection.get_positions(symbol)
            closed_count = 0
            
            for pos in positions:
                try:
                    # Crea richiesta di chiusura
                    symbol_info = connection.get_symbol_info(pos.symbol)
                    if not symbol_info:
                        continue
                        
                    close_request = {
                        "action": 1,  # TRADE_ACTION_DEAL
                        "symbol": pos.symbol,
                        "volume": pos.volume,
                        "type": 1 if pos.type == 0 else 0,  # Opposto
                        "position": pos.ticket,
                        "price": symbol_info.ask if pos.type == 0 else symbol_info.bid,
                        "deviation": 10,
                        "magic": connection.config.magic_base,
                        "comment": "QTS-CLOSE-ALL",
                        "type_time": 0,  # GTC
                        "type_filling": 2,  # FOK
                    }
                    
                    result = connection.send_order(close_request)
                    if result and result.retcode == 0:
                        closed_count += 1
                        
                except Exception as e:
                    logger.error(f"Errore chiusura posizione {pos.ticket} su {name}: {str(e)}")
                    
            results[name] = closed_count
            logger.info(f"📊 {name}: {closed_count} posizioni chiuse")
            
        return results

    def get_global_status_report(self) -> Dict:
        """
        Genera report completo dello stato di tutti i broker
        
        Returns:
            Report dettagliato con stato e statistiche
        """
        broker_reports = {}
        
        for name, connection in self.connections.items():
            broker_reports[name] = connection.get_status_report()
            
        # Aggrega statistiche
        total_balance = sum(
            report.get('balance', 0) 
            for report in broker_reports.values() 
            if report.get('status') == 'connected'
        )
        
        total_equity = sum(
            report.get('equity', 0) 
            for report in broker_reports.values() 
            if report.get('status') == 'connected'
        )
        
        return {
            'timestamp': time.time(),
            'global_stats': self.global_stats,
            'total_balance': total_balance,
            'total_equity': total_equity,
            'total_profit_loss': total_equity - total_balance,
            'broker_reports': broker_reports,
            'active_brokers': len(self.get_active_connections()),
            'total_brokers': len(self.connections)
        }

    def shutdown_all(self) -> None:
        """Chiude tutte le connessioni e ferma il manager"""
        logger.info("🛑 Shutdown di tutti i broker...")
        
        # Ferma monitoring
        self.stop_monitoring()
        
        # Disconnetti tutti i broker
        for name, connection in self.connections.items():
            try:
                connection.disconnect()
                logger.info(f"✅ {name} disconnesso")
            except Exception as e:
                logger.error(f"Errore disconnessione {name}: {str(e)}")
                
        # Shutdown executor
        self.executor.shutdown(wait=True, timeout=30)
        
        logger.info("✅ BrokerManager shutdown completato")
