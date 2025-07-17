# ====================================================================================
# QUANTUM TICK SYSTEM - MILESTONE EDITION (REV 6.0) PRODUZIONE
# Sistema di trading algoritmico basato su entropia, stati quantistici e risk management avanzato
# ====================================================================================

import MetaTrader5 as mt5
import numpy as np
import json
import logging
import time
from datetime import datetime, time as dt_time, timedelta  # <-- AGGIUNTO timedelta
from typing import Dict, Tuple, List, Any
from collections import deque, defaultdict
from threading import Lock
from logging.handlers import RotatingFileHandler
import os
import sys
from functools import lru_cache


# Configurazioni globali
CONFIG_FILE = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json"

# Carica la configurazione JSON all'avvio
def load_config(config_path=CONFIG_FILE):
    with open(config_path) as f:
        return json.load(f)

config = load_config()

# Ora puoi ottenere il percorso del log dal JSON
LOG_FILE = config["logging"]["log_file"]


# -----------------------------------------------------------
# SEZIONE LOGGING
# -----------------------------------------------------------

def setup_logger(config_path=CONFIG_FILE):
    """Configura il sistema di logging"""
    logger = logging.getLogger('QuantumTradingSystem')
    
    if logger.handlers:
        return logger

    # Carica la configurazione
    with open(config_path) as f:
        config = json.load(f)
    
    log_config = config.get('logging', {})
    
    # Crea la directory dei log se non esiste
    log_dir = os.path.dirname(log_config.get('log_file', 'logs/default.log'))
    os.makedirs(log_dir, exist_ok=True)

    # Formattazione
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler con rotazione
    file_handler = RotatingFileHandler(
        log_config.get('log_file', LOG_FILE),
        maxBytes=log_config.get('max_size_mb', 10)*1024*1024,
        backupCount=log_config.get('backup_count', 5),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))

    # Console Handler (mostra tutto da INFO in su)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))
    console_handler.setFormatter(formatter)

    # Configurazione finale
    logger.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger

def clean_old_logs(log_file=LOG_FILE, max_backups=5):
    """Pulizia dei vecchi file di log"""
    try:
        for i in range(max_backups + 1, 10):
            fname = f"{log_file}.{i}"
            if os.path.exists(fname):
                os.remove(fname)
    except Exception as e:
        print(f"Pulizia log fallita: {str(e)}")

logger = setup_logger()
clean_old_logs()

# -----------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------

def parse_time(time_str: str) -> Tuple[dt_time, dt_time]:
    """Converte una stringa 'HH:MM-HH:MM' in due oggetti time"""
    try:
        if isinstance(time_str, list):  # Se già parsato
            return time_str[0], time_str[1]
            
        if "-" not in time_str:  # Formato singolo
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            return time_obj, time_obj
            
        start_str, end_str = time_str.split('-')
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        return start, end
        
    except ValueError as e:
        logger.error(f"Formato orario non valido: {time_str} | Errore: {str(e)}")
        return dt_time(0, 0), dt_time(23, 59)  # Default 24h

def is_trading_hours(symbol: str, config: Dict) -> bool:
    """Versione compatibile con sessioni multiple"""
    try:
        symbol_config = config.get('symbols', {}).get(symbol, {})
        trading_hours = symbol_config.get('trading_hours', ["00:00-24:00"])
        now = datetime.now().time()
        
        for time_range in trading_hours:
            if isinstance(time_range, str):  # Formato legacy "HH:MM-HH:MM"
                start, end = parse_time(time_range)
                if start <= end:
                    if start <= now <= end:
                        return True
                else:  # Overnight (es. 22:00-02:00)
                    if now >= start or now <= end:
                        return True
                        
            elif isinstance(time_range, list):  # Nuovo formato ["HH:MM", "HH:MM"]
                start, end = parse_time("-".join(time_range))
                if start <= now <= end:
                    return True
                    
        return False
        
    except Exception as e:
        logger.error(f"Errore controllo orari {symbol}: {str(e)}")
        return True  # Fallback: assume sempre trading
        
# -----------------------------------------------------------
# CLASSI CORE DEL SISTEMA
# -----------------------------------------------------------

""" 
1- ConfigManager - La prima classe necessaria, carica e gestisce la configurazione del sistema da file JSON.
"""
class ConfigManager:
    def __init__(self, config_path: str):
        if isinstance(config_path, dict):
            self._config = config_path
        else:
            self._config = self._load_config(config_path)
        
        # Aggiungi la validazione durante l'inizializzazione
        self._validate_config()
        
        self.symbols = list(self._config.get('symbols', {}).keys())

    def _validate_config(self):
        """Valida la struttura base del file di configurazione"""
        required_sections = ['symbols', 'risk_parameters']
        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"Sezione {section} mancante nella configurazione")
        
        # Validazione aggiuntiva per i simboli
        if not isinstance(self._config['symbols'], dict) or len(self._config['symbols']) == 0:
            raise ValueError("Sezione symbols deve contenere almeno un simbolo configurato")
        
        # Validazione parametri di rischio
        risk_params = self._config.get('risk_parameters', {})
        if not isinstance(risk_params, dict):
            raise ValueError("Sezione risk_parameters deve essere un dizionario")
    
        
    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                # Normalizza la struttura della configurazione
                return self._normalize_config(config)
        except Exception as e:
            logger.error(f"Errore nel caricamento del config: {str(e)}", exc_info=True)
            raise
    
    def _normalize_config(self, config: Dict) -> Dict:
        """Normalizza la struttura della configurazione per gestire le duplicazioni"""
        # Unisci risk_parameters e risk_management
        if 'risk_management' in config and 'risk_parameters' in config:
            config['risk_parameters'].update(config['risk_management'])
            del config['risk_management']
        
        # Sposta le impostazioni di trailing stop da features a risk_parameters
        if 'features' in config and 'trailing_stop' in config['features']:
            if 'trailing_stop' not in config['risk_parameters']:
                config['risk_parameters']['trailing_stop'] = {}
            config['risk_parameters']['trailing_stop'].update(
                config['features']['trailing_stop'])
        
        return config
        
    @property
    def config(self):
        return self._config
        
    def get(self, key: str, default=None):
        return self._config.get(key, default)
        
   
    def get_risk_params(self, symbol: str = None) -> Dict:
        """Versione semplificata che unisce risk_parameters e risk_management"""
        base = self.config.get('risk_parameters', {})
        if not symbol:
            return base
            
        symbol_config = self.config.get('symbols', {}).get(symbol, {}).get('risk_management', {})
        trailing_base = base.get('trailing_stop', {})
        trailing_symbol = symbol_config.get('trailing_stop', {})
        
        return {
            **base,
            **symbol_config,
            'trailing_stop': {
                **trailing_base,
                **trailing_symbol
            }
        }
        
    def _get_max_allowed_spread(self, symbol: str) -> float:
        """Restituisce lo spread massimo consentito per un simbolo"""
        try:
            DEFAULT_SPREADS = {
                'SP500': 10.0,
                'NAS100': 15.0,
                'XAUUSD': 30.0,
                'BTCUSD': 50.0,
                'ETHUSD': 40.0,
                'default': 20.0
            }
            
            # Accedi direttamente a self.config che è già un dict
            risk_params = self.config.get('risk_parameters', {})
            spread_config = risk_params.get('max_spread', {})
            
            if isinstance(spread_config, dict):
                symbol_spread = spread_config.get(symbol, spread_config.get('default', 'auto'))
            else:
                symbol_spread = spread_config
                
            if isinstance(symbol_spread, str):
                symbol_spread = symbol_spread.lower()
                if symbol_spread == 'adaptive':
                    volatility = self.calculate_quantum_volatility(symbol)
                    base_spread = DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default'])
                    return float(base_spread * volatility)
                elif symbol_spread == 'auto':
                    return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
            
            return float(symbol_spread)
            
        except Exception as e:
            logger.error(f"Errore determinazione spread per {symbol}: {str(e)}")
            return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
        
        
"""
2- QuantumEngine - Il motore principale che elabora i tick di mercato e genera segnali di trading 
basati sull'entropia e stati quantistici. Dipende dalla configurazione.
"""



