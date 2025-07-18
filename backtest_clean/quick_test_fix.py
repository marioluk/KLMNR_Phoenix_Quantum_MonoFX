#!/usr/bin/env python3
"""
Test rapido per verificare il fix del datetime
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_high_stakes_optimizer import AutonomousHighStakesOptimizer

def test_fix():
    print("🧪 TEST FIX DATETIME")
    print("="*25)
    
    try:
        # Inizializza optimizer
        optimizer = AutonomousHighStakesOptimizer()
        print("✅ Optimizer inizializzato")
        
        # Genera config test
        config = optimizer.generate_optimized_config('moderate')
        print("✅ Configurazione generata")
        
        # Test backtest autonomo
        result = optimizer.run_autonomous_backtest(config, test_days=30)
        print("✅ Backtest autonomo eseguito")
        
        print(f"📈 P&L: €{result['daily_avg_pnl']:.2f}/day")
        print(f"🎯 Win Rate: {result['win_rate']:.1f}%")
        print(f"📊 Trades: {result['total_trades']}")
        print(f"⚖️ Periodo: {result['period_type']}")
        
        print("\n🎉 FIX DATETIME CONFERMATO!")
        print("✅ Sistema autonomo funziona correttamente")
        
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fix()
