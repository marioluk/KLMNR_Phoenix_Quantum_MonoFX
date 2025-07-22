# Avvio automatico Quantum Trading System su Windows

## Procedura consigliata con shell:startup

1. **Configura il batch**
   - Usa il file `avvio_quantum_trading.bat` nella cartella `legacy_system`.
   - Assicurati che il batch abbia percorsi relativi per lo script Python:
     ```bat
     set PY_SCRIPT="PRO-THE5ERS-QM-PHOENIX-GITCOP.py"
     ```
2. **Crea un collegamento in shell:startup**
   - Clicca col tasto destro su `avvio_quantum_trading.bat` e scegli "Crea collegamento".
   - Premi `Win+R`, digita `shell:startup` e premi Invio.
   - Incolla il collegamento nella cartella che si apre.
3. **Vantaggi**
   - Il batch viene eseguito dalla sua directory, quindi i percorsi relativi funzionano.
   - Puoi aggiornare il batch senza dover ricopiare nulla.
   - I log e i file di configurazione saranno sempre trovati.
4. **Cosa fa il batch**
   - Avvia MT5 con il percorso configurato.
   - Attende 10 secondi per il caricamento.
   - Avvia lo script Python in una shell separata, mostrando eventuali errori.

## Note aggiuntive
- Puoi aggiungere altri script al batch se necessario.
- Se vuoi avvio in background, togli `cmd /k`.
- Per assistenza o personalizzazioni, consulta la documentazione o chiedi supporto.
