#!/usr/bin/env python3
"""
Test per la funzionalità di analisi simboli e spread
"""

import os
import sys
import json
import glob

def simple_test():
    """Test semplificato per verificare i file"""
    
    print("🧪 TEST SEMPLIFICATO")
    print("="*25)
    print()
    
    # Directory corrente
    base_dir = os.getcwd()
    print(f"📁 Directory: {base_dir}")
    
    # Cerca configurazioni
    config_files = glob.glob("config_autonomous_high_stakes_*.json")
    configs_dir = glob.glob("configs/*production_ready*.json")
    
    all_configs = config_files + configs_dir
    
    print(f"📊 Configurazioni trovate: {len(all_configs)}")
    
    for config_file in all_configs[:3]:  # Solo primi 3 per test
        print(f"   📄 {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            symbols = config.get('symbols', {})
            print(f"      🎯 Simboli: {len(symbols)}")
            
            for symbol in list(symbols.keys())[:2]:  # Solo primi 2 simboli
                symbol_config = symbols[symbol]
                risk_mgmt = symbol_config.get('risk_management', {})
                contract_size = risk_mgmt.get('contract_size', 0)
                print(f"         💰 {symbol}: Size={contract_size}")
            
        except Exception as e:
            print(f"      ❌ Errore: {e}")
        
        print()

if __name__ == "__main__":
    simple_test()
