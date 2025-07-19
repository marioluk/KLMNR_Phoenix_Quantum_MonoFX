# KLMNR Phoenix Quantum Multi-Broker System
## Guida Configurazione Avvio Automatico Server

### 📁 Script Disponibili

| Script | Descrizione | Uso |
|--------|-------------|-----|
| `start_multi_broker_production.bat` | Avvio interattivo con finestra | Avvio manuale, debug |
| `start_multi_broker_service.bat` | Avvio silenzioso background | Cronjob, script automatici |
| `stop_multi_broker.bat` | Arresto sicuro del sistema | Spegnimento controllato |
| `monitor_multi_broker.bat` | Monitoraggio stato sistema | Controllo stato |
| `watchdog_multi_broker.bat` | **Auto-restart con monitoraggio** | **🎯 PRODUZIONE** |

---

## 🚀 Setup Avvio Automatico (CONSIGLIATO)

### Opzione 1: Task Scheduler Windows (MIGLIORE)

1. **Apri Task Scheduler**
   ```
   Tasto Windows + R → taskschd.msc → Enter
   ```

2. **Crea Nuova Attività**
   - Click destro su "Libreria Utilità di pianificazione"
   - "Crea attività..."

3. **Scheda Generale**
   - Nome: `KLMNR Phoenix Quantum Multi-Broker`
   - Descrizione: `Sistema trading multi-broker con auto-restart`
   - Seleziona: `Esegui indipendentemente dalla connessione dell'utente`
   - Seleziona: `Esegui con i privilegi più elevati`

4. **Scheda Trigger**
   - Nuovo trigger → `All'avvio`
   - Ritarda attività di: `2 minuti`

5. **Scheda Azioni**
   - Nuova azione → `Avvia programma`
   - Programma: `C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\watchdog_multi_broker.bat`
   - Inizia da: `C:\KLMNR_Projects\KLMNR_Phoenix_Quantum`

6. **Scheda Condizioni**
   - Deseleziona: `Avvia l'attività solo se il computer è alimentato da rete elettrica`

7. **Scheda Impostazioni**
   - Seleziona: `Consenti l'esecuzione dell'attività su richiesta`
   - Seleziona: `Se l'attività è già in esecuzione: Non avviare una nuova istanza`

---

### Opzione 2: Avvio Automatico Semplice

**Per test o avvio manuale:**
```batch
# Avvio normale
C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\start_multi_broker_production.bat

# Avvio background
C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\start_multi_broker_service.bat
```

---

## 📊 Monitoraggio e Controllo

### Controllo Stato
```batch
C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\monitor_multi_broker.bat
```

### Arresto Sistema
```batch
C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\stop_multi_broker.bat
```

### Log Files
```
logs/system_startup.log     - Log avvio/arresto sistema
logs/multi_broker_output.log - Output completo sistema
logs/watchdog.log           - Log del watchdog auto-restart
logs/trading/               - Log trading per broker
```

---

## ⚙️ Configurazione Avanzata

### Parametri Watchdog
Il watchdog controlla ogni **5 minuti** se il sistema è attivo e lo riavvia automaticamente se necessario.

### Modifica Intervallo Controllo
Modifica nel file `watchdog_multi_broker.bat` la riga:
```batch
timeout /t 300 /nobreak >nul    # 300 = 5 minuti
```

### Avvio con Parametri Specifici
Modifica nel file di avvio la riga:
```batch
python multi_broker_launcher.py --broker THE5ERS  # Solo The5ers
python multi_broker_launcher.py --dry-run         # Modalità test
```

---

## 🔧 Troubleshooting

### Sistema Non Si Avvia
1. Controlla logs: `logs/system_startup.log`
2. Verifica Python: `python --version`
3. Testa manualmente: `start_multi_broker_production.bat`

### MetaTrader5 Non Connette
1. Verifica percorsi MT5 nei file `config/broker_*.json`
2. Controlla credenziali broker
3. Testa connessione MT5 manuale

### Watchdog Non Funziona
1. Esegui Task Scheduler come Amministratore
2. Verifica permessi directory `C:\KLMNR_Projects\KLMNR_Phoenix_Quantum`
3. Controlla log: `logs/watchdog.log`

---

## 🎯 Configurazione Produzione Consigliata

**Setup Finale per Server di Produzione:**

1. ✅ Usa `watchdog_multi_broker.bat` con Task Scheduler
2. ✅ Avvio automatico all'avvio Windows
3. ✅ Auto-restart ogni 5 minuti se necessario  
4. ✅ Log completi per monitoraggio
5. ✅ Controllo stato con `monitor_multi_broker.bat`

**Il sistema sarà completamente autonomo e si riavvierà automaticamente in caso di problemi!**
