# Daily Trade Limit Mode

Questa configurazione controlla come viene applicato il limite massimo di operazioni giornaliere (`max_daily_trades`) nel sistema Phoenix Quantum MonoFX.

## Opzioni disponibili

- `"daily_trade_limit_mode": "per_symbol"`
  - Il limite viene applicato separatamente per ogni simbolo.
  - Esempio: con `max_daily_trades: 6`, puoi fare fino a 6 trade su EURUSD, 6 su USDJPY, ecc.
- `"daily_trade_limit_mode": "global"`
  - Il limite viene applicato come somma totale su tutti i simboli.
  - Esempio: con `max_daily_trades: 6`, puoi fare 6 trade in totale sommando tutti i simboli.

## Dove si imposta

Aggiungi il parametro nella sezione `risk_parameters` del file di configurazione:

```json
"risk_parameters": {
    "max_daily_trades": 6,
    "daily_trade_limit_mode": "per_symbol"
    // ...altri parametri...
}
```

Se il parametro manca, il sistema userà la modalità `global` come default.

## Impatto

- La modalità scelta influenza sia il comportamento live che la generazione automatica delle configurazioni tramite l'optimizer.
- Puoi cambiare la modalità in qualsiasi momento modificando il file di configurazione e riavviando lo script.

---
Per dettagli tecnici vedi anche i commenti inline in `autonomous_challenge_optimizer.py` e la documentazione generale del progetto.
