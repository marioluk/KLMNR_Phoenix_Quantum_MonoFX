# [29/07/2025] Miglioramento logging segnali e report periodico

- [x] Implementato buffer thread-safe per accumulo segnali generati (BUY, SELL, SCARTATO, HOLD) in QuantumEngine.
- [x] Aggiunto thread di report periodico ogni 5 minuti che stampa un riepilogo sintetico dei segnali generati (simbolo, tipo, motivo) in formato tabellare nei log.
- [x] Il report riduce il rumore nei log e migliora la leggibilità per la diagnosi.
- [x] Tutti i punti di generazione segnale (inclusi scarti per buffer insufficiente, confidence bassa, cooldown, ecc.) ora accumulano l'evento nel buffer per il report.
- [x] Il formato del report è compatto e facilmente leggibile.

TODO PROSSIMI PASSI:
- [x] Visualizzazione nella dashboard della sequenza segnali e relativo esito (tabella integrata in dashboard_broker.py e diagnostics.html).
- [ ] Eventuale esportazione CSV/JSON dei report periodici per analisi esterna. _(rimandato, non prioritario al momento)_

# TODO Dashboard Phoenix Quantum MonoFX

## Analisi Segnali Trading & Apertura Posizioni (2025-07-29)

- [x] Log dettagliato dei segnali: per ogni segnale, loggare simbolo, entropy, spin, timestamp, esito (aperta/scartata) e motivazione.
- [x] Tabella segnali nella dashboard: mostrare cronologia segnali con esito e motivazione.
- [x] Individuare e loggare nel codice di trading i punti in cui viene valutato/aperto/scartato un segnale.
- [x] Visualizzazione nella dashboard della sequenza segnali e relativo esito.
# TODO Dashboard Phoenix Quantum MonoFX

Checklist miglioramenti e attività suggerite per la dashboard:

- [x] **Aggiungere pagina di stato MT5**
    - [x] Mostrare connessione, account, server, saldo, equity, posizioni aperte
- [x] **Endpoint API per stato MT5**
    - Esporre `/api/mt5_status` con info connessione e account
- [ ] **Notifiche real-time in dashboard**
    - Alert per disconnessione MT5, drawdown critico, target raggiunto
- [ ] **Storico errori e warning**
    - Visualizzare ultimi errori/warning rilevati nei log
- [ ] **Migliorare UI/UX**
    - Layout responsive, colori chiari/scuri, icone intuitive
- [ ] **Documentazione API**
    - Aggiungere sezione con descrizione endpoint disponibili
- [ ] **Refactoring codice**
    - Separare logica backend, API e frontend
- [ ] **Test automatici**
    - Aggiungere test per parsing log, API, calcolo metriche
- [ ] **Configurazione avanzata**
    - Permettere selezione file config/log da interfaccia
    - Visualizzazione e modifica parametri di configurazione dal file JSON tramite dashboard (UI dedicata)
- [ ] **Esportazione dati**
    - Download CSV di metriche, trade, segnali

> Aggiorna questa checklist man mano che completi le attività!
