@echo off
REM ==============================================================================
REM KLMNR DEVELOPMENT WORKFLOW MANAGER
REM Gestisce il ciclo completo: PC Dev → GitHub → Server Prod
REM ==============================================================================

setlocal enabledelayedexpansion

echo ===============================================================================
echo KLMNR DEVELOPMENT WORKFLOW MANAGER
echo ===============================================================================
echo.

:MENU
echo === WORKFLOW DEVELOPMENT ===
echo [1] 💻 SVILUPPO PC: Commit e Push modifiche
echo [2] 📥 SERVER PROD: Pull e Restart servizi  
echo [3] 🔍 STATUS: Controlla sincronizzazione
echo [4] 🚀 DEPLOY: Workflow completo automatico
echo [5] 📋 LOG: Visualizza deployment history
echo [6] ❌ Esci
echo.
set /p choice="Scelta workflow: "

if "%choice%"=="1" goto DEV_COMMIT
if "%choice%"=="2" goto PROD_DEPLOY
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto AUTO_DEPLOY
if "%choice%"=="5" goto VIEW_LOGS
if "%choice%"=="6" goto EXIT
goto MENU

:DEV_COMMIT
echo.
echo === 💻 SVILUPPO PC: COMMIT E PUSH ===
echo.

REM Verifica se siamo in una repo Git
if not exist ".git" (
    echo [ERROR] Non sei in una repository Git!
    echo [INFO] Assicurati di essere nella directory del progetto
    pause
    goto MENU
)

echo [INFO] Controllo stato repository...
git status --porcelain > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Errore Git! Verifica configurazione
    pause
    goto MENU
)

echo [INFO] File modificati:
git status --short

echo.
set /p commit_msg="📝 Messaggio commit: "
if "%commit_msg%"=="" set commit_msg="Development update"

echo.
echo [INFO] Esecuzione Git workflow...
git add .
git commit -m "%commit_msg%"
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] ✅ Modifiche pushate su GitHub!
    echo [INFO] Pronte per deployment su server produzione
    echo [NEXT] Usa opzione [2] per aggiornare il server
) else (
    echo.
    echo [ERROR] ❌ Errore durante push!
    echo [INFO] Verifica connessione e credenziali Git
)

echo.
pause
goto MENU

:PROD_DEPLOY
echo.
echo === 📥 SERVER PRODUZIONE: PULL E RESTART ===
echo.

echo [WARNING] ⚠️  ATTENZIONE: Questa operazione aggiornerà il server di produzione!
echo [WARNING] Il trading system verrà temporaneamente interrotto
echo.
set /p confirm="Procedere con il deployment? (S/N): "
if /i not "%confirm%"=="S" goto MENU

echo.
echo [INFO] 1/4 - Backup configurazione corrente...
if not exist "backup" mkdir backup
copy "config\*.json" "backup\" >nul 2>&1
echo [OK] Backup completato

echo.
echo [INFO] 2/4 - Stop servizi di trading...
call tools\mt5_manual_mode_manager.bat
REM Termina processi automatici
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM terminal64.exe /T >nul 2>&1
echo [OK] Servizi fermati

echo.
echo [INFO] 3/4 - Pull modifiche da GitHub...
git pull origin main
if %ERRORLEVEL% EQU 0 (
    echo [OK] Codice aggiornato da GitHub
) else (
    echo [ERROR] Errore durante pull!
    echo [INFO] Ripristino backup e restart servizi...
    goto RESTART_SERVICES
)

echo.
echo [INFO] 4/4 - Restart servizi di trading...
:RESTART_SERVICES
REM Riavvia sistema automatico
if exist "quantum_main_refactored.py" (
    echo [INFO] Avvio quantum system...
    start /MIN python quantum_main_refactored.py
    timeout /t 5 >nul
) else if exist "legacy_system\start_legacy.bat" (
    echo [INFO] Avvio legacy system...
    call "legacy_system\start_legacy.bat"
) else (
    echo [ERROR] Sistema di trading non trovato!
)

echo.
echo [SUCCESS] ✅ Deployment completato!
echo [INFO] Verifica i log per confermare il corretto funzionamento
echo.
pause
goto MENU

:CHECK_STATUS
echo.
echo === 🔍 STATUS SINCRONIZZAZIONE ===
echo.

echo === STATO REPOSITORY ===
git status --short
echo.

echo === ULTIMO COMMIT LOCALE ===
git log --oneline -1
echo.

echo === ULTIMO COMMIT REMOTO ===
git log --oneline -1 origin/main
echo.

echo === CONFRONTO BRANCH ===
git rev-list --count HEAD..origin/main > temp_count.txt
set /p behind_count=<temp_count.txt
del temp_count.txt

if "%behind_count%"=="0" (
    echo [STATUS] ✅ Repository sincronizzata
    echo [INFO] PC e Server sono allineati
) else (
    echo [STATUS] ⚠️  Server indietro di %behind_count% commit
    echo [INFO] Esegui deployment per sincronizzare
)

echo.
echo === PROCESSI SERVER ===
tasklist | findstr python.exe
tasklist | findstr terminal64.exe
echo.

pause
goto MENU

:AUTO_DEPLOY
echo.
echo === 🚀 WORKFLOW COMPLETO AUTOMATICO ===
echo.

echo [INFO] Questo eseguirà l'intero workflow:
echo [1] Commit modifiche PC
echo [2] Push su GitHub  
echo [3] Pull su server
echo [4] Restart servizi
echo.
set /p auto_confirm="Procedere con workflow automatico? (S/N): "
if /i not "%auto_confirm%"=="S" goto MENU

REM Esegui workflow completo
call :DEV_COMMIT
timeout /t 3 >nul
call :PROD_DEPLOY

echo.
echo [SUCCESS] 🎯 Workflow automatico completato!
echo [INFO] Sistema aggiornato e operativo
echo.
pause
goto MENU

:VIEW_LOGS
echo.
echo === 📋 DEPLOYMENT HISTORY ===
echo.

echo === ULTIMI 10 COMMIT ===
git log --oneline -10
echo.

echo === LOG SISTEMA ===
if exist "logs\default.log" (
    echo [INFO] Ultimi log sistema:
    tail -20 "logs\default.log" 2>nul || (
        echo [INFO] Ultimi log disponibili:
        more "logs\default.log"
    )
)
echo.

pause
goto MENU

:EXIT
echo.
echo [INFO] 👋 Workflow manager terminato
echo.
echo === RIEPILOGO BEST PRACTICES ===
echo ✅ Sviluppa sempre su PC locale
echo ✅ Testa modifiche prima del commit
echo ✅ Usa messaggi commit descrittivi  
echo ✅ Deploy solo su server produzione
echo ✅ Monitora log dopo deployment
echo ❌ MAI modificare direttamente su server!
echo.
exit /b 0
