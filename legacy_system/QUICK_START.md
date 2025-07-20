# 🎯 LEGACY SYSTEM - QUICK START GUIDE [PRODUZIONE ATTIVA]

## ⚠️ SISTEMA IN PRODUZIONE - LUGLIO 2025

**IMPORTANTE:** Questo sistema è attualmente operativo in produzione su The5ers High Stakes Challenge. 
Non modificare senza test approfonditi su demo account.

## 🚀 Avvio Rapido Sistema Produzione

### Windows (Metodo Raccomandato):
```cmd
cd legacy_system
start_legacy.bat
```

### Avvio Diretto Produzione:
```bash
cd legacy_system
python PRO-THE5ERS-QM-PHOENIX-GITCOP.py
```

### Linux/Mac:
```bash
cd legacy_system
python start_legacy.py
```

## ⚙️ Configurazione Produzione Attiva

### 🔥 CONFIGURAZIONE AUTOMATICA ATTIVA:
Il sistema utilizza ora la configurazione ottimizzata automaticamente:
```json
CONFIG_FILE = "config/config_autonomous_high_stakes_conservative_production_ready.json"
```

### Daily Config Updater:
- ✅ **Attivo**: Sistema di aggiornamento configurazioni daily alle 06:00
- ✅ **Backup automatico**: Configurazioni precedenti salvate
- ✅ **Validazione**: Controlli automatici post-aggiornamento
- ✅ **Ottimizzazione autonoma**: Selezione simboli e parametri automatica

### Configurazione MT5 (se necessario modificare):
```json
{
  "metatrader5": {
    "login": YOUR_LOGIN,
    "password": "YOUR_PASSWORD", 
    "server": "YOUR_SERVER"
  }
}
```

## 📊 Monitoraggio Sistema Produzione

### Status Attivo:
- **Sistema**: ✅ PRODUZIONE ATTIVA su The5ers High Stakes Challenge
- **Configurazione**: ✅ Auto-ottimizzata daily (4 simboli, risk 0.5%)
- **Log File**: `logs/PRO-THE5ERS-QM-PHOENIX-GITCOP-log-STEP1.log`
- **Console Output**: Messaggi in tempo reale con heartbeat ogni 5 minuti
- **Automazione**: Daily config update alle 06:00

### Metriche Sistema:
- **Risk Management**: Ultra-conservativo (0.5% per trade)
- **Simboli Attivi**: 4 strumenti ottimizzati automaticamente
- **Cooldown**: 1800s position, 900s signal
- **Drawdown Protection**: -2% soft limit, -5% hard limit

## 🛑 Stop Sistema

- **Ctrl+C** nel terminale per stop graceful
- **Emergency stop automatico** per drawdown > -5%
- **Chiusura automatica** in caso di errori critici MT5

## 🔄 Aggiornamento Configurazioni

### Sistema Automatico Attivo:
```bash
# Eseguito automaticamente alle 06:00 daily
python daily_config_updater.py --days 30
```

### Aggiornamento Manuale (se necessario):
```bash
cd backtest_legacy
python daily_config_updater.py --days 30
```

---

**🏆 SISTEMA LEGACY - PRODUZIONE ATTIVA THE5ERS HIGH STAKES CHALLENGE - LUGLIO 2025**
