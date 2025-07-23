# 🎯 BROKER QUANTUM TRADING SYSTEM - LEGACY MONOLITHIC VERSION
## Sistema Monolitico Completo e Funzionante

---

## 🚨 **AGGIORNAMENTO - 20 LUGLIO 2025**

✅ **SISTEMA COMPLETAMENTE RISOLTO E OPERATIVO**

### 🔧 **Fix Implementati Oggi:**
1. **Git Repository**: Pulito e ottimizzato dopo rimozione estensione Gait
2. **MT5 Connection**: Configurazione Broker FivePercentOnline-Real funzionante
3. **File Path Management**: Sistema robusto per ricerca config automatica
4. **Production Converter**: Funziona da qualsiasi directory con ricerca intelligente
5. **Autonomous Optimizer**: Menu continuo per workflow fluido

### 🎯 **Sistema Pronto Per Produzione:**
- ✅ Repository Git pulito e funzionante
- ✅ MT5 connesso correttamente a Broker
- ✅ File management intelligente implementato
- ✅ Tools di conversione ottimizzati
- ✅ Workflow development-to-production streamlined

---

## 🚨 **IMPORTANTE - SISTEMA LEGACY**

⚠️ **Questo README documenta il SISTEMA MONOLITICO** contenuto nel file `phoenix_quantum_monofx_program.py`

🔄 **Per panoramica completa del progetto** → vedi `README_PROJECT_OVERVIEW.md`  
🏗️ **Per sistema modulare refactorizzato** → vedi cartella `quantum_trading_system/`  
📚 **Per documentazione legacy dedicata** → vedi `legacy_system/README_LEGACY.md`  
🎯 **Per sistema backtest integrato** → vedi `legacy_system/backtest_mono/README.md`

## 📁 **ORGANIZZAZIONE PROJECT AGGIORNATA**

### Sistema Reorganizzato e Ottimizzato (Luglio 2025)
```
KLMNR_Phoenix_Quantum/
├── legacy_system/              # 🏛️ Sistema Legacy Completo e FUNZIONANTE
│   ├── phoenix_quantum_monofx_program.py  # Main MonoFX (MT5 FIXED)
│   ├── config/                 # Configurazioni centralizzate
│   ├── backtest_mono/        # Tools di backtest (AGGIORNATI)
│   │   ├── autonomous_high_stakes_optimizer.py  # 🚀 Menu continuo
│   │   ├── production_converter.py              # 🔄 Smart file discovery
│   │   └── README.md                             # Documentazione aggiornata
│   ├── dashboard_legacy/       # Dashboard web legacy
│   └── logs/                   # Log files
├── quantum_trading_system/     # 🚀 Sistema Moderno (In sviluppo)
├── dashboard/                  # 🎨 Dashboard Moderna (Futura)
├── backtest/                  # 🧪 Tools di testing e analisi
├── docs/                      # 📚 Documentazione
└── .gitignore                 # 🔧 Git ottimizzato (FIXED)
```

### Quick Start
- **Sistema Legacy**: `cd legacy_system && start_legacy.bat`
- **Dashboard Legacy**: `cd legacy_system/dashboard_legacy && start_dashboard.bat`
- **Backtest Tools**: `cd backtest_clean`

---

## 📋 **OVERVIEW ARCHITETTURALE - SISTEMA LEGACY**

Il sistema è implementato attraverso **6 classi principali** che operano in sinergia per fornire un trading system completo basato su su principi quantistici e analisi dell'entropia. Il core engine applica algoritmi matematici avanzati per l'analisi dei tick di mercato e la generazione di segnali di alta qualità.

### **�️ ARCHITETTURA DELLE CLASSI:**
1. **`ConfigManager`** - Gestione configurazione e validazione parametri
2. **`QuantumEngine`** - Motore di analisi quantistica e generazione segnali  
3. **`DailyDrawdownTracker`** - Monitoraggio protezioni Broker
4. **`QuantumRiskManager`** - Gestione rischio e position sizing
5. **`TradingMetrics`** - Raccolta e analisi delle metriche di performance
6. **`QuantumTradingSystem`** - Coordinatore principale e entry point

