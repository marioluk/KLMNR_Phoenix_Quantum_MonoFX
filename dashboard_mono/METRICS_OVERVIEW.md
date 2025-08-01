# Metrics Overview – Phoenix Quantum MonoFX Dashboard

Questa tabella riassume le metriche e funzionalità attualmente disponibili nella dashboard e quelle suggerite per una Performance Analytics completa.

| Categoria                | Metrica/Funzione                        | Stato Attuale         | Note / Da Aggiungere                                      |
|--------------------------|-----------------------------------------|-----------------------|-----------------------------------------------------------|
| **P&L e Drawdown**       | P&L cumulativo                          | DISPONIBILE           | Grafico Plotly già presente                               |
|                          | Drawdown attuale e max                  | DISPONIBILE           | Grafico Plotly già presente                               |
|                          | Profit Percentage                       | DISPONIBILE           |                                                           |
|                          | Profit Factor                           | DISPONIBILE           |                                                           |
| **Trade & Segnali**      | Numero totale trade                     | DISPONIBILE           |                                                           |
|                          | Win rate globale                        | DISPONIBILE           |                                                           |
|                          | Win rate per simbolo                    | DISPONIBILE           |                                                           |
|                          | Trade timeline                          | DISPONIBILE           |                                                           |
|                          | Segnali quantum (totali, buy/sell)      | DISPONIBILE           |                                                           |
|                          | Entropy/spin medi                       | DISPONIBILE           |                                                           |
|                          | Tabella sequenza segnali                | DISPONIBILE           |                                                           |
|                          | Segnali non eseguiti                    | DISPONIBILE           | API e tabella                                             |
| **Distribuzioni**        | Performance per simbolo                  | DISPONIBILE           |                                                           |
|                          | Performance oraria                      | DISPONIBILE           |                                                           |
|                          | Grafici breakdown per simbolo/orario    | PARZIALE              | Da arricchire con heatmap, filtri, breakdown avanzato     |
| **Motivi di blocco**     | Motivo blocco segnale                   | DISPONIBILE           | Tabella e diagnostica                                     |
|                          | Report motivi di blocco aggregati       | PARZIALE              | Da migliorare: breakdown per orario, simbolo, filtro      |
| **Parametri attivi**     | Visualizzazione parametri attivi         | DA AGGIUNGERE         | Mostrare parametri di filtro attivi per ogni segnale      |
|                          | Evidenziare parametri troppo restrittivi | DA AGGIUNGERE         | Analisi storica e alert                                   |
| **Commissioni/Swap**     | Commissioni e swap                      | DA AGGIUNGERE         | Calcolo e breakdown su trade                              |
| **Pattern di errore**    | Perdite consecutive, orari critici       | DA AGGIUNGERE         | Riconoscimento pattern, alert automatici                  |
| **Reportistica**         | Download CSV/JSON report                 | DISPONIBILE           |                                                           |
|                          | Generazione report HTML/PDF              | DA AGGIUNGERE         |                                                           |
| **Notifiche/Alert**      | Notifiche drawdown, target, anomalie     | PARZIALE              | Da estendere con alert automatici e notifiche avanzate    |
| **UX/Interattività**     | Filtri avanzati, modifica parametri      | DA AGGIUNGERE         | Interazione diretta dalla dashboard                       |
| **Documentazione**       | Spiegazione motivi di blocco, best practice | DA AGGIUNGERE     | Sezione dedicata nella dashboard                          |

---

> Aggiornare questa tabella ogni volta che vengono aggiunte nuove metriche o funzionalità.

Per dettagli tecnici e implementativi, fare riferimento al codice in `dashboard_broker.py` e alla documentazione in `README.md`.
