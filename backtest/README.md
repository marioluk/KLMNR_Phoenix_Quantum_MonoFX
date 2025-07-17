# THE5ERS QUANTUM ALGORITHM - BACKTEST & OPTIMIZATION SYSTEM

## 📋 Panoramica

Sistema completo di backtest e ottimizzazione per l'algoritmo Quantum Trading sviluppato per la **The5ers High Stakes Challenge**. Include:

- **Backtest Engine**: Simulazione storica dell'algoritmo
- **Parameter Optimizer**: Ottimizzazione automatica dei parametri
- **Results Analyzer**: Analisi avanzata dei risultati
- **Compliance Checker**: Verifica conformità regole The5ers

## 🎯 Obiettivi The5ers High Stakes Challenge

| Fase | Profit Target | Max Daily Loss | Max Total Loss | Min Profitable Days |
|------|---------------|----------------|----------------|---------------------|
| **Step 1** | 8% | 5% | 10% | 3 |
| **Step 2** | 5% | 5% | 10% | 3 |
| **Scaling** | 10% | 5% | 10% | 3 |

## 🚀 Quick Start

### 1. Installazione

```bash
# Clona il repository
git clone <repository-url>
cd The5ers/backtest

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Avvio Ottimizzazione (Windows)

```bash
# Esegui il batch file
run_optimization.bat
```

### 3. Avvio Manuale

```bash
# Configura l'ambiente Python
python -m venv venv
venv\Scripts\activate

# Installa dipendenze
pip install numpy pandas matplotlib seaborn scipy scikit-learn

# Avvia ottimizzazione
python run_optimization.py
```

## 📁 Struttura del Progetto

```
backtest/
├── backtest_engine.py      # Engine principale di backtest
├── parameter_optimizer.py  # Sistema di ottimizzazione parametri
├── results_analyzer.py     # Analisi e visualizzazione risultati
├── config.py              # Configurazioni e scenari
├── run_optimization.py    # Script principale
├── run_optimization.bat   # Batch per Windows
├── data/                  # Dati storici (CSV, MT5, etc.)
├── results/               # Risultati ottimizzazione (JSON)
├── reports/               # Report e grafici
└── logs/                  # File di log
```

## 🔧 Configurazione

### Scenari di Ottimizzazione Disponibili

1. **conservative_step1**: Ottimizzazione conservativa per Step 1
2. **aggressive_step2**: Ottimizzazione aggressiva per Step 2  
3. **scaling_optimized**: Ottimizzazione per fase Scaling
4. **balanced_all_steps**: Ottimizzazione bilanciata per tutte le fasi

### Parametri Ottimizzabili

#### Quantum Engine
- `buffer_size`: Dimensione buffer tick (200-800)
- `spin_window`: Finestra calcolo spin (30-120)
- `min_spin_samples`: Minimo campioni spin (10-50)
- `spin_threshold`: Soglia attivazione spin (0.15-0.45)
- `signal_cooldown`: Cooldown segnali (300-1800s)
- `entropy_buy_threshold`: Soglia entropia BUY (0.50-0.70)
- `entropy_sell_threshold`: Soglia entropia SELL (0.30-0.50)

#### Risk Management
- `position_cooldown`: Cooldown posizioni (600-1800s)
- `max_daily_trades`: Max trade giornalieri (3-8)
- `profit_multiplier`: Moltiplicatore TP (1.5-3.0)
- `risk_percent`: Percentuale rischio (0.008-0.020)

#### Trailing Stop
- `activation_pips`: Pips attivazione (50-150)
- `step_pips`: Step pips (25-75)
- `lock_percentage`: Percentuale blocco (0.3-0.8)

## 🎛️ Utilizzo Avanzato

### Personalizzazione Scenario

```python
# Modifica config.py
CUSTOM_SCENARIO = {
    "description": "Scenario personalizzato",
    "symbols": ["EURUSD", "GBPUSD"],
    "parameter_ranges": {
        "risk_percent": {"min": 0.010, "max": 0.015, "step": 0.001}
    },
    "fitness_weights": {
        "return": 0.4,
        "drawdown": 0.3,
        "win_rate": 0.3
    }
}
```

### Ottimizzazione Personalizzata

```python
from parameter_optimizer import QuantumParameterOptimizer
from backtest_engine import BacktestConfig, The5ersRules

