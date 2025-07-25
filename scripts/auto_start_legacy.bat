@echo off
REM =================================================================
REM AUTO START LEGACY - Avvio automatico sistema legacy al boot
REM Creato per Task Scheduler Windows 10 Pro
REM =================================================================

echo [%date% %time%] AVVIO AUTOMATICO SISTEMA LEGACY
echo =================================================================

REM Cambia alla directory corretta
cd /d "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum_MonoFX"

REM Verifica che siamo nella directory corretta
if not exist "phoenix_quantum_monofx_program.py" (
    echo [ERROR] File principale non trovato in: %CD%
    echo [ERROR] Controlla il percorso del progetto
    exit /b 1
)

REM Attendi connessione di rete (importante per broker connection)
echo [INFO] Attesa connessione di rete...
timeout /t 30 /nobreak >nul

REM Controlla connettività internet
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Connessione internet non disponibile, riprovo in 60 secondi...
    timeout /t 60 /nobreak >nul
    ping -n 1 google.com >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Connessione internet non disponibile dopo 90 secondi
        exit /b 1
    )
)

echo [INFO] Connessione di rete verificata
echo [INFO] Avvio sistema legacy...

REM Crea log di avvio
echo [%date% %time%] Sistema legacy avviato automaticamente >> logs\auto_start.log

REM Avvia il sistema legacy
call start_legacy.bat

echo [%date% %time%] Sistema legacy terminato
