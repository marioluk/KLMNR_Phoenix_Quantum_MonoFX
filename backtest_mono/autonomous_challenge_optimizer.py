import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional, Any
import itertools
import time


# =============================================================
# CORRELAZIONE TRA TIPOLOGIA DI TRADING E PARAMETRI SL/TP/TS
# =============================================================
# | Tipologia   | Stop Loss (SL)         | Take Profit (TP)         | Trailing Stop (TS)                | Note operative                       |
# |-------------|------------------------|--------------------------|------------------------------------|--------------------------------------|
# | Scalping    | 6-12 pips (molto stretto) | 10-20 pips (stretto)      | Attivazione rapida, step piccoli   | Protezione immediata, trade brevi    |
# | Intraday    | 15-30 pips (medio)     | 30-60 pips (medio)       | Attivazione media, step medi       | Nessuna posizione overnight          |
# | Swing       | 50-120 pips (ampio)    | 100-250 pips (ampio)     | Attivazione solo dopo movimenti ampi, step larghi | Posizioni multi-day, oscillazioni ampie |
# | Position    | 150-400 pips (molto ampio) | 300-800 pips (molto ampio) | Attivazione tardiva, step molto larghi | Segue trend di fondo, trade lunghi   |
#
# Questi parametri sono definiti nei preset di get_trading_mode_params e ottimizzati dinamicamente in optimize_symbol_parameters.
# La funzione calculate_sl_tp_with_volatility calcola SL/TP in base alla volatilità del simbolo:
#   - SL = max(base_sl * volatility_factor, min_sl)
#   - TP = SL * profit_multiplier
# Il trailing stop viene configurato per ogni tipologia e simbolo, con step e attivazione coerenti con l'orizzonte temporale.
#
# Esempio di calcolo nel codice:
#   sl_pips, tp_pips = self.calculate_sl_tp_with_volatility(symbol, base_sl, min_sl, profit_multiplier, volatility)
#   trailing_stop = {"enable": True, "activation_pips": ..., "step_pips": ..., "lock_percentage": ...}
#
# Tutta la logica di ottimizzazione garantisce che i parametri siano coerenti con la tipologia di trading selezionata.
# =============================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class AutonomousHighStakesOptimizer:
    def validate_trading_params(self, params: dict, mode: str, log_file: str = None) -> list:
        """
        Valida i parametri di trading rispetto alla tipologia selezionata.
        Restituisce una lista di warning/suggerimenti.
        Se log_file è fornito, scrive i warning anche su file.
        """
        warnings = []
        ranges = {
            # Scalping: operatività ultra-veloce su timeframe M1-M5, molti trade al giorno, posizioni di breve durata
            'scalping': {
                'max_position_hours': (0.05, 2),      # Durata posizione: da pochi minuti a max 2 ore
                'buffer_size': (100, 300),            # Storico tick/candele: sufficiente per pattern rapidi
                'spin_window': (10, 30),              # Finestra di calcolo segnali: breve
                'signal_cooldown': (60, 300),         # Attesa tra segnali: da 1 a 5 minuti
                'max_daily_trades': (20, 100)         # Trade giornalieri: molto elevato
            },
            # Intraday: operatività su timeframe M15-H1, nessuna posizione overnight, sfrutta volatilità giornaliera
            'intraday': {
                'max_position_hours': (2, 12),        # Durata posizione: da 2 a 12 ore
                'buffer_size': (300, 800),            # Storico tick/candele: copre l'intera giornata
                'spin_window': (20, 60),              # Finestra di calcolo segnali: media
                'signal_cooldown': (300, 1200),       # Attesa tra segnali: da 5 a 20 minuti
                'max_daily_trades': (5, 20)           # Trade giornalieri: moderato
            },
            # Swing: operatività su timeframe H1-D1, posizioni multi-day, coglie oscillazioni ampie
            'swing': {
                'max_position_hours': (24, 96),       # Durata posizione: da 1 a 4 giorni
                'buffer_size': (800, 2000),           # Storico tick/candele: copre settimane
                'spin_window': (40, 120),             # Finestra di calcolo segnali: ampia
                'signal_cooldown': (1200, 3600),      # Attesa tra segnali: da 20 minuti a 1 ora
                'max_daily_trades': (1, 6)            # Trade giornalieri: pochi
            },
            # Position: operatività su timeframe D1-W1, posizioni di lungo periodo, segue trend
            'position': {
                'max_position_hours': (96, 336),      # Durata posizione: da 4 a 14 giorni
                'buffer_size': (1500, 5000),          # Storico tick/candele: copre mesi
                'spin_window': (100, 300),            # Finestra di calcolo segnali: molto ampia
                'signal_cooldown': (3600, 14400),     # Attesa tra segnali: da 1 a 4 ore
                'max_daily_trades': (1, 2)            # Trade giornalieri: rarissimi
            }
        }
        ref = ranges.get(mode, ranges['intraday'])
        for key, (min_val, max_val) in ref.items():
            val = params.get(key)
            if val is not None and not (min_val <= val <= max_val):
                warnings.append(f"Parametro '{key}'={val} fuori range per '{mode}' [{min_val}-{max_val}]")
        # Scrivi su file se richiesto
        if log_file and warnings:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[VALIDAZIONE PARAMETRI - {mode.upper()}] {datetime.now().isoformat()}\n")
                    for w in warnings:
                        f.write(f"  - {w}\n")
            except Exception as e:
                print(f"[VALIDAZIONE PARAMETRI] Errore scrittura log: {e}")
        return warnings
    def generate_optimized_config_for_mode(self, aggressiveness: str, mode: str) -> Dict:
        # Ottieni parametri tipologia trading
        params = self.get_trading_mode_params(mode)
        # Validazione automatica parametri globali
        logs_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, f"log_param_validation_{mode}_{aggressiveness}.log")
        summary_file = os.path.join(logs_dir, f"summary_param_validation_{mode}_{aggressiveness}.log")
        all_warnings = []
        warnings = self.validate_trading_params(params, mode, log_file=log_file)
        if warnings:
            print(f"[VALIDAZIONE PARAMETRI - {mode.upper()}] WARNING:")
            for w in warnings:
                print(f"  - {w}")
            print(f"[VALIDAZIONE PARAMETRI] Log scritto su: {log_file}")
            print(f"❌ Configurazione BLOCCATA: parametri globali fuori range.")
            all_warnings.extend([f"GLOBAL: {w}" for w in warnings])
        config = self.create_base_config_template()
        config['metadata']['trading_mode'] = mode
        config['metadata']['comment'] = params['comment']
        config['metadata']['aggressiveness'] = aggressiveness
        config['risk_parameters']['max_position_hours'] = params['max_position_hours']
        config['risk_parameters']['position_cooldown'] = params['position_cooldown']
        config['risk_parameters']['stop_loss_pips'] = params['stop_loss_pips']
        config['risk_parameters']['take_profit_pips'] = params['take_profit_pips']
        config['quantum_params']['buffer_size'] = params['buffer_size']
        config['quantum_params']['spin_window'] = params['spin_window']
        config['quantum_params']['min_spin_samples'] = params['min_spin_samples']
        config['quantum_params']['signal_cooldown'] = params['signal_cooldown']
        # Applica override aggressività
        config['risk_parameters']['risk_percent'] = 0.005 if aggressiveness == "conservative" else (0.007 if aggressiveness == "moderate" else 0.009)
        config['risk_parameters']['max_daily_trades'] = 4 if aggressiveness == "conservative" else (6 if aggressiveness == "moderate" else 8)
        config['risk_parameters']['max_concurrent_trades'] = 2 if aggressiveness == "conservative" else (3 if aggressiveness == "moderate" else 4)
        # Seleziona simboli ottimali per aggressività
        optimal_symbols = self.select_optimal_symbols(aggressiveness)
        optimized_symbols = {}
        total_score = 0
        spin_thresholds = []
        # Validazione parametri dei singoli simboli
        for symbol in optimal_symbols:
            symbol_params = self.optimize_symbol_parameters(symbol, aggressiveness)
            symbol_warnings = self.validate_trading_params(symbol_params, mode, log_file=log_file)
            if symbol_warnings:
                print(f"[VALIDAZIONE PARAMETRI - {mode.upper()}][{symbol}] WARNING:")
                for w in symbol_warnings:
                    print(f"  - {w}")
                print(f"[VALIDAZIONE PARAMETRI] Log scritto su: {log_file}")
                print(f"❌ Configurazione BLOCCATA: parametri simbolo '{symbol}' fuori range.")
                all_warnings.extend([f"{symbol}: {w}" for w in symbol_warnings])
            # Normalizza spin_threshold tra 0.15 e 1.0
            st = symbol_params.get('spin_threshold', 0.25)
            st = max(0.15, min(float(st), 1.0))
            symbol_params['spin_threshold'] = st
            if 'quantum_params_override' not in symbol_params:
                symbol_params['quantum_params_override'] = {}
            symbol_params['quantum_params_override']['spin_threshold'] = st
            spin_thresholds.append(st)
            optimized_symbols[symbol] = symbol_params
            total_score += symbol_params['optimization_score']
        # Se ci sono warning, blocca la generazione e scrivi riepilogo
        if all_warnings:
            print("\n===== RIEPILOGO WARNING PARAMETRI TROVATI =====")
            for w in all_warnings:
                print(f"  - {w}")
            try:
                with open(summary_file, "a", encoding="utf-8") as f:
                    f.write(f"[RIEPILOGO PARAMETRI - {mode.upper()} - {aggressiveness}] {datetime.now().isoformat()}\n")
                    for w in all_warnings:
                        f.write(f"  - {w}\n")
            except Exception as e:
                print(f"[RIEPILOGO PARAMETRI] Errore scrittura log: {e}")
            raise ValueError(f"Parametri fuori range: {all_warnings}")
        config['symbols'] = optimized_symbols
        config['pip_size_map'] = {
            "EURUSD": 0.0001,
            "GBPUSD": 0.0001,
            "USDJPY": 0.01,
            "USDCHF": 0.0001,
            "AUDUSD": 0.0001,
            "USDCAD": 0.0001,
            "NZDUSD": 0.0001,
            "BTCUSD": 0.01,
            "ETHUSD": 0.01,
            "XAUUSD": 0.1,
            "XAGUSD": 0.01,
            "SP500": 0.1,
            "NAS100": 0.1,
            "US30": 0.1,
            "DAX40": 0.1,
            "FTSE100": 0.1,
            "JP225": 1.0,
            "default": 0.0001
        }
        if spin_thresholds:
            config['quantum_params']['spin_threshold'] = round(sum(spin_thresholds) / len(spin_thresholds), 3)
        else:
            config['quantum_params']['spin_threshold'] = 0.25
        avg_score = total_score / len(optimal_symbols)
        config['quantum_params']['adaptive_threshold'] = 0.60 + (avg_score / 200)
        config['quantum_params']['volatility_filter'] = 0.70 + (avg_score / 300)
        config['quantum_params']['confluence_threshold'] = 0.65 + (avg_score / 250)
        config['optimization_results'] = {
            'aggressiveness_level': aggressiveness,
            'symbols_count': len(optimal_symbols),
            'average_optimization_score': round(avg_score, 2),
            'total_optimization_score': round(total_score, 2),
            'optimization_period': f"{self.optimization_days} days",
            'optimization_timestamp': datetime.now().isoformat()
        }
        return config
    # =============================
    # Tipologie di Trading per Timeframe
    # =============================
    # ... Tutto il codice della classe come da file di produzione ...
    def get_trading_mode_params(self, mode: str) -> dict:
        presets = {
            'scalping': {
                'max_position_hours': 0.5,           # Range valido: 0.05-2
                'max_daily_trades': 30,              # Range valido: 20-100
                'position_cooldown': 120,            # Valore tipico
                'stop_loss_pips': 8,                 # SL stretto
                'take_profit_pips': 15,              # TP stretto
                'buffer_size': 150,                  # Range valido: 100-300
                'spin_window': 15,                   # Range valido: 10-30
                'min_spin_samples': 4,               # Valore tipico
                'signal_cooldown': 120,              # Range valido: 60-300
                'comment': 'Scalping: altissima velocità, molti trade al giorno, spread ridotto'
            },
            'intraday': {
                'max_position_hours': 8,             # Range valido: 2-12
                'max_daily_trades': 10,              # Range valido: 5-20
                'position_cooldown': 900,            # Valore tipico
                'stop_loss_pips': 20,                # SL medio
                'take_profit_pips': 40,              # TP medio
                'buffer_size': 500,                  # Range valido: 300-800
                'spin_window': 40,                   # Range valido: 20-60
                'min_spin_samples': 8,               # Valore tipico
                'signal_cooldown': 600,              # Range valido: 300-1200
                'comment': 'Intraday: nessuna posizione overnight, sfrutta volatilità giornaliera'
            },
            'swing': {
                'max_position_hours': 48,            # Range valido: 24-96
                'max_daily_trades': 3,               # Range valido: 1-6
                'position_cooldown': 7200,           # Valore tipico
                'stop_loss_pips': 80,                # SL ampio
                'take_profit_pips': 180,             # TP ampio
                'buffer_size': 1200,                 # Range valido: 800-2000
                'spin_window': 80,                   # Range valido: 40-120
                'min_spin_samples': 20,              # Valore tipico
                'signal_cooldown': 2400,             # Range valido: 1200-3600
                'comment': 'Swing Trading: coglie oscillazioni di prezzo più ampie'
            },
            'position': {
                'max_position_hours': 168,           # Range valido: 96-336
                'max_daily_trades': 1,               # Range valido: 1-2
                'position_cooldown': 43200,          # Valore tipico
                'stop_loss_pips': 300,               # SL molto ampio
                'take_profit_pips': 600,             # TP molto ampio
                'buffer_size': 2000,                 # Range valido: 1500-5000
                'spin_window': 150,                  # Range valido: 100-300
                'min_spin_samples': 40,              # Valore tipico
                'signal_cooldown': 7200,             # Range valido: 3600-14400
                'comment': 'Position Trading: segue trend di lungo periodo, operatività tranquilla'
            }
        }
        return presets.get(mode, presets['intraday'])

    def generate_mode_config(self, mode: str) -> dict:
        params = self.get_trading_mode_params(mode)
        config = self.create_base_config_template()
        config['metadata']['trading_mode'] = mode
        config['metadata']['comment'] = params['comment']
        config['risk_parameters']['max_position_hours'] = params['max_position_hours']
        config['risk_parameters']['max_daily_trades'] = params['max_daily_trades']
        config['risk_parameters']['position_cooldown'] = params['position_cooldown']
        config['risk_parameters']['stop_loss_pips'] = params['stop_loss_pips']
        config['risk_parameters']['take_profit_pips'] = params['take_profit_pips']
        config['quantum_params']['buffer_size'] = params['buffer_size']
        config['quantum_params']['spin_window'] = params['spin_window']
        config['quantum_params']['min_spin_samples'] = params['min_spin_samples']
        config['quantum_params']['signal_cooldown'] = params['signal_cooldown']
        config['symbols'] = {s: {'enabled': True, 'comment': params['comment']} for s in self.available_symbols[:5]}
        return config

    @staticmethod
    def calculate_sl_tp_with_volatility(symbol: str, base_sl: float, min_sl: float, profit_multiplier: float, volatility: float) -> Tuple[float, float]:
        if symbol in ['XAUUSD', 'XAGUSD', 'SP500', 'NAS100', 'US30']:
            volatility_factor = min(volatility, 1.5)
        else:
            volatility_factor = min(volatility, 1.2)
        buffer_factor = 1.15
        adjusted_sl = base_sl * volatility_factor
        if adjusted_sl <= min_sl * 1.05:
            sl_pips = int(round(min_sl * buffer_factor))
        else:
            sl_pips = int(round(max(adjusted_sl, min_sl)))
        tp_pips = int(round(sl_pips * profit_multiplier))
        return sl_pips, tp_pips

    @staticmethod
    def calculate_normalized_spin(ticks: list) -> float:
        if not ticks or len(ticks) < 3:
            return 0.0
        valid_ticks = [t for t in ticks if t.get('direction', 0) != 0]
        if len(valid_ticks) < 3:
            return 0.0
        positive = sum(1 for t in valid_ticks if t.get('direction', 0) > 0)
        negative = sum(1 for t in valid_ticks if t.get('direction', 0) < 0)
        total = len(valid_ticks)
        raw_spin = (positive - negative) / total
        return raw_spin

    def __init__(self, optimization_days=60, output_dir=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = output_dir or self.base_dir
        self.optimization_days = optimization_days
        self.high_stakes_params = {
            'account_balance': 5000,
            'target_daily_profit': 25,
            'validation_days': 3,
            'daily_loss_limit': 250,
            'leverage': 100,
            'max_daily_loss_percent': 0.05
        }
        self.available_symbols = [
            'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'SP500', 'NAS100', 'US30',
            'BTCUSD', 'ETHUSD', 'XAUUSD'
        ]
        self.param_ranges = {
            'risk_percent': [0.003, 0.005, 0.007, 0.008, 0.010, 0.012],
            'max_daily_trades': [3, 4, 5, 6, 7, 8],
            'max_concurrent_trades': [2, 3, 4],
            'stop_loss_pips': [10, 12, 15, 18, 20, 25],
            'take_profit_pips': [15, 20, 25, 30, 35, 40],
            'signal_threshold': [0.55, 0.60, 0.65, 0.70, 0.75],
            'spin_threshold': [0.15, 0.25, 0.35, 0.5, 0.7, 1.0],
            'volatility_filter': [0.60, 0.65, 0.70, 0.75, 0.80],
            'trend_strength': [0.50, 0.55, 0.60, 0.65, 0.70]
        }
        self.optimized_configs = {}

    def generate_all_configs(self) -> Dict[str, str]:
        levels = ["conservative", "moderate", "aggressive"]
        results = {}
        for level in levels:
            config = self.generate_optimized_config(level)
            filepath = self.save_config(config, level)
            results[level] = filepath
        return results

    def create_base_config_template(self) -> Dict:
        base_config = {
            "metadata": {
                "version": "2.0",
                "created_by": "AutonomousHighStakesOptimizer",
                "creation_date": datetime.now().isoformat(),
                "description": "Configurazione generata autonomamente per High Stakes Challenge",
                "optimization_period_days": self.optimization_days
            },
            "high_stakes_challenge": self.high_stakes_params,
            "trading_algorithm": {
                "name": "phoenix_quantum_monofx_program",
                "version": "2.0",
                "description": "Algoritmo quantum ottimizzato per il broker"
            },
            "quantum_params": {
                "buffer_size": 500,
                "signal_cooldown": 600,
                "adaptive_threshold": 0.65,
                "volatility_filter": 0.75,
                "trend_strength_min": 0.60,
                "confluence_threshold": 0.70,
                "quantum_boost": True,
                "neural_enhancement": True
            },
            "risk_parameters": {
                "risk_percent": 0.007,
                "max_daily_trades": 6,
                "max_concurrent_trades": 3,
                "min_profit_target": 0.015,
                "stop_loss_atr_multiplier": 1.5,
                "take_profit_atr_multiplier": 2.5,
                "daily_loss_limit": 0.05,
                "max_drawdown": 0.08,
                "risk_reward_ratio": 1.8,
                # daily_trade_limit_mode: modalità di conteggio trade giornalieri.
                # "per_symbol": il limite max_daily_trades viene applicato separatamente a ciascun simbolo (es: 6 trade per EURUSD, 6 per USDJPY, ...)
                # "global": il limite max_daily_trades viene applicato come somma totale su tutti i simboli (es: 6 trade totali su tutti i simboli)
                # Modifica questo parametro per cambiare la logica del counter giornaliero.
                "daily_trade_limit_mode": "global"
            },
            "symbols": {},
            "trading_sessions": {
                "london": {"start": "08:00", "end": "17:00", "enabled": True},
                "newyork": {"start": "13:00", "end": "22:00", "enabled": True},
                "tokyo": {"start": "00:00", "end": "09:00", "enabled": False},
                "sydney": {"start": "22:00", "end": "07:00", "enabled": False}
            },
            "filters": {
                "news_filter": True,
                "spread_filter": True,
                "volatility_filter": True,
                "trend_filter": True,
                "time_filter": True
            }
        }
        return base_config

    def run_parameter_optimization(self, symbol: str, days: int = 30) -> Dict:
        import random, hashlib
        seed_str = f"{symbol}_{days}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        best_params = {}
        best_score = 0
        for risk in self.param_ranges['risk_percent']:
            for trades in self.param_ranges['max_daily_trades']:
                for sl_pips in self.param_ranges['stop_loss_pips']:
                    for tp_pips in self.param_ranges['take_profit_pips']:
                        for signal_th in self.param_ranges['signal_threshold']:
                            for spin_th in self.param_ranges['spin_threshold']:
                                score = self.simulate_backtest_score(
                                    symbol, risk, trades, sl_pips, tp_pips, signal_th, days, spin_th
                                )
                                if score > best_score:
                                    best_score = score
                                    best_params = {
                                        'risk_percent': risk,
                                        'max_daily_trades': trades,
                                        'stop_loss_pips': sl_pips,
                                        'take_profit_pips': tp_pips,
                                        'signal_threshold': signal_th,
                                        'spin_threshold': spin_th,
                                        'score': score
                                    }
        return best_params

    def simulate_backtest_score(self, symbol: str, risk: float, trades: int, sl_pips: int, tp_pips: int, signal_th: float, days: int, spin_th: float) -> float:
        import random
        symbol_characteristics = {
            'EURUSD': {'volatility': 0.7, 'trend': 0.8, 'spread': 1.2},
            'USDJPY': {'volatility': 0.6, 'trend': 0.7, 'spread': 1.5},
            'GBPUSD': {'volatility': 0.8, 'trend': 0.6, 'spread': 2.0},
            'USDCHF': {'volatility': 0.6, 'trend': 0.7, 'spread': 1.8},
            'AUDUSD': {'volatility': 0.7, 'trend': 0.6, 'spread': 2.0},
            'USDCAD': {'volatility': 0.7, 'trend': 0.6, 'spread': 2.0},
            'NZDUSD': {'volatility': 0.9, 'trend': 0.5, 'spread': 2.5},
            'BTCUSD': {'volatility': 3.5, 'trend': 0.4, 'spread': 25.0},
            'ETHUSD': {'volatility': 2.8, 'trend': 0.4, 'spread': 15.0},
            'XAUUSD': {'volatility': 1.5, 'trend': 0.5, 'spread': 3.5},
            'XAGUSD': {'volatility': 2.0, 'trend': 0.4, 'spread': 4.0},
            'SP500': {'volatility': 1.2, 'trend': 0.7, 'spread': 1.5},
            'NAS100': {'volatility': 1.8, 'trend': 0.7, 'spread': 5.0},
            'US30': {'volatility': 1.5, 'trend': 0.6, 'spread': 6.0},
            'DAX40': {'volatility': 1.4, 'trend': 0.7, 'spread': 2.5},
            'FTSE100': {'volatility': 1.1, 'trend': 0.6, 'spread': 2.0},
            'JP225': {'volatility': 1.3, 'trend': 0.6, 'spread': 3.0}
        }
        char = symbol_characteristics.get(symbol, {'volatility': 1.0, 'trend': 0.6, 'spread': 2.5})
        n_ticks = 20
        directions = [random.choice([1, -1]) for _ in range(n_ticks)]
        ticks = [{'direction': d} for d in directions]
        spin = self.calculate_normalized_spin(ticks)
        # Simula la logica di filtro come nello script principale
        confidence = 1.0  # semplificazione, puoi raffinare se vuoi
        buy_condition = spin > spin_th * confidence and signal_th > 0.5
        sell_condition = spin < -spin_th * confidence and signal_th < 0.5
        # Penalizza se non si generano mai segnali
        if not (buy_condition or sell_condition):
            return 0.0
        rr_ratio = tp_pips / sl_pips if sl_pips > 0 else 2.0
        optimal_risk = 0.007
        risk_penalty = abs(risk - optimal_risk) * 10
        base_win_rate = 0.65 + (signal_th - 0.6) * 0.3 - risk_penalty
        win_rate = max(0.4, min(0.85, base_win_rate + random.uniform(-0.1, 0.1)))
        avg_win = tp_pips * char['trend']
        avg_loss = sl_pips
        profit_factor = (win_rate * avg_win) / ((1 - win_rate) * avg_loss) if avg_loss > 0 else 1.0
        trade_penalty = max(0, (trades - 6) * 0.1)
        spread_penalty = char['spread'] * 0.02
        score = (profit_factor * win_rate * (1 - trade_penalty - spread_penalty)) * 100
        return max(0, score)

    def optimize_trading_hours(self, symbol: str, score: float) -> list:
        base_windows = {
            'EURUSD': ["09:00-10:30", "14:00-16:00"],
            'USDJPY': ["08:00-09:30", "13:00-15:00"],
            'GBPUSD': ["10:00-12:00"],
            'USDCHF': ["09:00-11:00"],
            'AUDUSD': ["22:00-23:30"],
            'USDCAD': ["14:00-16:00"],
            'NZDUSD': ["21:00-22:30"],
            'BTCUSD': ["00:00-23:59"],
            'ETHUSD': ["00:00-23:59"],
            'XAUUSD': ["13:00-15:00", "16:00-18:00"],
            'XAGUSD': ["13:00-15:00"],
            'SP500': ["15:30-22:00"],
            'NAS100': ["15:30-22:00"],
            'US30': ["15:30-22:00"],
            'DAX40': ["09:00-17:30"],
            'FTSE100': ["09:00-17:30"],
            'JP225': ["02:00-08:00"]
        }
        windows = base_windows.get(symbol, ["14:00-16:00"])
        if score > 80:
            if symbol in ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]:
                windows = ["08:00-12:00", "13:00-17:00", "18:00-20:00"]
            elif symbol in ["SP500", "NAS100", "US30"]:
                windows = ["15:00-22:00", "13:00-14:30"]
            elif symbol in ["BTCUSD", "ETHUSD"]:
                windows = ["00:00-23:59"]
        elif score < 55:
            windows = [w.split('-')[0] + '-' + (str(int(w.split('-')[0][:2])+1).zfill(2)+":00") for w in windows]
        return windows

    def optimize_symbol_parameters(self, symbol: str, aggressiveness: str) -> Dict:
        base_params = self.run_parameter_optimization(symbol, self.optimization_days)
        aggressiveness_multipliers = {
            'conservative': {'risk': 0.8, 'trades': 0.8, 'sl': 1.2, 'tp': 0.9, 'signal': 1.1},
            'moderate': {'risk': 1.0, 'trades': 1.0, 'sl': 1.0, 'tp': 1.0, 'signal': 1.0},
            'aggressive': {'risk': 1.3, 'trades': 1.2, 'sl': 0.8, 'tp': 1.2, 'signal': 0.9}
        }
        multipliers = aggressiveness_multipliers.get(aggressiveness, aggressiveness_multipliers['moderate'])
        symbol_characteristics = {
            'EURUSD': {'volatility': 0.7},
            'USDJPY': {'volatility': 0.6},
            'GBPUSD': {'volatility': 0.8},
            'USDCHF': {'volatility': 0.6},
            'AUDUSD': {'volatility': 0.7},
            'USDCAD': {'volatility': 0.7},
            'NZDUSD': {'volatility': 0.9},
            'BTCUSD': {'volatility': 3.5},
            'ETHUSD': {'volatility': 2.8},
            'XAUUSD': {'volatility': 1.5},
            'XAGUSD': {'volatility': 2.0},
            'SP500': {'volatility': 1.2},
            'NAS100': {'volatility': 1.8},
            'US30': {'volatility': 1.5},
            'DAX40': {'volatility': 1.4},
            'FTSE100': {'volatility': 1.1},
            'JP225': {'volatility': 1.3}
        }
        char = symbol_characteristics.get(symbol, {'volatility': 1.0})
        volatility = char['volatility']
        base_sl = base_params['stop_loss_pips'] * multipliers['sl']
        if symbol in ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']:
            min_sl = 250 * multipliers['sl']
        elif symbol in ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225']:
            min_sl = 400 * multipliers['sl']
        elif symbol in ['XAUUSD', 'XAGUSD']:
            min_sl = 800 * multipliers['sl']
        elif symbol in ['BTCUSD', 'ETHUSD']:
            min_sl = 1200 * multipliers['sl']
        else:
            min_sl = 300 * multipliers['sl']
        profit_multiplier = 2.2 * multipliers['tp']
        sl_pips, tp_pips = self.calculate_sl_tp_with_volatility(symbol, base_sl, min_sl, profit_multiplier, volatility)
        score = base_params['score']
        signal_buy_threshold = round(base_params['signal_threshold'] * multipliers['signal'], 3)
        signal_sell_threshold = round((1 - base_params['signal_threshold']) * multipliers['signal'], 3)
        confidence_threshold = round((signal_buy_threshold + (1 - signal_sell_threshold)) / 2, 3)
        optimized_params = {
            'enabled': True,
            'risk_percent': base_params['risk_percent'],
            'lot_size': round(base_params['risk_percent'] * 10, 3),
            'stop_loss_pips': int(sl_pips),
            'take_profit_pips': int(tp_pips),
            'signal_buy_threshold': signal_buy_threshold,
            'signal_sell_threshold': signal_sell_threshold,
            'confidence_threshold': confidence_threshold,
            'spin_threshold': base_params.get('spin_threshold', 0.25),
            'max_spread': self.get_symbol_max_spread(symbol),
            'trading_hours': self.optimize_trading_hours(symbol, score),
            'optimization_score': score,
            'aggressiveness_applied': aggressiveness
        }
        return optimized_params

    def get_symbol_max_spread(self, symbol: str) -> float:
        spread_limits = {
            "EURUSD": 12, 'USDJPY': 10, 'GBPUSD': 15, 'USDCHF': 15,
            'AUDUSD': 3.5, 'USDCAD': 3.5, 'NZDUSD': 4.0,
            'BTCUSD': 250, 'ETHUSD': 150,
            'XAUUSD': 40, 'XAGUSD': 4.0,
            'SP500': 60, 'NAS100': 180, 'US30': 60,
            'DAX40': 2.5, 'FTSE100': 2.0, 'JP225': 3.0
        }
        return spread_limits.get(symbol, 4.0)

    def get_symbol_sessions(self, symbol: str) -> List[str]:
        session_mapping = {
            'EURUSD': ['London', 'NewYork'],
            'USDJPY': ['Tokyo', 'London'],
            'GBPUSD': ['London'],
            'USDCHF': ['London'],
            'AUDUSD': ['Sydney', 'Tokyo'],
            'USDCAD': ['NewYork'],
            'NZDUSD': ['Sydney'],
            'BTCUSD': ['Crypto'],
            'ETHUSD': ['Crypto'],
            'XAUUSD': ['London', 'NewYork'],
            'XAGUSD': ['London'],
            'SP500': ['NewYork'],
            'NAS100': ['NewYork'],
            'US30': ['NewYork'],
            'DAX40': ['Frankfurt'],
            'FTSE100': ['London'],
            'JP225': ['Tokyo']
        }
        return session_mapping.get(symbol, ['London', 'NewYork'])

    def select_optimal_symbols(self, aggressiveness: str) -> List[str]:
        symbol_scores = {}
        for symbol in self.available_symbols:
            params = self.run_parameter_optimization(symbol, 14)
            symbol_scores[symbol] = params['score']
        sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)
        symbol_counts = {
            'conservative': 4,
            'moderate': 5,
            'aggressive': 6
        }
        count = symbol_counts.get(aggressiveness, 5)
        selected = [symbol for symbol, score in sorted_symbols[:count]]
        return selected

    def generate_optimized_config(self, aggressiveness: str) -> Dict:
        config = self.create_base_config_template()
        optimal_symbols = self.select_optimal_symbols(aggressiveness)
        optimized_symbols = {}
        total_score = 0
        for symbol in optimal_symbols:
            symbol_params = self.optimize_symbol_parameters(symbol, aggressiveness)
            optimized_symbols[symbol] = symbol_params
            total_score += symbol_params['optimization_score']
        config['symbols'] = optimized_symbols
        avg_score = total_score / len(optimal_symbols)
        if aggressiveness == 'conservative':
            config['risk_parameters']['risk_percent'] = 0.005
            config['risk_parameters']['max_daily_trades'] = 4
            config['risk_parameters']['max_concurrent_trades'] = 2
        elif aggressiveness == 'moderate':
            config['risk_parameters']['risk_percent'] = 0.007
            config['risk_parameters']['max_daily_trades'] = 6
            config['risk_parameters']['max_concurrent_trades'] = 3
        else:
            config['risk_parameters']['risk_percent'] = 0.009
            config['risk_parameters']['max_daily_trades'] = 8
            config['risk_parameters']['max_concurrent_trades'] = 4
        config['quantum_params']['adaptive_threshold'] = 0.60 + (avg_score / 200)
        config['quantum_params']['volatility_filter'] = 0.70 + (avg_score / 300)
        config['quantum_params']['confluence_threshold'] = 0.65 + (avg_score / 250)
        config['optimization_results'] = {
            'aggressiveness_level': aggressiveness,
            'symbols_count': len(optimal_symbols),
            'average_optimization_score': round(avg_score, 2),
            'total_optimization_score': round(total_score, 2),
            'optimization_period': f"{self.optimization_days} days",
            'optimization_timestamp': datetime.now().isoformat()
        }
        return config

    def save_config(self, config: Dict, aggressiveness: str, base_config_path: str = None) -> str:
        """
        Salva la configurazione generata, includendo tutti i parametri richiesti dal file di produzione e mantenendo i parametri ottimizzati.
        """
        import json
        config_dir = os.path.join(os.path.dirname(self.output_dir), "config")
        os.makedirs(config_dir, exist_ok=True)
        now = datetime.now()
        timestamp_str = now.strftime("%d%m%Y%H%M")
        day = str(now.day)
        month = str(now.month)
        year = str(now.year)[-2:]
        magic_number = int(f"{day}{month}{year}1")
        filename = f"config_autonomous_challenge_{aggressiveness}_production_ready.json"
        filepath = os.path.join(config_dir, filename)

        # Carica parametri di base dal file di configurazione se fornito
        base_conf = {}
        if base_config_path and os.path.exists(base_config_path):
            with open(base_config_path, 'r', encoding='utf-8') as f:
                base_conf = json.load(f)

        def get_param(section, key, default):
            return base_conf.get(section, {}).get(key, default)

        def get_section(section, default):
            return base_conf.get(section, default)

        # --- QUANTUM PARAMS ---
        quantum_params = {
            "buffer_size": config.get("quantum_params", {}).get("buffer_size", 880),
            "spin_window": config.get("quantum_params", {}).get("spin_window", 67),
            "min_spin_samples": config.get("quantum_params", {}).get("min_spin_samples", 23),
            "spin_threshold": config.get("quantum_params", {}).get("spin_threshold", 0.25),
            "signal_cooldown": config.get("quantum_params", {}).get("signal_cooldown", 600),
            "entropy_thresholds": config.get("quantum_params", {}).get("entropy_thresholds", {"buy_signal": 0.54, "sell_signal": 0.46}),
            "volatility_scale": config.get("quantum_params", {}).get("volatility_scale", 4.54)
        }
        # Se ottimizzato, inserisci spin_threshold migliore trovato
        if 'spin_threshold' in config:
            quantum_params['spin_threshold'] = config['spin_threshold']

        # --- RISK PARAMETERS ---
        risk_parameters = {
            #"magic_number": config.get("risk_parameters", {}).get("magic_number", 147251),
            "position_cooldown": config.get("risk_parameters", {}).get("position_cooldown", 900),
            "max_daily_trades": config.get("risk_parameters", {}).get("max_daily_trades", 4),
            "max_positions": config.get("risk_parameters", {}).get("max_positions", 1),
            "min_sl_distance_pips": {
                "EURUSD": 30,
                "GBPUSD": 35,
                "USDJPY": 25,
                "XAUUSD": 150,
                "NAS100": 50,
                "SP500": 15,
                "US30": 30,
                "BTCUSD": 200,
                "ETHUSD": 100,
                "USDCHF": 30,
                "default": 40
            },
            "base_sl_pips": {
                "EURUSD": 50,
                "GBPUSD": 60,
                "USDJPY": 40,
                "XAUUSD": 220,
                "NAS100": 100,
                "SP500": 30,
                "US30": 60,
                "BTCUSD": 400,
                "ETHUSD": 200,
                "USDCHF": 50,
                "default": 80
            },
            "profit_multiplier": config.get("risk_parameters", {}).get("profit_multiplier", 2.2),
            "max_position_hours": config.get("risk_parameters", {}).get("max_position_hours", 6),
            "risk_percent": config.get("risk_parameters", {}).get("risk_percent", 0.005),
            "trailing_stop": config.get("risk_parameters", {}).get("trailing_stop", {"enable": True, "activation_pips": 100, "step_pips": 50, "lock_percentage": 0.5}),
            # Nuovi parametri globali per normalizzazione size e rischio globale
            "target_pip_value": 10.0,
            "max_global_exposure": 50000.0
        }

        # --- SYMBOLS ---
        symbols = {}
        # Parametri di normalizzazione e rischio globale
        # Valori di default robusti, possono essere raffinati in futuro
        default_target_pip_value = 10.0  # USD per pip, normalizzazione P&L
        default_max_global_exposure = 50000.0  # Esposizione massima in USD
        for symbol, params in config.get('symbols', {}).items():
            # Ricostruisci la sezione risk_management per ogni simbolo
            risk_management = {
                "contract_size": params.get("contract_size", 0.01),
                "profit_multiplier": params.get("profit_multiplier", 2.2),
                "risk_percent": params.get("risk_percent", 0.08),
                "trailing_stop": params.get("trailing_stop", {"activation_pips": 24, "step_pips": 12}),
                # Nuovi parametri per normalizzazione size e rischio globale
                "target_pip_value": params.get("target_pip_value", default_target_pip_value),
                "max_global_exposure": params.get("max_global_exposure", default_max_global_exposure)
            }
            # Permetti override dei parametri ottimizzati
            for k in ["contract_size", "min_sl_distance_pips", "base_sl_pips", "profit_multiplier", "risk_percent", "trailing_stop", "target_pip_value", "max_global_exposure"]:
                if k in params:
                    risk_management[k] = params[k]
            # Quantum override
            quantum_override = params.get("quantum_params_override", {})
            for k in ["spin_window", "min_spin_samples", "signal_cooldown", "entropy_thresholds"]:
                if k in params:
                    quantum_override[k] = params[k]
            symbols[symbol] = {
                "risk_management": risk_management,
                "timezone": params.get("timezone", "Europe/Rome"),
                "trading_hours": params.get("trading_hours", ["09:00-10:30", "14:00-16:00"]),
                "comment": params.get("comment", f"Override generato dinamicamente per {symbol} - score {params.get('optimization_score', 0):.2f}"),
                "quantum_params_override": quantum_override
            }

        # --- MAX SPREAD ---
        # Popola sempre max_spread per tutti i simboli selezionati
        max_spread = get_param("risk_parameters", "max_spread", {})
        # Ricava max_spread per ogni simbolo selezionato, fallback 20
        all_symbols = list(config.get('symbols', {}).keys())
        max_spread_dict = {}
        for s in all_symbols:
            val = None
            # 1. Dal config generato
            if s in max_spread:
                val = max_spread[s]
            # 2. Dal params del simbolo
            elif 'max_spread' in config['symbols'][s]:
                val = config['symbols'][s]['max_spread']
            # 3. Dal metodo get_symbol_max_spread
            else:
                val = self.get_symbol_max_spread(s)
            # 4. Fallback
            if val is None:
                val = 20
            max_spread_dict[s] = val
        risk_parameters["max_spread"] = max_spread_dict

        # --- TRAILING STOP ---
        # Assicura che trailing_stop sia sempre presente e coerente
        trailing_stop = get_param("risk_parameters", "trailing_stop", {})
        if not trailing_stop or not isinstance(trailing_stop, dict):
            trailing_stop = {"enable": True, "activation_pips": 100, "step_pips": 50, "lock_percentage": 0.5}
        # Fai merge con eventuali override da config
        trailing_stop_override = config.get("risk_parameters", {}).get("trailing_stop", {})
        if isinstance(trailing_stop_override, dict):
            trailing_stop = {**trailing_stop, **trailing_stop_override}
        risk_parameters["trailing_stop"] = trailing_stop

        # --- PRODUZIONE CONFIG ---
        # Inserisci sempre pip_size_map globale
        config['pip_size_map'] = config.get('pip_size_map', {
            "EURUSD": 0.0001,
            "GBPUSD": 0.0001,
            "USDJPY": 0.01,
            "USDCHF": 0.0001,
            "AUDUSD": 0.0001,
            "USDCAD": 0.0001,
            "NZDUSD": 0.0001,
            "BTCUSD": 0.01,
            "ETHUSD": 0.01,
            "XAUUSD": 0.1,
            "XAGUSD": 0.01,
            "SP500": 0.1,
            "NAS100": 0.1,
            "US30": 0.1,
            "DAX40": 0.1,
            "FTSE100": 0.1,
            "JP225": 1.0,
            "default": 0.0001
        })
        production_config = {
            "logging": {
                "log_file": f"logs/log_autonomous_challenge_{aggressiveness}_production_ready_{timestamp_str}.log",
                "max_size_mb": get_param("logging", "max_size_mb", 50),
                "backup_count": get_param("logging", "backup_count", 7),
                "log_level": get_param("logging", "log_level", "INFO")
            },
            "metatrader5": get_section("metatrader5", {
                "login": 25437097,
                "password": "wkchTWEO_.00",
                "server": "FivePercentOnline-Real",
                "path": "C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe",
                "port": 18889
            }),
            "account_currency": base_conf.get("account_currency", "USD"),
            "magic_number": magic_number,
            "initial_balance": base_conf.get("initial_balance", 5000),
            "quantum_params": quantum_params,
            "risk_parameters": risk_parameters,
            "symbols": symbols,
            "pip_size_map": {
                "EURUSD": 0.0001,
                "GBPUSD": 0.0001,
                "USDJPY": 0.01,
                "USDCHF": 0.0001,
                "XAUUSD": 0.01,
                "XAGUSD": 0.01,
                "SP500": 1.0,
                "NAS100": 1.0,
                "US30": 1.0,
                "BTCUSD": 0.01,
                "ETHUSD": 0.01,
                "default": 0.0001
            },
            "challenge_specific": get_section("challenge_specific", {
                "step1_target": 8,
                "max_daily_loss_percent": 5,
                "max_total_loss_percent": 10,
                "drawdown_protection": {
                    "soft_limit": 0.02,
                    "hard_limit": 0.05
                }
            }),
            "conversion_metadata": {
                "created_by": "AutonomousHighStakesOptimizer",
                "creation_date": datetime.now().isoformat(),
                "aggressiveness": aggressiveness
            }
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"config": production_config}, f, indent=4)
            return filepath
        except Exception as e:
            logger.error(f"❌ Errore salvataggio {filepath}: {e}")
            raise

