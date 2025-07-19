# 🔧 GUIDA PERSONALIZZAZIONE CONFIGURAZIONI BROKER

## 📍 Percorsi MT5 Aggiornati:
- **The5ers**: `C:\MT5\FivePercentOnlineMetaTrader5\terminal64.exe`
- **FTMO**: `C:\MT5\FTMOGlobalMarketsMT5Terminal\terminal64.exe`  
- **MyForexFunds**: `C:\MT5\MyForexFundsMT5Terminal\terminal64.exe`

## ⚙️ CONFIGURAZIONI DA PERSONALIZZARE:

### 1. The5ers Challenge (config/broker_the5ers_challenge.json):
```json
"mt5_config": {
    "server": "The5ers-Demo",           // ← Il tuo server The5ers
    "login": 123456789,                 // ← Il tuo login account
    "password": "YourPassword123",      // ← La tua password
    "path": "C:\\MT5\\FivePercentOnlineMetaTrader5\\terminal64.exe"
}
```

### 2. FTMO Challenge (config/broker_ftmo_challenge.json):
```json
"mt5_config": {
    "server": "FTMO-Server",            // ← Il tuo server FTMO
    "login": 987654321,                 // ← Il tuo login account
    "password": "YourFTMOPassword456",  // ← La tua password
    "path": "C:\\MT5\\FTMOGlobalMarketsMT5Terminal\\terminal64.exe"
}
```

### 3. MyForexFunds Eval (config/broker_myforexfunds_eval.json):
```json
"mt5_config": {
    "server": "MyForexFunds-Demo",      // ← Il tuo server MFF
    "login": 555123456,                 // ← Il tuo login account
    "password": "YourMFFPassword789",   // ← La tua password  
    "path": "C:\\MT5\\MyForexFundsMT5Terminal\\terminal64.exe"
}
```

## 🚨 IMPORTANTE - SOSTITUISCI:
1. **Server names** con i tuoi server reali
2. **Login numbers** con i tuoi account reali
3. **Passwords** con le tue password reali
4. **Verifica i percorsi MT5** esistano sul tuo sistema

## ✅ DOPO LA PERSONALIZZAZIONE:
```bash
python multi_broker_launcher.py --check-only
```

---
*KLMNR Phoenix Quantum v6.0.0 - Multi-Broker Configuration Guide*
