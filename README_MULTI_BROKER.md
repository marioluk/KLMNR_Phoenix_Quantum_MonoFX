# Multi-Broker Quantum Trading System

Sistema di trading quantistico avanzato con supporto multi-broker per **The5ers**, **FTMO**, **MyForexFunds** e altri prop trading firms.

## 🚀 Caratteristiche Principali

### Multi-Broker Support
- ✅ **The5ers Challenge/Funded Accounts**
- ✅ **FTMO Challenge/Funded Accounts** 
- ✅ **MyForexFunds Evaluation/Funded Accounts**
- ✅ **Supporto per broker personalizzati**
- ✅ **Gestione multiple installazioni MT5**

### Quantum Trading Engine
- 🧠 **Algoritmi quantistici avanzati**
- 📊 **Neural networks multi-layer**
- 🔄 **Analisi multi-timeframe**
- 📈 **Sentiment analysis integrata**
- ⚡ **Scalping e swing trading**

### Risk Management Avanzato
- 🛡️ **Drawdown protection per broker**
- 📊 **Risk pooling cross-broker**
- 🎯 **Position sizing dinamico**
- ⚠️ **Emergency stop-loss globale**
- 📈 **Compliance challenge rules**

### Orchestrazione Intelligente
- 🔄 **Load balancing automatico**
- 📡 **Failover e ridondanza**
- 🎯 **Best execution routing**
- 📊 **Monitoraggio real-time**
- 🔧 **Auto-reconnection**

## 📁 Struttura del Progetto

```
quantum_trading_system/
├── brokers/              # 🏢 Gestione multi-broker
│   ├── connection.py     # Connessioni MT5 individuali
│   ├── manager.py        # Orchestratore centrale
│   └── config_loader.py  # Caricamento configurazioni
├── trading/              # 📈 Sistema di trading
│   ├── main_system.py    # Sistema singolo broker
│   └── multi_system.py   # Sistema multi-broker
├── engine/               # ⚡ Motore quantistico
├── risk/                 # 🛡️ Risk management
├── config/               # ⚙️ Gestione configurazioni
└── ...

config/                   # 📝 Configurazioni
├── multi_broker_master_config.json
├── broker_the5ers_challenge.json
├── broker_ftmo_challenge.json
└── broker_myforexfunds_eval.json
```

## 🚀 Quick Start

### 1. Installazione

```bash
# Clona il repository
git clone <repo-url>
cd The5ers

# Installa dipendenze
pip install MetaTrader5 numpy pandas scikit-learn

# Verifica installazioni MT5
python multi_broker_launcher.py --check-only
```

### 2. Configurazione

#### A. Configura i tuoi account broker
Modifica i file in `config/`:

**The5ers (`broker_the5ers_challenge.json`):**
```json
{
  "broker_name": "THE5ERS",
  "mt5_config": {
    "server": "The5ers-Demo",
    "login": 123456789,
    "password": "YourPassword123",
    "path": "C:\\Program Files\\MetaTrader 5 The5ers\\terminal64.exe"
  },
  "risk_management": {
    "max_daily_loss": 500.0,
    "max_total_loss": 2500.0,
    "profit_target": 5000.0
  }
}
```

**FTMO (`broker_ftmo_challenge.json`):**
```json
{
  "broker_name": "FTMO", 
  "mt5_config": {
    "server": "FTMO-Server",
    "login": 987654321,
    "password": "YourFTMOPassword456"
  }
}
```

#### B. Personalizza il master config
Modifica `config/multi_broker_master_config.json`:

```json
{
  "multi_broker_config": {
    "broker_configs": [
      "config/broker_the5ers_challenge.json",
      "config/broker_ftmo_challenge.json"
    ],
    "global_settings": {
      "max_total_positions": 10,
      "max_positions_per_broker": 5
    }
  }
}
```

### 3. Avvio Sistema

#### Opzione A: Script Windows (Raccomandato)
```bash
start_multi_broker.bat
```

#### Opzione B: Python diretto
```bash
# Tutti i broker
python multi_broker_launcher.py

# Solo The5ers
python multi_broker_launcher.py --broker THE5ERS

# Solo FTMO  
python multi_broker_launcher.py --broker FTMO

# Modalità debug
python multi_broker_launcher.py --debug

# Test senza trading
python multi_broker_launcher.py --dry-run
```

## 📊 Monitoraggio e Controllo

### Dashboard Real-time
```bash
# Avvia dashboard web
cd dashboard
python dashboard_the5ers.py
```

### Log Files
```
logs/
├── multi_broker_system.log      # Log principale
├── the5ers_broker.log           # Log The5ers
├── ftmo_broker.log              # Log FTMO
└── trading/
    ├── trades_the5ers.log
    └── trades_ftmo.log
```

### Status Report
Il sistema genera report automatici ogni 60 secondi con:
- 💰 Balance e equity per broker
- 📊 P/L aggregato
- 🔄 Stato connessioni
- 📈 Performance metrics
- ⚠️ Alert e warnings

## 🎯 Strategie di Trading

### Routing Intelligente
Il sistema automaticamente:
1. **Analizza spread** di tutti i broker
2. **Seleziona migliore esecuzione**
3. **Bilancia il carico** tra broker
4. **Gestisce correlazioni** cross-broker

