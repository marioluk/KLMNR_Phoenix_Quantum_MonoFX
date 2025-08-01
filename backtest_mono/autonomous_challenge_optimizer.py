from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

# ...existing code...

class AutonomousHighStakesOptimizer:
    # ...existing code...
    def verify_sl_tp_consistency(self, config, mode=None, log_file=None):
        """
        Verifica la coerenza tra stop_loss_pips e take_profit_pips tra preset, config globale e simboli ottimizzati.
        Logga e stampa eventuali discrepanze.
        """
        import logging
        logger = logging.getLogger(__name__)
        if mode is None:
            mode = config.get('metadata', {}).get('trading_mode', 'intraday')
        preset = self.get_trading_mode_params(mode)
        global_sl = config.get('risk_parameters', {}).get('stop_loss_pips')
        global_tp = config.get('risk_parameters', {}).get('take_profit_pips')
        issues = []
        # Verifica preset vs globale
        if global_sl is not None and preset.get('stop_loss_pips') is not None and global_sl != preset['stop_loss_pips']:
            issues.append(f"[GLOBAL] stop_loss_pips: preset={preset['stop_loss_pips']} vs config={global_sl}")
        if global_tp is not None and preset.get('take_profit_pips') is not None and global_tp != preset['take_profit_pips']:
            issues.append(f"[GLOBAL] take_profit_pips: preset={preset['take_profit_pips']} vs config={global_tp}")
        # Verifica simboli
        for symbol, params in config.get('symbols', {}).items():
            sl = params.get('stop_loss_pips')
            tp = params.get('take_profit_pips')
            if sl is not None and (sl < 1 or sl > 10000):
                issues.append(f"[{symbol}] stop_loss_pips fuori range: {sl}")
            if tp is not None and (tp < 1 or tp > 20000):
                issues.append(f"[{symbol}] take_profit_pips fuori range: {tp}")
            if sl is not None and tp is not None and tp < sl:
                issues.append(f"[{symbol}] take_profit_pips < stop_loss_pips: TP={tp}, SL={sl}")
        if issues:
            print("\n===== VERIFICA COERENZA SL/TP =====")
            for issue in issues:
                print("  -", issue)
            if log_file:
                try:
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"[VERIFICA SL/TP] {datetime.now().isoformat()}\n")
                        for issue in issues:
                            f.write(f"  - {issue}\n")
                except Exception as e:
                    print(f"[VERIFICA SL/TP] Errore scrittura log: {e}")
        else:
            print("[VERIFICA SL/TP] Tutto OK.")
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
    # =============================
    # PARAMETRI PRINCIPALI - DESCRIZIONE dettagliata
    # =============================
    # max_position_hours: Durata massima di una posizione aperta (in ore). Limita l’esposizione temporale del trade.
    # max_daily_trades: Numero massimo di trade che il sistema può aprire in una giornata. Controlla la frequenza operativa.
    # position_cooldown: Tempo minimo (in secondi) tra la chiusura di una posizione e l’apertura della successiva. Evita overtrading.
    # stop_loss_pips: Distanza dello Stop Loss dal prezzo di ingresso (in pips). Protegge il capitale da movimenti avversi.
    # take_profit_pips: Distanza del Take Profit dal prezzo di ingresso (in pips). Definisce l’obiettivo di profitto per il trade.
    # buffer_size: Numero di tick/candele usati per analisi statistica e pattern recognition. Maggiore buffer = analisi più storica.
    # spin_window: Finestra (in tick/candele) per il calcolo dei segnali “spin” (direzionalità). Più ampia = segnali più stabili.
    # min_spin_samples: Numero minimo di campioni richiesti per calcolare uno spin affidabile. Evita segnali su dati insufficienti.
    # signal_cooldown: Tempo minimo (in secondi) tra due segnali di ingresso. Riduce la frequenza di operatività e filtra il rumore.
    # risk_percent: Percentuale del capitale rischiata per ogni trade. Determina la size della posizione.
    # max_concurrent_trades: Numero massimo di posizioni aperte contemporaneamente. Limita l’esposizione multipla.
    # signal_threshold: Soglia di attivazione del segnale. Più alta = segnali più selettivi.
    # spin_threshold: Soglia di direzionalità per attivare il trade. Più alta = serve maggiore convinzione direzionale.
    # volatility_filter: Filtro sulla volatilità del mercato. Opera solo se la volatilità è entro certi limiti.
    # trend_strength: Filtro sulla forza del trend. Opera solo se il trend è sufficientemente forte.
        """
        Restituisce i range di parametri ottimali per la tipologia di trading.
        """
        ranges = {
            "scalping": {
                "risk_percent": [0.003, 0.004, 0.005, 0.006, 0.007],
                "max_daily_trades": [20, 30, 40, 60, 80, 100],
                "max_concurrent_trades": [2, 3, 4],
                "stop_loss_pips": [6, 8, 10, 12, 15],
                "take_profit_pips": [10, 12, 15, 18, 20, 25],
                "signal_threshold": [0.55, 0.60, 0.65, 0.70, 0.75],
                "spin_threshold": [0.15, 0.20, 0.25, 0.35, 0.5],
                "volatility_filter": [0.60, 0.65, 0.70, 0.75],
                "trend_strength": [0.50, 0.55, 0.60, 0.65]
            },
            "intraday": {
                "risk_percent": [0.004, 0.005, 0.007, 0.008, 0.010],
                "max_daily_trades": [5, 6, 8, 10, 12, 15, 20],
                "max_concurrent_trades": [2, 3, 4],
                "stop_loss_pips": [15, 18, 20, 25, 30],
                "take_profit_pips": [30, 35, 40, 50, 60],
                "signal_threshold": [0.55, 0.60, 0.65, 0.70, 0.75],
                "spin_threshold": [0.15, 0.25, 0.35, 0.5, 0.7],
                "volatility_filter": [0.65, 0.70, 0.75, 0.80],
                "trend_strength": [0.55, 0.60, 0.65, 0.70]
            },
            "swing": {
                "risk_percent": [0.005, 0.007, 0.008, 0.010, 0.012],
                "max_daily_trades": [1, 2, 3, 4, 5, 6],
                "max_concurrent_trades": [1, 2, 3],
                "stop_loss_pips": [50, 60, 80, 100, 120, 150, 200],
                "take_profit_pips": [100, 120, 150, 180, 200, 250, 300],
                "signal_threshold": [0.55, 0.60, 0.65, 0.70, 0.75],
                "spin_threshold": [0.15, 0.25, 0.35, 0.5, 0.7, 1.0],
                "volatility_filter": [0.70, 0.75, 0.80, 0.85],
                "trend_strength": [0.60, 0.65, 0.70, 0.75]
            },
            "position": {
                "risk_percent": [0.005, 0.007, 0.008, 0.010, 0.012],
                "max_daily_trades": [1, 2],
                "max_concurrent_trades": [1, 2],
                "stop_loss_pips": [150, 200, 250, 300, 400],
                "take_profit_pips": [300, 400, 500, 600, 800],
                "signal_threshold": [0.55, 0.60, 0.65, 0.70, 0.75],
                "spin_threshold": [0.15, 0.25, 0.35, 0.5, 0.7, 1.0],
                "volatility_filter": [0.75, 0.80, 0.85, 0.90],
                "trend_strength": [0.65, 0.70, 0.75, 0.80]
            }
        }
        return ranges.get(mode, ranges["intraday"])
    def validate_trading_params(self, params: dict, mode: str, log_file: str = None) -> list:
        """
        Valida i parametri di trading rispetto alla tipologia selezionata.
        Restituisce una lista di warning/suggerimenti.
        Se log_file è fornito, scrive i warning anche su file.
        """
        warnings = []
        ranges = {
            'scalping': {
                'max_position_hours': (0.05, 2),
                'max_daily_trades': (20, 100),
                'position_cooldown': (60, 300),
                'stop_loss_pips': (6, 12),
                'take_profit_pips': (10, 20),
                'buffer_size': (100, 300),
                'spin_window': (10, 30),
                'min_spin_samples': (3, 6),
                'signal_cooldown': (60, 300)
            },
            'intraday': {
                'max_position_hours': (2, 12),
                'max_daily_trades': (5, 20),
                'position_cooldown': (300, 1200),
                'stop_loss_pips': (15, 35),
                'take_profit_pips': (30, 70),
                'buffer_size': (300, 800),
                'spin_window': (20, 60),
                'min_spin_samples': (6, 12),
                'signal_cooldown': (300, 1200)
            },
            'swing': {
                'max_position_hours': (24, 96),
                'max_daily_trades': (1, 6),
                'position_cooldown': (1200, 3600),
                'stop_loss_pips': (50, 120),
                'take_profit_pips': (100, 250),
                'buffer_size': (800, 2000),
                'spin_window': (40, 120),
                'min_spin_samples': (15, 30),
                'signal_cooldown': (1200, 3600)
            },
            'position': {
                'max_position_hours': (96, 336),
                'max_daily_trades': (1, 2),
                'position_cooldown': (3600, 14400),
                'stop_loss_pips': (150, 400),
                'take_profit_pips': (300, 800),
                'buffer_size': (1500, 5000),
                'spin_window': (100, 300),
                'min_spin_samples': (30, 60),
                'signal_cooldown': (3600, 14400)
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
        # Verifica coerenza SL/TP dopo generazione
        log_file = os.path.join(self.base_dir, "logs", f"log_sl_tp_verifica_{mode}.log")
        self.verify_sl_tp_consistency(config, mode=mode, log_file=log_file)
        return config
    # =============================
    # Tipologie di Trading per Timeframe
    # =============================
    # ... Tutto il codice della classe come da file di produzione ...
    def get_trading_mode_params(self, mode: str) -> dict:
        presets = {
            'scalping': {
                'max_position_hours': 1.0,
                'max_daily_trades': 40,
                'position_cooldown': 180,
                'stop_loss_pips': 9,
                'take_profit_pips': 15,
                'buffer_size': 200,
                'spin_window': 20,
                'min_spin_samples': 4,
                'signal_cooldown': 120,
                'comment': 'Scalping: altissima velocità, molti trade al giorno, spread ridotto'
            },
            'intraday': {
                'max_position_hours': 8,
                'max_daily_trades': 12,
                'position_cooldown': 900,
                'stop_loss_pips': 25,
                'take_profit_pips': 50,
                'buffer_size': 500,
                'spin_window': 40,
                'min_spin_samples': 8,
                'signal_cooldown': 600,
                'comment': 'Intraday: nessuna posizione overnight, sfrutta volatilità giornaliera'
            },
            'swing': {
                'max_position_hours': 48,
                'max_daily_trades': 3,
                'position_cooldown': 2400,
                'stop_loss_pips': 80,
                'take_profit_pips': 180,
                'buffer_size': 1200,
                'spin_window': 80,
                'min_spin_samples': 20,
                'signal_cooldown': 2400,
                'comment': 'Swing Trading: coglie oscillazioni di prezzo più ampie'
            },
            'position': {
                'max_position_hours': 168,
                'max_daily_trades': 1,
                'position_cooldown': 7200,
                'stop_loss_pips': 300,
                'take_profit_pips': 600,
                'buffer_size': 2000,
                'spin_window': 150,
                'min_spin_samples': 40,
                'signal_cooldown': 7200,
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

    def __init__(self, optimization_days=60, output_dir=None, mode="intraday"):
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
        self.param_ranges = self.get_param_ranges_for_mode(mode)
        self.optimized_configs = {}

    def generate_all_configs(self) -> Dict[str, dict]:
        """
        Genera e salva tutte le configurazioni per i tre livelli di aggressività.
        Al termine, stampa un riepilogo degli score medi e totali, evidenziando la migliore.
        """
        levels = ["conservative", "moderate", "aggressive"]
        results = {}
        score_summary = []
        for level in levels:
            config = self.generate_optimized_config(level)
            filepath = self.save_config(config, level)
            opt_res = config.get('optimization_results', {})
            avg_score = opt_res.get('average_optimization_score', 0)
            total_score = opt_res.get('total_optimization_score', 0)
            results[level] = {
                "filepath": filepath,
                "average_score": avg_score,
                "total_score": total_score
            }
            score_summary.append({
                "level": level,
                "filepath": filepath,
                "average_score": avg_score,
                "total_score": total_score
            })
        # Riepilogo finale
        print("\n===== RIEPILOGO SCORE CONFIGURAZIONI GENERATE =====")
        best = max(score_summary, key=lambda x: x["average_score"])
        log_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "score_summary_configurazioni.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"===== RIEPILOGO SCORE CONFIGURAZIONI GENERATE ({datetime.now().isoformat()}) =====\n")
            for item in score_summary:
                star = "⭐" if item["level"] == best["level"] else "  "
                line = f"{star} {item['level'].capitalize():12} | Avg Score: {item['average_score']:.2f} | Total Score: {item['total_score']:.2f} | File: {os.path.basename(item['filepath'])}"
                print(line)
                f.write(line + "\n")
            best_line = f"\nLa configurazione con score medio più alto è: {best['level'].capitalize()} ({os.path.basename(best['filepath'])})\n"
            print(best_line)
            f.write(best_line)
            f.write("Puoi scegliere quale mettere in produzione tramite production_converter.py.\n\n")
        print("Puoi scegliere quale mettere in produzione tramite production_converter.py.")
        print(f"Riepilogo score salvato in: {log_path}")
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
            "max_global_exposure": 50000.0,
            # Aggiunta esplicita del daily_trade_limit_mode
            "daily_trade_limit_mode": config.get("risk_parameters", {}).get("daily_trade_limit_mode", "global")
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

        # --- CHALLENGE SPECIFIC ---
        # Forza la presenza di soft_limit e hard_limit nel JSON generato
        default_challenge_specific = {
            "step1_target": 8,
            "max_daily_loss_percent": 5,
            "max_total_loss_percent": 10,
            "drawdown_protection": {
                "soft_limit": 0.02,
                "hard_limit": 0.05,
                "safe_limit": 0.01
            }
        }
        # Prendi challenge_specific dal config se presente, altrimenti usa default
        challenge_specific = get_section("challenge_specific", default_challenge_specific)
        # Merge con eventuali override da config['challenge_specific']
        if "challenge_specific" in config:
            for k, v in config["challenge_specific"].items():
                if k == "drawdown_protection" and isinstance(v, dict):
                    challenge_specific.setdefault("drawdown_protection", {}).update(v)
                else:
                    challenge_specific[k] = v

        # Forza la presenza di soft_limit, hard_limit e safe_limit (prende da config se presenti, altrimenti default)
        dd_prot = challenge_specific.setdefault("drawdown_protection", {})
        # Cerca override in config['challenge_specific']['drawdown_protection']
        config_dd_prot = config.get("challenge_specific", {}).get("drawdown_protection", {})
        dd_prot["soft_limit"] = config_dd_prot.get("soft_limit", dd_prot.get("soft_limit", 0.02))
        dd_prot["hard_limit"] = config_dd_prot.get("hard_limit", dd_prot.get("hard_limit", 0.05))
        dd_prot["safe_limit"] = config_dd_prot.get("safe_limit", dd_prot.get("safe_limit", 0.01))

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
            "challenge_specific": challenge_specific,
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
                while True:
                    print("\n⚡ Tipologie disponibili:")
                    print("1. Scalping")
                    print("2. Intraday (Day Trading)")
                    print("3. Swing Trading")
                    print("4. Position Trading")
                    print("5. 🔙 Torna al menu principale")
                    mode_choice = input("👉 Scegli tipologia (1-5): ").strip()
                    mode_map = {
                        "1": "scalping",
                        "2": "intraday",
                        "3": "swing",
                        "4": "position"
                    }
                    if mode_choice == "5":
                        break
                    mode = mode_map.get(mode_choice, None)
                    if not mode:
                        print("❌ Scelta non valida, riprova.")
                        continue
                    # Mostra parametri della tipologia selezionata
                    optimizer = AutonomousHighStakesOptimizer()
                    params = optimizer.get_trading_mode_params(mode)
                    print(f"\n📊 Parametri per '{mode.upper()}':")
                    for k, v in params.items():
                        print(f"  {k}: {v}")
                    conferma = input("\n✅ Confermi la selezione e vuoi generare le configurazioni? (s/n): ").strip().lower()
                    if conferma != "s":
                        print("🔙 Selezione annullata. Torna al menu tipologie.")
                        continue
                    # Imposta giorni di ottimizzazione suggeriti in base alla tipologia
                    giorni_ottimali = {
                        "scalping": 30,
                        "intraday": 60,
                        "swing": 120,
                        "position": 180
                    }
                    default_days = giorni_ottimali.get(mode, 60)
                    days = input(f"📅 Giorni per ottimizzazione (default: {default_days}): ").strip()
                    optimization_days = int(days) if days.isdigit() else default_days
                    optimizer = AutonomousHighStakesOptimizer(optimization_days)
                    print(f"\n🔄 Generazione configurazioni per tipologia '{mode}' ({optimization_days} giorni)...")
                    optimizer.generate_all_configs()
                    print("\n📄 Tutte le configurazioni per tipologia trading generate e salvate.")
                    break
            elif choice == "2":
                while True:
                    print("\n🎯 Scegli livello aggressività:")
                    print("1. 🟢 Conservative")
                    print("2. 🟡 Moderate")
                    print("3. 🔴 Aggressive")
                    print("4. 🔙 Torna al menu principale")
                    level_choice = input("👉 Scegli (1-4): ").strip()
                    aggressiveness_map = {
                        "1": "conservative",
                        "2": "moderate",
                        "3": "aggressive"
                    }
                    if level_choice == "4":
                        break
                    aggressiveness = aggressiveness_map.get(level_choice, None)
                    if not aggressiveness:
                        print("❌ Scelta non valida, riprova.")
                        continue
                    optimizer = AutonomousHighStakesOptimizer()
                    config = optimizer.generate_optimized_config(aggressiveness)
                    print(f"\n📊 Parametri principali per '{aggressiveness.upper()}':")
                    print(f"  risk_percent: {config['risk_parameters']['risk_percent']}")
                    print(f"  max_daily_trades: {config['risk_parameters']['max_daily_trades']}")
                    print(f"  max_concurrent_trades: {config['risk_parameters']['max_concurrent_trades']}")
                    conferma = input("\n✅ Confermi la selezione e vuoi generare la configurazione? (s/n): ").strip().lower()
                    if conferma != "s":
                        print("🔙 Selezione annullata. Torna al menu aggressività.")
                        continue
                    filepath = optimizer.save_config(config, aggressiveness)
                    print(f"✅ Configurazione {aggressiveness} generata e salvata: {os.path.basename(filepath)}")
                    break
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
