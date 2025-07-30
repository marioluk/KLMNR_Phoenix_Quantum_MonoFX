@echo off
REM Archivio e pulizia log segnali e report motivi blocco
cd /d %~dp0
cd ..
set LOGDIR=logs
set DATETIME=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATETIME=%DATETIME: =0%

REM Archivia signals_tick_log.csv
if exist %LOGDIR%\signals_tick_log.csv (
    move %LOGDIR%\signals_tick_log.csv %LOGDIR%\signals_tick_log_%DATETIME%.csv
)

REM Archivia trade_decision_report.csv
if exist %LOGDIR%\trade_decision_report.csv (
    move %LOGDIR%\trade_decision_report.csv %LOGDIR%\trade_decision_report_%DATETIME%.csv
)

REM Archivia block_reasons_report_*.csv e *.json
for %%F in (%LOGDIR%\block_reasons_report_*.csv) do (
    if exist "%%F" move "%%F" "%%~dpnF_%DATETIME%%%~xF"
)
for %%F in (%LOGDIR%\block_reasons_report_*.json) do (
    if exist "%%F" move "%%F" "%%~dpnF_%DATETIME%%%~xF"
)

echo Pulizia e archiviazione completata.
pause
