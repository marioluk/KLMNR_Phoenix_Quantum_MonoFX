# 🎯 LEGACY SYSTEM - QUICK START GUIDE

## 🚀 Avvio Rapido

### Windows:
```cmd
cd legacy_system
start_legacy.bat
```

### Linux/Mac:
```bash
cd legacy_system
python start_legacy.py
```

### Avvio Diretto:
```bash
cd legacy_system
python PRO-THE5ERS-QM-PHOENIX-GITCOP.py
```

## ⚙️ Configurazione

1. **Modifica credenziali MT5** nel file `PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json`:
```json
{
  "metatrader5": {
    "login": YOUR_LOGIN,
    "password": "YOUR_PASSWORD", 
    "server": "YOUR_SERVER"
  }
}
```

2. **Verifica simboli** disponibili sul tuo broker
3. **Testa in DEMO** prima del live trading

## 📊 Monitoraggio

- **Log File**: `logs/PRO-THE5ERS-QM-PHOENIX-GITCOP-log-STEP1.log`
- **Console Output**: Messaggi in tempo reale
- **Heartbeat**: Ogni 5 minuti status sistema

## 🛑 Stop Sistema

- **Ctrl+C** nel terminale
- **Chiusura automatica** in caso di errori critici
- **Emergency stop** per drawdown > -5%

---

**🏆 SISTEMA LEGACY - PRONTO PER THE5ERS HIGH STAKES CHALLENGE**
