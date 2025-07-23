@echo off
REM Avvio automatico MT5 e script Python
REM Modifica i percorsi qui sotto secondo la tua installazione

set MT5_PATH="C:\MT5\FivePercentOnlineMetaTrader5\terminal64.exe"
set PY_SCRIPT="phoenix_quantum_monofx_program.py"

REM Avvia MT5
start "MT5" %MT5_PATH%
REM Attendi 10 secondi per il caricamento
timeout /t 10 /nobreak
REM Avvia lo script Python

start "PythonScript" cmd /k python %PY_SCRIPT%

REM Puoi aggiungere qui altre istruzioni se necessario
