#!/usr/bin/env python3
"""Test per production_converter dalla root"""

import os
import sys

# Aggiungi il percorso per import
sys.path.append('legacy_system/backtest_legacy')

from production_converter import find_autonomous_configs

print('🔍 TEST RICERCA DA ROOT:')
print(f'📂 Directory corrente: {os.getcwd()}')
print()

files = find_autonomous_configs()
print(f'\n📊 RISULTATO FINALE: {len(files)} file trovati')

if files:
    print('\n📋 File trovati:')
    for file_path in files:
        print(f'   • {file_path}')
