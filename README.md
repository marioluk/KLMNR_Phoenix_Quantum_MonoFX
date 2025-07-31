# 📊 Esportazione motivi blocco ordini (logs/trade_decision_report.csv)

Da luglio 2025, ogni volta che il sistema valuta la possibilità di eseguire un ordine (BUY/SELL) e questo viene bloccato (o tutte le condizioni sono OK), il motivo viene salvato automaticamente in un file CSV chiamato `logs/trade_decision_report.csv` nella cartella dei log del progetto.

**Cosa contiene il file:**

- `timestamp`: data e ora del controllo
- `symbol`: simbolo valutato
- `step`: fase della logica (es: can_trade, trading_hours, buffer_tick, ecc)
- `detail`: dettaglio del motivo o conferma che tutte le condizioni sono OK

**Esempio di riga CSV:**

```
2025-07-29 15:32:10,EURUSD,can_trade,Motivo: can_trade() = False (cooldown, spread, max posizioni, ecc.)
2025-07-29 15:32:11,EURUSD,trading_hours,Motivo: fuori orario di trading
2025-07-29 15:32:12,EURUSD,ok,TUTTE LE CONDIZIONI OK: pronto per esecuzione trade BUY su EURUSD (size: 0.10)
```

Questo report può essere aperto con Excel o strumenti di analisi dati per capire in modo rapido e trasparente tutti i motivi per cui un ordine non viene eseguito.

**Nota:** il file viene aggiornato automaticamente ad ogni ciclo di valutazione, non serve alcuna azione manuale.


# [29/07/2025] Novità: Logging segnali tick-by-tick

## Logging avanzato dei segnali di trading

Il motore QuantumEngine ora stampa un log dettagliato dei segnali ad ogni tick (tick-by-tick), senza più report periodico. Ogni segnale viene loggato subito con tutte le informazioni utili (simbolo, entropy, spin, motivazione, ecc). La dashboard si occuperà di aggregare e visualizzare i dati in forma tabellare/grafica.

### Esempio di log tick-by-tick

```
[SIGNAL-DEBUG] [APERTURA] EURUSD | MOTIVO: Condizioni soddisfatte per segnale 'BUY' | Dettagli: {...}
[SIGNAL-DEBUG] [SCARTATO] EURUSD | MOTIVO: Buffer tick insufficiente | Dettagli: {...}
```

## Prossimi sviluppi

- Visualizzazione nella dashboard della sequenza segnali e relativo esito (aggregazione lato dashboard).
- Esportazione CSV/JSON dei log tick-by-tick per analisi esterna.

# 🆕 [29/07/2025] Logging dettagliato dei segnali di trading

Da luglio 2025, ogni segnale generato dal sistema (BUY, SELL, HOLD) viene tracciato nei log con una struttura dettagliata e motivazione, per massima trasparenza e diagnosi.

Esempio di log:

```
[SIGNAL-DEBUG] [APERTURA] EURUSD | MOTIVO: Condizioni soddisfatte per segnale 'BUY' | Dettagli: {'symbol': 'EURUSD', 'signal': 'BUY', 'entropy': 0.62, 'spin': 0.3, 'confidence': 0.9, 'volatility': 1.12, 'buy_thresh': 0.55, 'sell_thresh': 0.45, 'price': 1.12345, 'timestamp': '2025-07-29T10:15:00'}
[SIGNAL-DEBUG] [SCARTATO] EURUSD | MOTIVO: Buffer tick insufficiente | Dettagli: {'symbol': 'EURUSD', 'ticks': 7, 'min_spin_samples': 10, 'timestamp': '2025-07-29T10:14:59'}
```

Questo permette di capire in tempo reale perché un segnale viene accettato o scartato, con tutti i parametri rilevanti.

# Debug e Diagnostica (Segnali e Strategie)

---
# 🔄 LOGICA SPIN QUANTISTICO: CALCOLO, NORMALIZZAZIONE E USO NEI SEGNALI BUY/SELL

---
# 🔄 LOGICA ENTROPIA: CALCOLO, NORMALIZZAZIONE E USO NEI SEGNALI BUY/SELL

## Calcolo dell'Entropia

