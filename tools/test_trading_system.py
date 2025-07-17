#!/usr/bin/env python3
"""
Test script per verificare il funzionamento del sistema di trading
"""

import sys
import os
import json
import time
from datetime import datetime

# Aggiungi il percorso del modulo principale
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from PRO-THE5ERS-QM-PHOENIX-GITCOP import QuantumTradingSystem, ConfigManager, logger
    import MetaTrader5 as mt5
except ImportError as e:
    print(f"Errore importazione: {e}")
    sys.exit(1)

def test_system_initialization():
    """Test inizializzazione sistema"""
    print("=== Test Inizializzazione Sistema ===")
    
    try:
        # Test 1: Caricamento configurazione
        config_file = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
        if not os.path.exists(config_file):
            print(f"❌ File configurazione non trovato: {config_file}")
            return False
            
        config_manager = ConfigManager(config_file)
        print(f"✅ Configurazione caricata: {len(config_manager.symbols)} simboli")
        
        # Test 2: Inizializzazione MT5
        if not mt5.initialize():
            print("❌ Impossibile inizializzare MT5")
            return False
        print("✅ MT5 inizializzato")
        
        # Test 3: Verifica simboli
        for symbol in config_manager.symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                print(f"✅ Simbolo {symbol}: attivo")
            else:
                print(f"❌ Simbolo {symbol}: non disponibile")
                
        # Test 4: Inizializzazione sistema completo
        system = QuantumTradingSystem(config_file)
        print("✅ Sistema inizializzato correttamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        return False
    finally:
        mt5.shutdown()

def test_signal_generation():
    """Test generazione segnali"""
    print("\n=== Test Generazione Segnali ===")
    
    try:
        config_file = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
        system = QuantumTradingSystem(config_file)
        
        # Simula alcuni tick per riempire il buffer
        for symbol in system.config_manager.symbols[:1]:  # Solo il primo simbolo
            print(f"\nTest per {symbol}:")
            
            # Verifica buffer
            buffer_size = len(system.engine.tick_buffer.get(symbol, []))
            min_samples = system.engine.min_spin_samples
            print(f"Buffer: {buffer_size}/{min_samples}")
            
            # Simula tick se buffer vuoto
            if buffer_size < min_samples:
                print("Simulazione tick per riempire buffer...")
                base_price = 1.1000 if symbol.startswith('EUR') else 2000.0
                
                for i in range(min_samples + 10):
                    price = base_price + (i * 0.0001)
                    system.engine.process_tick(symbol, price)
                    
                print(f"Buffer riempito: {len(system.engine.tick_buffer[symbol])}")
            
            # Test generazione segnale
            signal, price = system.engine.get_signal(symbol)
            print(f"Segnale generato: {signal} a prezzo {price}")
            
            # Test controlli trading
            can_trade = system.engine.can_trade(symbol)
            print(f"Può tradare: {can_trade}")
            
            if can_trade:
                # Test calcolo dimensione
                position_size = system.risk_manager.calculate_position_size(
                    symbol, price, signal
                )
                print(f"Dimensione posizione calcolata: {position_size}")
                
        return True
        
    except Exception as e:
        print(f"❌ Errore test segnali: {e}")
        return False
    finally:
        system.stop()

def test_debug_status():
    """Test debug status"""
    print("\n=== Test Debug Status ===")
    
    try:
        config_file = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
        system = QuantumTradingSystem(config_file)
        
        # Debug status per ogni simbolo
        for symbol in system.config_manager.symbols:
            system.debug_trade_status(symbol)
            print()  # Spazio tra simboli
            
        return True
        
    except Exception as e:
        print(f"❌ Errore debug status: {e}")
        return False
    finally:
        system.stop()

def run_all_tests():
    """Esegue tutti i test"""
    print("🚀 Avvio test sistema di trading")
    print("=" * 50)
    
    tests = [
        test_system_initialization,
        test_signal_generation,
        test_debug_status
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            time.sleep(1)  # Pausa tra test
        except Exception as e:
            print(f"❌ Test fallito: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Risultati Test:")
    print(f"Successi: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ Tutti i test superati!")
        return True
    else:
        print("❌ Alcuni test falliti")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
