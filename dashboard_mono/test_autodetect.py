#!/usr/bin/env python3
"""
Test auto-detect configurazione per dashboard legacy
"""

import os
import sys

# Simula il working directory della dashboard
os.chdir(r"c:\KLMNR_Projects\KLMNR_Phoenix_Quantum_MonoFX\dashboard_mono")

print("🧪 TEST AUTO-DETECT CONFIGURAZIONE DASHBOARD LEGACY")
print("=" * 60)

# Test del path
print(f"📁 Working Directory: {os.getcwd()}")

# Test auto-detect config file
config_file = None

if config_file is None:
    # Path reale usato dalla dashboard (config nella root progetto)
    config_path = os.path.normpath(os.path.join(os.getcwd(), '..', '..', 'config', 'config_autonomous_challenge_production_ready.json'))
    if os.path.exists(config_path):
        config_file = config_path
        print(f"✅ Config trovato: {config_file}")
    else:
        print(f"❌ Config non trovata: {config_path}")
        config_file = None


if config_file and os.path.exists(config_file):
    abs_path = os.path.abspath(config_file)
    print(f"📍 Absolute path: {abs_path}")
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"✅ JSON caricato correttamente")
        print(f"🔧 Broker: {config.get('broker', 'N/A')}")
        print(f"📊 The5ers config: {config.get('THE5ERS_specific', {}).get('step1_target', 'N/A')}%")
    except Exception as e:
        print(f"❌ Errore caricamento JSON: {e}")
else:
    print(f"❌ Config file non trovato o non accessibile.")

print("=" * 60)
print("✅ Test completato!")
