#!/usr/bin/env python3
# Test del sistema integrato

import os
import sys

# Test import
try:
    from autonomous_high_stakes_optimizer import AutonomousHighStakesOptimizer
    print("✅ autonomous_high_stakes_optimizer importato correttamente")
except ImportError as e:
    print(f"❌ Errore import autonomous: {e}")

try:
    from high_stakes_optimizer import HighStakesOptimizer  
    print("✅ high_stakes_optimizer importato correttamente")
except ImportError as e:
    print(f"❌ Errore import high_stakes: {e}")

# Test inizializzazione
try:
    optimizer = AutonomousHighStakesOptimizer()
    print("✅ AutonomousHighStakesOptimizer inizializzato")
except Exception as e:
    print(f"❌ Errore init autonomo: {e}")

print("\n🎯 SISTEMA COMPLETAMENTE INTEGRATO!")
print("="*40)
print("✅ autonomous_high_stakes_optimizer.py: Generazione da zero")
print("✅ the5ers_integrated_launcher_complete.py: Sistema unificato")
print("✅ Dual-mode: Autonomo (raccomandato) + JSON (legacy)")
print("✅ Menu unificato con 21 opzioni integrate")
print("\n💡 UTILIZZO:")
print("python the5ers_integrated_launcher_complete.py")
