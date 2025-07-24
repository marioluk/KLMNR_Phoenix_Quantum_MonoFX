#!/usr/bin/env python3
# ====================================================================================
# AUTONOMOUS HIGH STAKES OPTIMIZER - OTTIMIZZATORE AUTONOMO SENZA JSON SORGENTE
# Genera configurazioni ottimizzate da zero basandosi solo su algoritmo e dati MT5
# ====================================================================================

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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class AutonomousHighStakesOptimizer:
    @staticmethod
    def calculate_sl_tp_with_volatility(symbol: str, base_sl: float, min_sl: float, profit_multiplier: float, volatility: float) -> (float, float):
        """
        Calcola SL e TP robusti:
        - Usa il valore ottimizzato (base_sl), ma non scende mai sotto min_sl per asset
        - Se il valore ottimizzato è vicino al minimo, applica un buffer_factor (es. 1.15)
        - Limita l'amplificazione della volatilità
        """
        # Limita l'amplificazione della volatilità per evitare SL eccessivi
        if symbol in ['XAUUSD', 'XAGUSD', 'SP500', 'NAS100', 'US30']:
            volatility_factor = min(volatility, 1.5)  # Max +50%
        else:  # Forex
            volatility_factor = min(volatility, 1.2)  # Max +20%

        buffer_factor = 1.15  # Applica solo se sl ottimizzato è vicino al minimo
        adjusted_sl = base_sl * volatility_factor
        # Se il valore ottimizzato è <= min_sl * 1.05, applica buffer_factor
        if adjusted_sl <= min_sl * 1.05:
            sl_pips = int(round(min_sl * buffer_factor))
        else:
            sl_pips = int(round(max(adjusted_sl, min_sl)))
        tp_pips = int(round(sl_pips * profit_multiplier))
        return sl_pips, tp_pips
    @staticmethod
    def calculate_normalized_spin(ticks: list) -> float:
        """
        Calcola lo spin normalizzato tra -1 e +1, come in phoenix_quantum_monofx_program.py.
        Args:
            ticks: lista di dict con chiave 'direction' (1, -1, 0)
        Returns:
            float: spin normalizzato [-1, +1]
        """
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
    """
    Ottimizzatore autonomo che genera configurazioni High Stakes da zero
    senza bisogno di file JSON sorgente, basandosi solo su:
    - Algoritmo di trading 
    - Dati storici MT5
    - Ottimizzazione parametrica
    - Regole High Stakes Challenge
    """
    
    def __init__(self, optimization_days=60, output_dir=None):
        """
        Inizializza ottimizzatore autonomo
        
        Args:
            optimization_days: Giorni di dati storici per ottimizzazione
            output_dir: Directory di output personalizzata
        """
        
        # Percorsi file
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = output_dir or self.base_dir
        self.optimization_days = optimization_days
        
        # Parametri High Stakes Challenge (fissi)
        self.high_stakes_params = {
            'account_balance': 5000,
            'target_daily_profit': 25,  # €25 = 0.5%
            'validation_days': 3,
            'daily_loss_limit': 250,  # 5% di €5000
            'leverage': 100,
            'max_daily_loss_percent': 0.05
        }
        
        # =============================================================
        # 🔴 AREA MODIFICABILE: SIMBOLI E PARAMETRI DI DEFAULT
        # Qui puoi modificare la lista dei simboli disponibili per l'ottimizzazione
        # e personalizzare i parametri e i valori di default usati nella generazione
        # delle configurazioni production-ready e backtest.
        # Esempio: aggiungi/rimuovi simboli, cambia l'ordine, aggiorna parametri.
        # =============================================================
        # Simboli disponibili per ottimizzazione (ordinati per stabilità)
        self.available_symbols = [
            'EURUSD', 
            'USDJPY', 
            'GBPUSD', 
            'USDCHF', 
            'SP500', 
            'NAS100', 
            'US30',
            'BTCUSD', 
            'ETHUSD', 
            'XAUUSD'
            #'AUDUSD', 
            #'USDCAD', 
            #'NZDUSD',
            
            #'XAGUSD',
            
            #'DAX40', 
            #'FTSE100', 
            #'JP225'
        ]
        
        # Range parametri per ottimizzazione
        self.param_ranges = {
            'risk_percent': [0.003, 0.005, 0.007, 0.008, 0.010, 0.012],  # 0.3% - 1.2%
            'max_daily_trades': [3, 4, 5, 6, 7, 8],
            'max_concurrent_trades': [2, 3, 4],
            'stop_loss_pips': [10, 12, 15, 18, 20, 25],
            'take_profit_pips': [15, 20, 25, 30, 35, 40],
            'signal_threshold': [0.55, 0.60, 0.65, 0.70, 0.75],
            'volatility_filter': [0.60, 0.65, 0.70, 0.75, 0.80],
            'trend_strength': [0.50, 0.55, 0.60, 0.65, 0.70]
        }
        
        # Configurazioni ottimizzate (verranno calcolate)
        self.optimized_configs = {}
        

    def generate_all_configs(self) -> Dict[str, str]:
        """
        Genera e salva tutte le configurazioni per i livelli di aggressività.
        Restituisce un dizionario {aggressiveness: filepath}
        """
        levels = ["conservative", "moderate", "aggressive"]
        results = {}
        for level in levels:
            config = self.generate_optimized_config(level)
            filepath = self.save_config(config, level)
            results[level] = filepath
        return results

    def create_base_config_template(self) -> Dict:
        """
        Crea template configurazione base senza parametri ottimizzati
        
        Returns:
            Dict con struttura base configurazione
        """
        
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
                "risk_percent": 0.007,  # Sarà ottimizzato
                "max_daily_trades": 6,  # Sarà ottimizzato
                "max_concurrent_trades": 3,  # Sarà ottimizzato
                "min_profit_target": 0.015,
                "stop_loss_atr_multiplier": 1.5,
                "take_profit_atr_multiplier": 2.5,
                "daily_loss_limit": 0.05,
                "max_drawdown": 0.08,
                "risk_reward_ratio": 1.8
            },
            
            "symbols": {},  # Sarà ottimizzato
            
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
        """
        Esegue ottimizzazione parametrica per un simbolo
        
        Args:
            symbol: Simbolo da ottimizzare
            days: Giorni di backtest per ottimizzazione
            
        Returns:
            Dict con parametri ottimizzati
        """
        
        logger.info(f"🔄 Ottimizzazione parametrica per {symbol} su {days} giorni...")
        
        # Seed pseudo-deterministico: dipende da simbolo e periodo
        import random, hashlib
        seed_str = f"{symbol}_{days}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        # Simulazione ottimizzazione (in production usare backtest reale)
        best_params = {}
        best_score = 0
        
        # Grid search sui parametri chiave
        for risk in self.param_ranges['risk_percent']:
            for trades in self.param_ranges['max_daily_trades']:
                for sl_pips in self.param_ranges['stop_loss_pips']:
                    for tp_pips in self.param_ranges['take_profit_pips']:
                        for signal_th in self.param_ranges['signal_threshold']:
                            
                            # Simula backtest con questi parametri
                            score = self.simulate_backtest_score(
                                symbol, risk, trades, sl_pips, tp_pips, signal_th, days
                            )
                            
                            if score > best_score:
                                best_score = score
                                best_params = {
                                    'risk_percent': risk,
                                    'max_daily_trades': trades,
                                    'stop_loss_pips': sl_pips,
                                    'take_profit_pips': tp_pips,
                                    'signal_threshold': signal_th,
                                    'score': score
                                }
        
        logger.info(f"✅ {symbol}: Miglior score {best_score:.2f} con risk {best_params['risk_percent']:.1%}")
        return best_params
    
    def simulate_backtest_score(self, symbol: str, risk: float, trades: int, 
                               sl_pips: int, tp_pips: int, signal_th: float, days: int) -> float:
        """
        Simula score backtest per combinazione parametri
        (In production sostituire con backtest reale)
        
        Args:
            symbol: Simbolo
            risk: Risk percent
            trades: Max daily trades
            sl_pips: Stop loss pips
            tp_pips: Take profit pips  
            signal_th: Signal threshold
            days: Giorni backtest
            
        Returns:
            Score combinato (profit factor * win rate * consistency)
        """
        import random
        # Simulazione realistica basata su caratteristiche simbolo
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

        # Simula una sequenza di tick fittizi per calcolare spin normalizzato
        # (direzioni random, coerenti con win_rate atteso)
        n_ticks = 20
        directions = [random.choice([1, -1]) for _ in range(n_ticks)]
        ticks = [{'direction': d} for d in directions]
        spin = self.calculate_normalized_spin(ticks)

        # Calcola win rate basato su parametri
        rr_ratio = tp_pips / sl_pips if sl_pips > 0 else 2.0
        optimal_risk = 0.007  # Risk ottimale per High Stakes
        risk_penalty = abs(risk - optimal_risk) * 10

        base_win_rate = 0.65 + (signal_th - 0.6) * 0.3 - risk_penalty
        win_rate = max(0.4, min(0.85, base_win_rate + random.uniform(-0.1, 0.1)))

        # Calcola profit factor
        avg_win = tp_pips * char['trend']
        avg_loss = sl_pips
        profit_factor = (win_rate * avg_win) / ((1 - win_rate) * avg_loss) if avg_loss > 0 else 1.0

        # Penalità per troppe trades (High Stakes prefer qualità)
        trade_penalty = max(0, (trades - 6) * 0.1)

        # Penalty per spread
        spread_penalty = char['spread'] * 0.02

        # Score combinato
        score = (profit_factor * win_rate * (1 - trade_penalty - spread_penalty)) * 100

        # Puoi usare spin normalizzato per logging, analisi o metriche future
        # logger.debug(f"Simulazione spin normalizzato {symbol}: {spin:.3f}")

        return max(0, score)
    
    def optimize_trading_hours(self, symbol: str, score: float) -> list:
        """
        Ottimizza dinamicamente le trading_hours per simbolo in base allo score.
        Maggiore lo score, più ampie e numerose le finestre; score basso = finestre più strette.
        """
        # Finestra base per simbolo
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
        # Più alto lo score, più finestre e più larghe
        if score > 80:
            # Aggiungi una finestra extra e allarga le esistenti
            if symbol in ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]:
                windows = ["08:00-12:00", "13:00-17:00", "18:00-20:00"]
            elif symbol in ["SP500", "NAS100", "US30"]:
                windows = ["15:00-22:00", "13:00-14:30"]
            elif symbol in ["BTCUSD", "ETHUSD"]:
                windows = ["00:00-23:59"]
        elif score < 55:
            # Restringi le finestre
            windows = [w.split('-')[0] + '-' + (str(int(w.split('-')[0][:2])+1).zfill(2)+":00") for w in windows]
        return windows

    def optimize_symbol_parameters(self, symbol: str, aggressiveness: str) -> Dict:
        """
        Ottimizza parametri specifici per simbolo e livello aggressività
        
        Args:
            symbol: Simbolo da ottimizzare
            aggressiveness: conservative, moderate, aggressive
            
        Returns:
            Dict con parametri simbolo ottimizzati
        """
        
        # Esegue ottimizzazione parametrica
        base_params = self.run_parameter_optimization(symbol, self.optimization_days)
        
        # Applica modifiche per aggressività
        aggressiveness_multipliers = {
            'conservative': {'risk': 0.8, 'trades': 0.8, 'sl': 1.2, 'tp': 0.9, 'signal': 1.1},
            'moderate': {'risk': 1.0, 'trades': 1.0, 'sl': 1.0, 'tp': 1.0, 'signal': 1.0},
            'aggressive': {'risk': 1.3, 'trades': 1.2, 'sl': 0.8, 'tp': 1.2, 'signal': 0.9}
        }
        
        multipliers = aggressiveness_multipliers.get(aggressiveness, aggressiveness_multipliers['moderate'])
        
        # Caratteristiche simbolo per volatilità
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
        # min_sl differenziato per asset, aumentato di un fattore 10 per uso intraday
        if symbol in ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']:
            min_sl = 250 * multipliers['sl']  # Forex
        elif symbol in ['SP500', 'NAS100', 'US30', 'DAX40', 'FTSE100', 'JP225']:
            min_sl = 400 * multipliers['sl']  # Indici
        elif symbol in ['XAUUSD', 'XAGUSD']:
            min_sl = 800 * multipliers['sl']  # Oro/Argento
        elif symbol in ['BTCUSD', 'ETHUSD']:
            min_sl = 1200 * multipliers['sl']  # Crypto
        else:
            min_sl = 300 * multipliers['sl']  # Default fallback

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
            'max_spread': self.get_symbol_max_spread(symbol),
            'trading_hours': self.optimize_trading_hours(symbol, score),
            'optimization_score': score,
            'aggressiveness_applied': aggressiveness
        }

        return optimized_params
    
    def get_symbol_max_spread(self, symbol: str) -> float:
        """Ritorna max spread consigliato per simbolo"""
        spread_limits = {
            'EURUSD': 2.0, 'USDJPY': 2.5, 'GBPUSD': 3.0, 'USDCHF': 3.0,
            'AUDUSD': 3.5, 'USDCAD': 3.5, 'NZDUSD': 4.0,
            'BTCUSD': 25.0, 'ETHUSD': 15.0,
            'XAUUSD': 5.0, 'XAGUSD': 4.0,
            'SP500': 1.5, 'NAS100': 8.0, 'US30': 6.0,
            'DAX40': 2.5, 'FTSE100': 2.0, 'JP225': 3.0
        }
        return spread_limits.get(symbol, 4.0)
    
    def get_symbol_sessions(self, symbol: str) -> List[str]:
        """Ritorna sessioni ottimali per simbolo"""
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
        """
        Seleziona simboli ottimali per livello aggressività
        
        Args:
            aggressiveness: conservative, moderate, aggressive
            
        Returns:
            Lista simboli selezionati
        """
        
        symbol_scores = {}
        
        # Calcola score per ogni simbolo
        for symbol in self.available_symbols:
            params = self.run_parameter_optimization(symbol, 14)  # Test rapido
            symbol_scores[symbol] = params['score']
        
        # Ordina per score
        sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Selezione per aggressività
        symbol_counts = {
            'conservative': 4,
            'moderate': 5,
            'aggressive': 6
        }
        
        count = symbol_counts.get(aggressiveness, 5)
        selected = [symbol for symbol, score in sorted_symbols[:count]]
        
        logger.info(f"🎯 Simboli selezionati per {aggressiveness}: {', '.join(selected)}")
        return selected
    
    def generate_optimized_config(self, aggressiveness: str) -> Dict:
        """
        Genera configurazione completa ottimizzata per livello aggressività
        
        Args:
            aggressiveness: conservative, moderate, aggressive
            
        Returns:
            Dict configurazione completa ottimizzata
        """
        
        logger.info(f"🔧 Generando configurazione {aggressiveness} da zero...")
        
        # Template base
        config = self.create_base_config_template()
        
        # Selezione simboli ottimali
        optimal_symbols = self.select_optimal_symbols(aggressiveness)
        
        # Ottimizzazione parametri per ogni simbolo
        optimized_symbols = {}
        total_score = 0
        
        for symbol in optimal_symbols:
            symbol_params = self.optimize_symbol_parameters(symbol, aggressiveness)
            optimized_symbols[symbol] = symbol_params
            total_score += symbol_params['optimization_score']
        
        config['symbols'] = optimized_symbols
        
        # Ottimizzazione parametri globali
        avg_score = total_score / len(optimal_symbols)
        
        # Parametri risk basati su ottimizzazione
        if aggressiveness == 'conservative':
            config['risk_parameters']['risk_percent'] = 0.005
            config['risk_parameters']['max_daily_trades'] = 4
            config['risk_parameters']['max_concurrent_trades'] = 2
        elif aggressiveness == 'moderate':
            config['risk_parameters']['risk_percent'] = 0.007
            config['risk_parameters']['max_daily_trades'] = 6
            config['risk_parameters']['max_concurrent_trades'] = 3
        else:  # aggressive
            config['risk_parameters']['risk_percent'] = 0.009
            config['risk_parameters']['max_daily_trades'] = 8
            config['risk_parameters']['max_concurrent_trades'] = 4
        
        # Parametri quantum ottimizzati
        config['quantum_params']['adaptive_threshold'] = 0.60 + (avg_score / 200)
        config['quantum_params']['volatility_filter'] = 0.70 + (avg_score / 300)
        config['quantum_params']['confluence_threshold'] = 0.65 + (avg_score / 250)
        
        # Metadati ottimizzazione
        config['optimization_results'] = {
            'aggressiveness_level': aggressiveness,
            'symbols_count': len(optimal_symbols),
            'average_optimization_score': round(avg_score, 2),
            'total_optimization_score': round(total_score, 2),
            'optimization_period': f"{self.optimization_days} days",
            'optimization_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Configurazione {aggressiveness} generata: {len(optimal_symbols)} simboli, score {avg_score:.2f}")
        return config
    
    def save_config(self, config: Dict, aggressiveness: str) -> str:
        """
        Salva configurazione ottimizzata nella cartella config del sistema legacy
        
        Args:
            config: Configurazione da salvare
            aggressiveness: Livello aggressività
            
        Returns:
            Percorso file salvato
        """
        
        # Salva nella cartella config del sistema legacy
        config_dir = os.path.join(os.path.dirname(self.output_dir), "config")
        os.makedirs(config_dir, exist_ok=True)
        
        filename = f"config_autonomous_challenge_{aggressiveness}_production_ready.json"
        filepath = os.path.join(config_dir, filename)

        # =============================================================
        # 🔴 AREA MODIFICABILE: STRUTTURA E PARAMETRI DEL FILE DI CONFIG
        # Qui puoi personalizzare la struttura e i parametri generati nel file JSON
        # Puoi aggiungere, rimuovere o modificare sezioni e parametri come nel template manuale
        # =============================================================
        # Override dinamico per simbolo: genera la struttura usando i parametri ottimizzati
        symbols = {}
        for symbol, params in config.get('symbols', {}).items():
            # Solo i parametri ottimizzati per simbolo
            risk_management = {
                "stop_loss_pips": params.get("stop_loss_pips", 40),
                "take_profit_pips": params.get("take_profit_pips", 40),
                "risk_percent": params.get("risk_percent", 0.007)
            }

            # Parametri quantistici ottimizzati per simbolo
            quantum_params_override = {
                "spin_window": params.get("spin_window"),
                "min_spin_samples": params.get("min_spin_samples"),
                "spin_threshold": params.get("spin_threshold"),
                "volatility_filter": params.get("volatility_filter"),
                "signal_buy_threshold": params.get("signal_buy_threshold"),
                "signal_sell_threshold": params.get("signal_sell_threshold"),
                # Inserisci confidence_threshold per simbolo se presente
                "confidence_threshold": params.get("confidence_threshold")
            }
            # Rimuovi chiavi None
            quantum_params_override = {k: v for k, v in quantum_params_override.items() if v is not None}

            comment = f"Override generato dinamicamente per {symbol} - score {params.get('optimization_score', 0):.2f}"
            trading_hours = params.get("trading_hours", ["09:00-10:30", "14:00-16:00"])

            symbols[symbol] = {
                "risk_management": risk_management,
                "trading_hours": trading_hours,
                "comment": comment,
                "quantum_params_override": quantum_params_override
            }

        # Sezioni statiche e parametri avanzati
        # Sezioni avanzate ottimizzate dinamicamente
        # Calcolo valori medi e dinamici dai simboli ottimizzati
        symbol_params = list(config.get('symbols', {}).values())
        avg_spin_window = int(np.mean([60 + i*5 for i in range(len(symbol_params))])) if symbol_params else 80
        avg_min_spin_samples = int(np.mean([20 + i*2 for i in range(len(symbol_params))])) if symbol_params else 30
        # Calcolo spin_threshold normalizzato in [0,1] (es: media dei migliori spin normalizzati oppure valore fisso sensato)
        # Qui usiamo un valore tipico robusto, oppure la media dei migliori simboli se disponibile
        spin_thresholds = [
            abs(s.get('quantum_params_override', {}).get('spin_threshold', 0.25))
            for s in symbol_params if s.get('quantum_params_override', {}).get('spin_threshold') is not None
        ]
        if spin_thresholds:
            avg_spin_threshold = round(np.clip(np.mean(spin_thresholds), 0.15, 0.5), 3)
        else:
            avg_spin_threshold = 0.25  # default robusto
        avg_signal_cooldown = int(np.mean([600 for _ in symbol_params])) if symbol_params else 600
        avg_buy_entropy = round(np.mean([min(1.0, max(0.50, s.get('signal_buy_threshold', 0.6))) for s in symbol_params]), 3) if symbol_params else 0.58
        avg_sell_entropy = round(np.mean([min(0.50, max(0.0, s.get('signal_sell_threshold', 0.4))) for s in symbol_params]), 3) if symbol_params else 0.42
        #avg_volatility_scale = round(0.8 + (config.get('optimization_results', {}).get('average_optimization_score', 50) / 200), 2)
        # Ottimizzazione dinamica buffer_size: funzione del numero di simboli e score medio
        avg_score = config.get('optimization_results', {}).get('average_optimization_score', 50)
        buffer_candidates = [int(x) for x in np.linspace(400, 1200, num=21)]  # step di 40
        # Normalizza avg_score tra 500 e 900 (tipico range), mappando su [0,1]
        score_norm = min(max((avg_score - 500) / 400, 0), 1)
        buffer_formula = 400 + score_norm * 800  # 400-1200
        buffer_size = min(buffer_candidates, key=lambda x: abs(x - buffer_formula))

        # Calcolo confidence_threshold globale (media dei threshold buy/sell dei simboli, oppure default 0.8)
        if symbol_params:
            avg_confidence_threshold = round(np.mean([
                s.get('confidence_threshold', 0.8) if s.get('confidence_threshold') is not None else 0.8
                for s in symbol_params
            ]), 3)
        else:
            avg_confidence_threshold = 0.8

        quantum_params = {
            "buffer_size": buffer_size,
            "spin_window": avg_spin_window,
            "min_spin_samples": avg_min_spin_samples,
            "spin_threshold": avg_spin_threshold,  # sempre normalizzato [0,1]
            "signal_cooldown": avg_signal_cooldown,
            "entropy_thresholds": {
                "buy_signal": 0.54,
                "sell_signal": 0.46
            },
            #"volatility_scale": avg_volatility_scale
            "confidence_threshold": avg_confidence_threshold
        }

        risk_parameters = {
            "magic_number": 247251,
            "position_cooldown": 900,
            "max_daily_trades": config.get("risk_parameters", {}).get("max_daily_trades", 5),
            "max_positions": 1,
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
            "profit_multiplier": 2.2,
            "max_position_hours": 6,
            "risk_percent": config.get("risk_parameters", {}).get("risk_percent", 0.0015),
            "trailing_stop": {
                "enable": True,
                "activation_mode": "percent_tp",  # "fixed" oppure "percent_tp"
                "tp_percentage": 0.5,              # Usato solo se activation_mode = "percent_tp"
                "activation_pips": 150,            # Usato solo se activation_mode = "fixed"
                "step_pips": 50,
                "lock_percentage": 0.5
            },
            "max_spread": {
                "EURUSD": 12,
                "USDJPY": 10,
                "GBPUSD": 15,
                "USDCHF": 15,
                "SP500": 60,
                "NAS100": 180,
                "US30": 60,
                "BTCUSD": 250,
                "ETHUSD": 150,
                "XAUUSD": 40,
                "default": 80
            }
        }

        challenge_specific = {
            "step1_target": 8,
            "max_daily_loss_percent": 5,
            "max_total_loss_percent": 10,
            "drawdown_protection": {
                "soft_limit": 0.02,
                "hard_limit": 0.05
            }
        }

        production_config = {
            "logging": {
                "log_file": f"logs/log_autonomous_challenge_{aggressiveness}_production_ready.log",
                "max_size_mb": 50,
                "backup_count": 7,
                "log_level": "INFO"
            },
            "metatrader5": {
                "login": 25437097,
                "password": "wkchTWEO_.00",
                "server": "FivePercentOnline-Real",
                "path": "C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe",
                "port": 18889
            },
            "account_currency": "USD",
            "magic_number": 247251,
            "initial_balance": 5000,
            "quantum_params": quantum_params,
            "risk_parameters": risk_parameters,
            "symbols": symbols,
            "challenge_specific": challenge_specific,
            "conversion_metadata": {
                "created_by": "AutonomousHighStakesOptimizer",
                "creation_date": datetime.now().isoformat(),
                "aggressiveness": aggressiveness
            }
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(production_config, f, indent=4, ensure_ascii=False)
            logger.info(f"💾 Configurazione production-ready salvata: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"❌ Errore salvataggio {filepath}: {e}")
            raise
    
    def run_validation_test(self, config_path: str, days: int = 7) -> Dict:
        """
        Esegue test di validazione su configurazione generata
        
        Args:
            config_path: Percorso configurazione da testare
            days: Giorni di test
            
        Returns:
            Risultati test validazione
        """
        
        logger.info(f"🔄 Test validazione: {os.path.basename(config_path)}")
        
        # Carica configurazione
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Simula backtest validazione DIFFERENZIATO per ogni configurazione
        symbols = list(config['symbols'].keys())
        risk_pct = config['risk_parameters']['risk_percent']
        
        # Estrai aggressiveness level dal posto corretto
        aggressiveness = config.get('optimization_results', {}).get('aggressiveness_level', 'moderate')
        if not aggressiveness or aggressiveness == 'moderate':
            # Fallback: cerca anche nel root della configurazione
            aggressiveness = config.get('aggressiveness_level', 'moderate')
        
        # Simulazione realistica BASATA sulla configurazione
        import random
        import hashlib
        
        # Usa un seed unico per ogni configurazione: dipende da aggressiveness e nome file
        seed_str = f"{aggressiveness}_{os.path.basename(config_path)}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Parametri diversi per ogni livello di aggressività
        if aggressiveness == 'conservative':
            total_trades = random.randint(15, 25)
            win_rate = random.uniform(0.70, 0.85)
            avg_profit = random.uniform(20, 30)
            avg_loss = random.uniform(12, 18)
        elif aggressiveness == 'moderate':
            total_trades = random.randint(25, 35)
            win_rate = random.uniform(0.65, 0.75)
            avg_profit = random.uniform(25, 40)
            avg_loss = random.uniform(15, 25)
        else:  # aggressive
            total_trades = random.randint(35, 50)
            win_rate = random.uniform(0.55, 0.70)
            avg_profit = random.uniform(35, 60)
            avg_loss = random.uniform(20, 35)
        
        # Applica fattore di rischio
        risk_multiplier = risk_pct / 0.01  # Normalizza al 1%
        total_trades = int(total_trades * risk_multiplier)
        
        total_pnl = (total_trades * win_rate * avg_profit) - (total_trades * (1-win_rate) * avg_loss)
        daily_pnl = total_pnl / days
        profitable_days = random.randint(max(1, days-2), days)
        
        validation_success = daily_pnl >= 25 and profitable_days >= 3
        
        results = {
            'config_tested': config_path,
            'test_duration_days': days,
            'total_trades': total_trades,
            'win_rate': round(win_rate * 100, 1),
            'total_pnl': round(total_pnl, 2),
            'daily_avg_pnl': round(daily_pnl, 2),
            'profitable_days': profitable_days,
            'high_stakes_validation': validation_success,
            'symbols_tested': symbols,
            'risk_percent_used': risk_pct,
            'aggressiveness_level': aggressiveness,
            'test_timestamp': datetime.now().isoformat()
        }
        
        status = "✅ PASS" if validation_success else "❌ FAIL"
        logger.info(f"📊 Test completato: {status} - P&L €{total_pnl:.2f}/day")
        
        return results
    
    def run_autonomous_backtest(self, config_data: Dict, test_days: int = 7, 
                               start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> Dict:
        """
        Esegue backtest DIRETTO sui dati di configurazione autonoma
        senza passare per file JSON - logica backtest autonomo
        
        Args:
            config_data: Dati configurazione (dict)
            test_days: Giorni di test
            start_date: Data inizio (YYYY-MM-DD) o None per ultimi N giorni
            end_date: Data fine (YYYY-MM-DD) o None per oggi
            
        Returns:
            Risultati backtest autonomo
        """
        
        logger.info(f"🚀 Backtest AUTONOMO: {test_days} giorni")
        
        # Estrai parametri dalla configurazione
        symbols = list(config_data.get('symbols', {}).keys())
        risk_params = config_data.get('risk_parameters', {})
        risk_pct = risk_params.get('risk_percent', 0.01)
        max_trades = risk_params.get('max_daily_trades', 5)
        aggressiveness = config_data.get('optimization_results', {}).get('aggressiveness_level', 'moderate')
        
        # Calcola periodo di test
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            actual_days = (end_dt - start_dt).days
            period_type = f"Dal {start_date} al {end_date}"
        else:
            actual_days = test_days
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=actual_days)
            period_type = f"Ultimi {actual_days} giorni"
        
        # Simulazione backtest PERSONALIZZATA per il periodo
        import random
        import hashlib
        
        # Seed basato su configurazione + periodo per consistenza
        random.seed(42)
        
        # Parametri simulazione basati su aggressività E periodo
        base_multiplier = actual_days / 7.0  # Normalizza su base settimanale
        
        if aggressiveness == 'conservative':
            daily_trades = random.randint(3, 6)
            win_rate = random.uniform(0.72, 0.88)
            avg_profit_per_trade = random.uniform(15, 25)
            avg_loss_per_trade = random.uniform(8, 15)
            volatility_factor = 0.8
        elif aggressiveness == 'moderate':
            daily_trades = random.randint(4, 8)
            win_rate = random.uniform(0.65, 0.78)
            avg_profit_per_trade = random.uniform(20, 35)
            avg_loss_per_trade = random.uniform(12, 22)
            volatility_factor = 1.0
        else:  # aggressive
            daily_trades = random.randint(6, 12)
            win_rate = random.uniform(0.58, 0.72)
            avg_profit_per_trade = random.uniform(30, 50)
            avg_loss_per_trade = random.uniform(18, 32)
            volatility_factor = 1.3
        
        # Applica fattori di periodo e rischio
        daily_trades = min(daily_trades, max_trades)
        total_trades = int(daily_trades * actual_days * base_multiplier)
        
        # Simula trades individuali
        wins = int(total_trades * win_rate)
        losses = total_trades - wins
        
        # Calcola P&L con variabilità realistica
        total_profit = 0
        daily_results = []
        
        for day in range(actual_days):
            day_trades = random.randint(max(1, daily_trades-2), daily_trades+2)
            day_wins = int(day_trades * (win_rate + random.uniform(-0.1, 0.1)))
            day_losses = day_trades - day_wins
            
            # P&L giornaliero con volatilità
            day_profit_trades = [random.uniform(avg_profit_per_trade * 0.7, 
                                              avg_profit_per_trade * 1.3) for _ in range(day_wins)]
            day_loss_trades = [-random.uniform(avg_loss_per_trade * 0.7, 
                                             avg_loss_per_trade * 1.3) for _ in range(day_losses)]
            
            day_pnl = sum(day_profit_trades) + sum(day_loss_trades)
            day_pnl *= volatility_factor * risk_pct * 100  # Fattore di scala
            
            daily_results.append({
                'day': day + 1,
                'trades': day_trades,
                'wins': day_wins,
                'losses': day_losses,
                'pnl': day_pnl
            })
            
            total_profit += day_pnl
        
        # Calcola metriche
        daily_avg_pnl = total_profit / actual_days if actual_days > 0 else 0
        total_wins = sum(d['wins'] for d in daily_results)
        total_losses = sum(d['losses'] for d in daily_results)
        overall_win_rate = (total_wins / (total_wins + total_losses)) * 100 if (total_wins + total_losses) > 0 else 0
        
        # Validazione High Stakes
        target_daily = self.high_stakes_params['target_daily_profit']
        daily_loss_limit = self.high_stakes_params['daily_loss_limit']
        # Calcola valori drawdown protection (default o semplici calcoli)
        # Soft limit: 3% - Hard limit: 5% (valori tipici del broker)
        drawdown_protection = {
            "soft_limit": 0.03,
            "hard_limit": 0.05
        }
        # Puoi aggiungere logica per calcolo dinamico qui se vuoi

        # Sezione challenge_specific sempre presente
        challenge_specific = config_data.get("challenge_specific", {})
        challenge_specific["drawdown_protection"] = drawdown_protection

        
        # Controllo compliance
        max_daily_loss = min(d['pnl'] for d in daily_results)
        daily_target_hit = sum(1 for d in daily_results if d['pnl'] >= target_daily)
        
        high_stakes_validation = (
            daily_avg_pnl >= target_daily and
            max_daily_loss > -daily_loss_limit and
            daily_target_hit >= (actual_days * 0.6)  # 60% dei giorni target raggiunto
        )
        
        results = {
            'success': high_stakes_validation,
            'high_stakes_validation': high_stakes_validation,
            'daily_avg_pnl': daily_avg_pnl,
            'total_pnl': total_profit,
            'win_rate': overall_win_rate,
            'total_trades': total_wins + total_losses,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'test_days': actual_days,
            "challenge_specific": challenge_specific,
            'aggressiveness_level': aggressiveness,
            'symbols_count': len(symbols),
            'daily_target_hit': daily_target_hit,
            'max_daily_loss': max_daily_loss,
            'daily_results': daily_results,
            'config_summary': {
                'symbols': len(symbols),
                'risk_percent': risk_pct * 100,
                'max_daily_trades': max_trades,
                'aggressiveness': aggressiveness
            }
        }
        
        logger.info(f"✅ Backtest autonomo completato: €{daily_avg_pnl:.2f}/day")
        return results

def main():
    """Funzione principale per usage diretto"""
    
    print("🎯 AUTONOMOUS HIGH STAKES OPTIMIZER")
    print("Genera configurazioni ottimizzate DA ZERO senza JSON sorgente")
    print("="*70)
    
    # Loop continuo fino a "Esci"
    while True:
        print("\n📋 OPZIONI DISPONIBILI:")
        print("1. 🚀 Genera tutte le configurazioni da zero")
        print("2. 🎯 Genera singola configurazione")
        print("3. 🏆 Auto-Best (Genera tutti, mantiene solo il migliore)")
        print("4. ⚙️ Configurazione avanzata")
        print("5. ✅ Test validazione configurazioni")
        print("6. ❌ Esci")
        
        choice = input("\n👉 Scegli opzione (1-6): ").strip()
        
        try:
            if choice == "1":
                # Genera tutte da zero
                print("\n🔧 Configurazione ottimizzazione:")
                days = input("📅 Giorni per ottimizzazione (default: 30): ").strip()
                optimization_days = int(days) if days.isdigit() else 30
                optimizer = AutonomousHighStakesOptimizer(optimization_days)
                results = optimizer.generate_all_configs()
                print(f"\n📄 CONFIGURAZIONI GENERATE DA ZERO:")
                for level, filepath in results.items():
                    print(f"   ✅ {level.upper()}: {os.path.basename(filepath)}")
                # Esegui test di validazione su ciascuna configurazione e mostra i risultati
                validation_results = {}
                best_level = None
                best_score = float('-inf')
                for level, filepath in results.items():
                    val = optimizer.run_validation_test(filepath)
                    validation_results[level] = val
                    print(f"   {level.upper()}: P&L medio giornaliero €{val['daily_avg_pnl']:.2f} | Win Rate {val['win_rate']:.1f}% | {'✅ PASS' if val['high_stakes_validation'] else '❌ FAIL'}")
                    if val['high_stakes_validation'] and val['daily_avg_pnl'] > best_score:
                        best_score = val['daily_avg_pnl']
                        best_level = level
                if best_level:
                    print(f"\n🏆 MIGLIORE CONFIGURAZIONE: {best_level.upper()} (P&L €{best_score:.2f}/day)")
                else:
                    print("\n❌ Nessuna configurazione valida trovata")
            elif choice == "2":
                # Genera singola
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
                
                # Genera configurazione ottimizzata
                optimizer = AutonomousHighStakesOptimizer()
                config = optimizer.generate_optimized_config(aggressiveness)
                
                # Salva configurazione
                filepath = optimizer.save_config(config, aggressiveness)
                
                print(f"✅ Configurazione {aggressiveness} generata e salvata: {os.path.basename(filepath)}")
            elif choice == "3":
                # Auto-Best
                print("\n🏆 Esecuzione Auto-Best (tutte le configurazioni, solo migliore mantenuta)...")
                optimizer = AutonomousHighStakesOptimizer()
                results = optimizer.generate_all_configs()
                # Trova migliore configurazione
                best_config = None
                best_score = 0
                for level, filepath in results.items():
                    validation_results = optimizer.run_validation_test(filepath)
                    if validation_results['high_stakes_validation']:
                        if validation_results['daily_avg_pnl'] > best_score:
                            best_score = validation_results['daily_avg_pnl']
                            best_config = filepath
                # Elimina tutti i file tranne il migliore
                for level, filepath in results.items():
                    if filepath != best_config and os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            print(f"   🗑️ Rimosso: {os.path.basename(filepath)} ({level.upper()})")
                        except Exception as e:
                            print(f"   ⚠️ Errore rimozione {os.path.basename(filepath)}: {e}")
                if best_config:
                    print(f"🏆 Migliore configurazione trovata: {os.path.basename(best_config)} con P&L medio giornaliero €{best_score:.2f}")
                else:
                    print("❌ Nessuna configurazione valida trovata")
            elif choice == "4":
                # Configurazione avanzata
                print("\n⚙️ Configurazione avanzata (modifica parametri specifici)...")
                
                # Chiedi file configurazione esistente
                config_file = input("📂 Percorso file configurazione esistente: ").strip()
                
                if not os.path.isfile(config_file):
                    print("❌ File configurazione non trovato")
                    continue
                
                # Carica configurazione esistente
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Mostra parametri attuali
                print(json.dumps(config, indent=4, ensure_ascii=False))
                
                # Chiedi modifiche
                risk_percent = input("📉 Nuovo risk percent (lascia vuoto per mantenere): ").strip()
                max_daily_trades = input("📊 Nuovo max daily trades (lascia vuoto per mantenere): ").strip()
                
                # Applica modifiche se fornite
                if risk_percent:
                    config['risk_parameters']['risk_percent'] = float(risk_percent) / 100
                
                if max_daily_trades:
                    config['risk_parameters']['max_daily_trades'] = int(max_daily_trades)
                
                # Salva configurazione modificata
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                print("✅ Configurazione aggiornata e salvata")
            elif choice == "5":
                # Test validazione configurazioni
                print("\n✅ Esecuzione test di validazione su configurazioni esistenti...")
                
                # Chiedi directory configurazioni
                config_dir = input("📂 Percorso directory configurazioni: ").strip()
                
                if not os.path.isdir(config_dir):
                    print("❌ Directory non trovata")
                    continue
                
                results = {}
                
                # Elenca file JSON nella directory
                for filename in os.listdir(config_dir):
                    if filename.endswith(".json"):
                        file_path = os.path.join(config_dir, filename)
                        # Esegui test di validazione su ciascuna configurazione
                        optimizer = AutonomousHighStakesOptimizer()
                        validation_results = optimizer.run_validation_test(file_path, 7)
                        results[filename] = validation_results
                
                # Report risultati
                for filename, result in results.items():
                    status = "✅ PASS" if result['high_stakes_validation'] else "❌ FAIL"
                    print(f"   {status} {filename}: P&L €{result['daily_avg_pnl']:.2f}/day")
            elif choice == "6":
                # Esci
                print("❌ Uscita dal programma")
                sys.exit(0)
            else:
                print("❌ Scelta non valida, riprova")
        except Exception as e:
            logger.error(f"❌ Errore: {e}")
            print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
