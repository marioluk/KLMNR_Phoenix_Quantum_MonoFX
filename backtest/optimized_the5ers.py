#!/usr/bin/env python3
# ====================================================================================
# OPTIMIZED THE5ERS SYSTEM - FINAL VERSION
# Sistema ottimizzato con i migliori parametri trovati
# ====================================================================================

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List, Tuple, Optional, Any

# Import del sistema base
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import (
    BacktestConfig, The5ersRules, WorkingBacktestEngine
)

def get_optimized_the5ers_config():
    """Configurazione ottimizzata basata sui risultati dell'ottimizzazione"""
    
    # Migliori parametri trovati dall'ottimizzazione
    optimized_config = {
        "quantum_params": {
            # Parametri ottimizzati per trading aggressivo ma controllato
            "entropy_threshold": 0.7,      # Selettivo sui segnali
            "coherence_threshold": 0.4,    # Permette più opportunità  
            "entanglement_strength": 1.6,  # Segnali frequenti e forti
            "buffer_size": 25,             # Buffer medio per stabilità
            "quantum_noise_factor": 0.15,  # Rumore controllato
            "decoherence_rate": 0.05       # Bassa decoerenza
        },
        
        "risk_parameters": {
            # Risk management ottimizzato per The5ers
            "max_risk_per_trade": 2.5,         # Rischio bilanciato per crescita
            "trailing_stop_pips": 20,          # Stop loss aggressivo
            "take_profit_ratio": 2.5,          # TP ratio equilibrato
            "position_cooldown_minutes": 20,   # Cooldown moderato
            "max_daily_loss_pct": 4.5,         # Sotto limite The5ers (5%)
            "max_total_loss_pct": 9.0,         # Sotto limite The5ers (10%)
            "risk_scaling_factor": 0.8         # Scaling conservativo
        },
        
        "trading_parameters": {
            # Parametri trading ottimizzati
            "min_confidence": 0.4,             # Confidence minima abbassata
            "max_positions": 3,                # Multi-position per opportunità
            "correlation_threshold": 0.7,      # Evita correlazioni eccessive
            "news_impact_hours": 2,            # Pausa durante news
            "session_preferences": {
                "london": 0.4,   # Sessione principale
                "new_york": 0.3, # Seconda scelta
                "asian": 0.2,    # Meno attiva
                "overlap": 0.5   # Sovrapposizioni migliori
            }
        },
        
        "symbols": {
            # Simboli ottimizzati per The5ers Challenge
            "EURUSD": {
                "enabled": True,
                "risk_multiplier": 1.0,
                "min_spread": 1.5,
                "quantum_sensitivity": 1.0
            },
            "GBPUSD": {
                "enabled": True, 
                "risk_multiplier": 1.1,  # Slightly higher risk for higher volatility
                "min_spread": 2.0,
                "quantum_sensitivity": 1.2
            },
            "XAUUSD": {
                "enabled": True,
                "risk_multiplier": 0.8,   # Lower risk for gold
                "min_spread": 3.0,
                "quantum_sensitivity": 0.9
            },
            "USDJPY": {
                "enabled": False,  # Disabilitato per focus
                "risk_multiplier": 1.0,
                "min_spread": 1.5,
                "quantum_sensitivity": 1.0
            }
        },
        
        "the5ers_specific": {
            # Configurazioni specifiche per The5ers Challenge
            "target_step1": 8.0,              # 8% per Step 1
            "target_step2": 5.0,              # 5% per Step 2  
            "target_scaling": 10.0,           # 10% per Scaling
            "daily_loss_limit": 5.0,          # 5% daily loss limit
            "total_loss_limit": 10.0,         # 10% total loss limit
            "minimum_trading_days": 5,        # Minimo 5 giorni di trading
            "profit_consistency_target": 0.6   # 60% giorni profittevoli
        }
    }
    
    return optimized_config

