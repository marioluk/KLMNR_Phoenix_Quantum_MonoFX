@echo off
REM =================================================================
REM GESTIONE TASK LEGACY - Controllo task scheduler
REM =================================================================

echo.
echo 🎮 GESTIONE TASK SISTEMA LEGACY
echo =================================================================
echo.

:menu
echo Scegli un'opzione:
echo.
echo [1] 📊 Stato del task
echo [2] ▶️  Avvia task manualmente  
echo [3] ⏹️  Ferma task
echo [4] ✅ Abilita task
echo [5] ❌ Disabilita task
echo [6] 📝 Visualizza log recenti
echo [7] 🔄 Riavvia task
echo [8] 🗑️  Elimina task
echo [0] ❌ Esci
echo.

choice /c 12345678 /m "Scelta"
set choice=%errorLevel%

echo.

if %choice%==1 goto status
if %choice%==2 goto start
if %choice%==3 goto stop
if %choice%==4 goto enable
if %choice%==5 goto disable
if %choice%==6 goto logs
if %choice%==7 goto restart
if %choice%==8 goto delete

goto menu

:status
echo 📊 STATO DEL TASK:
echo =================================================================
schtasks /query /tn "KLMNR_Legacy_AutoStart" /fo LIST 2>nul
if %errorLevel% neq 0 (
    echo ❌ Task non trovato! Esegui setup_auto_start.bat per crearlo.
) else (
    echo.
    echo 📈 STATISTICHE ESECUZIONE:
    schtasks /query /tn "KLMNR_Legacy_AutoStart" /fo LIST | findstr /C:"Last Run Time" /C:"Last Result" /C:"Next Run Time"
)
goto menu_pause

:start
echo ▶️ AVVIO MANUALE DEL TASK...
schtasks /run /tn "KLMNR_Legacy_AutoStart"
if %errorLevel% equ 0 (
    echo ✅ Task avviato con successo!
    echo 💡 Controlla i log per seguire l'esecuzione
) else (
    echo ❌ Errore nell'avvio del task
)
goto menu_pause

:stop
echo ⏹️ INTERRUZIONE DEL TASK...
schtasks /end /tn "KLMNR_Legacy_AutoStart"
if %errorLevel% equ 0 (
    echo ✅ Task interrotto con successo!
) else (
    echo ❌ Errore nell'interruzione (forse non era in esecuzione)
)
goto menu_pause

:enable
echo ✅ ABILITAZIONE DEL TASK...
schtasks /change /tn "KLMNR_Legacy_AutoStart" /enable
if %errorLevel% equ 0 (
    echo ✅ Task abilitato! Si avvierà al prossimo boot.
) else (
    echo ❌ Errore nell'abilitazione del task
)
goto menu_pause

:disable
echo ❌ DISABILITAZIONE DEL TASK...
schtasks /change /tn "KLMNR_Legacy_AutoStart" /disable
if %errorLevel% equ 0 (
    echo ✅ Task disabilitato! Non si avvierà più automaticamente.
) else (
    echo ❌ Errore nella disabilitazione del task
)
goto menu_pause

:logs
echo 📝 LOG RECENTI:
echo =================================================================
if exist "logs\auto_start_%date:~6,4%%date:~3,2%%date:~0,2%.log" (
    echo 📄 Log di oggi:
    type "logs\auto_start_%date:~6,4%%date:~3,2%%date:~0,2%.log" | tail -20
) else (
    echo 📄 Log più recente:
    for /f %%f in ('dir logs\auto_start_*.log /b /o:-d 2^>nul') do (
        echo File: %%f
        type "logs\%%f" | tail -20
        goto logs_end
    )
    echo ❌ Nessun log trovato
)
:logs_end
goto menu_pause

:restart
echo 🔄 RIAVVIO DEL TASK...
schtasks /end /tn "KLMNR_Legacy_AutoStart" >nul 2>&1
timeout /t 2 >nul
schtasks /run /tn "KLMNR_Legacy_AutoStart"
if %errorLevel% equ 0 (
    echo ✅ Task riavviato con successo!
) else (
    echo ❌ Errore nel riavvio del task
)
goto menu_pause

:delete
echo.
echo ⚠️  ATTENZIONE: Stai per eliminare il task di avvio automatico!
choice /c YN /m "Sei sicuro (Y/N)"
if %errorLevel% equ 1 (
    schtasks /delete /tn "KLMNR_Legacy_AutoStart" /f
    if %errorLevel% equ 0 (
        echo ✅ Task eliminato con successo!
        echo 💡 Usa setup_auto_start.bat per ricrearlo
    ) else (
        echo ❌ Errore nell'eliminazione del task
    )
) else (
    echo ❌ Operazione annullata
)
goto menu_pause

:menu_pause
echo.
pause
echo.
goto menu
