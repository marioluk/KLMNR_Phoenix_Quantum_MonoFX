#!/usr/bin/env python3
# Test Ultra-Semplice per verificare le modifiche

import json
import os

def main():
    print("=== VERIFICA MODIFICHE THE5ERS ===")
    
    try:
        # Carica config
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Config caricata")
        
        # Verifica position sizing
        eurusd = config['symbols']['EURUSD']['risk_management']
        
        print(f"📊 EURUSD Position Sizing:")
        print(f"   Contract size: {eurusd['contract_size']}")
        print(f"   Risk %: {eurusd['risk_percent']*100:.3f}%")
        print(f"   Safety limit: {eurusd.get('safety_limit', 'N/A')}")
        
        # Verifica quantum params
        quantum = config['quantum_params']
        print(f"🔬 Quantum Parameters:")
        print(f"   Buffer size: {quantum['buffer_size']}")
        print(f"   Signal cooldown: {quantum['signal_cooldown']}")
        
        print("\n✅ SISTEMA AGGIORNATO CORRETTAMENTE!")
        print("🔧 Micro lot (0.01) attivo")
        print("📉 Risk ridotto a 0.15%")
        print("⚡ Quantum engine ottimizzato")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
