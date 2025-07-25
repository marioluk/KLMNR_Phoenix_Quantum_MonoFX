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
from typing import Dict, Tuple, List, Any, Optional
from collections import deque, defaultdict
from threading import Lock
from logging.handlers import RotatingFileHandler
import os
import sys
from functools import lru_cache


# Configurazioni globali
CONFIG_FILE = "config/config_autonomous_challenge_production_ready.json"

# Carica la configurazione JSON all'avvio
def auto_correct_symbols(config):
    """
    Versione semplificata: non effettua correzioni automatiche, restituisce la configurazione invariata.
    """
    return config
def load_config(config_path=CONFIG_FILE):
    with open(config_path) as f:
        return json.load(f)

config = load_config()

# Correggi i simboli in base a quelli disponibili su MT5
config = auto_correct_symbols(config)

# Reload automatico della configurazione ogni 15 minuti
import threading
def periodic_reload_config(interval=900):
    global config
    while True:
        time.sleep(interval)
        try:
            config = load_config()
            print(f"[{datetime.now()}] Configurazione ricaricata.")
        except Exception as e:
            print(f"Errore reload config: {e}")

# Avvia il thread di reload all’avvio
reload_thread = threading.Thread(target=periodic_reload_config, daemon=True)
reload_thread.start()

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
            # Assicurati che gli elementi siano oggetti time
            start = time_str[0]
            end = time_str[1]
            if isinstance(start, str):
                start = datetime.strptime(start, "%H:%M").time()
            if isinstance(end, str):
                end = datetime.strptime(end, "%H:%M").time()
            return start, end
            
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
        debug_ranges = []
        for time_range in trading_hours:
            if isinstance(time_range, str):  # Formato legacy "HH:MM-HH:MM"
                start, end = parse_time(time_range)
                debug_ranges.append(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")
                if start <= end:
                    if start <= now <= end:
                        logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} - INTERVALLO: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} -> OK")
                        return True
                else:  # Overnight (es. 22:00-02:00)
                    if now >= start or now <= end:
                        logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} - INTERVALLO: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} (overnight) -> OK")
                        return True
            elif isinstance(time_range, list):  # Nuovo formato ["HH:MM", "HH:MM"]
                start, end = parse_time("-".join(time_range))
                debug_ranges.append(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")
                if start <= now <= end:
                    logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} - INTERVALLO: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} (list) -> OK")
                    return True
        logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} - FUORI ORARIO. Intervalli validi: {debug_ranges}")
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
        symbols_section = self._config.get('symbols', {})
        if not isinstance(symbols_section, dict) or len(symbols_section) == 0:
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
        
   
    def get_risk_params(self, symbol: Optional[str] = None) -> Dict:
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
                    # Volatility calculation must be handled outside ConfigManager
                    logger.error("Adaptive spread calculation requires volatility, which is not available in ConfigManager.")
                    return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
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
        
        # Inizializza signal_stats per evitare errori
        self.signal_stats = {'BUY': 0, 'SELL': 0}
        
       
        
        
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
            logger.info(f"Cooldown normale attivo per {symbol} - {position_cooldown - (time.time() - last_close):.0f}s rimanenti")
            return True
            
        # 2. Controlla cooldown segnali (900s)
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.last_signal_time.get(symbol, 0)
        if time.time() - last_signal < signal_cooldown:
            logger.debug(f"Cooldown segnale attivo per {symbol} - {signal_cooldown - (time.time() - last_signal):.0f}s rimanenti")
            return True
            
        return False
    

    def can_trade(self, symbol: str) -> bool:
        # 0. Controllo limiti di posizione per simbolo
        position_limits = getattr(self, 'position_limits', {})
        max_positions_per_symbol = getattr(self, 'max_positions_per_symbol', None)
        if max_positions_per_symbol is not None:
            current_limit = position_limits.get(symbol, 0)
            if current_limit >= max_positions_per_symbol:
                logger.info(
                    "\n-------------------- [POSITION LIMIT] ------------------\n"
                    f"Symbol: {symbol}\n"
                    f"Current: {current_limit}\n"
                    f"Max Allowed: {max_positions_per_symbol}\n"
                    "------------------------------------------------------\n"
                )
                return False
        """Verifica se è possibile aprire una nuova posizione con controlli completi"""
        # 1. Controlla cooldown
        if self.is_in_cooldown_period(symbol):
            return False
            
        # 2. Verifica spread
        try:
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.info(f"Impossibile ottenere info simbolo {symbol}")
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
            
        # 4. Controlla trades giornalieri - RIMOSSO controllo qui per evitare duplicazione
        # Il controllo viene fatto in _process_single_symbol
            
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
        Logga ogni tick per debug approfondito.
        """
        if symbol not in self.tick_buffer:
            with self.buffer_lock:
                self.tick_buffer[symbol] = deque(maxlen=self.buffer_size)
            logger.info(f"Inizializzato buffer per {symbol}")

        if price <= 0:
            return

        # Calcola delta e direzione
        if len(self.tick_buffer[symbol]) > 0:
            last_price = self.tick_buffer[symbol][-1]['price']
            delta = price - last_price
            direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
        else:
            delta = 0
            direction = 0

        self.tick_buffer[symbol].append({
            'price': price,
            'delta': delta,
            'direction': direction,
            'time': time.time()
        })

        # Log dettagliato per ogni tick
        logger.debug(f"[TICK] {symbol}: price={price}, delta={delta}, direction={direction}, buffer_size={len(self.tick_buffer[symbol])}")

    def get_signal(self, symbol: str, for_trading: bool = False) -> Tuple[str, float]:
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

        # Log dettagliato del buffer e dei prezzi
        last_tick_price = recent_ticks[-1]['price'] if recent_ticks else 0.0
        logger.debug(f"{symbol}: Ultimo prezzo buffer={last_tick_price}, Confidenza calcolata={confidence:.3f}, Spin={spin:.3f}, Buffer size={len(ticks)}")

        # 3. Filtri conservativi (tua logica originale)
        if confidence < 0.8:
            logger.debug(f"{symbol}: Confidence troppo bassa ({confidence:.2f}/0.8) -> HOLD. Prezzo={last_tick_price}")
            return "HOLD", last_tick_price

        # 4. Verifica cooldown segnali (900s)
        last_signal_time = self.last_signal_time.get(symbol, 0)
        if time.time() - last_signal_time < self.signal_cooldown:
            remaining = int(self.signal_cooldown - (time.time() - last_signal_time))
            logger.debug(f"{symbol}: In cooldown segnali ({remaining}s rimanenti) -> HOLD. Prezzo={last_tick_price}")
            return "HOLD", last_tick_price

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
                    f"SELL: E<{sell_thresh:.3f}? {entropy < sell_thresh} & S<{-self.spin_threshold * confidence:.3f}? {spin < -self.spin_threshold * confidence} = {sell_condition} | Prezzo={last_tick_price}")

        if buy_condition:
            signal = "BUY"
        elif sell_condition:
            signal = "SELL"

        # 7. Registrazione segnale (senza influenzare cooldown posizioni)
        if signal != "HOLD":
            # Solo imposta il cooldown se stiamo effettivamente facendo trading
            if for_trading:
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
                f"Cooldown segnale attivato (900s) | Prezzo={last_tick_price}"
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
                            f"and Spin={spin:.2f} < {-self.spin_threshold*confidence:.2f} | Prezzo={last_tick_price}")

        # Restituisci sempre il prezzo reale dell'ultimo tick del buffer
        return signal, last_tick_price
        
        
    """
    4. Controlli di Mercato e Connessione
    """
    

    def check_tick_activity(self):
        """Monitoraggio stato mercato e qualità dati con heartbeat. Log dettagliato se i tick non arrivano."""
        current_time = time.time()
        issues = []
        warning_symbols = []
        heartbeat_data = []

        if not mt5.terminal_info().connected:
            logger.warning("Connessione MT5 non disponibile")
            return False

        # Recupera la lista dei simboli disponibili su MT5
        available_symbols = [s.name for s in mt5.symbols_get() or []]

        for symbol in self._config_manager.symbols:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    # Log dettagliato: nome simbolo, simboli disponibili, visibilità
                    symbol_info = mt5.symbol_info(symbol)
                    is_visible = symbol_info.visible if symbol_info else False
                    logger.warning(
                        f"{symbol}: Nessun dato tick disponibile | "
                        f"Simbolo visibile: {is_visible} | "
                        f"Simboli disponibili: {available_symbols[:10]}..."
                    )
                    issues.append(f"{symbol}: Nessun dato tick disponibile")
                    continue

                spread = (mt5.symbol_info(symbol).ask - mt5.symbol_info(symbol).bid) / self._get_pip_size(symbol) if mt5.symbol_info(symbol) else 0

                ticks = list(self.tick_buffer.get(symbol, []))[-self.spin_window:]

                if len(ticks) >= self.min_spin_samples:
                    deltas = tuple(t['delta'] for t in ticks if abs(t['delta']) > 1e-10)
                    entropy = self.calculate_entropy(deltas)
                    spin = sum(1 for t in ticks if t['direction'] > 0) / len(ticks) * 2 - 1
                    confidence = min(1.0, abs(spin) * np.sqrt(len(ticks)))
                    volatility = 1 + abs(spin) * entropy
                else:
                    entropy, spin, confidence, volatility = 0.0, 0.0, 0.0, 1.0

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

                if is_trading_hours(symbol, self._config_manager.config):
                    max_spread = self._config_manager._get_max_allowed_spread(symbol)
                    if spread > max_spread:
                        issues.append(f"{symbol}: Spread {spread:.1f}p > max {max_spread:.1f}p")

                if len(self.tick_buffer.get(symbol, [])) < self.min_spin_samples:
                    warning_symbols.append(symbol)

            except Exception as e:
                logger.error(f"Errore monitoraggio {symbol}: {str(e)}", exc_info=True)

        if heartbeat_data:
            hb_msg = "HEARTBEAT:\n" + "\n".join(
                f"{d['symbol']}: Bid={d['bid']:.5f} | Ask={d['ask']:.5f} | "
                f"Spread={d['spread']:.1f}p | Buffer={d['buffer_size']} | "
                f"E={d['E']:.2f} | S={d['S']:.2f} | C={d['C']:.2f} | V={d['V']:.2f}"
                for d in heartbeat_data[:5]
            )
            logger.info(hb_msg)
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
3- DailyDrawdownTracker - Monitora il drawdown giornaliero con protezione challenge. 
Può essere inizializzato indipendentemente ma viene utilizzato dal sistema principale.
"""

