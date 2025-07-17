#!/usr/bin/env python3
# ====================================================================================
# AGGRESSIVE TEST - THE5ERS QUANTUM BACKTEST
# Test con parametri aggressivi per dimostrare il sistema
# ====================================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import *

def run_aggressive_test():
    """Test aggressivo per dimostrare il sistema in azione"""
    
    print("\n🔥 AVVIO TEST AGGRESSIVO - DIMOSTRAZIONE SISTEMA")
    print("="*70)
    
    # Configurazione MOLTO aggressiva per garantire trades
    config = get_the5ers_config()
    
    # Parametri ultra-aggressivi
    config['quantum_params']['entropy_threshold'] = 0.05  # MOLTO basso
    config['quantum_params']['coherence_threshold'] = 0.3
    config['quantum_params']['buffer_size'] = 20  # Buffer più piccolo
    config['risk_parameters']['position_cooldown_minutes'] = 5  # Cooldown minimo
    config['risk_parameters']['max_risk_per_trade'] = 3.0  # Più risk per trade
    
    # Test configuration 
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-10",  # 10 giorni
        initial_balance=100000,
        symbols=["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"],  # 4 simboli
        timeframe="M5"  # 5 minuti per massimi dati
    )
    
    the5ers_rules = The5ersRules()
    
    print(f"📊 Configurazione Test Aggressivo:")
    print(f"   - Periodo: {backtest_config.start_date} - {backtest_config.end_date}")
    print(f"   - Balance: ${backtest_config.initial_balance:,}")
    print(f"   - Simboli: {backtest_config.symbols}")
    print(f"   - Timeframe: {backtest_config.timeframe}")
    print(f"   - Entropy threshold: {config['quantum_params']['entropy_threshold']} (AGGRESSIVO)")
    print(f"   - Max risk per trade: {config['risk_parameters']['max_risk_per_trade']}%")
    print(f"   - Cooldown: {config['risk_parameters']['position_cooldown_minutes']} min")
    
    # Crea engine con logging più dettagliato
    engine = WorkingBacktestEngine(config, backtest_config, the5ers_rules)
    
    print("\n⚡ Esecuzione backtest aggressivo...")
    print("   (Potrebbe richiedere qualche secondo...)")
    
    results = engine.run_backtest()
    
    # Mostra risultati
    print("\n" + "="*70)
    print("📈 RISULTATI TEST AGGRESSIVO")
    print("="*70)
    print(f"Balance iniziale:    ${results['initial_balance']:,}")
    print(f"Balance finale:      ${results['final_balance']:,}")
    print(f"Return assoluto:     ${results['total_return']:,.2f}")
    print(f"Return percentuale:  {results['total_return_pct']:.2f}%")
    print(f"Trades totali:       {results['total_trades']}")
    print(f"Trades vincenti:     {results['winning_trades']}")
    print(f"Trades perdenti:     {results['losing_trades']}")
    print(f"Win rate:            {results['win_rate']:.1f}%")
    print(f"Max drawdown:        {results['max_drawdown']:.2f}%")
    print(f"Giorni profittevoli: {results['profitable_days']}")
    print(f"Sharpe ratio:        {results['sharpe_ratio']:.2f}")
    
    print(f"\n🎯 THE5ERS CHALLENGE STATUS:")
    compliance = results['the5ers_compliance']
    
    step1_status = "🟢 PASSED" if compliance['step1_achieved'] else "🔴 FAILED"
    step2_status = "🟢 PASSED" if compliance['step2_achieved'] else "🔴 FAILED"
    scaling_status = "🟢 PASSED" if compliance['scaling_achieved'] else "🔴 FAILED"
    
    print(f"Step 1 (8%):         {step1_status}")
    print(f"Step 2 (5%):         {step2_status}")
    print(f"Scaling (10%):       {scaling_status}")
    print(f"Max loss limit:      {'🟢 OK' if not compliance['total_loss_violated'] else '🔴 VIOLATED'}")
    print(f"Daily loss limit:    {'🟢 OK' if not compliance['daily_loss_violated'] else '🔴 VIOLATED'}")
    print(f"Min profitable days: {'🟢 OK' if compliance['min_profitable_days'] else '🔴 INSUFFICIENT'}")
    
    # Analisi dettagliata trades
    if results['total_trades'] > 0:
        print(f"\n📊 ANALISI DETTAGLIATA TRADES:")
        trades = results['trades']
        
        # Statistiche base
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        print(f"   📈 Trades vincenti: {len(winning_trades)}")
        if winning_trades:
            avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades)
            max_win = max(t['pnl'] for t in winning_trades)
            print(f"      - Profitto medio: ${avg_win:.2f}")
            print(f"      - Profitto massimo: ${max_win:.2f}")
        
        print(f"   📉 Trades perdenti: {len(losing_trades)}")
        if losing_trades:
            avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
            max_loss = min(t['pnl'] for t in losing_trades)
            print(f"      - Perdita media: ${avg_loss:.2f}")
            print(f"      - Perdita massima: ${max_loss:.2f}")
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        print(f"   💎 Profit Factor: {profit_factor:.2f}")
        
        # Expectancy
        expectancy = (avg_win * len(winning_trades) - abs(avg_loss) * len(losing_trades)) / len(trades) if len(trades) > 0 else 0
        print(f"   🎯 Expectancy: ${expectancy:.2f}")
        
        # Recovery factor
        recovery_factor = abs(results['total_return']) / results['max_drawdown'] if results['max_drawdown'] > 0 else float('inf')
        print(f"   🔄 Recovery Factor: {recovery_factor:.2f}")
        
        # Analisi per simbolo
        print(f"\n💱 PERFORMANCE PER SIMBOLO:")
        symbol_stats = {}
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'trades': 0, 'pnl': 0, 'wins': 0, 'avg_confidence': 0}
            symbol_stats[symbol]['trades'] += 1
            symbol_stats[symbol]['pnl'] += trade['pnl']
            symbol_stats[symbol]['avg_confidence'] += trade['confidence']
            if trade['pnl'] > 0:
                symbol_stats[symbol]['wins'] += 1
        
        for symbol, stats in symbol_stats.items():
            win_rate = (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0
            avg_conf = stats['avg_confidence'] / stats['trades'] if stats['trades'] > 0 else 0
            profit_status = "📈" if stats['pnl'] > 0 else "📉" if stats['pnl'] < 0 else "➡️"
            print(f"   {profit_status} {symbol}: {stats['trades']} trades, ${stats['pnl']:.2f}, {win_rate:.1f}% WR, {avg_conf:.2f} conf")
        
        # Top 5 migliori e peggiori trades
        print(f"\n🏆 TOP 5 MIGLIORI TRADES:")
        best_trades = sorted(trades, key=lambda x: x['pnl'], reverse=True)[:5]
        for i, trade in enumerate(best_trades, 1):
            duration = (trade['exit_time'] - trade['entry_time']).total_seconds() / 60
            print(f"   {i}. {trade['signal']} {trade['symbol']}: ${trade['pnl']:.2f} ({duration:.0f}min, {trade['reason']})")
        
        print(f"\n💸 TOP 5 PEGGIORI TRADES:")
        worst_trades = sorted(trades, key=lambda x: x['pnl'])[:5]
        for i, trade in enumerate(worst_trades, 1):
            duration = (trade['exit_time'] - trade['entry_time']).total_seconds() / 60
            print(f"   {i}. {trade['signal']} {trade['symbol']}: ${trade['pnl']:.2f} ({duration:.0f}min, {trade['reason']})")
        
        # Analisi timing
        print(f"\n⏰ ANALISI TIMING:")
        buy_trades = [t for t in trades if t['signal'] == 'BUY']
        sell_trades = [t for t in trades if t['signal'] == 'SELL']
        
        if buy_trades:
            buy_win_rate = len([t for t in buy_trades if t['pnl'] > 0]) / len(buy_trades) * 100
            buy_avg_pnl = sum(t['pnl'] for t in buy_trades) / len(buy_trades)
            print(f"   📊 BUY trades: {len(buy_trades)}, {buy_win_rate:.1f}% WR, ${buy_avg_pnl:.2f} avg")
        
        if sell_trades:
            sell_win_rate = len([t for t in sell_trades if t['pnl'] > 0]) / len(sell_trades) * 100
            sell_avg_pnl = sum(t['pnl'] for t in sell_trades) / len(sell_trades)
            print(f"   📊 SELL trades: {len(sell_trades)}, {sell_win_rate:.1f}% WR, ${sell_avg_pnl:.2f} avg")
    
    # Analisi equity curve
    if results['equity_curve']:
        print(f"\n📈 ANALISI EQUITY CURVE:")
        equity_values = [point['equity'] for point in results['equity_curve']]
        max_equity = max(equity_values)
        min_equity = min(equity_values)
        
        print(f"   💰 Equity massima: ${max_equity:,.2f}")
        print(f"   📉 Equity minima: ${min_equity:,.2f}")
        print(f"   📊 Range equity: ${max_equity - min_equity:,.2f}")
        print(f"   📈 Crescita equity: {((results['final_balance'] - results['initial_balance']) / results['initial_balance']) * 100:.2f}%")
    
    # Analisi giornaliera dettagliata
    if results['daily_results']:
        print(f"\n📅 PERFORMANCE GIORNALIERA DETTAGLIATA:")
        sorted_days = sorted(results['daily_results'].items())
        positive_days = sum(1 for _, pnl in sorted_days if pnl > 0)
        negative_days = sum(1 for _, pnl in sorted_days if pnl < 0)
        
        print(f"   📊 Giorni positivi: {positive_days}")
        print(f"   📊 Giorni negativi: {negative_days}")
        print(f"   📊 Giorni neutri: {len(sorted_days) - positive_days - negative_days}")
        
        for date, pnl in sorted_days:
            if pnl > 0:
                status = "💚"
            elif pnl < 0:
                status = "❌"
            else:
                status = "⚪"
            print(f"   {status} {date}: ${pnl:.2f}")
        
        # Migliori e peggiori giorni
        if sorted_days:
            best_day = max(sorted_days, key=lambda x: x[1])
            worst_day = min(sorted_days, key=lambda x: x[1])
            print(f"\n   🏆 Miglior giorno: {best_day[0]} (${best_day[1]:.2f})")
            print(f"   💸 Peggior giorno: {worst_day[0]} (${worst_day[1]:.2f})")
    
    return results

if __name__ == "__main__":
    try:
        print("🎯 DIMOSTRAZIONE SISTEMA QUANTUM TRADING THE5ERS")
        print("📋 Questo test usa parametri aggressivi per mostrare il sistema in azione")
        
        results = run_aggressive_test()
        
        print("\n" + "="*70)
        print("🎊 RIEPILOGO FINALE DIMOSTRAZIONE")
        print("="*70)
        
        if results['total_trades'] > 0:
            print(f"✅ SISTEMA FUNZIONANTE!")
            print(f"📊 Trades eseguiti: {results['total_trades']}")
            print(f"💰 Return finale: {results['total_return_pct']:.2f}%")
            print(f"🎯 Win Rate: {results['win_rate']:.1f}%")
            print(f"📉 Max Drawdown: {results['max_drawdown']:.2f}%")
            
            # Challenge status
            compliance = results['the5ers_compliance']
            if compliance['step1_achieved']:
                print(f"🏆 TARGET STEP 1 (8%) RAGGIUNTO!")
            elif compliance['step2_achieved']:
                print(f"🥈 TARGET STEP 2 (5%) RAGGIUNTO!")
            elif results['total_return_pct'] > 0:
                print(f"📈 SISTEMA PROFITTEVOLE - Necessario tuning per target")
            else:
                print(f"⚠️  SISTEMA NECESSITA OTTIMIZZAZIONE")
            
            print(f"\n🔧 PROSSIMI PASSI RACCOMANDATI:")
            print(f"1. 🎛️  Ottimizza parametri quantum per target specifici")
            print(f"2. 📊 Testa periodi più lunghi (1-3 mesi)")
            print(f"3. 🔄 Implementa walk-forward analysis")
            print(f"4. 📈 Usa dati di mercato reali")
            print(f"5. 🎯 Ottimizzazione multi-obiettivo")
            
        else:
            print(f"⚠️  NESSUN TRADE ESEGUITO")
            print(f"💡 Il sistema richiede ulteriore tuning dei parametri")
            print(f"🔧 Suggerimenti:")
            print(f"   - Ridurre entropy_threshold < 0.05")
            print(f"   - Ridurre buffer_size < 20")
            print(f"   - Aumentare periodo di test")
        
        print(f"\n🚀 IL SISTEMA DI BACKTEST È OPERATIVO!")
        print(f"Ora puoi procedere con l'ottimizzazione completa per The5ers Challenge")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
