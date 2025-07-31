# TODO Analisi Segnali, Dashboard e Migliorie Phoenix Quantum MonoFX



## 🚨 PRIORITÀ: Debug Pipeline Segnali → Ordini

- [x] **Verificare generazione segnali** (log, dashboard, parametri corretti)
    - [done 30/07/2025] Debug approfondito su generazione segnali, parametri e log, ora tutto tracciato e visibile.
- [x] **Controllare motivi di blocco** (colonna motivazione, filtri attivi)
    - [done 30/07/2025] Tutti i motivi di blocco ora sono loggati, esportati e visualizzati in dashboard e diagnostica.
- [x] **Analizzare pipeline segnali→ordini** (funzioni di trasformazione, chiamate effettive)
    - [done 30/07/2025] Pipeline completamente tracciata, con log dettagliati e tracing su ogni step.
- [x] **Controllare errori runtime** (log, eccezioni, connessione broker)
    - [done 30/07/2025] Risolti errori AttributeError, threading MT5 e gestione eccezioni su trade.
- [x] **Verificare condizioni operative** (saldo, leva, modalità, parametri rischio)
    - [done 30/07/2025] Tutti i parametri di rischio e operatività ora sono loggati e validati a runtime.
- [x] **Test manuale** (forzare segnale valido, ridurre filtri temporaneamente)
    - [done 30/07/2025] Test manuale completato: trade eseguito correttamente dopo fix pipeline.
- [x] **Analisi codice** (condizioni if, chiamate effettive invio ordini)


[IN VALIDAZIONE] **Fix lot size e parametri rischio:**
    - [in validazione 30/07/2025] Nuova generazione config: pip_value_map, spin_threshold, max_spread e trailing_stop sempre presenti e robusti. Size, SL e TP ora dovrebbero essere corretti e coerenti. Da monitorare live.

    - Se i test live confermano il comportamento corretto, spuntare anche:
        - [MEDIA] Validazione automatica della configurazione all’avvio
        - [MEDIA] Centralizzare magic number e fallback/configurazioni
        - [MEDIA] Possibilità di testare e confrontare tutti i tipi di trading in backtest_mono
        - [MEDIA] Togliere tutti i riferimenti a legacy e sostituire con mono

    - Se emergono nuovi edge case, aggiorna la checklist e procedi con fix mirati.

- [ ] **[ALTA]** controllare tutti i parametri che determinano l'estensione oraria della    strategia, ossia paragonare la dimensione del buffer e degli altri parametri che incidono sul periodo e confrontarli con i timeframe da m1 a h1

- [ ] **[ALTA]** controllare stop E TAKE PROFIT PERCHé SONO ANCORA STRETTI E TROPPO VICINI AL PREZZO D'INGRESSO

- [ ] **[ALTA]** controllare trailing stop

- [ ] **[ALTA]** avvicinarsi alla soglia soft del 2% del drawdown tra 1% e il 2%

- [ ] **[ALTA]** reintrodurre la possibilità di applicare il massimo numero di trade giornalieri al singolo simbolo o globali

> Questo file è la **roadmap e checklist ufficiale** del progetto Phoenix Quantum MonoFX.
> Contiene tutte le attività aperte, le priorità, le idee di miglioramento e le implementazioni pianificate.
> Aggiorna solo qui la lista delle cose da fare: tutti i file TODO secondari sono storici o di appoggio temporaneo.


## 1. Logging, Diagnostica e Trasparenza Segnali

- [x] **[ALTA] Logging tick-by-tick di ogni segnale (BUY/SELL/HOLD/SCARTATO)** con:
    - [x] **[ALTA] Simbolo, entropy, spin, confidence, timestamp, prezzo**
    - [x] **[ALTA] Esito e motivazione (apertura/scarto)** *(completato: ora ogni motivo di blocco è dettagliato e tracciato)*
- [x] **[ALTA] Dettaglio su filtri/blocchi** (buffer insufficiente, confidence bassa, cooldown, spread, orario, max trade, ecc.)
    - [done 30/07/2025] Tutti i motivi di blocco sono ora loggati, esportati e visualizzati in dashboard/diagnostica. Report e automazione completati.
- [x] **[MEDIA] Esportazione segnali e motivi di blocco in CSV/JSON per analisi esterna**
- [x] **[MEDIA] Aggiungere contatori per ogni tipo di blocco e report periodico sintetico nei log**
    - [done 30/07/2025] Ogni 100 segnali viene scritto nei log un riepilogo automatico dei motivi di blocco, con contatori thread-safe e reset.
- [x] **[MEDIA] Uniformare la struttura dei dati tra log, dashboard e funzioni di analisi**
    - [done 30/07/2025] Struttura dati ora coerente tra log, dashboard e funzioni di analisi. Tutti i motivi di blocco e i dettagli sono esportati e visualizzati in modo uniforme.

## 2. Dashboard: Visualizzazione, Aggregazione e UX
- [x] **[ALTA] Tabella cronologia/sequenza segnali con esito e motivazione** *(con refresh manuale e auto)*
- [ ] **[MEDIA] Statistiche e grafici aggregati** (ratio BUY/SELL, motivi di scarto, distribuzione segnali)
- [ ] **[MEDIA] Visualizzazione parametri attivi di filtro** (entropy, spin, confidence, cooldown, orari, spread, ecc.)
- [ ] **[MEDIA] Evidenziare parametri troppo restrittivi rispetto ai dati storici**
- [ ] **[MEDIA] Consentire modifica rapida dei parametri di filtro dalla dashboard**
- [ ] **[ALTA] Notifiche real-time** (es. disconnessione MT5, drawdown critico, target raggiunto)
- [ ] **[ALTA] Storico errori/warning** e miglioramento UI/UX (responsive, dark/light, icone)
+ [x] **[MEDIA] Esportazione dati e download CSV dalla dashboard**
+     - [done 30/07/2025] Implementato bottone, API Flask e logica JS per generazione e download CSV direttamente dalla dashboard.

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
- [x] **[MEDIA] Coordinare periodicità di aggiornamento/lettura tra log e dashboard** *(refresh segnali implementato)*
- [ ] **[MEDIA] Documentare chiaramente tutti i motivi di blocco e la loro logica**
- [ ] **[MEDIA] Aggiornare guida utente/dashboard con sezione debug segnali e best practice**

## 6. Nuove Implementazioni e Extra

- [ ] **[MEDIA] Possibilità di testare e confrontare tutti i tipi di trading in backtest_mono, segnalando la migliore configurazione**
- [ ] **[MEDIA] Togliere tutti i riferimenti a legacy e sostituire con mono**
- [ ] **[MEDIA] Configurazione avanzata:** selezione file config/log da interfaccia, modifica parametri da dashboard

---

> Aggiorna questa checklist man mano che completi le attività o identifichi nuove aree di intervento. Le priorità sono indicate tra parentesi quadre: **[ALTA]**, **[MEDIA]**, **[BASSA]**.
