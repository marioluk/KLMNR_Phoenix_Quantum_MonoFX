import os
import csv
import datetime
import logging
import time
import json

def parse_time(timestr, fmt='%Y-%m-%d %H:%M:%S'):
    """Parsa una stringa di tempo in oggetto datetime, gestendo errori."""
    try:
        return datetime.datetime.strptime(timestr, fmt)
    except Exception:
        return None

def log_signal_tick(symbol, tick, reason=None, log_path=None):
    """Logga un tick di segnale su file CSV."""
    try:
        if log_path is None:
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'signals_tick_log.csv')
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
            report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'trade_decision_report.csv')
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
