## 🚨 PRIORITÀ: Debug Pipeline Segnali → Ordini

...

---
**[TODO] Integrazione Performance Analytics automatica**

- Integrare una funzione/modulo che analizzi automaticamente i report dei trade giornalieri e settimanali (esportati da MT5 o generati dal sistema), con:
    - Calcolo di profitto/perdita netta, win rate, drawdown, commissioni, swap, profitto medio per trade, distribuzione per simbolo e orario.
    - Riconoscimento pattern di errore (es. perdite consecutive, orari critici, simboli problematici).
    - Generazione di report grafici e testuali (es. CSV, HTML, PDF) per audit e ottimizzazione.
    - Notifiche automatiche in caso di anomalie o performance fuori target.
    - Integrazione con la dashboard e log centralizzati.


---
[MEDIA] **Implementare pagina Performance Analytics nella dashboard_mono**
    - Visualizzazione e analisi avanzata dei report trading direttamente dalla dashboard
    - Statistiche, grafici, download, alert e filtri avanzati
    - Vedi dettagli in TODO_DASHBOARD.md

Obiettivo: automatizzare il monitoraggio della strategia, facilitare l’analisi e il tuning dei parametri, migliorare la trasparenza e la reattività operativa.

...

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


[x] **Fix lot size e parametri rischio:**
    - [done 31/07/2025] Nuova generazione config: pip_value_map, spin_threshold, max_spread e trailing_stop sempre presenti e robusti. Size, SL e TP ora sono corretti e coerenti, validati anche live.

    - TODO:
        - [x] [MEDIA] Validazione automatica della configurazione all’avvio [done 31/07/2025]
        - [x] [MEDIA] Centralizzare magic number e fallback/configurazioni [done 31/07/2025]

    - Se emergono nuovi edge case, aggiorna la checklist e procedi con fix mirati.


- [x] **[ALTA]** Limite massimo di operazioni giornaliere max_daily_trades ora robusto e persistente [fix 31/07/2025]

- [x] **[ALTA]** il lot size è sempre a 0.1 controllare la funizone di calcolo tenendo in cosiderazione che la size deve essere dimensionata in base alla massima esposizione consentita e proporzionalmente nei vari simboli in modo tale che profitti e perdite dei singoli simboli siano simili

- [x] **[ALTA]** Controllare se funziona il COOLDOWN

- [x] **[ALTA]** comportamento anomalo su SP500 E NAS100 vanno in cooldown senza aver aperto posizioni di trading

- [ ] **[ALTA]** il livello di sl e tp degli indici è troppo stretto 

- [ ] **[ALTA]** controllare tutti i parametri che determinano l'estensione oraria della    strategia, ossia paragonare la dimensione del buffer e degli altri parametri che incidono sul periodo e confrontarli con i timeframe da m1 a h1

- [ ] **[ALTA]** controllare stop E TAKE PROFIT PERCHé SONO ANCORA STRETTI E TROPPO VICINI AL PREZZO D'INGRESSO

- [x] **[ALTA]** controllare trailing stop

- [ ] **[ALTA]** avvicinarsi alla soglia soft del 2% del drawdown tra 1% e il 2%

- [ ] **[ALTA]** reintrodurre la possibilità di applicare il massimo numero di trade giornalieri al singolo simbolo o globali

Giorni per ottimizzazione (default: 60):

revers signal, può avere senso con cooldawn?



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
- [ ] **[MEDIA]** Possibilità di testare e confrontare tutti i tipi di trading in backtest_mono
- [ ] **[MEDIA]** Togliere tutti i riferimenti a legacy e sostituire con mono

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



## DEBUG

- [x] Il cooldawn sembra non funzionare 
- [x] non scrive in backtest/logs. li produce al primo otimizaer del giorno, ogni giorno vengono cancellati
- [x] daily_trade_limit_mode non viene inserito nel file json

- [ ] Mi spieghi questi parametri che si vedono all'avvio nella shel ma non vengono riportati nei log?
🚀 ==> AVVIO QUANTUM TRADING SYSTEM <== 🚀
📋 Sistema con 4 simboli configurati
🎯 Simboli: {'EURUSD': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.007, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['08:00-12:00', '13:00-17:00', '18:00-20:00'], 'comment': 'Override generato dinamicamente per EURUSD - score 778.68', 'quantum_params_override': {}}, 'USDJPY': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.005, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['08:00-12:00', '13:00-17:00', '18:00-20:00'], 'comment': 'Override generato dinamicamente per USDJPY - score 687.99', 'quantum_params_override': {}}, 'USDCHF': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.007, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['09:00-11:00'], 'comment': 'Override generato dinamicamente per USDCHF - score 677.35', 'quantum_params_override': {}}, 'SP500': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.007, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['15:00-22:00', '13:00-14:30'], 'comment': 'Override generato dinamicamente per SP500 - score 705.14', 'quantum_params_override': {}}}
[2025-08-01 01:44:43,256] INFO: Avvio sistema con 4 simboli
✅ Componenti critici inizializzati correttamente
[2025-08-01 01:44:43,257] INFO: Sistema di trading avviato correttamente
