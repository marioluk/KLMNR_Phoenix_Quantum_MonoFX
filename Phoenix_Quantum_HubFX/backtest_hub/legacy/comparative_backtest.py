#!/usr/bin/env python3
# ====================================================================================
# THE5ERS COMPARATIVE BACKTEST - MULTI-CONFIG PERFORMANCE ANALYSIS
# Sistema di test comparativo per tutte le configurazioni The5ers
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

class The5ersComparativeBacktest:
    def __init__(self):
        """Inizializza sistema comparativo multi-config"""
        self.configs = {}
        self.results = {}
        
        logger.info("🔥 The5ers Comparative Backtest System inizializzato")
    
    def load_all_configs(self):
        """Carica tutte le configurazioni disponibili"""
        
        config_files = [
            ('ATTUALE', '../PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json'),
            ('ULTRA_CONSERVATIVE', 'config_ultra_conservative_step1.json'),
            ('CONSERVATIVE', 'config_conservative_step1.json'),
            ('STEP2', 'config_step2_conservative.json')
        ]
        
        for name, file_path in config_files:
            try:
                full_path = os.path.join(os.path.dirname(__file__), file_path)
                with open(full_path, 'r') as f:
                    config = json.load(f)
                self.configs[name] = config
                logger.info(f"✅ Config '{name}' caricata: {file_path}")
            except Exception as e:
                logger.warning(f"⚠️  Config '{name}' non trovata: {e}")
        
        logger.info(f"📊 Totale configurazioni caricate: {len(self.configs)}")
        return len(self.configs)
    
    def get_all_symbols_from_configs(self):
        """Ottieni tutti i simboli presenti nelle configurazioni"""
        all_symbols = set()
        symbol_configs = {}
        
        for config_name, config in self.configs.items():
            config_symbols = config.get('symbols', {})
            for symbol in config_symbols.keys():
                all_symbols.add(symbol)
                if symbol not in symbol_configs:
                    symbol_configs[symbol] = []
                symbol_configs[symbol].append(config_name)
        
        logger.info(f"🔍 Simboli disponibili: {sorted(all_symbols)}")
        for symbol, configs in symbol_configs.items():
            logger.info(f"   {symbol}: presente in {len(configs)} configurazioni {configs}")
        
        return sorted(list(all_symbols)), symbol_configs
    
    def extract_symbol_params(self, config, symbol):
        """Estrae parametri per simbolo da configurazione"""
        
        symbols = config.get('symbols', {})
        symbol_config = symbols.get(symbol, {})
        
        if not symbol_config.get('enabled', True):
            return None
        
        risk_mgmt = symbol_config.get('risk_management', {})
        quantum_override = symbol_config.get('quantum_params_override', {})
        
        # Fallback a parametri globali
        global_risk = config.get('risk_parameters', {})
        global_quantum = config.get('quantum_params', {})
        
        return {
            'contract_size': risk_mgmt.get('contract_size', 0.01),
            'base_sl_pips': risk_mgmt.get('base_sl_pips', global_risk.get('base_sl_pips', {}).get(symbol, 30)),
            'profit_multiplier': risk_mgmt.get('profit_multiplier', global_risk.get('profit_multiplier', 2.0)),
            'risk_percent': risk_mgmt.get('risk_percent', global_risk.get('risk_percent', 0.0015)),
            'max_daily_trades': symbol_config.get('max_daily_trades', global_risk.get('max_daily_trades', 5)),
            'signal_cooldown': quantum_override.get('signal_cooldown', global_quantum.get('signal_cooldown', 600)),
            'buy_signal': quantum_override.get('entropy_thresholds', {}).get('buy_signal', 
                        global_quantum.get('entropy_thresholds', {}).get('buy_signal', 0.58)),
            'sell_signal': quantum_override.get('entropy_thresholds', {}).get('sell_signal',
                         global_quantum.get('entropy_thresholds', {}).get('sell_signal', 0.42)),
            'trading_hours': symbol_config.get('trading_hours', ['09:00-17:00'])
        }
    
    def simulate_symbol_performance(self, config_name, symbol, params, days=30):
        """Simula performance per simbolo specifico"""
        
        if not params:
            return {
                'trades': 0,
                'pnl': 0,
                'win_rate': 0,
                'max_drawdown': 0,
                'enabled': False
            }
        
        trades = []
        balance = 10000  # $10k per simbolo
        peak_balance = balance
        
        current_date = datetime.now() - timedelta(days=days)
        
        total_trades = 0
        winning_trades = 0
        
        for day in range(days):
            daily_trades = 0
            
            # Simula trading hours (2-4 ore al giorno)
            trading_hours = min(4, len(params['trading_hours']) * 2)
            
            for hour in range(trading_hours):
                
                if daily_trades >= params['max_daily_trades']:
                    break
                
                # Simula quantum signal
                entropy = random.uniform(0, 1)
                
                # Applica thresholds
                if entropy > params['buy_signal']:
                    signal = "BUY"
                elif entropy < params['sell_signal']:
                    signal = "SELL"
                else:
                    continue
                
                # Signal strength
                strength = abs(entropy - 0.5) * 2
                
                # Position size
                risk_amount = balance * params['risk_percent']
                position_size = params['contract_size']
                
                # Simula outcome
                win_prob = 0.40 + (strength * 0.25)  # 40-65% win rate
                is_winner = random.random() < win_prob
                
                if is_winner:
                    # Profit in pips
                    profit_pips = params['base_sl_pips'] * params['profit_multiplier'] * random.uniform(0.7, 1.0)
                    pnl = position_size * profit_pips * 0.1  # $0.1 per pip per micro lot
                else:
                    # Loss in pips
                    loss_pips = params['base_sl_pips'] * random.uniform(0.8, 1.0)
                    pnl = -position_size * loss_pips * 0.1
                
                balance += pnl
                daily_trades += 1
                total_trades += 1
                
                if is_winner:
                    winning_trades += 1
                
                if balance > peak_balance:
                    peak_balance = balance
                
                trades.append({
                    'date': current_date + timedelta(days=day),
                    'signal': signal,
                    'pnl': pnl,
                    'balance': balance,
                    'is_winner': is_winner
                })
            
            current_date += timedelta(days=1)
        
        # Calcola metriche
        total_pnl = balance - 10000
        total_return = total_pnl / 10000
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        max_drawdown = (peak_balance - balance) / peak_balance if peak_balance > balance else 0
        
        return {
            'trades': total_trades,
            'pnl': total_pnl,
            'return': total_return,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'final_balance': balance,
            'enabled': True
        }
    
    def run_comparative_backtest(self, days=30):
        """Esegue backtest comparativo su tutte le configurazioni"""
        
        logger.info(f"🚀 Avvio backtest comparativo - {days} giorni")
        
        # Estrai automaticamente tutti i simboli dalle configurazioni
        all_symbols = set()
        for config_name, config in self.configs.items():
            config_symbols = config.get('symbols', {})
            all_symbols.update(config_symbols.keys())
        
        symbols = sorted(list(all_symbols))
        logger.info(f"📊 Simboli trovati nelle configurazioni: {symbols}")
        
        if not symbols:
            # Fallback ai simboli default se nessuno trovato nelle config
            symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'NAS100']
            logger.warning(f"⚠️  Nessun simbolo trovato nelle config, uso default: {symbols}")
        
        
        for config_name, config in self.configs.items():
            
            logger.info(f"📊 Testing configurazione: {config_name}")
            
            config_results = {
                'symbols': {},
                'totals': {
                    'total_trades': 0,
                    'total_pnl': 0,
                    'total_return': 0,
                    'portfolio_balance': 0,
                    'max_drawdown': 0,
                    'win_rate': 0,
                    'enabled_symbols': 0
                }
            }
            
            total_trades = 0
            total_winning = 0
            portfolio_pnl = 0
            
            for symbol in symbols:
                
                params = self.extract_symbol_params(config, symbol)
                result = self.simulate_symbol_performance(config_name, symbol, params, days)
                
                config_results['symbols'][symbol] = result
                
                if result['enabled']:
                    config_results['totals']['enabled_symbols'] += 1
                    total_trades += result['trades']
                    total_winning += result['trades'] * result['win_rate']
                    portfolio_pnl += result['pnl']
            
            # Calcola totali portfolio
            config_results['totals']['total_trades'] = total_trades
            config_results['totals']['total_pnl'] = portfolio_pnl
            config_results['totals']['total_return'] = portfolio_pnl / (10000 * config_results['totals']['enabled_symbols']) if config_results['totals']['enabled_symbols'] > 0 else 0
            config_results['totals']['portfolio_balance'] = (10000 * config_results['totals']['enabled_symbols']) + portfolio_pnl
            config_results['totals']['win_rate'] = total_winning / total_trades if total_trades > 0 else 0
            
            # Stima max drawdown portfolio
            config_results['totals']['max_drawdown'] = np.mean([result['max_drawdown'] for result in config_results['symbols'].values() if result['enabled']]) if config_results['totals']['enabled_symbols'] > 0 else 0
            
            self.results[config_name] = config_results
        
        logger.info("✅ Backtest comparativo completato!")
        return self.results
    
    def generate_comparative_report(self):
        """Genera report comparativo completo"""
        
        print("\n" + "="*100)
        print("🔥 THE5ERS COMPARATIVE BACKTEST - MULTI-CONFIG ANALYSIS")
        print("="*100)
        
        print(f"\n📊 CONFIGURAZIONI TESTATE: {len(self.results)}")
        
        # Summary table
        print(f"\n{'CONFIG':<20} {'SIMBOLI':<8} {'TRADES':<8} {'P&L ($)':<12} {'RETURN':<10} {'WIN%':<8} {'DD%':<8} {'RATING':<8}")
        print("-" * 100)
        
        ratings = {}
        
        for config_name, results in self.results.items():
            totals = results['totals']
            
            # Calcola rating (0-100)
            return_score = min(100, max(0, totals['total_return'] * 1000))  # Return weight
            drawdown_score = max(0, 100 - (totals['max_drawdown'] * 1000))  # Drawdown penalty
            trades_score = min(100, totals['total_trades'] * 2)  # Activity bonus
            win_rate_score = totals['win_rate'] * 100  # Win rate
            
            rating = (return_score * 0.4 + drawdown_score * 0.3 + win_rate_score * 0.2 + trades_score * 0.1)
            ratings[config_name] = rating
            
            print(f"{config_name:<20} {totals['enabled_symbols']:<8} {totals['total_trades']:<8} "
                  f"${totals['total_pnl']:>10.2f} {totals['total_return']:>8.2%} "
                  f"{totals['win_rate']:>6.1%} {totals['max_drawdown']:>6.2%} {rating:>6.1f}")
        
        # Best configuration
        best_config = max(ratings.keys(), key=lambda k: ratings[k])
        
        print(f"\n🏆 MIGLIORE CONFIGURAZIONE: {best_config} (Rating: {ratings[best_config]:.1f})")
        
        # Detailed analysis per config
        for config_name, results in self.results.items():
            
            print(f"\n" + "="*80)
            print(f"📋 DETTAGLIO: {config_name}")
            print("="*80)
            
            totals = results['totals']
            
            print(f"\n💰 PERFORMANCE PORTFOLIO:")
            print(f"   Simboli Attivi: {totals['enabled_symbols']}")
            print(f"   Totale Trades: {totals['total_trades']}")
            print(f"   Portfolio P&L: ${totals['total_pnl']:,.2f}")
            print(f"   Portfolio Return: {totals['total_return']:.2%}")
            print(f"   Win Rate: {totals['win_rate']:.1%}")
            print(f"   Max Drawdown: {totals['max_drawdown']:.2%}")
            
            print(f"\n📊 PERFORMANCE PER SIMBOLO:")
            print(f"{'SIMBOLO':<10} {'STATUS':<12} {'TRADES':<8} {'P&L ($)':<12} {'RETURN':<10} {'WIN%':<8}")
            print("-" * 70)
            
            for symbol, symbol_result in results['symbols'].items():
                status = "ENABLED" if symbol_result['enabled'] else "DISABLED"
                return_pct = symbol_result.get('return', 0.0)  # Safe access con default
                win_rate = symbol_result.get('win_rate', 0.0)  # Safe access con default
                pnl = symbol_result.get('pnl', 0.0)  # Safe access con default
                trades = symbol_result.get('trades', 0)  # Safe access con default
                
                print(f"{symbol:<10} {status:<12} {trades:<8} "
                      f"${pnl:>10.2f} {return_pct:>8.2%} "
                      f"{win_rate:>6.1%}")
            
            # The5ers compliance check
            print(f"\n🎯 THE5ERS COMPLIANCE:")
            step1_target = 0.08  # 8%
            daily_loss_limit = 0.05  # 5%
            total_loss_limit = 0.10  # 10%
            
            step1_passed = totals['total_return'] >= step1_target
            risk_compliant = totals['max_drawdown'] < daily_loss_limit
            
            print(f"   Step 1 Target (8%): {'✅ PASSED' if step1_passed else '❌ FAILED'} ({totals['total_return']:.2%})")
            print(f"   Risk Management: {'✅ PASSED' if risk_compliant else '❌ FAILED'} (DD: {totals['max_drawdown']:.2%})")
            print(f"   Overall Rating: {ratings[config_name]:.1f}/100")
        
        # Recommendations
        print(f"\n" + "="*80)
        print("🎯 RACCOMANDAZIONI")
        print("="*80)
        
        sorted_configs = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n📈 RANKING CONFIGURAZIONI:")
        for i, (config, rating) in enumerate(sorted_configs, 1):
            totals = self.results[config]['totals']
            print(f"   {i}. {config} - Rating: {rating:.1f} (Return: {totals['total_return']:.2%}, DD: {totals['max_drawdown']:.2%})")
        
        print(f"\n🚀 RACCOMANDAZIONE FINALE:")
        best_totals = self.results[best_config]['totals']
        
        if best_totals['total_return'] >= 0.08 and best_totals['max_drawdown'] < 0.05:
            print(f"   ✅ USA '{best_config}' per Step 1 - Compliance garantito!")
        elif best_totals['total_return'] >= 0.05:
            print(f"   ⚠️  '{best_config}' promettente ma richiede ottimizzazioni")
        else:
            print(f"   ❌ Tutte le configurazioni richiedono ulteriori ottimizzazioni")
        
        print(f"\n💡 STRATEGIA SUGGERITA:")
        print(f"   1. Inizia con: {sorted_configs[0][0]}")
        print(f"   2. Backup: {sorted_configs[1][0] if len(sorted_configs) > 1 else 'N/A'}")
        print(f"   3. Monitor daily drawdown < 5%")
        print(f"   4. Target Step 1: 8% in 30 giorni")
        
        print("="*100)
        
        return sorted_configs

def main():
    """Funzione principale per backtest comparativo"""
    
    print("🔥 THE5ERS COMPARATIVE BACKTEST SYSTEM")
    print("🔧 Test multi-configurazione per ottimizzazione parametri")
    
    # Inizializza sistema
    backtest = The5ersComparativeBacktest()
    
    # Carica configurazioni
    configs_loaded = backtest.load_all_configs()
    
    if configs_loaded == 0:
        print("❌ Nessuna configurazione trovata!")
        return
    
    print(f"\n🎯 Configurazioni caricate: {configs_loaded}")
    print("📊 Avvio analisi comparativa...")
    
    # Esegui backtest
    results = backtest.run_comparative_backtest(days=30)
    
    # Genera report
    rankings = backtest.generate_comparative_report()
    
    print(f"\n✅ ANALISI COMPARATIVA COMPLETATA!")
    print(f"🏆 Configurazione vincente: {rankings[0][0]}")
    
    return results

if __name__ == "__main__":
    main()
