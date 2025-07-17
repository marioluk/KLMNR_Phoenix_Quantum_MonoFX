#!/usr/bin/env python3
# ====================================================================================
# EXTENDED TEST - THE5ERS QUANTUM BACKTEST
# Test esteso per vedere l'algoritmo in azione
# ====================================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import *

def run_extended_test():
    """Test esteso con più giorni e parametri ottimizzati"""
    
    print("\n🚀 AVVIO TEST ESTESO - 1 SETTIMANA")
    print("="*60)
    
    # Configurazione estesa
    config = get_the5ers_config()
    
    # Parametri più aggressivi per vedere trades
    config['quantum_params']['entropy_threshold'] = 0.3  # Più basso = più trades
    config['risk_parameters']['position_cooldown_minutes'] = 15  # Cooldown ridotto
    
    # Test configuration (1 settimana, multi-simbolo)
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-07",  # 1 settimana
        initial_balance=100000,
        symbols=["EURUSD", "GBPUSD", "XAUUSD"],  # 3 simboli
        timeframe="M15"  # 15 minuti per più dati
    )
    
    the5ers_rules = The5ersRules()
    
    print(f"📊 Configurazione Test Esteso:")
    print(f"   - Periodo: {backtest_config.start_date} - {backtest_config.end_date}")
    print(f"   - Balance iniziale: ${backtest_config.initial_balance:,}")
    print(f"   - Simboli: {backtest_config.symbols}")
    print(f"   - Timeframe: {backtest_config.timeframe}")
    print(f"   - Entropy threshold: {config['quantum_params']['entropy_threshold']}")
    print(f"   - Target Step 1: {the5ers_rules.step1_target}%")
    
    # Crea e esegui backtest
    engine = WorkingBacktestEngine(config, backtest_config, the5ers_rules)
    
    print("\n⚡ Esecuzione backtest esteso...")
    results = engine.run_backtest()
    
    # Mostra risultati dettagliati
    print("\n" + "="*60)
    print("📈 RISULTATI TEST ESTESO")
    print("="*60)
    print(f"Balance iniziale:    ${results['initial_balance']:,}")
    print(f"Balance finale:      ${results['final_balance']:,}")
    print(f"Return totale:       ${results['total_return']:,.2f}")
    print(f"Return percentuale:  {results['total_return_pct']:.2f}%")
    print(f"Trades totali:       {results['total_trades']}")
    print(f"Trades vincenti:     {results['winning_trades']}")
    print(f"Trades perdenti:     {results['losing_trades']}")
    print(f"Win rate:            {results['win_rate']:.1f}%")
    print(f"Max drawdown:        {results['max_drawdown']:.2f}%")
    print(f"Giorni profittevoli: {results['profitable_days']}")
    print(f"Sharpe ratio:        {results['sharpe_ratio']:.2f}")
    
    print(f"\n🎯 THE5ERS COMPLIANCE CHECK:")
    compliance = results['the5ers_compliance']
    print(f"Step 1 (8%):         {'✅ PASSED' if compliance['step1_achieved'] else '❌ FAILED'}")
    print(f"Step 2 (5%):         {'✅ PASSED' if compliance['step2_achieved'] else '❌ FAILED'}")
    print(f"Scaling (10%):       {'✅ PASSED' if compliance['scaling_achieved'] else '❌ FAILED'}")
    print(f"Max total loss:      {'✅ OK' if not compliance['total_loss_violated'] else '❌ VIOLATED'}")
    print(f"Daily loss limit:    {'✅ OK' if not compliance['daily_loss_violated'] else '❌ VIOLATED'}")
    print(f"Min profitable days: {'✅ OK' if compliance['min_profitable_days'] else '❌ INSUFFICIENT'}")
    
    # Analisi trades
    if results['total_trades'] > 0:
        print(f"\n📝 ANALISI TRADES:")
        winning_trades = [t for t in results['trades'] if t['pnl'] > 0]
        losing_trades = [t for t in results['trades'] if t['pnl'] <= 0]
        
        if winning_trades:
            avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades)
            max_win = max(t['pnl'] for t in winning_trades)
            print(f"   Avg winning trade: ${avg_win:.2f}")
            print(f"   Max winning trade: ${max_win:.2f}")
        
        if losing_trades:
            avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
            max_loss = min(t['pnl'] for t in losing_trades)
            print(f"   Avg losing trade:  ${avg_loss:.2f}")
            print(f"   Max losing trade:  ${max_loss:.2f}")
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        print(f"   Profit factor:     {profit_factor:.2f}")
        
        # Top 5 trades
        print(f"\n🏆 TOP 5 TRADES:")
        sorted_trades = sorted(results['trades'], key=lambda x: x['pnl'], reverse=True)[:5]
        for i, trade in enumerate(sorted_trades, 1):
            print(f"   {i}. {trade['signal']} {trade['symbol']}: ${trade['pnl']:.2f}")
        
        # Analisi per simbolo
        print(f"\n📊 PERFORMANCE PER SIMBOLO:")
        symbol_stats = {}
        for trade in results['trades']:
            symbol = trade['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'trades': 0, 'pnl': 0, 'wins': 0}
            symbol_stats[symbol]['trades'] += 1
            symbol_stats[symbol]['pnl'] += trade['pnl']
            if trade['pnl'] > 0:
                symbol_stats[symbol]['wins'] += 1
        
        for symbol, stats in symbol_stats.items():
            win_rate = (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0
            print(f"   {symbol}: {stats['trades']} trades, ${stats['pnl']:.2f}, {win_rate:.1f}% win rate")
    
    # Analisi giornaliera
    if results['daily_results']:
        print(f"\n📅 PERFORMANCE GIORNALIERA:")
        for date, pnl in results['daily_results'].items():
            status = "💚" if pnl > 0 else "❌" if pnl < 0 else "⚪"
            print(f"   {date}: {status} ${pnl:.2f}")
    
    return results

def run_parameter_sensitivity():
    """Test di sensibilità dei parametri"""
    
    print("\n🧪 TEST SENSIBILITÀ PARAMETRI")
    print("="*50)
    
    base_config = get_the5ers_config()
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-03",
        initial_balance=100000,
        symbols=["EURUSD"],
        timeframe="M15"
    )
    the5ers_rules = The5ersRules()
    
    # Test diversi entropy threshold
    entropy_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    print("🔬 Testing entropy threshold values...")
    best_return = -float('inf')
    best_entropy = None
    
    for entropy in entropy_values:
        config = base_config.copy()
        config['quantum_params']['entropy_threshold'] = entropy
        
        engine = WorkingBacktestEngine(config, backtest_config, the5ers_rules)
        results = engine.run_backtest()
        
        print(f"   Entropy {entropy:.1f}: {results['total_trades']} trades, {results['total_return_pct']:.2f}% return")
        
        if results['total_return_pct'] > best_return:
            best_return = results['total_return_pct']
            best_entropy = entropy
    
    print(f"\n🏆 Miglior entropy threshold: {best_entropy} ({best_return:.2f}% return)")
    
    return best_entropy

def create_optimization_plan():
    """Crea piano di ottimizzazione"""
    
    print("\n📋 PIANO DI OTTIMIZZAZIONE THE5ERS")
    print("="*50)
    
    plan = {
        'parameters_to_optimize': [
            'entropy_threshold',
            'coherence_threshold', 
            'entanglement_strength',
            'buffer_size',
            'max_risk_per_trade',
            'trailing_stop_pips',
            'take_profit_ratio'
        ],
        'optimization_ranges': {
            'entropy_threshold': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'coherence_threshold': [0.5, 0.6, 0.7, 0.8, 0.9],
            'entanglement_strength': [0.8, 1.0, 1.2, 1.5, 2.0],
            'buffer_size': [20, 30, 50, 70, 100],
            'max_risk_per_trade': [1.0, 1.5, 2.0, 2.5, 3.0],
            'trailing_stop_pips': [10, 15, 20, 25, 30],
            'take_profit_ratio': [1.5, 2.0, 2.5, 3.0]
        },
        'objectives': [
            'total_return_pct',
            'win_rate',
            'profit_factor',
            'max_drawdown',
            'sharpe_ratio'
        ],
        'constraints': {
            'max_drawdown': 8.0,  # Sotto il limite del 10%
            'min_trades': 10,     # Almeno 10 trades per validità statistica
            'the5ers_compliance': True
        }
    }
    
    print("🎯 Parametri da ottimizzare:")
    for param in plan['parameters_to_optimize']:
        values = plan['optimization_ranges'][param]
        print(f"   {param}: {values}")
    
    print(f"\n📊 Obiettivi:")
    for objective in plan['objectives']:
        print(f"   - {objective}")
    
    print(f"\n⚠️  Vincoli:")
    for constraint, value in plan['constraints'].items():
        print(f"   - {constraint}: {value}")
    
    print(f"\n🚀 Strategia raccomandata:")
    print(f"   1. Grid Search su parametri quantum")
    print(f"   2. Genetic Algorithm per ottimizzazione multi-obiettivo")
    print(f"   3. Walk-forward analysis per robustezza")
    print(f"   4. Monte Carlo per analisi rischio")
    
    return plan

if __name__ == "__main__":
    try:
        # Test esteso
        print("FASE 1: TEST ESTESO")
        results = run_extended_test()
        
        # Test sensibilità
        print("\n" + "="*60)
        print("FASE 2: ANALISI SENSIBILITÀ")
        best_entropy = run_parameter_sensitivity()
        
        # Piano ottimizzazione
        print("\n" + "="*60)
        print("FASE 3: PIANO OTTIMIZZAZIONE")
        plan = create_optimization_plan()
        
        # Riepilogo finale
        print("\n" + "="*60)
        print("🎯 RIEPILOGO FINALE")
        print("="*60)
        
        if results['total_trades'] > 0:
            print(f"✅ Sistema funzionante: {results['total_trades']} trades eseguiti")
            print(f"💰 Return test: {results['total_return_pct']:.2f}%")
            print(f"🎲 Win rate: {results['win_rate']:.1f}%")
            print(f"📉 Max drawdown: {results['max_drawdown']:.2f}%")
            
            if results['the5ers_compliance']['step1_achieved']:
                print(f"🏆 TARGET STEP 1 RAGGIUNTO!")
            else:
                print(f"⚠️  Target Step 1 non raggiunto - servono ottimizzazioni")
        else:
            print(f"⚠️  Nessun trade nel test - parametri troppo conservativi")
        
        print(f"\n🔧 Miglior entropy threshold trovato: {best_entropy}")
        print(f"📈 Prossimo step: Ottimizzazione completa parametri")
        
        print(f"\n🚀 COMANDI PER CONTINUARE:")
        print(f"1. Modifica parametri in working_backtest.py")
        print(f"2. Esegui test più lunghi (1 mese)")
        print(f"3. Implementa ottimizzazione automatica")
        print(f"4. Test con dati reali di mercato")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
