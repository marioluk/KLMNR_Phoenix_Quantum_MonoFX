
# Guida Multi-Broker

## Descrizione
Il sistema quantum supporta operatività multi-broker con configurazione centralizzata e gestione automatica.

## Setup multi-broker
1. Configura ogni broker in `config/`
2. Verifica mapping simboli in `broker_symbol_mapping.json`
3. Avvia il sistema con:
   ```sh
   python quantum_main_refactored.py
   ```

## Esempio di configurazione
```json
{
  "brokers": ["The5ers", "FTMO", "Topstep"],
  "symbols": ["EURUSD", "USDJPY"]
}
```

## Best practice
- Validare la connessione di ogni broker
- Monitorare i log per errori di mapping

---
Vedi anche: [Modulo Brokers](../MODULES/brokers.md)
