import csv
import json
import os

# Percorso CSV segnali
csv_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'signals_tick_log.csv')
json_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'signals_tick_log.json')

if not os.path.exists(csv_path):
    print(f"File CSV non trovato: {csv_path}")
    exit(1)

signals = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Conversione numerica dei campi principali
        for k in ['entropy', 'spin', 'confidence', 'price']:
            if k in row:
                try:
                    row[k] = float(row[k])
                except Exception:
                    pass
        signals.append(row)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)

print(f"Esportazione completata: {json_path} ({len(signals)} segnali)")
