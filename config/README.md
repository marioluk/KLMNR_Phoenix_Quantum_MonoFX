# ## [2025-08-01] Migliorie gestione drawdown
# - safe_limit, soft_limit e hard_limit sono ora sempre presenti nel file di configurazione generato.
# - Tutta la logica di gestione del rischio e protezione drawdown è ora completamente config-driven.
# - Verificato l’utilizzo corretto di tutti i limiti nel sistema di trading principale.
## README Configurazione

## Logica automatica: giorni ottimali e parametri per tipologia

La generazione delle configurazioni tramite `autonomous_challenge_optimizer.py` è ora completamente automatizzata:

- Il menu interattivo mostra i parametri principali per ogni tipologia di trading.
- I giorni di ottimizzazione vengono suggeriti automaticamente in base alla tipologia selezionata:
  - Scalping: 30 giorni
  - Intraday: 60 giorni
  - Swing: 120 giorni
  - Position: 180 giorni
- Tutti i parametri sono validati e coerenti con la tipologia scelta.
- Possibilità di tornare indietro senza uscire dal programma.

Consulta la tabella parametri nel codice per dettagli su SL/TP/TS e range operativi.

### Log dettagliato calcolo size (risk management)
Per abilitare il log dettagliato del calcolo della size (incluso [SIZE-DEBUG] con risk_amount, sl_pips, pip_value, contract_size, size e tipo strumento):

1. Apri il file `config_autonomous_challenge_production_ready.json`.
2. Nella sezione `"logging"`, imposta:
   ```json
   "log_level": "DEBUG"
   ```
3. Riavvia il sistema di trading.

Vedrai nei log tutte le informazioni utili per il debug delle differenze tra forex, indici e metalli.

### Note aggiuntive
- Ricordati di riportare il log_level a "INFO" in produzione per evitare file di log troppo grandi.
- Per troubleshooting avanzato, consulta anche la documentazione tecnica nella cartella `docs/`.

---

## 📑 Parametri di configurazione accettati

| Chiave principale | Sottochiave / Parametro         | Tipo      | Default / Esempio | Descrizione breve |
|-------------------|----------------------------------|-----------|-------------------|-------------------|
| logging           | log_file                         | string    | logs/log_...log   | Path file di log  |
| logging           | max_size_mb                      | int       | 50                | Max size log (MB) |
| logging           | backup_count                     | int       | 7                 | Rotazione log     |
| logging           | log_level                        | string    | INFO              | Livello log       |
| metatrader5       | login                            | int       | ...               | Login MT5         |
| metatrader5       | password                         | string    | ...               | Password MT5      |
| metatrader5       | server                           | string    | ...               | Server MT5        |
| metatrader5       | path                             | string    | ...               | Path terminal     |
| metatrader5       | port                             | int       | 18889             | Porta terminal    |
| account_currency  |                                  | string    | USD               | Valuta account    |
| initial_balance   |                                  | float     | 5000              | Balance iniziale  |
| quantum_params    | buffer_size                      | int       | 200               | Buffer segnali    |
| quantum_params    | signal_cooldown                  | int       | 300               | Cooldown segnali  |
| quantum_params    | adaptive_threshold               | float     | ...               | Soglia adattiva   |
| quantum_params    | volatility_filter                | float     | ...               | Filtro volatilità |
| quantum_params    | trend_strength_min               | float     | 0.6               | Min trend         |
| quantum_params    | confluence_threshold             | float     | ...               | Soglia confluenza |
| quantum_params    | quantum_boost                    | bool      | true              | Boost quantum     |
| quantum_params    | neural_enhancement               | bool      | true              | Potenziamento NN  |
| quantum_params    | spin_window                      | int       | 20                | Finestra spin     |
| quantum_params    | min_spin_samples                 | int       | 5                 | Min campioni spin |
| risk_parameters   | magic_number                     | int       | ...               | Magic number      |
| risk_parameters   | position_cooldown                | int       | 900               | Cooldown posizioni|
| risk_parameters   | max_daily_trades                 | int       | 4                 | Max trade/giorno  |
| risk_parameters   | daily_trade_limit_mode           | string    | per_symbol        | Limite trade/giorno|
| risk_parameters   | max_positions                    | int       | 1                 | Max posizioni     |
| risk_parameters   | profit_multiplier                | float     | 2.2               | Moltiplicatore TP |
| risk_parameters   | max_position_hours               | int       | 6                 | Max ore posizione |
| risk_parameters   | risk_percent                     | float     | 0.005             | % rischio trade   |
| symbols           | <SYMBOL>                         | oggetto   | ...               | Config per simbolo|
| symbols.<SYMBOL>  | risk_management                  | oggetto   | ...               | SL/TP/risk per sym|
| symbols.<SYMBOL>  | timezone                         | string    | Europe/Rome       | Fuso orario       |
| symbols.<SYMBOL>  | trading_hours                    | lista     | ...               | Orari trading     |
| symbols.<SYMBOL>  | quantum_params_override           | oggetto   | ...               | Override quantum  |
| challenge_specific| step1_target                     | float     | 8                 | Target profit %   |
| challenge_specific| max_daily_loss_percent           | float     | 5                 | Max perdita/giorno|
| challenge_specific| max_total_loss_percent           | float     | 10                | Max perdita totale|
| challenge_specific| drawdown_protection.soft_limit   | float     | 0.02              | Soft DD limit     |
| challenge_specific| drawdown_protection.hard_limit   | float     | 0.05              | Hard DD limit     |
| conversion_metadata| created_by                       | string    | ...               | Tool generazione  |
| conversion_metadata| creation_date                    | string    | ...               | Data creazione    |
| conversion_metadata| aggressiveness                   | string    | ...               | Profilo rischio   |

> Per ogni simbolo (es. EURUSD, SP500, USDJPY, ecc.) vanno definiti almeno: `risk_management`, `timezone`, `trading_hours`. Gli override sono opzionali.

---

Questa tabella riassume tutti i parametri accettati nei file di configurazione. Per dettagli avanzati, consultare anche la documentazione tecnica in `docs/`.