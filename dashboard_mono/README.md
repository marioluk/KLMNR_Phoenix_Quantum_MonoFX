# =============================================================
# RIEPILOGO SCORE CONFIGURAZIONI OTTIMIZZATE
# =============================================================

Ad ogni generazione delle configurazioni (conservative, moderate, aggressive), il sistema salva un riepilogo degli score medi e totali in:
`../logs/score_summary_configurazioni.log`

**Cosa contiene il file di log:**
- Score medio e totale per ciascun livello di aggressività
- Evidenziazione automatica della configurazione con score più alto
- Nome file di ciascuna configurazione generata
- Data e ora della generazione

**Esempio di log:**
```
===== RIEPILOGO SCORE CONFIGURAZIONI GENERATE (2025-08-01T12:34:56) =====
  Conservative  | Avg Score: 68.20 | Total Score: 272.80 | File: config_autonomous_challenge_conservative_production_ready.json
⭐ Moderate     | Avg Score: 72.50 | Total Score: 362.50 | File: config_autonomous_challenge_moderate_production_ready.json
  Aggressive   | Avg Score: 70.10 | Total Score: 420.60 | File: config_autonomous_challenge_aggressive_production_ready.json

La configurazione con score medio più alto è: Moderate (config_autonomous_challenge_moderate_production_ready.json)
Puoi scegliere quale mettere in produzione tramite production_converter.py.
```

**Significato degli score:**
- Lo score medio rappresenta la qualità/efficacia della configurazione (profit factor, win rate, penalità rischio, spread, ecc.)
- Lo score totale è la somma degli score dei simboli selezionati
- La configurazione migliore viene solo evidenziata, il deploy rimane manuale

**Come scegliere la configurazione migliore:**
Consulta il file di log per confrontare gli score e scegli la configurazione più adatta alle tue esigenze tramite lo script `production_converter.py`.

**Nota:** Il log viene aggiornato ad ogni generazione, puoi consultarlo in qualsiasi momento.
# THE5ERS DASHBOARD - LEGACY SYSTEM

Dashboard web interattiva per il monitoraggio del sistema di trading legacy The5ers.

## 🚀 CARATTERISTICHE

### Monitoraggio Real-Time
- **Metriche Trading**: Profit%, P&L, Win Rate, Drawdown
- **Compliance The5ers**: Target Step 1 (8%), Drawdown (2%/5%)
- **Quantum Signals**: Analisi entropy e spin in tempo reale
- **Integrazione MT5**: Dati completi da MetaTrader5

### Grafici Interattivi
- **P&L Cumulativo**: Trend performance nel tempo
- **Drawdown**: Monitoraggio rischio con limiti
- **Balance/Equity**: Andamento account
- **Performance Oraria**: Analisi per ora del giorno
- **Performance per Simbolo**: Risultati per strumento
- **Distribuzione Segnali**: Scatter plot entropy vs spin

## 📁 STRUTTURA

```
dashboard_mono/
├── dashboard_the5ers.py          # Main dashboard application
├── start_dashboard.bat           # Launcher Windows
├── start_dashboard_debug.py      # Debug launcher
├── start_dashboard_remote.bat    # Remote access launcher
└── templates/
    └── dashboard.html            # Web interface template
```

## ⚙️ CONFIGURAZIONE AUTOMATICA

La dashboard utilizza **auto-detect** per la configurazione:

1. **Prima scelta**: `../config/config_autonomous_high_stakes_production_ready.json`
2. **Fallback**: File config nella directory corrente

## 🎮 AVVIO

### Avvio Standard
```bash
# Windows
start_dashboard.bat

# Python diretto
python dashboard_the5ers.py
```

### Avvio Debug
```bash
python start_dashboard_debug.py
```

### Accesso Remoto
```bash
start_dashboard_remote.bat
```

## 🌐 ACCESSO WEB

- **Locale**: http://127.0.0.1:5000
- **Remoto**: http://[TUO_IP]:5000

## 📊 FUNZIONALITÀ AVANZATE

### Aggiornamento Automatico
- Refresh ogni 2 secondi
- Monitoring real-time dei log
- Aggiornamento MT5 programmato

### Refresh MT5 Manuale
- Pulsante "Refresh MT5" nell'interfaccia
- Carica dati completi della challenge
- Update immediato delle metriche

### Indicatori Compliance
- ✅ **Target Raggiunto**: Profit >= 8%
- 🎯 **Target Pendente**: Profit < 8%
- ✅ **Drawdown OK**: DD < 2%
- ⚠️ **Drawdown Warning**: DD 2-5%
- 🚨 **Drawdown Critico**: DD >= 5%

## 🔧 REQUISITI

### Python Packages
```bash
pip install flask plotly pandas MetaTrader5
```

### File Necessari
- Configurazione legacy: `../config/config_autonomous_high_stakes_production_ready.json`
- Log file (auto-detect da config)
- Template HTML

## 📈 INTEGRAZIONE MT5

### Connessione Automatica
- Login automatico da configurazione
- Caricamento storia deals completa
- Calcolo metriche real-time

### Dati Supportati
- **Account Info**: Balance, Equity, Positions
- **Trading History**: Tutti i deals della challenge
- **Performance**: P&L, Drawdown, Win Rate per simbolo/ora

## 🎯 METRICHE THE5ERS

### Target Compliance
- **Step 1**: 8% profit requirement
- **Drawdown Soft**: 2% warning level
- **Drawdown Hard**: 5% danger level

### Calcoli Automatici
- **Profit %**: (Total P&L / Initial Balance) × 100
- **Win Rate**: (Winning Trades / Total Trades) × 100
- **Profit Factor**: Total Profit / Total Loss
- **Max Drawdown**: Peak-to-trough decline

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

## 🚨 TROUBLESHOOTING

### Config Non Trovato
```
❌ Config file non trovato
💡 Verificare: ../config/config_autonomous_high_stakes_production_ready.json
```

### MT5 Non Connesso
```
⚠️ MetaTrader5 non disponibile - usando solo dati log
🔧 Installare: pip install MetaTrader5
```

### Port Già in Uso
```
❌ Port 5000 già occupato
🔧 Chiudere altre dashboard o usare port diverso
```

## 🔄 CHANGELOG

### v2.0 - Legacy Integration
- Auto-detect configurazione legacy
- Path relativi per sistema legacy
- Badge "Legacy System" nell'interfaccia
- Compatibilità con nuova struttura folders

### v1.0 - Initial Release
- Dashboard web completa
- Integrazione MT5
- Grafici real-time
- Compliance monitoring

## 📝 NOTE

- **Compatibilità**: Windows con MetaTrader5
- **Browser**: Chrome, Firefox, Edge supportati
- **Performance**: Refresh automatico ogni 2 secondi
- **Sicurezza**: Accesso locale di default

## 🔗 INTEGRAZIONE SISTEMA

Questa dashboard fa parte del **sistema legacy** e si integra con:
- `../PRO-THE5ERS-QM-PHOENIX-GITCOP.py` (Main system)
- `../config/` (Configurazioni)
- `../../logs/` (File di log)

Per il **sistema moderno**, vedere `../../quantum_trading_system/`
