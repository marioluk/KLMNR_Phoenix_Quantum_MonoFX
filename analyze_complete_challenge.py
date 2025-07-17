#!/usr/bin/env python3
"""
THE5ERS COMPLETE CHALLENGE ANALYZER
Analizza tutti i dati della challenge Step 1 dal 7 luglio 2025
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import MetaTrader5 as mt5
from collections import defaultdict
import pandas as pd

class The5ersCompleteAnalyzer:
    def __init__(self, config_file: str):
        """
        Inizializza l'analyzer completo per la challenge Step 1
        
        Args:
            config_file: Path al file di configurazione JSON
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.mt5_config = self.config.get('metatrader5', {})
        
        # Parametri The5ers
        self.the5ers_params = self.config.get('THE5ERS_specific', {})
        self.step1_target = self.the5ers_params.get('step1_target', 8)
        self.drawdown_soft = self.the5ers_params.get('drawdown_protection', {}).get('soft_limit', 2)
        self.drawdown_hard = self.the5ers_params.get('drawdown_protection', {}).get('hard_limit', 5)
        
        # Periodo challenge Step 1 (dal 7 luglio 2025)
        self.challenge_start = datetime(2025, 7, 7, 0, 0, 0)
        self.challenge_end = datetime.now()
        
        # Dati per analisi
        self.trades = []
        self.daily_stats = defaultdict(lambda: {
            'trades': 0,
            'profit': 0.0,
            'win_rate': 0.0,
            'symbols': set()
        })
        
        print(f"🏆 THE5ERS COMPLETE CHALLENGE ANALYZER")
        print(f"📄 Config: {config_file}")
        print(f"📅 Challenge Period: {self.challenge_start.strftime('%Y-%m-%d')} to {self.challenge_end.strftime('%Y-%m-%d')}")
        print(f"⏰ Days Active: {(self.challenge_end - self.challenge_start).days}")
        print("-" * 70)

    def load_config(self) -> Dict:
        """Carica configurazione JSON"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Errore caricamento config: {e}")
            return {}

    def connect_mt5(self) -> bool:
        """Connette a MetaTrader5"""
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
            
            print(f"✅ Connesso a MT5 - Account: {login}")
            return True
            
        except Exception as e:
            print(f"❌ Errore connessione MT5: {e}")
            return False

    def get_challenge_history(self) -> List[Dict]:
        """Ottiene tutta la storia della challenge da MT5"""
        try:
            print("📊 Recuperando storia completa della challenge...")
            
            # Ottieni tutti i deals nel periodo
            deals = mt5.history_deals_get(self.challenge_start, self.challenge_end)
            if deals is None:
                print("❌ Nessun deal trovato")
                return []
            
            trades = []
            for deal in deals:
                if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                    trade = {
                        'ticket': deal.ticket,
                        'symbol': deal.symbol,
                        'type': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL',
                        'volume': deal.volume,
                        'price': deal.price,
                        'profit': deal.profit,
                        'swap': deal.swap,
                        'commission': deal.commission,
                        'time': datetime.fromtimestamp(deal.time),
                        'magic': deal.magic,
                        'comment': deal.comment
                    }
                    trades.append(trade)
            
            # Ordina per tempo
            trades.sort(key=lambda x: x['time'])
            
            print(f"✅ Trovati {len(trades)} trades nel periodo challenge")
            return trades
            
        except Exception as e:
            print(f"❌ Errore recupero storia: {e}")
            return []

    def get_account_history(self) -> List[Dict]:
        """Ottiene storia balance dell'account"""
        try:
            # Ottieni account info attuale
            account_info = mt5.account_info()
            if account_info is None:
                return []
            
            # Per semplicità, usiamo i dati attuali
            # In un'implementazione completa, potresti voler salvare snapshots giornalieri
            return [{
                'date': datetime.now(),
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'profit': account_info.profit
            }]
            
        except Exception as e:
            print(f"❌ Errore getting account history: {e}")
            return []

    def analyze_trades(self) -> Dict:
        """Analizza tutti i trades della challenge"""
        if not self.trades:
            return {}
            
        print("📈 Analizzando performance trades...")
        
        # Separa winning e losing trades
        winning_trades = [t for t in self.trades if t['profit'] > 0]
        losing_trades = [t for t in self.trades if t['profit'] <= 0]
        
        # Calcola metriche base
        total_profit = sum(t['profit'] for t in winning_trades)
        total_loss = sum(abs(t['profit']) for t in losing_trades)
        net_profit = total_profit - total_loss
        
        # Calcola profit factor
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Win rate
        win_rate = (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0
        
        # Calcola drawdown e profit percentage
        account_history = self.get_account_history()
        current_balance = account_history[0]['balance'] if account_history else 100000  # Default
        profit_percentage = (net_profit / current_balance) * 100
        
        # Calcola max drawdown approssimativo
        running_profit = 0
        max_profit = 0
        max_drawdown = 0
        
        for trade in self.trades:
            running_profit += trade['profit']
            max_profit = max(max_profit, running_profit)
            current_drawdown = max_profit - running_profit
            max_drawdown = max(max_drawdown, current_drawdown)
        
        max_drawdown_percent = (max_drawdown / current_balance) * 100
        
        # Analisi per simbolo
        symbol_stats = defaultdict(lambda: {
            'trades': 0,
            'profit': 0.0,
            'winning_trades': 0,
            'best_trade': 0.0,
            'worst_trade': 0.0
        })
        
        for trade in self.trades:
            symbol = trade['symbol']
            symbol_stats[symbol]['trades'] += 1
            symbol_stats[symbol]['profit'] += trade['profit']
            
            if trade['profit'] > 0:
                symbol_stats[symbol]['winning_trades'] += 1
                symbol_stats[symbol]['best_trade'] = max(symbol_stats[symbol]['best_trade'], trade['profit'])
            else:
                symbol_stats[symbol]['worst_trade'] = min(symbol_stats[symbol]['worst_trade'], trade['profit'])
        
        # Calcola win rate per simbolo
        for symbol, stats in symbol_stats.items():
            if stats['trades'] > 0:
                stats['win_rate'] = (stats['winning_trades'] / stats['trades']) * 100
        
        # Analisi temporale
        hourly_stats = defaultdict(lambda: {'trades': 0, 'profit': 0.0})
        daily_stats = defaultdict(lambda: {'trades': 0, 'profit': 0.0})
        
        for trade in self.trades:
            hour = trade['time'].hour
            date = trade['time'].date()
            
            hourly_stats[hour]['trades'] += 1
            hourly_stats[hour]['profit'] += trade['profit']
            
            daily_stats[date]['trades'] += 1
            daily_stats[date]['profit'] += trade['profit']
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_profit': net_profit,
            'profit_factor': profit_factor,
            'profit_percentage': profit_percentage,
            'max_drawdown_percent': max_drawdown_percent,
            'avg_win': total_profit / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_loss / len(losing_trades) if losing_trades else 0,
            'largest_win': max((t['profit'] for t in winning_trades), default=0),
            'largest_loss': min((t['profit'] for t in losing_trades), default=0),
            'current_balance': current_balance,
            'symbol_stats': dict(symbol_stats),
            'hourly_stats': dict(hourly_stats),
            'daily_stats': dict(daily_stats)
        }

    def check_the5ers_compliance(self, metrics: Dict) -> Dict:
        """Verifica compliance The5ers"""
        compliance = {}
        
        # Target check
        profit_pct = metrics.get('profit_percentage', 0)
        if profit_pct >= self.step1_target:
            compliance['target_status'] = 'ACHIEVED'
            compliance['target_message'] = f"🎉 TARGET STEP 1 ACHIEVED: {profit_pct:.2f}%"
        else:
            remaining = self.step1_target - profit_pct
            compliance['target_status'] = 'PENDING'
            compliance['target_message'] = f"🎯 Target Progress: {profit_pct:.2f}% / {self.step1_target}% (Remaining: {remaining:.2f}%)"
        
        # Drawdown check
        max_dd = metrics.get('max_drawdown_percent', 0)
        if max_dd >= self.drawdown_hard:
            compliance['drawdown_status'] = 'VIOLATED'
            compliance['drawdown_message'] = f"🚨 DRAWDOWN LIMIT VIOLATED: {max_dd:.2f}% (Limit: {self.drawdown_hard}%)"
        elif max_dd >= self.drawdown_soft:
            compliance['drawdown_status'] = 'WARNING'
            compliance['drawdown_message'] = f"⚠️ DRAWDOWN WARNING: {max_dd:.2f}% (Soft: {self.drawdown_soft}%)"
        else:
            compliance['drawdown_status'] = 'OK'
            compliance['drawdown_message'] = f"✅ Drawdown OK: {max_dd:.2f}%"
        
        # Trading activity check
        total_trades = metrics.get('total_trades', 0)
        days_active = (self.challenge_end - self.challenge_start).days
        avg_trades_per_day = total_trades / days_active if days_active > 0 else 0
        
        compliance['activity_message'] = f"📊 Trading Activity: {total_trades} trades in {days_active} days (Avg: {avg_trades_per_day:.1f}/day)"
        
        return compliance

    def generate_complete_report(self) -> str:
        """Genera report completo della challenge"""
        
        if not self.connect_mt5():
            return "❌ Impossibile connettersi a MT5"
        
        try:
            # Ottieni dati completi
            self.trades = self.get_challenge_history()
            
            if not self.trades:
                return "❌ Nessun trade trovato nel periodo della challenge"
            
            # Analizza i dati
            metrics = self.analyze_trades()
            compliance = self.check_the5ers_compliance(metrics)
            
            # Genera report
            report = []
            report.append("=" * 80)
            report.append("🏆 THE5ERS STEP 1 CHALLENGE - COMPLETE ANALYSIS")
            report.append("=" * 80)
            report.append(f"📅 Challenge Period: {self.challenge_start.strftime('%Y-%m-%d')} to {self.challenge_end.strftime('%Y-%m-%d')}")
            report.append(f"⏰ Days Active: {(self.challenge_end - self.challenge_start).days}")
            report.append(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # THE5ERS COMPLIANCE STATUS
            report.append("🎯 THE5ERS COMPLIANCE STATUS")
            report.append("-" * 60)
            report.append(f"Target Status: {compliance['target_message']}")
            report.append(f"Drawdown Status: {compliance['drawdown_message']}")
            report.append(f"Activity Status: {compliance['activity_message']}")
            report.append("")
            
            # OVERALL PERFORMANCE
            report.append("📊 OVERALL PERFORMANCE SUMMARY")
            report.append("-" * 60)
            report.append(f"Total Trades: {metrics['total_trades']}")
            report.append(f"Win Rate: {metrics['win_rate']:.1f}% ({metrics['winning_trades']} wins / {metrics['losing_trades']} losses)")
            report.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
            report.append(f"Net P&L: ${metrics['net_profit']:.2f}")
            report.append(f"Profit Percentage: {metrics['profit_percentage']:.2f}%")
            report.append(f"Current Balance: ${metrics['current_balance']:.2f}")
            report.append(f"Max Drawdown: {metrics['max_drawdown_percent']:.2f}%")
            report.append("")
            
            # DETAILED PERFORMANCE
            report.append("💰 DETAILED PERFORMANCE BREAKDOWN")
            report.append("-" * 60)
            report.append(f"Gross Profit: ${metrics['total_profit']:.2f}")
            report.append(f"Gross Loss: ${metrics['total_loss']:.2f}")
            report.append(f"Average Win: ${metrics['avg_win']:.2f}")
            report.append(f"Average Loss: ${metrics['avg_loss']:.2f}")
            report.append(f"Largest Win: ${metrics['largest_win']:.2f}")
            report.append(f"Largest Loss: ${metrics['largest_loss']:.2f}")
            report.append("")
            
            # PERFORMANCE BY SYMBOL
            report.append("📈 PERFORMANCE BY SYMBOL")
            report.append("-" * 60)
            for symbol, stats in metrics['symbol_stats'].items():
                report.append(f"{symbol}:")
                report.append(f"  Trades: {stats['trades']} | Win Rate: {stats['win_rate']:.1f}%")
                report.append(f"  Net P&L: ${stats['profit']:.2f}")
                report.append(f"  Best Trade: ${stats['best_trade']:.2f}")
                report.append(f"  Worst Trade: ${stats['worst_trade']:.2f}")
                report.append("")
            
            # BEST PERFORMING HOURS
            report.append("🕐 BEST PERFORMING HOURS")
            report.append("-" * 60)
            sorted_hours = sorted(metrics['hourly_stats'].items(), key=lambda x: x[1]['profit'], reverse=True)
            for hour, stats in sorted_hours[:8]:  # Top 8 hours
                report.append(f"{hour:02d}:00 - P&L: ${stats['profit']:.2f} | Trades: {stats['trades']}")
            report.append("")
            
            # DAILY PERFORMANCE SUMMARY
            report.append("📅 DAILY PERFORMANCE SUMMARY")
            report.append("-" * 60)
            sorted_days = sorted(metrics['daily_stats'].items(), key=lambda x: x[0])
            for date, stats in sorted_days[-10:]:  # Last 10 days
                report.append(f"{date.strftime('%Y-%m-%d')}: ${stats['profit']:.2f} | {stats['trades']} trades")
            report.append("")
            
            # CHALLENGE PROGRESS
            report.append("🎯 CHALLENGE PROGRESS")
            report.append("-" * 60)
            progress_percent = (metrics['profit_percentage'] / self.step1_target) * 100
            report.append(f"Progress: {progress_percent:.1f}% of target completed")
            
            if metrics['profit_percentage'] >= self.step1_target:
                report.append("🎉 CONGRATULATIONS! Step 1 target achieved!")
                report.append("✅ Ready to proceed to Step 2!")
            else:
                remaining = self.step1_target - metrics['profit_percentage']
                remaining_money = (remaining / 100) * metrics['current_balance']
                report.append(f"💰 Amount needed: ${remaining_money:.2f} ({remaining:.2f}%)")
            
            report.append("")
            
            # RECOMMENDATIONS
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 60)
            
            # Analizza pattern e genera raccomandazioni
            recommendations = []
            
            if metrics['win_rate'] < 50:
                recommendations.append("🔧 Consider adjusting quantum parameters to improve win rate")
            
            if metrics['profit_factor'] < 1.5:
                recommendations.append("⚠️ Profit factor is low - review risk management")
            
            # Analizza simboli
            best_symbol = max(metrics['symbol_stats'].items(), key=lambda x: x[1]['profit']) if metrics['symbol_stats'] else None
            worst_symbol = min(metrics['symbol_stats'].items(), key=lambda x: x[1]['profit']) if metrics['symbol_stats'] else None
            
            if best_symbol:
                recommendations.append(f"📈 Focus more on {best_symbol[0]} - best performer (${best_symbol[1]['profit']:.2f})")
            
            if worst_symbol and worst_symbol[1]['profit'] < 0:
                recommendations.append(f"📉 Consider reducing exposure to {worst_symbol[0]} - underperforming")
            
            # Analizza orari
            best_hour = max(metrics['hourly_stats'].items(), key=lambda x: x[1]['profit']) if metrics['hourly_stats'] else None
            if best_hour:
                recommendations.append(f"🕐 Most profitable hour: {best_hour[0]:02d}:00 - consider increasing activity")
            
            if metrics['max_drawdown_percent'] > 1:
                recommendations.append("🛡️ Consider tightening risk management - drawdown is significant")
            
            if not recommendations:
                recommendations.append("✅ Overall performance looks good - keep following the strategy")
            
            for rec in recommendations:
                report.append(f"  • {rec}")
            
            report.append("")
            report.append("=" * 80)
            
            return "\n".join(report)
            
        except Exception as e:
            return f"❌ Errore generazione report: {e}"
        finally:
            mt5.shutdown()

    def save_report(self, filename: str = None):
        """Salva report completo su file"""
        if filename is None:
            filename = f"the5ers_complete_challenge_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_complete_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report completo salvato: {filename}")
        except Exception as e:
            print(f"❌ Errore salvataggio report: {e}")
            
        # Stampa anche a schermo
        print("\n" + report)

def main():
    """Funzione principale"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_complete_challenge.py <config_file>")
        print("Example: python analyze_complete_challenge.py PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    if not os.path.exists(config_file):
        print(f"❌ Config file non trovato: {config_file}")
        sys.exit(1)
    
    # Crea analyzer
    analyzer = The5ersCompleteAnalyzer(config_file)
    
    # Genera e salva report completo
    print("🏆 Generando analisi completa della challenge Step 1...")
    analyzer.save_report()
    print("✅ Analisi completa terminata!")

if __name__ == "__main__":
    main()
