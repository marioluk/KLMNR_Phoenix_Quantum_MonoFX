#!/usr/bin/env python3
# ====================================================================================
# REAL SYSTEM TEST - THE5ERS QUANTUM BACKTEST
# Test con l'algoritmo quantum reale
# ====================================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== REAL SYSTEM TEST - THE5ERS QUANTUM BACKTEST ===")

# Aggiungi il path principale
main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if main_path not in sys.path:
    sys.path.append(main_path)

print(f"Main path: {main_path}")
print(f"Current path: {os.getcwd()}")

# Test 1: Verifica file esistenti
print("\nTest 1: Checking required files...")
required_files = [
    "PRO-THE5ERS-QM-PHOENIX-GITCOP.py",
    "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
]

for file in required_files:
    file_path = os.path.join(main_path, file)
    if os.path.exists(file_path):
        print(f"✓ Found: {file}")
    else:
        print(f"✗ Missing: {file}")

# Test 2: Caricare il config dalla directory backtest
print("\nTest 2: Loading backtest config...")
try:
    from config import get_default_config
    config = get_default_config()
    print("✓ Backtest config loaded successfully")
    print(f"  - Symbols: {list(config.get('symbols', {}).keys())}")
    print(f"  - Quantum buffer size: {config.get('quantum_params', {}).get('buffer_size', 'N/A')}")
except Exception as e:
    print(f"✗ Backtest config loading failed: {e}")
    sys.exit(1)

# Test 3: Provare a caricare il backtest engine
print("\nTest 3: Loading backtest engine...")
try:
    from backtest_engine import QuantumBacktestEngine, BacktestConfig, The5ersRules
    print("✓ Backtest engine loaded successfully")
except Exception as e:
    print(f"✗ Backtest engine loading failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Configurazione di un test veloce
print("\nTest 4: Setting up quick test configuration...")
try:
    # Configurazione test minima
    test_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-01",  # Solo 1 giorno
        initial_balance=100000,
        symbols=["EURUSD"],
        timeframe="M5"  # 5 minuti per essere più veloce
    )
    
    the5ers_rules = The5ersRules(
        step1_target=8.0,
        step2_target=5.0,
        scaling_target=10.0,
        max_daily_loss=5.0,
        max_total_loss=10.0,
        min_profitable_days=3
    )
    
    print("✓ Test configuration created")
    print(f"  - Test period: {test_config.start_date}")
    print(f"  - Balance: ${test_config.initial_balance:,}")
    print(f"  - Symbols: {test_config.symbols}")
    
except Exception as e:
    print(f"✗ Test configuration failed: {e}")
    sys.exit(1)

# Test 5: Provare a creare il backtest engine
print("\nTest 5: Creating backtest engine...")
try:
    # Prova a creare l'engine quantum con fallback al mock
    try:
        engine = QuantumBacktestEngine(config, test_config, the5ers_rules)
        engine_type = "Real Quantum Engine"
    except Exception as e:
        print(f"  Warning: Real engine failed ({e}), using mock...")
        # Usa il mock engine dal test precedente
        from standalone_test import MockQuantumBacktestEngine
        engine = MockQuantumBacktestEngine(config, test_config, the5ers_rules)
        engine_type = "Mock Engine"
    
    print(f"✓ Backtest engine created: {engine_type}")
    
except Exception as e:
    print(f"✗ Engine creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Eseguire un backtest veloce
print("\nTest 6: Running quick backtest...")
try:
    results = engine.run_backtest()
    
    print("✓ Backtest completed successfully!")
    print(f"  - Engine type: {engine_type}")
    print(f"  - Initial balance: ${results['initial_balance']:,}")
    print(f"  - Final balance: ${results['final_balance']:,}")
    print(f"  - Total return: {results['total_return_pct']:.2f}%")
    print(f"  - Total trades: {results['total_trades']}")
    print(f"  - Win rate: {results['win_rate']:.1f}%")
    print(f"  - Max drawdown: {results['max_drawdown']:.2f}%")
    
    # The5ers compliance
    compliance = results.get('the5ers_compliance', {})
    print(f"  - Step 1 (8%): {'✓' if compliance.get('step1_achieved') else '✗'}")
    print(f"  - Step 2 (5%): {'✓' if compliance.get('step2_achieved') else '✗'}")
    print(f"  - Scaling (10%): {'✓' if compliance.get('scaling_achieved') else '✗'}")
    print(f"  - Max loss violated: {'✗' if compliance.get('total_loss_violated') else '✓'}")
    
except Exception as e:
    print(f"✗ Backtest execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("🎉 REAL SYSTEM TEST COMPLETED!")
print("="*60)

if engine_type == "Real Quantum Engine":
    print("\n✅ IL SISTEMA QUANTUM REALE FUNZIONA!")
    print("Puoi procedere con l'ottimizzazione completa:")
    print("1. python examples.py - per test interattivi")
    print("2. python run_optimization.py - per ottimizzazione parametri")
else:
    print("\n⚠️  SISTEMA IN MODALITÀ MOCK")
    print("Per usare l'algoritmo quantum reale:")
    print("1. Verifica che PRO-THE5ERS-QM-PHOENIX-GITCOP.py sia accessibile")
    print("2. Verifica che il file di configurazione JSON esista")
    print("3. Risolvi eventuali problemi di import")

print(f"\n📊 Risultati del test:")
print(f"Return: {results['total_return_pct']:.2f}% (Target Step 1: 8%)")
print(f"Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.1f}%")
print(f"Max Drawdown: {results['max_drawdown']:.2f}% (Limite: 10%)")
