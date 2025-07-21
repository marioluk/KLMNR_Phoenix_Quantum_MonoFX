
# Modulo Metrics

## Descrizione
Il modulo Metrics raccoglie e analizza le performance del sistema, producendo report e statistiche custom.

### Principali metriche
- Sharpe Ratio
- Max Drawdown
- Win Rate
- Profit Factor

### Esempio di utilizzo
```python
from metrics import calculate_sharpe, calculate_drawdown
sharpe = calculate_sharpe(returns)
dd = calculate_drawdown(equity_curve)
```

### Best practice
- Automatizzare la raccolta dati
- Validare le metriche con test

---
Vedi anche: [Refactoring Guide](../REFERENCE/refactoring_guide.md)
