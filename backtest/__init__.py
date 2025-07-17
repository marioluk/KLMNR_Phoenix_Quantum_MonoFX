# ====================================================================================
# THE5ERS QUANTUM ALGORITHM - BACKTEST MODULE
# Sistema di backtest e ottimizzazione per algoritmo quantum trading
# ====================================================================================

__version__ = "1.0.0"
__author__ = "The5ers Quantum Team"
__description__ = "Backtest and Optimization System for The5ers High Stakes Challenge"

# Import principali per facilità d'uso
from .backtest_engine import QuantumBacktestEngine, BacktestConfig, The5ersRules
from .parameter_optimizer import QuantumParameterOptimizer
from .results_analyzer import ResultsAnalyzer
from .config import get_default_config, OPTIMIZATION_SCENARIOS

__all__ = [
    'QuantumBacktestEngine',
    'BacktestConfig', 
    'The5ersRules',
    'QuantumParameterOptimizer',
    'ResultsAnalyzer',
    'get_default_config',
    'OPTIMIZATION_SCENARIOS'
]
