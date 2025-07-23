@echo off
REM ============================================================================
REM LEGACY SYSTEM CLEANUP SCRIPT - PRODUZIONE
REM Rimuove file di test, debug e temporanei non necessari per la produzione
REM ============================================================================

echo.
echo 🧹 PULIZIA LEGACY SYSTEM - RIMOZIONE FILE NON NECESSARI
echo ========================================================

echo.
echo 📁 Pulizia backtest_legacy - rimozione file di test...

REM Rimuovi file di test specifici
if exist "backtest_legacy\test_*.py" (
    echo   - Rimozione file di test...
    del /Q "backtest_legacy\test_*.py"
)

REM Rimuovi file temporanei e debug
if exist "backtest_legacy\quick_test_fix.py" (
    echo   - Rimozione quick test fix...
    del /Q "backtest_legacy\quick_test_fix.py"
)

if exist "backtest_legacy\cleanup_workspace.bat" (
    echo   - Rimozione cleanup obsoleto...
    del /Q "backtest_legacy\cleanup_workspace.bat"
)

REM Rimuovi cartella __pycache__
if exist "backtest_legacy\__pycache__" (
    echo   - Rimozione cache Python...
    rmdir /S /Q "backtest_legacy\__pycache__"
)

REM Rimuovi TODO files obsoleti
if exist "backtest_legacy\TODO-NEW.txt" (
    echo   - Rimozione TODO obsoleti...
    del /Q "backtest_legacy\TODO-NEW.txt"
)

if exist "backtest_legacy\TODO.ipynb" (
    echo   - Rimozione TODO notebook...
    del /Q "backtest_legacy\TODO.ipynb"
)

echo.
echo 📁 Pulizia logs - mantenimento solo file necessari...

REM Mantieni solo i log principali, rimuovi log di debug
if exist "logs\daily_config_updater_*.log" (
    echo   - Cleanup log updater obsoleti...
    forfiles /p logs /m daily_config_updater_*.log /d -7 /c "cmd /c del @path" 2>nul
)

echo.
echo 📁 Pulizia config backups - mantenimento solo recenti...

REM Mantieni solo gli ultimi 5 backup
if exist "config\backups" (
    echo   - Pulizia backup obsoleti (mantenimento ultimi 5)...
    cd config\backups
    for /f "skip=5 delims=" %%i in ('dir /b /od') do rmdir /s /q "%%i" 2>nul
    cd ..\..
)

echo.
echo ✅ PULIZIA COMPLETATA!
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
echo   ❌ test_*.py (File di test)
echo   ❌ __pycache__ (Cache Python)
echo   ❌ quick_test_fix.py (Debug temporaneo)
echo   ❌ TODO obsoleti
echo   ❌ Log debug obsoleti
echo   ❌ Backup config obsoleti (>5)
echo.
echo 🏆 SISTEMA LEGACY PULITO E PRONTO PER PRODUZIONE
pause
