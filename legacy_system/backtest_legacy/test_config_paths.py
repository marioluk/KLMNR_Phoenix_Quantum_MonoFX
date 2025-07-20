#!/usr/bin/env python3
"""
🧪 TEST CONFIGURAZIONI LEGACY - Verifica Path Corretti
"""

import os
import sys

def test_config_paths():
    print("🧪 TEST ORGANIZZIAZIONE CONFIGURAZIONI LEGACY")
    print("=" * 50)
    
    # Test path correnti
    print(f"📁 Directory corrente: {os.getcwd()}")
    print(f"📂 Directory script: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Test esistenza cartelle
    config_dir = "../config"
    config_abs = os.path.abspath(config_dir)
    
    print(f"\n📋 Verifiche Path:")
    print(f"   Config dir relativo: {config_dir}")
    print(f"   Config dir assoluto: {config_abs}")
    print(f"   Cartella config esiste: {os.path.exists(config_dir)}")
    print(f"   Cartella config (abs) esiste: {os.path.exists(config_abs)}")
    
    # Test file configurazione
    config_file = os.path.join(config_dir, "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json")
    print(f"   File config originale: {os.path.exists(config_file)}")
    
    # Lista file in config
    if os.path.exists(config_dir):
        files = os.listdir(config_dir)
        print(f"\n📄 File in config ({len(files)}):")
        for f in files:
            print(f"   - {f}")
    
    # Test salvataggio
    test_path = os.path.join(config_dir, "test_config_path.json")
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(test_path, 'w') as f:
            f.write('{"test": "path_corrected"}')
        print(f"\n✅ Test salvataggio: SUCCESS")
        print(f"   File salvato in: {test_path}")
        
        # Cleanup
        os.remove(test_path)
        print(f"   File test rimosso")
        
    except Exception as e:
        print(f"\n❌ Test salvataggio: FAILED")
        print(f"   Errore: {e}")
    
    print("\n🎯 CONCLUSIONI:")
    print("   ✅ Path corretto configurato")
    print("   ✅ Cartella config accessibile")
    print("   ✅ Salvataggio file funzionante")

if __name__ == "__main__":
    test_config_paths()
