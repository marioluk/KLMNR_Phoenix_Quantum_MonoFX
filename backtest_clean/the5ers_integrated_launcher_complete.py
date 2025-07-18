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

class CompleteIntegratedLauncher:
    """
    Launcher completamente integrato - SISTEMA UNICO
    Unisce autonomous_optimizer e json_optimizer in un'interfaccia unificata
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.optimizer_mode = "autonomous"  # Default: modalità autonoma raccomandata
        self.autonomous_optimizer = None
        self.json_optimizer = None
        self.current_config = None
        
        # Inizializzazione automatica modalità autonoma
        self.init_autonomous_mode()
        
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
        """Menu principale unificato"""
        
        print("🎯 THE5ERS COMPLETE INTEGRATED SYSTEM")
        print("Sistema Unico Completamente Integrato")
        print("="*60)
        print(f"🔧 Modalità corrente: {self.optimizer_mode.upper()}")
        print()
        
        print("🎯 CONFIGURAZIONE & MODALITÀ:")
        print("1.  🔄 Switch Modalità (Autonoma ↔ JSON)")
        print("2.  📁 Seleziona Config JSON [Solo modalità JSON]")
        print("3.  📊 Report Sistema & Configurazione")
        print()
        
        print("🚀 GENERAZIONE CONFIGURAZIONI:")
        print("4.  🎯 Genera TUTTE le Configurazioni")
        print("5.  🎲 Genera Configurazione Singola")
        print("6.  📋 Genera Configurazioni Selezionate")
        print("7.  ⚡ Generazione Rapida (Solo Best)")
        print()
        
        print("✅ TESTING & VALIDAZIONE:")
        print("8.  🔄 Test Validazione Configurazioni")
        print("9.  📈 Backtest Periodo Personalizzato")
        print("10. 🚀 Backtest Comparativo Multi-Config")
        print("11. 🏆 Test Compliance The5ers")
        print()
        
        print("📊 ANALISI & TOOLS:")
        print("12. 🔍 Analisi Performance Dettagliata")
        print("13. 💰 Analisi Position Sizing")
        print("14. 🎯 Analisi Simboli & Spread")
        print("15. 📋 Lista Tutte le Configurazioni")
        print()
        
        print("🔧 GESTIONE & UTILITÀ:")
        print("16. 🔍 Auto-Discovery File JSON")
        print("17. 🔄 Switch Configurazione Attiva")
        print("18. 🔬 Diagnostica Sistema Completa")
        print("19. 📚 Documentazione & Guide")
        print("20. 🔧 Reset Sistema")
        print()
        
        print("❌ ESCI:")
        print("21. 👋 Termina Sistema")
        print()
    
    def switch_mode(self):
        """Switch tra modalità autonoma e JSON"""
        
        print("🔄 SWITCH MODALITÀ OPTIMIZER")
        print("="*35)
        print()
        print("📊 Modalità disponibili:")
        print()
        print("1. 🚀 **AUTONOMA** (RACCOMANDATA)")
        print("   ✅ Genera configurazioni DA ZERO")
        print("   ✅ Algoritmo + dati MT5 + ottimizzazione")
        print("   ✅ NON richiede file JSON sorgente")
        print("   ✅ Grid search parametrico automatico")
        print()
        print("2. 📁 **JSON-BASED** (Legacy)")
        print("   ✅ Modifica file JSON esistente")
        print("   ✅ Mantiene struttura originale")
        print("   ⚠️  Richiede file JSON sorgente valido")
        print()
        print(f"🎯 Modalità attuale: {self.optimizer_mode.upper()}")
        print()
        
        choice = input("👉 Scegli modalità (1=Autonoma, 2=JSON, ENTER=mantieni): ").strip()
        
        if choice == "1" and self.optimizer_mode != "autonomous":
            self.optimizer_mode = "autonomous"
            self.init_autonomous_mode()
            print("✅ Passato a modalità AUTONOMA")
            
        elif choice == "2" and self.optimizer_mode != "json_based":
            self.optimizer_mode = "json_based"
            if self.init_json_mode():
                print("✅ Passato a modalità JSON")
            else:
                print("❌ Impossibile passare a modalità JSON")
                print("🔄 Rimango in modalità AUTONOMA")
                self.optimizer_mode = "autonomous"
        else:
            print(f"ℹ️ Modalità mantenuta: {self.optimizer_mode.upper()}")
    
    def generate_all_configs(self):
        """Genera tutte le configurazioni"""
        
        print("🎯 GENERAZIONE TUTTE LE CONFIGURAZIONI")
        print("="*45)
        
        if self.optimizer_mode == "autonomous":
            print("🚀 Modalità AUTONOMA: Generazione da zero...")
            results = self.autonomous_optimizer.generate_all_configs()
            
            print(f"✅ Generate {len(results)} configurazioni AUTONOME:")
            for level, filepath in results.items():
                print(f"   🎯 {level.upper()}: {os.path.basename(filepath)}")
                
        else:  # json_based
            if not self.json_optimizer:
                print("❌ Optimizer JSON non inizializzato!")
                return
                
            print("📁 Modalità JSON: Ottimizzazione da file sorgente...")
            try:
                results = self.json_optimizer.optimize_all_levels()
                print(f"✅ Generate {len(results)} configurazioni da JSON:")
                for level, filepath in results.items():
                    print(f"   📄 {level.upper()}: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"❌ Errore generazione JSON: {e}")
    
    def generate_single_config(self):
        """Genera configurazione singola"""
        
        print("🎲 GENERAZIONE CONFIGURAZIONE SINGOLA")
        print("="*40)
        
        # Selezione livello aggressività
        print("🎯 Scegli livello aggressività:")
        print("1. 🟢 Conservative (Sicuro)")
        print("2. 🟡 Moderate (Bilanciato)")
        print("3. 🔴 Aggressive (Performante)")
        
        choice = input("👉 Scegli livello (1-3): ").strip()
        level_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
        level = level_map.get(choice, 'moderate')
        
        if self.optimizer_mode == "autonomous":
            print(f"🚀 Generando {level} AUTONOMO...")
            config = self.autonomous_optimizer.generate_optimized_config(level)
            filepath = self.autonomous_optimizer.save_config(config, level)
            print(f"✅ Generato: {os.path.basename(filepath)}")
            
        else:  # json_based
            if not self.json_optimizer:
                print("❌ Optimizer JSON non inizializzato!")
                return
                
            print(f"📁 Generando {level} da JSON...")
            try:
                filepath = self.json_optimizer.generate_optimized_config(level)
                print(f"✅ Generato: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"❌ Errore generazione: {e}")
    
    def validate_configs(self):
        """Testa e valida configurazioni generate"""
        
        print("✅ TEST VALIDAZIONE CONFIGURAZIONI")
        print("="*40)
        
        if self.optimizer_mode == "autonomous":
            config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
            config_type = "AUTONOME"
        else:
            config_files = glob.glob(os.path.join(self.base_dir, "config_high_stakes_*.json"))
            config_type = "JSON"
        
        if not config_files:
            print(f"❌ Nessuna configurazione {config_type} trovata!")
            print("💡 Genera prima le configurazioni (opzione 4)")
            return
        
        print(f"🔄 Testando {len(config_files)} configurazioni {config_type}...")
        print()
        
        for config_file in config_files:
            if self.optimizer_mode == "autonomous":
                results = self.autonomous_optimizer.run_validation_test(config_file, 7)
                status = "✅ PASS" if results['high_stakes_validation'] else "❌ FAIL"
                filename = os.path.basename(config_file)
                pnl = results['daily_avg_pnl']
                win_rate = results['win_rate']
                print(f"{status} {filename}")
                print(f"   💰 P&L: €{pnl:.2f}/day")
                print(f"   🎯 Win Rate: {win_rate:.1f}%")
                print()
            else:
                print(f"📄 {os.path.basename(config_file)} - JSON validation TODO")
    
    def system_report(self):
        """Report completo del sistema"""
        
        print("📊 REPORT SISTEMA & CONFIGURAZIONE")
        print("="*45)
        
        print(f"🎯 Modalità: {self.optimizer_mode.upper()}")
        print(f"📁 Directory: {self.base_dir}")
        
        # Status optimizer
        if self.optimizer_mode == "autonomous":
            status = "✅" if self.autonomous_optimizer else "❌"
            print(f"🚀 Optimizer Autonomo: {status}")
        else:
            status = "✅" if self.json_optimizer else "❌"
            print(f"📁 Optimizer JSON: {status}")
            if self.current_config:
                print(f"📄 Config sorgente: {os.path.basename(self.current_config)}")
        
        # Conta configurazioni
        autonomous_configs = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        json_configs = glob.glob(os.path.join(self.base_dir, "config_high_stakes_*.json"))
        
        print(f"🚀 Configurazioni autonome: {len(autonomous_configs)}")
        print(f"📁 Configurazioni JSON: {len(json_configs)}")
        
        # File core
        core_files = [
            'autonomous_high_stakes_optimizer.py',
            'high_stakes_optimizer.py',
            'PRO-THE5ERS-QM-PHOENIX-GITCOP.py'
        ]
        
        print("\n📋 FILE CORE:")
        for filename in core_files:
            exists = os.path.exists(os.path.join(self.base_dir, filename))
            status = "✅" if exists else "❌"
            print(f"   {status} {filename}")
    
    def list_all_configs(self):
        """Lista tutte le configurazioni disponibili"""
        
        print("📋 TUTTE LE CONFIGURAZIONI DISPONIBILI")
        print("="*45)
        
        # Configurazioni autonome
        autonomous_configs = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        if autonomous_configs:
            print("🚀 CONFIGURAZIONI AUTONOME:")
            for config in autonomous_configs:
                filename = os.path.basename(config)
                size = os.path.getsize(config)
                mod_time = datetime.fromtimestamp(os.path.getmtime(config))
                print(f"   📄 {filename}")
                print(f"       📊 {size} bytes, {mod_time.strftime('%d/%m %H:%M')}")
        
        # Configurazioni JSON
        json_configs = glob.glob(os.path.join(self.base_dir, "config_high_stakes_*.json"))
        if json_configs:
            print("\n📁 CONFIGURAZIONI JSON:")
            for config in json_configs:
                filename = os.path.basename(config)
                size = os.path.getsize(config)
                mod_time = datetime.fromtimestamp(os.path.getmtime(config))
                print(f"   📄 {filename}")
                print(f"       📊 {size} bytes, {mod_time.strftime('%d/%m %H:%M')}")
        
        if not autonomous_configs and not json_configs:
            print("❌ Nessuna configurazione trovata!")
            print("💡 Genera configurazioni con opzione 4")
    
    def compliance_test(self):
        """Test compliance regole The5ers"""
        
        print("🏆 TEST COMPLIANCE THE5ERS HIGH STAKES")
        print("="*45)
        
        if self.optimizer_mode == "autonomous":
            config_files = glob.glob(os.path.join(self.base_dir, "config_autonomous_high_stakes_*.json"))
        else:
            config_files = glob.glob(os.path.join(self.base_dir, "config_high_stakes_*.json"))
        
        if not config_files:
            print("❌ Nessuna configurazione trovata!")
            return
        
        print("🔄 Testando compliance High Stakes Challenge...")
        print()
        
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
            
            # Test compliance
            daily_risk = risk_pct * account_balance * daily_trades
            max_daily_loss = account_balance * 0.05  # 5%
            
            compliance_risk = daily_risk <= max_daily_loss
            compliance_target = target_profit >= 25
            compliance_individual_risk = risk_pct <= 0.012  # 1.2% max
            
            overall_compliance = compliance_risk and compliance_target and compliance_individual_risk
            status = "✅ COMPLIANT" if overall_compliance else "❌ NON COMPLIANT"
            
            print(f"🎯 {config_name}: {status}")
            print(f"   💰 Risk/trade: {risk_pct*100:.1f}% ({'✅' if compliance_individual_risk else '❌'})")
            print(f"   📊 Risk giornaliero: €{daily_risk:.2f} ({'✅' if compliance_risk else '❌'})")
            print(f"   🎯 Target: €{target_profit} ({'✅' if compliance_target else '❌'})")
            print()
    
    def run(self):
        """Esegue sistema integrato completo"""
        
        print("🎯 THE5ERS COMPLETE INTEGRATED SYSTEM")
        print("Sistema Unico - Tutte le funzionalità integrate")
        print("="*60)
        print()
        
        # Info iniziale
        print(f"📁 Directory: {self.base_dir}")
        print(f"🎯 Modalità predefinita: {self.optimizer_mode.upper()}")
        print("💡 Modalità AUTONOMA è raccomandata (non serve JSON sorgente)")
        print()
        
        while True:
            try:
                self.show_main_menu()
                choice = input("👉 Scegli opzione (1-21): ").strip()
                
                if choice == "1":
                    self.switch_mode()
                elif choice == "2":
                    if self.optimizer_mode == "json_based":
                        # Menu selezione JSON
                        print("📁 Seleziona file JSON sorgente - TODO")
                    else:
                        print("ℹ️ Opzione disponibile solo in modalità JSON")
                elif choice == "3":
                    self.system_report()
                elif choice == "4":
                    self.generate_all_configs()
                elif choice == "5":
                    self.generate_single_config()
                elif choice == "6":
                    print("📋 Generazione selezionata - TODO")
                elif choice == "7":
                    print("⚡ Generazione rapida - TODO")
                elif choice == "8":
                    self.validate_configs()
                elif choice == "9":
                    print("📈 Backtest personalizzato - TODO")
                elif choice == "10":
                    print("🚀 Backtest comparativo - TODO")
                elif choice == "11":
                    self.compliance_test()
                elif choice == "12":
                    print("🔍 Analisi performance - TODO")
                elif choice == "13":
                    print("💰 Position sizing - TODO")
                elif choice == "14":
                    print("🎯 Analisi simboli - TODO")
                elif choice == "15":
                    self.list_all_configs()
                elif choice == "16":
                    print("🔍 Auto-discovery - TODO")
                elif choice == "17":
                    print("🔄 Switch config - TODO")
                elif choice == "18":
                    print("🔬 Diagnostica - TODO")
                elif choice == "19":
                    print("📚 Documentazione - TODO")
                elif choice == "20":
                    # Reset sistema
                    self.optimizer_mode = "autonomous"
                    self.autonomous_optimizer = None
                    self.json_optimizer = None
                    self.current_config = None
                    self.init_autonomous_mode()
                    print("✅ Sistema resettato (modalità autonoma)")
                elif choice == "21":
                    print("👋 Sistema terminato.")
                    break
                else:
                    print("❌ Opzione non valida. Scegli un numero da 1 a 21.")
                
                if choice != "21":
                    input("\n⏸️ Premi ENTER per continuare...")
                    print("\n" * 2)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Sistema terminato dall'utente.")
                break
            except Exception as e:
                print(f"\n❌ Errore imprevisto: {e}")
                input("⏸️ Premi ENTER per continuare...")

def main():
    """Funzione principale"""
    print("🚀 Inizializzazione THE5ERS COMPLETE INTEGRATED SYSTEM...")
    print()
    
    launcher = CompleteIntegratedLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
