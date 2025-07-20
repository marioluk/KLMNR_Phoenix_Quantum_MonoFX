@echo off
echo.
echo 🎯 THE5ERS QUANTUM TRADING SYSTEM - LEGACY LAUNCHER
echo ================================================================
echo.

REM Controllo che siamo nella cartella corretta
if not exist "PRO-THE5ERS-QM-PHOENIX-GITCOP.py" (
    echo ❌ ERRORE: File principale non trovato!
    echo    Assicurati di essere nella cartella legacy_system/
    pause
    exit /b 1
)

if not exist "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json" (
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
echo 📊 Monitor log: logs/PRO-THE5ERS-QM-PHOENIX-GITCOP-log-STEP1.log
echo ================================================================
echo.

REM Avvia il sistema
python PRO-THE5ERS-QM-PHOENIX-GITCOP.py

echo.
echo ✅ Sistema legacy terminato
pause
