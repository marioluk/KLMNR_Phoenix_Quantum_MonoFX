# Refactoring Phoenix Quantum MonoFX

## ✅ Cose già fatte

- [x] Spostate tutte le classi core (`QuantumEngine`, `ConfigManager`, `DailyDrawdownTracker`, `QuantumRiskManager`) in file dedicati.
- [x] Centralizzate tutte le funzioni di utility e logging (`log_signal_tick`, `log_signal_tick_with_reason`, ecc.) in `utils.py`.
- [x] Aggiornati gli import nel file principale per usare solo le versioni centralizzate delle utility.
- [x] Rimosso codice duplicato e legacy relativo a logging e utility dal file principale.
- [x] Verificato che il file principale non abbia errori di compilazione.


## 🟡 Da fare (prossimi step)

- [x] Rimosso tutte le funzioni stub temporanee e placeholder dal file principale (`phoenix_quantum_monofx_program.py`).
- [x] Eliminati/commentati i commenti legacy e i print/debug inutili.
- [x] Puliti gli import non più necessari (es. `import csv`, `import os` se non usati direttamente).
- [x] Verificare che tutte le chiamate a utility e logging puntino a `utils.py`.
- [x] Spostare eventuali costanti globali in un file dedicato (`constants.py`).
- [x] Separare la logica di avvio (main, thread, setup) in un modulo dedicato (es. `runner.py`).
- [x] Creare la cartella `core/` per le classi principali.
- [x] Spostare la classe `QuantumEngine` in `core/quantum_engine.py` ✅
- [x] Spostare la classe `ConfigManager` in `core/config_manager.py` ✅
- [x] Spostare la classe `DailyDrawdownTracker` in `core/daily_drawdown_tracker.py` ✅
- [x] Spostare la classe `QuantumRiskManager` in `core/quantum_risk_manager.py` ✅
- [x] Aggiornare tutti gli import per riflettere la nuova struttura. ✅
 - [x] Spostare `utils.py` in una cartella dedicata (`core/` o `utils/`).
 - [x] Spostare `constants.py` in una cartella dedicata (`core/` o `utils/`).
 - [x] Aggiornare tutti gli import relativi a `utils` e `constants`.
- [ ] Eseguire test di integrazione per verificare che tutto funzioni dopo il refactoring.
- [ ] (Opzionale) Aggiungere test automatici per le utility e le classi core.

---

> Aggiorna questa lista man mano che completi i task. Segui l'ordine suggerito per un refactoring ordinato e sicuro.
