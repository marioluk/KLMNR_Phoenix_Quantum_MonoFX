#!/usr/bin/env python3
"""
PRODUCTION CONVERTER - Sistema di Gestione Configurazioni Ottimizzate
Gestisce la conversione dei file ottimizzati in configurazione di produzione
Logica CORRETTA:
1. L'ottimizzatore genera: config_autonomous_high_stakes_[STRATEGY]_production_ready.json
2. Il sistema seleziona il migliore e lo copia in: config_autonomous_high_stakes_conservative_production_ready.json
3. Il software di trading legge: config_autonomous_high_stakes_conservative_production_ready.json
"""

import os
import sys
import glob
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional

# Import del converter
try:
    from config_converter import ConfigConverter
except ImportError:
    print("❌ Errore: ConfigConverter non trovato")
    print("💡 Assicurati che config_converter.py sia nella directory corrente")
    sys.exit(1)

def find_production_ready_configs() -> List[str]:
    """
    Trova tutti i file config_autonomous_*_production_ready.json
    
    Returns:
        Lista di percorsi assoluti ai file trovati
    """
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "..", "config")
    
    if not os.path.exists(config_dir):
        return []
    
    pattern = os.path.join(config_dir, "config_autonomous_high_stakes_*_production_ready.json")
    found_files = glob.glob(pattern)
    
    return sorted(found_files)

def select_best_config(production_ready_files: List[str]) -> Optional[str]:
    """
    Seleziona il miglior file di configurazione basato su criteri prestazionali
    
    Args:
        production_ready_files: Lista dei file production-ready
        
    Returns:
        Path del miglior file o None se nessuno trovato
    """
    
    if not production_ready_files:
        return None
    
    # Ordine di preferenza: conservative > moderate > aggressive
    strategy_priority = ["conservative", "moderate", "aggressive"]
    
    for strategy in strategy_priority:
        for file_path in production_ready_files:
            if f"_{strategy}_production_ready.json" in file_path:
                return file_path
    
    # Se non trova nessuna strategia specifica, prende il primo disponibile
    return production_ready_files[0]

def deploy_best_config() -> bool:
    """
    Trova il miglior config production-ready e lo deploy come file principale
    
    Returns:
        True se deploy riuscito, False altrimenti
    """
    
    print("🎯 DEPLOY MIGLIOR CONFIGURAZIONE")
    print("="*50)
    
    # Trova file production-ready
    production_files = find_production_ready_configs()
    
    if not production_files:
        print("❌ Nessun file *_production_ready.json trovato")
        print("💡 Esegui prima l'ottimizzazione autonoma")
        return False
    
    print(f"📁 Trovati {len(production_files)} file production-ready:")
    for file_path in production_files:
        filename = os.path.basename(file_path)
        print(f"   • {filename}")
    
    # Seleziona il migliore
    best_file = select_best_config(production_files)
    best_filename = os.path.basename(best_file)
    
    print(f"\n🏆 Migliore selezionato: {best_filename}")
    
    # Path del file principale
    # Usa sempre path assoluto per legacy_system/config
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.abspath(os.path.join(script_dir, "..", "config"))
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    main_config_path = os.path.join(config_dir, "config_autonomous_high_stakes_conservative_production_ready.json")
    
    import time
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            # Backup del file esistente nella cartella backup
            if os.path.exists(main_config_path):
                backup_dir = os.path.join(config_dir, "backup")
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                backup_filename = f"config_autonomous_high_stakes_conservative_production_ready.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path = os.path.join(backup_dir, backup_filename)
                shutil.copy2(main_config_path, backup_path)
                print(f"💾 Backup creato: backup/{backup_filename}")
            # Deploy del nuovo file
            shutil.copy2(best_file, main_config_path)
            print(f"✅ Deploy completato!")
            print(f"📁 File principale aggiornato: config_autonomous_high_stakes_conservative_production_ready.json")
            return True
        except Exception as e:
            if hasattr(e, 'winerror') and e.winerror == 32:
                print(f"⚠️ File bloccato da un altro processo (tentativo {attempt}/{max_attempts}). Riprovo tra 2 secondi...")
                time.sleep(2)
            else:
                print(f"❌ Errore durante il deploy: {e}")
                return False
    print("❌ Errore: il file rimane bloccato dopo 3 tentativi. Chiudi tutte le applicazioni che lo usano e riprova.")
    return False

