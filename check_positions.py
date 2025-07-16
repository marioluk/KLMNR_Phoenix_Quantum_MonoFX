import MetaTrader5 as mt5

# Connessione
mt5.initialize(path='C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe')
mt5.login(25437097, password='wkchTWEO_.00', server='FivePercentOnline-Real')

print("=== VERIFICA POSIZIONI APERTE ===")
positions = mt5.positions_get()

if positions:
    for pos in positions:
        print(f"Ticket: {pos.ticket}")
        print(f"Simbolo: {pos.symbol}")
        print(f"Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
        print(f"Volume: {pos.volume}")
        print(f"Prezzo apertura: {pos.price_open}")
        print(f"SL: {pos.sl}")
        print(f"TP: {pos.tp}")
        print(f"Profitto: {pos.profit:.2f} USD")
        print(f"Magic: {pos.magic}")
        print("---")
else:
    print("Nessuna posizione aperta")

# Verifica account
account = mt5.account_info()
print(f"\nBilancio: {account.balance:.2f} USD")
print(f"Equity: {account.equity:.2f} USD")
print(f"Margin: {account.margin:.2f} USD")

mt5.shutdown()
