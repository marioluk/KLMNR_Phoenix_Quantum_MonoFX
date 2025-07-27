# TODO - Migliorie e Refactoring Phoenix Quantum MonoFX

## Validazione e Gestione Configurazione
- [x] Implementare validazione automatica del file di configurazione all’avvio
- [x] Segnalare parametri mancanti, incoerenti o valori fuori range (log warning/error)
- [x] Centralizzare tutti i magic number (es. orari, spread, pips) usando solo valori dal file di configurazione
- [x] Aggiungere fallback o default per parametri opzionali
- [x] Controllare che tutti i simboli abbiano i campi richiesti (risk_management, trading_hours, ecc.)

## Stile, Best Practice e Robustezza
- [x] Aggiungere type hint a tutti i metodi pubblici e principali
- [x] Estrarre costanti hardcoded in alto al file o nella config
- [x] Migliorare la gestione delle eccezioni: evitare di "mangiare" errori critici, loggare sempre con contesto
- [x] Estrarre utility/metodi privati per evitare duplicazione di controlli (es. simboli, posizioni, limiti)
- [x] Spezzare i metodi molto lunghi in funzioni più piccole e testabili
- [x] Aggiungere test automatici/unitari per la business logic
- [x] Documentare meglio i parametri e i return nei docstring

## Logging e Debug
- [x] Uniformare i livelli di log e i messaggi (info, warning, error, critical, debug)
- [x] Migliorare i messaggi di log per i casi di edge-case o fallback

## Edge Case e Funzionalità
- [x] Implementare la funzione `get_daily_loss` (attualmente stub)
- [x] Verificare che la funzione `is_trading_hours` gestisca bene fusi orari e giorni festivi
- [x] Verificare che tutte le variabili condivise siano protette da lock/thread-safe

## Extra
- [x] Centralizzare la documentazione delle configurazioni e dei parametri accettati
- [x] Aggiornare la documentazione tecnica e README con le nuove best practice

---

> Aggiornare questa lista man mano che si implementano le migliorie o si identificano nuove aree di intervento.
