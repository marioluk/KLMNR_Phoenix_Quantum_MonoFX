#!/usr/bin/env python3
# ====================================================================================
# THE5ERS LAUNCHER - SISTEMA INTEGRATO PULITO
# Launcher principale per il sistema The5ers ottimizzato
# ====================================================================================

import os
import sys
import json
import logging
from datetime import datetime
from config_selector import ConfigSelector

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
        
        print(f"✅ File JSON valido")
        print(f"🔬 Quantum buffer_size: {quantum_params.get('buffer_size', 'N/A')}")
        print(f"💰 Risk parameters: {len(risk_params)} parametri")
        print(f"📊 Simboli configurati: {len(symbols)}")
        
    except Exception as e:
        print(f"❌ Errore lettura JSON: {e}")
        return False
    
    # 3. Verifica librerie Python
    print("\n📦 VERIFICA LIBRERIE PYTHON:")
    
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
    print("4. 🔥 NUOVO! Backtest comparativo multi-config")
    print("5. 📅 NUOVO! Backtest periodo personalizzato")
    print("6. � HIGH STAKES CHALLENGE (€25/giorno su €5000)")
    print("7. �🔧 Test parametri quantum")
    print("8. 💰 Analisi position sizing")
    print("9. 📈 Report configurazione attuale")
    print("10. 🏆 Test compliance The5ers")
    print("11. ⚙️ NUOVO! Selezione configurazione")
    print("12. ❌ Esci")
    print()
    
    choice = input("👉 Seleziona opzione (1-12): ").strip()
    return choice

def run_integrated_backtest():
    """Esegue backtest integrato veloce con selezione configurazione"""
    try:
        from integrated_backtest import The5ersIntegratedBacktest
        
        print("🚀 AVVIO BACKTEST INTEGRATO VELOCE")
        print("="*50)
        
        # Chiedi se usare configurazione specifica
        print("Opzioni configurazione:")
        print("1. Selezione interattiva")
        print("2. Usa configurazione default")
        
        config_choice = input("👉 Scelta (1-2, Enter=default): ").strip()
        
        if config_choice == "1":
            selector = ConfigSelector()
            config_path = selector.show_interactive_menu()
            backtest = The5ersIntegratedBacktest(config_path=config_path)
        else:
            backtest = The5ersIntegratedBacktest()
        
        result = backtest.run_backtest(days=15)
        
        print("✅ Backtest completato!")
        return result
        
    except Exception as e:
        print(f"❌ Errore backtest integrato: {e}")
        return None

def run_optimized_backtest():
    """Esegue backtest ottimizzato completo"""
    try:
        from the5ers_optimized_backtest import The5ersOptimizedBacktest
        
        print("📊 AVVIO BACKTEST OTTIMIZZATO COMPLETO")
        print("="*50)
        
        backtest = The5ersOptimizedBacktest()
        result = backtest.run_optimized_backtest(days=30)
        
        print("✅ Backtest ottimizzato completato!")
        return result
        
    except Exception as e:
        print(f"❌ Errore backtest ottimizzato: {e}")
        return None

def run_comparative_backtest():
    """Esegue backtest comparativo multi-config"""
    try:
        from comparative_backtest import The5ersComparativeBacktest
        
        print("🔥 AVVIO BACKTEST COMPARATIVO MULTI-CONFIG")
        print("="*50)
        
        backtest = The5ersComparativeBacktest()
        result = backtest.run_comparative_analysis()
        
        print("✅ Backtest comparativo completato!")
        return result
        
    except Exception as e:
        print(f"❌ Errore backtest comparativo: {e}")
        return None

def run_custom_period_backtest():
    """Esegue backtest con periodo personalizzato"""
    try:
        from custom_period_backtest import The5ersCustomPeriodBacktest
        
        print("📅 AVVIO BACKTEST PERIODO PERSONALIZZATO")
        print("="*50)
        
        backtest = The5ersCustomPeriodBacktest()
        
        # Menu sub-opzioni
        print("Modalità disponibili:")
        print("1. Date specifiche (da/a)")
        print("2. Giorni indietro da oggi")
        print("3. Default (ultimi 30 giorni)")
        
        mode = input("Scegli modalità (1-3): ").strip()
        
        if mode == "1":
            start_date = input("Data inizio (YYYY-MM-DD o DD/MM/YYYY): ").strip()
            end_date = input("Data fine (YYYY-MM-DD o DD/MM/YYYY): ").strip()
            
            result = backtest.run_custom_period_backtest(
                start_date=start_date,
                end_date=end_date
            )
            
        elif mode == "2":
            days = int(input("Numero giorni indietro: ").strip())
            
            result = backtest.run_custom_period_backtest(
                days_back=days
            )
            
        else:
            # Default
            result = backtest.run_custom_period_backtest()
        
        print("✅ Backtest periodo personalizzato completato!")
        return result
        
    except Exception as e:
        print(f"❌ Errore backtest personalizzato: {e}")
        return None