L'**entropia** misura la "disordine" o imprevedibilità delle variazioni di prezzo (delta) in una finestra di tick.

- **Formula:**
  ```
  E = -Σ (pᵢ * log(pᵢ)) / log(N)
  ```
  dove:
    - pᵢ = |deltaᵢ| / somma(|delta|) (probabilità normalizzata di ogni variazione)
    - N = numero di delta validi nella finestra
    - La somma è su tutti i delta ≠ 0

- **Range:** l'entropia è sempre normalizzata tra 0 (massimo ordine, tutti i delta uguali) e 1 (massimo disordine, delta distribuiti uniformemente).
- **Normalizzazione:** la divisione per `log(N)` garantisce che il massimo valore sia 1 indipendentemente dalla finestra.

## Logica BUY/SELL

- L'entropia viene usata insieme allo spin per generare i segnali:
  - **BUY:** `entropia > soglia_buy` **e** `spin > spin_threshold * confidence`
  - **SELL:** `entropia < soglia_sell` **e** `spin < -spin_threshold * confidence`
  - **HOLD:** nessuna delle due condizioni

- Le soglie di entropia (`soglia_buy`, `soglia_sell`) sono configurabili e possono essere adattate dinamicamente in base alla volatilità.
- L'entropia non viene mai "invertita" o modificata prima della decisione: il confronto è sempre diretto con la soglia.

## Esempio pratico

Supponiamo:
  - entropia = 0.62, soglia_buy = 0.55, spin = 0.30, confidence = 0.9, spin_threshold = 0.25
  - Condizione BUY: 0.62 > 0.55 (TRUE) **e** 0.30 > 0.25 * 0.9 → 0.30 > 0.225 (TRUE) ⇒ BUY

Se invece:
  - entropia = 0.40, soglia_sell = 0.45, spin = -0.35, confidence = 0.8, spin_threshold = 0.25
  - Condizione SELL: 0.40 < 0.45 (TRUE) **e** -0.35 < -0.25 * 0.8 → -0.35 < -0.20 (TRUE) ⇒ SELL

## Riepilogo

- L'entropia è sempre normalizzata tra 0 e 1.
- Le soglie sono configurabili e possono essere adattive.
- La logica implementata corrisponde esattamente a quella descritta nei commenti e nella documentazione del codice.
- Se vuoi cambiare la sensibilità dei segnali, agisci su `entropy_thresholds` nella config.

---

## Calcolo dello Spin

Lo **spin** è una misura del momentum direzionale dei tick di mercato:

- **Formula:**
  ```
  S = (N⁺ - N⁻) / N_total
  ```
  dove:
    - N⁺ = numero tick con direzione positiva (prezzo in salita)
    - N⁻ = numero tick con direzione negativa (prezzo in discesa)
    - N_total = N⁺ + N⁻

- **Range:** lo spin è sempre compreso tra -1 (tutti short) e +1 (tutti long), 0 se bilanciato.
- **Non viene mai normalizzato tra 0 e 1** e non viene applicato il modulo prima della decisione buy/sell.

## Calcolo della Confidenza

- **Formula:**
  ```
  C = |N⁺ - N⁻| / N_total × √N_total
  ```
  - C è una misura di quanto è sbilanciato il momentum, pesata per il numero di tick.
  - Range: [0, 1] (viene troncata a 1.0 se superiore)

## Logica BUY/SELL

- La decisione di acquisto/vendita si basa su:
  - **BUY:** `spin > spin_threshold * confidence` e entropia > soglia buy
  - **SELL:** `spin < -spin_threshold * confidence` e entropia < soglia sell
  - **HOLD:** nessuna delle due condizioni

- **Nota:**
  - Lo spin positivo genera solo segnali BUY, quello negativo solo SELL.
  - Il modulo (`abs(spin)`) viene usato solo per la volatilità, mai per la logica buy/sell.
  - La soglia `spin_threshold` è normalizzata tra 0 e 1 e va impostata in config in questo range.

## Esempio pratico

Supponiamo:
  - spin = 0.35, confidence = 0.8, spin_threshold = 0.25
  - Condizione BUY: 0.35 > 0.25 * 0.8 → 0.35 > 0.20 → TRUE
  - Condizione SELL: non valutata perché spin > 0

