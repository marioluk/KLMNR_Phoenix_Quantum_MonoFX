#!/usr/bin/env python3
"""
QUANTUM TRADING SYSTEM - MAIN LAUNCHER
Sistema di trading algoritmico quantistico modulare
"""

import sys
import logging
from pathlib import Path

# Aggiungi il path del modulo quantum_trading_system
sys.path.insert(0, str(Path(__file__).parent))

from quantum_trading_system import QuantumTradingSystem
from quantum_trading_system.logging import setup_logger

# Configurazione predefinita
CONFIG_FILE = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json"

def main():
    """
    Funzione principale per avviare il sistema di trading
    """
    print("=" * 60)
    print("🚀 QUANTUM TRADING SYSTEM - MILESTONE EDITION (REV 6.0)")
    print("🔬 Sistema modulare di trading algoritmico quantistico")
    print("=" * 60)
    
    # Setup logger
    logger = setup_logger(CONFIG_FILE)
    
    try:
        # Inizializza e avvia il sistema
        system = QuantumTradingSystem(CONFIG_FILE)
        
        print("\n✅ Sistema inizializzato con successo!")
        print("🎯 Premere Ctrl+C per fermare il sistema")
        print("-" * 60)
        
        # Avvia il sistema
        system.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Interruzione da utente ricevuta")
        logger.info("Sistema fermato dall'utente")
        
    except Exception as e:
        print(f"\n❌ Errore critico: {str(e)}")
        logger.critical(f"Errore iniziale: {str(e)}", exc_info=True)
        
    finally:
        print("\n📊 Sistema terminato")
        logger.info("Applicazione terminata")


if __name__ == "__main__":
    main()
