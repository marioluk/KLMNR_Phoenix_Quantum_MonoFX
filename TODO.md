# ROADMAP Phoenix Quantum MonoFX


---
**Legenda Priorità:**
- [ALTA] = Critico/da fare subito
- [MEDIA] = Importante/da pianificare
- [BASSA] = Miglioria/fine tuning
---

---

## 1. BACKEND (Trading System, Logica, Risk, Config, Robustezza)

### Debug Pipeline Segnali → Ordini
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

### Fix lot size e parametri rischio
[x] **Fix lot size e parametri rischio:**
    - [done 31/07/2025] Nuova generazione config: pip_value_map, spin_threshold, max_spread e trailing_stop sempre presenti e robusti. Size, SL e TP ora sono corretti e coerenti, validati anche live.
    - TODO:
        - [x] [MEDIA] Validazione automatica della configurazione all’avvio [done 31/07/2025]
        - [x] [MEDIA] Centralizzare magic number e fallback/configurazioni [done 31/07/2025]
    - Se emergono nuovi edge case, aggiorna la checklist e procedi con fix mirati.

### Altre attività backend
 [~] **[ALTA]** il livello di sl e tp degli indici è troppo stretto *(IN TEST: valori aumentati, validazione rispetto a volatilità e timeframe già effettuata; monitorare su posizioni reali SP500/NAS100)*
- [x] **[ALTA]** controllare stop E TAKE PROFIT PERCHé SONO ANCORA STRETTI E TROPPO VICINI AL PREZZO D'INGRESSO
- [x] **[ALTA]** controllare tutti i parametri che determinano l'estensione oraria della strategia, ossia paragonare la dimensione del buffer e degli altri parametri che incidono sul periodo e confrontarli con i timeframe da m1 a h1
- [x] **[ALTA]** controllare trailing stop
- [x] **[ALTA]** avvicinarsi alla soglia soft del 2% del drawdown tra 1% e il 2% - acceleratore/freno
- [x] **[ALTA]** reintrodurre la possibilità di applicare il massimo numero di trade giornalieri al singolo simbolo o globali
    - [x - done 01/08/2025] Funzionalità consolidata: daily_trade_limit_mode ora sempre presente in config, logica aggiornata e log diagnostici per blocco sia globale che per simbolo.

---

## 2. FRONTEND / DASHBOARD

### Performance Analytics e Dashboard
**[TODO] Integrazione Performance Analytics automatica**
- Integrare una funzione/modulo che analizzi automaticamente i report dei trade giornalieri e settimanali (esportati da MT5 o generati dal sistema), con:
    - Calcolo di profitto/perdita netta, win rate, drawdown, commissioni, swap, profitto medio per trade, distribuzione per simbolo e orario.
    - Riconoscimento pattern di errore (es. perdite consecutive, orari critici, simboli problematici).
    - Generazione di report grafici e testuali (es. CSV, HTML, PDF) per audit e ottimizzazione.
    - Notifiche automatiche in caso di anomalie o performance fuori target.
    - Integrazione con la dashboard e log centralizzati.

[MEDIA] **Implementare pagina Performance Analytics nella dashboard_mono**
    - Visualizzazione e analisi avanzata dei report trading direttamente dalla dashboard
    - Statistiche, grafici, download, alert e filtri avanzati
    - Vedi dettagli in TODO_DASHBOARD.md

Obiettivo: automatizzare il monitoraggio della strategia, facilitare l’analisi e il tuning dei parametri, migliorare la trasparenza e la reattività operativa.

### Dashboard: Visualizzazione, Aggregazione e UX
- [x] **[ALTA] Tabella cronologia/sequenza segnali con esito e motivazione** *(con refresh manuale e auto)*
- [ ] **[MEDIA] Statistiche e grafici aggregati** (ratio BUY/SELL, motivi di scarto, distribuzione segnali)
- [ ] **[MEDIA] Visualizzazione parametri attivi di filtro** (entropy, spin, confidence, cooldown, orari, spread, ecc.)
- [ ] **[MEDIA] Evidenziare parametri troppo restrittivi rispetto ai dati storici**
- [ ] **[MEDIA] Consentire modifica rapida dei parametri di filtro dalla dashboard**
- [x] **[ALTA] Notifiche real-time** (es. disconnessione MT5, drawdown critico, target raggiunto)
- [X] **[ALTA] Storico errori/warning** 
- [ ] **[ALTA] miglioramento UI/UX (responsive, dark/light, icone)**
+ [x] **[MEDIA] Esportazione dati e download CSV dalla dashboard**
+     - [done 30/07/2025] Implementato bottone, API Flask e logica JS per generazione e download CSV direttamente dalla dashboard.
- [X] **[MEDIA]** Togliere tutti i riferimenti a legacy e sostituire con mono
- [ ] **[MEDIA]** Consentire test e confronto di tutti i tipi di trading dalla dashboard
- [ ] **[MEDIA]** Configurazione avanzata: selezione file config/log da interfaccia, modifica parametri da dashboard
- [ ] **[MEDIA] Definire formato dati condiviso (JSON, CSV, DB) tra codice e dashboard**
- [x] **[MEDIA] Coordinare periodicità di aggiornamento/lettura tra log e dashboard** *(refresh segnali implementato)*
- [ ] **[MEDIA] Documentare chiaramente tutti i motivi di blocco e la loro logica**
- [ ] **[MEDIA] Aggiornare guida utente/dashboard con sezione debug segnali e best practice**

