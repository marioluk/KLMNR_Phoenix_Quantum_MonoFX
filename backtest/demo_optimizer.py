#!/usr/bin/env python3
# ====================================================================================
# DEMO OPTIMIZER - THE5ERS QUANTUM ALGORITHM
# Ottimizzatore demo che garantisce generazione di trade
# ====================================================================================

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import random
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Import del nostro sistema di backtest
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import (
    get_the5ers_config, BacktestConfig, The5ersRules, 
    WorkingBacktestEngine
)

class DemoOptimizer:
    """Ottimizzatore demo che genera sempre trade per testare logica"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Parametri più permissivi per garantire trade
        self.param_ranges = {
            'entropy_threshold': [0.1, 0.2, 0.3],  # Più bassi
            'coherence_threshold': [0.3, 0.4, 0.5],  # Più bassi  
            'entanglement_strength': [0.8, 1.0, 1.2],
            'buffer_size': [20, 30, 40],  # Più piccoli
            'max_risk_per_trade': [1.0, 1.5, 2.0],
            'trailing_stop_pips': [20, 25, 30],
            'take_profit_ratio': [2.0, 2.5, 3.0],
            'position_cooldown_minutes': [10, 15, 20]
        }
    
    def calculate_demo_score(self, results: Dict[str, Any]) -> float:
        """Calcola score demo semplificato"""
        
        if results['total_trades'] == 0:
            return 0.0
        
        return_pct = results['total_return_pct']
        max_dd = results['max_drawdown']
        win_rate = results['win_rate']
        trades = results['total_trades']
        
        # Score base sui risultati
        score = 0.0
        
        # Profitto (40 punti)
        if return_pct > 0:
            score += min(40.0, return_pct * 5)  # 8% = 40 punti
        
        # Controllo rischio (30 punti)
        if max_dd <= 3.0:
            score += 30.0
        elif max_dd <= 5.0:
            score += 20.0
        elif max_dd <= 8.0:
            score += 10.0
        
        # Win rate (20 punti)
        score += min(20.0, (win_rate / 50.0) * 20.0)
        
        # Numero trade (10 punti)
        score += min(10.0, (trades / 10.0) * 10.0)
        
        return min(100.0, max(0.0, score))
    
    def test_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Testa parametri con sistema semplificato"""
        
        start_time = time.time()
        
        try:
            # Configurazione base
            config = get_the5ers_config()
            
            # Applica parametri
            config['quantum_params'].update({
                'entropy_threshold': params['entropy_threshold'],
                'coherence_threshold': params['coherence_threshold'], 
                'entanglement_strength': params['entanglement_strength'],
                'buffer_size': int(params['buffer_size'])
            })
            
            config['risk_parameters'].update({
                'max_risk_per_trade': params['max_risk_per_trade'],
                'trailing_stop_pips': int(params['trailing_stop_pips']),
                'take_profit_ratio': params['take_profit_ratio'],
                'position_cooldown_minutes': int(params['position_cooldown_minutes'])
            })
            
            # Test su periodo breve
            backtest_config = BacktestConfig(
                start_date="2024-01-01",
                end_date="2024-01-03",  # Solo 2 giorni
                initial_balance=100000,
                symbols=["EURUSD"],  # Solo 1 simbolo
                timeframe="M15"
            )
            
            the5ers_rules = The5ersRules()
            
            # Esegui backtest
            engine = WorkingBacktestEngine(config, backtest_config, the5ers_rules)
            results = engine.run_backtest()
            
            # Calcola score
            demo_score = self.calculate_demo_score(results)
            execution_time = time.time() - start_time
            
            return {
                'parameters': params,
                'results': results,
                'demo_score': demo_score,
                'execution_time': execution_time,
                'success': True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'parameters': params,
                'results': {},
                'demo_score': 0.0,
                'execution_time': execution_time,
                'success': False,
                'error': str(e)
            }
    
    def run_demo_optimization(self, max_tests: int = 12) -> List[Dict[str, Any]]:
        """Esegue ottimizzazione demo veloce"""
        
        print("🎯 DEMO OTTIMIZZAZIONE PARAMETRI")
        print("="*50)
        
        # Genera combinazioni
        combinations = []
        
        # Configurazioni test
        test_configs = [
            # Ultra permissiva
            {
                'entropy_threshold': 0.1,
                'coherence_threshold': 0.3,
                'entanglement_strength': 0.8,
                'buffer_size': 20,
                'max_risk_per_trade': 2.0,
                'trailing_stop_pips': 25,
                'take_profit_ratio': 2.5,
                'position_cooldown_minutes': 10
            },
            # Moderata
            {
                'entropy_threshold': 0.2,
                'coherence_threshold': 0.4,
                'entanglement_strength': 1.0,
                'buffer_size': 30,
                'max_risk_per_trade': 1.5,
                'trailing_stop_pips': 25,
                'take_profit_ratio': 2.0,
                'position_cooldown_minutes': 15
            },
            # Conservativa  
            {
                'entropy_threshold': 0.3,
                'coherence_threshold': 0.5,
                'entanglement_strength': 1.2,
                'buffer_size': 40,
                'max_risk_per_trade': 1.0,
                'trailing_stop_pips': 30,
                'take_profit_ratio': 3.0,
                'position_cooldown_minutes': 20
            }
        ]
        
        combinations.extend(test_configs)
        
        # Aggiungi combinazioni casuali
        random.seed(42)
        while len(combinations) < max_tests:
            combo = {}
            for param, values in self.param_ranges.items():
                combo[param] = random.choice(values)
            combinations.append(combo)
        
        print(f"📊 Testando {len(combinations)} configurazioni")
        print(f"⏱️  Test veloce su EURUSD 01-03 Gen 2024")
        
        # Test
        results = []
        for i, params in enumerate(combinations, 1):
            print(f"\nTest {i}/{len(combinations)}: {params}")
            
            result = self.test_parameters(params)
            results.append(result)
            
            if result['success']:
                res = result['results']
                print(f"✅ Score: {result['demo_score']:.1f}, "
                      f"Return: {res['total_return_pct']:.2f}%, "
                      f"Trades: {res['total_trades']}, "
                      f"WinRate: {res['win_rate']:.1f}%")
            else:
                print(f"❌ Errore: {result.get('error', 'Unknown')}")
        
        # Ordina per score
        valid_results = [r for r in results if r['success'] and r['results']['total_trades'] > 0]
        valid_results.sort(key=lambda x: x['demo_score'], reverse=True)
        
        return valid_results
    
    def generate_demo_report(self, results: List[Dict[str, Any]]):
        """Genera report demo"""
        
        if not results:
            print("❌ Nessun risultato con trade generati!")
            return
        
        print("\n" + "="*60)
        print("🏆 DEMO REPORT OTTIMIZZAZIONE")
        print("="*60)
        
        print(f"\n📊 Risultati validi: {len(results)}")
        
        # Top 3
        print(f"\n🥇 TOP 3 CONFIGURAZIONI:")
        for i, result in enumerate(results[:3], 1):
            res = result['results']
            
            print(f"\n{i}. Demo Score: {result['demo_score']:.1f}/100")
            print(f"   📈 Return: {res['total_return_pct']:.2f}%")
            print(f"   📉 Max DD: {res['max_drawdown']:.2f}%")
            print(f"   🎯 Win Rate: {res['win_rate']:.1f}%")
            print(f"   🔢 Trades: {res['total_trades']}")
            print(f"   ⏱️  Tempo: {result['execution_time']:.1f}s")
            print(f"   🔧 Parametri chiave:")
            params = result['parameters']
            print(f"      entropy_threshold: {params['entropy_threshold']}")
            print(f"      coherence_threshold: {params['coherence_threshold']}")
            print(f"      max_risk_per_trade: {params['max_risk_per_trade']}")
        
        # Migliore configurazione
        best = results[0]
        print(f"\n🏆 MIGLIORE CONFIGURAZIONE:")
        print(f"Score: {best['demo_score']:.1f}/100")
        print(f"Parametri completi: {best['parameters']}")
        
        best_res = best['results']
        print(f"\nDettagli performance:")
        print(f"- Return: {best_res['total_return_pct']:.2f}%")
        print(f"- Max Drawdown: {best_res['max_drawdown']:.2f}%")
        print(f"- Win Rate: {best_res['win_rate']:.1f}%") 
        print(f"- Total Trades: {best_res['total_trades']}")
        print(f"- Profitable Days: {best_res['profitable_days']}")

def run_demo():
    """Esegue demo ottimizzazione"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    optimizer = DemoOptimizer()
    results = optimizer.run_demo_optimization(max_tests=9)
    
    optimizer.generate_demo_report(results)
    
    return results

if __name__ == "__main__":
    print("🚀 AVVIO DEMO OTTIMIZZAZIONE")
    print("🎯 Test veloce per trovare parametri che generano trade")
    
    try:
        results = run_demo()
        
        if results:
            print(f"\n🎉 DEMO COMPLETATA!")
            print(f"✅ Trovate {len(results)} configurazioni funzionanti")
            best_score = max(r['demo_score'] for r in results)
            print(f"🏆 Miglior score: {best_score:.1f}/100")
        else:
            print(f"\n⚠️  Nessuna configurazione ha generato trade")
            print(f"💡 Prova con parametri ancora più permissivi")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
