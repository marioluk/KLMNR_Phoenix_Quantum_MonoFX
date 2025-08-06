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
import csv
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

# === GESTIONE TRADE COUNT STATE JSON ===
TRADE_COUNT_PATH = os.path.join(os.path.dirname(__file__), 'logs', 'trade_count_state.json')
def load_trade_count_state(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception:
        return {"date": "", "trade_count": {}}

def save_trade_count_state(path, state):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f)

try:
    config_manager = ConfigManager(config_path)
    engine = config_manager.engine
    symbols = list(config_manager.config.get('symbols', {}).keys())
    logger.info(f"Simboli attivi: {symbols}")
    logger.info("Avvio ciclo principale di polling prezzi e segnali...")
    last_heartbeat = time.time()
    HEARTBEAT_INTERVAL = 60  # secondi
    while True:
        # Carica lo stato trade_count
        trade_count_state = load_trade_count_state(TRADE_COUNT_PATH)
        today = datetime.now().strftime('%Y-%m-%d')
        # Reset giornaliero avanzato con backup
        def backup_trade_count_state(path, date):
            import shutil
            if os.path.isfile(path) and date:
                backup_path = path.replace('.json', f'_{date}_backup.json')
                try:
                    shutil.copy2(path, backup_path)
                except Exception as e:
                    logger.warning(f"Impossibile creare backup trade_count_state: {e}")
        if trade_count_state['date'] != today:
            backup_trade_count_state(TRADE_COUNT_PATH, trade_count_state['date'])
            trade_count_state['date'] = today
            trade_count_state['trade_count'] = {}
            save_trade_count_state(TRADE_COUNT_PATH, trade_count_state)
            logger.info(f"[TRADE COUNT RESET] Reset giornaliero effettuato, backup creato.")
        for symbol in symbols:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None or tick.bid is None:
                logger.warning(f"Tick non disponibile per {symbol}")
                write_report_row(symbol, "tick", "Tick non disponibile", f"tick={tick}")
                continue
            price = tick.bid
            engine.process_tick(symbol, price)
            signal, signal_price = engine.get_signal(symbol)
            # --- LOGICA DI BLOCCO TRADE ---
            blocked = False
            block_reason = None
            # Recupera contatori dal file JSON
            trade_count = trade_count_state['trade_count'].get(symbol, 0)
            max_daily_trades = config_manager.config.get('risk_parameters', {}).get('max_daily_trades', 8)
            current_positions = config_manager.get_current_positions() if hasattr(config_manager, 'get_current_positions') else 0
            max_positions = config_manager.config.get('risk_parameters', {}).get('max_positions', 1)
            # Recupera parametri di segnale per log
            ticks_buffer = list(engine.get_tick_buffer(symbol))
            buffer_size = len(ticks_buffer)
            confidence = None
            entropy = None
            spin = None
            if buffer_size > 0:
                spin_window = min(engine.spin_window, buffer_size)
                recent_ticks = ticks_buffer[-spin_window:]
                spin, confidence = engine.calculate_spin(recent_ticks)
                deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10)
                entropy = engine.calculate_entropy(deltas)
            # Orario di trading
            from utils.utils import is_trading_hours
            trading_hours = is_trading_hours(symbol, config_manager.config)
            # Controllo limiti
            if trade_count >= max_daily_trades:
                blocked = True
                block_reason = f"max_daily_trades ({trade_count}/{max_daily_trades})"
            elif current_positions >= max_positions:
                blocked = True
                block_reason = f"max_positions ({current_positions}/{max_positions})"
            # Logging dettagliato
            logger.info("\n==================== [DEBUG TRADE DECISION] ====================")
            logger.info(f"Symbol: {symbol}\n--------------------")
            logger.info(f"can_trade: {not blocked}")
            logger.info(f"trading_hours: {trading_hours}")
            logger.info(f"Dettaglio: Confidence: {confidence if confidence is not None else '-'}; Entropia: {entropy if entropy is not None else '-'}; Spin: {spin if spin is not None else '-'}; Buffer tick: {buffer_size}")
            if blocked:
                logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: {block_reason}")
                if block_reason.startswith('max_daily_trades'):
                    logger.info(f"🚫 Limite totale trade giornalieri raggiunto: {trade_count}/{max_daily_trades}. Nessun nuovo trade verrà aperto oggi.")
                elif block_reason.startswith('max_positions'):
                    logger.info(f"🚫 Limite posizioni raggiunto: {current_positions}/{max_positions}. Nessun nuovo trade verrà aperto ora.")
                logger.info("")
                write_report_row(symbol, "block", f"Blocco: {block_reason}", f"trade_count={trade_count}, current_positions={current_positions}")
                continue
            else:
                logger.info(f"Segnale: {signal} @ {signal_price:.5f}")
                logger.info("")
            # Log normale se non bloccato
            detail = f"Segnale: {signal} @ {signal_price:.5f}"
            extra = f"price={price:.5f}"
            write_report_row(symbol, "signal", detail, extra)
            logger.debug(f"[{symbol}] Prezzo: {price:.5f} | Segnale: {signal} @ {signal_price:.5f}")
            # === INCREMENTO TRADE COUNT DOPO TRADE ESEGUITO ===
            trade_executed = False
            if signal in ("BUY", "SELL"):
                # Esempio di invio ordine a MT5 (sostituisci con la tua logica reale)
                order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
                lot_size = 0.01  # Sostituisci con la tua logica di calcolo size
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": order_type,
                    "price": price,
                    "deviation": 10,
                    "magic": 123456,
                    "comment": "PhoenixQuantumAuto",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    trade_executed = True
                    logger.info(f"[TRADE EXECUTED] {symbol} ordine aperto con successo. Ticket: {result.order}")
                else:
                    logger.warning(f"[TRADE FAILED] {symbol} ordine non aperto. Retcode: {getattr(result, 'retcode', None)}")
            if trade_executed:
                trade_count_state['trade_count'][symbol] = trade_count + 1
                save_trade_count_state(TRADE_COUNT_PATH, trade_count_state)
        # Heartbeat periodico
        if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
            try:
                engine.check_tick_activity()
                report_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'trade_decision_report.csv')
                if os.path.isfile(report_path):
                    step_counts = {}
                    symbol_counts = {}
                    with open(report_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            step = row.get('step', 'unknown')
                            symbol = row.get('symbol', 'unknown')
                            step_counts[step] = step_counts.get(step, 0) + 1
                            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
                    logger.info(f"[HEARTBEAT REPORT] trade_decision_report.csv: per step: {step_counts} | per symbol: {symbol_counts}")
            except Exception as e:
                logger.warning(f"Errore heartbeat: {e}")
            last_heartbeat = time.time()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Interrotto manualmente dall'utente.")
except Exception as e:
    logger.exception(f"Errore nel ciclo principale: {e}")
