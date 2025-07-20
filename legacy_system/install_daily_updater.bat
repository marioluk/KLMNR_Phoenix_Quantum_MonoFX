@echo off
REM ==============================================================================
REM QUICK ADMIN CHECK - Verifica e lancio setup come amministratore
REM ==============================================================================

echo ===============================================================================
echo KLMNR DAILY CONFIG UPDATER - INSTALLAZIONE AUTOMATICA
echo ===============================================================================
echo.

REM Verifica privilegi amministratore
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Privilegi amministratore richiesti per installazione Task Scheduler
    echo.
    echo SOLUZIONI:
    echo.
    echo [OPZIONE 1] Manuale - Apri CMD come Amministratore
    echo   1. Tasto destro su "Prompt dei comandi" 
    echo   2. Seleziona "Esegui come amministratore"
    echo   3. Naviga nella directory: cd "%~dp0"
    echo   4. Esegui: setup_auto_start_daily_updater.bat
    echo.
    echo [OPZIONE 2] Automatica - Rilancio con privilegi (Raccomandato)
    echo.
    set /p choice="Vuoi provare a rilanciare automaticamente come amministratore? (S/N): "
    
    if /i "%choice%"=="S" (
        echo [INFO] Rilancio come amministratore...
        echo [INFO] Potrebbe apparire una finestra UAC - conferma per procedere
        
        REM Rilancia con privilegi amministratore
        powershell -Command "Start-Process '%~dp0setup_auto_start_daily_updater.bat' -Verb RunAs"
        
        echo [INFO] Setup avviato in finestra separata con privilegi amministratore
        echo [INFO] Controlla la nuova finestra per completare l'installazione
    ) else (
        echo [INFO] Installazione annullata
        echo [INFO] Usa l'OPZIONE 1 per installare manualmente
    )
    
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Privilegi amministratore disponibili
    echo [INFO] Avvio installazione diretta...
    echo.
    
    REM Esegui setup direttamente
    call "%~dp0setup_auto_start_daily_updater.bat"
    
    echo.
    echo [INFO] Installazione completata
    pause
    exit /b 0
)