def main():
    print("🎯 AUTONOMOUS HIGH STAKES OPTIMIZER")
    print("Genera configurazioni ottimizzate DA ZERO senza JSON sorgente")
    print("="*70)

    while True:
        print("\n📋 OPZIONI DISPONIBILI:")
        print("1. 🚀 Genera tutte le configurazioni da zero")
        print("2. 🎯 Genera singola configurazione")
        print("3. ❌ Esci")

        choice = input("\n👉 Scegli opzione (1-3): ").strip()

        try:
            if choice == "1":
                print("\n⚡ Tipologie disponibili:")
                print("1. Scalping")
                print("2. Intraday (Day Trading)")
                print("3. Swing Trading")
                print("4. Position Trading")
                mode_choice = input("� Scegli tipologia (1-4): ").strip()
                mode_map = {
                    "1": "scalping",
                    "2": "intraday",
                    "3": "swing",
                    "4": "position"
                }
                mode = mode_map.get(mode_choice, "intraday")
                days = input("�📅 Giorni per ottimizzazione (default: 60): ").strip()
                optimization_days = int(days) if days.isdigit() else 60
                optimizer = AutonomousHighStakesOptimizer(optimization_days)
                levels = ["conservative", "moderate", "aggressive"]
                print(f"\n🔄 Generazione configurazioni per tipologia '{mode}'...")
                for level in levels:
                    config = optimizer.generate_optimized_config_for_mode(level, mode)
                    filepath = optimizer.save_config(config, f"{level}_{mode}")
                    print(f"   ✅ {level.upper()}: {os.path.basename(filepath)}")
                print("\n📄 Tutte le configurazioni per tipologia trading generate e salvate.")
            elif choice == "2":
                print("\n🎯 Scegli livello aggressività:")
                print("1. 🟢 Conservative")
                print("2. 🟡 Moderate")
                print("3. 🔴 Aggressive")
                level_choice = input("👉 Scegli (1-3): ").strip()
                aggressiveness = {
                    "1": "conservative",
                    "2": "moderate",
                    "3": "aggressive"
                }.get(level_choice, "moderate")
                optimizer = AutonomousHighStakesOptimizer()
                config = optimizer.generate_optimized_config(aggressiveness)
                filepath = optimizer.save_config(config, aggressiveness)
                print(f"✅ Configurazione {aggressiveness} generata e salvata: {os.path.basename(filepath)}")
            elif choice == "3":
                print("Uscita dal programma.")
                break
            else:
                print("❌ Scelta non valida, riprova")
        except Exception as e:
            logger.error(f"❌ Errore: {e}")
            print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
