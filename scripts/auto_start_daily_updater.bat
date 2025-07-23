@echo off
REM ==============================================================================
REM AUTO START DAILY CONFIG UPDATER - BAT Wrapper
REM Wrapper CMD per compatibilità con AutoStartDailyUpdater.ps1
REM ==============================================================================

setlocal enabledelayedexpansion

REM Configurazione
set SCRIPT_DIR=%~dp0
set BACKTEST_DIR=%SCRIPT_DIR%backtest_mono
set LOGS_DIR=%SCRIPT_DIR%logs
set POWERSHELL_SCRIPT=%SCRIPT_DIR%AutoStartDailyUpdater.ps1

REM Data corrente per log
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"

set LOG_FILE=%LOGS_DIR%\auto_start_daily_updater_%YYYY%%MM%%DD%.log

echo ===============================================================================
echo KLMNR DAILY CONFIG UPDATER - AUTO START (BAT)
echo ===============================================================================
echo Data: %YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%
echo Script Dir: %SCRIPT_DIR%
echo Backtest Dir: %BACKTEST_DIR%
echo Log File: %LOG_FILE%
echo.

REM Crea directory logs se non esiste
if not exist "%LOGS_DIR%" (
    mkdir "%LOGS_DIR%"
    echo [INFO] Directory logs creata: %LOGS_DIR%
)

REM Verifica connettività (ping veloce)
echo [INFO] Verifica connettività internet...
ping -n 1 -w 3000 8.8.8.8 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Connessione internet verificata
) else (
    echo [WARNING] Connessione internet non disponibile
    echo [WARNING] Il daily config updater potrebbe non funzionare correttamente
)

REM Verifica file daily config updater
if not exist "%BACKTEST_DIR%\daily_config_updater.py" (
    echo [ERROR] File daily_config_updater.py non trovato
    echo [ERROR] Path: %BACKTEST_DIR%\daily_config_updater.py
    echo [ERROR] Auto-start terminato con errore
    exit /b 1
)

echo [INFO] File daily_config_updater.py verificato

REM Verifica se PowerShell è disponibile
where powershell >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] PowerShell disponibile, uso script avanzato
    echo [INFO] Avvio: %POWERSHELL_SCRIPT%
    echo.
    
    REM Esegui script PowerShell
    powershell -ExecutionPolicy Bypass -File "%POWERSHELL_SCRIPT%" -LogPath "%LOG_FILE%"
    set POWERSHELL_EXIT=%ERRORLEVEL%
    
    echo.
    echo [INFO] PowerShell script terminato con exit code: %POWERSHELL_EXIT%
    exit /b %POWERSHELL_EXIT%
    
) else (
    echo [INFO] PowerShell non disponibile, esecuzione diretta
    echo.
    
    REM Cambia directory
    pushd "%BACKTEST_DIR%"
    
    REM Esegui daily config updater direttamente
    echo [INFO] Avvio daily_config_updater.py...
    
    REM Prova prima con il BAT wrapper se esiste
    if exist "daily_config_updater.bat" (
        echo [INFO] Uso wrapper BAT: daily_config_updater.bat
        call daily_config_updater.bat
        set EXIT_CODE=!ERRORLEVEL!
    ) else (
        echo [INFO] Esecuzione diretta Python
        python daily_config_updater.py --days 60
        set EXIT_CODE=!ERRORLEVEL!
    )
    
    popd
    
    REM Controlla risultato
    if !EXIT_CODE! EQU 0 (
        echo.
        echo [SUCCESS] Daily config updater completato con successo!
        echo [INFO] Configurazioni ottimali generate e pronte per produzione
    ) else (
        echo.
        echo [ERROR] Daily config updater terminato con errori (Exit code: !EXIT_CODE!)
        echo [ERROR] Verificare i log per dettagli
    )
    
    exit /b !EXIT_CODE!
)
