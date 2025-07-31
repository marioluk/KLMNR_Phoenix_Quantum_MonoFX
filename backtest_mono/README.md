# Autonomous High Stakes Optimizer

Ottimizzatore autonomo per la generazione di configurazioni di trading ad alte prestazioni per Phoenix Quantum MonoFX.

## Funzionalità principali
- Generazione automatica di configurazioni per diverse tipologie di trading: scalping, intraday, swing, position.
- Validazione automatica dei parametri per coerenza con la tipologia di trading selezionata.
- Logging centralizzato di tutti i warning e errori di validazione nella cartella `logs`.
- Blocco della generazione della configurazione in caso di errori critici sui parametri.
- Riepilogo finale dei warning trovati, sia su console che su file.
- Parametri ottimizzati per ogni simbolo selezionato, con override e normalizzazione.
- Configurazioni pronte per l'utilizzo in ambiente di produzione MetaTrader5.

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
