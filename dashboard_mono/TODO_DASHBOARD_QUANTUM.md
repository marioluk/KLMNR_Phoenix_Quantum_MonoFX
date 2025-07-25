# TODO Dashboard Quantistica - Roadmap Funzionalità

## Funzionalità essenziali per una dashboard di trading professionale

### 1. Monitoraggio in tempo reale
- Aggiornamento live di prezzi, equity, bilancio, P&L, drawdown, posizioni aperte
- Visualizzazione tick e dati di mercato per ogni simbolo

### 2. Gestione delle posizioni
- Elenco dettagliato delle posizioni aperte (simbolo, size, prezzo, P&L, orario apertura)
- Pulsanti per chiusura manuale, stop loss/take profit, modifica ordini

### 3. Storico operazioni
- Tabella con storico trade: data, simbolo, direzione, size, prezzo, P&L, motivo apertura/chiusura
- Filtri per periodo, simbolo, tipo operazione

### 4. Grafici avanzati
- Grafico equity/bilancio nel tempo
- Grafico drawdown (con evidenza livelli critici)
- Grafico P&L cumulativo
- Grafico performance per simbolo e per ora
- Visualizzazione segnali quantum (entropia/spin)

### 5. Metriche di performance
- Win rate, profit factor, numero trade, trade giornalieri, max drawdown, profitto totale
- Indicatori di rischio: rischio attuale, rischio massimo, rischio per simbolo

### 6. Stato compliance e obiettivi
- Visualizzazione stato challenge (target raggiunto, drawdown, limiti, warning)
- Badge/alert per superamento limiti o obiettivi

### 7. Gestione ordini e trading manuale
- Pulsanti per invio ordini buy/sell, gestione size, impostazione SL/TP
- Modalità trading manuale/automatico

### 8. Notifiche e alert
- Notifiche in tempo reale per eventi critici (drawdown, errore, trade eseguito, disconnessione MT5)
- Log eventi recenti

### 9. Configurazione e personalizzazione
- Selettore config, parametri di rischio, filtri simboli, personalizzazione layout

### 10. Sicurezza e accesso
- Login utente, gestione permessi, log attività

---

Queste sono le basi. Vuoi una roadmap di implementazione, oppure vuoi partire da una di queste funzionalità e vedere come integrarla nella dashboard?

---

## Roadmap di Implementazione (Step by Step)

### Fase 1: Core Live & Backend
- [x] API Flask per live status (prezzi, equity, bilancio, P&L, drawdown, posizioni)
- [x] API per storico operazioni (con filtri symbol, type, time)
- [x] API per metriche di performance
- [x] API per segnali quantum
- [x] API per gestione ordini manuali (buy/sell, modifica SL/TP, chiusura)

### Fase 2: Frontend Dashboard
- [x] Pagina principale con live status e tick per simbolo
- [x] Tabella posizioni aperte con azioni manuali
- [x] Tabella storico operazioni con filtri
 - [ ] Grafici avanzati (equity, drawdown, P&L, performance per simbolo/ora)
     - [x] Scegliere e installare la libreria grafica (es. Recharts, Chart.js)
     - [x] Definire le API/backend per fornire dati storici e aggregati
     - [x] Creare componente React per grafico equity/bilancio nel tempo
     - [x] Creare componente React per grafico drawdown (con limiti evidenziati)
     - [x] Creare componente React per grafico P&L cumulativo
     - [x] Creare componente React per performance per simbolo e per ora
     - [x] Integrare filtri (periodo, simbolo, tipo grafico)
     - [x] Ottimizzare la visualizzazione (responsive, UX, evidenza limiti)
- [x] Visualizzazione segnali quantum (entropia/spin)
- [x] Widget metriche di performance
- [x] Badge/alert compliance e obiettivi
- [x] Log eventi recenti e notifiche

### Fase 3: Configurazione & Sicurezza
- [ ] Selettore config e parametri di rischio
- [ ] Filtri simboli e personalizzazione layout
- [ ] Login utente e gestione permessi
- [ ] Log attività e sicurezza

### Fase 4: Ottimizzazione & UX
- [ ] Aggiornamento live via WebSocket (invece di polling)
- [ ] Modalità dark/light, responsive, mobile friendly
- [ ] Documentazione utente e guida rapida

---

**Priorità consigliata:**
1. Monitoraggio live e tabella posizioni
2. Storico operazioni e metriche
3. Grafici avanzati e segnali quantum
4. Gestione ordini manuali
5. Notifiche, configurazione, sicurezza

Ogni step può essere implementato e testato singolarmente. Vuoi partire dal primo step frontend (visualizzazione live status) o da una API specifica?
