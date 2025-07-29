

# ATTENZIONE: Questo file è stato accorpato nel nuovo TODO.md centrale.
# Consulta e aggiorna solo `TODO.md` nella root del progetto per la roadmap completa e aggiornata.
# Puoi mantenere qui note storiche o dettagli specifici temporanei.

# TODO Analisi Segnali Quantum - Diagnosi, Debug e Dashboard

## File coinvolti principali
- `phoenix_quantum_monofx_program.py`  →  logica segnali, logging, funzioni di trading (in particolare il metodo `get_signal`)
- `dashboard_mono/dashboard_broker.py` e altri file in `dashboard_mono/`  →  visualizzazione e aggregazione segnali
- `backtest_mono/autonomous_challenge_optimizer.py`  →  logica di ottimizzazione e test segnali
- File di log generati dal sistema (es. in `logs/`)
- Eventuali file di esportazione/interfaccia (es. CSV/JSON condivisi tra codice e dashboard)

---

## Obiettivo
- Capire perché la strategia/algoritmo non genera segnali/trade, rendere trasparente il processo di filtro e facilitare la diagnosi dei blocchi, sia nei log che nella dashboard.

---

## Azioni da implementare

- [ ] **Logging dettagliato dei segnali (tick-by-tick)**
    - [ ] Ogni segnale deve essere loggato in tempo reale, senza report periodico.
    - [ ] Il log deve includere:
        - [ ] Simbolo, entropy, spin, confidence, timestamp, prezzo
        - [ ] Esito: segnale generato (BUY/SELL/HOLD), motivazione (apertura/scarto)
        - [ ] Dettaglio su eventuali filtri/blocchi (es. buffer insufficiente, confidence bassa, cooldown attivo)
    - [ ] Il metodo di riferimento è `get_signal` in `phoenix_quantum_monofx_program.py` (già presente, ma da verificare/estendere se necessario).
    - [ ] Loggare ogni segnale bloccato con dettaglio del motivo (entropy, spin, confidence, orario, cooldown, spread, ecc.)
    - [ ] Assicurarsi che i motivi di blocco siano estratti e salvati nella timeline dei segnali (sia nei log che nella dashboard)
    - [ ] Aggiungere un contatore per ogni tipo di blocco (es. entropy, spin, orario, cooldown, spread, max trade, ecc.)
    - [ ] Esportare la sequenza segnali e motivi di blocco in CSV/Excel per analisi offline
    - [ ] Mostrare nella dashboard i motivi di blocco più frequenti (grafico/istogramma)

- [ ] **Dashboard: tabella segnali e aggregazione**
    - [ ] La dashboard deve aggregare i log tick-by-tick e mostrare:
        - [ ] Timestamp, simbolo, entropy, spin, confidence, direzione, esito, motivazione, prezzo
        - [ ] Statistiche e grafici aggregati (es. ratio BUY/SELL, motivi di scarto, distribuzione segnali)
    - [ ] Prevedere una sezione che mostri la sequenza dei segnali e il relativo esito.
    - [ ] Visualizzare nella dashboard i parametri attivi di filtro segnali (soglie entropy, spin, confidence, cooldown, orari, spread, ecc.)
    - [ ] Consentire la modifica rapida dei parametri di filtro (anche solo temporaneamente) per testare l'impatto sulla generazione segnali
    - [ ] Evidenziare nella dashboard se i parametri sono troppo restrittivi rispetto ai dati storici

- [ ] **Codice di trading e parsing dati**
    - [ ] Individuare dove viene gestito il segnale e dove viene chiamata la funzione di apertura ordine.
    - [ ] Assicurarsi che i log siano completi e che le motivazioni di scarto/apertura siano sempre tracciate.
    - [ ] Eventuale esportazione dei segnali su file CSV o altro formato per la dashboard.
    - [ ] Migliorare la funzione di parsing dei log per estrarre tutti i dettagli utili (motivo blocco, valori entropy/spin, parametri attivi al momento del segnale)
    - [ ] Uniformare la struttura dei dati tra log, dashboard e funzioni di analisi (es. motivi di blocco sempre presenti e standardizzati)
    - [ ] Validare che la timeline dei segnali in dashboard sia coerente con i log e con la logica di filtro

- [ ] **Analisi e Debug Strategia**
    - [ ] Aggiungere una funzione di "simulazione segnali" che mostra, per una finestra temporale, quanti segnali sarebbero passati con parametri meno restrittivi
    - [ ] Implementare un report automatico che suggerisce quali filtri sono troppo stringenti (es. "entropy > 0.8 ha bloccato il 90% dei segnali")
    - [ ] Consentire il replay di una giornata di log per vedere in tempo reale come agiscono i filtri

- [ ] **Collaborazione log-dashboard e documentazione**
    - [ ] Definire un formato dati condiviso (es. JSON, CSV, DB) per permettere alla dashboard di leggere i segnali generati dal codice di trading.
    - [ ] Coordinare la periodicità di aggiornamento/lettura tra log e dashboard.
    - [ ] Documentare chiaramente tutti i motivi di blocco possibili e la loro logica
    - [ ] Aggiornare la guida utente/dashboard con una sezione "debug segnali" e best practice per la diagnosi

---

## Note operative
- Il logging dei segnali è già tick-by-tick nel metodo `get_signal`, ma va verificata la completezza delle informazioni e la facilità di parsing per la dashboard.
- La dashboard dovrà occuparsi di aggregazione e visualizzazione, ma serve un formato dati chiaro e accessibile.
- La logica di apertura posizione è nel metodo `get_signal` e nei punti dove viene chiamato per il trading reale.
- Serve collaborazione tra log, codice di trading e dashboard per una diagnosi efficace e una visualizzazione chiara.
- L'obiettivo è rendere trasparente e facilmente analizzabile il processo di generazione e blocco dei segnali, per poter agire in modo mirato sui parametri o sulla logica.
