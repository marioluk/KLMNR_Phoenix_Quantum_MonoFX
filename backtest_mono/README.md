# ## [2025-08-01] Migliorie gestione drawdown
# - safe_limit, soft_limit e hard_limit sono ora sempre presenti nel file di configurazione generato.
# - Tutta la logica di gestione del rischio e protezione drawdown è ora completamente config-driven.
# - Verificato l’utilizzo corretto di tutti i limiti nel sistema di trading principale.
# Autonomous High Stakes Optimizer

Ottimizzatore autonomo per la generazione di configurazioni di trading ad alte prestazioni per Phoenix Quantum MonoFX.


## Parametri principali di configurazione

### max_position_hours
Durata massima di una posizione aperta (in ore). Limita il tempo di esposizione di ogni trade per ridurre il rischio di movimenti imprevisti.

### max_daily_trades
Numero massimo di trade che il sistema può aprire in una giornata. Utile per controllare la frequenza operativa e gestire il rischio di overtrading.

### position_cooldown
Tempo minimo (in secondi) tra la chiusura di una posizione e l’apertura della successiva. Previene aperture troppo ravvicinate.

### stop_loss_pips
Distanza dello Stop Loss dal prezzo di ingresso (in pips). Protegge il capitale da movimenti avversi e limita le perdite.

### take_profit_pips
Distanza del Take Profit dal prezzo di ingresso (in pips). Definisce l’obiettivo di profitto per il trade.

### buffer_size
Numero di tick/candele usati per analisi statistica e pattern recognition. Un buffer più grande consente analisi più approfondite.

### spin_window
Finestra (in tick/candele) per il calcolo dei segnali “spin” (direzionalità). Una finestra più ampia genera segnali più stabili.

### min_spin_samples
Numero minimo di campioni richiesti per calcolare uno spin affidabile. Evita segnali su dati insufficienti.

### signal_cooldown
Tempo minimo (in secondi) tra due segnali di ingresso. Riduce la frequenza di operatività e filtra il rumore di mercato.

### risk_percent
Percentuale del capitale rischiata per ogni trade. Determina la size della posizione e il rischio per operazione.

### max_concurrent_trades
Numero massimo di posizioni aperte contemporaneamente. Limita l’esposizione multipla su diversi strumenti.

### signal_threshold
Soglia di attivazione del segnale. Più alta = segnali più selettivi e meno frequenti.

### spin_threshold
Soglia di direzionalità per attivare il trade. Più alta = serve maggiore convinzione direzionale.

### volatility_filter
Filtro sulla volatilità del mercato. Opera solo se la volatilità è entro certi limiti, per evitare mercati troppo instabili.

### trend_strength
Filtro sulla forza del trend. Opera solo se il trend è sufficientemente forte, per evitare operatività in fasi laterali.

## Novità: Menu Interattivo e Automazione Giorni Ottimali

Lo script `autonomous_challenge_optimizer.py` ora include:

- **Menu interattivo** per la selezione della tipologia di trading (Scalping, Intraday, Swing, Position).
- Visualizzazione dei parametri principali per ogni tipologia prima della conferma.
- Possibilità di annullare la selezione e tornare al menu senza uscire dal programma.
- **Suggerimento automatico dei giorni ottimali** per il backtest in base alla tipologia scelta:
  - Scalping: 30 giorni
  - Intraday: 60 giorni
  - Swing: 120 giorni
  - Position: 180 giorni
- Conferma esplicita prima della generazione delle configurazioni.

Esempio di flusso:

1. Scegli la tipologia di trading dal menu.
2. Visualizza i parametri associati.
3. Conferma la selezione.
4. Inserisci (o accetta) il valore suggerito per i giorni di ottimizzazione.
5. Genera e salva le configurazioni.

## Struttura delle cartelle
- `backtest_mono/` : contiene lo script ottimizzatore e la logica di generazione.
- `config/` : output delle configurazioni generate.
- `logs/` : log di validazione e riepiloghi.
- `archive/`, `docs/`, `results/` : supporto e documentazione.

## Utilizzo
1. Avvia lo script `autonomous_challenge_optimizer.py`.
2. Seleziona la tipologia di trading e il livello di aggressività desiderato.
3. Le configurazioni vengono generate e salvate in `config/`, con log dettagliati in `logs/`.

## Parametri chiave validati
---
## Spiegazione parametro max_global_exposure

Il parametro `max_global_exposure` rappresenta l'esposizione massima consentita in USD su tutte le posizioni aperte contemporaneamente dal sistema.

Questa esposizione è il valore nozionale totale delle posizioni, cioè la somma del valore di mercato di tutti i trade aperti, calcolata come:

    esposizione = volume (lotti) × contract size × prezzo corrente

per ogni simbolo, sommando su tutti i simboli.

**Comprende la leva finanziaria:**
- Se hai $5.000 di capitale e una leva 1:100, puoi teoricamente aprire posizioni fino a $500.000 di valore nozionale.
- Il limite di $50.000 serve a mantenere il rischio sotto controllo, impedendo che il sistema esponga il conto a movimenti troppo ampi rispetto al capitale.

In pratica, il sistema non aprirà nuove posizioni se la somma del valore nozionale di tutte le posizioni aperte supera $50.000, anche se la leva consentirebbe di più.
Questo parametro è pensato per proteggere il capitale e limitare il rischio massimo, indipendentemente dalla leva disponibile.

Se vuoi un limite più conservativo, puoi ridurre questo valore (ad esempio a $25.000). Se vuoi sfruttare di più la leva, puoi aumentarlo, ma con maggiore rischio.
- `max_position_hours`, `max_daily_trades`, `buffer_size`, `spin_window`, `signal_cooldown`, ecc.
- Validazione sia globale che per ogni simbolo selezionato.

## Note
- Tutti i log di validazione sono centralizzati in `backtest_mono/logs`.
- In caso di parametri fuori range, la generazione viene bloccata e viene fornito un riepilogo dettagliato.

## Autore
- GitHub Copilot per KLMNR Phoenix Quantum MonoFX
