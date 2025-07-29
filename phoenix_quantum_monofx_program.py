
import os
# debug estremo iniziale

#print("[DEBUG] Inizio esecuzione modulo phoenix_quantum_monofx_program.py")

#print("[DEBUG-TRACE] Prima di import os")
import os
#print("[DEBUG-TRACE] Dopo import os")
#print("[DEBUG-TRACE] Prima di import json")
import json
#print("[DEBUG-TRACE] Dopo import json")
#print("[DEBUG-TRACE] Prima di import logging")
import logging
#print("[DEBUG-TRACE] Dopo import logging")
#print("[DEBUG-TRACE] Prima di import time")
import time
#print("[DEBUG-TRACE] Dopo import time")


#print("[DEBUG] Import base completati")

#print("[DEBUG-TRACE] Prima di import datetime")
from datetime import datetime, time as dt_time, timedelta
#print("[DEBUG-TRACE] Dopo import datetime")
#print("[DEBUG-TRACE] Prima di import typing")
from typing import Dict, Tuple, List, Any, Optional
#print("[DEBUG-TRACE] Dopo import typing")
#print("[DEBUG-TRACE] Prima di import collections")
from collections import deque, defaultdict
#print("[DEBUG-TRACE] Dopo import collections")
#print("[DEBUG-TRACE] Prima di import RotatingFileHandler")
try:
    from logging.handlers import RotatingFileHandler
    #print("[DEBUG-TRACE] Dopo import RotatingFileHandler")
except Exception as e:
    print(f"[IMPORT ERROR] logging.handlers: {e}")
#print("[DEBUG-TRACE] Prima di import lru_cache")
try:
    from functools import lru_cache
    #print("[DEBUG-TRACE] Dopo import lru_cache")
except Exception as e:
    print(f"[IMPORT ERROR] functools.lru_cache: {e}")
#print("[DEBUG-TRACE] Prima di import threading")
try:
    import threading
    #print("[DEBUG-TRACE] Dopo import threading")
except Exception as e:
    print(f"[IMPORT ERROR] threading: {e}")
#print("[DEBUG-TRACE] Prima di import traceback")
try:
    import traceback
    #print("[DEBUG-TRACE] Dopo import traceback")
except Exception as e:
    print(f"[IMPORT ERROR] traceback: {e}")
#print("[DEBUG-TRACE] Prima di import numpy as np")
try:
    import numpy as np
    #print("[DEBUG-TRACE] Dopo import numpy as np")
except Exception as e:
    print(f"[IMPORT ERROR] numpy: {e}")


# Dipendenze esterne/metatrader5
#print("[DEBUG] Prima del blocco import MT5")
try:
    import MetaTrader5 as mt5
    #print("[DEBUG] Import MT5 completato")
except ImportError as e:
    print(f"[IMPORT ERROR] {e}. Alcune funzionalità potrebbero non funzionare correttamente.")

# Stub temporanei per funzioni mancanti
def auto_correct_symbols(config):
    """Stub temporaneo: restituisce la config senza modifiche."""
    return config

def validate_config(config):
    """Stub temporaneo: non fa nulla, da implementare."""
    pass



# ===================== CONFIGURAZIONI GLOBALI E COSTANTI =====================
# Tutte le costanti di sistema sono centralizzate qui per chiarezza e manutenzione
#print("[DEBUG] Prima di calcolare PROJECT_ROOT e costanti globali")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE: str = os.path.join(PROJECT_ROOT, "config", "config_autonomous_challenge_production_ready.json")
DEFAULT_CONFIG_RELOAD_INTERVAL: int = 900  # secondi (15 minuti)
DEFAULT_LOG_FILE: str = "logs/default.log"
DEFAULT_LOG_MAX_SIZE_MB: int = 10
DEFAULT_LOG_BACKUP_COUNT: int = 5
DEFAULT_LOG_MAX_BACKUPS: int = 10
DEFAULT_TRADING_HOURS: str = "00:00-24:00"
DEFAULT_TIME_RANGE: tuple = (0, 0, 23, 59)  # (h1, m1, h2, m2)
#print("[DEBUG] Costanti globali definite")

# ===================== STUB FUNZIONI DI UTILITÀ MANCANTI =====================
# Queste funzioni sono placeholder per evitare errori di import/esecuzione.
# TODO: Sostituire con implementazioni reali o import corretti.
def load_config(path: str = CONFIG_FILE):
    """Stub: Carica la configurazione da file JSON."""
    from types import SimpleNamespace
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Se già ha la chiave 'config', wrappo in un oggetto
            if 'config' in data:
                return SimpleNamespace(config=data['config'])
            else:
                return SimpleNamespace(config=data)
    except Exception as e:
        print(f"[load_config] Errore caricamento config: {e}")
        return SimpleNamespace(config={})

def set_config(config):
    """Stub: imposta la configurazione globale."""
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = config

def set_log_file(log_file):
    """Stub: imposta il file di log."""
    global _LOG_FILE
    _LOG_FILE = log_file

def get_log_file():
    """Restituisce il file di log attuale dalla configurazione, con fallback."""
    # Prova a recuperare dalla configurazione globale
    config = globals().get('_GLOBAL_CONFIG', None)
    if config is not None:
        # Supporta sia SimpleNamespace che dict
        conf = getattr(config, 'config', config)
        log_file = None
        if isinstance(conf, dict):
            log_file = conf.get('logging', {}).get('log_file')
        if log_file:
            return log_file
    # Fallback su variabile globale o default
    return globals().get('_LOG_FILE', DEFAULT_LOG_FILE)

def set_logger(logger_obj):
    """Stub: imposta il logger globale."""
    global logger
    logger = logger_obj

def setup_logger(config_path=None):
    """Crea e restituisce un logger base. Accetta un argomento opzionale per compatibilità futura."""
    logger = logging.getLogger("phoenix_quantum")
    if not logger.handlers:
        # Handler per console
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        # Handler per file
        try:
            from logging.handlers import RotatingFileHandler
            log_file = get_log_file()
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"[LOGGING ERROR] Impossibile aggiungere RotatingFileHandler: {e}")
    # Imposta il livello di log dinamicamente dal file di configurazione se presente
    log_level = None
    try:
        import json
        if config_path and isinstance(config_path, str):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'config' in data:
                    log_level = data['config'].get('logging', {}).get('log_level', None)
                else:
                    log_level = data.get('logging', {}).get('log_level', None)
        else:
            config = globals().get('_GLOBAL_CONFIG', None)
            if config is not None:
                conf = getattr(config, 'config', config)
                log_level = conf.get('logging', {}).get('log_level', None)
    except Exception:
        pass
    level_map = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET
    }
    if log_level:
        logger.setLevel(level_map.get(str(log_level).upper(), logging.INFO))
    else:
        logger.setLevel(logging.INFO)
    return logger

def get_logger():
    """Stub: restituisce il logger globale."""
    return globals().get('logger', setup_logger())


def clean_old_logs():
    pass

# ===================== CONFIG MANAGER (RIPRISTINATO) =====================
class ConfigManager:
    def __init__(self, config_path: str):
        self._lock = threading.Lock()
        self._config_path = config_path
        self._config = self._load_configuration(config_path)
        self._validate_config(self._config)

    def _load_configuration(self, config_path):
        if not os.path.isabs(config_path):
            project_root = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.abspath(os.path.join(project_root, 'config', os.path.basename(config_path)))
        with open(config_path) as f:
            loaded = json.load(f)
        return loaded

    def _validate_config(self, config):
        required_top = ["logging", "metatrader5", "quantum_params", "risk_parameters", "symbols"]
        for key in required_top:
            if key not in config:
                raise ValueError(f"Parametro mancante nella configurazione: '{key}'")
        # Logica di fallback e default per metatrader5
        mt5_conf = config.get("metatrader5", {})
        mt5_defaults = {
            "login": 0,
            "password": "",
            "server": "",
            "path": "",
            "port": 0
        }
        for k, v in mt5_defaults.items():
            if k not in mt5_conf:
                mt5_conf[k] = v
                logger.warning(f"[Config] {k} non trovato in metatrader5, uso default {v}")
        config["metatrader5"] = mt5_conf

    @property
    def config(self):
        with self._lock:
            return self._config

    def get(self, key, default=None):
        with self._lock:
            return self._config.get(key, default)

    def set(self, key, value):
        with self._lock:
            self._config[key] = value

    def get_risk_params(self, symbol: Optional[str] = None) -> Dict:
        with self._lock:
            base = self._config.get('risk_parameters', {})
            if not symbol:
                return base
            symbol_config = self._config.get('symbols', {}).get(symbol, {}).get('risk_management', {})
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
        log_conf["backup_count"] = 5
        logger.warning("[Config] backup_count non trovato o troppo basso, uso default 5")




## --- Tutte le funzioni e classi rimangono qui ---

# --- Avvio sistema solo se eseguito come script principale ---

