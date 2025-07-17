#!/usr/bin/env python3
# ====================================================================================
# UPDATED BACKTEST ENGINE - THE5ERS QUANTUM SYSTEM
# Backtest aggiornato che riflette le ultime modifiche ai file principali
# ====================================================================================

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=== UPDATED THE5ERS QUANTUM BACKTEST ENGINE ===")

# ====================================================================================
# CONFIGURATION LOADER
# ====================================================================================

def load_real_config():
    """Carica la configurazione reale dal file JSON"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info("✅ Configurazione reale caricata correttamente")
        return config
        
    except Exception as e:
        logger.error(f"❌ Errore caricamento configurazione: {e}")
        return {}

# ====================================================================================
# BACKTEST COMPONENTS
# ====================================================================================

@dataclass 
class BacktestConfig:
    """Configurazione del backtest"""
    start_date: str
    end_date: str  
    initial_balance: float
    symbols: List[str]
    timeframe: str = "M15"

@dataclass
class The5ersRules:
    """Regole The5ers Challenge"""
    daily_loss_limit: float = 5.0  # %
    total_loss_limit: float = 10.0  # %
    profit_target: float = 8.0  # %
    minimum_trading_days: int = 5

class UpdatedQuantumEngine:
    """Engine quantum semplificato che riflette le modifiche principali"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quantum_params = config.get('quantum_params', {})
        self.symbols_config = config.get('symbols', {})
        
        # Buffer per ogni simbolo
        self.tick_buffers = {}
        self.entropy_cache = {}
        self.signal_cooldown = {}
        
        # Parametri quantum aggiornati
        self.buffer_size = self.quantum_params.get('buffer_size', 500)
        self.entropy_thresholds = self.quantum_params.get('entropy_thresholds', {
            'buy_signal': 0.58,
            'sell_signal': 0.42
        })
        self.signal_cooldown_time = self.quantum_params.get('signal_cooldown', 600)
        
        logger.info(f"🔧 Quantum Engine inizializzato:")
        logger.info(f"   Buffer size: {self.buffer_size}")
        logger.info(f"   Buy threshold: {self.entropy_thresholds['buy_signal']}")
        logger.info(f"   Sell threshold: {self.entropy_thresholds['sell_signal']}")
        logger.info(f"   Signal cooldown: {self.signal_cooldown_time}s")
        
        # Inizializza buffer per simboli attivi
        for symbol in self.symbols_config.keys():
            self.tick_buffers[symbol] = []
            self.entropy_cache[symbol] = 0.5
            self.signal_cooldown[symbol] = 0
    
    def process_tick(self, symbol: str, price: float, timestamp: datetime):
        """Processa un tick e aggiorna buffer"""
        
        if symbol not in self.tick_buffers:
            self.tick_buffers[symbol] = []
        
        # Aggiungi tick al buffer
        self.tick_buffers[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Mantieni dimensione buffer
        if len(self.tick_buffers[symbol]) > self.buffer_size:
            self.tick_buffers[symbol].pop(0)
        
        # Calcola entropy se abbiamo abbastanza dati
        if len(self.tick_buffers[symbol]) >= 20:
            self._calculate_entropy(symbol)
    
    def _calculate_entropy(self, symbol: str):
        """Calcola entropy quantistica basata sui tick"""
        
        buffer = self.tick_buffers[symbol]
        if len(buffer) < 10:
            return
        
        # Estrai prezzi
        prices = [tick['price'] for tick in buffer[-50:]]  # Ultimi 50 tick
        
        # Calcola returns
        returns = np.diff(prices) / prices[:-1]
        
        # Calcola entropy semplificata (basata su volatilità normalizzata)
        if len(returns) > 0:
            volatility = np.std(returns)
            mean_return = np.mean(returns)
            
            # Entropy basata su distribuzione returns
            entropy = 0.5 + (mean_return / (volatility + 1e-10)) * 0.1
            entropy = max(0.0, min(1.0, entropy))  # Clamp tra 0 e 1
            
            self.entropy_cache[symbol] = entropy
    
    def get_signal(self, symbol: str, current_time: datetime) -> Tuple[str, float]:
        """Genera segnale basato su entropy"""
        
        # Verifica cooldown
        if current_time.timestamp() - self.signal_cooldown.get(symbol, 0) < self.signal_cooldown_time:
            return "HOLD", 0.0
        
        # Ottieni entropy corrente  
        entropy = self.entropy_cache.get(symbol, 0.5)
        
        # Verifica soglie
        buy_threshold = self.entropy_thresholds['buy_signal']
        sell_threshold = self.entropy_thresholds['sell_signal']
        
        # Genera segnale
        if entropy > buy_threshold:
            confidence = min(0.9, (entropy - buy_threshold) * 3)
            self.signal_cooldown[symbol] = current_time.timestamp()
            return "BUY", confidence
        elif entropy < sell_threshold:
            confidence = min(0.9, (sell_threshold - entropy) * 3)
            self.signal_cooldown[symbol] = current_time.timestamp()
            return "SELL", confidence
        
        return "HOLD", 0.0
    
    def can_trade(self, symbol: str) -> bool:
        """Verifica se può tradare (semplificato per backtest)"""
        return len(self.tick_buffers.get(symbol, [])) >= 20

class UpdatedRiskManager:
    """Risk Manager aggiornato che riflette le modifiche principali"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.risk_params = config.get('risk_parameters', {})
        self.symbols_config = config.get('symbols', {})
        
        logger.info("🛡️  Risk Manager aggiornato inizializzato")
    
    def calculate_position_size(self, symbol: str, account_balance: float, signal: str, confidence: float) -> float:
        """Calcola position size usando la logica aggiornata dal file principale"""
        
        try:
            # Ottieni configurazione simbolo
            symbol_config = self.symbols_config.get(symbol, {})
            risk_config = symbol_config.get('risk_management', {})
            
            # Parametri aggiornati (più conservativi)
            risk_percent = risk_config.get('risk_percent', 0.0015)  # 0.15% - molto conservativo
            contract_size = risk_config.get('contract_size', 0.01)  # 0.01 lotti (micro lot)
            base_sl_pips = risk_config.get('base_sl_pips', 50)
            
            # Calcola risk amount
            risk_amount = account_balance * risk_percent
            
            # Pip value per simbolo (semplificato per backtest)
            pip_values = {
                'EURUSD': 0.1,   # Per micro lot (0.01)
                'GBPUSD': 0.1,   
                'USDJPY': 0.09,  
                'XAUUSD': 0.01,  
                'NAS100': 0.01
            }
            
            pip_value = pip_values.get(symbol, 0.1)
            
            # Calcola size basato su risk
            if base_sl_pips > 0 and pip_value > 0:
                calculated_size = risk_amount / (base_sl_pips * pip_value)
            else:
                calculated_size = contract_size
            
            # Safety limit - massimo 0.5 lotti (come nel file principale)
            max_size_limit = 0.5
            if calculated_size > max_size_limit:
                logger.warning(f"Size limitata per {symbol}: {calculated_size:.4f} -> {max_size_limit}")
                calculated_size = max_size_limit
            
            # Usa sempre contract_size fisso per sicurezza (0.01)
            position_size = contract_size
            
            # Verifica che non superi il 2% del conto
            max_size_by_balance = account_balance * 0.02
            notional_value = position_size * 100000  # Converti in valore nozionale
            if notional_value > max_size_by_balance:
                position_size = max_size_by_balance / 100000
            
            # Minimum 0.01 lot
            position_size = max(0.01, round(position_size, 2))
            
            logger.debug(f"Position size {symbol}: Risk={risk_percent*100:.3f}%, "
                        f"Contract={contract_size}, Final={position_size}")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Errore calcolo position size {symbol}: {e}")
            return 0.01  # Fallback to minimum size
    
    def calculate_sl_tp(self, symbol: str, entry_price: float, signal: str) -> Tuple[float, float]:
        """Calcola stop loss e take profit"""
        
        symbol_config = self.symbols_config.get(symbol, {})
        risk_config = symbol_config.get('risk_management', {})
        
        base_sl_pips = risk_config.get('base_sl_pips', 50)
        profit_multiplier = risk_config.get('profit_multiplier', 2.2)
        
        # Pip size per simbolo
        pip_sizes = {
            'EURUSD': 0.0001,
            'GBPUSD': 0.0001,
            'USDJPY': 0.01,
            'XAUUSD': 0.01,
            'NAS100': 1.0
        }
        
        pip_size = pip_sizes.get(symbol, 0.0001)
        
        # Calcola SL e TP
        sl_distance = base_sl_pips * pip_size
        tp_distance = sl_distance * profit_multiplier
        
        if signal == "BUY":
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
        else:  # SELL
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance
        
        return sl_price, tp_price

class DataGenerator:
    """Generatore di dati sintetici per test"""
    
    @staticmethod
    def generate_realistic_data(symbol: str, start_date: str, end_date: str, timeframe: str = "M15") -> pd.DataFrame:
        """Genera dati più realistici per il testing"""
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Frequenza basata sul timeframe
        freq_map = {"M1": "1min", "M5": "5min", "M15": "15min", "H1": "1H"}
        freq = freq_map.get(timeframe, "15min")
        
        # Genera timestamp
        timestamps = pd.date_range(start=start, end=end, freq=freq)
        n_points = len(timestamps)
        
        # Parametri per simbolo
        symbol_params = {
            'EURUSD': {'base': 1.1000, 'volatility': 0.0002, 'trend': 0.00001},
            'GBPUSD': {'base': 1.3000, 'volatility': 0.0003, 'trend': -0.00001},
            'USDJPY': {'base': 110.00, 'volatility': 0.02, 'trend': 0.001},
            'XAUUSD': {'base': 1800.0, 'volatility': 1.0, 'trend': 0.1},
            'NAS100': {'base': 14000.0, 'volatility': 15.0, 'trend': 1.0}
        }
        
        params = symbol_params.get(symbol, symbol_params['EURUSD'])
        
        # Genera prezzi con trend e mean reversion
        np.random.seed(42)  # Per riproducibilità
        
        # Random walk con trend
        returns = np.random.normal(params['trend'], params['volatility'], n_points)
        
        # Aggiungi mean reversion
        prices = [params['base']]
        for i in range(1, n_points):
            mean_reversion = (params['base'] - prices[-1]) * 0.001
            price = prices[-1] + returns[i] + mean_reversion
            prices.append(price)
        
        prices = np.array(prices)
        
        # Genera OHLCV
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': prices * (1 + np.random.uniform(0, 0.0005, n_points)),
            'low': prices * (1 - np.random.uniform(0, 0.0005, n_points)),
            'close': prices * (1 + np.random.uniform(-0.0002, 0.0002, n_points)),
            'volume': np.random.randint(50, 200, n_points)
        })
        
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"📊 Generati {len(df)} punti dati per {symbol} ({start_date} - {end_date})")
        return df

class UpdatedBacktestEngine:
    """Engine principale del backtest aggiornato"""
    
    def __init__(self, backtest_config: BacktestConfig, the5ers_rules: The5ersRules):
        self.backtest_config = backtest_config
        self.the5ers_rules = the5ers_rules
        
        # Carica configurazione reale
        self.real_config = load_real_config()
        
        # Inizializza componenti
        self.quantum_engine = UpdatedQuantumEngine(self.real_config)
        self.risk_manager = UpdatedRiskManager(self.real_config)
        self.data_generator = DataGenerator()
        
        # Stato backtest
        self.current_balance = backtest_config.initial_balance
        self.trades = []
        self.daily_results = {}
        self.open_positions = {}
        
        # Statistiche
        self.total_trades = 0
        self.winning_trades = 0
        self.max_drawdown = 0.0
        
        logger.info(f"🚀 Backtest Engine inizializzato:")
        logger.info(f"   Periodo: {backtest_config.start_date} - {backtest_config.end_date}")
        logger.info(f"   Simboli: {backtest_config.symbols}")
        logger.info(f"   Saldo iniziale: ${backtest_config.initial_balance:,.2f}")
    
    def run_backtest(self) -> Dict[str, Any]:
        """Esegue il backtest completo"""
        
        logger.info("▶️  Avvio backtest...")
        
        start_date = pd.to_datetime(self.backtest_config.start_date)
        end_date = pd.to_datetime(self.backtest_config.end_date)
        
        # Genera dati per ogni simbolo
        symbol_data = {}
        for symbol in self.backtest_config.symbols:
            symbol_data[symbol] = self.data_generator.generate_realistic_data(
                symbol, self.backtest_config.start_date, self.backtest_config.end_date, 
                self.backtest_config.timeframe
            )
        
        # Processa giorno per giorno
        current_date = start_date
        while current_date <= end_date:
            day_start_balance = self.current_balance
            
            # Processa ogni simbolo per il giorno corrente
            for symbol in self.backtest_config.symbols:
                self._process_symbol_day(symbol, symbol_data[symbol], current_date)
            
            # Calcola risultati giornalieri
            day_profit = self.current_balance - day_start_balance
            day_profit_pct = (day_profit / day_start_balance) * 100 if day_start_balance > 0 else 0
            
            self.daily_results[current_date.strftime("%Y-%m-%d")] = {
                'profit': day_profit,
                'profit_pct': day_profit_pct,
                'balance': self.current_balance
            }
            
            # Aggiorna drawdown
            if hasattr(self, 'peak_balance'):
                if self.current_balance > self.peak_balance:
                    self.peak_balance = self.current_balance
            else:
                self.peak_balance = self.current_balance
            
            current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance * 100
            self.max_drawdown = max(self.max_drawdown, current_drawdown)
            
            # Verifica regole The5ers
            if day_profit_pct < -self.the5ers_rules.daily_loss_limit:
                logger.warning(f"⚠️  Daily loss limit violato: {day_profit_pct:.2f}%")
            
            current_date += timedelta(days=1)
        
        # Calcola risultati finali
        results = self._calculate_final_results()
        
        logger.info("✅ Backtest completato!")
        self._print_results(results)
        
        return results
    
    def _process_symbol_day(self, symbol: str, symbol_data: pd.DataFrame, date: datetime):
        """Processa un simbolo per un giorno specifico"""
        
        # Filtra dati per il giorno corrente
        day_start = date.replace(hour=0, minute=0, second=0)
        day_end = date.replace(hour=23, minute=59, second=59)
        
        day_data = symbol_data.loc[
            (symbol_data.index >= day_start) & (symbol_data.index <= day_end)
        ]
        
        # Processa ogni tick del giorno
        for timestamp, row in day_data.iterrows():
            current_price = row['close']
            
            # Aggiorna quantum engine
            self.quantum_engine.process_tick(symbol, current_price, timestamp)
            
            # Gestisci posizioni aperte
            if symbol in self.open_positions:
                self._manage_position(symbol, current_price, timestamp)
            
            # Verifica nuovi segnali (solo se non abbiamo posizioni aperte)
            elif self.quantum_engine.can_trade(symbol):
                signal, confidence = self.quantum_engine.get_signal(symbol, timestamp)
                
                if signal in ["BUY", "SELL"] and confidence > 0.5:
                    self._open_position(symbol, signal, current_price, timestamp, confidence)
    
    def _open_position(self, symbol: str, signal: str, price: float, timestamp: datetime, confidence: float):
        """Apre una nuova posizione"""
        
        # Calcola position size
        position_size = self.risk_manager.calculate_position_size(
            symbol, self.current_balance, signal, confidence
        )
        
        if position_size <= 0:
            return
        
        # Calcola SL e TP
        sl_price, tp_price = self.risk_manager.calculate_sl_tp(symbol, price, signal)
        
        # Crea posizione
        position = {
            'symbol': symbol,
            'signal': signal,
            'entry_price': price,
            'entry_time': timestamp,
            'volume': position_size,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'confidence': confidence
        }
        
        self.open_positions[symbol] = position
        
        logger.debug(f"📈 Posizione aperta: {symbol} {signal} @ {price:.5f} "
                    f"Vol: {position_size} Conf: {confidence:.2f}")
    
    def _manage_position(self, symbol: str, current_price: float, timestamp: datetime):
        """Gestisce una posizione aperta"""
        
        position = self.open_positions[symbol]
        
        # Verifica condizioni di chiusura
        exit_reason = None
        
        if position['signal'] == 'BUY':
            if current_price <= position['sl_price']:
                exit_reason = 'SL'
            elif current_price >= position['tp_price']:
                exit_reason = 'TP'
        else:  # SELL
            if current_price >= position['sl_price']:
                exit_reason = 'SL'
            elif current_price <= position['tp_price']:
                exit_reason = 'TP'
        
        # Timeout dopo 6 ore
        time_diff = (timestamp - position['entry_time']).total_seconds()
        if time_diff > 6 * 3600:  # 6 ore
            exit_reason = 'TIMEOUT'
        
        # Chiudi posizione se necessario
        if exit_reason:
            self._close_position(symbol, current_price, timestamp, exit_reason)
    
    def _close_position(self, symbol: str, exit_price: float, timestamp: datetime, reason: str):
        """Chiude una posizione"""
        
        position = self.open_positions[symbol]
        
        # Calcola profit
        if position['signal'] == 'BUY':
            price_diff = exit_price - position['entry_price']
        else:
            price_diff = position['entry_price'] - exit_price
        
        # Profit in USD (semplificato)
        if symbol in ['EURUSD', 'GBPUSD']:
            profit = price_diff * position['volume'] * 100000  # Standard lot conversion
        elif symbol == 'USDJPY':
            profit = price_diff * position['volume'] * 1000
        elif symbol == 'XAUUSD':
            profit = price_diff * position['volume'] * 100
        elif symbol == 'NAS100':
            profit = price_diff * position['volume'] * 1
        else:
            profit = price_diff * position['volume'] * 100000
        
        # Sottrai spread (semplificato)
        spread_cost = position['volume'] * 2  # $2 per lot di spread
        profit -= spread_cost
        
        # Aggiorna saldo
        self.current_balance += profit
        
        # Registra trade
        trade = {
            'symbol': symbol,
            'signal': position['signal'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'volume': position['volume'],
            'profit': profit,
            'reason': reason,
            'confidence': position['confidence']
        }
        
        self.trades.append(trade)
        
        # Aggiorna statistiche
        self.total_trades += 1
        if profit > 0:
            self.winning_trades += 1
        
        # Rimuovi posizione
        del self.open_positions[symbol]
        
        logger.debug(f"📉 Posizione chiusa: {symbol} {reason} P&L: ${profit:.2f}")
    
    def _calculate_final_results(self) -> Dict[str, Any]:
        """Calcola risultati finali"""
        
        total_return = self.current_balance - self.backtest_config.initial_balance
        total_return_pct = (total_return / self.backtest_config.initial_balance) * 100
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        profitable_days = len([d for d in self.daily_results.values() if d['profit'] > 0])
        
        # The5ers compliance
        the5ers_compliance = {
            'step1_achieved': total_return_pct >= 8.0,
            'step2_achieved': total_return_pct >= 5.0,
            'scaling_achieved': total_return_pct >= 10.0,
            'daily_loss_violated': any(d['profit_pct'] < -5.0 for d in self.daily_results.values()),
            'total_loss_violated': self.max_drawdown > 10.0
        }
        
        return {
            'initial_balance': self.backtest_config.initial_balance,
            'final_balance': self.current_balance,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'max_drawdown': self.max_drawdown,
            'profitable_days': profitable_days,
            'the5ers_compliance': the5ers_compliance,
            'trades': self.trades,
            'daily_results': self.daily_results
        }
    
    def _print_results(self, results: Dict[str, Any]):
        """Stampa risultati formattati"""
        
        print("\n" + "="*60)
        print("🏆 RISULTATI BACKTEST THE5ERS QUANTUM SYSTEM")
        print("="*60)
        
        print(f"💰 Balance iniziale:     ${results['initial_balance']:,.2f}")
        print(f"💰 Balance finale:       ${results['final_balance']:,.2f}")
        print(f"📈 Return totale:        {results['total_return_pct']:.2f}%")
        print(f"📉 Max Drawdown:         {results['max_drawdown']:.2f}%")
        print(f"🔢 Trades totali:        {results['total_trades']}")
        print(f"🎯 Win Rate:             {results['win_rate']:.1f}%")
        print(f"📊 Giorni profittevoli:  {results['profitable_days']}")
        
        print(f"\n🎯 THE5ERS COMPLIANCE:")
        compliance = results['the5ers_compliance']
        print(f"   Step 1 (8%):          {'✅' if compliance['step1_achieved'] else '❌'}")
        print(f"   Step 2 (5%):          {'✅' if compliance['step2_achieved'] else '❌'}")
        print(f"   Scaling (10%):        {'✅' if compliance['scaling_achieved'] else '❌'}")
        print(f"   Daily loss OK:        {'✅' if not compliance['daily_loss_violated'] else '❌'}")
        print(f"   Total loss OK:        {'✅' if not compliance['total_loss_violated'] else '❌'}")
        
        if results['total_trades'] > 0:
            avg_profit = results['total_return'] / results['total_trades']
            print(f"\n📊 STATISTICHE AGGIUNTIVE:")
            print(f"   Profit medio per trade: ${avg_profit:.2f}")
            print(f"   Trades vincenti:        {results['winning_trades']}")
            print(f"   Trades perdenti:        {results['total_trades'] - results['winning_trades']}")

# ====================================================================================
# MAIN EXECUTION
# ====================================================================================

def run_updated_backtest():
    """Esegue backtest con configurazione aggiornata"""
    
    # Configurazione backtest
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-10",  # 10 giorni di test
        initial_balance=100000,
        symbols=["EURUSD", "GBPUSD", "XAUUSD"],
        timeframe="M15"
    )
    
    # Regole The5ers
    the5ers_rules = The5ersRules(
        daily_loss_limit=5.0,
        total_loss_limit=10.0,
        profit_target=8.0,
        minimum_trading_days=5
    )
    
    # Esegui backtest
    engine = UpdatedBacktestEngine(backtest_config, the5ers_rules)
    results = engine.run_backtest()
    
    return results

if __name__ == "__main__":
    print("🚀 AVVIO BACKTEST AGGIORNATO")
    print("🔧 Usando configurazione reale dai file modificati")
    
    try:
        results = run_updated_backtest()
        
        print(f"\n🎉 BACKTEST COMPLETATO!")
        print(f"✨ Sistema testato con parametri aggiornati")
        
    except Exception as e:
        logger.error(f"❌ Errore durante backtest: {e}")
        import traceback
        traceback.print_exc()
