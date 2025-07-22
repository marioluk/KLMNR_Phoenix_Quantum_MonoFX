@echo off
REM Avvio automatico MT5 e script Python
REM Modifica i percorsi qui sotto secondo la tua installazione

set MT5_PATH="C:\Program Files\MetaTrader 5\terminal64.exe"
set PY_SCRIPT="C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system\PRO-THE5ERS-QM-PHOENIX-GITCOP.py"

REM Avvia MT5
start "MT5" %MT5_PATH%
REM Attendi 10 secondi per il caricamento
timeout /t 10 /nobreak
REM Avvia lo script Python
start "PythonScript" python %PY_SCRIPT%

REM Puoi aggiungere qui altre istruzioni se necessario
