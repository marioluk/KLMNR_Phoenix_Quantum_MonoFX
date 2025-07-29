# TODO Analisi Segnali Trading & Apertura Posizioni

## Obiettivo
Capire perché l'algoritmo non apre posizioni e avere chiarezza sui segnali di trading, sia nei log che nella dashboard.

## Azioni da implementare

1. **Log dettagliato dei segnali**
   - Per ogni segnale di trading, aggiungere un log che indichi:
     - Segnale ricevuto (simbolo, entropy, spin, timestamp, ecc.)
     - Motivazione per cui viene aperta o scartata una posizione
     - Eventuali filtri o condizioni che bloccano l'apertura

2. **Dashboard: tabella segnali**
   - Aggiungere una tabella nella dashboard che mostri la cronologia dei segnali con:
     - Timestamp, simbolo, entropy, spin, direzione, esito (aperta/scartata), motivazione

3. **Codice di trading**
   - Individuare dove viene gestito il segnale e dove viene chiamata la funzione di apertura ordine
   - Aggiungere log come descritto sopra

4. **Visualizzazione**
   - Aggiungere nella dashboard una sezione che mostri la sequenza dei segnali e il relativo esito

---

## Note
- La logica di apertura posizione probabilmente non è in `dashboard_broker.py` ma nello script di trading principale.
- Serve collaborazione tra log, codice di trading e dashboard per una diagnosi efficace.