class QuantumEngine:
    """
    1. Inizializzazione e Setup
    Costruttore della classe, carica i parametri di configurazione e inizializza buffer, cache e variabili di stato.
    """
    
    def __init__(self, config):
        """Initialize with either ConfigManager or dict"""
        if hasattr(config, 'get_risk_params'):  # It's a ConfigManager
            self._config_manager = config
            self._config = config.config
        else:  # It's a raw dict
            self._config_manager = None
            self._config = config

        self.tick_buffer = defaultdict(deque)
        self.position_cooldown = {}  # Traccia ultima chiusura per simbolo
        self.buffer_lock = Lock()    # <-- AGGIUNTO lock per thread safety

        # MODIFICA QUI - Parametri buffer ridotti per debug
        # Parametri configurabili
        quantum_params = self._config.get('quantum_params', {})
        self.buffer_size = quantum_params.get('buffer_size', 100)  # Era 250
        self.spin_window = quantum_params.get('spin_window', 20)   # Era 50
        self.min_spin_samples = quantum_params.get('min_spin_samples', 10)  # Era 20
        self.spin_threshold = quantum_params.get('spin_threshold', 0.25)
        self.signal_cooldown = quantum_params.get('signal_cooldown', 300)
    
        
        # Inizializza buffer per simboli
        for symbol in self._config.get('symbols', {}):
            self.tick_buffer[symbol] = deque(maxlen=self.buffer_size)
        
        # Cache con timeout
        self.last_signal_time = {}
        self._volatility_cache = {}
        self._spin_cache = {}
        self._cache_timeout = 60  # secondi
        
        self.last_warning_time = {}
        self.warning_cooldown = 300  # 5 minuti tra warning simili
        
       
        
        
    @property
    def config(self):
        """Property per accesso alla configurazione"""
        return self._config    
    
    def is_in_cooldown_period(self, symbol: str) -> bool:
        """Verifica se il simbolo è in un periodo di cooldown"""
        # 1. Controlla cooldown normale posizioni (1800s)
        last_close = self.position_cooldown.get(symbol, 0)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        if time.time() - last_close < position_cooldown:
            logger.debug(f"Cooldown normale attivo per {symbol} - {position_cooldown - (time.time() - last_close):.0f}s rimanenti")
            return True
            
        # 2. Controlla cooldown segnali (900s)
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.last_signal_time.get(symbol, 0)
        if time.time() - last_signal < signal_cooldown:
            logger.debug(f"Cooldown segnale attivo per {symbol} - {signal_cooldown - (time.time() - last_signal):.0f}s rimanenti")
            return True
    

    def can_trade(self, symbol: str) -> bool:
        """Verifica se è possibile aprire una nuova posizione con controlli completi"""
        # 1. Controlla cooldown
        if self.is_in_cooldown_period(symbol):
            return False
            
        # 2. Verifica spread
        try:
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.debug(f"Impossibile ottenere info simbolo {symbol}")
                return False
                
            current_spread = (symbol_info.ask - symbol_info.bid) / self._get_pip_size(symbol)
            max_spread = self.config.get('risk_parameters', {}).get('max_spread', {})
            
            if isinstance(max_spread, dict):
                max_allowed = max_spread.get(symbol, max_spread.get('default', 20))
            else:
                max_allowed = max_spread
                
            if current_spread > max_allowed:
                logger.debug(f"Spread {symbol} troppo alto: {current_spread:.1f}p > {max_allowed}p")
                return False
                
        except Exception as e:
            logger.error(f"Errore verifica spread {symbol}: {e}")
            return False
            
        # 3. Controlla numero massimo posizioni aperte
        positions = mt5.positions_get()
        if positions and len(positions) >= self.config.get('risk_parameters', {}).get('max_positions', 1):
            logger.debug(f"Massimo numero posizioni raggiunto: {len(positions)}")
            return False
            
        # 4. Controlla trades giornalieri
        today = datetime.now().date()
        try:
            # Conta i trades di oggi
            history = mt5.history_deals_get(
                datetime.combine(today, dt_time.min),
                datetime.combine(today, dt_time.max)
            )
            if history:
                today_trades = len([d for d in history if d.type in [0, 1]])  # Buy/Sell orders
                max_daily = self.config.get('risk_parameters', {}).get('max_daily_trades', 6)
                if today_trades >= max_daily:
                    logger.debug(f"Limite trades giornalieri raggiunto: {today_trades}/{max_daily}")
                    return False
        except Exception as e:
            logger.error(f"Errore controllo trades giornalieri: {e}")
            
        return True
        
    def record_trade_close(self, symbol: str):
        """Registra la chiusura solo se effettivamente avvenuta"""
        # Modificato per registrare solo chiusure reali
        if mt5.positions_get(symbol=symbol) is None or len(mt5.positions_get(symbol=symbol)) == 0:
            self.position_cooldown[symbol] = time.time()
            logger.debug(f"Cooldown registrato per {symbol} (1800s)")

        

    """
    2. Metodi di Calcolo Quantistico
    """
    @staticmethod
    @lru_cache(maxsize=1000)
    def calculate_entropy(deltas: Tuple[float]) -> float:
        """
        Calcola l'entropia normalizzata (tra 0 e 1) da una sequenza di delta di prezzo.
        Utilizza lru_cache per ottimizzare i calcoli ripetuti.
        """
        deltas_arr = np.array(deltas)
        abs_deltas = np.abs(deltas_arr)
        sum_abs_deltas = np.sum(abs_deltas) + 1e-10
        
        prob = abs_deltas / sum_abs_deltas
        valid_probs = prob[(prob > 0) & np.isfinite(prob)]
        
        if len(valid_probs) == 0:
            return 0.0
        
        entropy = -np.sum(valid_probs * np.log(valid_probs + 1e-10)) / np.log(len(valid_probs) + 1e-10)
        return float(np.clip(entropy, 0.0, 1.0))

    def calculate_spin(self, ticks: List[Dict]) -> Tuple[float, float]:
        """
        Calcola lo "spin quantistico" (bilanciamento direzionale dei tick) e la confidenza del segnale.
        Usa una finestra mobile (spin_window) e soglie configurabili (spin_threshold).
        
        Calcola lo spin quantistico e la confidenza del segnale.
        Versione come metodo d'istanza che usa la cache.
        """
        if not ticks or len(ticks) < self.min_spin_samples:
            return 0.0, 0.0
        
        # Chiave di cache corretta con parentesi chiuse
        cache_key = hash(tuple((t['price'], t['direction']) for t in ticks[-self.spin_window:]))
        
        return self._get_cached(
            self._spin_cache,
            cache_key,
            self._calculate_spin_impl,
            ticks[-self.spin_window:]
        )

    def _calculate_spin_impl(self, ticks: List[Dict]) -> Tuple[float, float]:
        """
        (metodo interno)
        Implementazione base del calcolo dello spin (senza cache).
        """
        if len(ticks) < 5:
            return 0.0, 0.0
            
        # Filtra i tick con direction valida (non zero)
        valid_ticks = [t for t in ticks if t.get('direction', 0) != 0]
        
        if len(valid_ticks) < 3:
            return 0.0, 0.0
            
        positive = sum(1 for t in valid_ticks if t.get('direction', 0) > 0)
        negative = sum(1 for t in valid_ticks if t.get('direction', 0) < 0)
        total = len(valid_ticks)
        
        # Calcolo spin bilanciato
        raw_spin = (positive - negative) / total
        
        # Confidence basata sulla deviazione dalla neutralità
        balance_deviation = abs(positive - negative) / total
        confidence = min(1.0, balance_deviation * np.sqrt(total))
        
        return raw_spin, confidence

    

    def calculate_quantum_volatility(self, symbol: str, window: int = 50) -> float:
        """
        Calcola una volatilità adattiva combinando entropia e spin.
        Usato per adattare dinamicamente stop-loss e take-profit.
        Calcola la volatilità quantistica con cache
        """
        def _calculate():
            ticks = list(self.tick_buffer.get(symbol, []))
            if len(ticks) < window:
                return 1.0

            deltas = np.array([t['delta'] for t in ticks[-window:]])
            prob_dist = np.abs(deltas) / (np.sum(np.abs(deltas)) + 1e-10)
            entropy = -np.sum(prob_dist * np.log(prob_dist + 1e-10)) / np.log(window)
            spin, _ = self._calculate_spin_impl(ticks)
            return 1 + abs(spin) * entropy

        return self._get_cached(self._volatility_cache, symbol, _calculate)
        
        
        
    """
    3. Gestione Tick e Segnali
    """

    def process_tick(self, symbol: str, price: float):

        """
        Aggiunge un nuovo tick al buffer circolare e calcola delta/direzione rispetto al tick precedente.
        Processa un nuovo tick di prezzo
        """
        if symbol not in self.tick_buffer:
            with self.buffer_lock:  # Usa il lock solo qui
                self.tick_buffer[symbol] = deque(maxlen=self.buffer_size)
            logger.info(f"Inizializzato buffer per {symbol}")
        
        if price <= 0:
            return
        
        # Logga il primo tick ricevuto
        if len(self.tick_buffer[symbol]) == 0:
            logger.info(f"Primo tick ricevuto per {symbol}: {price}")
        
        # Calcola delta e direzione
        if len(self.tick_buffer[symbol]) > 0:
            last_price = self.tick_buffer[symbol][-1]['price']
            delta = price - last_price
            direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
        else:
            delta = 0
            direction = 0  # Neutro invece di bias up
        
        self.tick_buffer[symbol].append({
            'price': price,
            'delta': delta,
            'direction': direction,
            'time': time.time()
        })

    def get_signal(self, symbol: str) -> Tuple[str, float]:
        """
        Genera un segnale di trading ("BUY"/"SELL"/"HOLD") basato su:
        - Entropia dei tick recenti
        - Spin e confidenza
        - Soglie adattive (entropy_thresholds dalla configurazione)
        
        Versione ottimizzata che:
        1. Mantiene tutti i tuoi parametri originali
        2. Gestisce correttamente il cooldown di 900s
        3. Aggiunge logging dettagliato
        4. Non modifica la logica del segnale
        
        Args:
            symbol: Simbolo da analizzare
            
        Returns:
            Tuple: (Segnale, Prezzo) - "BUY"/"SELL"/"HOLD"
        """
        ticks = list(self.tick_buffer.get(symbol, []))
        
        # 1. Verifica preliminare buffer
        if len(ticks) < self.min_spin_samples:
            logger.debug(f"{symbol}: Buffer insufficiente ({len(ticks)}/{self.min_spin_samples} ticks)")
            return "HOLD", 0.0

        # 2. Calcolo spin e confidenza
        spin_window = min(self.spin_window, len(ticks))
        recent_ticks = ticks[-spin_window:]
        spin, confidence = self.calculate_spin(recent_ticks)
        
        # 3. Filtri conservativi (tua logica originale)
        if confidence < 0.8:
            logger.debug(f"{symbol}: Confidence troppo bassa ({confidence:.2f}/0.8)")
            return "HOLD", 0.0
            
        # 4. Verifica cooldown segnali (900s)
        last_signal_time = self.last_signal_time.get(symbol, 0)
        if time.time() - last_signal_time < self.signal_cooldown:
            remaining = int(self.signal_cooldown - (time.time() - last_signal_time))
            logger.debug(f"{symbol}: In cooldown segnali ({remaining}s rimanenti)")
            return "HOLD", 0.0

        # 5. Calcolo metriche (tua logica originale invariata)
        deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10)
        entropy = self.calculate_entropy(deltas)
        volatility = 1 + abs(spin) * entropy
        
        thresholds = self.config.get('quantum_params', {}).get('entropy_thresholds', {})
        base_buy_thresh = thresholds.get('buy_signal', 0.55)
        base_sell_thresh = thresholds.get('sell_signal', 0.45)
        
        # Applica la volatilità in modo simmetrico
        buy_thresh = base_buy_thresh * (1 + (volatility - 1) * 0.5)
        sell_thresh = base_sell_thresh * (1 - (volatility - 1) * 0.5)

        # 6. Generazione segnale con logging simmetrico
        signal = "HOLD"
        
        # Log delle condizioni per debug
        buy_condition = entropy > buy_thresh and spin > self.spin_threshold * confidence
        sell_condition = entropy < sell_thresh and spin < -self.spin_threshold * confidence
        
        logger.debug(f"{symbol} Signal Analysis: "
                    f"E={entropy:.3f} S={spin:.3f} C={confidence:.3f} | "
                    f"BUY: E>{buy_thresh:.3f}? {entropy > buy_thresh} & S>{self.spin_threshold * confidence:.3f}? {spin > self.spin_threshold * confidence} = {buy_condition} | "
                    f"SELL: E<{sell_thresh:.3f}? {entropy < sell_thresh} & S<{-self.spin_threshold * confidence:.3f}? {spin < -self.spin_threshold * confidence} = {sell_condition}")
        
        if buy_condition:
            signal = "BUY"
        elif sell_condition:
            signal = "SELL"

        # 7. Registrazione segnale (senza influenzare cooldown posizioni)
        if signal != "HOLD":
            self.last_signal_time[symbol] = time.time()
            
            # Monitora bias direzionale
            if not hasattr(self, 'signal_stats'):
                self.signal_stats = {'BUY': 0, 'SELL': 0}
            self.signal_stats[signal] += 1
            
            buy_ratio = self.signal_stats['BUY'] / (self.signal_stats['BUY'] + self.signal_stats['SELL'])
            
            logger.info(
                f"Segnale {signal} per {symbol}: "
                f"E={entropy:.2f} S={spin:.2f} V={volatility:.2f} C={confidence:.2f} | "
                f"Soglie: B={buy_thresh:.2f} S={sell_thresh:.2f} | "
                f"Bias Check: BUY={self.signal_stats['BUY']} SELL={self.signal_stats['SELL']} Ratio={buy_ratio:.2f} | "
                f"Cooldown segnale attivato (900s)"
            )
            
            # Avviso se bias eccessivo
            if (self.signal_stats['BUY'] + self.signal_stats['SELL']) > 10:
                if buy_ratio > 0.8:
                    logger.warning(f"⚠️ BIAS LONG DETECTED: {buy_ratio:.1%} buy signals!")
                elif buy_ratio < 0.2:
                    logger.warning(f"⚠️ BIAS SHORT DETECTED: {buy_ratio:.1%} buy signals!")
            
            # Aggiungi logging esplicito per i segnali SELL
            if signal == "SELL":
                logger.debug(f"SELL signal conditions met for {symbol}: "
                            f"Entropy={entropy:.2f} < {sell_thresh:.2f} "
                            f"and Spin={spin:.2f} < {-self.spin_threshold*confidence:.2f}")
        
        return signal, recent_ticks[-1]['price'] if recent_ticks else 0.0
        
        
    """
    4. Controlli di Mercato e Connessione
    """
    
    def check_tick_activity(self):
        """Monitoraggio stato mercato e qualità dati con heartbeat."""
        current_time = time.time()
        issues = []
        warning_symbols = []
        heartbeat_data = []
        
        if not mt5.terminal_info().connected:
            logger.warning("Connessione MT5 non disponibile")
            return False

        for symbol in self._config_manager.symbols:  # Usa _config_manager invece di config_manager
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    issues.append(f"{symbol}: Nessun dato tick disponibile")
                    continue
                    
                symbol_info = mt5.symbol_info(symbol)
                spread = (symbol_info.ask - symbol_info.bid) / self._get_pip_size(symbol) if symbol_info else 0
                
                # Usa la STESSA finestra temporale di get_signal
                ticks = list(self.tick_buffer.get(symbol, []))[-self.spin_window:]
                
                if len(ticks) >= self.min_spin_samples:
                    # Calcoli IDENTICI a get_signal()
                    deltas = tuple(t['delta'] for t in ticks if abs(t['delta']) > 1e-10)
                    entropy = self.calculate_entropy(deltas)
                    spin = sum(1 for t in ticks if t['direction'] > 0) / len(ticks) * 2 - 1
                    confidence = min(1.0, abs(spin) * np.sqrt(len(ticks)))
                    volatility = 1 + abs(spin) * entropy
                else:
                    entropy, spin, confidence, volatility = 0.0, 0.0, 0.0, 1.0

                # Preparazione dati heartbeat
                state = {
                    'symbol': symbol,
                    'bid': tick.bid,
                    'ask': tick.ask,
                    'spread': spread,
                    'buffer_size': len(self.tick_buffer.get(symbol, [])),
                    'E': round(entropy, 2),
                    'S': round(spin, 2),
                    'C': round(confidence, 2),
                    'V': round(volatility, 2),
                    'timestamp': current_time
                }
                heartbeat_data.append(state)

                # Verifiche aggiuntive
                if is_trading_hours(symbol, self._config_manager.config):
                    max_spread = self._config_manager._get_max_allowed_spread(symbol)  # Corretto qui
                    if spread > max_spread:
                        issues.append(f"{symbol}: Spread {spread:.1f}p > max {max_spread:.1f}p")

                if len(self.tick_buffer.get(symbol, [])) < self.min_spin_samples:
                    warning_symbols.append(symbol)

            except Exception as e:
                logger.error(f"Errore monitoraggio {symbol}: {str(e)}", exc_info=True)

        # Logging consolidato
        if heartbeat_data:
            hb_msg = "HEARTBEAT:\n" + "\n".join(
                f"{d['symbol']}: Bid={d['bid']:.5f} | Ask={d['ask']:.5f} | "
                f"Spread={d['spread']:.1f}p | Buffer={d['buffer_size']} | "
                f"E={d['E']:.2f} | S={d['S']:.2f} | C={d['C']:.2f} | V={d['V']:.2f}"
                for d in heartbeat_data[:5]  # Limita a 5 simboli per leggibilità
            )
            logger.info(hb_msg)
            
            # Log sistema attivo
            positions_count = len(mt5.positions_get() or [])
            logger.info(f"Sistema attivo - Posizioni: {positions_count}/1")

        if warning_symbols:
            logger.warning(f"Buffer insufficiente: {', '.join(warning_symbols[:3])}")
        if issues:
            logger.warning(f"Problemi: {' | '.join(issues[:3])}")

        return True
        
        
    def get_remaining_cooldown(self, symbol: str) -> float:
        """Restituisce i secondi rimanenti di cooldown per un simbolo"""
        # 1. Controlla cooldown normale posizioni (1800s)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        last_close = self.position_cooldown.get(symbol, 0)
        position_remaining = max(0, position_cooldown - (time.time() - last_close))
        
        # 2. Controlla cooldown segnali (900s)
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.last_signal_time.get(symbol, 0)
        signal_remaining = max(0, signal_cooldown - (time.time() - last_signal))
        
        # Restituisce il cooldown più lungo rimanente
        return max(position_remaining, signal_remaining)
        
        
    """
    5. Utility e Cache
    """    
    
    def _get_cached(self, cache_dict, key, calculate_func, *args):
        """
        (metodo interno)
        Gestisce una cache con timeout per ottimizzare calcoli ripetuti (es. volatilità).
        Helper per gestire cache con timeout
        """
        now = time.time()
        if key in cache_dict:
            value, timestamp = cache_dict[key]
            if now - timestamp < self._cache_timeout:
                return value
        
        value = calculate_func(*args)
        cache_dict[key] = (value, now)
        return value
        
    
        
        
    def _get_pip_size(self, symbol: str) -> float:
        """
        Calcola la dimensione di un pip in modo robusto (supporta simboli come BTCUSD, XAUUSD).
        Calcola la dimensione di un pip in modo robusto
        """
        try:
            # 1. Prova a ottenere info da MT5
            info = mt5.symbol_info(symbol)
            if info and info.point > 0:
                return info.point
                
            # 2. Fallback per simboli speciali
            pip_map = {
                'BTCUSD': 1.0,
                'ETHUSD': 0.1,
                'XAUUSD': 0.01,
                'SP500': 0.1,
                'NAS100': 0.1,
                'default': 0.0001
            }
            base_symbol = symbol.split('.')[0]  # Rimuove .cash/.pro
            return pip_map.get(base_symbol, pip_map['default'])
            
        except Exception as e:
            logger.debug(f"Errore pip size per {symbol}: {str(e)}")
            return 0.0001  # Valore di fallback sicuro    


    def get_quantum_params(self, symbol: str) -> dict:
        """Restituisce i parametri quantistici con eventuali override"""
        base_params = self._config.get('quantum_params', {})
        symbol_config = self._config.get('symbols', {}).get(symbol, {})
        
        # Applica override se presente
        if 'quantum_params_override' in symbol_config:
            return {**base_params, **symbol_config['quantum_params_override']}
        return base_params
    
        
