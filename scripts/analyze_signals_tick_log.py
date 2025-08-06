def parse_dict(s):
    try:
        # Rimuove np.float64 e converte in float
        s = s.replace('np.float64', '')
        d = ast.literal_eval(s)
        for k, v in d.items():
            if isinstance(v, tuple) and len(v) == 1:
                d[k] = float(v[0])
            elif isinstance(v, float) or isinstance(v, int):
                d[k] = float(v)
            else:
                try:
                    d[k] = float(str(v))
                except:
                    pass
        return d
    except Exception as e:
        return {}

def main():
    import pandas as pd
    import ast
    from datetime import datetime
    # Percorso del file CSV (modifica se necessario)
    CSV_PATH = 'logs/signals_tick_log.csv'
    OUTPUT_PATH = 'logs/signals_tick_log_summary.csv'


    # --- FILTRO DATA E SIMBOLO INTERATTIVO ---
    print("\n[Opzionale] Inserisci data/ora inizio (YYYY-MM-DD HH:MM:SS) o lascia vuoto:")
    data_inizio = input().strip()
    print("[Opzionale] Inserisci data/ora fine (YYYY-MM-DD HH:MM:SS) o lascia vuoto:")
    data_fine = input().strip()
    print("[Opzionale] Inserisci uno o più simboli separati da virgola (es: GBPUSD,ETHUSD) o lascia vuoto per tutti:")
    simboli_input = input().strip()

    df = pd.read_csv(CSV_PATH, header=None, names=['timestamp', 'symbol', 'data', 'reason'])
    # Converte la colonna timestamp in datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Applica filtro data se specificato
    if data_inizio:
        df = df[df['timestamp'] >= pd.to_datetime(data_inizio)]
    if data_fine:
        df = df[df['timestamp'] <= pd.to_datetime(data_fine)]

    # Applica filtro simbolo se specificato
    if simboli_input:
        simboli = [s.strip().upper() for s in simboli_input.split(',') if s.strip()]
        df = df[df['symbol'].str.upper().isin(simboli)]

    # Estrai i dati dal dizionario
    indicators = df['data'].apply(parse_dict).apply(pd.Series)
    df = pd.concat([df, indicators], axis=1)
    # Statistiche per segnale
    print('--- Statistiche per segnale ---')
    print(df['signal'].value_counts())
    print('\n--- Motivazioni per segnale ---')
    print(df.groupby(['signal', 'reason']).size())
    print('\n--- Medie indicatori per segnale ---')
    print(df.groupby('signal')[['entropy', 'spin', 'confidence']].mean())
    print('\n--- Esempi HOLD ---')
    print(df[df['signal']=='HOLD'].head(10))

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
