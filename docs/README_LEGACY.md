# 📦 STRUTTURA DEL SISTEMA LEGACY E MANUTENZIONE


## Struttura consigliata

```
legacy_system/
│
├── config/                # Solo file di configurazione attivi e centralizzati
├── dashboard_mono/      # Dashboard e tool di visualizzazione
├── backtest_mono/       # Script e tool di backtest
│   ├── legacy/            # Script legacy non più usati, da archiviare o eliminare
│   ├── docs/              # Documentazione tecnica e guide
│   └── configs/           # Config di test/backtest (se necessario, altrimenti centralizza in config/)
├── logs/                  # Solo log attuali, archivia o elimina quelli vecchi
├── scripts/               # Batch, PowerShell, automazione (unifica qui tutti gli script di avvio/stop)
├── README_LEGACY.md       # Un solo README chiaro per tutto il sistema legacy
├── archive/               # Tutto ciò che è obsoleto, non più usato, ma che vuoi conservare per storico
└── ... altri file/documenti legacy
```


## Pulizia automatica

Utilizza lo script `scripts/cleanup_universal.bat` per:
- Rimuovere file di test, debug, temporanei, notebook, cache Python, script di cleanup obsoleti e backup vecchi
- Mantenere solo i file essenziali per la produzione
- La variabile `CLEAN_DIRS` nello script può essere personalizzata per aggiungere/rimuovere directory

### Personalizzazione avanzata
- Se vuoi che una directory (es. `archive`) non venga mai pulita, basta rimuoverla da `CLEAN_DIRS` oppure aggiungere un controllo:
  ```bat
  if "%%D"=="archive" goto :SKIP_ARCHIVE
  ...comandi di pulizia...
  :SKIP_ARCHIVE
  ```
- Puoi aggiungere pattern specifici per ogni sottocartella, oppure escludere file che vuoi sempre conservare.
- Aggiorna lo script e questa documentazione ogni volta che modifichi la struttura o le regole di pulizia.

## Best practice
- Centralizza tutte le configurazioni legacy in `config/`
- Mantieni la dashboard, i backtest e i log separati
- Usa la cartella `scripts/` per tutti gli script di automazione e manutenzione
- Aggiorna questa documentazione se modifichi la struttura
# 🎯 QUANTUM TRADING SYSTEM - LEGACY ENTERPRISE VERSION
## Sistema Enterprise con Automazione Completa - STATO: PRODUZIONE 24/7 ✅

---

## 📋 **OVERVIEW SISTEMA ENTERPRISE - AUTOMAZIONE 2025**

🏆 **SISTEMA ENTERPRISE-GRADE IN PRODUZIONE** - Sistema legacy completamente automatizzato con infrastruttura enterprise Windows, auto-start, daily updates e monitoring multi-dispositivo.

### **� IMPLEMENTAZIONI ENTERPRISE COMPLETATE (20 LUGLIO 2025):**
- ✅ **Auto-Start Infrastructure** - Task Scheduler + PowerShell automation 
- ✅ **Daily Autonomous Updates** - Config optimization alle 06:00
- ✅ **MT5 Headless Integration** - API trading background 24/7
- ✅ **Multi-Device Architecture** - Server + monitoring devices
- ✅ **Professional Workflow** - PC Dev → GitHub → Server pipeline
- ✅ **Safety Tools** - MT5 Manual Mode Manager
- ✅ **Enterprise Logging** - Comprehensive monitoring system
- ✅ **Git Version Control** - Professional development lifecycle

---

## 🤖 **AUTOMAZIONE ENTERPRISE - INFRASTRUCTURE**

### **🔧 AUTO-START AL BOOT (Task Scheduler):**
```powershell
# Task configurati automaticamente:
- KLMNR_Legacy_System_AutoStart (06:05 al boot)
- KLMNR_Daily_Config_Updater (06:00 daily)

# Scripts PowerShell enterprise:
- AutoStartLegacy.ps1 -> Sistema trading principale
- AutoStartDailyUpdater.ps1 -> Daily optimization
```

### **� DAILY CONFIG UPDATER - AUTONOMO:**
```bash
# Automazione quotidiana alle 06:00:
✅ Analisi performance ultimi 30 giorni
✅ Ottimizzazione parametri intelligente  
✅ Backup configurazioni automatico
✅ Score-based selection (Attuale: 748.00 CONSERVATIVE)
✅ Validazione post-update completa
✅ Log dettagliato per troubleshooting
```

### **🖥️ MT5 HEADLESS INTEGRATION:**
```bash
# MT5 Background API (senza GUI):
✅ Trading via Python API MetaTrader5
✅ Nessuna interferenza GUI
✅ Processi: terminal64.exe (background) + python.exe
✅ Multi-device monitoring (laptop/smartphone safe)
✅ Connection: FivePercentOnline-Real server
```

