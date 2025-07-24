## README Configurazione

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