---

## 🔬 **ANALISI TECNICA DELLE CLASSI**

### **1. ConfigManager** - Gestione Configurazione e Validazione

**Responsabilità:** Carica, valida e normalizza la configurazione JSON del sistema.

#### **Metodi Principali:**
- `__init__(config_path)` - Caricamento e validazione configurazione
- `_validate_config()` - Verifica sezioni obbligatorie (symbols, risk_parameters)
- `_normalize_config()` - Unifica risk_parameters e risk_management per compatibilità
- `get_risk_params(symbol)` - Estrae parametri di rischio per simbolo specifico
- `_get_max_allowed_spread(symbol)` - Calcola spread massimo consentito

#### **Validazioni Implementate:**
```python
required_sections = ['symbols', 'risk_parameters']
# Verifica esistenza sezioni critiche
# Controllo tipo di dato e struttura dati
# Normalizzazione parametri duplicati
```

#### **Logica di Normalizzazione:**
Il sistema gestisce configurazioni legacy unificando:
- `risk_management` → `risk_parameters` 
- `features.trailing_stop` → `risk_parameters.trailing_stop`

---

### **2. QuantumEngine** - Motore di Analisi Quantistica

**Responsabilità:** Elaborazione tick, calcolo entropia e generazione segnali di trading.

#### **Parametri Configurabili:**
```python
buffer_size = 100        # Dimensione buffer tick (ridotta per debug)
spin_window = 20         # Finestra mobile per calcolo spin
min_spin_samples = 10    # Campioni minimi per validità segnale
signal_cooldown = 300    # Cooldown tra segnali (secondi)
```

#### **Metodi di Calcolo Quantistico:**

**a) `calculate_entropy(deltas)`** - Calcolo Entropia Normalizzata
```python
@staticmethod
@lru_cache(maxsize=1000)
def calculate_entropy(deltas: Tuple[float]) -> float:
    # Normalizzazione delta: P(i) = |Δᵢ| / Σ|Δⱼ|
    prob = abs_deltas / sum_abs_deltas
    # Shannon entropy: H = -Σ P(i) * log(P(i))
    entropy = -np.sum(valid_probs * np.log(valid_probs + 1e-10))
    # Normalizzazione [0,1]: H_norm = H / log(n)
    return entropy / np.log(len(valid_probs) + 1e-10)
```

**b) `calculate_spin(ticks)`** - Spin Quantistico e Confidenza
```python
def calculate_spin(self, ticks: List[Dict]) -> Tuple[float, float]:
    # Filtraggio tick validi (direction ≠ 0)
    positive = sum(1 for t in valid_ticks if t['direction'] > 0)
    negative = sum(1 for t in valid_ticks if t['direction'] < 0)
    
    # Spin bilanciato: S = (N⁺ - N⁻) / N_total
    raw_spin = (positive - negative) / total
    
    # Confidenza: C = |N⁺ - N⁻| / N_total * √N_total
    confidence = abs(positive - negative) / total * sqrt(total)
    return raw_spin, confidence
```

**c) `calculate_quantum_volatility(symbol)`** - Volatilità Adattiva
```python
# Combina entropia e spin per volatilità quantistica
deltas = [t['delta'] for t in ticks[-window:]]
prob_dist = |deltas| / Σ|deltas|
entropy = -Σ(P * log(P)) / log(window)
volatility = 1 + |spin| * entropy
```

#### **Controlli di Trading:**

**a) `can_trade(symbol)`** - Verifica Condizioni Trading
1. **Cooldown Check**: Posizioni (1800s) + Segnali (900s)
2. **Spread Control**: Verifica spread < max_allowed
3. **Position Limits**: max_positions configurabile
4. **Symbol Info**: Validazione dati broker

**b) `is_in_cooldown_period(symbol)`** - Gestione Cooldown
- Cooldown normale posizioni: 1800 secondi
- Cooldown segnali: 900 secondi  
- Prevenzione over-trading

