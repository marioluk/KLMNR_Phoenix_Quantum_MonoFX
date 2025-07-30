@echo off
REM Script batch per analisi incrociata segnali/trade/motivi blocco
cd /d %~dp0
python analyze_signals_vs_trades.py
pause
