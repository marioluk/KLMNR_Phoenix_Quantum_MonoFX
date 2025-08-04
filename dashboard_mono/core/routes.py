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
    mt5c = None
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
    global orders
    # --- IMPORT ORDINI DA FILE CSV (se orders è vuoto) ---
    import csv
    import os
    if not orders:
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'archive', 'mt5_orders.csv')
        if os.path.exists(csv_path):
            print(f"[IMPORT ORDERS] Carico ordini da {csv_path}")
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                orders = [dict(row) for row in reader]
            print(f"[IMPORT ORDERS] {len(orders)} ordini importati")
    # Metriche base da account
    metrics = {
        'balance': account_info.get('balance', 0),
        'equity': account_info.get('equity', 0),
        'profit': account_info.get('profit', 0),
        'positions_count': len(positions),
        'positions_open': len(positions),
        'orders_count': len(orders),
        'drawdown_recovery_time': 0.0,
        # Forza sempre initial_balance a 5000
        'initial_balance': 5000
    }
    # Recupera storico trades
    trade_history = mt5c.get_trade_history() if mt5c and mt5c.connected else []
    # Stampa solo i trade filtrati, non tutto lo storico raw
    # Calcolo P&L totale
    exclude_comments = [
        'INITIAL_DEPOSIT', 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'INTERNAL_TRANSFER', 'FEE', 'COMMISSION', 'ADJUSTMENT'
    ]
    trade_history_filtered = [
        t for t in trade_history
        if (
            isinstance(t, dict)
            and not any(str(t.get('comment', '')).upper().startswith(ex) for ex in exclude_comments)
            and t.get('symbol', '') != ''
            and t.get('volume', 0) > 0
        )
    ]
    total_pnl = sum(t.get('profit', 0) for t in trade_history_filtered)
    total_profit = sum(t.get('profit', 0) for t in trade_history_filtered if t.get('profit', 0) > 0)
    total_loss = sum(abs(t.get('profit', 0)) for t in trade_history_filtered if t.get('profit', 0) < 0)
    metrics['total_pnl'] = total_pnl
    metrics['total_profit'] = total_profit
    metrics['total_loss'] = total_loss
    # Calcolo Win Rate
    wins = sum(1 for t in trade_history_filtered if t.get('profit', 0) > 0)
    losses = sum(1 for t in trade_history_filtered if t.get('profit', 0) < 0)
    total_trades = len(trade_history_filtered)
    metrics['total_trades'] = total_trades
    metrics['profit_factor'] = (total_profit / total_loss) if total_loss > 0 else 0.0
    metrics['win_rate'] = (wins / total_trades * 100) if total_trades > 0 else 0.0
    # Calcolo Max Drawdown (approssimato) e Drawdown Recovery Time con log dettagliato
    balance_curve = []
    time_curve = []
    pnl_curve = []
    hourly_curve = {}
    symbol_curve = {}
    # Il capitale iniziale deve essere 5000 (non il balance attuale né il balance da account_info)
    balance = 5000
    for t in trade_history_filtered:
        profit = t.get('profit', 0)
        balance += profit
        balance_curve.append(balance)
        time_curve.append(t.get('time', None))
        pnl_curve.append(profit)
        # Raggruppa per ora
        time_val = t.get('time', None)
        if time_val:
            try:
                from datetime import datetime
                dt = datetime.fromtimestamp(float(time_val)) if isinstance(time_val, (int, float)) else datetime.fromisoformat(str(time_val))
                hour = dt.strftime('%Y-%m-%d %H:00')
                hourly_curve[hour] = hourly_curve.get(hour, 0) + profit
            except Exception:
                pass
        # Raggruppa per simbolo
        symbol = t.get('symbol', None)
        if symbol:
            symbol_curve[symbol] = symbol_curve.get(symbol, 0) + profit
    print("DEBUG balance_curve:", balance_curve)
    print("DEBUG time_curve:", time_curve)
    max_dd = 0.0
    peak_idx = 0
    trough_idx = 0
    peak = None
    for i, b in enumerate(balance_curve):
        if peak is None or b > peak:
            peak = b
            peak_idx = i
        dd = peak - b
        if dd > max_dd:
            max_dd = dd
            trough_idx = i
    print(f"DEBUG peak_idx={peak_idx}, peak={balance_curve[peak_idx] if balance_curve else None}")
    print(f"DEBUG trough_idx={trough_idx}, trough={balance_curve[trough_idx] if balance_curve else None}")
    recovery_idx = None
    for i in range(trough_idx + 1, len(balance_curve)):
        if balance_curve[i] >= peak:
            recovery_idx = i
            break
    print(f"DEBUG recovery_idx={recovery_idx}, recovery={balance_curve[recovery_idx] if recovery_idx is not None else None}")
    if recovery_idx is not None and time_curve[peak_idx] and time_curve[recovery_idx]:
        from datetime import datetime
        t1 = time_curve[peak_idx]
        t2 = time_curve[recovery_idx]
        print(f"DEBUG t1={t1}, t2={t2}")
        if t1 == t2:
            metrics['drawdown_recovery_time'] = '-'
        elif isinstance(t1, (int, float)) and isinstance(t2, (int, float)):
            minutes = (t2 - t1) / 60
            metrics['drawdown_recovery_time'] = round(minutes, 2) if minutes > 0 else '-'
        else:
            try:
                dt1 = datetime.fromtimestamp(float(t1)) if isinstance(t1, (int, float)) else datetime.fromisoformat(str(t1))
                dt2 = datetime.fromtimestamp(float(t2)) if isinstance(t2, (int, float)) else datetime.fromisoformat(str(t2))
                minutes = (dt2 - dt1).total_seconds() / 60
                metrics['drawdown_recovery_time'] = round(minutes, 2) if minutes > 0 else '-'
            except Exception as e:
                print("DEBUG errore conversione timestamp:", e)
                metrics['drawdown_recovery_time'] = '-'
    else:
        metrics['drawdown_recovery_time'] = '-'
    max_drawdown = 0.0
    peak = None
    for b in balance_curve:
        if peak is None or b > peak:
            peak = b
        dd = (peak - b)
        if dd > max_drawdown:
            max_drawdown = dd
    metrics['max_drawdown'] = max_drawdown
    # Calcolo volatilità portafoglio (deviazione standard della balance_curve)
    import math
    if len(balance_curve) > 1:
        mean_balance = sum(balance_curve) / len(balance_curve)
        variance = sum((b - mean_balance) ** 2 for b in balance_curve) / (len(balance_curve) - 1)
        volatility = math.sqrt(variance)
    else:
        volatility = 0.0
    metrics['volatility'] = round(volatility, 2)
    print(f"DEBUG drawdown_recovery_time={metrics['drawdown_recovery_time']} min, max_drawdown={max_drawdown}, volatility={volatility}")

    # --- METRICHE AVANZATE ---
    import numpy as np
    # Sharpe Ratio e Sortino Ratio
    returns = np.array([t.get('profit', 0) for t in trade_history_filtered])
    if len(returns) > 1:
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0.0
        sharpe_ratio = mean_return / std_return if std_return > 0 else 0.0
        sortino_ratio = mean_return / downside_std if downside_std > 0 else 0.0
    else:
        sharpe_ratio = 0.0
        sortino_ratio = 0.0
    metrics['sharpe_ratio'] = round(sharpe_ratio, 2)
    metrics['sortino_ratio'] = round(sortino_ratio, 2)

    # Trade Duration Media (in minuti) usando ordini MT5
    durations = []
    from datetime import datetime
    def to_timestamp(val):
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        try:
            return datetime.strptime(str(val), '%Y.%m.%d %H:%M:%S').timestamp()
        except Exception:
            pass
        try:
            return datetime.strptime(str(val), '%Y-%m-%d %H:%M:%S').timestamp()
        except Exception:
            pass
        try:
            return datetime.strptime(str(val), '%d.%m.%Y %H:%M').timestamp()
        except Exception:
            pass
        try:
            return datetime.strptime(str(val), '%d.%m.%Y %H:%M:%S').timestamp()
        except Exception:
            pass
        try:
            return datetime.fromisoformat(str(val)).timestamp()
        except Exception:
            pass
        try:
            from dateutil import parser
            return parser.parse(str(val)).timestamp()
        except Exception:
            pass
        return None

    # Usa la lista ordini MT5 (orders) se disponibile
    orders_data = orders if orders else []
    print("[DEBUG ORDERS_RAW] primi 10 ordini:")
    for idx, o in enumerate(orders_data[:10]):
        print(f"  Ordine {idx}:", {k: o.get(k) for k in o.keys()})
    # Adatta parsing per report MT5: campi 'Tipo', 'Simbolo', 'Volume', 'Orario di Apertura', 'Ora', 'Stato'
    def get_val(o, keys):
        for k in keys:
            if k in o and o[k]:
                return o[k]
        return None
    # Filtra solo buy/sell filled
    orders_filled = [o for o in orders_data if get_val(o, ['Tipo','type']) in ('buy', 'sell') and get_val(o, ['Simbolo','symbol']) and get_val(o, ['Volume','volume','volume_lotto']) and get_val(o, ['Stato','state']).lower() == 'filled']
    print("[DEBUG ORDERS_FILLED]", len(orders_filled), "ordini trovati:")
    for o in orders_filled:
        print("  ", {k: o.get(k) for k in o.keys() if 'orario' in k.lower() or 'ora' in k.lower() or 'time' in k.lower() or k in ['Tipo','type','Simbolo','symbol','Volume','volume','Stato','state']})
    # Raggruppa per simbolo e volume
    from collections import defaultdict
    order_groups = defaultdict(list)
    for o in orders_filled:
        key = (get_val(o, ['Simbolo','symbol']), get_val(o, ['Volume','volume','volume_lotto']))
        order_groups[key].append(o)

    for key, group in order_groups.items():
        print(f"[DEBUG GROUP] symbol={key[0]}, volume={key[1]}, n_ordini={len(group)}")
        # Ordina per orario di apertura
        group_sorted = sorted(group, key=lambda x: to_timestamp(get_val(x, ['Orario di Apertura','Ora','open_time','Orario','Orario Apertura','Orario di apertura'])))
        for idx, o in enumerate(group_sorted):
            ts_apertura = to_timestamp(get_val(o, ['Orario di Apertura','open_time','Orario','Orario Apertura','Orario di apertura']))
            ts_chiusura = to_timestamp(get_val(o, ['Ora','Orario di Chiusura','close_time']))
            print(f"    Ordine {idx}: tipo={get_val(o,['Tipo','type'])}, ts_apertura={ts_apertura}, ts_chiusura={ts_chiusura}, raw={[get_val(o, ['Orario di Apertura','open_time','Orario','Orario Apertura','Orario di apertura']), get_val(o, ['Ora','Orario di Chiusura','close_time'])]} ")
        # Cerca coppie buy/sell consecutive
        for i in range(len(group_sorted)-1):
            o1 = group_sorted[i]
            o2 = group_sorted[i+1]
            if get_val(o1, ['Tipo','type']) == 'buy' and get_val(o2, ['Tipo','type']) == 'sell':
                ot = to_timestamp(get_val(o1, ['Orario di Apertura','open_time','Orario','Orario Apertura','Orario di apertura']))
                ct = to_timestamp(get_val(o2, ['Ora','Orario di Chiusura','close_time']))
                print(f"      [PAIR] buy_ts={ot}, sell_ts={ct}")
                if ot and ct and ct > ot:
                    duration_min = (ct - ot) / 60
                    if duration_min <= 1440:
                        durations.append(duration_min)
    metrics['avg_trade_duration'] = round(np.mean(durations), 2) if durations else 0.0
    metrics['avg_trade_duration_minutes'] = metrics['avg_trade_duration']
    if not durations:
        metrics['avg_trade_duration_note'] = 'Durata media non disponibile: dati ordini assenti o non parsabili.'
        print("[RIEPILOGO] Nessun trade con durata calcolabile dagli ordini. Controlla che la lista orders abbia i campi orario e tipo corretti.")

    # Max Consecutive Wins/Losses
    max_consec_wins = 0
    max_consec_losses = 0
    current_wins = 0
    current_losses = 0
    for t in trade_history_filtered:
        profit = t.get('profit', 0)
        if profit > 0:
            current_wins += 1
            current_losses = 0
        elif profit < 0:
            current_losses += 1
            current_wins = 0
        else:
            current_wins = 0
            current_losses = 0
        if current_wins > max_consec_wins:
            max_consec_wins = current_wins
        if current_losses > max_consec_losses:
            max_consec_losses = current_losses
    metrics['max_consecutive_wins'] = max_consec_wins
    metrics['max_consecutive_losses'] = max_consec_losses

    # --- GRAFICI ---
    from datetime import datetime
    metrics['pnl_chart'] = {
        'data': [{
            'x': [datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d %H:%M') if t else None for t in time_curve],
            'y': pnl_curve,
            'type': 'bar',
            'name': 'P&L'
        }],
        'layout': {
            'title': 'P&L per trade',
            'xaxis': {'title': 'Data'},
            'yaxis': {'title': 'Profitto'}
        }
    }
    metrics['drawdown_chart'] = {
        'data': [{
            'x': [datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d %H:%M') if t else None for t in time_curve],
            'y': [max(balance_curve[:i+1]) - b for i, b in enumerate(balance_curve)],
            'type': 'scatter',
            'name': 'Drawdown'
        }],
        'layout': {
            'title': 'Drawdown',
            'xaxis': {'title': 'Data'},
            'yaxis': {'title': 'Drawdown'}
        }
    }
    metrics['balance_chart'] = {
        'data': [{
            'x': [datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d %H:%M') if t else None for t in time_curve],
            'y': balance_curve,
            'type': 'scatter',
            'name': 'Balance'
        }],
        'layout': {
            'title': 'Balance',
            'xaxis': {'title': 'Data'},
            'yaxis': {'title': 'Balance'}
        }
    }
    metrics['hourly_chart'] = {
        'data': [{
            'x': list(hourly_curve.keys()),
            'y': list(hourly_curve.values()),
            'type': 'bar',
            'name': 'P&L orario'
        }],
        'layout': {
            'title': 'P&L per ora',
            'xaxis': {'title': 'Ora'},
            'yaxis': {'title': 'Profitto'}
        }
    }
    metrics['symbols_chart'] = {
        'data': [{
            'x': list(symbol_curve.keys()),
            'y': list(symbol_curve.values()),
            'type': 'bar',
            'name': 'P&L per simbolo'
        }],
        'layout': {
            'title': 'P&L per simbolo',
            'xaxis': {'title': 'Simbolo'},
            'yaxis': {'title': 'Profitto'}
        }
    }
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
    # Passa i dati dei grafici
    return render_template(
        'dashboard.html',
        metrics=metrics_norm,
        percent_signals_executed=percent_signals_executed,
        mt5_warning=mt5_warning,
        pnl_chart=metrics_norm.get('pnl_chart'),
        drawdown_chart=metrics_norm.get('drawdown_chart'),
        balance_chart=metrics_norm.get('balance_chart'),
        hourly_chart=metrics_norm.get('hourly_chart'),
        symbols_chart=metrics_norm.get('symbols_chart')
    )

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
    return render_template(
        'home.html',
        metrics=metrics_norm,
        percent_signals_executed=percent_signals_executed,
        mt5_warning=mt5_warning,
        pnl_source=pnl_source,
        pnl_chart=metrics_norm.get('pnl_chart'),
        drawdown_chart=metrics_norm.get('drawdown_chart'),
        balance_chart=metrics_norm.get('balance_chart'),
        hourly_chart=metrics_norm.get('hourly_chart'),
        symbols_chart=metrics_norm.get('symbols_chart')
    )

@dashboard_bp.route('/performance')
def performance():
    metrics_norm = MetricsCalculator(build_metrics()).ensure_all_metrics()
    return render_template(
        'performance.html',
        metrics=metrics_norm,
        pnl_chart=metrics_norm.get('pnl_chart'),
        drawdown_chart=metrics_norm.get('drawdown_chart'),
        balance_chart=metrics_norm.get('balance_chart'),
        hourly_chart=metrics_norm.get('hourly_chart'),
        symbols_chart=metrics_norm.get('symbols_chart')
    )

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
