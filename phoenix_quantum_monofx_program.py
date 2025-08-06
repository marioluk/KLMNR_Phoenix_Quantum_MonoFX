# === IMPORT STANDARD E CORE CENTRALIZZATI ===
import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime, time as dt_time, timedelta
from typing import Tuple, Any
import numpy as np
import MetaTrader5 as mt5
# ===================== IMPORT DELLE CLASSI CORE =====================
from utils.utils import log_signal_tick, write_report_row, load_json_file, save_json_file, safe_sleep, parse_time_range, set_symbol_data
from utils.constants import DEFAULT_TIME_RANGE, DEFAULT_TRADING_HOURS, DEFAULT_SPREADS, DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, DEFAULT_LOG_FORMAT, DEFAULT_LOG_MAX_BYTES, DEFAULT_LOG_BACKUP_COUNT
from core.config_manager import ConfigManager
from core.quantum_engine import QuantumEngine
from core.daily_drawdown_tracker import DailyDrawdownTracker
from core.quantum_risk_manager import QuantumRiskManager
# from utils.utils import setup_logger  # se serve per get_logger()


def get_logger():
    """Stub: restituisce il logger globale."""
    return globals().get('logger', setup_logger())




# === INIZIALIZZAZIONE LOGGING DA CONFIG ===
import os
import time
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config_autonomous_challenge_production_ready.json')
if not os.path.exists(config_path):
    print(f"File di configurazione non trovato: {config_path}")
    exit(1)
with open(config_path, 'r', encoding='utf-8') as f:
    config_data = json.load(f)
logging_config = config_data.get('config', {}).get('logging', {})
log_file = logging_config.get('log_file', 'phoenix_quantum.log')
max_size_mb = logging_config.get('max_size_mb', 10)
backup_count = logging_config.get('backup_count', 5)
log_level = logging_config.get('log_level', 'INFO').upper()
log_format = '%(asctime)s [%(levelname)s] %(message)s'

os.makedirs(os.path.dirname(log_file), exist_ok=True)

handlers = [logging.StreamHandler()]
try:
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(file_handler)
except Exception as e:
    print(f"[WARNING] Impossibile configurare il file di log: {e}")

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format=log_format,
    handlers=handlers
)
logger = logging.getLogger("phoenix_quantum")


# === INIZIALIZZAZIONE MT5 ALL'AVVIO ===

mt5_config = config_data.get('config', {}).get('metatrader5', {})
logger.info(f"Provo a inizializzare MT5 con: {mt5_config}")
if not mt5.initialize(
    path=mt5_config.get('path', 'C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe'),
    login=int(mt5_config.get('login', 0)),
    password=mt5_config.get('password', ''),
    server=mt5_config.get('server', 'FivePercentOnline-Real'),
    port=int(mt5_config.get('port', 18889))
):
    logger.error(f"Errore inizializzazione MT5: {mt5.last_error()}")
    exit(2)
logger.info("MT5 inizializzato e collegato con successo!")

# === AVVIO LOGICA DI TRADING AUTOMATICA ===
try:
    config_manager = ConfigManager(config_path)
    engine = config_manager.engine
    symbols = list(config_manager.config.get('symbols', {}).keys())
    logger.info(f"Simboli attivi: {symbols}")
    logger.info("Avvio ciclo principale di polling prezzi e segnali...")
    last_heartbeat = time.time()
    HEARTBEAT_INTERVAL = 60  # secondi
    while True:
        for symbol in symbols:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None or tick.bid is None:
                logger.warning(f"Tick non disponibile per {symbol}")
                # Logga anche la decisione di non processare per tick mancante
                write_report_row(symbol, "tick", "Tick non disponibile", f"tick={tick}")
                print(f"[REPORT] {symbol}, tick, Tick non disponibile, tick={tick}")
                continue
            price = tick.bid
            engine.process_tick(symbol, price)
            signal, signal_price = engine.get_signal(symbol)
            # Logga la decisione di segnale su report CSV e stampa a video
            detail = f"Segnale: {signal} @ {signal_price:.5f}"
            extra = f"price={price:.5f}"
            write_report_row(symbol, "signal", detail, extra)
            print(f"[REPORT] {symbol}, signal, {detail}, {extra}")
            logger.debug(f"[{symbol}] Prezzo: {price:.5f} | Segnale: {signal} @ {signal_price:.5f}")
        # Heartbeat periodico
        if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
            try:
                engine.check_tick_activity()
            except Exception as e:
                logger.warning(f"Errore heartbeat: {e}")
            last_heartbeat = time.time()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Interrotto manualmente dall'utente.")
except Exception as e:
    logger.exception(f"Errore nel ciclo principale: {e}")