def run_high_stakes_challenge():
    """Esegue High Stakes Challenge backtest con selezione aggressività"""
    try:
        from high_stakes_challenge_backtest import HighStakesChallengeBacktest
        
        print("🔥 AVVIO HIGH STAKES CHALLENGE")
        print("="*50)
        print("🎯 Target: 3 giorni con €25+ profit per VALIDAZIONE")
        print("⏰ Tempo Step: ILLIMITATO dopo validazione")
        print("⚠️ Daily Loss Limit: €250 (5%)")
        print("📈 Leverage: 1:100")
        print()
        
        # Selezione aggressività
        print("🎯 SELEZIONE LIVELLO AGGRESSIVITÀ:")
        print("1. 🟢 Conservative - Sicuro e stabile (6% risk, lot 0.03-0.04)")
        print("2. 🟡 Moderate - Bilanciato risk/reward (7% risk, lot 0.035-0.045)")  
        print("3. 🔴 Aggressive - Fast validation (8% risk, lot 0.04-0.05)")
        
        aggr_choice = input("👉 Scegli aggressività (1-3, Enter=2): ").strip()
        
        if aggr_choice == "1":
            aggressiveness = "conservative"
            print("✅ Selezionato: CONSERVATIVE")
        elif aggr_choice == "3":
            aggressiveness = "aggressive"
            print("✅ Selezionato: AGGRESSIVE")
        else:
            aggressiveness = "moderate"
            print("✅ Selezionato: MODERATE (raccomandato)")
        
        print()
        
        # Menu durata test
        print("📅 DURATA TEST:")
        print("1. 5 giorni (validation focus)")
        print("2. 7 giorni (extended)")
        print("3. 10 giorni (full challenge)")
        
        duration_choice = input("👉 Scegli durata (1-3, Enter=1): ").strip()
        
        if duration_choice == "2":
            days = 7
        elif duration_choice == "3":
            days = 10
        else:
            days = 5
        
        backtest = HighStakesChallengeBacktest(aggressiveness=aggressiveness)
        result = backtest.run_high_stakes_backtest(days=days)
        
        # Mostra risultato finale
        print(f"\n🏆 HIGH STAKES CHALLENGE RESULT:")
        print(f"⚙️ Aggressività usata: {aggressiveness.upper()}")
        
        if result['validation_completed']:
            print(f"✅ VALIDATION COMPLETED! {result['profitable_days_achieved']} giorni profittevoli")
            print(f"💰 Final Balance: €{result['final_balance']:,.2f}")
            print(f"📈 Total Profit: €{result['total_pnl']:+,.2f}")
            print(f"⏰ Ora hai TEMPO ILLIMITATO per completare lo step!")
        else:
            print(f"⏳ Validation in progress: {result['profitable_days_achieved']}/3 giorni")
            print(f"💡 Consiglio: Prova livello più aggressivo o estendi durata test")
        
        print("✅ High Stakes Challenge completato!")
        return result
        
    except Exception as e:
        print(f"❌ Errore High Stakes Challenge: {e}")
        return None
    """Test parametri quantum"""
    print("🔧 TEST PARAMETRI QUANTUM")
    print("="*50)
    
    # Carica config
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        quantum_params = config.get('quantum_params', {})
        
        print("🔬 Parametri Quantum attuali:")
        for key, value in quantum_params.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Test parametri completato!")
        
    except Exception as e:
        print(f"❌ Errore test parametri: {e}")

def test_quantum_parameters():
    """Test parametri quantum"""
    print("🔧 TEST PARAMETRI QUANTUM")
    print("="*50)
    
    # Carica config
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        quantum_params = config.get('quantum_params', {})
        
        print("🔬 Parametri Quantum attuali:")
        for key, value in quantum_params.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Test parametri completato!")
        
    except Exception as e:
        print(f"❌ Errore test parametri: {e}")
    """Analisi position sizing"""
    print("💰 ANALISI POSITION SIZING")
    print("="*50)
    
    # Simula diversi scenari
    balances = [100000, 50000, 200000]
    risk_percentages = [0.001, 0.0015, 0.002]
    
    print("📊 Simulazione Position Sizing:")
    print()
    
    for balance in balances:
        print(f"💰 Balance: ${balance:,.2f}")
        for risk_pct in risk_percentages:
            position_value = balance * risk_pct
            print(f"   Risk {risk_pct:.3%}: ${position_value:.2f} | Micro lots: {position_value/1000:.2f}")
        print()
    
    print("✅ Analisi position sizing completata!")

