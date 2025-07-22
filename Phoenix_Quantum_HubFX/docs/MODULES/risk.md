
# Modulo Risk

## Descrizione
Il modulo Risk gestisce la protezione del capitale, il calcolo del drawdown e il sizing delle posizioni in base ai parametri configurati.

### Flusso operativo
1. Ricezione segnali dal modulo engine
2. Calcolo rischio e validazione operatività
3. Invio segnali validati al modulo trading

### Principali funzioni
- `calculate_drawdown(equity_curve)`
- `validate_signal(signal, risk_params)`

### Esempio di utilizzo
```python
from risk import calculate_drawdown, validate_signal
dd = calculate_drawdown(equity_curve)
if validate_signal(signal, risk_params):
    trader.execute(signal)
```

### Best practice
- Separare calcolo rischio da logica di trading
- Validare ogni segnale prima dell’esecuzione

---
Vedi anche: [Refactoring Guide](../REFERENCE/refactoring_guide.md)
