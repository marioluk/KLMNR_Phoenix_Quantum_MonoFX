@echo off
REM Esporta i segnali dal CSV in JSON per analisi esterna
cd /d %~dp0
python export_signals_to_json.py
pause
