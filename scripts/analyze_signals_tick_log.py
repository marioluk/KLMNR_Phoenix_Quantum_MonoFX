def parse_dict(s):
    import re
    import ast
    try:
        # Solo stringhe che iniziano con '{' sono dict validi
        if not isinstance(s, str) or not s.strip().startswith('{'):
            return {}
        # Sostituisce np.float64(xxx) con xxx (float)
        s = re.sub(r"np\.float64\(([^)]+)\)", r"\1", s)
        d = ast.literal_eval(s)
        for k, v in d.items():
            try:
                d[k] = float(v)
            except:
                d[k] = v
        return d
    except Exception as e:
        print(f"[PARSE ERROR] Stringa non parsabile: {s} | Errore: {e}")
        return {}

def main():

    # ...esistente codice di caricamento e parsing...

    # Estrai i dati dal dizionario
    indicators = df['data'].apply(parse_dict).apply(pd.Series)
    df = pd.concat([df, indicators], axis=1)
    print("\n[DEBUG] Colonne dopo il parsing:", df.columns.tolist())
    if 'signal' not in df.columns:
        print("\n[DEBUG] Esempi di dict estratti da 'data':")
        print(df['data'].head(3).tolist())
        print("\nNessun dato valido dopo il parsing dei segnali.")
        return

    # Parametri di soglia dalla config (modifica se necessario)
    BUY_SIGNAL = 0.54
    SELL_SIGNAL = 0.46
    SPIN_THRESHOLD = 0.25

    import numpy as np
    def check_expected_signal(row):
        entropy = row.get('entropy', None)
        spin = row.get('spin', None)
        confidence = row.get('confidence', None)
        if entropy is None or spin is None or confidence is None:
            return 'HOLD', 'Dati insufficienti'
        volatility = 1 + abs(spin) * entropy
        buy_thresh = BUY_SIGNAL * (1 + (volatility - 1) * 0.5)
        sell_thresh = SELL_SIGNAL * (1 - (volatility - 1) * 0.5)
        reasons = []
        # BUY
        if entropy > buy_thresh:
            if spin > SPIN_THRESHOLD * confidence:
                return 'BUY', ''
            else:
                reasons.append(f"spin={spin:.3f} <= {SPIN_THRESHOLD}*{confidence:.3f}={SPIN_THRESHOLD*confidence:.3f}")
        else:
            reasons.append(f"entropy={entropy:.3f} <= buy_thresh={buy_thresh:.3f}")
        # SELL
        if entropy < sell_thresh:
            if spin < -SPIN_THRESHOLD * confidence:
                return 'SELL', ''
            else:
                reasons.append(f"spin={spin:.3f} >= -{SPIN_THRESHOLD}*{confidence:.3f}={-SPIN_THRESHOLD*confidence:.3f}")
        else:
            reasons.append(f"entropy={entropy:.3f} >= sell_thresh={sell_thresh:.3f}")
        return 'HOLD', ' | '.join(reasons)

    # Applica la logica a ogni riga
    df[['expected_signal','fail_reason']] = df.apply(lambda row: pd.Series(check_expected_signal(row)), axis=1)

    # Mostra confronto tra segnale reale e atteso
    print('\n--- Confronto segnale reale vs atteso (prime 20 righe) ---')
    print(df[['timestamp','symbol','signal','expected_signal','fail_reason']].head(20))

    # Statistiche di match
    match = (df['signal'] == df['expected_signal']).mean()
    print(f"\nPercentuale segnali che coincidono con la logica attesa: {match*100:.2f}%")

    import pandas as pd
    import ast
    from datetime import datetime
    # Percorso del file CSV (modifica se necessario)
    CSV_PATH = 'logs/signals_tick_log.csv'
    OUTPUT_PATH = 'logs/signals_tick_log_summary.csv'


    # --- FILTRO DATA E SIMBOLO INTERATTIVO ---
    print("\n[Opzionale] Inserisci data/ora inizio (YYYY-MM-DD o YYYY-MM-DD HH:MM:SS) o lascia vuoto:")
    data_inizio = input().strip()
    print("[Opzionale] Inserisci data/ora fine (YYYY-MM-DD o YYYY-MM-DD HH:MM:SS) o lascia vuoto:")
    data_fine = input().strip()
    print("[Opzionale] Inserisci uno o più simboli separati da virgola (es: GBPUSD,ETHUSD) o lascia vuoto per tutti:")
    simboli_input = input().strip()

    df = pd.read_csv(CSV_PATH, header=None, names=['timestamp', 'symbol', 'data', 'reason'])
    # Salta la prima riga se contiene header (es. 'timestamp' nella colonna timestamp)
    if str(df.iloc[0]['timestamp']).lower() == 'timestamp':
        df = df.iloc[1:].reset_index(drop=True)
    print("\n[DEBUG] Prime 10 righe del DataFrame caricato dal CSV:")
    print(df.head(10))
    # Converte la colonna timestamp in datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Applica filtro data se specificato
    if data_inizio:
        # Se solo data, considera tutto il giorno
        if len(data_inizio) == 10:
            start = pd.to_datetime(data_inizio + ' 00:00:00')
        else:
            start = pd.to_datetime(data_inizio)
        df = df[df['timestamp'] >= start]
    if data_fine:
        if len(data_fine) == 10:
            end = pd.to_datetime(data_fine + ' 23:59:59')
        else:
            end = pd.to_datetime(data_fine)
        df = df[df['timestamp'] <= end]

    # Applica filtro simbolo se specificato
    if simboli_input:
        simboli = [s.strip().upper() for s in simboli_input.split(',') if s.strip()]
        df = df[df['symbol'].str.upper().isin(simboli)]

    if df.empty:
        print("\nNessun dato trovato per i filtri selezionati.")
        return

    # Estrai i dati dal dizionario
    indicators = df['data'].apply(parse_dict).apply(pd.Series)
    df = pd.concat([df, indicators], axis=1)
    print("\n[DEBUG] Colonne dopo il parsing:", df.columns.tolist())
    if 'signal' not in df.columns:
        print("\n[DEBUG] Esempi di dict estratti da 'data':")
        print(df['data'].head(3).tolist())
        print("\nNessun dato valido dopo il parsing dei segnali.")
        return
    # Statistiche per segnale
    print('--- Statistiche per segnale ---')
    print(df['signal'].value_counts())
    print('\n--- Motivazioni per segnale ---')
    print(df.groupby(['signal', 'reason']).size())
    print('\n--- Medie indicatori per segnale ---')
    print(df.groupby('signal')[['entropy', 'spin', 'confidence']].mean())
    print('\n--- Esempi HOLD ---')
    print(df[df['signal']=='HOLD'].head(10))
    print('\n--- Esempi di segnali scartati (prime 10 HOLD con motivazione) ---')
    print(df[df['expected_signal'] != df['signal']][['timestamp','symbol','signal','expected_signal','fail_reason']].head(10))

    # Salva riepilogo in un nuovo CSV
    summary = df.groupby(['signal', 'reason']).agg({
        'timestamp': 'count',
        'entropy': 'mean',
        'spin': 'mean',
        'confidence': 'mean'
    }).rename(columns={'timestamp': 'count'})
    summary = summary.reset_index()
    summary.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSalvato riepilogo in {OUTPUT_PATH}")
    print(summary)

if __name__ == '__main__':
    main()
