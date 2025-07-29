# TODO Dashboard Phoenix Quantum MonoFX

## Analisi Segnali Trading & Apertura Posizioni (2025-07-29)

- [ ] Log dettagliato dei segnali: per ogni segnale, loggare simbolo, entropy, spin, timestamp, esito (aperta/scartata) e motivazione.
- [ ] Tabella segnali nella dashboard: mostrare cronologia segnali con esito e motivazione.
- [ ] Individuare e loggare nel codice di trading i punti in cui viene valutato/aperto/scartato un segnale.
- [ ] Visualizzazione nella dashboard della sequenza segnali e relativo esito.
# TODO Dashboard Phoenix Quantum MonoFX

Checklist miglioramenti e attività suggerite per la dashboard:

- [x] **Aggiungere pagina di stato MT5**
    - [x] Mostrare connessione, account, server, saldo, equity, posizioni aperte
- [ ] **Endpoint API per stato MT5**
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
- [ ] **Esportazione dati**
    - Download CSV di metriche, trade, segnali

> Aggiorna questa checklist man mano che completi le attività!