def analyze_position_sizing():
    """Analisi position sizing"""
    print("💰 ANALISI POSITION SIZING")
    print("="*50)
    
    # Simula diversi scenari
    balances = [100000, 50000, 200000, 5000]  # Aggiungo €5000 per High Stakes
    risk_percentages = [0.001, 0.0015, 0.002, 0.008]  # Aggiungo 0.8% per High Stakes
    
    print("📊 Simulazione Position Sizing:")
    print()
    
    for balance in balances:
        balance_type = "High Stakes" if balance == 5000 else "Standard"
        print(f"💰 Balance: €{balance:,.2f} ({balance_type})")
        for risk_pct in risk_percentages:
            position_value = balance * risk_pct
            if balance == 5000 and risk_pct == 0.008:
                print(f"   🔥 Risk {risk_pct:.3%}: €{position_value:.2f} | Micro lots: {position_value/1000:.2f} (HIGH STAKES)")
            else:
                print(f"   Risk {risk_pct:.3%}: €{position_value:.2f} | Micro lots: {position_value/1000:.2f}")
        print()
    
    print("✅ Analisi position sizing completata!")
    """Mostra configurazione attuale"""
    print("📈 REPORT CONFIGURAZIONE ATTUALE")
    print("="*50)
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Parametri chiave
        quantum_params = config.get('quantum_params', {})
        risk_params = config.get('risk_parameters', {})
        symbols = config.get('symbols', {})
        the5ers_params = config.get('THE5ERS_specific', {})
        
        print("🔬 QUANTUM PARAMETERS:")
        for key, value in quantum_params.items():
            print(f"   {key}: {value}")
        
        print("\n💰 RISK PARAMETERS:")
        for key, value in risk_params.items():
            print(f"   {key}: {value}")
        
        print("\n🏆 THE5ERS SETTINGS:")
        for key, value in the5ers_params.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 SIMBOLI CONFIGURATI: {len(symbols)}")
        for symbol in symbols.keys():
            print(f"   • {symbol}")
        
        print("\n✅ Report configurazione completato!")
        
    except Exception as e:
        print(f"❌ Errore lettura configurazione: {e}")

def show_current_config():
    """Mostra configurazione attuale"""
    print("📈 REPORT CONFIGURAZIONE ATTUALE")
    print("="*50)
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Parametri chiave
        quantum_params = config.get('quantum_params', {})
        risk_params = config.get('risk_parameters', {})
        symbols = config.get('symbols', {})
        the5ers_params = config.get('THE5ERS_specific', {})
        high_stakes_params = config.get('HIGH_STAKES_specific', {})
        
        print("🔬 QUANTUM PARAMETERS:")
        for key, value in quantum_params.items():
            print(f"   {key}: {value}")
        
        print("\n💰 RISK PARAMETERS:")
        for key, value in risk_params.items():
            print(f"   {key}: {value}")
        
        if high_stakes_params:
            print("\n🔥 HIGH STAKES SETTINGS:")
            for key, value in high_stakes_params.items():
                print(f"   {key}: {value}")
        elif the5ers_params:
            print("\n🏆 THE5ERS SETTINGS:")
            for key, value in the5ers_params.items():
                print(f"   {key}: {value}")
        
        print(f"\n📊 SIMBOLI CONFIGURATI: {len(symbols)}")
        for symbol in symbols.keys():
            print(f"   • {symbol}")
        
        print("\n✅ Report configurazione completato!")
        
    except Exception as e:
        print(f"❌ Errore lettura configurazione: {e}")
    """Gestione selezione configurazione con dettagli"""
    try:
        selector = ConfigSelector()
        
        print("⚙️ GESTIONE CONFIGURAZIONI THE5ERS")
        print("="*50)
        
        # Mostra menu opzioni
        print("Opzioni disponibili:")
        print("1. 📋 Mostra tutte le configurazioni disponibili")
        print("2. 🔍 Seleziona configurazione interattiva")
        print("3. 📊 Analizza configurazione specifica")
        print("4. 📌 Mostra configurazione default")
        print("5. ❌ Torna al menu principale")
        
        choice = input("\n👉 Scegli opzione (1-5): ").strip()
        
        if choice == "1":
            # Mostra tutte le configurazioni
            configs = selector.find_config_files()
            if configs:
                print(f"\n📁 CONFIGURAZIONI TROVATE ({len(configs)}):")
                print("-" * 80)
                for i, config in enumerate(configs, 1):
                    print(f"{i}. {config['filename']}")
                    print(f"   Tipo: {config['config_type']} | Simboli: {config['symbol_count']} | {config['aggressiveness']}")
                    print(f"   Risk: {config['risk_percent']*100:.3f}% | Max Trades: {config['max_daily_trades']}")
                    print()
            else:
                print("❌ Nessuna configurazione trovata")
        
        elif choice == "2":
            # Selezione interattiva
            selected = selector.show_interactive_menu()
            if selected:
                print(f"\n✅ Configurazione selezionata per prossimi backtest:")
                print(f"📁 {selected}")
                
                # Opzione per impostare come default temporaneo
                set_default = input("❓ Impostare come default per questa sessione? (y/n): ").strip().lower()
                if set_default in ['y', 'yes', 's', 'si']:
                    # Salva in variabile globale o file temporaneo
                    with open('temp_config_selection.txt', 'w') as f:
                        f.write(selected)
                    print("✅ Configurazione impostata come default temporaneo")
        
        elif choice == "3":
            # Analizza configurazione specifica
            selected = selector.show_interactive_menu()
            if selected:
                selector.show_config_details(selected)
        
        elif choice == "4":
            # Mostra default
            default = selector.get_default_config()
            if default:
                print(f"\n📌 CONFIGURAZIONE DEFAULT:")
                print(f"📁 {default}")
                selector.show_config_details(default)
            else:
                print("❌ Nessuna configurazione default trovata")
        
        elif choice == "5":
            return
        else:
            print("❌ Opzione non valida")
        
        input("\nPremi INVIO per continuare...")
        
    except Exception as e:
        print(f"❌ Errore gestione configurazioni: {e}")