# --- Avvio sistema solo se eseguito come script principale ---
def main():
    print("[DEBUG] Inizio main()")
    set_config(auto_correct_symbols(load_config()))
    print("[DEBUG] Configurazione caricata e impostata")

    def periodic_reload_config(interval: int = DEFAULT_CONFIG_RELOAD_INTERVAL) -> None:
        while True:
            time.sleep(interval)
            try:
                new_config = load_config()
                set_config(auto_correct_symbols(new_config))
                print(f"[{datetime.now()}] Configurazione ricaricata.")
            except Exception as e:
                print(f"Errore reload config: {e}")

    reload_thread = threading.Thread(target=periodic_reload_config, daemon=True)
    reload_thread.start()
    print("[DEBUG] Thread di reload configurazione avviato")

    set_log_file(get_log_file())
    print("[DEBUG] Log file impostato")
    set_logger(setup_logger())
    print("[DEBUG] Logger impostato")
    clean_old_logs()
    print("[DEBUG] Pulizia vecchi log eseguita")
    global logger
    logger = get_logger()
    print("[DEBUG] Logger globale ottenuto")

    # --- TEST LOGGING CONFIGURAZIONE ---
    logger.debug("[TEST] Questo è un messaggio DEBUG (dovrebbe vedersi solo se log_level=DEBUG)")
    logger.info("[TEST] Questo è un messaggio INFO (dovrebbe vedersi se log_level=INFO o inferiore)")
    logger.warning("[TEST] Questo è un messaggio WARNING (dovrebbe vedersi sempre)")
    logger.error("[TEST] Questo è un messaggio ERROR (dovrebbe vedersi sempre)")
    logger.critical("[TEST] Questo è un messaggio CRITICAL (dovrebbe vedersi sempre)")
    print("[LOG TEST] Livello logger:", logger.level)
    for h in logger.handlers:
        print("[LOG TEST] Handler:", h, "Level:", h.level)
    print("[DEBUG] Fine main() - setup completato")



# --- Esegui solo se eseguito come script principale ---
if __name__ == "__main__":
    main()

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
        logger.error(f"[parse_time] Formato orario non valido: {time_str} | Errore: {str(e)}", exc_info=True)
        h1, m1, h2, m2 = DEFAULT_TIME_RANGE
        return dt_time(h1, m1), dt_time(h2, m2)  # Default 24h

def is_trading_hours(symbol: str, config: dict) -> bool:
    """Versione compatibile con sessioni multiple"""
    global logger
    try:
        logger
    except NameError:
        import logging
        logger = logging.getLogger("phoenix_quantum")
    try:
        import pytz
        import holidays
        symbol_config = config.get('symbols', {}).get(symbol, {})
        trading_hours = symbol_config.get('trading_hours', [DEFAULT_TRADING_HOURS])
        timezone_str = symbol_config.get('timezone', 'Europe/Rome')
        tz = pytz.timezone(timezone_str)
        now_dt = datetime.now(tz)
        now = now_dt.time()
        today = now_dt.date()
        debug_ranges = []
        # Festività nazionali (Italia di default, configurabile)
        country = symbol_config.get('holiday_country', 'IT')
        holiday_calendar = holidays.country_holidays(country)
        if today in holiday_calendar:
            logger.info(f"[{symbol}] Oggi è festivo ({today}): {holiday_calendar.get(today)}")
            return False
        for time_range in trading_hours:
            if isinstance(time_range, str):  # Formato legacy "HH:MM-HH:MM"
                start, end = parse_time(time_range)
                debug_ranges.append(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")
                if start <= end:
                    if start <= now <= end:
                        logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} {timezone_str} - INTERVALLO: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} -> OK")
                        return True
                else:  # Overnight (es. 22:00-02:00)
                    if now >= start or now <= end:
                        logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} {timezone_str} - INTERVALLO: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} (overnight) -> OK")
                        return True
            elif isinstance(time_range, list):  # Nuovo formato ["HH:MM", "HH:MM"]
                start, end = parse_time("-".join(time_range))
                debug_ranges.append(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")
                if start <= now <= end:
                    logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} {timezone_str} - INTERVALLO: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} (list) -> OK")
                    return True
        logger.debug(f"[{symbol}] ORA: {now.strftime('%H:%M:%S')} {timezone_str} - FUORI ORARIO. Intervalli validi: {debug_ranges}")
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
    def __init__(self, config_path: str) -> None:
        """Costruttore principale thread-safe"""
        from threading import Lock
        logger.info(
            "\n==================== [AVVIO QUANTUM TRADING SYSTEM] ====================\n"
            f"File configurazione: {config_path}\n"
            "------------------------------------------------------\n"
        )
        self._setup_logger(config_path)
        logger.info("✅ Logger configurato")
        self._config_path = config_path
        self.running = False
        logger.info("📋 Caricamento configurazione...")
        self._load_configuration(config_path)  # Questo inizializza self.config
        # Validazione automatica della configurazione
        try:
            validate_config(self.config.config)
            logger.info("✅ Configurazione caricata e validata")
        except Exception as e:
            logger.critical(f"Errore di validazione configurazione: {e}")
            raise
        if not hasattr(self.config, 'config') or 'symbols' not in self.config.config:
            pass
        logger.info(
            "\n-------------------- [SIMBOLI CONFIGURATI] ----------------------\n"
            f"Simboli trovati: {list(self.config.config['symbols'].keys())}\n"
            "------------------------------------------------------\n"
        )
        self._config = self.config
        logger.info("🔄 Inizializzazione componenti core...")
        if not self._initialize_mt5():
            pass
        logger.info("📡 Attivazione simboli in MT5...")
        self._activate_symbols()
        logger.info("✅ Simboli attivati")
        logger.info("🧠 Inizializzazione Quantum Engine...")
        self.engine = QuantumEngine(self)
        # Stampa subito il report segnali (anche vuoto) nel main thread
        if hasattr(self.engine, '_flush_signal_report'):
            self.engine._flush_signal_report(force_empty=True, startup=True)
            logger.info("[DEBUG] Chiamata a _flush_signal_report(force_empty=True, startup=True) eseguita nel main thread")
        self.engine.start_signal_reporting()
        logger.info("✅ Quantum Engine pronto")
        self.risk_manager = QuantumRiskManager(self, self.engine, self)  # Passa self come terzo parametro
        self.max_positions = self.get_risk_params().get('max_positions', 4)
        # Locks per variabili runtime
        self._trade_count_lock = Lock()
        self._current_positions_lock = Lock()
        self._metrics_lock = Lock()
        self._trade_metrics_lock = Lock()
        # Variabili protette
        self._current_positions = 0
        self._trade_count = defaultdict(int)
        self._metrics = TradingMetrics()
        self.account_info = mt5.account_info()
        self.currency = (
            self.account_info.currency 
            if self.account_info 
            else self.config.config.get('account_currency', 'USD')
        )
        if not self.account_info:
            pass
        self._trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'symbol_stats': defaultdict(dict)
        }
        initial_equity = self.account_info.equity if self.account_info else 10000

    # Getter/setter thread-safe per current_positions
    def get_current_positions(self) -> int:
        with self._current_positions_lock:
            return self._current_positions
    def set_current_positions(self, value: int) -> None:
        with self._current_positions_lock:
            self._current_positions = value

    # Getter/setter thread-safe per trade_count
    def get_trade_count(self, symbol: str = None) -> int:
        with self._trade_count_lock:
            if symbol is not None:
                return self._trade_count.get(symbol, 0)
            return dict(self._trade_count)
    def inc_trade_count(self, symbol: str) -> None:
        with self._trade_count_lock:
            self._trade_count[symbol] += 1
    def set_trade_count(self, symbol: str, value: int) -> None:
        with self._trade_count_lock:
            self._trade_count[symbol] = value

    # Getter/setter thread-safe per metrics (TradingMetrics)
    def get_metrics(self) -> dict:
        with self._metrics_lock:
            return self._metrics
    def set_metrics(self, metrics):
        with self._metrics_lock:
            self._metrics = metrics

    # Getter/setter thread-safe per trade_metrics (dict)
    def get_trade_metrics(self, key=None):
        with self._trade_metrics_lock:
            if key is not None:
                return self._trade_metrics.get(key, None)
            return dict(self._trade_metrics)
    def set_trade_metrics(self, key, value):
        with self._trade_metrics_lock:
            self._trade_metrics[key] = value
    def inc_trade_metrics(self, key, amount=1):
        with self._trade_metrics_lock:
            self._trade_metrics[key] += amount
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
        """Restituisce lo spread massimo consentito per un simbolo dalla config risk_parameters.max_spread, fallback solo se non presente"""
        try:
            DEFAULT_SPREADS = {
                'SP500': 10.0,
                'NAS100': 15.0,
                'XAUUSD': 30.0,
                'BTCUSD': 50.0,
                'ETHUSD': 40.0,
                'default': 20.0
            }
            risk_params = self.config.get('risk_parameters', {})
            spread_config = risk_params.get('max_spread', None)
            if spread_config is None:
                return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
            if isinstance(spread_config, dict):
                symbol_spread = spread_config.get(symbol, spread_config.get('default', None))
                if symbol_spread is None:
                    return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
            else:
                symbol_spread = spread_config
            return float(symbol_spread)
        except Exception as e:
            logger.error(f"[ConfigManager] Errore determinazione max_spread per {symbol}: {str(e)}")
            return 20.0
        
        