### Risk Management Coordinato
- **Shared Risk Pool**: Rischio condiviso tra broker
- **Cross-Broker Hedging**: Hedging automatico
- **Correlation Control**: Controllo correlazioni
- **Emergency Stops**: Stop-loss di emergenza

### Algoritmi Quantum per Broker
- **The5ers**: Scalping aggressivo
- **FTMO**: Swing trading conservativo  
- **MyForexFunds**: Momentum balanced
- **Custom**: Configurazione personalizzata

## ⚙️ Configurazione Avanzata

### Symbol Routing
```json
"symbol_routing": {
  "EURUSD": ["THE5ERS", "FTMO", "MYFOREXFUNDS"],
  "XAUUSD": ["THE5ERS", "FTMO"],
  "BTCUSD": ["THE5ERS"]
}
```

### Execution Strategy
```json
"execution_strategy": {
  "best_spread_routing": true,
  "latency_optimization": true,
  "broker_selection_criteria": [
    "spread", "latency", "reliability"
  ]
}
```

### Risk Coordination
```json
"risk_coordination": {
  "shared_risk_pool": true,
  "risk_distribution": {
    "THE5ERS": 0.5,
    "FTMO": 0.3, 
    "MYFOREXFUNDS": 0.2
  }
}
```

## 🔧 Troubleshooting

### Problemi Comuni

#### 1. Connessione MT5 fallita
```bash
# Verifica installazioni
python multi_broker_launcher.py --check-only

# Controlla credenziali nei config files
# Assicurati che MT5 sia chiuso prima dell'avvio
```

#### 2. Errore configurazione
```bash
# Valida JSON
python -m json.tool config/broker_the5ers_challenge.json

# Controlla path nei log
tail -f logs/multi_broker_system.log
```

#### 3. Performance lenta
```bash
# Riduci numero broker attivi
python multi_broker_launcher.py --broker THE5ERS

# Ottimizza configurazione quantum
# Riduci "quantum_strength" e "neural_network_depth"
```

### Log Analysis
```bash
# Monitor logs in tempo reale
Get-Content logs/multi_broker_system.log -Wait

# Cerca errori
findstr "ERROR" logs/*.log

# Analizza performance  
findstr "TRADE" logs/trading/*.log
```

## 🚀 Estensioni e Customizzazioni

### Aggiungere Nuovo Broker
1. **Crea configurazione** in `config/broker_newbroker.json`
2. **Aggiungi al master config** nel array `broker_configs`
3. **Configura MT5 path** specifico
4. **Testa connessione**

### Custom Trading Algorithm
```python
# In quantum_config per broker specifico
"quantum_config": {
  "algorithm_mode": "custom_strategy",
  "custom_parameters": {
    "entry_threshold": 0.8,
    "exit_threshold": 0.3,
    "timeframe_mix": ["M5", "H1", "H4"]
  }
}
```

### Integration con Altri Sistemi
- **REST API** per controllo esterno
- **WebSocket** per real-time data
- **Database** per storage storico
- **Telegram/Discord** per notifiche

## 📈 Performance e Monitoring

### Metriche Chiave
- **Win Rate** per broker e globale
- **Average Profit/Loss** per simbolo
- **Drawdown Maximum** e recovery time
- **Execution Latency** per broker
- **Spread Comparison** real-time

### Alert System
- 🔴 **Critical**: Connessione broker persa
- 🟡 **Warning**: Drawdown vicino al limite
- 🟢 **Info**: Trade eseguito con successo
- 🔵 **Debug**: Dettagli algoritmo quantum

## 🛡️ Sicurezza e Compliance

### Challenge Rules Compliance
- ✅ **Maximum Daily Loss** rispettato
- ✅ **Maximum Total Loss** rispettato  
- ✅ **Minimum Trading Days** tracciato
- ✅ **Consistency Rules** applicate
- ✅ **News Trading Restrictions** verificate

### Data Protection
- 🔒 **Credenziali cifrate** in configurazione
- 🛡️ **Logging sicuro** senza password
- 📊 **Audit trail** completo
- 🔄 **Backup automatico** configurazioni

## 📞 Supporto

### Documentazione
- 📚 [API Reference](docs/api_reference.md)
- 🎯 [Trading Strategies](docs/strategies.md) 
- 🔧 [Configuration Guide](docs/configuration.md)
- 🚀 [Deployment Guide](docs/deployment.md)

### Community
- 💬 Discord: [Quantum Traders](https://discord.gg/quantum-traders)
- 📧 Email: support@quantumtrading.io
- 🐛 Issues: [GitHub Issues](https://github.com/quantum-trading/issues)

---

## 🎯 Getting Started Checklist

- [ ] ✅ **Python 3.8+ installato**
- [ ] ✅ **MetaTrader5 package installato**
- [ ] ✅ **Almeno una installazione MT5**
- [ ] ✅ **Account broker configurato (The5ers/FTMO/MFF)**
- [ ] ✅ **File configurazione personalizzati**
- [ ] ✅ **Test connessione superato**
- [ ] 🚀 **Sistema avviato con successo**

**Happy Trading! 📈🚀**
