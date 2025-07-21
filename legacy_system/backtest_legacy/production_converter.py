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
        print("❌ Nessun file di configurazione disponibile per il deploy.")
        return False
    print("\nConfigurazioni disponibili per il deploy:")
    for idx, fname in enumerate(files, 1):
        print(f"  {idx}. {fname}")
    choice = input(f"\nScegli il numero della configurazione da mandare in produzione (1-{len(files)}): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
        print("❌ Scelta non valida.")
        return False
    src_file = os.path.join(config_dir, files[int(choice)-1])
    dst_file = os.path.join(config_dir, "config_autonomous_high_stakes_production_ready.json")
    # ...existing code...
    # Backup se esiste già
    if os.path.exists(dst_file):
        backup_dir = os.path.join(config_dir, "backup")
        os.makedirs(backup_dir, exist_ok=True)
        backup_filename = f"config_autonomous_high_stakes_production_ready.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(backup_dir, backup_filename)
        shutil.copy2(dst_file, backup_path)
        print(f"💾 Backup creato: backup/{backup_filename}")
    # Copia/aggiorna file
    shutil.copy2(src_file, dst_file)
    print(f"✅ Deploy completato!")
    print(f"📁 File principale aggiornato: config_autonomous_high_stakes_production_ready.json")
    return True

if __name__ == "__main__":
    deploy_ready_config()