def find_autonomous_configs() -> List[str]:
    """
    Trova tutti i file config_autonomous_*.json in tutte le possibili ubicazioni
    Esclude i file già convertiti (_production_ready)
    
    Returns:
        Lista di percorsi assoluti ai file trovati
    """
    
    # Determina percorsi assoluti basati sulla posizione del file corrente
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    search_dirs = [
        os.path.join(script_dir, "configs"),                    # backtest_legacy/configs/
        os.path.join(script_dir, "..", "config"),               # legacy_system/config/
        script_dir,                                             # backtest_legacy/ (directory script)
        os.path.join(script_dir, "..", "..", "config"),         # root/config/ (se esistesse)
        os.getcwd(),                                           # Directory corrente (da dove viene eseguito)
        os.path.join(os.getcwd(), "legacy_system", "backtest_legacy"),  # Se eseguito da root
        os.path.join(os.getcwd(), "legacy_system", "config")    # Se eseguito da root
    ]
    
    all_files = []
    
    print("🔍 Ricerca file config_autonomous_*.json in:")
    
    for search_dir in search_dirs:
        # Converti in percorso assoluto e normalizza
        abs_search_dir = os.path.abspath(search_dir)
        display_path = os.path.relpath(abs_search_dir) if len(os.path.relpath(abs_search_dir)) < len(abs_search_dir) else abs_search_dir
        
        print(f"   📁 {display_path}:", end=" ")
        if os.path.exists(abs_search_dir):
            pattern = os.path.join(abs_search_dir, "config_autonomous_*.json")
            found_files = glob.glob(pattern)
            
            # Filtra solo i file non convertiti (esclude _production_ready)
            filtered_files = []
            for file_path in found_files:
                if "_production_ready" not in os.path.basename(file_path):
                    abs_path = os.path.abspath(file_path)
                    if abs_path not in [os.path.abspath(f) for f in all_files]:
                        all_files.append(file_path)
                        filtered_files.append(file_path)
            
            if filtered_files:
                print(f"✅ {len(filtered_files)} file trovati (su {len(found_files)} totali)")
                for file_path in filtered_files:
                    display_file = os.path.relpath(file_path) if len(os.path.relpath(file_path)) < len(file_path) else file_path
                    print(f"      • {display_file}")
            else:
                total_found = len(found_files)
                if total_found > 0:
                    print(f"⚠️ {total_found} file trovati ma tutti già convertiti")
                else:
                    print("❌ nessun file")
        else:
            print("❌ directory non esiste")
    
    print(f"\n📊 TOTALE: {len(all_files)} file autonomi non convertiti")
    return sorted(all_files)

def convert_all_autonomous_configs(source_dir: str = None, production_template: str = None):
    """
    Converte tutte le configurazioni autonome in formato produzione
    
    Args:
        source_dir: Directory contenente i config autonomi (deprecato, usa ricerca automatica)
        production_template: Path al template produzione
    """
    
    print("🔄 CONVERSIONE AUTOMATICA CONFIG AUTONOMI")
    print("="*50)
    
    # Trova tutti i file autonomi in tutte le possibili ubicazioni
    autonomous_files = find_autonomous_configs()
    
    if not autonomous_files:
        print("❌ Nessun file config_autonomous_*.json trovato")
        print("🔍 Ricerca effettuata in:")
        print("   • configs/ (backtest_legacy/configs/)")
        print("   • ../config/ (legacy_system/config/)")
        print("   • . (directory corrente)")
        return
    
    print(f"📁 Trovati {len(autonomous_files)} file autonomi:")
    for file_path in autonomous_files:
        rel_path = os.path.relpath(file_path)
        print(f"   • {rel_path}")
    print()
    
    # Template produzione - cerca in diverse ubicazioni
    if not production_template:
        template_paths = [
            "../PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json",  # legacy_system/
            "../config/PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json",  # legacy_system/config/
            "configs/PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"     # backtest_legacy/configs/
        ]
        
        for template_path in template_paths:
            if os.path.exists(template_path):
                production_template = template_path
                break
    
    if production_template and os.path.exists(production_template):
        print(f"📋 Template produzione: {os.path.relpath(production_template)}")
    else:
        print("⚠️ Template produzione non trovato, usando template di default")
        production_template = None
    
    # Inizializza converter
    converter = ConfigConverter(production_template)
    
    converted_files = []
    
    # Converti ogni file
    for autonomous_file in autonomous_files:
        try:
            print(f"🔄 Convertendo: {os.path.relpath(autonomous_file)}")
            
            # Nome file output - salva nella stessa directory dell'originale
            file_dir = os.path.dirname(autonomous_file)
            base_name = os.path.splitext(os.path.basename(autonomous_file))[0]
            output_name = f"{base_name}_production_ready.json"
            output_path = os.path.join(file_dir, output_name)
            
            # Converti
            converted_path = converter.convert_autonomous_to_production(
                autonomous_file, 
                output_path
            )
            
            converted_files.append(converted_path)
            print(f"✅ Convertito: {os.path.relpath(converted_path)}")
            
        except Exception as e:
            print(f"❌ Errore conversione {os.path.relpath(autonomous_file)}: {e}")
    
    # Riepilogo
    print(f"\n🎯 CONVERSIONE COMPLETATA")
    print(f"✅ {len(converted_files)} file convertiti con successo")
    
    if converted_files:
        print("\n📋 FILE PRONTI PER PRODUZIONE:")
        for file_path in converted_files:
            print(f"   • {os.path.relpath(file_path)}")
        
        print("\n💡 PROSSIMI PASSI:")
        print("1. Testa i file convertiti in ambiente sicuro")
        print("2. Valida compatibilità con l'algoritmo principale")
        print("3. Deploy graduale in produzione")

