@echo off
rem ===================================================================
rem KLMNR Phoenix Quantum Multi-Broker Trading System
rem Script con auto-restart per Task Scheduler di Windows
rem ===================================================================

setlocal enabledelayedexpansion

rem Imposta directory di lavoro
cd /d "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum"

rem Crea directory logs se non esiste
if not exist "logs" mkdir logs

rem Log dell'avvio del watchdog
echo %date% %time% - Avvio Watchdog Multi-Broker >> logs\watchdog.log

:MAIN_LOOP
    echo %date% %time% - Controllo stato sistema... >> logs\watchdog.log
    
    rem Controlla se il sistema è già in esecuzione
    set "system_running=0"
    for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| find "python.exe"') do (
        rem Rimuovi virgolette
        set "pid=%%i"
        set "pid=!pid:"=!"
        
        rem Verifica se è il nostro processo
        wmic process where "ProcessId=!pid!" get CommandLine /format:list 2>nul | find "multi_broker_launcher" >nul
        if not errorlevel 1 (
            set "system_running=1"
            echo %date% %time% - Sistema già attivo PID: !pid! >> logs\watchdog.log
        )
    )
    
    rem Se non è in esecuzione, avvialo
    if "!system_running!"=="0" (
        echo %date% %time% - Sistema non attivo, avvio... >> logs\watchdog.log
        
        rem Avvia il sistema in background
        start /b python multi_broker_launcher.py >> logs\multi_broker_output.log 2>&1
        
        if errorlevel 1 (
            echo %date% %time% - ERRORE avvio sistema >> logs\watchdog.log
        ) else (
            echo %date% %time% - Sistema avviato con successo >> logs\watchdog.log
        )
    )
    
    rem Attendi 5 minuti prima del prossimo controllo
    timeout /t 300 /nobreak >nul
    
    goto MAIN_LOOP

rem Questo punto non dovrebbe mai essere raggiunto
echo %date% %time% - Watchdog terminato inaspettatamente >> logs\watchdog.log
