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

# Import del converter
try:
    from config_converter import ConfigConverter
except ImportError:
    print("❌ Errore: ConfigConverter non trovato")
    print("💡 Assicurati che config_converter.py sia nella directory corrente")
    sys.exit(1)

def convert_all_autonomous_configs(source_dir: str = "../config", production_template: str = None):
    """
    Converte tutte le configurazioni autonome in formato produzione
    
    Args:
        source_dir: Directory contenente i config autonomi
        production_template: Path al template produzione
    """
    
    print("🔄 CONVERSIONE AUTOMATICA CONFIG AUTONOMI")
    print("="*50)
    
    # Trova tutti i file autonomi
    autonomous_files = glob.glob(os.path.join(source_dir, "config_autonomous_*.json"))
    
    if not autonomous_files:
        print(f"❌ Nessun file autonomo trovato in {source_dir}")
        return
    
    print(f"📁 Trovati {len(autonomous_files)} file autonomi")
    
    # Template produzione
    if not production_template:
        production_template = "../PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
    
    if not os.path.exists(production_template):
        print(f"⚠️ Template produzione non trovato: {production_template}")
        print("💡 Usando template di default")
        production_template = None
    
    # Inizializza converter
    converter = ConfigConverter(production_template)
    
    converted_files = []
    
    # Converti ogni file
    for autonomous_file in autonomous_files:
        try:
            print(f"\n🔄 Convertendo: {os.path.basename(autonomous_file)}")
            
            # Nome file output
            base_name = os.path.splitext(os.path.basename(autonomous_file))[0]
            output_name = f"{base_name}_production_ready.json"
            output_path = os.path.join(source_dir, output_name)
            
            # Converti
            converted_path = converter.convert_autonomous_to_production(
                autonomous_file, 
                output_path
            )
            
            converted_files.append(converted_path)
            print(f"✅ Convertito: {os.path.basename(converted_path)}")
            
        except Exception as e:
            print(f"❌ Errore conversione {autonomous_file}: {e}")
    
    # Riepilogo
    print(f"\n🎯 CONVERSIONE COMPLETATA")
    print(f"✅ {len(converted_files)} file convertiti con successo")
    print(f"📁 File disponibili in: {source_dir}")
    
    if converted_files:
        print("\n📋 FILE PRONTI PER PRODUZIONE:")
        for file_path in converted_files:
            print(f"   • {os.path.basename(file_path)}")
        
        print("\n💡 PROSSIMI PASSI:")
        print("1. Testa i file convertiti in ambiente sicuro")
        print("2. Valida compatibilità con l'algoritmo principale")
        print("3. Deploy graduale in produzione")

def convert_single_config():
    """Interfaccia interattiva per conversione singola"""
    
    print("🔄 CONVERSIONE SINGOLA CONFIG")
    print("="*40)
    
    # Lista file autonomi disponibili
    configs_dir = "../config"
    if os.path.exists(configs_dir):
        autonomous_files = glob.glob(os.path.join(configs_dir, "config_autonomous_*.json"))
    else:
        autonomous_files = glob.glob("config_autonomous_*.json")
    
    if not autonomous_files:
        print("❌ Nessun file autonomo trovato")
        return
    
    print("📋 File autonomi disponibili:")
    for i, file_path in enumerate(autonomous_files, 1):
        print(f"{i}. {os.path.basename(file_path)}")
    
    # Selezione utente
    try:
        choice = int(input("\n👉 Scegli file da convertire (numero): ")) - 1
        
        if choice < 0 or choice >= len(autonomous_files):
            print("❌ Scelta non valida")
            return
        
        selected_file = autonomous_files[choice]
        
        # Template produzione
        production_template = input("📁 Path template produzione (ENTER per default): ").strip()
        if not production_template:
            production_template = "../PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"
        
        # Converti
        converter = ConfigConverter(production_template if os.path.exists(production_template) else None)
        converted_path = converter.convert_autonomous_to_production(selected_file)
        
        print(f"\n✅ Conversione completata!")
        print(f"📁 File convertito: {converted_path}")
        
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
            # Lista file
            configs_dir = "configs"
            autonomous_files = glob.glob(os.path.join(configs_dir, "config_autonomous_*.json"))
            production_files = glob.glob(os.path.join(configs_dir, "*_production_ready.json"))
            
            print(f"\n📋 CONFIG AUTONOMI ({len(autonomous_files)}):")
            for file_path in autonomous_files:
                print(f"   • {os.path.basename(file_path)}")
            
            print(f"\n📋 CONFIG PRODUZIONE ({len(production_files)}):")
            for file_path in production_files:
                print(f"   • {os.path.basename(file_path)}")
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