---

## 3. BACKTEST & ANALISI

- [ ] **[MEDIA] Possibilità di testare e confrontare tutti i tipi di trading in backtest_mono, segnalando la migliore configurazione**
- [ ] **[MEDIA] Migliorare parsing log per estrarre dettagli utili** (motivo blocco, valori entropy/spin, parametri attivi)
- [ ] **[MEDIA] Validare coerenza timeline segnali tra dashboard, log e logica di filtro**
- [ ] **[MEDIA] Simulazione segnali:** mostrare quanti sarebbero passati con parametri meno restrittivi
- [ ] **[MEDIA] Report automatico su filtri troppo stringenti** (es. “entropy > 0.8 ha bloccato il 90% dei segnali”)
- [ ] **[BASSA] Replay di una giornata di log** per vedere in tempo reale l’effetto dei filtri
- [ ] **[MEDIA] Refactoring codice:** separare logica backend, API e frontend
- [ ] **[MEDIA] Edge case:** gestione fusi orari, giorni festivi, variabili thread-safe
- [ ] **[MEDIA] Test automatici/unitari per business logic, parsing log, API, metriche**
- [ ] **[MEDIA] Validazione automatica della configurazione all’avvio**
- [ ] **[MEDIA] Centralizzare magic number e fallback/configurazioni**
- [ ] **[MEDIA] Type hint, docstring, gestione eccezioni, metodi privati per evitare duplicazioni**

---

## DEBUG GIORNALIERO

- [x] Il cooldawn sembra non funzionare 
- [x] non scrive in backtest/logs. li produce al primo otimizaer del giorno, ogni giorno vengono cancellati
- [x] daily_trade_limit_mode non viene inserito nel file json
- [x] Mi spieghi questi parametri che si vedono all'avvio nella shel ma non vengono riportati nei log?
🚀 ==> AVVIO QUANTUM TRADING SYSTEM <== 🚀
📋 Sistema con 4 simboli configurati
🎯 Simboli: {'EURUSD': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.007, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['08:00-12:00', '13:00-17:00', '18:00-20:00'], 'comment': 'Override generato dinamicamente per EURUSD - score 778.68', 'quantum_params_override': {}}, 'USDJPY': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.005, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['08:00-12:00', '13:00-17:00', '18:00-20:00'], 'comment': 'Override generato dinamicamente per USDJPY - score 687.99', 'quantum_params_override': {}}, 'USDCHF': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.007, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['09:00-11:00'], 'comment': 'Override generato dinamicamente per USDCHF - score 677.35', 'quantum_params_override': {}}, 'SP500': {'risk_management': {'contract_size': 0.01, 'profit_multiplier': 2.2, 'risk_percent': 0.007, 'trailing_stop': {'activation_pips': 24, 'step_pips': 12}, 'target_pip_value': 10.0, 'max_global_exposure': 50000.0}, 'timezone': 'Europe/Rome', 'trading_hours': ['15:00-22:00', '13:00-14:30'], 'comment': 'Override generato dinamicamente per SP500 - score 705.14', 'quantum_params_override': {}}}
[2025-08-01 01:44:43,256] INFO: Avvio sistema con 4 simboli
✅ Componenti critici inizializzati correttamente
[2025-08-01 01:44:43,257] INFO: Sistema di trading avviato correttamente

---

## 4. DOCUMENTAZIONE & BEST PRACTICE

- [ ] Aggiornare guida utente e README con esempi di configurazione e avvio
- [ ] Documentare chiaramente tutti i motivi di blocco e la loro logica
- [ ] Aggiornare la sezione debug segnali e best practice operative
- [ ] Mantenere changelog e roadmap sempre aggiornati
- [ ] Documentare API e struttura dati condivisa tra backend e dashboard
