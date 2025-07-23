@echo off
echo.
echo 🚀 KLMNR PHOENIX QUANTUM - MIGRATION SCRIPT
echo ==========================================
echo.
echo 📦 Questo script migra KLMNR_Phoenix_Quantum su un nuovo PC
echo.
echo 🎯 PASSI ESEGUITI:
echo    1. Crea directory C:\KLMNR_Projects
echo    2. Clone repository da GitHub  
echo    3. Verifica struttura
echo    4. Test sistema
echo.
echo ⚠️  PREREQUISITI:
echo    • Git installato
echo    • Python installato
echo    • Connessione internet
echo.
echo 🔄 Inizio migrazione...
echo.

REM Crea directory principale
echo 📁 Creazione C:\KLMNR_Projects...
mkdir "C:\KLMNR_Projects" 2>nul
cd /d "C:\KLMNR_Projects"

echo.
echo 📥 Clone repository GitHub...
git clone https://github.com/marioluk/KLMNR_Phoenix_Quantum.git KLMNR_Phoenix_Quantum

echo.
echo 📂 Accesso directory progetto...
cd "KLMNR_Phoenix_Quantum"

echo.
echo 🔍 Verifica struttura...
dir /b

echo.
echo 🧪 Test sistema...
set PYTHONPATH=%CD%;%PYTHONPATH%
python multi_broker_launcher.py --check-only

echo.
echo ✅ MIGRAZIONE COMPLETATA!
echo.
echo 📋 PROSSIMI PASSI:
echo    1. Personalizza credenziali in config\broker_*.json
echo    2. Aggiorna percorsi MT5 se necessario
echo    3. Testa connessioni broker
echo.
echo 📖 Leggi: CONFIGURAZIONE_BROKER_GUIDE.md
echo.
pause