# Configura parametri
config = get_default_config()
backtest_config = BacktestConfig(
    start_date="2024-01-01",
    end_date="2024-06-30",
    initial_balance=100000,
    symbols=["EURUSD", "GBPUSD"]
)

# Avvia ottimizzazione
optimizer = QuantumParameterOptimizer(config, backtest_config, the5ers_rules)
results = optimizer.optimize_grid_search(max_combinations=500)
```

## 📊 Analisi Risultati

### Generazione Report

```python
from results_analyzer import ResultsAnalyzer

# Carica risultati
analyzer = ResultsAnalyzer(results_file="results/optimization_results.json")

# Genera report completo
analyzer.generate_comprehensive_report("reports/")

# Ottieni raccomandazioni
recommendations = analyzer.get_optimization_recommendations()

# Esporta migliore configurazione
best_config = analyzer.export_best_config("best_config.json")
```

### Confronto Scenari

```python
from results_analyzer import compare_optimization_results

# Confronta risultati di diversi scenari
compare_optimization_results([
    "results/conservative_step1.json",
    "results/aggressive_step2.json",
    "results/scaling_optimized.json"
], "comparisons/")
```

## 📈 Interpretazione Risultati

### Metriche Principali

- **Fitness Score**: Punteggio combinato di performance
- **The5ers Score**: Punteggio specifico per regole The5ers
- **Return %**: Rendimento percentuale
- **Win Rate**: Percentuale trade vincenti
- **Max Drawdown**: Massimo drawdown
- **Sharpe Ratio**: Rapporto rischio-rendimento

### Compliance The5ers

- ✅ **Step1 Achieved**: Target 8% raggiunto
- ✅ **Step2 Achieved**: Target 5% raggiunto  
- ✅ **Scaling Achieved**: Target 10% raggiunto
- ❌ **Daily Loss Violated**: Perdita giornaliera > 5%
- ❌ **Total Loss Violated**: Perdita totale > 10%
- ✅ **Min Profitable Days**: Almeno 3 giorni profittevoli

## 🔍 Troubleshooting

### Problemi Comuni

1. **Errore "ModuleNotFoundError"**
   ```bash
   pip install numpy pandas matplotlib seaborn scipy scikit-learn
   ```

2. **Dati storici mancanti**
   - Il sistema genera dati sintetici per default
   - Per dati reali, posiziona i CSV in `data/`

3. **Ottimizzazione lenta**
   - Riduci `max_combinations` in `config.py`
   - Usa meno simboli per test rapidi

4. **Errori di memoria**
   - Riduci `population_size` per algoritmi genetici
   - Usa meno generazioni

### Performance Tips

- **Parallelizzazione**: Usa `parallel_jobs=4` in config
- **Cache**: I risultati vengono automaticamente cachati
- **Filtri**: Usa `max_combinations` per limitare test
- **Simboli**: Inizia con 2-3 simboli per test rapidi

## 📋 Checklist Pre-Ottimizzazione

- [ ] Configurazione simboli corretta
- [ ] Date di backtest appropriate
- [ ] Parametri range ragionevoli
- [ ] Spazio disco sufficiente per risultati
- [ ] Tempo di esecuzione stimato accettabile

## 🎯 Strategia di Ottimizzazione Consigliata

### Fase 1: Esplorazione Rapida
```python
# Test rapido con pochi parametri
scenario = "conservative_step1"
max_combinations = 100
symbols = ["EURUSD"]
```

### Fase 2: Ottimizzazione Mirata
```python
# Ottimizzazione approfondita sui parametri migliori
scenario = "balanced_all_steps"
max_combinations = 500
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
```

### Fase 3: Validazione
```python
# Test su periodo diverso per validazione
start_date = "2024-07-01"
end_date = "2024-12-31"
```

## 📞 Supporto

Per problemi o domande:
1. Controlla i log in `logs/`
2. Verifica la configurazione in `config.py`
3. Consulta la documentazione del codice
4. Apri un issue nel repository

## 🔄 Prossimi Sviluppi

- [ ] Integrazione dati MT5 in tempo reale
- [ ] Ottimizzazione multi-obiettivo avanzata
- [ ] Dashboard web interattiva
- [ ] Notifiche automatiche risultati
- [ ] Backup cloud risultati

---

**Nota**: Questo sistema è progettato specificamente per la The5ers High Stakes Challenge. Adattare parametri e regole per altri broker o challenge.
