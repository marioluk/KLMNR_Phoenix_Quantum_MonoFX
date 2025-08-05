
import MetaTrader5 as mt5
import csv
from datetime import datetime

# Configura login MT5
LOGIN = 12345678  # Sostituisci con il tuo login
PASSWORD = "password"  # Sostituisci con la tua password
SERVER = "YourBroker-Server"  # Sostituisci con il tuo server

if not mt5.initialize(login=LOGIN, password=PASSWORD, server=SERVER):
    print(f"Errore inizializzazione MT5: {mt5.last_error()}")
    exit(1)

start_date = datetime(2025, 8, 1)
end_date = datetime.now()
orders = mt5.history_orders_get(start_date, end_date)
if orders is None:
    print(f"Errore recupero ordini: {mt5.last_error()}")
    mt5.shutdown()
    exit(1)

csv_path = "..\\logs\\mt5_orders.csv"
with open(csv_path, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tipo", "Simbolo", "Volume", "Orario di Apertura", "Orario di Chiusura", "Stato"])
    count = 0
    for o in orders:
        tipo = "buy" if o.type == mt5.ORDER_TYPE_BUY else "sell" if o.type == mt5.ORDER_TYPE_SELL else str(o.type)
        simbolo = o.symbol
        volume = o.volume_initial
        open_time = datetime.fromtimestamp(o.time_setup).strftime("%Y-%m-%d %H:%M:%S") if o.time_setup else ""
        close_time = datetime.fromtimestamp(o.time_done).strftime("%Y-%m-%d %H:%M:%S") if o.time_done else ""
        stato = "filled" if o.state == mt5.ORDER_STATE_FILLED else str(o.state)
        writer.writerow([tipo, simbolo, volume, open_time, close_time, stato])
        count += 1

mt5.shutdown()
print(f"Ordini esportati in {csv_path}. Totale ordini: {count}")
