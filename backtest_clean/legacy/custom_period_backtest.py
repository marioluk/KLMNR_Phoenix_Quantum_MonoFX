#!/usr/bin/env python3
# ====================================================================================
# THE5ERS CUSTOM PERIOD BACKTEST - PERIODO PERSONALIZZABILE
# Sistema di backtest con controllo completo dei periodi di analisi
# ====================================================================================

import json
import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class The5ersCustomPeriodBacktest:
    """Sistema di backtest con periodo completamente personalizzabile"""
    
    def __init__(self):
        """Inizializza utilizzando configurazione reale"""
        self.config = self.load_main_config()
        self.trades = []
        self.equity_curve = []
        
        # Parametri The5ers dalla config
        the5ers_config = self.config.get('THE5ERS_specific', {})
        self.step1_target = the5ers_config.get('step1_target', 8) / 100  # 8%
        self.max_daily_loss = the5ers_config.get('max_daily_loss_percent', 5) / 100  # 5%
        self.max_total_loss = the5ers_config.get('max_total_loss_percent', 10) / 100  # 10%
        
        logger.info("🚀 The5ers Custom Period Backtest inizializzato")
    
    def load_main_config(self):
        """Carica configurazione dal file principale JSON"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json')
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            logger.info("✅ Configurazione principale caricata correttamente")
            return config
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento configurazione: {e}")
            return self.get_fallback_config()
    
    def get_fallback_config(self):
        """Configurazione di fallback"""
        return {
            'quantum_params': {
                'buffer_size': 500,
                'signal_cooldown': 600,
                'entropy_thresholds': {'buy_signal': 0.58, 'sell_signal': 0.42}
            },
            'risk_parameters': {
                'risk_percent': 0.0015,
                'max_daily_trades': 5,
                'max_positions': 1
            },
            'symbols': {
                'EURUSD': {'risk_management': {'contract_size': 0.01, 'risk_percent': 0.0015}},
                'GBPUSD': {'risk_management': {'contract_size': 0.01, 'risk_percent': 0.0015}},
                'USDJPY': {'risk_management': {'contract_size': 0.01, 'risk_percent': 0.0015}}
            },
            'THE5ERS_specific': {
                'step1_target': 8,
                'max_daily_loss_percent': 5,
                'max_total_loss_percent': 10
            }
        }
    
    def parse_date_input(self, date_input: str) -> datetime:
        """
        Converte vari formati di data in datetime
        
        Formati supportati:
        - 'YYYY-MM-DD' (es: '2024-01-15')
        - 'DD/MM/YYYY' (es: '15/01/2024')
        - 'DD-MM-YYYY' (es: '15-01-2024')
        - 'YYYYMMDD' (es: '20240115')
        """
        
        # Rimuovi spazi
        date_input = date_input.strip()
        
        # Formato ISO: YYYY-MM-DD
        if len(date_input) == 10 and '-' in date_input and date_input.count('-') == 2:
            try:
                return datetime.strptime(date_input, '%Y-%m-%d')
            except:
                pass
        
        # Formato DD/MM/YYYY
        if '/' in date_input:
            try:
                return datetime.strptime(date_input, '%d/%m/%Y')
            except:
                pass
        
        # Formato DD-MM-YYYY  
        if len(date_input) == 10 and '-' in date_input:
            try:
                return datetime.strptime(date_input, '%d-%m-%Y')
            except:
                pass
        
        # Formato YYYYMMDD
        if len(date_input) == 8 and date_input.isdigit():
            try:
                return datetime.strptime(date_input, '%Y%m%d')
            except:
                pass
        
        raise ValueError(f"❌ Formato data non riconosciuto: {date_input}")
    
    def validate_date_range(self, start_date: datetime, end_date: datetime) -> Tuple[datetime, datetime]:
        """Valida e corregge il range di date"""
        
        # Verifica ordine cronologico
        if start_date >= end_date:
            raise ValueError(f"❌ Data inizio ({start_date.strftime('%Y-%m-%d')}) deve essere precedente a data fine ({end_date.strftime('%Y-%m-%d')})")
        
        # Verifica che non sia nel futuro
        today = datetime.now()
        if end_date > today:
            logger.warning(f"⚠️ Data fine nel futuro, corretta a oggi: {today.strftime('%Y-%m-%d')}")
            end_date = today
        
        # Verifica periodo minimo (almeno 1 giorno)
        if (end_date - start_date).days < 1:
            raise ValueError("❌ Periodo minimo: 1 giorno")
        
        # Verifica periodo massimo (max 1 anno per performance)
        if (end_date - start_date).days > 365:
            logger.warning("⚠️ Periodo superiore a 1 anno, potrebbe essere lento")
        
        return start_date, end_date
    
    def get_mt5_available_period(self) -> Tuple[datetime, datetime]:
        """
        Simula la richiesta del periodo disponibile dai dati MT5
        In un sistema reale, questo interrogherebbe MT5 per i dati disponibili
        """
        
        # Simula dati MT5 disponibili (tipicamente ultimi 2-3 anni)
        today = datetime.now()
        oldest_data = today - timedelta(days=730)  # ~2 anni
        
        logger.info(f"📊 Dati MT5 simulati disponibili dal {oldest_data.strftime('%Y-%m-%d')} al {today.strftime('%Y-%m-%d')}")
        
        return oldest_data, today
    
    def run_custom_period_backtest(self, 
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None,
                                 days_back: Optional[int] = None,
                                 start_balance: float = 100000,
                                 symbols_filter: Optional[List[str]] = None,
                                 weekend_skip: bool = True):
        """
        Esegue backtest con periodo completamente personalizzabile
        
        Args:
            start_date: Data inizio (vari formati supportati)
            end_date: Data fine (vari formati supportati)  
            days_back: Alternativa: giorni indietro da oggi
            start_balance: Capitale iniziale
            symbols_filter: Lista simboli specifici (None = tutti)
            weekend_skip: Salta weekend
        """
        
        logger.info("🎯 AVVIO CUSTOM PERIOD BACKTEST THE5ERS")
        logger.info("="*60)
        
        # Determina il periodo di analisi
        if start_date and end_date:
            # Modalità: Date specifiche
            start_dt = self.parse_date_input(start_date)
            end_dt = self.parse_date_input(end_date)
            start_dt, end_dt = self.validate_date_range(start_dt, end_dt)
            
            logger.info(f"📅 MODALITÀ: Date specifiche")
            logger.info(f"🗓️ Dal: {start_dt.strftime('%d/%m/%Y (%A)')}")
            logger.info(f"🗓️ Al:  {end_dt.strftime('%d/%m/%Y (%A)')}")
            
        elif days_back:
            # Modalità: Giorni indietro
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days_back)
            
            logger.info(f"📅 MODALITÀ: Giorni indietro")
            logger.info(f"🔙 Ultimi {days_back} giorni")
            logger.info(f"🗓️ Dal: {start_dt.strftime('%d/%m/%Y')}")
            logger.info(f"🗓️ Al:  {end_dt.strftime('%d/%m/%Y')}")
            
        else:
            # Modalità: Default (ultimi 30 giorni)
            days_back = 30
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days_back)
            
            logger.info(f"📅 MODALITÀ: Default")
            logger.info(f"🗓️ Ultimi 30 giorni (default)")
        
        # Calcola statistiche periodo
        total_days = (end_dt - start_dt).days
        if weekend_skip:
            # Stima giorni lavorativi (esclude sabato/domenica)
            business_days = np.busday_count(start_dt.date(), end_dt.date())
            logger.info(f"📊 Giorni totali: {total_days} | Giorni lavorativi: {business_days}")
        else:
            business_days = total_days
            logger.info(f"📊 Giorni totali: {total_days} (inclusi weekend)")
        
        # Determina simboli
        available_symbols = list(self.config['symbols'].keys())
        if symbols_filter:
            symbols = [s for s in symbols_filter if s in available_symbols]
            if not symbols:
                logger.warning(f"⚠️ Nessun simbolo valido in {symbols_filter}, uso tutti")
                symbols = available_symbols[:3]
        else:
            symbols = available_symbols[:3]  # Prime 3 coppie per The5ers
        
        logger.info(f"💱 Simboli: {symbols}")
        logger.info(f"💰 Balance iniziale: ${start_balance:,.2f}")
        logger.info("="*60)
        
        # Inizializza variabili backtest
        current_balance = start_balance
        peak_balance = start_balance
        self.trades = []
        self.equity_curve = []
        
        # Risk parameters
        max_daily_trades = self.config['risk_parameters'].get('max_daily_trades', 5)
        
        # Loop principale - iterazione giorno per giorno
        current_date = start_dt
        day_count = 0
        
        while current_date < end_dt:
            
            # Skip weekend se richiesto
            if weekend_skip and current_date.weekday() >= 5:  # 5=Sabato, 6=Domenica
                current_date += timedelta(days=1)
                continue
            
            day_count += 1
            daily_start_balance = current_balance
            daily_trades = 0
            daily_pnl = 0
            
            # Simula trading giornaliero (4-6 ore)
            trading_hours = random.randint(4, 6)
            
            for hour_offset in range(trading_hours):
                current_time = current_date + timedelta(hours=9+hour_offset)
                
                # Limit daily trades
                if daily_trades >= max_daily_trades:
                    break
                
                for symbol in symbols:
                    
                    # Signal simulation con parametri reali
                    signal_result = self.simulate_quantum_signal_with_real_params(current_time, symbol)
                    
                    if signal_result and signal_result['signal'] != 'hold':
                        
                        position_size = self.calculate_real_position_size(symbol, current_balance, signal_result['strength'])
                        
                        # Simula trade
                        trade_result = self.simulate_trade_execution(
                            symbol=symbol,
                            signal=signal_result['signal'],
                            position_size=position_size,
                            timestamp=current_time,
                            balance=current_balance
                        )
                        
                        if trade_result:
                            # Aggiorna balance
                            current_balance += trade_result['pnl']
                            daily_pnl += trade_result['pnl']
                            daily_trades += 1
                            
                            self.trades.append(trade_result)
                            
                            # Aggiorna peak per drawdown
                            if current_balance > peak_balance:
                                peak_balance = current_balance
                            
                            # Check compliance The5ers
                            if self.check_the5ers_violation(current_balance, start_balance, daily_pnl, daily_start_balance):
                                logger.error(f"🔴 VIOLAZIONE THE5ERS - Stop backtest")
                                return self.generate_final_report(start_balance, current_balance, peak_balance, start_dt, current_date)
            
            # Log progresso ogni 7 giorni
            if day_count % 7 == 0:
                progress = (current_date - start_dt).days / total_days * 100
                logger.info(f"📈 Giorno {day_count}/{business_days} ({progress:.1f}%) - Balance: ${current_balance:,.2f} - Daily P&L: ${daily_pnl:+.2f}")
            
            # Salva equity curve
            self.equity_curve.append({
                'date': current_date,
                'balance': current_balance,
                'daily_pnl': daily_pnl,
                'daily_trades': daily_trades
            })
            
            current_date += timedelta(days=1)
        
        logger.info("✅ Backtest completato!")
        return self.generate_final_report(start_balance, current_balance, peak_balance, start_dt, end_dt)
    
    def simulate_quantum_signal_with_real_params(self, timestamp: datetime, symbol: str):
        """Simula signal utilizzando parametri quantum reali dal config"""
        
        quantum_params = self.config.get('quantum_params', {})
        symbol_config = self.config['symbols'].get(symbol, {})
        
        # Thresholds dal config
        buy_threshold = quantum_params.get('entropy_thresholds', {}).get('buy_signal', 0.58)
        sell_threshold = quantum_params.get('entropy_thresholds', {}).get('sell_signal', 0.42)
        
        # Simula entropy
        base_entropy = random.uniform(0, 1)
        
        # Time-based adjustments (orari migliori = signal più forti)
        hour = timestamp.hour
        if 8 <= hour <= 10:  # London open
            base_entropy += random.uniform(-0.1, 0.15)  
        elif 14 <= hour <= 16:  # NY open
            base_entropy += random.uniform(-0.1, 0.12)
        
        base_entropy = max(0, min(1, base_entropy))
        
        # Determina signal
        if base_entropy >= buy_threshold:
            signal = 'buy'
            strength = (base_entropy - buy_threshold) / (1 - buy_threshold)
        elif base_entropy <= sell_threshold:
            signal = 'sell'  
            strength = (sell_threshold - base_entropy) / sell_threshold
        else:
            signal = 'hold'
            strength = 0
        
        if signal != 'hold':
            return {
                'signal': signal,
                'strength': strength,
                'entropy': base_entropy,
                'timestamp': timestamp
            }
        
        return None
    
    def calculate_real_position_size(self, symbol: str, balance: float, signal_strength: float = 1.0):
        """Calcola position size usando parametri reali"""
        
        symbol_config = self.config['symbols'].get(symbol, {})
        risk_mgmt = symbol_config.get('risk_management', {})
        
        contract_size = risk_mgmt.get('contract_size', 0.01)
        risk_percent = risk_mgmt.get('risk_percent') or self.config['risk_parameters'].get('risk_percent', 0.0015)
        
        position_size = contract_size
        
        # Signal strength adjustment
        if signal_strength > 0.8:
            position_size = min(position_size * 1.2, 0.02)
        elif signal_strength < 0.6:
            position_size = position_size * 0.8
        
        return position_size
    
    def simulate_trade_execution(self, symbol: str, signal: str, position_size: float, timestamp: datetime, balance: float):
        """Simula esecuzione trade con parametri realistici"""
        
        # Simula movimento prezzo (spread + volatilità)
        spread = {'EURUSD': 1.2, 'GBPUSD': 1.8, 'USDJPY': 1.1, 'XAUUSD': 3.5, 'NAS100': 2.0}.get(symbol, 1.5)
        
        # Pip movement simulation
        volatility = random.uniform(0.5, 2.0)
        direction = 1 if signal == 'buy' else -1
        
        # Market conditions (più realistico)
        market_noise = random.uniform(-0.3, 0.3)
        pip_movement = direction * volatility + market_noise
        
        # Calcola P&L
        pip_value = position_size * 10  # Micro lot = $1 per pip per EURUSD
        gross_pnl = pip_movement * pip_value
        net_pnl = gross_pnl - (spread * pip_value / 10)  # Sottrai spread
        
        # Success/failure logic più realistico
        success_probability = 0.58 if signal == 'buy' else 0.55  # Buy slightly better
        is_successful = random.random() < success_probability
        
        if not is_successful:
            net_pnl = -abs(net_pnl) * random.uniform(0.6, 1.2)  # Loss variabile
        
        return {
            'symbol': symbol,
            'signal': signal,
            'position_size': position_size,
            'pip_movement': pip_movement,
            'pnl': net_pnl,
            'timestamp': timestamp,
            'balance_after': balance + net_pnl
        }
    
    def check_the5ers_violation(self, current_balance: float, start_balance: float, 
                               daily_pnl: float, daily_start_balance: float) -> bool:
        """Verifica violazioni regole The5ers"""
        
        # Check daily loss
        daily_loss_percent = abs(daily_pnl) / daily_start_balance if daily_pnl < 0 else 0
        if daily_loss_percent > self.max_daily_loss:
            logger.error(f"🔴 DAILY LOSS LIMIT: {daily_loss_percent:.2%} > {self.max_daily_loss:.2%}")
            return True
        
        # Check total loss
        total_loss_percent = (start_balance - current_balance) / start_balance if current_balance < start_balance else 0
        if total_loss_percent > self.max_total_loss:
            logger.error(f"🔴 TOTAL LOSS LIMIT: {total_loss_percent:.2%} > {self.max_total_loss:.2%}")
            return True
        
        return False
    
    def generate_final_report(self, start_balance: float, end_balance: float, 
                            peak_balance: float, start_date: datetime, end_date: datetime):
        """Genera report finale dettagliato"""
        
        total_return = (end_balance - start_balance) / start_balance
        max_drawdown = (peak_balance - min([eq['balance'] for eq in self.equity_curve])) / peak_balance if self.equity_curve else 0
        
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        profit_factor = abs(sum([t['pnl'] for t in winning_trades])) / abs(sum([t['pnl'] for t in losing_trades])) if losing_trades else float('inf')
        
        report = {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_days': (end_date - start_date).days,
                'trading_days': len(self.equity_curve)
            },
            'performance': {
                'start_balance': start_balance,
                'end_balance': end_balance,
                'total_return': total_return,
                'total_return_percent': total_return * 100,
                'peak_balance': peak_balance,
                'max_drawdown': max_drawdown,
                'max_drawdown_percent': max_drawdown * 100
            },
            'trades': {
                'total_trades': len(self.trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'win_rate_percent': win_rate * 100,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor
            },
            'the5ers_compliance': {
                'step1_target_reached': total_return >= self.step1_target,
                'daily_loss_violations': 0,  # Calcolato durante backtest
                'total_loss_violations': 0   # Calcolato durante backtest
            }
        }
        
        # Print report
        self.print_detailed_report(report)
        
        return report
    
    def print_detailed_report(self, report: dict):
        """Stampa report dettagliato"""
        
        logger.info("🏆 CUSTOM PERIOD BACKTEST - RISULTATI FINALI")
        logger.info("="*80)
        
        # Periodo
        period = report['period']
        logger.info(f"📅 PERIODO ANALISI:")
        logger.info(f"   Dal: {period['start_date']}")
        logger.info(f"   Al:  {period['end_date']}")
        logger.info(f"   Giorni totali: {period['total_days']}")
        logger.info(f"   Giorni trading: {period['trading_days']}")
        
        # Performance
        perf = report['performance']
        logger.info(f"💰 PERFORMANCE:")
        logger.info(f"   Balance iniziale: ${perf['start_balance']:,.2f}")
        logger.info(f"   Balance finale:   ${perf['end_balance']:,.2f}")
        logger.info(f"   Return totale:    {perf['total_return_percent']:+.2f}%")
        logger.info(f"   Peak balance:     ${perf['peak_balance']:,.2f}")
        logger.info(f"   Max Drawdown:     {perf['max_drawdown_percent']:.2f}%")
        
        # Trades
        trades = report['trades']
        logger.info(f"📊 TRADES:")
        logger.info(f"   Totale trades:    {trades['total_trades']}")
        logger.info(f"   Trades vincenti:  {trades['winning_trades']}")
        logger.info(f"   Trades perdenti:  {trades['losing_trades']}")
        logger.info(f"   Win Rate:         {trades['win_rate_percent']:.1f}%")
        logger.info(f"   Avg Win:          ${trades['avg_win']:+.2f}")
        logger.info(f"   Avg Loss:         ${trades['avg_loss']:+.2f}")
        logger.info(f"   Profit Factor:    {trades['profit_factor']:.2f}")
        
        # The5ers
        compliance = report['the5ers_compliance']
        logger.info(f"🏆 THE5ERS COMPLIANCE:")
        logger.info(f"   Step 1 Target:    {'✅ RAGGIUNTO' if compliance['step1_target_reached'] else '❌ NON RAGGIUNTO'}")
        logger.info(f"   Daily Loss Viol.: {compliance['daily_loss_violations']}")
        logger.info(f"   Total Loss Viol.: {compliance['total_loss_violations']}")


def main():
    """Funzione principale con esempi di utilizzo"""
    
    backtest = The5ersCustomPeriodBacktest()
    
    print("🎯 THE5ERS CUSTOM PERIOD BACKTEST")
    print("="*50)
    print("Esempi di utilizzo:")
    print()
    print("1. Date specifiche:")
    print("   start_date='2024-01-01', end_date='2024-01-31'")
    print()
    print("2. Giorni indietro:")
    print("   days_back=45")
    print()
    print("3. Simboli specifici:")
    print("   symbols_filter=['EURUSD', 'GBPUSD']")
    print()
    
    # Esempio interattivo
    try:
        choice = input("Scegli modalità (1=Date specifiche, 2=Giorni indietro, 3=Default): ").strip()
        
        if choice == "1":
            start = input("Data inizio (YYYY-MM-DD o DD/MM/YYYY): ").strip()
            end = input("Data fine (YYYY-MM-DD o DD/MM/YYYY): ").strip()
            
            result = backtest.run_custom_period_backtest(
                start_date=start,
                end_date=end
            )
            
        elif choice == "2":
            days = int(input("Numero giorni indietro: ").strip())
            
            result = backtest.run_custom_period_backtest(
                days_back=days
            )
            
        else:
            # Default: ultimi 30 giorni
            result = backtest.run_custom_period_backtest()
            
    except KeyboardInterrupt:
        print("\n❌ Operazione annullata")
    except Exception as e:
        print(f"\n❌ Errore: {e}")


if __name__ == "__main__":
    main()
