@echo off
echo ================================================================================
echo 🚀 THE5ERS DASHBOARD - ACCESSO REMOTO (Mono SYSTEM)
echo ================================================================================
echo 🌐 Dashboard accessibile da altri computer
echo 📱 Usa: http://[TUO_IP]:5000 (es: http://192.168.1.21:5000)
echo 🔒 Assicurati che il firewall Windows permetta la porta 5000
echo 📁 Configurazione auto-detect dal sistema Mono
echo ================================================================================
echo.

pause
REM Trova l'IP locale
echo 🔍 Il tuo IP locale è:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo    http://%%b:5000
    )
)
echo.

REM Controlla se esiste il file di config nella cartella corretta (root progetto)
if not exist "..\config\config_autonomous_challenge_production_ready.json" (
    echo ERROR: Config file not found!
    echo Please ensure ..\config\config_autonomous_challenge_production_ready.json exists
    pause
    exit /b 1
)

echo 🔄 Avvio dashboard con accesso remoto...
python dashboard_broker.py
pause
