#!/usr/bin/env python3
"""Test rapido per verificare i risultati differenziati"""

import os
import glob
from autonomous_high_stakes_optimizer import AutonomousHighStakesOptimizer

def test_differentiated_results():
    print("🧪 TEST VALIDAZIONE DIFFERENZIATA")
    print("="*50)
    
    optimizer = AutonomousHighStakesOptimizer()
    config_files = glob.glob('config_autonomous_high_stakes_*.json')
    
    if not config_files:
        print("❌ Nessuna configurazione trovata!")
        return
    
    print(f"📁 Trovate {len(config_files)} configurazioni")
    print()
    
    for config_file in config_files:
        results = optimizer.run_validation_test(config_file, 7)
        print(f"📄 {os.path.basename(config_file)}:")
        print(f"   📊 Livello: {results.get('aggressiveness_level', 'unknown')}")
        print(f"   💰 P&L: €{results['daily_avg_pnl']:.2f}/day")
        print(f"   🎯 Win Rate: {results['win_rate']:.1f}%")
        print(f"   📈 Trades: {results['total_trades']}")
        print(f"   ⚖️ Risk: {results['risk_percent_used']*100:.1f}%")
        print()

if __name__ == "__main__":
    test_differentiated_results()
