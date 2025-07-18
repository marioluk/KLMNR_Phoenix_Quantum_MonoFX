# Quantum Trading System - Architettura Modulare

## 🏗️ Struttura del Progetto Refactorizzato

Il sistema di trading è stato ristrutturato in un'architettura modulare per migliorare:
- **Manutenibilità**: Codice organizzato in moduli specifici
- **Testabilità**: Componenti isolati e testabili singolarmente  
- **Scalabilità**: Facile aggiunta di nuove funzionalità
- **Riusabilità**: Componenti riutilizzabili in altri progetti

## 📁 Struttura Directory

```
quantum_trading_system/
├── __init__.py                 # Esportazioni principali
├── config/                     # Gestione configurazione
│   ├── __init__.py
│   └── manager.py             # ConfigManager
├── logging/                    # Sistema di logging
│   ├── __init__.py
│   └── setup.py              # Setup e configurazione log
├── engine/                     # Motore quantistico
│   ├── __init__.py
│   └── quantum_engine.py     # QuantumEngine
├── risk/                       # Gestione del rischio
│   ├── __init__.py
│   ├── manager.py            # QuantumRiskManager
│   └── drawdown_tracker.py  # DailyDrawdownTracker
├── trading/                    # Sistema principale
│   ├── __init__.py
│   └── main_system.py       # QuantumTradingSystem
├── utils/                      # Funzioni utility
│   ├── __init__.py
│   └── helpers.py           # Funzioni helper
└── metrics/                    # Metriche e reporting
    ├── __init__.py
    └── trading_metrics.py   # TradingMetrics
```

## 🔧 Come Usare il Sistema Refactorizzato

### Avvio del Sistema

```bash
# Avvia il nuovo sistema modulare
python quantum_main_refactored.py
```

### Uso Programmatico

```python
from quantum_trading_system import QuantumTradingSystem

# Inizializza il sistema
system = QuantumTradingSystem("config.json")

# Avvia il trading
system.start()
```

### Uso di Componenti Singoli

```python
from quantum_trading_system.config import ConfigManager
from quantum_trading_system.engine import QuantumEngine
from quantum_trading_system.risk import QuantumRiskManager

# Usa solo il config manager
config = ConfigManager("config.json")
symbols = config.symbols

# Usa solo il motore quantistico
engine = QuantumEngine(config)
signal, price = engine.get_signal("EURUSD")
```

## 📋 Componenti Principali

### 1. ConfigManager (`config/manager.py`)
- Carica e valida la configurazione JSON
- Gestisce parametri globali e specifici per simbolo
- Normalizza la struttura della configurazione

### 2. QuantumEngine (`engine/quantum_engine.py`)
- Elabora tick di mercato in tempo reale
- Calcola entropia e spin quantistico
- Genera segnali di trading (BUY/SELL/HOLD)
- Gestisce buffer circolari e cache

### 3. QuantumRiskManager (`risk/manager.py`)
- Calcola dimensioni delle posizioni
- Gestisce stop loss e take profit dinamici
- Controlla margini e limiti di rischio
- Integrato con DailyDrawdownTracker

### 4. QuantumTradingSystem (`trading/main_system.py`)
- Coordina tutti i componenti
- Gestisce il loop principale di trading
- Monitora posizioni e connessioni MT5
- Implementa logica di esecuzione ordini

### 5. TradingMetrics (`metrics/trading_metrics.py`)
- Traccia performance di trading
- Calcola win rate, Sharpe ratio, profit factor
- Genera report per simbolo
- Monitora drawdown e metriche chiave

## 🚀 Vantaggi dell'Architettura Modulare

### ✅ Prima (Monolitico)
- Un singolo file di 2400+ righe
- Difficile da manutenere e debuggare
- Testing complesso
- Dipendenze circolari

### ✅ Dopo (Modulare)
- 8 moduli specializzati (150-400 righe ciascuno)
- Responsabilità ben separate
- Testing unitario semplificato
- Dipendenze chiare e unidirezionali

## 🧪 Testing dei Componenti

```python
# Test del config manager
from quantum_trading_system.config import ConfigManager
config = ConfigManager("test_config.json")
assert len(config.symbols) > 0

# Test del motore quantistico
from quantum_trading_system.engine import QuantumEngine
engine = QuantumEngine(config)
engine.process_tick("EURUSD", 1.1000)
signal, price = engine.get_signal("EURUSD")
assert signal in ["BUY", "SELL", "HOLD"]

# Test del risk manager
from quantum_trading_system.risk import QuantumRiskManager
risk_mgr = QuantumRiskManager(config, engine)
size = risk_mgr.calculate_position_size("EURUSD", 1.1000, "BUY")
assert size > 0
```

## 📊 Monitoraggio e Logging

Il sistema mantiene la stessa funzionalità di logging avanzato:

- **Log rotativi** con dimensione massima configurabile
- **Livelli di log** configurabili (DEBUG, INFO, WARNING, ERROR)
- **Output console** e file simultaneo
- **Tracciamento errori** dettagliato con stack trace

## 🔄 Migrazione dal Sistema Originale

1. **Backup**: Salva il file originale come `PRO-THE5ERS-QM-PHOENIX-GITCOP-LEGACY.py`
2. **Config**: Usa la stessa configurazione JSON esistente
3. **Test**: Avvia `quantum_main_refactored.py` in modalità demo
4. **Validazione**: Confronta comportamento e performance
5. **Switch**: Sostituisci il sistema originale

## 🛠️ Personalizzazione

### Aggiungere Nuovi Simboli
```python
# Modifica config JSON
"symbols": {
    "BTCUSD": {
        "risk_management": {
            "contract_size": 0.01,
            "base_sl_pips": 500
        }
    }
}
```

### Nuove Metriche
```python
# Estendi TradingMetrics
class CustomMetrics(TradingMetrics):
    def calculate_custom_ratio(self):
        # La tua logica qui
        pass
```

### Nuovo Risk Manager
```python
# Estendi QuantumRiskManager
class ConservativeRiskManager(QuantumRiskManager):
    def calculate_position_size(self, symbol, price, signal):
        # Risk management più conservativo
        base_size = super().calculate_position_size(symbol, price, signal)
        return base_size * 0.5  # Dimezza la size
```

## 📈 Performance e Scalabilità

- **Memoria**: Ridotto uso tramite buffer circolari e cache con timeout
- **CPU**: Calcoli ottimizzati con LRU cache e numpy
- **I/O**: Logging asincrono e batch processing
- **Concorrenza**: Thread-safe con Lock appropriati

## 🔒 Sicurezza e Stabilità

- **Validazione input**: Controlli estensivi su dati MT5
- **Gestione errori**: Try-catch granulari con logging
- **Graceful shutdown**: Chiusura pulita con cleanup risorse
- **Recovery**: Auto-riconnessione MT5 e gestione fallimenti

---

**Nota**: Il sistema refactorizzato mantiene al 100% la compatibilità funzionale con il sistema originale, aggiungendo solo benefici architetturali.