---

### **3. DailyDrawdownTracker** - Protezione Broker

**Responsabilità:** Monitoraggio continuo del drawdown per compliance Broker.

#### **Parametri Critici:**
```python
soft_limit = 0.02    # 2% - Warning level
hard_limit = 0.05    # 5% - Stop immediato
daily_high          # Picco giornaliero di equity
max_daily_drawdown  # Massimo drawdown raggiunto
```

#### **Algoritmo di Monitoraggio:**
```python
def check_limits(self, current_equity: float) -> Tuple[bool, bool]:
    # Calcolo percentuale drawdown
    drawdown_pct = (current_equity - daily_high) / daily_high
    
    # Controllo soglie
    soft_hit = drawdown_pct <= -soft_limit   # -2%
    hard_hit = drawdown_pct <= -hard_limit   # -5%
    
    # Logging critico per hard limit
    if hard_hit:
        logger.critical("HARD LIMIT HIT! Trading STOP")
    
    return soft_hit, hard_hit
```

#### **Reset Giornaliero:**
- Reset automatico a mezzanotte
- Nuovo daily_high = max(equity, balance)
- Disattivazione protezioni temporanee

---

### **4. QuantumRiskManager** - Gestione Rischio e Position Sizing

**Responsabilità:** Calcolo dimensioni posizioni, livelli SL/TP e controllo margine.

#### **Calcolo Position Size:**

**Algoritmo Principal:**
```python
def calculate_position_size(symbol, price, signal) -> float:
    # 1. Rischio base in valuta account
    risk_percent = config.risk_percent  # Default: 2%
    risk_amount = account_equity * risk_percent
    
    # 2. Stop Loss dinamico in pips
    sl_pips = calculate_sl_pips(symbol)  # Con volatilità
    
    # 3. Valore pip dal broker
    pip_value = symbol_data['pip_value']
    
    # 4. Calcolo size: Size = Risk_Amount / (SL_pips * Pip_Value)
    size = risk_amount / (sl_pips * pip_value)
    
    # 5. Safety limit assoluto
    size = min(size, 0.1)  # Max 0.1 lotti
    
    return apply_size_limits(symbol, size)
```

#### **Controllo Margine:**
```python
def _apply_size_limits(symbol, size):
    # Calcolo margine richiesto
    margin_required = mt5.order_calc_margin(ORDER_TYPE_BUY, symbol, size, ask)
    
    # Limite conservativo: max 80% margine libero
    max_margin = account.margin_free * 0.8
    
    if margin_required > max_margin:
        # Riduzione automatica size
        safe_size = size * (max_margin / margin_required)
        return round_to_step(safe_size)
```

#### **Livelli Dinamici SL/TP:**
```python
def calculate_dynamic_levels(symbol, position_type, entry_price):
    # Parametri base da configurazione
    min_sl = config.min_sl_distance_pips    # Es: 100 pips
    base_sl = config.base_sl_pips           # Es: 150 pips  
    tp_multiplier = config.profit_multiplier # Es: 2.0x
    
    # Adattamento per volatilità quantistica
    volatility = engine.calculate_quantum_volatility(symbol)
    sl_pips = max(min_sl, base_sl * (1.0 + 0.5 * volatility))
    tp_pips = sl_pips * tp_multiplier
    
    # Calcolo prezzi finali
    if position_type == BUY:
        sl_price = entry_price - (sl_pips * pip_size)
        tp_price = entry_price + (tp_pips * pip_size)
    else:  # SELL
        sl_price = entry_price + (sl_pips * pip_size) 
        tp_price = entry_price - (tp_pips * pip_size)
```

---

### **5. TradingMetrics** - Sistema di Monitoraggio Performance

**Responsabilità:** Raccolta, calcolo e reporting delle metriche di trading.

