import sys
import os

print("=== DEBUG INFO ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test 1: Check if parent directory exists
parent_dir = os.path.dirname(os.getcwd())
print(f"Parent directory: {parent_dir}")
print(f"Parent directory exists: {os.path.exists(parent_dir)}")

# Test 2: Check if main file exists
main_file = os.path.join(parent_dir, 'PRO-THE5ERS-QM-PHOENIX-GITCOP.py')
print(f"Main file path: {main_file}")
print(f"Main file exists: {os.path.exists(main_file)}")

# Test 3: Try to import using importlib
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("quantum_module", main_file)
    quantum_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quantum_module)
    print("✓ Main file loaded successfully")
    
    # Check available classes
    print(f"Available classes: {[name for name in dir(quantum_module) if not name.startswith('_')]}")
    
except Exception as e:
    print(f"✗ Error loading main file: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test config import
try:
    from config import get_default_config
    config = get_default_config()
    print("✓ Config loaded successfully")
    print(f"Config keys: {list(config.keys())}")
except Exception as e:
    print(f"✗ Error loading config: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test backtest_engine import
try:
    from backtest_engine import QuantumBacktestEngine
    print("✓ Backtest engine loaded successfully")
except Exception as e:
    print(f"✗ Error loading backtest engine: {e}")
    import traceback
    traceback.print_exc()