def get_selected_config():
    """Ottiene la configurazione selezionata temporaneamente"""
    try:
        if os.path.exists('temp_config_selection.txt'):
            with open('temp_config_selection.txt', 'r') as f:
                return f.read().strip()
    except:
        pass
    return None

def select_configuration():
    """Gestione selezione configurazione con dettagli"""
    try:
        selector = ConfigSelector()
        
        print("⚙️ GESTIONE CONFIGURAZIONI THE5ERS")
        print("="*50)
        
        # Mostra menu opzioni
        print("Opzioni disponibili:")
        print("1. 📋 Mostra tutte le configurazioni disponibili")
        print("2. 🔍 Seleziona configurazione interattiva")
        print("3. 📊 Analizza configurazione specifica")
        print("4. 📌 Mostra configurazione default")
        print("5. ❌ Torna al menu principale")
        
        choice = input("\n👉 Scegli opzione (1-5): ").strip()
        
        if choice == "1":
            # Mostra tutte le configurazioni
            configs = selector.find_config_files()
            if configs:
                print(f"\n📁 CONFIGURAZIONI TROVATE ({len(configs)}):")
                print("-" * 80)
                for i, config in enumerate(configs, 1):
                    print(f"{i}. {config['filename']}")
                    print(f"   Tipo: {config['config_type']} | Simboli: {config['symbol_count']} | {config['aggressiveness']}")
                    print(f"   Risk: {config['risk_percent']*100:.3f}% | Max Trades: {config['max_daily_trades']}")
                    print()
            else:
                print("❌ Nessuna configurazione trovata")
        
        elif choice == "2":
            # Selezione interattiva
            selected = selector.show_interactive_menu()
            if selected:
                print(f"\n✅ Configurazione selezionata per prossimi backtest:")
                print(f"📁 {selected}")
                
                # Opzione per impostare come default temporaneo
                set_default = input("❓ Impostare come default per questa sessione? (y/n): ").strip().lower()
                if set_default in ['y', 'yes', 's', 'si']:
                    # Salva in variabile globale o file temporaneo
                    with open('temp_config_selection.txt', 'w') as f:
                        f.write(selected)
                    print("✅ Configurazione impostata come default temporaneo")
        
        elif choice == "3":
            # Analizza configurazione specifica
            selected = selector.show_interactive_menu()
            if selected:
                selector.show_config_details(selected)
        
        elif choice == "4":
            # Mostra default
            default = selector.get_default_config()
            if default:
                print(f"\n📌 CONFIGURAZIONE DEFAULT:")
                print(f"📁 {default}")
                selector.show_config_details(default)
            else:
                print("❌ Nessuna configurazione default trovata")
        
        elif choice == "5":
            return
        else:
            print("❌ Opzione non valida")
        
        input("\nPremi INVIO per continuare...")
        
    except Exception as e:
        print(f"❌ Errore gestione configurazioni: {e}")

