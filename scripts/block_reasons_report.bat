@echo off
REM Lancia report motivi di blocco segnali (orario e daily)
cd /d %~dp0
cd ..

REM Report orario
python scripts\block_reasons_report.py --period hourly

REM Report daily
python scripts\block_reasons_report.py --period daily

pause