"""
2- QuantumEngine - Il motore principale che elabora i tick di mercato e genera segnali di trading 
basati sull'entropia e stati quantistici. Dipende dalla configurazione.
"""



class QuantumEngine:
    # Buffer thread-safe per segnali e thread di report
    _signal_report_buffer = []
    _signal_report_lock = threading.Lock()
    _signal_report_interval = 300  # 5 minuti
    _signal_report_thread_started = False

    def _start_signal_report_thread(self):
        if getattr(self, '_signal_report_thread_started', False):
            return
        self._signal_report_thread_started = True
        def report_loop():
            # Stampa subito un report all'avvio per confermare attivazione
            self._flush_signal_report(force_empty=True, startup=True)
            while True:
                time.sleep(self._signal_report_interval)
                self._flush_signal_report(force_empty=True)
        t = threading.Thread(target=report_loop, daemon=True)
        t.start()

    def _flush_signal_report(self, force_empty=False, startup=False):
        with self._signal_report_lock:
            report_time = datetime.now().isoformat()
            if not self._signal_report_buffer:
                if force_empty:
                    # Stampa comunque un report vuoto
                    msg = ("\n==================== [SIGNAL REPORT - {time}] ====================\n"
                           "Nessun segnale generato negli ultimi 5 minuti.\n"
                           "===============================================================\n")
                    if startup:
                        msg = ("\n==================== [SIGNAL REPORT - {time}] ====================\n"
                               "[AVVIO] Sistema di log segnali attivato.\n"
                               "Nessun segnale generato finora.\n"
                               "===============================================================\n")
                    logger.info(msg.format(time=report_time))
                return
            try:
                # Sintesi: simbolo | tipo | motivo
                lines = [
                    f"{e['symbol']:<12} | {e['status']:<9} | {e['motivo']}"
                    for e in self._signal_report_buffer
                ]
                table = "Simbolo      | Tipo      | Motivo\n" + "-"*60 + "\n" + "\n".join(lines)
                logger.info(f"\n==================== [SIGNAL REPORT - {report_time}] ====================\n"
                            f"Segnali generati negli ultimi 5 minuti: {len(self._signal_report_buffer)}\n"
                            f"{table}\n"
                            f"===============================================================\n")
            except Exception as e:
                logger.error(f"[SIGNAL REPORT] Errore generazione report: {e}")
            self._signal_report_buffer.clear()

    def start_signal_reporting(self):
        self._start_signal_report_thread()
    @property
    def config_dict(self):
        """Restituisce sempre il dict di configurazione, sia che il config manager sia un dict che un oggetto complesso"""
        if hasattr(self.config_manager, 'config') and isinstance(self.config_manager.config, dict):
            return self.config_manager.config
        elif isinstance(self.config_manager, dict):
            return self.config_manager
        return {}
    # get_quantum_params è già definito in fondo alla classe, quindi questa versione viene rimossa per evitare duplicazione.
    def _check_signal_cooldown(self, symbol: str, last_signal_time: float) -> bool:
        global logger
        if 'logger' not in globals() or logger is None:
            from logging import getLogger
            logger = getLogger("phoenix_quantum")
        """
        Verifica se il simbolo è in periodo di cooldown per i segnali.

        Args:
            symbol (str): Simbolo da controllare.
            last_signal_time (float): Timestamp dell'ultimo segnale.

        Returns:
            bool: True se in cooldown, False altrimenti.
        """
        if time.time() - last_signal_time < self.signal_cooldown:
            remaining = int(self.signal_cooldown - (time.time() - last_signal_time))
            logger.debug(f"{symbol}: In cooldown segnali ({remaining}s rimanenti)")
            return True
        return False

    def _calculate_signal_thresholds(self, volatility: float) -> tuple:
        global logger
        if 'logger' not in globals() or logger is None:
            from logging import getLogger
            logger = getLogger("phoenix_quantum")
        """
        Calcola le soglie di entropia per BUY e SELL in base alla volatilità.

        Args:
            volatility (float): Volatilità calcolata.

        Returns:
            tuple: (buy_thresh, sell_thresh)
        """
        thresholds = self.config.get('quantum_params', {}).get('entropy_thresholds', {})
        base_buy_thresh = thresholds.get('buy_signal', 0.55)
        base_sell_thresh = thresholds.get('sell_signal', 0.45)
        buy_thresh = base_buy_thresh * (1 + (volatility - 1) * 0.5)
        sell_thresh = base_sell_thresh * (1 - (volatility - 1) * 0.5)
        return buy_thresh, sell_thresh

    def _log_signal_bias(self, symbol: str, stats: dict, buy_ratio: float):
        global logger
        if 'logger' not in globals() or logger is None:
            from logging import getLogger
            logger = getLogger("phoenix_quantum")
        if (stats['BUY'] + stats['SELL']) > 10:
            if buy_ratio > 0.8:
                logger.warning(f"⚠️ BIAS LONG DETECTED: {buy_ratio:.1%} buy signals!")
            elif buy_ratio < 0.2:
                logger.warning(f"⚠️ BIAS SHORT DETECTED: {buy_ratio:.1%} buy signals!")

    def _log_signal_debug(self, symbol: str, entropy: float, spin: float, confidence: float, buy_thresh: float, sell_thresh: float, buy_condition: bool, sell_condition: bool, last_tick_price: float):
        global logger
        if 'logger' not in globals() or logger is None:
            from logging import getLogger
            logger = getLogger("phoenix_quantum")
        logger.debug(f"{symbol} Signal Analysis: "
            f"E={entropy:.3f} S={spin:.3f} C={confidence:.3f} | "
            f"BUY: E>{buy_thresh:.3f}? {entropy > buy_thresh} & S>{self.spin_threshold * confidence:.3f}? {spin > self.spin_threshold * confidence} = {buy_condition} | "
            f"SELL: E<{sell_thresh:.3f}? {entropy < sell_thresh} & S<{-self.spin_threshold * confidence:.3f}? {spin < -self.spin_threshold * confidence} = {sell_condition} | Prezzo={last_tick_price}")
    def _get_symbol_config(self, symbol: str) -> dict:
        """
        Restituisce la configurazione completa di un simbolo.

        Args:
            symbol (str): Simbolo da cercare.

        Returns:
            dict: Configurazione del simbolo.
        """
        return self.config.get('symbols', {}).get(symbol, {})
    """
    1. Inizializzazione e Setup
    Costruttore della classe, carica i parametri di configurazione e inizializza buffer, cache e variabili di stato.
    """
    
    def __init__(self, config):
        """
        Inizializza QuantumEngine con ConfigManager o dict.

        Args:
            config (ConfigManager|dict): Oggetto di configurazione.
        """
        # Se riceve un ConfigManager, usa direttamente
        if hasattr(config, 'get_risk_params') and hasattr(config, 'config'):
            self._config_manager = config
            self._config = config.config
        else:
            # Se riceve un dict puro, crea un ConfigManager temporaneo
            from types import SimpleNamespace
            if isinstance(config, dict):
                from copy import deepcopy
                config_obj = SimpleNamespace(config=deepcopy(config))
                from threading import Lock

                class DummyConfigManager:
                    def __init__(self, config):
                        self.config = config.config if hasattr(config, 'config') else config
                        self._lock = Lock()

                    @property
                    def config_dict(self):
                        return self.config

                    def get_risk_params(self, symbol=None):
                        with self._lock:
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

                    @property
                    def symbols(self):
                        # Restituisce la lista dei simboli come in ConfigManager
                        syms = self.config.get('symbols', {})
                        if isinstance(syms, dict):
                            return list(syms.keys())
                        return syms

                    def _get_max_allowed_spread(self, symbol: str) -> float:
                        """Restituisce lo spread massimo consentito per un simbolo (compatibilità ConfigManager)"""
                        try:
                            DEFAULT_SPREADS = {
                                'SP500': 10.0,
                                'NAS100': 15.0,
                                'XAUUSD': 30.0,
                                'BTCUSD': 50.0,
                                'ETHUSD': 40.0,
                                'default': 20.0
                            }
                            risk_params = self.config.get('risk_parameters', {})
                            spread_config = risk_params.get('max_spread', {})
                            if isinstance(spread_config, dict):
                                symbol_spread = spread_config.get(symbol, spread_config.get('default', 'auto'))
                            else:
                                symbol_spread = spread_config
                            if isinstance(symbol_spread, str):
                                symbol_spread = symbol_spread.lower()
                                if symbol_spread == 'adaptive':
                                    return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
                                elif symbol_spread == 'auto':
                                    return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
                            return float(symbol_spread)
                        except Exception as e:
                            return float(20.0)

                self._config_manager = DummyConfigManager(config_obj)
                self._config = config
            else:
                self._config_manager = None
                self._config = config

        # Lock per tutte le strutture dati runtime condivise
        self._runtime_lock = threading.RLock()

        # Strutture dati protette
        self._tick_buffer = defaultdict(deque)
        self._position_cooldown = {}
        self._last_signal_time = {}
        self._volatility_cache = {}
        self._spin_cache = {}
        self._signal_stats = {'BUY': 0, 'SELL': 0}
        self._last_warning_time = {}

        # Parametri buffer/config

        # Parametri sempre dalla config (quantum_params)
        quantum_params = self.config.get('quantum_params', {})
        self.buffer_size = quantum_params.get('buffer_size', 100)
        self.spin_window = quantum_params.get('spin_window', 20)
        self.min_spin_samples = quantum_params.get('min_spin_samples', 10)
        self.spin_threshold = quantum_params.get('spin_threshold', 0.25)
        self.signal_cooldown = quantum_params.get('signal_cooldown', 300)
        self.entropy_thresholds = quantum_params.get('entropy_thresholds', {'buy_signal': 0.55, 'sell_signal': 0.45})

        # Inizializza buffer per simboli
        for symbol in self.config.get('symbols', {}):
            self._tick_buffer[symbol] = deque(maxlen=self.buffer_size)

        self._cache_timeout = 60  # secondi
        self.warning_cooldown = 300  # 5 minuti tra warning simili

    # --- Getter/setter thread-safe per strutture dati runtime ---
    def get_tick_buffer(self, symbol=None):
        """
        Restituisce il buffer dei tick per un simbolo o tutti.

        Args:
            symbol (str, optional): Simbolo. Se None, restituisce tutti i buffer.

        Returns:
            deque|dict: Buffer del simbolo o tutti i buffer.
        """
        with self._runtime_lock:
            if symbol is not None:
                return self._tick_buffer[symbol]
            return self._tick_buffer

    def append_tick(self, symbol, tick):
        """
        Aggiunge un tick al buffer del simbolo.

        Args:
            symbol (str): Simbolo.
            tick (dict): Tick da aggiungere.
        """
        with self._runtime_lock:
            self._tick_buffer[symbol].append(tick)

    def get_position_cooldown(self, symbol=None):
        with self._runtime_lock:
            if symbol is not None:
                return self._position_cooldown.get(symbol, 0)
            return dict(self._position_cooldown)

    def set_position_cooldown(self, symbol, value):
        with self._runtime_lock:
            self._position_cooldown[symbol] = value

    def get_last_signal_time(self, symbol=None):
        with self._runtime_lock:
            if symbol is not None:
                return self._last_signal_time.get(symbol, 0)
            return dict(self._last_signal_time)

    def set_last_signal_time(self, symbol, value):
        with self._runtime_lock:
            self._last_signal_time[symbol] = value

    def get_signal_stats(self):
        with self._runtime_lock:
            return dict(self._signal_stats)

    def inc_signal_stats(self, signal):
        with self._runtime_lock:
            if signal in self._signal_stats:
                self._signal_stats[signal] += 1
            else:
                self._signal_stats[signal] = 1

    def get_volatility_cache(self):
        with self._runtime_lock:
            return dict(self._volatility_cache)

    def set_volatility_cache(self, key, value):
        with self._runtime_lock:
            self._volatility_cache[key] = value

    def get_spin_cache(self):
        with self._runtime_lock:
            return dict(self._spin_cache)

    def set_spin_cache(self, key, value):
        with self._runtime_lock:
            self._spin_cache[key] = value

    def get_last_warning_time(self, symbol=None):
        with self._runtime_lock:
            if symbol is not None:
                return self._last_warning_time.get(symbol, 0)
            return dict(self._last_warning_time)

    def set_last_warning_time(self, symbol, value):
        with self._runtime_lock:
            self._last_warning_time[symbol] = value
        
    @property
    def config(self):
        """Property per accesso alla configurazione"""
        return self._config
    
    def is_in_cooldown_period(self, symbol: str) -> bool:
        """Verifica se il simbolo è in un periodo di cooldown"""
        last_close = self.get_position_cooldown(symbol)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        if time.time() - last_close < position_cooldown:
            logger.info(f"Cooldown normale attivo per {symbol} - {position_cooldown - (time.time() - last_close):.0f}s rimanenti")
            return True
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.get_last_signal_time(symbol)
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
                logger.error(f"Impossibile ottenere info simbolo {symbol}")
                return False
            current_spread = (symbol_info.ask - symbol_info.bid) / self._get_pip_size(symbol)
            symbol_config = self._get_symbol_config(symbol)
            max_spread = symbol_config.get('max_spread', self.config.get('risk_parameters', {}).get('max_spread', {}))
            if isinstance(max_spread, dict):
                max_allowed = max_spread.get(symbol, max_spread.get('default', 20))
            else:
                max_allowed = max_spread
            if current_spread > max_allowed:
                logger.warning(f"Spread {symbol} troppo alto: {current_spread:.1f}p > {max_allowed}p")
                return False
        except Exception as e:
            logger.error(f"Errore verifica spread {symbol}: {e}")
            return False
            
        # 3. Controlla numero massimo posizioni aperte
        positions = mt5.positions_get()
        if positions and len(positions) >= self.config.get('risk_parameters', {}).get('max_positions', 1):
            logger.warning(f"Massimo numero posizioni raggiunto: {len(positions)}")
            return False
            
        # 4. Controlla trades giornalieri - RIMOSSO controllo qui per evitare duplicazione
        # Il controllo viene fatto in _process_single_symbol
            
        return True
        
    def record_trade_close(self, symbol: str):
        """Registra la chiusura solo se effettivamente avvenuta"""
        if mt5.positions_get(symbol=symbol) is None or len(mt5.positions_get(symbol=symbol)) == 0:
            self.set_position_cooldown(symbol, time.time())
            logger.info(f"Cooldown registrato per {symbol} (1800s)")

        

    """
    2. Metodi di Calcolo Quantistico
    """
    @staticmethod
    @lru_cache(maxsize=1000)
    def calculate_entropy(deltas: Tuple[float]) -> float:
        """
        Calcola l'entropia normalizzata (tra 0 e 1) da una sequenza di delta di prezzo.

        Args:
            deltas (Tuple[float]): Sequenza di variazioni di prezzo.

        Returns:
            float: Entropia normalizzata (0-1).
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

        Args:
            ticks (List[Dict]): Lista di tick con campo 'direction'.

        Returns:
            Tuple[float, float]: (spin, confidenza)
        """
        # print debug rimosso
        if not ticks or len(ticks) < self.min_spin_samples:
            #print(f"[DEBUG-TEST] [calculate_spin] POCHI TICK: {len(ticks)} < {self.min_spin_samples}")
            return 0.0, 0.0
        cache_key = hash(tuple((t['price'], t['direction']) for t in ticks[-self.spin_window:]))
        # print debug rimosso
        result = self._get_cached(
            self._spin_cache,
            cache_key,
            self._calculate_spin_impl,
            ticks[-self.spin_window:]
        )
        # print debug rimosso
        return result

    def _calculate_spin_impl(self, ticks: List[Dict]) -> Tuple[float, float]:
        """
        (metodo interno)
        Implementazione base del calcolo dello spin (senza cache).
        """
        try:
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
        except Exception as e:
            #print(f"[DEBUG-TEST] [_calculate_spin_impl] EXCEPTION: {e}")
            import logging
            logging.getLogger("phoenix_quantum").error(f"[QuantumEngine._calculate_spin_impl] EXCEPTION: {e}")
            return 0.0, 0.0

    

    def calculate_quantum_volatility(self, symbol: str, window: int = 50) -> float:
        """
        Calcola una volatilità adattiva combinando entropia e spin.

        Args:
            symbol (str): Simbolo.
            window (int, optional): Finestra di calcolo. Default 50.

        Returns:
            float: Volatilità quantistica.
        """
        def _calculate():
            ticks = list(self.get_tick_buffer(symbol))
            if len(ticks) < window:
                return 1.0

            deltas = np.array([t['delta'] for t in ticks[-window:]])
            prob_dist = np.abs(deltas) / (np.sum(np.abs(deltas)) + 1e-10)
            entropy = -np.sum(prob_dist * np.log(prob_dist + 1e-10)) / np.log(window)
            spin, _ = self._calculate_spin_impl(ticks)
            return 1 + abs(spin) * entropy

        return self._get_cached(self.get_volatility_cache(), symbol, _calculate)
        
        
        
    """
    3. Gestione Tick e Segnali
    """

    def process_tick(self, symbol: str, price: float):
        global logger
        if 'logger' not in globals() or logger is None:
            from logging import getLogger
            logger = getLogger("phoenix_quantum")
        """
        Aggiunge un nuovo tick al buffer circolare e calcola delta/direzione rispetto al tick precedente.

        Args:
            symbol (str): Simbolo.
            price (float): Prezzo del tick.

        Returns:
            None
        """
        try:
            buf = self.get_tick_buffer(symbol)
            if price <= 0:
                logger.warning(f"[process_tick] Prezzo non valido per {symbol}: {price}")
                return
            if len(buf) > 0:
                last_price = buf[-1]['price']
                delta = price - last_price
                direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
            else:
                delta = 0
                direction = 0
            self.append_tick(symbol, {
                'price': price,
                'delta': delta,
                'direction': direction,
                'time': time.time()
            })
            # Usa sempre il getter anche per il debug
            logger.debug(f"[TICK] {symbol}: price={price}, delta={delta}, direction={direction}, buffer_size={len(self.get_tick_buffer(symbol))}")
        except Exception as e:
            logger.error(f"[process_tick] Errore durante l'elaborazione del tick per {symbol}: {e}", exc_info=True)

    def get_signal(self, symbol: str, for_trading: bool = False) -> Tuple[str, float]:
        global logger
        if 'logger' not in globals() or logger is None:
            from logging import getLogger
            logger = getLogger("phoenix_quantum")
        try:
            ticks = list(self.get_tick_buffer(symbol))
            from phoenix_quantum_monofx_program import is_trading_hours
            config_dict = self._config.config if hasattr(self._config, 'config') else self._config
            # 1. Buffer insufficiente
            if len(ticks) < self.min_spin_samples:
                motivo = "Buffer tick insufficiente"
                dettagli = {
                    "symbol": symbol,
                    "ticks": len(ticks),
                    "min_spin_samples": self.min_spin_samples,
                    "timestamp": datetime.now().isoformat(),
                }
                status = "SCARTATO"
                if not is_trading_hours(symbol, config_dict):
                    motivo += " (mercato chiuso)"
                with self._signal_report_lock:
                    self._signal_report_buffer.append({
                        "symbol": symbol,
                        "status": status,
                        "motivo": motivo,
                        "dettagli": dettagli
                    })
                return "HOLD", 0.0
            spin_window = min(self.spin_window, len(ticks))
            recent_ticks = ticks[-spin_window:]
            spin, confidence = self.calculate_spin(recent_ticks)
            last_tick_price = recent_ticks[-1]['price'] if recent_ticks else 0.0
            # 2. Confidence troppo bassa
            if confidence < 0.8:
                motivo = "Confidence troppo bassa"
                dettagli = {
                    "symbol": symbol,
                    "confidence": confidence,
                    "threshold": 0.8,
                    "spin": spin,
                    "timestamp": datetime.now().isoformat(),
                }
                status = "SCARTATO"
                with self._signal_report_lock:
                    self._signal_report_buffer.append({
                        "symbol": symbol,
                        "status": status,
                        "motivo": motivo,
                        "dettagli": dettagli
                    })
                return "HOLD", last_tick_price
            last_signal_time = self.get_last_signal_time(symbol)
            # 3. Cooldown attivo
            if self._check_signal_cooldown(symbol, last_signal_time):
                motivo = "Cooldown segnale attivo"
                dettagli = {
                    "symbol": symbol,
                    "last_signal_time": last_signal_time,
                    "now": time.time(),
                    "cooldown": self.signal_cooldown,
                    "timestamp": datetime.now().isoformat(),
                }
                status = "SCARTATO"
                with self._signal_report_lock:
                    self._signal_report_buffer.append({
                        "symbol": symbol,
                        "status": status,
                        "motivo": motivo,
                        "dettagli": dettagli
                    })
                return "HOLD", last_tick_price
            deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10)
            entropy = self.calculate_entropy(deltas)
            volatility = 1 + abs(spin) * entropy
            buy_thresh, sell_thresh = self._calculate_signal_thresholds(volatility)
            signal = "HOLD"
            buy_condition = entropy > buy_thresh and spin > self.spin_threshold * confidence
            sell_condition = entropy < sell_thresh and spin < -self.spin_threshold * confidence
            self._log_signal_debug(symbol, entropy, spin, confidence, buy_thresh, sell_thresh, buy_condition, sell_condition, last_tick_price)
            # 4. BUY/SELL
            if buy_condition:
                signal = "BUY"
            elif sell_condition:
                signal = "SELL"
            if signal != "HOLD":
                if for_trading:
                    self.set_last_signal_time(symbol, time.time())
                self.inc_signal_stats(signal)
                stats = self.get_signal_stats()
                buy_ratio = stats['BUY'] / (stats['BUY'] + stats['SELL']) if (stats['BUY'] + stats['SELL']) > 0 else 0
                motivazione = "Condizioni soddisfatte per segnale 'BUY'" if signal == "BUY" else "Condizioni soddisfatte per segnale 'SELL'"
                dettagli = {
                    "symbol": symbol,
                    "signal": signal,
                    "entropy": round(entropy, 4),
                    "spin": round(spin, 4),
                    "confidence": round(confidence, 4),
                    "volatility": round(volatility, 4),
                    "buy_thresh": round(buy_thresh, 4),
                    "sell_thresh": round(sell_thresh, 4),
                    "price": last_tick_price,
                    "timestamp": datetime.now().isoformat(),
                }
                status = "APERTURA"
                with self._signal_report_lock:
                    self._signal_report_buffer.append({
                        "symbol": symbol,
                        "status": status,
                        "motivo": motivazione,
                        "dettagli": dettagli
                    })
                self._log_signal_bias(symbol, stats, buy_ratio)
            else:
                motivazione = "Nessuna condizione soddisfatta per BUY/SELL"
                dettagli = {
                    "symbol": symbol,
                    "entropy": round(entropy, 4),
                    "spin": round(spin, 4),
                    "confidence": round(confidence, 4),
                    "volatility": round(volatility, 4),
                    "buy_thresh": round(buy_thresh, 4),
                    "sell_thresh": round(sell_thresh, 4),
                    "price": last_tick_price,
                    "timestamp": datetime.now().isoformat(),
                }
                status = "HOLD"
                with self._signal_report_lock:
                    self._signal_report_buffer.append({
                        "symbol": symbol,
                        "status": status,
                        "motivo": motivazione,
                        "dettagli": dettagli
                    })
            return signal, last_tick_price
        except Exception as e:
            logger.error(f"[get_signal] Errore durante la generazione del segnale per {symbol}: {e}", exc_info=True)
            return "HOLD", 0.0
        
        
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
        available_symbols = [s.name for s in mt5.symbols_get() or []]
        for symbol in self._config_manager.symbols:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
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
                ticks = list(self.get_tick_buffer(symbol))[-self.spin_window:]
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
                    'buffer_size': len(self.get_tick_buffer(symbol)),
                    'E': round(entropy, 2),
                    'S': round(spin, 2),
                    'C': round(confidence, 2),
                    'V': round(volatility, 2),
                    'timestamp': current_time
                }
                heartbeat_data.append(state)
                # Controlli spread e buffer solo se orari di trading
                if is_trading_hours(symbol, self._config_manager.config_dict):
                    max_spread = self._config_manager._get_max_allowed_spread(symbol)
                    if spread > max_spread:
                        issues.append(f"{symbol}: Spread {spread:.1f}p > max {max_spread:.1f}p")
                    if len(self.get_tick_buffer(symbol)) < self.min_spin_samples:
                        warning_symbols.append(symbol)
            except Exception as e:
                logger.error(f"Errore monitoraggio {symbol}: {str(e)}", exc_info=True)
        if heartbeat_data:
            hb_msg = ("\n==================== [HEARTBEAT] ====================\n" +
                "\n".join(
                    f"Symbol: {d['symbol']}\n"
                    f"  Bid: {d['bid']:.5f}\n"
                    f"  Ask: {d['ask']:.5f}\n"
                    f"  Spread: {d['spread']:.1f} pips\n"
                    f"  Buffer Size: {d['buffer_size']}\n"
                    f"  Entropy (E): {d['E']:.2f}\n"
                    f"  Spin (S): {d['S']:.2f}\n"
                    f"  Confidence (C): {d['C']:.2f}\n"
                    f"  Volatility (V): {d['V']:.2f}\n"
                    "------------------------------------------------------"
                for d in heartbeat_data[:5]) +
                "\n======================================================\n"
            )
            logger.info(hb_msg)
            positions_count = len(mt5.positions_get() or [])
            logger.info(f"Sistema attivo - Posizioni: {positions_count}/1")
        else:
            logger.info("\n==================== [HEARTBEAT] ====================\n"
                        "Nessun tick valido ricevuto per nessun simbolo!\n"
                        "Possibile problema di connessione, dati o mercato chiuso.\n"
                        "======================================================\n")
            positions_count = len(mt5.positions_get() or [])
            logger.info(f"Sistema attivo - Posizioni: {positions_count}/1")
        if warning_symbols:
            # Mostra il warning solo se almeno uno dei simboli è in orario di mercato
            warning_symbols_open = [s for s in warning_symbols if is_trading_hours(s, self._config_manager.config_dict)]
            if warning_symbols_open:
                logger.warning(f"Buffer insufficiente: {', '.join(warning_symbols_open[:3])}")
            else:
                logger.debug(f"[NO WARNING] Buffer insufficiente ma tutti i simboli sono fuori orario di mercato: {', '.join(warning_symbols[:3])}")
        if issues:
            logger.warning(f"Problemi: {' | '.join(issues[:3])}")
        return True
        
        
    def get_remaining_cooldown(self, symbol: str) -> float:
        """Restituisce i secondi rimanenti di cooldown per un simbolo"""
        # 1. Controlla cooldown normale posizioni (1800s)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        last_close = self.get_position_cooldown(symbol)
        position_remaining = max(0, position_cooldown - (time.time() - last_close))

        # 2. Controlla cooldown segnali (900s)
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.get_last_signal_time(symbol)
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
        Tutto thread-safe e a prova di deadlock.
        """
        # print debug rimosso
        acquired = self._runtime_lock.acquire(timeout=2.0)
        if not acquired:
        # print debug rimosso
            import logging
            logging.getLogger("phoenix_quantum").error("[QuantumEngine._get_cached] DEADLOCK TIMEOUT su _runtime_lock! Restituisco fallback.")
            # Fallback: restituisco valore neutro
            return (0.0, 0.0)
        try:
            # print debug rimosso
            now = time.time()
            if cache_dict is self._volatility_cache:
                cache = self.get_volatility_cache()
            elif cache_dict is self._spin_cache:
                cache = self.get_spin_cache()
            else:
                cache = cache_dict
            if key in cache:
                value, timestamp = cache[key]
                #print(f"[DEBUG-TEST] [_get_cached] CACHE HIT: value={value}, timestamp={timestamp}")
                if now - timestamp < self._cache_timeout:
                    #print(f"[DEBUG-TEST] [_get_cached] CACHE VALID RETURN {value}")
                    return value
            # print debug rimosso
            # Timeout per la funzione di calcolo
            import concurrent.futures
            value = None
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(calculate_func, *args)
                    value = future.result(timeout=2.0)
            except concurrent.futures.TimeoutError:
                #print(f"[DEBUG-TEST] [_get_cached] TIMEOUT su calculate_func! Restituisco fallback.")
                import logging
                logging.getLogger("phoenix_quantum").error("[QuantumEngine._get_cached] TIMEOUT su calculate_func! Restituisco fallback.")
                value = (0.0, 0.0)
            except Exception as e:
                #print(f"[DEBUG-TEST] [_get_cached] EXCEPTION in calculate_func: {e}")
                import logging
                logging.getLogger("phoenix_quantum").error(f"[QuantumEngine._get_cached] EXCEPTION in calculate_func: {e}")
                value = (0.0, 0.0)
            # print debug rimosso
            cache[key] = (value, now)
            if cache_dict is self._volatility_cache:
                self.set_volatility_cache(key, (value, now))
            elif cache_dict is self._spin_cache:
                self.set_spin_cache(key, (value, now))
            else:
                cache_dict[key] = (value, now)
            # print debug rimosso
            return value
        finally:
            self._runtime_lock.release()
        
    
        
        
    def _get_pip_size(self, symbol: str) -> float:
        """
        Calcola la dimensione di un pip in modo robusto (supporta simboli come BTCUSD, XAUUSD).
        Tutto thread-safe.
        """
        with self._runtime_lock:
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
        base_params = self.config.get('quantum_params', {})
        symbol_config = self.config.get('symbols', {}).get(symbol, {})
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
        """Inizializzazione con accesso sicuro alla configurazione e protezione thread-safe"""
        self._lock = threading.Lock()
        actual_config = config.config if hasattr(config, 'config') else config
        self._daily_high = initial_equity
        self._current_equity = initial_equity
        self._current_balance = initial_equity
        self._last_update_date = datetime.now().date()
        self.currency = actual_config.get('account_currency', 'USD')
        try:
            dd_config = actual_config.get('challenge_specific', {}).get('drawdown_protection', {})
            self.soft_limit = float(dd_config.get('soft_limit', 0.05))
            self.hard_limit = float(dd_config.get('hard_limit', 0.10))
        except Exception as e:
            raise ValueError(f"Configurazione drawdown mancante: {str(e)}") from e
        self._protection_active = False
        self._max_daily_drawdown = 0.0
        self._last_check_time = time.time()

    # Getter/setter thread-safe
    def get_daily_high(self):
        with self._lock:
            return self._daily_high
    def set_daily_high(self, value):
        with self._lock:
            self._daily_high = value
    def get_current_equity(self):
        with self._lock:
            return self._current_equity
    def set_current_equity(self, value):
        with self._lock:
            self._current_equity = value
    def get_current_balance(self):
        with self._lock:
            return self._current_balance
    def set_current_balance(self, value):
        with self._lock:
            self._current_balance = value
    def get_last_update_date(self):
        with self._lock:
            return self._last_update_date
    def set_last_update_date(self, value):
        with self._lock:
            self._last_update_date = value
    def get_protection_active(self):
        with self._lock:
            return self._protection_active
    def set_protection_active(self, value):
        with self._lock:
            self._protection_active = value
    def get_max_daily_drawdown(self):
        with self._lock:
            return self._max_daily_drawdown
    def set_max_daily_drawdown(self, value):
        with self._lock:
            self._max_daily_drawdown = value
    def get_last_check_time(self):
        with self._lock:
            return self._last_check_time
    def set_last_check_time(self, value):
        with self._lock:
            self._last_check_time = value

    def update(self, current_equity: float, current_balance: float) -> None:
        """Aggiorna i valori di equity e balance (thread-safe, robusto)"""
        try:
            today = datetime.now().date()
            with self._lock:
                if today != self._last_update_date:
                    self._daily_high = max(current_equity, current_balance)
                    self._current_balance = current_balance
                    self._last_update_date = today
                    self._protection_active = False
                    self._max_daily_drawdown = 0.0
                    logger.info(f"Reset giornaliero drawdown. Nuovo high: {self._daily_high:.2f} {self.currency}")
                else:
                    self._daily_high = max(self._daily_high, current_equity, current_balance)
                    self._current_equity = current_equity
                    self._current_balance = current_balance
        except Exception as e:
            logger.error(f"[DailyDrawdownTracker.update] Errore aggiornamento equity/balance: {e}", exc_info=True)

    def check_limits(self, current_equity: float) -> Tuple[bool, bool]:
        """Verifica se sono stati raggiunti i limiti di drawdown (thread-safe, robusto)"""
        try:
            with self._lock:
                if time.time() - self._last_check_time < 5:
                    return False, False
                self._last_check_time = time.time()
                try:
                    drawdown_pct = (current_equity - self._daily_high) / self._daily_high
                    self._max_daily_drawdown = min(self._max_daily_drawdown, drawdown_pct)
                    soft_hit = drawdown_pct <= -self.soft_limit
                    hard_hit = drawdown_pct <= -self.hard_limit
                    if hard_hit:
                        logger.critical(
                            f"HARD LIMIT HIT! Drawdown: {drawdown_pct*100:.2f}% | "
                            f"High: {self._daily_high:.2f} {self.currency} | "
                            f"Current: {current_equity:.2f} {self.currency}"
                        )
                    elif soft_hit and not self._protection_active:
                        logger.warning(
                            f"SOFT LIMIT HIT! Drawdown: {drawdown_pct*100:.2f}% | "
                            f"Max Daily: {self._max_daily_drawdown*100:.2f}%"
                        )
                    return soft_hit, hard_hit
                except ZeroDivisionError:
                    logger.error("Errore calcolo drawdown (daily_high zero)")
                    return False, False
        except Exception as e:
            logger.error(f"[DailyDrawdownTracker.check_limits] Errore controllo limiti drawdown: {e}", exc_info=True)
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

    def _calculate_drawdown(self, profits: np.ndarray) -> float:
        """ Calcola il drawdown massimo dalla curva di equity."""
        equity_curve = np.cumsum(profits)
        peak = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - peak) / (peak + 1e-10)
        return np.min(drawdowns) * 100

    def _calculate_sharpe(self, profits: np.ndarray) -> float:
        """ Calcola lo Sharpe Ratio annualizzato."""
        # Esempio semplice: Sharpe annualizzato con risk-free rate 0
        if len(profits) < 2:
            return 0.0
        mean = np.mean(profits)
        std = np.std(profits)
        if std == 0:
            return 0.0
        sharpe = mean / std * np.sqrt(252)  # 252 giorni di trading
        return sharpe

    def get_metrics_summary(self):
        """Restituisce un riassunto delle metriche principali."""
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



class QuantumTradingSystem:
    def _safe_sleep(self, seconds):
        """Sleep frazionato che permette l'interruzione rapida con Ctrl+C"""
        interval = 0.1
        slept = 0
        while self.running and slept < seconds:
            time.sleep(min(interval, seconds - slept))
            slept += interval

    @property
    def symbols(self):
        """Restituisce la lista dei simboli configurati in modo robusto"""
        # Prova a recuperare i simboli da diverse possibili strutture
        if hasattr(self, '_config'):
            if hasattr(self._config, 'symbols') and self._config.symbols:
                # Caso: self._config ha attributo symbols
                return list(self._config.symbols)
            elif hasattr(self._config, 'config') and isinstance(self._config.config, dict) and 'symbols' in self._config.config:
                # Caso: self._config.config['symbols']
                return list(self._config.config['symbols'].keys())
            elif isinstance(self._config, dict) and 'symbols' in self._config:
                # Caso: self._config è un dict
                return list(self._config['symbols'].keys())
        return []
    def _main_loop(self):
        """
        cuore pulsante
        Loop principale con variabili di tempo come attributi di istanza
        Loop principale di trading
        """
        # NB: KeyboardInterrupt viene gestito SOLO nel ciclo esterno (start)
        while self.running:
            try:
                # Verifica connessione MT5
                if not mt5.terminal_info().connected:
                    logger.error("Connessione MT5 persa!")
                    self._safe_sleep(5)
                    continue
                current_time = time.time()
                # Controlli periodici
                if current_time - self.last_connection_check > 30:  # Check più frequente
                    if not self._verify_connection():
                        self._safe_sleep(5)
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
                    # Debug periodico dello stato trading (ogni 5 minuti, per tutti i simboli)
                    for symbol in self.symbols:
                        self.debug_trade_status(symbol)
                if time.time() - self.last_buffer_check > 300:  # 5 minuti
                    self.check_buffers()
                    self.last_buffer_check = time.time()
                if current_time - self.last_position_check > 30:
                    self._monitor_open_positions()
                    self._validate_positions()
                    self.close_positions_before_weekend()  # <--- AGGIUNTO QUI
                    self.last_position_check = current_time
                for symbol in self.symbols:
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
                        buffer_size = len(self.engine.get_tick_buffer(symbol))
                        logger.debug(
                            "\n-------------------- [BUFFER-DEBUG] --------------------\n"
                            f"Symbol: {symbol}\n"
                            f"Buffer Size: {buffer_size}\n"
                            "------------------------------------------------------\n"
                        )
                # Gestione errori SOLO per _process_symbols, non per KeyboardInterrupt
                start_time = time.time()
                self._process_symbols()
                process_time = time.time() - start_time
                if process_time > 5:
                    logger.warning(f"Processamento simboli lento: {process_time:.2f}s")
                self._safe_sleep(0.5)
            except Exception as e:
                logger.error(f"Errore nel processamento simboli: {str(e)}", exc_info=True)
                self._safe_sleep(5)
    """
    Sistema completo di trading algoritmico quantistico
    """

    def get_live_status(self):
        """Restituisce lo stato live del sistema per la dashboard (tick, equity, bilancio, P&L, drawdown, posizioni)"""
        try:
            # Info account
            account = mt5.account_info()
            equity = account.equity if account else None
            balance = account.balance if account else None
            currency = account.currency if account else 'USD'
            # Drawdown
            drawdown = None
            if hasattr(self, 'drawdown_tracker'):
                drawdown = self.drawdown_tracker.get_drawdown() if hasattr(self.drawdown_tracker, 'get_drawdown') else None
            # P&L
            total_profit = self.trade_metrics.get('total_profit', 0.0)
            # Posizioni aperte
            open_positions = []
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    open_positions.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'price_current': pos.price_current,
                        'profit': pos.profit,
                        'sl': pos.sl,
                        'tp': pos.tp,
                        'time': pos.time
                    })
            # Tick e dati di mercato per ogni simbolo
            symbols_data = {}
            for symbol in self._config.config['symbols']:
                tick = mt5.symbol_info_tick(symbol)
                symbols_data[symbol] = {
                    'bid': getattr(tick, 'bid', None),
                    'ask': getattr(tick, 'ask', None),
                    'last': getattr(tick, 'last', None),
                    'spread': getattr(tick, 'ask', 0) - getattr(tick, 'bid', 0) if tick else None,
                    'time': getattr(tick, 'time', None)
                }
            return {
                'equity': equity,
                'balance': balance,
                'currency': currency,
                'drawdown': drawdown,
                'total_profit': total_profit,
                'open_positions': open_positions,
                'symbols_data': symbols_data
            }
        except Exception as e:
            logger.error(f"Errore get_live_status: {str(e)}")
            return {}

    def get_trade_history(self):
        """Restituisce lo storico operazioni reali da MT5 (ultimi 30 giorni)"""
        from datetime import datetime, timedelta
        try:
            date_to = datetime.now()
            date_from = date_to - timedelta(days=30)
            deals = mt5.history_deals_get(date_from, date_to)
            history = []
            if deals:
                for d in deals:
                    history.append({
                        'ticket': d.ticket,
                        'symbol': d.symbol,
                        'type': 'BUY' if d.type == mt5.ORDER_TYPE_BUY else 'SELL',
                        'volume': d.volume,
                        'price': d.price,
                        'profit': d.profit,
                        'time': d.time,
                        'comment': d.comment
                    })
            return history
        except Exception as e:
            logger.error(f"Errore get_trade_history: {str(e)}")
            return []

    def send_manual_order(self, symbol, type_, size, sl=None, tp=None):
        """
        Invia un ordine manuale buy/sell su MT5
        Args:
            symbol: str
            type_: 'BUY' o 'SELL'
            size: float
            sl: float (prezzo stop loss)
            tp: float (prezzo take profit)
        Returns:
            dict: risultato operazione
        """
        try:
            if type_ == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
            elif type_ == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
            else:
                return {'success': False, 'error': 'Tipo ordine non valido'}

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {'success': False, 'error': f'Simbolo {symbol} non trovato'}

            price = symbol_info.ask if order_type == mt5.ORDER_TYPE_BUY else symbol_info.bid
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': float(size),
                'type': order_type,
                'price': price,
                'sl': sl if sl else 0.0,
                'tp': tp if tp else 0.0,
                'deviation': 10,
                'magic': 123456,
                'comment': 'Manual order from dashboard',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'ticket': result.order, 'result': str(result)}
            else:
                return {'success': False, 'error': str(result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def modify_order(self, ticket, sl=None, tp=None):
        """
        Modifica SL/TP di una posizione aperta
        Args:
            ticket: int
            sl: float
            tp: float
        Returns:
            dict: risultato operazione
        """
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'error': f'Posizione {ticket} non trovata'}
            pos = position[0]
            request = {
                'action': mt5.TRADE_ACTION_SLTP,
                'position': ticket,
                'sl': sl if sl else pos.sl,
                'tp': tp if tp else pos.tp,
                'symbol': pos.symbol,
                'magic': pos.magic,
                'comment': 'Modify SL/TP from dashboard'
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'result': str(result)}
            else:
                return {'success': False, 'error': str(result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def close_order(self, ticket):
        """
        Chiude manualmente una posizione aperta
        Args:
            ticket: int
        Returns:
            dict: risultato operazione
        """
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'error': f'Posizione {ticket} non trovata'}
            pos = position[0]
            symbol = pos.symbol
            volume = pos.volume
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info(symbol).ask
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': volume,
                'type': order_type,
                'position': ticket,
                'price': price,
                'deviation': 10,
                'magic': pos.magic,
                'comment': 'Manual close from dashboard',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'result': str(result)}
            else:
                return {'success': False, 'error': str(result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    """
    1. Inizializzazione e Configurazione
    """
    
    def __init__(self, config_path: str):
        """Costruttore principale"""
        logger.info(
            "\n==================== [AVVIO QUANTUM TRADING SYSTEM] ====================\n"
            f"File configurazione: {config_path}\n"
            "------------------------------------------------------\n"
        )
        self._setup_logger(config_path)
        logger.info("✅ Logger configurato")
        self._config_path = config_path
        self.running = False
        logger.info("📋 Caricamento configurazione...")
        self._load_configuration(config_path)  # Questo inizializza self._config
        logger.info("✅ Configurazione caricata")
        if not hasattr(self._config, 'config') or 'symbols' not in self._config.config:
            logger.error("Configurazione simboli non valida nel file di configurazione")
            raise ValueError("Sezione symbols mancante nella configurazione")
        logger.info(
            "\n-------------------- [SIMBOLI CONFIGURATI] ----------------------\n"
            f"Simboli trovati: {list(self._config.config['symbols'].keys())}\n"
            "------------------------------------------------------\n"
        )
        logger.info("🔄 Inizializzazione componenti core...")
        if not self._initialize_mt5():
            raise RuntimeError("Inizializzazione MT5 fallita")
        logger.info("📡 Attivazione simboli in MT5...")
        self._activate_symbols()
        logger.info("✅ Simboli attivati")
        logger.info("🧠 Inizializzazione Quantum Engine...")
        self.engine = QuantumEngine(self._config.config)
        logger.info("✅ Quantum Engine pronto")
        self.risk_manager = QuantumRiskManager(self._config.config, self.engine, self)  # Passa il dict config
        self.max_positions = self._config.config.get('risk_parameters', {}).get('max_positions', 4)
        self.current_positions = 0
        self.trade_count = defaultdict(int)
        self.metrics_lock = threading.Lock()
        self.position_lock = threading.Lock()
        self.metrics = TradingMetrics()
        self.account_info = mt5.account_info()
        self.currency = (
            self.account_info.currency 
            if self.account_info 
            else self._config.config.get('account_currency', 'USD')
        )
        if not self.account_info:
            logger.warning(f"Usando valuta di fallback: {self.currency}")
        self.trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'symbol_stats': defaultdict(dict)
        }
        initial_equity = self.account_info.equity if self.account_info else 10000
        self.drawdown_tracker = DailyDrawdownTracker(
            initial_equity=initial_equity,
            config=self._config.config
        )
        self.last_position_check = 0
        self.last_connection_check = 0
        self.last_account_update = 0
        self.last_tick_check = 0
        self.last_buffer_check = 0
        logger.info(
            "\n==================== [SISTEMA INIZIALIZZATO] ====================\n"
            f"Simboli configurati: {list(self._config.config['symbols'].keys())}\n"
            f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}\n"
            "======================================================\n"
        )
        initial_equity = self.account_info.equity if self.account_info else 10000
        self.drawdown_tracker = DailyDrawdownTracker(
            initial_equity=initial_equity,
            config=self._config.config
        )

        # Stato sistema
        self.last_position_check = 0
        self.last_connection_check = 0
        self.last_account_update = 0
        self.last_tick_check = 0
        self.last_buffer_check = 0

        logger.info("Sistema inizializzato correttamente")

        logger.info(f"Simboli configurati: {list(self._config.config['symbols'].keys())}")
        logger.info(f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}")
    
    def _activate_symbols(self):
        """Attiva automaticamente i simboli richiesti in MT5"""
        try:
            symbols_to_activate = list(self._config.config['symbols'].keys())
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
            self._config = load_config(config_path)
            # Verifica di base
            if not hasattr(self._config, 'config'):
                raise ValueError("Struttura config non valida")
            if 'symbols' not in self._config.config:
                raise ValueError("Sezione 'symbols' mancante nel file di configurazione")
            logger.info(f"Configurazione caricata con {len(self._config.config['symbols'])} simboli")
        except Exception as e:
            logger.error(f"Errore caricamento configurazione: {str(e)}")
            raise
            
            

    def _initialize_mt5(self) -> bool:
        """Connessione a MetaTrader 5 con configurazione specifica challenge"""
        try:
            # Chiudi eventuali connessioni precedenti
            mt5.shutdown()
            
            # Ottieni configurazione MT5 specifica
            mt5_config = self._config.config.get('metatrader5', {})
            
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
                self._safe_sleep(2)
                
                # Usa la stessa logica di _initialize_mt5 per riconnessione
                mt5_config = self._config.config.get('metatrader5', {})
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
            # Controllo robusto presenza simboli su self._config
            symbols = None
            if hasattr(self, '_config'):
                # Caso attributo symbols
                if hasattr(self._config, 'symbols') and self._config.symbols:
                    symbols = self._config.symbols
                # Caso _config.config['symbols']
                elif hasattr(self._config, 'config') and isinstance(self._config.config, dict) and 'symbols' in self._config.config:
                    symbols = self._config.config['symbols']
                # Caso dict puro
                elif isinstance(self._config, dict) and 'symbols' in self._config:
                    symbols = self._config['symbols']
            if not symbols or not isinstance(symbols, (dict, list)) or len(symbols) == 0:
                raise RuntimeError("Configurazione non valida - simboli mancanti")

            print(f"📋 Sistema con {len(symbols)} simboli configurati")
            print(f"🎯 Simboli: {symbols}")  # Mostra la lista direttamente
            logger.info(f"Avvio sistema con {len(symbols)} simboli")

            if not hasattr(self, 'engine') or not hasattr(self, 'risk_manager'):
                raise RuntimeError("Componenti critici non inizializzati")

            print("✅ Componenti critici inizializzati correttamente")
            self.running = True
            logger.info("Sistema di trading avviato correttamente")

            print("🔄 Inizio loop principale...")

            while self.running:
                try:
                    self._main_loop()
                    self._safe_sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("Arresto richiesto dall'utente")
                    self.running = False
                except Exception as e:
                    logger.error(f"Errore durante l'esecuzione: {str(e)}", exc_info=True)
                    print(f"❌ Errore nel loop: {e}")
                    self._safe_sleep(5)

        except Exception as e:
            logger.critical(f"Errore fatale: {str(e)}", exc_info=True)
            print(f"💀 Errore fatale: {e}")
            import traceback
            traceback.print_exc()
        # finally:  # RIMOSSO: non serve più chiamare self.stop() qui
        #     self.stop()

    def stop(self):
        """Ferma il sistema e fa cleanup"""
        self.running = False
        logger.info("Sistema di trading fermato. Cleanup completato.")

    def _process_symbols(self):
        """Processa tutti i simboli configurati"""
        current_positions = len(mt5.positions_get() or [])
        
        for symbol in self._config.config['symbols']:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    continue

                if not self._validate_tick(tick):
                    continue

                # Inserisci il tick nel buffer della QuantumEngine
                if hasattr(self, 'engine') and hasattr(self.engine, 'process_tick'):
                    # Usa il prezzo medio tra bid e ask se disponibile, altrimenti bid
                    price = None
                    if hasattr(tick, 'last') and tick.last and tick.last > 0:
                        price = tick.last
                    elif hasattr(tick, 'bid') and hasattr(tick, 'ask') and tick.bid > 0 and tick.ask > 0:
                        price = (tick.bid + tick.ask) / 2
                    elif hasattr(tick, 'bid') and tick.bid > 0:
                        price = tick.bid
                    if price:
                        self.engine.process_tick(symbol, price)
                        # Logga i primi tick inseriti per ogni simbolo
                        buffer_len = len(self.engine.get_tick_buffer(symbol))
                        if buffer_len <= 5:
                            logger.debug(f"[DEBUG TICK BUFFER] {symbol}: Inserito tick n.{buffer_len} - prezzo={price}")

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
            risk_params = self._config.config['risk_parameters']
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
            if not is_trading_hours(symbol, self._config.config):
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
            self._safe_sleep(1)
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
        max_spread = self._config._get_max_allowed_spread(symbol)
        
        if spread > max_spread * 1.2:  # Tolleranza +20%
            logger.debug(f"Spread {spread:.1f}p troppo alto per {symbol} (max {max_spread:.1f}p)")
            return False

        # 6. Verifica buffer dati sufficiente
        if len(self.engine.tick_buffer.get(symbol, [])) < self.engine.min_spin_samples:
            if is_trading_hours(symbol, self._config.config):
                logger.debug(f"Dati insufficienti nel buffer per {symbol}")
                return False
            # Se il mercato è chiuso, non bloccare per buffer insufficiente

        return True

    """
    6. Utility e Helper Methods
    """

    def debug_trade_status(self, symbol: str):
        """Debug dello stato di trading per un simbolo specifico"""
        try:
            # Verifica can_trade
            can_trade = self.engine.can_trade(symbol)
            # Verifica orari (usa config_dict per compatibilità)
            config_dict = None
            if hasattr(self, 'config_manager') and self.config_manager is not None:
                if hasattr(self.config_manager, 'config_dict'):
                    config_dict = self.config_manager.config_dict
                elif hasattr(self.config_manager, 'config'):
                    config = self.config_manager.config
                    config_dict = config.config if hasattr(config, 'config') else config
            else:
                config_dict = self._config.config if hasattr(self._config, 'config') else self._config
            trading_hours = is_trading_hours(symbol, config_dict)
            # Verifica posizioni esistenti
            positions = mt5.positions_get(symbol=symbol)
            has_position = positions and len(positions) > 0
            # Verifica limite trades giornalieri
            daily_count = self.trade_count.get(symbol, 0)
            daily_limit = 0
            try:
                daily_limit = config_dict.get('risk_parameters', {}).get('max_daily_trades', 0)
            except Exception:
                daily_limit = 0
            # Verifica buffer (usa getter thread-safe)
            buffer_size = len(self.engine.get_tick_buffer(symbol)) if hasattr(self.engine, 'get_tick_buffer') else 0
            min_samples = getattr(self.engine, 'min_spin_samples', 0)
            # Log informativo sullo stato trading
            logger.info(f"🔍 TRADE STATUS {symbol}: can_trade={can_trade}, trading_hours={trading_hours}, "
                        f"has_position={has_position}, daily_trades={daily_count}/{daily_limit}, "
                        f"buffer={buffer_size}/{min_samples}")
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
        initial_balance = self._config.config.get('initial_balance', balance)
        max_daily_loss = initial_balance * self._config.config.get('challenge_specific', {}).get('max_daily_loss_percent', 0) / 100
        max_total_loss = initial_balance * self._config.config.get('challenge_specific', {}).get('max_total_loss_percent', 0) / 100
        profit_target = initial_balance * self._config.config.get('challenge_specific', {}).get('step1_target', 0) / 100

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
        """Calcola la perdita giornaliera sommando i profitti dei deals chiusi nella data specificata."""
        from datetime import datetime, timedelta
        try:
            # Inizio e fine giornata
            date_from = datetime.combine(day, datetime.min.time())
            date_to = datetime.combine(day, datetime.max.time())
            deals = mt5.history_deals_get(date_from, date_to)
            if not deals:
                logger.info(f"Nessun deal trovato per la data {day}")
                return 0.0
            daily_loss = sum(d.profit for d in deals)
            logger.debug(f"Perdita/profitto totale del {day}: {daily_loss}")
            return daily_loss
        except Exception as e:
            logger.error(f"Errore nel calcolo della perdita giornaliera per {day}: {str(e)}")
            return 0.0

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
        for symbol in self._config.config['symbols']:
            buffer = self.engine.get_tick_buffer(symbol)
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