#### **Metriche Tracciate:**
- **Volume**: Total trades, winners, losers
- **Performance**: Total P&L, win rate, average profit/loss
- **Risk**: Maximum drawdown, risk-adjusted returns
- **Timing**: Trade duration, session performance
- **Symbol-specific**: Performance per simbolo

#### **Calcoli Statistici:**
```python
# Win Rate
win_rate = successful_trades / total_trades * 100

# Profit Factor  
profit_factor = gross_profit / abs(gross_loss)

# Sharpe Ratio (risk-adjusted return)
sharpe = (return_mean - risk_free_rate) / return_std

# Maximum Drawdown
max_dd = max((peak - trough) / peak for peak, trough in equity_curve)
```

---

### **6. QuantumTradingSystem** - Coordinatore Principale

**Responsabilità:** Orchestrazione del sistema completo, gestione del ciclo di vita.

#### **Inizializzazione Sistema:**
```python
def __init__(self, config_path: str):
    # 1. Setup logging
    self._setup_logger(config_path)
    
    # 2. Caricamento configurazione
    self.config = ConfigManager(config_path)
    
    # 3. Inizializzazione MT5 e attivazione simboli
    self._initialize_mt5()
    self._activate_symbols()
    
    # 4. Inizializzazione componenti core
    self.engine = QuantumEngine(self.config)
    self.risk_manager = QuantumRiskManager(self.config, self.engine, self)
    
    # 5. Setup metriche e drawdown tracker
    self.metrics = TradingMetrics()
    self.drawdown_tracker = DailyDrawdownTracker(initial_equity, config)
```

#### **Ciclo Principale di Trading:**
```python
def start(self):
    self.running = True
    while self.running:
        # 1. Verifica connessione MT5
        if not self._verify_connection():
            continue
            
        # 2. Aggiornamento account info
        self._update_account_info()
        
        # 3. Controllo drawdown giornaliero
        if self._check_daily_limits():
            break  # Stop per protezione
            
        # 4. Processamento simboli configurati
        for symbol in self.config.symbols:
            self._process_symbol(symbol)
            
        # 5. Gestione posizioni esistenti
        self._manage_existing_positions()
        
        # 6. Pausa tra cicli
        time.sleep(1)
```

---

## ⚙️ **LOGICA DI TRADING E PUNTI DI INGRESSO/USCITA**

### **Algoritmo di Generazione Segnali:**

#### **Condizioni di Ingresso:**
1. **Verifica Prerequisiti:**
   ```python
   # Orari di trading validi
   if not is_trading_hours(symbol, config): return
   # Spread accettabile  
   if current_spread > max_allowed_spread: return
   # Cooldown rispettato
   if is_in_cooldown_period(symbol): return
   # Buffer tick sufficiente
   if len(tick_buffer[symbol]) < min_samples: return
   ```

2. **Calcolo Segnale Quantistico:**
   ```python
   # Estrazione tick recenti
   recent_ticks = tick_buffer[symbol][-buffer_size:]
   
   # Calcolo entropia normalizzata [0,1]
   deltas = [tick['delta'] for tick in recent_ticks]
   entropy = calculate_entropy(tuple(deltas))
   
   # Calcolo spin e confidenza
   spin, confidence = calculate_spin(recent_ticks)
   
   # Generazione segnale finale
   signal_strength = abs(spin) * confidence * entropy
   
   # Soglie configurabili
   buy_threshold = quantum_params['entropy_thresholds']['buy_signal']   # 0.58
   sell_threshold = quantum_params['entropy_thresholds']['sell_signal'] # 0.42
   
   if entropy > buy_threshold and spin > 0:
       return "BUY", signal_strength
   elif entropy < sell_threshold and spin < 0:
       return "SELL", signal_strength
   ```

