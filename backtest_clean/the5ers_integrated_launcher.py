#!/usr/bin/env python3
# ====================================================================================
# THE5ERS INTEGRATED LAUNCHER - SISTEMA COMPLETO CON OPTIMIZER CONFIGURABILE
# Launcher integrato che permette configurazione completa dell'ottimizzatore
# ====================================================================================

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import glob

# Import dell'optimizer
try:
    from high_stakes_optimizer import HighStakesOptimizer
except ImportError:
    print("❌ Errore: high_stakes_optimizer.py non trovato nella directory corrente")
    sys.exit(1)

class IntegratedLauncher:
    """
    Launcher integrato con configurazione completa dell'optimizer
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.optimizer = None
        self.current_config = None
        
    def show_main_menu(self):
        """Menu principale integrato"""
        
        print("🎯 THE5ERS INTEGRATED LAUNCHER")
        print("Sistema completo con ottimizzatore configurabile")
        print("="*60)
        print()
        
        print("🔧 CONFIGURAZIONE OPTIMIZER:")
        print("1.  📁 Seleziona File JSON Sorgente")
        print("2.  ⚙️ Configura Parametri High Stakes")
        print("3.  🎯 Configura Livelli Aggressività")
        print("4.  📊 Configura Simboli Preferiti")
        print()
        
        print("🔥 OTTIMIZZAZIONE:")
        print("5.  🚀 Genera TUTTE le Configurazioni")
        print("6.  🎯 Genera Configurazione Singola")
        print("7.  📋 Genera Configurazioni Selezionate")
        print("8.  ✅ Valida Configurazioni Generate")
        print()
        
        print("📊 BACKTEST AVANZATI:")
        print("9.  🔥 High Stakes Challenge Configurabile")
        print("10. 📈 Backtest Periodo Personalizzato")
        print("11. 🚀 Backtest Comparativo Multi-Config")
        print("12. 🔍 Analisi Performance Dettagliata")
        print()
        
        print("⚙️ GESTIONE CONFIGURAZIONI:")
        print("13. 📋 Lista Tutte le Configurazioni")
        print("14. 🔍 Auto-Discovery File JSON")
        print("15. 📊 Report Configurazione Attuale")
        print("16. 🔄 Switch Configurazione Dinamica")
        print()
        
        print("📊 ANALISI TOOLS:")
        print("17. 💰 Analisi Position Sizing Avanzata")
        print("18. 🔍 Analisi Simboli Multi-Timeframe")
        print("19. 🏆 Test Compliance The5ers")
        print("20. 🔬 Diagnostica Sistema Completa")
        print()
        
        print("📄 SISTEMA:")
        print("21. 📚 Documentazione Integrata")
        print("22. 🔧 Reset Configurazione Optimizer")
        print("23. 💾 Salva Configurazione Corrente")
        print("24. ❌ Esci")
        print()
        
    def init_optimizer(self, source_config=None, custom_params=None):
        """Inizializza optimizer con parametri configurabili"""
        
        try:
            # Trova config sorgente automaticamente se non specificato
            if not source_config:
                source_config = self.find_default_source_config()
            
            self.optimizer = HighStakesOptimizer(
                source_config_path=source_config,
                custom_params=custom_params or {},
                output_dir=self.base_dir
            )
            
            self.current_config = source_config
            print(f"✅ Optimizer inizializzato con: {os.path.basename(source_config)}")
            
        except Exception as e:
            print(f"❌ Errore inizializzazione optimizer: {e}")
            return False
        
        return True
    
    def find_default_source_config(self) -> str:
        """Trova automaticamente il file config sorgente"""
        
        # Lista priorità file sorgente
        candidates = [
            "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json",
            "config.json",
            "PRO-THE5ERS-QM-PHOENIX-GITCOP.json"
        ]
        
        # Cerca nella directory corrente e parent
        search_dirs = [self.base_dir, os.path.dirname(self.base_dir)]
        
        for directory in search_dirs:
            for candidate in candidates:
                path = os.path.join(directory, candidate)
                if os.path.exists(path):
                    return path
        
        # Fallback: primo JSON trovato con "config" nel nome
        for directory in search_dirs:
            for file in os.listdir(directory):
                if file.endswith('.json') and 'config' in file.lower():
                    return os.path.join(directory, file)
        
        raise FileNotFoundError("Nessun file di configurazione sorgente trovato")
    
    def select_source_config(self):
        """Menu selezione file JSON sorgente"""
        
        print("📁 SELEZIONE FILE JSON SORGENTE")
        print("="*40)
        
        # Auto-discovery
        try:
            if not self.optimizer:
                temp_optimizer = HighStakesOptimizer()
                configs = temp_optimizer.get_available_configs()
            else:
                configs = self.optimizer.get_available_configs()
            
            if not configs:
                print("❌ Nessun file JSON trovato!")
                return
            
            print("📋 File JSON disponibili:")
            for i, config in enumerate(configs, 1):
                name = os.path.basename(config)
                size = os.path.getsize(config)
                mod_time = datetime.fromtimestamp(os.path.getmtime(config))
                print(f"{i:2d}. {name} ({size} bytes, {mod_time.strftime('%d/%m %H:%M')})")
            
            print(f"{len(configs)+1:2d}. 📁 Inserisci percorso manuale")
            print(f"{len(configs)+2:2d}. ❌ Annulla")
            
            choice = input(f"\n👉 Scegli file (1-{len(configs)+2}): ").strip()
            
            if choice == str(len(configs)+2):
                return
            elif choice == str(len(configs)+1):
                manual_path = input("📁 Inserisci percorso completo: ").strip()
                if os.path.exists(manual_path):
                    selected_config = manual_path
                else:
                    print(f"❌ File non trovato: {manual_path}")
                    return
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(configs):
                        selected_config = configs[idx]
                    else:
                        print("❌ Selezione non valida")
                        return
                except ValueError:
                    print("❌ Inserire un numero valido")
                    return
            
            # Reinizializza optimizer con nuovo config
            custom_params = self.optimizer.custom_params if self.optimizer else {}
            if self.init_optimizer(selected_config, custom_params):
                print(f"✅ Configurazione sorgente cambiata: {os.path.basename(selected_config)}")
            
        except Exception as e:
            print(f"❌ Errore selezione config: {e}")
    
    def configure_high_stakes_params(self):
        """Configurazione parametri High Stakes"""
        
        print("⚙️ CONFIGURAZIONE PARAMETRI HIGH STAKES")
        print("="*45)
        
        if not self.optimizer:
            self.init_optimizer()
        
        current = self.optimizer.high_stakes_params
        
        print("📊 Parametri attuali:")
        for key, value in current.items():
            print(f"   {key}: {value}")
        
        print("\n🔧 Configurazione (ENTER per mantenere):")
        
        new_params = {}
        
        # Account Balance
        balance = input(f"💰 Account Balance (attuale: €{current['account_balance']}): ").strip()
        if balance:
            try:
                new_params['account_balance'] = int(balance)
            except ValueError:
                print("❌ Valore non valido per account balance")
        
        # Target Daily Profit
        target = input(f"🎯 Target Daily Profit (attuale: €{current['target_daily_profit']}): ").strip()
        if target:
            try:
                new_params['target_daily_profit'] = float(target)
            except ValueError:
                print("❌ Valore non valido per target profit")
        
        # Validation Days
        days = input(f"📅 Giorni Validazione (attuale: {current['validation_days']}): ").strip()
        if days:
            try:
                new_params['validation_days'] = int(days)
            except ValueError:
                print("❌ Valore non valido per giorni validazione")
        
        # Daily Loss Limit
        loss_limit = input(f"⛔ Daily Loss Limit (attuale: €{current['daily_loss_limit']}): ").strip()
        if loss_limit:
            try:
                new_params['daily_loss_limit'] = float(loss_limit)
            except ValueError:
                print("❌ Valore non valido per loss limit")
        
        # Leverage
        leverage = input(f"📈 Leverage (attuale: {current['leverage']}): ").strip()
        if leverage:
            try:
                new_params['leverage'] = int(leverage)
            except ValueError:
                print("❌ Valore non valido per leverage")
        
        if new_params:
            self.optimizer.configure_optimizer(high_stakes_params=new_params)
            print(f"✅ Parametri High Stakes aggiornati: {len(new_params)} modifiche")
        else:
            print("ℹ️ Nessuna modifica effettuata")
    
    def configure_aggressiveness_levels(self):
        """Configurazione livelli aggressività"""
        
        print("🎯 CONFIGURAZIONE LIVELLI AGGRESSIVITÀ")
        print("="*42)
        
        if not self.optimizer:
            self.init_optimizer()
        
        levels = self.optimizer.aggressiveness_levels
        
        print("📋 Livelli attuali:")
        for level, config in levels.items():
            print(f"\n🔹 {level.upper()}:")
            print(f"   Nome: {config['name']}")
            print(f"   Risk Multiplier: {config['risk_multiplier']}")
            print(f"   Trades Multiplier: {config['trades_multiplier']}")
            print(f"   Simboli: {config['symbols_count']}")
            print(f"   Target Score: {config['target_score']}")
        
        print(f"\n🔧 Scegli livello da modificare:")
        print("1. Conservative")
        print("2. Moderate")
        print("3. Aggressive")
        print("4. ❌ Annulla")
        
        choice = input("👉 Scegli (1-4): ").strip()
        
        level_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
        
        if choice not in level_map:
            return
        
        level_key = level_map[choice]
        current = levels[level_key]
        
        print(f"\n🔧 Modifica {current['name']} (ENTER per mantenere):")
        
        new_config = {}
        
        # Risk Multiplier
        risk = input(f"⚡ Risk Multiplier (attuale: {current['risk_multiplier']}): ").strip()
        if risk:
            try:
                new_config['risk_multiplier'] = float(risk)
            except ValueError:
                print("❌ Valore non valido per risk multiplier")
        
        # Trades Multiplier
        trades = input(f"📊 Trades Multiplier (attuale: {current['trades_multiplier']}): ").strip()
        if trades:
            try:
                new_config['trades_multiplier'] = float(trades)
            except ValueError:
                print("❌ Valore non valido per trades multiplier")
        
        # Symbols Count
        symbols = input(f"🔢 Numero Simboli (attuale: {current['symbols_count']}): ").strip()
        if symbols:
            try:
                new_config['symbols_count'] = int(symbols)
            except ValueError:
                print("❌ Valore non valido per numero simboli")
        
        # Target Score
        score = input(f"🎯 Target Score (attuale: {current['target_score']}): ").strip()
        if score:
            try:
                new_config['target_score'] = int(score)
            except ValueError:
                print("❌ Valore non valido per target score")
        
        if new_config:
            update_dict = {level_key: new_config}
            self.optimizer.configure_optimizer(aggressiveness_levels=update_dict)
            print(f"✅ Livello {current['name']} aggiornato: {len(new_config)} modifiche")
        else:
            print("ℹ️ Nessuna modifica effettuata")
    
    def generate_selected_configs(self):
        """Genera solo configurazioni selezionate"""
        
        print("📋 GENERAZIONE CONFIGURAZIONI SELEZIONATE")
        print("="*45)
        
        if not self.optimizer:
            self.init_optimizer()
        
        levels = list(self.optimizer.aggressiveness_levels.keys())
        
        print("🎯 Scegli livelli da generare:")
        for i, level in enumerate(levels, 1):
            name = self.optimizer.aggressiveness_levels[level]['name']
            desc = self.optimizer.aggressiveness_levels[level]['description']
            print(f"{i}. {name} - {desc}")
        
        print(f"{len(levels)+1}. 🔄 Tutti")
        print(f"{len(levels)+2}. ❌ Annulla")
        
        choices = input(f"\n👉 Scegli livelli (es: 1,3 o {len(levels)+1} per tutti): ").strip()
        
        if choices == str(len(levels)+2):
            return
        elif choices == str(len(levels)+1):
            selected_levels = levels
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choices.split(',')]
                selected_levels = [levels[i] for i in indices if 0 <= i < len(levels)]
                
                if not selected_levels:
                    print("❌ Nessun livello valido selezionato")
                    return
                    
            except (ValueError, IndexError):
                print("❌ Formato selezione non valido (usa: 1,2,3)")
                return
        
        # Directory output
        output_dir = input("📂 Directory output (ENTER per corrente): ").strip()
        if not output_dir:
            output_dir = self.base_dir
        
        # Genera configurazioni
        try:
            results = self.optimizer.optimize_all_levels(output_dir, selected_levels)
            
            print(f"\n📄 CONFIGURAZIONI GENERATE:")
            for level, filepath in results.items():
                print(f"✅ {level.upper()}: {os.path.basename(filepath)}")
                
        except Exception as e:
            print(f"❌ Errore generazione: {e}")
    
    def run_configurable_high_stakes(self):
        """High Stakes Challenge configurabile"""
        
        print("🔥 HIGH STAKES CHALLENGE CONFIGURABILE")
        print("="*42)
        
        # Lista configurazioni disponibili
        config_files = glob.glob("config_high_stakes_*.json")
        if not config_files:
            print("❌ Nessuna configurazione High Stakes trovata!")
            print("💡 Genera prima le configurazioni (opzione 5-7)")
            return
        
        print("📋 Configurazioni disponibili:")
        for i, config in enumerate(config_files, 1):
            name = os.path.basename(config)
            print(f"{i}. {name}")
        
        config_choice = input(f"\n👉 Scegli configurazione (1-{len(config_files)}): ").strip()
        
        try:
            config_idx = int(config_choice) - 1
            if not (0 <= config_idx < len(config_files)):
                print("❌ Selezione non valida")
                return
            
            selected_config = config_files[config_idx]
            
        except ValueError:
            print("❌ Inserire un numero valido")
            return
        
        # Parametri test
        print("\n⚙️ Configurazione test:")
        
        # Giorni test
        days = input("📅 Giorni test (default: 5): ").strip()
        test_days = int(days) if days.isdigit() else 5
        
        # Periodo personalizzato
        use_custom = input("📆 Usare periodo personalizzato? (y/N): ").strip().lower()
        
        start_date = None
        end_date = None
        
        if use_custom == 'y':
            start_str = input("📅 Data inizio (YYYY-MM-DD) o giorni indietro (es: 30): ").strip()
            
            if start_str.isdigit():
                # Giorni indietro
                days_back = int(start_str)
                start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
            else:
                # Data specifica
                start_date = start_str
                end_str = input("📅 Data fine (YYYY-MM-DD, ENTER per oggi): ").strip()
                end_date = end_str if end_str else datetime.now().strftime('%Y-%m-%d')
        
        # Costruisci comando
        cmd = ["python", "PRO-THE5ERS-QM-PHOENIX-GITCOP.py"]
        
        # Aggiungi parametri
        cmd.extend(["--config", selected_config])
        cmd.extend(["--days", str(test_days)])
        
        if start_date:
            cmd.extend(["--start-date", start_date])
        if end_date:
            cmd.extend(["--end-date", end_date])
        
        cmd.append("--high-stakes")
        
        print(f"\n🚀 Eseguendo: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ High Stakes completato con successo!")
                print("\n📊 OUTPUT:")
                print(result.stdout)
            else:
                print("❌ Errore durante esecuzione:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Errore esecuzione comando: {e}")
    
    def run(self):
        """Esegue launcher integrato"""
        
        # Inizializzazione automatica
        print("🔄 Inizializzazione sistema...")
        if not self.init_optimizer():
            print("❌ Impossibile inizializzare optimizer")
            return
        
        while True:
            try:
                self.show_main_menu()
                choice = input("👉 Scegli opzione (1-24): ").strip()
                
                if choice == "1":
                    self.select_source_config()
                elif choice == "2":
                    self.configure_high_stakes_params()
                elif choice == "3":
                    self.configure_aggressiveness_levels()
                elif choice == "4":
                    print("🔧 Configurazione simboli - TODO")
                elif choice == "5":
                    if self.optimizer:
                        results = self.optimizer.optimize_all_levels()
                        print(f"✅ Generate {len(results)} configurazioni")
                elif choice == "6":
                    print("🔧 Configurazione singola - TODO")
                elif choice == "7":
                    self.generate_selected_configs()
                elif choice == "8":
                    print("🔧 Validazione - TODO")
                elif choice == "9":
                    self.run_configurable_high_stakes()
                elif choice == "10":
                    print("🔧 Backtest periodo - TODO")
                elif choice == "11":
                    print("🔧 Backtest comparativo - TODO")
                elif choice == "12":
                    print("🔧 Analisi performance - TODO")
                elif choice == "13":
                    if self.optimizer:
                        configs = self.optimizer.get_available_configs()
                        print(f"📋 Trovate {len(configs)} configurazioni:")
                        for config in configs:
                            print(f"   📄 {os.path.basename(config)}")
                elif choice == "14":
                    print("🔧 Auto-discovery - TODO")
                elif choice == "15":
                    if self.current_config:
                        print(f"📊 Config attuale: {os.path.basename(self.current_config)}")
                    else:
                        print("❌ Nessuna configurazione caricata")
                elif choice == "16":
                    print("🔧 Switch dinamica - TODO")
                elif choice == "17":
                    print("🔧 Position sizing - TODO")
                elif choice == "18":
                    print("🔧 Analisi simboli - TODO")
                elif choice == "19":
                    print("🔧 Test compliance - TODO")
                elif choice == "20":
                    print("🔧 Diagnostica - TODO")
                elif choice == "21":
                    print("🔧 Documentazione - TODO")
                elif choice == "22":
                    self.optimizer = None
                    self.current_config = None
                    print("✅ Configurazione optimizer resettata")
                elif choice == "23":
                    print("🔧 Salva config - TODO")
                elif choice == "24":
                    print("👋 Launcher terminato.")
                    break
                else:
                    print("❌ Opzione non valida. Scegli un numero da 1 a 24.")
                
                if choice != "24":
                    input("\n⏸️ Premi ENTER per continuare...")
                    print("\n" * 2)  # Spazio tra operazioni
                    
            except KeyboardInterrupt:
                print("\n\n👋 Launcher terminato dall'utente.")
                break
            except Exception as e:
                print(f"\n❌ Errore imprevisto: {e}")
                input("⏸️ Premi ENTER per continuare...")

def main():
    """Funzione principale"""
    launcher = IntegratedLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
