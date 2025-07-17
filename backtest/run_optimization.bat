@echo off
echo ==========================================
echo THE5ERS QUANTUM ALGORITHM OPTIMIZER
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python non trovato nel PATH
    echo Installare Python o aggiungerlo al PATH
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "results" mkdir results
if not exist "reports" mkdir reports
if not exist "data" mkdir data

echo Cartelle create/verificate:
echo - logs/
echo - results/
echo - reports/
echo - data/
echo.

REM Set up virtual environment if needed
if not exist "venv" (
    echo Creazione virtual environment...
    python -m venv venv
    echo Virtual environment creato
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required packages
echo Installazione dipendenze...
pip install numpy pandas matplotlib seaborn scipy scikit-learn

echo.
echo ==========================================
echo AVVIO OTTIMIZZAZIONE
echo ==========================================
echo.

REM Run the optimization
python run_optimization.py

echo.
echo ==========================================
echo OTTIMIZZAZIONE COMPLETATA
echo ==========================================
echo.
echo Controlla i file di risultati in:
echo - results/
echo - reports/
echo.

pause
