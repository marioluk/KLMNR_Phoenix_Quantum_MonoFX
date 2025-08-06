from datetime import time as dt_time
import os
import csv
import datetime
import logging
import time
import json

from utils.constants import DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, DEFAULT_LOG_FORMAT, DEFAULT_LOG_MAX_BYTES, DEFAULT_LOG_BACKUP_COUNT

# Funzione parse_time_range già presente
def setup_logger(config_path=None):
    """Configura e restituisce un logger globale per il sistema."""
    logger = logging.getLogger("phoenix_quantum")
    if not logger.handlers:
        handler = logging.handlers.RotatingFileHandler(
            DEFAULT_LOG_FILE,
            maxBytes=DEFAULT_LOG_MAX_BYTES,
            backupCount=DEFAULT_LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, DEFAULT_LOG_LEVEL, logging.INFO))
    return logger

def clean_old_logs(log_dir=None, max_files=10):
    """Elimina i vecchi file di log mantenendo solo i più recenti."""
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.isdir(log_dir):
        return
    logs = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)
    for old_log in logs[max_files:]:
        try:
            os.remove(os.path.join(log_dir, old_log))
        except Exception:
            pass

def validate_config(config):
    """Placeholder per validazione della configurazione."""
    # Implementare validazione reale se necessario
    if not isinstance(config, dict):
        raise ValueError("Config non valida: deve essere un dict")
    if 'symbols' not in config:
        raise ValueError("Config non valida: manca la chiave 'symbols'")
    return True

def is_trading_hours(symbol, config):
    """Verifica se il simbolo è in orario di trading secondo la configurazione."""
    # Placeholder: sempre True, implementare logica reale se serve
    return True

# Funzione parse_time_range già presente
def set_symbol_data(obj, symbol, value):
    """Imposta i dati di un simbolo in modo thread-safe su un oggetto con _lock e _symbol_data."""
    with obj._lock:
        obj._symbol_data[symbol] = value

# Funzione parse_time per parsing orari generici (es. inizio/fine)
def parse_time_range(time_str: str) -> tuple:
    """Parsa una stringa oraria in una tupla (inizio, fine)."""
    # TODO: implementazione reale, placeholder
    from datetime import time as dt_time
    return (dt_time(0, 0), dt_time(23, 59))

def log_signal_tick(symbol, tick, reason=None, log_path=None):
    """Logga un tick di segnale su file CSV."""
    try:
        if log_path is None:
            # Scrivi nella cartella logs della root principale
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            log_path = os.path.join(project_root, 'logs', 'signals_tick_log.csv')
        # Rotazione: se il file supera 10MB, rinomina con timestamp
        max_size_mb = 10
        if os.path.isfile(log_path) and os.path.getsize(log_path) > max_size_mb * 1024 * 1024:
            base, ext = os.path.splitext(log_path)
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            rotated = f"{base}_{ts}{ext}"
            os.rename(log_path, rotated)
        file_exists = os.path.isfile(log_path)
        with open(log_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['timestamp', 'symbol', 'tick', 'reason'])
            writer.writerow([
                datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
                symbol,
                tick,
                reason if reason else ''
            ])
    except Exception as e:
        logging.getLogger("phoenix_quantum").error(f"Errore log_signal_tick: {str(e)}")

def write_report_row(symbol, step, detail, extra=None, report_path=None):
    """Scrive una riga di report trade decision su file CSV."""
    try:
        if report_path is None:
            # Scrivi nella cartella logs della root principale
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            report_path = os.path.join(project_root, 'logs', 'trade_decision_report.csv')
        file_exists = os.path.isfile(report_path)
        with open(report_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['timestamp', 'symbol', 'step', 'detail', 'extra'])
            writer.writerow([
                datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
                symbol,
                step,
                detail,
                extra if extra is not None else ''
            ])
    except Exception as e:
        logging.getLogger("phoenix_quantum").error(f"Errore scrittura report trade decision: {str(e)}")

def load_json_file(path):
    """Carica un file JSON e gestisce errori."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def save_json_file(path, data):
    """Salva un file JSON e gestisce errori."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except Exception:
        return False

def safe_sleep(seconds):
    """Sleep sicuro che ignora eventuali eccezioni."""
    try:
        time.sleep(seconds)
    except Exception:
        pass
