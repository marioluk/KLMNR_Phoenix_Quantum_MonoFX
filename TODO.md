# TODO Analisi Segnali, Dashboard e Migliorie Phoenix Quantum MonoFX

> Questo file è la **roadmap e checklist ufficiale** del progetto Phoenix Quantum MonoFX.
> Contiene tutte le attività aperte, le priorità, le idee di miglioramento e le implementazioni pianificate.
> Aggiorna solo qui la lista delle cose da fare: tutti i file TODO secondari sono storici o di appoggio temporaneo.

## 1. Logging, Diagnostica e Trasparenza Segnali

- [ ] **[ALTA] Logging tick-by-tick di ogni segnale (BUY/SELL/HOLD/SCARTATO)** con:
    - [ ] **[ALTA] Simbolo, entropy, spin, confidence, timestamp, prezzo**
    - [ ] **[ALTA] Esito e motivazione (apertura/scarto)**
    - [ ] **[ALTA] Dettaglio su filtri/blocchi** (buffer insufficiente, confidence bassa, cooldown, spread, orario, max trade, ecc.)
- [ ] **[MEDIA] Esportazione segnali e motivi di blocco in CSV/JSON per analisi esterna**
- [ ] **[MEDIA] Aggiungere contatori per ogni tipo di blocco e report periodico sintetico nei log**
- [ ] **[MEDIA] Uniformare la struttura dei dati tra log, dashboard e funzioni di analisi**

## 2. Dashboard: Visualizzazione, Aggregazione e UX

- [ ] **[ALTA] Tabella cronologia/sequenza segnali con esito e motivazione**
- [ ] **[MEDIA] Statistiche e grafici aggregati** (ratio BUY/SELL, motivi di scarto, distribuzione segnali)
- [ ] **[MEDIA] Visualizzazione parametri attivi di filtro** (entropy, spin, confidence, cooldown, orari, spread, ecc.)
- [ ] **[MEDIA] Evidenziare parametri troppo restrittivi rispetto ai dati storici**
- [ ] **[MEDIA] Consentire modifica rapida dei parametri di filtro dalla dashboard**
- [ ] **[ALTA] Notifiche real-time** (es. disconnessione MT5, drawdown critico, target raggiunto)
- [ ] **[ALTA] Storico errori/warning** e miglioramento UI/UX (responsive, dark/light, icone)
- [ ] **[MEDIA] Esportazione dati e download CSV dalla dashboard**

## 3. Parsing, Analisi e Debug Strategia

- [ ] **[MEDIA] Migliorare parsing log per estrarre dettagli utili** (motivo blocco, valori entropy/spin, parametri attivi)
- [ ] **[MEDIA] Validare coerenza timeline segnali tra dashboard, log e logica di filtro**
- [ ] **[MEDIA] Simulazione segnali:** mostrare quanti sarebbero passati con parametri meno restrittivi
- [ ] **[MEDIA] Report automatico su filtri troppo stringenti** (es. “entropy > 0.8 ha bloccato il 90% dei segnali”)
- [ ] **[BASSA] Replay di una giornata di log** per vedere in tempo reale l’effetto dei filtri

## 4. Refactoring, Best Practice e Robustezza

- [ ] **[MEDIA] Validazione automatica della configurazione all’avvio**
- [ ] **[MEDIA] Centralizzare magic number e fallback/configurazioni**
- [ ] **[MEDIA] Type hint, docstring, gestione eccezioni, metodi privati per evitare duplicazioni**
- [ ] **[MEDIA] Test automatici/unitari per business logic, parsing log, API, metriche**
- [ ] **[MEDIA] Refactoring codice:** separare logica backend, API e frontend
- [ ] **[MEDIA] Edge case:** gestione fusi orari, giorni festivi, variabili thread-safe

## 5. Collaborazione log-dashboard e Documentazione

- [ ] **[MEDIA] Definire formato dati condiviso (JSON, CSV, DB) tra codice e dashboard**
- [ ] **[MEDIA] Coordinare periodicità di aggiornamento/lettura tra log e dashboard**
- [ ] **[MEDIA] Documentare chiaramente tutti i motivi di blocco e la loro logica**
- [ ] **[MEDIA] Aggiornare guida utente/dashboard con sezione debug segnali e best practice**

## 6. Nuove Implementazioni e Extra

- [ ] **[MEDIA] Possibilità di testare e confrontare tutti i tipi di trading in backtest_mono, segnalando la migliore configurazione**
- [ ] **[MEDIA] Togliere tutti i riferimenti a legacy e sostituire con mono**
- [ ] **[MEDIA] Configurazione avanzata:** selezione file config/log da interfaccia, modifica parametri da dashboard

---

> Aggiorna questa checklist man mano che completi le attività o identifichi nuove aree di intervento. Le priorità sono indicate tra parentesi quadre: **[ALTA]**, **[MEDIA]**, **[BASSA]**.
