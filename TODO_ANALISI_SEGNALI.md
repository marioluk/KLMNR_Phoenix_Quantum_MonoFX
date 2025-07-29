

# ATTENZIONE: Questo file è stato accorpato nel nuovo TODO.md centrale.
# Consulta e aggiorna solo `TODO.md` nella root del progetto per la roadmap completa e aggiornata.
# Qui puoi mantenere solo note storiche, dettagli specifici o idee temporanee non ancora consolidate che non sono già in TODO.md.

---

## Idee temporanee o dettagli non ancora consolidati

## File coinvolti principali

## Note operative
- Il logging dei segnali è già tick-by-tick nel metodo `get_signal`, ma va verificata la completezza delle informazioni e la facilità di parsing per la dashboard.
- La dashboard dovrà occuparsi di aggregazione e visualizzazione, ma serve un formato dati chiaro e accessibile.
- La logica di apertura posizione è nel metodo `get_signal` e nei punti dove viene chiamato per il trading reale.
- Serve collaborazione tra log, codice di trading e dashboard per una diagnosi efficace e una visualizzazione chiara.
- L'obiettivo è rendere trasparente e facilmente analizzabile il processo di generazione e blocco dei segnali, per poter agire in modo mirato sui parametri o sulla logica.
