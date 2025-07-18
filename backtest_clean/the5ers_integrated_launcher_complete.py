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
        print("13. � Report Sistema & Configurazione")
        print("14. 🔬 Diagnostica Sistema Completa")
        print("15. 📚 Documentazione & Guide")
        print("16. 🔧 Reset Sistema")
        print()
        
        print("🗂️ LEGACY (Nascosto):")
        print("17. 📁 Modalità JSON (Legacy)")
        print()
        
        print("❌ ESCI:")
        print("18. 👋 Termina Sistema")
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
                choice = input("👉 Scegli opzione (1-18): ").strip()
                
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
                    # Modalità legacy nascosta
                    print("📁 MODALITÀ JSON LEGACY")
                    print("⚠️ Modalità non supportata in questa versione ottimizzata")
                    print("💡 La modalità autonoma offre funzionalità superiori")
                    print("🚀 Usa le opzioni 1-16 per funzionalità complete")
                elif choice == "18":
                    print("👋 Sistema autonomo terminato.")
                    break
                else:
                    print("❌ Opzione non valida. Scegli un numero da 1 a 18.")
                
                if choice != "18":
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
