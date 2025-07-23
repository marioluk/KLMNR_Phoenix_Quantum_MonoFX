# Pulizia automatica sistema legacy

Questo documento descrive lo script `cleanup_production.bat` per la pulizia del sistema legacy.

## Funzionalità
- Rimuove file di test (`test_*.py`), file temporanei, cache Python (`__pycache__`), TODO obsoleti, log di debug e backup di configurazione non più necessari.
- Mantiene solo i file essenziali per la produzione:
  - `phoenix_quantum_monofx_program.py` (sistema principale)
  - `config/*.json` (configurazioni attive)
  - `config/backups` (ultimi 5 backup)
  - `daily_config_updater.py` (automazione)
  - `*.md` (documentazione)
  - `start_legacy.*` (script di avvio)
  - `logs/*.log` (log principali)

## Esecuzione

Apri un prompt dei comandi nella cartella `legacy_system` ed esegui:
```
cleanup_production.bat
```

Al termine, il sistema sarà pronto per la produzione.
