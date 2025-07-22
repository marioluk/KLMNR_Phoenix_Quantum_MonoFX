"""
DailyDrawdownTracker - Monitoraggio del drawdown giornaliero con protezione THE5ERS
"""

import logging
import time
from datetime import datetime
from typing import Dict, Tuple

logger = logging.getLogger('QuantumTradingSystem')


class DailyDrawdownTracker:
    """
    Monitora il drawdown giornaliero con protezione per i limiti THE5ERS
    """
    
    def __init__(self, initial_equity: float, config: Dict):
        """
        Inizializza il tracker del drawdown
        
        Args:
            initial_equity: Equity iniziale
            config: Configurazione del sistema (dict o ConfigManager)
        """
        # Estrai il dizionario config se è un ConfigManager
        actual_config = config.config if hasattr(config, 'config') else config
        
        self.daily_high = initial_equity
        self.current_equity = initial_equity
        self.current_balance = initial_equity
        self.last_update_date = datetime.now().date()
        self.currency = actual_config.get('account_currency', 'USD')
        
        try:
            dd_config = actual_config['THE5ERS_specific']['drawdown_protection']
            self.soft_limit = float(dd_config['soft_limit'])
            self.hard_limit = float(dd_config['hard_limit'])
        except KeyError as e:
            raise ValueError(f"Configurazione drawdown mancante: {str(e)}") from e
        
        self.protection_active = False
        self.max_daily_drawdown = 0.0
        self.last_check_time = time.time()

    def update(self, current_equity: float, current_balance: float) -> None:
        """
        Aggiorna i valori di equity e balance
        
        Args:
            current_equity: Equity corrente
            current_balance: Balance corrente
        """
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
        """
        Verifica se sono stati raggiunti i limiti di drawdown
        
        Args:
            current_equity: Equity corrente da verificare
            
        Returns:
            Tupla (soft_limit_hit, hard_limit_hit)
        """
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

    def get_current_drawdown(self) -> float:
        """
        Restituisce il drawdown corrente in percentuale
        
        Returns:
            Drawdown corrente (valore negativo)
        """
        if self.daily_high == 0:
            return 0.0
        return (self.current_equity - self.daily_high) / self.daily_high

    def get_remaining_limit(self) -> Tuple[float, float]:
        """
        Restituisce i margini rimanenti prima dei limiti
        
        Returns:
            Tupla (soft_limit_remaining, hard_limit_remaining) in percentuale
        """
        current_dd = abs(self.get_current_drawdown())
        soft_remaining = max(0, self.soft_limit - current_dd)
        hard_remaining = max(0, self.hard_limit - current_dd)
        return soft_remaining, hard_remaining
