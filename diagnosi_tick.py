import MetaTrader5 as mt5
import time

# Connessione
if not mt5.initialize(path='C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe'):
    print('Errore inizializzazione MT5')
    exit()

if not mt5.login(25437097, password='wkchTWEO_.00', server='FivePercentOnline-Real'):
    print('Errore login MT5')
    exit()

print('=== DIAGNOSI TICK INVALIDI ===')
symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'NAS100']
max_spreads = {'EURUSD': 18, 'GBPUSD': 22, 'USDJPY': 15, 'XAUUSD': 40, 'NAS100': 35}

for symbol in symbols:
    symbol_info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    
    if not symbol_info:
        print(f'{symbol}: ❌ SIMBOLO NON TROVATO')
        continue
        
    if not tick:
        print(f'{symbol}: ❌ NESSUN TICK')
        continue
        
    spread = (tick.ask - tick.bid) / symbol_info.point
    max_spread = max_spreads.get(symbol, 20)
    
    status = '✅ OK' if spread <= max_spread else '❌ SPREAD ALTO'
    
    print(f'{symbol}: {status}')
    print(f'  Bid={tick.bid:.5f} | Ask={tick.ask:.5f}')
    print(f'  Spread={spread:.1f}p (max={max_spread}p)')
    print(f'  Time={tick.time} | Valid={tick.bid > 0 and tick.ask > 0}')
    print()

# Test connessione
account = mt5.account_info()
if account:
    print(f'Account: {account.login} | Server: {account.server}')
    print(f'Connessione: ✅ ATTIVA')
else:
    print('Connessione: ❌ PROBLEMI')

mt5.shutdown()
