#!/usr/bin/env python3
"""
Test rapido per verificare i simboli aggiornati
"""

from autonomous_high_stakes_optimizer import AutonomousHighStakesOptimizer

def test_symbols():
    print("🔧 TEST SIMBOLI AGGIORNATI")
    print("="*40)
    
    try:
        opt = AutonomousHighStakesOptimizer()
        
        print(f"✅ Simboli disponibili: {len(opt.available_symbols)}")
        print("\n📋 LISTA SIMBOLI:")
        for i, symbol in enumerate(opt.available_symbols, 1):
            spread = opt.get_symbol_max_spread(symbol)
            sessions = opt.get_symbol_sessions(symbol)
            print(f"   {i:2d}. {symbol:7s} - Spread max: {spread:4.1f} - Sessioni: {', '.join(sessions)}")
        
        print(f"\n🎯 CONFIGURAZIONI POSSIBILI:")
        levels = ['conservative', 'moderate', 'aggressive']
        for level in levels:
            symbols = opt.select_optimal_symbols(level)
            print(f"   {level.upper():12s}: {len(symbols)} simboli -> {', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''}")
        
        print(f"\n✅ Test completato con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    test_symbols()
