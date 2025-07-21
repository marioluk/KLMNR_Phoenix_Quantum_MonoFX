@echo off
REM =================================================================
REM SETUP AUTO START - Configurazione avvio automatico sistema legacy
REM Per Windows 10 Pro con Task Scheduler
REM =================================================================

echo.
echo 🔧 SETUP AVVIO AUTOMATICO SISTEMA LEGACY
echo =================================================================
echo.

REM Verifica privilegi amministratore
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRORE: Questo script richiede privilegi di amministratore!
    echo    Clicca tasto destro e "Esegui come amministratore"
    pause
    exit /b 1
)

echo ✅ Privilegi amministratore verificati
echo.

REM Verifica che siamo nella directory corretta
if not exist "AutoStartLegacy.ps1" (
    echo ❌ ERRORE: File AutoStartLegacy.ps1 non trovato!
    echo    Assicurati di essere nella cartella legacy_system/
    pause
    exit /b 1
)

if not exist "KLMNR_Legacy_AutoStart.xml" (
    echo ❌ ERRORE: File task XML non trovato!
    pause
    exit /b 1
)

echo ✅ File di configurazione trovati
echo.

REM Crea cartella logs se non esiste
if not exist "logs" mkdir logs

echo 📋 Configurazione Task Scheduler...

REM Rimuovi task esistente se presente
schtasks /query /tn "KLMNR_Legacy_AutoStart" >nul 2>&1
if %errorLevel% equ 0 (
    echo    Rimozione task esistente...
    schtasks /delete /tn "KLMNR_Legacy_AutoStart" /f >nul
)

REM Importa il nuovo task
echo    Importazione nuovo task...
schtasks /create /xml "KLMNR_Legacy_AutoStart.xml" /tn "KLMNR_Legacy_AutoStart"

if %errorLevel% neq 0 (
    echo ❌ ERRORE: Fallita creazione task!
    pause
    exit /b 1
)

echo ✅ Task Scheduler configurato con successo!
echo.

REM Verifica task creato
echo 📊 Verifica configurazione:
schtasks /query /tn "KLMNR_Legacy_AutoStart" /fo LIST | findstr /C:"Task Name" /C:"Status" /C:"Next Run Time"

echo.
echo 🎯 CONFIGURAZIONE COMPLETATA!
echo =================================================================
echo.
echo ✅ Task "KLMNR_Legacy_AutoStart" creato
echo ⏰ Avvio: 2 minuti dopo il boot del sistema
echo 🔄 Restart automatico: 3 tentativi (5 min pausa)
echo 📝 Log: legacy_system/logs/auto_start_YYYYMMDD.log
echo.
echo 🛠️  GESTIONE TASK:
echo    ▶️  Test manuale: schtasks /run /tn "KLMNR_Legacy_AutoStart"
echo    ⏹️  Disabilita:   schtasks /change /tn "KLMNR_Legacy_AutoStart" /disable
echo    ✅ Abilita:      schtasks /change /tn "KLMNR_Legacy_AutoStart" /enable
echo    🗑️  Rimuovi:      schtasks /delete /tn "KLMNR_Legacy_AutoStart" /f
echo.
echo 📱 Monitoraggio tramite Task Scheduler:
echo    1. Apri Task Scheduler (taskschd.msc)
echo    2. Vai su "Task Scheduler Library"
echo    3. Cerca "KLMNR_Legacy_AutoStart"
echo.

choice /c YN /m "Vuoi testare il task ora (Y/N)"
if %errorLevel% equ 1 (
    echo.
    echo 🧪 Test del task...
    schtasks /run /tn "KLMNR_Legacy_AutoStart"
    echo    Task avviato! Controlla i log per l'esito.
)

echo.
echo ✅ Setup completato! Il sistema si avvierà automaticamente al prossimo boot.
pause
