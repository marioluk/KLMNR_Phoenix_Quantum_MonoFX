#!/usr/bin/env python3
"""Test per verificare la funzione find_autonomous_configs"""

import os
import sys
import glob
from typing import List

def find_autonomous_configs() -> List[str]:
    """
    Trova tutti i file config_autonomous_*.json in tutte le possibili ubicazioni
    Esclude i file già convertiti (_production_ready)
    
    Returns:
        Lista di percorsi assoluti ai file trovati
    """
    
    search_dirs = [
        "configs",                          # backtest_legacy/configs/
        "../config",                        # legacy_system/config/
        ".",                               # backtest_legacy/ (directory corrente)
        "../../config",                     # root/config/ (se esistesse)
    ]
    
    all_files = []
    
    print("🔍 Ricerca file config_autonomous_*.json in:")
    
    for search_dir in search_dirs:
        print(f"   📁 {search_dir}:", end=" ")
        if os.path.exists(search_dir):
            pattern = os.path.join(search_dir, "config_autonomous_*.json")
            found_files = glob.glob(pattern)
            
            # Filtra solo i file non convertiti (esclude _production_ready)
            filtered_files = []
            for file_path in found_files:
                if "_production_ready" not in os.path.basename(file_path):
                    abs_path = os.path.abspath(file_path)
                    if abs_path not in [os.path.abspath(f) for f in all_files]:
                        all_files.append(file_path)
                        filtered_files.append(file_path)
            
            if filtered_files:
                print(f"✅ {len(filtered_files)} file trovati (su {len(found_files)} totali)")
                for file_path in filtered_files:
                    print(f"      • {os.path.relpath(file_path)}")
            else:
                total_found = len(found_files)
                if total_found > 0:
                    print(f"⚠️ {total_found} file trovati ma tutti già convertiti")
                else:
                    print("❌ nessun file")
        else:
            print("❌ directory non esiste")
    
    print(f"\n📊 TOTALE: {len(all_files)} file autonomi non convertiti")
    return sorted(all_files)

if __name__ == "__main__":
    print("🎯 TEST RICERCA FILE AUTONOMI")
    print("="*40)
    print(f"📂 Directory corrente: {os.getcwd()}")
    print()
    
    files = find_autonomous_configs()
    
    if files:
        print("\n📋 FILE TROVATI:")
        for i, file_path in enumerate(files, 1):
            print(f"{i}. {os.path.relpath(file_path)}")
    else:
        print("\n❌ Nessun file config_autonomous_*.json trovato")
