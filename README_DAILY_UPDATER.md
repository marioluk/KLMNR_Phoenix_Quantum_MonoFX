# DAILY CONFIG UPDATER - Sistema di Aggiornamento Automatico

Sistema automatizzato per l'aggiornamento giornaliero delle configurazioni di trading attraverso l'ottimizzazione autonoma e la conversione al formato di produzione.

## 🎯 Strategia Nome File

Il sistema utilizza una strategia intelligente per mantenere la compatibilità con il codice legacy:

- **File Generato**: `config_autonomous_high_stakes_conservative_production_ready.json`
- **Posizione**: `config/` (directory principale)
- **Compatibilità**: Funziona direttamente con `legacy_system/PRO-THE5ERS-QM-PHOENIX-GITCOP.py`
- **No Modifiche**: Il sistema legacy non richiede cambiamenti al path di configurazione

### Vantaggi
- ✅ Compatibilità diretta con sistema legacy
- ✅ Automazione trasparente 
- ✅ Nessuna modifica richiesta ai riferimenti esistenti
- ✅ Configurazione sempre aggiornata e ottimale

## 🔄 Processo Automatico

### 1. Backup e Sicurezza
- Backup automatico configurazioni esistenti
- Retention period di 30 giorni (configurabile)
- Pulizia automatica backup obsoleti

### 2. Ottimizzazione
- Esecuzione autonomous high stakes optimizer
- Analisi ultimi 30 giorni di dati
- Selezione automatica configurazione migliore (Auto-Best)

### 3. Conversione e Deploy
- Conversione formato produzione
- Salvataggio diretto con nome standard (senza [BEST])
- Validazione completa configurazione finale

### 4. Monitoring
- Logging dettagliato di tutte le operazioni
- Report finale con statistiche
- Gestione errori robusta

## 📋 Configurazione Cronjob

### Windows Task Scheduler

1. **Apri Task Scheduler**
   ```
   taskschd.msc
   ```

2. **Crea Attività Base**
   - Nome: `Daily Config Updater`
   - Descrizione: `Aggiornamento giornaliero configurazioni trading`

3. **Trigger**
   - Tipo: `Daily`
   - Ora: `06:00`
   - Ricorrenza: `Every day`

4. **Azione**
   - Programma: `cmd.exe`
   - Argomenti: `/c "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\daily_config_updater.bat" auto`
   - Inizia in: `C:\KLMNR_Projects\KLMNR_Phoenix_Quantum`

5. **Condizioni**
   - ✅ Avvia solo se il computer è collegato alla rete elettrica
   - ✅ Avvia solo se disponibile connessione di rete
   - ❌ Riattiva il computer per eseguire l'attività

6. **Impostazioni**
   - ✅ Consenti esecuzione dell'attività su richiesta
   - ✅ Esegui l'attività appena possibile dopo l'inizio programmato non eseguito
   - ❌ Arresta l'attività se è in esecuzione per più di: 1 ora

### Linux Crontab

```bash
# Modifica crontab
crontab -e

# Aggiungi riga per esecuzione alle 06:00 ogni giorno
0 6 * * * cd /path/to/KLMNR_Phoenix_Quantum && python3 daily_config_updater.py --log-level INFO >> logs/daily_updater/cron.log 2>&1
```

## 🚀 Esecuzione Manuale

### Windows
```bash
# Directory del progetto
cd C:\KLMNR_Projects\KLMNR_Phoenix_Quantum

# Esecuzione diretta
python daily_config_updater.py

# Con parametri specifici
python daily_config_updater.py --workspace . --retention-days 30 --log-level INFO

# Tramite batch
daily_config_updater.bat
```

### Linux/macOS
```bash
# Directory del progetto
cd /path/to/KLMNR_Phoenix_Quantum

# Esecuzione diretta
python3 daily_config_updater.py

# Con parametri specifici
python3 daily_config_updater.py --workspace . --retention-days 30 --log-level INFO
```

## 📊 Monitoring e Log

### Directory Log
```
logs/daily_updater/
├── daily_updater_20250720_060001.log  # Log Python dettagliato
├── daily_updater_batch_20250720_060001.log  # Log batch Windows
└── cron.log  # Log crontab Linux
```

