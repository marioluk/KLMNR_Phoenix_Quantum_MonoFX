@echo off
rem ===================================================================
rem KLMNR Phoenix Quantum Multi-Broker Trading System
rem Script di monitoraggio stato sistema
rem ===================================================================

title Monitor Multi-Broker System

echo ===================================================================
echo  📊 MONITOR KLMNR PHOENIX QUANTUM MULTI-BROKER SYSTEM
echo ===================================================================
echo  🕒 Timestamp: %date% %time%
echo ===================================================================
echo.

rem Controlla se il sistema è in esecuzione
echo 🔍 Controllo processi attivi...
echo.

set "found_multibroker=0"
set "found_mt5=0"

rem Cerca processi Python multi-broker
for /f "tokens=2,5" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv') do (
    rem Rimuovi le virgolette
    set "pid=%%i"
    set "pid=!pid:"=!"
    
    rem Controlla se è il nostro processo
    wmic process where "ProcessId=!pid!" get CommandLine /format:list 2>nul | find "multi_broker_launcher" >nul
    if not errorlevel 1 (
        echo ✅ Multi-Broker System ATTIVO - PID: !pid!
        set "found_multibroker=1"
    )
)

if "%found_multibroker%"=="0" (
    echo ❌ Multi-Broker System NON ATTIVO
)

echo.

rem Cerca processi MetaTrader5
for /f "tokens=2,5" %%i in ('tasklist /fi "imagename eq terminal64.exe" /fo csv') do (
    rem Rimuovi le virgolette
    set "pid=%%i"
    set "pid=!pid:"=!"
    echo ✅ MetaTrader5 ATTIVO - PID: !pid!
    set "found_mt5=1"
)

if "%found_mt5%"=="0" (
    echo ℹ️  Nessun MetaTrader5 attivo
)

echo.
echo ===================================================================

rem Mostra ultimi log se esistono
if exist "logs\system_startup.log" (
    echo 📋 ULTIMI LOG DI SISTEMA:
    echo -------------------------------------------------------------------
    powershell "Get-Content 'logs\system_startup.log' | Select-Object -Last 10"
    echo.
)

if exist "logs\multi_broker_output.log" (
    echo 📊 ULTIMI LOG MULTI-BROKER:
    echo -------------------------------------------------------------------
    powershell "Get-Content 'logs\multi_broker_output.log' | Select-Object -Last 5"
    echo.
)

echo ===================================================================
echo 💡 COMANDI DISPONIBILI:
echo   - start_multi_broker_production.bat : Avvia sistema (interattivo)
echo   - start_multi_broker_service.bat    : Avvia sistema (background)
echo   - stop_multi_broker.bat             : Ferma sistema
echo   - monitor_multi_broker.bat          : Questo script
echo ===================================================================
echo.
pause
