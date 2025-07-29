
# TODO Analisi Segnali Quantum - Diagnosi e Debug

## Obiettivo
Capire perché la strategia non genera segnali/trade, rendere trasparente il processo di filtro e facilitare la diagnosi dei blocchi.

---

## 1. Logging e Diagnostica
- [ ] Loggare ogni segnale bloccato con dettaglio del motivo (entropy, spin, confidence, orario, cooldown, spread, ecc.)
- [ ] Assicurarsi che i motivi di blocco siano estratti e salvati nella timeline dei segnali (sia nei log che nella dashboard)
- [ ] Aggiungere un contatore per ogni tipo di blocco (es. entropy, spin, orario, cooldown, spread, max trade, ecc.)
- [ ] Esportare la sequenza segnali e motivi di blocco in CSV/Excel per analisi offline
- [ ] Mostrare nella dashboard i motivi di blocco più frequenti (grafico/istogramma)

## 2. Parametri e Filtri
- [ ] Visualizzare nella dashboard i parametri attivi di filtro segnali (soglie entropy, spin, confidence, cooldown, orari, spread, ecc.)
- [ ] Consentire la modifica rapida dei parametri di filtro (anche solo temporaneamente) per testare l'impatto sulla generazione segnali
- [ ] Evidenziare nella dashboard se i parametri sono troppo restrittivi rispetto ai dati storici

## 3. Parsing e Aggregazione Dati
- [ ] Migliorare la funzione di parsing dei log per estrarre tutti i dettagli utili (motivo blocco, valori entropy/spin, parametri attivi al momento del segnale)
- [ ] Uniformare la struttura dei dati tra log, dashboard e funzioni di analisi (es. motivi di blocco sempre presenti e standardizzati)
- [ ] Validare che la timeline dei segnali in dashboard sia coerente con i log e con la logica di filtro

## 4. Analisi e Debug Strategia
- [ ] Aggiungere una funzione di "simulazione segnali" che mostra, per una finestra temporale, quanti segnali sarebbero passati con parametri meno restrittivi
- [ ] Implementare un report automatico che suggerisce quali filtri sono troppo stringenti (es. "entropy > 0.8 ha bloccato il 90% dei segnali")
- [ ] Consentire il replay di una giornata di log per vedere in tempo reale come agiscono i filtri

## 5. Documentazione e Supporto
- [ ] Documentare chiaramente tutti i motivi di blocco possibili e la loro logica
- [ ] Aggiornare la guida utente/dashboard con una sezione "debug segnali" e best practice per la diagnosi

---

## Note
- Queste attività coinvolgono: `phoenix_quantum_monofx_program.py`, `dashboard_broker.py`, `autonomous_challenge_optimizer.py`, file di configurazione e log.
- L'obiettivo è rendere trasparente e facilmente analizzabile il processo di generazione e blocco dei segnali, per poter agire in modo mirato sui parametri o sulla logica.
