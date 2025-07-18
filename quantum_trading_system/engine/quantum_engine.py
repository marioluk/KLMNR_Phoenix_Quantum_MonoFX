"""
QuantumEngine - Motore principale per l'analisi quantistica dei tick di mercato
"""

import MetaTrader5 as mt5
import numpy as np
import time
import logging
from collections import deque, defaultdict
from threading import Lock
from typing import Dict, List, Tuple, Any
from functools import lru_cache

logger = logging.getLogger('QuantumTradingSystem')


class QuantumEngine:
    """
    Motore principale che elabora i tick di mercato e genera segnali di trading 
    basati sull'entropia e stati quantistici
    """
    
    def __init__(self, config):
        """
        Inizializza il motore quantistico
        
        Args:
            config: ConfigManager o dizionario di configurazione
        """
        # Gestione configurazione
        if hasattr(config, 'get_risk_params'):  # È un ConfigManager
            self._config_manager = config
            self._config = config.config
        else:  # È un dizionario raw
            self._config_manager = None
            self._config = config

        # Buffer e thread safety
        self.tick_buffer = defaultdict(deque)
        self.position_cooldown = {}  # Traccia ultima chiusura per simbolo
        self.buffer_lock = Lock()

        # Parametri configurabili dal JSON
        quantum_params = self._config.get('quantum_params', {})
        self.buffer_size = quantum_params.get('buffer_size', 100)
        self.spin_window = quantum_params.get('spin_window', 20)
        self.min_spin_samples = quantum_params.get('min_spin_samples', 10)
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
        
        # Statistiche segnali per bias detection
        self.signal_stats = {'BUY': 0, 'SELL': 0}
        
    @property
    def config(self) -> Dict:
        """Accesso alla configurazione"""
        return self._config    
    
    def is_in_cooldown_period(self, symbol: str) -> bool:
        """
        Verifica se il simbolo è in un periodo di cooldown
        
        Args:
            symbol: Simbolo da verificare
            
        Returns:
            True se in cooldown, False altrimenti
        """
        # Controlla cooldown normale posizioni (1800s)
        last_close = self.position_cooldown.get(symbol, 0)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        if time.time() - last_close < position_cooldown:
            logger.info(f"Cooldown normale attivo per {symbol} - {position_cooldown - (time.time() - last_close):.0f}s rimanenti")
            return True
            
        # Controlla cooldown segnali (900s)
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        last_signal = self.last_signal_time.get(symbol, 0)
        if time.time() - last_signal < signal_cooldown:
            logger.info(f"Cooldown segnale attivo per {symbol} - {signal_cooldown - (time.time() - last_signal):.0f}s rimanenti")
            return True
            
        return False

    def can_trade(self, symbol: str) -> bool:
        """
        Verifica se è possibile aprire una nuova posizione
        
        Args:
            symbol: Simbolo da verificare
            
        Returns:
            True se si può aprire una posizione, False altrimenti
        """
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
            
        return True
        
    def record_trade_close(self, symbol: str) -> None:
        """
        Registra la chiusura di una posizione per il cooldown
        
        Args:
            symbol: Simbolo della posizione chiusa
        """
        # Verifica che la posizione sia effettivamente chiusa
        if mt5.positions_get(symbol=symbol) is None or len(mt5.positions_get(symbol=symbol)) == 0:
            self.position_cooldown[symbol] = time.time()
            logger.debug(f"Cooldown registrato per {symbol} (1800s)")

    @staticmethod
    @lru_cache(maxsize=1000)
    def calculate_entropy(deltas: Tuple[float]) -> float:
        """
        Calcola l'entropia normalizzata (tra 0 e 1) da una sequenza di delta di prezzo
        
        Args:
            deltas: Tupla di differenze di prezzo
            
        Returns:
            Entropia normalizzata tra 0 e 1
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
        Calcola lo "spin quantistico" (bilanciamento direzionale) e la confidenza
        
        Args:
            ticks: Lista di tick con 'price', 'delta', 'direction'
            
        Returns:
            Tupla (spin, confidenza)
        """
        if not ticks or len(ticks) < self.min_spin_samples:
            return 0.0, 0.0
        
        # Cache key con hash dei tick recenti
        cache_key = hash(tuple((t['price'], t['direction']) for t in ticks[-self.spin_window:]))
        
        return self._get_cached(
            self._spin_cache,
            cache_key,
            self._calculate_spin_impl,
            ticks[-self.spin_window:]
        )

    def _calculate_spin_impl(self, ticks: List[Dict]) -> Tuple[float, float]:
        """
        Implementazione del calcolo dello spin senza cache
        
        Args:
            ticks: Lista di tick da analizzare
            
        Returns:
            Tupla (spin, confidenza)
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
        Calcola la volatilità quantistica combinando entropia e spin
        
        Args:
            symbol: Simbolo da analizzare
            window: Finestra di tick da considerare
            
        Returns:
            Volatilità quantistica
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

    def process_tick(self, symbol: str, price: float) -> None:
        """
        Aggiunge un nuovo tick al buffer e calcola delta/direzione
        
        Args:
            symbol: Simbolo del tick
            price: Prezzo del tick
        """
        if symbol not in self.tick_buffer:
            with self.buffer_lock:
                self.tick_buffer[symbol] = deque(maxlen=self.buffer_size)
            logger.info(f"Inizializzato buffer per {symbol}")
        
        if price <= 0:
            return
        
        # Log primo tick
        if len(self.tick_buffer[symbol]) == 0:
            logger.info(f"Primo tick ricevuto per {symbol}: {price}")
        
        # Calcola delta e direzione
        if len(self.tick_buffer[symbol]) > 0:
            last_price = self.tick_buffer[symbol][-1]['price']
            delta = price - last_price
            direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
        else:
            delta = 0
            direction = 0  # Neutro
        
        self.tick_buffer[symbol].append({
            'price': price,
            'delta': delta,
            'direction': direction,
            'time': time.time()
        })

    def get_signal(self, symbol: str, for_trading: bool = False) -> Tuple[str, float]:
        """
        Genera un segnale di trading basato su entropia e spin quantistico
        
        Args:
            symbol: Simbolo da analizzare
            for_trading: Se True, attiva il cooldown dopo il segnale
            
        Returns:
            Tupla (segnale, prezzo) - "BUY"/"SELL"/"HOLD"
        """
        ticks = list(self.tick_buffer.get(symbol, []))
        
        # 1. Verifica buffer
        if len(ticks) < self.min_spin_samples:
            logger.debug(f"{symbol}: Buffer insufficiente ({len(ticks)}/{self.min_spin_samples} ticks)")
            return "HOLD", 0.0

        # 2. Calcolo spin e confidenza
        spin_window = min(self.spin_window, len(ticks))
        recent_ticks = ticks[-spin_window:]
        spin, confidence = self.calculate_spin(recent_ticks)
        
        # 3. Filtri conservativi
        if confidence < 0.8:
            logger.debug(f"{symbol}: Confidence troppo bassa ({confidence:.2f}/0.8)")
            return "HOLD", 0.0
            
        # 4. Verifica cooldown segnali
        last_signal_time = self.last_signal_time.get(symbol, 0)
        if time.time() - last_signal_time < self.signal_cooldown:
            remaining = int(self.signal_cooldown - (time.time() - last_signal_time))
            logger.debug(f"{symbol}: In cooldown segnali ({remaining}s rimanenti)")
            return "HOLD", 0.0

        # 5. Calcolo metriche
        deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10)
        entropy = self.calculate_entropy(deltas)
        volatility = 1 + abs(spin) * entropy
        
        thresholds = self.config.get('quantum_params', {}).get('entropy_thresholds', {})
        base_buy_thresh = thresholds.get('buy_signal', 0.55)
        base_sell_thresh = thresholds.get('sell_signal', 0.45)
        
        # Applica volatilità
        buy_thresh = base_buy_thresh * (1 + (volatility - 1) * 0.5)
        sell_thresh = base_sell_thresh * (1 - (volatility - 1) * 0.5)

        # 6. Generazione segnale
        signal = "HOLD"
        
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

        # 7. Registrazione segnale
        if signal != "HOLD":
            if for_trading:
                self.last_signal_time[symbol] = time.time()
            
            # Statistiche bias
            self.signal_stats[signal] += 1
            
            buy_ratio = self.signal_stats['BUY'] / (self.signal_stats['BUY'] + self.signal_stats['SELL'])
            
            logger.info(
                f"Segnale {signal} per {symbol}: "
                f"E={entropy:.2f} S={spin:.2f} V={volatility:.2f} C={confidence:.2f} | "
                f"Soglie: B={buy_thresh:.2f} S={sell_thresh:.2f} | "
                f"Bias Check: BUY={self.signal_stats['BUY']} SELL={self.signal_stats['SELL']} Ratio={buy_ratio:.2f}"
            )
            
            # Avviso bias eccessivo
            if (self.signal_stats['BUY'] + self.signal_stats['SELL']) > 10:
                if buy_ratio > 0.8:
                    logger.warning(f"⚠️ BIAS LONG DETECTED: {buy_ratio:.1%} buy signals!")
                elif buy_ratio < 0.2:
                    logger.warning(f"⚠️ BIAS SHORT DETECTED: {buy_ratio:.1%} buy signals!")
        
        return signal, recent_ticks[-1]['price'] if recent_ticks else 0.0

    def _get_cached(self, cache_dict: Dict, key: Any, calculate_func, *args) -> Any:
        """
        Sistema di cache con timeout per i calcoli
        
        Args:
            cache_dict: Dizionario cache
            key: Chiave cache
            calculate_func: Funzione di calcolo
            *args: Argomenti per la funzione
            
        Returns:
            Risultato calcolato o da cache
        """
        now = time.time()
        if key in cache_dict:
            value, timestamp = cache_dict[key]
            if now - timestamp < self._cache_timeout:
                return value
        
        # Calcola nuovo valore
        result = calculate_func(*args)
        cache_dict[key] = (result, now)
        return result

    def _get_pip_size(self, symbol: str) -> float:
        """
        Calcola la dimensione del pip per il simbolo
        
        Args:
            symbol: Simbolo di trading
            
        Returns:
            Dimensione del pip
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                if symbol_info.digits == 5 or symbol_info.digits == 3:
                    return 0.0001 if symbol_info.digits == 5 else 0.01
                else:
                    return 10 ** (-symbol_info.digits + 1)
            
            # Fallback per simboli comuni
            if 'JPY' in symbol:
                return 0.01
            elif 'XAU' in symbol or 'GOLD' in symbol:
                return 0.1
            else:
                return 0.0001
                
        except Exception as e:
            logger.error(f"Errore calcolo pip size per {symbol}: {e}")
            return 0.0001

    def get_remaining_cooldown(self, symbol: str) -> float:
        """
        Restituisce il tempo rimanente di cooldown per un simbolo
        
        Args:
            symbol: Simbolo da verificare
            
        Returns:
            Secondi rimanenti di cooldown (0 se non in cooldown)
        """
        now = time.time()
        
        # Controlla cooldown posizioni
        last_close = self.position_cooldown.get(symbol, 0)
        position_cooldown = self.config.get('risk_parameters', {}).get('position_cooldown', 1800)
        position_remaining = max(0, position_cooldown - (now - last_close))
        
        # Controlla cooldown segnali
        last_signal = self.last_signal_time.get(symbol, 0)
        signal_cooldown = self.config.get('quantum_params', {}).get('signal_cooldown', 900)
        signal_remaining = max(0, signal_cooldown - (now - last_signal))
        
        return max(position_remaining, signal_remaining)

    def get_quantum_params(self, symbol: str) -> Dict:
        """
        Ottiene i parametri quantistici per un simbolo specifico
        
        Args:
            symbol: Simbolo di trading
            
        Returns:
            Dizionario con i parametri quantistici
        """
        base_params = self.config.get('quantum_params', {})
        symbol_config = self.config.get('symbols', {}).get(symbol, {})
        symbol_params = symbol_config.get('quantum_params_override', {})
        
        # Merge dei parametri con override per simbolo
        return {**base_params, **symbol_params}
