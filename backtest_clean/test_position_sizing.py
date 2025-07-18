#!/usr/bin/env python3
"""
Test rapido per l'analisi position sizing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from the5ers_integrated_launcher_complete import The5ersIntegratedLauncher

def test_position_sizing():
    print("🧪 TEST POSITION SIZING ANALYSIS")
    print("="*35)
    
    try:
        # Inizializza launcher
        launcher = The5ersIntegratedLauncher()
        print("✅ Launcher inizializzato")
        
        # Verifica che ci siano configurazioni
        import glob
        config_files = glob.glob(os.path.join(launcher.base_dir, "config_autonomous_high_stakes_*.json"))
        
        if not config_files:
            print("⚠️ Nessuna configurazione trovata - genero una di test...")
            config = launcher.autonomous_optimizer.generate_optimized_config('moderate')
            filepath = launcher.autonomous_optimizer.save_config(config, 'moderate')
            print(f"✅ Configurazione test creata: {os.path.basename(filepath)}")
        
        print(f"📊 Configurazioni disponibili: {len(config_files)}")
        
        # Test position sizing analysis
        print("\n🔄 Testando analisi position sizing...")
        result = launcher.position_sizing_analysis()
        
        print("✅ Position sizing analysis completata!")
        print(f"📈 Configurazioni analizzate: {len(result) if result else 0}")
        
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_position_sizing()
