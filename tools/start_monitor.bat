@echo off
REM BROKER LIVE MONITORING BATCH SCRIPT
REM Avvia il monitor live per trading broker

echo ========================================
echo THE5ERS LIVE MONITOR
echo BROKER LIVE MONITOR
echo ========================================

REM Controlla se esiste il file di config
if not exist "phoenix_quantum_monofx_config-140725-STEP1.json" (
    echo ERROR: Config file not found!
    echo Please ensure phoenix_quantum_monofx_config-140725-STEP1.json exists
    pause
    exit /b 1
)

REM Controlla se esiste la directory logs
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

echo Starting BROKER Live Monitor...
echo Press Ctrl+C to stop and generate report
echo ========================================

REM Avvia il monitor
python monitor_broker_live.py phoenix_quantum_monofx_config-140725-STEP1.json

echo ========================================
echo Monitor stopped
echo ========================================
pause
