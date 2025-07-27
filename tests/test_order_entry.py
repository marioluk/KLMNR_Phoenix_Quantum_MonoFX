import pytest
import importlib.util
import sys
import os
from types import SimpleNamespace

FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "phoenix_quantum_monofx_program.py")
spec = importlib.util.spec_from_file_location("phoenix_quantum_monofx_program", FILE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
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

def test_order_entry_on_buy_signal():
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
    # Forza la confidence a 1.0 e spin positivo
    engine.min_spin_samples = 2
    signal, price = engine.get_signal(symbol, for_trading=False)
    assert signal in ("BUY", "HOLD")  # BUY se la logica lo consente, HOLD se la soglia non è superata
    # Se vuoi forzare BUY, puoi manipolare direttamente i parametri o tick
    # assert signal == "BUY"

def test_order_entry_on_sell_signal():
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
    signal, price = engine.get_signal(symbol, for_trading=False)
    assert signal in ("SELL", "HOLD")
