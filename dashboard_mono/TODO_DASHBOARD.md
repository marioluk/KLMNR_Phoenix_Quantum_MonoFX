# ATTENZIONE: Questo file TODO è stato accorpato e centralizzato in `TODO.md` nella root del progetto.
# Consulta e aggiorna solo `TODO.md` per la roadmap completa, le priorità e lo stato delle attività.
# Qui sotto trovi lo storico delle attività completate e delle idee storiche specifiche della dashboard.

---

## Storico attività completate dashboard

- [x] Implementato buffer thread-safe per accumulo segnali generati (BUY, SELL, SCARTATO, HOLD) in QuantumEngine.
- [x] Aggiunto thread di report periodico ogni 5 minuti che stampa un riepilogo sintetico dei segnali generati (simbolo, tipo, motivo) in formato tabellare nei log.
- [x] Il report riduce il rumore nei log e migliora la leggibilità per la diagnosi.
- [x] Tutti i punti di generazione segnale (inclusi scarti per buffer insufficiente, confidence bassa, cooldown, ecc.) ora accumulano l'evento nel buffer per il report.
- [x] Il formato del report è compatto e facilmente leggibile.
- [x] Visualizzazione nella dashboard della sequenza segnali e relativo esito (tabella integrata in dashboard_broker.py e diagnostics.html).
- [x] Log dettagliato dei segnali: per ogni segnale, loggare simbolo, entropy, spin, timestamp, esito (aperta/scartata) e motivazione.
- [x] Tabella segnali nella dashboard: mostrare cronologia segnali con esito e motivazione.
- [x] Individuare e loggare nel codice di trading i punti in cui viene valutato/aperto/scartato un segnale.
- [x] Visualizzazione nella dashboard della sequenza segnali e relativo esito.
- [x] Aggiunta pagina di stato MT5: mostra connessione, account, server, saldo, equity, posizioni aperte.
- [x] Endpoint API per stato MT5: esposto `/api/mt5_status` con info connessione e account.

---

[TODO] Pagina Performance Analytics


**[TODO] Pagina Performance Analytics**

- Creare una pagina dedicata nella dashboard per l’analisi automatica dei report di trading:
    - Statistiche aggregate: profitto/perdita netta, win rate, drawdown, commissioni, swap, profitto medio per trade
    - Grafici interattivi: distribuzione per simbolo, orario, andamento equity
    - Report dettagliati e download (CSV, PDF)
    - Notifiche e alert automatici su anomalie o performance fuori target
    - Filtri avanzati per periodo, simbolo, tipo operazione
    - Integrazione con log e dati live

Obiettivo: rendere la dashboard uno strumento completo per monitoraggio, audit e tuning operativo.



## Idee storiche e dettagli temporanei

- Eventuale esportazione CSV/JSON dei report periodici per analisi esterna. _(rimandato, non prioritario al momento)_
- Migliorare UI/UX: layout responsive, colori chiari/scuri, icone intuitive.
- Documentazione API: aggiungere sezione con descrizione endpoint disponibili.
