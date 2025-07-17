# ====================================================================================
# QUANTUM BACKTEST ENGINE - THE5ERS HIGH STAKES CHALLENGE OPTIMIZATION
# Sistema di backtest per ottimizzazione parametri algoritmo quantum
# ====================================================================================

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import sys
import importlib.util
import os

# Carica il file principale usando importlib (file con trattini)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_file_path = os.path.join(parent_dir, 'PRO-THE5ERS-QM-PHOENIX-GITCOP.py')
config_file_path = os.path.join(parent_dir, 'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')

# Carica la configurazione JSON aggiornata dal file principale
def load_the5ers_config():
    """Carica la configurazione aggiornata dal file JSON principale"""
    try:
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Configurazione caricata da: {config_file_path}")
        print(f"🔬 Quantum buffer_size: {config['quantum_params']['buffer_size']}")
        print(f"💰 Risk percent: {config['risk_parameters']['risk_percent']*100:.3f}%")
        
        return config
    except Exception as e:
        logging.error(f"❌ Errore caricamento config: {e}")
        return {}
        return {}

# Funzione per utilizzare la configurazione reale per il backtest
def get_real_config_for_backtest():
    """Ottiene configurazione reale dal file JSON per il backtest"""
    config = load_the5ers_config()
    
    # Estrai parametri rilevanti per il backtest
    backtest_config = {
        'quantum_params': config.get('quantum_params', {}),
        'risk_parameters': config.get('risk_parameters', {}),
        'symbols': config.get('symbols', {}),
        'THE5ERS_specific': config.get('THE5ERS_specific', {}),
        'initial_balance': config.get('initial_balance', 100000)
    }
    
    print(f"🎯 Backtest config estratto per {len(backtest_config['symbols'])} simboli")
    return backtest_config

spec = importlib.util.spec_from_file_location("quantum_module", main_file_path)
quantum_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quantum_module)

# Importa le classi necessarie
QuantumEngine = quantum_module.QuantumEngine
QuantumRiskManager = quantum_module.QuantumRiskManager
ConfigManager = quantum_module.ConfigManager

# ====================================================================================
# CONFIGURAZIONE BACKTEST
# ====================================================================================

@dataclass
class BacktestConfig:
    """Configurazione del backtest"""
    start_date: str
    end_date: str
    initial_balance: float
    symbols: List[str]
    timeframe: str = "M1"  # Timeframe dei dati
    commission: float = 0.0  # Commissioni per trade
    spread: float = 2.0  # Spread medio in pips
    
@dataclass
class The5ersRules:
    """Regole specifiche The5ers High Stakes Challenge"""
    step1_target: float = 8.0  # %
    step2_target: float = 5.0  # %
    scaling_target: float = 10.0  # %
    max_daily_loss: float = 5.0  # %
    max_total_loss: float = 10.0  # %
    min_profitable_days: int = 3
    max_trading_period_days: int = 999  # Unlimited
    
@dataclass
class TradeResult:
    """Risultato di un singolo trade"""
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    volume: float
    profit: float
    profit_pct: float
    trade_type: str  # BUY/SELL
    exit_reason: str  # TP/SL/TIMEOUT/MANUAL
    
# ====================================================================================
# HISTORICAL DATA HANDLER
# ====================================================================================

