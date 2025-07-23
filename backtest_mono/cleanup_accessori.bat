@echo off
REM Script per eliminare file accessori/legacy dalla cartella backtest_mono

del autonomous_high_stakes_optimizer.py /f /q
 del autonomous_optimizer.py /f /q
 del challenge_optimizer.py /f /q
 del config_converter.py /f /q
 del daily_config_updater.py /f /q
 del daily_config_updater.bat /f /q
 del high_stakes_optimizer.py /f /q
 del integrated_backtest.py /f /q
 del integrated_launcher_complete.py /f /q
 del master_analyzer.py /f /q
 del symbol_analyzer.py /f /q
 del verify_symbols.py /f /q

echo File accessori eliminati.
pause