class OptimizedThe5ersSystem:
    """Sistema completo ottimizzato per The5ers Challenge"""
    
    def __init__(self):
        self.config = get_optimized_the5ers_config()
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 OPTIMIZED THE5ERS SYSTEM INITIALIZED")
    
    def run_step1_simulation(self, days: int = 10) -> Dict[str, Any]:
        """Simula Step 1 Challenge (target 8%)"""
        
        print("🎯 THE5ERS STEP 1 CHALLENGE SIMULATION")
        print("="*50)
        print("📊 Target: 8% profit in maximum 30 days")
        print("⚠️  Risk Limits: 5% daily loss, 10% total loss")
        
        # Configurazione backtest per Step 1
        backtest_config = BacktestConfig(
            start_date="2024-01-01",
            end_date=(datetime(2024, 1, 1) + timedelta(days=days)).strftime("%Y-%m-%d"),
            initial_balance=100000,  # $100k account
            symbols=["EURUSD", "GBPUSD", "XAUUSD"],
            timeframe="M15"
        )
        
        the5ers_rules = The5ersRules(
            daily_loss_limit=5.0,
            total_loss_limit=10.0,
            profit_target=8.0,
            minimum_trading_days=5
        )
        
        # Esegui backtest con configurazione ottimizzata
        engine = WorkingBacktestEngine(self.config, backtest_config, the5ers_rules)
        results = engine.run_backtest()
        
        # Analisi risultati Step 1
        self.analyze_step1_results(results)
        
        return results
    
    def run_step2_simulation(self, days: int = 10) -> Dict[str, Any]:
        """Simula Step 2 Challenge (target 5%)"""
        
        print("🎯 THE5ERS STEP 2 CHALLENGE SIMULATION") 
        print("="*50)
        print("📊 Target: 5% profit in maximum 60 days")
        print("⚠️  Risk Limits: 5% daily loss, 10% total loss")
        
        # Configurazione per Step 2 (più conservativa)
        step2_config = self.config.copy()
        step2_config['risk_parameters']['max_risk_per_trade'] = 2.0  # Più conservativo
        step2_config['quantum_params']['entropy_threshold'] = 0.8   # Più selettivo
        
        backtest_config = BacktestConfig(
            start_date="2024-02-01", 
            end_date=(datetime(2024, 2, 1) + timedelta(days=days)).strftime("%Y-%m-%d"),
            initial_balance=100000,
            symbols=["EURUSD", "GBPUSD", "XAUUSD"],
            timeframe="M15"
        )
        
        the5ers_rules = The5ersRules(
            daily_loss_limit=5.0,
            total_loss_limit=10.0,
            profit_target=5.0,
            minimum_trading_days=5
        )
        
        engine = WorkingBacktestEngine(step2_config, backtest_config, the5ers_rules)
        results = engine.run_backtest()
        
        self.analyze_step2_results(results)
        
        return results
    
    def run_scaling_simulation(self, days: int = 15) -> Dict[str, Any]:
        """Simula Scaling Phase (target 10%)"""
        
        print("🎯 THE5ERS SCALING PHASE SIMULATION")
        print("="*50)
        print("📊 Target: 10% profit per month")
        print("⚠️  Risk Limits: 5% daily loss, 10% total loss")
        
        # Configurazione per Scaling (più aggressiva)
        scaling_config = self.config.copy()
        scaling_config['risk_parameters']['max_risk_per_trade'] = 3.0  # Più aggressivo
        scaling_config['quantum_params']['entropy_threshold'] = 0.6   # Meno selettivo
        scaling_config['quantum_params']['entanglement_strength'] = 2.0  # Più forte
        
        backtest_config = BacktestConfig(
            start_date="2024-03-01",
            end_date=(datetime(2024, 3, 1) + timedelta(days=days)).strftime("%Y-%m-%d"),
            initial_balance=100000,
            symbols=["EURUSD", "GBPUSD", "XAUUSD"],
            timeframe="M15"
        )
        
        the5ers_rules = The5ersRules(
            daily_loss_limit=5.0,
            total_loss_limit=10.0,
            profit_target=10.0,
            minimum_trading_days=8
        )
        
        engine = WorkingBacktestEngine(scaling_config, backtest_config, the5ers_rules)
        results = engine.run_backtest()
        
        self.analyze_scaling_results(results)
        
        return results
    
    def analyze_step1_results(self, results: Dict[str, Any]):
        """Analizza risultati Step 1"""
        
        print(f"\n📊 STEP 1 CHALLENGE RESULTS:")
        print(f"="*40)
        
        compliance = results['the5ers_compliance']
        
        print(f"💰 Return: {results['total_return_pct']:.2f}% (target: 8.0%)")
        print(f"📉 Max Drawdown: {results['max_drawdown']:.2f}% (limit: 10.0%)")
        print(f"🎯 Win Rate: {results['win_rate']:.1f}%")
        print(f"🔢 Total Trades: {results['total_trades']}")
        print(f"💵 Profitable Days: {results['profitable_days']}")
        
        # The5ers Compliance
        print(f"\n🏆 THE5ERS COMPLIANCE:")
        target = "✅ PASSED" if compliance['step1_achieved'] else "❌ FAILED"
        daily_loss = "✅ OK" if not compliance['daily_loss_violated'] else "❌ VIOLATED"
        total_loss = "✅ OK" if not compliance['total_loss_violated'] else "❌ VIOLATED"
        
        print(f"   Target Achievement: {target}")
        print(f"   Daily Loss Control: {daily_loss}")
        print(f"   Total Loss Control: {total_loss}")
        
        # Verdetto finale
        if compliance['step1_achieved'] and not compliance['daily_loss_violated'] and not compliance['total_loss_violated']:
            print(f"\n🎉 STEP 1 CHALLENGE: ✅ PASSED!")
            print(f"🚀 Ready to proceed to Step 2!")
        else:
            print(f"\n⚠️  STEP 1 CHALLENGE: ❌ FAILED")
            if not compliance['step1_achieved']:
                print(f"   - Target not reached ({results['total_return_pct']:.2f}% < 8.0%)")
            if compliance['daily_loss_violated']:
                print(f"   - Daily loss limit violated")
            if compliance['total_loss_violated']:
                print(f"   - Total loss limit violated")
    
    def analyze_step2_results(self, results: Dict[str, Any]):
        """Analizza risultati Step 2"""
        
        print(f"\n📊 STEP 2 CHALLENGE RESULTS:")
        print(f"="*40)
        
        compliance = results['the5ers_compliance']
        
        print(f"💰 Return: {results['total_return_pct']:.2f}% (target: 5.0%)")
        print(f"📉 Max Drawdown: {results['max_drawdown']:.2f}% (limit: 10.0%)")
        print(f"🎯 Win Rate: {results['win_rate']:.1f}%")
        print(f"🔢 Total Trades: {results['total_trades']}")
        
        # Verdetto
        if compliance['step2_achieved'] and not compliance['daily_loss_violated'] and not compliance['total_loss_violated']:
            print(f"\n🎉 STEP 2 CHALLENGE: ✅ PASSED!")
            print(f"🚀 Ready for Scaling Phase!")
        else:
            print(f"\n⚠️  STEP 2 CHALLENGE: ❌ FAILED")
    
    def analyze_scaling_results(self, results: Dict[str, Any]):
        """Analizza risultati Scaling"""
        
        print(f"\n📊 SCALING PHASE RESULTS:")
        print(f"="*40)
        
        compliance = results['the5ers_compliance']
        
        print(f"💰 Return: {results['total_return_pct']:.2f}% (target: 10.0%)")
        print(f"📉 Max Drawdown: {results['max_drawdown']:.2f}% (limit: 10.0%)")
        print(f"🎯 Win Rate: {results['win_rate']:.1f}%")
        print(f"🔢 Total Trades: {results['total_trades']}")
        
        # Verdetto
        if compliance['scaling_achieved'] and not compliance['daily_loss_violated'] and not compliance['total_loss_violated']:
            print(f"\n🎉 SCALING PHASE: ✅ PASSED!")
            print(f"🏆 Ready for live The5ers funding!")
        else:
            print(f"\n⚠️  SCALING PHASE: ❌ FAILED")
    
    def run_complete_challenge_simulation(self):
        """Simula l'intero percorso The5ers Challenge"""
        
        print("🏆 THE5ERS COMPLETE CHALLENGE SIMULATION")
        print("="*60)
        print("🎯 Testing full pathway: Step 1 → Step 2 → Scaling")
        
        # Step 1
        print(f"\n" + "="*20 + " STEP 1 " + "="*20)
        step1_results = self.run_step1_simulation(days=8)
        
        # Step 2  
        print(f"\n" + "="*20 + " STEP 2 " + "="*20)
        step2_results = self.run_step2_simulation(days=8)
        
        # Scaling
        print(f"\n" + "="*20 + " SCALING " + "="*19)
        scaling_results = self.run_scaling_simulation(days=10)
        
        # Risultato finale
        step1_pass = (step1_results['the5ers_compliance']['step1_achieved'] and 
                     not step1_results['the5ers_compliance']['daily_loss_violated'] and
                     not step1_results['the5ers_compliance']['total_loss_violated'])
        
        step2_pass = (step2_results['the5ers_compliance']['step2_achieved'] and
                     not step2_results['the5ers_compliance']['daily_loss_violated'] and
                     not step2_results['the5ers_compliance']['total_loss_violated'])
        
        scaling_pass = (scaling_results['the5ers_compliance']['scaling_achieved'] and
                       not scaling_results['the5ers_compliance']['daily_loss_violated'] and
                       not scaling_results['the5ers_compliance']['total_loss_violated'])
        
        print(f"\n" + "="*60)
        print(f"🏆 FINAL THE5ERS CHALLENGE RESULTS")
        print(f"="*60)
        
        print(f"📊 Step 1: {'✅ PASSED' if step1_pass else '❌ FAILED'} ({step1_results['total_return_pct']:.2f}%)")
        print(f"📊 Step 2: {'✅ PASSED' if step2_pass else '❌ FAILED'} ({step2_results['total_return_pct']:.2f}%)")
        print(f"📊 Scaling: {'✅ PASSED' if scaling_pass else '❌ FAILED'} ({scaling_results['total_return_pct']:.2f}%)")
        
        overall_pass = step1_pass and step2_pass and scaling_pass
        
        if overall_pass:
            print(f"\n🎉 THE5ERS CHALLENGE: ✅ COMPLETE SUCCESS!")
            print(f"🏆 System ready for live trading with The5ers funding!")
        else:
            print(f"\n⚠️  THE5ERS CHALLENGE: ❌ PARTIAL SUCCESS")
            print(f"🔧 System needs optimization for failed stages")
        
        return {
            'step1': step1_results,
            'step2': step2_results, 
            'scaling': scaling_results,
            'overall_success': overall_pass
        }

def run_optimized_system():
    """Esegue il sistema ottimizzato completo"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    system = OptimizedThe5ersSystem()
    
    print("🚀 STARTING OPTIMIZED THE5ERS SYSTEM")
    print("🔧 Using parameters optimized through automated testing")
    print("="*60)
    
    # Mostra configurazione ottimizzata
    config = system.config
    print(f"\n🔧 OPTIMIZED PARAMETERS:")
    print(f"   Entropy Threshold: {config['quantum_params']['entropy_threshold']}")
    print(f"   Coherence Threshold: {config['quantum_params']['coherence_threshold']}")
    print(f"   Entanglement Strength: {config['quantum_params']['entanglement_strength']}")
    print(f"   Max Risk per Trade: {config['risk_parameters']['max_risk_per_trade']}%")
    print(f"   Trailing Stop: {config['risk_parameters']['trailing_stop_pips']} pips")
    print(f"   Take Profit Ratio: {config['risk_parameters']['take_profit_ratio']}")
    
    try:
        # Esegui simulazione completa
        results = system.run_complete_challenge_simulation()
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = run_optimized_system()
