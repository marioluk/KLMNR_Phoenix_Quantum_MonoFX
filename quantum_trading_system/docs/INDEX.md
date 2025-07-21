# Quantum Trading System - Indice Globale Documentazione

## Sezioni Principali
- [Architettura](REFERENCE/ARCHITECTURE.md)
- [Confronto Legacy vs Quantum](REFERENCE/REFACTORING_COMPARISON.md)
- [Refactoring Guide](REFERENCE/refactoring_guide.md)
- [TODO Roadmap](REFERENCE/todo.md)

## Moduli Tecnici
- [Engine](MODULES/engine.md)
- [Risk](MODULES/risk.md)
- [Metrics](MODULES/metrics.md)
- [Config](MODULES/config.md)
- [Trading](MODULES/trading.md)
- [Brokers](MODULES/brokers.md)
- [Utils](MODULES/utils.md)

## Guide Operative
- [Guida Installazione](GUIDES/setup.md)
- [Guida Multi-Broker](GUIDES/multi_broker.md)
- [Daily Updater](GUIDES/README_DAILY_UPDATER.md)
- [Avvio Automatico](GUIDES/README_AVVIO_AUTOMATICO.md)

## Configurazione
- [Guida Configurazione Broker](CONFIGURATION/CONFIGURAZIONE_BROKER_GUIDE.md)
- [Broker Config Guide](CONFIGURATION/broker_config_guide.md)

---

# Esportazione PDF/HTML della documentazione

## PDF (consigliato: VS Code Markdown PDF)
1. Installa l'estensione "Markdown PDF" in VS Code
2. Apri il file da esportare (es. ARCHITECTURE.md)
3. Premi F1 e seleziona `Markdown PDF: Export (pdf)`

## HTML (consigliato: Docsify o Pandoc)
- Docsify: https://docsify.js.org/
- Pandoc:
  ```sh
  pandoc ARCHITECTURE.md -o ARCHITECTURE.html
  pandoc INDEX.md -o DOCUMENTAZIONE_QUANTUM.html
  ```

## Suggerimenti
- Per una documentazione navigabile, esporta `INDEX.md` come homepage
- Puoi unire più file Markdown in un unico PDF/HTML con Pandoc:
  ```sh
  pandoc INDEX.md REFERENCE/ARCHITECTURE.md MODULES/engine.md ... -o quantum_system.pdf
  ```

---
Per supporto o personalizzazioni, chiedi pure!
