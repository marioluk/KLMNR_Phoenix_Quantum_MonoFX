"""
QUANTUM TRADING SYSTEM - MILESTONE EDITION (REV 6.0) PRODUZIONE
Sistema di trading algoritmico basato su entropia, stati quantistici e risk management avanzato

Architettura modulare:
- config: Gestione configurazione
- logging: Sistema di logging avanzato  
- engine: Motore quantistico per analisi tick
- risk: Risk management e drawdown tracking
- trading: Sistema principale di trading
- utils: Funzioni utility e helper
- metrics: Metriche e reporting
- brokers: Gestione multi-broker (The5ers, FTMO, MyForexFunds)
"""

__version__ = "6.0.0"
__author__ = "Quantum Trading Team"

from .trading.main_system import QuantumTradingSystem
from .trading.multi_system import MultiQuantumTradingSystem
from .config.manager import ConfigManager
from .engine.quantum_engine import QuantumEngine
from .risk.manager import QuantumRiskManager
from .logging.setup import setup_logger
from .brokers.manager import BrokerManager
from .brokers.connection import BrokerConnection
from .brokers.config_loader import MultiBrokerConfigLoader

__all__ = [
    'QuantumTradingSystem',
    'MultiQuantumTradingSystem',
    'ConfigManager', 
    'QuantumEngine',
    'QuantumRiskManager',
    'setup_logger',
    'BrokerManager',
    'BrokerConnection',
    'MultiBrokerConfigLoader'
]
