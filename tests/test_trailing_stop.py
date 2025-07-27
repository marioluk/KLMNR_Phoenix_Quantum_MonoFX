import pytest

# ...existing code from archive/test_trailing_stop.py...

import pytest

def simulate_trailing_stop_long(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence):
    """
    Simula una posizione long con trailing stop e verifica attivazione e aggiornamento SL.
    Restituisce lista di tuple (prezzo, sl_attuale, attivato)
    """
    sl = None
    activated = False
    results = []
    max_profit = 0
    for price in price_sequence:
        profit = price - entry_price
        max_profit = max(max_profit, profit)
        activation_level = (take_profit - entry_price) * trailing_activation_pct
        trailing_distance = (take_profit - entry_price) * trailing_distance_pct
        if not activated and profit >= activation_level:
            activated = True
            sl = price - trailing_distance
        elif activated:
            # Aggiorna SL solo se nuovo massimo
            if profit > (sl - entry_price):
                sl = price - trailing_distance
        results.append((price, sl, activated))
    return results

@pytest.mark.parametrize("entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence, expected", [
    (100, 110, 0.5, 0.3, [100, 102, 105, 108, 110],
     [(100, None, False), (102, None, False), (105, 102.0, True), (108, 105.0, True), (110, 107.0, True)]),
    (100, 110, 0.5, 0.3, [100, 101, 102, 103, 104],
     [(100, None, False), (101, None, False), (102, None, False), (103, None, False), (104, None, False)]),
])
def test_trailing_stop_activation(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence, expected):
    results = simulate_trailing_stop_long(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence)
    assert results == expected


def simulate_trailing_stop_short(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence):
    """
    Simula una posizione short con trailing stop e verifica attivazione e aggiornamento SL.
    Restituisce lista di tuple (prezzo, sl_attuale, attivato)
    """
    sl = None
    activated = False
    results = []
    max_profit = 0
    for price in price_sequence:
        profit = entry_price - price  # In short, profit aumenta se il prezzo scende
        max_profit = max(max_profit, profit)
        activation_level = (entry_price - take_profit) * trailing_activation_pct
        trailing_distance = (entry_price - take_profit) * trailing_distance_pct
        if not activated and profit >= activation_level:
            activated = True
            sl = price + trailing_distance
        elif activated:
            # Aggiorna SL solo se nuovo massimo
            if profit > (entry_price - sl):
                sl = price + trailing_distance
        results.append((price, sl, activated))
    return results

@pytest.mark.parametrize("entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence, expected", [
    (110, 100, 0.5, 0.3, [110, 108, 106, 104, 100],
     [(110, None, False), (108, None, False), (106, None, False), (104, 107.0, True), (100, 103.0, True)]),
    (110, 100, 0.5, 0.3, [110, 109, 108, 107, 106],
     [(110, None, False), (109, None, False), (108, None, False), (107, None, False), (106, None, False)]),
])
def test_trailing_stop_activation_short(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence, expected):
    results = simulate_trailing_stop_short(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence)
    assert results == expected
