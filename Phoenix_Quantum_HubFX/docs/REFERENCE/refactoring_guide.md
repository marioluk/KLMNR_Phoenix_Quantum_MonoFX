
# Refactoring Guide

## Principi di Refactoring
- Separazione delle responsabilità tra moduli
- Minimizzazione delle dipendenze
- Scrivere funzioni pure dove possibile
- Utilizzare test automatici per ogni componente

## Esempio di refactoring
Prima:
```python
def process(data):
    # logica e gestione dati insieme
    ...
```
Dopo:
```python
def normalize(data):
    ...
def calculate_signals(normalized):
    ...
```

## Best Practice
- Documentare ogni funzione con docstring
- Usare type hinting per chiarezza
- Refactoring incrementale e test continuo

---
Questa guida è collegata ai moduli tecnici e agli esempi pratici.
