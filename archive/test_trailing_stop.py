"""
Test unitario/simulazione per trailing stop logica
"""

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
    return results
    return results

        print(f"Prezzo: {price:.2f} | SL: {sl_str} | Trailing attivo: {attivato}")
