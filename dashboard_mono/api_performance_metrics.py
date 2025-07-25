from flask import Blueprint, jsonify

api_performance_metrics = Blueprint('api_performance_metrics', __name__)

@api_performance_metrics.route('/api/performance_metrics', methods=['GET'])
def get_performance_metrics():
    # TODO: Sostituisci questi dati con quelli reali dal sistema di trading
    equity_history = [
        {"timestamp": "2025-07-26 10:00", "equity": 10000, "balance": 10000},
        {"timestamp": "2025-07-26 11:00", "equity": 10050, "balance": 10020},
        # ...
    ]
    drawdown_history = [
        {"timestamp": "2025-07-26 10:00", "drawdown": -0.01},
        {"timestamp": "2025-07-26 11:00", "drawdown": -0.02},
        # ...
    ]
    drawdown_limits = {"soft": -0.05, "hard": -0.10}
    pl_history = [
        {"timestamp": "2025-07-26 10:00", "pl_cumulative": 0},
        {"timestamp": "2025-07-26 11:00", "pl_cumulative": 50},
        # ...
    ]
    symbol_performance = [
        {"symbol": "EURUSD", "pl": 120, "trades": 5},
        {"symbol": "XAUUSD", "pl": -30, "trades": 2},
        # ...
    ]
    return jsonify({
        "equity_history": equity_history,
        "drawdown_history": drawdown_history,
        "drawdown_limits": drawdown_limits,
        "pl_history": pl_history,
        "symbol_performance": symbol_performance
    })
