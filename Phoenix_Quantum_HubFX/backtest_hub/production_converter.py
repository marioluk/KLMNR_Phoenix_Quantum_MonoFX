#!/usr/bin/env python3
"""
PRODUCTION CONVERTER - Sistema di Gestione Configurazioni Ottimizzate
Gestisce la conversione dei file ottimizzati in configurazione di produzione
Logica CORRETTA:
1. L'ottimizzatore genera: config_autonomous_high_stakes_[STRATEGY]_production_ready.json
2. Il sistema seleziona il migliore e lo copia in: config_autonomous_high_stakes_conservative_production_ready.json
3. Il software di trading legge: config_autonomous_high_stakes_conservative_production_ready.json
"""

import os
import shutil
from datetime import datetime

def deploy_ready_config():
    """
    Copia/aggiorna il file di produzione già pronto e crea backup se necessario.
    """
    print("🎯 DEPLOY CONFIGURAZIONE PRONTA")
    print("="*50)
    # Mostra i file disponibili
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.abspath(os.path.join(script_dir, "..", "config"))
    files = [f for f in os.listdir(config_dir) if f.startswith("config_autonomous_high_stakes_") and f.endswith("_production_ready.json")]
    if not files:
        print("❌ Nessun file di configurazione disponibile.")
        return False
    print("\nConfigurazioni disponibili:")
    for idx, fname in enumerate(files, 1):
        print(f"  {idx}. {fname}")
    print("\nNon viene più effettuata la copia/rename: usa direttamente il file desiderato con --config nel main script.")
    return True

if __name__ == "__main__":
    deploy_ready_config()