Se invece:
  - spin = -0.40, confidence = 0.7, spin_threshold = 0.25
  - Condizione SELL: -0.40 < -0.25 * 0.7 → -0.40 < -0.175 → TRUE
  - Condizione BUY: non valutata perché spin < 0

## Riepilogo

- Lo spin è simmetrico, negativo per sell, positivo per buy.
- Non viene mai reso positivo tramite modulo prima della decisione buy/sell.
- La logica implementata corrisponde esattamente a quella descritta nei commenti e nella documentazione del codice.
- Se vuoi cambiare la sensibilità dei segnali, agisci su `spin_threshold` nella config.

---

## Segnali di Debug Utilizzati

Durante la fase di troubleshooting e test sono stati utilizzati i seguenti segnali di debug (print temporanei, ora rimossi):

- `[DEBUG-TEST] [get_signal] INIZIO: symbol=...`
- `[DEBUG-TEST] [calculate_spin] INIZIO: ticks=...`
- `[DEBUG-TEST] [calculate_spin] cache_key: ...`
- `[DEBUG-TEST] [calculate_spin] RISULTATO: ...`
- `[DEBUG-TEST] [_get_cached] INIZIO: key=..., cache_dict=...`
- `[DEBUG-TEST] [_get_cached] PRESO LOCK`
- `[DEBUG-TEST] [_get_cached] DEADLOCK TIMEOUT su _runtime_lock! Restituisco fallback.`
- `[DEBUG-TEST] [_get_cached] CACHE MISS, calcolo valore...`
- `[DEBUG-TEST] [_get_cached] VALORE CALCOLATO: ...`
- `[DEBUG-TEST] [_get_cached] VALORE SALVATO IN CACHE`

Questi segnali sono stati fondamentali per:
- Tracciare il flusso di esecuzione durante i test
- Individuare deadlock o blocchi su threading/lock
- Verificare la corretta propagazione dei dati tra funzioni
- Validare la presenza di output anche in ambiente pytest

## Strategie di Troubleshooting adottate

- Mock di moduli esterni (es. `mt5`) nei test
- Import dinamico del modulo principale nei test
- Print di debug in ogni funzione critica (inizio, fine, errori)
- Timeout e fallback nei lock per evitare deadlock
- Uso di `threading.RLock` per la sicurezza thread-safe
- Timeout sulle funzioni di calcolo intensive

## Come riutilizzare

Se in futuro dovessi riscontrare blocchi, deadlock o assenza di output nei test:
1. Inserisci print simili a quelli sopra nelle funzioni sospette
2. Verifica la presenza di output sia in esecuzione diretta che in pytest (`-s`)
3. Applica timeout e fallback nei lock
4. Mocka le dipendenze esterne nei test
5. Consulta questa sezione per esempi di segnali e strategie

---
# Changelog (Modifiche recenti a phoenix_quantum_monofx_program.py)

## 28-07-2025

- **Correzione funzione setup_logger:**
  - Ora accetta un argomento opzionale `config_path` per compatibilità futura con chiamate da altre classi (es. ConfigManager).
  - Risolto il TypeError "setup_logger() takes 0 positional arguments but 1 was given" che impediva l'avvio del sistema.
  - Test di logging e avvio sistema ora funzionano senza errori.
- **Commit dedicato:**
  - Le modifiche sono state committate separatamente solo su questo file per tracciabilità.

---
# Novità: Opzione Trailing Stop Dinamico e Limite Trade Giornaliero Globale/Per-Simbolo
## 🚨 AGGIORNAMENTO - 24 LUGLIO 2025: Limite trade giornaliero globale/per-simbolo

Da questa versione è possibile scegliere se il limite massimo di trade giornalieri (`max_daily_trades`) venga applicato globalmente su tutti i simboli oppure separatamente per ogni simbolo. Questa opzione è configurabile tramite il nuovo parametro:

```json
"risk_parameters": {
    ...
    "max_daily_trades": 6,
    "daily_trade_limit_mode": "global" // "global" (default) oppure "per_symbol"
}
```

- Se `daily_trade_limit_mode` è `global`, il limite massimo di trade giornalieri viene applicato all'intero sistema (tutti i simboli sommati).
- Se `daily_trade_limit_mode` è `per_symbol`, il limite viene applicato separatamente per ogni simbolo.

