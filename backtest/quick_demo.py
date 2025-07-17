#!/usr/bin/env python3
# ====================================================================================
# QUICK DEMO - THE5ERS QUANTUM BACKTEST
# Demo veloce per mostrare il sistema funzionante
# ====================================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import *

def run_quick_demo():
    """Demo veloce con dati limitati"""
    
    print("\n⚡ DEMO VELOCE SISTEMA QUANTUM TRADING")
    print("="*50)
    
    # Configurazione super aggressiva ma veloce
    config = get_the5ers_config()
    config['quantum_params']['entropy_threshold'] = 0.01  # ULTRA aggressivo
    config['quantum_params']['buffer_size'] = 10         # Buffer minimo
    config['risk_parameters']['position_cooldown_minutes'] = 1  # Quasi nessun cooldown
    
    # Test MOLTO limitato per velocità
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-02",  # Solo 2 giorni
        initial_balance=100000,
        symbols=["EURUSD"],     # Solo 1 simbolo
        timeframe="M5"          # 5 minuti
    )
    
    the5ers_rules = The5ersRules()
    
    print(f"📊 Configurazione Demo:")
    print(f"   - Periodo: {backtest_config.start_date} - {backtest_config.end_date}")
    print(f"   - Simbolo: {backtest_config.symbols[0]}")
    print(f"   - Entropy threshold: {config['quantum_params']['entropy_threshold']} (ULTRA-AGGRESSIVO)")
    
    # Esegui demo
    engine = WorkingBacktestEngine(config, backtest_config, the5ers_rules)
    
    print("\n⚡ Esecuzione demo...")
    results = engine.run_backtest()
    
    # Risultati
    print("\n" + "="*50)
    print("📈 RISULTATI DEMO")
    print("="*50)
    print(f"Balance: ${results['initial_balance']:,} → ${results['final_balance']:,}")
    print(f"Return: {results['total_return_pct']:.2f}%")
    print(f"Trades: {results['total_trades']}")
    print(f"Win rate: {results['win_rate']:.1f}%")
    print(f"Max drawdown: {results['max_drawdown']:.2f}%")
    
    if results['total_trades'] > 0:
        print(f"\n✅ SISTEMA FUNZIONANTE!")
        print(f"🎯 {results['total_trades']} trades eseguiti")
        
        # Mostra alcuni trades
        print(f"\n📝 Esempi di trades:")
        for i, trade in enumerate(results['trades'][:3], 1):
            status = "💚" if trade['pnl'] > 0 else "❌"
            print(f"   {i}. {status} {trade['signal']} {trade['symbol']}: ${trade['pnl']:.2f}")
        
        # The5ers status
        if results['the5ers_compliance']['step1_achieved']:
            print(f"\n🏆 TARGET STEP 1 RAGGIUNTO IN DEMO!")
        elif results['total_return_pct'] > 0:
            print(f"\n📈 Demo profittevole - sistema promettente!")
    
    else:
        print(f"\n⚠️  Nessun trade in demo - parametri ancora troppo conservativi")
    
    return results

if __name__ == "__main__":
    try:
        results = run_quick_demo()
        
        print("\n" + "="*50)
        print("🎊 CONCLUSIONI DEMO")
        print("="*50)
        
        if results['total_trades'] > 0:
            print(f"✅ Il sistema di backtest quantum è FUNZIONANTE!")
            print(f"📊 Eseguiti {results['total_trades']} trades in demo")
            print(f"💰 Return demo: {results['total_return_pct']:.2f}%")
            
            print(f"\n🚀 PROSSIMI PASSI:")
            print(f"1. ⏰ Estendi periodo di test (1 settimana+)")
            print(f"2. 💱 Aggiungi più simboli (GBPUSD, XAUUSD, etc.)")
            print(f"3. 🎛️  Ottimizza parametri per target The5ers")
            print(f"4. 📊 Implementa ottimizzazione automatica")
            print(f"5. 📈 Test con dati di mercato reali")
            
            print(f"\n🎯 IL SISTEMA È PRONTO PER L'OTTIMIZZAZIONE!")
            
        else:
            print(f"⚠️  Sistema necessita ulteriore tuning")
            print(f"💡 Prova parametri ancora più aggressivi")
        
        print(f"\n📋 Il backtest engine per The5ers Challenge è operativo!")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
