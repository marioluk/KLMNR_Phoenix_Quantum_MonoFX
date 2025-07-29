import os
import csv
from typing import List, Dict

def read_trade_decision_report(max_rows: int = 100) -> List[Dict]:
    """Legge le ultime righe dal file trade_decision_report.csv e restituisce una lista di dict."""
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'trade_decision_report.csv')
    if not os.path.exists(report_path):
        return []
    rows = []
    with open(report_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Garantisce compatibilità con vecchi file senza colonna 'extra'
            if 'extra' not in row:
                row['extra'] = ''
            rows.append(row)
    # Ritorna solo le ultime max_rows
    return rows[-max_rows:]