class HistoricalDataHandler:
    """Gestisce i dati storici per il backtest"""
    
    def __init__(self, data_path: str = "data/"):
        self.data_path = Path(data_path)
        self.data_cache = {}
        self.logger = logging.getLogger(__name__)
        
    def load_historical_data(self, symbol: str, start_date: str, end_date: str, 
                           timeframe: str = "M1") -> pd.DataFrame:
        """
        Carica dati storici per un simbolo
        
        Args:
            symbol: Simbolo da caricare (es. EURUSD)
            start_date: Data inizio formato YYYY-MM-DD
            end_date: Data fine formato YYYY-MM-DD
            timeframe: Timeframe dei dati
            
        Returns:
            DataFrame con colonne: timestamp, open, high, low, close, volume
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{timeframe}"
        
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
            
        # Percorso file dati
        data_file = self.data_path / f"{symbol}_{timeframe}_{start_date}_{end_date}.csv"
        
        if data_file.exists():
            df = pd.read_csv(data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            self.data_cache[cache_key] = df
            return df
        else:
            # Se non esiste, genera dati sintetici per test
            self.logger.warning(f"File dati non trovato: {data_file}. Generando dati sintetici.")
            return self._generate_synthetic_data(symbol, start_date, end_date, timeframe)
            
    def _generate_synthetic_data(self, symbol: str, start_date: str, end_date: str, 
                               timeframe: str) -> pd.DataFrame:
        """Genera dati sintetici per test (da sostituire con dati reali)"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Frequenza basata sul timeframe
        freq_map = {"M1": "1min", "M5": "5min", "M15": "15min", "H1": "1H", "D1": "1D"}
        freq = freq_map.get(timeframe, "1min")
        
        # Genera timestamp
        timestamps = pd.date_range(start=start, end=end, freq=freq)
        
        # Prezzo base per simbolo
        base_prices = {
            "EURUSD": 1.1000,
            "GBPUSD": 1.3000,
            "USDJPY": 110.00,
            "XAUUSD": 1800.00,
            "NAS100": 14000.00
        }
        
        base_price = base_prices.get(symbol, 1.0000)
        
        # Genera dati con random walk
        np.random.seed(42)  # Per riproducibilità
        n_points = len(timestamps)
        
        # Volatilità per simbolo
        volatilities = {
            "EURUSD": 0.0001,
            "GBPUSD": 0.0002,
            "USDJPY": 0.01,
            "XAUUSD": 0.5,
            "NAS100": 10.0
        }
        
        volatility = volatilities.get(symbol, 0.0001)
        
        # Genera prezzi con random walk
        returns = np.random.normal(0, volatility, n_points)
        prices = base_price + np.cumsum(returns)
        
        # Genera OHLC
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': prices * (1 + np.random.uniform(0, 0.001, n_points)),
            'low': prices * (1 - np.random.uniform(0, 0.001, n_points)),
            'close': prices * (1 + np.random.uniform(-0.0005, 0.0005, n_points)),
            'volume': np.random.randint(100, 1000, n_points)
        })
        
        df.set_index('timestamp', inplace=True)
        return df
        
    def get_tick_data(self, symbol: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Converte dati OHLC in tick data per il quantum engine
        
        Args:
            symbol: Simbolo
            start_time: Timestamp inizio
            end_time: Timestamp fine
            
        Returns:
            Lista di tick nel formato richiesto dal quantum engine
        """
        # Carica dati base
        start_date = start_time.strftime("%Y-%m-%d")
        end_date = end_time.strftime("%Y-%m-%d")
        
        df = self.load_historical_data(symbol, start_date, end_date)
        
        # Filtra per periodo richiesto
        mask = (df.index >= start_time) & (df.index <= end_time)
        df_filtered = df.loc[mask]
        
        # Converti in tick (usa close price)
        ticks = []
        for timestamp, row in df_filtered.iterrows():
            ticks.append({
                'symbol': symbol,
                'price': row['close'],
                'timestamp': timestamp,
                'bid': row['close'] - 0.00001,  # Spread simulato
                'ask': row['close'] + 0.00001
            })
            
        return ticks

# ====================================================================================
# BACKTEST ENGINE PRINCIPALE
# ====================================================================================

class QuantumBacktestEngine:
    """Engine principale per il backtest dell'algoritmo quantum"""
    
    def __init__(self, config: Dict, backtest_config: BacktestConfig, 
                 the5ers_rules: The5ersRules):
        self.config = config
        self.backtest_config = backtest_config
        self.the5ers_rules = the5ers_rules
        self.data_handler = HistoricalDataHandler()
        
        # Inizializza componenti quantum
        self.config_manager = ConfigManager(config)
        self.quantum_engine = QuantumEngine(self.config_manager)
        self.risk_manager = QuantumRiskManager(self.config_manager)
        
        # Stato del backtest
        self.current_balance = backtest_config.initial_balance
        self.equity_curve = []
        self.trades = []
        self.daily_results = {}
        self.current_positions = {}
        
        # Statistiche
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        
        self.logger = logging.getLogger(__name__)
        
    def run_backtest(self) -> Dict:
        """
        Esegue il backtest completo
        
        Returns:
            Dizionario con risultati del backtest
        """
        self.logger.info("Avvio backtest...")
        self.logger.info(f"Periodo: {self.backtest_config.start_date} - {self.backtest_config.end_date}")
        self.logger.info(f"Simboli: {self.backtest_config.symbols}")
        self.logger.info(f"Saldo iniziale: ${self.backtest_config.initial_balance:,.2f}")
        
        # Converti date
        start_date = pd.to_datetime(self.backtest_config.start_date)
        end_date = pd.to_datetime(self.backtest_config.end_date)
        
        # Itera per ogni giorno
        current_date = start_date
        while current_date <= end_date:
            self._process_day(current_date)
            current_date += timedelta(days=1)
            
        # Calcola risultati finali
        results = self._calculate_final_results()
        
        self.logger.info("Backtest completato!")
        self.logger.info(f"Saldo finale: ${self.current_balance:,.2f}")
        self.logger.info(f"Profit totale: {results['total_return_pct']:.2f}%")
        self.logger.info(f"Trades totali: {self.total_trades}")
        self.logger.info(f"Win rate: {results['win_rate']:.2f}%")
        
        return results
        
    def _process_day(self, date: datetime):
        """Processa un singolo giorno di trading"""
        day_start_balance = self.current_balance
        
        # Processa ogni simbolo
        for symbol in self.backtest_config.symbols:
            self._process_symbol_day(symbol, date)
            
        # Calcola risultati giornalieri
        day_profit = self.current_balance - day_start_balance
        day_profit_pct = (day_profit / day_start_balance) * 100
        
        self.daily_results[date.strftime("%Y-%m-%d")] = {
            'starting_balance': day_start_balance,
            'ending_balance': self.current_balance,
            'profit': day_profit,
            'profit_pct': day_profit_pct,
            'trades': len([t for t in self.trades if t.entry_time.date() == date.date()])
        }
        
        # Aggiorna equity curve
        self.equity_curve.append({
            'date': date,
            'balance': self.current_balance,
            'drawdown': self.current_drawdown
        })
        
        # Verifica regole The5ers
        self._check_the5ers_rules(date)
        
    def _process_symbol_day(self, symbol: str, date: datetime):
        """Processa un simbolo per un giorno"""
        # Ottieni tick data per il giorno
        day_start = date.replace(hour=0, minute=0, second=0)
        day_end = date.replace(hour=23, minute=59, second=59)
        
        ticks = self.data_handler.get_tick_data(symbol, day_start, day_end)
        
        # Processa ogni tick
        for tick in ticks:
            # Aggiorna quantum engine
            self.quantum_engine.process_tick(symbol, tick['price'])
            
            # Verifica segnali
            signal, price = self.quantum_engine.get_signal(symbol)
            
            if signal in ['BUY', 'SELL'] and symbol not in self.current_positions:
                self._open_position(symbol, signal, price, tick['timestamp'])
                
            # Gestisci posizioni aperte
            if symbol in self.current_positions:
                self._manage_position(symbol, tick)
                
    def _open_position(self, symbol: str, signal: str, price: float, timestamp: datetime):
        """Apre una nuova posizione"""
        if not self.quantum_engine.can_trade(symbol):
            return
            
        # Calcola dimensione posizione
        position_size = self.risk_manager.calculate_position_size(
            symbol, self.current_balance, signal
        )
        
        if position_size <= 0:
            return
            
        # Calcola SL e TP
        sl_price, tp_price = self.risk_manager.calculate_sl_tp(symbol, price, signal)
        
        # Crea posizione
        position = {
            'symbol': symbol,
            'type': signal,
            'entry_price': price,
            'entry_time': timestamp,
            'volume': position_size,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'current_price': price
        }
        
        self.current_positions[symbol] = position
        self.logger.debug(f"Posizione aperta: {symbol} {signal} @ {price:.5f}")
        
    def _manage_position(self, symbol: str, tick: Dict):
        """Gestisce una posizione aperta"""
        position = self.current_positions[symbol]
        current_price = tick['price']
        position['current_price'] = current_price
        
        # Verifica condizioni di chiusura
        exit_reason = None
        
        if position['type'] == 'BUY':
            if current_price <= position['sl_price']:
                exit_reason = 'SL'
            elif current_price >= position['tp_price']:
                exit_reason = 'TP'
        else:  # SELL
            if current_price >= position['sl_price']:
                exit_reason = 'SL'
            elif current_price <= position['tp_price']:
                exit_reason = 'TP'
                
        # Verifica timeout (max 6 ore)
        if (tick['timestamp'] - position['entry_time']).total_seconds() > 6 * 3600:
            exit_reason = 'TIMEOUT'
            
        # Chiudi posizione se necessario
        if exit_reason:
            self._close_position(symbol, current_price, tick['timestamp'], exit_reason)
            
    def _close_position(self, symbol: str, exit_price: float, timestamp: datetime, reason: str):
        """Chiude una posizione"""
        position = self.current_positions[symbol]
        
        # Calcola profit
        if position['type'] == 'BUY':
            profit = (exit_price - position['entry_price']) * position['volume']
        else:
            profit = (position['entry_price'] - exit_price) * position['volume']
            
        # Sottrai commissioni e spread
        profit -= self.backtest_config.commission
        profit -= self.backtest_config.spread * position['volume'] * 0.0001  # Spread cost
        
        # Aggiorna saldo
        self.current_balance += profit
        profit_pct = (profit / self.backtest_config.initial_balance) * 100
        
        # Crea trade result
        trade = TradeResult(
            symbol=symbol,
            entry_time=position['entry_time'],
            exit_time=timestamp,
            entry_price=position['entry_price'],
            exit_price=exit_price,
            volume=position['volume'],
            profit=profit,
            profit_pct=profit_pct,
            trade_type=position['type'],
            exit_reason=reason
        )
        
        self.trades.append(trade)
        
        # Aggiorna statistiche
        self.total_trades += 1
        if profit > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
            
        # Calcola drawdown
        peak_balance = max([eq['balance'] for eq in self.equity_curve] + [self.current_balance])
        self.current_drawdown = ((peak_balance - self.current_balance) / peak_balance) * 100
        self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
        
        # Rimuovi posizione
        del self.current_positions[symbol]
        
        # Registra cooldown
        self.quantum_engine.record_trade_close(symbol)
        
        self.logger.debug(f"Posizione chiusa: {symbol} {reason} P&L: ${profit:.2f}")
        
    def _check_the5ers_rules(self, date: datetime):
        """Verifica conformità alle regole The5ers"""
        # Verifica daily loss
        today_key = date.strftime("%Y-%m-%d")
        if today_key in self.daily_results:
            daily_loss_pct = abs(min(0, self.daily_results[today_key]['profit_pct']))
            if daily_loss_pct > self.the5ers_rules.max_daily_loss:
                self.logger.warning(f"Violazione daily loss: {daily_loss_pct:.2f}%")
                
        # Verifica total loss
        total_loss_pct = ((self.backtest_config.initial_balance - self.current_balance) / 
                         self.backtest_config.initial_balance) * 100
        if total_loss_pct > self.the5ers_rules.max_total_loss:
            self.logger.warning(f"Violazione total loss: {total_loss_pct:.2f}%")
            
    def _calculate_final_results(self) -> Dict:
        """Calcola i risultati finali del backtest"""
        total_return = self.current_balance - self.backtest_config.initial_balance
        total_return_pct = (total_return / self.backtest_config.initial_balance) * 100
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Calcola profitable days
        profitable_days = len([d for d in self.daily_results.values() if d['profit'] > 0])
        
        # Calcola Sharpe ratio (semplificato)
        daily_returns = [d['profit_pct'] for d in self.daily_results.values()]
        sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) if np.std(daily_returns) > 0 else 0
        
        # Verifica conformità The5ers
        the5ers_compliance = {
            'step1_achieved': total_return_pct >= self.the5ers_rules.step1_target,
            'step2_achieved': total_return_pct >= self.the5ers_rules.step2_target,
            'scaling_achieved': total_return_pct >= self.the5ers_rules.scaling_target,
            'daily_loss_violated': any(abs(min(0, d['profit_pct'])) > self.the5ers_rules.max_daily_loss 
                                     for d in self.daily_results.values()),
            'total_loss_violated': ((self.backtest_config.initial_balance - self.current_balance) / 
                                  self.backtest_config.initial_balance) * 100 > self.the5ers_rules.max_total_loss,
            'min_profitable_days': profitable_days >= self.the5ers_rules.min_profitable_days
        }
        
        return {
            'initial_balance': self.backtest_config.initial_balance,
            'final_balance': self.current_balance,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'max_drawdown': self.max_drawdown,
            'current_drawdown': self.current_drawdown,
            'profitable_days': profitable_days,
            'sharpe_ratio': sharpe_ratio,
            'the5ers_compliance': the5ers_compliance,
            'equity_curve': self.equity_curve,
            'daily_results': self.daily_results,
            'trades': self.trades
        }
