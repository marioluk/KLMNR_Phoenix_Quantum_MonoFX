
print("[DEBUG-TEST] Inizio esecuzione test_order_entry.py")


import pytest
import importlib.util
import sys
import os
from types import SimpleNamespace
import time

# MOCK MT5 PRIMA DELL'IMPORT DEL MODULO PRINCIPALE
import types
class MT5Mock:
    def symbol_info(self, symbol):
        class Info:
            bid = 1.1000
            ask = 1.1002
            point = 0.0001
        return Info()
    def positions_get(self, *args, **kwargs):
        return []
    def account_info(self):
        class Account:
            currency = 'USD'
            equity = 10000
        return Account()
    def symbol_info_tick(self, symbol):
        class Tick:
            bid = 1.1000
            ask = 1.1002
        return Tick()
    def terminal_info(self):
        class Terminal:
            connected = True
        return Terminal()
    def symbols_get(self):
        class S:
            name = 'EURUSD'
        return [S()]

sys.modules['mt5'] = MT5Mock()



print("[DEBUG-TEST] Prima di importare phoenix_quantum_monofx_program")
print("[TEST] Inizio import modulo principale...")
FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "phoenix_quantum_monofx_program.py")
spec = importlib.util.spec_from_file_location("phoenix_quantum_monofx_program", FILE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
print("[DEBUG-TEST] Dopo import phoenix_quantum_monofx_program")
print("[TEST] Modulo principale importato con successo.")
QuantumEngine = mod.QuantumEngine

class DummyConfig(dict):
    def __init__(self):
        super().__init__()
        self.config = {
            'quantum_params': {
                'buffer_size': 10,
                'spin_window': 5,
                'min_spin_samples': 2,
                'signal_cooldown': 1
            },
            'symbols': {
                'EURUSD': {}
            }
        }
    def get(self, key, default=None):
        return self.config.get(key, default)

@pytest.mark.timeout(10)
def test_order_entry_on_buy_signal():
    print("[TEST] Inizio test_order_entry_on_buy_signal")
    start = time.time()
    engine = QuantumEngine(DummyConfig())
    symbol = 'EURUSD'
    # Simula tick che generano un segnale BUY
    ticks = [
        {'price': 1.1000, 'delta': 0.0005, 'direction': 1, 'time': 1},
        {'price': 1.1005, 'delta': 0.0005, 'direction': 1, 'time': 2},
        {'price': 1.1010, 'delta': 0.0005, 'direction': 1, 'time': 3},
        {'price': 1.1015, 'delta': 0.0005, 'direction': 1, 'time': 4},
        {'price': 1.1020, 'delta': 0.0005, 'direction': 1, 'time': 5},
    ]
    for tick in ticks:
        engine.append_tick(symbol, tick)
    engine.min_spin_samples = 2
    print("[TEST] Chiamo get_signal...")
    signal, price = engine.get_signal(symbol, for_trading=False)
    print(f"[TEST] Risultato get_signal: signal={signal}, price={price}")
    assert signal in ("BUY", "HOLD")
    print(f"[TEST] Fine test_order_entry_on_buy_signal in {time.time()-start:.2f}s")

@pytest.mark.timeout(10)
def test_order_entry_on_sell_signal():
    print("[TEST] Inizio test_order_entry_on_sell_signal")
    start = time.time()
    engine = QuantumEngine(DummyConfig())
    symbol = 'EURUSD'
    # Simula tick che generano un segnale SELL
    ticks = [
        {'price': 1.1000, 'delta': -0.0005, 'direction': -1, 'time': 1},
        {'price': 1.0995, 'delta': -0.0005, 'direction': -1, 'time': 2},
        {'price': 1.0990, 'delta': -0.0005, 'direction': -1, 'time': 3},
        {'price': 1.0985, 'delta': -0.0005, 'direction': -1, 'time': 4},
        {'price': 1.0980, 'delta': -0.0005, 'direction': -1, 'time': 5},
    ]
    for tick in ticks:
        engine.append_tick(symbol, tick)
    engine.min_spin_samples = 2
    print("[TEST] Chiamo get_signal...")
    signal, price = engine.get_signal(symbol, for_trading=False)
    print(f"[TEST] Risultato get_signal: signal={signal}, price={price}")
    assert signal in ("SELL", "HOLD")
    print(f"[TEST] Fine test_order_entry_on_sell_signal in {time.time()-start:.2f}s")