#### **Esecuzione Ordine:**
```python
def execute_trade(symbol, signal, signal_strength):
    # 1. Calcolo position size
    position_size = risk_manager.calculate_position_size(symbol, current_price, signal)
    
    # 2. Calcolo livelli SL/TP dinamici
    sl_price, tp_price = risk_manager.calculate_dynamic_levels(
        symbol, order_type, entry_price
    )
    
    # 3. Preparazione richiesta MT5
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": position_size,
        "type": mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(symbol).ask if signal == "BUY" else bid,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": f"QTS_{signal}_{signal_strength:.2f}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK, # se non viene accettato prova ORDER_FILLING_IOC
    }
    
    # 4. Invio ordine
    result = mt5.order_send(request)
    return result
```

### **Gestione Posizioni Aperte:**

#### **Trailing Stop Logic:**
```python
def update_trailing_stop(position):
    symbol = position.symbol
    config = get_symbol_config(symbol)
    
    # Parametri trailing
    activation_distance = config['trailing_stop']['activation_distance_pips']
    trail_distance = config['trailing_stop']['trail_distance_pips'] 
    
    current_price = get_current_price(symbol)
    profit_pips = calculate_profit_pips(position, current_price)
    
    # Attivazione trailing quando profitto > activation_distance
    if profit_pips >= activation_distance:
        new_sl = calculate_trailing_sl(position, current_price, trail_distance)
        
        # Aggiornamento solo se nuovo SL è più favorevole
        if is_better_sl(position.sl, new_sl, position.type):
            modify_position_sl(position, new_sl)
```

#### **Condizioni di Uscita:**
1. **Stop Loss Hit**: Perdita massima raggiunta
2. **Take Profit Hit**: Obiettivo di profitto raggiunto  
3. **Trailing Stop**: Protezione profitti dinamica
4. **Daily Drawdown**: Protezione Broker (-2% soft, -5% hard)
5. **End of Session**: Chiusura forzata fuori orari
6. **Emergency Stop**: Disconnessione MT5 o errori critici

---

---

---

## 📐 **APPENDICE MATEMATICA - FORMULE E ALGORITMI**

### **1. Calcolo Entropia Shannon Normalizzata**

**Formula Base:**
```
H(X) = -∑ᵢ P(xᵢ) × log(P(xᵢ))
```

**Implementazione Sistema:**
```python
# Normalizzazione probabilità dai delta di prezzo
P(i) = |Δᵢ| / ∑ⱼ|Δⱼ|

# Shannon entropy con regolarizzazione
H = -∑ᵢ P(i) × log(P(i) + ε)   dove ε = 1e-10

# Normalizzazione [0,1]
H_norm = H / log(n)   dove n = numero campioni
```

**Proprietà Matematiche:**
- **Range**: [0, 1] - 0 = ordine perfetto, 1 = massimo disordine
- **Monotonia**: Crescente con l'aleatorietà dei movimenti
- **Sensibilità**: Alta per cambiamenti nella distribuzione dei delta

### **2. Calcolo Spin Quantistico**

**Formula Spin Bilanciato:**
```
S = (N⁺ - N⁻) / N_total

dove:
N⁺ = numero tick con direzione positiva (prezzo in salita)
N⁻ = numero tick con direzione negativa (prezzo in discesa)
N_total = N⁺ + N⁻
```

**Formula Confidenza:**
```
C = |N⁺ - N⁻| / N_total × √N_total

dove:
|N⁺ - N⁻| = valore assoluto dello sbilanciamento
√N_total = peso statístico (aumenta con più campioni)
```

**Interpretazione Fisica:**
- **S > 0**: Momentum rialzista dominante
- **S < 0**: Momentum ribassista dominante  
- **S ≈ 0**: Equilibrio, nessuna direzione prevalente
- **C**: Confidenza nel segnale (0 = incerto, 1 = molto sicuro)

### **3. Volatilità Quantistica**

**Formula Combinata:**
```
V_quantum = 1 + |S| × H

dove:
|S| = valore assoluto dello spin (intensità direzionale)
H = entropia normalizzata (disordine del mercato)
```

**Spiegazione Matematica:**
- **Base = 1**: Volatilità neutra
- **|S|**: Amplifica con momentum direzionale forte
- **H**: Amplifica con alta aleatorietà/incertezza
- **Risultato**: Volatilità adattiva che aumenta con instabilità e directional bias

