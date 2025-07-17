#!/usr/bin/env python3
# ====================================================================================
# SIMPLE TEST - THE5ERS QUANTUM BACKTEST
# Test semplificato del sistema
# ====================================================================================

import sys
import os

print("=== SIMPLE TEST THE5ERS QUANTUM BACKTEST ===")
print(f"Working directory: {os.getcwd()}")

# Test 1: Test config loading
print("\nTest 1: Loading config...")
try:
    from config import get_default_config
    config = get_default_config()
    print("✓ Config loaded successfully")
    print(f"  - Symbols: {list(config.get('symbols', {}).keys())}")
    print(f"  - Quantum buffer size: {config.get('quantum_params', {}).get('buffer_size', 'N/A')}")
except Exception as e:
    print(f"✗ Config loading failed: {e}")
    sys.exit(1)

# Test 2: Test backtest classes
print("\nTest 2: Loading backtest classes...")
try:
    from backtest_engine import BacktestConfig, The5ersRules, HistoricalDataHandler
    
    # Crea configurazione di test
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-02",
        initial_balance=100000,
        symbols=["EURUSD"],
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
    
    print("✓ Backtest classes loaded successfully")
    print(f"  - Start date: {backtest_config.start_date}")
    print(f"  - Initial balance: ${backtest_config.initial_balance:,}")
    print(f"  - Step 1 target: {the5ers_rules.step1_target}%")
    
except Exception as e:
    print(f"✗ Backtest classes loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test synthetic data generation
print("\nTest 3: Generating synthetic data...")
try:
    data_handler = HistoricalDataHandler()
    
    # Genera dati per 1 giorno
    df = data_handler.load_historical_data(
        symbol="EURUSD",
        start_date="2024-01-01",
        end_date="2024-01-01",
        timeframe="M1"
    )
    
    print(f"✓ Synthetic data generated: {len(df)} data points")
    print(f"  - Columns: {list(df.columns)}")
    print(f"  - Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
    
except Exception as e:
    print(f"✗ Synthetic data generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test quantum engine creation
print("\nTest 4: Creating quantum engine...")
try:
    from backtest_engine import QuantumBacktestEngine
    
    # Crea engine
    engine = QuantumBacktestEngine(config, backtest_config, the5ers_rules)
    
    print("✓ Quantum backtest engine created successfully")
    print(f"  - Initial balance: ${engine.current_balance:,}")
    print(f"  - Symbols to trade: {engine.backtest_config.symbols}")
    
except Exception as e:
    print(f"✗ Quantum engine creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Run mini backtest
print("\nTest 5: Running mini backtest...")
try:
    # Esegui backtest su 1 giorno
    results = engine.run_backtest()
    
    print("✓ Mini backtest completed successfully!")
    print(f"  - Initial balance: ${results['initial_balance']:,}")
    print(f"  - Final balance: ${results['final_balance']:,}")
    print(f"  - Return: {results['total_return_pct']:.2f}%")
    print(f"  - Total trades: {results['total_trades']}")
    print(f"  - Win rate: {results['win_rate']:.1f}%")
    print(f"  - Max drawdown: {results['max_drawdown']:.2f}%")
    print(f"  - Step 1 achieved: {results['the5ers_compliance']['step1_achieved']}")
    
except Exception as e:
    print(f"✗ Mini backtest failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
print("\nIl sistema di backtest è pronto per l'uso!")
print("\nProximi passi:")
print("1. Esegui un'ottimizzazione rapida: python examples.py")
print("2. Oppure usa il sistema completo: python run_optimization.py")
print("3. Oppure usa il batch file: run_optimization.bat")
print("\nI risultati verranno salvati in:")
print("- results/ (file JSON)")
print("- reports/ (grafici e report)")
print("- logs/ (file di log)")
