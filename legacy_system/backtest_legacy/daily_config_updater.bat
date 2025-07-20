@echo off
REM ==============================================================================
REM DAILY CONFIG UPDATER - Launcher per Windows
REM Aggiornamento automatico configurazioni The5ers
REM ==============================================================================

set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%..\logs

REM Crea directory log se non esiste
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Data corrente per log
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

echo ===============================================================================
echo THE5ERS DAILY CONFIG UPDATER - %YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%
echo ===============================================================================
echo.

REM Cambio directory
cd /d "%SCRIPT_DIR%"

REM Esegui aggiornamento con logging
echo 📅 Avvio aggiornamento giornaliero configurazioni...
echo 📁 Directory: %SCRIPT_DIR%
echo 📊 Log: %LOG_DIR%\daily_config_updater_%YYYY%%MM%%DD%.log
echo.

python daily_config_updater.py --days 30 2>&1

REM Controlla risultato
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ AGGIORNAMENTO COMPLETATO CON SUCCESSO
    echo 📄 Controlla i nuovi file nella cartella config
) else (
    echo.
    echo ❌ AGGIORNAMENTO FALLITO - ERRORLEVEL: %ERRORLEVEL%
    echo 📋 Controlla il log per dettagli: %LOG_DIR%\daily_config_updater_%YYYY%%MM%%DD%.log
)

echo.
echo Premi un tasto per continuare...
pause >nul
