from flask import Blueprint, render_template, request, jsonify
from .metrics import MetricsCalculator
from .utils import deduplicate_pnl_history
import os
from .mt5_connector import MT5Connector

## Blueprint Flask
dashboard_bp = Blueprint('dashboard', __name__)

# Route diagnostica trading
@dashboard_bp.route('/diagnostics')
def diagnostics():
    # Popola tabella motivi blocco trade con dati reali dai deals MT5
    trade_decision_table = []
    trade_history = mt5c.get_trade_history() if mt5c and mt5c.connected else []
    for t in trade_history[-100:]:
        # Motivo blocco: se profit negativo, evidenzia come "Perdita"; se positivo, "Profitto"; altrimenti "Neutro"
        detail = "Profitto" if t.get('profit', 0) > 0 else ("Perdita" if t.get('profit', 0) < 0 else "Neutro")
        extra = f"Volume: {t.get('volume', 0)}, Commissione: {t.get('commission', 0)}, Swap: {t.get('swap', 0)}"
        trade_decision_table.append({
            'timestamp': str(t.get('time', '')),
            'symbol': t.get('symbol', ''),
            'step': t.get('type', ''),
            'detail': detail,
            'extra': extra
        })
    # Parametri quantum da config
    quantum_cfg = account_info.get('quantum_params', {}) if account_info else {}
    buy_entropy = quantum_cfg.get('entropy_thresholds', {}).get('buy_signal', 0.54)
    sell_entropy = quantum_cfg.get('entropy_thresholds', {}).get('sell_signal', 0.46)
    spin_threshold = quantum_cfg.get('spin_threshold', 0.25)
    min_spin_samples = quantum_cfg.get('min_spin_samples', 23)
    spin_window = quantum_cfg.get('spin_window', 67)
    signal_cooldown = quantum_cfg.get('signal_cooldown', 600)
    return render_template('diagnostics.html',
        trade_decision_table=trade_decision_table,
        buy_entropy=buy_entropy,
        sell_entropy=sell_entropy,
        spin_threshold=spin_threshold,
        min_spin_samples=min_spin_samples,
        spin_window=spin_window,
        signal_cooldown=signal_cooldown
    )
"""
Definizione delle route Flask, importando metriche e utilità.
"""
from flask import Blueprint, render_template, request, jsonify
from .metrics import MetricsCalculator
from .utils import deduplicate_pnl_history
import os
from .mt5_connector import MT5Connector

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', 'config_autonomous_challenge_production_ready.json')
try:
    mt5c = MT5Connector(CONFIG_PATH)
    account_info = mt5c.get_account_info() or {}
    positions = mt5c.get_positions() or []
    orders = mt5c.get_orders() or []
except Exception as e:
    account_info = {}
    positions = []
    orders = []
def get_mt5_status_info():
    info = {
        'connessione': 'OK' if mt5c and mt5c.connected else 'FALLITA',
        'account': account_info.get('login', '-') if account_info else '-',
        'server': account_info.get('server', '-') if account_info else '-',
        'saldo': account_info.get('balance', 0) if account_info else 0,
        'equity': account_info.get('equity', 0) if account_info else 0,
        'posizioni_aperte': len(positions) if positions else 0,
        'errore': getattr(mt5c, 'last_error', None)
    }
    return info

def build_metrics():
    # Metriche base da account
    metrics = {
        'balance': account_info.get('balance', 0),
        'equity': account_info.get('equity', 0),
        'profit': account_info.get('profit', 0),
        'positions_count': len(positions),
        'orders_count': len(orders),
    }
    # Recupera storico trades
    trade_history = mt5c.get_trade_history() if mt5c and mt5c.connected else []
    # Calcolo P&L totale
    total_pnl = sum(t.get('profit', 0) for t in trade_history)
    metrics['total_pnl'] = total_pnl
    # Calcolo Win Rate
    wins = sum(1 for t in trade_history if t.get('profit', 0) > 0)
    losses = sum(1 for t in trade_history if t.get('profit', 0) < 0)
    total_trades = wins + losses
    metrics['win_rate'] = (wins / total_trades * 100) if total_trades > 0 else 0.0
    # Calcolo Max Drawdown (approssimato)
    balance_curve = []
    balance = account_info.get('balance', 0)
    for t in trade_history:
        balance += t.get('profit', 0)
        balance_curve.append(balance)
    max_drawdown = 0.0
    peak = None
    for b in balance_curve:
        if peak is None or b > peak:
            peak = b
        dd = (peak - b)
        if dd > max_drawdown:
            max_drawdown = dd
    metrics['max_drawdown'] = max_drawdown
    return metrics

def build_signals_timeline():
    # Placeholder: puoi popolare con logica reale se hai segnali
    return []



