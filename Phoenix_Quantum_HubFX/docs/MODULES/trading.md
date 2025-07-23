
# Modulo Trading

## Descrizione
Il modulo Trading coordina il ciclo operativo, gestisce l’invio ordini e l’integrazione multi-broker.

### Ciclo operativo
1. Ricezione segnali validati
2. Invio ordini ai broker
3. Monitoraggio esecuzione e logging (log_utils)

### Principali classi
- `TradingCoordinator`: orchestrazione ordini e broker

### Esempio di utilizzo
```python
from trading import TradingCoordinator
trader = TradingCoordinator(config)
trader.execute(signals)
```

### Best practice
- Gestire errori e retry automatici
- Logging dettagliato di ogni operazione (log_utils)

---
Vedi anche: [Refactoring Guide](../REFERENCE/refactoring_guide.md)
