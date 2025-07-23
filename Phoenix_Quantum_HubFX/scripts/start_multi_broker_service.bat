@echo off
rem ===================================================================
rem KLMNR Phoenix Quantum Multi-Broker Trading System
rem Script di avvio automatico SILENZIOSO per servizi/cronjob
rem ===================================================================

rem Imposta directory di lavoro
cd /d "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum"

rem Log dell'avvio
echo %date% %time% - Avvio Multi-Broker System >> logs\system_startup.log

rem Verifica prerequisiti (silenzioso)
if not exist "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum" (
    echo %date% %time% - ERRORE: Directory non trovata >> logs\system_startup.log
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo %date% %time% - ERRORE: Python non disponibile >> logs\system_startup.log
    exit /b 1
)

if not exist "multi_broker_launcher.py" (
    echo %date% %time% - ERRORE: Launcher non trovato >> logs\system_startup.log
    exit /b 1
)

rem Crea directory logs se non esiste
if not exist "logs" mkdir logs

rem Avvia in background con redirect dei log
echo %date% %time% - Sistema avviato in modalità produzione >> logs\system_startup.log

rem Avvio con output reindirizzato ai log
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py >> logs\multi_broker_output.log 2>&1

rem Log del risultato
if errorlevel 1 (
    echo %date% %time% - Sistema terminato con errore %errorlevel% >> logs\system_startup.log
) else (
    echo %date% %time% - Sistema terminato correttamente >> logs\system_startup.log
)

exit /b %errorlevel%
