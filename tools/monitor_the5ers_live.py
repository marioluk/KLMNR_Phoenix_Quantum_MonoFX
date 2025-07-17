#!/usr/bin/env python3
"""
THE5ERS LIVE TRADING MONITOR
Monitoraggio in tempo reale dei parametri The5ers e metriche chiave
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import sys

class The5ersMonitor:
    def __init__(self, config_file: str, log_file: str = None):
        """
        Inizializza il monitor The5ers
        
        Args:
            config_file: Path al file di configurazione JSON
            log_file: Path al file di log (opzionale, auto-detect da config)
        """
        self.config_file = config_file
        self.config = self.load_config()
        
        # Auto-detect log file se non specificato
        if log_file is None:
            self.log_file = self.config.get('logging', {}).get('log_file', 'logs/trading.log')
        else:
            self.log_file = log_file
            
        # Parametri The5ers
        self.the5ers_params = self.config.get('THE5ERS_specific', {})
        self.step1_target = self.the5ers_params.get('step1_target', 8)  # %
        self.drawdown_soft = self.the5ers_params.get('drawdown_protection', {}).get('soft_limit', 2)  # %
        self.drawdown_hard = self.the5ers_params.get('drawdown_protection', {}).get('hard_limit', 5)  # %
        
        # Metriche tracking
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'daily_trades': 0,
            'positions_open': 0,
            'last_trade_time': None,
            'account_balance': 0.0,
            'account_equity': 0.0,
            'profit_percentage': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'quantum_signals': {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'signal_accuracy': 0.0,
                'entropy_avg': 0.0,
                'spin_avg': 0.0
            }
        }
        
        # Status flags
        self.is_monitoring = False
        self.last_log_position = 0
        
        print(f"🔧 THE5ERS MONITOR INIZIALIZZATO")
        print(f"📊 Target Step 1: {self.step1_target}%")
        print(f"⚠️  Drawdown Soft: {self.drawdown_soft}%")
        print(f"🚨 Drawdown Hard: {self.drawdown_hard}%")
        print(f"📄 Log File: {self.log_file}")
        print("-" * 60)

    def load_config(self) -> Dict:
        """Carica la configurazione JSON"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Errore caricamento config: {e}")
            return {}

    def parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Analizza una riga di log e estrae informazioni rilevanti
        
        Returns:
            Dict con info parsed o None se non rilevante
        """
        line = line.strip()
        if not line:
            return None
            
        # Pattern per diversi tipi di log
        patterns = {
            'trade_opened': r'Trade opened: (\w+) (BUY|SELL) (\d+\.\d+) lots at (\d+\.\d+)',
            'trade_closed': r'Trade closed: (\w+) (BUY|SELL) (\d+\.\d+) lots at (\d+\.\d+), P&L: ([-+]?\d+\.\d+)',
            'quantum_signal': r'Quantum signal: (\w+) (BUY|SELL) - Entropy: (\d+\.\d+), Spin: ([-+]?\d+\.\d+)',
            'account_info': r'Account Balance: (\d+\.\d+), Equity: (\d+\.\d+), Margin: (\d+\.\d+)',
            'position_info': r'Open positions: (\d+)',
            'daily_reset': r'Daily trading reset',
            'drawdown_warning': r'Drawdown warning: Current DD: (\d+\.\d+)%',
            'bias_warning': r'Bias warning: (Buy|Sell) bias detected: (\d+\.\d+)%'
        }
        
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return {
                    'type': pattern_name,
                    'timestamp': self.extract_timestamp(line),
                    'data': match.groups()
                }
        
        return None

    def extract_timestamp(self, line: str) -> Optional[datetime]:
        """Estrae timestamp dalla riga di log"""
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',
            r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in timestamp_patterns:
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

    def update_metrics(self, parsed_data: Dict):
        """Aggiorna le metriche basandosi sui dati parsed"""
        data_type = parsed_data['type']
        data = parsed_data['data']
        
        if data_type == 'trade_opened':
            self.metrics['positions_open'] += 1
            
        elif data_type == 'trade_closed':
            # symbol, direction, lots, price, pnl
            pnl = float(data[4])
            self.metrics['total_trades'] += 1
            self.metrics['positions_open'] = max(0, self.metrics['positions_open'] - 1)
            self.metrics['last_trade_time'] = parsed_data['timestamp']
            
            if pnl > 0:
                self.metrics['winning_trades'] += 1
                self.metrics['total_profit'] += pnl
                self.metrics['consecutive_wins'] += 1
                self.metrics['consecutive_losses'] = 0
                self.metrics['max_consecutive_wins'] = max(
                    self.metrics['max_consecutive_wins'], 
                    self.metrics['consecutive_wins']
                )
                if pnl > self.metrics['largest_win']:
                    self.metrics['largest_win'] = pnl
                    
            else:
                self.metrics['losing_trades'] += 1
                self.metrics['total_loss'] += abs(pnl)
                self.metrics['consecutive_losses'] += 1
                self.metrics['consecutive_wins'] = 0
                self.metrics['max_consecutive_losses'] = max(
                    self.metrics['max_consecutive_losses'], 
                    self.metrics['consecutive_losses']
                )
                if abs(pnl) > self.metrics['largest_loss']:
                    self.metrics['largest_loss'] = abs(pnl)
            
            # Calcola metriche derivate
            self.calculate_derived_metrics()
            
        elif data_type == 'quantum_signal':
            # symbol, direction, entropy, spin
            self.metrics['quantum_signals']['total_signals'] += 1
            if data[1].upper() == 'BUY':
                self.metrics['quantum_signals']['buy_signals'] += 1
            else:
                self.metrics['quantum_signals']['sell_signals'] += 1
                
            entropy = float(data[2])
            spin = float(data[3])
            
            # Media mobile semplice per entropy e spin
            total_signals = self.metrics['quantum_signals']['total_signals']
            self.metrics['quantum_signals']['entropy_avg'] = (
                (self.metrics['quantum_signals']['entropy_avg'] * (total_signals - 1) + entropy) / total_signals
            )
            self.metrics['quantum_signals']['spin_avg'] = (
                (self.metrics['quantum_signals']['spin_avg'] * (total_signals - 1) + spin) / total_signals
            )
            
        elif data_type == 'account_info':
            # balance, equity, margin
            self.metrics['account_balance'] = float(data[0])
            self.metrics['account_equity'] = float(data[1])
            
        elif data_type == 'drawdown_warning':
            # current_dd_percent
            self.metrics['current_drawdown'] = float(data[0])
            self.metrics['max_drawdown'] = max(self.metrics['max_drawdown'], self.metrics['current_drawdown'])

    def calculate_derived_metrics(self):
        """Calcola metriche derivate"""
        total_trades = self.metrics['total_trades']
        
        if total_trades > 0:
            self.metrics['win_rate'] = (self.metrics['winning_trades'] / total_trades) * 100
            
            if self.metrics['winning_trades'] > 0:
                self.metrics['avg_win'] = self.metrics['total_profit'] / self.metrics['winning_trades']
                
            if self.metrics['losing_trades'] > 0:
                self.metrics['avg_loss'] = self.metrics['total_loss'] / self.metrics['losing_trades']
                
            if self.metrics['total_loss'] > 0:
                self.metrics['profit_factor'] = self.metrics['total_profit'] / self.metrics['total_loss']
            else:
                self.metrics['profit_factor'] = float('inf') if self.metrics['total_profit'] > 0 else 0
                
        # Calcola percentuale di profitto
        if self.metrics['account_balance'] > 0:
            net_profit = self.metrics['total_profit'] - self.metrics['total_loss']
            self.metrics['profit_percentage'] = (net_profit / self.metrics['account_balance']) * 100
            
        # Calcola accuratezza segnali quantum
        total_signals = self.metrics['quantum_signals']['total_signals']
        if total_signals > 0:
            buy_signals = self.metrics['quantum_signals']['buy_signals']
            sell_signals = self.metrics['quantum_signals']['sell_signals']
            
            # Approssimazione accuratezza basata su win rate
            if self.metrics['winning_trades'] > 0:
                self.metrics['quantum_signals']['signal_accuracy'] = self.metrics['win_rate']

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

    def check_the5ers_compliance(self) -> Dict[str, str]:
        """Controlla compliance con regole The5ers"""
        status = {}
        
        # Check profit target
        if self.metrics['profit_percentage'] >= self.step1_target:
            status['target'] = f"✅ TARGET RAGGIUNTO: {self.metrics['profit_percentage']:.2f}%"
        else:
            remaining = self.step1_target - self.metrics['profit_percentage']
            status['target'] = f"🎯 Target: {self.metrics['profit_percentage']:.2f}% / {self.step1_target}% (Mancano: {remaining:.2f}%)"
        
        # Check drawdown
        if self.metrics['current_drawdown'] >= self.drawdown_hard:
            status['drawdown'] = f"🚨 DRAWDOWN CRITICO: {self.metrics['current_drawdown']:.2f}% (Limite: {self.drawdown_hard}%)"
        elif self.metrics['current_drawdown'] >= self.drawdown_soft:
            status['drawdown'] = f"⚠️  DRAWDOWN WARNING: {self.metrics['current_drawdown']:.2f}% (Soft: {self.drawdown_soft}%)"
        else:
            status['drawdown'] = f"✅ Drawdown OK: {self.metrics['current_drawdown']:.2f}%"
        
        # Check daily trades
        max_daily = self.config.get('risk_parameters', {}).get('max_daily_trades', 5)
        if self.metrics['daily_trades'] >= max_daily:
            status['daily_trades'] = f"⚠️  LIMITE DAILY TRADES: {self.metrics['daily_trades']}/{max_daily}"
        else:
            status['daily_trades'] = f"✅ Daily trades: {self.metrics['daily_trades']}/{max_daily}"
        
        # Check positions
        max_positions = self.config.get('risk_parameters', {}).get('max_positions', 1)
        if self.metrics['positions_open'] >= max_positions:
            status['positions'] = f"⚠️  MAX POSITIONS: {self.metrics['positions_open']}/{max_positions}"
        else:
            status['positions'] = f"✅ Positions: {self.metrics['positions_open']}/{max_positions}"
        
        return status

    def display_dashboard(self):
        """Mostra dashboard completo"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("🚀 THE5ERS LIVE TRADING MONITOR")
        print("=" * 80)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # THE5ERS COMPLIANCE
        print("📊 THE5ERS COMPLIANCE STATUS")
        print("-" * 40)
        compliance = self.check_the5ers_compliance()
        for key, value in compliance.items():
            print(f"   {value}")
        print()
        
        # ACCOUNT INFO
        print("💰 ACCOUNT INFORMATION")
        print("-" * 40)
        print(f"   Balance: ${self.metrics['account_balance']:.2f}")
        print(f"   Equity: ${self.metrics['account_equity']:.2f}")
        print(f"   Profit%: {self.metrics['profit_percentage']:.2f}%")
        print(f"   Net P&L: ${self.metrics['total_profit'] - self.metrics['total_loss']:.2f}")
        print()
        
        # TRADING STATISTICS
        print("📈 TRADING STATISTICS")
        print("-" * 40)
        print(f"   Total Trades: {self.metrics['total_trades']}")
        print(f"   Win Rate: {self.metrics['win_rate']:.1f}%")
        print(f"   Profit Factor: {self.metrics['profit_factor']:.2f}")
        print(f"   Avg Win: ${self.metrics['avg_win']:.2f}")
        print(f"   Avg Loss: ${self.metrics['avg_loss']:.2f}")
        print(f"   Largest Win: ${self.metrics['largest_win']:.2f}")
        print(f"   Largest Loss: ${self.metrics['largest_loss']:.2f}")
        print()
        
        # QUANTUM SIGNALS
        print("🔬 QUANTUM SIGNALS")
        print("-" * 40)
        qs = self.metrics['quantum_signals']
        print(f"   Total Signals: {qs['total_signals']}")
        print(f"   Buy/Sell: {qs['buy_signals']}/{qs['sell_signals']}")
        print(f"   Signal Accuracy: {qs['signal_accuracy']:.1f}%")
        print(f"   Avg Entropy: {qs['entropy_avg']:.3f}")
        print(f"   Avg Spin: {qs['spin_avg']:.3f}")
        print()
        
        # RISK METRICS
        print("⚠️  RISK METRICS")
        print("-" * 40)
        print(f"   Current Drawdown: {self.metrics['current_drawdown']:.2f}%")
        print(f"   Max Drawdown: {self.metrics['max_drawdown']:.2f}%")
        print(f"   Consecutive Wins: {self.metrics['consecutive_wins']}")
        print(f"   Consecutive Losses: {self.metrics['consecutive_losses']}")
        print(f"   Max Consecutive Wins: {self.metrics['max_consecutive_wins']}")
        print(f"   Max Consecutive Losses: {self.metrics['max_consecutive_losses']}")
        print()
        
        # SYSTEM STATUS
        print("🔧 SYSTEM STATUS")
        print("-" * 40)
        print(f"   Monitoring: {'🟢 ACTIVE' if self.is_monitoring else '🔴 INACTIVE'}")
        print(f"   Last Update: {datetime.now().strftime('%H:%M:%S')}")
        if self.metrics['last_trade_time']:
            print(f"   Last Trade: {self.metrics['last_trade_time'].strftime('%H:%M:%S')}")
        print()
        
        print("=" * 80)
        print("Press Ctrl+C to stop monitoring")
        print("=" * 80)

    def monitor_loop(self):
        """Loop principale di monitoraggio"""
        self.is_monitoring = True
        
        try:
            while self.is_monitoring:
                # Leggi nuove entry dal log
                new_lines = self.read_new_log_entries()
                
                # Processa nuove entry
                for line in new_lines:
                    parsed = self.parse_log_line(line)
                    if parsed:
                        self.update_metrics(parsed)
                
                # Aggiorna dashboard
                self.display_dashboard()
                
                # Attendi prima del prossimo update
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring interrotto dall'utente")
            self.is_monitoring = False
        except Exception as e:
            print(f"\n\n❌ Errore nel monitoring: {e}")
            self.is_monitoring = False

    def generate_report(self) -> str:
        """Genera report testuale completo"""
        report = []
        report.append("=" * 60)
        report.append("THE5ERS TRADING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Compliance
        report.append("THE5ERS COMPLIANCE:")
        compliance = self.check_the5ers_compliance()
        for key, value in compliance.items():
            report.append(f"  {value}")
        report.append("")
        
        # Performance
        report.append("PERFORMANCE METRICS:")
        report.append(f"  Total Trades: {self.metrics['total_trades']}")
        report.append(f"  Win Rate: {self.metrics['win_rate']:.1f}%")
        report.append(f"  Profit Factor: {self.metrics['profit_factor']:.2f}")
        report.append(f"  Net P&L: ${self.metrics['total_profit'] - self.metrics['total_loss']:.2f}")
        report.append(f"  Profit%: {self.metrics['profit_percentage']:.2f}%")
        report.append("")
        
        # Risk
        report.append("RISK ANALYSIS:")
        report.append(f"  Max Drawdown: {self.metrics['max_drawdown']:.2f}%")
        report.append(f"  Current Drawdown: {self.metrics['current_drawdown']:.2f}%")
        report.append(f"  Largest Win: ${self.metrics['largest_win']:.2f}")
        report.append(f"  Largest Loss: ${self.metrics['largest_loss']:.2f}")
        report.append("")
        
        # Quantum
        qs = self.metrics['quantum_signals']
        report.append("QUANTUM SIGNALS:")
        report.append(f"  Total Signals: {qs['total_signals']}")
        report.append(f"  Buy/Sell Ratio: {qs['buy_signals']}/{qs['sell_signals']}")
        report.append(f"  Signal Accuracy: {qs['signal_accuracy']:.1f}%")
        report.append(f"  Avg Entropy: {qs['entropy_avg']:.3f}")
        report.append(f"  Avg Spin: {qs['spin_avg']:.3f}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

    def save_report(self, filename: str = None):
        """Salva report su file"""
        if filename is None:
            filename = f"the5ers_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report salvato: {filename}")
        except Exception as e:
            print(f"❌ Errore salvataggio report: {e}")

def main():
    """Funzione principale"""
    if len(sys.argv) < 2:
        print("Usage: python monitor_the5ers_live.py <config_file> [log_file]")
        print("Example: python monitor_the5ers_live.py PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(config_file):
        print(f"❌ Config file non trovato: {config_file}")
        sys.exit(1)
    
    # Crea monitor
    monitor = The5ersMonitor(config_file, log_file)
    
    try:
        # Avvia monitoring
        print("🚀 Avvio monitoring The5ers...")
        print("Press Ctrl+C to stop and generate report")
        print("-" * 60)
        
        monitor.monitor_loop()
        
    except KeyboardInterrupt:
        print("\n\n📊 Generating final report...")
        monitor.save_report()
        print("✅ Monitoring terminato")

if __name__ == "__main__":
    main()
