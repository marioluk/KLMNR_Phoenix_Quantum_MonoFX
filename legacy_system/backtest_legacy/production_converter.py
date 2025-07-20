#!/usr/bin/env python3
"""
PRODUCTION CONVERTER - Integrazione con Sistema Autonomo
Aggiunti al sistema autonomo le funzionalità di conversione automatica
"""

import os
import sys
import glob
import json
from datetime import datetime
from typing import List

# Import del converter
try:
    from config_converter import ConfigConverter
except ImportError:
    print("❌ Errore: ConfigConverter non trovato")
    print("💡 Assicurati che config_converter.py sia nella directory corrente")
    sys.exit(1)

def find_autonomous_configs() -> List[str]:
    """
    Trova tutti i file config_autonomous_*.json in tutte le possibili ubicazioni
    Esclude i file già convertiti (_production_ready)
    
    Returns:
        Lista di percorsi assoluti ai file trovati
    """
    
    search_dirs = [
        "configs",                          # backtest_legacy/configs/
        "../config",                        # legacy_system/config/
        ".",                               # backtest_legacy/ (directory corrente)
        "../../config",                     # root/config/ (se esistesse)
    ]
    
    all_files = []
    
    print("🔍 Ricerca file config_autonomous_*.json in:")
    
    for search_dir in search_dirs:
        print(f"   📁 {search_dir}:", end=" ")
        if os.path.exists(search_dir):
            pattern = os.path.join(search_dir, "config_autonomous_*.json")
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
                    print(f"      • {os.path.relpath(file_path)}")
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
        converted_path = converter.convert_autonomous_to_production(selected_file)
        
        print(f"\n✅ Conversione completata!")
        print(f"📁 File convertito: {os.path.relpath(converted_path)}")
        
    except ValueError:
        print("❌ Input non valido")
    except Exception as e:
        print(f"❌ Errore conversione: {e}")

def main():
    """Menu principale converter"""
    
    print("🎯 THE5ERS CONFIG CONVERTER")
    print("Converte configurazioni autonome in formato produzione")
    print("="*60)
    print()
    
    while True:
        print("OPZIONI CONVERSIONE:")
        print("1. 🔄 Converti TUTTI i config autonomi")
        print("2. 📋 Converti SINGOLO config")
        print("3. 📊 Lista config disponibili")
        print("4. 👋 Esci")
        print()
        
        choice = input("👉 Scegli opzione (1-4): ").strip()
        
        if choice == "1":
            convert_all_autonomous_configs()
        elif choice == "2":
            convert_single_config()
        elif choice == "3":
            # Lista file con ricerca intelligente
            autonomous_files = find_autonomous_configs()
            
            # Trova anche i file _production_ready
            production_files = []
            search_dirs = ["configs", "../config", "."]
            
            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    pattern = os.path.join(search_dir, "*_production_ready.json")
                    found_files = glob.glob(pattern)
                    for file_path in found_files:
                        abs_path = os.path.abspath(file_path)
                        if abs_path not in [os.path.abspath(f) for f in production_files]:
                            production_files.append(file_path)
            
            print(f"\n📋 CONFIG AUTONOMI ({len(autonomous_files)}):")
            if autonomous_files:
                for file_path in autonomous_files:
                    print(f"   • {os.path.relpath(file_path)}")
            else:
                print("   Nessun file trovato")
            
            print(f"\n📋 CONFIG PRODUZIONE ({len(production_files)}):")
            if production_files:
                for file_path in production_files:
                    print(f"   • {os.path.relpath(file_path)}")
            else:
                print("   Nessun file trovato")
        elif choice == "4":
            print("👋 Converter terminato.")
            break
        else:
            print("❌ Opzione non valida.")
        
        if choice != "4":
            input("\n⏸️ Premi ENTER per continuare...")
            print("\n" * 2)

if __name__ == "__main__":
    main()
