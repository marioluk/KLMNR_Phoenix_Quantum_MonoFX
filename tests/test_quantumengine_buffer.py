import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from phoenix_quantum_monofx_program import QuantumEngine

def test_buffer_popolazione():
    config_dict = {
        "symbols": {
            "EURUSD": {}
        },
        "quantum_params": {
            "buffer_size": 10
        }
    }
    engine = QuantumEngine(config_dict)
    symbol = "EURUSD"
    prezzi_test = [1.1000, 1.1005, 1.1002, 1.1008]
    for prezzo in prezzi_test:
        engine.process_tick(symbol, prezzo)
    buffer = engine.get_tick_buffer(symbol)
    assert len(buffer) == len(prezzi_test), f"Il buffer non contiene il numero atteso di tick! ({len(buffer)} invece di {len(prezzi_test)})"
    assert [t['price'] for t in buffer] == prezzi_test, "I prezzi nel buffer non corrispondono ai tick inseriti!"
