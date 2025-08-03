import json
import MetaTrader5 as mt5

class MT5Connector:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.connected = False
        self.last_error = None
        self._connect_mt5()

    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['config']['metatrader5']

    def _connect_mt5(self):
        cfg = self.config
        self.connected = mt5.initialize(
            path=cfg['path'],
            login=cfg['login'],
            password=cfg['password'],
            server=cfg['server'],
            port=cfg.get('port', 443)
        )
        if not self.connected:
            self.last_error = mt5.last_error()
            print(f"[MT5Connector] Errore connessione MT5: {self.last_error}")

    def get_account_info(self):
        if not self.connected:
            return None
        return mt5.account_info()._asdict() if mt5.account_info() else None

    def get_positions(self):
        if not self.connected:
            return []
        positions = mt5.positions_get()
        return [p._asdict() for p in positions] if positions else []

    def get_orders(self):
        if not self.connected:
            return []
        orders = mt5.orders_get()
        return [o._asdict() for o in orders] if orders else []

    def get_trade_history(self, date_from=None, date_to=None):
        """
        Restituisce la lista dei trades chiusi (deals) tra date_from e date_to.
        Se non specificato, prende tutto lo storico disponibile (ultimi 90 giorni).
        """
        import datetime
        if not self.connected:
            return []
        if date_from is None:
            date_from = datetime.datetime.now() - datetime.timedelta(days=90)
        if date_to is None:
            date_to = datetime.datetime.now()
        deals = mt5.history_deals_get(date_from, date_to)
        return [d._asdict() for d in deals] if deals else []

    def shutdown(self):
        mt5.shutdown()
        self.connected = False