"""
3- DailyDrawdownTracker - Monitora il drawdown giornaliero con protezione THE5ERS. 
Può essere inizializzato indipendentemente ma viene utilizzato dal sistema principale.
"""
class DailyDrawdownTracker:
    """Monitoraggio del drawdown giornaliero con protezione THE5ERS"""
    
    def __init__(self, initial_equity: float, config: Dict):
        """Inizializzazione con accesso sicuro alla configurazione"""
        # Se config è un ConfigManager, estrai il dizionario config
        actual_config = config.config if hasattr(config, 'config') else config
        
        self.daily_high = initial_equity
        self.current_equity = initial_equity
        self.current_balance = initial_equity
        self.last_update_date = datetime.now().date()
        self.currency = actual_config.get('account_currency', 'USD')
        
        try:
            dd_config = actual_config['THE5ERS_specific']['drawdown_protection']
            self.soft_limit = float(dd_config['soft_limit'])
            self.hard_limit = float(dd_config['hard_limit'])
        except KeyError as e:
            raise ValueError(f"Configurazione drawdown mancante: {str(e)}") from e
        
        self.protection_active = False
        self.max_daily_drawdown = 0.0
        self.last_check_time = time.time()

    def update(self, current_equity: float, current_balance: float) -> None:
        """Aggiorna i valori di equity e balance"""
        today = datetime.now().date()
        
        if today != self.last_update_date:
            self.daily_high = max(current_equity, current_balance)
            self.current_balance = current_balance
            self.last_update_date = today
            self.protection_active = False
            self.max_daily_drawdown = 0.0
            logger.info(f"Reset giornaliero drawdown. Nuovo high: {self.daily_high:.2f} {self.currency}")
        else:
            self.daily_high = max(self.daily_high, current_equity, current_balance)
            self.current_equity = current_equity
            self.current_balance = current_balance

    def check_limits(self, current_equity: float) -> Tuple[bool, bool]:
        """Verifica se sono stati raggiunti i limiti di drawdown"""
        if time.time() - self.last_check_time < 5:
            return False, False
            
        self.last_check_time = time.time()
        
        try:
            drawdown_pct = (current_equity - self.daily_high) / self.daily_high
            self.max_daily_drawdown = min(self.max_daily_drawdown, drawdown_pct)
            
            soft_hit = drawdown_pct <= -self.soft_limit
            hard_hit = drawdown_pct <= -self.hard_limit
            
            if hard_hit:
                logger.critical(
                    f"HARD LIMIT HIT! Drawdown: {drawdown_pct*100:.2f}% | "
                    f"High: {self.daily_high:.2f} {self.currency} | "
                    f"Current: {current_equity:.2f} {self.currency}"
                )
            elif soft_hit and not self.protection_active:
                logger.warning(
                    f"SOFT LIMIT HIT! Drawdown: {drawdown_pct*100:.2f}% | "
                    f"Max Daily: {self.max_daily_drawdown*100:.2f}%"
                )
                
            return soft_hit, hard_hit
            
        except ZeroDivisionError:
            logger.error("Errore calcolo drawdown (daily_high zero)")
            return False, False



