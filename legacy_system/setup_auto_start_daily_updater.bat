@echo off
REM ==============================================================================
REM SETUP AUTO START DAILY CONFIG UPDATER
REM Installazione automatica Task Scheduler per Daily Config Updater alle 06:00
REM ==============================================================================

echo ===============================================================================
echo KLMNR DAILY CONFIG UPDATER - SETUP AUTO START
echo ===============================================================================
echo.

REM Verifica privilegi amministratore
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Questo script richiede privilegi di amministratore
    echo [INFO] Clicca destro sul file e seleziona "Esegui come amministratore"
    echo.
    pause
    exit /b 1
)

echo [OK] Privilegi amministratore verificati
echo.

REM Configurazione paths
set SCRIPT_DIR=%~dp0
set XML_FILE=%SCRIPT_DIR%KLMNR_Daily_Config_Updater.xml
set BAT_FILE=%SCRIPT_DIR%auto_start_daily_updater.bat
set PS_FILE=%SCRIPT_DIR%AutoStartDailyUpdater.ps1
set TASK_NAME=KLMNR_Daily_Config_Updater

echo [INFO] Directory: %SCRIPT_DIR%
echo [INFO] Task XML: %XML_FILE%
echo [INFO] BAT Script: %BAT_FILE%
echo [INFO] PowerShell Script: %PS_FILE%
echo [INFO] Task Name: %TASK_NAME%
echo.

REM Verifica file necessari
echo [INFO] Verifica file necessari...

if not exist "%XML_FILE%" (
    echo [ERROR] File XML non trovato: %XML_FILE%
    goto :error
)
echo [OK] File XML trovato

if not exist "%BAT_FILE%" (
    echo [ERROR] File BAT non trovato: %BAT_FILE%
    goto :error
)
echo [OK] File BAT trovato

if not exist "%PS_FILE%" (
    echo [ERROR] File PowerShell non trovato: %PS_FILE%
    goto :error
)
echo [OK] File PowerShell trovato

echo.

REM Verifica se task esiste già
echo [INFO] Verifica task esistente...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Task %TASK_NAME% già esistente
    echo [INFO] Rimozione task esistente...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Task esistente rimosso
    ) else (
        echo [ERROR] Errore rimozione task esistente
        goto :error
    )
) else (
    echo [OK] Nessun task esistente da rimuovere
)

echo.

REM Importa task dal file XML
echo [INFO] Importazione task nel Task Scheduler...
schtasks /create /xml "%XML_FILE%" /tn "%TASK_NAME%"

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Task importato con successo!
) else (
    echo [ERROR] Errore importazione task (Exit code: %ERRORLEVEL%)
    goto :error
)

echo.

REM Verifica task creato
echo [INFO] Verifica task creato...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Task verificato nel Task Scheduler
    echo [INFO] Dettagli task:
    schtasks /query /tn "%TASK_NAME%" /fo LIST | findstr /C:"TaskName" /C:"Next Run Time" /C:"Status" 2>nul
) else (
    echo [WARNING] Non riesco a verificare il task (potrebbe essere un problema di privilegi)
    echo [INFO] Il task dovrebbe essere stato creato correttamente
)

echo.

REM Opzioni post-installazione
echo ===============================================================================
echo INSTALLAZIONE COMPLETATA!
echo ===============================================================================
echo.
echo Il Daily Config Updater è ora configurato per eseguire:
echo - OGNI GIORNO alle 06:00
echo - Con restart automatico su errore (max 3 tentativi)
echo - Con log dettagliati in legacy_system\logs\
echo.
echo OPZIONI DISPONIBILI:
echo.
echo [1] Test immediato del task
echo [2] Visualizza dettagli task
echo [3] Modifica orario esecuzione
echo [4] Disabilita task temporaneamente
echo [5] Esci
echo.

:menu
set /p choice="Scegli opzione (1-5): "

if "%choice%"=="1" goto :test_task
if "%choice%"=="2" goto :show_details
if "%choice%"=="3" goto :modify_schedule
if "%choice%"=="4" goto :disable_task
if "%choice%"=="5" goto :exit_success

echo [ERROR] Opzione non valida. Riprova.
goto :menu

:test_task
echo.
echo [INFO] Avvio test immediato del task...
schtasks /run /tn "%TASK_NAME%"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task avviato
    echo [INFO] Controlla i log in: %SCRIPT_DIR%logs\auto_start_daily_updater_*.log
) else (
    echo [ERROR] Errore avvio task
)
echo.
goto :menu

:show_details
echo.
echo [INFO] Dettagli task:
echo -------------------------------------------------------------------------------
schtasks /query /tn "%TASK_NAME%" /fo LIST /v
echo -------------------------------------------------------------------------------
echo.
goto :menu

:modify_schedule
echo.
echo [INFO] Per modificare l'orario, usa il Task Scheduler di Windows:
echo 1. Premi Win+R, digita 'taskschd.msc' e premi Invio
echo 2. Cerca il task '%TASK_NAME%'
echo 3. Doppio click per modificare le proprietà
echo 4. Vai alla scheda 'Trigger' per cambiare l'orario
echo.
goto :menu

:disable_task
echo.
echo [INFO] Disabilitazione temporanea del task...
schtasks /change /tn "%TASK_NAME%" /disable
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task disabilitato
    echo [INFO] Per riabilitarlo: schtasks /change /tn "%TASK_NAME%" /enable
) else (
    echo [ERROR] Errore disabilitazione task
)
echo.
goto :menu

:error
echo.
echo [ERROR] Installazione fallita!
echo [INFO] Verifica i log di Windows Event Viewer per dettagli
echo.
pause
exit /b 1

:exit_success
echo.
echo [INFO] Setup completato con successo!
echo [INFO] Il Daily Config Updater si avvierà automaticamente alle 06:00
echo.
pause
exit /b 0
