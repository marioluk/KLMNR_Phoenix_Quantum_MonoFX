"""
BrokerConnection - Gestione singola connessione broker con MT5
"""

import MetaTrader5 as mt5
import time
import logging
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger('QuantumTradingSystem')


class BrokerStatus(Enum):
    """Stati possibili di una connessione broker"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class BrokerConfig:
    """Configurazione per un singolo broker"""
    name: str
    mt5_path: str
    login: int
    password: str
    server: str
    port: int = 18889
    timeout: int = 60000
    max_reconnect_attempts: int = 3
    reconnect_delay: int = 30
    symbols: List[str] = None
    account_currency: str = "USD"
    magic_base: int = 100000  # Base per magic numbers


class BrokerConnection:
    """
    Gestisce una singola connessione a un broker MT5
    Ogni broker ha la sua istanza MT5 separata
    """
    
    def __init__(self, broker_config: BrokerConfig):
        """
        Inizializza la connessione al broker
        
        Args:
            broker_config: Configurazione del broker
        """
        self.config = broker_config
        self.status = BrokerStatus.DISCONNECTED
        self.last_connection_attempt = 0
        self.reconnect_attempts = 0
        self.account_info = None
        self.last_error = None
        
        # Statistiche connessione
        self.connection_stats = {
            'total_connections': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'last_connected': None,
            'uptime_seconds': 0
        }
        
        logger.info(f"Inizializzato BrokerConnection per {self.config.name}")

    def connect(self) -> bool:
        """
        Stabilisce connessione con il broker MT5
        
        Returns:
            True se connesso con successo, False altrimenti
        """
        try:
            self.status = BrokerStatus.CONNECTING
            self.last_connection_attempt = time.time()
            
            logger.info(f"🔗 Connessione a {self.config.name}...")
            
            # Shutdown precedente per sicurezza
            mt5.shutdown()
            
            # Tentativo di connessione
            success = mt5.initialize(
                path=self.config.mt5_path,
                login=self.config.login,
                password=self.config.password,
                server=self.config.server,
                timeout=self.config.timeout,
                port=self.config.port
            )
            
            if success:
                # Verifica account info
                self.account_info = mt5.account_info()
                if self.account_info:
                    self.status = BrokerStatus.CONNECTED
                    self.reconnect_attempts = 0
                    self.connection_stats['successful_connections'] += 1
                    self.connection_stats['last_connected'] = time.time()
                    
                    logger.info(f"✅ {self.config.name} connesso - Account: {self.account_info.login}")
                    logger.info(f"   Server: {self.account_info.server}")
                    logger.info(f"   Balance: {self.account_info.balance:.2f} {self.config.account_currency}")
                    
                    # Attiva simboli se specificati
                    if self.config.symbols:
                        self._activate_symbols()
                    
                    return True
                else:
                    self.status = BrokerStatus.ERROR
                    self.last_error = "Account info non disponibile"
            else:
                error = mt5.last_error()
                self.status = BrokerStatus.ERROR
                self.last_error = f"Errore MT5: {error}"
                self.connection_stats['failed_connections'] += 1
                
            self.reconnect_attempts += 1
            logger.error(f"❌ Connessione {self.config.name} fallita: {self.last_error}")
            return False
            
        except Exception as e:
            self.status = BrokerStatus.ERROR
            self.last_error = str(e)
            self.reconnect_attempts += 1
            logger.error(f"❌ Eccezione connessione {self.config.name}: {str(e)}")
            return False
        finally:
            self.connection_stats['total_connections'] += 1

    def disconnect(self) -> None:
        """Disconnette dal broker"""
        try:
            if self.status == BrokerStatus.CONNECTED:
                mt5.shutdown()
                logger.info(f"🔌 {self.config.name} disconnesso")
            self.status = BrokerStatus.DISCONNECTED
        except Exception as e:
            logger.error(f"Errore disconnessione {self.config.name}: {str(e)}")

    def is_connected(self) -> bool:
        """
        Verifica se la connessione è attiva
        
        Returns:
            True se connesso e funzionante
        """
        try:
            if self.status != BrokerStatus.CONNECTED:
                return False
                
            # Test rapido con account info
            account = mt5.account_info()
            if account is None:
                logger.warning(f"⚠️ {self.config.name} - Account info persa")
                self.status = BrokerStatus.ERROR
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Errore verifica connessione {self.config.name}: {str(e)}")
            self.status = BrokerStatus.ERROR
            return False

    def auto_reconnect(self) -> bool:
        """
        Tentativo automatico di riconnessione
        
        Returns:
            True se riconnesso con successo
        """
        if self.reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.warning(f"🚫 {self.config.name} - Max tentativi riconnessione raggiunti")
            return False
            
        time_since_last = time.time() - self.last_connection_attempt
        if time_since_last < self.config.reconnect_delay:
            return False
            
        logger.info(f"🔄 {self.config.name} - Tentativo riconnessione {self.reconnect_attempts + 1}")
        return self.connect()

    def _activate_symbols(self) -> None:
        """Attiva i simboli specifici del broker"""
        try:
            activated = 0
            for symbol in self.config.symbols:
                if mt5.symbol_select(symbol, True):
                    activated += 1
                    logger.debug(f"✅ {symbol} attivato su {self.config.name}")
                else:
                    logger.warning(f"⚠️ Impossibile attivare {symbol} su {self.config.name}")
                    
            logger.info(f"📊 {self.config.name} - {activated}/{len(self.config.symbols)} simboli attivati")
            
        except Exception as e:
            logger.error(f"Errore attivazione simboli {self.config.name}: {str(e)}")

    def get_positions(self, symbol: Optional[str] = None) -> List:
        """
        Ottiene le posizioni aperte
        
        Args:
            symbol: Simbolo specifico (opzionale)
            
        Returns:
            Lista delle posizioni
        """
        try:
            if not self.is_connected():
                return []
                
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()
                
            return list(positions) if positions else []
            
        except Exception as e:
            logger.error(f"Errore recupero posizioni {self.config.name}: {str(e)}")
            return []

    def get_symbol_info(self, symbol: str) -> Optional[Any]:
        """
        Ottiene informazioni su un simbolo
        
        Args:
            symbol: Nome del simbolo
            
        Returns:
            Info simbolo o None
        """
        try:
            if not self.is_connected():
                return None
            return mt5.symbol_info(symbol)
        except Exception as e:
            logger.error(f"Errore info simbolo {symbol} su {self.config.name}: {str(e)}")
            return None

    def get_tick(self, symbol: str) -> Optional[Any]:
        """
        Ottiene l'ultimo tick per un simbolo
        
        Args:
            symbol: Nome del simbolo
            
        Returns:
            Tick info o None
        """
        try:
            if not self.is_connected():
                return None
            return mt5.symbol_info_tick(symbol)
        except Exception as e:
            logger.error(f"Errore tick {symbol} su {self.config.name}: {str(e)}")
            return None

    def send_order(self, request: Dict) -> Optional[Any]:
        """
        Invia un ordine al broker
        
        Args:
            request: Richiesta ordine MT5
            
        Returns:
            Risultato ordine o None
        """
        try:
            if not self.is_connected():
                logger.error(f"❌ {self.config.name} non connesso per ordine")
                return None
                
            # Aggiungi magic number broker-specifico se non presente
            if 'magic' not in request:
                request['magic'] = self.config.magic_base
                
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Ordine {self.config.name} eseguito - Ticket: {result.order}")
            else:
                logger.error(f"❌ Ordine {self.config.name} fallito: {result.retcode if result else 'No result'}")
                
            return result
            
        except Exception as e:
            logger.error(f"Errore invio ordine {self.config.name}: {str(e)}")
            return None

    def get_account_info(self) -> Optional[Any]:
        """
        Ottiene informazioni account aggiornate
        
        Returns:
            Account info o None
        """
        try:
            if not self.is_connected():
                return None
            self.account_info = mt5.account_info()
            return self.account_info
        except Exception as e:
            logger.error(f"Errore account info {self.config.name}: {str(e)}")
            return None

    def get_status_report(self) -> Dict:
        """
        Genera report dello stato della connessione
        
        Returns:
            Dizionario con stato e statistiche
        """
        uptime = 0
        if (self.status == BrokerStatus.CONNECTED and 
            self.connection_stats['last_connected']):
            uptime = time.time() - self.connection_stats['last_connected']
            
        return {
            'broker': self.config.name,
            'status': self.status.value,
            'last_error': self.last_error,
            'reconnect_attempts': self.reconnect_attempts,
            'account_login': self.account_info.login if self.account_info else None,
            'server': self.config.server,
            'balance': self.account_info.balance if self.account_info else 0,
            'equity': self.account_info.equity if self.account_info else 0,
            'currency': self.config.account_currency,
            'uptime_minutes': uptime / 60,
            'connection_stats': self.connection_stats,
            'symbols_count': len(self.config.symbols) if self.config.symbols else 0
        }