"""
4- QuantumRiskManager - Gestisce il rischio, calcola dimensioni di posizione e livelli SL/TP. 
Dipende da QuantumEngine e dalla configurazione.
"""       

    
class QuantumRiskManager:
    """
    1. Inizializzazione
    """
    def __init__(self, config, engine, trading_system=None):
        """Initialize with either ConfigManager or dict"""
        if hasattr(config, 'get_risk_params'):  # It's a ConfigManager
            self._config_manager = config
            self._config = config.config
        else:  # It's a raw dict
            self._config_manager = None
            self._config = config
        
        self.engine = engine
        self.trading_system = trading_system  # Inizializza correttamente qui
        
        # Inizializzazione semplificata
        account_info = mt5.account_info()
        self.drawdown_tracker = DailyDrawdownTracker(
            account_info.equity if account_info else 10000,
            self._config
        )
        
        self.symbol_data = {}
        
        # Inizializza il tracker di drawdown
        account_info = mt5.account_info()
        self.drawdown_tracker = DailyDrawdownTracker(
            account_info.equity if account_info else 10000,
            self.config
        )
        
        # Parametri da config
        self.trailing_stop_activation = config.get('risk_management', {}).get('trailing_stop_activation', 0.5)
        self.trailing_step = config.get('risk_management', {}).get('trailing_step', 0.3)
        self.profit_multiplier = config.get('risk_management', {}).get('profit_multiplier', 1.5)
    
    @property
    def config(self):
        """Property per accesso alla configurazione"""
        return self._config
        
        
    """
    2. Calcolo Dimensioni Posizione
    """
    def calculate_position_size(self, symbol: str, price: float, signal: str) -> float:
        try:
            # 1. Ottieni parametri di rischio NORMALIZZATI
            risk_config = self.get_risk_config(symbol)
            account = mt5.account_info()
            
            # 2. Calcola rischio assoluto in valuta base
            risk_amount = account.equity * (risk_config['risk_percent'] / 100)
            
            # 3. Calcola SL in pips con volatilità
            sl_pips = self._calculate_sl_pips(symbol)
            
            # 4. Calcola PIP VALUE normalizzato
            pip_value = self._get_normalized_pip_value(symbol, price)
            
            # 5. Calcola size con protezioni
            size = risk_amount / (sl_pips * pip_value)
            size = self._apply_size_limits(symbol, size)
            
            logger.info(
                f"Size calc {symbol}: "
                f"Risk=${risk_amount:.2f} | "
                f"SL={sl_pips:.1f}pips | "
                f"PipValue=${pip_value:.4f} | "
                f"Size={size:.2f}"
            )
            
            return size
            
        except Exception as e:
            logger.error(f"Error calculating size: {str(e)}")
            return 0.0
    
       

    def _get_normalized_pip_value(self, symbol: str, price: float) -> float:
        """Restituisce il pip value normalizzato per 1 lotto"""
        # Forex standard (EURUSD, GBPUSD, ecc.)
        if symbol.upper().endswith("USD") or symbol.upper().startswith("EUR") or symbol.upper().startswith("GBP") or symbol.upper().startswith("AUD") or symbol.upper().startswith("NZD") or symbol.upper().startswith("CAD") or symbol.upper().startswith("CHF") or symbol.upper().startswith("JPY"):
            return 10.0  # $10 per pip per 1 lotto
        elif "XAUUSD" in symbol:
            return 0.01  # $0.01 per pip per 1 lotto
        elif "SP500" in symbol or "NAS100" in symbol or "US30" in symbol:
            return 0.1   # $0.1 per pip per 1 lotto
        else:
            return 1.0   # Default fallback

    def _apply_size_limits(self, symbol: str, size: float) -> float:
        """Applica limiti di dimensione"""
        info = mt5.symbol_info(symbol)
        if not info:
            return 0.0
            
        # Arrotonda al passo corretto
        step = info.volume_step
        size = round(size / step) * step
        
        # Applica minimi/massimi
        size = max(size, info.volume_min)
        size = min(size, info.volume_max)
        
        logger.info(f"Size finale per {symbol}: {size}")
        
        return size
    

    """
    3. Gestione Stop Loss e Take Profit
    """
    
    def calculate_dynamic_levels(self, symbol: str, position_type: int, entry_price: float) -> Tuple[float, float]:
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
                   
    
    """
    4. Utility e Limitatori di Rischio
    """
    
    def _get_risk_percent(self, symbol: str) -> float:
        """Ottiene la percentuale di rischio con validazione"""
        risk_pct = self._get_config(symbol, 'risk_percent', 0.01)
        return np.clip(risk_pct, 0.001, 0.05)  # Min 0.1%, Max 5%
        
        
    def _calculate_sl_pips(self, symbol: str) -> float:
        """Calcola gli SL pips con volatilità adattiva"""
        min_sl = self._get_config(symbol, 'min_sl_distance_pips', 
                  {'default': 15, 'XAUUSD': 80, 'BTCUSD': 150}.get(symbol, 15))
        
        base_sl = self._get_config(symbol, 'base_sl_pips', 
                  {'default': 30, 'XAUUSD': 150, 'BTCUSD': 400}.get(symbol, 30))
        
        # Ottieni la volatilità quantistica corrente
        volatility = self.engine.calculate_quantum_volatility(symbol)
        
        # Aggiusta gli SL in base alla volatilità
        return max(base_sl * volatility, min_sl)  

    
    def _round_to_step(self, size: float, symbol: str) -> float:
        """Arrotonda la dimensione al passo di volume"""
        step = self.symbol_data[symbol]['volume_step']
        if step > 0:
            size = round(size / step) * step
        return max(size, self.symbol_data[symbol]['volume_min'])
        
        
        
    def _get_config(self, symbol: str, key: str, default: Any = None) -> Any:
        """Helper per ottenere valori dalla configurazione"""
        # Accesso sicuro alla configurazione
        config = self.config.config if hasattr(self.config, 'config') else self.config
        
        # Cerca prima nelle impostazioni specifiche del simbolo, poi nei parametri generali di rischio
        symbol_config = config.get('symbols', {}).get(symbol, {})
        if key in symbol_config.get('risk_management', {}):
            return symbol_config['risk_management'][key]
        
        return config.get('risk_parameters', {}).get(key, default)
        

    
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
            
            # Log per debug
            logger.debug(f"Configurazione rischio per {symbol}: {merged_config}")
            
            return merged_config
            
        except Exception as e:
            logger.error(f"Errore in get_risk_config: {str(e)}")
            return {}
    
    
    """
    5. Validazione e Controlli
    """
    
    def _load_symbol_data(self, symbol: str) -> bool:
        """Calcolo preciso del pip value per tutti i tipi di strumenti"""
        try:
            if symbol in self.symbol_data:
                return True
                
            info = mt5.symbol_info(symbol)
            if not info:
                logger.error(f"Impossibile ottenere info MT5 per {symbol}")
                return False
            
            # Accesso alla configurazione universale
            config = self.config.config if hasattr(self.config, 'config') else self.config
            symbol_config = config.get('symbols', {}).get(symbol, {})
            risk_config = symbol_config.get('risk_management', {})
            
            point = info.point
            contract_size = risk_config.get('contract_size', 1.0)
            
            # Calcolo preciso del pip value
            if symbol in ['XAUUSD', 'XAGUSD']:
                pip_value = 0.01  # 1 pip = $0.01 per ounce
            elif symbol in ['SP500', 'NAS100', 'US30']:
                pip_value = 0.1 * contract_size  # 1 pip = $0.1 per indice
            else:  # Forex (EURUSD, GBPUSD, ecc.)
                pip_value = (point * 10000) * contract_size  # $10 per lotto standard
            
            self.symbol_data[symbol] = {
                'pip_value': pip_value,
                'volume_step': info.volume_step,
                'digits': info.digits,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'contract_size': contract_size
            }
            
            logger.debug(f"Dati precisi per {symbol}: PipValue={pip_value:.2f}, ContractSize={contract_size}")
            return True
            
        except Exception as e:
            logger.error(f"Errore critico in _load_symbol_data: {str(e)}")
            return False

    
    """
    6. Gestione Margine ed Equity
    """
   

"""
5- TradingMetrics - Monitora le metriche di performance. 
Classe indipendente ma utilizzata dal sistema principale.
"""

