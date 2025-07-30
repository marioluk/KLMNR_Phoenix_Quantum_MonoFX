#!/usr/bin/env python3
"""
block_reasons_report.py - Analisi motivi di blocco segnali (report orario, daily, aggregabile)

- Analizza il file CSV dei segnali (logs/signals_tick_log.csv)
- Conta i motivi di blocco per ogni ora (default) o per giorno
- Output: CSV e JSON (per dashboard/analisi)

Usage:
    python block_reasons_report.py [--period hourly|daily] [--output-dir DIR]

"""
import os
import sys
import csv
import json
from collections import defaultdict
from datetime import datetime

LOG_PATH = os.path.join("logs", "signals_tick_log.csv")
DEFAULT_OUTPUT_DIR = "logs"


def parse_timestamp(ts):
    # Supporta vari formati timestamp
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except Exception:
            continue
    return None

def aggregate_block_reasons(period="hourly", output_dir=DEFAULT_OUTPUT_DIR):
    if not os.path.exists(LOG_PATH):
        print(f"❌ Log file non trovato: {LOG_PATH}")
        return
    counts = defaultdict(lambda: defaultdict(int))  # {period_key: {reason: count}}
    with open(LOG_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            motivo = row.get('motivo_blocco', '').strip()
            esito = row.get('esito', '').strip().upper()
            ts = parse_timestamp(row.get('timestamp', ''))
            if not motivo or esito != 'SCARTATO' or not ts:
                continue
            if period == "hourly":
                key = ts.strftime("%Y-%m-%d %H:00")
            elif period == "daily":
                key = ts.strftime("%Y-%m-%d")
            else:
                key = ts.strftime("%Y-%m-%d %H:00")
            counts[key][motivo] += 1
    # Output CSV
    csv_path = os.path.join(output_dir, f"block_reasons_report_{period}.csv")
    all_reasons = set(r for v in counts.values() for r in v)
    all_reasons = sorted(all_reasons)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([period] + all_reasons)
        for key in sorted(counts):
            row = [key] + [counts[key].get(r, 0) for r in all_reasons]
            writer.writerow(row)
    # Output JSON
    json_path = os.path.join(output_dir, f"block_reasons_report_{period}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(counts, f, indent=2, ensure_ascii=False)
    print(f"✅ Report motivi di blocco generato: {csv_path}\n✅ Anche in JSON: {json_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analisi motivi di blocco segnali (orario/daily)")
    parser.add_argument('--period', choices=['hourly', 'daily'], default='hourly', help='Periodo di aggregazione')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help='Cartella output')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    aggregate_block_reasons(args.period, args.output_dir)