def convert_single_config():
    """Interfaccia interattiva per conversione singola"""
    
    print("🔄 CONVERSIONE SINGOLA CONFIG")
    print("="*40)
    
    # Trova file autonomi disponibili con ricerca intelligente
    autonomous_files = find_autonomous_configs()
    
    if not autonomous_files:
        print("❌ Nessun file config_autonomous_*.json trovato")
        print("🔍 Ricerca effettuata in:")
        print("   • configs/ (backtest_legacy/configs/)")
        print("   • ../config/ (legacy_system/config/)")
        print("   • . (directory corrente)")
        return
    
    print("📋 File autonomi disponibili:")
    for i, file_path in enumerate(autonomous_files, 1):
        rel_path = os.path.relpath(file_path)
        print(f"{i}. {rel_path}")
    
    # Selezione utente
    try:
        choice = int(input("\n👉 Scegli file da convertire (numero): ")) - 1
        
        if choice < 0 or choice >= len(autonomous_files):
            print("❌ Scelta non valida")
            return
        
        selected_file = autonomous_files[choice]
        
        # Template produzione - cerca automaticamente
        production_template = input("📁 Path template produzione (ENTER per ricerca automatica): ").strip()
        if not production_template:
            # Ricerca automatica template
            template_paths = [
                "../PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json",
                "../config/PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json",
                "configs/PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
            ]
            
            for template_path in template_paths:
                if os.path.exists(template_path):
                    production_template = template_path
                    print(f"📋 Template trovato: {os.path.relpath(template_path)}")
                    break
        
        # Converti
        converter = ConfigConverter(production_template if production_template and os.path.exists(production_template) else None)
        # Il file finale deve essere sempre config_autonomous_high_stakes_production_ready.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(script_dir, "..", "config")
        output_path = os.path.join(config_dir, "config_autonomous_high_stakes_production_ready.json")
        converted_path = converter.convert_autonomous_to_production(selected_file, output_path)
        print(f"\n✅ Conversione completata!")
        print(f"📁 File convertito: {os.path.relpath(converted_path)}")
        
    except ValueError:
        print("❌ Input non valido")
    except Exception as e:
        print(f"❌ Errore conversione: {e}")

def main():
    """Menu principale converter"""
    
    print("🎯 THE5ERS CONFIG CONVERTER")
    print("Gestione configurazioni ottimizzate per produzione")
    print("="*60)
    print()
    
    while True:
        print("OPZIONI DISPONIBILI:")
        print("1. 🔄 Converti TUTTI i config autonomi")
        print("2. 📋 Converti SINGOLO config")
        print("3. 🎯 DEPLOY miglior configurazione (NUOVO)")
        print("4. 📊 Lista config disponibili")
        print("5. 👋 Esci")
        print()
        
        choice = input("👉 Scegli opzione (1-5): ").strip()
        
        if choice == "1":
            convert_all_autonomous_configs()
        elif choice == "2":
            convert_single_config()
        elif choice == "3":
            deploy_best_config()
        elif choice == "4":
            # Lista file con ricerca intelligente
            autonomous_files = find_autonomous_configs()
            
            # Trova anche i file _production_ready usando percorsi assoluti
            production_files = []
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            search_dirs = [
                os.path.join(script_dir, "configs"),                    # backtest_legacy/configs/
                os.path.join(script_dir, "..", "config"),               # legacy_system/config/
                script_dir,                                             # backtest_legacy/
                os.path.join(script_dir, "..", "..", "config"),         # root/config/
                os.getcwd(),                                           # Directory corrente
                os.path.join(os.getcwd(), "legacy_system", "backtest_legacy"),  # Se eseguito da root
                os.path.join(os.getcwd(), "legacy_system", "config")    # Se eseguito da root
            ]
            
            for search_dir in search_dirs:
                abs_search_dir = os.path.abspath(search_dir)
                if os.path.exists(abs_search_dir):
                    pattern = os.path.join(abs_search_dir, "*_production_ready.json")
                    found_files = glob.glob(pattern)
                    for file_path in found_files:
                        abs_path = os.path.abspath(file_path)
                        if abs_path not in [os.path.abspath(f) for f in production_files]:
                            production_files.append(file_path)
            
            print(f"\n📋 CONFIG AUTONOMI ({len(autonomous_files)}):")
            if autonomous_files:
                for file_path in autonomous_files:
                    display_path = os.path.relpath(file_path) if len(os.path.relpath(file_path)) < len(file_path) else file_path
                    print(f"   • {display_path}")
            else:
                print("   Nessun file trovato")
            
            print(f"\n📋 CONFIG PRODUZIONE ({len(production_files)}):")
            if production_files:
                for file_path in production_files:
                    display_path = os.path.relpath(file_path) if len(os.path.relpath(file_path)) < len(file_path) else file_path
                    print(f"   • {display_path}")
            else:
                print("   Nessun file trovato")
        elif choice == "5":
            print("👋 Converter terminato.")
            break
        else:
            print("❌ Opzione non valida.")
        
        if choice != "5":
            input("\n⏸️ Premi ENTER per continuare...")
            print("\n" * 2)

if __name__ == "__main__":
    main()
