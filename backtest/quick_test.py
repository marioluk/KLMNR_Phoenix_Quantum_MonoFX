#!/usr/bin/env python3
# ====================================================================================
# QUICK TEST - THE5ERS QUANTUM BACKTEST
# Test rapido del sistema di backtest
# ====================================================================================

import sys
import os
import logging
from datetime import datetime

# Aggiungi percorso parent per import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging semplice
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Testa gli import necessari"""
    try:
        logger.info("Testing imports...")
        
        # Test import algoritmo principale
        import sys
        import importlib.util
        import os
        
        # Carica il file principale usando importlib
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PRO-THE5ERS-QM-PHOENIX-GITCOP.py')
        spec = importlib.util.spec_from_file_location("quantum_module", file_path)
        quantum_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quantum_module)
        
        # Ottieni le classi
        QuantumEngine = quantum_module.QuantumEngine
        ConfigManager = quantum_module.ConfigManager
        
        logger.info("✓ Algoritmo principale importato")
        
        # Test import backtest engine
        from backtest_engine import QuantumBacktestEngine, BacktestConfig, The5ersRules
        logger.info("✓ Backtest engine importato")
        
        # Test import configurazione
        from config import get_default_config
        logger.info("✓ Configurazione importata")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Errore import: {e}")
        return False

def test_config_loading():
    """Testa il caricamento della configurazione"""
    try:
        logger.info("Testing config loading...")
        
        from config import get_default_config
        config = get_default_config()
        
        # Verifica sezioni principali
        required_sections = ['quantum_params', 'risk_parameters', 'symbols']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Sezione mancante: {section}")
        
        logger.info(f"✓ Configurazione caricata ({len(config)} sezioni)")
        logger.info(f"✓ Simboli configurati: {list(config['symbols'].keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Errore config: {e}")
        return False

def test_synthetic_data():
    """Testa la generazione di dati sintetici"""
    try:
        logger.info("Testing synthetic data generation...")
        
        from backtest_engine import HistoricalDataHandler
        
        data_handler = HistoricalDataHandler()
        
        # Genera dati di test
        df = data_handler.load_historical_data(
            symbol="EURUSD",
            start_date="2024-01-01",
            end_date="2024-01-02",
            timeframe="M1"
        )
        
        logger.info(f"✓ Dati sintetici generati: {len(df)} righe")
        logger.info(f"✓ Colonne: {list(df.columns)}")
        
        # Test tick conversion
        from datetime import datetime
        ticks = data_handler.get_tick_data(
            symbol="EURUSD",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 10, 0)
        )
        
        logger.info(f"✓ Tick data convertiti: {len(ticks)} tick")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Errore dati sintetici: {e}")
        return False

def test_quantum_engine():
    """Testa il quantum engine"""
    try:
        logger.info("Testing quantum engine...")
        
        from config import get_default_config
        import sys
        import importlib.util
        import os
        
        # Carica il file principale usando importlib
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PRO-THE5ERS-QM-PHOENIX-GITCOP.py')
        spec = importlib.util.spec_from_file_location("quantum_module", file_path)
        quantum_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quantum_module)
        
        QuantumEngine = quantum_module.QuantumEngine
        ConfigManager = quantum_module.ConfigManager
        
        config = get_default_config()
        config_manager = ConfigManager(config)
        quantum_engine = QuantumEngine(config_manager)
        
        # Test processamento tick
        test_prices = [1.1000, 1.1001, 1.1002, 1.0999, 1.1003]
        
        for price in test_prices:
            quantum_engine.process_tick("EURUSD", price)
        
        logger.info(f"✓ Quantum engine processato {len(test_prices)} tick")
        
        # Test generazione segnale
        signal, price = quantum_engine.get_signal("EURUSD")
        logger.info(f"✓ Segnale generato: {signal} @ {price}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Errore quantum engine: {e}")
        return False

def test_simple_backtest():
    """Testa un backtest semplice"""
    try:
        logger.info("Testing simple backtest...")
        
        from config import get_default_config
        from backtest_engine import QuantumBacktestEngine, BacktestConfig, The5ersRules
        
        # Configurazione minima
        config = get_default_config()
        
        backtest_config = BacktestConfig(
            start_date="2024-01-01",
            end_date="2024-01-02",  # Solo 1 giorno
            initial_balance=100000,
            symbols=["EURUSD"],     # Solo 1 simbolo
            timeframe="M1"
        )
        
        the5ers_rules = The5ersRules(
            step1_target=8.0,
            step2_target=5.0,
            scaling_target=10.0,
            max_daily_loss=5.0,
            max_total_loss=10.0,
            min_profitable_days=3
        )
        
        # Esegui backtest
        engine = QuantumBacktestEngine(config, backtest_config, the5ers_rules)
        results = engine.run_backtest()
        
        # Verifica risultati
        logger.info(f"✓ Backtest completato!")
        logger.info(f"  - Saldo iniziale: ${results['initial_balance']:,.2f}")
        logger.info(f"  - Saldo finale: ${results['final_balance']:,.2f}")
        logger.info(f"  - Return: {results['total_return_pct']:.2f}%")
        logger.info(f"  - Trades: {results['total_trades']}")
        logger.info(f"  - Win rate: {results['win_rate']:.1f}%")
        logger.info(f"  - Max drawdown: {results['max_drawdown']:.2f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Errore backtest: {e}")
        return False

def main():
    """Funzione principale di test"""
    logger.info("="*60)
    logger.info("THE5ERS QUANTUM BACKTEST - QUICK TEST")
    logger.info("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Loading Test", test_config_loading),
        ("Synthetic Data Test", test_synthetic_data),
        ("Quantum Engine Test", test_quantum_engine),
        ("Simple Backtest Test", test_simple_backtest)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*40}")
        logger.info(f"RUNNING: {test_name}")
        logger.info(f"{'='*40}")
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {test_name} FAILED")
                
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} FAILED: {e}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED! Sistema pronto per l'uso.")
        logger.info("\nProximi passi:")
        logger.info("1. Esegui: python examples.py")
        logger.info("2. Oppure: python run_optimization.py")
        logger.info("3. Oppure: run_optimization.bat")
    else:
        logger.error("❌ Alcuni test sono falliti. Controllare gli errori sopra.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
