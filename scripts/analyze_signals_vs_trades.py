import csv
import json
import os
from collections import defaultdict
from datetime import datetime

LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
SIGNALS_FILE = os.path.join(LOGS_DIR, 'signals_tick_log.csv')
BLOCKS_FILE = os.path.join(LOGS_DIR, 'block_reasons_report.csv')
TRADES_FILE = os.path.join(LOGS_DIR, 'trade_decision_report.csv')

OUTPUT_CSV = os.path.join(LOGS_DIR, 'signals_vs_trades_report.csv')
OUTPUT_JSON = os.path.join(LOGS_DIR, 'signals_vs_trades_report.json')

def parse_csv(path):
    if not os.path.isfile(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    signals = parse_csv(SIGNALS_FILE)
    blocks = parse_csv(BLOCKS_FILE)
    trades = parse_csv(TRADES_FILE)

    # Indicizza trades per (symbol, timestamp) arrotondato ai secondi
    trade_index = defaultdict(list)
    for t in trades:
        key = (t.get('symbol'), t.get('timestamp', '')[:19])
        trade_index[key].append(t)

    # Indicizza motivi di blocco per (symbol, timestamp) arrotondato ai secondi
    block_index = defaultdict(list)
    for b in blocks:
        key = (b.get('Symbol'), b.get('Timestamp', '')[:19])
        block_index[key].append(b)

    report = []
    for s in signals:
        symbol = s.get('symbol') or s.get('Symbol')
        ts = s.get('timestamp') or s.get('Timestamp')
        ts_sec = ts[:19] if ts else ''
        esito = s.get('esito') or s.get('Esito')
        motivo = s.get('motivo_blocco') or s.get('Motivo Blocco')
        # Considera solo segnali BUY/SELL
        if esito not in ('BUY', 'SELL'):
            continue
        # Cerca trade effettivo
        trade_found = False
        trade_info = None
        for t in trade_index.get((symbol, ts_sec), []):
            if t.get('esito') in ('BUY', 'SELL'):
                trade_found = True
                trade_info = t
                break
        # Cerca motivo di blocco se non c'è trade
        block_info = None
        if not trade_found:
            for b in block_index.get((symbol, ts_sec), []):
                block_info = b
                break
        report.append({
            'timestamp': ts,
            'symbol': symbol,
            'segnale': esito,
            'trade_aperto': trade_found,
            'motivo_blocco': motivo if not trade_found else '',
            'dettaglio_blocco': block_info.get('Motivo/Dettaglio') if block_info else '',
            'extra_blocco': block_info.get('Extra') if block_info else '',
            'trade_info': trade_info or {},
        })

    # Salva CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['timestamp', 'symbol', 'segnale', 'trade_aperto', 'motivo_blocco', 'dettaglio_blocco', 'extra_blocco', 'trade_info']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in report:
            row_out = row.copy()
            row_out['trade_info'] = json.dumps(row_out['trade_info'], ensure_ascii=False)
            writer.writerow(row_out)
    # Salva JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report generato: {OUTPUT_CSV}\nReport generato: {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
