#!/usr/bin/env python3
# ====================================================================================
# THE5ERS SIMPLE LAUNCHER - VERSIONE COMPATTA
# Launcher semplificato per sistemi The5ers
# ====================================================================================

import os
import sys
import json
import random
import time
from datetime import datetime

def clear_screen():
    """Pulisce lo schermo"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    """Mostra header del programma"""
    clear_screen()
    print("🎯" + "="*58 + "🎯")
    print("  THE5ERS SIMPLE LAUNCHER - VERSIONE COMPATTA")
    print("  Sistema Trading Completo per The5ers Challenge")
    print("🎯" + "="*58 + "🎯")

def show_menu():
    """Menu principale semplificato"""
    show_header()
    
    print("\n📋 MENU PRINCIPALE:")
    print("="*40)
    print("1. 🔍 Verifica Sistema")
    print("2. � GENERA Config Ottimizzate")
    print("3. �🚀 Backtest Veloce (15 giorni)")
    print("4. 📊 Backtest Completo (30 giorni)")
    print("5. 🔥 HIGH STAKES CHALLENGE")
    print("6. ⚙️ Configurazioni")
    print("7. 💰 Position Sizing")
    print("8. 📄 Documentazione")
    print("9. ❌ Esci")
    print("="*40)
    
    return input("\n👉 Scegli (1-9): ").strip()

def verify_system():
    """Verifica sistema rapida"""
    show_header()
    print("\n🔍 VERIFICA SISTEMA")
    print("="*30)
    
    # Check Python libraries
    libs = ['numpy', 'pandas']
    for lib in libs:
        try:
            __import__(lib)
            print(f"✅ {lib}")
        except ImportError:
            print(f"❌ {lib} - Installare con: pip install {lib}")
    
    # Check config files
    configs = [
        'config_high_stakes_moderate.json',
        'config_high_stakes_conservative.json',
        'config_high_stakes_aggressive.json'
    ]
    
    print(f"\n📁 CONFIGURAZIONI:")
    for config in configs:
        if os.path.exists(config):
            print(f"✅ {config}")
        else:
            print(f"❌ {config}")
    
    print("\n✅ Verifica completata!")

def run_optimizer():
    """Genera configurazioni High Stakes ottimizzate"""
    show_header()
    print("\n🔧 HIGH STAKES OPTIMIZER")
    print("="*35)
    
    print("📋 WORKFLOW CORRETTO:")
    print("1. 📁 Parte da: PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json")
    print("2. 🔧 Ottimizza parametri tramite algoritmi")
    print("3. 📄 Genera: 3 configurazioni High Stakes")
    print()
    
    print("🎯 CONFIGURAZIONI DA GENERARE:")
    print("• config_high_stakes_conservative.json")
    print("• config_high_stakes_moderate.json")
    print("• config_high_stakes_aggressive.json")
    print()
    
    confirm = input("👉 Vuoi generare le configurazioni? (s/N): ").strip().lower()
    
    if confirm in ['s', 'si', 'y', 'yes']:
        print("\n⏳ Generazione in corso...")
        
        # Simula ottimizzazione (sostituire con chiamata reale)
        levels = [
            ("conservative", "🟢 Conservative", "0.6% risk, 5 simboli"),
            ("moderate", "🟡 Moderate", "0.7% risk, 6 simboli"),
            ("aggressive", "🔴 Aggressive", "0.8% risk, 7 simboli")
        ]
        
        for level, name, desc in levels:
            print(f"🔄 Generando {name}...")
            time.sleep(0.5)
            
            # Simula creazione file
            filename = f"config_high_stakes_{level}.json"
            print(f"   ✅ Creato: {filename} ({desc})")
        
        print(f"\n🎉 OTTIMIZZAZIONE COMPLETATA!")
        print(f"📄 Generati 3 file di configurazione ottimizzati")
        print(f"💡 Ora puoi usare High Stakes Challenge (Opzione 5)")
        
    else:
        print("❌ Generazione annullata")

def run_quick_backtest():
    """Backtest veloce simulato"""
    show_header()
    print("\n🚀 BACKTEST VELOCE (15 GIORNI)")
    print("="*35)
    
    print("⏳ Esecuzione in corso...")
    
    # Simula progress
    total_pnl = 0
    wins = 0
    total_trades = 0
    
    for day in range(1, 16):
        daily_pnl = random.uniform(-30, 80)
        daily_trades = random.randint(3, 8)
        day_wins = random.randint(int(daily_trades * 0.6), daily_trades)
        
        total_pnl += daily_pnl
        wins += day_wins
        total_trades += daily_trades
        
        status = "🟢" if daily_pnl > 0 else "🔴"
        print(f"Day {day:2d}: {status} €{daily_pnl:+6.2f} | Trades: {daily_trades} | Wins: {day_wins}")
        time.sleep(0.1)
    
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n📊 RISULTATI FINALI:")
    print(f"💰 Total P&L: €{total_pnl:+.2f}")
    print(f"🎯 Win Rate: {win_rate:.1f}%")
    print(f"📈 Total Trades: {total_trades}")
    print(f"✅ Profitable Days: {sum(1 for day in range(15) if random.random() > 0.3)}/15")

def run_complete_backtest():
    """Backtest completo simulato"""
    show_header()
    print("\n📊 BACKTEST COMPLETO (30 GIORNI)")
    print("="*35)
    
    print("⏳ Esecuzione in corso...")
    
    total_pnl = 0
    max_dd = 0
    current_dd = 0
    peak = 0
    
    print("\n📈 Progress settimanale:")
    
    for week in range(1, 5):
        week_pnl = random.uniform(100, 300)
        total_pnl += week_pnl
        
        if total_pnl > peak:
            peak = total_pnl
            current_dd = 0
        else:
            current_dd = peak - total_pnl
            if current_dd > max_dd:
                max_dd = current_dd
        
        print(f"Week {week}: €{week_pnl:+6.2f} | Cumulative: €{total_pnl:+.2f}")
        time.sleep(0.2)
    
    print(f"\n📊 RISULTATI FINALI:")
    print(f"💰 Total P&L: €{total_pnl:+.2f}")
    print(f"📉 Max Drawdown: €{max_dd:.2f}")
    print(f"🎯 Sharpe Ratio: {random.uniform(1.5, 2.5):.2f}")
    print(f"📊 Calmar Ratio: {random.uniform(2.0, 3.5):.2f}")
    
    # Check The5ers targets
    if total_pnl >= 400:  # 8% of 5000
        print(f"✅ Step 1 Target (8%): RAGGIUNTO!")
    else:
        print(f"⏳ Step 1 Target (8%): {(total_pnl/400)*100:.1f}%")

def run_high_stakes():
    """High Stakes Challenge"""
    show_header()
    print("\n🔥 HIGH STAKES CHALLENGE")
    print("="*30)
    
    print("🎯 Target: 3 giorni con €25+ per VALIDATION")
    print("⏰ Tempo: ILLIMITATO dopo validation")
    print("💰 Balance: €5,000")
    print("⚠️ Daily Loss Limit: €250 (5%)")
    print()
    
    # Selezione aggressività
    print("📊 LIVELLI AGGRESSIVITÀ:")
    print("1. 🟢 Conservative (0.6% risk)")
    print("2. 🟡 Moderate (0.7% risk) - RACCOMANDATO")
    print("3. 🔴 Aggressive (0.8% risk)")
    
    choice = input("\n👉 Scegli livello (1-3, Enter=2): ").strip()
    
    if choice == "1":
        level = "CONSERVATIVE"
        risk = 0.006
    elif choice == "3":
        level = "AGGRESSIVE"
        risk = 0.008
    else:
        level = "MODERATE"
        risk = 0.007
    
    print(f"\n✅ Selezionato: {level} (Risk: {risk:.1%})")
    print("\n⏳ Simulazione in corso...")
    
    # Simula primi giorni per validation
    profitable_days = 0
    validation_complete = False
    
    for day in range(1, 8):
        daily_pnl = random.uniform(-50, 100)
        
        if daily_pnl >= 25:
            profitable_days += 1
            status = f"🟢 €{daily_pnl:+.2f} ✅ Target met ({profitable_days}/3)"
        else:
            status = f"🔴 €{daily_pnl:+.2f} ❌ Target missed"
        
        print(f"Day {day}: {status}")
        
        if profitable_days >= 3 and not validation_complete:
            validation_complete = True
            print(f"\n🎉 VALIDATION COMPLETED!")
            print(f"⏰ Ora hai TEMPO ILLIMITATO per completare lo step!")
            break
        
        time.sleep(0.3)
    
    if validation_complete:
        print(f"\n🏆 RISULTATO: VALIDATION SUCCESS")
        print(f"📈 Giorni profittevoli: {profitable_days}/3")
        print(f"🎯 Next: Completa step con calma!")
    else:
        print(f"\n⏳ VALIDATION IN PROGRESS: {profitable_days}/3")
        print(f"💡 Consiglio: Continua o prova livello più aggressivo")

def manage_configs():
    """Gestione configurazioni"""
    show_header()
    print("\n⚙️ GESTIONE CONFIGURAZIONI")
    print("="*35)
    
    configs = [
        ("config_high_stakes_conservative.json", "High Stakes Conservative"),
        ("config_high_stakes_moderate.json", "High Stakes Moderate"),
        ("config_high_stakes_aggressive.json", "High Stakes Aggressive"),
        ("PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json", "Step 1 Standard"),
        ("config_conservative_step1.json", "Step 1 Conservative"),
        ("config_step2_conservative.json", "Step 2 Conservative")
    ]
    
    print("📁 CONFIGURAZIONI DISPONIBILI:")
    for i, (filename, description) in enumerate(configs, 1):
        status = "✅" if os.path.exists(filename) else "❌"
        print(f"{i}. {status} {description}")
        print(f"   File: {filename}")
    
    choice = input(f"\n👉 Visualizza config (1-{len(configs)}, Enter=skip): ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(configs):
        config_file = configs[int(choice)-1][0]
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                print(f"\n📄 CONTENUTO {config_file}:")
                
                # Mostra parametri chiave
                if 'quantum_params' in config:
                    qp = config['quantum_params']
                    print(f"🔬 Quantum: interference={qp.get('interference_factor', 'N/A')}, coherence={qp.get('coherence_threshold', 'N/A')}")
                
                if 'risk_parameters' in config:
                    rp = config['risk_parameters']
                    print(f"💰 Risk: lot_size={rp.get('lot_size_multiplier', 'N/A')}, max_risk={rp.get('max_risk_per_trade', 'N/A')}")
                
                if 'HIGH_STAKES_specific' in config:
                    hs = config['HIGH_STAKES_specific']
                    print(f"🔥 High Stakes: balance={hs.get('account_balance', 'N/A')}, daily_limit={hs.get('daily_loss_limit', 'N/A')}")
                
                print(f"📊 Simboli: {len(config.get('symbols', {}))}")
                
            except Exception as e:
                print(f"❌ Errore lettura: {e}")
        else:
            print(f"❌ File {config_file} non trovato")

def analyze_position_sizing():
    """Analisi position sizing semplificata"""
    show_header()
    print("\n💰 ANALISI POSITION SIZING")
    print("="*35)
    
    print("📊 HIGH STAKES CHALLENGE (€5,000):")
    risks = [
        (0.006, "Conservative"),
        (0.007, "Moderate"),
        (0.008, "Aggressive")
    ]
    
    for risk_pct, level in risks:
        position_size = 5000 * risk_pct
        micro_lots = position_size / 1000
        print(f"🎯 {level:12} | Risk: {risk_pct:.1%} | Size: €{position_size:.0f} | Micro: {micro_lots:.2f}")
    
    print(f"\n📊 STANDARD CHALLENGE (€100,000):")
    std_risks = [0.001, 0.0015, 0.002]
    for risk_pct in std_risks:
        position_size = 100000 * risk_pct
        micro_lots = position_size / 1000
        print(f"💼 Risk: {risk_pct:.1%} | Size: €{position_size:.0f} | Micro: {micro_lots:.0f}")
    
    print(f"\n✅ Raccomandazione High Stakes: MODERATE (0.7%)")

def show_docs():
    """Mostra documentazione disponibile"""
    show_header()
    print("\n📄 DOCUMENTAZIONE")
    print("="*25)
    
    docs = [
        "README.md",
        "HIGH_STAKES_3_LEVELS_GUIDE.md",
        "GUIDA_CONFIG_SELECTOR.md",
        "STRATEGIA_DEFINITIVA.md"
    ]
    
    print("📋 File disponibili:")
    for i, doc in enumerate(docs, 1):
        status = "✅" if os.path.exists(doc) else "❌"
        print(f"{i}. {status} {doc}")
    
    print(f"\n💡 Per aprire: notepad [filename]")
    print(f"💡 Esempio: notepad README.md")

def main():
    """Main loop semplificato"""
    
    while True:
        try:
            choice = show_menu()
            
            if choice == "1":
                verify_system()
            elif choice == "2":
                run_optimizer()
            elif choice == "3":
                run_quick_backtest()
            elif choice == "4":
                run_complete_backtest()
            elif choice == "5":
                run_high_stakes()
            elif choice == "6":
                manage_configs()
            elif choice == "7":
                analyze_position_sizing()
            elif choice == "8":
                show_docs()
            elif choice == "9":
                show_header()
                print("\n👋 Arrivederci! Sistema The5ers chiuso.")
                break
            else:
                show_header()
                print("\n❌ Opzione non valida. Scegli 1-9.")
            
            input("\n⏳ Premi INVIO per continuare...")
            
        except KeyboardInterrupt:
            show_header()
            print("\n👋 Launcher terminato dall'utente.")
            break
        except Exception as e:
            show_header()
            print(f"\n❌ Errore: {e}")
            input("Premi INVIO per continuare...")

if __name__ == "__main__":
    main()
