# TODO Phoenix Quantum MonoFX – Attività Aperte

## Dashboard & UX
- [ ] **[MEDIA] Statistiche e grafici aggregati** (ratio BUY/SELL, motivi di scarto, distribuzione segnali)
- [ ] **[MEDIA] Visualizzazione parametri attivi di filtro** (entropy, spin, confidence, cooldown, orari, spread, ecc.)
- [ ] **[MEDIA] Evidenziare parametri troppo restrittivi rispetto ai dati storici**
- [ ] **[MEDIA] Modifica rapida dei parametri di filtro dalla dashboard**
- [ ] **[ALTA] Notifiche real-time** (disconnessione MT5, drawdown critico, target raggiunto)
- [ ] **[ALTA] Storico errori/warning** e miglioramento UI/UX (responsive, dark/light, icone)
- [ ] **[MEDIA] Togliere tutti i riferimenti a legacy e sostituire con mono**
- [ ] **[MEDIA] Test e confronto di tutti i tipi di trading dalla dashboard**
- [ ] **[MEDIA] Configurazione avanzata: selezione file config/log da interfaccia, modifica parametri da dashboard**
- [ ] **[MEDIA] Definire formato dati condiviso (JSON, CSV, DB) tra codice e dashboard**
- [ ] **[MEDIA] Documentare chiaramente tutti i motivi di blocco e la loro logica**
- [ ] **[MEDIA] Aggiornare guida utente/dashboard con sezione debug segnali e best practice**

## Backtest & Analisi
- [ ] **[MEDIA] Testare e confrontare tutti i tipi di trading in backtest_mono**
- [ ] **[MEDIA] Migliorare parsing log per estrarre dettagli utili** (motivo blocco, valori entropy/spin, parametri attivi)
- [ ] **[MEDIA] Validare coerenza timeline segnali tra dashboard, log e logica di filtro**
- [ ] **[MEDIA] Simulazione segnali con parametri meno restrittivi**
- [ ] **[MEDIA] Report automatico su filtri troppo stringenti**
- [ ] **[BASSA] Replay di una giornata di log**
- [ ] **[MEDIA] Refactoring codice:** separare logica backend, API e frontend
- [ ] **[MEDIA] Gestione edge case:** fusi orari, giorni festivi, variabili thread-safe
- [ ] **[MEDIA] Test automatici/unitari per business logic, parsing log, API, metriche**
- [ ] **[MEDIA] Type hint, docstring, gestione eccezioni, metodi privati per evitare duplicazioni**

## Documentazione & Best Practice
- [ ] **Aggiornare guida utente e README con esempi di configurazione e avvio**
- [ ] **Documentare API e struttura dati condivisa tra backend e dashboard**
- [ ] **Mantenere changelog e roadmap sempre aggiornati**

---

**Legenda Priorità:**
- [ALTA] = Critico/da fare subito
- [MEDIA] = Importante/da pianificare
- [BASSA] = Miglioria/fine tuning

---

*Ultimo aggiornamento: 01/08/2025*
