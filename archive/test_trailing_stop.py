"""
Test unitario/simulazione per trailing stop logica
"""
def test_trailing_stop_activation(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence):
    """
    Simula una posizione long con trailing stop e verifica attivazione e aggiornamento SL.
    Args:
        entry_price: Prezzo di ingresso
        take_profit: Livello TP
        trailing_activation_pct: Percentuale profitto per attivazione trailing (es. 0.5)
        trailing_distance_pct: Distanza trailing stop dal massimo profitto (es. 0.3)
        price_sequence: Lista di prezzi simulati (es. [entry, ..., max, ..., tp])
    Returns:
        Lista di tuple (prezzo, sl_attuale, attivato)
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

def test_trailing_stop_activation_short(entry_price, take_profit, trailing_activation_pct, trailing_distance_pct, price_sequence):
    """
    Simula una posizione short con trailing stop e verifica attivazione e aggiornamento SL.
    Args:
        entry_price: Prezzo di ingresso
        take_profit: Livello TP (inferiore all'entry)
        trailing_activation_pct: Percentuale profitto per attivazione trailing (es. 0.5)
        trailing_distance_pct: Distanza trailing stop dal massimo profitto (es. 0.3)
        price_sequence: Lista di prezzi simulati (es. [entry, ..., min, ..., tp])
    Returns:
        Lista di tuple (prezzo, sl_attuale, attivato)
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

if __name__ == "__main__":
    print("\n--- Test trailing stop ---")
    entry = 100.0
    tp = 110.0
    activation_pct = 0.5  # 50% profitto
    distance_pct = 0.3    # trailing stop a 30% dal massimo profitto
    prices = [100, 102, 104, 106, 108, 109, 110]  # Simulazione salita verso TP
    test_results = test_trailing_stop_activation(entry, tp, activation_pct, distance_pct, prices)
    for price, sl, attivato in test_results:
        sl_str = f"{sl:.2f}" if sl is not None else "-"
        print(f"Prezzo: {price:.2f} | SL: {sl_str} | Trailing attivo: {attivato}")

    print("\n--- Test trailing stop SHORT ---")
    entry_short = 110.0
    tp_short = 100.0
    activation_pct_short = 0.5  # 50% profitto
    distance_pct_short = 0.3    # trailing stop a 30% dal massimo profitto
    prices_short = [110, 108, 106, 104, 102, 101, 100]  # Simulazione discesa verso TP
    test_results_short = test_trailing_stop_activation_short(entry_short, tp_short, activation_pct_short, distance_pct_short, prices_short)
    for price, sl, attivato in test_results_short:
        sl_str = f"{sl:.2f}" if sl is not None else "-"
        print(f"Prezzo: {price:.2f} | SL: {sl_str} | Trailing attivo: {attivato}")
