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
    @staticmethod
    def get_default_config_path():
        """Restituisce il path centralizzato del file di configurazione challenge."""
        # 1. Cerca nella cartella 'config' della root del progetto
        config_root = os.path.join(os.path.dirname(__file__), '..', 'config', 'config_autonomous_challenge_production_ready.json')
        config_root = os.path.normpath(config_root)
        if os.path.exists(config_root):
            return config_root
        # 2. Cerca nella cartella superiore (legacy)
        challenge_config = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config_autonomous_challenge_production_ready.json')
        challenge_config = os.path.normpath(challenge_config)
        if os.path.exists(challenge_config):
            return challenge_config
        # 3. Fallback: cerca nella directory corrente
        fallback = os.path.join(os.getcwd(), 'config_autonomous_challenge_production_ready.json')
        return fallback

    @staticmethod
    def get_default_log_path(config: dict = None):
        """Restituisce il path del file di log più recente che corrisponde al pattern log_autonomous_challenge_*.log nella cartella logs/ della root del progetto."""
        import glob
        # Determina la root del progetto (un livello sopra la cartella corrente)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(project_root, 'logs')
        pattern = os.path.join(logs_dir, 'log_autonomous_challenge_*.log')
        log_files = glob.glob(pattern)
        if log_files:
            # Seleziona il file più recente
            log_files.sort(key=os.path.getmtime, reverse=True)
            return log_files[0]
        # Fallback: usa il log file dal config se esiste
        if config:
            log_path = config.get('logging', {}).get('log_file')
            if log_path:
                return log_path
        # Fallback finale: trading.log
        return os.path.join(logs_dir, 'trading.log')

    def __init__(self, config_file: str = None, log_file: str = None, use_mt5: bool = True):
        """
        Inizializza la dashboard grafica The5ers
        
        Args:
            config_file: Path al file di configurazione JSON (auto-detect se None)
            log_file: Path al file di log (opzionale, auto-detect da config)
            use_mt5: Se True, usa dati MT5 per analisi completa
        """
        # Auto-detect config file se non specificato (per sistema legacy)
        if config_file is None:
            config_file = self.get_default_config_path()
        
        self.config_file = config_file
        self.config = self.load_config()
        self.use_mt5 = use_mt5 and MT5_AVAILABLE
        
        # Auto-detect log file se non specificato
        if log_file is None:
            self.log_file = self.get_default_log_path(self.config)
        else:
            self.log_file = log_file
            
        # Parametri The5ers
        self.the5ers_params = self.config.get('THE5ERS_specific', {})
        self.step1_target = self.the5ers_params.get('step1_target', 8)
        self.drawdown_soft = self.the5ers_params.get('drawdown_protection', {}).get('soft_limit', 2)
        self.drawdown_hard = self.the5ers_params.get('drawdown_protection', {}).get('hard_limit', 5)
        
        # Configurazione MT5
        if self.use_mt5:
            self.mt5_config = self.config.get('metatrader5', {})
            self.challenge_start = datetime(2025, 7, 7, 0, 0, 0)  # Inizio challenge
            
        # Dati per grafici (con buffer limitato per performance)
        self.max_data_points = 1000
        self.pnl_history = deque(maxlen=self.max_data_points)
        self.drawdown_history = deque(maxlen=self.max_data_points)
        self.balance_history = deque(maxlen=self.max_data_points)
        self.trades_timeline = deque(maxlen=self.max_data_points)
        self.signals_timeline = deque(maxlen=self.max_data_points)
        self.hourly_performance = defaultdict(lambda: {'pnl': 0, 'trades': 0})
        self.symbol_performance = defaultdict(lambda: {'pnl': 0, 'trades': 0, 'win_rate': 0})
        
        # Metriche real-time
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
                'avg_spin': 0.0
            }
        }
        
        # Status monitoring
        self.is_monitoring = False
        self.last_log_position = 0
        self.last_update = datetime.now()
        self.mt5_connected = False
        
        # Flask app
        self.app = Flask(__name__)
        self.setup_routes()
        
        print(f"🎨 THE5ERS GRAPHICAL DASHBOARD INIZIALIZZATO")
        print(f"📊 Target Step 1: {self.step1_target}%")
        print(f"⚠️  Drawdown Soft: {self.drawdown_soft}%")
        print(f"🚨 Drawdown Hard: {self.drawdown_hard}%")
        print(f"📄 Log File: {self.log_file}")
        print(f"🔌 MT5 Integration: {'✅ Enabled' if self.use_mt5 else '❌ Disabled'}")
        print("-" * 60)

    def load_config(self) -> Dict:
        """Carica la configurazione JSON"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Errore caricamento config: {e}")
            return {}

    def setup_routes(self):
        """Configura le route Flask"""
        
        @self.app.route('/')
        def dashboard():
            """Pagina principale dashboard"""
            return render_template('dashboard.html')
            
        @self.app.route('/api/metrics')
        def get_metrics():
            """API per ottenere metriche correnti"""
            return jsonify(self.current_metrics)
            
        @self.app.route('/api/compliance')
        def get_compliance():
            """API per stato compliance The5ers"""
            return jsonify(self.get_compliance_status())
            
        @self.app.route('/api/charts/pnl')
        def get_pnl_chart():
            """API per grafico P&L nel tempo"""
            return jsonify(self.create_pnl_chart())
            
        @self.app.route('/api/charts/drawdown')
        def get_drawdown_chart():
            """API per grafico drawdown"""
            return jsonify(self.create_drawdown_chart())
            
        @self.app.route('/api/charts/balance')
        def get_balance_chart():
            """API per grafico balance"""
            return jsonify(self.create_balance_chart())
            
        @self.app.route('/api/charts/hourly')
        def get_hourly_chart():
            """API per performance oraria"""
            return jsonify(self.create_hourly_chart())
            
        @self.app.route('/api/charts/symbols')
        def get_symbols_chart():
            """API per performance per simbolo"""
            return jsonify(self.create_symbols_chart())
            
        @self.app.route('/api/charts/signals')
        def get_signals_chart():
            """API per analisi segnali quantum"""
            return jsonify(self.create_signals_chart())
            
        @self.app.route('/api/refresh_mt5')
        def refresh_mt5_data():
            """API per aggiornare dati completi da MT5"""
            if self.use_mt5:
                success = self.load_complete_mt5_data()
                return jsonify({'success': success})
            return jsonify({'success': False, 'message': 'MT5 not available'})

    def connect_mt5(self) -> bool:
        """Connette a MetaTrader5"""
        if not self.use_mt5:
            return False
            
        try:
            # Inizializza MT5
            if not mt5.initialize():
                print(f"❌ Errore inizializzazione MT5")
                return False
            
            # Login
            login = self.mt5_config.get('login')
            password = self.mt5_config.get('password')
            server = self.mt5_config.get('server')
            
            if not mt5.login(login, password, server):
                print(f"❌ Errore login MT5: {mt5.last_error()}")
                return False
            
            self.mt5_connected = True
            print(f"✅ Connesso a MT5 - Account: {login}")
            return True
            
        except Exception as e:
            print(f"❌ Errore connessione MT5: {e}")
            return False

    def load_complete_mt5_data(self) -> bool:
        """Carica dati completi da MT5 per tutta la challenge"""
        if not self.connect_mt5():
            return False
            
        try:
            print("🔄 Caricando dati completi da MT5...")
            
            # Ottieni account info
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
                return False
                
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
            
            return True
            
        except Exception as e:
            print(f"❌ Errore caricamento dati MT5: {e}")
            return False
        finally:
            if self.mt5_connected:
                mt5.shutdown()
                self.mt5_connected = False

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
            # ...existing code...
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
            if self.current_metrics['total_trades'] > 0:
                self.current_metrics['win_rate'] = (self.current_metrics['winning_trades'] / self.current_metrics['total_trades']) * 100
            current_drawdown = self.calculate_max_drawdown()
            self.current_metrics['current_drawdown'] = current_drawdown
            self.current_metrics['max_drawdown'] = max(self.current_metrics['max_drawdown'], current_drawdown)
            return {'type': 'trade_closed', 'data': match.groups()}

        # Heartbeat con formato compatto (EURUSD: Bid=... E=... S=...)
        match = re.search(r'(\w+): Bid=[\d\.]+.*E=(\d+\.\d+).*S=([-+]?\d+\.\d+)', line, re.IGNORECASE)
        if match:
            symbol = match.group(1)
            entropy = float(match.group(2))
            spin = float(match.group(3))
            # ...existing code...
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
                self.signals_timeline.append({
                    'timestamp': timestamp.isoformat(),
                    'symbol': symbol,
                    'direction': 'BUY' if spin > 0 else 'SELL',
                    'entropy': entropy,
                    'spin': spin
                })
            return {'type': 'heartbeat', 'data': match.groups()}

        # Heartbeat con formato a blocchi (Symbol: ... Entropy (E): ... Spin (S): ...)
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
            # ...existing code...
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
                self.signals_timeline.append({
                    'timestamp': timestamp.isoformat(),
                    'symbol': symbol,
                    'direction': 'BUY' if spin > 0 else 'SELL',
                    'entropy': entropy,
                    'spin': spin
                })
            # Pulisce i dati temporanei
            del self._last_symbol
            del self._last_entropy
            return {'type': 'heartbeat_block', 'data': (symbol, entropy, spin)}

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
        """Crea grafico P&L nel tempo"""
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
            hovermode='x unified'
        )
        return {
            'data': [trace.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_drawdown_chart(self) -> Dict:
        """Crea grafico drawdown"""
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
            hovermode='x unified'
        )
        return {
            'data': [trace.to_plotly_json(), soft_limit_line.to_plotly_json(), hard_limit_line.to_plotly_json()],
            'layout': layout.to_plotly_json()
        }

    def create_balance_chart(self) -> Dict:
        """Crea grafico balance/equity"""
        if not self.balance_history:
            balance_trace = go.Scatter(
                x=[datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                y=[5000],
                mode='lines',
                name='Balance',
                line=dict(color='#4ecdc4', width=2)
            )
            equity_trace = go.Scatter(
                x=[datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                y=[5000],
                mode='lines',
                name='Equity',
                line=dict(color='#f7b731', width=2)
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
            mode='lines',
            name='Balance',
            line=dict(color='#4ecdc4', width=2)
        )
        equity_trace = go.Scatter(
            x=timestamps,
            y=equities,
            mode='lines',
            name='Equity',
            line=dict(color='#45b7d1', width=2)
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

    def monitoring_loop(self):
        """Loop di monitoraggio in background"""
        self.is_monitoring = True
        
        # Carica dati iniziali dal log
        print("🔄 Caricamento iniziale dati dal log...")
        self.analyze_log_file()
        
        # Carica dati completi da MT5 se disponibile
        if self.use_mt5:
            print("🔄 Caricamento iniziale dati MT5...")
            self.load_complete_mt5_data()
        
        mt5_update_counter = 0
        
        while self.is_monitoring:
            try:
                # Leggi nuove entry dal log (per real-time updates)
                new_lines = self.read_new_log_entries()
                
                # Processa nuove entry
                for line in new_lines:
                    self.analyze_log_line(line)
                
                # Aggiorna dati MT5 ogni 30 secondi
                if self.use_mt5 and mt5_update_counter >= 30:
                    self.load_complete_mt5_data()
                    mt5_update_counter = 0
                else:
                    mt5_update_counter += 1
                
                # Aggiorna timestamp
                self.last_update = datetime.now()
                
                # Attendi prima del prossimo update
                time.sleep(1)  # Update ogni secondo per real-time
                
            except Exception as e:
                print(f"❌ Errore nel monitoring loop: {e}")
                time.sleep(5)

    def start_dashboard(self, host='127.0.0.1', port=5000, debug=False):
        """Avvia la dashboard web"""
        
        # Avvia monitoring in background
        monitoring_thread = threading.Thread(target=self.monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        print(f"🚀 Avvio dashboard web su http://{host}:{port}")
        print("📊 Dashboard disponibile nel browser")
        print("🔄 Monitoraggio real-time attivo")
        print("-" * 60)
        
        # Avvia Flask app
        self.app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """Funzione principale con auto-detect config per sistema legacy"""
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
        # Avvia dashboard con accesso remoto
        dashboard.start_dashboard(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard interrotta dall'utente")
        dashboard.is_monitoring = False

if __name__ == "__main__":
    main()
