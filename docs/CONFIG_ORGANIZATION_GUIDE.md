# 📂 CONFIGURAZIONI LEGACY SYSTEM - Guida Organizzazione

## 🎯 Struttura Configurazioni
```
legacy_system/
├── config/                                      # 📁 TUTTE LE CONFIGURAZIONI
│   ├── config_autonomous_high_stakes_production_ready.json  # Config attuale
│   ├── config_autonomous_high_stakes_conservative.json   # Generated autonomi
│   ├── config_autonomous_high_stakes_moderate.json
│   ├── config_autonomous_high_stakes_aggressive.json
│   ├── config_high_stakes_conservative.json             # Generated da JSON optimizer
│   ├── config_high_stakes_moderate.json
│   ├── config_high_stakes_aggressive.json
│   └── *_production_ready.json                          # Convertiti per produzione
├── backtest_mono/                             # 📁 TOOLS GENERAZIONE CONFIG
│   ├── autonomous_high_stakes_optimizer.py     # Genera config da zero
│   ├── high_stakes_optimizer.py                # Ottimizza config esistenti
│   ├── config_converter.py                     # Converte per produzione
│   ├── production_converter.py                 # Batch converter
│   └── the5ers_integrated_launcher_complete.py # Launcher unificato
└── phoenix_quantum_monofx_program.py           # Sistema principale
```

## 🚀 Uso Corretto

### **Generazione Configurazioni Nuove:**
```bash
cd legacy_system/backtest_mono
python the5ers_integrated_launcher_complete.py
# ✅ Le configurazioni saranno salvate in ../config/
```

### **Ottimizzazione Configurazioni Esistenti:**
```bash
cd legacy_system/backtest_mono
python high_stakes_optimizer.py
# ✅ Le configurazioni ottimizzate saranno salvate in ../config/
```

### **Conversione per Produzione:**
```bash
cd legacy_system/backtest_mono
python production_converter.py
# ✅ Le configurazioni pronte per produzione saranno salvate in ../config/
```

### **Avvio Sistema Legacy:**
```bash
cd legacy_system
python start_legacy.py
# ✅ Cerca automaticamente config in config/ e poi nella directory corrente
```

## 🔧 Modifiche Implementate

### **📁 Path Corretti:**
- `autonomous_high_stakes_optimizer.py`: Salva in `../config/`
- `high_stakes_optimizer.py`: Salva in `../config/`
- `config_converter.py`: Salva in `../config/`
- `production_converter.py`: Cerca in `../config/`
- `start_legacy.py`: Cerca config prima in `config/` poi in directory corrente

### **🔄 Retro-compatibilità:**
- I tools cercano prima nella nuova struttura (`../config/`)
- Fallback alla directory corrente per compatibilità
- Creazione automatica cartella `config/` se non esiste

## 📝 Note Importanti

1. **✅ SISTEMATO**: I file di configurazione non vengono più salvati nella directory principale
2. **📁 ORGANIZZAZIONE**: Tutte le configurazioni sono centralizate in `legacy_system/config/`
3. **🔄 COMPATIBILITÀ**: I tools legacy funzionano senza modifiche comportamentali
4. **🚀 PRODUZIONE**: Il sistema legacy cerca automaticamente le configurazioni nella posizione corretta

---
*Aggiornato: 20 luglio 2025 - Correzione path configurazioni sistema legacy*
