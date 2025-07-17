#!/usr/bin/env python3
# ====================================================================================
# AUTOMATIC PARAMETER OPTIMIZER - THE5ERS QUANTUM ALGORITHM
# Sistema di ottimizzazione automatica per The5ers Challenge
# ====================================================================================

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import itertools
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import random
import time
import os
from pathlib import Path

# Import del nostro sistema di backtest
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import (
    get_the5ers_config, BacktestConfig, The5ersRules, 
    WorkingBacktestEngine
)

# ====================================================================================
# MAIN OPTIMIZATION RUNNER
# ====================================================================================

class AutomaticParameterOptimizer:
    """Ottimizzatore automatico dei parametri quantum per The5ers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results_dir = Path("optimization_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Parametri da ottimizzare con i loro range
        self.param_ranges = {
            'entropy_threshold': [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'coherence_threshold': [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'entanglement_strength': [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5],
            'buffer_size': [10, 15, 20, 25, 30, 40, 50, 70, 100],
            'max_risk_per_trade': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
            'trailing_stop_pips': [10, 15, 20, 25, 30, 35, 40],
            'take_profit_ratio': [1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
            'position_cooldown_minutes': [5, 10, 15, 20, 30, 45, 60]
        }
    
    def calculate_the5ers_score(self, results: Dict[str, Any], target_step: int = 1) -> float:
        """Calcola score The5ers (0-100)"""
        if results['total_trades'] < 5:
            return 0.0
        
        compliance = results['the5ers_compliance']
        return_pct = results['total_return_pct']
        max_dd = results['max_drawdown']
        win_rate = results['win_rate']
        
        targets = {1: 8.0, 2: 5.0, 3: 10.0}
        target = targets.get(target_step, 8.0)
        
        score = 0.0
        
        # Target Achievement (40 points)
        if return_pct >= target:
            score += 40.0
        else:
            score += (return_pct / target) * 40.0 if return_pct > 0 else 0.0
        
        # Risk Management (25 points)
        if max_dd <= 5.0:
            score += 25.0
        elif max_dd <= 8.0:
            score += 20.0
        elif max_dd <= 10.0:
            score += 15.0
        else:
            score += max(0, 15.0 - (max_dd - 10.0) * 2)
        
        # Consistency (20 points)
        daily_results = results.get('daily_results', {})
        profitable_days = len([pnl for pnl in daily_results.values() if pnl > 0])
        total_days = max(1, len(daily_results))
        consistency_score = min(20.0, (profitable_days / total_days) * 30.0)
        score += consistency_score
        
        # Win Rate (10 points)
        score += min(10.0, (win_rate / 60.0) * 10.0)
        
        # Compliance Bonus (5 points)
        if not compliance['daily_loss_violated'] and not compliance['total_loss_violated']:
            score += 5.0
        
        # Penalties
        if compliance['total_loss_violated']:
            score *= 0.5
        if compliance['daily_loss_violated']:
            score *= 0.8
        
        return min(100.0, max(0.0, score))
    
    def test_parameter_combination(self, params: Dict[str, Any], 
                                 config: Dict[str, Any],
                                 test_period: Tuple[str, str],
                                 symbols: List[str]) -> Dict[str, Any]:
        """Testa una combinazione di parametri"""
        
        start_time = time.time()
        
        try:
            # Applica parametri alla configurazione
            test_config = config.copy()
            
            # Parametri quantum
            if 'entropy_threshold' in params:
                test_config['quantum_params']['entropy_threshold'] = params['entropy_threshold']
            if 'coherence_threshold' in params:
                test_config['quantum_params']['coherence_threshold'] = params['coherence_threshold']
            if 'entanglement_strength' in params:
                test_config['quantum_params']['entanglement_strength'] = params['entanglement_strength']
            if 'buffer_size' in params:
                test_config['quantum_params']['buffer_size'] = int(params['buffer_size'])
            
            # Parametri risk
            if 'max_risk_per_trade' in params:
                test_config['risk_parameters']['max_risk_per_trade'] = params['max_risk_per_trade']
            if 'trailing_stop_pips' in params:
                test_config['risk_parameters']['trailing_stop_pips'] = int(params['trailing_stop_pips'])
            if 'take_profit_ratio' in params:
                test_config['risk_parameters']['take_profit_ratio'] = params['take_profit_ratio']
            if 'position_cooldown_minutes' in params:
                test_config['risk_parameters']['position_cooldown_minutes'] = int(params['position_cooldown_minutes'])
            
            # Configurazione backtest
            backtest_config = BacktestConfig(
                start_date=test_period[0],
                end_date=test_period[1],
                initial_balance=100000,
                symbols=symbols,
                timeframe="M15"
            )
            
            the5ers_rules = The5ersRules()
            
            # Esegui backtest
            engine = WorkingBacktestEngine(test_config, backtest_config, the5ers_rules)
            results = engine.run_backtest()
            
            # Calcola score
            the5ers_score = self.calculate_the5ers_score(results, target_step=1)
            execution_time = time.time() - start_time
            
            return {
                'parameters': params,
                'results': results,
                'the5ers_score': the5ers_score,
                'execution_time': execution_time,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'parameters': params,
                'results': {},
                'the5ers_score': 0.0,
                'execution_time': execution_time,
                'success': False,
                'error': str(e)
            }
    
    def generate_parameter_combinations(self, max_combinations: int = 50) -> List[Dict[str, Any]]:
        """Genera combinazioni di parametri smart"""
        
        # Strategia 1: Combinazioni casuali ma intelligenti
        combinations = []
        
        # Aggiungi alcune configurazioni base
        base_configs = [
            # Conservativa
            {
                'entropy_threshold': 0.7,
                'coherence_threshold': 0.8,
                'entanglement_strength': 1.0,
                'buffer_size': 50,
                'max_risk_per_trade': 1.5,
                'trailing_stop_pips': 25,
                'take_profit_ratio': 2.0,
                'position_cooldown_minutes': 30
            },
            # Aggressiva
            {
                'entropy_threshold': 0.3,
                'coherence_threshold': 0.5,
                'entanglement_strength': 1.5,
                'buffer_size': 30,
                'max_risk_per_trade': 2.5,
                'trailing_stop_pips': 20,
                'take_profit_ratio': 2.5,
                'position_cooldown_minutes': 15
            },
            # Bilanciata
            {
                'entropy_threshold': 0.5,
                'coherence_threshold': 0.7,
                'entanglement_strength': 1.2,
                'buffer_size': 40,
                'max_risk_per_trade': 2.0,
                'trailing_stop_pips': 25,
                'take_profit_ratio': 2.5,
                'position_cooldown_minutes': 20
            }
        ]
        
        combinations.extend(base_configs)
        
        # Genera combinazioni casuali
        random.seed(42)  # Per riproducibilità
        while len(combinations) < max_combinations:
            combo = {}
            for param, values in self.param_ranges.items():
                combo[param] = random.choice(values)
            combinations.append(combo)
        
        return combinations[:max_combinations]
    
    def run_quick_optimization(self, max_tests: int = 30) -> List[Dict[str, Any]]:
        """Esegue ottimizzazione veloce"""
        
        self.logger.info("🚀 AVVIO OTTIMIZZAZIONE VELOCE")
        
        # Configurazione base
        config = get_the5ers_config()
        
        # Periodo di test (breve per velocità)
        test_period = ("2024-01-01", "2024-01-07")  # 1 settimana
        symbols = ["EURUSD", "GBPUSD"]  # 2 simboli
        
        # Genera combinazioni
        combinations = self.generate_parameter_combinations(max_tests)
        
        self.logger.info(f"📊 Testando {len(combinations)} combinazioni")
        self.logger.info(f"📅 Periodo: {test_period[0]} - {test_period[1]}")
        self.logger.info(f"💱 Simboli: {symbols}")
        
        # Test delle combinazioni
        results = []
        for i, params in enumerate(combinations, 1):
            self.logger.info(f"Test {i}/{len(combinations)}: {params}")
            
            result = self.test_parameter_combination(params, config, test_period, symbols)
            results.append(result)
            
            if result['success']:
                self.logger.info(f"✅ Score: {result['the5ers_score']:.1f}, "
                               f"Return: {result['results']['total_return_pct']:.2f}%, "
                               f"DD: {result['results']['max_drawdown']:.2f}%")
            else:
                self.logger.warning(f"❌ Errore: {result['error']}")
        
        # Ordina per score
        valid_results = [r for r in results if r['success']]
        valid_results.sort(key=lambda x: x['the5ers_score'], reverse=True)
        
        return valid_results
    
    def run_extended_optimization(self, max_tests: int = 50) -> List[Dict[str, Any]]:
        """Esegue ottimizzazione estesa"""
        
        self.logger.info("🚀 AVVIO OTTIMIZZAZIONE ESTESA")
        
        # Configurazione base
        config = get_the5ers_config()
        
        # Periodo di test esteso
        test_period = ("2024-01-01", "2024-01-21")  # 3 settimane
        symbols = ["EURUSD", "GBPUSD", "XAUUSD"]  # 3 simboli
        
        # Genera più combinazioni
        combinations = self.generate_parameter_combinations(max_tests)
        
        self.logger.info(f"📊 Testando {len(combinations)} combinazioni")
        self.logger.info(f"📅 Periodo: {test_period[0]} - {test_period[1]}")
        self.logger.info(f"💱 Simboli: {symbols}")
        
        # Test delle combinazioni
        results = []
        for i, params in enumerate(combinations, 1):
            self.logger.info(f"Test {i}/{len(combinations)}: {params}")
            
            result = self.test_parameter_combination(params, config, test_period, symbols)
            results.append(result)
            
            if result['success']:
                self.logger.info(f"✅ Score: {result['the5ers_score']:.1f}, "
                               f"Return: {result['results']['total_return_pct']:.2f}%, "
                               f"DD: {result['results']['max_drawdown']:.2f}%")
            else:
                self.logger.warning(f"❌ Errore: {result['error']}")
        
        # Ordina per score
        valid_results = [r for r in results if r['success']]
        valid_results.sort(key=lambda x: x['the5ers_score'], reverse=True)
        
        return valid_results
    
    def save_optimization_results(self, results: List[Dict[str, Any]], prefix: str = "optimization"):
        """Salva risultati ottimizzazione"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva CSV summary
        csv_data = []
        for result in results:
            if result['success']:
                row = result['parameters'].copy()
                row.update({
                    'the5ers_score': result['the5ers_score'],
                    'total_return_pct': result['results']['total_return_pct'],
                    'max_drawdown': result['results']['max_drawdown'],
                    'win_rate': result['results']['win_rate'],
                    'total_trades': result['results']['total_trades'],
                    'execution_time': result['execution_time']
                })
                csv_data.append(row)
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            csv_file = self.results_dir / f"{prefix}_results_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            self.logger.info(f"📄 Risultati salvati: {csv_file}")
            return csv_file
        
        return None
    
    def generate_optimization_report(self, results: List[Dict[str, Any]]):
        """Genera report ottimizzazione"""
        
        valid_results = [r for r in results if r['success']]
        
        if not valid_results:
            print("❌ Nessun risultato valido trovato!")
            return
        
        print("\n" + "="*80)
        print("🏆 REPORT OTTIMIZZAZIONE PARAMETRI THE5ERS")
        print("="*80)
        
        print(f"\n📊 STATISTICHE GENERALI:")
        print(f"   Tests totali: {len(results)}")
        print(f"   Tests validi: {len(valid_results)}")
        print(f"   Tasso successo: {len(valid_results)/len(results)*100:.1f}%")
        
        # Top 5 risultati
        print(f"\n🥇 TOP 5 CONFIGURAZIONI:")
        for i, result in enumerate(valid_results[:5], 1):
            res = result['results']
            compliance = res['the5ers_compliance']
            
            print(f"\n{i}. Score The5ers: {result['the5ers_score']:.1f}/100")
            print(f"   📈 Return: {res['total_return_pct']:.2f}%")
            print(f"   📉 Max DD: {res['max_drawdown']:.2f}%") 
            print(f"   🎯 Win Rate: {res['win_rate']:.1f}%")
            print(f"   🔢 Trades: {res['total_trades']}")
            print(f"   ⏱️  Tempo: {result['execution_time']:.1f}s")
            
            # Compliance
            step1 = "✅" if compliance['step1_achieved'] else "❌"
            step2 = "✅" if compliance['step2_achieved'] else "❌"
            scaling = "✅" if compliance['scaling_achieved'] else "❌"
            
            print(f"   🎯 Compliance: Step1 {step1} | Step2 {step2} | Scaling {scaling}")
            print(f"   🔧 Parametri: {result['parameters']}")
        
        # Analisi miglior configurazione
        best = valid_results[0]
        print(f"\n🏆 MIGLIOR CONFIGURAZIONE DETTAGLI:")
        print(f"Score The5ers: {best['the5ers_score']:.1f}/100")
        
        best_results = best['results']
        best_compliance = best_results['the5ers_compliance']
        
        print(f"\n📊 Performance:")
        print(f"   Return: {best_results['total_return_pct']:.2f}%")
        print(f"   Max Drawdown: {best_results['max_drawdown']:.2f}%")
        print(f"   Win Rate: {best_results['win_rate']:.1f}%")
        print(f"   Total Trades: {best_results['total_trades']}")
        print(f"   Profitable Days: {best_results['profitable_days']}")
        
        print(f"\n🎯 The5ers Compliance:")
        print(f"   Step 1 (8%): {'✅ PASSED' if best_compliance['step1_achieved'] else '❌ FAILED'}")
        print(f"   Step 2 (5%): {'✅ PASSED' if best_compliance['step2_achieved'] else '❌ FAILED'}")
        print(f"   Scaling (10%): {'✅ PASSED' if best_compliance['scaling_achieved'] else '❌ FAILED'}")
        print(f"   Daily Loss: {'✅ OK' if not best_compliance['daily_loss_violated'] else '❌ VIOLATED'}")
        print(f"   Total Loss: {'✅ OK' if not best_compliance['total_loss_violated'] else '❌ VIOLATED'}")
        
        print(f"\n🔧 Parametri Ottimali:")
        for param, value in best['parameters'].items():
            print(f"   {param}: {value}")
        
        # Raccomandazioni
        print(f"\n🚀 RACCOMANDAZIONI:")
        if best['the5ers_score'] >= 80:
            print("   ✅ Configurazione eccellente! Pronta per The5ers Challenge")
        elif best['the5ers_score'] >= 60:
            print("   ⚠️  Configurazione buona, possibili miglioramenti")
        else:
            print("   ❌ Configurazione necessita ottimizzazioni significative")
        
        if best_compliance['step1_achieved']:
            print("   🏆 Pronto per Step 1 Challenge!")
        elif best_results['total_return_pct'] > 0:
            print("   📈 Sistema profittevole, ottimizza per target The5ers")
        else:
            print("   ⚠️  Rivedi parametri di base")

