@echo off
REM THE5ERS GRAPHICAL DASHBOARD LAUNCHER (LEGACY SYSTEM)
REM Avvia la dashboard web interattiva per il sistema legacy

echo ==========================================
echo THE5ERS GRAPHICAL DASHBOARD - LEGACY
echo ==========================================

REM Controlla se esiste il file di config nella cartella corretta (root progetto)
if not exist "..\config\config_autonomous_challenge_production_ready.json" (
    echo ERROR: Config file not found!
    echo Please ensure ..\config\config_autonomous_challenge_production_ready.json exists
    pause
    exit /b 1
)

REM Controlla se esiste la directory logs
    if not exist "..\..\logs" (
        echo Creating logs directory...
        mkdir "..\..\logs"
    )

REM Controlla se esiste la directory templates
if not exist "templates" (
    echo ERROR: Templates directory not found!
    echo Please ensure the templates directory exists with dashboard.html
    pause
    exit /b 1
)

echo Installing required Python packages...
pip install flask plotly pandas MetaTrader5 > nul 2>&1

echo Starting THE5ERS Graphical Dashboard - LEGACY SYSTEM...
echo Web interface will be available at: http://127.0.0.1:5000
echo Features:
echo - Real-time data from log files
echo - Complete challenge data from MT5
echo - Auto-detect configuration from legacy system
echo - Click "Refresh MT5" button to update with latest data
echo ==========================================

REM Avvia la dashboard e apri il browser
    start http://127.0.0.1:5000
    python dashboard_broker.py

echo ==========================================
echo Dashboard stopped
echo ==========================================
pause
