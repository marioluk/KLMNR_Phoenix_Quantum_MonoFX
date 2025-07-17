@echo off
echo ================================================================================
echo 🚀 THE5ERS DASHBOARD - ACCESSO REMOTO
echo ================================================================================
echo 🌐 Dashboard accessibile da altri computer
echo 📱 Usa: http://[TUO_IP]:5000 (es: http://192.168.1.21:5000)
echo 🔒 Assicurati che il firewall Windows permetta la porta 5000
echo ================================================================================
echo.

REM Trova l'IP locale
echo 🔍 Il tuo IP locale è:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo    http://%%b:5000
    )
)
echo.

echo 🔄 Avvio dashboard con accesso remoto...
python dashboard_the5ers.py PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json

pause
