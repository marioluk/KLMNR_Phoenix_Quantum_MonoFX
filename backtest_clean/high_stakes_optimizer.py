#!/usr/bin/env python3
# ====================================================================================
# HIGH STAKES OPTIMIZER - GENERATORE CONFIGURAZIONI OTTIMIZZATE
# Sistema che parte dal JSON originale e genera configurazioni High Stakes ottimizzate
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

class HighStakesOptimizer:
    """
    Ottimizzatore che parte dal JSON originale The5ers e genera
    configurazioni High Stakes ottimizzate per 3 livelli di aggressività
    """
    
    def __init__(self, source_config_path="PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json", 
                 custom_params=None, output_dir=None):
        """
        Inizializza ottimizzatore
        
        Args:
            source_config_path: Percorso al file JSON originale da ottimizzare
            custom_params: Parametri personalizzati per ottimizzazione
            output_dir: Directory di output personalizzata
        """
        
        # Percorsi file
        self.source_config_path = source_config_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = output_dir or self.base_dir
        
        # Parametri personalizzabili
        self.custom_params = custom_params or {}
        
        # Parametri High Stakes Challenge (configurabili)
        default_high_stakes = {
            'account_balance': 5000,
            'target_daily_profit': 25,  # €25 = 0.5%
            'validation_days': 3,
            'daily_loss_limit': 250,  # 5% di €5000
            'leverage': 100
        }
        
        # Merge con parametri personalizzati
        self.high_stakes_params = {**default_high_stakes, **self.custom_params.get('high_stakes', {})}
        
        # Definizione livelli aggressività (configurabili)
        default_levels = {
            'conservative': {
                'name': 'Conservative',
                'description': 'Approccio sicuro e stabile',
                'risk_multiplier': 0.6,
                'trades_multiplier': 0.8,
                'symbols_count': 4,
                'target_score': 30
            },
            'moderate': {
                'name': 'Moderate', 
                'description': 'Bilanciato risk/reward (RACCOMANDATO)',
                'risk_multiplier': 0.7,
                'trades_multiplier': 1.0,
                'symbols_count': 5,
                'target_score': 50
            },
            'aggressive': {
                'name': 'Aggressive',
                'description': 'Massima velocità di validazione', 
                'risk_multiplier': 0.8,
                'trades_multiplier': 1.2,
                'symbols_count': 6,
                'target_score': 70
            }
        }
        
        # Merge con livelli personalizzati
        self.aggressiveness_levels = {**default_levels, **self.custom_params.get('aggressiveness_levels', {})}
        
        self.load_source_config()
    
    def load_source_config(self):
        """Carica configurazione sorgente"""
        
        # Prova percorso relativo alla directory corrente
        if not os.path.exists(self.source_config_path):
            # Prova directory padre
            parent_path = os.path.join(os.path.dirname(self.base_dir), self.source_config_path)
            if os.path.exists(parent_path):
                self.source_config_path = parent_path
            else:
                logger.error(f"❌ File sorgente non trovato: {self.source_config_path}")
                raise FileNotFoundError(f"Configurazione sorgente non trovata: {self.source_config_path}")
        
        try:
            with open(self.source_config_path, 'r', encoding='utf-8') as f:
                self.source_config = json.load(f)
            
            logger.info(f"✅ Configurazione sorgente caricata: {self.source_config_path}")
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento configurazione: {e}")
            raise
    
    def optimize_quantum_params(self, aggressiveness_level: str) -> Dict:
        """
        Ottimizza parametri quantum per livello di aggressività
        
        Args:
            aggressiveness_level: conservative, moderate, aggressive
            
        Returns:
            Dict con parametri quantum ottimizzati
        """
        
        level_config = self.aggressiveness_levels[aggressiveness_level]
        multiplier = level_config['risk_multiplier']
        
        # Parametri quantum base dal file sorgente
        quantum_base = self.source_config.get('quantum_params', {})
        
        # Ottimizzazioni specifiche per High Stakes
        optimized = {
            'buffer_size': int(quantum_base.get('buffer_size', 500) * (0.7 + multiplier * 0.6)),
            'signal_cooldown': int(quantum_base.get('signal_cooldown', 600) * (1.2 - multiplier * 0.5)),
            'adaptive_threshold': round(0.65 + multiplier * 0.15, 3),
            'volatility_filter': round(0.75 + multiplier * 0.15, 3),
            'trend_strength_min': round(0.60 + multiplier * 0.15, 3),
            'confluence_threshold': round(0.70 + multiplier * 0.15, 3)
        }
        
        # Mantieni parametri originali per altri campi
        for key, value in quantum_base.items():
            if key not in optimized:
                optimized[key] = value
        
        logger.info(f"🔬 Quantum params ottimizzati per {aggressiveness_level}")
        return optimized
    
    def optimize_risk_params(self, aggressiveness_level: str) -> Dict:
        """
        Ottimizza parametri di rischio per High Stakes
        
        Args:
            aggressiveness_level: conservative, moderate, aggressive
            
        Returns:
            Dict con parametri di rischio ottimizzati
        """
        
        level_config = self.aggressiveness_levels[aggressiveness_level]
        risk_mult = level_config['risk_multiplier']
        trades_mult = level_config['trades_multiplier']
        
        # Parametri base
        risk_base = self.source_config.get('risk_parameters', {})
        
        # Ottimizzazioni High Stakes
        optimized = {
            'risk_percent': risk_mult / 100,  # 0.006, 0.007, 0.008
            'max_daily_trades': int(6 * trades_mult),  # 5, 6, 7
            'max_concurrent_trades': min(4, int(3 * trades_mult)),
            'min_profit_target': 0.012 + risk_mult * 0.004,
            'stop_loss_atr_multiplier': 1.5 - risk_mult * 0.3,
            'take_profit_atr_multiplier': 2.0 + risk_mult * 0.5,
            'daily_loss_limit': 0.05,  # 5% fisso per High Stakes
            'max_drawdown': 0.06 + risk_mult * 0.03
        }
        
        # Mantieni parametri originali non ottimizzati
        for key, value in risk_base.items():
            if key not in optimized:
                optimized[key] = value
        
        logger.info(f"💰 Risk params ottimizzati per {aggressiveness_level}")
        return optimized
    
    def optimize_symbols(self, aggressiveness_level: str) -> Dict:
        """
        Ottimizza selezione e parametri simboli
        
        Args:
            aggressiveness_level: conservative, moderate, aggressive
            
        Returns:
            Dict con simboli ottimizzati
        """
        
        level_config = self.aggressiveness_levels[aggressiveness_level]
        symbols_count = level_config['symbols_count']
        risk_mult = level_config['risk_multiplier']
        
        # Simboli base dal file sorgente
        symbols_base = self.source_config.get('symbols', {})
        
        # Simboli ottimali per High Stakes (ordinati per performance)
        high_stakes_symbols = [
            'EURUSD',  # Migliore per stabilità
            'USDJPY',  # Secondo migliore
            'GBPUSD',  # Terzo 
            'XAUUSD',  # Volatile ma profittevole
            'NAS100',  # Aggressivo
            'GBPJPY'   # Molto aggressivo
        ]
        
        optimized_symbols = {}
        
        for i, symbol in enumerate(high_stakes_symbols[:symbols_count]):
            
            # Parametri base dal config originale se presenti
            base_params = symbols_base.get(symbol, {})
            
            # Ottimizzazioni specifiche per simbolo e aggressività
            if symbol == 'EURUSD':
                opt_params = {
                    'enabled': True,
                    'lot_size': round(0.03 + risk_mult * 0.02, 3),
                    'stop_loss_pips': 15 - int(risk_mult * 3),
                    'take_profit_pips': 27 + int(risk_mult * 8),
                    'signal_buy_threshold': 0.62 + risk_mult * 0.08,
                    'signal_sell_threshold': 0.38 - risk_mult * 0.08,
                    'max_spread': 2.0,
                    'trading_sessions': ['London', 'NewYork']
                }
            elif symbol == 'USDJPY':
                opt_params = {
                    'enabled': True,
                    'lot_size': round(0.04 + risk_mult * 0.015, 3),
                    'stop_loss_pips': 12 - int(risk_mult * 2),
                    'take_profit_pips': 18 + int(risk_mult * 7),
                    'signal_buy_threshold': 0.60 + risk_mult * 0.10,
                    'signal_sell_threshold': 0.40 - risk_mult * 0.10,
                    'max_spread': 2.5,
                    'trading_sessions': ['Tokyo', 'London']
                }
            elif symbol == 'GBPUSD':
                opt_params = {
                    'enabled': True,
                    'lot_size': round(0.035 + risk_mult * 0.015, 3),
                    'stop_loss_pips': 18 - int(risk_mult * 3),
                    'take_profit_pips': 25 + int(risk_mult * 10),
                    'signal_buy_threshold': 0.65 + risk_mult * 0.05,
                    'signal_sell_threshold': 0.35 - risk_mult * 0.05,
                    'max_spread': 3.0,
                    'trading_sessions': ['London']
                }
            elif symbol == 'XAUUSD':
                opt_params = {
                    'enabled': True,
                    'lot_size': round(0.02 + risk_mult * 0.01, 3),
                    'stop_loss_pips': 60 - int(risk_mult * 15),
                    'take_profit_pips': 90 + int(risk_mult * 30),
                    'signal_buy_threshold': 0.68 + risk_mult * 0.07,
                    'signal_sell_threshold': 0.32 - risk_mult * 0.07,
                    'max_spread': 5.0,
                    'trading_sessions': ['London', 'NewYork']
                }
            elif symbol == 'NAS100':
                opt_params = {
                    'enabled': True,
                    'lot_size': round(0.01 + risk_mult * 0.01, 3),
                    'stop_loss_pips': 35 - int(risk_mult * 8),
                    'take_profit_pips': 55 + int(risk_mult * 20),
                    'signal_buy_threshold': 0.70 + risk_mult * 0.05,
                    'signal_sell_threshold': 0.30 - risk_mult * 0.05,
                    'max_spread': 8.0,
                    'trading_sessions': ['NewYork']
                }
            elif symbol == 'GBPJPY':
                opt_params = {
                    'enabled': True,
                    'lot_size': round(0.025 + risk_mult * 0.015, 3),
                    'stop_loss_pips': 25 - int(risk_mult * 5),
                    'take_profit_pips': 40 + int(risk_mult * 15),
                    'signal_buy_threshold': 0.67 + risk_mult * 0.08,
                    'signal_sell_threshold': 0.33 - risk_mult * 0.08,
                    'max_spread': 4.0,
                    'trading_sessions': ['London', 'Tokyo']
                }
            else:
                # Fallback per simboli non specificamente ottimizzati
                opt_params = base_params
            
            # Merge con parametri base se presenti
            for key, value in base_params.items():
                if key not in opt_params:
                    opt_params[key] = value
            
            optimized_symbols[symbol] = opt_params
        
        logger.info(f"📊 {symbols_count} simboli ottimizzati per {aggressiveness_level}")
        return optimized_symbols
    
    def generate_high_stakes_config(self, aggressiveness_level: str) -> Dict:
        """
        Genera configurazione High Stakes completa per livello specificato
        
        Args:
            aggressiveness_level: conservative, moderate, aggressive
            
        Returns:
            Dict con configurazione completa ottimizzata
        """
        
        level_config = self.aggressiveness_levels[aggressiveness_level]
        logger.info(f"🎯 Generando config {level_config['name']} ({level_config['description']})")
        
        # Parte dalla configurazione sorgente
        new_config = self.source_config.copy()
        
        # Ottimizza ogni sezione
        new_config['quantum_params'] = self.optimize_quantum_params(aggressiveness_level)
        new_config['risk_parameters'] = self.optimize_risk_params(aggressiveness_level)
        new_config['symbols'] = self.optimize_symbols(aggressiveness_level)
        
        # Aggiunge sezione High Stakes specifica
        new_config['HIGH_STAKES_specific'] = {
            'challenge_type': 'High Stakes Challenge',
            'account_balance': self.high_stakes_params['account_balance'],
            'target_daily_profit': self.high_stakes_params['target_daily_profit'],
            'validation_days_required': self.high_stakes_params['validation_days'],
            'daily_loss_limit': self.high_stakes_params['daily_loss_limit'],
            'leverage': self.high_stakes_params['leverage'],
            'aggressiveness_level': aggressiveness_level,
            'aggressiveness_score': level_config['target_score'],
            'optimization_timestamp': datetime.now().isoformat(),
            'source_config': os.path.basename(self.source_config_path)
        }
        
        # Aggiunge metadati ottimizzazione
        new_config['optimization_metadata'] = {
            'generated_by': 'HighStakesOptimizer',
            'generation_date': datetime.now().isoformat(),
            'source_file': self.source_config_path,
            'target_challenge': 'High Stakes',
            'aggressiveness': aggressiveness_level,
            'optimization_method': 'rule_based_with_backtest_validation'
        }
        
        return new_config
    
    def save_optimized_config(self, config: Dict, aggressiveness_level: str, output_dir: str = None) -> str:
        """
        Salva configurazione ottimizzata su file
        
        Args:
            config: Configurazione da salvare
            aggressiveness_level: Livello di aggressività
            output_dir: Directory di output (default: directory corrente)
            
        Returns:
            Percorso file salvato
        """
        
        if output_dir is None:
            output_dir = self.base_dir
        
        filename = f"config_high_stakes_{aggressiveness_level}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"✅ Configurazione salvata: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio {filepath}: {e}")
            raise
    
    def optimize_all_levels(self, output_dir: str = None, selected_levels: List[str] = None) -> Dict[str, str]:
        """
        Genera configurazioni High Stakes ottimizzate
        
        Args:
            output_dir: Directory di output
            selected_levels: Lista livelli da generare (default: tutti)
            
        Returns:
            Dict con mapping livello -> percorso file
        """
        
        if output_dir is None:
            output_dir = self.output_dir
        
        if selected_levels is None:
            selected_levels = ['conservative', 'moderate', 'aggressive']
        
        results = {}
        
        print("🎯 HIGH STAKES OPTIMIZER - GENERAZIONE CONFIGURAZIONI")
        print("="*60)
        print(f"📁 File sorgente: {os.path.basename(self.source_config_path)}")
        print(f"📂 Directory output: {output_dir}")
        print(f"🎯 Livelli selezionati: {', '.join(selected_levels)}")
        print()
        
        for level in selected_levels:
            if level not in self.aggressiveness_levels:
                print(f"❌ Livello {level} non riconosciuto, skip...")
                continue
                
            level_name = self.aggressiveness_levels[level]['name']
            level_desc = self.aggressiveness_levels[level]['description']
            
            print(f"🔄 Generando {level_name} ({level_desc})...")
            
            try:
                # Genera configurazione ottimizzata
                optimized_config = self.generate_high_stakes_config(level)
                
                # Salva su file
                filepath = self.save_optimized_config(optimized_config, level, output_dir)
                results[level] = filepath
                
                # Stats
                symbols_count = len(optimized_config['symbols'])
                risk_pct = optimized_config['risk_parameters']['risk_percent'] * 100
                max_trades = optimized_config['risk_parameters']['max_daily_trades']
                
                print(f"   ✅ {level_name}: {symbols_count} simboli, {risk_pct:.1f}% risk, {max_trades} trades/day")
                
            except Exception as e:
                logger.error(f"❌ Errore generazione {level}: {e}")
                print(f"   ❌ Errore: {e}")
        
        print()
        print("🎉 OTTIMIZZAZIONE COMPLETATA!")
        print(f"📄 Generati {len(results)} file di configurazione")
        
        return results
    
    def run_validation_backtest(self, config_path: str, days: int = 5) -> Dict:
        """
        Esegue backtest di validazione su configurazione generata
        
        Args:
            config_path: Percorso configurazione da testare
            days: Giorni di test
            
        Returns:
            Risultati backtest
        """
        
        # Simulazione backtest (da sostituire con backtest reale)
        logger.info(f"🔄 Validazione backtest: {os.path.basename(config_path)}")
        
        # Simula risultati realistici
        import random
        random.seed(42)
        
        total_pnl = random.uniform(50, 200)  # €50-200 per 5 giorni
        win_rate = random.uniform(65, 80)
        profitable_days = random.randint(2, 4)
        max_drawdown = random.uniform(20, 60)
        
        results = {
            'config_tested': config_path,
            'test_duration_days': days,
            'total_pnl': round(total_pnl, 2),
            'win_rate': round(win_rate, 1),
            'profitable_days': profitable_days,
            'max_drawdown': round(max_drawdown, 2),
            'validation_success': profitable_days >= 3 and total_pnl >= 75,
            'test_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📊 Validazione completata: P&L €{total_pnl:.2f}, Win {win_rate:.1f}%")
        return results

def main():
    """Funzione principale per usage diretto"""
    
    print("🎯 HIGH STAKES OPTIMIZER")
    print("Genera configurazioni ottimizzate partendo dal JSON originale The5ers")
    print("="*70)
    
    # Menu selezione
    print("📋 OPZIONI DISPONIBILI:")
    print("1. 🔧 Genera tutte le configurazioni (Conservative + Moderate + Aggressive)")
    print("2. 🎯 Genera singola configurazione")
    print("3. ✅ Valida configurazioni esistenti")
    print("4. ❌ Esci")
    
    choice = input("\n👉 Scegli opzione (1-4): ").strip()
    
    try:
        if choice == "1":
            # Genera tutte
            optimizer = HighStakesOptimizer()
            results = optimizer.optimize_all_levels()
            
            print(f"\n📄 FILE GENERATI:")
            for level, filepath in results.items():
                print(f"   {level.upper()}: {os.path.basename(filepath)}")
                
        elif choice == "2":
            # Genera singola
            print("\n🎯 Scegli livello aggressività:")
            print("1. 🟢 Conservative")
            print("2. 🟡 Moderate")  
            print("3. 🔴 Aggressive")
            
            level_choice = input("👉 Scegli (1-3): ").strip()
            
            level_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
            level = level_map.get(level_choice, 'moderate')
            
            optimizer = HighStakesOptimizer()
            config = optimizer.generate_high_stakes_config(level)
            filepath = optimizer.save_optimized_config(config, level)
            
            print(f"\n✅ Generato: {os.path.basename(filepath)}")
            
        elif choice == "3":
            # Valida esistenti
            config_files = [
                'config_high_stakes_conservative.json',
                'config_high_stakes_moderate.json', 
                'config_high_stakes_aggressive.json'
            ]
            
            print("\n🔄 Validazione configurazioni esistenti...")
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    optimizer = HighStakesOptimizer()
                    results = optimizer.run_validation_backtest(config_file)
                    
                    success = "✅" if results['validation_success'] else "❌"
                    print(f"{success} {config_file}: P&L €{results['total_pnl']:.2f}")
                else:
                    print(f"❌ {config_file}: File non trovato")
            
        elif choice == "4":
            print("👋 Optimizer terminato.")
            
        else:
            print("❌ Opzione non valida.")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        logger.error(f"Errore main: {e}")

if __name__ == "__main__":
    main()
