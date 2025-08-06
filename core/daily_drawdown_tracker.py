# daily_drawdown_tracker.py
"""
Modulo DailyDrawdownTracker: traccia il drawdown giornaliero e verifica i limiti di rischio.
"""
from datetime import datetime

import logging
logger = logging.getLogger("phoenix_quantum")

import threading

from typing import Dict, Tuple

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

