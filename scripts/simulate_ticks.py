"""
Script di simulazione tick per testare QuantumEngine e la generazione dei segnali.
Popola il buffer tick e stampa il segnale generato.
"""
import sys
import os
import time
import random

# Assicurati che il path includa la root del progetto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from phoenix_quantum_monofx_program import QuantumEngine, load_config, auto_correct_symbols

# Carica la configurazione come nel main

config = auto_correct_symbols(load_config())
if hasattr(config, '__dict__'):
    config = config.__dict__
engine = QuantumEngine(config)

symbol = "EURUSD"  # Puoi cambiare il simbolo per test

# Simula 50 tick con variazione casuale
base_price = 1.1000
for i in range(50):
    price = base_price + random.uniform(-0.001, 0.001)
    engine.process_tick(symbol, price)
    time.sleep(0.01)  # Simula arrivo tick

signal, last_price = engine.get_signal(symbol)
print(f"Segnale generato per {symbol}: {signal} @ {last_price}")