### **Prerequisiti Produzione:**
```bash
pip install MetaTrader5 numpy
```

### **Avvio Sistema Legacy (Produzione):**
```bash
cd c:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system
python phoenix_quantum_monofx_program.py
```

### **File di Configurazione Attivi:**
 🔄 `config/config_autonomous_high_stakes_production_ready.json` - Configurazione legacy aggiornata

---

## 🏗️ **ARCHITETTURA MONOLITICA**

Il sistema è strutturato in **6 classi principali** all'interno del singolo file:
config_manager = ConfigManager("config-STEP1.json")
```
python -c "import json; print('OK' if json.load(open('config/config_autonomous_high_stakes_production_ready.json')) else 'ERROR')"
### **2. QuantumEngine**
Motore di calcolo quantistico per analisi tick e generazione segnali
```python
engine = QuantumEngine(config_manager)
signal, price = engine.get_signal("EURUSD")
```

### **3. DailyDrawdownTracker**
Monitoraggio protezioni challenge (soft -2%, hard -5%)
```python
tracker = DailyDrawdownTracker(initial_equity, config)
soft_hit, hard_hit = tracker.check_limits(current_equity)
```

### **4. QuantumRiskManager**
Calcolo posizioni, SL/TP dinamici e controllo margine
```python
risk_manager = QuantumRiskManager(config, engine)
size = risk_manager.calculate_position_size("EURUSD", price, "BUY")
```

### **5. TradingMetrics**
Raccolta e analisi metriche di performance
```python
metrics = TradingMetrics()
metrics.update_trade("EURUSD", profit)
```

### **6. QuantumTradingSystem**
Coordinatore principale e loop di trading
```python
system = QuantumTradingSystem("config-STEP1.json")
system.start()
```

---

## 🔬 **ALGORITMI QUANTISTICI IMPLEMENTATI**

### **Calcolo Entropia Shannon Normalizzata:**
```python
@staticmethod
@lru_cache(maxsize=1000)
def calculate_entropy(deltas: Tuple[float]) -> float:
    # Normalizzazione: P(i) = |Δᵢ| / Σ|Δⱼ|
    prob = abs_deltas / sum_abs_deltas
    # Shannon entropy: H = -Σ P(i) * log(P(i))
    entropy = -np.sum(valid_probs * np.log(valid_probs + 1e-10))
    # Normalizzazione [0,1]: H_norm = H / log(n)
    return entropy / np.log(len(valid_probs) + 1e-10)
```

### **Calcolo Spin Quantistico:**
```python
def calculate_spin(self, ticks: List[Dict]) -> Tuple[float, float]:
    # Spin bilanciato: S = (N⁺ - N⁻) / N_total
    raw_spin = (positive - negative) / total
    # Confidenza: C = |N⁺ - N⁻| / N_total * √N_total
    confidence = abs(positive - negative) / total * sqrt(total)
    return raw_spin, confidence
```

### **Volatilità Quantistica Adattiva:**
```python
def calculate_quantum_volatility(self, symbol: str, window: int = 50) -> float:
    # Combina entropia e spin per volatilità quantistica
    volatility = 1 + abs(spin) * entropy
    return volatility
```

---

## ⚙️ **PARAMETRI DI CONFIGURAZIONE**

### **Parametri Quantistici (ottimizzati per debug):**
```json
{
  "quantum_params": {
    "buffer_size": 100,           // Ridotto da 250 per debug
    "spin_window": 20,            // Ridotto da 50 per debug
    "min_spin_samples": 10,       // Ridotto da 20 per debug
    "spin_threshold": 0.25,
    "signal_cooldown": 300,       // 5 minuti
    "entropy_thresholds": {
      "buy_signal": 0.58,
      "sell_signal": 0.42
    }
  }
}
```

### **Parametri di Rischio (ultra-conservativi):**
```json
{
  "risk_parameters": {
    "position_cooldown": 1800,    // 30 minuti tra posizioni
    "max_daily_trades": 5,
    "max_positions": 1,
    "risk_percent": 0.0015,       // 0.15% per trade
    "profit_multiplier": 2.2,
    "max_position_hours": 6
  }
}
```

### **Protezioni challenge:**
```json
{
  "challenge_specific": {
    "step1_target": 8,            // 8% target profitto
    "max_daily_loss_percent": 5,  // 5% perdita massima giornaliera
    "max_total_loss_percent": 10, // 10% perdita massima totale
    "drawdown_protection": {
      "soft_limit": 0.02,         // 2% warning
      "hard_limit": 0.05          // 5% stop immediato
    }
  }
}
```

---

## 📊 **MONITORAGGIO E LOGGING**

### **Log File:**
- Posizione: `logs/log_autonomous_high_stakes_conservative_production_ready.log`
- Rotazione: 50MB, 7 backup
- Livello: INFO con debug dettagliato

### **Heartbeat Sistema:**
```
HEARTBEAT:
EURUSD: Bid=1.09123 | Ask=1.09125 | Spread=0.2p | Buffer=45 | E=0.67 | S=0.12 | C=0.85 | V=1.23
GBPUSD: Bid=1.26789 | Ask=1.26791 | Spread=0.2p | Buffer=42 | E=0.58 | S=-0.08 | C=0.72 | V=1.15
Sistema attivo - Posizioni: 0/1
```

### **Metriche Trading:**
```python
# Report automatico performance
📊 PERFORMANCE REPORT:
   Trades: 24
   Win Rate: 67.5%
   Avg Profit: $12.45
   Max Drawdown: -1.2%
   Sharpe Ratio: 1.85
   Profit Factor: 2.34