class TradingMetrics:
    """Monitoraggio delle metriche di performance"""  
    
    """
    1. Inizializzazione  
    """  
    def __init__(self):
        self.metrics = {
            'total_trades': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'profit_factor': 0,
            'symbol_stats': defaultdict(dict)
        }
        self._profit_history = []
        
    """
    2. Aggiornamento Metriche
    """

    def update_trade(self, symbol: str, profit: float):
        """Aggiorna le metriche dopo ogni trade."""
        self.metrics['total_trades'] += 1
        self._profit_history.append(profit)
        
        if symbol not in self.metrics['symbol_stats']:
            self.metrics['symbol_stats'][symbol] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_profit': 0.0,
                'max_drawdown': 0.0
            }
            
        stats = self.metrics['symbol_stats'][symbol]
        stats['trades'] += 1
        stats['total_profit'] += profit
        
        if profit >= 0:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        self._calculate_metrics()

    def _calculate_metrics(self):
        """Ricalcola le metriche aggregate:"""
        if not self._profit_history:
            return
            
        profits = np.array(self._profit_history)
        self.metrics['win_rate'] = np.mean(profits >= 0) * 100
        self.metrics['avg_profit'] = np.mean(profits)
        self.metrics['max_drawdown'] = self._calculate_drawdown(profits)
        self.metrics['sharpe_ratio'] = self._calculate_sharpe(profits)
        self.metrics['profit_factor'] = self._calculate_profit_factor(profits)
        
        for symbol, stats in self.metrics['symbol_stats'].items():
            if stats['trades'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['trades']) * 100
                stats['avg_profit'] = stats['total_profit'] / stats['trades']


    """
    3. Calcoli Statistici (metodi interni)
    """

    def _calculate_drawdown(self, profits: np.ndarray) -> float:
        """ Calcola il drawdown massimo dalla curva di equity."""
        equity_curve = np.cumsum(profits)
        peak = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - peak) / (peak + 1e-10)
        return np.min(drawdowns) * 100

    def _calculate_sharpe(self, profits: np.ndarray) -> float:
        """ Calcola lo Sharpe Ratio annualizzato."""
        if len(profits) < 2:
            return 0.0
            
        daily_returns = profits / np.mean(profits[:-1]) if np.mean(profits[:-1]) != 0 else profits
        sharpe = np.mean(daily_returns) / (np.std(daily_returns) + 1e-10)
        return sharpe * np.sqrt(252)

    def _calculate_profit_factor(self, profits: np.ndarray) -> float:
        """Calcola il rapporto tra profitti e perdite."""
        gross_profit = profits[profits > 0].sum()
        gross_loss = -profits[profits < 0].sum()
        return gross_profit / (gross_loss + 1e-10)
        
    """
    4. Report e Output
    """
   
        


"""
6- QuantumTradingSystem - La classe principale che coordina tutto:

    -Utilizza ConfigManager per caricare la configurazione

    -Istanzia QuantumEngine per l'elaborazione dei segnali

    -Utilizza QuantumRiskManager per la gestione del rischio

    -Monitora le posizioni con DailyDrawdownTracker

    -Tiene traccia delle performance con TradingMetrics
"""        