### Contenuto Log Tipico
```
2025-07-20 06:00:01 | INFO     | DailyConfigUpdater | 🚀 DailyConfigUpdater inizializzato
2025-07-20 06:00:01 | INFO     | DailyConfigUpdater | 📁 Workspace: C:\KLMNR_Projects\KLMNR_Phoenix_Quantum
2025-07-20 06:00:01 | INFO     | DailyConfigUpdater | 🎯 Target config: config\config_autonomous_high_stakes_conservative_production_ready.json
2025-07-20 06:00:02 | INFO     | DailyConfigUpdater | 🔍 Validazione ambiente...
2025-07-20 06:00:02 | INFO     | DailyConfigUpdater | ✅ Ambiente validato
2025-07-20 06:00:03 | INFO     | DailyConfigUpdater | 💾 Backup configurazioni esistenti...
2025-07-20 06:00:03 | INFO     | DailyConfigUpdater | ✅ Backup creato: config_autonomous_high_stakes_conservative_production_ready.json.backup_20250720_060003
2025-07-20 06:00:04 | INFO     | DailyConfigUpdater | 🤖 Esecuzione autonomous high stakes optimizer...
2025-07-20 06:00:15 | INFO     | DailyConfigUpdater | ✅ Autonomous optimizer completato
2025-07-20 06:00:16 | INFO     | DailyConfigUpdater | 🔍 Ricerca file BEST...
2025-07-20 06:00:16 | INFO     | DailyConfigUpdater | ✅ File BEST trovato: config_autonomous_high_stakes_conservative[BEST]_20250720.json
2025-07-20 06:00:17 | INFO     | DailyConfigUpdater | 🔄 Conversione e salvataggio configurazione standard...
2025-07-20 06:00:19 | INFO     | DailyConfigUpdater | ✅ Configurazione salvata come: config_autonomous_high_stakes_conservative_production_ready.json
2025-07-20 06:00:19 | INFO     | DailyConfigUpdater | 🧹 File BEST temporaneo rimosso: config_autonomous_high_stakes_conservative[BEST]_20250720.json
2025-07-20 06:00:20 | INFO     | DailyConfigUpdater | ✅ Configurazione validata: 3 simboli
2025-07-20 06:00:20 | INFO     | DailyConfigUpdater | ✅ AGGIORNAMENTO GIORNALIERO COMPLETATO CON SUCCESSO
```

## 🔍 Troubleshooting

### Problemi Comuni

#### 1. Script Non Trovato
**Errore**: `Script Python non trovato`
**Soluzione**: 
```bash
# Verifica esistenza file
ls daily_config_updater.py

# Se mancante, verifica directory corrente
pwd
```

#### 2. Errore Autonomous Optimizer
**Errore**: `Optimizer fallito con codice: 1`
**Soluzione**: 
```bash
# Test manuale optimizer
python tools/autonomous_high_stakes_optimizer.py --days 30 --auto-best

# Controlla log per dettagli specifici
```

#### 3. Errore Conversione
**Errore**: `Conversione fallita`
**Soluzione**:
```bash
# Verifica converter
python tools/production_config_converter.py --help

# Test manuale conversione
python tools/production_config_converter.py config/test.json --output config/test_output.json
```

#### 4. Permessi File
**Errore**: `Permission denied`
**Soluzione**:
```bash
# Windows - Esegui come Administrator
# Linux - Verifica permessi
chmod +x daily_config_updater.py
```

### Debug Avanzato

#### Esecuzione Debug
```bash
# Livello debug massimo
python daily_config_updater.py --log-level DEBUG

# Output verboso
python daily_config_updater.py --log-level DEBUG 2>&1 | tee debug.log
```

#### Controllo Ambiente
```bash
# Verifica Python
python --version

# Verifica dipendenze
pip list | grep -E "(pandas|numpy|json)"

# Verifica struttura directory
tree . -d -L 2
```

## 📈 Performance e Ottimizzazione

### Metriche Monitorate
- **Tempo Esecuzione**: ~20-60 secondi tipico
- **Dimensione Config**: ~50-200KB tipico
- **Simboli Configurati**: 1-10 simboli tipico
- **Win Rate**: Monitorato se disponibile in metadata

### Parametri Configurabili
```bash
# Retention backup personalizzato
python daily_config_updater.py --retention-days 60

# Workspace personalizzato
python daily_config_updater.py --workspace /custom/path

# Log level personalizzato
python daily_config_updater.py --log-level WARNING
```

## 🔐 Sicurezza e Best Practices

### Backup
- ✅ Backup automatico prima di ogni aggiornamento
- ✅ Retention period configurabile
- ✅ Backup comprende tutte le configurazioni importanti
- ✅ Ripristino manuale sempre possibile

### Validazione
- ✅ Validazione ambiente prima dell'esecuzione
- ✅ Controllo integrità file di configurazione
- ✅ Validazione JSON strutturale
- ✅ Controllo sezioni obbligatorie

### Monitoring
- ✅ Log dettagliati di tutte le operazioni
- ✅ Report finale con statistiche
- ✅ Exit code appropriati per monitoring esterno
- ✅ Timeout per evitare hang del processo

## 📞 Supporto

Per problemi o domande:
1. Controlla i log in `logs/daily_updater/`
2. Esegui test manuale con `--log-level DEBUG`
3. Verifica configurazione cronjob/Task Scheduler
4. Consulta sezione Troubleshooting

---
**Sistema KLMNR Phoenix Quantum Trading**  
**Versione**: 2.0  
**Data**: 20 Luglio 2025
