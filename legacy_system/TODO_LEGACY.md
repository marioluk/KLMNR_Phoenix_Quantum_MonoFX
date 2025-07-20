# 📋 TODO LEGACY SYSTEM - THE5ERS QUANTUM TRADING SYSTEM
## Lista Prioritizzata per Sistema Monolitico

---

## 🚨 **CRITICAL - PRODUZIONE IMMEDIATA**

### **P1 - Testing e Validazione**
- [ ] **Test Connessione MT5 Demo** - Verificare login/password/server The5ers
- [ ] **Test Simboli Disponibili** - Confermare EURUSD, GBPUSD, USDJPY, XAUUSD, NAS100
- [ ] **Test Spread Control** - Verificare soglie spread durante diverse sessioni
- [ ] **Test Position Sizing** - Validare calcoli con diversi balance demo
- [ ] **Test Drawdown Protection** - Simulare scenari -2% e -5%

### **P1 - Backup e Deployment**  
- [x] **✅ SISTEMATO: Organizzazione Configurazioni** - File config ora in `config/`
- [x] **✅ SISTEMATO: Path Backtest Corretti** - Tools backtest salvano in `config/`
- [ ] **Backup Sistema Completo** - Copiare file .py e .json in cartella separata
- [ ] **Validazione Configurazione** - Test caricamento config JSON
- [ ] **Test Avvio Sistema** - Verificare inizializzazione senza errori
- [ ] **Log Directory Setup** - Creare cartella `logs/` e verificare permessi
- [ ] **Emergency Stop Test** - Verificare Ctrl+C e shutdown automatico

---

## ⚡ **HIGH - OTTIMIZZAZIONI PRE-LIVE**

### **P2 - Performance e Stabilità**
- [ ] **Buffer Size Optimization** - Testare valori 50, 75, 100, 150 per buffer_size
- [ ] **Signal Quality Analysis** - Analizzare bias BUY/SELL su 1000+ segnali demo
- [ ] **Cooldown Tuning** - Ottimizzare position_cooldown (1800s) e signal_cooldown (300s)
- [ ] **Memory Usage Monitor** - Verificare crescita memoria su run 24h
- [ ] **Connection Stability** - Test riconnessione automatica MT5

### **P2 - Risk Management Fine-Tuning**
- [ ] **Position Size Validation** - Confermare calcoli pip value per tutti i simboli
- [ ] **Margin Safety Test** - Verificare limite 80% margine libero
- [ ] **SL/TP Distance Check** - Validare distanze minime per ogni simbolo
- [ ] **Trailing Stop Logic** - Test attivazione e step del trailing stop
- [ ] **Max Daily Trades** - Confermare limite 5 trades/giorno

---

## 🔧 **MEDIUM - MIGLIORAMENTI SISTEMA**

### **P3 - Logging e Monitoring**
- [ ] **Enhanced Heartbeat** - Aggiungere timestamp e durata operazione
- [ ] **Error Categorization** - Classificare errori: Network, Broker, Logic, Config
- [ ] **Performance Metrics Export** - Salvare metriche in JSON per analisi esterna
- [ ] **Alert System** - Email/notification per drawdown warning e hard limits
- [ ] **Daily Report Generator** - Summary automatico fine giornata

### **P3 - Configuration Enhancements**
- [ ] **Multi-Config Support** - Gestire config diversi per demo/live/test
- [ ] **Symbol-Specific Overrides** - Override parametri quantistici per simbolo
- [ ] **Session Management** - Diversi parametri per sessioni Tokyo/London/NY
- [ ] **Config Validation Tool** - Script separato per validazione JSON
- [ ] **Hot Config Reload** - Ricaricamento config senza restart (se possibile)

---

## 🛠️ **LOW - FUTURE ENHANCEMENTS**

### **P4 - Code Quality**
- [ ] **Type Hints Completion** - Aggiungere type hints mancanti
- [ ] **Docstring Enhancement** - Documentare tutti i metodi pubblici
- [ ] **Code Comments Review** - Aggiornare commenti obsoleti
- [ ] **Variable Naming** - Standardizzare naming conventions
- [ ] **Dead Code Removal** - Rimuovere codice commentato inutile

### **P4 - Additional Features**
- [ ] **Partial Position Closing** - Chiusura parziale a profit intermedi
- [ ] **News Event Filter** - Skip trading durante news ad alto impatto
- [ ] **Correlation Matrix** - Evitare posizioni correlate simultanee
- [ ] **Volatility Breakout Filter** - Skip trading in mercati troppo volatili
- [ ] **Weekend Gap Protection** - Gestione gap di apertura lunedì

---

## 🏥 **MAINTENANCE - ONGOING**

### **Manutenzione Settimanale**
- [ ] **Log File Cleanup** - Gestire rotazione e archiviazione log
- [ ] **Performance Review** - Analisi metriche settimanali
- [ ] **Config Backup** - Backup configurazioni modificate
- [ ] **System Health Check** - Verifica integrità file e connessioni
- [ ] **Market Condition Review** - Adattamento parametri a nuove condizioni

