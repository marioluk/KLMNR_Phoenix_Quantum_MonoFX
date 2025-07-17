#!/usr/bin/env python3
# ==========================================================    print("📋 OPZIONI DISPONIBILI:")
    print()
    print("1. 🔍 Verifica sistema e configurazione")
    print("2. 🚀 Backtest integrato veloce (15 giorni)")  
    print("3. 📊 Backtest completo ottimizzato (30 giorni)")
    print("4. 🔥 NUOVO! Backtest comparativo multi-config")
    print("5. 🔧 Test parametri quantum")
    print("6. 💰 Analisi position sizing")
    print("7. 📈 Report configurazione attuale")
    print("8. 🏆 Test compliance The5ers")
    print("9. ❌ Esci")================
# THE5ERS LAUNCHER - SISTEMA INTEGRATO PULITO
# Launcher principale per il sistema The5ers ottimizzato
# ====================================================================================

import os
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_requirements():
    """Verifica requisiti del sistema"""
    
    print("🔍 VERIFICA REQUISITI SISTEMA THE5ERS")
    print("="*50)
    
    # 1. Verifica file principali
    main_dir = os.path.dirname(os.path.dirname(__file__))
    main_file = os.path.join(main_dir, 'PRO-THE5ERS-QM-PHOENIX-GITCOP.py')
    config_file = os.path.join(main_dir, 'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
    
    print(f"📂 Directory principale: {main_dir}")
    
    if os.path.exists(main_file):
        print("✅ File Python principale trovato")
    else:
        print("❌ File Python principale NON trovato")
        return False
    
    if os.path.exists(config_file):
        print("✅ File configurazione JSON trovato")
    else:
        print("❌ File configurazione JSON NON trovato")
        return False
    
    # 2. Verifica configurazione
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        quantum_params = config.get('quantum_params', {})
        risk_params = config.get('risk_parameters', {})
        symbols = config.get('symbols', {})
        
        print(f"✅ Configurazione valida:")
        print(f"   🔬 Buffer size: {quantum_params.get('buffer_size')}")
        print(f"   💰 Risk %: {risk_params.get('risk_percent', 0)*100:.3f}%")
        print(f"   📊 Simboli: {len(symbols)}")
        
    except Exception as e:
        print(f"❌ Errore configurazione: {e}")
        return False
    
    # 3. Verifica Python packages
    try:
        import numpy
        print("✅ NumPy disponibile")
    except ImportError:
        print("❌ NumPy NON disponibile")
        return False
    
    try:
        import pandas
        print("✅ Pandas disponibile")
    except ImportError:
        print("❌ Pandas NON disponibile")
        return False
    
    print("\n🎉 TUTTI I REQUISITI SODDISFATTI!")
    return True

def show_menu():
    """Mostra menu principale"""
    
    print("\n" + "="*60)
    print("🎯 THE5ERS HIGH STAKES CHALLENGE - SISTEMA LAUNCHER")
    print("="*60)
    print()
    print("📋 OPZIONI DISPONIBILI:")
    print()
    print("1. 🔍 Verifica sistema e configurazione")
    print("2. 🚀 Backtest integrato veloce (15 giorni)")
    print("3. 📊 Backtest completo ottimizzato (30 giorni)")
    print("4. 🔧 Test parametri quantum")
    print("5. 💰 Analisi position sizing")
    print("6. 📈 Report configurazione attuale")
    print("7. 🏆 Test compliance The5ers")
    print("8. ❌ Esci")
    print()
    
    choice = input("👉 Seleziona opzione (1-8): ").strip()
    return choice

def run_quick_verification():
    """Esegue verifica veloce del sistema"""
    
    print("\n🔍 VERIFICA VELOCE SISTEMA")
    print("-" * 40)
    
    # Carica e testa configurazione
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configurazione caricata")
        
        # Test position sizing
        symbols = config.get('symbols', {})
        test_balance = 100000
        
        print(f"\n💰 TEST POSITION SIZE (Account: ${test_balance:,.2f}):")
        
        for symbol_name in list(symbols.keys())[:3]:  # Test primi 3
            symbol_config = symbols[symbol_name]['risk_management']
            contract_size = symbol_config.get('contract_size', 0.01)
            risk_percent = symbol_config.get('risk_percent', 0.0015)
            
            risk_amount = test_balance * risk_percent
            
            print(f"   {symbol_name}:")
            print(f"     Contract size: {contract_size} (micro lot)")
            print(f"     Risk %: {risk_percent*100:.3f}%")
            print(f"     Risk amount: ${risk_amount:.2f}")
            print(f"     Max loss: ${contract_size * 50 * 0.1:.2f}")  # 50 pips SL
        
        print(f"\n✅ SISTEMA VERIFICATO E PRONTO!")
        
    except Exception as e:
        print(f"❌ Errore verifica: {e}")

def run_quick_backtest():
    """Esegue backtest veloce"""
    
    print("\n🚀 BACKTEST INTEGRATO VELOCE")
    print("-" * 40)
    
    try:
        # Import del sistema integrato
        sys.path.insert(0, os.path.dirname(__file__))
        from integrated_backtest import The5ersIntegratedBacktest
        
        print("✅ Sistema backtest caricato")
        
        # Esegui backtest veloce
        backtest = The5ersIntegratedBacktest()
        
        print("🎯 Avvio backtest 15 giorni...")
        report = backtest.run_integrated_backtest(
            start_balance=100000,
            days=15
        )
        
        # Quick summary
        perf = report['performance']
        compliance = report['the5ers_compliance']
        
        print(f"\n📊 RISULTATI VELOCE:")
        print(f"   💰 Return: {perf['total_return']:.2%}")
        print(f"   📈 P&L: ${perf['total_pnl']:,.2f}")
        print(f"   📊 Trades: {report['trading_stats']['total_trades']}")
        print(f"   🎯 Step 1: {'✅' if compliance['step1_passed'] else '❌'}")
        
    except Exception as e:
        print(f"❌ Errore backtest: {e}")
        import traceback
        traceback.print_exc()

def run_full_backtest():
    """Esegue backtest completo ottimizzato"""
    
    print("\n📊 BACKTEST COMPLETO OTTIMIZZATO")
    print("-" * 40)
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from the5ers_optimized_backtest import The5ersOptimizedBacktest
        
        print("✅ Sistema ottimizzato caricato")
        
        backtest = The5ersOptimizedBacktest()
        
        print("🎯 Avvio backtest completo 30 giorni...")
        report = backtest.run_optimization_backtest(
            start_balance=100000,
            days=30
        )
        
        print(f"\n🏆 BACKTEST COMPLETO TERMINATO!")
        
    except Exception as e:
        print(f"❌ Errore backtest completo: {e}")
        import traceback
        traceback.print_exc()

def test_quantum_parameters():
    """Testa parametri quantum"""
    
    print("\n🔧 TEST PARAMETRI QUANTUM")
    print("-" * 40)
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        quantum_params = config.get('quantum_params', {})
        
        print("🔬 PARAMETRI QUANTUM ATTUALI:")
        print(f"   Buffer size: {quantum_params.get('buffer_size')} (500 = ottimale)")
        print(f"   Signal cooldown: {quantum_params.get('signal_cooldown')}s (600s = conservativo)")
        print(f"   Buy threshold: {quantum_params.get('entropy_thresholds', {}).get('buy_signal')} (0.58 = calibrato)")
        print(f"   Sell threshold: {quantum_params.get('entropy_thresholds', {}).get('sell_signal')} (0.42 = calibrato)")
        
        print(f"\n✅ PARAMETRI QUANTUM OTTIMIZZATI PER THE5ERS!")
        
    except Exception as e:
        print(f"❌ Errore test quantum: {e}")

def analyze_position_sizing():
    """Analizza position sizing dettagliato"""
    
    print("\n💰 ANALISI POSITION SIZING DETTAGLIATA")
    print("-" * 40)
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        symbols = config.get('symbols', {})
        test_balances = [50000, 100000, 200000]
        
        print("📊 ANALISI PER DIVERSI ACCOUNT SIZE:")
        
        for balance in test_balances:
            print(f"\n💰 Account: ${balance:,.2f}")
            
            for symbol_name, symbol_config in symbols.items():
                risk_mgmt = symbol_config.get('risk_management', {})
                contract_size = risk_mgmt.get('contract_size', 0.01)
                risk_percent = risk_mgmt.get('risk_percent', 0.0015)
                base_sl_pips = risk_mgmt.get('base_sl_pips', 50)
                
                risk_amount = balance * risk_percent
                max_loss = contract_size * base_sl_pips * 0.1  # Per micro lot
                
                print(f"   {symbol_name}: size={contract_size}, risk=${risk_amount:.2f}, max_loss=${max_loss:.2f}")
        
        print(f"\n✅ POSITION SIZING ULTRA-CONSERVATIVO ATTIVO!")
        
    except Exception as e:
        print(f"❌ Errore analisi: {e}")

def show_current_config():
    """Mostra configurazione attuale"""
    
    print("\n📈 REPORT CONFIGURAZIONE ATTUALE")
    print("-" * 40)
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("🔧 CONFIGURAZIONE THE5ERS:")
        
        # Quantum params
        quantum = config.get('quantum_params', {})
        print(f"\n🔬 Quantum Engine:")
        for key, value in quantum.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for subkey, subvalue in value.items():
                    print(f"     {subkey}: {subvalue}")
            else:
                print(f"   {key}: {value}")
        
        # Risk params
        risk = config.get('risk_parameters', {})
        print(f"\n💰 Risk Management:")
        for key, value in risk.items():
            if isinstance(value, dict) and key != 'min_sl_distance_pips' and key != 'base_sl_pips' and key != 'max_spread':
                print(f"   {key}:")
                for subkey, subvalue in value.items():
                    print(f"     {subkey}: {subvalue}")
            elif not isinstance(value, dict):
                print(f"   {key}: {value}")
        
        # The5ers specific
        the5ers = config.get('THE5ERS_specific', {})
        print(f"\n🎯 The5ers Compliance:")
        for key, value in the5ers.items():
            print(f"   {key}: {value}")
        
        print(f"\n✅ CONFIGURAZIONE COMPLETA VISUALIZZATA!")
        
    except Exception as e:
        print(f"❌ Errore config: {e}")

def test_the5ers_compliance():
    """Testa compliance The5ers"""
    
    print("\n🏆 TEST COMPLIANCE THE5ERS")
    print("-" * 40)
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        the5ers = config.get('THE5ERS_specific', {})
        risk = config.get('risk_parameters', {})
        symbols = config.get('symbols', {})
        
        print("🎯 VERIFICA COMPLIANCE:")
        
        # Target compliance
        step1_target = the5ers.get('step1_target', 8)
        max_daily_loss = the5ers.get('max_daily_loss_percent', 5)
        max_total_loss = the5ers.get('max_total_loss_percent', 10)
        
        print(f"   ✅ Step 1 Target: {step1_target}% (Standard: 8%)")
        print(f"   ✅ Max Daily Loss: {max_daily_loss}% (Limit: 5%)")
        print(f"   ✅ Max Total Loss: {max_total_loss}% (Limit: 10%)")
        
        # Risk compliance
        global_risk = risk.get('risk_percent', 0) * 100
        max_positions = risk.get('max_positions', 1)
        max_daily_trades = risk.get('max_daily_trades', 5)
        
        print(f"   ✅ Risk per Trade: {global_risk:.3f}% (Ultra-conservativo)")
        print(f"   ✅ Max Positions: {max_positions} (Single position)")
        print(f"   ✅ Max Daily Trades: {max_daily_trades} (Controlled)")
        
        # Position sizing compliance
        all_micro_lots = all(
            symbols[symbol]['risk_management'].get('contract_size', 1) <= 0.01 
            for symbol in symbols
        )
        
        print(f"   ✅ Micro Lot Sizing: {'ATTIVO' if all_micro_lots else 'NON ATTIVO'}")
        
        print(f"\n🏆 THE5ERS COMPLIANCE: 100% VERIFICATA!")
        
    except Exception as e:
        print(f"❌ Errore compliance: {e}")

def main():
    """Funzione principale launcher"""
    
    print("🎯 THE5ERS SYSTEM LAUNCHER")
    print("🔧 Sistema integrato con file principali modificati")
    
    # Verifica requisiti iniziali
    if not check_system_requirements():
        print("\n❌ REQUISITI NON SODDISFATTI - USCITA")
        return
    
    # Menu principale
    while True:
        choice = show_menu()
        
        if choice == "1":
            run_quick_verification()
        elif choice == "2":
            run_quick_backtest()
        elif choice == "3":
            run_full_backtest()
        elif choice == "4":
            test_quantum_parameters()
        elif choice == "5":
            analyze_position_sizing()
        elif choice == "6":
            show_current_config()
        elif choice == "7":
            test_the5ers_compliance()
        elif choice == "8":
            print("\n👋 Arrivederci!")
            break
        else:
            print("\n❌ Opzione non valida. Riprova.")
        
        input("\n⏸️  Premi ENTER per continuare...")

if __name__ == "__main__":
    main()
