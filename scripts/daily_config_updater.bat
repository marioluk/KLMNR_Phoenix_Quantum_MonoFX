@echo off
REM ============================================================================
REM DAILY CONFIG UPDATER - Windows Batch Launcher
REM ============================================================================
REM
REM Script Windows per l'esecuzione automatica dell'aggiornamento giornaliero
REM delle configurazioni di trading tramite Windows Task Scheduler.
REM
REM Configurazione Task Scheduler:
REM - Trigger: Daily at 06:00
REM - Action: Start a program
REM - Program: cmd.exe
REM - Arguments: /c "C:\path\to\daily_config_updater.bat"
REM - Start in: C:\KLMNR_Projects\KLMNR_Phoenix_Quantum
REM
REM Autore: KLMNR System
REM Data: 20 Luglio 2025
REM ============================================================================

setlocal enabledelayedexpansion

REM Configurazione
set "SCRIPT_DIR=%~dp0"
set "WORKSPACE_DIR=%SCRIPT_DIR%"
set "PYTHON_SCRIPT=%WORKSPACE_DIR%daily_config_updater.py"
set "LOG_DIR=%WORKSPACE_DIR%logs\daily_updater"
set "TIMESTAMP=%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "LOG_FILE=%LOG_DIR%\daily_updater_batch_%TIMESTAMP%.log"

REM Pulizia timestamp (rimuovi spazi)
set "TIMESTAMP=%TIMESTAMP: =0%"
set "LOG_FILE=%LOG_DIR%\daily_updater_batch_%TIMESTAMP%.log"

echo ============================================================================
echo DAILY CONFIG UPDATER - Avvio %DATE% %TIME%
echo ============================================================================

REM Crea directory log se non esiste
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Verifica esistenza script Python
if not exist "%PYTHON_SCRIPT%" (
    echo ERRORE: Script Python non trovato: %PYTHON_SCRIPT%
    echo Assicurati che il file daily_config_updater.py esista nella directory del workspace.
    pause
    exit /b 1
)

REM Log avvio
echo [%DATE% %TIME%] Avvio daily config updater... >> "%LOG_FILE%"
echo [%DATE% %TIME%] Workspace: %WORKSPACE_DIR% >> "%LOG_FILE%"
echo [%DATE% %TIME%] Script: %PYTHON_SCRIPT% >> "%LOG_FILE%"

REM Cambia directory workspace
cd /d "%WORKSPACE_DIR%"

REM Esegui script Python
echo Esecuzione aggiornamento configurazioni...
echo [%DATE% %TIME%] Esecuzione script Python... >> "%LOG_FILE%"

python "%PYTHON_SCRIPT%" --workspace "%WORKSPACE_DIR%" --log-level INFO >> "%LOG_FILE%" 2>&1

REM Controlla risultato
set "EXIT_CODE=%ERRORLEVEL%"
echo [%DATE% %TIME%] Script completato con codice: %EXIT_CODE% >> "%LOG_FILE%"

if %EXIT_CODE% equ 0 (
    echo ============================================================================
    echo ✅ AGGIORNAMENTO COMPLETATO CON SUCCESSO
    echo ============================================================================
    echo [%DATE% %TIME%] ✅ SUCCESSO: Aggiornamento completato >> "%LOG_FILE%"
) else (
    echo ============================================================================
    echo ❌ AGGIORNAMENTO FALLITO - Codice errore: %EXIT_CODE%
    echo ============================================================================
    echo [%DATE% %TIME%] ❌ ERRORE: Aggiornamento fallito con codice %EXIT_CODE% >> "%LOG_FILE%"
)

echo Log salvato in: %LOG_FILE%
echo.

REM Se eseguito manualmente, attendi input
if /i "%1" neq "auto" (
    echo Premere un tasto per continuare...
    pause >nul
)

echo [%DATE% %TIME%] Script batch terminato >> "%LOG_FILE%"

exit /b %EXIT_CODE%
