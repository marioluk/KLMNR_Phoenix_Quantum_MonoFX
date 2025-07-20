@echo off
REM ==============================================================================
REM MT5 MANUAL MODE MANAGER
REM Gestisce l'apertura sicura di MT5 manuale senza interferenze
REM ==============================================================================

setlocal enabledelayedexpansion

echo ===============================================================================
echo KLMNR MT5 MANUAL MODE MANAGER
echo ===============================================================================
echo.

:MENU
echo Scegli un'opzione:
echo [1] Ferma sistema automatico e apri MT5 manuale
echo [2] Chiudi MT5 manuale e riavvia sistema automatico
echo [3] Controlla stato processi MT5
echo [4] Esci
echo.
set /p choice="Scelta: "

if "%choice%"=="1" goto STOP_AUTO
if "%choice%"=="2" goto START_AUTO
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto EXIT
goto MENU

:STOP_AUTO
echo.
echo [INFO] Fermo sistema automatico...
echo [WARNING] ATTENZIONE: Il trading automatico verrà interrotto!
set /p confirm="Sei sicuro? (S/N): "
if /i not "%confirm%"=="S" goto MENU

echo [INFO] Termino processi Python...
tasklist | findstr python.exe >nul
if %ERRORLEVEL% EQU 0 (
    taskkill /F /IM python.exe /T >nul 2>&1
    echo [OK] Processi Python terminati
) else (
    echo [INFO] Nessun processo Python attivo
)

echo [INFO] Termino processi MT5 background...
tasklist | findstr terminal64.exe >nul
if %ERRORLEVEL% EQU 0 (
    taskkill /F /IM terminal64.exe /T >nul 2>&1
    echo [OK] Processi MT5 background terminati
) else (
    echo [INFO] Nessun processo MT5 background attivo
)

echo.
echo [SUCCESS] Sistema automatico fermato!
echo [INFO] Ora puoi aprire MT5 manualmente senza interferenze
echo [WARNING] RICORDA: Usa opzione [2] per riavviare il sistema automatico
echo.
pause
goto MENU

:START_AUTO
echo.
echo [INFO] Riavvio sistema automatico...

echo [INFO] Verifico che MT5 manuale sia chiuso...
tasklist | findstr terminal.exe >nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] MT5 ancora aperto manualmente!
    echo [WARNING] Chiudi prima MT5 manuale per evitare conflitti
    pause
    goto MENU
)

echo [INFO] Avvio sistema di trading automatico...
cd /d "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum"

REM Verifica quale sistema usare
if exist "quantum_main_refactored.py" (
    echo [INFO] Avvio quantum_main_refactored.py in background...
    start /MIN python quantum_main_refactored.py
    echo [OK] Sistema automatico riavviato
) else if exist "legacy_system\start_legacy.bat" (
    echo [INFO] Avvio sistema legacy...
    call "legacy_system\start_legacy.bat"
    echo [OK] Sistema legacy riavviato
) else (
    echo [ERROR] Sistema automatico non trovato!
    echo [ERROR] Verifica i file di avvio
)

echo.
echo [SUCCESS] Sistema automatico riavviato!
echo [INFO] Controlla i log per verificare il corretto funzionamento
echo.
pause
goto MENU

:CHECK_STATUS
echo.
echo [INFO] Controllo stato processi MT5...
echo.

echo === PROCESSI PYTHON ===
tasklist | findstr python.exe
if %ERRORLEVEL% NEQ 0 echo [INFO] Nessun processo Python attivo

echo.
echo === PROCESSI MT5 ===
tasklist | findstr terminal
if %ERRORLEVEL% NEQ 0 echo [INFO] Nessun processo MT5 attivo

echo.
echo === ANALISI STATO ===
tasklist | findstr python.exe >nul
set PYTHON_RUNNING=%ERRORLEVEL%

tasklist | findstr terminal64.exe >nul
set MT5_BG_RUNNING=%ERRORLEVEL%

tasklist | findstr terminal.exe >nul
set MT5_GUI_RUNNING=%ERRORLEVEL%

if %PYTHON_RUNNING% EQU 0 (
    if %MT5_BG_RUNNING% EQU 0 (
        echo [STATUS] Sistema automatico ATTIVO (Python + MT5 background)
    ) else (
        echo [STATUS] Sistema automatico PARZIALE (Solo Python)
    )
) else (
    if %MT5_GUI_RUNNING% EQU 0 (
        echo [STATUS] MT5 manuale ATTIVO (Interferenza possibile!)
        echo [WARNING] Chiudi MT5 manuale o ferma sistema automatico
    ) else (
        echo [STATUS] Tutti i sistemi FERMI
    )
)

echo.
pause
goto MENU

:EXIT
echo.
echo [INFO] Uscita dal MT5 Manual Mode Manager
echo [INFO] Ricorda: Non aprire mai MT5 manuale mentre il sistema automatico è attivo!
echo.
exit /b 0
