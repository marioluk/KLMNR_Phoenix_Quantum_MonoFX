
import importlib.util
import sys
import os
import pytest

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

def test_entropy_basic():
    engine = QuantumEngine(DummyConfig())
    # Entropia di una sequenza costante deve essere 0
    deltas = (0.0, 0.0, 0.0, 0.0)
    entropy = engine.calculate_entropy(deltas)
    assert entropy == pytest.approx(0.0, abs=1e-6)

    # Entropia di una sequenza alternata
    deltas = (1.0, -1.0, 1.0, -1.0)
    entropy = engine.calculate_entropy(deltas)
    assert 0.9 < entropy <= 1.0
