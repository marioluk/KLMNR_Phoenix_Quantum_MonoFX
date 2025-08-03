#!/usr/bin/env python3
"""
THE5ERS GRAPHICAL DASHBOARD
Dashboard web interattiva con grafici in tempo reale per monitoraggio The5ers
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import sys
from flask import Flask, render_template, jsonify
from dashboard_utils import read_trade_decision_report
from collections import defaultdict, deque
import plotly.graph_objs as go
import plotly.utils

# Importa MT5 per dati completi
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️  MetaTrader5 non disponibile - usando solo dati log")

class The5ersGraphicalDashboard:
    def add_test_route(self):
        @self.app.route('/test')
        def test():
            return 'Flask funziona!'
    def load_signals_from_csv(self, csv_path=None, max_rows=1000):
        """Carica i segnali dal file CSV strutturato e popola signals_timeline."""
        import csv
        import os
        if csv_path is None:
            # Default path: logs/signals_tick_log.csv nella root del progetto
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(project_root, 'logs', 'signals_tick_log.csv')
        if not os.path.exists(csv_path):
            print(f"[CSV] File non trovato: {csv_path}")
            return
        self.signals_timeline.clear()
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)[-max_rows:]
                for row in rows:
                    # Conversione tipi
                    spin = float(row['spin'])
                    if spin > 0:
                        direction = 'BUY'
                    elif spin < 0:
                        direction = 'SELL'
                    else:
                        direction = 'NEUTRAL'
                    signal = {
                        'timestamp': row['timestamp'],
                        'symbol': row['symbol'],
                        'entropy': float(row['entropy']),
                        'spin': spin,
                        'confidence': float(row['confidence']),
                        'price': float(row['price']),
                        'esito': row['esito'],
                        'direction': direction,
                        'motivo_blocco': row.get('motivo_blocco', '')
                    }
                    self.signals_timeline.append(signal)
            print(f"[CSV] Caricati {len(self.signals_timeline)} segnali da {csv_path}")
        except Exception as e:
            print(f"[CSV] Errore lettura segnali: {e}")
    def load_complete_mt5_data(self):
        """Carica tutti i dati da MT5 e aggiorna tutte le metriche e le timeline (comportamento storico)."""
        if not MT5_AVAILABLE or not self.use_mt5:
            print("[MT5] Modulo non disponibile o non abilitato, skip load_complete_mt5_data.")
            return
        try:
            account_info = mt5.account_info()
            if account_info:
                self.current_metrics['current_balance'] = account_info.balance
                self.current_metrics['current_equity'] = account_info.equity
                self.current_metrics['positions_open'] = len(mt5.positions_get() or [])
                self.balance_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'balance': account_info.balance,
                    'equity': account_info.equity
                })

            deals = mt5.history_deals_get(self.challenge_start, datetime.now())
            if deals is None:
                print("❌ Nessun deal trovato")
                return

            self.pnl_history.clear()
            self.symbol_performance.clear()
            self.hourly_performance.clear()

            cumulative_pnl = 0
            total_trades = 0
            winning_trades = 0

            for deal in deals:
                if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                    deal_time = datetime.fromtimestamp(deal.time)
                    total_trades += 1
                    cumulative_pnl += deal.profit
                    if deal.profit > 0:
                        winning_trades += 1
                    self.pnl_history.append({
                        'timestamp': deal_time.isoformat(),
                        'pnl': deal.profit,
                        'cumulative_pnl': cumulative_pnl,
                        'symbol': deal.symbol,
                        'direction': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL'
                    })
                    self.symbol_performance[deal.symbol]['pnl'] += deal.profit
                    self.symbol_performance[deal.symbol]['trades'] += 1
                    hour = deal_time.hour
                    self.hourly_performance[hour]['pnl'] += deal.profit
                    self.hourly_performance[hour]['trades'] += 1

            self.current_metrics['total_trades'] = total_trades
            self.current_metrics['winning_trades'] = winning_trades
            self.current_metrics['total_pnl'] = cumulative_pnl

            if total_trades > 0:
                self.current_metrics['win_rate'] = (winning_trades / total_trades) * 100

            if self.current_metrics['current_balance'] > 0:
                self.current_metrics['profit_percentage'] = (cumulative_pnl / self.current_metrics['current_balance']) * 100

            total_profit = sum(deal.profit for deal in deals if deal.profit > 0)
            total_loss = sum(abs(deal.profit) for deal in deals if deal.profit < 0)

            if total_loss > 0:
                self.current_metrics['profit_factor'] = total_profit / total_loss
            else:
                self.current_metrics['profit_factor'] = float('inf') if total_profit > 0 else 0

            # Calcolo Sharpe Ratio
            returns = []
            for i in range(1, len(self.pnl_history)):
                prev = self.pnl_history[i-1]['cumulative_pnl']
                curr = self.pnl_history[i]['cumulative_pnl']
                returns.append(curr - prev)
            if returns:
                avg_return = sum(returns) / len(returns)
                std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
                risk_free_rate = 0.0  # Puoi personalizzare
                if std_return > 0:
                    sharpe_ratio = (avg_return - risk_free_rate) / std_return
                else:
                    sharpe_ratio = 0.0
                self.current_metrics['sharpe_ratio'] = sharpe_ratio
                # Calcolo Sortino Ratio
                downside_returns = [r for r in returns if r < 0]
                if downside_returns:
                    downside_std = (sum((r) ** 2 for r in downside_returns) / len(downside_returns)) ** 0.5
                    if downside_std > 0:
                        sortino_ratio = (avg_return - risk_free_rate) / downside_std
                    else:
                        sortino_ratio = 0.0
                else:
                    sortino_ratio = 0.0
                self.current_metrics['sortino_ratio'] = sortino_ratio
                # Calcolo Trade Duration Media
                durations = []
                for deal in deals:
                    if hasattr(deal, 'time') and hasattr(deal, 'time_exit') and deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                        entry_time = datetime.fromtimestamp(deal.time)
                        exit_time = datetime.fromtimestamp(deal.time_exit)
                        duration = (exit_time - entry_time).total_seconds() / 60.0
                        if duration > 0:
                            durations.append(duration)
                if durations:
                    avg_duration = sum(durations) / len(durations)
                else:
                    avg_duration = 0.0
                self.current_metrics['avg_trade_duration_minutes'] = avg_duration
                # Calcolo Max Consecutive Wins/Losses
                max_wins = 0
                max_losses = 0
                current_wins = 0
                current_losses = 0
                for deal in deals:
                    if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                        if deal.profit > 0:
                            current_wins += 1
                            max_losses = max(max_losses, current_losses)
                            current_losses = 0
                        elif deal.profit < 0:
                            current_losses += 1
                            max_wins = max(max_wins, current_wins)
                            current_wins = 0
                        else:
                            max_wins = max(max_wins, current_wins)
                            max_losses = max(max_losses, current_losses)
                            current_wins = 0
                            current_losses = 0
                max_wins = max(max_wins, current_wins)
                max_losses = max(max_losses, current_losses)
                self.current_metrics['max_consecutive_wins'] = max_wins
                self.current_metrics['max_consecutive_losses'] = max_losses
            else:
                self.current_metrics['sharpe_ratio'] = 0.0
                self.current_metrics['sortino_ratio'] = 0.0

            # Ricostruisci drawdown_history per mostrare l'andamento storico
            self.drawdown_history.clear()
            if self.pnl_history:
                initial_balance = self.current_metrics.get('current_balance', 5000.0)
                max_balance = initial_balance
                for entry in self.pnl_history:
                    current_balance = initial_balance + entry['cumulative_pnl']
                    if current_balance > max_balance:
                        max_balance = current_balance
                    if max_balance > 0:
                        current_drawdown = ((max_balance - current_balance) / max_balance) * 100
                    else:
                        current_drawdown = 0.0
                    self.drawdown_history.append({
                        'timestamp': entry['timestamp'],
                        'drawdown': current_drawdown
                    })
                # Aggiorna le metriche con il max drawdown storico
                max_drawdown = max((item['drawdown'] for item in self.drawdown_history), default=0.0)
                self.current_metrics['max_drawdown'] = max_drawdown
                self.current_metrics['current_drawdown'] = self.drawdown_history[-1]['drawdown'] if self.drawdown_history else 0.0
            else:
                self.current_metrics['max_drawdown'] = 0.0
                self.current_metrics['current_drawdown'] = 0.0

            for symbol, stats in self.symbol_performance.items():
                if stats['trades'] > 0:
                    symbol_winning = sum(1 for deal in deals if deal.symbol == symbol and deal.profit > 0)
                    stats['win_rate'] = (symbol_winning / stats['trades']) * 100

            print(f"✅ Caricati {total_trades} trades da MT5")
            print(f"📊 P&L Totale: ${cumulative_pnl:.2f}")
            print(f"🎯 Profit %: {self.current_metrics['profit_percentage']:.2f}%")
        except Exception as e:
            print(f"❌ Errore caricamento dati MT5: {e}")
        # Non chiudere la connessione qui!
    def load_config(self) -> dict:
        """Carica il file di configurazione JSON e restituisce un dizionario. Se fallisce, restituisce {}."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"❌ Errore caricamento file di configurazione {self.config_file}: {e}")
            return {}
    def create_signals_sequence_table(self, max_rows=100):
        """Restituisce una lista di dict con la sequenza segnali e relativo esito."""
        # Mostra solo gli ultimi max_rows segnali
        rows = list(self.signals_timeline)[-max_rows:]
        table = []
        for s in rows:
            table.append({
                'timestamp': s['timestamp'],
                'symbol': s['symbol'],
                'direction': s['direction'],
                'entropy': s['entropy'],
                'spin': s['spin'],
                'esito': s.get('esito', 'NESSUNA AZIONE') if s.get('esito') else 'NESSUNA AZIONE',
                'motivo_blocco': s.get('motivo_blocco', ''),
                'trade_pnl': s.get('trade_pnl'),
                'trade_time': s.get('trade_time')
            })
        return table
    @staticmethod
    def get_default_config_path():
        """Restituisce sempre il path assoluto del file di configurazione come nello script principale."""
        # Path assoluto dalla root del progetto
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config', 'config_autonomous_challenge_production_ready.json')
        config_path = os.path.normpath(config_path)
        print(f"[DEBUG] get_default_config_path: {config_path}")
        return config_path

    @staticmethod
    def get_default_log_path(config: dict = None):
        """Restituisce il path assoluto del file di log con data, es: logs/log_autonomous_challenge_YYYYMMDD.log"""
        from datetime import datetime
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(project_root, 'logs')
        today_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(logs_dir, f'log_autonomous_challenge_{today_str}.log')
        return log_file

    def __init__(self, config_file: str = None, log_file: str = None, use_mt5: bool = True):
        """
        Inizializza la dashboard grafica The5ers
        
        Args:
            config_file: Path al file di configurazione JSON (auto-detect se None)
            log_file: Path al file di log (opzionale, auto-detect da config)
            use_mt5: Se True, usa dati MT5 per analisi completa
        """
        # Inizializza attributi fondamentali PRIMA di qualsiasi metodo che li usa
        self.mt5_connected = False
        self.challenge_start = datetime(2025, 7, 7, 0, 0, 0)
        self.max_data_points = 1000
        self.pnl_history = deque(maxlen=self.max_data_points)
        self.drawdown_history = deque(maxlen=self.max_data_points)
        self.balance_history = deque(maxlen=self.max_data_points)
        self.trades_timeline = deque(maxlen=self.max_data_points)
        # Ogni elemento: {'timestamp', 'symbol', 'direction', 'entropy', 'spin', 'esito', 'trade_pnl', 'trade_time'}
        self.signals_timeline = deque(maxlen=self.max_data_points)
        self.hourly_performance = defaultdict(lambda: {'pnl': 0, 'trades': 0})
        self.symbol_performance = defaultdict(lambda: {'pnl': 0, 'trades': 0, 'win_rate': 0})
        self.current_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'current_balance': 0.0,
            'current_equity': 0.0,
            'current_drawdown': 0.0,
            'max_drawdown': 0.0,
            'profit_percentage': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'daily_trades': 0,
            'positions_open': 0,
            'quantum_signals': {
                'total': 0,
                'buy': 0,
                'sell': 0,
                'avg_entropy': 0.0,
                'avg_spin': 0.0,
                'avg_confidence': 0.0
            }
        }
        self.is_monitoring = False
        self.last_log_position = 0
        self.last_update = datetime.now()
        self.realtime_notifications = deque(maxlen=50)
        # Storico errori/warning (max 100)
        self.errors_warnings = deque(maxlen=100)
        # Inizializza sempre use_mt5 con il valore passato
        self.use_mt5 = use_mt5
        # Inizializza sempre drawdown_hard e drawdown_soft con valori di default
        self.drawdown_hard = 5
        self.drawdown_soft = 2
        # Inizializza sempre step1_target con valore di default
        self.step1_target = 8
        # Flask app: inizializza subito per evitare errori
        import os
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        self.app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
        # Auto-detect config file se non specificato (per sistema mono)
        if config_file is None:
            config_file = self.get_default_config_path()

        self.config_file = config_file
        # Inizializza sempre log_file con il path di default
        self.log_file = self.get_default_log_path()
    def log_error_warning(self, msg: str, details: dict = None, level: str = "ERROR"):
        """Salva un errore/warning nello storico dedicato."""
        entry = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "level": level,
            "message": msg,
            "details": details or {}
        }
        print(f"[{level}] {entry['timestamp']}: {msg}")
        self.errors_warnings.appendleft(entry)

        # Se il drawdown è > 0 ma la drawdown_history è vuota, aggiungi un punto per il grafico
        if self.current_metrics['current_drawdown'] > 0 and not self.drawdown_history:
            self.drawdown_history.append({
                'timestamp': datetime.now().isoformat(),
                'drawdown': self.current_metrics['current_drawdown']
            })


        print(f"[DEBUG] Config file utilizzato: {self.config_file}")
        raw_config = self.load_config()
        # Gestione errori caricamento config
        if not raw_config or not isinstance(raw_config, dict):
            print("❌ Errore: file di configurazione non valido o non caricato. Controlla il percorso e il formato JSON.")
            self.config = {}
            self.use_mt5 = False
        elif 'config' in raw_config and isinstance(raw_config['config'], dict):
            self.config = raw_config['config']
            print("[DEBUG] Configurazione: wrapper 'config' rilevato, uso raw_config['config']")
        else:
            self.config = raw_config
            print("[DEBUG] Configurazione: uso raw_config diretto")
        self.use_mt5 = use_mt5 and MT5_AVAILABLE and bool(self.config)

        # Aggiorna log_file se specificato o se la config lo richiede
        if log_file is not None:
            self.log_file = log_file
        elif hasattr(self, 'config'):
            self.log_file = self.get_default_log_path(self.config)

        # Parametri The5ers
        self.the5ers_params = self.config.get('THE5ERS_specific', {})
        self.step1_target = self.the5ers_params.get('step1_target', 8)
        self.drawdown_soft = self.the5ers_params.get('drawdown_protection', {}).get('soft_limit', 2)
        self.drawdown_hard = self.the5ers_params.get('drawdown_protection', {}).get('hard_limit', 5)

        # Configurazione MT5
        if self.use_mt5:
            self.mt5_config = self.config.get('metatrader5', {})
            # self.challenge_start già impostato sopra, eventualmente sovrascrivilo qui se serve

        # Carica segnali dal CSV all'avvio
        self.load_signals_from_csv()




    def send_realtime_notification(self, event_type: str, message: str, details: dict = None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        notif = {
            'event_type': event_type,
            'message': message,
            'timestamp': timestamp,
            'details': details or {}
        }
        print(f"[NOTIFICA][{event_type}] {timestamp}: {message}")
        self.realtime_notifications.appendleft(notif)

    def setup_routes(self):
        @self.app.route('/performance')
        def performance():
            metrics = self.current_metrics
            # Fix: aggiungi dati grafico se non presenti
            if 'performance_chart' not in metrics:
                import datetime
                metrics['performance_chart'] = {
                    'dates': [datetime.datetime.now().strftime('%Y-%m-%d')],
                    'pnl': [0.0]
                }
            # Rigenera i grafici principali come nella dashboard
            pnl_chart = self.create_pnl_chart()
            drawdown_chart = self.create_drawdown_chart()
            balance_chart = self.create_balance_chart()
            hourly_chart = self.create_hourly_chart()
            symbols_chart = self.create_symbols_chart()
            return render_template('performance.html', metrics=metrics, pnl_chart=pnl_chart, drawdown_chart=drawdown_chart, balance_chart=balance_chart, hourly_chart=hourly_chart, symbols_chart=symbols_chart)

        @self.app.route('/advanced_metrics')
        def advanced_metrics():
            # Aggiorna i dati dal log prima di calcolare le metriche
            self.analyze_log_file()
            # Import robusto per compatibilità
            try:
                from datetime import datetime as dt_class
            except ImportError:
                import datetime as dtmod
                dt_class = dtmod.datetime
            metrics = self.current_metrics
            # Fix: aggiungi dati grafico se non presenti
            if 'advanced_chart' not in metrics:
                import datetime as dtmod
                metrics['advanced_chart'] = {
                    'dates': [dtmod.datetime.now().strftime('%Y-%m-%d')],
                    'rrr': [0.0]
                }
            # Rigenera breakdown e grafici avanzati
            daily_rrr_values = []
            daily_rrr_labels = []
            daily = {}
            for entry in self.pnl_history:
                try:
                    dt = dt_class.fromisoformat(entry['timestamp'])
                except AttributeError:
                    import datetime as dtmod
                    dt = dtmod.datetime.fromisoformat(entry['timestamp'])
                day = dt.strftime('%Y-%m-%d')
                if day not in daily:
                    daily[day] = {'pnl': 0.0, 'trades': 0}
                daily[day]['pnl'] += float(entry['pnl'] or 0)
                daily[day]['trades'] += 1
            for day, stats in sorted(daily.items()):
                rrr = abs(stats['pnl']) / stats['trades'] if stats['trades'] > 0 else 0.0
                daily_rrr_values.append(rrr)
                daily_rrr_labels.append(day)
            daily_rrr_chart = {
                'data': [go.Bar(x=daily_rrr_labels, y=daily_rrr_values, marker_color=['#00ffe7' if v>=0 else '#ff3c3c' for v in daily_rrr_values], name='RRR Giornaliero').to_plotly_json()],
                'layout': go.Layout(title='Risk/Reward Ratio Giornaliero', xaxis={'title':'Data'}, yaxis={'title':'RRR'}, plot_bgcolor='#181c20').to_plotly_json()
            }
            weekly = {}
            weekly_rrr_values = []
            weekly_rrr_labels = []
            for entry in self.pnl_history:
                dt = datetime.fromisoformat(entry['timestamp'])
                week = dt.strftime('%Y-W%U')
                if week not in weekly:
                    weekly[week] = {'pnl': 0.0, 'trades': 0}
                weekly[week]['pnl'] += float(entry['pnl'] or 0)
                weekly[week]['trades'] += 1
            for week, stats in sorted(weekly.items()):
                rrr = abs(stats['pnl']) / stats['trades'] if stats['trades'] > 0 else 0.0
                weekly_rrr_values.append(rrr)
                weekly_rrr_labels.append(week)
            weekly_rrr_chart = {
                'data': [go.Bar(x=weekly_rrr_labels, y=weekly_rrr_values, marker_color=['#00bfff' if v>=0 else '#fd7e14' for v in weekly_rrr_values], name='RRR Settimanale').to_plotly_json()],
                'layout': go.Layout(title='Risk/Reward Ratio Settimanale', xaxis={'title':'Settimana'}, yaxis={'title':'RRR'}, plot_bgcolor='#181c20').to_plotly_json()
            }
            advanced_chart = {
                'dates': daily_rrr_labels,
                'rrr': daily_rrr_values
            }
            metrics['advanced_chart'] = advanced_chart
            return render_template('advanced_metrics.html', metrics=metrics, daily_rrr_chart=daily_rrr_chart, weekly_rrr_chart=weekly_rrr_chart)

        @self.app.route('/quantum_metrics')
        def quantum_metrics():
            metrics = self.current_metrics
            percent_signals_executed = 0.0
            if metrics.get('quantum_signals', {}).get('total', 0) > 0:
                executed_signals = sum(1 for s in self.signals_timeline if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE')
                percent_signals_executed = (executed_signals / metrics['quantum_signals']['total'] * 100)
            # Fix: aggiungi dati grafico se non presenti
            # Rigenera quantum_chart come andamento storico
            quantum_dates = []
            quantum_executed = []
            # Breakdown giornaliero
            daily_signals = {}
            for s in self.signals_timeline:
                day = s['timestamp'][:10]
                if day not in daily_signals:
                    daily_signals[day] = {'total': 0, 'executed': 0}
                daily_signals[day]['total'] += 1
                if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE':
                    daily_signals[day]['executed'] += 1
            for day, stats in sorted(daily_signals.items()):
                quantum_dates.append(day)
                percent = (stats['executed']/stats['total']*100) if stats['total']>0 else 0.0
                quantum_executed.append(percent)
            metrics['quantum_chart'] = {
                'dates': quantum_dates,
                'executed': quantum_executed
            }
            # Rigenera signals_chart e breakdown percentuali come nella dashboard
            signals_chart = self.create_signals_chart()
            daily_percent_signals_executed = getattr(self, 'daily_percent_signals_executed', {})
            weekly_percent_signals_executed = getattr(self, 'weekly_percent_signals_executed', {})
            return render_template('quantum_metrics.html', metrics=metrics, percent_signals_executed=percent_signals_executed, signals_chart=signals_chart, daily_percent_signals_executed=daily_percent_signals_executed, weekly_percent_signals_executed=weekly_percent_signals_executed)
        app = self.app
        print('[DEBUG] Registrazione route / (home) in corso...')
        # Route di test minimale
        self.add_test_route()
        @app.route('/api/errors_warnings', methods=['GET'])
        def api_errors_warnings():
            """Restituisce lo storico errori/warning (max 100)"""
            return jsonify({
                'success': True,
                'errors_warnings': list(self.errors_warnings)
            })
        @app.route('/api/unexecuted_signals', methods=['GET'])
        def api_unexecuted_signals():
            """Restituisce segnali BUY/SELL non eseguiti, filtrabili per simbolo e numero righe."""
            import csv
            from flask import request
            symbol = request.args.get('symbol', '').upper().strip()
            try:
                max_rows = int(request.args.get('max_rows', 20))
            except Exception:
                max_rows = 20
            logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
            json_path = os.path.join(logs_dir, 'signals_vs_trades_report.json')
            if not os.path.isfile(json_path):
                # Se il file non esiste, restituisci lista vuota
                filtered = []
            else:
                import json
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                filtered = [row for row in data if not row.get('trade_aperto') and row.get('segnale') in ('BUY', 'SELL')]
                if symbol:
                    filtered = [row for row in filtered if row.get('symbol', '').upper() == symbol]
                filtered = filtered[-max_rows:]
            return jsonify({'success': True, 'rows': filtered})
        app = self.app
        from flask import render_template
        from flask import request
        import subprocess
        import sys
        import os
        from flask import send_file
        @app.route('/api/run_signals_vs_trades_report', methods=['POST'])
        def api_run_signals_vs_trades_report():
            """Lancia lo script di analisi incrociata segnali/trade/blocchi e restituisce output e stato."""
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'analyze_signals_vs_trades.py'))
            python_exe = sys.executable or 'python'
            try:
                result = subprocess.run(
                    [python_exe, script_path],
                    capture_output=True, text=True, timeout=120, cwd=os.path.dirname(script_path)
                )
                # Percorsi output
                logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
                csv_path = os.path.join(logs_dir, 'signals_vs_trades_report.csv')
                json_path = os.path.join(logs_dir, 'signals_vs_trades_report.json')
                return jsonify({
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'csv_report': '/download/signals_vs_trades_report.csv',
                    'json_report': '/download/signals_vs_trades_report.json'
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @app.route('/api/generate_signals_tick_log', methods=['POST'])
        def api_generate_signals_tick_log():
            """Lancia la generazione del file signals_tick_log.csv (segnali tick) e restituisce output e stato."""
            # Qui si assume che la generazione avvenga tramite script Python dedicato o funzione
            # Se esiste uno script, ad esempio export_signals_to_json.py, si può adattare
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'export_signals_to_json.py'))
            python_exe = sys.executable or 'python'
            try:
                result = subprocess.run(
                    [python_exe, script_path],
                    capture_output=True, text=True, timeout=120, cwd=os.path.dirname(script_path)
                )
                logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
                csv_path = os.path.join(logs_dir, 'signals_tick_log.csv')
                json_path = os.path.join(logs_dir, 'signals_tick_log.json')
                return jsonify({
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'csv_path': '/download/signals_tick_log.csv',
                    'json_path': '/download/signals_tick_log.json'
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        @app.route('/download/signals_vs_trades_report.csv')
        def download_signals_vs_trades_csv():
            logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
            csv_path = os.path.join(logs_dir, 'signals_vs_trades_report.csv')
            return send_file(csv_path, as_attachment=True)

        @app.route('/download/signals_vs_trades_report.json')
        def download_signals_vs_trades_json():
            logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
            json_path = os.path.join(logs_dir, 'signals_vs_trades_report.json')
            return send_file(json_path, as_attachment=True)

        @app.route('/mt5_status')
        def mt5_status_page():
            # Ottieni info MT5 come nel JSON API
            info = {
                'connessione': 'OK' if self.mt5_connected else 'DISCONNESSO',
                'account': self.current_metrics.get('current_balance', None),
                'server': getattr(self, 'mt5_config', {}).get('server', ''),
                'saldo': self.current_metrics.get('current_balance', None),
                'equity': self.current_metrics.get('current_equity', None),
                'posizioni_aperte': self.current_metrics.get('positions_open', None)
            }
            return render_template('mt5_status.html', mt5_info=info)

        @app.route('/api/archive_and_cleanup_logs', methods=['POST'])
        def api_archive_and_cleanup_logs():
            """Lancia lo script batch di archiviazione/pulizia log e restituisce output."""
            import subprocess
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'archive_and_cleanup_logs.bat'))
            try:
                result = subprocess.run([script_path], capture_output=True, text=True, timeout=60, shell=True, cwd=os.path.dirname(script_path))
                return jsonify({
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @app.route('/api/refresh_signals', methods=['POST'])
        def api_refresh_signals():
            # Ricarica i segnali dal CSV e restituisce la tabella aggiornata
            self.load_signals_from_csv()
            table = self.create_signals_sequence_table()
            return jsonify({'signals_sequence_table': table})

        @app.route('/api/mt5_status')
        def api_mt5_status():
            # Raccogli info stato MT5
            info = {
                'connessione': 'OK' if self.mt5_connected else 'DISCONNESSO',
                'account': self.current_metrics.get('current_balance', None),
                'server': getattr(self, 'mt5_config', {}).get('server', ''),
                'saldo': self.current_metrics.get('current_balance', None),
                'equity': self.current_metrics.get('current_equity', None),
                'posizioni_aperte': self.current_metrics.get('positions_open', None)
            }
            return jsonify(info)

        @app.route('/')
        def home():
            # Pagina di benvenuto con estratto metriche principali
            print('[DEBUG] Chiamata route / (home)')
            try:
                # Espongo le metriche principali e lo stato MT5
                metrics = self.current_metrics
                percent_signals_executed = 0.0
                if metrics.get('quantum_signals', {}).get('total', 0) > 0:
                    executed_signals = sum(1 for s in self.signals_timeline if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE')
                    percent_signals_executed = (executed_signals / metrics['quantum_signals']['total'] * 100)
                mt5_warning = ""
                if not MT5_AVAILABLE:
                    mt5_warning = "<div style='color:red; font-weight:bold; margin-bottom:10px;'>⚠️ Modulo MetaTrader5 non installato: dati live non disponibili.</div>"
                elif not self.use_mt5:
                    mt5_warning = "<div style='color:orange; font-weight:bold; margin-bottom:10px;'>⚠️ Connessione MT5 non attiva o file di configurazione non valido.</div>"
                elif not self.mt5_connected:
                    mt5_warning = "<div style='color:orange; font-weight:bold; margin-bottom:10px;'>⚠️ MT5 non connesso: mostra solo dati da log.</div>"
                return render_template('home.html', metrics=metrics, percent_signals_executed=percent_signals_executed, mt5_warning=mt5_warning)
            except Exception as e:
                print(f'[ERRORE TEMPLATE] {e}')
                return f"Template home.html non trovato o errore: {e}", 500

        @app.route('/dashboard')
        def dashboard():
            # Calcolo percentuale segnali quantum eseguiti
            total_signals = self.current_metrics['quantum_signals']['total']
            executed_signals = sum(1 for s in self.signals_timeline if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE')
            percent_signals_executed = (executed_signals / total_signals * 100) if total_signals > 0 else 0.0

            # Breakdown giornaliero
            daily_signals = {}
            for s in self.signals_timeline:
                day = s['timestamp'][:10]
                if day not in daily_signals:
                    daily_signals[day] = {'total': 0, 'executed': 0}
                daily_signals[day]['total'] += 1
                if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE':
                    daily_signals[day]['executed'] += 1
            daily_percent_signals_executed = {d: (v['executed']/v['total']*100 if v['total']>0 else 0.0) for d,v in daily_signals.items()}

            # Breakdown settimanale
            weekly_signals = {}
            for s in self.signals_timeline:
                week = datetime.fromisoformat(s['timestamp']).strftime('%Y-W%U')
                if week not in weekly_signals:
                    weekly_signals[week] = {'total': 0, 'executed': 0}
                weekly_signals[week]['total'] += 1
                if s.get('esito') and s.get('esito') != 'NESSUNA AZIONE':
                    weekly_signals[week]['executed'] += 1
            weekly_percent_signals_executed = {w: (v['executed']/v['total']*100 if v['total']>0 else 0.0) for w,v in weekly_signals.items()}
            # Calcola breakdown giornaliero e settimanale
            daily = {}
            weekly = {}
            for entry in self.pnl_history:
                dt = datetime.fromisoformat(entry['timestamp'])
                day = dt.strftime('%Y-%m-%d')
                week = dt.strftime('%Y-W%U')
                commission = float(entry.get('commission', 0) or 0)
                swap = float(entry.get('swap', 0) or 0)
                cost = commission + swap
                if day not in daily:
                    daily[day] = {'pnl': 0.0, 'trades': 0, 'wins': 0, 'commission': 0.0, 'swap': 0.0, 'cost': 0.0}
                if week not in weekly:
                    weekly[week] = {'pnl': 0.0, 'trades': 0, 'wins': 0, 'commission': 0.0, 'swap': 0.0, 'cost': 0.0}
                daily[day]['pnl'] += float(entry['pnl'] or 0)
                daily[day]['trades'] += 1
                daily[day]['commission'] += commission
                daily[day]['swap'] += swap
                daily[day]['cost'] += cost
                weekly[week]['pnl'] += float(entry['pnl'] or 0)
                weekly[week]['trades'] += 1
                weekly[week]['commission'] += commission
                weekly[week]['swap'] += swap
                weekly[week]['cost'] += cost
                if entry['pnl'] > 0:
                    daily[day]['wins'] += 1
                    weekly[week]['wins'] += 1
            # Calcola win rate e profit %
            daily_breakdown = []
            for day, stats in sorted(daily.items()):
                win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
                profit_pct = (stats['pnl'] / self.current_metrics['current_balance'] * 100) if self.current_metrics['current_balance'] > 0 else 0
                daily_breakdown.append({
                    'date': day,
                    'pnl': stats['pnl'],
                    'trades': stats['trades'],
                    'win_rate': win_rate,
                    'profit_pct': profit_pct,
                    'commission': stats['commission'],
                    'swap': stats['swap'],
                    'cost': stats['cost']
                })
            weekly_breakdown = []
            for week, stats in sorted(weekly.items()):
                win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
                profit_pct = (stats['pnl'] / self.current_metrics['current_balance'] * 100) if self.current_metrics['current_balance'] > 0 else 0
                weekly_breakdown.append({
                    'week': week,
                    'pnl': stats['pnl'],
                    'trades': stats['trades'],
                    'win_rate': win_rate,
                    'profit_pct': profit_pct,
                    'commission': stats['commission'],
                    'swap': stats['swap'],
                    'cost': stats['cost']
                })
            # Ora i breakdown sono definiti, posso generare i grafici
            import plotly.graph_objs as go
            daily_chart_data = []
            daily_chart_labels = []
            for day in daily_breakdown:
                daily_chart_labels.append(day['date'])
                daily_chart_data.append(day['pnl'])
            daily_breakdown_chart = {
                'data': [go.Bar(x=daily_chart_labels, y=daily_chart_data, marker_color=['#00ffe7' if v>=0 else '#ff3c3c' for v in daily_chart_data], name='P&L Giornaliero').to_plotly_json()],
                'layout': go.Layout(title='Rendimento Giornaliero', xaxis={'title':'Data'}, yaxis={'title':'P&L ($)'}, plot_bgcolor='#181c20').to_plotly_json()
            }
            weekly_chart_data = []
            weekly_chart_labels = []
            for week in weekly_breakdown:
                weekly_chart_labels.append(week['week'])
                weekly_chart_data.append(week['pnl'])
            weekly_breakdown_chart = {
                'data': [go.Bar(x=weekly_chart_labels, y=weekly_chart_data, marker_color=['#00bfff' if v>=0 else '#fd7e14' for v in weekly_chart_data], name='P&L Settimanale').to_plotly_json()],
                'layout': go.Layout(title='Rendimento Settimanale', xaxis={'title':'Settimana'}, yaxis={'title':'P&L ($)'}, plot_bgcolor='#181c20').to_plotly_json()
            }
            # Dashboard principale con grafici
            pnl_chart = self.create_pnl_chart()
            drawdown_chart = self.create_drawdown_chart()
            balance_chart = self.create_balance_chart()
            hourly_chart = self.create_hourly_chart()
            symbols_chart = self.create_symbols_chart()
            signals_chart = self.create_signals_chart()
            metrics = self.current_metrics
            compliance = self.get_compliance_status()
            mt5_warning = ""
            if not MT5_AVAILABLE:
                mt5_warning = "<div style='color:red; font-weight:bold; margin-bottom:10px;'>⚠️ Modulo MetaTrader5 non installato: dati live non disponibili.</div>"
            elif not self.use_mt5:
                mt5_warning = "<div style='color:orange; font-weight:bold; margin-bottom:10px;'>⚠️ Connessione MT5 non attiva o file di configurazione non valido.</div>"
            elif not self.mt5_connected:
                mt5_warning = "<div style='color:orange; font-weight:bold; margin-bottom:10px;'>⚠️ MT5 non connesso: mostra solo dati da log.</div>"
            # Le tabelle diagnostiche sono ora su /diagnostics
            # Carica segnali non eseguiti per la tabella (ultimi 20)
            # NB: questa logica può essere raffinata lato frontend, qui forniamo i dati
            import json
            logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
            json_path = os.path.join(logs_dir, 'signals_vs_trades_report.json')
            unexecuted_signals = []
            if os.path.isfile(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for row in data:
                        # Assicura che direction sia presente e coerente con signals_sequence_table
                        direction = row.get('direction')
                        if not direction and row.get('segnale') in ('BUY', 'SELL'):
                            direction = row.get('segnale')
                            row['direction'] = direction
                        if not row.get('trade_aperto') and direction in ('BUY', 'SELL'):
                            # Genera link dettagliato per diagnostics usando direction
                            symbol = row.get('symbol', '')
                            timestamp = row.get('timestamp', '')
                            link = f"/diagnostics?symbol={symbol}&direction={direction}&timestamp={timestamp}"
                            row['dettagli_link'] = link
                            # Aggiungi dettagli extra per la tabella dashboard
                            row['motivo_blocco'] = row.get('motivo_blocco', '')
                            row['parametro_non_soddisfatto'] = row.get('parametro_non_soddisfatto', '')
                            row['dettagli_tecnici'] = row.get('dettagli_tecnici', '')
                            # Se disponibili, aggiungi anche altri dettagli utili
                            unexecuted_signals.append(row)
                # Mostra solo gli ultimi 20
                unexecuted_signals = unexecuted_signals[-20:]
            # Calcolo RRR medio globale, giornaliero e settimanale
            def calc_rrr(entries):
                rrrs = []
                for e in entries:
                    # RRR = abs(profit) / abs(loss) per trade, qui semplificato come profit/loss ratio
                    # Se hai stop_loss e take_profit, puoi usare quelli
                    # Qui usiamo solo pnl positivo/negativo
                    if 'pnl' in e and e['pnl'] != 0:
                        # Simulazione: RRR = abs(pnl) / abs(pnl) = 1, ma in realtà serve info su rischio e reward
                        # Se hai info su stop_loss/take_profit, sostituisci qui
                        rrrs.append(abs(e['pnl']) / 1.0)  # Placeholder
                if rrrs:
                    return sum(rrrs) / len(rrrs)
                return 0.0

            # Calcolo volatilità portafoglio
            def calc_volatility(pnl_list):
                if len(pnl_list) < 2:
                    return 0.0
                mean = sum(pnl_list) / len(pnl_list)
                variance = sum((x - mean) ** 2 for x in pnl_list) / (len(pnl_list) - 1)
                return variance ** 0.5

            # Volatilità globale
            pnl_values = [float(entry['pnl']) for entry in self.pnl_history]
            portfolio_volatility = calc_volatility(pnl_values)

            # Volatilità giornaliera
            daily_volatility = {}
            for day in daily_breakdown:
                day_pnl = [float(entry['pnl']) for entry in self.pnl_history if entry['timestamp'][:10] == day['date']]
                daily_volatility[day['date']] = calc_volatility(day_pnl)

            # Volatilità settimanale
            weekly_volatility = {}
            for week in weekly_breakdown:
                week_pnl = [float(entry['pnl']) for entry in self.pnl_history if datetime.fromisoformat(entry['timestamp']).strftime('%Y-W%U') == week['week']]
                weekly_volatility[week['week']] = calc_volatility(week_pnl)

            # RRR medio globale
            avg_rrr_global = calc_rrr(self.pnl_history)

            # RRR giornaliero
            daily_rrr_values = []
            daily_rrr_labels = []
            for day in daily_breakdown:
                # Simulazione: usa pnl/trades come proxy
                rrr = abs(day['pnl']) / day['trades'] if day['trades'] > 0 else 0.0
                daily_rrr_values.append(rrr)
                daily_rrr_labels.append(day['date'])
            import plotly.graph_objs as go
            daily_rrr_chart = {
                'data': [go.Bar(x=daily_rrr_labels, y=daily_rrr_values, marker_color=['#00ffe7' if v>=0 else '#ff3c3c' for v in daily_rrr_values], name='RRR Giornaliero').to_plotly_json()],
                'layout': go.Layout(title='Risk/Reward Ratio Giornaliero', xaxis={'title':'Data'}, yaxis={'title':'RRR'}, plot_bgcolor='#181c20').to_plotly_json()
            }

            # RRR settimanale
            weekly_rrr_values = []
            weekly_rrr_labels = []
            for week in weekly_breakdown:
                rrr = abs(week['pnl']) / week['trades'] if week['trades'] > 0 else 0.0
                weekly_rrr_values.append(rrr)
                weekly_rrr_labels.append(week['week'])
            weekly_rrr_chart = {
                'data': [go.Bar(x=weekly_rrr_labels, y=weekly_rrr_values, marker_color=['#00bfff' if v>=0 else '#fd7e14' for v in weekly_rrr_values], name='RRR Settimanale').to_plotly_json()],
                'layout': go.Layout(title='Risk/Reward Ratio Settimanale', xaxis={'title':'Settimana'}, yaxis={'title':'RRR'}, plot_bgcolor='#181c20').to_plotly_json()
            }

            # Espone i grafici come attributi della classe per accesso robusto da tutte le route
            self.daily_rrr_chart = daily_rrr_chart
            self.weekly_rrr_chart = weekly_rrr_chart

            # Calcolo Drawdown Recovery Time e breakdown
            def calc_drawdown_recovery(drawdown_history, pnl_history):
                recovery_times = []
                drawdown_points = []
                for i, dd in enumerate(drawdown_history):
                    if dd['drawdown'] > 0:
                        drawdown_points.append((i, dd['drawdown'], dd['timestamp']))
                for idx, dd_val, dd_ts in drawdown_points:
                    for j in range(idx+1, len(drawdown_history)):
                        if drawdown_history[j]['drawdown'] <= 0.01:
                            t1 = datetime.fromisoformat(dd_ts)
                            t2 = datetime.fromisoformat(drawdown_history[j]['timestamp'])
                            recovery_minutes = (t2 - t1).total_seconds() / 60.0
                            recovery_times.append(recovery_minutes)
                            break
                if recovery_times:
                    return sum(recovery_times) / len(recovery_times)
                return 0.0

            drawdown_recovery_time = calc_drawdown_recovery(self.drawdown_history, self.pnl_history)

            daily_drawdown_recovery = {}
            weekly_drawdown_recovery = {}
            for day in daily_breakdown:
                times = []
                for dd in self.drawdown_history:
                    if dd['timestamp'][:10] == day['date']:
                        times.append(dd)
                if times:
                    rec = calc_drawdown_recovery(times, self.pnl_history)
                    daily_drawdown_recovery[day['date']] = rec
            for week in weekly_breakdown:
                times = []
                for dd in self.drawdown_history:
                    dt = datetime.fromisoformat(dd['timestamp'])
                    week_str = dt.strftime('%Y-W%U')
                    if week_str == week['week']:
                        times.append(dd)
                if times:
                    rec = calc_drawdown_recovery(times, self.pnl_history)
                    weekly_drawdown_recovery[week['week']] = rec

            return render_template(
                'dashboard.html',
                pnl_chart=pnl_chart,
                drawdown_chart=drawdown_chart,
                balance_chart=balance_chart,
                hourly_chart=hourly_chart,
                symbols_chart=symbols_chart,
                signals_chart=signals_chart,
                metrics=metrics,
                compliance=compliance,
                mt5_warning=mt5_warning,
                unexecuted_signals=unexecuted_signals,
                realtime_notifications=list(self.realtime_notifications),
                daily_breakdown=daily_breakdown,
                weekly_breakdown=weekly_breakdown,
                daily_breakdown_chart=daily_breakdown_chart,
                weekly_breakdown_chart=weekly_breakdown_chart,
                daily_rrr_chart=daily_rrr_chart,
                weekly_rrr_chart=weekly_rrr_chart,
                avg_rrr_global=avg_rrr_global,
                drawdown_recovery_time=drawdown_recovery_time,
                daily_drawdown_recovery=daily_drawdown_recovery,
                weekly_drawdown_recovery=weekly_drawdown_recovery,
                portfolio_volatility=portfolio_volatility,
                daily_volatility=daily_volatility,
               weekly_volatility=weekly_volatility,
               percent_signals_executed=percent_signals_executed,
               daily_percent_signals_executed=daily_percent_signals_executed,
               weekly_percent_signals_executed=weekly_percent_signals_executed
            )

        # ...existing code...


        @app.route('/diagnostics')
        def diagnostics():
            # Deep-link: accetta parametri GET per filtrare/evidenziare un segnale
            from flask import request
            symbol = request.args.get('symbol', '').upper().strip()
            direction = request.args.get('direction', '').upper().strip()
            timestamp = request.args.get('timestamp', '').strip()
            # Tabella segnali quantum
            signals_sequence_table = self.create_signals_sequence_table()
            # Se sono presenti parametri, filtra/evidenzia il segnale richiesto
            highlight_signal = None
            def normalize_ts(ts):
                # Normalizza il timestamp a stringa 'YYYY-MM-DD HH:MM:SS' (ignora ms, T, Z, ecc)
                from datetime import datetime
                if not ts:
                    return ''
                # Prova vari formati comuni
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S'):
                    try:
                        dt = datetime.strptime(ts[:19], fmt)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        pass
                # fallback: taglia a 19 caratteri se sembra ISO
                if len(ts) >= 19:
                    return ts[:19].replace('T', ' ')
                return ts
            if symbol and direction and timestamp:
                ts_norm = normalize_ts(timestamp)
                for s in signals_sequence_table:
                    if (
                        s['symbol'].upper() == symbol and
                        s['direction'].upper() == direction and
                        normalize_ts(s['timestamp']) == ts_norm
                    ):
                        highlight_signal = s
                        break
            # Tabella decisioni trade
            trade_decision_table = read_trade_decision_report(100)
            # Parametri quantum dal file di config
            config = self.load_config()
            quantum = config.get('config', {}).get('quantum_params', {})
            entropy_thresholds = quantum.get('entropy_thresholds', {})
            buy_entropy = entropy_thresholds.get('buy_signal', None)
            sell_entropy = entropy_thresholds.get('sell_signal', None)
            spin_window = quantum.get('spin_window', None)
            min_spin_samples = quantum.get('min_spin_samples', None)
            spin_threshold = quantum.get('spin_threshold', None)
            signal_cooldown = quantum.get('signal_cooldown', None)
            # Passa i parametri al template, aggiungi highlight_signal
            return render_template(
                'diagnostics.html',
                signals_sequence_table=signals_sequence_table,
                trade_decision_table=trade_decision_table,
                buy_entropy=buy_entropy,
                sell_entropy=sell_entropy,
                spin_window=spin_window,
                min_spin_samples=min_spin_samples,
                spin_threshold=spin_threshold,
                signal_cooldown=signal_cooldown,
                highlight_signal=highlight_signal
            )

        @app.route('/api/run_block_reasons_report', methods=['POST'])
        def api_run_block_reasons_report():
            """Lancia il report motivi di blocco (orario/daily) e restituisce output e stato."""
            import subprocess
            from flask import request
            period = request.json.get('period', 'hourly')
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'block_reasons_report.py'))
            python_exe = sys.executable or 'python'
            try:
                result = subprocess.run(
                    [python_exe, script_path, '--period', period],
                    capture_output=True, text=True, timeout=60, cwd=os.path.dirname(script_path)
                )
                return jsonify({
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'period': period
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e), 'period': period}), 500

        try:
            account_info = mt5.account_info()
            if account_info:
                self.current_metrics['current_balance'] = account_info.balance
                self.current_metrics['current_equity'] = account_info.equity
                self.current_metrics['positions_open'] = len(mt5.positions_get() or [])
                # Aggiorna balance history
                self.balance_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'balance': account_info.balance,
                    'equity': account_info.equity
                })

            # Ottieni storia completa deals
            deals = mt5.history_deals_get(self.challenge_start, datetime.now())
            if deals is None:
                print("❌ Nessun deal trovato")
                return

            # Reset dati per reload completo
            self.pnl_history.clear()
            self.symbol_performance.clear()
            self.hourly_performance.clear()

            # Processa tutti i deals
            cumulative_pnl = 0
            total_trades = 0
            winning_trades = 0

            for deal in deals:
                if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                    deal_time = datetime.fromtimestamp(deal.time)
                    # Aggiorna metriche
                    total_trades += 1
                    cumulative_pnl += deal.profit
                    if deal.profit > 0:
                        winning_trades += 1
                    # Aggiorna P&L history
                    self.pnl_history.append({
                        'timestamp': deal_time.isoformat(),
                        'pnl': deal.profit,
                        'cumulative_pnl': cumulative_pnl,
                        'symbol': deal.symbol,
                        'direction': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL'
                    })
                    # Aggiorna performance per simbolo
                    self.symbol_performance[deal.symbol]['pnl'] += deal.profit
                    self.symbol_performance[deal.symbol]['trades'] += 1
                    # Aggiorna performance oraria
                    hour = deal_time.hour
                    self.hourly_performance[hour]['pnl'] += deal.profit
                    self.hourly_performance[hour]['trades'] += 1

            # Aggiorna metriche globali
            self.current_metrics['total_trades'] = total_trades
            self.current_metrics['winning_trades'] = winning_trades
            self.current_metrics['total_pnl'] = cumulative_pnl

            if total_trades > 0:
                self.current_metrics['win_rate'] = (winning_trades / total_trades) * 100

            if self.current_metrics['current_balance'] > 0:
                self.current_metrics['profit_percentage'] = (cumulative_pnl / self.current_metrics['current_balance']) * 100

            # Calcola profit factor
            total_profit = sum(deal.profit for deal in deals if deal.profit > 0)
            total_loss = sum(abs(deal.profit) for deal in deals if deal.profit < 0)

            if total_loss > 0:
                self.current_metrics['profit_factor'] = total_profit / total_loss
            else:
                self.current_metrics['profit_factor'] = float('inf') if total_profit > 0 else 0

            # Calcola Max Drawdown
            max_drawdown = self.calculate_max_drawdown()
            self.current_metrics['max_drawdown'] = max_drawdown
            self.current_metrics['current_drawdown'] = max_drawdown  # Aggiorna anche current drawdown

            # Calcola win rate per simbolo
            for symbol, stats in self.symbol_performance.items():
                if stats['trades'] > 0:
                    symbol_winning = sum(1 for deal in deals if deal.symbol == symbol and deal.profit > 0)
                    stats['win_rate'] = (symbol_winning / stats['trades']) * 100

            print(f"✅ Caricati {total_trades} trades da MT5")
            print(f"📊 P&L Totale: ${cumulative_pnl:.2f}")
            print(f"🎯 Profit %: {self.current_metrics['profit_percentage']:.2f}%")

        except Exception as e:
            print(f"❌ Errore caricamento dati MT5: {e}")
        # Non chiudere la connessione qui!

    def calculate_max_drawdown(self) -> float:
        """Calcola il Max Drawdown dai dati P&L"""
        if not self.pnl_history:
            return 0.0
            
        # Usa il balance iniziale dell'account come base
        initial_balance = self.current_metrics.get('current_balance', 5000.0)  # Default 5000 per The5ers
        
        # Calcola il running maximum del balance
        max_balance = initial_balance
        max_drawdown = 0
        
        for entry in self.pnl_history:
            current_balance = initial_balance + entry['cumulative_pnl']
            
            # Aggiorna il massimo balance raggiunto
            if current_balance > max_balance:
                max_balance = current_balance
            
            # Calcola drawdown corrente
            if max_balance > 0:
                current_drawdown = ((max_balance - current_balance) / max_balance) * 100
                max_drawdown = max(max_drawdown, current_drawdown)
        
        return max_drawdown

    def analyze_log_file(self):
        """Analizza tutto il file di log per dati storici. Se il file non esiste, lo crea vuoto."""
        if not os.path.exists(self.log_file):
            print(f"⚠️ File di log non trovato: {self.log_file}. Creo file vuoto...")
            try:
                # Crea file vuoto
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                print(f"✅ File di log creato: {self.log_file}")
            except Exception as e:
                print(f"❌ Errore creazione file di log: {e}")
            return
        print(f"🔄 Analizzando file di log: {self.log_file}")
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            processed_lines = 0
            for line in lines:
                result = self.analyze_log_line(line)
                if result:
                    processed_lines += 1
            print(f"✅ Analizzate {processed_lines} righe significative su {len(lines)} totali")
            print(f"📊 Quantum Signals trovati: {self.current_metrics['quantum_signals']['total']}")
        except Exception as e:
            print(f"❌ Errore durante l'analisi del log: {e}")

    def analyze_log_line(self, line: str) -> Optional[dict]:
        """Analizza una riga di log e aggiorna i dati. Supporta sia formato compatto che a blocchi."""
        line = line.strip()
        if not line:
            return None

        timestamp = self.extract_timestamp(line)

        # Trade closed - aggiorna P&L
        match = re.search(r'Trade closed: (\w+) (BUY|SELL) (\d+\.\d+) lots at (\d+\.\d+), P&L: ([-+]?\d+\.\d+)', line, re.IGNORECASE)
        if match:
            symbol = match.group(1)
            direction = match.group(2)
            pnl = float(match.group(5))
            self.current_metrics['total_trades'] += 1
            self.current_metrics['total_pnl'] += pnl
            if pnl > 0:
                self.current_metrics['winning_trades'] += 1
            self.symbol_performance[symbol]['pnl'] += pnl
            self.symbol_performance[symbol]['trades'] += 1
            hour = timestamp.hour
            self.hourly_performance[hour]['pnl'] += pnl
            self.hourly_performance[hour]['trades'] += 1
            self.pnl_history.append({
                'timestamp': timestamp.isoformat(),
                'pnl': pnl,
                'cumulative_pnl': self.current_metrics['total_pnl'],
                'symbol': symbol,
                'direction': direction
            })
            # Associa il trade al segnale quantum più recente compatibile (stesso symbol, stessa direzione, esito None, entro 1 ora)
            for s in reversed(self.signals_timeline):
                if (
                    s['symbol'] == symbol and
                    s['direction'] == direction and
                    s.get('esito') is None and
                    abs((timestamp - datetime.fromisoformat(s['timestamp'])).total_seconds()) < 3600
                ):
                    s['esito'] = 'TRADE'
                    s['trade_pnl'] = pnl
                    s['trade_time'] = timestamp.isoformat()
                    break
            if self.current_metrics['total_trades'] > 0:
                self.current_metrics['win_rate'] = (self.current_metrics['winning_trades'] / self.current_metrics['total_trades']) * 100
            current_drawdown = self.calculate_max_drawdown()
            self.current_metrics['current_drawdown'] = current_drawdown
            self.current_metrics['max_drawdown'] = max(self.current_metrics['max_drawdown'], current_drawdown)
            return {'type': 'trade_closed', 'data': match.groups()}

        # Heartbeat con formato compatto (EURUSD: Bid=... E=... S=... C=...)
        match = re.search(r'(\w+): Bid=[\d\.]+.*E=(\d+\.\d+).*S=([-+]?\d+\.\d+)(?:.*C=(\d+\.\d+))?', line, re.IGNORECASE)
        if match:
            symbol = match.group(1)
            entropy = float(match.group(2))
            spin = float(match.group(3))
            confidence = float(match.group(4)) if match.group(4) is not None else None
            if entropy > 0 or abs(spin) > 0:
                self.current_metrics['quantum_signals']['total'] += 1
                if spin > 0:
                    self.current_metrics['quantum_signals']['buy'] += 1
                else:
                    self.current_metrics['quantum_signals']['sell'] += 1
                total = self.current_metrics['quantum_signals']['total']
                self.current_metrics['quantum_signals']['avg_entropy'] = (
                    (self.current_metrics['quantum_signals']['avg_entropy'] * (total - 1) + entropy) / total
                )
                self.current_metrics['quantum_signals']['avg_spin'] = (
                    (self.current_metrics['quantum_signals']['avg_spin'] * (total - 1) + spin) / total
                )
                if confidence is not None:
                    prev_avg_conf = self.current_metrics['quantum_signals']['avg_confidence']
                    self.current_metrics['quantum_signals']['avg_confidence'] = (
                        (prev_avg_conf * (total - 1) + confidence) / total
                    )
                self.signals_timeline.append({
                    'timestamp': timestamp.isoformat(),
                    'symbol': symbol,
                    'direction': 'BUY' if spin > 0 else 'SELL',
                    'entropy': entropy,
                    'spin': spin,
                    'confidence': confidence
                })
                return {'type': 'heartbeat', 'data': match.groups()}

        # Heartbeat con formato a blocchi (Symbol: ... Entropy (E): ... Spin (S): ... Confidence (C): ...)
        # Estrae il simbolo
        match_symbol = re.match(r'Symbol:\s*(\w+)', line)
        if match_symbol:
            self._last_symbol = match_symbol.group(1)
            return None
        # Estrae Entropy
        match_entropy = re.match(r'Entropy \(E\):\s*([-+]?\d+\.\d+)', line)
        if match_entropy and hasattr(self, '_last_symbol'):
            self._last_entropy = float(match_entropy.group(1))
            return None
        # Estrae Spin
        match_spin = re.match(r'Spin \(S\):\s*([-+]?\d+\.\d+)', line)
        if match_spin and hasattr(self, '_last_symbol') and hasattr(self, '_last_entropy'):
            spin = float(match_spin.group(1))
            entropy = self._last_entropy
            symbol = self._last_symbol
            # Confidence opzionale
            confidence = None
            match_conf = re.match(r'Confidence \(C\):\s*([-+]?\d+\.\d+)', line)
            if match_conf:
                confidence = float(match_conf.group(1))
            # Conta sempre il blocco heartbeat, anche se entropy/spin sono zero
            self.current_metrics['quantum_signals']['total'] += 1
            if spin > 0:
                self.current_metrics['quantum_signals']['buy'] += 1
            elif spin < 0:
                self.current_metrics['quantum_signals']['sell'] += 1
            # Calcola media solo se total > 0
            total = self.current_metrics['quantum_signals']['total']
            self.current_metrics['quantum_signals']['avg_entropy'] = (
                (self.current_metrics['quantum_signals']['avg_entropy'] * (total - 1) + entropy) / total
            )
            self.current_metrics['quantum_signals']['avg_spin'] = (
                (self.current_metrics['quantum_signals']['avg_spin'] * (total - 1) + spin) / total
            )
            if confidence is not None:
                prev_avg_conf = self.current_metrics['quantum_signals']['avg_confidence']
                self.current_metrics['quantum_signals']['avg_confidence'] = (
                    (prev_avg_conf * (total - 1) + confidence) / total
                )
            self.signals_timeline.append({
                'timestamp': timestamp.isoformat(),
                'symbol': symbol,
                'direction': 'BUY' if spin > 0 else ('SELL' if spin < 0 else 'NEUTRAL'),
                'entropy': entropy,
                'spin': spin,
                'confidence': confidence
            })
            # Pulisce i dati temporanei
            del self._last_symbol
            del self._last_entropy
            return {'type': 'heartbeat_block', 'data': (symbol, entropy, spin, confidence)}

        # Account info
        match = re.search(r'Account Balance: (\d+\.\d+), Equity: (\d+\.\d+)', line, re.IGNORECASE)
        if match:
            balance = float(match.group(1))
            equity = float(match.group(2))
            self.current_metrics['current_balance'] = balance
            self.current_metrics['current_equity'] = equity
            if balance > 0:
                self.current_metrics['profit_percentage'] = (self.current_metrics['total_pnl'] / balance) * 100
            self.balance_history.append({
                'timestamp': timestamp.isoformat(),
                'balance': balance,
                'equity': equity
            })
            return {'type': 'account_info', 'data': match.groups()}

        # Drawdown warning
        match = re.search(r'Drawdown warning: Current DD: (\d+\.\d+)%', line, re.IGNORECASE)
        if match:
            drawdown = float(match.group(1))
            self.current_metrics['current_drawdown'] = drawdown
            self.current_metrics['max_drawdown'] = max(self.current_metrics['max_drawdown'], drawdown)
            self.drawdown_history.append({
                'timestamp': timestamp.isoformat(),
                'drawdown': drawdown
            })
            return {'type': 'drawdown_warning', 'data': match.groups()}

        return None

    def extract_timestamp(self, line: str) -> datetime:
        """Estrae timestamp dalla riga"""
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',
            r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        return datetime.strptime(match.group(1), '%d/%m/%Y %H:%M:%S')
                    except:
                        try:
                            return datetime.strptime(match.group(1), '%d-%m-%Y %H:%M:%S')
                        except:
                            pass
        
        return datetime.now()

    def read_new_log_entries(self) -> List[str]:
        """Legge nuove entry dal file di log"""
        if not os.path.exists(self.log_file):
            return []
            
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                f.seek(self.last_log_position)
                new_lines = f.readlines()
                self.last_log_position = f.tell()
                return new_lines
        except Exception as e:
            print(f"❌ Errore lettura log: {e}")
            return []

    def get_compliance_status(self) -> Dict:
        """Ottiene stato compliance The5ers"""
        status = {}
        
        # Target check
        if self.current_metrics['profit_percentage'] >= self.step1_target:
            status['target'] = {
                'status': 'achieved',
                'message': f"✅ TARGET RAGGIUNTO: {self.current_metrics['profit_percentage']:.2f}%",
                'value': self.current_metrics['profit_percentage'],
                'target': self.step1_target
            }
        else:
            remaining = self.step1_target - self.current_metrics['profit_percentage']
            status['target'] = {
                'status': 'pending',
                'message': f"🎯 Target: {self.current_metrics['profit_percentage']:.2f}% / {self.step1_target}%",
                'value': self.current_metrics['profit_percentage'],
                'target': self.step1_target,
                'remaining': remaining
            }
        
        # Drawdown check
        dd = self.current_metrics['current_drawdown']
        if dd >= self.drawdown_hard:
            status['drawdown'] = {
                'status': 'critical',
                'message': f"🚨 DRAWDOWN CRITICO: {dd:.2f}%",
                'value': dd,
                'soft_limit': self.drawdown_soft,
                'hard_limit': self.drawdown_hard
            }
        elif dd >= self.drawdown_soft:
            status['drawdown'] = {
                'status': 'warning',
                'message': f"⚠️ DRAWDOWN WARNING: {dd:.2f}%",
                'value': dd,
                'soft_limit': self.drawdown_soft,
                'hard_limit': self.drawdown_hard
            }
        else:
            status['drawdown'] = {
                'status': 'ok',
                'message': f"✅ Drawdown OK: {dd:.2f}%",
                'value': dd,
                'soft_limit': self.drawdown_soft,
                'hard_limit': self.drawdown_hard
            }
        
        return status

    def create_pnl_chart(self) -> Dict:
        """Crea grafico P&L nel tempo con annotazioni su picchi e minimi"""
        if not self.pnl_history:
            trace = go.Scatter(
                x=[datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                y=[0],
                mode='lines+markers',
                name='Cumulative P&L',
                line=dict(color='#00d4aa', width=2),
                marker=dict(size=4)
            )
            layout = go.Layout(
                title='Cumulative P&L Over Time',
                xaxis=dict(title='Time'),
                yaxis=dict(title='P&L ($)'),
                hovermode='x unified',
                plot_bgcolor='#f9f9f9',
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        text='No trades yet',
                        showarrow=False,
                        font=dict(size=16, color='gray')
                    )
                ]
            )
            return {
                'data': [trace.to_plotly_json()],
                'layout': layout.to_plotly_json()
            }
        timestamps = [item['timestamp'] for item in self.pnl_history]
        cumulative_pnl = [item['cumulative_pnl'] for item in self.pnl_history]
        # Annotazioni su massimo e minimo P&L
        max_pnl = max(cumulative_pnl)
        min_pnl = min(cumulative_pnl)
        max_idx = cumulative_pnl.index(max_pnl)
        min_idx = cumulative_pnl.index(min_pnl)
        annotations = [
            dict(
                x=timestamps[max_idx],
                y=max_pnl,
                xref='x',
                yref='y',
                text=f'Picco P&L: {max_pnl:.2f}',
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                font=dict(color='green', size=12)
            ),
            dict(
                x=timestamps[min_idx],
                y=min_pnl,
                xref='x',
                yref='y',
                text=f'Min P&L: {min_pnl:.2f}',
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=40,
                font=dict(color='red', size=12)
            )
        ]
        trace = go.Scatter(
            x=timestamps,
            y=cumulative_pnl,
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='#00d4aa', width=2),
            marker=dict(size=4)
        )
        layout = go.Layout(
            title='Cumulative P&L Over Time',
            xaxis=dict(title='Time'),
            yaxis=dict(title='P&L ($)'),
            hovermode='x unified',
            plot_bgcolor='#f9f9f9',
            annotations=annotations
        )
        return {
            'data': [trace.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_drawdown_chart(self) -> Dict:
        """Crea grafico drawdown con annotazioni su superamento limiti"""
        if not self.drawdown_history:
            trace = go.Scatter(
                x=[datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                y=[0],
                mode='lines+markers',
                name='Drawdown',
                line=dict(color='#ff6b6b', width=2),
                marker=dict(size=4),
                fill='tozeroy'
            )
            layout = go.Layout(
                title='Drawdown Over Time',
                xaxis=dict(title='Time'),
                yaxis=dict(title='Drawdown (%)'),
                hovermode='x unified',
                plot_bgcolor='#f9f9f9',
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        text='No drawdown data yet',
                        showarrow=False,
                        font=dict(size=16, color='gray')
                    )
                ]
            )
            return {
                'data': [trace.to_plotly_json()],
                'layout': layout.to_plotly_json()
            }
        timestamps = [item['timestamp'] for item in self.drawdown_history]
        drawdowns = [item['drawdown'] for item in self.drawdown_history]
        # Annotazioni su superamento limiti
        annotations = []
        for i, dd in enumerate(drawdowns):
            if dd >= self.drawdown_hard:
                annotations.append(dict(
                    x=timestamps[i],
                    y=dd,
                    xref='x',
                    yref='y',
                    text=f'🚨 Hard Limit: {dd:.2f}%',
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-30,
                    font=dict(color='red', size=12)
                ))
            elif dd >= self.drawdown_soft:
                annotations.append(dict(
                    x=timestamps[i],
                    y=dd,
                    xref='x',
                    yref='y',
                    text=f'⚠️ Soft Limit: {dd:.2f}%',
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-30,
                    font=dict(color='orange', size=12)
                ))
        trace = go.Scatter(
            x=timestamps,
            y=drawdowns,
            mode='lines+markers',
            name='Drawdown',
            line=dict(color='#ff6b6b', width=2),
            marker=dict(size=4),
            fill='tozeroy'
        )
        soft_limit_line = go.Scatter(
            x=timestamps,
            y=[self.drawdown_soft] * len(timestamps),
            mode='lines',
            name='Soft Limit',
            line=dict(color='orange', width=1, dash='dash')
        )
        hard_limit_line = go.Scatter(
            x=timestamps,
            y=[self.drawdown_hard] * len(timestamps),
            mode='lines',
            name='Hard Limit',
            line=dict(color='red', width=1, dash='dash')
        )
        layout = go.Layout(
            title='Drawdown Over Time',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Drawdown (%)'),
            hovermode='x unified',
            plot_bgcolor='#f9f9f9',
            annotations=annotations
        )
        return {
            'data': [trace.to_plotly_json(), soft_limit_line.to_plotly_json(), hard_limit_line.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_balance_chart(self) -> Dict:
        """Crea grafico balance/equity con colori ben distinti e sempre visibili"""
        if not self.balance_history or len(self.balance_history) < 2:
            # Mostra almeno due punti fittizi per evitare problemi di visualizzazione
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            balance_trace = go.Scatter(
                x=[now, now],
                y=[5000, 5000],
                mode='lines+markers',
                name='Balance',
                line=dict(color='#00d4aa', width=2),  # Aqua
                marker=dict(size=4)
            )
            equity_trace = go.Scatter(
                x=[now, now],
                y=[5000, 5000],
                mode='lines+markers',
                name='Equity',
                line=dict(color='orange', width=2),  # Arancione
                marker=dict(size=4)
            )
            layout = go.Layout(
                title='Balance vs Equity',
                xaxis=dict(title='Time'),
                yaxis=dict(title='Amount ($)'),
                hovermode='x unified',
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        text='No balance history yet',
                        showarrow=False,
                        font=dict(size=16, color='gray')
                    )
                ]
            )
            return {
                'data': [balance_trace.to_plotly_json(), equity_trace.to_plotly_json()],
                'layout': layout.to_plotly_json()
            }
        timestamps = [item['timestamp'] for item in self.balance_history]
        balances = [item['balance'] for item in self.balance_history]
        equities = [item['equity'] for item in self.balance_history]
        balance_trace = go.Scatter(
            x=timestamps,
            y=balances,
            mode='lines+markers',
            name='Balance',
            line=dict(color='#00d4aa', width=2),  # Aqua
            marker=dict(size=4)
        )
        equity_trace = go.Scatter(
            x=timestamps,
            y=equities,
            mode='lines+markers',
            name='Equity',
            line=dict(color='orange', width=2),  # Arancione
            marker=dict(size=4)
        )
        layout = go.Layout(
            title='Account Balance & Equity',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Amount ($)'),
            hovermode='x unified'
        )
        return {
            'data': [balance_trace.to_plotly_json(), equity_trace.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_hourly_chart(self) -> Dict:
        """Crea grafico performance oraria"""
        if not self.hourly_performance or all(self.hourly_performance[hour]['trades'] == 0 for hour in range(24)):
            hours = list(range(24))
            pnl_values = [0] * 24
            pnl_trace = go.Bar(
                x=hours,
                y=pnl_values,
                name='P&L per Hour',
                marker=dict(color='lightgray')
            )
            layout = go.Layout(
                title='Performance by Hour of Day',
                xaxis=dict(title='Hour', tickvals=hours, ticktext=[f"{h:02d}:00" for h in hours]),
                yaxis=dict(title='P&L ($)'),
                hovermode='x unified',
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        text='No hourly data yet',
                        showarrow=False,
                        font=dict(size=16, color='gray')
                    )
                ]
            )
            return {
                'data': [pnl_trace.to_plotly_json()],
                'layout': layout.to_plotly_json()
            }
        hours = list(range(24))
        pnl_values = [self.hourly_performance[hour]['pnl'] for hour in hours]
        trade_counts = [self.hourly_performance[hour]['trades'] for hour in hours]
        pnl_trace = go.Bar(
            x=hours,
            y=pnl_values,
            name='P&L per Hour',
            marker=dict(color=['green' if pnl >= 0 else 'red' for pnl in pnl_values])
        )
        layout = go.Layout(
            title='Performance by Hour of Day',
            xaxis=dict(title='Hour', tickvals=hours, ticktext=[f"{h:02d}:00" for h in hours]),
            yaxis=dict(title='P&L ($)'),
            hovermode='x unified'
        )
        return {
            'data': [pnl_trace.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_symbols_chart(self) -> Dict:
        """Crea grafico performance per simbolo"""
        if not self.symbol_performance or all(self.symbol_performance[symbol]['trades'] == 0 for symbol in self.symbol_performance):
            symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'NAS100']
            pnl_values = [0] * len(symbols)
            pnl_trace = go.Bar(
                x=symbols,
                y=pnl_values,
                name='P&L per Symbol',
                marker=dict(color='lightgray')
            )
            layout = go.Layout(
                title='Performance by Symbol',
                xaxis=dict(title='Symbol'),
                yaxis=dict(title='P&L ($)'),
                hovermode='x unified',
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        text='No symbol data yet',
                        showarrow=False,
                        font=dict(size=16, color='gray')
                    )
                ]
            )
            return {
                'data': [pnl_trace.to_plotly_json()],
                'layout': layout.to_plotly_json()
            }
        symbols = list(self.symbol_performance.keys())
        pnl_values = [self.symbol_performance[symbol]['pnl'] for symbol in symbols]
        trade_counts = [self.symbol_performance[symbol]['trades'] for symbol in symbols]
        pnl_trace = go.Bar(
            x=symbols,
            y=pnl_values,
            name='P&L per Symbol',
            marker=dict(color=['green' if pnl >= 0 else 'red' for pnl in pnl_values])
        )
        layout = go.Layout(
            title='Performance by Symbol',
            xaxis=dict(title='Symbol'),
            yaxis=dict(title='P&L ($)'),
            hovermode='x unified'
        )
        return {
            'data': [pnl_trace.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_signals_chart(self) -> Dict:
        """Crea grafico distribuzione segnali quantum"""
        if not self.signals_timeline:
            buy_trace = go.Scatter(
                x=[0.5],
                y=[0],
                mode='markers',
                name='Buy Signals',
                marker=dict(color='green', size=8)
            )
            sell_trace = go.Scatter(
                x=[0.5],
                y=[0],
                mode='markers',
                name='Sell Signals',
                marker=dict(color='red', size=8)
            )
            layout = go.Layout(
                title='Quantum Signals Distribution',
                xaxis=dict(title='Entropy'),
                yaxis=dict(title='Spin'),
                hovermode='closest',
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        text='No signals data yet',
                        showarrow=False,
                        font=dict(size=16, color='gray')
                    )
                ]
            )
            return {
                'data': [buy_trace.to_plotly_json(), sell_trace.to_plotly_json()],
                'layout': layout.to_plotly_json()
            }
        buy_signals = [s for s in self.signals_timeline if s['direction'] == 'BUY']
        sell_signals = [s for s in self.signals_timeline if s['direction'] == 'SELL']
        buy_trace = go.Scatter(
            x=[s['entropy'] for s in buy_signals],
            y=[s['spin'] for s in buy_signals],
            mode='markers',
            name='Buy Signals',
            marker=dict(color='green', size=8)
        )
        sell_trace = go.Scatter(
            x=[s['entropy'] for s in sell_signals],
            y=[s['spin'] for s in sell_signals],
            mode='markers',
            name='Sell Signals',
            marker=dict(color='red', size=8)
        )
        layout = go.Layout(
            title='Quantum Signals Distribution',
            xaxis=dict(title='Entropy'),
            yaxis=dict(title='Spin'),
            hovermode='closest'
        )
        return {
            'data': [buy_trace.to_plotly_json(), sell_trace.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def send_realtime_notification(self, event_type: str, message: str, details: dict = None):
        """
        Invia una notifica real-time (log, print, estendibile per email/webhook).
        event_type: 'mt5_disconnect', 'drawdown_critical', 'target_reached', ecc.
        message: testo della notifica.
        details: dict opzionale con info aggiuntive.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        notif = {
            'event_type': event_type,
            'message': message,
            'timestamp': timestamp,
            'details': details or {}
        }
        print(f"[NOTIFICA][{event_type}] {timestamp}: {message}")
        self.realtime_notifications.appendleft(notif)

    def monitoring_loop(self):
        """Loop di monitoraggio in background"""
        self.is_monitoring = True

        # Carica dati iniziali dal log (popola tutte le metriche aggregate)
        print("🔄 Caricamento iniziale dati dal log...")
        self.analyze_log_file()

        # Forza connessione MT5 se richiesto SOLO per balance/equity/posizioni
        if self.use_mt5:
            print("🔄 Tentativo connessione a MetaTrader5...")
            if not mt5.initialize() and mt5.last_error() != (0, 'No error'):
                print(f"❌ Errore connessione MT5: {mt5.last_error()}")
                self.mt5_connected = False
            else:
                self.mt5_connected = True
                print("✅ Connessione a MT5 riuscita!")
                print("🔄 Caricamento stato account MT5...")
                self.load_complete_mt5_data()

        mt5_update_counter = 0

        while self.is_monitoring:
            try:
                # Leggi nuove entry dal log (per real-time updates)
                new_lines = self.read_new_log_entries()

                # Processa nuove entry (aggiorna metriche aggregate)
                for line in new_lines:
                    self.analyze_log_line(line)

                # Aggiorna solo balance/equity/posizioni da MT5 ogni 30 secondi
                if self.use_mt5 and mt5_update_counter >= 30:
                    self.load_complete_mt5_data()
                    mt5_update_counter = 0
                else:
                    mt5_update_counter += 1

                # Aggiorna timestamp
                self.last_update = datetime.now()

                # Notifica disconnessione MT5
                if self.use_mt5 and not self.mt5_connected:
                    self.send_realtime_notification(
                        event_type='mt5_disconnect',
                        message='❌ Disconnessione da MT5 rilevata!',
                        details={'mt5_connected': self.mt5_connected}
                    )

                # Notifica drawdown critico
                if self.current_metrics['current_drawdown'] >= self.drawdown_hard:
                    self.send_realtime_notification(
                        event_type='drawdown_critical',
                        message=f'🚨 Drawdown critico: {self.current_metrics["current_drawdown"]:.2f}',
                        details={'drawdown': self.current_metrics['current_drawdown']}
                    )

                # Notifica target raggiunto
                if self.current_metrics['profit_percentage'] >= self.step1_target:
                    self.send_realtime_notification(
                        event_type='target_reached',
                        message=f'✅ Target raggiunto: {self.current_metrics["profit_percentage"]:.2f}%',
                        details={'profit_percentage': self.current_metrics['profit_percentage']}
                    )

                # Attendi prima del prossimo update
                time.sleep(1)  # Update ogni secondo per real-time
            except Exception as e:
                print(f"❌ Errore nel monitoring loop: {e}")
                time.sleep(5)

    def start_dashboard(self, host='127.0.0.1', port=5000, debug=False):
        """Avvia la dashboard web"""
        

        # Registra tutte le route prima di avviare il monitoring e il server Flask
        self.setup_routes()

        # Avvia monitoring in background
        monitoring_thread = threading.Thread(target=self.monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()

        # Debug: stampa tutte le route registrate
        print('[DEBUG] Route Flask registrate (start_dashboard):')
        for rule in self.app.url_map.iter_rules():
            print(f"  {rule}")

        print(f"🚀 Avvio dashboard web su http://{host}:{port}")
        print("📊 Dashboard disponibile nel browser")
        print("🔄 Monitoraggio real-time attivo")
        print("-" * 60)

        # Avvia Flask app
        self.app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """Funzione principale con auto-detect config per sistema mono"""
    config_file = None
    log_file = None
    
    if len(sys.argv) >= 2:
        config_file = sys.argv[1]
        log_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(config_file):
            print(f"❌ Config file non trovato: {config_file}")
            print("💡 Provo auto-detect configurazione...")
            config_file = None
    
    # Crea dashboard (auto-detect config se None)
    dashboard = The5ersGraphicalDashboard(config_file, log_file)


    try:
        # Avvia dashboard Flask su porta alternativa per debug
        dashboard.start_dashboard(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard interrotta dall'utente")
        dashboard.is_monitoring = False
        # Chiudi la connessione MT5 solo alla fine
        if hasattr(mt5, 'shutdown'):
            mt5.shutdown()

if __name__ == "__main__":
    main()