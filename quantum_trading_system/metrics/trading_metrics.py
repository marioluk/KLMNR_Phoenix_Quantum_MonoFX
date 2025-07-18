"""
TradingMetrics - Monitoraggio delle metriche di performance del sistema
"""

import numpy as np
import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger('QuantumTradingSystem')


class TradingMetrics:
    """
    Monitora le metriche di performance del sistema di trading
    """
    
    def __init__(self):
        """Inizializza il sistema di metriche"""
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
        
    def update_trade(self, symbol: str, profit: float) -> None:
        """
        Aggiorna le metriche dopo ogni trade
        
        Args:
            symbol: Simbolo del trade
            profit: Profitto/perdita del trade
        """
        self.metrics['total_trades'] += 1
        self._profit_history.append(profit)
        
        if symbol not in self.metrics['symbol_stats']:
            self.metrics['symbol_stats'][symbol] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_profit': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'avg_profit': 0.0
            }
            
        stats = self.metrics['symbol_stats'][symbol]
        stats['trades'] += 1
        stats['total_profit'] += profit
        
        if profit >= 0:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        self._calculate_metrics()

    def _calculate_metrics(self) -> None:
        """Ricalcola le metriche aggregate"""
        if not self._profit_history:
            return
            
        profits = np.array(self._profit_history)
        self.metrics['win_rate'] = np.mean(profits >= 0) * 100
        self.metrics['avg_profit'] = np.mean(profits)
        self.metrics['max_drawdown'] = self._calculate_drawdown(profits)
        self.metrics['sharpe_ratio'] = self._calculate_sharpe(profits)
        self.metrics['profit_factor'] = self._calculate_profit_factor(profits)
        
        # Aggiorna statistiche per simbolo
        for symbol, stats in self.metrics['symbol_stats'].items():
            if stats['trades'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['trades']) * 100
                stats['avg_profit'] = stats['total_profit'] / stats['trades']

    def _calculate_drawdown(self, profits: np.ndarray) -> float:
        """
        Calcola il drawdown massimo dalla curva di equity
        
        Args:
            profits: Array dei profitti
            
        Returns:
            Drawdown massimo in percentuale
        """
        if len(profits) == 0:
            return 0.0
            
        equity_curve = np.cumsum(profits)
        peak = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - peak) / (peak + 1e-10)
        return abs(np.min(drawdowns)) * 100

    def _calculate_sharpe(self, profits: np.ndarray) -> float:
        """
        Calcola il Sharpe Ratio
        
        Args:
            profits: Array dei profitti
            
        Returns:
            Sharpe Ratio
        """
        if len(profits) == 0 or np.std(profits) == 0:
            return 0.0
        return np.mean(profits) / np.std(profits)

    def _calculate_profit_factor(self, profits: np.ndarray) -> float:
        """
        Calcola il Profit Factor
        
        Args:
            profits: Array dei profitti
            
        Returns:
            Profit Factor
        """
        if len(profits) == 0:
            return 0.0
            
        gross_profit = np.sum(profits[profits > 0])
        gross_loss = abs(np.sum(profits[profits < 0]))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss

    def get_summary(self) -> Dict:
        """
        Restituisce un riassunto delle metriche
        
        Returns:
            Dizionario con le metriche principali
        """
        return {
            'total_trades': self.metrics['total_trades'],
            'win_rate': f"{self.metrics['win_rate']:.1f}%",
            'avg_profit': f"{self.metrics['avg_profit']:.2f}",
            'max_drawdown': f"{self.metrics['max_drawdown']:.2f}%",
            'sharpe_ratio': f"{self.metrics['sharpe_ratio']:.2f}",
            'profit_factor': f"{self.metrics['profit_factor']:.2f}",
            'total_profit': f"{sum(self._profit_history):.2f}" if self._profit_history else "0.00"
        }

    def get_symbol_stats(self, symbol: str) -> Dict:
        """
        Restituisce le statistiche per un simbolo specifico
        
        Args:
            symbol: Simbolo richiesto
            
        Returns:
            Dizionario con le statistiche del simbolo
        """
        if symbol not in self.metrics['symbol_stats']:
            return {}
        
        stats = self.metrics['symbol_stats'][symbol]
        return {
            'trades': stats['trades'],
            'wins': stats['wins'],
            'losses': stats['losses'],
            'win_rate': f"{stats['win_rate']:.1f}%",
            'total_profit': f"{stats['total_profit']:.2f}",
            'avg_profit': f"{stats['avg_profit']:.2f}"
        }

    def log_performance_summary(self) -> None:
        """Log delle performance principali"""
        summary = self.get_summary()
        
        logger.info("=== PERFORMANCE SUMMARY ===")
        logger.info(f"Total Trades: {summary['total_trades']}")
        logger.info(f"Win Rate: {summary['win_rate']}")
        logger.info(f"Total Profit: ${summary['total_profit']}")
        logger.info(f"Avg Profit: ${summary['avg_profit']}")
        logger.info(f"Max Drawdown: {summary['max_drawdown']}")
        logger.info(f"Sharpe Ratio: {summary['sharpe_ratio']}")
        logger.info(f"Profit Factor: {summary['profit_factor']}")
        
        # Statistiche per simbolo
        if self.metrics['symbol_stats']:
            logger.info("=== SYMBOL BREAKDOWN ===")
            for symbol, stats in self.metrics['symbol_stats'].items():
                if stats['trades'] > 0:
                    symbol_summary = self.get_symbol_stats(symbol)
                    logger.info(f"{symbol}: {symbol_summary['trades']} trades, "
                               f"WR: {symbol_summary['win_rate']}, "
                               f"P/L: ${symbol_summary['total_profit']}")

    def reset_metrics(self) -> None:
        """Reset di tutte le metriche"""
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
        logger.info("Metriche di trading resettate")

    def get_recent_performance(self, last_n_trades: int = 10) -> Dict:
        """
        Analizza le performance degli ultimi N trade
        
        Args:
            last_n_trades: Numero di trade recenti da analizzare
            
        Returns:
            Dizionario con le metriche degli ultimi trade
        """
        if len(self._profit_history) < last_n_trades:
            recent_profits = self._profit_history
        else:
            recent_profits = self._profit_history[-last_n_trades:]
        
        if not recent_profits:
            return {}
        
        profits = np.array(recent_profits)
        return {
            'trades_analyzed': len(recent_profits),
            'win_rate': f"{np.mean(profits >= 0) * 100:.1f}%",
            'avg_profit': f"{np.mean(profits):.2f}",
            'total_profit': f"{np.sum(profits):.2f}",
            'best_trade': f"{np.max(profits):.2f}",
            'worst_trade': f"{np.min(profits):.2f}"
        }
