#!/usr/bin/env python3
"""
🚀 LEGACY SYSTEM LAUNCHER - THE5ERS QUANTUM TRADING SYSTEM
Launcher rapido per il sistema monolitico legacy
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🎯 THE5ERS QUANTUM TRADING SYSTEM - LEGACY LAUNCHER")
    print("=" * 60)
    
    # Verifica che siamo nella cartella corretta
    if not os.path.exists("PRO-THE5ERS-QM-PHOENIX-GITCOP.py"):
        print("❌ ERRORE: File principale non trovato!")
        print("   Assicurati di essere nella cartella legacy_system/")
        return False
    
    # Verifica file configurazione (cerca prima in config/, poi nella directory corrente)
    config_paths = [
        "config/config_autonomous_high_stakes_production_ready.json",
        "config/config_autonomous_high_stakes_production_ready.json"
    ]
    
    config_file = None
    for path in config_paths:
        if os.path.exists(path):
            config_file = path
            break
    
    if not config_file:
        print("❌ ERRORE: File configurazione non trovato!")
        print("   Cercato in:")
        for path in config_paths:
            print(f"   - {path}")
        return False
    
    print("✅ File sistema trovati")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"⚙️ Configurazione: {config_file}")
    print()
    
    # Controllo prerequisiti
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 library disponibile")
    except ImportError:
        print("❌ ERRORE: MetaTrader5 non installato")
        print("   Esegui: pip install MetaTrader5")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy disponibile")
    except ImportError:
        print("❌ ERRORE: NumPy non installato")
        print("   Esegui: pip install numpy")
        return False
    
    print()
    print("🚀 Avvio sistema legacy...")
    print("💡 Usa Ctrl+C per fermare il sistema")
    print("📊 Monitor log: logs/log_autonomous_high_stakes_conservative_production_ready.log")
    print("=" * 60)
    print()
    
    # Avvia il sistema
    try:
        subprocess.run([sys.executable, "PRO-THE5ERS-QM-PHOENIX-GITCOP.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Sistema fermato dall'utente")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Errore nell'esecuzione: {e}")
        return False
    except Exception as e:
        print(f"\n💀 Errore inaspettato: {e}")
        return False
    
    print("\n✅ Sistema legacy terminato correttamente")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
