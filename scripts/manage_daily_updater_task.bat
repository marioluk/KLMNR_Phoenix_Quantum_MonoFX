@echo off
REM ==============================================================================
REM MANAGE DAILY CONFIG UPDATER TASK
REM Gestione completa del task Daily Config Updater
REM ==============================================================================

setlocal enabledelayedexpansion

set TASK_NAME=KLMNR_Daily_Config_Updater
set SCRIPT_DIR=%~dp0
set LOGS_DIR=%SCRIPT_DIR%logs

echo ===============================================================================
echo KLMNR DAILY CONFIG UPDATER - TASK MANAGEMENT
echo ===============================================================================
echo Task Name: %TASK_NAME%
echo Logs Dir: %LOGS_DIR%
echo.

REM Verifica se task esiste
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Task '%TASK_NAME%' non trovato!
    echo [INFO] Esegui prima setup_auto_start_daily_updater.bat per installarlo
    echo.
    pause
    exit /b 1
)

:menu
echo OPZIONI DISPONIBILI:
echo.
echo [1] Stato del task
echo [2] Avvia task manualmente
echo [3] Ferma task in esecuzione
echo [4] Abilita task
echo [5] Disabilita task
echo [6] Visualizza log recenti
echo [7] Visualizza tutti i log
echo [8] Elimina log vecchi (^>7 giorni)
echo [9] Rimuovi task completamente
echo [0] Esci
echo.

set /p choice="Scegli opzione (0-9): "

if "%choice%"=="1" goto :status
if "%choice%"=="2" goto :run_task
if "%choice%"=="3" goto :stop_task
if "%choice%"=="4" goto :enable_task
if "%choice%"=="5" goto :disable_task
if "%choice%"=="6" goto :recent_logs
if "%choice%"=="7" goto :all_logs
if "%choice%"=="8" goto :cleanup_logs
if "%choice%"=="9" goto :remove_task
if "%choice%"=="0" goto :exit

echo [ERROR] Opzione non valida. Riprova.
echo.
goto :menu

:status
echo.
echo [INFO] Stato task '%TASK_NAME%':
echo -------------------------------------------------------------------------------
schtasks /query /tn "%TASK_NAME%" /fo LIST | findstr /C:"TaskName" /C:"Next Run Time" /C:"Last Run Time" /C:"Last Result" /C:"Status"
echo -------------------------------------------------------------------------------
echo.
goto :menu

:run_task
echo.
echo [INFO] Avvio manuale del task...
schtasks /run /tn "%TASK_NAME%"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task avviato con successo
    echo [INFO] Controlla lo stato con l'opzione 1
) else (
    echo [ERROR] Errore avvio task (Exit code: %ERRORLEVEL%)
)
echo.
goto :menu

:stop_task
echo.
echo [INFO] Arresto del task in esecuzione...
schtasks /end /tn "%TASK_NAME%"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task arrestato con successo
) else (
    echo [INFO] Task non in esecuzione o errore arresto
)
echo.
goto :menu

:enable_task
echo.
echo [INFO] Abilitazione task...
schtasks /change /tn "%TASK_NAME%" /enable
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task abilitato con successo
    echo [INFO] Il task verrà eseguito automaticamente alle 06:00
) else (
    echo [ERROR] Errore abilitazione task
)
echo.
goto :menu

:disable_task
echo.
echo [INFO] Disabilitazione task...
schtasks /change /tn "%TASK_NAME%" /disable
if %ERRORLEVEL% EQU 0 (
    echo [OK] Task disabilitato con successo
    echo [WARNING] Il task NON verrà più eseguito automaticamente
) else (
    echo [ERROR] Errore disabilitazione task
)
echo.
goto :menu

:recent_logs
echo.
echo [INFO] Log recenti del Daily Config Updater:
echo ===============================================================================

REM Trova il log più recente
set RECENT_LOG=
for /f "delims=" %%f in ('dir /b /o-d "%LOGS_DIR%\auto_start_daily_updater_*.log" 2^>nul') do (
    if "!RECENT_LOG!"=="" set RECENT_LOG=%%f
)

if "!RECENT_LOG!"=="" (
    echo [INFO] Nessun log trovato
) else (
    echo [FILE] %LOGS_DIR%\!RECENT_LOG!
    echo -------------------------------------------------------------------------------
    type "%LOGS_DIR%\!RECENT_LOG!"
)

echo ===============================================================================
echo.
goto :menu

:all_logs
echo.
echo [INFO] Tutti i log del Daily Config Updater:
echo ===============================================================================

if not exist "%LOGS_DIR%\auto_start_daily_updater_*.log" (
    echo [INFO] Nessun log trovato
) else (
    for %%f in ("%LOGS_DIR%\auto_start_daily_updater_*.log") do (
        echo.
        echo [FILE] %%f
        echo -------------------------------------------------------------------------------
        type "%%f"
        echo -------------------------------------------------------------------------------
    )
)

echo ===============================================================================
echo.
goto :menu

:cleanup_logs
echo.
echo [INFO] Pulizia log più vecchi di 7 giorni...

set /a count=0
for %%f in ("%LOGS_DIR%\auto_start_daily_updater_*.log") do (
    forfiles /p "%LOGS_DIR%" /m "%%~nxf" /d -7 >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        del "%%f"
        set /a count+=1
        echo [DELETE] %%~nxf
    )
)

if !count! EQU 0 (
    echo [INFO] Nessun log da rimuovere
) else (
    echo [SUCCESS] Rimossi !count! log obsoleti
)
echo.
goto :menu

:remove_task
echo.
echo [WARNING] Questa operazione rimuoverà completamente il task!
echo [WARNING] Il Daily Config Updater NON verrà più eseguito automaticamente!
echo.
set /p confirm="Sei sicuro? (S/N): "

if /i "%confirm%"=="S" (
    echo [INFO] Rimozione task...
    schtasks /delete /tn "%TASK_NAME%" /f
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Task rimosso con successo
        echo [INFO] Per reinstallarlo, esegui setup_auto_start_daily_updater.bat
    ) else (
        echo [ERROR] Errore rimozione task
    )
) else (
    echo [INFO] Operazione annullata
)
echo.
goto :menu

:exit
echo.
echo [INFO] Task Management terminato
exit /b 0