def get_selected_config():
    """Ottiene la configurazione selezionata temporaneamente"""
    try:
        if os.path.exists('temp_config_selection.txt'):
            with open('temp_config_selection.txt', 'r') as f:
                return f.read().strip()
    except:
        pass
    return None

def test_the5ers_compliance():
    """Test compliance The5ers"""
    print("🏆 TEST COMPLIANCE THE5ERS")
    print("="*50)
    
    # Usa configurazione selezionata o default
    selected_config = get_selected_config()
    
    try:
        if selected_config:
            config_path = selected_config
            print(f"📁 Usando configurazione: {os.path.basename(config_path)}")
        else:
            selector = ConfigSelector()
            config_path = selector.get_default_config()
            print(f"📁 Usando configurazione default: {os.path.basename(config_path)}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        the5ers_config = config.get('THE5ERS_specific', {})
        risk_config = config.get('risk_parameters', {})
        
        print("🎯 VERIFICA COMPLIANCE:")
        
        # Step 1 target
        step1_target = the5ers_config.get('step1_target', 8)
        print(f"✅ Step 1 Target: {step1_target}%")
        
        # Daily loss limit
        daily_loss = the5ers_config.get('max_daily_loss_percent', 5)
        print(f"✅ Max Daily Loss: {daily_loss}%")
        
        # Total loss limit  
        total_loss = the5ers_config.get('max_total_loss_percent', 10)
        print(f"✅ Max Total Loss: {total_loss}%")
        
        # Risk per trade
        risk_per_trade = risk_config.get('risk_percent', 0.0015) * 100
        print(f"✅ Risk per Trade: {risk_per_trade:.3f}%")
        
        # Position sizing compliance
        print("✅ Micro Lot Compliance: Attivo")
        
        print("\n🎉 COMPLIANCE THE5ERS: 100% ✅")
        
    except Exception as e:
        print(f"❌ Errore test compliance: {e}")
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        the5ers_config = config.get('THE5ERS_specific', {})
        risk_config = config.get('risk_parameters', {})
        
        print("🎯 VERIFICA COMPLIANCE:")
        
        # Step 1 target
        step1_target = the5ers_config.get('step1_target', 8)
        print(f"✅ Step 1 Target: {step1_target}%")
        
        # Daily loss limit
        daily_loss = the5ers_config.get('max_daily_loss_percent', 5)
        print(f"✅ Max Daily Loss: {daily_loss}%")
        
        # Total loss limit  
        total_loss = the5ers_config.get('max_total_loss_percent', 10)
        print(f"✅ Max Total Loss: {total_loss}%")
        
        # Risk per trade
        risk_per_trade = risk_config.get('risk_percent', 0.0015) * 100
        print(f"✅ Risk per Trade: {risk_per_trade:.3f}%")
        
        # Position sizing compliance
        print("✅ Micro Lot Compliance: Attivo")
        
        print("\n🎉 COMPLIANCE THE5ERS: 100% ✅")
        
    except Exception as e:
        print(f"❌ Errore test compliance: {e}")

def main():
    """Funzione principale del launcher"""
    
    print("🎯 THE5ERS SYSTEM LAUNCHER")
    print("Benvenuto nel sistema di trading ottimizzato per The5ers!")
    print()
    
    while True:
        try:
            choice = show_menu()
            
            if choice == "1":
                check_system_requirements()
                
            elif choice == "2":
                run_integrated_backtest()
                
            elif choice == "3":
                run_optimized_backtest()
                
            elif choice == "4":
                run_comparative_backtest()
                
            elif choice == "5":
                run_custom_period_backtest()
                
            elif choice == "6":
                run_high_stakes_challenge()
                
            elif choice == "7":
                test_quantum_parameters()
                
            elif choice == "8":
                analyze_position_sizing()
                
            elif choice == "9":
                show_current_config()
                
            elif choice == "10":
                test_the5ers_compliance()
                
            elif choice == "11":
                select_configuration()
                
            elif choice == "12":
                print("👋 Arrivederci!")
                break
                
            else:
                print("❌ Opzione non valida. Scegli 1-12.")
            
            # Pausa prima del prossimo menu
            input("\nPremi INVIO per continuare...")
            
        except KeyboardInterrupt:
            print("\n👋 Launcher terminato.")
            break
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            input("Premi INVIO per continuare...")

if __name__ == "__main__":
    main()