**Dove viene applicata questa logica:**
- Trading engine (`phoenix_quantum_monofx_program.py`): la logica di conteggio e blocco trade è aggiornata per supportare entrambe le modalità.
- Ottimizzatore/autogeneratore (`autonomous_challenge_optimizer.py`): i template e le configurazioni generate includono il nuovo parametro, con default `global`.

**Nota:** Puoi cambiare la modalità in qualsiasi momento aggiornando la configurazione, senza modificare il codice.

**Esempio di sezione risk_parameters:**
```json
"risk_parameters": {
    "risk_percent": 0.007,
    "max_daily_trades": 6,
    "max_concurrent_trades": 3,
    "daily_trade_limit_mode": "per_symbol"
}
```

**Compatibilità:**
- Le vecchie configurazioni senza il parametro useranno la modalità globale (default).

---

Da luglio 2025 è possibile scegliere la modalità di attivazione del trailing stop direttamente da file di configurazione tramite il parametro:

```json
"trailing_stop": {
    "enable": true,
    "activation_mode": "fixed",      // "fixed" (default) oppure "percent_tp"
    "activation_pips": 150,           // usato solo se activation_mode = "fixed"
    "tp_percentage": 0.5,             // usato solo se activation_mode = "percent_tp"
    "step_pips": 50,
    "lock_percentage": 0.5
}
```


- Se `activation_mode` è `fixed`, il trailing stop si attiva al raggiungimento di `activation_pips` pips di profitto.
- Se `activation_mode` è `percent_tp`, il trailing stop si attiva automaticamente quando il profitto raggiunge la percentuale di take profit specificata da `tp_percentage` (es: 0.5 = 50%) calcolata per la posizione (dinamico per ogni trade/simbolo).

Questa logica è implementata sia nell'optimizer che nel trading engine. Non è più necessario modificare il codice per cambiare la modalità: basta aggiornare la configurazione.

**Esempio:**


Per attivare il trailing stop al 50% del TP:
```json
"trailing_stop": {
    "enable": true,
    "activation_mode": "percent_tp",
    "tp_percentage": 0.5,         // attiva trailing al 50% del TP
    "activation_pips": 150,       // ignorato in questa modalità
    "step_pips": 50,
    "lock_percentage": 0.5
}
```

Per attivare il trailing stop al 70% del TP:
```json
"trailing_stop": {
    "enable": true,
    "activation_mode": "percent_tp",
    "tp_percentage": 0.7,         // attiva trailing al 70% del TP
    "activation_pips": 150,       // ignorato
    "step_pips": 50,
    "lock_percentage": 0.5
}
```

Per attivare il trailing stop a 150 pips fissi:
```json
"trailing_stop": {
    "enable": true,
    "activation_mode": "fixed",
    "activation_pips": 150,
    "step_pips": 50,
    "lock_percentage": 0.5
}
```

**Nota:** La modalità può essere cambiata in qualsiasi momento aggiornando la config, senza riavviare il sistema.
# 🎯 BROKER QUANTUM TRADING SYSTEM MONOLITHIC VERSION
## Sistema Monolitico Completo e Funzionante

---


## 🚨 **AGGIORNAMENTI RECENTI**

### 24 LUGLIO 2025
**Nuova opzione `daily_trade_limit_mode` (globale/per-simbolo) per il limite massimo di trade giornalieri.**
Configurabile da file di configurazione, supportata sia dal motore di trading che dall'ottimizzatore. Default: globale.

### 20 LUGLIO 2025

✅ **SISTEMA COMPLETAMENTE RISOLTO E OPERATIVO**

### 🔥 MODIFICA CRITICA - NORMALIZZAZIONE SPIN_THRESHOLD (24 luglio 2025)

**Da questa versione, il parametro `spin_threshold` nella configurazione è SEMPRE normalizzato nell'intervallo [0,1]** e calcolato in modo robusto dall'ottimizzatore, perfettamente coerente con la logica del trading engine (`phoenix_quantum_monofx_program.py`).

