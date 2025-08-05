"""
Modulo per la gestione e il calcolo delle metriche di performance (Sharpe, Sortino, ecc.)
"""

class MetricsCalculator:
    def __init__(self, metrics_dict=None):
        self.metrics = metrics_dict or {}

    def calculate_total_pnl(self, trade_history=None):
        # Forza sempre il capitale iniziale a 5000
        self.metrics['initial_balance'] = 5000
        """
        Calcola la somma dei profitti dei trade chiusi.
        Se trade_history è vuoto o None, calcola come differenza tra balance attuale e iniziale.
        Inoltre calcola la somma dei soli profitti e delle sole perdite.
        """
        print("DEBUG trade_history da MT5:", trade_history)
        # Filtro i movimenti non di trading (depositi, prelievi, trasferimenti, commissioni, ecc.)
        exclude_comments = [
            'INITIAL_DEPOSIT', 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'INTERNAL_TRANSFER', 'FEE', 'COMMISSION', 'ADJUSTMENT'
        ]
        if trade_history:
            trade_history = [
                t for t in trade_history
                if (
                    isinstance(t, dict)
                    and not any(t.get('comment', '').upper().startswith(ex) for ex in exclude_comments)
                    and t.get('symbol', '') != ''
                    and t.get('volume', 0) > 0
                )
            ]
        print("DEBUG trade_history filtrato:", trade_history)
        initial_balance = self.metrics.get('initial_balance', 5000)
        # Usa il saldo attuale da MT5, se disponibile, altrimenti somma profitti all'iniziale
        current_balance = self.metrics.get('balance', initial_balance)
        if not trade_history:
            # Se non ci sono trade chiusi, tutte le metriche sono zero
            self.metrics['total_pnl'] = 0.0
            self.metrics['total_profit'] = 0.0
            self.metrics['total_loss'] = 0.0
            self.metrics['profit_percentage'] = 0.0
            return 0.0
        total_pnl = 0.0
        total_profit = 0.0
        total_loss = 0.0
        for t in trade_history:
            # Supporta sia dict che oggetti Trade
            profit = t.get('profit', 0.0) if isinstance(t, dict) else getattr(t, 'pnl', 0.0)
            total_pnl += profit
            if profit > 0:
                total_profit += profit
            if profit < 0:
                total_loss += abs(profit)
        self.metrics['total_trades'] = len(trade_history)
        self.metrics['profit_factor'] = (total_profit / total_loss) if total_loss > 0 else 0.0
        self.metrics['total_pnl'] = total_pnl
        self.metrics['total_profit'] = total_profit
        self.metrics['total_loss'] = total_loss
        # Calcolo profit_percentage
        self.metrics['profit_percentage'] = ((current_balance - initial_balance) / initial_balance) * 100 if initial_balance else 0.0

        # Calcolo Drawdown Recovery Time (in minuti)
        # Serve una curva balance e timestamp
        balance_curve = []
        time_curve = []
        balance = initial_balance
        for t in trade_history:
            balance += t.get('profit', 0.0) if isinstance(t, dict) else getattr(t, 'pnl', 0.0)
            balance_curve.append(balance)
            time_curve.append(t.get('time', None))
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
        # Trova il primo recupero dopo il trough
        recovery_idx = None
        for i in range(trough_idx + 1, len(balance_curve)):
            if balance_curve[i] >= peak:
                recovery_idx = i
                break
        if recovery_idx is not None and time_curve[peak_idx] and time_curve[recovery_idx]:
            # Calcolo tempo in minuti tra peak e recovery
            from datetime import datetime
            t1 = time_curve[peak_idx]
            t2 = time_curve[recovery_idx]
            # Supporta sia timestamp che stringa
            if isinstance(t1, (int, float)) and isinstance(t2, (int, float)):
                minutes = (t2 - t1) / 60
            else:
                try:
                    dt1 = datetime.fromtimestamp(float(t1)) if isinstance(t1, (int, float)) else datetime.fromisoformat(str(t1))
                    dt2 = datetime.fromtimestamp(float(t2)) if isinstance(t2, (int, float)) else datetime.fromisoformat(str(t2))
                    minutes = (dt2 - dt1).total_seconds() / 60
                except Exception:
                    minutes = 0.0
            self.metrics['drawdown_recovery_time'] = round(minutes, 2)
        else:
            self.metrics['drawdown_recovery_time'] = 0.0
        return total_pnl

    def ensure_all_metrics(self):
        # Imposta tutte le metriche usate nei template a 0.0 se non definite
        for key in [
            'sharpe_ratio', 'sortino_ratio', 'profit_factor',
            'total_pnl', 'current_balance', 'current_equity', 'current_drawdown',
            'win_rate', 'profit_percentage', 'positions_open', 'positions_count', 'daily_trades'
        ]:
            if key not in self.metrics or self.metrics[key] is None:
                self.metrics[key] = 0.0
            else:
                try:
                    self.metrics[key] = float(self.metrics[key])
                except Exception:
                    self.metrics[key] = 0.0
        # drawdown_recovery_time: se è None, metti '-', altrimenti lascia il valore reale (numerico o stringa)
        if 'drawdown_recovery_time' not in self.metrics or self.metrics['drawdown_recovery_time'] is None:
            self.metrics['drawdown_recovery_time'] = '-'
        # Se è numerico, lascia invariato
        elif isinstance(self.metrics['drawdown_recovery_time'], (int, float)):
            pass
        # Se è stringa '-', lascia invariato
        elif isinstance(self.metrics['drawdown_recovery_time'], str) and self.metrics['drawdown_recovery_time'] == '-':
            pass
        # Altrimenti prova a convertire in float
        else:
            try:
                self.metrics['drawdown_recovery_time'] = float(self.metrics['drawdown_recovery_time'])
            except Exception:
                self.metrics['drawdown_recovery_time'] = '-'

        # max_drawdown: se è None, metti 0.0, altrimenti lascia il valore reale
        if 'max_drawdown' not in self.metrics or self.metrics['max_drawdown'] is None:
            self.metrics['max_drawdown'] = 0.0
        else:
            try:
                self.metrics['max_drawdown'] = float(self.metrics['max_drawdown'])
            except Exception:
                pass

        # volatility: se è None, metti 0.0, altrimenti lascia il valore reale
        if 'volatility' not in self.metrics or self.metrics['volatility'] is None:
            self.metrics['volatility'] = 0.0
        else:
            try:
                self.metrics['volatility'] = float(self.metrics['volatility'])
            except Exception:
                pass
        # Normalizza e assicura tutte le metriche richieste, SENZA sovrascrivere drawdown_recovery_time, max_drawdown e volatility se già presenti
        m = self.metrics
        m['total_pnl'] = m.get('total_pnl', 0.0)
        m['total_profit'] = m.get('total_profit', 0.0)
        m['total_loss'] = m.get('total_loss', 0.0)
        m['total_trades'] = m.get('total_trades', 0)
        m['profit_factor'] = m.get('profit_factor', 0.0)
        m['win_rate'] = m.get('win_rate', 0.0)
        m['positions_open'] = m.get('positions_open', 0)
        m['orders_count'] = m.get('orders_count', 0)
        # drawdown_recovery_time, max_drawdown e volatility NON vengono sovrascritti qui
        # ...altre metriche...
        return m

    # Qui puoi aggiungere metodi per calcolare Sharpe, Sortino, ecc.
