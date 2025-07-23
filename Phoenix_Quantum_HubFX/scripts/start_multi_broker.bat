@echo off
REM Multi-Broker Quantum Trading System - Windows Launcher
REM The5ers | FTMO | MyForexFunds | Multi-MT5 Support

title Multi-Broker Quantum Trading System

echo.
echo ========================================================
echo   MULTI-BROKER QUANTUM TRADING SYSTEM LAUNCHER
echo ========================================================
echo   Version 6.0.0 - Production Ready
echo   Supporting: The5ers, FTMO, MyForexFunds
echo ========================================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python non trovato nel PATH
    echo [INFO] Assicurati di aver installato Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Python trovato
echo.

REM Verifica file configurazione
if not exist "config\multi_broker_master_config.json" (
    echo [ERROR] File configurazione master non trovato
    echo [INFO] Assicurati che config\multi_broker_master_config.json esista
    pause
    exit /b 1
)

echo [INFO] Configurazione master trovata
echo.

REM Menu di scelta
echo Seleziona modalita di avvio:
echo.
echo 1. Avvio normale (tutti i broker)
echo 2. Solo The5ers
echo 3. Solo FTMO  
echo 4. Solo MyForexFunds
echo 5. Modalita debug
echo 6. Test configurazioni (senza trading)
echo 7. Dry run (simulazione)
echo.
set /p choice="Inserisci scelta (1-7): "

REM Processa scelta
if "%choice%"=="1" goto normal_start
if "%choice%"=="2" goto the5ers_only
if "%choice%"=="3" goto ftmo_only
if "%choice%"=="4" goto mff_only
if "%choice%"=="5" goto debug_mode
if "%choice%"=="6" goto check_only
if "%choice%"=="7" goto dry_run
goto invalid_choice

:normal_start
echo.
echo [INFO] Avvio normale - Tutti i broker
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py
goto end

:the5ers_only
echo.
echo [INFO] Avvio solo The5ers
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --broker THE5ERS
goto end

:ftmo_only
echo.
echo [INFO] Avvio solo FTMO
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --broker FTMO
goto end

:mff_only
echo.
echo [INFO] Avvio solo MyForexFunds
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --broker MYFOREXFUNDS
goto end

:debug_mode
echo.
echo [INFO] Modalita debug attiva
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --debug
goto end

:check_only
echo.
echo [INFO] Verifica configurazioni
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --check-only
pause
goto end

:dry_run
echo.
echo [INFO] Modalita dry-run (simulazione)
echo.
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --dry-run
goto end

:invalid_choice
echo.
echo [ERROR] Scelta non valida
pause
goto end

:end
echo.
echo [INFO] Operazione completata
echo.
pause
