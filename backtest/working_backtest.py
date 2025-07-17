#!/usr/bin/env python3
# ====================================================================================
# WORKING BACKTEST SYSTEM - THE5ERS QUANTUM
# Sistema di backtest funzionante per The5ers Challenge
# ====================================================================================

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=== THE5ERS QUANTUM BACKTEST SYSTEM ===")

# ====================================================================================
# CONFIGURATION SYSTEM
# ====================================================================================

def get_the5ers_config():
    """Configuration per The5ers High Stakes Challenge - Aggiornata con contract_size corretti"""
    return {
        'symbols': {
            'EURUSD': {
                'spread': 0.00018, 
                'quantum_channels': 5, 
                'pip_value': 0.0001,
                'risk_management': {
                    'contract_size': 0.01,
                    'risk_percent': 0.012,
                    'base_sl_pips': 50,
                    'profit_multiplier': 2.2
                }
            },
            'GBPUSD': {
                'spread': 0.00025, 
                'quantum_channels': 5, 
                'pip_value': 0.0001,
                'risk_management': {
                    'contract_size': 0.01,
                    'risk_percent': 0.012,
                    'base_sl_pips': 60,
                    'profit_multiplier': 2.3
                }
            },
            'USDJPY': {
                'spread': 0.00020, 
                'quantum_channels': 5, 
                'pip_value': 0.01,
                'risk_management': {
                    'contract_size': 0.01,
                    'risk_percent': 0.012,
                    'base_sl_pips': 40,
                    'profit_multiplier': 2.1
                }
            },
            'USDCHF': {
                'spread': 0.00022, 
                'quantum_channels': 5, 
                'pip_value': 0.0001,
                'risk_management': {
                    'contract_size': 0.01,
                    'risk_percent': 0.012,
                    'base_sl_pips': 50,
                    'profit_multiplier': 2.2
                }
            },
            'XAUUSD': {
                'spread': 0.50, 
                'quantum_channels': 4, 
                'pip_value': 0.01,
                'risk_management': {
                    'contract_size': 0.01,
                    'risk_percent': 0.010,
                    'base_sl_pips': 220,
                    'profit_multiplier': 2.4
                }
            },
            'US30': {
                'spread': 2.0, 
                'quantum_channels': 4, 
                'pip_value': 1.0,
                'risk_management': {
                    'contract_size': 0.01,
                    'risk_percent': 0.010,
                    'base_sl_pips': 250,
                    'profit_multiplier': 2.5
                }
            }
        },
        'quantum_params': {
            'buffer_size': 50,
            'entropy_threshold': 0.7,
            'coherence_threshold': 0.8,
            'entanglement_strength': 1.2,
            'spin_correlation_threshold': 0.85,
            'quantum_noise_filter': 0.3
        },
        'risk_parameters': {
            'max_risk_per_trade': 2.0,
            'max_daily_risk': 5.0,
            'max_total_risk': 10.0,
            'trailing_stop_pips': 20,
            'take_profit_ratio': 2.0,
            'position_cooldown_minutes': 30
        },
        'the5ers_rules': {
            'step1_target': 8.0,
            'step2_target': 5.0,
            'scaling_target': 10.0,
            'max_daily_loss': 5.0,
            'max_total_loss': 10.0,
            'min_profitable_days': 3,
            'min_trading_days': 5,
            'consistency_rule': True
        },
        'timeframes': {
            'primary': 'M5',
            'secondary': 'M15',
            'tertiary': 'H1'
        },
        'trading_hours': {
            'start': 8,  # 8:00 UTC
            'end': 17    # 17:00 UTC
        }
    }

# ====================================================================================
# CORE CLASSES
# ====================================================================================

class BacktestConfig:
    def __init__(self, start_date: str, end_date: str, initial_balance: float, 
                 symbols: List[str], timeframe: str = "M5"):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.symbols = symbols
        self.timeframe = timeframe

