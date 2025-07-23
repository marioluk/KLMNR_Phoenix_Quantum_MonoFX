
# Modulo Utils

## Descrizione
Il modulo Utils contiene funzioni di supporto, mapping simboli, log_utils (logging custom) e conversioni dati.

### Principali utility
- `map_symbol(symbol)`: mapping tra simboli broker
- `log_event(event)`: logging custom (tramite log_utils)

### Esempio di utilizzo
```python
from utils import map_symbol, log_event
mapped = map_symbol('EURUSD')
log_event('Order sent')
```

### Best practice
- Centralizzare le utility per evitare duplicazioni
- Logging strutturato e timestamp (log_utils)

---
Vedi anche: [Refactoring Guide](../REFERENCE/refactoring_guide.md)
