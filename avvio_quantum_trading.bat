@echo off
REM Avvio automatico MT5, script Python, backend Flask e frontend React
REM Modifica i percorsi qui sotto secondo la tua installazione

set MT5_PATH="C:\MT5\FivePercentOnlineMetaTrader5\terminal64.exe"
set PY_SCRIPT="phoenix_quantum_monofx_program.py"
set BACKEND_PATH="dashboard_mono\api_live_status.py"
set FRONTEND_PATH="dashboard_mono\react"

REM Avvia MT5
start "MT5" %MT5_PATH%
REM Attendi 10 secondi per il caricamento di MT5
timeout /t 10 /nobreak

REM Avvia backend Flask
start "BackendFlask" cmd /k python %BACKEND_PATH%
REM Attendi 5 secondi per sicurezza
timeout /t 5 /nobreak

REM Avvia lo script Python principale
start "PythonScript" cmd /k python %PY_SCRIPT%
REM Attendi 3 secondi per sicurezza
timeout /t 3 /nobreak


REM Avvia frontend React (corretto: usa call e virgolette)
start "FrontendReact" cmd /k "cd /d %~dp0%FRONTEND_PATH% && call npm start"

REM Attendi 2 secondi e apri il browser sulla dashboard
timeout /t 2 /nobreak
start "" http://localhost:5173/

REM Fine avvio automatico
