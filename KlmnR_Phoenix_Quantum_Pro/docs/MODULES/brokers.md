# Modulo Brokers

Integrazione e setup broker.

(Compila con contenuti da README_MULTI_BROKER.md e CONFIGURAZIONE_BROKER_GUIDE.md se necessario)

## Descrizione
Il modulo Brokers gestisce l’integrazione con i broker supportati tramite API, setup e validazione connessioni.

### Principali API/supporti
- MetaTrader 5 (MT5)
- The5ers, FTMO, Topstep, MyForexFunds, FundedNext

### Esempio di utilizzo
```python
from brokers import BrokerAPI
broker = BrokerAPI(config)
broker.connect()
broker.send_order(order)
```

### Best practice
- Validare la connessione ad ogni avvio
- Gestire errori di rete e timeout

---
Vedi anche: [Guida Multi-Broker](../GUIDES/multi_broker.md)
