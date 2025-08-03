"""
Modelli dati per trade, segnali, ecc.
"""

class Trade:
    def __init__(self, timestamp, pnl, symbol, direction, commission=0.0, swap=0.0):
        self.timestamp = timestamp
        self.pnl = pnl
        self.symbol = symbol
        self.direction = direction
        self.commission = commission
        self.swap = swap

class Signal:
    def __init__(self, timestamp, symbol, direction, esito):
        self.timestamp = timestamp
        self.symbol = symbol
        self.direction = direction
        self.esito = esito
