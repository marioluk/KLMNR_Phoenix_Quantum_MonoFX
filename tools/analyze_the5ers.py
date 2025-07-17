#!/usr/bin/env python3
"""
THE5ERS METRICS ANALYZER
Script per analisi dettagliata delle metriche da file di log
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

class The5ersAnalyzer:
    def __init__(self, config_file: str, log_file: str):
        """
        Inizializza l'analyzer per analisi post-trading
        
        Args:
            config_file: Path al file di configurazione JSON
            log_file: Path al file di log da analizzare
        """
        self.config_file = config_file
        self.log_file = log_file
        self.config = self.load_config()
        
        # Parametri The5ers
        self.the5ers_params = self.config.get('THE5ERS_specific', {})
        self.step1_target = self.the5ers_params.get('step1_target', 8)
        self.drawdown_soft = self.the5ers_params.get('drawdown_protection', {}).get('soft_limit', 2)
        self.drawdown_hard = self.the5ers_params.get('drawdown_protection', {}).get('hard_limit', 5)
        
        # Dati per analisi
        self.trades = []
        self.signals = []
        self.account_history = []
        self.daily_stats = defaultdict(lambda: {
            'trades': 0,
            'profit': 0.0,
            'signals': 0,
            'drawdown': 0.0
        })
        
        print(f"📊 THE5ERS ANALYZER INIZIALIZZATO")
        print(f"📄 Config: {config_file}")
        print(f"📄 Log: {log_file}")
        print("-" * 60)

    def load_config(self) -> Dict:
        """Carica configurazione JSON"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Errore caricamento config: {e}")
            return {}

    def parse_log_file(self):
        """Analizza completamente il file di log"""
        if not os.path.exists(self.log_file):
            print(f"❌ Log file non trovato: {self.log_file}")
            return
            
        print("🔍 Analizzando file di log...")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                self.parse_log_line(line.strip(), line_num)
        
        print(f"✅ Analisi completata:")
        print(f"   - {len(self.trades)} trades trovati")
        print(f"   - {len(self.signals)} segnali quantum")
        print(f"   - {len(self.account_history)} aggiornamenti account")
        print()

    def parse_log_line(self, line: str, line_num: int):
        """Analizza singola riga di log"""
        if not line:
            return
            
        timestamp = self.extract_timestamp(line)
        
        # Trade opened
        match = re.search(r'Trade opened: (\w+) (BUY|SELL) (\d+\.\d+) lots at (\d+\.\d+)', line, re.IGNORECASE)
        if match:
            trade = {
                'timestamp': timestamp,
                'line': line_num,
                'symbol': match.group(1),
                'direction': match.group(2),
                'lots': float(match.group(3)),
                'open_price': float(match.group(4)),
                'status': 'opened'
            }
            self.trades.append(trade)
            
            # Aggiorna stats giornaliere
            date_key = timestamp.strftime('%Y-%m-%d')
            self.daily_stats[date_key]['trades'] += 1
            return
            
        # Trade closed
        match = re.search(r'Trade closed: (\w+) (BUY|SELL) (\d+\.\d+) lots at (\d+\.\d+), P&L: ([-+]?\d+\.\d+)', line, re.IGNORECASE)
        if match:
            # Trova trade aperto corrispondente
            symbol = match.group(1)
            direction = match.group(2)
            lots = float(match.group(3))
            close_price = float(match.group(4))
            pnl = float(match.group(5))
            
            for trade in reversed(self.trades):
                if (trade['symbol'] == symbol and 
                    trade['direction'] == direction and 
                    trade['lots'] == lots and 
                    trade['status'] == 'opened'):
                    
                    trade['close_price'] = close_price
                    trade['close_timestamp'] = timestamp
                    trade['pnl'] = pnl
                    trade['status'] = 'closed'
                    trade['duration'] = (timestamp - trade['timestamp']).total_seconds() / 60  # minuti
                    break
            
            # Aggiorna stats giornaliere
            date_key = timestamp.strftime('%Y-%m-%d')
            self.daily_stats[date_key]['profit'] += pnl
            return
            
        # Quantum signal
        match = re.search(r'Quantum signal: (\w+) (BUY|SELL) - Entropy: (\d+\.\d+), Spin: ([-+]?\d+\.\d+)', line, re.IGNORECASE)
        if match:
            signal = {
                'timestamp': timestamp,
                'line': line_num,
                'symbol': match.group(1),
                'direction': match.group(2),
                'entropy': float(match.group(3)),
                'spin': float(match.group(4))
            }
            self.signals.append(signal)
            
            # Aggiorna stats giornaliere
            date_key = timestamp.strftime('%Y-%m-%d')
            self.daily_stats[date_key]['signals'] += 1
            return
            
        # Account info
        match = re.search(r'Account Balance: (\d+\.\d+), Equity: (\d+\.\d+), Margin: (\d+\.\d+)', line, re.IGNORECASE)
        if match:
            account = {
                'timestamp': timestamp,
                'balance': float(match.group(1)),
                'equity': float(match.group(2)),
                'margin': float(match.group(3))
            }
            self.account_history.append(account)
            return
            
        # Drawdown warning
        match = re.search(r'Drawdown warning: Current DD: (\d+\.\d+)%', line, re.IGNORECASE)
        if match:
            date_key = timestamp.strftime('%Y-%m-%d')
            self.daily_stats[date_key]['drawdown'] = max(
                self.daily_stats[date_key]['drawdown'], 
                float(match.group(1))
            )
            return

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

    def calculate_metrics(self) -> Dict:
        """Calcola tutte le metriche"""
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_drawdown': 0
            }
        
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] < 0]
        
        total_profit = sum(t['pnl'] for t in winning_trades)
        total_loss = sum(abs(t['pnl']) for t in losing_trades)
        
        metrics = {
            'total_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(closed_trades)) * 100,
            'total_pnl': total_profit - total_loss,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_factor': total_profit / total_loss if total_loss > 0 else float('inf'),
            'avg_win': total_profit / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_loss / len(losing_trades) if losing_trades else 0,
            'largest_win': max((t['pnl'] for t in winning_trades), default=0),
            'largest_loss': max((abs(t['pnl']) for t in losing_trades), default=0),
            'avg_trade_duration': sum(t['duration'] for t in closed_trades) / len(closed_trades),
            'max_drawdown': max((day['drawdown'] for day in self.daily_stats.values()), default=0)
        }
        
        # Calcola profit percentage se abbiamo dati account
        if self.account_history:
            initial_balance = self.account_history[0]['balance']
            metrics['profit_percentage'] = (metrics['total_pnl'] / initial_balance) * 100
        else:
            metrics['profit_percentage'] = 0
            
        return metrics

    def analyze_quantum_signals(self) -> Dict:
        """Analizza efficacia dei segnali quantum"""
        if not self.signals:
            return {}
            
        # Raggruppa segnali per simbolo
        by_symbol = defaultdict(list)
        for signal in self.signals:
            by_symbol[signal['symbol']].append(signal)
            
        analysis = {}
        
        for symbol, signals in by_symbol.items():
            buy_signals = [s for s in signals if s['direction'] == 'BUY']
            sell_signals = [s for s in signals if s['direction'] == 'SELL']
            
            analysis[symbol] = {
                'total_signals': len(signals),
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'buy_sell_ratio': len(buy_signals) / len(sell_signals) if sell_signals else float('inf'),
                'avg_entropy': sum(s['entropy'] for s in signals) / len(signals),
                'avg_spin': sum(s['spin'] for s in signals) / len(signals),
                'entropy_range': [min(s['entropy'] for s in signals), max(s['entropy'] for s in signals)],
                'spin_range': [min(s['spin'] for s in signals), max(s['spin'] for s in signals)]
            }
            
        return analysis

    def analyze_by_symbol(self) -> Dict:
        """Analizza performance per simbolo"""
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        
        by_symbol = defaultdict(list)
        for trade in closed_trades:
            by_symbol[trade['symbol']].append(trade)
            
        analysis = {}
        
        for symbol, trades in by_symbol.items():
            winning_trades = [t for t in trades if t['pnl'] > 0]
            losing_trades = [t for t in trades if t['pnl'] < 0]
            
            total_profit = sum(t['pnl'] for t in winning_trades)
            total_loss = sum(abs(t['pnl']) for t in losing_trades)
            
            analysis[symbol] = {
                'total_trades': len(trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': (len(winning_trades) / len(trades)) * 100,
                'total_pnl': total_profit - total_loss,
                'profit_factor': total_profit / total_loss if total_loss > 0 else float('inf'),
                'avg_duration': sum(t['duration'] for t in trades) / len(trades),
                'best_trade': max((t['pnl'] for t in trades), default=0),
                'worst_trade': min((t['pnl'] for t in trades), default=0)
            }
            
        return analysis

    def analyze_by_time(self) -> Dict:
        """Analizza performance per ora del giorno"""
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        
        by_hour = defaultdict(list)
        for trade in closed_trades:
            hour = trade['timestamp'].hour
            by_hour[hour].append(trade)
            
        analysis = {}
        
        for hour, trades in by_hour.items():
            winning_trades = [t for t in trades if t['pnl'] > 0]
            total_pnl = sum(t['pnl'] for t in trades)
            
            analysis[hour] = {
                'total_trades': len(trades),
                'winning_trades': len(winning_trades),
                'win_rate': (len(winning_trades) / len(trades)) * 100,
                'total_pnl': total_pnl,
                'avg_pnl': total_pnl / len(trades)
            }
            
        return analysis

    def check_the5ers_compliance(self, metrics: Dict) -> Dict:
        """Verifica compliance The5ers"""
        compliance = {}
        
        # Target check
        if metrics['profit_percentage'] >= self.step1_target:
            compliance['target_status'] = 'ACHIEVED'
            compliance['target_message'] = f"✅ Target raggiunto: {metrics['profit_percentage']:.2f}%"
        else:
            compliance['target_status'] = 'PENDING'
            remaining = self.step1_target - metrics['profit_percentage']
            compliance['target_message'] = f"🎯 Target: {metrics['profit_percentage']:.2f}% / {self.step1_target}% (Mancano: {remaining:.2f}%)"
        
        # Drawdown check
        max_dd = metrics['max_drawdown']
        if max_dd >= self.drawdown_hard:
            compliance['drawdown_status'] = 'VIOLATED'
            compliance['drawdown_message'] = f"🚨 Drawdown violato: {max_dd:.2f}% (Limite: {self.drawdown_hard}%)"
        elif max_dd >= self.drawdown_soft:
            compliance['drawdown_status'] = 'WARNING'
            compliance['drawdown_message'] = f"⚠️  Drawdown warning: {max_dd:.2f}% (Soft: {self.drawdown_soft}%)"
        else:
            compliance['drawdown_status'] = 'OK'
            compliance['drawdown_message'] = f"✅ Drawdown OK: {max_dd:.2f}%"
            
        return compliance

    def generate_report(self) -> str:
        """Genera report completo"""
        self.parse_log_file()
        
        metrics = self.calculate_metrics()
        quantum_analysis = self.analyze_quantum_signals()
        symbol_analysis = self.analyze_by_symbol()
        time_analysis = self.analyze_by_time()
        compliance = self.check_the5ers_compliance(metrics)
        
        report = []
        report.append("=" * 80)
        report.append("THE5ERS DETAILED ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Period: {self.get_analysis_period()}")
        report.append("")
        
        # THE5ERS COMPLIANCE
        report.append("🏆 THE5ERS COMPLIANCE")
        report.append("-" * 50)
        report.append(f"Target Status: {compliance['target_message']}")
        report.append(f"Drawdown Status: {compliance['drawdown_message']}")
        report.append("")
        
        # OVERALL PERFORMANCE
        report.append("📊 OVERALL PERFORMANCE")
        report.append("-" * 50)
        report.append(f"Total Trades: {metrics['total_trades']}")
        report.append(f"Win Rate: {metrics['win_rate']:.1f}%")
        report.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
        report.append(f"Total P&L: ${metrics['total_pnl']:.2f}")
        report.append(f"Profit Percentage: {metrics['profit_percentage']:.2f}%")
        report.append(f"Average Win: ${metrics['avg_win']:.2f}")
        report.append(f"Average Loss: ${metrics['avg_loss']:.2f}")
        report.append(f"Largest Win: ${metrics['largest_win']:.2f}")
        report.append(f"Largest Loss: ${metrics['largest_loss']:.2f}")
        report.append(f"Average Trade Duration: {metrics['avg_trade_duration']:.1f} minutes")
        report.append(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        report.append("")
        
        # PERFORMANCE BY SYMBOL
        report.append("📈 PERFORMANCE BY SYMBOL")
        report.append("-" * 50)
        for symbol, data in symbol_analysis.items():
            report.append(f"{symbol}:")
            report.append(f"  Trades: {data['total_trades']} | Win Rate: {data['win_rate']:.1f}%")
            report.append(f"  P&L: ${data['total_pnl']:.2f} | PF: {data['profit_factor']:.2f}")
            report.append(f"  Best: ${data['best_trade']:.2f} | Worst: ${data['worst_trade']:.2f}")
            report.append(f"  Avg Duration: {data['avg_duration']:.1f} min")
            report.append("")
        
        # QUANTUM SIGNALS ANALYSIS
        report.append("🔬 QUANTUM SIGNALS ANALYSIS")
        report.append("-" * 50)
        for symbol, data in quantum_analysis.items():
            report.append(f"{symbol}:")
            report.append(f"  Total Signals: {data['total_signals']}")
            report.append(f"  Buy/Sell: {data['buy_signals']}/{data['sell_signals']} (Ratio: {data['buy_sell_ratio']:.2f})")
            report.append(f"  Avg Entropy: {data['avg_entropy']:.3f} (Range: {data['entropy_range'][0]:.3f} - {data['entropy_range'][1]:.3f})")
            report.append(f"  Avg Spin: {data['avg_spin']:.3f} (Range: {data['spin_range'][0]:.3f} - {data['spin_range'][1]:.3f})")
            report.append("")
        
        # PERFORMANCE BY TIME
        report.append("🕐 PERFORMANCE BY HOUR")
        report.append("-" * 50)
        best_hours = sorted(time_analysis.items(), key=lambda x: x[1]['total_pnl'], reverse=True)[:5]
        report.append("Top 5 most profitable hours:")
        for hour, data in best_hours:
            report.append(f"  {hour:02d}:00 - Trades: {data['total_trades']}, P&L: ${data['total_pnl']:.2f}, Win Rate: {data['win_rate']:.1f}%")
        report.append("")
        
        # DAILY SUMMARY
        report.append("📅 DAILY SUMMARY")
        report.append("-" * 50)
        for date, data in sorted(self.daily_stats.items()):
            report.append(f"{date}: {data['trades']} trades, ${data['profit']:.2f} P&L, {data['signals']} signals, {data['drawdown']:.2f}% DD")
        report.append("")
        
        # RECOMMENDATIONS
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 50)
        recommendations = self.generate_recommendations(metrics, symbol_analysis, quantum_analysis, time_analysis)
        for rec in recommendations:
            report.append(f"  • {rec}")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)

    def get_analysis_period(self) -> str:
        """Ottieni periodo di analisi"""
        if not self.trades:
            return "No data"
            
        start_date = min(t['timestamp'] for t in self.trades)
        end_date = max(t['timestamp'] for t in self.trades)
        
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    def generate_recommendations(self, metrics: Dict, symbol_analysis: Dict, quantum_analysis: Dict, time_analysis: Dict) -> List[str]:
        """Genera raccomandazioni basate sull'analisi"""
        recommendations = []
        
        # Performance generale
        if metrics['win_rate'] < 50:
            recommendations.append("Consider adjusting quantum thresholds to improve win rate")
        
        if metrics['profit_factor'] < 1.5:
            recommendations.append("Profit factor is low - review risk management parameters")
        
        # Analisi per simbolo
        best_symbol = max(symbol_analysis.items(), key=lambda x: x[1]['total_pnl']) if symbol_analysis else None
        worst_symbol = min(symbol_analysis.items(), key=lambda x: x[1]['total_pnl']) if symbol_analysis else None
        
        if best_symbol:
            recommendations.append(f"Focus more on {best_symbol[0]} - best performing symbol")
        
        if worst_symbol and worst_symbol[1]['total_pnl'] < 0:
            recommendations.append(f"Consider reducing exposure to {worst_symbol[0]} - underperforming")
        
        # Analisi temporale
        if time_analysis:
            best_hour = max(time_analysis.items(), key=lambda x: x[1]['avg_pnl'])
            recommendations.append(f"Most profitable hour: {best_hour[0]:02d}:00 - consider increasing activity")
        
        # Quantum signals
        for symbol, data in quantum_analysis.items():
            if data['buy_sell_ratio'] > 2 or data['buy_sell_ratio'] < 0.5:
                recommendations.append(f"Review quantum parameters for {symbol} - signal bias detected")
        
        # Drawdown
        if metrics['max_drawdown'] > 1:
            recommendations.append("Consider tightening risk management - drawdown is significant")
        
        return recommendations

    def save_report(self, filename: str = None):
        """Salva report su file"""
        if filename is None:
            filename = f"the5ers_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report salvato: {filename}")
        except Exception as e:
            print(f"❌ Errore salvataggio report: {e}")

def main():
    """Funzione principale"""
    if len(sys.argv) < 3:
        print("Usage: python analyze_the5ers.py <config_file> <log_file>")
        print("Example: python analyze_the5ers.py config.json logs/trading.log")
        sys.exit(1)
    
    config_file = sys.argv[1]
    log_file = sys.argv[2]
    
    if not os.path.exists(config_file):
        print(f"❌ Config file non trovato: {config_file}")
        sys.exit(1)
        
    if not os.path.exists(log_file):
        print(f"❌ Log file non trovato: {log_file}")
        sys.exit(1)
    
    # Crea analyzer
    analyzer = The5ersAnalyzer(config_file, log_file)
    
    # Genera e salva report
    print("📊 Generating detailed analysis report...")
    analyzer.save_report()
    print("✅ Analysis completed!")

if __name__ == "__main__":
    main()