- Tutti i segnali BUY/SELL ora usano soglie di spin consistenti e confrontabili.
- La generazione del file di configurazione produce `spin_threshold` normalizzato (es: 0.25, 0.3, ecc.), mai valori >1.
- Questo elimina ogni ambiguità tra ottimizzatore, config e motore di trading.
- Per aumentare la frequenza dei segnali, abbassare leggermente `spin_threshold` (es: 0.15-0.20).

**IMPORTANTE:** Se usi vecchi file config, assicurati che `spin_threshold` sia nel range [0,1]!

---

### �🔧 **Fix Implementati Oggi:**
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

## 🚨 **IMPORTANTE - SISTEMA MONOLITICO**

⚠️ **Questo README documenta il SISTEMA MONOLITICO** contenuto nel file `phoenix_quantum_monofx_program.py`

🔄 **Per panoramica completa del progetto** → vedi `README_PROJECT_OVERVIEW.md`  
🎯 **Per sistema backtest integrato** → vedi `/backtest_mono/README.md`

## 📁 **ORGANIZZAZIONE PROJECT AGGIORNATA**

### Sistema Reorganizzato e Ottimizzato (Luglio 2025)
```
KLMNR_Phoenix_Quantum_MonoFX/
│   ├── phoenix_quantum_monofx_program.py  # Main MonoFX (MT5 FIXED)
│   ├── config/                 # Configurazioni centralizzate
│   ├── backtest_mono/        # Tools di backtest (AGGIORNATI)
│   │   ├── autonomous_high_stakes_optimizer.py  # 🚀 Menu continuo
│   │   ├── production_converter.py              # 🔄 Smart file discovery
│   │   └── README.md                             # Documentazione aggiornata
│   ├── dashboard_mono/       # Dashboard web mono
│   └── logs/                   # Log files
├── quantum_trading_system/     # 🚀 Sistema Moderno (In sviluppo)
├── dashboard_mono/                  # 🎨 Dashboard Moderna (Futura)
├── backtest/                  # 🧪 Tools di testing e analisi
├── docs/                      # 📚 Documentazione
└── .gitignore                 # 🔧 Git ottimizzato (FIXED)
```

### Quick Start

- **Dashboard Mono**: `cd legacy_system/dashboard_mono && start_dashboard.bat`
- **Backtest Tools**: `cd backtest_clean`

---

## 📋 **OVERVIEW ARCHITETTURALE - SISTEMA MONOLITICO**

Il sistema è implementato attraverso **6 classi principali** che operano in sinergia per fornire un trading system completo basato su principi quantistici e analisi dell'entropia. Il core engine applica algoritmi matematici avanzati per l'analisi dei tick di mercato e la generazione di segnali di alta qualità.

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
    
    # 5. Setup metriche e drawdown tracker
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
        
        if self._check_daily_limits():
            
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
1. **Verifica Prerequisiti:**
   ```python
   # Orari di trading validi
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

### **4. Position Sizing Formula**

**Algoritmo Kelly-Based Modificato:**
```
Position_Size = Risk_Amount / (SL_pips × Pip_Value)

dove:
Risk_Amount = Account_Equity × Risk_Percentage
SL_pips = max(Min_SL, Base_SL × (1 + 0.5 × V_quantum))
Pip_Value = valore monetario per pip (da broker)
```

#### **Controllo Margine:**
```
Safe_Size = Position_Size × min(1, Max_Margin / Required_Margin)

dove:
Max_Margin = Account_Free_Margin × 0.8  (80% del margine libero)
```

### **5. Stop Loss Dinamico**

**Calcolo Adattivo:**
```
SL_dynamic = max(Min_SL_pips, Base_SL_pips × Volatility_Factor)

dove:
Volatility_Factor = 1 + α × V_quantum
α = coefficiente di sensibilità (default: 0.5)

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

---

# 🚀 Best Practice 2025 - Phoenix Quantum MonoFX

- Tutte le configurazioni sono centralizzate in `config/` e documentate in `config/README.md` (tabella parametri accettati)
- Validazione automatica della configurazione all’avvio: warning/errore per parametri mancanti o incoerenti
- Fallback e default robusti per tutti i parametri opzionali
- Magic number, spread, orari, pips e limiti sono gestiti solo tramite file di configurazione
- Logging uniforme (info, warning, error, critical, debug) e messaggi dettagliati per edge-case
- Tutte le variabili condivise sono protette da lock/thread-safe
- Test automatici/unitari per la business logic e validazione config
- Docstring dettagliati per ogni funzione pubblica e parametri
- Un solo README principale per chiarezza, con rimando a `config/README.md` e `docs/CONFIG_ORGANIZATION_GUIDE.md`

