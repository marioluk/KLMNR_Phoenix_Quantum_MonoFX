#!/usr/bin/env python3
"""
DAILY CONFIG UPDATER - Sistema di Aggiornamento Automatico Configurazioni
==========================================================================

Sistema automatizzato per l'aggiornamento giornaliero delle configurazioni di trading
utilizzando il processo di ottimizzazione autonoma con selezione automatica della 
configurazione migliore e conversione al formato di produzione.

Caratteristiche:
- Backup automatico delle configurazioni esistenti
- Generazione configurazione ottimale tramite autonomous high stakes optimizer
- Selezione automatica del file BEST
- Salvataggio diretto con nome standard (senza [BEST])
- Conversione formato produzione
- Validazione completa
- Logging dettagliato
- Gestione errori robusta

Utilizzo Cronjob:
Windows Task Scheduler: 06:00 ogni giorno
Linux Crontab: 0 6 * * *

Autore: KLMNR System
Data: 20 Luglio 2025
"""

import os
import sys
import json
import shutil
import logging
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


class DailyConfigUpdater:
    """
    Orchestratore principale per l'aggiornamento automatico delle configurazioni
    """
    
    def __init__(self, 
                 workspace_dir: Optional[str] = None,
                 backup_retention_days: int = 30,
                 log_level: str = "INFO"):
        """
        Inizializza il sistema di aggiornamento giornaliero
        
        Args:
            workspace_dir: Directory workspace (auto-detect se None)
            backup_retention_days: Giorni di retention backup
            log_level: Livello logging
        """
        
        # Configurazione directory
        self.workspace_dir = Path(workspace_dir) if workspace_dir else self._find_workspace_dir()
        self.backup_dir = self.workspace_dir / "config" / "backups" / "daily_auto"
        self.config_dir = self.workspace_dir / "config"
        self.tools_dir = self.workspace_dir / "tools"
        
        # Configurazione sistema
        self.backup_retention_days = backup_retention_days
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup logging
        self.logger = self._setup_logging(log_level)
        
        # Paths importanti
        self.autonomous_optimizer_path = self.tools_dir / "autonomous_high_stakes_optimizer.py"
        self.production_converter_path = self.tools_dir / "production_config_converter.py"
        
        # File di configurazione standard (senza [BEST])
        self.standard_config_name = "config_autonomous_high_stakes_conservative_production_ready.json"
        self.target_config_path = self.config_dir / self.standard_config_name
        
        self.logger.info(f"🚀 DailyConfigUpdater inizializzato")
        self.logger.info(f"📁 Workspace: {self.workspace_dir}")
        self.logger.info(f"🎯 Target config: {self.target_config_path}")
        
        
    def _find_workspace_dir(self) -> Path:
        """Auto-rileva la directory workspace"""
        current = Path.cwd()
        
        # Cerca indicatori di workspace
        workspace_indicators = [
            "quantum_trading_system",
            "legacy_system", 
            "tools",
            "config"
        ]
        
        # Controlla directory corrente e parent
        for path in [current] + list(current.parents):
            if all((path / indicator).exists() for indicator in workspace_indicators):
                return path
                
        # Fallback
        return current
        
        
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Configura sistema di logging"""
        logger = logging.getLogger('DailyConfigUpdater')
        
        if logger.handlers:
            return logger
            
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = self.workspace_dir / "logs" / "daily_updater"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"daily_updater_{self.timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.propagate = False
        return logger


    def run_daily_update(self) -> bool:
        """
        Esegue l'aggiornamento giornaliero completo
        
        Returns:
            True se successo, False se errore
        """
        
        self.logger.info("=" * 80)
        self.logger.info("🌅 AVVIO AGGIORNAMENTO GIORNALIERO CONFIGURAZIONI")
        self.logger.info("=" * 80)
        
        try:
            # 1. Validazioni preliminari
            if not self._validate_environment():
                return False
                
            # 2. Backup configurazioni esistenti
            if not self._backup_existing_configs():
                return False
                
            # 3. Pulizia backup vecchi
            self._cleanup_old_backups()
            
            # 4. Genera configurazione migliore e salva con nome standard
            if not self._generate_optimal_config():
                return False
                
            # 5. Report finale
            self._generate_final_report()
            
            self.logger.info("=" * 80)
            self.logger.info("✅ AGGIORNAMENTO GIORNALIERO COMPLETATO CON SUCCESSO")
            self.logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRORE CRITICO: {e}", exc_info=True)
            return False


    def _validate_environment(self) -> bool:
        """Valida ambiente di esecuzione"""
        
        self.logger.info("🔍 Validazione ambiente...")
        
        # Controlla directory essenziali
        required_dirs = [self.config_dir, self.tools_dir]
        for dir_path in required_dirs:
            if not dir_path.exists():
                self.logger.error(f"❌ Directory mancante: {dir_path}")
                return False
                
        # Controlla script necessari
        required_scripts = [self.autonomous_optimizer_path, self.production_converter_path]
        for script_path in required_scripts:
            if not script_path.exists():
                self.logger.error(f"❌ Script mancante: {script_path}")
                return False
                
        # Controlla Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, check=True)
            self.logger.info(f"✅ Python: {result.stdout.strip()}")
        except subprocess.SubprocessError as e:
            self.logger.error(f"❌ Errore Python: {e}")
            return False
            
        self.logger.info("✅ Ambiente validato")
        return True


    def _backup_existing_configs(self) -> bool:
        """Crea backup delle configurazioni esistenti"""
        
        self.logger.info("💾 Backup configurazioni esistenti...")
        
        try:
            # Crea directory backup
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_created = False
            
            # Backup configurazione target se esiste
            if self.target_config_path.exists():
                backup_name = f"{self.standard_config_name}.backup_{self.timestamp}"
                backup_path = self.backup_dir / backup_name
                
                shutil.copy2(self.target_config_path, backup_path)
                self.logger.info(f"✅ Backup creato: {backup_name}")
                backup_created = True
                
            # Backup di altre configurazioni importanti
            config_patterns = [
                "config_autonomous_high_stakes_*.json",
                "*_production_ready.json"
            ]
            
            for pattern in config_patterns:
                for config_file in self.config_dir.glob(pattern):
                    if config_file != self.target_config_path:  # Evita duplicati
                        backup_name = f"{config_file.name}.backup_{self.timestamp}"
                        backup_path = self.backup_dir / backup_name
                        
                        shutil.copy2(config_file, backup_path)
                        self.logger.info(f"✅ Backup aggiuntivo: {backup_name}")
                        backup_created = True
                        
            if not backup_created:
                self.logger.warning("⚠️ Nessuna configurazione da backuppare trovata")
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore backup: {e}")
            return False


    def _cleanup_old_backups(self):
        """Rimuove backup più vecchi del retention period"""
        
        try:
            if not self.backup_dir.exists():
                return
                
            cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob("*.backup_*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    removed_count += 1
                    
            if removed_count > 0:
                self.logger.info(f"🧹 Rimossi {removed_count} backup obsoleti")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Errore pulizia backup: {e}")


    def _generate_optimal_config(self) -> bool:
        """Genera configurazione ottimale e salva con nome standard"""
        
        self.logger.info("=== GENERAZIONE CONFIGURAZIONE OTTIMALE ===")
        
        try:
            # 1. Esegui autonomous high stakes optimizer con Auto-Best
            if not self._run_autonomous_optimizer():
                return False
                
            # 2. Trova il file BEST generato
            best_config_path = self._find_best_config_file()
            if not best_config_path:
                self.logger.error("❌ File BEST non trovato")
                return False
                
            # 3. Converte e salva direttamente con nome standard (senza [BEST])
            if not self._convert_and_save_as_standard(best_config_path):
                return False
                
            # 4. Valida configurazione finale
            if not self._validate_final_config():
                return False
                
            self.logger.info("✅ Configurazione ottimale generata e salvata")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore generazione configurazione: {e}")
            return False


    def _run_autonomous_optimizer(self) -> bool:
        """Esegue l'autonomous high stakes optimizer"""
        
        self.logger.info("🤖 Esecuzione autonomous high stakes optimizer...")
        
        try:
            # Comando per eseguire l'optimizer con Auto-Best (opzione 3)
            cmd = [
                sys.executable,
                str(self.autonomous_optimizer_path),
                "--days", "30",  # Ultimi 30 giorni
                "--auto-best"    # Selezione automatica migliore
            ]
            
            self.logger.info(f"Comando: {' '.join(cmd)}")
            
            # Esegui con timeout
            result = subprocess.run(
                cmd,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minuti timeout
                check=False
            )
            
            # Log output
            if result.stdout:
                self.logger.info("Output optimizer:")
                for line in result.stdout.strip().split('\n'):
                    self.logger.info(f"  {line}")
                    
            if result.stderr:
                self.logger.warning("Stderr optimizer:")
                for line in result.stderr.strip().split('\n'):
                    self.logger.warning(f"  {line}")
                    
            if result.returncode != 0:
                self.logger.error(f"❌ Optimizer fallito con codice: {result.returncode}")
                return False
                
            self.logger.info("✅ Autonomous optimizer completato")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Timeout optimizer (>5 minuti)")
            return False
        except Exception as e:
            self.logger.error(f"❌ Errore esecuzione optimizer: {e}")
            return False


    def _find_best_config_file(self) -> Optional[Path]:
        """Trova il file di configurazione BEST più recente"""
        
        self.logger.info("🔍 Ricerca file BEST...")
        
        try:
            # Pattern per file BEST
            best_patterns = [
                "config_autonomous_high_stakes_*[BEST]*.json",
                "*[BEST]*.json"
            ]
            
            best_files = []
            
            for pattern in best_patterns:
                best_files.extend(self.config_dir.glob(pattern))
                
            if not best_files:
                self.logger.error("❌ Nessun file BEST trovato")
                return None
                
            # Trova il più recente
            latest_best = max(best_files, key=lambda f: f.stat().st_mtime)
            
            self.logger.info(f"✅ File BEST trovato: {latest_best.name}")
            return latest_best
            
        except Exception as e:
            self.logger.error(f"❌ Errore ricerca BEST: {e}")
            return None


    def _convert_and_save_as_standard(self, best_config_path: Path) -> bool:
        """Converte il file BEST e lo salva con nome standard"""
        
        self.logger.info("🔄 Conversione e salvataggio configurazione standard...")
        
        try:
            # Comando per convertire in formato produzione
            cmd = [
                sys.executable,
                str(self.production_converter_path),
                str(best_config_path),
                "--output", str(self.target_config_path),  # Salva direttamente con nome standard
                "--optimize"
            ]
            
            self.logger.info(f"Comando conversione: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=120,  # 2 minuti timeout
                check=False
            )
            
            # Log output
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    self.logger.info(f"  {line}")
                    
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    self.logger.warning(f"  {line}")
                    
            if result.returncode != 0:
                self.logger.error(f"❌ Conversione fallita con codice: {result.returncode}")
                return False
                
            # Verifica che il file sia stato creato
            if not self.target_config_path.exists():
                self.logger.error(f"❌ File target non creato: {self.target_config_path}")
                return False
                
            self.logger.info(f"✅ Configurazione salvata come: {self.target_config_path.name}")
            
            # Rimuovi il file BEST temporaneo se diverso dal target
            if best_config_path != self.target_config_path:
                try:
                    best_config_path.unlink()
                    self.logger.info(f"🧹 File BEST temporaneo rimosso: {best_config_path.name}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Non riuscito a rimuovere file BEST: {e}")
                    
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Timeout conversione (>2 minuti)")
            return False
        except Exception as e:
            self.logger.error(f"❌ Errore conversione: {e}")
            return False


    def _validate_final_config(self) -> bool:
        """Valida la configurazione finale"""
        
        self.logger.info("✅ Validazione configurazione finale...")
        
        try:
            if not self.target_config_path.exists():
                self.logger.error("❌ File configurazione finale non esiste")
                return False
                
            with open(self.target_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Validazioni essenziali
            required_sections = ['symbols', 'risk_parameters', 'quantum_params']
            for section in required_sections:
                if section not in config:
                    self.logger.error(f"❌ Sezione {section} mancante")
                    return False
                    
            # Controlla simboli
            symbols = config.get('symbols', {})
            if len(symbols) == 0:
                self.logger.error("❌ Nessun simbolo configurato")
                return False
                
            # Controlla metadata
            metadata = config.get('metadata', {})
            if 'creation_date' not in metadata:
                self.logger.warning("⚠️ Metadata incompleti")
                
            self.logger.info(f"✅ Configurazione validata: {len(symbols)} simboli")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON non valido: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Errore validazione: {e}")
            return False


    def _generate_final_report(self):
        """Genera report finale dell'aggiornamento"""
        
        self.logger.info("📊 Generazione report finale...")
        
        try:
            # Statistiche file di configurazione
            config_size = self.target_config_path.stat().st_size if self.target_config_path.exists() else 0
            
            # Carica configurazione per dettagli
            symbols_count = 0
            metadata = {}
            
            if self.target_config_path.exists():
                try:
                    with open(self.target_config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    symbols_count = len(config.get('symbols', {}))
                    metadata = config.get('metadata', {})
                except:
                    pass
                    
            # Conteggio backup
            backup_count = len(list(self.backup_dir.glob("*.backup_*"))) if self.backup_dir.exists() else 0
            
            # Report
            self.logger.info("=" * 60)
            self.logger.info("📋 REPORT AGGIORNAMENTO GIORNALIERO")
            self.logger.info("=" * 60)
            self.logger.info(f"📅 Data/Ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"📁 Workspace: {self.workspace_dir}")
            self.logger.info(f"🎯 Configurazione: {self.target_config_path.name}")
            self.logger.info(f"📏 Dimensione file: {config_size:,} bytes")
            self.logger.info(f"🔣 Simboli configurati: {symbols_count}")
            self.logger.info(f"💾 Backup creati: {backup_count}")
            
            if metadata:
                if 'optimization_score' in metadata:
                    self.logger.info(f"⭐ Score ottimizzazione: {metadata['optimization_score']:.4f}")
                if 'total_trades' in metadata:
                    self.logger.info(f"📈 Trades totali: {metadata['total_trades']}")
                if 'win_rate' in metadata:
                    self.logger.info(f"🎯 Win rate: {metadata['win_rate']:.1f}%")
                    
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Errore generazione report: {e}")


def main():
    """Funzione principale per esecuzione da cronjob"""
    
    # Parse argomenti di base
    import argparse
    parser = argparse.ArgumentParser(description="Daily Config Updater")
    parser.add_argument("--workspace", help="Directory workspace")
    parser.add_argument("--retention-days", type=int, default=30, 
                       help="Giorni retention backup")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    try:
        # Inizializza updater
        updater = DailyConfigUpdater(
            workspace_dir=args.workspace,
            backup_retention_days=args.retention_days,
            log_level=args.log_level
        )
        
        # Esegui aggiornamento
        success = updater.run_daily_update()
        
        # Exit code appropriato per cronjob
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"ERRORE CRITICO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
