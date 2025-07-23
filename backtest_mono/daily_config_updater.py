#!/usr/bin/env python3
"""
DAILY CONFIG UPDATER - Aggiornamento Automatico Configurazioni
Sistema automatizzato per generazione e conversione giornaliera delle configurazioni ottimali
Ideale per esecuzione con cronjob
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

# Setup logging per cronjob - COMPATIBILE WINDOWS
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"daily_config_updater_{datetime.now().strftime('%Y%m%d')}.log")

# Formatter senza emoji per compatibilità Windows
formatter_console = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter_file = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Setup handlers
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(formatter_file)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter_console)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Import dei moduli necessari
try:
    from autonomous_optimizer import AutonomousOptimizer
    from config_converter import ConfigConverter
    from production_converter import find_autonomous_configs
except ImportError as e:
    logger.error(f"[ERROR] Errore import: {e}")
    sys.exit(1)

class DailyConfigUpdater:
    """
    Sistema automatizzato per aggiornamento giornaliero configurazioni
    """
    
    def __init__(self, optimization_days: int = 30, backup_old_configs: bool = True):
        """
        Args:
            optimization_days: Giorni di dati per ottimizzazione (default: 30)
            backup_old_configs: Se fare backup delle configurazioni precedenti
        """
        self.optimization_days = optimization_days
        self.backup_old_configs = backup_old_configs
        
        # Percorsi
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.legacy_dir = os.path.dirname(self.script_dir)
        self.config_dir = os.path.join(self.legacy_dir, "config")
        self.backup_dir = os.path.join(self.config_dir, "backups")
        
        # Inizializza componenti
        self.optimizer = AutonomousOptimizer(optimization_days)
        self.converter = None  # Sarà inizializzato quando necessario
        
        logger.info(f"[INIT] Daily Config Updater inizializzato")
        logger.info(f"[CONFIG] Ottimizzazione su {optimization_days} giorni")
        logger.info(f"[PATH] Config dir: {self.config_dir}")
        
    def backup_existing_configs(self) -> Dict[str, str]:
        """
        Fa backup delle configurazioni esistenti
        
        Returns:
            Dict con mapping tipo_config -> percorso_backup
        """
        
        if not self.backup_old_configs:
            logger.info("⏭️ Backup disabilitato, saltando...")
            return {}
        
        logger.info("[BACKUP] Backup configurazioni esistenti...")
        
        # Crea directory backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = os.path.join(self.backup_dir, timestamp)
        os.makedirs(backup_subdir, exist_ok=True)
        
        backup_mapping = {}
        
        # Pattern file da salvare
        patterns = [
            "config_autonomous_high_stakes_*.json",
            "*_production_ready.json"
        ]
        
        import glob
        
        for pattern in patterns:
            search_pattern = os.path.join(self.config_dir, pattern)
            files = glob.glob(search_pattern)
            
            for file_path in files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    backup_path = os.path.join(backup_subdir, filename)
                    
                    try:
                        import shutil
                        shutil.copy2(file_path, backup_path)
                        backup_mapping[filename] = backup_path
                        logger.info(f"   [BACKUP] {filename} -> {os.path.relpath(backup_path)}")
                    except Exception as e:
                        logger.warning(f"   [WARNING] Errore backup {filename}: {e}")
        
        if backup_mapping:
            logger.info(f"[SUCCESS] Backup completato: {len(backup_mapping)} file in {os.path.relpath(backup_subdir)}")
        else:
            logger.info("[INFO] Nessun file da salvare trovato")
            
        return backup_mapping
    
    def generate_optimal_config(self) -> Optional[str]:
        """
        Genera la configurazione ottimale usando Auto-Best
        
        Returns:
            Percorso del file generato o None se errore
        """
        
        logger.info("[TARGET] Generazione configurazione ottimale...")
        logger.info(f"[STATS] Analizzando ultimi {self.optimization_days} giorni di dati")
        
        try:
            # Genera tutte le configurazioni
            logger.info("[PROCESS] Generando tutte le configurazioni per confronto...")
            results = self.optimizer.generate_all_configs()
            
            if not results:
                logger.error("[ERROR] Nessuna configurazione generata")
                return None
            
            # Analizza e trova la migliore
            logger.info("[BEST] Analisi per identificare la migliore...")
            
            best_config = None
            best_score = 0
            best_level = None
            
            for level, filepath in results.items():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    score = config.get('optimization_results', {}).get('average_optimization_score', 0)
                    symbols_count = len(config.get('symbols', {}))
                    risk_pct = config.get('risk_parameters', {}).get('risk_percent', 0) * 100
                    
                    logger.info(f"   [STATS] {level.upper()}: Score={score:.2f}, Simboli={symbols_count}, Risk={risk_pct:.1f}%")
                    
                    if score > best_score:
                        best_score = score
                        best_level = level
                        best_config = filepath
                        
                except Exception as e:
                    logger.error(f"   [ERROR] Errore analisi {level}: {e}")
            
            if not best_config:
                logger.error("[ERROR] Nessuna configurazione valida trovata")
                return None
            
            logger.info(f"[WINNER] MIGLIORE: {best_level.upper()} (Score: {best_score:.2f})")
            logger.info(f"[FILE] File: {os.path.basename(best_config)}")
            
            # Pulizia: elimina configurazioni non ottimali
            logger.info("[CLEANUP] Pulizia file non ottimali...")
            files_removed = 0
            
            for level, filepath in results.items():
                if filepath != best_config and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        files_removed += 1
                        logger.info(f"   [DELETE] Rimosso: {os.path.basename(filepath)} ({level.upper()})")
                    except Exception as e:
                        logger.warning(f"   [WARNING] Errore rimozione {os.path.basename(filepath)}: {e}")
            
            logger.info(f"[SUCCESS] Generazione completata: {os.path.basename(best_config)}")
            logger.info(f"[CLEANUP] Rimossi {files_removed} file non ottimali")
            
            return best_config
            
        except Exception as e:
            logger.error(f"[ERROR] Errore generazione configurazione: {e}")
            return None
    
    def convert_to_production(self, autonomous_config_path: str) -> Optional[str]:
        """
        Converte configurazione autonoma in formato produzione
        
        Args:
            autonomous_config_path: Percorso configurazione autonoma
            
        Returns:
            Percorso file produzione o None se errore
        """
        
        logger.info("[PROCESS] Conversione a formato produzione...")
        
        try:
            # Trova template produzione
            template_paths = [
                os.path.join(self.legacy_dir, "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"),
                os.path.join(self.config_dir, "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json")
            ]
            
            production_template = None
            for template_path in template_paths:
                if os.path.exists(template_path):
                    production_template = template_path
                    break
            
            if production_template:
                logger.info(f"[REPORT] Template trovato: {os.path.relpath(production_template)}")
            else:
                logger.warning("[WARNING] Template produzione non trovato, usando default")
            
            # Inizializza converter
            self.converter = ConfigConverter(production_template)
            
            # Nome file output STANDARD (senza [BEST] per compatibilità sistema legacy)
            output_name = "config_autonomous_high_stakes_conservative_production_ready.json"
            output_path = os.path.join(self.config_dir, output_name)
            
            logger.info(f"[TARGET] Target: {output_name} (nome standard per compatibilità legacy)")
            
            # Converti
            converted_path = self.converter.convert_autonomous_to_production(
                autonomous_config_path, 
                output_path
            )
            
            logger.info(f"[SUCCESS] Conversione completata: {os.path.relpath(converted_path)}")
            logger.info(f"[LINK] Compatibile con sistema legacy (stesso path CONFIG_FILE)")
            
            # Rimuovi file autonomo originale se è diverso dal target
            if autonomous_config_path != converted_path and os.path.exists(autonomous_config_path):
                try:
                    os.remove(autonomous_config_path)
                    logger.info(f"[CLEANUP] File autonomo temporaneo rimosso: {os.path.basename(autonomous_config_path)}")
                except Exception as e:
                    logger.warning(f"[WARNING] Non riuscito a rimuovere file temporaneo: {e}")
            
            # Valida file convertito
            if self.validate_production_config(converted_path):
                logger.info("[SUCCESS] File produzione validato con successo")
                return converted_path
            else:
                logger.error("[ERROR] Validazione file produzione fallita")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Errore conversione: {e}")
            return None
    
    def validate_production_config(self, config_path: str) -> bool:
        """
        Valida la configurazione produzione generata
        
        Args:
            config_path: Percorso file da validare
            
        Returns:
            True se valido, False altrimenti
        """
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Controlli di base
            required_sections = ['symbols', 'risk_parameters']  # Rimossa metadata obbligatoria
            for section in required_sections:
                if section not in config:
                    logger.error(f"[ERROR] Sezione {section} mancante")
                    return False
            
            # Controllo simboli
            symbols = config.get('symbols', {})
            if len(symbols) == 0:
                logger.error("[ERROR] Nessun simbolo configurato")
                return False
            
            # Controllo parametri risk
            risk_params = config.get('risk_parameters', {})
            if not risk_params.get('risk_percent'):
                logger.error("[ERROR] Risk percent non configurato")
                return False
            
            # Controllo metadata (opzionale)
            metadata = config.get('metadata', config.get('conversion_metadata', {}))
            if metadata:
                logger.info(f"[INFO] Metadata trovati: {len(metadata)} campi")
            
            logger.info(f"[SUCCESS] Validazione OK: {len(symbols)} simboli, risk {risk_params.get('risk_percent', 0)*100:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Errore validazione: {e}")
            return False
    
    def cleanup_old_backups(self, keep_days: int = 7):
        """
        Pulisce backup vecchi oltre keep_days giorni
        
        Args:
            keep_days: Giorni di backup da mantenere
        """
        
        if not os.path.exists(self.backup_dir):
            return
        
        logger.info(f"[CLEANUP] Pulizia backup oltre {keep_days} giorni...")
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        
        try:
            for backup_folder in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, backup_folder)
                
                if os.path.isdir(backup_path):
                    # Estrai data dal nome cartella (formato YYYYMMDD_HHMMSS)
                    try:
                        date_str = backup_folder.split('_')[0]
                        backup_date = datetime.strptime(date_str, '%Y%m%d')
                        
                        if backup_date < cutoff_date:
                            import shutil
                            shutil.rmtree(backup_path)
                            removed_count += 1
                            logger.info(f"   [DELETE] Rimosso backup: {backup_folder}")
                            
                    except (ValueError, IndexError):
                        logger.warning(f"   [WARNING] Nome backup non riconosciuto: {backup_folder}")
            
            if removed_count > 0:
                logger.info(f"[SUCCESS] Rimossi {removed_count} backup obsoleti")
            else:
                logger.info("[INFO] Nessun backup da rimuovere")
                
        except Exception as e:
            logger.error(f"[ERROR] Errore pulizia backup: {e}")
    
    def run_daily_update(self) -> bool:
        """
        Esegue l'aggiornamento giornaliero completo
        
        Returns:
            True se successo, False se errore
        """
        
        logger.info("[START] AVVIO AGGIORNAMENTO GIORNALIERO CONFIG")
        logger.info("="*60)
        logger.info(f"[DATE] Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"[STATS] Periodo ottimizzazione: {self.optimization_days} giorni")
        
        try:
            # 1. Backup configurazioni esistenti
            backup_mapping = self.backup_existing_configs()
            
            # 2. Genera configurazione ottimale
            best_config_path = self.generate_optimal_config()
            if not best_config_path:
                logger.error("[ERROR] Fallita generazione configurazione ottimale")
                return False
            
            # 3. Converti a formato produzione
            production_config_path = self.convert_to_production(best_config_path)
            if not production_config_path:
                logger.error("[ERROR] Fallita conversione a formato produzione")
                return False
            
            # 4. Pulizia backup vecchi
            self.cleanup_old_backups()
            
            # 5. Report finale
            logger.info("[COMPLETE] AGGIORNAMENTO GIORNALIERO COMPLETATO!")
            logger.info(f"[SUCCESS] Config autonomo: {os.path.relpath(best_config_path)}")
            logger.info(f"[SUCCESS] Config produzione: {os.path.relpath(production_config_path)}")
            
            if backup_mapping:
                logger.info(f"[BACKUP] Backup precedenti: {len(backup_mapping)} file")
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Errore aggiornamento giornaliero: {e}")
            return False

def main():
    """Entry point principale"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Config Updater per The5ers')
    parser.add_argument('--days', type=int, default=30, help='Giorni di ottimizzazione (default: 30)')
    parser.add_argument('--no-backup', action='store_true', help='Disabilita backup configurazioni esistenti')
    parser.add_argument('--quiet', action='store_true', help='Solo log su file, niente output console')
    
    args = parser.parse_args()
    
    # Configura logging se richiesto quiet
    if args.quiet:
        # Rimuove handler console, mantiene solo file
        logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]
    
    # Inizializza updater
    updater = DailyConfigUpdater(
        optimization_days=args.days,
        backup_old_configs=not args.no_backup
    )
    
    # Esegui aggiornamento
    success = updater.run_daily_update()
    
    # Exit code per cronjob
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
