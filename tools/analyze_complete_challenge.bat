@echo off
REM THE5ERS COMPLETE CHALLENGE ANALYSIS
REM Analizza tutti i dati della challenge Step 1 dal 7 luglio

echo ==========================================
echo THE5ERS COMPLETE CHALLENGE ANALYSIS
echo ==========================================

REM Controlla se esiste il file di config
if not exist "phoenix_quantum_hubfx_program-config-140725-STEP1.json" (
    echo ERROR: Config file not found!
    echo Please ensure phoenix_quantum_hubfx_program-config-140725-STEP1.json exists
    pause
    exit /b 1
)

echo Starting Complete Challenge Analysis...
echo This will analyze ALL your trades from July 7th, 2025
echo Data will be retrieved directly from MetaTrader 5
echo ==========================================

REM Avvia l'analisi completa
python analyze_complete_challenge.py phoenix_quantum_hubfx_program-config-140725-STEP1.json

echo ==========================================
echo Complete Challenge Analysis finished!
echo Check the generated report file.
echo ==========================================
pause
