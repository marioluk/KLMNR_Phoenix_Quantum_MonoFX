# TODO Analisi Segnali Trading & Apertura Posizioni

## Obiettivo
Capire perché l'algoritmo non apre posizioni e avere chiarezza sui segnali di trading, sia nei log che nella dashboard.

## Azioni da implementare

1. **Log dettagliato dei segnali (tick-by-tick)**
   - Ogni segnale viene loggato subito (tick-by-tick), senza report periodico.
   - Il log include:
     - Segnale ricevuto (simbolo, entropy, spin, timestamp, ecc.)
     - Motivazione per cui viene aperta o scartata una posizione
     - Eventuali filtri o condizioni che bloccano l'apertura

2. **Dashboard: tabella segnali e aggregazione**
   - La dashboard dovrà aggregare i log tick-by-tick e mostrare:
     - Timestamp, simbolo, entropy, spin, direzione, esito (aperta/scartata), motivazione
     - Statistiche e grafici aggregati

3. **Codice di trading**
   - Individuare dove viene gestito il segnale e dove viene chiamata la funzione di apertura ordine
   - Aggiungere log come descritto sopra

4. **Visualizzazione**
   - Aggiungere nella dashboard una sezione che mostri la sequenza dei segnali e il relativo esito

---

## Note
- Il logging dei segnali è ora tick-by-tick, senza report periodico.
- La dashboard dovrà occuparsi di aggregazione e visualizzazione.
- La logica di apertura posizione probabilmente non è in `dashboard_broker.py` ma nello script di trading principale.
- Serve collaborazione tra log, codice di trading e dashboard per una diagnosi efficace.
