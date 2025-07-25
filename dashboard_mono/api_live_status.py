import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify
from flask import request
from phoenix_quantum_monofx_program import QuantumTradingSystem
import threading
import time

app = Flask(__name__)

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'config_autonomous_challenge_production_ready.json'))
system = QuantumTradingSystem(config_path)

# Avvia il sistema in un thread separato
threading.Thread(target=system.start, daemon=True).start()

@app.route('/api/live_status', methods=['GET'])
def live_status():
    """Restituisce lo stato live del sistema in formato JSON"""
    status = system.get_live_status()
    return jsonify(status)

# Endpoint per lo storico operazioni
@app.route('/api/trade_history', methods=['GET'])
def trade_history():
    """Restituisce lo storico operazioni filtrato"""
    history = system.get_trade_history()
    symbol = request.args.get('symbol')
    type_ = request.args.get('type')
    from_time = request.args.get('from_time', type=int)
    to_time = request.args.get('to_time', type=int)

    def match(trade):
        if symbol and trade.get('symbol') != symbol:
            return False
        if type_ and trade.get('type') != type_:
            return False
        if from_time and trade.get('time') < from_time:
            return False
        if to_time and trade.get('time') > to_time:
            return False
        return True

    filtered = [trade for trade in history if match(trade)]
    return jsonify(filtered)

# Endpoint per metriche di performance
@app.route('/api/performance_metrics', methods=['GET'])
def performance_metrics():
    """Restituisce metriche di performance globali e per simbolo"""
    history = system.get_trade_history()
    symbol = request.args.get('symbol')
    from_time = request.args.get('from_time', type=int)
    to_time = request.args.get('to_time', type=int)

    def match(trade):
        if symbol and trade.get('symbol') != symbol:
            return False
        if from_time and trade.get('time') < from_time:
            return False
        if to_time and trade.get('time') > to_time:
            return False
        return True

    filtered = [trade for trade in history if match(trade)]

    # Calcolo metriche
    total_trades = len(filtered)
    wins = [t for t in filtered if t.get('profit', 0) > 0]
    losses = [t for t in filtered if t.get('profit', 0) < 0]
    win_rate = round(len(wins) / total_trades * 100, 2) if total_trades else 0.0
    total_profit = round(sum(t.get('profit', 0) for t in filtered), 2)
    gross_profit = sum(t.get('profit', 0) for t in wins)
    gross_loss = abs(sum(t.get('profit', 0) for t in losses))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss else None
    # Max drawdown (approssimato)
    equity_curve = []
    eq = 0.0
    for t in filtered:
        eq += t.get('profit', 0)
        equity_curve.append(eq)
    max_drawdown = 0.0
    peak = 0.0
    for e in equity_curve:
        if e > peak:
            peak = e
        dd = peak - e
        if dd > max_drawdown:
            max_drawdown = dd
    max_drawdown = round(max_drawdown, 2)

    metrics = {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'total_profit': total_profit,
        'max_drawdown': max_drawdown
    }
    return jsonify(metrics)

# Endpoint per segnali quantum
@app.route('/api/quantum_signals', methods=['GET'])
def quantum_signals():
    """Restituisce segnali quantum reali per ogni simbolo configurato"""
    signals = {}
    for symbol in system.config_manager.symbols:
        # Ottieni buffer tick
        ticks = list(system.engine.tick_buffer.get(symbol, []))
        # Calcola entropia
        deltas = tuple(t['delta'] for t in ticks if abs(t['delta']) > 1e-10)
        entropia = system.engine.calculate_entropy(deltas) if deltas else 0.0
        # Calcola spin e confidenza
        spin, confidence = system.engine.calculate_spin(ticks)
        # Calcola trend
        trend = 'BULLISH' if spin > 0 else 'BEARISH' if spin < 0 else 'NEUTRAL'
        # Calcola volatilità quantistica
        volatility = 1 + abs(spin) * entropia
        # Segnale attuale
        signal, price = system.engine.get_signal(symbol, for_trading=False)
        signals[symbol] = {
            'entropia': round(entropia, 3),
            'spin': round(spin, 3),
            'confidence': round(confidence, 3),
            'trend': trend,
            'volatility': round(volatility, 3),
            'signal': signal,
            'price': price,
            'timestamp': int(time.time())
        }
    return jsonify(signals)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# --- ENDPOINTS ORDINI MANUALI ---
@app.route('/api/order', methods=['POST'])
def order():
    """
    Invia un ordine manuale (buy/sell) con parametri: symbol, type, size, sl, tp
    """
    data = request.json
    symbol = data.get('symbol')
    type_ = data.get('type')  # 'BUY' o 'SELL'
    size = data.get('size')
    sl = data.get('sl')
    tp = data.get('tp')
    result = system.send_manual_order(symbol, type_, size, sl, tp)
    return jsonify(result)

@app.route('/api/order/modify', methods=['POST'])
def order_modify():
    """
    Modifica SL/TP di una posizione aperta
    """
    data = request.json
    ticket = data.get('ticket')
    sl = data.get('sl')
    tp = data.get('tp')
    result = system.modify_order(ticket, sl, tp)
    return jsonify(result)

@app.route('/api/order/close', methods=['POST'])
def order_close():
    """
    Chiude manualmente una posizione
    """
    data = request.json
    ticket = data.get('ticket')
    result = system.close_order(ticket)
    return jsonify(result)

@app.route('/api/performance_metrics', methods=['GET'])
def performance_metrics_advanced():
    """Restituisce dati aggregati per tutti i grafici avanzati della dashboard"""
    # Recupera i dati reali dal sistema, oppure mock temporanei
    equity_history = system.get_equity_history() if hasattr(system, 'get_equity_history') else []
    drawdown_history = system.get_drawdown_history() if hasattr(system, 'get_drawdown_history') else []
    drawdown_limits = {"soft": -0.05, "hard": -0.10}
    pl_history = system.get_pl_history() if hasattr(system, 'get_pl_history') else []
    symbol_performance = system.get_symbol_performance() if hasattr(system, 'get_symbol_performance') else []

    return jsonify({
        "equity_history": equity_history,
        "drawdown_history": drawdown_history,
        "drawdown_limits": drawdown_limits,
        "pl_history": pl_history,
        "symbol_performance": symbol_performance
    })
