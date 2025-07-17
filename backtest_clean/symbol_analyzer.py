#!/usr/bin/env python3
# ====================================================================================
# THE5ERS SYMBOL PERFORMANCE ANALYZER
# Analizza performance simboli specifici per step ottimali
# ====================================================================================

import json
import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class The5ersSymbolAnalyzer:
    def __init__(self):
        """Inizializza analizzatore simboli"""
        self.symbol_data = {}
        self.session_performance = {}
        
        # Definizioni sessioni trading
        self.trading_sessions = {
            'ASIAN': {'start': 2, 'end': 4, 'description': 'Asian Session'},
            'LONDON': {'start': 9, 'end': 12, 'description': 'London Session'},
            'OVERLAP': {'start': 14, 'end': 16, 'description': 'London/NY Overlap'},
            'NY': {'start': 15, 'end': 17, 'description': 'New York Session'},
            'DEAD': {'start': 18, 'end': 1, 'description': 'Dead Zone'}
        }
        
        # Caratteristiche simboli
        self.symbol_characteristics = {
            'EURUSD': {
                'tier': 1,
                'spread_avg': 1.5,
                'volatility': 'LOW',
                'best_sessions': ['LONDON', 'OVERLAP'],
                'the5ers_rating': 95,
                'step1_suitability': 10,
                'step2_suitability': 9,
                'step3_suitability': 8
            },
            'USDJPY': {
                'tier': 1,
                'spread_avg': 2.0,
                'volatility': 'MEDIUM',
                'best_sessions': ['ASIAN', 'LONDON'],
                'the5ers_rating': 88,
                'step1_suitability': 9,
                'step2_suitability': 10,
                'step3_suitability': 9
            },
            'GBPUSD': {
                'tier': 2,
                'spread_avg': 3.5,
                'volatility': 'HIGH',
                'best_sessions': ['LONDON', 'OVERLAP'],
                'the5ers_rating': 75,
                'step1_suitability': 6,
                'step2_suitability': 8,
                'step3_suitability': 7
            },
            'XAUUSD': {
                'tier': 3,
                'spread_avg': 5.5,
                'volatility': 'VERY_HIGH',
                'best_sessions': ['OVERLAP', 'NY'],
                'the5ers_rating': 65,
                'step1_suitability': 3,
                'step2_suitability': 5,
                'step3_suitability': 7
            },
            'NAS100': {
                'tier': 4,
                'spread_avg': 12.0,
                'volatility': 'EXTREME',
                'best_sessions': ['NY'],
                'the5ers_rating': 45,
                'step1_suitability': 1,
                'step2_suitability': 2,
                'step3_suitability': 4
            }
        }
        
        logger.info("🔍 The5ers Symbol Analyzer inizializzato")
    
    def get_session_for_hour(self, hour):
        """Determina sessione trading per ora"""
        for session_name, session_info in self.trading_sessions.items():
            start = session_info['start']
            end = session_info['end']
            
            if start <= end:  # Normale range
                if start <= hour <= end:
                    return session_name
            else:  # Cross-midnight range
                if hour >= start or hour <= end:
                    return session_name
        
        return 'DEAD'
    
    def calculate_session_bonus(self, symbol, hour):
        """Calcola bonus performance per sessione"""
        session = self.get_session_for_hour(hour)
        symbol_info = self.symbol_characteristics.get(symbol, {})
        best_sessions = symbol_info.get('best_sessions', [])
        
        if session in best_sessions:
            return 1.3  # +30% performance in sessione ottimale
        elif session == 'DEAD':
            return 0.6  # -40% performance in dead zone
        else:
            return 1.0  # Performance normale
    
    def calculate_spread_impact(self, symbol, session_bonus):
        """Calcola impatto spread su profitabilità"""
        symbol_info = self.symbol_characteristics.get(symbol, {})
        spread_avg = symbol_info.get('spread_avg', 3.0)
        
        # Spread impatta inversamente su micro lot
        spread_penalty = max(0.5, 1.0 - (spread_avg - 1.0) * 0.1)
        
        return spread_penalty * session_bonus
    
    def simulate_symbol_step_performance(self, symbol, step, days=30):
        """Simula performance simbolo per step specifico"""
        
        symbol_info = self.symbol_characteristics.get(symbol, {})
        step_suitability = symbol_info.get(f'step{step}_suitability', 5)
        
        # Parametri step-specific
        if step == 1:
            target_return = 0.08  # 8%
            max_daily_trades = 4
            risk_per_trade = 0.0015
            base_sl_pips = 20
        elif step == 2:
            target_return = 0.05  # 5%
            max_daily_trades = 3
            risk_per_trade = 0.0010
            base_sl_pips = 18
        else:  # step 3+
            target_return = 0.03  # 3%
            max_daily_trades = 2
            risk_per_trade = 0.0008
            base_sl_pips = 15
        
        balance = 10000
        peak_balance = balance
        total_trades = 0
        winning_trades = 0
        session_stats = {session: {'trades': 0, 'pnl': 0} for session in self.trading_sessions.keys()}
        
        current_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            daily_trades = 0
            
            # Simula trading durante le ore ottimali per il simbolo
            best_sessions = symbol_info.get('best_sessions', ['LONDON'])
            
            for session_name in best_sessions:
                session_info = self.trading_sessions[session_name]
                session_hours = session_info['end'] - session_info['start'] + 1
                
                for hour_offset in range(session_hours):
                    if daily_trades >= max_daily_trades:
                        break
                    
                    current_hour = session_info['start'] + hour_offset
                    
                    # Bonus sessione
                    session_bonus = self.calculate_session_bonus(symbol, current_hour)
                    spread_bonus = self.calculate_spread_impact(symbol, session_bonus)
                    
                    # Suitability bonus per step
                    step_bonus = step_suitability / 10.0
                    
                    # Probabilità segnale basata su caratteristiche simbolo
                    signal_probability = 0.3 * session_bonus * step_bonus
                    
                    if random.random() > signal_probability:
                        continue
                    
                    # Genera segnale
                    signal = random.choice(['BUY', 'SELL'])
                    
                    # Win probability basata su caratteristiche
                    base_win_rate = 0.45
                    win_rate = base_win_rate + (step_bonus * 0.15) + (spread_bonus * 0.10)
                    
                    is_winner = random.random() < win_rate
                    
                    # Calcola P&L
                    if is_winner:
                        profit_pips = base_sl_pips * random.uniform(1.2, 2.0)
                        pnl = 0.01 * profit_pips * 0.1 * spread_bonus  # Micro lot
                    else:
                        loss_pips = base_sl_pips * random.uniform(0.8, 1.0)
                        pnl = -0.01 * loss_pips * 0.1
                    
                    balance += pnl
                    daily_trades += 1
                    total_trades += 1
                    
                    if is_winner:
                        winning_trades += 1
                    
                    if balance > peak_balance:
                        peak_balance = balance
                    
                    # Stats per sessione
                    session = self.get_session_for_hour(current_hour)
                    session_stats[session]['trades'] += 1
                    session_stats[session]['pnl'] += pnl
            
            current_date += timedelta(days=1)
        
        # Calcola metriche finali
        total_pnl = balance - 10000
        total_return = total_pnl / 10000
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        max_drawdown = (peak_balance - balance) / peak_balance if peak_balance > balance else 0
        
        # Score performance per step
        return_score = min(100, (total_return / target_return) * 100) if target_return > 0 else 0
        risk_score = max(0, 100 - (max_drawdown * 1000))
        efficiency_score = win_rate * 100
        
        overall_score = (return_score * 0.4 + risk_score * 0.3 + efficiency_score * 0.3)
        
        return {
            'symbol': symbol,
            'step': step,
            'total_trades': total_trades,
            'pnl': total_pnl,
            'return': total_return,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'final_balance': balance,
            'session_stats': session_stats,
            'target_return': target_return,
            'return_score': return_score,
            'risk_score': risk_score,
            'efficiency_score': efficiency_score,
            'overall_score': overall_score,
            'step_suitability': step_suitability,
            'tier': symbol_info.get('tier', 4),
            'the5ers_rating': symbol_info.get('the5ers_rating', 50)
        }
    
    def analyze_all_symbols_all_steps(self, days=30):
        """Analizza tutti i simboli per tutti gli step"""
        
        logger.info("🔍 Avvio analisi completa simboli per tutti gli step")
        
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'NAS100']
        steps = [1, 2, 3]
        
        results = {}
        
        for step in steps:
            results[f'step_{step}'] = {}
            logger.info(f"📊 Analizzando STEP {step}...")
            
            step_results = []
            
            for symbol in symbols:
                result = self.simulate_symbol_step_performance(symbol, step, days)
                results[f'step_{step}'][symbol] = result
                step_results.append(result)
            
            # Ordina per overall_score
            step_results.sort(key=lambda x: x['overall_score'], reverse=True)
            results[f'step_{step}']['ranking'] = step_results
        
        logger.info("✅ Analisi completa terminata")
        return results
    
    def generate_symbol_report(self, results):
        """Genera report completo analisi simboli"""
        
        print("\n" + "="*100)
        print("🔍 THE5ERS SYMBOL PERFORMANCE ANALYSIS - COMPLETE REPORT")
        print("="*100)
        
        steps = [1, 2, 3]
        
        for step in steps:
            step_data = results[f'step_{step}']
            ranking = step_data['ranking']
            
            print(f"\n" + "="*80)
            print(f"📊 STEP {step} ANALYSIS - TARGET: {ranking[0]['target_return']:.1%}")
            print("="*80)
            
            print(f"\n{'RANK':<6} {'SYMBOL':<8} {'TIER':<6} {'SCORE':<8} {'RETURN':<10} {'WIN%':<8} {'DD%':<8} {'TRADES':<8}")
            print("-" * 80)
            
            for i, result in enumerate(ranking, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐"
                print(f"{emoji} {i:<4} {result['symbol']:<8} {result['tier']:<6} {result['overall_score']:<7.1f} "
                      f"{result['return']:>8.2%} {result['win_rate']:>6.1%} {result['max_drawdown']:>6.2%} {result['total_trades']:<8}")
            
            # Best symbol analysis
            best = ranking[0]
            print(f"\n🏆 BEST SYMBOL FOR STEP {step}: {best['symbol']}")
            print(f"   Overall Score: {best['overall_score']:.1f}/100")
            print(f"   Return Score: {best['return_score']:.1f}/100 (Target: {best['target_return']:.1%})")
            print(f"   Risk Score: {best['risk_score']:.1f}/100")
            print(f"   Efficiency Score: {best['efficiency_score']:.1f}/100")
            
            # Session analysis for best symbol
            print(f"\n📅 SESSION PERFORMANCE - {best['symbol']}:")
            session_stats = best['session_stats']
            for session_name, stats in session_stats.items():
                if stats['trades'] > 0:
                    avg_pnl = stats['pnl'] / stats['trades']
                    print(f"   {session_name}: {stats['trades']} trades, ${stats['pnl']:.2f} total, ${avg_pnl:.2f} avg")
        
        # Cross-step recommendations
        print(f"\n" + "="*80)
        print("🎯 CROSS-STEP RECOMMENDATIONS")
        print("="*80)
        
        # Find consistent performers
        symbol_avg_scores = {}
        for symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'NAS100']:
            scores = []
            for step in steps:
                result = results[f'step_{step}'][symbol]
                scores.append(result['overall_score'])
            symbol_avg_scores[symbol] = np.mean(scores)
        
        sorted_symbols = sorted(symbol_avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 OVERALL SYMBOL RANKING (Cross-step performance):")
        for i, (symbol, avg_score) in enumerate(sorted_symbols, 1):
            tier = self.symbol_characteristics[symbol]['tier']
            rating = self.symbol_characteristics[symbol]['the5ers_rating']
            
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐"
            print(f"   {emoji} {i}. {symbol}: {avg_score:.1f}/100 (Tier {tier}, Rating {rating}/100)")
        
        # Specific recommendations
        print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
        
        best_step1 = results['step_1']['ranking'][0]['symbol']
        best_step2 = results['step_2']['ranking'][0]['symbol']
        best_step3 = results['step_3']['ranking'][0]['symbol']
        
        print(f"   🎯 STEP 1 (8% target): Focus on {best_step1}")
        print(f"   📊 STEP 2 (5% target): Transition to {best_step2}")
        print(f"   🏆 STEP 3 (3% target): Secure with {best_step3}")
        
        # Portfolio allocation
        print(f"\n📈 OPTIMAL PORTFOLIO ALLOCATION:")
        top_symbol = sorted_symbols[0][0]
        second_symbol = sorted_symbols[1][0]
        
        print(f"   PRIMARY (70%): {top_symbol} - Consistent performer")
        print(f"   SECONDARY (25%): {second_symbol} - Diversification")
        print(f"   TACTICAL (5%): Opportunistic on other symbols")
        
        # Session recommendations
        print(f"\n⏰ OPTIMAL TRADING SESSIONS:")
        for symbol in sorted_symbols[:3]:
            symbol_name = symbol[0]
            best_sessions = self.symbol_characteristics[symbol_name]['best_sessions']
            session_desc = [self.trading_sessions[s]['description'] for s in best_sessions]
            print(f"   {symbol_name}: {', '.join(session_desc)}")
        
        print("="*100)
        
        return sorted_symbols

def main():
    """Funzione principale per analisi simboli"""
    
    print("🔍 THE5ERS SYMBOL PERFORMANCE ANALYZER")
    print("📊 Analisi strategica simboli per ogni step della challenge")
    
    # Inizializza analyzer
    analyzer = The5ersSymbolAnalyzer()
    
    # Esegui analisi completa
    print("\n🚀 Avvio analisi completa...")
    results = analyzer.analyze_all_symbols_all_steps(days=30)
    
    # Genera report
    rankings = analyzer.generate_symbol_report(results)
    
    print(f"\n✅ ANALISI SIMBOLI COMPLETATA!")
    print(f"🏆 Best overall symbol: {rankings[0][0]}")
    
    return results

if __name__ == "__main__":
    main()
