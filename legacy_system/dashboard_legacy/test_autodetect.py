#!/usr/bin/env python3
"""
Test auto-detect configurazione per dashboard legacy
"""

import os
import sys

# Simula il working directory della dashboard
os.chdir(r"c:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system\dashboard_legacy")

print("🧪 TEST AUTO-DETECT CONFIGURAZIONE DASHBOARD LEGACY")
print("=" * 60)

# Test del path
print(f"📁 Working Directory: {os.getcwd()}")

# Test auto-detect config file
config_file = None

# Auto-detect config file (come nel codice dashboard)
if config_file is None:
    # Cerca prima nella cartella config del sistema legacy
    legacy_config = "../config/PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
    if os.path.exists(legacy_config):
        config_file = legacy_config
        print(f"✅ Config trovato: {config_file}")
    else:
        # Fallback alla directory corrente
        config_file = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
        print(f"⚠️  Fallback config: {config_file}")

# Test esistenza file
print(f"📄 Config file: {config_file}")
print(f"🔍 File exists: {os.path.exists(config_file)}")

if os.path.exists(config_file):
    abs_path = os.path.abspath(config_file)
    print(f"📍 Absolute path: {abs_path}")
    
    # Test caricamento JSON
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"✅ JSON caricato correttamente")
        print(f"🔧 Broker: {config.get('broker', 'N/A')}")
        print(f"📊 The5ers config: {config.get('THE5ERS_specific', {}).get('step1_target', 'N/A')}%")
    except Exception as e:
        print(f"❌ Errore caricamento JSON: {e}")

print("=" * 60)
print("✅ Test completato!")