### **4. Position Sizing Formula**

**Algoritmo Kelly-Based Modificato:**
```
Position_Size = Risk_Amount / (SL_pips × Pip_Value)

dove:
Risk_Amount = Account_Equity × Risk_Percentage
SL_pips = max(Min_SL, Base_SL × (1 + 0.5 × V_quantum))
Pip_Value = valore monetario per pip (da broker)
```

**Controllo Margine:**
```
Safe_Size = Position_Size × min(1, Max_Margin / Required_Margin)

dove:
Max_Margin = Account_Free_Margin × 0.8  (80% del margine libero)
Required_Margin = MT5.order_calc_margin(symbol, size, price)
```

### **5. Stop Loss Dinamico**

**Calcolo Adattivo:**
```
SL_dynamic = max(Min_SL_pips, Base_SL_pips × Volatility_Factor)

dove:
Volatility_Factor = 1 + α × V_quantum
α = coefficiente di sensibilità (default: 0.5)
```

**Take Profit Correlato:**
```
TP_pips = SL_pips × Profit_Multiplier

dove:
Profit_Multiplier = configurabile per simbolo (1.5 - 2.5)
```

### **6. Drawdown Protection Formula**

**Calcolo Percentuale Drawdown:**
```
DD% = (Current_Equity - Daily_High) / Daily_High

dove:
Daily_High = max(Equity, Balance) del giorno corrente
Current_Equity = equity in tempo reale
```

**Soglie Broker:**
```
Soft_Limit = -2%   # Warning e riduzione aggressività
Hard_Limit = -5%   # Stop immediato del trading
```

### **7. Signal Strength Computation**

**Forza Segnale Combinata:**
```
Signal_Strength = |S| × C × H

dove:
|S| = |spin| = intensità direzionale [0,1]
C = confidence = affidabilità statistica [0,1]  
H = entropy = aleatorietà normalizzata [0,1]
```

**Soglie Decisioni:**
```
BUY_Signal: H > 0.58 AND S > 0 AND Signal_Strength > threshold
SELL_Signal: H < 0.42 AND S < 0 AND Signal_Strength > threshold
```

### **8. Trailing Stop Mathematics**

**Aggiornamento Dinamico SL:**
```
Per posizione LONG:
New_SL = max(Current_SL, Current_Price - Trail_Distance_pips × Pip_Size)

Per posizione SHORT:
New_SL = min(Current_SL, Current_Price + Trail_Distance_pips × Pip_Size)
```

**Condizione Attivazione:**
```
Profit_pips = |Current_Price - Entry_Price| / Pip_Size
Attivazione: Profit_pips >= Activation_Distance_pips
```

### **9. Risk-Adjusted Performance Metrics**

**Sharpe Ratio:**
```
Sharpe = (R_mean - R_f) / σ_R

dove:
R_mean = return medio del periodo
R_f = risk-free rate (tasso privo di rischio)
σ_R = deviazione standard dei return
```

**Maximum Drawdown:**
```
MaxDD = max(Peak_i - Trough_j) / Peak_i   per tutti i ≤ j

dove Peak_i e Trough_j sono i picchi e valli dell'equity curve
```

**Profit Factor:**
```
PF = Gross_Profit / |Gross_Loss|

dove:
Gross_Profit = ∑(tutti i trade vincenti)
Gross_Loss = ∑(tutti i trade perdenti)
```

---

## 🏆 **STATUS PROGETTO**

✅ **Sistema Completo e Testato**  
✅ **Broker Compliance Verificata**  
✅ **Configurazione Produzione Identificata**  
✅ **Risk Management Ultra-Conservativo**  
✅ **Analisi Matematica Documentata**  

**🚀 CORE ENGINE PRONTO PER DEPLOYMENT SU BROKER HIGH STAKES CHALLENGE**

---

*Sistema progettato per maximizzare le probabilità di successo attraverso algoritmi quantistici avanzati, matematica finanziaria rigorosa e risk management disciplinato.*
