# 🔧 GUIDA USO CONFIG SELECTOR

## 🎯 **SELEZIONE DINAMICA CONFIGURAZIONI THE5ERS**

Il sistema `config_selector.py` permette di scegliere dinamicamente quale configurazione JSON utilizzare per i backtest, invece di essere legati al file hardcoded `PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json`.

---

## 📋 **FUNZIONALITÀ PRINCIPALI**

### **1. Rilevamento Automatico:**
- Trova tutti i file `*config*.json` nella directory
- Analizza automaticamente tipo e aggressività
- Classifica come Step 1, Step 2, Conservative, etc.

### **2. Menu Interattivo:**
- Tabella comparativa con tutte le opzioni
- Dettagli su simboli, risk%, trades/giorno
- Conferma prima della selezione

### **3. Analisi Intelligente:**
- Calcolo automatico dell'aggressività
- Estrazione parametri chiave
- Validazione configurazioni

---

## 🚀 **ESEMPI D'USO**

### **1. Launcher Principale:**
```bash
cd backtest_clean
python the5ers_launcher.py
# Opzione 10: Selezione configurazione
```

### **2. Backtest con Config Specifica:**
```bash
python the5ers_launcher.py
# Opzione 2: Backtest integrato
# Scegli "1" per selezione interattiva
```

### **3. Test Diretto:**
```bash
python config_selector.py
# Menu completo con test
```

---

## 📊 **OUTPUT TIPO**

```
🎯 SELEZIONE CONFIGURAZIONE THE5ERS
================================================================================

#   Tipo            File                                Simboli  Risk%    Trades   Aggressività
------------------------------------------------------------------------------------------
1   Step 1          PRO-THE5ERS-QM-PHOENIX-GITCOP-c... 6        0.150%   5        🟡 Moderate
2   Step 2          config_step2_conservative.json     6        0.150%   5        🟢 Conservative  
3   Conservative    config_conservative_step1.json     5        0.100%   3        🟢 Conservative
4   Ultra Conservative config_ultra_conservative_s... 3        0.080%   2        🟢 Conservative

Trovati 4 file di configurazione

👉 Seleziona configurazione (1-4, 0=annulla): 2

✅ Selezionata: config_step2_conservative.json
📁 Percorso: c:\GitRepos\The5ers\backtest_clean\config_step2_conservative.json
🎯 Tipo: Step 2
💱 Simboli: EURUSD, GBPUSD, USDJPY...
⚖️ Aggressività: 🟢 Conservative

❓ Confermi la selezione? (y/n): y
```

---

## ⚙️ **INTEGRAZIONE SISTEMA**

### **File Aggiornati:**
- `integrated_backtest.py` - Supporto config dinamiche
- `the5ers_launcher.py` - Menu opzione 10
- `config_selector.py` - Modulo core

### **Compatibilità:**
- ✅ Tutti i backtest esistenti
- ✅ Sistema comparative analysis  
- ✅ Custom period backtest
- ✅ Master analyzer

---

## 🎯 **VANTAGGI**

### **Flessibilità:**
- Switch rapido tra Step 1/Step 2
- Test configurazioni conservative vs aggressive
- Confronto parametri senza modificare file

### **Produzione:**
- Facile passaggio da test a live
- Backup automatico configurazioni
- Rollback rapido in caso di problemi

### **Sviluppo:**
- Test A/B su configurazioni
- Validazione parametri automatica
- Analytics comparativo

---

## 📝 **FORMATI FILE SUPPORTATI**

Il sistema rileva automaticamente file con pattern:
- `*config*.json`
- `*CONFIG*.json`
- `PRO-THE5ERS*.json`
- `*STEP*.json`

E li analizza per estrarre:
- Tipo strategia (Step 1/2, Conservative, etc.)
- Numero simboli configurati
- Risk percentage per trade
- Max trades giornalieri
- Livello aggressività (Conservative/Moderate/Aggressive)

---

## 🏆 **READY FOR PRODUCTION**

Il sistema è completamente integrato e pronto per:
- ✅ **Switch configurazioni** in tempo reale
- ✅ **Test multiple strategie** senza modifiche manuali
- ✅ **Deploy sicuro** con validazione automatica
- ✅ **Backup/Restore** configurazioni rapido

**🚀 Ora puoi gestire infinite configurazioni The5ers dinamicamente!**
