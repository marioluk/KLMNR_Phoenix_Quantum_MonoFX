
# Guida Avvio Automatico Quantum

## Descrizione
Il sistema quantum può essere avviato automaticamente tramite Task Scheduler e script PowerShell/BAT.

## Setup Task Scheduler
1. Apri Task Scheduler su Windows
2. Crea task per avvio automatico:
   - `auto_start_daily_updater.bat` (daily alle 06:00)
   - `auto_start_legacy.bat` (boot server)
3. Verifica script PowerShell:
   - `AutoStartDailyUpdater.ps1`
   - `AutoStartLegacy.ps1`

## Esempio di configurazione
```sh
SCHTASKS /Create /SC DAILY /TN "KLMNR_Daily_Config_Updater" /TR "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\auto_start_daily_updater.bat" /ST 06:00
```

## Best practice
- Testare manualmente ogni script prima di automatizzare
- Monitorare i log di Task Scheduler

---
Vedi anche: [Guida Installazione](setup.md)
