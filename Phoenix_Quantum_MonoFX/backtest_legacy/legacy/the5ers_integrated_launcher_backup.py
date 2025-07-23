#!/usr/bin/env python3
# ====================================================================================
# THE5ERS INTEGRATED LAUNCHER - SISTEMA COMPLETO CON OPTIMIZER CONFIGURABILE
# Launcher integrato che permette configurazione completa dell'ottimizzatore
# ====================================================================================

import os
import sys
import json
import subprocess
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import glob

# Import dell'optimizer
try:
    from high_stakes_optimizer import HighStakesOptimizer
    from autonomous_high_stakes_optimizer import AutonomousHighStakesOptimizer
except ImportError as e:
    print(f"❌ Errore import optimizer: {e}")
    print("💡 Assicurati che i file optimizer siano nella directory corrente")
    sys.exit(1)

class IntegratedLauncher:
    """
    Launcher integrato con configurazione completa dell'optimizer
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.optimizer = None
        self.autonomous_optimizer = None
        self.current_config = None
        self.optimizer_mode = "autonomous"  # "autonomous" o "json_based"
        
    def show_main_menu(self):
        """Menu principale integrato"""
        
        print("🎯 THE5ERS INTEGRATED LAUNCHER")
        print("Sistema completo con ottimizzatore configurabile")
        print("="*60)
        print()
        
        print("🔧 CONFIGURAZIONE OPTIMIZER:")
        print("1.  🎯 Modalità Ottimizzazione (JSON vs Autonoma)")
        print("2.  📁 Seleziona File JSON Sorgente [Solo modalità JSON]")
        print("3.  ⚙️ Configura Parametri High Stakes")
        print("4.  🎯 Configura Livelli Aggressività")
        print("5.  📊 Configura Simboli Preferiti")
        print()
        
        print("🔥 OTTIMIZZAZIONE:")
        print("6.  🚀 Genera TUTTE le Configurazioni")
        print("7.  🎯 Genera Configurazione Singola")
        print("8.  📋 Genera Configurazioni Selezionate")
        print("9.  ✅ Valida Configurazioni Generate")
        print()
        
        print("📊 BACKTEST AVANZATI:")
        print("10. 🔥 High Stakes Challenge Configurabile")
        print("11. 📈 Backtest Periodo Personalizzato")
        print("12. 🚀 Backtest Comparativo Multi-Config")
        print("13. 🔍 Analisi Performance Dettagliata")
        print()
        
        print("⚙️ GESTIONE CONFIGURAZIONI:")
        print("14. 📋 Lista Tutte le Configurazioni")
        print("15. 🔍 Auto-Discovery File JSON")
        print("16. 📊 Report Configurazione Attuale")
        print("17. 🔄 Switch Configurazione Dinamica")
        print()
        
        print("📊 ANALISI TOOLS:")
        print("18. 💰 Analisi Position Sizing Avanzata")
        print("19. 🔍 Analisi Simboli Multi-Timeframe")
        print("20. 🏆 Test Compliance The5ers")
        print("21. 🔬 Diagnostica Sistema Completa")
        print()
        
        print("📄 SISTEMA:")
        print("22. 📚 Documentazione Integrata")
        print("23. 🔧 Reset Configurazione Optimizer")
        print("24. 💾 Salva Configurazione Corrente")
        print("25. ❌ Esci")
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
    
    def select_optimizer_mode(self):
        """Selezione modalità optimizer"""
        
        print("🎯 MODALITÀ OTTIMIZZAZIONE")
        print("="*30)
        print()
        print("📋 Modalità disponibili:")
        print()
        print("1. 🚀 **AUTONOMA** (RACCOMANDATO)")
        print("   ✅ Genera configurazioni DA ZERO")
        print("   ✅ Basato solo su algoritmo + dati MT5")
        print("   ✅ NON richiede file JSON sorgente")
        print("   ✅ Ottimizzazione parametrica completa")
        print()
        print("2. 📁 **BASATA SU JSON**")
        print("   ✅ Modifica file JSON esistente")
        print("   ✅ Mantiene struttura originale")
        print("   ⚠️  Richiede file JSON sorgente")
        print()
        print(f"📊 Modalità attuale: {self.optimizer_mode.upper()}")
        print()
        
        choice = input("👉 Scegli modalità (1=Autonoma, 2=JSON, ENTER=mantieni): ").strip()
        
        if choice == "1":
            self.optimizer_mode = "autonomous"
            print("✅ Modalità cambiata: AUTONOMA")
            print("🎯 Generazione configurazioni da zero senza JSON sorgente")
            
            # Inizializza optimizer autonomo
            self.autonomous_optimizer = AutonomousHighStakesOptimizer(output_dir=self.base_dir)
            self.optimizer = None
            
        elif choice == "2":
            self.optimizer_mode = "json_based"
            print("✅ Modalità cambiata: BASATA SU JSON")
            print("📁 Richiede file JSON sorgente per modifiche")
            
            # Prova inizializzazione JSON-based
            try:
                self.init_optimizer()
            except Exception as e:
                print(f"⚠️  Errore inizializzazione JSON: {e}")
                print("💡 Dovrai selezionare file JSON sorgente (opzione 2)")
                
        else:
            print(f"ℹ️ Modalità mantenuta: {self.optimizer_mode.upper()}")
    
    def select_source_config(self):
        """Menu selezione file JSON sorgente (solo per modalità JSON)"""
        
        if self.optimizer_mode == "autonomous":
            print("ℹ️ MODALITÀ AUTONOMA ATTIVA")
            print("🚀 Non serve file JSON sorgente!")
            print("💡 Le configurazioni vengono generate da zero")
            return
        
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
        print(f"🎯 Modalità optimizer: {self.optimizer_mode.upper()}")
        
        if self.optimizer_mode == "autonomous":
            print("🚀 Modalità AUTONOMA: Generazione da zero senza JSON")
            self.autonomous_optimizer = AutonomousHighStakesOptimizer(output_dir=self.base_dir)
        else:
            print("📁 Modalità JSON: Richiede file sorgente")
            if not self.init_optimizer():
                print("⚠️ Impossibile inizializzare optimizer JSON")
                print("💡 Passa alla modalità AUTONOMA (opzione 1)")
        
        while True:
            try:
                self.show_main_menu()
                choice = input("👉 Scegli opzione (1-25): ").strip()
                
                if choice == "1":
                    self.select_optimizer_mode()
                elif choice == "2":
                    self.select_source_config()
                elif choice == "3":
                    if self.optimizer_mode == "json_based" and self.optimizer:
                        self.configure_high_stakes_params()
                    else:
                        print("⚠️ Configurazione High Stakes non disponibile in modalità autonoma")
                        print("💡 I parametri vengono ottimizzati automaticamente")
                elif choice == "4":
                    if self.optimizer_mode == "json_based" and self.optimizer:
                        self.configure_aggressiveness_levels()
                    else:
                        print("⚠️ Configurazione aggressività non disponibile in modalità autonoma")
                        print("💡 I livelli vengono ottimizzati automaticamente")
                elif choice == "5":
                    print("🔧 Configurazione simboli - TODO")
                elif choice == "6":
                    # Genera tutte le configurazioni
                    if self.optimizer_mode == "autonomous":
                        if self.autonomous_optimizer:
                            results = self.autonomous_optimizer.generate_all_configs()
                            print(f"✅ Generate {len(results)} configurazioni AUTONOME")
                        else:
                            print("❌ Optimizer autonomo non inizializzato")
                    else:
                        if self.optimizer:
                            results = self.optimizer.optimize_all_levels()
                            print(f"✅ Generate {len(results)} configurazioni da JSON")
                        else:
                            print("❌ Optimizer JSON non inizializzato")
                elif choice == "7":
                    # Genera configurazione singola
                    if self.optimizer_mode == "autonomous":
                        if self.autonomous_optimizer:
                            print("\n🎯 GENERAZIONE CONFIGURAZIONE SINGOLA AUTONOMA")
                            print("="*50)
                            print("1. � Conservative")
                            print("2. 🟡 Moderate") 
                            print("3. 🔴 Aggressive")
                            
                            level_choice = input("👉 Scegli livello (1-3): ").strip()
                            level_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
                            level = level_map.get(level_choice, 'moderate')
                            
                            config = self.autonomous_optimizer.generate_optimized_config(level)
                            filepath = self.autonomous_optimizer.save_config(config, level)
                            print(f"✅ Generato AUTONOMO: {os.path.basename(filepath)}")
                        else:
                            print("❌ Optimizer autonomo non inizializzato")
                    else:
                        if self.optimizer:
                            levels = self.optimizer.aggressiveness_levels.keys()
                            print(f"\n🎯 Configurazioni disponibili: {', '.join(levels)}")
                            level = input("👉 Scegli livello: ").strip().lower()
                            if level in levels:
                                result = self.optimizer.generate_optimized_config(level)
                                print(f"✅ Generato da JSON: {os.path.basename(result)}")
                            else:
                                print("❌ Livello non valido")
                        else:
                            print("❌ Optimizer JSON non inizializzato")
                elif choice == "8":
                    if self.optimizer_mode == "json_based" and self.optimizer:
                        self.generate_selected_configs()
                    elif self.optimizer_mode == "autonomous":
                        if self.autonomous_optimizer:
                            print("\n🎯 SELEZIONE CONFIGURAZIONI AUTONOME")
                            print("="*40)
                            print("1. Conservative + Moderate")
                            print("2. Moderate + Aggressive")
                            print("3. Solo Conservative")
                            print("4. Solo Aggressive")
                            
                            sel_choice = input("� Scegli (1-4): ").strip()
                            
                            results = {}
                            if sel_choice == "1":
                                for level in ['conservative', 'moderate']:
                                    config = self.autonomous_optimizer.generate_optimized_config(level)
                                    filepath = self.autonomous_optimizer.save_config(config, level)
                                    results[level] = filepath
                            elif sel_choice == "2":
                                for level in ['moderate', 'aggressive']:
                                    config = self.autonomous_optimizer.generate_optimized_config(level)
                                    filepath = self.autonomous_optimizer.save_config(config, level)
                                    results[level] = filepath
                            elif sel_choice == "3":
                                config = self.autonomous_optimizer.generate_optimized_config('conservative')
                                filepath = self.autonomous_optimizer.save_config(config, 'conservative')
                                results['conservative'] = filepath
                            elif sel_choice == "4":
                                config = self.autonomous_optimizer.generate_optimized_config('aggressive')
                                filepath = self.autonomous_optimizer.save_config(config, 'aggressive')
                                results['aggressive'] = filepath
                            
                            print(f"✅ Generate {len(results)} configurazioni AUTONOME selezionate")
                        else:
                            print("❌ Optimizer autonomo non inizializzato")
                    else:
                        print("❌ Nessun optimizer disponibile")
                elif choice == "9":
                    # Validazione configurazioni
                    if self.optimizer_mode == "autonomous":
                        import glob
                        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
                        
                        if config_files:
                            print(f"\n🔄 VALIDAZIONE {len(config_files)} CONFIGURAZIONI AUTONOME")
                            print("="*50)
                            
                            for config_file in config_files:
                                results = self.autonomous_optimizer.run_validation_test(config_file, 7)
                                status = "✅ PASS" if results['high_stakes_validation'] else "❌ FAIL"
                                filename = os.path.basename(config_file)
                                pnl = results['daily_avg_pnl']
                                print(f"{status} {filename}: €{pnl:.2f}/day")
                        else:
                            print("❌ Nessuna configurazione autonoma trovata!")
                            print("� Genera prima le configurazioni (opzione 6)")
                    else:
                        print("�🔧 Validazione configurazioni JSON - TODO")
                        # Implementazione per modalità JSON se necessario
                elif choice == "10":
                    self.run_configurable_high_stakes()
                elif choice == "11":
                    # Backtest periodo personalizzato
                    if self.optimizer_mode == "autonomous":
                        print("\n📈 BACKTEST PERIODO PERSONALIZZATO")
                        print("="*40)
                        
                        days = input("📅 Giorni di backtest (default: 30): ").strip()
                        test_days = int(days) if days.isdigit() else 30
                        
                        level_choice = input("🎯 Livello aggressività (conservative/moderate/aggressive): ").strip().lower()
                        if level_choice not in ['conservative', 'moderate', 'aggressive']:
                            level_choice = 'moderate'
                        
                        print(f"� Eseguendo backtest {level_choice} su {test_days} giorni...")
                        
                        # Genera config temporanea per test
                        temp_optimizer = AutonomousHighStakesOptimizer(test_days)
                        config = temp_optimizer.generate_optimized_config(level_choice)
                        
                        # Simula backtest risultati
                        symbols = list(config['symbols'].keys())
                        score = config['optimization_results']['average_optimization_score']
                        
                        print(f"✅ Backtest completato:")
                        print(f"   📊 Simboli testati: {', '.join(symbols[:3])}...")
                        print(f"   🎯 Score ottimizzazione: {score:.2f}")
                        print(f"   ⏱️ Periodo: {test_days} giorni")
                        print(f"   📈 Livello: {level_choice}")
                    else:
                        print("�🔧 Backtest periodo personalizzato - JSON mode TODO")
                        
                elif choice == "12":
                    # Backtest comparativo
                    if self.optimizer_mode == "autonomous":
                        print("\n🚀 BACKTEST COMPARATIVO MULTI-CONFIG")
                        print("="*45)
                        
                        import glob
                        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
                        
                        if len(config_files) < 2:
                            print("❌ Servono almeno 2 configurazioni per il confronto")
                            print("💡 Genera prima tutte le configurazioni (opzione 6)")
                        else:
                            print(f"🔄 Confrontando {len(config_files)} configurazioni...")
                            
                            comparison_results = []
                            for config_file in config_files:
                                results = self.autonomous_optimizer.run_validation_test(config_file, 14)
                                comparison_results.append({
                                    'config': os.path.basename(config_file),
                                    'pnl': results['daily_avg_pnl'],
                                    'win_rate': results['win_rate'],
                                    'trades': results['total_trades']
                                })
                            
                            # Ordina per PnL
                            comparison_results.sort(key=lambda x: x['pnl'], reverse=True)
                            
                            print("\n📊 RISULTATI COMPARATIVI:")
                            print("="*50)
                            for i, result in enumerate(comparison_results, 1):
                                config_name = result['config'].replace('config_autonomous_high_stakes_', '').replace('.json', '')
                                print(f"{i}. {config_name.upper()}")
                                print(f"   💰 P&L: €{result['pnl']:.2f}/day")
                                print(f"   🎯 Win Rate: {result['win_rate']:.1f}%")
                                print(f"   📊 Trades: {result['trades']}")
                                print()
                    else:
                        print("🔧 Backtest comparativo - JSON mode TODO")
                elif choice == "13":
                    # Analisi performance dettagliata
                    if self.optimizer_mode == "autonomous":
                        print("\n� ANALISI PERFORMANCE DETTAGLIATA")
                        print("="*40)
                        
                        import glob
                        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
                        
                        if not config_files:
                            print("❌ Nessuna configurazione trovata!")
                            print("💡 Genera prima le configurazioni (opzione 6)")
                        else:
                            for config_file in config_files:
                                with open(config_file, 'r', encoding='utf-8') as f:
                                    config = json.load(f)
                                
                                config_name = os.path.basename(config_file).replace('config_autonomous_high_stakes_', '').replace('.json', '')
                                print(f"\n📊 ANALISI: {config_name.upper()}")
                                print("-" * 30)
                                
                                # Parametri ottimizzazione
                                opt_results = config.get('optimization_results', {})
                                risk_params = config.get('risk_parameters', {})
                                symbols = config.get('symbols', {})
                                
                                print(f"🎯 Score ottimizzazione: {opt_results.get('average_optimization_score', 'N/A')}")
                                print(f"💰 Risk percent: {risk_params.get('risk_percent', 0)*100:.1f}%")
                                print(f"📊 Max daily trades: {risk_params.get('max_daily_trades', 'N/A')}")
                                print(f"🔍 Simboli attivi: {len(symbols)}")
                                print(f"📅 Periodo opt: {opt_results.get('optimization_period', 'N/A')}")
                                
                                # Performance simboli
                                print(f"\n🎯 TOP SIMBOLI:")
                                symbol_scores = [(sym, data.get('optimization_score', 0)) 
                                               for sym, data in symbols.items()]
                                symbol_scores.sort(key=lambda x: x[1], reverse=True)
                                
                                for sym, score in symbol_scores[:3]:
                                    print(f"   {sym}: {score:.1f}")
                    else:
                        print("�🔧 Analisi performance - JSON mode TODO")
                elif choice == "14":
                    # Lista configurazioni
                    configs = []
                    if self.optimizer_mode == "autonomous":
                        configs = glob.glob("config_autonomous_high_stakes_*.json")
                    else:
                        configs = glob.glob("config_high_stakes_*.json")
                    
                    if configs:
                        print(f"📋 Trovate {len(configs)} configurazioni ({self.optimizer_mode}):")
                        for config in configs:
                            print(f"   📄 {os.path.basename(config)}")
                    else:
                        print("❌ Nessuna configurazione trovata per modalità {self.optimizer_mode}")
                elif choice == "15":
                    # Auto-discovery file JSON
                    print("\n🔍 AUTO-DISCOVERY FILE JSON")
                    print("="*30)
                    
                    search_patterns = [
                        "*.json",
                        "*config*.json", 
                        "*the5ers*.json",
                        "*phoenix*.json"
                    ]
                    
                    found_files = []
                    for pattern in search_patterns:
                        files = glob.glob(os.path.join(self.base_dir, pattern))
                        found_files.extend(files)
                    
                    # Rimuovi duplicati e ordina
                    unique_files = list(set(found_files))
                    unique_files.sort()
                    
                    if unique_files:
                        print(f"📋 Trovati {len(unique_files)} file JSON:")
                        for i, file_path in enumerate(unique_files, 1):
                            filename = os.path.basename(file_path)
                            size = os.path.getsize(file_path)
                            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            
                            # Determina tipo
                            file_type = "❓ Unknown"
                            if "autonomous" in filename:
                                file_type = "🚀 Autonomous"
                            elif "config" in filename:
                                file_type = "⚙️ Config"
                            elif "high_stakes" in filename:
                                file_type = "🎯 High Stakes"
                            
                            print(f"   {i:2d}. {filename}")
                            print(f"       📊 {size} bytes, {mod_time.strftime('%d/%m %H:%M')}")
                            print(f"       🏷️ {file_type}")
                    else:
                        print("❌ Nessun file JSON trovato nella directory corrente")
                        
                elif choice == "16":
                    # Report configurazione attuale
                    mode_info = f"Modalità: {self.optimizer_mode.upper()}"
                    
                    print(f"\n📊 REPORT CONFIGURAZIONE ATTUALE")
                    print("="*40)
                    print(f"🎯 {mode_info}")
                    
                    if self.current_config:
                        config_name = os.path.basename(self.current_config)
                        print(f"📄 Config attiva: {config_name}")
                        
                        # Leggi dettagli configurazione
                        try:
                            with open(self.current_config, 'r', encoding='utf-8') as f:
                                config_data = json.load(f)
                            
                            # Mostra informazioni chiave
                            metadata = config_data.get('metadata', {})
                            risk_params = config_data.get('risk_parameters', {})
                            symbols = config_data.get('symbols', {})
                            
                            print(f"📅 Creato: {metadata.get('creation_date', 'N/A')}")
                            print(f"🔧 Versione: {metadata.get('version', 'N/A')}")
                            print(f"💰 Risk percent: {risk_params.get('risk_percent', 0)*100:.1f}%")
                            print(f"📊 Max daily trades: {risk_params.get('max_daily_trades', 'N/A')}")
                            print(f"🎯 Simboli configurati: {len(symbols)}")
                            
                            if symbols:
                                print(f"📋 Simboli: {', '.join(list(symbols.keys())[:5])}{'...' if len(symbols) > 5 else ''}")
                            
                        except Exception as e:
                            print(f"❌ Errore lettura config: {e}")
                    else:
                        print(f"❌ Nessuna configurazione caricata")
                        
                        # Suggerimenti
                        if self.optimizer_mode == "autonomous":
                            print("💡 Genera configurazioni: opzione 6")
                        else:
                            print("💡 Seleziona config JSON: opzione 2")
                        "*phoenix*.json"
                    ]
                    
                    found_files = []
                    for pattern in search_patterns:
                        files = glob.glob(os.path.join(self.base_dir, pattern))
                        found_files.extend(files)
                    
                    # Rimuovi duplicati e ordina
                    unique_files = list(set(found_files))
                    unique_files.sort()
                    
                    if unique_files:
                        print(f"� Trovati {len(unique_files)} file JSON:")
                        for i, file_path in enumerate(unique_files, 1):
                            filename = os.path.basename(file_path)
                            size = os.path.getsize(file_path)
                            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            
                            # Determina tipo
                            file_type = "❓ Unknown"
                            if "autonomous" in filename:
                                file_type = "🚀 Autonomous"
                            elif "config" in filename:
                                file_type = "⚙️ Config"
                            elif "high_stakes" in filename:
                                file_type = "🎯 High Stakes"
                            
                            print(f"   {i:2d}. {filename}")
                            print(f"       📊 {size} bytes, {mod_time.strftime('%d/%m %H:%M')}")
                            print(f"       🏷️ {file_type}")
                    else:
                        print("❌ Nessun file JSON trovato nella directory corrente")
                        
                elif choice == "17":
                    # Switch configurazione dinamica
                    print("\n🔄 SWITCH CONFIGURAZIONE DINAMICA")
                    print("="*40)
                    
                    if self.optimizer_mode == "autonomous":
                        import glob
                        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
                        
                        if not config_files:
                            print("❌ Nessuna configurazione autonoma trovata!")
                        else:
                            print("📋 Configurazioni disponibili:")
                            for i, config_file in enumerate(config_files, 1):
                                filename = os.path.basename(config_file)
                                config_name = filename.replace('config_autonomous_high_stakes_', '').replace('.json', '')
                                print(f"   {i}. {config_name.upper()}")
                            
                            choice_idx = input(f"👉 Scegli configurazione (1-{len(config_files)}): ").strip()
                            try:
                                idx = int(choice_idx) - 1
                                if 0 <= idx < len(config_files):
                                    selected_config = config_files[idx]
                                    self.current_config = selected_config
                                    config_name = os.path.basename(selected_config)
                                    print(f"✅ Configurazione attiva: {config_name}")
                                else:
                                    print("❌ Selezione non valida")
                            except ValueError:
                                print("❌ Inserire un numero valido")
                    else:
                        print("🔧 Switch dinamico disponibile per modalità JSON")
                        if self.optimizer:
                            self.select_source_config()
                elif choice == "18":
                    # Analisi Position Sizing Avanzata
                    print("\n� ANALISI POSITION SIZING AVANZATA")
                    print("="*45)
                    
                    if self.optimizer_mode == "autonomous" and self.autonomous_optimizer:
                        account_balance = input("💰 Account Balance (default: €5000): ").strip()
                        balance = float(account_balance) if account_balance else 5000
                        
                        risk_percentages = [0.003, 0.005, 0.007, 0.009, 0.012]
                        
                        print(f"\n📊 ANALISI POSITION SIZING per Account €{balance}")
                        print("-" * 50)
                        
                        for risk_pct in risk_percentages:
                            risk_amount = balance * risk_pct
                            max_loss_trade = risk_amount
                            daily_risk = risk_amount * 6  # max 6 trades/day
                            
                            print(f"🎯 Risk {risk_pct*100:.1f}%:")
                            print(f"   💰 Risk per trade: €{risk_amount:.2f}")
                            print(f"   ⛔ Max loss/trade: €{max_loss_trade:.2f}")
                            print(f"   📊 Risk giornaliero: €{daily_risk:.2f}")
                            print(f"   📈 Compliance: {'✅' if daily_risk <= balance*0.05 else '❌'}")
                            print()
                    else:
                        print("❌ Richiede modalità autonoma attiva")
                        
                elif choice == "19":
                    # Analisi simboli multi-timeframe
                    print("\n� ANALISI SIMBOLI MULTI-TIMEFRAME")
                    print("="*40)
                    
                    if self.optimizer_mode == "autonomous" and self.autonomous_optimizer:
                        symbols = self.autonomous_optimizer.available_symbols
                        
                        print("📊 SIMBOLI DISPONIBILI E CARATTERISTICHE:")
                        print("-" * 45)
                        
                        symbol_analysis = {
                            'EURUSD': {'volatility': 'Bassa', 'spread': 'Ottimo', 'sessioni': 'London, NY'},
                            'USDJPY': {'volatility': 'Bassa', 'spread': 'Buono', 'sessioni': 'Tokyo, London'},
                            'GBPUSD': {'volatility': 'Media', 'spread': 'Buono', 'sessioni': 'London'},
                            'USDCHF': {'volatility': 'Bassa', 'spread': 'Buono', 'sessioni': 'London'},
                            'AUDUSD': {'volatility': 'Media', 'spread': 'Medio', 'sessioni': 'Sydney, Tokyo'},
                            'XAUUSD': {'volatility': 'Alta', 'spread': 'Medio', 'sessioni': 'London, NY'},
                            'NAS100': {'volatility': 'Molto Alta', 'spread': 'Alto', 'sessioni': 'NY'},
                            'GBPJPY': {'volatility': 'Molto Alta', 'spread': 'Medio', 'sessioni': 'London, Tokyo'}
                        }
                        
                        for symbol in symbols[:8]:  # Top 8
                            analysis = symbol_analysis.get(symbol, {'volatility': 'Media', 'spread': 'Medio', 'sessioni': 'London, NY'})
                            print(f"🎯 {symbol}:")
                            print(f"   📈 Volatilità: {analysis['volatility']}")
                            print(f"   💰 Spread: {analysis['spread']}")
                            print(f"   ⏰ Sessioni: {analysis['sessioni']}")
                            print()
                    else:
                        print("❌ Richiede modalità autonoma attiva")
                        
                elif choice == "20":
                    # Test compliance The5ers
                    print("\n🏆 TEST COMPLIANCE THE5ERS")
                    print("="*35)
                    
                    if self.optimizer_mode == "autonomous":
                        import glob
                        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
                        
                        if not config_files:
                            print("❌ Nessuna configurazione trovata!")
                        else:
                            print("� Testando compliance High Stakes Challenge...")
                            print()
                            
                            for config_file in config_files:
                                with open(config_file, 'r', encoding='utf-8') as f:
                                    config = json.load(f)
                                
                                config_name = os.path.basename(config_file).replace('config_autonomous_high_stakes_', '').replace('.json', '')
                                
                                # Test parametri
                                risk_params = config.get('risk_parameters', {})
                                high_stakes = config.get('high_stakes_challenge', {})
                                
                                risk_pct = risk_params.get('risk_percent', 0)
                                daily_trades = risk_params.get('max_daily_trades', 0)
                                account_balance = high_stakes.get('account_balance', 5000)
                                target_profit = high_stakes.get('target_daily_profit', 25)
                                
                                # Calcoli compliance
                                daily_risk = risk_pct * account_balance * daily_trades
                                max_daily_loss = account_balance * 0.05  # 5%
                                compliance_risk = daily_risk <= max_daily_loss
                                compliance_target = target_profit >= 25
                                
                                status = "✅ COMPLIANT" if (compliance_risk and compliance_target) else "❌ NON COMPLIANT"
                                
                                print(f"🎯 {config_name.upper()}: {status}")
                                print(f"   💰 Risk giornaliero: €{daily_risk:.2f} (max €{max_daily_loss:.2f})")
                                print(f"   🎯 Target profit: €{target_profit} (min €25)")
                                print(f"   📊 Risk/trade: {risk_pct*100:.1f}%")
                                print()
                    else:
                        print("❌ Test compliance solo per modalità autonoma")
                        
                elif choice == "21":
                    # Diagnostica sistema completa
                    print("\n� DIAGNOSTICA SISTEMA COMPLETA")
                    print("="*35)
                    
                    print("🔍 Controllo componenti sistema...")
                    print()
                    
                    # Check files
                    core_files = [
                        'autonomous_high_stakes_optimizer.py',
                        'high_stakes_optimizer.py',
                        'PRO-THE5ERS-QM-PHOENIX-GITCOP.py'
                    ]
                    
                    print("📁 FILE CORE:")
                    for filename in core_files:
                        filepath = os.path.join(self.base_dir, filename)
                        exists = os.path.exists(filepath)
                        status = "✅" if exists else "❌"
                        print(f"   {status} {filename}")
                    
                    print()
                    
                    # Check configurazioni
                    config_patterns = [
                        'config_autonomous_high_stakes_*.json',
                        'config_high_stakes_*.json',
                        '*config*.json'
                    ]
                    
                    print("⚙️ CONFIGURAZIONI:")
                    total_configs = 0
                    for pattern in config_patterns:
                        files = glob.glob(os.path.join(self.base_dir, pattern))
                        total_configs += len(files)
                        print(f"   📊 {pattern}: {len(files)} file")
                    
                    print(f"   📋 Totale configurazioni: {total_configs}")
                    print()
                    
                    # Check optimizer status
                    print("🎯 STATUS OPTIMIZER:")
                    print(f"   🔧 Modalità: {self.optimizer_mode.upper()}")
                    print(f"   🚀 Autonomo: {'✅' if self.autonomous_optimizer else '❌'}")
                    print(f"   📁 JSON-based: {'✅' if self.optimizer else '❌'}")
                    print(f"   📊 Config attiva: {'✅' if self.current_config else '❌'}")
                    
                elif choice == "22":
                    # Documentazione integrata
                    print("\n📚 DOCUMENTAZIONE INTEGRATA")
                    print("="*35)
                    
                    print("📖 GUIDE DISPONIBILI:")
                    print("1. 🚀 Guida Modalità Autonoma")
                    print("2. 📁 Guida Modalità JSON") 
                    print("3. 🎯 High Stakes Challenge Rules")
                    print("4. ⚙️ Parametri Ottimizzazione")
                    print("5. 🔧 Troubleshooting")
                    
                    doc_choice = input("\n👉 Scegli guida (1-5): ").strip()
                    
                    if doc_choice == "1":
                        print("\n🚀 GUIDA MODALITÀ AUTONOMA")
                        print("="*30)
                        print("La modalità autonoma genera configurazioni DA ZERO senza")
                        print("richiedere file JSON sorgente. Utilizza:")
                        print("• Algoritmo PRO-THE5ERS-QM-PHOENIX-GITCOP.py")
                        print("• Dati storici MT5")
                        print("• Ottimizzazione parametrica automatica")
                        print("• Grid search su simboli e parametri")
                        print("\n✅ VANTAGGI:")
                        print("• Non serve file JSON esistente")
                        print("• Ottimizzazione completa automatica")
                        print("• 3 livelli aggressività generati")
                        print("• Selezione simboli ottimale")
                        
                    elif doc_choice == "3":
                        print("\n🎯 HIGH STAKES CHALLENGE RULES")
                        print("="*35)
                        print("📊 PARAMETRI CHALLENGE:")
                        print("• Account: €5,000")
                        print("• Target giornaliero: €25 (0.5%)")
                        print("• Giorni validazione: 3 giorni")
                        print("• Max loss giornaliero: €250 (5%)")
                        print("• Dopo validazione: target illimitato")
                        print("\n✅ COMPLIANCE REQUIREMENTS:")
                        print("• Risk per trade: max 1.2%")
                        print("• Max trades giornalieri: ≤8")
                        print("• Gestione drawdown: <8%")
                        print("• News filter: attivo")
                    
                    else:
                        print("💡 Guida non ancora implementata")
                elif choice == "23":
                    # Reset configurazione
                    self.optimizer = None
                    self.autonomous_optimizer = None
                    self.current_config = None
                    self.optimizer_mode = "autonomous"
                    print("✅ Configurazione optimizer resettata (modalità autonoma)")
                elif choice == "24":
                    print("🔧 Salva config - TODO")
                elif choice == "25":
                    print("👋 Launcher terminato.")
                    break
                else:
                    print("❌ Opzione non valida. Scegli un numero da 1 a 25.")
                
                if choice != "25":
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
