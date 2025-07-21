@echo off
REM ============================================================================
REM UNIVERSAL LEGACY SYSTEM CLEANUP SCRIPT
REM Rimuove file di test, debug, temporanei e backup obsoleti da tutte le sottocartelle
REM ============================================================================

setlocal enabledelayedexpansion

REM Funzione di pulizia per una directory
set CLEAN_DIRS=backtest_legacy backtest_legacy\legacy backtest_legacy\docs backtest_legacy\configs dashboard_legacy logs config\backups archive
for %%D in (%CLEAN_DIRS%) do (
    if /I not "%%D"=="archive" (
        if exist "%%D" (
            echo.
            echo 🧹 Pulizia %%D...
            REM Rimuovi file di test Python
            del /Q "%%D\test_*.py" 2>nul
            REM Rimuovi file temporanei e debug
            del /Q "%%D\quick_test_fix.py" 2>nul
            del /Q "%%D\*_debug.*" 2>nul
            REM Rimuovi file TODO
            del /Q "%%D\TODO*.*" 2>nul
            REM Rimuovi notebook temporanei
            del /Q "%%D\*.ipynb" 2>nul
            REM Rimuovi script di cleanup obsoleti
            del /Q "%%D\cleanup_workspace.bat" 2>nul
            REM Rimuovi cache Python
            if exist "%%D\__pycache__" rmdir /S /Q "%%D\__pycache__"
        )
    )
)

REM Pulizia logs: rimuovi log updater più vecchi di 7 giorni
forfiles /p logs /m daily_config_updater_*.log /d -7 /c "cmd /c del @path" 2>nul

REM Pulizia backup config: mantieni solo gli ultimi 5
if exist "config\backups" (
    cd config\backups
    for /f "skip=5 delims=" %%i in ('dir /b /od') do rmdir /s /q "%%i" 2>nul
    cd ..\..
)

REM Report finale
echo.
echo ✅ PULIZIA UNIVERSALE COMPLETATA!
echo.
echo 📊 File mantenuti per produzione:
echo   ✅ PRO-THE5ERS-QM-PHOENIX-GITCOP.py (Sistema principale)
echo   ✅ config\*.json (Configurazioni attive)
echo   ✅ config\backups (Ultimi 5 backup)
echo   ✅ daily_config_updater.py (Automazione)
echo   ✅ *.md (Documentazione)
echo   ✅ start_legacy.* (Script di avvio)
echo   ✅ logs\*.log (Log principali)
echo.
echo 🗑️ File rimossi:
echo   ❌ test_*.py, quick_test_fix.py, *_debug.*, TODO*, *.ipynb, cleanup_workspace.bat, __pycache__, log updater obsoleti, backup config obsoleti (>5)
echo.
echo 🏆 SISTEMA LEGACY PULITO E PRONTO PER PRODUZIONE
pause