class QuantumTradingSystem:
    """
    Sistema completo di trading algoritmico quantistico
    """
    
    """
    1. Inizializzazione e Configurazione
    """
    
    def __init__(self, config_path: str):
        """Costruttore principale"""
        # Inizializzazione base
        self._setup_logger(config_path)
        self._config_path = config_path
        self.running = False
        
        # Caricamento configurazione
        self._load_configuration(config_path)  # Questo inizializza self.config
        
        # Verifica configurazione minima
        if not hasattr(self.config, 'config') or 'symbols' not in self.config.config:
            logger.error("Configurazione simboli non valida nel file di configurazione")
            raise ValueError("Sezione symbols mancante nella configurazione")
        
        # Inizializzazione componenti core
        self.config_manager = ConfigManager(config_path)
        self._config = self.config_manager.config
        
        # Attiva automaticamente i simboli in MT5
        self._activate_symbols()
        
        self.engine = QuantumEngine(self.config_manager)
        self.risk_manager = QuantumRiskManager(self.config_manager, self.engine, self)  # Passa self come terzo parametro
        
        self.max_positions = self.config_manager.get_risk_params().get('max_positions', 4)
        self.current_positions = 0
        self.trade_count = defaultdict(int)
        
        # Inizializzazione MT5
        if not self._initialize_mt5():
            raise RuntimeError("Inizializzazione MT5 fallita")
        
        # Metriche e tracking
        self.metrics_lock = Lock()
        self.position_lock = Lock()
        self.metrics = TradingMetrics()
        
        # Info account e valuta
        self.account_info = mt5.account_info()
        self.currency = (
            self.account_info.currency 
            if self.account_info 
            else self.config.config.get('account_currency', 'USD')
        )
        if not self.account_info:
            logger.warning(f"Usando valuta di fallback: {self.currency}")
        
        # Inizializzazione metriche trading
        self.trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'symbol_stats': defaultdict(dict)
        }
        
        # Drawdown tracker
        initial_equity = self.account_info.equity if self.account_info else 10000
        self.drawdown_tracker = DailyDrawdownTracker(
            initial_equity=initial_equity,
            config=self.config.config
        )
        
        # Stato sistema
        self.last_position_check = 0
        self.last_connection_check = 0
        self.last_account_update = 0
        self.last_tick_check = 0
        self.last_buffer_check = 0
        
        logger.info("Sistema inizializzato correttamente")
        
        logger.info(f"Simboli configurati: {self.config_manager.symbols}")
        logger.info(f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}")
    
    def _activate_symbols(self):
        """Attiva automaticamente i simboli richiesti in MT5"""
        try:
            symbols_to_activate = list(self.config_manager.symbols)
            logger.info(f"Attivazione simboli in MT5: {symbols_to_activate}")
            
            for symbol in symbols_to_activate:
                # Verifica se il simbolo esiste
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    logger.warning(f"Simbolo {symbol} non trovato nel broker")
                    continue
                    
                # Attiva il simbolo se non è già attivo
                if not symbol_info.visible:
                    if mt5.symbol_select(symbol, True):
                        logger.info(f"Simbolo {symbol} attivato con successo")
                    else:
                        logger.error(f"Impossibile attivare il simbolo {symbol}")
                else:
                    logger.info(f"Simbolo {symbol} già attivo")
                    
        except Exception as e:
            logger.error(f"Errore durante l'attivazione dei simboli: {str(e)}")
   
   
    def _setup_logger(self, config_path: str):
        """Configura il sistema di logging"""
        global logger
        logger = setup_logger(config_path)
        clean_old_logs()
        
        
    def _load_configuration(self, config_path: str):
        """Carica il file di configurazione"""
        try:
            logger.info(f"Caricamento configurazione da {config_path}")
            
            # Carica la configurazione usando ConfigManager
            self.config = ConfigManager(config_path)
            
            # Verifica di base
            if not hasattr(self.config, 'config'):
                raise ValueError("Struttura config non valida")
                
            if 'symbols' not in self.config.config:
                raise ValueError("Sezione 'symbols' mancante nel file di configurazione")
                
            logger.info(f"Configurazione caricata con {len(self.config.config['symbols'])} simboli")
            
        except Exception as e:
            logger.critical(f"Errore caricamento configurazione: {str(e)}")
            raise
            
            

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
                port=int(config.get('port', 18889))  # Default a 18889 se non specificato
            ):
                logger.error(f"Errore inizializzazione MT5: {mt5.last_error()}")
                return False
                
            logger.info(f"Connesso a {config.get('server', '')} sulla porta {config.get('port', 18889)}")
            return True
            
        except Exception as e:
            logger.error(f"Eccezione durante inizializzazione MT5: {str(e)}")
            return False
            

    """
    2. Gestione Connessione e Ambiente
    """

    def _verify_connection(self) -> bool:
        """Verifica/connessione MT5 - Verifica la connessione MT5 con ripristino automatico"""
        try:
            if not mt5.initialize() or not mt5.terminal_info().connected:
                logger.warning("Connessione MT5 persa, tentativo di riconnessione...")
                mt5.shutdown()
                time.sleep(5)
                return mt5.initialize()
            return True
        except Exception as e:
            logger.error(f"Errore verifica connessione: {str(e)}")
            return False
        
       
                 

    """
    3. Core del Trading System            
    """        
        
    def start(self):
        """Avvia il sistema"""
        try:
            if not hasattr(self, 'config') or not hasattr(self.config, 'symbols'):
                raise RuntimeError("Configurazione non valida - simboli mancanti")
                
            logger.info(f"Avvio sistema con {len(self.config.symbols)} simboli")
            
            if not hasattr(self, 'engine') or not hasattr(self, 'risk_manager'):
                raise RuntimeError("Componenti critici non inizializzati")
            
            self.running = True
            logger.info("Sistema di trading avviato correttamente")
            
            while self.running:
                try:
                    self._main_loop()
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("Arresto richiesto dall'utente")
                    self.running = False
                except Exception as e:
                    logger.error(f"Errore durante l'esecuzione: {str(e)}", exc_info=True)
                    time.sleep(5)
                    
        except Exception as e:
            logger.critical(f"Errore fatale: {str(e)}", exc_info=True)
        finally:
            self.stop()
                
                
    def stop(self):
        """Ferma il sistema"""
        self.running = False
        
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


    def _main_loop(self):
        """
        cuore pulsante
        Loop principale con variabili di tempo come attributi di istanza
        Loop principale di trading
        """
        
        while self.running:
            # Verifica connessione MT5
            if not mt5.terminal_info().connected:
                logger.error("Connessione MT5 persa!")
                time.sleep(5)
                continue
                
            # DEBUG: Verifica fuso orario
            server_time = mt5.symbol_info_tick("EURUSD").time_msc if mt5.symbol_info_tick("EURUSD") else None

            current_time = time.time()
            
            # Controlli periodici
            if current_time - self.last_connection_check > 30:  # Check più frequente
                if not self._verify_connection():
                    time.sleep(5)
                    continue
                self.last_connection_check = current_time
                
            
            if current_time - self.last_connection_check > 60:
                self._verify_connection()
                self.last_connection_check = current_time
                
            if current_time - self.last_account_update > 60:
                self._update_account_info()
                self.last_account_update = current_time
                self._check_drawdown_limits()
            
            if current_time - self.last_tick_check > 300:
                self.engine.check_tick_activity()  # Qui viene chiamato check_tick_activity()
                self.last_tick_check = current_time
                
                
            if time.time() - self.last_buffer_check > 300:  # 5 minuti
                self.check_buffers()
                self.last_buffer_check = time.time()
            
            
            if current_time - self.last_position_check > 30:
                self._monitor_open_positions()
                self._validate_positions()
                self.close_positions_before_weekend()  # <--- AGGIUNTO QUI
                self.last_position_check = current_time
                
            for symbol in self.config_manager.symbols:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    self.engine.process_tick(symbol, tick.bid)
                    buffer_size = len(self.engine.tick_buffer.get(symbol, []))
                    logger.debug(f"{symbol} buffer: {buffer_size}")
                
            try:
                # Timeout per process_symbols
                start_time = time.time()
                self._process_symbols()
                process_time = time.time() - start_time
                
                # Log se il processamento è lento
                if process_time > 5:
                    logger.warning(f"Processamento simboli lento: {process_time:.2f}s")
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Errore nel processamento simboli: {str(e)}", exc_info=True)
                time.sleep(5)

            except KeyboardInterrupt:
                logger.info("Ctrl+C rilevato, arresto sistema...")
                self.running = False
                raise
            except Exception as e:
                logger.critical(f"Errore critico nel main loop: {str(e)}")
                time.sleep(10)    
    
    def _process_symbols(self):
        """
        Elabora tutti i simboli
        Processa tutti i simboli con gestione robusta degli errori di connessione
        """
        logger.debug(f"Current positions: {len(mt5.positions_get() or [])}/{self.max_positions}")
        logger.debug(f"Symbols to process: {self.config.symbols}")
        
        try:
            # Controllo connessione e posizioni con gestione errori
            if not self._verify_connection():
                return
                
            positions = mt5.positions_get()
            current_positions = len(positions) if positions is not None else 0
            
            if current_positions >= self.max_positions:
                logger.debug(f"Raggiunto max_positions ({self.max_positions}), salto nuovi trade")
                return
                
            for symbol in self.config.symbols:
                try:
                    if not self._validate_symbol(symbol):
                        continue
                        
                    tick = mt5.symbol_info_tick(symbol)
                    if not tick:
                        logger.debug(f"Nessun tick disponibile per {symbol}")
                        continue
                        
                    self._process_single_symbol(symbol, tick, current_positions)
                    
                except Exception as e:
                    logger.error(f"Errore processando {symbol}: {str(e)}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Errore critico in _process_symbols: {str(e)}", exc_info=True)
            raise
    
        
    def _process_single_symbol(self, symbol: str, tick, current_positions: int):
        # Aggiungi controllo tempo minimo tra ordini
        MIN_ORDER_INTERVAL = 5  # secondi
        last_trade_time = getattr(self, f'_last_trade_time_{symbol}', 0)
        if time.time() - last_trade_time < MIN_ORDER_INTERVAL:
            logger.debug(f"Attendendo {MIN_ORDER_INTERVAL}s tra ordini per {symbol}")
            return
        
        
        # Ottieni i parametri quantistici specifici
        q_params = self.engine.get_quantum_params(symbol)
        
        # Verifica buffer
        required_samples = q_params.get('min_spin_samples', 100)
        if len(self.engine.tick_buffer[symbol]) < required_samples:
            logger.debug(f"Attendendo più dati per {symbol}...")
            return
        
        # Gestione sessioni speciali (es. per XAUUSD)
        if 'special_sessions' in self.config.config['symbols'].get(symbol, {}):
            self._handle_special_sessions(symbol)
            
        """Processa un singolo simbolo con controllo avanzato dei limiti"""
        # 1. Verifica concurrency-safe del limite giornaliero
        with self.metrics_lock:
            daily_limit = self.config.config['risk_parameters']['max_daily_trades']
            if self.trade_count.get(symbol, 0) >= daily_limit:
                logger.debug(f"Bloccato {symbol}: raggiunto limite {daily_limit} trade giornalieri")
                return
                
        # 2. Verifica cooldown con logging migliorato
        # 2. Verifica cooldown con logging migliorato
        if not self.engine.can_trade(symbol):
            existing_pos = self._get_existing_position(symbol)
            cooldown_left = self.engine.get_remaining_cooldown(symbol)  # Ora questo metodo esiste
            logger.debug(f"{symbol} in cooldown - {cooldown_left:.0f}s rimanenti")
            return
            
        # 3. Elaborazione tick con controllo qualità dati
        if not self._validate_tick(tick):  # Nuovo metodo helper
            #logger.warning(f"Tick non valido per {symbol} - saltato")
            logger.debug(f"Tick non valido per {symbol} - saltato")
            return
            
        self.engine.process_tick(symbol, tick.bid)
        
        # 4. Ottenimento segnale con timeout
        try:
            signal, price = self.engine.get_signal(symbol)
        except TimeoutError:
            logger.error(f"Timeout ottenimento segnale per {symbol}")
            return
            
        if signal == "HOLD":
            return
            
        # 5. Gestione posizione esistente con lock
        with self.position_lock:
            existing_pos = self._get_existing_position(symbol)
            if existing_pos:
                if ((existing_pos.type == mt5.ORDER_TYPE_BUY and signal == "BUY") or
                   (existing_pos.type == mt5.ORDER_TYPE_SELL and signal == "SELL")):
                    logger.debug(f"Segnale {signal} ignorato per posizione esistente")
                    return
                if not self._close_position(existing_pos):
                    return
                    
        # 6. Calcolo dimensione con fallback
        entry_price = tick.ask if signal == "BUY" else tick.bid
        try:
            position_size = self.risk_manager.calculate_position_size(
                symbol, entry_price, signal)
            if position_size <= 0:
                logger.debug(f"Dimensione posizione non valida per {symbol}")
                return
        except Exception as e:
            logger.error(f"Errore calcolo dimensione {symbol}: {str(e)}")
            return
            
        # 7. Esecuzione trade con verifica finale limite
        with self.metrics_lock:  # Double-check pattern
            if self.trade_count.get(symbol, 0) >= daily_limit:
                logger.debug(f"Limite raggiunto durante processing per {symbol}")
                return

                
            if self._execute_trade(symbol, signal, tick, entry_price, position_size):
                setattr(self, f'_last_trade_time_{symbol}', time.time())  # Aggiorna timestamp
                self.trade_count[symbol] += 1  # Incremento solo qui!
                self.engine.record_trade_close(symbol)
                logger.info(f"Trade #{self.trade_count[symbol]}/{daily_limit} eseguito per {symbol}")
                
                
    def _handle_special_sessions(self, symbol: str):
        """Applica modifiche durante sessioni speciali (es. asiatica per XAUUSD)"""
        now = datetime.now().time()
        symbol_config = self.config.config['symbols'].get(symbol, {})
        special_config = symbol_config.get('special_sessions', {})
        
        for session_name, session_config in special_config.items():
            start_str, end_str = session_config['time_range'][0].split('-')
            start = parse_time(start_str)
            end = parse_time(end_str)
            
            in_session = (start <= now <= end) if start <= end else (now >= start or now <= end)
            
            if in_session:
                logger.info(f"Applicando parametri sessione {session_name} per {symbol}")
                
                # 3. Aggiusta parametri quantistici se necessario
                if 'quantum_params_override' in symbol_config:
                    q_params = symbol_config['quantum_params_override']
                    if 'spin_window' in q_params:
                        # Aggiungi validazione per evitare infinito
                        if not isinstance(q_params['spin_window'], (int, float)) or q_params['spin_window'] == float('inf'):
                            logger.warning(f"Valore spin_window non valido per {symbol}, usando default")
                            q_params['spin_window'] = self.engine.spin_window  # Usa il valore di default
                        
                        # Ora esegui la modifica in sicurezza
                        new_window = int(q_params['spin_window'] * 1.2)  # +20% finestra
                        if new_window > 0:  # Ulteriore validazione
                            q_params['spin_window'] = new_window
                        else:
                            logger.warning(f"Nuovo spin_window non valido per {symbol}, mantenuto originale")
    
                
    def get_remaining_cooldown(self, symbol: str) -> float:
        """Restituisce secondi rimanenti di cooldown"""
        last_close = self.position_cooldown.get(symbol, 0)
        return max(0, self.position_cooldown - (time.time() - last_close))

    def _validate_tick(self, tick) -> bool:
        """Aggiungi controllo per evitare bias di direzione"""
        if not tick or tick.bid <= 0 or tick.ask <= 0:
            return False
            
        symbol = tick.symbol if hasattr(tick, 'symbol') else "SP500"
        
        # Controlla che il mercato non sia in piatto
        spread = abs(tick.ask - tick.bid)
        pip_size = self.engine._get_pip_size(symbol)
        spread_pips = spread / pip_size
        
        # Se lo spread è troppo stretto, potrebbe indicare mercato poco liquido
        if spread_pips < 0.5:  # Soglia da adattare
            logger.debug(f"Spread troppo stretto per {symbol}: {spread_pips:.1f}pips")
            return False
            
        return True

       
    """
    4. Gestione Ordini e Posizioni
    """                       
        
    def _execute_trade(self, symbol: str, signal: str, tick, price: float, size: float) -> bool:
        try:
            # 1. Determinazione tipo posizione
            position_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
            execution_price = tick.ask if signal == "BUY" else tick.bid

            # 2. Calcolo SL/TP con 3 tentativi
            sl, tp = None, None
            for attempt in range(3):
                try:
                    sl, tp = self.risk_manager.calculate_dynamic_levels(symbol, position_type, execution_price)
                    if sl != 0.0 and tp != 0.0:
                        break
                except Exception as e:
                    logger.warning(f"Tentativo {attempt+1} fallito per {symbol}: {str(e)}")
                    time.sleep(1)

            # 3. Fallback se SL/TP non validi
            if sl == 0.0 or tp == 0.0:
                logger.warning(f"Calcolo dinamico fallito per {symbol}, usando fallback")
                sl, tp = self._get_fallback_levels(symbol, position_type, execution_price)
                if not self._validate_levels(symbol, execution_price, sl, tp):
                    raise ValueError(f"Fallback SL/TP non validi per {symbol}")

            # 4. Preparazione richiesta di trading
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": size,
                "type": position_type,
                "price": execution_price,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": self.config.config['magic_number'],
                "comment": "QTS-TRADE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # Verifica margine sufficiente
            required_margin = mt5.order_calc_margin(
                position_type,  # Usa position_type invece di rifare il check
                symbol,
                size,
                execution_price
            )
            if required_margin > self.account_info.margin_free:
                logger.error(f"Margine insufficiente per {symbol}: {self.account_info.margin_free} < {required_margin}")
                return False

            # 5. Esecuzione dell'ordine (UNA SOLA VOLTA!)
            result = mt5.order_send(request)
            
            # Log dettagliato del risultato senza usare vars()
            logger.debug(f"Risultato ordine: Retcode={result.retcode}, Deal={result.deal}, Order={result.order}")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_desc = mt5.last_error()
                logger.error(f"Errore esecuzione {symbol}: {result.comment} (code: {result.retcode}) - {error_desc}")
                return False

            # 6. Registrazione successo
            logger.info(f"Trade eseguito {symbol} {size} lots a {execution_price} | SL: {sl:.2f} | TP: {tp:.2f}")
            logger.info(f"Ticket: {result.order} | Deal: {result.deal}")
            
            # 7. Aggiornamento metriche con timeout
            try:
                with self.metrics_lock:
                    self.trade_count[symbol] += 1
                    self.engine.record_trade_close(symbol)
                logger.info(f"Metriche aggiornate per {symbol}")
            except Exception as e:
                logger.error(f"Errore aggiornamento metriche per {symbol}: {str(e)}")
            
            # 8. Pausa di sicurezza post-trade
            time.sleep(2)
            logger.info(f"Trade {symbol} completato, sistema pronto per continuare")
            
            return True

        except Exception as e:
            logger.error(f"Errore critico in _execute_trade per {symbol}: {str(e)}", exc_info=True)
            return False
          

        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return False
            
        point = symbol_info.point
        min_distance = max(
            self.get_risk_config(symbol).get('stops_level', 15) * point,
            (symbol_info.ask - symbol_info.bid) * 1.5  # 1.5x spread corrente
        )
        
        return (abs(entry - sl) >= min_distance and 
                abs(entry - tp) >= min_distance)
                

    # --- Metodi di supporto --- #
    
    def _get_fallback_levels(self, symbol: str, position_type: int, price: float) -> Tuple[float, float]:
        """Livelli di emergenza basati solo su parametri base"""
        config = self.get_risk_config(symbol)
        sl_pips = config.get('base_sl_pips', 80)
        tp_pips = sl_pips * config.get('profit_multiplier', 2.5)
        pip_size = self.engine._get_pip_size(symbol)
        
        if position_type == mt5.ORDER_TYPE_BUY:
            return (
                round(price - sl_pips * pip_size, 6),
                round(price + tp_pips * pip_size, 6)
            )
        return (
            round(price + sl_pips * pip_size, 6),
            round(price - tp_pips * pip_size, 6)
        )
        

    # --- Fine Metodi di supporto ---        

    def _get_existing_position(self, symbol: str):
        """Chiude una posizione - Recupera posizioni esistenti"""
        positions = mt5.positions_get(symbol=symbol)
        if positions and len(positions) > 0:
            return positions[0]
        return None
      
      
    def _close_position(self, position):
        if self._check_position_closed(position.ticket):
            return True
            
        # Aggiungere controllo durata minima
        min_duration = 300  # 5 minuti
        
        # Converti position.time in datetime se necessario
        if isinstance(position.time, (int, float)):
            position_time = datetime.fromtimestamp(position.time)
        else:
            position_time = position.time
        
        if (datetime.now() - position_time) < timedelta(seconds=min_duration):
            logger.warning(f"Posizione {position.ticket} chiusa troppo presto")
            return False
        
        """Versione migliorata con verifica dello stato"""
        if self._check_position_closed(position.ticket):
            logger.debug(f"Posizione {position.ticket} già chiusa")
            return True
            
        if not position or not hasattr(position, 'ticket'):
            logger.error("Posizione non valida per la chiusura")
            return False
            
        existing_positions = mt5.positions_get(ticket=position.ticket)
        if not existing_positions or len(existing_positions) == 0:
            logger.info(f"Posizione {position.ticket} già chiusa o non esistente")
            return True
            
        try:
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                logger.error(f"Impossibile ottenere info simbolo {position.symbol}")
                return False
                
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": symbol_info.ask if position.type == mt5.ORDER_TYPE_BUY else symbol_info.bid,
                "deviation": 10,
                "magic": self.config.config['magic_number'],
                "comment": "QTS-CLOSE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            if not self._validate_close_request(close_request, position):
                return False
                
            result = mt5.order_send(close_request)
                
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                profit = (position.price_current - position.price_open) * position.volume
                self._update_trade_metrics(
                    success=True, 
                    symbol=position.symbol, 
                    profit=profit
                )
                return True
                
            logger.info(f"Posizione {position.ticket} chiusa con successo a {close_request['price']}")
            return True
            
        except Exception as e:
            logger.error(f"Eccezione durante chiusura posizione {position.ticket if hasattr(position, 'ticket') else 'N/A'}: {str(e)}", exc_info=True)
            return False
        
        
    
    """
    5. Monitoraggio Posizioni
    """
    
    def _monitor_open_positions(self):
        positions = mt5.positions_get()
        if positions:
            for pos in positions:
                # DEBUG: Verifica struttura della posizione
                logger.debug(f"Position structure: {dir(pos)}")
                logger.debug(f"Position details: Ticket={pos.ticket}, Time={pos.time}, Type={type(pos.time)}")
                
                self._check_position_timeout(pos)
        """Monitoraggio posizioni con gestione errori migliorata"""
        try:
            with self.position_lock:
                positions = mt5.positions_get()
                if positions is None:
                    logger.warning("Nessuna posizione ottenuta da MT5")
                    return
                    
                self.current_positions = len(positions)
                
                for position in positions:
                    try:
                        # Verifica se la posizione esiste ancora
                        current_pos = mt5.positions_get(ticket=position.ticket)
                        if not current_pos or len(current_pos) == 0:
                            continue
                            
                        tick = mt5.symbol_info_tick(position.symbol)
                        if not tick:
                            logger.debug(f"Nessun tick per {position.symbol}")
                            continue
                        
                        current_price = tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask
                        
                        # Gestione trailing stop
                        self._manage_trailing_stop(position, current_price)
                        
                        # Gestione timeout
                        self._check_position_timeout(position)
                        
                    except Exception as e:
                        logger.error(f"Errore monitoraggio posizione {position.ticket}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Errore critico in _monitor_open_positions: {str(e)}")
            
    def _check_position_closed(self, ticket: int) -> bool:
        """Verifica se una posizione è stata chiusa"""
        positions = mt5.positions_get(ticket=ticket)
        return positions is None or len(positions) == 0
    
    
    def _manage_trailing_stop(self, position, current_price: float) -> bool:
        """Gestione avanzata del trailing stop con gestione errori migliorata"""
        try:
            # Ottieni la configurazione dal risk_manager
            config = self.risk_manager.get_risk_config(position.symbol)
            trailing_config = config.get('trailing_stop', {})
            
            if not trailing_config.get('enable', False):
                return False

            pip_size = self.engine._get_pip_size(position.symbol)
            current_sl = position.sl or 0
            
            # Calcola parametri trailing
            activation_pips = trailing_config.get('activation_pips', 50)
            step_pips = trailing_config.get('step_pips', 20)
            lock_percentage = trailing_config.get('lock_percentage', 0.5)

            if position.type == mt5.ORDER_TYPE_BUY:
                profit_pips = (current_price - position.price_open) / pip_size
                new_sl = position.price_open + (lock_percentage * (current_price - position.price_open))
                new_sl = max(new_sl, current_sl + (step_pips * pip_size))
            else:
                profit_pips = (position.price_open - current_price) / pip_size
                new_sl = position.price_open - (lock_percentage * (position.price_open - current_price))
                new_sl = min(new_sl, current_sl - (step_pips * pip_size))

            # Applica trailing solo se superata l'attivazione
            if profit_pips >= activation_pips:
                if ((position.type == mt5.ORDER_TYPE_BUY and new_sl > current_sl) or
                    (position.type == mt5.ORDER_TYPE_SELL and new_sl < current_sl)):
                    return self._modify_position(position, sl=new_sl)
                    
            return False
        
        except Exception as e:
            logger.error(f"Errore critico in trailing stop per posizione {position.ticket}: {str(e)}")
            return False
            


    def _check_position_timeout(self, position):
        """Controlla timeout posizione con gestione robusta dei timestamp"""
        try:
            # Accesso alla configurazione
            max_hours = self.config.config.get('risk_parameters', {}).get('max_position_hours', 12)
            
            if not hasattr(position, 'time'):
                logger.warning(f"Posizione {position.ticket} senza attributo time")
                return

            # DEBUG: Log del timestamp originale
            logger.debug(f"Position {position.ticket} raw time: {position.time} (type: {type(position.time)})")

            # Conversione del tempo della posizione
            if isinstance(position.time, (int, float)):
                # Converti timestamp Unix in datetime
                position_dt = datetime.fromtimestamp(position.time)
            elif isinstance(position.time, datetime):
                position_dt = position.time
            else:
                logger.error(f"Formato tempo non supportato per posizione {position.ticket}: {type(position.time)}")
                return

            # Calcolo della durata CORRETTO
            current_dt = datetime.now()
            duration = current_dt - position_dt
            duration_hours = duration.total_seconds() / 3600

            # DEBUG: Log dei tempi calcolati
            logger.debug(f"Position {position.ticket} opened at: {position_dt}, current: {current_dt}, duration: {duration_hours:.2f}h")

            if duration_hours > max_hours:
                logger.info(f"Chiusura posizione {position.ticket} per timeout ({duration_hours:.1f}h > {max_hours}h)")
                self._close_position(position)
                
        except Exception as e:
            logger.error(f"Errore controllo timeout posizione {position.ticket}: {str(e)}", exc_info=True)
        
        

    def _modify_position(self, position, sl=None, tp=None) -> bool:
        """Modifica SL/TP di una posizione esistente con controlli avanzati"""
        try:
            # Verifica se la posizione esiste ancora
            current_pos = mt5.positions_get(ticket=position.ticket)
            if not current_pos or len(current_pos) == 0:
                logger.debug(f"Posizione {position.ticket} non trovata")
                return False

            # Calcola le nuove valori solo se diversi dagli attuali
            new_sl = round(sl, 5) if sl is not None else position.sl
            new_tp = round(tp, 5) if tp is not None else position.tp
            
            # Verifica se ci sono effettivi cambiamenti
            if (abs(new_sl - (position.sl or 0)) < 0.00001 and 
                abs(new_tp - (position.tp or 0)) < 0.00001):
                logger.debug(f"Nessun cambiamento necessario per posizione {position.ticket}")
                return True

            # Prepara la richiesta di modifica
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position.ticket,
                "symbol": position.symbol,
                "sl": new_sl,
                "tp": new_tp,
                "deviation": 10,
                "type_time": mt5.ORDER_TIME_GTC,
            }

            # Invia la richiesta
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Posizione {position.ticket} modificata: SL={new_sl}, TP={new_tp}")
                return True
            else:
                logger.error(f"Errore modifica posizione {position.ticket}: {result.comment} (code: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Eccezione durante modifica posizione {position.ticket}: {str(e)}")
            return False
                
            
    def _validate_positions(self):
        """Verifica posizioni duplicate"""
        symbols_with_positions = set()
        positions = mt5.positions_get()
        
        if positions:
            for pos in positions:
                if pos.symbol in symbols_with_positions:
                    logger.error(f"Trovata posizione duplicata per {pos.symbol}!")
                    self._close_position(pos)
                else:
                    symbols_with_positions.add(pos.symbol)



    """
    6. Risk Management
    """

   
                    
    def _check_drawdown_limits(self):
        """Controlla limiti drawdown"""
        if not hasattr(self, 'drawdown_tracker') or not self.account_info:
            return
        
        soft_hit, hard_hit = self.drawdown_tracker.check_limits(self.account_info.equity)
        
        if hard_hit:
            logger.critical("Hard drawdown limit raggiunto!")
            raise RuntimeError("Hard drawdown limit raggiunto")
        
        if soft_hit and not self.drawdown_tracker.protection_active:
            logger.warning("Soft drawdown limit - riduzione esposizione")
            self.drawdown_tracker.protection_active = True
            self.max_positions = max(1, self.max_positions // 2)
            logger.info(f"Max posizioni ridotto a {self.max_positions}")          



            
    


    """
    7. Metriche e Reporting
    """

    def _update_trade_metrics(self, success: bool, symbol: str, profit: float = 0.0) -> None:
        """Aggiorna metriche con controllo del limite giornaliero"""
        today = datetime.now().date()
        
        with self.metrics_lock:
            # Reset counter if new day (deve essere la PRIMA operazione)
            if not hasattr(self, '_last_trade_day') or self._last_trade_day != today:
                self._last_trade_day = today
                self.trade_count = defaultdict(int)
                
            # Verifica limite PRIMA di incrementare
            if self.trade_count[symbol] >= self.config.config['risk_parameters']['max_daily_trades']:
                logger.warning(f"Raggiunto limite giornaliero per {symbol} - trade non conteggiato")
                return
                
            # Solo ora incrementiamo il contatore
            self.trade_count[symbol] += 1
            self.trade_metrics['total_trades'] += 1
            
            if success:
                self.trade_metrics['successful_trades'] += 1
                self.trade_metrics['total_profit'] += profit
                
                if symbol not in self.trade_metrics['symbol_stats']:
                    self.trade_metrics['symbol_stats'][symbol] = {
                        'wins': 0,
                        'losses': 0,
                        'total_profit': 0.0
                    }
                    
                stats = self.trade_metrics['symbol_stats'][symbol]
                stats['total_profit'] += profit
                if profit >= 0:
                    stats['wins'] += 1
                else:
                    stats['losses'] += 1
                    
                if hasattr(self, 'metrics'):
                    self.metrics.update_trade(symbol, profit)
            else:
                self.trade_metrics['failed_trades'] += 1
                
        logger.info(f"Trade {'successful' if success else 'failed'} | {symbol} | Profit: {profit:.2f}")


    def _update_account_info(self):
        """Aggiorna info account"""
        self.account_info = mt5.account_info()
        if self.account_info:
            self.drawdown_tracker.update(self.account_info.equity, self.account_info.balance)




    """
    8. Validazioni
    """
    def _validate_symbol(self, symbol: str) -> bool:
        """Validazione avanzata per strategia tick-based"""
        # 1. Controllo connessione e disponibilità simbolo
        # Aggiungi nel metodo _validate_symbol():
        if not mt5.symbol_select(symbol, True):
            logger.error(f"Impossibile selezionare {symbol}")
            return False
        
        if not mt5.terminal_info().connected:
            logger.error(f"2 - Impossibile selezionare {symbol}")
            return False

        # 2. Verifica orari trading dalla configurazione
        if not is_trading_hours(symbol, self.config.config):
            return False
            

        buffer = self.engine.tick_buffer.get(symbol, [])
        if len(buffer) < self.engine.min_spin_samples:
            logger.debug(f"Attendendo dati per {symbol} ({len(buffer)}/{self.engine.min_spin_samples})")
            return False  # Oppure continua se vuoi solo loggare

        # 3. Controllo qualità del tick (invece del timeframe)
        tick = mt5.symbol_info_tick(symbol)
        
        if not tick:
            logger.error(f"Nessun tick ricevuto per {symbol}")
            return False
        
        if tick.time_msc < (time.time() - 60)*1000:  # Se il tick è più vecchio di 60s
            logger.debug(f"Dati tick obsoleti per {symbol} ({(time.time()*1000 - tick.time_msc)/1000:.1f}s)")
            return False

        # 4. Controllo spread e liquidità
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return False
            
        spread = (symbol_info.ask - symbol_info.bid) / self.engine._get_pip_size(symbol)
        max_spread = self.config_manager._get_max_allowed_spread(symbol)  # Modificato qui
        
        if spread > max_spread * 1.2:  # Tolleranza +20%
            logger.debug(f"Spread {spread:.1f}p troppo alto per {symbol} (max {max_spread:.1f}p)")
            return False

        """
        # 5. Controllo volume/minimo movimento
        if (symbol_info.volume_min > 0.1 or 
            symbol_info.volume_step < 0.01 or
            symbol_info.trade_tick_size < 0.1):
            logger.debug(f"Condizioni contratto non ottimali per {symbol}")
            return False
        """
        # 6. Verifica buffer dati sufficiente
        if len(self.engine.tick_buffer.get(symbol, [])) < self.engine.min_spin_samples:
            logger.debug(f"Dati insufficienti nel buffer per {symbol}")
            return False

        return True
 
    
    def _validate_close_request(self, request, position):
        """Controlla richiesta chiusura"""
        if not position or not hasattr(position, 'price_open'):
            return False
            
        if position.price_open == 0:
            return False
            
            
        price_diff = abs(request['price'] - position.price_open)
        if price_diff / position.price_open > 0.1:
            logger.warning(f"Prezzo di chiusura sospetto per {position.symbol}")
            return False
            
        symbol_info = mt5.symbol_info(position.symbol)
        if not symbol_info:
            logger.error(f"Impossibile ottenere info per {position.symbol}")
            return False
            
        if request['volume'] < symbol_info.volume_min:
            logger.error(f"Volume troppo piccolo per chiudere {position.symbol}")
            return False
            
        return True
        
    def check_buffers(self):
        """Monitora lo stato dei buffer dei tick per tutti i simboli"""
        if not hasattr(self, 'engine') or not hasattr(self.engine, 'tick_buffer'):
            logger.warning("Engine o tick_buffer non inizializzati")
            return
            
        for symbol in self.config.symbols:
            buffer_size = len(self.engine.tick_buffer.get(symbol, []))
            logger.info(f"{symbol} buffer: {buffer_size}/{self.engine.buffer_size} | "
                       f"Min samples: {self.engine.min_spin_samples}")
    
    def check_the5ers_limits(self):
        """Controlla i limiti imposti dal broker The5ers"""
        account_info = mt5.account_info()
        if not account_info:
            logger.error("Impossibile ottenere info account MT5")
            return False

        # Calcola equity, balance, drawdown, profit
        equity = account_info.equity
        balance = account_info.balance
        initial_balance = self.config.get('initial_balance', balance)
        max_daily_loss = initial_balance * self.config.config['THE5ERS_specific']['max_daily_loss_percent'] / 100
        max_total_loss = initial_balance * self.config.config['THE5ERS_specific']['max_total_loss_percent'] / 100
        profit_target = initial_balance * self.config.config['THE5ERS_specific']['step1_target'] / 100

        # Daily loss check
        today = datetime.now().date()
        daily_loss = self.get_daily_loss(today)
        if daily_loss < -max_daily_loss:
            logger.warning(f"Limite di perdita giornaliera superato: {daily_loss} < {-max_daily_loss}")
            return False

        # Total loss check
        total_loss = balance - initial_balance
        if total_loss < -max_total_loss:
            logger.warning(f"Limite di perdita totale superato: {total_loss} < {-max_total_loss}")
            return False

        # Profit target check
        if total_loss >= profit_target:
            logger.info(f"Profit target raggiunto: {total_loss} >= {profit_target}")
            # Qui puoi gestire la logica di avanzamento step/scaling
            return False

        return True

    def get_daily_loss(self, day):
        """Calcola la perdita giornaliera (stub, da implementare con storico trades)"""
        # TODO: Implementa la logica per calcolare la perdita giornaliera
        return 0

    def can_trade(self, symbol: str) -> bool:
        """Versione semplificata che rispetta solo i tuoi cooldown configurati"""
        if not self.check_the5ers_limits():
            logger.warning("Trading bloccato per limiti The5ers")
            return False
        return not self.is_in_cooldown_period(symbol)

    def close_positions_before_weekend(self):
        """Chiude tutte le posizioni aperte il venerdì sera prima della chiusura dei mercati"""
        now = datetime.now()
        # Venerdì = 4 (lunedì=0), chiusura alle 21:00 (adatta l'orario secondo il broker)
        if now.weekday() == 4 and now.hour >= 21:
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    try:
                        self._close_position(pos)
                        logger.info(f"Chiusura automatica posizione {pos.ticket} su {pos.symbol} per fine settimana.")
                    except Exception as e:
                        logger.error(f"Errore chiusura automatica {pos.ticket}: {str(e)}")


if __name__ == "__main__":
    try:
        # Carica la configurazione prima di tutto
        system = QuantumTradingSystem(CONFIG_FILE)
        system.start()
    except Exception as e:
        logger.critical(f"Errore iniziale: {str(e)}", exc_info=True)
    finally:
        logger.info("Applicazione terminata")