```

---

## 🛡️ **SICUREZZA E PROTEZIONI**

### **Protezioni Multiple:**
1. **Cooldown Posizioni**: 30 minuti tra aperture sullo stesso simbolo
2. **Cooldown Segnali**: 5 minuti tra segnali consecutivi
3. **Spread Control**: Blocco automatico se spread > soglia
4. **Margin Control**: Usa max 80% del margine libero
5. **Size Limits**: Massimo 0.1 lotti per posizione
6. **Drawdown Protection**: Stop automatico a -5%
7. **Trading Hours**: Rispetta orari configurati per simbolo
8. **Emergency Stop**: Chiusura automatica weekend e disconnessioni

### **Validazioni Input:**
- Verifica simboli disponibili in MT5
- Controllo dati tick aggiornati (<60s)
- Validazione prezzi e spread
- Controllo configurazione JSON

---

## 🔧 **TROUBLESHOOTING**

### **Problemi Comuni:**

**1. Errore Connessione MT5:**
```
❌ Errore: Inizializzazione MT5 fallita
✅ Soluzione: Verifica path, login, password nel config JSON
```

**2. Nessun Segnale Generato:**
```
❌ Buffer insufficiente o cooldown attivo
✅ Aspetta accumulo dati (min 10 tick) o fine cooldown
```

**3. Trade Rifiutati:**
```
❌ Spread troppo alto o margine insufficiente
✅ Controlla impostazioni broker e capitale disponibile
```

**4. Errori di Configurazione:**
```bash
# Valida la sintassi del config JSON
python -c "import json; print('OK' if json.load(open('PRO-CHALLENGE-QM-PHOENIX-GITCOP-config-STEP1.json')) else 'ERROR')"
```

---

## 📈 **PERFORMANCE ATTESE**

### **Obiettivi Challenge Step 1:**
- **Target**: +8% in 30 giorni
- **Max Daily Loss**: -5%
- **Max Total Loss**: -10%
- **Win Rate Atteso**: 60-70%
- **Risk/Reward**: 1:2.2
- **Max Drawdown**: <-3%

### **Simboli Ottimizzati:**
- **EURUSD**: Parametri conservativi, alta liquidità
- **GBPUSD**: Gestione volatilità, spread premium
- **USDJPY**: Specializzato sessione asiatica
- **XAUUSD**: Risk ridotto, spread aumentati
- **NAS100**: High volatility, parametri ristretti

---

## � **BACKTEST LEGACY**

Il sistema legacy ha i suoi strumenti di backtesting dedicati in:
```bash
cd backtest_mono/
```

**Caratteristiche Backtest Legacy:**
- ✅ Compatibile con sistema monolitico
- ✅ Scripts di analisi performance
- ✅ Tools di ottimizzazione parametri
- ✅ Report storici challenge
- ✅ Configurazioni pre-validate

**Differenza dal Sistema Moderno:**
- Legacy: `backtest_mono/` (questo sistema)
- Moderno: `../backtest/` (sistema modulare)

---

## �🚨 **IMPORTANTE - SISTEMA LEGACY**

⚠️ **Questo è il SISTEMA LEGACY MONOLITICO** - Completamente funzionante e testato per produzione.

🔄 **Sistema Modulare in Sviluppo** - La nuova versione modulare è nella cartella `quantum_trading_system/`

📅 **Cronologia:**
- **Legacy**: Sistema monolitico stabile (questo file)
- **Refactored**: Sistema modulare in testing (cartella `quantum_trading_system/`)
- **Target**: Migrazione graduale al sistema modulare

---

## 🏆 **STATUS ATTUALE**

✅ **Sistema Completo e Funzionante**  
✅ **Sintassi Python Validata**  
✅ **Configurazione challenge Pronta**  
✅ **Risk Management Ultra-Conservativo**  
✅ **Logging e Monitoraggio Completi**  
✅ **Protezioni Multi-Layer Attive**

**🚀 PRONTO PER DEPLOYMENT IMMEDIATO SU CHALLENGE**

---

*Sistema legacy monolitico progettato per massima affidabilità e semplicità di deployment. Un singolo file, massima potenza quantistica.*
