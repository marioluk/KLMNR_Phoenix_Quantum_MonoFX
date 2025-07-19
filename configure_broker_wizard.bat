@echo off
echo.
echo 🔧 KLMNR PHOENIX QUANTUM - BROKER CONFIGURATION WIZARD
echo ====================================================
echo.
echo 📝 Questo script ti aiuta a personalizzare le credenziali broker
echo.
echo ⚠️  ATTENZIONE: Devi avere le tue credenziali reali pronte!
echo.
echo 📋 CREDENZIALI NECESSARIE:
echo.
echo 🏢 THE5ERS:
echo    • Server Name (es: The5ers-Demo o The5ers-Live)
echo    • Login Number 
echo    • Password
echo.
echo 🏢 FTMO:
echo    • Server Name (es: FTMO-Server o FTMO-Demo)
echo    • Login Number
echo    • Password  
echo.
echo 🏢 MYFOREXFUNDS:
echo    • Server Name (es: MyForexFunds-Demo)
echo    • Login Number
echo    • Password
echo.
echo 📂 VERIFICA ANCHE CHE ESISTANO I PERCORSI MT5:
echo    • C:\MT5\FivePercentOnlineMetaTrader5\terminal64.exe
echo    • C:\MT5\FTMOGlobalMarketsMT5Terminal\terminal64.exe  
echo    • C:\MT5\MyForexFundsMT5Terminal\terminal64.exe
echo.
echo 🚀 DOPO LA PERSONALIZZAZIONE MANUALE DEI JSON:
echo    python multi_broker_launcher.py --check-only
echo.
echo 📖 Per dettagli: leggi CONFIGURAZIONE_BROKER_GUIDE.md
echo.
pause
