
@echo off
echo.
echo 🎯 QUANTUM TRADING SYSTEM - LEGACY LAUNCHER
echo ================================================================
echo.

REM Spostati nella directory root del progetto (una cartella sopra "scripts")
cd /d "%~dp0.."

REM Controllo che siamo nella cartella corretta
if not exist "phoenix_quantum_monofx_program.py" (
    echo ❌ ERRORE: File principale non trovato!
    echo    Assicurati di essere nella root del progetto!
    pause
    exit /b 1
)

if not exist "config/config_autonomous_high_stakes_production_ready.json" (
    echo ❌ ERRORE: File configurazione non trovato!
    echo    Assicurati che il file config JSON sia presente
    pause
    exit /b 1
)

echo ✅ File sistema trovati
echo 📁 Working directory: %CD%
echo.

REM Controllo Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRORE: Python non trovato nel PATH
    echo    Installa Python e assicurati sia nel PATH
    pause
    exit /b 1
)

echo ✅ Python disponibile
echo.

echo 🚀 Avvio sistema legacy...
echo 💡 Usa Ctrl+C per fermare il sistema
echo 📊 Monitor log: logs/log_autonomous_high_stakes_conservative_production_ready.log
echo 🔗 Connessione: Challenge-Account
echo ================================================================
echo.

REM Avvia il sistema
python phoenix_quantum_monofx_program.py

echo.
echo ✅ Sistema legacy terminato
pause
