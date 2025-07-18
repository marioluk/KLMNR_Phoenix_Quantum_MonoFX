#!/usr/bin/env python3
# ====================================================================================
# THE5ERS CONFIG SELECTOR - SELEZIONE DINAMICA CONFIGURAZIONI
# Sistema per scegliere dinamicamente il file di configurazione JSON
# ====================================================================================

import os
import json
import glob
from typing import List, Dict, Optional

class ConfigSelector:
    """Gestore per la selezione dinamica delle configurazioni"""
    
    def __init__(self, base_dir: str = None):
        """
        Inizializza il selettore di configurazioni
        
        Args:
            base_dir: Directory base dove cercare i file config (default: parent dir)
        """
        if base_dir is None:
            # Directory padre del sistema backtest
            self.base_dir = os.path.dirname(os.path.dirname(__file__))
        else:
            self.base_dir = base_dir
    
    def find_config_files(self) -> List[Dict]:
        """
        Trova tutti i file di configurazione JSON disponibili
        
        Returns:
            Lista di dizionari con info sui file config
        """
        configs = []
        
        # Pattern di ricerca per file config
        patterns = [
            "*config*.json",
            "*CONFIG*.json", 
            "PRO-THE5ERS*.json",
            "*STEP*.json"
        ]
        
        found_files = set()  # Usa set per evitare duplicati
        
        for pattern in patterns:
            search_path = os.path.join(self.base_dir, pattern)
            for file_path in glob.glob(search_path):
                if os.path.isfile(file_path):
                    found_files.add(file_path)
        
        # Cerca anche nella sottodirectory backtest_clean
        backtest_dir = os.path.join(self.base_dir, 'backtest_clean')
        if os.path.exists(backtest_dir):
            for pattern in patterns:
                search_path = os.path.join(backtest_dir, pattern)
                for file_path in glob.glob(search_path):
                    if os.path.isfile(file_path):
                        found_files.add(file_path)
        
        # Analizza ogni file trovato
        for file_path in sorted(found_files):
            try:
                config_info = self.analyze_config_file(file_path)
                if config_info:
                    configs.append(config_info)
            except Exception as e:
                print(f"⚠️ Errore analisi {os.path.basename(file_path)}: {e}")
        
        return configs
    
    def analyze_config_file(self, file_path: str) -> Optional[Dict]:
        """
        Analizza un file di configurazione per estrarre informazioni chiave
        
        Args:
            file_path: Percorso del file da analizzare
            
        Returns:
            Dizionario con informazioni del file o None se non valido
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Estrai informazioni chiave
            filename = os.path.basename(file_path)
            
            # Determina il tipo (Step 1, Step 2, etc.)
            config_type = "Unknown"
            if "step1" in filename.lower():
                config_type = "Step 1"
            elif "step2" in filename.lower():
                config_type = "Step 2"
            elif "conservative" in filename.lower():
                config_type = "Conservative"
            elif "ultra" in filename.lower():
                config_type = "Ultra Conservative"
            elif "aggressive" in filename.lower():
                config_type = "Aggressive"
            
            # Analizza contenuto
            symbols = list(config.get('symbols', {}).keys())
            risk_percent = config.get('risk_parameters', {}).get('risk_percent', 0)
            max_trades = config.get('risk_parameters', {}).get('max_daily_trades', 0)
            
            # The5ers specific
            the5ers_config = config.get('THE5ERS_specific', {})
            step_target = the5ers_config.get('step1_target') or the5ers_config.get('step2_target', 'N/A')
            
            # Calcola "aggressività" basata sui parametri
            aggressiveness = self.calculate_aggressiveness(config)
            
            return {
                'file_path': file_path,
                'filename': filename,
                'config_type': config_type,
                'symbols': symbols,
                'symbol_count': len(symbols),
                'risk_percent': risk_percent,
                'max_daily_trades': max_trades,
                'step_target': step_target,
                'aggressiveness': aggressiveness,
                'file_size': os.path.getsize(file_path),
                'last_modified': os.path.getmtime(file_path)
            }
            
        except Exception as e:
            print(f"❌ Errore lettura {file_path}: {e}")
            return None
    
    def calculate_aggressiveness(self, config: Dict) -> str:
        """
        Calcola il livello di aggressività della configurazione
        
        Args:
            config: Configurazione da analizzare
            
        Returns:
            Stringa che descrive l'aggressività (Conservative, Moderate, Aggressive)
        """
        score = 0
        
        # Risk percent (più alto = più aggressivo)
        risk_percent = config.get('risk_parameters', {}).get('risk_percent', 0)
        if risk_percent > 0.002:
            score += 2
        elif risk_percent > 0.0015:
            score += 1
        
        # Max trades (più alto = più aggressivo)
        max_trades = config.get('risk_parameters', {}).get('max_daily_trades', 0)
        if max_trades > 5:
            score += 2
        elif max_trades > 3:
            score += 1
        
        # Numero simboli (più simboli = più aggressivo)
        symbol_count = len(config.get('symbols', {}))
        if symbol_count > 5:
            score += 2
        elif symbol_count > 3:
            score += 1
        
        # Profit multiplier medio
        symbols = config.get('symbols', {})
        profit_multipliers = []
        for symbol_config in symbols.values():
            pm = symbol_config.get('risk_management', {}).get('profit_multiplier', 2.0)
            profit_multipliers.append(pm)
        
        if profit_multipliers:
            avg_pm = sum(profit_multipliers) / len(profit_multipliers)
            if avg_pm > 2.5:
                score += 2
            elif avg_pm > 2.2:
                score += 1
        
        # Classifica aggressività
        if score <= 2:
            return "🟢 Conservative"
        elif score <= 5:
            return "🟡 Moderate"
        else:
            return "🔴 Aggressive"
    
    def show_interactive_menu(self) -> Optional[str]:
        """
        Mostra menu interattivo per selezione configurazione
        
        Returns:
            Percorso del file selezionato o None se annullato
        """
        configs = self.find_config_files()
        
        if not configs:
            print("❌ Nessun file di configurazione trovato!")
            return None
        
        print("\n" + "="*80)
        print("🎯 SELEZIONE CONFIGURAZIONE THE5ERS")
        print("="*80)
        print()
        
        # Ordina per tipo e nome
        configs.sort(key=lambda x: (x['config_type'], x['filename']))
        
        print(f"{'#':<3} {'Tipo':<15} {'File':<35} {'Simboli':<8} {'Risk%':<8} {'Trades':<8} {'Aggressività'}")
        print("-" * 90)
        
        for i, config in enumerate(configs, 1):
            print(f"{i:<3} {config['config_type']:<15} {config['filename'][:32]:<35} "
                  f"{config['symbol_count']:<8} {config['risk_percent']*100:.3f}%{'':<7} "
                  f"{config['max_daily_trades']:<8} {config['aggressiveness']}")
        
        print("-" * 90)
        print(f"\nTrovati {len(configs)} file di configurazione")
        print()
        
        while True:
            try:
                choice = input(f"👉 Seleziona configurazione (1-{len(configs)}, 0=annulla): ").strip()
                
                if choice == "0":
                    print("❌ Selezione annullata")
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(configs):
                    selected = configs[choice_num - 1]
                    
                    print(f"\n✅ Selezionata: {selected['filename']}")
                    print(f"📁 Percorso: {selected['file_path']}")
                    print(f"🎯 Tipo: {selected['config_type']}")
                    print(f"💱 Simboli: {', '.join(selected['symbols'][:3])}{'...' if len(selected['symbols']) > 3 else ''}")
                    print(f"⚖️ Aggressività: {selected['aggressiveness']}")
                    
                    confirm = input("\n❓ Confermi la selezione? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes', 's', 'si']:
                        return selected['file_path']
                    else:
                        print("🔄 Riprova la selezione...")
                        continue
                else:
                    print(f"❌ Numero non valido. Inserisci 1-{len(configs)} o 0")
                    
            except ValueError:
                print("❌ Inserisci un numero valido")
            except KeyboardInterrupt:
                print("\n❌ Selezione annullata")
                return None
    
    def get_default_config(self) -> Optional[str]:
        """
        Restituisce il file di configurazione di default
        
        Returns:
            Percorso del file default o None se non trovato
        """
        # Cerca nell'ordine di priorità
        default_names = [
            'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json',
            'config_step2_conservative.json',
            'config_conservative_step1.json'
        ]
        
        for name in default_names:
            file_path = os.path.join(self.base_dir, name)
            if os.path.exists(file_path):
                return file_path
            
            # Cerca anche in backtest_clean
            file_path = os.path.join(self.base_dir, 'backtest_clean', name)
            if os.path.exists(file_path):
                return file_path
        
        # Se non trova nulla, prende il primo disponibile
        configs = self.find_config_files()
        if configs:
            return configs[0]['file_path']
        
        return None
    
    def show_config_details(self, config_path: str):
        """
        Mostra dettagli di una configurazione specifica
        
        Args:
            config_path: Percorso del file di configurazione
        """
        try:
            config_info = self.analyze_config_file(config_path)
            if not config_info:
                print(f"❌ Impossibile analizzare {config_path}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n📋 DETTAGLI CONFIGURAZIONE: {config_info['filename']}")
            print("="*60)
            
            print(f"🎯 Tipo: {config_info['config_type']}")
            print(f"⚖️ Aggressività: {config_info['aggressiveness']}")
            print(f"💰 Risk per trade: {config_info['risk_percent']*100:.3f}%")
            print(f"📊 Max trades/giorno: {config_info['max_daily_trades']}")
            print(f"💱 Simboli ({config_info['symbol_count']}): {', '.join(config_info['symbols'])}")
            
            # The5ers specifics
            the5ers = config.get('THE5ERS_specific', {})
            if the5ers:
                print(f"\n🏆 THE5ERS SETTINGS:")
                print(f"   Target Step: {the5ers.get('step1_target', 'N/A')}%")
                print(f"   Max Daily Loss: {the5ers.get('max_daily_loss_percent', 'N/A')}%")
                print(f"   Max Total Loss: {the5ers.get('max_total_loss_percent', 'N/A')}%")
            
            # Quantum params
            quantum = config.get('quantum_params', {})
            if quantum:
                print(f"\n🔬 QUANTUM PARAMETERS:")
                print(f"   Buffer Size: {quantum.get('buffer_size', 'N/A')}")
                print(f"   Signal Cooldown: {quantum.get('signal_cooldown', 'N/A')}s")
                entropy = quantum.get('entropy_thresholds', {})
                if entropy:
                    print(f"   Buy Signal: {entropy.get('buy_signal', 'N/A')}")
                    print(f"   Sell Signal: {entropy.get('sell_signal', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Errore visualizzazione dettagli: {e}")


def main():
    """Funzione principale per test del selettore"""
    
    selector = ConfigSelector()
    
    print("🧪 TEST CONFIG SELECTOR")
    print("="*50)
    
    # Mostra tutti i file trovati
    configs = selector.find_config_files()
    print(f"📁 Trovati {len(configs)} file di configurazione")
    
    # Test menu interattivo
    selected = selector.show_interactive_menu()
    
    if selected:
        print(f"\n🎯 File selezionato: {selected}")
        selector.show_config_details(selected)
    
    # Mostra default
    default = selector.get_default_config()
    print(f"\n📌 Default config: {default}")


if __name__ == "__main__":
    main()