### **Manutenzione Mensile**
- [ ] **Deep Performance Analysis** - Analisi completa sharpe, drawdown, win rate
- [ ] **Parameter Optimization** - Test A/B su parametri critici
- [ ] **Risk Model Validation** - Verifica aderenza modello rischio
- [ ] **Broker Condition Check** - Verifica spread medi, execution quality
- [ ] **System Upgrade Evaluation** - Valutazione necessità aggiornamenti

---

## 🚨 **EMERGENCY PROCEDURES**

### **Scenari di Emergenza**
- [ ] **Hard Stop Procedure** - Procedura immediata stop sistema
- [ ] **Manual Position Management** - Chiusura manuale posizioni aperte
- [ ] **Config Recovery** - Ripristino configurazione da backup
- [ ] **Data Backup Recovery** - Ripristino log e metriche
- [ ] **Broker Communication** - Contatti diretti per problemi critici

### **Rollback Procedures**
- [ ] **System State Snapshot** - Salvare stato sistema pre-modifiche
- [ ] **Quick Rollback Script** - Script automatico ripristino
- [ ] **Config Version Control** - Tracking modifiche configurazione
- [ ] **Emergency Contacts** - Lista contatti per supporto urgente
- [ ] **Downtime Minimization** - Procedure restart rapido

---

## 📊 **TESTING CHECKLIST PRE-LIVE**

### **Demo Trading Phase (7-14 giorni)**
- [ ] **Connection Stability** - Test connessione MT5 per periodo esteso
- [ ] **Signal Generation** - Confermare generazione segnali su tutti i simboli
- [ ] **Position Execution** - Verificare apertura/chiusura posizioni
- [ ] **Risk Controls** - Test trigger protezioni drawdown
- [ ] **Performance Baseline** - Stabilire baseline performance demo

### **Live Migration Checklist**
- [ ] **Config Switch** - Aggiornare login/server da demo a live
- [ ] **Initial Capital Verification** - Confermare balance account live
- [ ] **Risk Parameters Validation** - Ricontrollare % rischio su balance reale
- [ ] **System Monitoring Setup** - Attivare monitoraggio continuo
- [ ] **Emergency Stop Ready** - Verificare procedure stop immediato

---

## 🔍 **MONITORING TARGETS**

### **KPI da Monitorare**
- [ ] **Win Rate Target**: >60%
- [ ] **Profit Factor Target**: >1.5
- [ ] **Max Drawdown Limit**: <-3%
- [ ] **Daily Trades**: <5 per giorno
- [ ] **Signal Quality**: Bias BUY/SELL <80%/20%

### **Alert Thresholds**
- [ ] **Drawdown Warning**: -1.5%
- [ ] **Drawdown Critical**: -2.5%
- [ ] **Win Rate Drop**: <50% su 20+ trades
- [ ] **Execution Errors**: >5% rejection rate
- [ ] **Connection Issues**: >30s disconnesso

---

## 💾 **BACKUP STRATEGY**

### **File da Backuppare**
- [ ] **Sistema Principale**: `PRO-THE5ERS-QM-PHOENIX-GITCOP.py`
- [ ] **Configurazione**: `PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json`
- [ ] **Log Critici**: Ultimi 7 giorni di log
- [ ] **Metriche**: Export dati performance
- [ ] **Screenshots**: Config MT5 e setup broker

### **Backup Schedule**
- [ ] **Giornaliero**: Log e metriche del giorno
- [ ] **Settimanale**: Backup completo sistema
- [ ] **Pre-Modifica**: Snapshot prima di ogni cambio
- [ ] **Mensile**: Archivio completo con performance
- [ ] **Pre-Live**: Backup completo prima del passaggio live

---

## 🎯 **SUCCESS CRITERIA**

### **Obiettivi The5ers Step 1**
- [ ] **Profit Target**: +8% in 30 giorni ✅
- [ ] **Max Daily Loss**: Rispettare limite -5% ✅
- [ ] **Max Total Loss**: Rispettare limite -10% ✅
- [ ] **Consistency**: Win rate mensile >60% ✅
- [ ] **Risk Management**: Max drawdown <-3% ✅

### **Sistema Legacy Success**
- [ ] **Uptime**: >99% disponibilità sistema
- [ ] **Zero Critical Bugs**: Nessun errore bloccante
- [ ] **Config Stability**: Configurazione stabile senza modifiche
- [ ] **Performance Predictability**: Metriche in linea con attese
- [ ] **Migration Readiness**: Sistema pronto per passaggio a modulare

---

*Last Updated: 20 Luglio 2025*  
*Priority: P1=Critical, P2=High, P3=Medium, P4=Low*  
*Status: 🚨=Urgent, ⚡=Important, 🔧=Normal, 🛠️=Future*
