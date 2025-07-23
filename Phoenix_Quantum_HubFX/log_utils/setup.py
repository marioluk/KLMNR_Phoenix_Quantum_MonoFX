# Utility per pulizia vecchi log
import os
def clean_old_logs(log_file="logs/default.log", max_backups=5):
    """Pulizia dei vecchi file di log"""
    try:
        for i in range(max_backups + 1, 10):
            fname = f"{log_file}.{i}"
            if os.path.exists(fname):
                os.remove(fname)
    except Exception as e:
        print(f"Pulizia log fallita: {str(e)}")
"""
Sistema di logging avanzato per Quantum Trading System
"""

import logging
import os
import json
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(config_path: str = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json") -> logging.Logger:
    """
    Configura il sistema di logging con rotazione file e output console
    
    Args:
        config_path: Percorso del file di configurazione JSON
        
    Returns:
        Logger configurato
    """
    logger = logging.getLogger('QuantumTradingSystem')

    # Rimuovi tutti gli handler esistenti per evitare duplicati o logger non configurati
    while logger.handlers:
        logger.handlers.pop()

    try:
        # Carica la configurazione
        with open(config_path) as f:
            config = json.load(f)

        log_config = config.get('logging', {})

        # Crea la directory dei log se non esiste
        log_file = log_config.get('log_file', 'logs/default.log')
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)

        # Formattazione
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler con rotazione
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get('max_size_mb', 10) * 1024 * 1024,
            backupCount=log_config.get('backup_count', 5),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))

        # Console Handler 
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))
        console_handler.setFormatter(formatter)

        # Configurazione finale
        logger.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    except Exception as e:
        # Fallback: solo console, livello WARNING
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
        logger.warning(f"[LOGGER FALLBACK] Errore configurazione logging: {e}")
    return logger
