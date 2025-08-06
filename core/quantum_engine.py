# quantum_engine.py
"""
Modulo QuantumEngine: motore principale per la generazione di segnali di trading quantistici.
"""
import threading
import time
from collections import defaultdict, deque
from functools import lru_cache
from typing import Tuple, List, Dict
import numpy as np
# Importa costanti e utilità

from utils.constants import DEFAULT_SPREADS
from utils.utils import log_signal_tick
import MetaTrader5 as mt5
import datetime

class QuantumEngine:
    def check_tick_activity(self):
        """Monitoraggio stato mercato e qualità dati con heartbeat. Log dettagliato se i tick non arrivano."""
        current_time = time.time()
        issues = []
        warning_symbols = []
        heartbeat_data = []
        try:
            if not mt5.terminal_info().connected:
                self.logger.warning("Connessione MT5 non disponibile")
                return False
        except Exception as e:
            self.logger.error(f"Errore accesso terminal_info MT5: {e}")
            return False
        available_symbols = [s.name for s in mt5.symbols_get() or []]
        symbols = list(self.config.get('symbols', {}).keys())
        for symbol in symbols:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    symbol_info = mt5.symbol_info(symbol)
                    is_visible = symbol_info.visible if symbol_info else False
                    self.logger.warning(
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
                    if len(ticks) == 0:
                        spin = 0
                        confidence = 0.0
                        volatility = 1.0
                        self.logger.warning(f"[BUFFER EMPTY] {symbol}: buffer tick vuoto - nessuna metrica calcolata, nessun segnale generabile. Possibili cause: feed dati assente, connessione MT5, mercato chiuso o errore precedente. Verifica log errori e stato connessione.")
                    else:
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
                # (is_trading_hours richiede config, qui si assume sempre attivo per semplicità)
                symbol_config = self.config.get('symbols', {}).get(symbol, {})
                max_spread = symbol_config.get('max_spread', self.config.get('risk_parameters', {}).get('max_spread', 20))
                # Se max_spread è un dict, estrai il valore corretto
                if isinstance(max_spread, dict):
                    max_spread_val = max_spread.get(symbol, max_spread.get('default', 20))
                else:
                    max_spread_val = max_spread
                if spread > max_spread_val:
                    issues.append(f"{symbol}: Spread {spread:.1f}p > max {max_spread_val:.1f}p")
                if len(self.get_tick_buffer(symbol)) < self.min_spin_samples:
                    warning_symbols.append(symbol)
            except Exception as e:
                self.logger.error(f"Errore monitoraggio {symbol}: {str(e)}", exc_info=True)
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
            self.logger.info(hb_msg)
            try:
                positions_count = len(mt5.positions_get() or [])
                self.logger.info(f"Sistema attivo - Posizioni: {positions_count}/1")
            except Exception:
                pass
        else:
            self.logger.info("\n==================== [HEARTBEAT] ====================\n"
                            "Nessun tick valido ricevuto per nessun simbolo!\n"
                            "Possibile problema di connessione, dati o mercato chiuso.\n"
                            "======================================================\n")
            try:
                positions_count = len(mt5.positions_get() or [])
                self.logger.info(f"Sistema attivo - Posizioni: {positions_count}/1")
            except Exception:
                pass
        if warning_symbols:
            self.logger.warning(f"Buffer insufficiente: {', '.join(warning_symbols[:3])}")
        if issues:
            self.logger.warning(f"Problemi: {' | '.join(issues[:3])}")
        return True
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.config = config_manager.config if hasattr(config_manager, 'config') else config_manager
        self._runtime_lock = threading.RLock()
        self._tick_buffer = defaultdict(deque)
        self._position_cooldown = {}
        self._last_signal_time = {}
        self._volatility_cache = {}
        self._spin_cache = {}
        self._signal_stats = {'BUY': 0, 'SELL': 0}
        self._last_warning_time = {}
        qp = self.config.get('quantum_params', {})
        self.buffer_size = qp.get('buffer_size', 100)
        self.spin_window = qp.get('spin_window', 20)
        self.min_spin_samples = qp.get('min_spin_samples', 10)
        self.spin_threshold = qp.get('spin_threshold', 0.25)
        self.signal_cooldown = qp.get('signal_cooldown', 300)
        self.entropy_thresholds = qp.get('entropy_thresholds', {'buy_signal': 0.55, 'sell_signal': 0.45})
        for symbol in self.config.get('symbols', {}):
            self._tick_buffer[symbol] = deque(maxlen=self.buffer_size)
        self._cache_timeout = 60
        self.warning_cooldown = 300
        self.last_confidence = None
        import logging
        self.logger = logging.getLogger("phoenix_quantum")

    def get_tick_buffer(self, symbol):
        return self._tick_buffer[symbol]

    def append_tick(self, symbol, tick):
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


    def is_in_cooldown_period(self, symbol: str) -> bool:
        last_close = self.get_position_cooldown(symbol)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        if time.time() - last_close < position_cooldown:
            self.logger.info(f"Cooldown normale attivo per {symbol} - {position_cooldown - (time.time() - last_close):.0f}s rimanenti")
            return True
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.get_last_signal_time(symbol)
        if time.time() - last_signal < signal_cooldown:
            self.logger.debug(f"Cooldown segnale attivo per {symbol} - {signal_cooldown - (time.time() - last_signal):.0f}s rimanenti")
            return True
        return False

    def can_trade(self, symbol: str) -> bool:
        position_limits = getattr(self, 'position_limits', {})
        max_positions_per_symbol = getattr(self, 'max_positions_per_symbol', None)
        if max_positions_per_symbol is not None:
            current_limit = position_limits.get(symbol, 0)
            if current_limit >= max_positions_per_symbol:
                self.logger.info(f"[POSITION LIMIT] Symbol: {symbol} | Current: {current_limit} | Max Allowed: {max_positions_per_symbol}")
                return False
        if self.is_in_cooldown_period(symbol):
            return False
        try:
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                self.logger.error(f"Impossibile ottenere info simbolo {symbol}")
                return False
            current_spread = (symbol_info.ask - symbol_info.bid) / self._get_pip_size(symbol)
            symbol_config = self.config.get('symbols', {}).get(symbol, {})
            max_spread = symbol_config.get('max_spread', self.config.get('risk_parameters', {}).get('max_spread', {}))
            if isinstance(max_spread, dict):
                max_allowed = max_spread.get(symbol, max_spread.get('default', 20))
            else:
                max_allowed = max_spread
            if current_spread > max_allowed:
                self.logger.warning(f"Spread {symbol} troppo alto: {current_spread:.1f}p > {max_allowed}p")
                return False
        except Exception as e:
            self.logger.error(f"Errore verifica spread {symbol}: {e}")
            return False
        positions = mt5.positions_get()
        if positions and len(positions) >= self.config.get('risk_parameters', {}).get('max_positions', 1):
            self.logger.warning(f"Massimo numero posizioni raggiunto: {len(positions)}")
            return False
        return True

    def record_trade_close(self, symbol: str):
        if mt5.positions_get(symbol=symbol) is None or len(mt5.positions_get(symbol=symbol)) == 0:
            self.set_position_cooldown(symbol, time.time())
            self.logger.info(f"Cooldown registrato per {symbol} (1800s)")

    @staticmethod
    @lru_cache(maxsize=1000)
    def calculate_entropy(deltas: Tuple[float]) -> float:
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
        if not ticks or len(ticks) < self.min_spin_samples:
            return 0.0, 0.0
        cache_key = hash(tuple((t['price'], t['direction']) for t in ticks[-self.spin_window:]))
        return self._get_cached(self._spin_cache, cache_key, self._calculate_spin_impl, ticks[-self.spin_window:])

    def _calculate_spin_impl(self, ticks: List[Dict]) -> Tuple[float, float]:
        try:
            if len(ticks) < 5:
                return 0.0, 0.0
            valid_ticks = [t for t in ticks if t.get('direction', 0) != 0]
            if len(valid_ticks) < 3:
                return 0.0, 0.0
            positive = sum(1 for t in valid_ticks if t.get('direction', 0) > 0)
            negative = sum(1 for t in valid_ticks if t.get('direction', 0) < 0)
            total = len(valid_ticks)
            raw_spin = (positive - negative) / total
            balance_deviation = abs(positive - negative) / total
            confidence = min(1.0, balance_deviation * np.sqrt(total))
            return raw_spin, confidence
        except Exception:
            return 0.0, 0.0

    def calculate_quantum_volatility(self, symbol: str, window: int = 50) -> float:
        def _calculate():
            ticks = list(self.get_tick_buffer(symbol))
            if len(ticks) < window:
                return 1.0
            deltas = np.array([t['delta'] for t in ticks[-window:]])
            prob_dist = np.abs(deltas) / (np.sum(np.abs(deltas)) + 1e-10)
            entropy = -np.sum(prob_dist * np.log(prob_dist + 1e-10)) / np.log(window)
            spin, _ = self._calculate_spin_impl(ticks)
            return 1 + abs(spin) * entropy
        return self._get_cached(self._volatility_cache, symbol, _calculate)

    def process_tick(self, symbol: str, price: float):
        buf = self.get_tick_buffer(symbol)
        if price <= 0:
            self.logger.warning(f"[process_tick] Prezzo non valido per {symbol}: {price}")
            return
        if len(buf) > 0:
            last_price = buf[-1]['price']
            delta = price - last_price
            direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
        else:
            delta = 0
            direction = 0
        tick = {
            'price': price,
            'delta': delta,
            'direction': direction,
            'time': time.time()
        }
        self.append_tick(symbol, tick)
        self.logger.debug(f"[TICK] {symbol}: price={price}, delta={delta}, direction={direction}, buffer_size={len(self.get_tick_buffer(symbol))}")
        if len(self.get_tick_buffer(symbol)) == 0:
            self.logger.warning(f"[process_tick] Buffer vuoto dopo inserimento per {symbol}.")

    def get_signal(self, symbol: str) -> Tuple[str, float]:
        ticks = list(self.get_tick_buffer(symbol))
        if len(ticks) < self.min_spin_samples:
            signal = "HOLD"
            last_tick_price = 0.0
            # Log anche i casi HOLD per buffer insufficiente
            log_signal_tick(symbol, {
                'price': last_tick_price,
                'entropy': 0.0,
                'spin': 0.0,
                'confidence': 0.0,
                'signal': signal
            }, reason="Buffer tick insufficiente")
            self.logger.debug(f"[CSV] {symbol}, {last_tick_price}, 0.0, 0.0, 0.0, {signal}, Buffer tick insufficiente")
            return signal, last_tick_price
        spin_window = min(self.spin_window, len(ticks))
        recent_ticks = ticks[-spin_window:]
        spin, confidence = self.calculate_spin(recent_ticks)
        last_tick_price = recent_ticks[-1]['price'] if recent_ticks else 0.0
        if confidence < 0.8:
            signal = "HOLD"
            log_signal_tick(symbol, {
                'price': last_tick_price,
                'entropy': 0.0,
                'spin': spin,
                'confidence': confidence,
                'signal': signal
            }, reason="Confidence troppo bassa")
            self.logger.debug(f"[CSV] {symbol}, {last_tick_price}, 0.0, {spin}, {confidence}, {signal}, Confidence troppo bassa")
            return signal, last_tick_price
        last_signal_time = self.get_last_signal_time(symbol)
        if self._check_signal_cooldown(symbol, last_signal_time):
            signal = "HOLD"
            log_signal_tick(symbol, {
                'price': last_tick_price,
                'entropy': 0.0,
                'spin': spin,
                'confidence': confidence,
                'signal': signal
            }, reason="Cooldown segnale attivo")
            self.logger.debug(f"[CSV] {symbol}, {last_tick_price}, 0.0, {spin}, {confidence}, {signal}, Cooldown segnale attivo")
            return signal, last_tick_price
        deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10)
        entropy = self.calculate_entropy(deltas)
        volatility = 1 + abs(spin) * entropy
        buy_thresh, sell_thresh = self._calculate_signal_thresholds(volatility)
        buy_condition = entropy > buy_thresh and spin > self.spin_threshold * confidence
        sell_condition = entropy < sell_thresh and spin < -self.spin_threshold * confidence
        if buy_condition:
            signal = "BUY"
            log_signal_tick(symbol, {
                'price': last_tick_price,
                'entropy': entropy,
                'spin': spin,
                'confidence': confidence,
                'signal': signal
            }, reason="Condizioni BUY")
            self.logger.debug(f"[CSV] {symbol}, {last_tick_price}, {entropy}, {spin}, {confidence}, {signal}, Condizioni BUY")
            return signal, last_tick_price
        elif sell_condition:
            signal = "SELL"
            log_signal_tick(symbol, {
                'price': last_tick_price,
                'entropy': entropy,
                'spin': spin,
                'confidence': confidence,
                'signal': signal
            }, reason="Condizioni SELL")
            self.logger.debug(f"[CSV] {symbol}, {last_tick_price}, {entropy}, {spin}, {confidence}, {signal}, Condizioni SELL")
            return signal, last_tick_price
        signal = "HOLD"
        log_signal_tick(symbol, {
            'price': last_tick_price,
            'entropy': entropy,
            'spin': spin,
            'confidence': confidence,
            'signal': signal
        }, reason="Nessuna condizione BUY/SELL")
        self.logger.debug(f"[CSV] {symbol}, {last_tick_price}, {entropy}, {spin}, {confidence}, {signal}, Nessuna condizione BUY/SELL")
        return signal, last_tick_price

    def _check_signal_cooldown(self, symbol: str, last_signal_time: float) -> bool:
        if time.time() - last_signal_time < self.signal_cooldown:
            remaining = int(self.signal_cooldown - (time.time() - last_signal_time))
            self.logger.info(f"{symbol}: Cooldown segnale attivo ({remaining}s rimanenti)")
            return True
        return False

    def _calculate_signal_thresholds(self, volatility: float) -> tuple:
        thresholds = self.config.get('quantum_params', {}).get('entropy_thresholds', {})
        base_buy_thresh = thresholds.get('buy_signal', 0.55)
        base_sell_thresh = thresholds.get('sell_signal', 0.45)
        buy_thresh = base_buy_thresh * (1 + (volatility - 1) * 0.5)
        sell_thresh = base_sell_thresh * (1 - (volatility - 1) * 0.5)
        return buy_thresh, sell_thresh

    def _get_cached(self, cache_dict, key, calculate_func, *args):
        acquired = self._runtime_lock.acquire(timeout=2.0)
        if not acquired:
            return (0.0, 0.0)
        try:
            now = time.time()
            cache = cache_dict
            if key in cache:
                value, timestamp = cache[key]
                if now - timestamp < self._cache_timeout:
                    return value
            try:
                value = calculate_func(*args)
            except Exception:
                value = (0.0, 0.0)
            cache[key] = (value, now)
            return value
        finally:
            self._runtime_lock.release()

    def _get_pip_size(self, symbol: str) -> float:
        with self._runtime_lock:
            try:
                info = mt5.symbol_info(symbol)
                if info and info.point > 0:
                    return info.point
                pip_map = {
                    'BTCUSD': 1.0,
                    'ETHUSD': 0.1,
                    'XAUUSD': 0.01,
                    'SP500': 0.1,
                    'NAS100': 0.1,
                    'default': 0.0001
                }
                base_symbol = symbol.split('.')[0]
                return pip_map.get(base_symbol, pip_map['default'])
            except Exception:
                return 0.0001

    def get_quantum_params(self, symbol: str) -> dict:
        base_params = self.config.get('quantum_params', {})
        symbol_config = self.config.get('symbols', {}).get(symbol, {})
        if 'quantum_params_override' in symbol_config:
            return {**base_params, **symbol_config['quantum_params_override']}
        return base_params
    