import numpy as np
from collections import defaultdict
import logging

class TradingMetrics:
    def __init__(self):
        self.metrics = {
            'total_trades': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'profit_factor': 0,
            'symbol_stats': defaultdict(dict)
        }
        self._profit_history = []
        self.logger = logging.getLogger("phoenix_quantum.metrics")

    """
    2. Aggiornamento Metriche
    """

    def update_trade(self, symbol: str, profit: float):
        """Aggiorna le metriche dopo ogni trade."""
        self.metrics['total_trades'] += 1
        self._profit_history.append(profit)
        
        if symbol not in self.metrics['symbol_stats']:
            self.metrics['symbol_stats'][symbol] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_profit': 0.0,
                'max_drawdown': 0.0
            }
            
        stats = self.metrics['symbol_stats'][symbol]
        stats['trades'] += 1
        stats['total_profit'] += profit
        
        if profit >= 0:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        self._calculate_metrics()

    def _calculate_metrics(self):
        """Ricalcola le metriche aggregate."""
        if not self._profit_history:
            return
        profits = np.array(self._profit_history)
        self.metrics['avg_profit'] = float(np.mean(profits))
        self.metrics['max_drawdown'] = float(self._calculate_drawdown(profits))
        self.metrics['sharpe_ratio'] = float(self._calculate_sharpe(profits))
        wins = sum(1 for p in profits if p > 0)
        self.metrics['win_rate'] = 100 * wins / len(profits)
        losses = sum(1 for p in profits if p < 0)
        gross_profit = sum(p for p in profits if p > 0)
        gross_loss = -sum(p for p in profits if p < 0)
        self.metrics['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else 0

    def _calculate_drawdown(self, profits: np.ndarray) -> float:
        """ Calcola il drawdown massimo dalla curva di equity."""
        equity_curve = np.cumsum(profits)
        peak = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - peak) / (peak + 1e-10)
        return np.min(drawdowns) * 100

    def _calculate_sharpe(self, profits: np.ndarray) -> float:
        """ Calcola lo Sharpe Ratio annualizzato."""
        # Esempio semplice: Sharpe annualizzato con risk-free rate 0
        if len(profits) < 2:
            return 0.0
        mean = np.mean(profits)
        std = np.std(profits)
        if std == 0:
            return 0.0
        sharpe = mean / std * np.sqrt(252)  # 252 giorni di trading
        return sharpe

    def get_metrics_summary(self):
        """Restituisce un riassunto delle metriche principali."""
        return {
            'total_trades': self.metrics['total_trades'],
            'win_rate': round(self.metrics['win_rate'], 2),
            'avg_profit': round(self.metrics['avg_profit'], 2),
            'max_drawdown': round(self.metrics['max_drawdown'], 2),
            'sharpe_ratio': round(self.metrics['sharpe_ratio'], 2),
            'profit_factor': round(self.metrics['profit_factor'], 2)
        }

    def get_symbol_stats(self, symbol: str) -> dict:
        """Restituisce le statistiche per un simbolo specifico"""
        if symbol not in self.metrics['symbol_stats']:
            return {}
        return self.metrics['symbol_stats'][symbol]

    def log_performance_report(self):
        """Stampa un report delle performance nei log"""
        summary = self.get_metrics_summary()
        self.logger.info(f"📊 PERFORMANCE REPORT:")
        self.logger.info(f"   Trades: {summary['total_trades']}")
        self.logger.info(f"   Win Rate: {summary['win_rate']}%")
        self.logger.info(f"   Avg Profit: ${summary['avg_profit']:.2f}")
        self.logger.info(f"   Max Drawdown: {summary['max_drawdown']}%")
        self.logger.info(f"   Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        self.logger.info(f"   Profit Factor: {summary['profit_factor']:.2f}")

