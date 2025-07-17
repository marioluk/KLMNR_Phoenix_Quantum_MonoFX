@echo off
REM THE5ERS ANALYSIS BATCH SCRIPT
REM Analizza i risultati di trading da log file

echo ========================================
echo THE5ERS TRADING ANALYSIS
echo ========================================

REM Controlla se esiste il file di config
if not exist "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json" (
    echo ERROR: Config file not found!
    echo Please ensure PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json exists
    pause
    exit /b 1
)

REM Controlla se esiste il file di log
if not exist "logs\PRO-THE5ERS-QM-PHOENIX-GITCOP-log-140725-STEP1.log" (
    echo ERROR: Log file not found!
    echo Please ensure logs\PRO-THE5ERS-QM-PHOENIX-GITCOP-log-140725-STEP1.log exists
    pause
    exit /b 1
)

echo Starting THE5ERS Analysis...
echo This will generate a detailed report of your trading performance
echo ========================================

REM Avvia l'analisi
python analyze_the5ers.py PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json logs\PRO-THE5ERS-QM-PHOENIX-GITCOP-log-140725-STEP1.log

echo ========================================
echo Analysis completed! Check the generated report file.
echo ========================================
pause
