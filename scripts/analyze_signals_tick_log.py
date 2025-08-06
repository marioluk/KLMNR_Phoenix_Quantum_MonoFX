import pandas as pd
import ast

# Percorso del file CSV (modifica se necessario)
CSV_PATH = 'logs/signals_tick_log.csv'

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
    df = pd.read_csv(CSV_PATH, header=None, names=['timestamp', 'symbol', 'data', 'reason'])
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

if __name__ == '__main__':
    main()
