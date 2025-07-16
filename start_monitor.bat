@echo off
REM THE5ERS LIVE MONITORING BATCH SCRIPT
REM Avvia il monitor live per trading The5ers

echo ========================================
echo THE5ERS LIVE MONITOR
echo ========================================

REM Controlla se esiste il file di config
if not exist "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json" (
    echo ERROR: Config file not found!
    echo Please ensure PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json exists
    pause
    exit /b 1
)

REM Controlla se esiste la directory logs
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

echo Starting THE5ERS Live Monitor...
echo Press Ctrl+C to stop and generate report
echo ========================================

REM Avvia il monitor
python monitor_the5ers_live.py PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json

echo ========================================
echo Monitor stopped
echo ========================================
pause