class The5ersRules:
    def __init__(self, step1_target: float = 8.0, step2_target: float = 5.0,
                 scaling_target: float = 10.0, max_daily_loss: float = 5.0,
                 max_total_loss: float = 10.0, min_profitable_days: int = 3):
        self.step1_target = step1_target
        self.step2_target = step2_target
        self.scaling_target = scaling_target
        self.max_daily_loss = max_daily_loss
        self.max_total_loss = max_total_loss
        self.min_profitable_days = min_profitable_days

class HistoricalDataHandler:
    """Gestore dati storici con generazione sintetica avanzata"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_historical_data(self, symbol: str, start_date: str, end_date: str, 
                           timeframe: str = "M5") -> pd.DataFrame:
        """Carica dati storici (sintetici per test)"""
        
        # Configurazione per symbol
        if 'USD' in symbol and 'XAU' not in symbol:
            base_price = 1.1000 if symbol == 'EURUSD' else 1.3000
            volatility = 0.0015
        elif 'JPY' in symbol:
            base_price = 150.0
            volatility = 0.8
        elif 'XAU' in symbol:
            base_price = 2000.0
            volatility = 15.0
        else:
            base_price = 35000.0  # US30
            volatility = 200.0
        
        # Genera date
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        if timeframe == "M1":
            freq = "1min"
        elif timeframe == "M5":
            freq = "5min"
        elif timeframe == "M15":
            freq = "15min"
        elif timeframe == "H1":
            freq = "1H"
        else:
            freq = "5min"
        
        dates = pd.date_range(start=start, end=end, freq=freq)
        
        # Genera dati con trend e volatilità realistica
        np.random.seed(42)  # Per riproducibilità
        
        data = []
        current_price = base_price
        
        for i, timestamp in enumerate(dates):
            # Trend component
            trend = np.sin(i * 0.01) * volatility * 0.1
            
            # Random walk component
            random_change = np.random.normal(0, volatility * 0.1)
            
            # Price movement
            price_change = trend + random_change
            current_price += price_change
            
            # Generate OHLC
            open_price = current_price
            close_price = open_price + np.random.normal(0, volatility * 0.05)
            
            high_price = max(open_price, close_price) + abs(np.random.normal(0, volatility * 0.03))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, volatility * 0.03))
            
            volume = np.random.randint(100, 1000)
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'volume': volume
            })
            
            current_price = close_price
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        self.logger.info(f"Generated {len(df)} data points for {symbol}")
        return df

class SimpleQuantumEngine:
    """Engine quantum aggiornato per riflettere modifiche file principale"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quantum_buffer = {}
        self.entropy_values = {}
        self.position_cooldown = {}
        self.logger = logging.getLogger(__name__)
        
        # Carica parametri REALI dal file JSON
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
            
            with open(config_path, 'r') as f:
                real_config = json.load(f)
            
            quantum_params = real_config.get('quantum_params', {})
            
            # Parametri quantum AGGIORNATI dal file modificato
            self.buffer_size = quantum_params.get('buffer_size', 500)  # Era 50, ora 500
            self.spin_window = quantum_params.get('spin_window', 80)   # Era 20, ora 80
            self.signal_cooldown = quantum_params.get('signal_cooldown', 600)  # Era 300, ora 600
            
            # Entropy thresholds aggiornati
            entropy_thresholds = quantum_params.get('entropy_thresholds', {})
            self.buy_threshold = entropy_thresholds.get('buy_signal', 0.58)   # Era 0.7, ora 0.58
            self.sell_threshold = entropy_thresholds.get('sell_signal', 0.42) # Era 0.3, ora 0.42
            
            self.logger.info(f"🔬 Quantum Engine aggiornato:")
            self.logger.info(f"   Buffer size: {self.buffer_size}")
            self.logger.info(f"   Spin window: {self.spin_window}")
            self.logger.info(f"   Signal cooldown: {self.signal_cooldown}s")
            self.logger.info(f"   Buy threshold: {self.buy_threshold}")
            self.logger.info(f"   Sell threshold: {self.sell_threshold}")
            
        except Exception as e:
            self.logger.error(f"Errore caricamento parametri quantum: {e}")
            # Fallback ai parametri di default
            self.buffer_size = 500
            self.spin_window = 80
            self.signal_cooldown = 600
            self.buy_threshold = 0.58
            self.sell_threshold = 0.42
        
        # Initialize quantum buffers per simbolo
        for symbol in config['symbols'].keys():
            self.quantum_buffer[symbol] = []
            self.entropy_values[symbol] = []
    
    def process_tick(self, symbol: str, price: float, timestamp: datetime):
        """Processa un tick di prezzo"""
        buffer_size = self.config['quantum_params']['buffer_size']
        
        # Aggiungi al buffer
        self.quantum_buffer[symbol].append(price)
        if len(self.quantum_buffer[symbol]) > buffer_size:
            self.quantum_buffer[symbol].pop(0)
        
        # Calcola entropia semplificata
        if len(self.quantum_buffer[symbol]) >= 10:
            prices = np.array(self.quantum_buffer[symbol][-10:])
            returns = np.diff(prices)
            if len(returns) > 0:
                entropy = -np.sum(returns**2) / len(returns)
                self.entropy_values[symbol].append(entropy)
    
    def get_signal(self, symbol: str) -> Tuple[str, float]:
        """Genera segnale di trading"""
        if symbol not in self.entropy_values or len(self.entropy_values[symbol]) < 5:
            return "HOLD", 0.0
        
        # Controlla cooldown
        current_time = datetime.now().timestamp()
        cooldown_period = self.signal_cooldown  # Usa parametro aggiornato (600s)
        
        if symbol in self.position_cooldown:
            if current_time - self.position_cooldown[symbol] < cooldown_period:
                return "HOLD", 0.0
        
        # Calcolo segnale basato su entropia con SOGLIE AGGIORNATE
        recent_entropy = self.entropy_values[symbol][-10:]  # Più campioni per stabilità
        if len(recent_entropy) < 5:
            return "HOLD", 0.0
            
        avg_entropy = np.mean(recent_entropy)
        entropy_trend = recent_entropy[-1] - recent_entropy[0] if len(recent_entropy) > 1 else 0
        
        # Usa le nuove soglie dal file modificato
        buy_threshold = self.buy_threshold     # 0.58 invece di 0.7
        sell_threshold = self.sell_threshold   # 0.42 invece di 0.3
        
        # Logica aggiornata per essere più selettiva
        signal = "HOLD"
        confidence = 0.0
        
        if avg_entropy > buy_threshold and entropy_trend > 0.01:
            signal = "BUY"
            confidence = min((avg_entropy - buy_threshold) * 2.5, 0.9)
        elif avg_entropy < sell_threshold and entropy_trend < -0.01:
            signal = "SELL"
            confidence = min((sell_threshold - avg_entropy) * 2.5, 0.9)
        
        # Registra cooldown se segnale generato
        if signal != "HOLD":
            self.position_cooldown[symbol] = current_time
        
        return signal, confidence
    
    def can_trade(self, symbol: str) -> bool:
        """Verifica se è possibile tradare"""
        return len(self.quantum_buffer.get(symbol, [])) >= 10
    
    def record_trade_close(self, symbol: str):
        """Registra chiusura trade per cooldown"""
        self.position_cooldown[symbol] = datetime.now().timestamp()