@dashboard_bp.route('/dashboard')
def dashboard():
    metrics_norm = MetricsCalculator(build_metrics()).ensure_all_metrics()
    percent_signals_executed = 0.0
    signals_timeline = build_signals_timeline()
    mt5_warning = getattr(mt5c, 'last_error', None)
    if metrics_norm.get('quantum_signals', {}).get('total', 0) > 0 and signals_timeline:
        executed_signals = sum(1 for s in signals_timeline if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE')
        percent_signals_executed = (executed_signals / metrics_norm['quantum_signals']['total'] * 100)
    return render_template('dashboard.html', metrics=metrics_norm, percent_signals_executed=percent_signals_executed, mt5_warning=mt5_warning)

@dashboard_bp.route('/mt5_status')
def mt5_status():
    mt5_info = get_mt5_status_info()
    return render_template('mt5_status.html', mt5_info=mt5_info)
@dashboard_bp.route('/')
def home():
    metrics_norm = MetricsCalculator(build_metrics()).ensure_all_metrics()
    percent_signals_executed = 0.0
    signals_timeline = build_signals_timeline()
    mt5_warning = getattr(mt5c, 'last_error', None)
    if metrics_norm.get('quantum_signals', {}).get('total', 0) > 0 and signals_timeline:
        executed_signals = sum(1 for s in signals_timeline if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE')
        percent_signals_executed = (executed_signals / metrics_norm['quantum_signals']['total'] * 100)
    pnl_source = metrics_norm.get('pnl_source', 'MT5')
    return render_template('home.html', metrics=metrics_norm, percent_signals_executed=percent_signals_executed, mt5_warning=mt5_warning, pnl_source=pnl_source)

@dashboard_bp.route('/performance')
def performance():
    metrics_norm = MetricsCalculator(build_metrics()).ensure_all_metrics()
    # Dummy chart se mancante
    if 'performance_chart' not in metrics_norm:
        from datetime import datetime
        metrics_norm['performance_chart'] = {
            'dates': [datetime.now().strftime('%Y-%m-%d')],
            'pnl': [0.0]
        }
    return render_template('performance.html', metrics=metrics_norm)

# Puoi aggiungere qui anche le altre route (home, performance, ecc.)

# Route API: segnali non eseguiti (dummy)
from flask import jsonify

@dashboard_bp.route('/api/unexecuted_signals')
def api_unexecuted_signals():
    # Qui puoi popolare con segnali reali se disponibili
    return jsonify({'success': True, 'rows': build_signals_timeline()})

# --- API placeholder per evitare 404 ---
@dashboard_bp.route('/api/run_signals_vs_trades_report', methods=['POST'])
def api_run_signals_vs_trades_report():
    data = request.get_json(force=True, silent=True) or {}
    print("[API] run_signals_vs_trades_report", data)
    return jsonify({'success': True, 'message': 'API run_signals_vs_trades_report non implementata', 'data': data})

@dashboard_bp.route('/api/generate_signals_tick_log', methods=['POST'])
def api_generate_signals_tick_log():
    data = request.get_json(force=True, silent=True) or {}
    print("[API] generate_signals_tick_log", data)
    return jsonify({'success': True, 'message': 'API generate_signals_tick_log non implementata', 'data': data})

@dashboard_bp.route('/api/archive_and_cleanup_logs', methods=['POST'])
def api_archive_and_cleanup_logs():
    data = request.get_json(force=True, silent=True) or {}
    print("[API] archive_and_cleanup_logs", data)
    return jsonify({'success': True, 'message': 'API archive_and_cleanup_logs non implementata', 'data': data})

@dashboard_bp.route('/api/run_block_reasons_report', methods=['POST'])
def api_run_block_reasons_report():
    data = request.get_json(force=True, silent=True) or {}
    print("[API] run_block_reasons_report", data)
    return jsonify({'success': True, 'message': 'API run_block_reasons_report non implementata', 'data': data})

# Route pagina Metriche Avanzate (placeholder)
@dashboard_bp.route('/quantum_metrics')
def quantum_metrics():
    metrics_norm = MetricsCalculator(build_metrics()).ensure_all_metrics()
    percent_signals_executed = 0.0
    signals_timeline = build_signals_timeline()
    daily_percent_signals_executed = {}
    weekly_percent_signals_executed = {}
    if metrics_norm.get('quantum_signals', {}).get('total', 0) > 0 and signals_timeline:
        executed_signals = sum(1 for s in signals_timeline if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE')
        percent_signals_executed = (executed_signals / metrics_norm['quantum_signals']['total'] * 100)
        daily_percent_signals_executed = {'2025-08-01': 80, '2025-08-02': 75, '2025-08-03': 90}
        weekly_percent_signals_executed = {'2025-W31': 82, '2025-W32': 88}
    return render_template('quantum_metrics.html',
        metrics=metrics_norm,
        percent_signals_executed=percent_signals_executed,
        daily_percent_signals_executed=daily_percent_signals_executed,
        weekly_percent_signals_executed=weekly_percent_signals_executed)
@dashboard_bp.route('/advanced_metrics')
def advanced_metrics():
    metrics_norm = MetricsCalculator(build_metrics()).ensure_all_metrics()
    return render_template('advanced_metrics.html', metrics=metrics_norm)
