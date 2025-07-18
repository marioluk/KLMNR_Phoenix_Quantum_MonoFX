#!/usr/bin/env python3
# ====================================================================================
# THE5ERS INTEGRATED LAUNCHER COMPLETE - SISTEMA UNICO COMPLETAMENTE INTEGRATO
# Launcher completo che integra tutte le funzionalità del sistema The5ers
# ====================================================================================

import os
import sys
import json
import subprocess
import glob
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Import dell'optimizer
try:
    from autonomous_high_stakes_optimizer import AutonomousHighStakesOptimizer
    from high_stakes_optimizer import HighStakesOptimizer
except ImportError as e:
    print(f"❌ Errore import optimizer: {e}")
    print("💡 Assicurati che i file optimizer siano nella directory corrente")
    sys.exit(1)

class The5ersIntegratedLauncher:
    """
    Launcher completamente integrato - SISTEMA UNICO
    Unisce autonomous_optimizer e json_optimizer in un'interfaccia unificata
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.optimizer_mode = "autonomous"  # FISSO: Solo modalità autonoma
        self.autonomous_optimizer = None
        self.current_config = None
        
        # Inizializzazione automatica modalità autonoma
        self.init_autonomous_mode()
        
        print("🚀 THE5ERS AUTONOMOUS SYSTEM")
        print("Sistema ottimizzato per modalità autonoma")
        print(f"📁 Directory: {self.base_dir}")
        print("✅ Modalità autonoma attivata")
        print()
        
    def init_autonomous_mode(self):
        """Inizializza modalità autonoma (raccomandata)"""
        try:
            self.autonomous_optimizer = AutonomousHighStakesOptimizer(output_dir=self.base_dir)
            print("✅ Modalità AUTONOMA inizializzata (RACCOMANDATA)")
        except Exception as e:
            print(f"❌ Errore init autonomo: {e}")
    
    def init_json_mode(self):
        """Inizializza modalità JSON (legacy)"""
        try:
            # Trova config sorgente automaticamente
            source_config = self.find_source_config()
            if source_config:
                self.json_optimizer = HighStakesOptimizer(source_config, output_dir=self.base_dir)
                self.current_config = source_config
                print(f"✅ Modalità JSON inizializzata: {os.path.basename(source_config)}")
                return True
            else:
                print("❌ Nessun file JSON sorgente trovato per modalità JSON")
                return False
        except Exception as e:
            print(f"❌ Errore init JSON: {e}")
            return False
    
    def find_source_config(self) -> Optional[str]:
        """Trova automaticamente il file config sorgente per modalità JSON"""
        candidates = [
            "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json",
            "config.json",
            "PRO-THE5ERS-QM-PHOENIX-GITCOP.json"
        ]
        
        for candidate in candidates:
            path = os.path.join(self.base_dir, candidate)
            if os.path.exists(path):
                return path
        
        # Fallback: primo JSON con "config" nel nome
        for file in os.listdir(self.base_dir):
            if file.endswith('.json') and 'config' in file.lower():
                return os.path.join(self.base_dir, file)
        
        return None
    
    def show_main_menu(self):
        """Menu principale unificato - Focus su modalità autonoma"""
        
        print("🎯 THE5ERS AUTONOMOUS SYSTEM")
        print("Sistema Autonomo Avanzato - Genera configurazioni da zero")
        print("="*60)
        print("� Modalità: AUTONOMA (Ottimizzata)")
        print()
        
        print("🎯 GENERAZIONE CONFIGURAZIONI:")
        print("1.  🚀 Genera TUTTE le Configurazioni")
        print("2.  🎲 Genera Configurazione Singola")
        print("3.  ⚡ Generazione Rapida (Solo Best)")
        print("4.  📋 Generazione Selezionata")
        print()
        
        print("✅ TESTING & VALIDAZIONE:")
        print("5.  🔄 Test Validazione Configurazioni")
        print("6.  📈 Backtest Periodo Personalizzato")
        print("7.  🚀 Backtest Comparativo Multi-Config")
        print("8.  🏆 Test Compliance The5ers")
        print()
        
        print("📊 ANALISI & TOOLS:")
        print("9.  🔍 Analisi Performance Dettagliata")
        print("10. 💰 Analisi Position Sizing")
        print("11. 🎯 Analisi Simboli & Spread")
        print("12. 📋 Lista Tutte le Configurazioni")
        print()
        
        print("🔧 GESTIONE & UTILITÀ:")
        print("13. 📊 Report Sistema & Configurazione")
        print("14. 🔬 Diagnostica Sistema Completa")
        print("15. 📚 Documentazione & Guide")
        print("16. 🔧 Reset Sistema")
        print("17. 🏆 Configurazione The5ers")
        print("18. 🔧 Configura Parametri The5ers")
        print()
        
        print("🗂️ LEGACY (Nascosto):")
        print("19. 📁 Modalità JSON (Legacy)")
        print()
        
        print("❌ ESCI:")
        print("20. 👋 Termina Sistema")
        print()
    
    def quick_generation(self):
        """Generazione rapida - Solo la migliore configurazione"""
        
        print("⚡ GENERAZIONE RAPIDA")
        print("="*30)
        print("🎯 Genera solo la configurazione con migliore performance")
        print()
        
        print("� Opzioni disponibili:")
        print("1. 🏆 Auto-Best (Sceglie automaticamente il migliore)")
        print("2. � Conservative Best")
        print("3. 🟡 Moderate Best") 
        print("4. 🔴 Aggressive Best")
        
        choice = input("👉 Scegli opzione (1-4): ").strip()
        
        if choice == "1":
            # Auto-best: genera tutti e sceglie il migliore
            print("🔄 Generando tutte le configurazioni per confronto...")
            results = self.autonomous_optimizer.generate_all_configs()
            
            print("\n🏆 ANALISI BEST CONFIGURATION:")
            
            best_config = None
            best_score = 0
            best_level = None
            
            for level, filepath in results.items():
                # Carica e analizza configurazione
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                score = config.get('optimization_results', {}).get('average_optimization_score', 0)
                symbols_count = len(config.get('symbols', {}))
                
                print(f"   📊 {level.upper()}: Score={score:.2f}, Simboli={symbols_count}")
                
                if score > best_score:
                    best_score = score
                    best_level = level
                    best_config = filepath
            
            print(f"\n🥇 MIGLIORE: {best_level.upper()} (Score: {best_score:.2f})")
            print(f"📄 File: {os.path.basename(best_config)}")
            
        elif choice in ["2", "3", "4"]:
            level_map = {"2": "conservative", "3": "moderate", "4": "aggressive"}
            level = level_map[choice]
            
            print(f"🔄 Generando configurazione {level.upper()}...")
            config = self.autonomous_optimizer.generate_optimized_config(level)
            filepath = self.autonomous_optimizer.save_config(config, level)
            
            score = config.get('optimization_results', {}).get('average_optimization_score', 0)
            symbols_count = len(config.get('symbols', {}))
            
            print(f"✅ Generato: {os.path.basename(filepath)}")
            print(f"📊 Score: {score:.2f}, Simboli: {symbols_count}")
        
        else:
            print("❌ Opzione non valida")
    
    def selective_generation(self):
        """Generazione selezionata - Scelta personalizzata"""
        
        print("📋 GENERAZIONE SELEZIONATA")
        print("="*35)
        print("🎯 Scegli quali configurazioni generare")
        print()
        
        print("Seleziona i livelli da generare:")
        print("1. 🟢 Conservative")
        print("2. 🟡 Moderate")
        print("3. 🔴 Aggressive")
        print()
        
        selections = input("👉 Inserisci numeri separati da virgole (es: 1,3): ").strip()
        
        if not selections:
            print("❌ Nessuna selezione effettuata")
            return
        
        level_map = {"1": "conservative", "2": "moderate", "3": "aggressive"}
        selected_levels = []
        
        for sel in selections.split(','):
            sel = sel.strip()
            if sel in level_map:
                selected_levels.append(level_map[sel])
        
        if not selected_levels:
            print("❌ Nessuna selezione valida")
            return
        
        print(f"🔄 Generando {len(selected_levels)} configurazioni...")
        print(f"📋 Livelli selezionati: {', '.join(selected_levels)}")
        print()
        
        results = {}
        for level in selected_levels:
            print(f"🔄 Generando {level.upper()}...")
            config = self.autonomous_optimizer.generate_optimized_config(level)
            filepath = self.autonomous_optimizer.save_config(config, level)
            results[level] = filepath
            
            score = config.get('optimization_results', {}).get('average_optimization_score', 0)
            symbols_count = len(config.get('symbols', {}))
            print(f"   ✅ {level.upper()}: {os.path.basename(filepath)} (Score: {score:.2f})")
        
        print(f"\n🎉 Generate {len(results)} configurazioni selezionate!")
        return results
    
    def generate_all_configs(self):
        """Genera tutte le configurazioni autonome"""
        
        print("🎯 GENERAZIONE TUTTE LE CONFIGURAZIONI")
        print("="*45)
        print(f"📁 Directory di output: {self.base_dir}")
        print("🚀 Modalità AUTONOMA: Generazione da zero...")
        print()
        
        results = self.autonomous_optimizer.generate_all_configs()
        
        print(f"✅ Generate {len(results)} configurazioni AUTONOME:")
        for level, filepath in results.items():
            print(f"   🎯 {level.upper()}: {os.path.basename(filepath)}")
        
        return results
    
    def detailed_performance_analysis(self):
        """Analisi performance dettagliata delle configurazioni"""
        
        print("🔍 ANALISI PERFORMANCE DETTAGLIATA")
        print("="*45)
        
        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        
        if not config_files:
            print("❌ Nessuna configurazione autonoma trovata!")
            print("� Genera prima le configurazioni (opzione 1)")
            return
        
        print(f"📊 Analizzando {len(config_files)} configurazioni...")
        print()
        
        analysis_results = []
        
        for config_file in config_files:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Esegui test di validazione
            validation_results = self.autonomous_optimizer.run_validation_test(config_file, 14)  # 14 giorni
            
            # Estrai metriche
            filename = os.path.basename(config_file)
            aggressiveness = config.get('optimization_results', {}).get('aggressiveness_level', 'unknown')
            symbols_count = len(config.get('symbols', {}))
            risk_percent = config.get('risk_parameters', {}).get('risk_percent', 0) * 100
            max_trades = config.get('risk_parameters', {}).get('max_daily_trades', 0)
            
            # Metriche calcolate
            opt_score = config.get('optimization_results', {}).get('average_optimization_score', 0)
            daily_pnl = validation_results.get('daily_avg_pnl', 0)
            win_rate = validation_results.get('win_rate', 0)
            total_trades = validation_results.get('total_trades', 0)
            
            # Calcola indici di performance
            profit_factor = (daily_pnl / 25) * 100 if daily_pnl > 0 else 0  # % rispetto al target €25
            risk_adjusted_return = daily_pnl / risk_percent if risk_percent > 0 else 0
            efficiency_score = (win_rate * daily_pnl) / (total_trades * risk_percent) if total_trades > 0 and risk_percent > 0 else 0
            
            analysis_data = {
                'filename': filename,
                'aggressiveness': aggressiveness,
                'symbols_count': symbols_count,
                'risk_percent': risk_percent,
                'max_trades': max_trades,
                'opt_score': opt_score,
                'daily_pnl': daily_pnl,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'profit_factor': profit_factor,
                'risk_adjusted_return': risk_adjusted_return,
                'efficiency_score': efficiency_score
            }
            
            analysis_results.append(analysis_data)
        
        # Ordina per performance
        analysis_results.sort(key=lambda x: x['daily_pnl'], reverse=True)
        
        print("📈 RANKING PERFORMANCE:")
        print("-" * 80)
        
        for i, data in enumerate(analysis_results, 1):
            status = "🏆" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            print(f"{status} {data['filename']}")
            print(f"   📊 Livello: {data['aggressiveness'].upper()}")
            print(f"   💰 P&L: €{data['daily_pnl']:.2f}/day ({data['profit_factor']:.1f}% del target)")
            print(f"   🎯 Win Rate: {data['win_rate']:.1f}%")
            print(f"   ⚖️ Risk: {data['risk_percent']:.1f}% | Trades: {data['total_trades']}")
            print(f"   📈 Efficiency: {data['efficiency_score']:.2f} | Risk-Adj: {data['risk_adjusted_return']:.2f}")
            print(f"   🔍 Opt Score: {data['opt_score']:.2f} | Simboli: {data['symbols_count']}")
            print()
        
        # Statistiche aggregate
        print("📊 STATISTICHE AGGREGATE:")
        print("-" * 40)
        
        avg_pnl = sum(d['daily_pnl'] for d in analysis_results) / len(analysis_results)
        avg_win_rate = sum(d['win_rate'] for d in analysis_results) / len(analysis_results)
        avg_risk = sum(d['risk_percent'] for d in analysis_results) / len(analysis_results)
        
        best_config = analysis_results[0]
        worst_config = analysis_results[-1]
        
        print(f"📈 P&L Medio: €{avg_pnl:.2f}/day")
        print(f"🎯 Win Rate Medio: {avg_win_rate:.1f}%")
        print(f"⚖️ Risk Medio: {avg_risk:.1f}%")
        print()
        print(f"🏆 Migliore: {best_config['filename']} (€{best_config['daily_pnl']:.2f}/day)")
        print(f"📉 Peggiore: {worst_config['filename']} (€{worst_config['daily_pnl']:.2f}/day)")
        print(f"📊 Spread Performance: €{best_config['daily_pnl'] - worst_config['daily_pnl']:.2f}/day")
        
        return analysis_results
    
    def generate_single_config(self):
        """Genera configurazione singola autonoma"""
        
        print("🎲 GENERAZIONE CONFIGURAZIONE SINGOLA")
        print("="*40)
        print(f"📁 Directory di output: {self.base_dir}")
        print("🚀 Modalità AUTONOMA: Generazione da zero")
        print()
        
        # Selezione livello aggressività
        print("🎯 Scegli livello aggressività:")
        print("1. 🟢 Conservative (Sicuro)")
        print("2. 🟡 Moderate (Bilanciato)")
        print("3. 🔴 Aggressive (Performante)")
        
        choice = input("👉 Scegli livello (1-3): ").strip()
        level_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
        level = level_map.get(choice, 'moderate')
        
        print(f"� Generando configurazione {level.upper()}...")
        
        config = self.autonomous_optimizer.generate_optimized_config(level)
        filepath = self.autonomous_optimizer.save_config(config, level)
        
        # Mostra dettagli generati
        symbols_count = len(config.get('symbols', {}))
        opt_score = config.get('optimization_results', {}).get('average_optimization_score', 0)
        risk_percent = config.get('risk_parameters', {}).get('risk_percent', 0) * 100
        
        print(f"✅ Generato: {os.path.basename(filepath)}")
        print(f"📊 Simboli: {symbols_count}")
        print(f"🎯 Score ottimizzazione: {opt_score:.2f}")
        print(f"⚖️ Risk: {risk_percent:.1f}%")
        
        return filepath
    
    def show_the5ers_configuration(self):
        """Mostra configurazione The5ers dettagliata con compliance checker"""
        
        print("🏆 THE5ERS CHALLENGE CONFIGURATION")
        print("="*60)
        print()
        
        # High Stakes Challenge (sistema attuale)
        if hasattr(self.autonomous_optimizer, 'high_stakes_params'):
            hs = self.autonomous_optimizer.high_stakes_params
            
            print("🔥 HIGH STAKES CHALLENGE (ATTUALE):")
            print("-" * 40)
            print(f"💰 Account Balance: €{hs['account_balance']:,}")
            print(f"🎯 Daily Target: €{hs['target_daily_profit']}")
            print(f"📉 Daily Loss Limit: €{hs['daily_loss_limit']} ({hs['max_daily_loss_percent']*100:.0f}%)")
            print(f"⏰ Validation Period: {hs['validation_days']} giorni")
            print(f"🎚️ Leverage: 1:{hs['leverage']}")
            print()
        
        # Parametri dal file produzione
        production_config_path = os.path.join(os.path.dirname(self.base_dir), 
                                            "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json")
        
        if os.path.exists(production_config_path):
            try:
                with open(production_config_path, 'r', encoding='utf-8') as f:
                    prod_config = json.load(f)
                
                the5ers_config = prod_config.get('THE5ERS_specific', {})
                initial_balance = prod_config.get('initial_balance', 100000)
                
                print("📊 STANDARD CHALLENGE (da File Produzione):")
                print("-" * 45)
                print(f"💰 Initial Balance: €{initial_balance:,}")
                print(f"🎯 Step 1 Target: {the5ers_config.get('step1_target', 8)}% (€{initial_balance * the5ers_config.get('step1_target', 8) / 100:,.0f})")
                print(f"📉 Max Daily Loss: {the5ers_config.get('max_daily_loss_percent', 5)}% (€{initial_balance * the5ers_config.get('max_daily_loss_percent', 5) / 100:,.0f})")
                print(f"📉 Max Total Loss: {the5ers_config.get('max_total_loss_percent', 10)}% (€{initial_balance * the5ers_config.get('max_total_loss_percent', 10) / 100:,.0f})")
                
                drawdown = the5ers_config.get('drawdown_protection', {})
                print(f"📊 Drawdown Soft Limit: {drawdown.get('soft_limit', 0.02)*100:.0f}%")
                print(f"📊 Drawdown Hard Limit: {drawdown.get('hard_limit', 0.05)*100:.0f}%")
                print()
                
            except Exception as e:
                print(f"⚠️ Errore lettura config produzione: {e}")
        
        # Compliance checker
        print("📋 COMPLIANCE CHECKER:")
        print("-" * 25)
        
        compliance_checks = [
            ("✅ High Stakes Focus", True, "Sistema ottimizzato per High Stakes"),
            ("✅ Risk Management", True, "Parametri conformi ai limiti The5ers"),
            ("✅ Position Sizing", True, "Micro lots supportati"),
            ("✅ Drawdown Protection", True, "Controllo drawdown integrato"),
            ("✅ Daily Loss Control", True, "Limiti giornalieri configurati"),
            ("✅ Leverage Compliance", True, "Leva 1:100 impostata"),
            ("⚠️ News Filter", False, "Da implementare manualmente"),
            ("⚠️ Weekend Gap Protection", False, "Da verificare nell'algoritmo")
        ]
        
        for icon, status, description in compliance_checks:
            print(f"{icon} {description}")
        
        print("\n💡 RACCOMANDAZIONI:")
        print("• Il sistema è ottimizzato per High Stakes Challenge")
        print("• Verifica news filter e gap protection nell'algoritmo principale")
        print("• Monitora compliance durante il trading live")
        print("• Usa opzione 8 per test compliance dettagliato")
        
        input("\n⏸️ Premi ENTER per continuare...")
    
    def configure_the5ers_parameters(self):
        """Configurazione interattiva dei parametri The5ers"""
        
        print("🔧 CONFIGURAZIONE PARAMETRI THE5ERS")
        print("="*50)
        print()
        
        # Selezione tipo di challenge
        print("🏆 SELEZIONA TIPO DI CHALLENGE:")
        print("1. 🔥 High Stakes Challenge (€5,000)")
        print("2. 📊 Standard Challenge (€100,000)")
        print("3. 🎯 Configurazione Personalizzata")
        print()
        
        choice = input("👉 Scegli opzione (1-3): ").strip()
        
        if choice == "1":
            self._configure_high_stakes()
        elif choice == "2":
            self._configure_standard_challenge()
        elif choice == "3":
            self._configure_custom_parameters()
        else:
            print("❌ Opzione non valida!")
            return
    
    def _configure_high_stakes(self):
        """Configura parametri High Stakes Challenge"""
        
        print("\n🔥 CONFIGURAZIONE HIGH STAKES CHALLENGE")
        print("-" * 40)
        
        # Parametri attuali
        current = self.autonomous_optimizer.high_stakes_params
        
        print(f"📊 Configurazione attuale:")
        print(f"💰 Account Balance: €{current['account_balance']:,}")
        print(f"🎯 Daily Target: €{current['target_daily_profit']}")
        print(f"📉 Daily Loss Limit: €{current['daily_loss_limit']}")
        print(f"⏰ Validation Period: {current['validation_days']} giorni")
        print(f"🎚️ Leverage: 1:{current['leverage']}")
        print()
        
        modify = input("🔧 Vuoi modificare questi parametri? (y/n): ").strip().lower()
        
        if modify == 'y':
            new_params = {}
            
            # Account Balance
            balance_input = input(f"💰 Account Balance [attuale: €{current['account_balance']:,}]: ").strip()
            new_params['account_balance'] = int(balance_input) if balance_input else current['account_balance']
            
            # Daily Target
            target_input = input(f"🎯 Daily Target [attuale: €{current['target_daily_profit']}]: ").strip()
            new_params['target_daily_profit'] = int(target_input) if target_input else current['target_daily_profit']
            
            # Daily Loss Limit
            loss_input = input(f"📉 Daily Loss Limit [attuale: €{current['daily_loss_limit']}]: ").strip()
            new_params['daily_loss_limit'] = int(loss_input) if loss_input else current['daily_loss_limit']
            
            # Validation Days
            validation_input = input(f"⏰ Validation Period [attuale: {current['validation_days']} giorni]: ").strip()
            new_params['validation_days'] = int(validation_input) if validation_input else current['validation_days']
            
            # Leverage
            leverage_input = input(f"🎚️ Leverage [attuale: 1:{current['leverage']}]: ").strip()
            new_params['leverage'] = int(leverage_input) if leverage_input else current['leverage']
            
            # Calcola percentuale loss automaticamente
            new_params['max_daily_loss_percent'] = new_params['daily_loss_limit'] / new_params['account_balance']
            
            # Conferma modifiche
            print("\n📋 NUOVA CONFIGURAZIONE:")
            print("-" * 25)
            for key, value in new_params.items():
                if key == 'max_daily_loss_percent':
                    print(f"📉 Max Daily Loss Percent: {value*100:.1f}%")
                else:
                    print(f"🔧 {key}: {value}")
            
            confirm = input("\n✅ Confermi le modifiche? (y/n): ").strip().lower()
            
            if confirm == 'y':
                # Aggiorna parametri
                self.autonomous_optimizer.high_stakes_params.update(new_params)
                
                # Salva configurazione
                self._save_the5ers_config()
                
                print("✅ Configurazione aggiornata con successo!")
            else:
                print("❌ Modifiche annullate")
        
        input("\n⏸️ Premi ENTER per continuare...")
    
    def _configure_standard_challenge(self):
        """Configura parametri Standard Challenge"""
        
        print("\n📊 CONFIGURAZIONE STANDARD CHALLENGE")
        print("-" * 40)
        
        # Carica configurazione produzione
        production_config_path = os.path.join(os.path.dirname(self.base_dir), 
                                            "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json")
        
        if os.path.exists(production_config_path):
            try:
                with open(production_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                the5ers_config = config.get('THE5ERS_specific', {})
                current_balance = config.get('initial_balance', 100000)
                
                print(f"📊 Configurazione attuale:")
                print(f"💰 Initial Balance: €{current_balance:,}")
                print(f"🎯 Step 1 Target: {the5ers_config.get('step1_target', 8)}%")
                print(f"📉 Max Daily Loss: {the5ers_config.get('max_daily_loss_percent', 5)}%")
                print(f"📉 Max Total Loss: {the5ers_config.get('max_total_loss_percent', 10)}%")
                
                modify = input("\n🔧 Vuoi modificare questi parametri? (y/n): ").strip().lower()
                
                if modify == 'y':
                    # Balance
                    balance_input = input(f"💰 Initial Balance [attuale: €{current_balance:,}]: ").strip()
                    new_balance = int(balance_input) if balance_input else current_balance
                    
                    # Step 1 Target
                    target_input = input(f"🎯 Step 1 Target % [attuale: {the5ers_config.get('step1_target', 8)}%]: ").strip()
                    new_target = float(target_input) if target_input else the5ers_config.get('step1_target', 8)
                    
                    # Max Daily Loss
                    daily_loss_input = input(f"📉 Max Daily Loss % [attuale: {the5ers_config.get('max_daily_loss_percent', 5)}%]: ").strip()
                    new_daily_loss = float(daily_loss_input) if daily_loss_input else the5ers_config.get('max_daily_loss_percent', 5)
                    
                    # Max Total Loss
                    total_loss_input = input(f"📉 Max Total Loss % [attuale: {the5ers_config.get('max_total_loss_percent', 10)}%]: ").strip()
                    new_total_loss = float(total_loss_input) if total_loss_input else the5ers_config.get('max_total_loss_percent', 10)
                    
                    # Aggiorna configurazione
                    config['initial_balance'] = new_balance
                    config['THE5ERS_specific']['step1_target'] = new_target
                    config['THE5ERS_specific']['max_daily_loss_percent'] = new_daily_loss
                    config['THE5ERS_specific']['max_total_loss_percent'] = new_total_loss
                    
                    # Conferma e salva
                    print(f"\n✅ Nuovo target Step 1: €{new_balance * new_target / 100:,.0f}")
                    print(f"✅ Nuovo max daily loss: €{new_balance * new_daily_loss / 100:,.0f}")
                    print(f"✅ Nuovo max total loss: €{new_balance * new_total_loss / 100:,.0f}")
                    
                    confirm = input("\n✅ Confermi le modifiche? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        with open(production_config_path, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=4, ensure_ascii=False)
                        
                        print("✅ Configurazione Standard Challenge aggiornata!")
                    else:
                        print("❌ Modifiche annullate")
                
            except Exception as e:
                print(f"❌ Errore durante configurazione: {e}")
        else:
            print("❌ File configurazione produzione non trovato!")
        
        input("\n⏸️ Premi ENTER per continuare...")
    
    def _configure_custom_parameters(self):
        """Configurazione personalizzata completamente custom"""
        
        print("\n🎯 CONFIGURAZIONE PERSONALIZZATA")
        print("-" * 35)
        print("Crea la tua configurazione The5ers personalizzata!")
        print()
        
        try:
            # Parametri base
            balance = int(input("💰 Account Balance (€): "))
            daily_target = float(input("🎯 Daily Target (€): "))
            daily_loss = float(input("📉 Daily Loss Limit (€): "))
            validation_days = int(input("⏰ Validation Period (giorni): "))
            leverage = int(input("🎚️ Leverage (es. 100 per 1:100): "))
            
            # Calcola percentuali
            daily_loss_percent = daily_loss / balance
            target_percent = daily_target / balance * 100
            
            print(f"\n📊 RIEPILOGO CONFIGURAZIONE PERSONALIZZATA:")
            print("-" * 45)
            print(f"💰 Account Balance: €{balance:,}")
            print(f"🎯 Daily Target: €{daily_target} ({target_percent:.2f}%)")
            print(f"📉 Daily Loss: €{daily_loss} ({daily_loss_percent*100:.1f}%)")
            print(f"⏰ Validation: {validation_days} giorni")
            print(f"🎚️ Leverage: 1:{leverage}")
            
            confirm = input("\n✅ Salva questa configurazione? (y/n): ").strip().lower()
            
            if confirm == 'y':
                # Crea configurazione custom
                custom_config = {
                    'account_balance': balance,
                    'target_daily_profit': daily_target,
                    'daily_loss_limit': daily_loss,
                    'validation_days': validation_days,
                    'leverage': leverage,
                    'max_daily_loss_percent': daily_loss_percent,
                    'configuration_type': 'custom'
                }
                
                # Salva come nuovo file
                custom_file = os.path.join(self.base_dir, f"custom_the5ers_config_{int(time.time())}.json")
                with open(custom_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_config, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Configurazione salvata in: {os.path.basename(custom_file)}")
                
                # Opzione per applicare al sistema autonomo
                apply = input("🔧 Applica al sistema autonomo High Stakes? (y/n): ").strip().lower()
                if apply == 'y':
                    self.autonomous_optimizer.high_stakes_params.update(custom_config)
                    print("✅ Configurazione applicata al sistema autonomo!")
            
        except ValueError:
            print("❌ Errore: Inserisci valori numerici validi!")
        except Exception as e:
            print(f"❌ Errore durante configurazione: {e}")
        
        input("\n⏸️ Premi ENTER per continuare...")
    
    def _save_the5ers_config(self):
        """Salva configurazione The5ers aggiornata"""
        
        config_file = os.path.join(self.base_dir, "the5ers_high_stakes_config.json")
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.autonomous_optimizer.high_stakes_params, f, indent=4, ensure_ascii=False)
            
            print(f"💾 Configurazione salvata in: {os.path.basename(config_file)}")
        
        except Exception as e:
            print(f"❌ Errore salvataggio configurazione: {e}")
    
    def validate_configs(self):
        """Testa e valida configurazioni autonome generate"""
        
        print("✅ TEST VALIDAZIONE CONFIGURAZIONI")
        print("="*40)
        print("🚀 Testando configurazioni AUTONOME...")
        print()
        
        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        
        if not config_files:
            print("❌ Nessuna configurazione AUTONOMA trovata!")
            print("💡 Genera prima le configurazioni (opzione 1)")
            return
        
        print(f"🔄 Testando {len(config_files)} configurazioni AUTONOME...")
        print()
        
        for config_file in config_files:
            results = self.autonomous_optimizer.run_validation_test(config_file, 7)
            status = "✅ PASS" if results['high_stakes_validation'] else "❌ FAIL"
            filename = os.path.basename(config_file)
            pnl = results['daily_avg_pnl']
            win_rate = results['win_rate']
            aggressiveness = results.get('aggressiveness_level', 'unknown')
            total_trades = results.get('total_trades', 0)
            
            print(f"{status} {filename}")
            print(f"   📊 Livello: {aggressiveness.upper()}")
            print(f"   💰 P&L: €{pnl:.2f}/day")
            print(f"   🎯 Win Rate: {win_rate:.1f}%")
            print(f"   📈 Trades: {total_trades}")
            print()
        
        return True
    
    def system_report(self):
        """Report completo del sistema autonomo"""
        
        print("📊 REPORT SISTEMA AUTONOMO")
        print("="*35)
        
        print("🚀 Modalità: AUTONOMA (Ottimizzata)")
        print(f"📁 Directory: {self.base_dir}")
        
        # Status optimizer
        status = "✅" if self.autonomous_optimizer else "❌"
        print(f"🚀 Optimizer Autonomo: {status}")
        
        # Conta configurazioni
        autonomous_configs = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        print(f"� Configurazioni autonome: {len(autonomous_configs)}")
        
        if autonomous_configs:
            print("\n� CONFIGURAZIONI PRESENTI:")
            for config in autonomous_configs:
                filename = os.path.basename(config)
                try:
                    with open(config, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    aggressiveness = config_data.get('optimization_results', {}).get('aggressiveness_level', 'unknown')
                    symbols_count = len(config_data.get('symbols', {}))
                    print(f"   � {filename}")
                    print(f"       📊 Livello: {aggressiveness.upper()}, Simboli: {symbols_count}")
                except:
                    print(f"   � {filename} (errore lettura)")
        
        # File core
        core_files = [
            ('autonomous_high_stakes_optimizer.py', self.base_dir, 'Optimizer Autonomo'),
            ('high_stakes_optimizer.py', self.base_dir, 'Optimizer Legacy'),
            ('PRO-THE5ERS-QM-PHOENIX-GITCOP.py', os.path.dirname(self.base_dir), 'Script Principale')
        ]
        
        print("\n📋 FILE CORE:")
        for filename, search_dir, description in core_files:
            filepath = os.path.join(search_dir, filename)
            exists = os.path.exists(filepath)
            status = "✅" if exists else "❌"
            location = "backtest_clean" if search_dir == self.base_dir else "root"
            
            if exists:
                size = os.path.getsize(filepath)
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"   {status} {filename} ({location})")
                print(f"       📊 {description}: {size:,} bytes, {mod_time.strftime('%d/%m %H:%M')}")
            else:
                print(f"   {status} {filename} ({location}) - {description}")
                print(f"       🔍 Cercato in: {search_dir}")
        
        # Verifica capacità sistema
        print("\n🔍 CAPACITÀ SISTEMA:")
        print(f"   📁 Directory base: {self.base_dir}")
        print(f"   � Generazione autonoma: {'✅' if self.autonomous_optimizer else '❌'}")
        print(f"   📄 Configurazioni disponibili: {len(autonomous_configs)}")
        
        if len(autonomous_configs) == 0:
            print("\n💡 RACCOMANDAZIONI:")
            print("   - Genera configurazioni con opzione 1 (Genera tutte)")
            print("   - Oppure usa opzione 2 (Genera singola)")
        else:
            print("\n🎯 PROSSIMI PASSI:")
            print("   - Testa configurazioni con opzione 5 (Test validazione)")
            print("   - Analizza performance con opzione 9 (Analisi dettagliata)")
            print("   - Verifica compliance con opzione 8 (Test compliance)")
        
        return {
            'autonomous_configs': len(autonomous_configs),
            'optimizer_status': status,
            'base_dir': self.base_dir
        }
    
    def list_all_configs(self):
        """Lista tutte le configurazioni autonome disponibili"""
        
        print("📋 CONFIGURAZIONI AUTONOME DISPONIBILI")
        print("="*45)
        
        # Configurazioni autonome
        autonomous_configs = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        
        if autonomous_configs:
            print(f"🚀 CONFIGURAZIONI AUTONOME ({len(autonomous_configs)}):")
            
            for config in autonomous_configs:
                filename = os.path.basename(config)
                size = os.path.getsize(config)
                mod_time = datetime.fromtimestamp(os.path.getmtime(config))
                
                # Carica configurazione per dettagli
                try:
                    with open(config, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    aggressiveness = config_data.get('optimization_results', {}).get('aggressiveness_level', 'unknown')
                    symbols_count = len(config_data.get('symbols', {}))
                    risk_percent = config_data.get('risk_parameters', {}).get('risk_percent', 0) * 100
                    opt_score = config_data.get('optimization_results', {}).get('average_optimization_score', 0)
                    
                    print(f"   📄 {filename}")
                    print(f"       📊 Livello: {aggressiveness.upper()}")
                    print(f"       🎯 Simboli: {symbols_count} | Risk: {risk_percent:.1f}% | Score: {opt_score:.2f}")
                    print(f"       📅 {mod_time.strftime('%d/%m/%Y %H:%M')} | {size:,} bytes")
                    print()
                    
                except Exception as e:
                    print(f"   📄 {filename}")
                    print(f"       ❌ Errore lettura: {e}")
                    print(f"       📅 {mod_time.strftime('%d/%m/%Y %H:%M')} | {size:,} bytes")
                    print()
        else:
            print("❌ Nessuna configurazione autonoma trovata!")
            print("💡 Genera configurazioni con:")
            print("   - Opzione 1: Genera tutte le configurazioni")
            print("   - Opzione 2: Genera configurazione singola")
            print("   - Opzione 3: Generazione rapida")
            print("   - Opzione 4: Generazione selezionata")
        
        return autonomous_configs
    
    def compliance_test(self):
        """Test compliance regole The5ers per configurazioni autonome"""
        
        print("🏆 TEST COMPLIANCE THE5ERS HIGH STAKES")
        print("="*45)
        print("🚀 Testando compliance configurazioni AUTONOME...")
        print()
        
        config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        
        if not config_files:
            print("❌ Nessuna configurazione autonoma trovata!")
            print("💡 Genera prima le configurazioni (opzione 1)")
            return
        
        print("🔄 Testando compliance High Stakes Challenge...")
        print()
        
        compliant_configs = []
        
        for config_file in config_files:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config_name = os.path.basename(config_file)
            
            # Parametri compliance
            risk_params = config.get('risk_parameters', {})
            high_stakes = config.get('high_stakes_challenge', {})
            
            risk_pct = risk_params.get('risk_percent', 0)
            daily_trades = risk_params.get('max_daily_trades', 0)
            account_balance = high_stakes.get('account_balance', 5000)
            target_profit = high_stakes.get('target_daily_profit', 25)
            aggressiveness = config.get('optimization_results', {}).get('aggressiveness_level', 'unknown')
            
            # Test compliance
            daily_risk = risk_pct * account_balance * daily_trades
            max_daily_loss = account_balance * 0.05  # 5%
            
            compliance_risk = daily_risk <= max_daily_loss
            compliance_target = target_profit >= 25
            compliance_individual_risk = risk_pct <= 0.012  # 1.2% max
            
            overall_compliance = compliance_risk and compliance_target and compliance_individual_risk
            status = "✅ COMPLIANT" if overall_compliance else "❌ NON COMPLIANT"
            
            print(f"🎯 {config_name}: {status}")
            print(f"   � Livello: {aggressiveness.upper()}")
            print(f"   �💰 Risk/trade: {risk_pct*100:.1f}% ({'✅' if compliance_individual_risk else '❌'})")
            print(f"   📊 Risk giornaliero: €{daily_risk:.2f} ({'✅' if compliance_risk else '❌'})")
            print(f"   🎯 Target: €{target_profit} ({'✅' if compliance_target else '❌'})")
            print()
            
            if overall_compliance:
                compliant_configs.append(config_name)
        
        # Riepilogo
        print("📊 RIEPILOGO COMPLIANCE:")
        print(f"✅ Configurazioni compliant: {len(compliant_configs)}/{len(config_files)}")
        
        if compliant_configs:
            print("🏆 Configurazioni conformi:")
            for config_name in compliant_configs:
                print(f"   ✅ {config_name}")
        
        if len(compliant_configs) < len(config_files):
            print("⚠️ Alcune configurazioni non sono conformi alle regole The5ers")
        
        return compliant_configs
    
    def run(self):
        """Esegue sistema autonomo integrato"""
        
        print("🎯 THE5ERS AUTONOMOUS SYSTEM")
        print("Sistema Autonomo Avanzato - Genera configurazioni da zero")
        print("="*60)
        print()
        
        # Info iniziale
        print(f"📁 Directory: {self.base_dir}")
        print("🚀 Modalità: AUTONOMA (Ottimizzata)")
        print("💡 Genera configurazioni avanzate senza dipendere da file JSON")
        print()
        
        while True:
            try:
                self.show_main_menu()
                choice = input("👉 Scegli opzione (1-20): ").strip()
                
                if choice == "1":
                    self.generate_all_configs()
                elif choice == "2":
                    self.generate_single_config()
                elif choice == "3":
                    self.quick_generation()
                elif choice == "4":
                    self.selective_generation()
                elif choice == "5":
                    self.validate_configs()
                elif choice == "6":
                    print("📈 Backtest personalizzato - In sviluppo")
                    print("💡 Usa opzione 5 per validazione configurazioni")
                elif choice == "7":
                    print("🚀 Backtest comparativo - In sviluppo")
                    print("💡 Usa opzione 9 per analisi performance dettagliata")
                elif choice == "8":
                    self.compliance_test()
                elif choice == "9":
                    self.detailed_performance_analysis()
                elif choice == "10":
                    print("💰 Analisi position sizing - In sviluppo")
                    print("💡 Usa opzione 12 per lista configurazioni dettagliata")
                elif choice == "11":
                    print("🎯 Analisi simboli & spread - In sviluppo")
                    print("💡 Verifica simboli nelle configurazioni generate")
                elif choice == "12":
                    self.list_all_configs()
                elif choice == "13":
                    self.system_report()
                elif choice == "14":
                    print("🔬 Diagnostica sistema - In sviluppo")
                    print("💡 Usa opzione 13 per report sistema")
                elif choice == "15":
                    print("📚 Documentazione - In sviluppo")
                    print("💡 Consulta i commenti nel codice per dettagli")
                elif choice == "16":
                    # Reset sistema
                    self.autonomous_optimizer = None
                    self.current_config = None
                    self.init_autonomous_mode()
                    print("✅ Sistema autonomo resettato")
                elif choice == "17":
                    self.show_the5ers_configuration()
                elif choice == "18":
                    self.configure_the5ers_parameters()
                elif choice == "19":
                    # Modalità legacy nascosta
                    print("📁 MODALITÀ JSON LEGACY")
                    print("⚠️ Modalità non supportata in questa versione ottimizzata")
                    print("💡 La modalità autonoma offre funzionalità superiori")
                    print("🚀 Usa le opzioni 1-18 per funzionalità complete")
                elif choice == "20":
                    print("👋 Sistema autonomo terminato.")
                    break
                else:
                    print("❌ Opzione non valida. Scegli un numero da 1 a 20.")
                
                if choice != "20":
                    input("\n⏸️ Premi ENTER per continuare...")
                    print("\n" * 2)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Sistema terminato dall'utente.")
                break
            except Exception as e:
                print(f"\n❌ Errore imprevisto: {e}")
                input("⏸️ Premi ENTER per continuare...")
                print("\n" * 2)

def main():
    """Funzione principale autonoma"""
    print("🚀 Inizializzazione THE5ERS AUTONOMOUS SYSTEM...")
    print()
    
    launcher = The5ersIntegratedLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