class SimpleRiskManager:
    """Risk manager semplificato"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.daily_risk_used = {}
        self.logger = logging.getLogger(__name__)
    
    def calculate_position_size(self, symbol: str, balance: float, signal: str, confidence: float) -> float:
        """Calcola size della posizione - AGGIORNATO per riflettere modifiche file principale"""
        
        # Ottieni configurazione reale dal file JSON
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
            
            with open(config_path, 'r') as f:
                real_config = json.load(f)
            
            symbol_config = real_config.get('symbols', {}).get(symbol, {})
            risk_config = symbol_config.get('risk_management', {})
            
            # Usa parametri REALI dal file modificato
            contract_size = risk_config.get('contract_size', 0.01)  # 0.01 = micro lot
            risk_percent = risk_config.get('risk_percent', 0.0015)  # 0.15% ultra-conservativo
            base_sl_pips = risk_config.get('base_sl_pips', 50)
            
            # Calcola risk amount
            risk_amount = balance * risk_percent
            
            # SAFETY: Usa sempre contract_size fisso (come nel file principale)
            # Questo risolve i problemi di position sizing eccessivo
            position_size = contract_size
            
            # Apply safety limit come nel file principale (max 0.5 lotti)
            max_size_limit = 0.5
            if position_size > max_size_limit:
                self.logger.warning(f"Size limitata per {symbol}: {position_size:.2f} -> {max_size_limit}")
                position_size = max_size_limit
            
            # Verifica che non superi il 2% del saldo
            max_size_by_balance = balance * 0.02
            notional_value = position_size * 100000  # Standard lot value
            if notional_value > max_size_by_balance:
                position_size = max_size_by_balance / 100000
            
            # Assicura minimum 0.01 lot
            position_size = max(0.01, round(position_size, 2))
            
            self.logger.debug(f"Position size {symbol}: "
                            f"Contract={contract_size}, Risk%={risk_percent*100:.3f}%, "
                            f"Final={position_size}")
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Errore calcolo position size {symbol}: {e}")
            # Fallback sicuro
            return 0.01
    
    def calculate_sl_tp(self, symbol: str, price: float, signal: str) -> Tuple[float, float]:
        """Calcola Stop Loss e Take Profit"""
        pip_value = self.config['symbols'][symbol]['pip_value']
        trailing_stop_pips = self.config['risk_parameters']['trailing_stop_pips']
        tp_ratio = self.config['risk_parameters']['take_profit_ratio']
        
        sl_distance = trailing_stop_pips * pip_value
        tp_distance = sl_distance * tp_ratio
        
        if signal == "BUY":
            sl = price - sl_distance
            tp = price + tp_distance
        else:  # SELL
            sl = price + sl_distance
            tp = price - tp_distance
        
        return round(sl, 5), round(tp, 5)
    
    def check_daily_risk(self, symbol: str, additional_risk: float) -> bool:
        """Verifica rischio giornaliero"""
        max_daily_risk = self.config['risk_parameters']['max_daily_risk']
        current_date = datetime.now().date()
        
        if current_date not in self.daily_risk_used:
            self.daily_risk_used[current_date] = 0
        
        return self.daily_risk_used[current_date] + additional_risk <= max_daily_risk

class WorkingBacktestEngine:
    """Engine di backtest funzionante"""
    
    def __init__(self, config: Dict, backtest_config: BacktestConfig, the5ers_rules: The5ersRules):
        self.config = config
        self.backtest_config = backtest_config
        self.the5ers_rules = the5ers_rules
        
        # Componenti
        self.data_handler = HistoricalDataHandler()
        self.quantum_engine = SimpleQuantumEngine(config)
        self.risk_manager = SimpleRiskManager(config)
        
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
        self.peak_balance = backtest_config.initial_balance
        
        self.logger = logging.getLogger(__name__)
    
    def run_backtest(self) -> Dict:
        """Esegue il backtest completo"""
        self.logger.info("Starting backtest...")
        
        # Carica dati per tutti i simboli
        market_data = {}
        for symbol in self.backtest_config.symbols:
            market_data[symbol] = self.data_handler.load_historical_data(
                symbol, 
                self.backtest_config.start_date,
                self.backtest_config.end_date,
                self.backtest_config.timeframe
            )
        
        # Esegui simulazione
        self._run_simulation(market_data)
        
        # Calcola risultati
        return self._calculate_results()
    
    def _run_simulation(self, market_data: Dict[str, pd.DataFrame]):
        """Esegue la simulazione principale"""
        
        # Trova intervallo comune
        all_timestamps = set()
        for df in market_data.values():
            all_timestamps.update(df.index)
        
        sorted_timestamps = sorted(all_timestamps)
        
        for timestamp in sorted_timestamps:
            # Aggiorna equity curve
            self.equity_curve.append({
                'timestamp': timestamp,
                'balance': self.current_balance,
                'equity': self._calculate_current_equity(timestamp, market_data)
            })
            
            # Processa ogni simbolo
            for symbol in self.backtest_config.symbols:
                if timestamp in market_data[symbol].index:
                    row = market_data[symbol].loc[timestamp]
                    self._process_symbol_tick(symbol, row, timestamp)
    
    def _process_symbol_tick(self, symbol: str, row: pd.Series, timestamp: datetime):
        """Processa un tick per un simbolo"""
        price = row['close']
        
        # Aggiorna quantum engine
        self.quantum_engine.process_tick(symbol, price, timestamp)
        
        # Controlla posizioni esistenti
        if symbol in self.current_positions:
            self._check_position_exit(symbol, price, timestamp)
        
        # Cerca nuove opportunità
        elif self.quantum_engine.can_trade(symbol):
            signal, confidence = self.quantum_engine.get_signal(symbol)
            
            if signal != "HOLD" and confidence > 0.5:
                self._try_open_position(symbol, signal, confidence, price, timestamp)
    
    def _try_open_position(self, symbol: str, signal: str, confidence: float, 
                          price: float, timestamp: datetime):
        """Prova ad aprire una posizione"""
        
        # Calcola position size
        position_size = self.risk_manager.calculate_position_size(
            symbol, self.current_balance, signal, confidence
        )
        
        # Calcola SL e TP
        sl, tp = self.risk_manager.calculate_sl_tp(symbol, price, signal)
        
        # Verifica rischio giornaliero
        risk_amount = position_size * abs(price - sl)
        if not self.risk_manager.check_daily_risk(symbol, risk_amount):
            return
        
        # Apri posizione
        position = {
            'symbol': symbol,
            'signal': signal,
            'entry_price': price,
            'position_size': position_size,
            'sl': sl,
            'tp': tp,
            'entry_time': timestamp,
            'confidence': confidence
        }
        
        self.current_positions[symbol] = position
        self.logger.info(f"Opened {signal} position for {symbol} at {price}")
    
    def _check_position_exit(self, symbol: str, current_price: float, timestamp: datetime):
        """Controlla se chiudere una posizione"""
        position = self.current_positions[symbol]
        should_close = False
        exit_reason = ""
        
        if position['signal'] == "BUY":
            if current_price <= position['sl']:
                should_close = True
                exit_reason = "SL Hit"
            elif current_price >= position['tp']:
                should_close = True
                exit_reason = "TP Hit"
        else:  # SELL
            if current_price >= position['sl']:
                should_close = True
                exit_reason = "SL Hit"
            elif current_price <= position['tp']:
                should_close = True
                exit_reason = "TP Hit"
        
        if should_close:
            self._close_position(symbol, current_price, timestamp, exit_reason)
    
    def _close_position(self, symbol: str, exit_price: float, timestamp: datetime, reason: str):
        """Chiude una posizione"""
        position = self.current_positions[symbol]
        
        # Calcola P&L
        if position['signal'] == "BUY":
            pnl = (exit_price - position['entry_price']) * position['position_size'] * 100000
        else:
            pnl = (position['entry_price'] - exit_price) * position['position_size'] * 100000
        
        # Applica spread
        spread = self.config['symbols'][symbol]['spread']
        pnl -= spread * position['position_size'] * 100000
        
        # Aggiorna balance
        self.current_balance += pnl
        
        # Registra trade
        trade = {
            'symbol': symbol,
            'signal': position['signal'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'pnl': pnl,
            'reason': reason,
            'confidence': position['confidence']
        }
        
        self.trades.append(trade)
        
        # Aggiorna statistiche
        self.total_trades += 1
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Rimuovi posizione
        del self.current_positions[symbol]
        
        # Record cooldown
        self.quantum_engine.record_trade_close(symbol)
        
        self.logger.info(f"Closed {position['signal']} {symbol} at {exit_price}, P&L: ${pnl:.2f}")
    
    def _calculate_current_equity(self, timestamp: datetime, market_data: Dict) -> float:
        """Calcola equity corrente includendo posizioni aperte"""
        equity = self.current_balance
        
        for symbol, position in self.current_positions.items():
            if timestamp in market_data[symbol].index:
                current_price = market_data[symbol].loc[timestamp, 'close']
                
                if position['signal'] == "BUY":
                    unrealized_pnl = (current_price - position['entry_price']) * position['position_size'] * 100000
                else:
                    unrealized_pnl = (position['entry_price'] - current_price) * position['position_size'] * 100000
                
                equity += unrealized_pnl
        
        return equity
    
    def _calculate_results(self) -> Dict:
        """Calcola risultati finali"""
        
        if not self.trades:
            # Nessun trade eseguito
            return {
                'initial_balance': self.backtest_config.initial_balance,
                'final_balance': self.current_balance,
                'total_return': 0.0,
                'total_return_pct': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'max_drawdown': 0.0,
                'current_drawdown': 0.0,
                'profitable_days': 0,
                'sharpe_ratio': 0.0,
                'the5ers_compliance': {
                    'step1_achieved': False,
                    'step2_achieved': False,
                    'scaling_achieved': False,
                    'daily_loss_violated': False,
                    'total_loss_violated': False,
                    'min_profitable_days': False
                },
                'equity_curve': self.equity_curve,
                'daily_results': {},
                'trades': []
            }
        
        # Calcola statistiche base
        total_return = self.current_balance - self.backtest_config.initial_balance
        total_return_pct = (total_return / self.backtest_config.initial_balance) * 100
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Calcola drawdown
        peak = self.backtest_config.initial_balance
        max_dd = 0
        
        for point in self.equity_curve:
            equity = point['equity']
            if equity > peak:
                peak = equity
            
            drawdown = (peak - equity) / peak * 100
            max_dd = max(max_dd, drawdown)
        
        # Calcola giorni profittevoli
        daily_pnl = {}
        for trade in self.trades:
            date = trade['exit_time'].date()
            if date not in daily_pnl:
                daily_pnl[date] = 0
            daily_pnl[date] += trade['pnl']
        
        profitable_days = sum(1 for pnl in daily_pnl.values() if pnl > 0)
        
        # Calcola Sharpe ratio semplificato
        if len(daily_pnl) > 1:
            daily_returns = list(daily_pnl.values())
            avg_return = np.mean(daily_returns)
            std_return = np.std(daily_returns)
            sharpe = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe = 0
        
        # Verifica compliance The5ers
        the5ers_compliance = {
            'step1_achieved': total_return_pct >= self.the5ers_rules.step1_target,
            'step2_achieved': total_return_pct >= self.the5ers_rules.step2_target,
            'scaling_achieved': total_return_pct >= self.the5ers_rules.scaling_target,
            'daily_loss_violated': any(pnl < -self.the5ers_rules.max_daily_loss * self.backtest_config.initial_balance / 100 
                                     for pnl in daily_pnl.values()),
            'total_loss_violated': total_return_pct < -self.the5ers_rules.max_total_loss,
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
            'max_drawdown': max_dd,
            'current_drawdown': self.current_drawdown,
            'profitable_days': profitable_days,
            'sharpe_ratio': sharpe,
            'the5ers_compliance': the5ers_compliance,
            'equity_curve': self.equity_curve,
            'daily_results': daily_pnl,
            'trades': self.trades
        }

# ====================================================================================
# MAIN TEST FUNCTION
# ====================================================================================

def run_quick_test():
    """Esegue un test veloce del sistema"""
    
    print("\n🚀 AVVIO TEST VELOCE SISTEMA BACKTEST")
    print("="*50)
    
    # Configurazione
    config = get_the5ers_config()
    
    # Test configuration (1 giorno, 1 simbolo)
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-01",
        initial_balance=100000,
        symbols=["EURUSD"],
        timeframe="M5"
    )
    
    the5ers_rules = The5ersRules()
    
    # Crea e esegui backtest
    print(f"📊 Configurazione Test:")
    print(f"   - Periodo: {backtest_config.start_date}")
    print(f"   - Balance iniziale: ${backtest_config.initial_balance:,}")
    print(f"   - Simboli: {backtest_config.symbols}")
    print(f"   - Timeframe: {backtest_config.timeframe}")
    print(f"   - Target Step 1: {the5ers_rules.step1_target}%")
    
    engine = WorkingBacktestEngine(config, backtest_config, the5ers_rules)
    
    print("\n⚡ Esecuzione backtest...")
    results = engine.run_backtest()
    
    # Mostra risultati
    print("\n" + "="*50)
    print("📈 RISULTATI TEST")
    print("="*50)
    print(f"Balance iniziale:    ${results['initial_balance']:,}")
    print(f"Balance finale:      ${results['final_balance']:,}")
    print(f"Return totale:       {results['total_return_pct']:.2f}%")
    print(f"Trades totali:       {results['total_trades']}")
    print(f"Trades vincenti:     {results['winning_trades']}")
    print(f"Win rate:            {results['win_rate']:.1f}%")
    print(f"Max drawdown:        {results['max_drawdown']:.2f}%")
    print(f"Giorni profittevoli: {results['profitable_days']}")
    print(f"Sharpe ratio:        {results['sharpe_ratio']:.2f}")
    
    print(f"\n🎯 THE5ERS COMPLIANCE:")
    compliance = results['the5ers_compliance']
    print(f"Step 1 (8%):         {'✅' if compliance['step1_achieved'] else '❌'}")
    print(f"Step 2 (5%):         {'✅' if compliance['step2_achieved'] else '❌'}")
    print(f"Scaling (10%):       {'✅' if compliance['scaling_achieved'] else '❌'}")
    print(f"Max loss OK:         {'✅' if not compliance['total_loss_violated'] else '❌'}")
    print(f"Daily loss OK:       {'✅' if not compliance['daily_loss_violated'] else '❌'}")
    print(f"Min profitable days: {'✅' if compliance['min_profitable_days'] else '❌'}")
    
    if results['total_trades'] > 0:
        print(f"\n📝 Esempio trade:")
        trade = results['trades'][0]
        print(f"   {trade['signal']} {trade['symbol']} @ {trade['entry_price']:.5f}")
        print(f"   Exit: {trade['exit_price']:.5f} ({trade['reason']})")
        print(f"   P&L: ${trade['pnl']:.2f}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_quick_test()
        print(f"\n🎉 TEST COMPLETATO CON SUCCESSO!")
        
        if results['total_trades'] > 0:
            print(f"\n✨ Il sistema ha eseguito {results['total_trades']} trades")
            print(f"💰 Return: {results['total_return_pct']:.2f}%")
            print(f"🎯 Target Step 1: {'RAGGIUNTO' if results['the5ers_compliance']['step1_achieved'] else 'NON RAGGIUNTO'}")
        else:
            print(f"\n⚠️  Nessun trade eseguito nel periodo di test")
            print(f"💡 Prova ad estendere il periodo di test o modificare i parametri")
        
        print(f"\n🚀 PROSSIMI PASSI:")
        print(f"1. Estendi il periodo di test (es: 1 settimana)")
        print(f"2. Aggiungi più simboli")
        print(f"3. Ottimizza i parametri quantum")
        print(f"4. Esegui test con dati reali")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
