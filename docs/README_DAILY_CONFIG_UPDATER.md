# DAILY CONFIG UPDATER - AUTO START SYSTEM

## 📋 PANORAMICA
Sistema automatizzato per l'aggiornamento giornaliero delle configurazioni di trading alle **06:00**.

Il Daily Config Updater:
- 🎯 Genera la configurazione ottimale analizzando 30 giorni di dati
- 🔄 Converte automaticamente in formato produzione
- 📁 Fa backup delle configurazioni precedenti  
- 🧹 Pulisce file temporanei e backup obsoleti
- ✅ Pronto per integrazione con sistema legacy

---

## 🚀 INSTALLAZIONE RAPIDA

### 1️⃣ Test del Sistema (OPZIONALE)
```powershell
cd c:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system
.\auto_start_daily_updater.bat
```

### 2️⃣ Installazione Task Scheduler (RICHIESTO)
**⚠️ ESEGUIRE COME AMMINISTRATORE**

```powershell
# Apri PowerShell come AMMINISTRATORE (tasto destro -> "Esegui come amministratore")
cd c:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system
.\setup_auto_start_daily_updater.bat
```

### 3️⃣ Gestione Task (OPZIONALE)
```powershell
# Gestione completa del task
.\manage_daily_updater_task.bat
```

---

## ⚙️ CONFIGURAZIONE TASK SCHEDULER

Il task viene configurato automaticamente con:

| Parametro | Valore |
|-----------|---------|
| **Nome Task** | `KLMNR_Daily_Config_Updater` |
| **Orario** | `06:00` ogni giorno |
| **Privilegi** | `Amministratore` |
| **Retry** | `3 tentativi` con 5 min di pausa |
| **Network** | Richiede connessione internet |
| **Timeout** | `1 ora` massimo |

---

## 📁 FILE CREATI

### Script Principali
- `AutoStartDailyUpdater.ps1` - Script PowerShell avanzato
- `auto_start_daily_updater.bat` - Wrapper BAT per compatibilità
- `setup_auto_start_daily_updater.bat` - Installazione automatica
- `manage_daily_updater_task.bat` - Gestione task

### Configurazione
- `KLMNR_Daily_Config_Updater.xml` - Template Task Scheduler

### Log
- `logs\auto_start_daily_updater_YYYYMMDD.log` - Log giornalieri auto-start

---

## 📊 MONITORAGGIO

### Verifica Stato Task
```powershell
# Metodo 1: Script di gestione
.\manage_daily_updater_task.bat

# Metodo 2: Comando diretto
schtasks /query /tn "KLMNR_Daily_Config_Updater" /fo LIST
```

### Controllo Log
```powershell
# Log più recente
Get-Content logs\auto_start_daily_updater_*.log | Select-Object -Last 20

# Tutti i log
dir logs\auto_start_daily_updater_*.log
```

---

## ✅ VERIFICA FUNZIONAMENTO

### Test Manuale (Immediate)
```powershell
# Avvia task manualmente
schtasks /run /tn "KLMNR_Daily_Config_Updater"

# Controlla log
Get-Content logs\auto_start_daily_updater_$(Get-Date -Format 'yyyyMMdd').log
```

### Verifica Automatica (Domani mattina)
Il task si avvierà automaticamente alle **06:00**.

Controlla:
1. **Log auto-start**: `logs\auto_start_daily_updater_*.log`
2. **Log daily updater**: `logs\daily_config_updater_*.log`  
3. **Nuove configurazioni**: `config\*_production_ready.json`

---

## 🔧 GESTIONE TASK

### Comandi Utili
```powershell
# Abilitare task
schtasks /change /tn "KLMNR_Daily_Config_Updater" /enable

# Disabilitare task
schtasks /change /tn "KLMNR_Daily_Config_Updater" /disable

# Rimuovere task
schtasks /delete /tn "KLMNR_Daily_Config_Updater" /f

# Modificare orario (via GUI)
taskschd.msc
```

### Script di Gestione
```powershell
# Menu interattivo completo
.\manage_daily_updater_task.bat
```

---

## 🔄 INTEGRAZIONE CON SISTEMA LEGACY

Il Daily Config Updater genera:

### File di Output
- `config_autonomous_high_stakes_conservative_production_ready.json` - **Config produzione**

### Backup Automatici  
- `config\backups\YYYYMMDD_HHMMSS\` - Backup configurazioni precedenti

### Compatibilità
- ✅ Stesso formato del sistema legacy esistente
- ✅ Stesso path CONFIG_FILE utilizzato
- ✅ Conversione automatica da formato autonomo a produzione

---

## 📈 BENEFICI

### ⏰ Automazione Completa
- Nessun intervento manuale richiesto
- Aggiornamento quotidiano alle 06:00
- Configurazioni sempre ottimizzate

### 🛡️ Sicurezza
- Backup automatico configurazioni precedenti
- Validazione file generati
- Log dettagliati per troubleshooting

### 🔧 Robustezza
- Retry automatico su errore (max 3 tentativi)
- Verifica connettività internet
- Gestione errori e timeout

### 📊 Monitoring
- Log dettagliati di ogni esecuzione
- Script di gestione e monitoraggio
- Integrazione con Task Scheduler di Windows

---

## ❗ NOTE IMPORTANTI

### Prerequisiti
- ✅ Sistema legacy funzionante
- ✅ Python configurato con tutti i moduli
- ✅ Connessione internet stabile
- ✅ Privilegi amministratore per installazione

### Configurazione Git
Il `.gitignore` è già configurato per escludere:
- `logs\auto_start_daily_updater_*.log`
- File di backup automatici
- Configurazioni temporanee

### Manutenzione
- I backup vengono automaticamente puliti dopo 7 giorni
- I log possono essere puliti manualmente via script gestione
- Il task può essere temporaneamente disabilitato senza rimuoverlo

---

## 🆘 TROUBLESHOOTING

### Problema: Task non si avvia
**Soluzione**: Verifica privilegi amministratore
```powershell
schtasks /query /tn "KLMNR_Daily_Config_Updater" /v
```

### Problema: Errori Python
**Soluzione**: Testa ambiente manualmente
```powershell
cd backtest_mono
python daily_config_updater.py --days 30
```

### Problema: Configurazioni non generate
**Soluzione**: Controlla log daily config updater
```powershell
Get-Content logs\daily_config_updater_*.log | Select-Object -Last 50
```

### Problema: Connettività
**Soluzione**: Il sistema verifica automaticamente e logga warnings

---

## 📞 SUPPORT

Per assistenza:
1. Controlla sempre prima i **log**
2. Usa `manage_daily_updater_task.bat` per diagnostica
3. Testa manualmente il `daily_config_updater.py`
4. Verifica Task Scheduler con `taskschd.msc`

---

**✅ SISTEMA PRONTO PER PRODUZIONE**

Il Daily Config Updater è ora completamente configurato e pronto per automatizzare l'aggiornamento giornaliero delle configurazioni di trading alle **06:00**.

**Prossimo step**: Eseguire `setup_auto_start_daily_updater.bat` come **amministratore** per completare l'installazione.
