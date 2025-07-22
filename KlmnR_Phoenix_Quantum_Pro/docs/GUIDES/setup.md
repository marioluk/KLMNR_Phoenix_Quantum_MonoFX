
# Guida Installazione e Avvio Rapido

## Prerequisiti
- Python 3.10+
- MetaTrader 5 installato (solo server)
- Configurazione broker in `config/`

## Installazione
1. Clona il repository:
   ```sh
   git clone https://github.com/marioluk/KLMNR_Phoenix_Quantum.git
   ```
2. Installa le dipendenze:
   ```sh
   pip install -r requirements.txt
   ```
3. Configura i parametri in `config/multi_broker_master_config.json`

## Avvio rapido
1. Avvia MT5 in modalità background (solo server):
   ```sh
   start_multi_broker_service.bat
   ```
2. Avvia il sistema quantum:
   ```sh
   python quantum_main_refactored.py
   ```

## Best practice
- Eseguire sempre backup della configurazione
- Validare la connessione broker prima di operare

---
Vedi anche: [Guida Avvio Automatico](README_AVVIO_AUTOMATICO.md)
