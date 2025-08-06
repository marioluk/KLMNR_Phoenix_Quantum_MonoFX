# Necessario per il caricamento della configurazione
import json
# config_manager.py
"""
Modulo ConfigManager: gestisce il caricamento e la validazione della configurazione del sistema trading.
"""

import os
import threading
from collections import defaultdict
from typing import Optional, Dict
import logging
import MetaTrader5 as mt5
from utils.utils import validate_config
from utils.constants import DEFAULT_SPREADS
from core.quantum_engine import QuantumEngine
from core.quantum_risk_manager import QuantumRiskManager
from core.trading_metrics import TradingMetrics

class ConfigManager:
    def __init__(self, config_path: str) -> None:
        """Costruttore principale thread-safe"""
        from threading import Lock
        self.logger = logging.getLogger("phoenix_quantum")
        self.logger.info(
            "\n==================== [AVVIO QUANTUM TRADING SYSTEM] ====================\n"
            f"File configurazione: {config_path}\n"
            "------------------------------------------------------\n"
        )
        # self._setup_logger(config_path)  # RIMOSSO: non implementato, logger già configurato nel main
        self.logger.info("✅ Logger configurato")
        self._config_path = config_path
        self.running = False
        self.logger.info("📋 Caricamento configurazione...")
        # Caricamento diretto della configurazione dal file JSON
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        # La struttura attesa è config_data['config']
        self.config = config_data['config']
        # Validazione automatica della configurazione
        try:
            validate_config(self.config)
            self.logger.info("✅ Configurazione caricata e validata")
        except Exception as e:
            self.logger.critical(f"Errore di validazione configurazione: {e}")
            raise
        # Se la configurazione non contiene simboli, logga un warning
        if 'symbols' not in self.config:
            self.logger.warning("La configurazione non contiene la chiave 'symbols'.")
        self.logger.info(
            "\n-------------------- [SIMBOLI CONFIGURATI] ----------------------\n"
            f"Simboli trovati: {list(self.config['symbols'].keys())}\n"
            "------------------------------------------------------\n"
        )
        self._config = self.config
        self.logger.info("🔄 Inizializzazione componenti core...")
        # self._initialize_mt5() rimosso: MT5 già inizializzato nel main
        # self._activate_symbols() rimosso: non implementato
        self.logger.info("🧠 Inizializzazione Quantum Engine...")
        self.engine = QuantumEngine(self)
        self.logger.info("✅ Quantum Engine pronto")
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
            self.logger.warning("Account info non disponibile, uso fallback per la valuta.")
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
    
    # Restituisce il numero di posizioni aperte per uno specifico simbolo (via MT5)
    def get_positions_for_symbol(self, symbol: str) -> int:
        try:
            positions = mt5.positions_get(symbol=symbol)
            return len(positions) if positions else 0
        except Exception as e:
            self.logger.warning(f"[ConfigManager] Errore nel recupero posizioni per {symbol}: {e}")
            return 0

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
            self.logger.error(f"[ConfigManager] Errore determinazione max_spread per {symbol}: {str(e)}")
            return 20.0
     
