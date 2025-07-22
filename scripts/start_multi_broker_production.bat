@echo off
rem ===================================================================
rem KLMNR Phoenix Quantum Multi-Broker Trading System
rem Script di avvio automatico per server di produzione
rem ===================================================================

title KLMNR Phoenix Quantum Multi-Broker System

rem Imposta directory di lavoro
cd /d "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum"

rem Verifica che la directory esista
if not exist "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum" (
    echo ERRORE: Directory non trovata!
    echo Verificare il percorso: C:\KLMNR_Projects\KLMNR_Phoenix_Quantum
    pause
    exit /b 1
)

rem Verifica che Python sia disponibile
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato nel PATH!
    echo Installare Python o aggiungere al PATH di sistema
    pause
    exit /b 1
)

rem Verifica che il file launcher esista
if not exist "multi_broker_launcher.py" (
    echo ERRORE: File multi_broker_launcher.py non trovato!
    pause
    exit /b 1
)

echo ===================================================================
echo  🚀 AVVIO KLMNR PHOENIX QUANTUM MULTI-BROKER SYSTEM
echo ===================================================================
echo  📁 Directory: %CD%
echo  🕒 Timestamp: %date% %time%
echo  🎯 Modalità: PRODUZIONE (Trading Reale)
echo ===================================================================
echo.

rem Avvia il sistema multi-broker in modalità produzione
python multi_broker_launcher.py

rem Se il programma termina con errore, mostra il codice
if errorlevel 1 (
    echo.
    echo ❌ ERRORE: Sistema terminato con codice %errorlevel%
    echo 📋 Controllare i log per dettagli
    echo 📁 Log directory: %CD%\logs\
    pause
) else (
    echo.
    echo ✅ Sistema terminato correttamente
)

rem Fine script
echo.
echo 🏁 Script terminato
pause
