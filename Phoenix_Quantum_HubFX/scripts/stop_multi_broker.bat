@echo off
rem ===================================================================
rem KLMNR Phoenix Quantum Multi-Broker Trading System
rem Script di arresto sicuro del sistema
rem ===================================================================

title Stop Multi-Broker System

echo ===================================================================
echo  🛑 ARRESTO KLMNR PHOENIX QUANTUM MULTI-BROKER SYSTEM
echo ===================================================================
echo.

rem Log dell'arresto
echo %date% %time% - Richiesta arresto sistema >> logs\system_startup.log

echo 🔍 Ricerca processi Python multi-broker...

rem Trova e termina gracefully i processi multi-broker
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    echo 🔍 Trovato processo Python: %%i
    
    rem Verifica se è il nostro processo (controlla la command line)
    wmic process where "ProcessId=%%i" get CommandLine /format:list 2>nul | find "multi_broker_launcher" >nul
    if not errorlevel 1 (
        echo 🛑 Terminazione processo multi-broker %%i...
        taskkill /pid %%i /t
        echo ✅ Processo %%i terminato
    )
)

echo.
echo 🔍 Verifica processi MetaTrader5...

rem Termina eventuali MT5 aperti dal sistema
tasklist /fi "imagename eq terminal64.exe" /fo csv | find "terminal64.exe" >nul
if not errorlevel 1 (
    echo 🛑 Terminazione MetaTrader5...
    taskkill /im terminal64.exe /t /f >nul 2>&1
    echo ✅ MetaTrader5 terminato
) else (
    echo ℹ️  Nessun processo MetaTrader5 attivo
)

echo.
echo ✅ Arresto completato
echo 📋 Controllare i log per dettagli: logs\system_startup.log
echo.
pause
