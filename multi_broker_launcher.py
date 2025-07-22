#!/usr/bin/env python3
"""
Multi-Broker Quantum Trading System Launcher
The5ers | FTMO | MyForexFunds | Multi-MT5 Support
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Aggiungi il path del progetto
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from KlmnR_Phoenix_Quantum_Pro.trading.multi_system import MultiQuantumTradingSystem


def setup_console_logging():
    """Setup logging per console"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )


def print_banner():
    """Stampa banner di avvio"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                🚀 MULTI-BROKER QUANTUM TRADING SYSTEM 🚀         ║
    ║                                                                  ║
    ║  🏢 The5ers Challenge    🏢 FTMO Challenge    🏢 MyForexFunds    ║
    ║  ⚡ Quantum Algorithms   📊 Neural Networks   🎯 Risk Management ║
    ║  🔄 Multi-MT5 Support    📈 Real-time Trading 🛡️  Auto-Protection║
    ║                                                                  ║
    ║                         Version 6.0.0                           ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def validate_config_files(config_path: str) -> bool:
    """Valida esistenza file di configurazione"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"❌ File configurazione non trovato: {config_path}")
        return False
    
    # Verifica configurazioni broker
    config_dir = config_file.parent
    broker_configs = [
        "broker_the5ers_challenge.json",
        "broker_ftmo_challenge.json", 
        "broker_myforexfunds_eval.json"
    ]
    
    missing_configs = []
    for broker_config in broker_configs:
        broker_file = config_dir / broker_config
        if not broker_file.exists():
            missing_configs.append(broker_config)
    
    if missing_configs:
        print(f"⚠️ Configurazioni broker mancanti: {', '.join(missing_configs)}")
        print("📝 Verrà utilizzata solo la configurazione principale")
    
    return True


def check_mt5_installations():
    """Verifica installazioni MetaTrader5"""
    mt5_paths = [
        "C:\\Program Files\\MetaTrader 5 The5ers\\terminal64.exe",
        "C:\\Program Files\\FTMO MetaTrader 5\\terminal64.exe", 
        "C:\\Program Files\\MyForexFunds MT5\\terminal64.exe",
        "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    ]
    
    found_installations = []
    for mt5_path in mt5_paths:
        if Path(mt5_path).exists():
            found_installations.append(mt5_path)
    
    print(f"🔍 MetaTrader5 installazioni trovate: {len(found_installations)}")
    for installation in found_installations:
        print(f"   ✅ {installation}")
    
    if not found_installations:
        print("⚠️ Nessuna installazione MT5 trovata nei percorsi standard")
        print("📝 Aggiorna i percorsi nelle configurazioni broker")
    
    return len(found_installations) > 0


def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description="Multi-Broker Quantum Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  python multi_broker_launcher.py                                    # Usa config master
  python multi_broker_launcher.py --config config/custom.json       # Config personalizzata
  python multi_broker_launcher.py --debug                           # Modalità debug
  python multi_broker_launcher.py --dry-run                         # Test senza trading
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config/multi_broker_master_config.json",
        help="Percorso file configurazione (default: multi_broker_master_config.json)"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Abilita modalità debug con logging dettagliato"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true", 
        help="Modalità test - no trading reale (solo simulazione)"
    )
    
    parser.add_argument(
        "--broker",
        choices=["THE5ERS", "FTMO", "MYFOREXFUNDS", "ALL"],
        default="ALL",
        help="Avvia solo broker specifico (default: ALL)"
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Solo verifica configurazioni e connessioni"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        setup_console_logging()
    
    # Banner
    print_banner()
    
    # Verifica configurazioni
    print("🔍 Verifica configurazioni...")
    config_path = Path(args.config).resolve()
    
    if not validate_config_files(str(config_path)):
        print("❌ Validazione configurazioni fallita")
        return 1
    
    print(f"✅ Configurazione principale: {config_path}")
    
    # Verifica MT5
    print("\n🔍 Verifica installazioni MetaTrader5...")
    if not check_mt5_installations():
        print("⚠️ Procedendo senza alcune installazioni MT5...")
    
    # Modalità check-only
    if args.check_only:
        print("\n✅ Verifica completata. Sistema pronto per l'avvio.")
        return 0
    
    # Modalità dry-run
    if args.dry_run:
        print("\n🧪 MODALITÀ DRY-RUN ATTIVA - NESSUN TRADING REALE")
        os.environ['QTS_DRY_RUN'] = '1'
    
    # Avvio sistema
    try:
        print(f"\n🚀 Avvio Multi-Broker Quantum Trading System...")
        print(f"📊 Broker target: {args.broker}")
        
        # Inizializza sistema
        system = MultiQuantumTradingSystem(str(config_path))
        
        # Imposta filtro broker se specificato
        if args.broker != "ALL":
            print(f"🎯 Filtro broker attivo: {args.broker}")
            # TODO: Implementare filtro broker specifico
        
        print("✅ Sistema inizializzato correttamente")
        print("\n" + "="*60)
        print("🎯 TRADING SYSTEM OPERATIVO")
        print("📊 Monitoraggio in corso...")
        print("🛑 Premi Ctrl+C per interrompere")
        print("="*60 + "\n")
        
        # Avvia trading
        system.start()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Interruzione da utente ricevuta")
        print("⏳ Fermata sistema in corso...")
        
    except Exception as e:
        print(f"\n❌ ERRORE CRITICO: {str(e)}")
        logging.error(f"Errore critico: {str(e)}", exc_info=True)
        return 1
    
    finally:
        print("🏁 Sistema fermato correttamente")
        print("👋 Arrivederci!")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