class DailyDrawdownTracker:
    """Monitoraggio del drawdown giornaliero con protezione challenge"""
    
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
            dd_config = actual_config.get('challenge_specific', {}).get('drawdown_protection', {})
            self.soft_limit = float(dd_config.get('soft_limit', 0.05))
            self.hard_limit = float(dd_config.get('hard_limit', 0.10))
        except Exception as e:
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
        """Calcola dimensione posizione con gestione robusta degli errori e log dettagliato"""
        try:
            # 1. Verifica parametri iniziali
            if not self._load_symbol_data(symbol):
                logger.error(f"Impossibile caricare dati simbolo {symbol}")
                return 0.0

            # 2. Ottieni parametri di rischio NORMALIZZATI
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
            contract_size = symbol_data.get('contract_size', 1.0)

            # 6. Calcola size base
            if sl_pips <= 0 or pip_value <= 0:
                logger.error(f"Valori non validi: sl_pips={sl_pips}, pip_value={pip_value}")
                return 0.0

            size = risk_amount / (sl_pips * pip_value)

            # SAFETY CHECK: Limite massimo assoluto per evitare position sizing eccessivi
            max_size_limit = 0.1  # Massimo 0.1 lotti per posizioni conservative
            if size > max_size_limit:
                logger.warning(f"Size limitata per {symbol}: {size:.2f} -> {max_size_limit} (Safety limit applicato)")
                size = max_size_limit

            # 7. Applica limiti
            size = self._apply_size_limits(symbol, size)

            # Determina tipo strumento per log
            if symbol in ['XAUUSD', 'XAGUSD']:
                symbol_type = 'Metallo'
            elif symbol in ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225']:
                symbol_type = 'Indice'
            else:
                symbol_type = 'Forex'

            logger.debug("\n" +
                "-------------------- [SIZE-DEBUG] --------------------\n" +
                f"Symbol: {symbol} ({symbol_type})\n" +
                f"Risk Amount: ${risk_amount:.2f} ({risk_percent*100:.2f}%)\n" +
                f"SL: {sl_pips:.2f} pips\n" +
                f"Pip Value: ${pip_value:.4f}\n" +
                f"Contract Size: {contract_size}\n" +
                f"Size: {size:.4f}\n" +
                "------------------------------------------------------\n"
            )
            logger.info("\n" +
                "==================== [SIZE-DEBUG] ====================\n" +
                f"Symbol: {symbol} ({symbol_type})\n" +
                f"Risk Amount: ${risk_amount:.2f} ({risk_percent*100:.2f}%)\n" +
                f"SL: {sl_pips:.2f} pips\n" +
                f"Pip Value: ${pip_value:.4f}\n" +
                f"Contract Size: {contract_size}\n" +
                f"Size: {size:.4f}\n" +
                "======================================================\n"
            )

            return size

        except Exception as e:
            logger.error(f"Errore calcolo dimensione {symbol}: {str(e)}", exc_info=True)
            return 0.0
    
       

    def _apply_size_limits(self, symbol: str, size: float) -> float:
        """Applica limiti di dimensione con controllo margine"""
        info = mt5.symbol_info(symbol)
        if not info:
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
        
        logger.info(
            "\n==================== [SIZE-FINALE] ====================\n"
            f"Symbol: {symbol}\n"
            f"Size finale: {size:.2f}\n"
            "======================================================\n"
        )
        
        return size
    

    """
    3. Gestione Stop Loss e Take Profit
    """
    
    def calculate_dynamic_levels(self, symbol: str, position_type: int, entry_price: float) -> Tuple[float, float]:
        try:
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
            profit_multiplier = self._get_config(symbol, 'profit_multiplier', 2.2)

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
            # Ora activation_pips è coerente con la modalità scelta
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
                f"SL: {sl_pips:.1f} pips\n"
                f"TP: {tp_pips:.1f} pips\n"
                f"Entry Price: {entry_price}\n"
                f"Volatility: {volatility:.2f}\n"
                f"Min SL: {min_sl}\n"
                f"Base SL: {base_sl}\n"
                f"Multiplier: {profit_multiplier}\n"
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
        step = self.symbol_data[symbol]['volume_step']
        if step > 0:
            size = round(size / step) * step
        return max(size, self.symbol_data[symbol]['volume_min'])
        
        
        
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
            
            logger.debug(f"Raw data for {symbol}: point={point}, contract_size={contract_size}")
            
            # Calcolo preciso del pip value
            if symbol in ['XAUUSD', 'XAGUSD']:
                # Per XAUUSD: 1 lotto = 100 once, 1 pip = $0.01 per oncia
                # Quindi 1 pip su 1 lotto = $1.00 (100 once x $0.01)
                pip_value = 1.0 * contract_size  # $1.00 per pip per lotto
            elif symbol in ['SP500', 'NAS100', 'US30']:
                # Per indici: 1 pip = $1.0 per lotto standard
                # Con contract_size 0.01 = $1.0 * 0.01 = $0.01 per pip
                pip_value = 1.0 * contract_size  # $1.0 per pip per lotto standard * contract_size
            else:  # Forex (EURUSD, GBPUSD, ecc.)
                # Per forex standard: 1 pip = $10 per lotto standard (100,000 unità)
                # contract_size 0.01 = mini lotto = $10 * 0.01 = $0.10 per pip
                pip_value = 10.0 * contract_size  # $10 per pip per lotto standard * contract_size
            
            self.symbol_data[symbol] = {
                'pip_value': pip_value,
                'volume_step': info.volume_step,
                'digits': info.digits,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'contract_size': contract_size
            }
            
            logger.debug(f"Dati caricati per {symbol}: PipValue=${pip_value:.2f}, ContractSize={contract_size}, Point={point}")
            
            # Log dettagliato per debug
            logger.info(f"SYMBOL CONFIG LOADED - {symbol}: "
                       f"Type={'Forex' if symbol not in ['XAUUSD','XAGUSD','SP500','NAS100','US30'] else 'Special'} | "
                       f"ContractSize={contract_size} | "
                       f"PipValue=${pip_value:.4f} | "
                       f"Point={point}")
            
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
    
    def get_metrics_summary(self) -> dict:
        """Restituisce un riassunto delle metriche di performance"""
        return {
            'total_trades': self.metrics['total_trades'],
            'win_rate': round(self.metrics['win_rate'], 2),
            'avg_profit': round(self.metrics['avg_profit'], 2),
            'max_drawdown': round(self.metrics['max_drawdown'], 2),
            'sharpe_ratio': round(self.metrics['sharpe_ratio'], 2),
            'profit_factor': round(self.metrics['profit_factor'], 2)
        }
    
    def get_symbol_stats(self, symbol: str) -> dict:
        """Restituisce le statistiche per un simbolo specifico"""
        if symbol not in self.metrics['symbol_stats']:
            return {}
        return self.metrics['symbol_stats'][symbol]
    
    def log_performance_report(self):
        """Stampa un report delle performance nei log"""
        summary = self.get_metrics_summary()
        logger.info(f"📊 PERFORMANCE REPORT:")
        logger.info(f"   Trades: {summary['total_trades']}")
        logger.info(f"   Win Rate: {summary['win_rate']}%")
        logger.info(f"   Avg Profit: ${summary['avg_profit']:.2f}")
        logger.info(f"   Max Drawdown: {summary['max_drawdown']}%")
        logger.info(f"   Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        logger.info(f"   Profit Factor: {summary['profit_factor']:.2f}")


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
        print(f"🔧 Inizializzazione QuantumTradingSystem...")
        print(f"📁 File configurazione: {config_path}")
        
        # Inizializzazione base
        self._setup_logger(config_path)
        print("✅ Logger configurato")
        
        self._config_path = config_path
        self.running = False
        
        # Caricamento configurazione
        print("📋 Caricamento configurazione...")
        self._load_configuration(config_path)  # Questo inizializza self.config
        print("✅ Configurazione caricata")
        
        # Verifica configurazione minima
        if not hasattr(self.config, 'config') or 'symbols' not in self.config.config:
            logger.error("Configurazione simboli non valida nel file di configurazione")
            raise ValueError("Sezione symbols mancante nella configurazione")
        
        print(f"🎯 Simboli trovati: {list(self.config.config['symbols'].keys())}")
        
        # Inizializzazione componenti core
        print("🔄 Inizializzazione componenti core...")
        self.config_manager = ConfigManager(config_path)
        self._config = self.config_manager.config
        
        # Inizializzazione MT5
        if not self._initialize_mt5():
            raise RuntimeError("Inizializzazione MT5 fallita")

        # Attiva automaticamente i simboli in MT5 (dopo l'inizializzazione!)
        print("📡 Attivazione simboli in MT5...")
        self._activate_symbols()
        print("✅ Simboli attivati")

        print("🧠 Inizializzazione Quantum Engine...")
        self.engine = QuantumEngine(self.config_manager)
        print("✅ Quantum Engine pronto")
        self.risk_manager = QuantumRiskManager(self.config_manager, self.engine, self)  # Passa self come terzo parametro

        self.max_positions = self.config_manager.get_risk_params().get('max_positions', 4)
        self.current_positions = 0
        self.trade_count = defaultdict(int)

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
            logger.error(f"Errore caricamento configurazione: {str(e)}")
            raise
            
            

    def _initialize_mt5(self) -> bool:
        """Connessione a MetaTrader 5 con configurazione specifica challenge"""
        try:
            # Chiudi eventuali connessioni precedenti
            mt5.shutdown()
            
            # Ottieni configurazione MT5 specifica
            mt5_config = self.config.config.get('metatrader5', {})
            
            # Inizializza con parametri specifici challenge
            if not mt5.initialize(
                path=mt5_config.get('path', 'C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe'),
                login=int(mt5_config.get('login', 0)),
                password=mt5_config.get('password', ''),
                server=mt5_config.get('server', 'FivePercentOnline-Real'),
                timeout=60000,
                port=int(mt5_config.get('port', 18889))
            ):
                logger.error(f"Inizializzazione MT5 challenge fallita: {mt5.last_error()}")
                return False
            
            terminal_info = mt5.terminal_info()
            if not terminal_info:
                logger.error("Impossibile ottenere info terminal MT5")
                return False
                
            logger.info(f"MT5 challenge inizializzato: {terminal_info.company} - {terminal_info.name}")
            logger.info(f"Server: {mt5_config.get('server')} | Porta: {mt5_config.get('port')} | Login: {mt5_config.get('login')}")
            return True
            
        except Exception as e:
            logger.error(f"Errore inizializzazione MT5 challenge: {str(e)}")
            return False

    """
    2. Gestione Connessione e Ambiente
    """

    def _verify_connection(self) -> bool:
        """Verifica/connessione MT5 - Verifica la connessione MT5 con ripristino automatico"""
        try:
            if not mt5.terminal_info() or not mt5.terminal_info().connected:
                logger.warning("Connessione MT5 challenge persa, tentativo di riconnessione...")
                mt5.shutdown()
                time.sleep(2)
                
                # Usa la stessa logica di _initialize_mt5 per riconnessione
                mt5_config = self.config.config.get('metatrader5', {})
                return mt5.initialize(
                    path=mt5_config.get('path', 'C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe'),
                    login=int(mt5_config.get('login', 0)),
                    password=mt5_config.get('password', ''),
                    server=mt5_config.get('server', 'FivePercentOnline-Real'),
                    timeout=60000,
                    port=int(mt5_config.get('port', 18889))
                )
            return True
        except Exception as e:
            logger.error(f"Errore verifica connessione challenge: {str(e)}")
            return False

    """
    3. Core del Trading System            
    """        
        
    def start(self):
        """Avvia il sistema"""
        print("🚀 ==> AVVIO QUANTUM TRADING SYSTEM <== 🚀")
        try:
            if not hasattr(self, 'config') or not hasattr(self.config, 'symbols'):
                raise RuntimeError("Configurazione non valida - simboli mancanti")
                
            print(f"📋 Sistema con {len(self.config.symbols)} simboli configurati")
            print(f"🎯 Simboli: {self.config.symbols}")  # Mostra la lista direttamente
            logger.info(f"Avvio sistema con {len(self.config.symbols)} simboli")
            
            if not hasattr(self, 'engine') or not hasattr(self, 'risk_manager'):
                raise RuntimeError("Componenti critici non inizializzati")
            
            print("✅ Componenti critici inizializzati correttamente")
            self.running = True
            logger.info("Sistema di trading avviato correttamente")
            
            print("🔄 Inizio loop principale...")
            
            while self.running:
                try:
                    self._main_loop()
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("Arresto richiesto dall'utente")
                    self.running = False
                except Exception as e:
                    logger.error(f"Errore durante l'esecuzione: {str(e)}", exc_info=True)
                    print(f"❌ Errore nel loop: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            logger.critical(f"Errore fatale: {str(e)}", exc_info=True)
            print(f"💀 Errore fatale: {e}")
            import traceback
            traceback.print_exc()
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
                
                # Debug periodico dello stato trading
                for symbol in self.config_manager.symbols:
                    self.debug_trade_status(symbol)
                    break  # Solo il primo simbolo per non spammare
                
                
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
                logger.debug(
                    "\n-------------------- [DEBUG TICK] ----------------------\n"
                    f"Symbol: {symbol}\n"
                    f"Tick: {tick}\n"
                    "------------------------------------------------------\n"
                )
                if tick:
                    logger.debug(
                        "\n-------------------- [DEBUG TICK] ----------------------\n"
                        f"Symbol: {symbol}\n"
                        f"Tick.bid: {getattr(tick, 'bid', None)}\n"
                        "------------------------------------------------------\n"
                    )
                    self.engine.process_tick(symbol, tick.bid)
                    buffer_size = len(self.engine.tick_buffer.get(symbol, []))
                    logger.debug(
                        "\n-------------------- [BUFFER-DEBUG] --------------------\n"
                        f"Symbol: {symbol}\n"
                        f"Buffer Size: {buffer_size}\n"
                        "------------------------------------------------------\n"
                    )
                
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
                raise
            except Exception as e:
                logger.critical(f"Errore critico nel main loop: {str(e)}")
                time.sleep(10)

    def _process_symbols(self):
        """Processa tutti i simboli configurati"""
        current_positions = len(mt5.positions_get() or [])
        
        for symbol in self.config_manager.symbols:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    continue
                    
                if not self._validate_tick(tick):
                    continue
                    
                self._process_single_symbol(symbol, tick, current_positions)
                
            except Exception as e:
                logger.error(f"Errore processamento {symbol}: {str(e)}", exc_info=True)
                
    def _process_single_symbol(self, symbol: str, tick, current_positions: int):
        """Processa un singolo simbolo per segnali di trading"""
        try:
            # 1. Verifica se possiamo fare trading
            if not self.engine.can_trade(symbol):
                return

            # 1.1. Controllo limite trade giornalieri (opzionale: globale o per simbolo)
            risk_params = self.config_manager.config['risk_parameters']
            daily_limit = risk_params.get('max_daily_trades', 5)
            # Nuovo parametro opzionale: 'daily_trade_limit_mode' ('global' o 'per_symbol')
            limit_mode = risk_params.get('daily_trade_limit_mode', 'global')
            if limit_mode == 'global':
                total_trades_today = sum(self.trade_count.values())
                if total_trades_today >= daily_limit:
                    logger.info(f"🚫 Limite totale trade giornalieri raggiunto: {total_trades_today}/{daily_limit}. Nessun nuovo trade verrà aperto oggi.")
                    return
            else:  # per_symbol
                trades_for_symbol = self.trade_count.get(symbol, 0)
                if trades_for_symbol >= daily_limit:
                    logger.info(f"🚫 Limite trade giornalieri per {symbol} raggiunto: {trades_for_symbol}/{daily_limit}. Nessun nuovo trade su questo simbolo oggi.")
                    return

            # 2. Verifica orari di trading
            if not is_trading_hours(symbol, self.config_manager.config):
                return

            # 3. Verifica posizioni esistenti
            existing_positions = mt5.positions_get(symbol=symbol)
            if existing_positions and len(existing_positions) > 0:
                return

            # 4. Verifica limite posizioni totali
            if current_positions >= self.max_positions:
                return

            # 5. Ottieni segnale (senza attivare cooldown)
            signal, price = self.engine.get_signal(symbol, for_trading=False)

            logger.debug(f"🔍 Segnale per {symbol}: {signal} (Price: {price})")

            if signal in ["BUY", "SELL"]:
                logger.info(f"🎯 SEGNALE ATTIVO {signal} per {symbol} - Controllo condizioni trading")

                # 5.1 Verifica cooldown segnale PRIMA di procedere
                if hasattr(self.engine, 'last_signal_time') and symbol in self.engine.last_signal_time:
                    time_since_last = time.time() - self.engine.last_signal_time[symbol]
                    if time_since_last < self.engine.signal_cooldown:
                        logger.info(f"⏰ {symbol}: In cooldown, salto trade (tempo rimanente: {self.engine.signal_cooldown - time_since_last:.1f}s)")
                        return

                # 5.2 Se tutto ok, ottieni segnale per trading (questo attiva il cooldown)
                trading_signal, trading_price = self.engine.get_signal(symbol, for_trading=True)

                if trading_signal in ["BUY", "SELL"]:
                    logger.info(f"✅ Segnale confermato per trading: {trading_signal}")

                    # 6. Calcola dimensione posizione
                    size = self.risk_manager.calculate_position_size(symbol, trading_price, trading_signal)

                    logger.info(f"💰 Size calcolata per {symbol}: {size} lots")

                    if size > 0:
                        logger.info(f"✅ Esecuzione trade autorizzata per {symbol} - Size: {size}")
                        # 7. Esegui il trade
                        success = self._execute_trade(symbol, trading_signal, tick, trading_price, size)
                        if success:
                            logger.info(f"🎉 Trade {symbol} eseguito con successo!")
                        else:
                            logger.error(f"❌ Trade {symbol} fallito durante esecuzione")
                    else:
                        logger.warning(f"⚠️ Trade {symbol} bloccato: size = 0")
                else:
                    logger.warning(f"🚫 {symbol}: Segnale non confermato per trading effettivo")
            else:
                logger.debug(f"💤 {symbol}: HOLD - nessuna azione")

        except Exception as e:
            logger.error(f"Errore processo simbolo {symbol}: {str(e)}", exc_info=True)

    def _execute_trade(self, symbol: str, signal: str, tick, price: float, size: float) -> bool:
        """Esegue un trade con gestione completa degli errori"""
        try:
            logger.info(f"🚀 INIZIO ESECUZIONE TRADE: {signal} {symbol} | Size: {size} | Price: {price}")
            
            # 1. Nota: can_trade() già verificato in _process_single_symbol()
            # Rimuoviamo il controllo ridondante che causa il blocco
            
            # 2. Determina tipo ordine
            order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
            
            # 3. Calcola livelli SL/TP
            sl_price, tp_price = self.risk_manager.calculate_dynamic_levels(
                symbol, order_type, price
            )
            
            # 4. Prepara richiesta ordine
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
                "magic": self.config.config['magic_number'],
                "comment": "QTS-AUTO",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,  # Prova FOK prima, poi IOC se fallisce
            }
            
            # 5. Esegui ordine con fallback per filling mode
            logger.info(f"Esecuzione {signal} {symbol}: {size} lots @ {execution_price}")
            result = mt5.order_send(request)
            
            # Se fallisce per filling mode, prova con metodo alternativo
            if result.retcode == 10030:  # Unsupported filling mode
                logger.warning(f"Filling mode FOK non supportato per {symbol}, provo con IOC")
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                result = mt5.order_send(request)
                
                if result.retcode == 10030:  # Ancora problemi
                    logger.warning(f"Filling mode IOC non supportato per {symbol}, provo Return")
                    request["type_filling"] = mt5.ORDER_FILLING_RETURN
                    result = mt5.order_send(request)
            
            # 6. Verifica risultato
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Trade fallito {symbol}: {result.retcode} - {result.comment}")
                return False
                
            logger.info(f"Trade eseguito {symbol} {size} lots a {execution_price} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")
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
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Errore esecuzione trade {symbol}: {str(e)}", exc_info=True)
            return False

    """
    4. Gestione Ordini e Posizioni
    """

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
        """Monitoraggio avanzato delle posizioni aperte"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
                
            for position in positions:
                try:
                    # Verifica che la posizione esista ancora
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
        try:
            positions = mt5.positions_get(ticket=ticket)
            return positions is None or len(positions) == 0
        except Exception as e:
            logger.error(f"Errore verifica posizione {ticket}: {str(e)}")
            return False

    def _manage_trailing_stop(self, position, current_price: float) -> bool:
        """Gestione avanzata del trailing stop con gestione errori migliorata"""
        try:
            # Verifica se trailing stop è abilitato
            risk_config = self.risk_manager.get_risk_config(position.symbol)
            trailing_config = risk_config.get('trailing_stop', {})
            
            if not trailing_config.get('enable', False):
                return False
                
            # Calcola profit corrente in pips
            pip_size = self.engine._get_pip_size(position.symbol)
            if position.type == mt5.ORDER_TYPE_BUY:
                profit_pips = (current_price - position.price_open) / pip_size
            else:
                profit_pips = (position.price_open - current_price) / pip_size
                
            # Verifica soglia di attivazione
            activation_pips = trailing_config.get('activation_pips', 150)
            if profit_pips < activation_pips:
                return False
                
            # Calcola nuovo SL
            trailing_distance = trailing_config.get('distance_pips', 100)
            
            if position.type == mt5.ORDER_TYPE_BUY:
                new_sl = current_price - (trailing_distance * pip_size)
                # Solo se migliore del SL attuale
                if position.sl == 0 or new_sl > position.sl:
                    return self._modify_position(position, sl=new_sl)
            else:
                new_sl = current_price + (trailing_distance * pip_size)
                # Solo se migliore del SL attuale
                if position.sl == 0 or new_sl < position.sl:
                    return self._modify_position(position, sl=new_sl)
                    
            return False
            
        except Exception as e:
            logger.error(f"Errore trailing stop posizione {position.ticket}: {str(e)}")
            return False

    def _check_position_timeout(self, position):
        """Controlla timeout posizione con gestione robusta dei timestamp"""
        try:
            # Ottieni configurazione timeout
            risk_config = self.risk_manager.get_risk_config(position.symbol)
            max_hours = risk_config.get('position_timeout_hours', 24)
            
            # Gestione robusta dei timestamp
            if hasattr(position, 'time_setup'):
                timestamp = position.time_setup
            elif hasattr(position, 'time'):
                timestamp = position.time
            else:
                logger.error(f"Posizione {position.ticket} senza timestamp valido")
                return
                
            # Converti timestamp in datetime
            if isinstance(timestamp, (int, float)):
                if timestamp > 1e10:  # Assume milliseconds
                    position_dt = datetime.fromtimestamp(timestamp / 1000)
                else:  # Assume seconds
                    position_dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, datetime):
                position_dt = timestamp
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
            # Verifica che la posizione esista ancora
            current_pos = mt5.positions_get(ticket=position.ticket)
            if not current_pos or len(current_pos) == 0:
                logger.debug(f"Posizione {position.ticket} non più esistente")
                return False
                
            # Prepara richiesta di modifica
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": sl if sl is not None else position.sl,
                "tp": tp if tp is not None else position.tp,
            }
            
            # Validazione livelli
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                return False
                
            # Arrotonda ai decimali corretti
            if request["sl"] != 0:
                request["sl"] = round(request["sl"], symbol_info.digits)
            if request["tp"] != 0:
                request["tp"] = round(request["tp"], symbol_info.digits)
                
            # Esegui modifica
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Posizione {position.ticket} modificata: SL={request['sl']}, TP={request['tp']}")
                return True
            else:
                logger.warning(f"Modifica posizione {position.ticket} fallita: {result.retcode}")
                return False
                
        except Exception as e:
            logger.error(f"Errore modifica posizione {position.ticket}: {str(e)}")
            return False

    def _validate_positions(self):
        """Verifica posizioni duplicate"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
                
            symbol_positions = defaultdict(list)
            for pos in positions:
                symbol_positions[pos.symbol].append(pos)
                
            for symbol, pos_list in symbol_positions.items():
                if len(pos_list) > 1:
                    logger.warning(f"Posizioni duplicate per {symbol}: {[p.ticket for p in pos_list]}")
                    
        except Exception as e:
            logger.error(f"Errore validazione posizioni: {str(e)}")

    """
    6. Risk Management
    """

    def _update_account_info(self):
        """Aggiorna info account"""
        try:
            self.account_info = mt5.account_info()
            if self.account_info and hasattr(self, 'drawdown_tracker'):
                self.drawdown_tracker.update(
                    self.account_info.equity,
                    self.account_info.balance
                )
        except Exception as e:
            logger.error(f"Errore aggiornamento account: {str(e)}")
                    
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

    """
    8. Validazioni
    """
    
    def _validate_tick(self, tick) -> bool:
        """Aggiungi controllo per evitare bias di direzione"""
        if not tick:
            return False
            
        # Verifica che il prezzo sia valido
        if tick.bid <= 0 or tick.ask <= 0:
            return False
            
        # Verifica spread ragionevole
        spread = tick.ask - tick.bid
        if spread <= 0 or spread > tick.bid * 0.1:  # Max 10% spread
            return False
            
        return True

    def _validate_symbol(self, symbol: str) -> bool:
        """Validazione avanzata per strategia tick-based"""
        # 1. Verifica base simbolo
        if not symbol or len(symbol) < 3:
            return False
            
        # 2. Verifica MT5 info
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.debug(f"Simbolo {symbol} non disponibile in MT5")
            return False
            
        # 3. Verifica tick corrente
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.info(f"Nessun tick disponibile per {symbol}")
            return False
        
        if tick.time_msc < (time.time() - 60)*1000:  # Se il tick è più vecchio di 60s
            logger.debug(f"Dati tick obsoleti per {symbol} ({(time.time()*1000 - tick.time_msc)/1000:.1f}s)")
            return False

        # 4. Controllo spread e liquidità
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return False
            
        spread = (symbol_info.ask - symbol_info.bid) / self.engine._get_pip_size(symbol)
        max_spread = self.config_manager._get_max_allowed_spread(symbol)
        
        if spread > max_spread * 1.2:  # Tolleranza +20%
            logger.debug(f"Spread {spread:.1f}p troppo alto per {symbol} (max {max_spread:.1f}p)")
            return False

        # 6. Verifica buffer dati sufficiente
        if len(self.engine.tick_buffer.get(symbol, [])) < self.engine.min_spin_samples:
            logger.debug(f"Dati insufficienti nel buffer per {symbol}")
            return False

        return True

    """
    6. Utility e Helper Methods
    """

    def debug_trade_status(self, symbol: str):
        """Debug dello stato di trading per un simbolo specifico"""
        try:
            # Verifica can_trade
            can_trade = self.engine.can_trade(symbol)
            
            # Verifica orari
            trading_hours = is_trading_hours(symbol, self.config_manager.config)
            
            # Verifica posizioni esistenti
            positions = mt5.positions_get(symbol=symbol)
            has_position = positions and len(positions) > 0
            
            # Verifica limite trades giornalieri
            daily_count = self.trade_count.get(symbol, 0)
            daily_limit = self.config_manager.config['risk_parameters']['max_daily_trades']
            
            # Verifica buffer
            buffer_size = len(self.engine.tick_buffer.get(symbol, []))
            min_samples = self.engine.min_spin_samples
            
            # non funziona stampa solo il primo simbolo EURUSD, non c'è un loop lo commento
            """
            logger.info(f"🔍 TRADE STATUS {symbol}: can_trade={can_trade}, trading_hours={trading_hours}, "
                        f"has_position={has_position}, daily_trades={daily_count}/{daily_limit}, "
                        f"buffer={buffer_size}/{min_samples}")
            """

                        
        except Exception as e:
            logger.error(f"Errore debug_trade_status per {symbol}: {str(e)}")
    
    def check_challenge_limits(self):
        """Controlla i limiti imposti dal broker challenge"""
        account_info = mt5.account_info()
        if not account_info:
            logger.error("Impossibile ottenere info account MT5")
            return False

        # Calcola equity, balance, drawdown, profit
        equity = account_info.equity
        balance = account_info.balance
        initial_balance = self.config.config.get('initial_balance', balance)
        max_daily_loss = initial_balance * self.config.config.get('challenge_specific', {}).get('max_daily_loss_percent', 0) / 100
        max_total_loss = initial_balance * self.config.config.get('challenge_specific', {}).get('max_total_loss_percent', 0) / 100
        profit_target = initial_balance * self.config.config.get('challenge_specific', {}).get('step1_target', 0) / 100

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
            return False

        return True

    def get_daily_loss(self, day):
        """Calcola la perdita giornaliera (stub, da implementare con storico trades)"""
        return 0

    def close_positions_before_weekend(self):
        """Chiude tutte le posizioni aperte il venerdì sera prima della chiusura dei mercati"""
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

    def check_buffers(self):
        """Controlla lo stato dei buffer di ogni simbolo"""
        for symbol in self.config_manager.symbols:
            buffer = self.engine.tick_buffer.get(symbol, [])
            logger.debug(f"Buffer {symbol}: {len(buffer)} ticks")


if __name__ == "__main__":
    try:
        # Carica la configurazione prima di tutto
        system = QuantumTradingSystem(CONFIG_FILE)
        system.start()
    except Exception as e:
        logger.critical(f"Errore iniziale: {str(e)}", exc_info=True)
    finally:
        logger.info("Applicazione terminata")