# ====================================================================================
# MAIN EXECUTION FUNCTIONS
# ====================================================================================

def run_quick_optimization():
    """Esegue ottimizzazione veloce (20-30 test)"""
    
    print("⚡ OTTIMIZZAZIONE VELOCE THE5ERS QUANTUM PARAMETERS")
    print("="*60)
    
    optimizer = AutomaticParameterOptimizer()
    results = optimizer.run_quick_optimization(max_tests=25)
    
    # Salva risultati
    csv_file = optimizer.save_optimization_results(results, "quick_optimization")
    
    # Genera report
    optimizer.generate_optimization_report(results)
    
    return results

def run_extended_optimization():
    """Esegue ottimizzazione estesa (40-50 test)"""
    
    print("🚀 OTTIMIZZAZIONE ESTESA THE5ERS QUANTUM PARAMETERS")
    print("="*60)
    
    optimizer = AutomaticParameterOptimizer()
    results = optimizer.run_extended_optimization(max_tests=40)
    
    # Salva risultati
    csv_file = optimizer.save_optimization_results(results, "extended_optimization")
    
    # Genera report
    optimizer.generate_optimization_report(results)
    
    return results

def run_comprehensive_optimization():
    """Esegue ottimizzazione completa (multi-step)"""
    
    print("🎯 OTTIMIZZAZIONE COMPLETA THE5ERS CHALLENGE")
    print("="*60)
    
    # Step 1: Quick optimization
    print("\n📋 FASE 1: Ottimizzazione veloce per parametri base...")
    quick_results = run_quick_optimization()
    
    # Step 2: Extended optimization sui migliori
    print("\n📋 FASE 2: Ottimizzazione estesa sui parametri migliori...")
    extended_results = run_extended_optimization()
    
    # Step 3: Analisi finale
    print("\n📋 FASE 3: Analisi finale e raccomandazioni...")
    
    all_results = quick_results + extended_results
    all_results.sort(key=lambda x: x['the5ers_score'], reverse=True)
    
    # Report finale
    optimizer = AutomaticParameterOptimizer()
    optimizer.generate_optimization_report(all_results[:10])  # Top 10
    
    return all_results

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("🎯 AVVIO OTTIMIZZAZIONE AUTOMATICA PARAMETRI")
        print("🔧 Sistema di ottimizzazione per The5ers Challenge")
        print("="*60)
        
        # Chiedi all'utente che tipo di ottimizzazione vuole
        print("\nTipi di ottimizzazione disponibili:")
        print("1. ⚡ Veloce (25 test, ~5-10 min)")
        print("2. 🚀 Estesa (40 test, ~15-20 min)")  
        print("3. 🎯 Completa (Multi-step, ~30-40 min)")
        
        choice = input("\nScegli ottimizzazione (1/2/3) [default=1]: ").strip()
        
        if choice == "2":
            results = run_extended_optimization()
        elif choice == "3":
            results = run_comprehensive_optimization()
        else:
            results = run_quick_optimization()
        
        print(f"\n🎉 OTTIMIZZAZIONE COMPLETATA!")
        print(f"✅ Trovate {len([r for r in results if r['success']])} configurazioni valide")
        print(f"🏆 Miglior score: {max(r['the5ers_score'] for r in results if r['success']):.1f}/100")
        
    except Exception as e:
        print(f"\n❌ ERRORE OTTIMIZZAZIONE: {e}")
        import traceback
        traceback.print_exc()
