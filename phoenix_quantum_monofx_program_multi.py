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
    # Inizializza QuantumTradingSystem per gestione ordini centralizzata
    from core.quantum_trading_system import QuantumTradingSystem
    trading_system = QuantumTradingSystem(config_path)
    logger.info(f"Simboli attivi: {symbols}")
    logger.info("Avvio ciclo principale di polling prezzi e segnali...")
    last_heartbeat = time.time()
    HEARTBEAT_INTERVAL = 60  # secondi
    while True:
        # Reset giornaliero avanzato con backup tramite core
        trading_system.reset_trade_count_if_new_day()
        for symbol in symbols:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None or tick.bid is None:
                logger.warning(f"Tick non disponibile per {symbol}")
                write_report_row(symbol, "tick", "Tick non disponibile", f"tick={tick}")
                continue
            price = tick.bid
            engine.process_tick(symbol, price)
            signal, signal_price = engine.get_signal(symbol)
            # --- LOGICA DI BLOCCO TRADE DELEGATA AL CORE ---
            can_trade, block_reason = trading_system.can_open_trade(symbol)
            # Determina il tipo di posizione aperta (BUY/SELL) se presente
            positions = mt5.positions_get(symbol=symbol)
            symbol_positions = len(positions) if positions else 0
            open_type = None
            open_ticket = None
            if positions and symbol_positions > 0:
                pos = positions[0]
                open_type = 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL'
                open_ticket = pos.ticket
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
            # Logica direzionale per posizione aperta
            blocked = not can_trade
            if not blocked and open_type is not None:
                if signal == open_type:
                    blocked = True
                    block_reason = f"same_position_type_open ({open_type})"
                elif signal in ("BUY", "SELL") and signal != open_type:
                    # Chiudi la posizione opposta prima di aprire la nuova
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": pos.volume,
                        "type": mt5.ORDER_TYPE_SELL if open_type == 'BUY' else mt5.ORDER_TYPE_BUY,
                        "position": open_ticket,
                        "price": price,
                        "deviation": 10,
                        "magic": 123456,
                        "comment": "PhoenixQuantumAuto-CLOSE",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    close_result = mt5.order_send(close_request)
                    if close_result and close_result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"[POSITION CLOSED] {symbol} posizione {open_type} chiusa con successo. Ticket: {open_ticket}")
                        symbol_positions -= 1
                        open_type = None
                    else:
                        blocked = True
                        block_reason = f"failed_close_opposite ({open_type})"
            logger.info(f"Dettaglio: Confidence: {confidence if confidence is not None else '-'}; Entropia: {entropy if entropy is not None else '-'}; Spin: {spin if spin is not None else '-'}; Buffer tick: {buffer_size}")
            if blocked:
                logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: {block_reason}")
                write_report_row(symbol, "block", f"Blocco: {block_reason}", f"trade_count={trading_system.get_trade_count(symbol)}, symbol_positions={symbol_positions}")
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
                order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
                try:
                    lot_size = config_manager.risk_manager.calculate_lot_size(symbol, order_type, price)
                except Exception as e:
                    logger.warning(f"[LOT SIZE ERROR] Errore nel calcolo della size per {symbol}: {e}")
                    lot_size = 0.01  # fallback di sicurezza
                sl_price, tp_price = config_manager.risk_manager.calculate_dynamic_levels(symbol, order_type, price)
                result = trading_system.send_manual_order(symbol, signal, lot_size, sl=sl_price, tp=tp_price)
                if result.get('success'):
                    trade_executed = True
                    logger.info(f"[TRADE EXECUTED] {symbol} ordine aperto con successo. Ticket: {result.get('ticket')} | Size: {lot_size} | SL: {sl_price} | TP: {tp_price}")
                else:
                    logger.warning(f"[TRADE FAILED] {symbol} ordine non aperto. Errore: {result.get('error')} | Size: {lot_size} | SL: {sl_price} | TP: {tp_price}")
            if trade_executed:
                # Aggiorna trade_count tramite core
                tc = trading_system.get_trade_count()
                tc[symbol] = tc.get(symbol, 0) + 1
                # Salva su file
                today = datetime.now().strftime('%Y-%m-%d')
                with open(trading_system._trade_count_file, 'w', encoding='utf-8') as f:
                    json.dump({'date': today, 'trade_count': tc}, f)
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
