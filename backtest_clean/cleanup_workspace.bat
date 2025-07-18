@echo off
echo 🧹 PULIZIA E RIORGANIZZAZIONE WORKSPACE THE5ERS
echo ================================================

cd /d "c:\GitRepos\The5ers\backtest_clean"

echo.
echo 📁 Spostamento file Markdown in docs/...
move "ANALISI_STRATEGICA_SIMBOLI.md" "docs\" >nul 2>&1
move "AUTONOMOUS_OPTIMIZER_GUIDE.md" "docs\" >nul 2>&1
move "CLEANUP_COMPLETED.md" "docs\" >nul 2>&1
move "CONFIGURAZIONE_PRODUZIONE_FINALE.md" "docs\" >nul 2>&1
move "DOCUMENTATION_INDEX.md" "docs\" >nul 2>&1
move "GUIDA_CONFIG_SELECTOR.md" "docs\" >nul 2>&1
move "HIGH_STAKES_3_LEVELS_GUIDE.md" "docs\" >nul 2>&1
move "HIGH_STAKES_CHALLENGE_GUIDE.md" "docs\" >nul 2>&1
move "INDEX_ANALISI_COMPLETE.md" "docs\" >nul 2>&1
move "INTEGRATED_SYSTEM_README.md" "docs\" >nul 2>&1
move "PARAMETRI_OTTIMIZZATI_SIMBOLI.md" "docs\" >nul 2>&1
move "README_LAUNCHER_AGGIORNATO.md" "docs\" >nul 2>&1
move "SISTEMA_INTEGRATO_COMPLETO.md" "docs\" >nul 2>&1
move "STRATEGIA_DEFINITIVA.md" "docs\" >nul 2>&1
move "SUPER_LAUNCHER_GUIDE.md" "docs\" >nul 2>&1
move "WORKFLOW_OPTIMIZATION_GUIDE.md" "docs\" >nul 2>&1
move "CLEANUP_PLAN.md" "docs\" >nul 2>&1

echo.
echo ⚙️ Spostamento file configurazione in configs/...
move "config_*.json" "configs\" >nul 2>&1

echo.
echo 📊 Spostamento risultati in results/...
move "*_RESULTS_*.json" "results\" >nul 2>&1
move "THE5ERS_COMPLETE_ANALYSIS_*.json" "results\" >nul 2>&1

echo.
echo 📦 Spostamento file legacy...
move "the5ers_launcher.py" "legacy\" >nul 2>&1
move "the5ers_launcher_fixed.py" "legacy\" >nul 2>&1
move "the5ers_simple_launcher.py" "legacy\" >nul 2>&1
move "the5ers_super_launcher.py" "legacy\" >nul 2>&1
move "the5ers_master_launcher.py" "legacy\" >nul 2>&1
move "the5ers_integrated_launcher.py" "legacy\" >nul 2>&1
move "the5ers_integrated_launcher_backup.py" "legacy\" >nul 2>&1
move "test_launcher.py" "legacy\" >nul 2>&1
move "test_integrated.bat" "legacy\" >nul 2>&1
move "config_selector.py" "legacy\" >nul 2>&1
move "custom_period_backtest.py" "legacy\" >nul 2>&1
move "comparative_backtest.py" "legacy\" >nul 2>&1
move "high_stakes_challenge_backtest.py" "legacy\" >nul 2>&1
move "the5ers_optimized_backtest.py" "legacy\" >nul 2>&1

echo.
echo ✅ PULIZIA COMPLETATA!
echo.
echo 📊 WORKSPACE ORGANIZZATO:
echo    📁 docs/     - Documentazione
echo    📁 configs/  - Configurazioni  
echo    📁 results/  - Risultati
echo    📁 legacy/   - File obsoleti
echo.
echo 🎯 FILE CORE MANTENUTI:
echo    ⭐ autonomous_high_stakes_optimizer.py
echo    ⭐ the5ers_integrated_launcher_complete.py
echo    🔧 high_stakes_optimizer.py
echo    🔧 integrated_backtest.py
echo    🔧 symbol_analyzer.py
echo    🔧 master_analyzer.py
echo    🔧 test_integration.py
echo.
pause
