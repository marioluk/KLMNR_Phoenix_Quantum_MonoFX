"""
Modulo per la gestione e il calcolo delle metriche di performance (Sharpe, Sortino, ecc.)
"""

class MetricsCalculator:
    def __init__(self, metrics_dict=None):
        self.metrics = metrics_dict or {}

    def ensure_all_metrics(self):
        # Imposta tutte le metriche usate nei template a 0.0 se non definite
        for key in [
            'sharpe_ratio', 'sortino_ratio', 'profit_factor', 'max_drawdown',
            'total_pnl', 'current_balance', 'current_equity', 'current_drawdown',
            'win_rate', 'profit_percentage', 'positions_open', 'daily_trades'
        ]:
            if key not in self.metrics or self.metrics[key] is None:
                self.metrics[key] = 0.0
            else:
                try:
                    self.metrics[key] = float(self.metrics[key])
                except Exception:
                    self.metrics[key] = 0.0
        return self.metrics

    # Qui puoi aggiungere metodi per calcolare Sharpe, Sortino, ecc.