---

# 📊 Range parametri per tipologia di trading

Dal 1 agosto 2025, la validazione automatica dei parametri (sia in config che nell’optimizer) utilizza i seguenti range ottimizzati per ciascuna tipologia di trading. Questi valori sono allineati a best practice e risultati di backtest.

| Tipologia     | buffer_size | spin_window | signal_cooldown | max_position_hours | max_daily_trades | Descrizione |
|--------------|-------------|-------------|-----------------|-------------------|------------------|-------------|
| Scalping     | 100–300     | 10–30       | 60–300          | 0.05–2            | 20–100           | M1–M5, operatività ultra-veloce |
| Intraday     | 300–800     | 20–60       | 300–1200        | 2–12              | 5–20             | M15–H1, nessuna posizione overnight |
| Swing        | 800–2000    | 40–120      | 1200–3600       | 24–96             | 1–6              | H1–D1, posizioni multi-day |
| Position     | 1500–5000   | 100–300     | 3600–14400      | 96–336            | 1–2              | D1–W1, posizioni di lungo periodo |

Questi range sono usati nella funzione `validate_trading_params` di `autonomous_challenge_optimizer.py` e sono commentati direttamente nel codice per massima leggibilità.

**Esempio di commento nel codice:**
```python
ranges = {
    # Scalping: operatività ultra-veloce su timeframe M1-M5, molti trade al giorno, posizioni di breve durata
    'scalping': {
        'max_position_hours': (0.05, 2),      # Durata posizione: da pochi minuti a max 2 ore
        'buffer_size': (100, 300),            # Storico tick/candele: sufficiente per pattern rapidi
        'spin_window': (10, 30),              # Finestra di calcolo segnali: breve
        'signal_cooldown': (60, 300),         # Attesa tra segnali: da 1 a 5 minuti
        'max_daily_trades': (20, 100)         # Trade giornalieri: molto elevato
    },
    # ... (vedi file per tutte le tipologie)
}
```

**Nota:** La validazione automatica blocca la generazione della configurazione se i parametri sono fuori range, con log dettagliato e riepilogo dei warning.

Per dettagli e override dei parametri, consulta anche `config/README.md` e la documentazione tecnica.

---

# =============================================================
# CORRELAZIONE TRA TIPOLOGIA DI TRADING E CALCOLO SL/TP/TS
# =============================================================
# | Tipologia   | Stop Loss (SL)         | Take Profit (TP)         | Trailing Stop (TS)                | Note operative                       |
# |-------------|------------------------|--------------------------|------------------------------------|--------------------------------------|
# | Scalping    | 6-12 pips (molto stretto) | 10-20 pips (stretto)      | Attivazione rapida, step piccoli   | Protezione immediata, trade brevi    |
# | Intraday    | 15-30 pips (medio)     | 30-60 pips (medio)       | Attivazione media, step medi       | Nessuna posizione overnight          |
# | Swing       | 50-120 pips (ampio)    | 100-250 pips (ampio)     | Attivazione solo dopo movimenti ampi, step larghi | Posizioni multi-day, oscillazioni ampie |
# | Position    | 150-400 pips (molto ampio) | 300-800 pips (molto ampio) | Attivazione tardiva, step molto larghi | Segue trend di fondo, trade lunghi   |
#
# Il calcolo di SL/TP/TS avviene sia nell'optimizer che nel sistema di trading:
#   - SL/TP sono calcolati dinamicamente in base a parametri di config, volatilità e tipologia trading.
#   - Trailing Stop viene configurato per ogni simbolo e tipologia, con step e attivazione coerenti.
#   - La logica segue la stessa struttura: per operatività più lunga, parametri più ampi; per operatività breve, parametri più stretti e reattivi.
#   - Esempio: sl_price, tp_price = self.risk_manager.calculate_dynamic_levels(symbol, order_type, price)
# =============================================================
