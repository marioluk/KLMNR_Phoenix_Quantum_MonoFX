# Autonomous High Stakes Optimizer

Ottimizzatore autonomo per la generazione di configurazioni di trading ad alte prestazioni per Phoenix Quantum MonoFX.

## Funzionalità principali

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
- `max_position_hours`, `max_daily_trades`, `buffer_size`, `spin_window`, `signal_cooldown`, ecc.
- Validazione sia globale che per ogni simbolo selezionato.

## Note
- Tutti i log di validazione sono centralizzati in `backtest_mono/logs`.
- In caso di parametri fuori range, la generazione viene bloccata e viene fornito un riepilogo dettagliato.

## Autore
- GitHub Copilot per KLMNR Phoenix Quantum MonoFX
