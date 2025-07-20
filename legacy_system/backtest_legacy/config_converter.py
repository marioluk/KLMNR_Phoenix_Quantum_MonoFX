#!/usr/bin/env python3
"""
CONFIG CONVERTER - Converte configurazioni autonome in formato produzione
Risolve incompatibilità tra file JSON generati autonomamente e formato richiesto per produzione
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

class ConfigConverter:
    """Converter per trasformare config autonomi in formato produzione"""
    
    def __init__(self, production_template_path: str = None):
        """
        Inizializza converter
        
        Args:
            production_template_path: Path al file template produzione
        """
        
        # Template base produzione
        if production_template_path and os.path.exists(production_template_path):
            with open(production_template_path, 'r', encoding='utf-8') as f:
                self.production_template = json.load(f)
        else:
            # Template di default se file non trovato
            self.production_template = self._get_default_production_template()
    
    def _get_default_production_template(self) -> Dict:
        """Restituisce template produzione di default"""
        return {
            "logging": {
                "log_file": "logs/PRO-THE5ERS-QM-PHOENIX-GITCOP-log-STEP1.log",
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
            "magic_number": 177251,
            "initial_balance": 100000
        }
    
    def convert_autonomous_to_production(self, autonomous_config_path: str, output_path: str = None) -> str:
        """
        Converte configurazione autonoma in formato produzione
        
        Args:
            autonomous_config_path: Path al file config autonomo
            output_path: Path di output (opzionale)
            
        Returns:
            Path del file convertito
        """
        
        print(f"🔄 Convertendo: {autonomous_config_path}")
        
        # Carica config autonomo
        with open(autonomous_config_path, 'r', encoding='utf-8') as f:
            autonomous_config = json.load(f)
        
        # Inizia con template produzione
        production_config = self.production_template.copy()
        
        # 1. CONVERTI QUANTUM PARAMS
        production_config['quantum_params'] = self._convert_quantum_params(autonomous_config)
        
        # 2. CONVERTI RISK PARAMETERS  
        production_config['risk_parameters'] = self._convert_risk_parameters(autonomous_config)
        
        # 3. CONVERTI SYMBOLS
        production_config['symbols'] = self._convert_symbols(autonomous_config)
        
        # 4. CONVERTI THE5ERS CONFIG
        production_config['THE5ERS_specific'] = self._convert_the5ers_config(autonomous_config)
        
        # 5. AGGIUNGI METADATI CONVERSIONE
        production_config['conversion_metadata'] = {
            "converted_from": os.path.basename(autonomous_config_path),
            "conversion_date": datetime.now().isoformat(),
            "converter_version": "1.0",
            "original_aggressiveness": autonomous_config.get('optimization_results', {}).get('aggressiveness_level', 'unknown')
        }
        
        # Salva file convertito nella cartella config del sistema legacy
        if not output_path:
            base_name = os.path.splitext(os.path.basename(autonomous_config_path))[0]
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
            os.makedirs(config_dir, exist_ok=True)
            output_path = os.path.join(config_dir, f"{base_name}_production_ready.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(production_config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Convertito: {output_path}")
        
        # Valida compatibilità
        self._validate_production_compatibility(production_config)
        
        return output_path
    
    def _convert_quantum_params(self, autonomous_config: Dict) -> Dict:
        """Converte parametri quantum dal formato autonomo"""
        
        autonomous_quantum = autonomous_config.get('quantum_params', {})
        
        # Converte adaptive_threshold e volatility_filter in entropy_thresholds
        adaptive_threshold = autonomous_quantum.get('adaptive_threshold', 0.65)
        
        # Normalizza i valori se sono fuori range [0,1]
        if adaptive_threshold > 1.0:
            adaptive_threshold = adaptive_threshold / 10.0  # Scala se necessario
        
        return {
            "buffer_size": autonomous_quantum.get('buffer_size', 500),
            "spin_window": 80,  # Default produzione
            "min_spin_samples": 30,  # Default produzione  
            "spin_threshold": 0.32,  # Default produzione
            "signal_cooldown": autonomous_quantum.get('signal_cooldown', 600),
            "entropy_thresholds": {
                "buy_signal": min(0.65, max(0.5, adaptive_threshold)),
                "sell_signal": min(0.5, max(0.35, 1.0 - adaptive_threshold))
            },
            "volatility_scale": 1.0
        }
    
    def _convert_risk_parameters(self, autonomous_config: Dict) -> Dict:
        """Converte parametri di rischio"""
        
        autonomous_risk = autonomous_config.get('risk_parameters', {})
        
        return {
            "magic_number": 147251,  # Default produzione
            "position_cooldown": 900,
            "max_daily_trades": autonomous_risk.get('max_daily_trades', 5),
            "max_positions": autonomous_risk.get('max_concurrent_trades', 1),
            "risk_percent": autonomous_risk.get('risk_percent', 0.0015),
            "profit_multiplier": 2.2,
            "max_position_hours": 6,
            "trailing_stop": {
                "enable": True,
                "activation_pips": 100,
                "step_pips": 50,
                "lock_percentage": 0.5
            },
            # Defaults per pips e spread
            "min_sl_distance_pips": {
                "EURUSD": 30, "GBPUSD": 35, "USDJPY": 25, "XAUUSD": 150, "NAS100": 50, "default": 40
            },
            "base_sl_pips": {
                "EURUSD": 50, "GBPUSD": 60, "USDJPY": 40, "XAUUSD": 220, "NAS100": 100, "default": 80
            },
            "max_spread": {
                "EURUSD": 12, "GBPUSD": 15, "USDJPY": 10, "XAUUSD": 40, "NAS100": 180, "default": 20
            }
        }
    
    def _convert_symbols(self, autonomous_config: Dict) -> Dict:
        """Converte configurazione simboli"""
        
        autonomous_symbols = autonomous_config.get('symbols', {})
        production_symbols = {}
        
        # Mapping delle sessioni
        session_mapping = {
            "London": ["09:00-10:30", "14:00-16:00"],
            "NewYork": ["14:00-16:00"], 
            "Tokyo": ["02:00-04:00", "09:00-10:30"]
        }
        
        for symbol, data in autonomous_symbols.items():
            if not data.get('enabled', True):
                continue
                
            # Converti in formato produzione
            production_symbols[symbol] = {
                "risk_management": {
                    "contract_size": data.get('lot_size', 0.01),
                    "min_sl_distance_pips": data.get('stop_loss_pips', 30),
                    "base_sl_pips": data.get('stop_loss_pips', 50),
                    "profit_multiplier": autonomous_config.get('risk_parameters', {}).get('risk_reward_ratio', 2.2),
                    "risk_percent": autonomous_config.get('risk_parameters', {}).get('risk_percent', 0.0015),
                    "trailing_stop": {
                        "activation_pips": data.get('take_profit_pips', 90),
                        "step_pips": data.get('take_profit_pips', 45) // 2 if data.get('take_profit_pips') else 45
                    }
                },
                "trading_hours": session_mapping.get(
                    data.get('trading_sessions', ['London'])[0], 
                    ["09:00-10:30", "14:00-16:00"]
                ),
                "comment": f"Converted from autonomous - score: {data.get('optimization_score', 0):.1f}",
                "quantum_params_override": {
                    "buffer_size": 500,
                    "spin_window": 70,
                    "min_spin_samples": 25,
                    "signal_cooldown": 800,
                    "entropy_thresholds": {
                        "buy_signal": data.get('signal_buy_threshold', 0.56),
                        "sell_signal": data.get('signal_sell_threshold', 0.44)
                    }
                }
            }
        
        return production_symbols
    
    def _convert_the5ers_config(self, autonomous_config: Dict) -> Dict:
        """Converte configurazione The5ers"""
        
        high_stakes = autonomous_config.get('high_stakes_challenge', {})
        
        return {
            "step1_target": 8,  # Default
            "max_daily_loss_percent": high_stakes.get('max_daily_loss_percent', 5),
            "max_total_loss_percent": 10,  # Default
            "drawdown_protection": {
                "soft_limit": 0.02,
                "hard_limit": high_stakes.get('max_daily_loss_percent', 0.05)
            }
        }
    
    def _validate_production_compatibility(self, config: Dict):
        """Valida che la configurazione sia compatibile con produzione"""
        
        required_sections = ['logging', 'metatrader5', 'quantum_params', 'risk_parameters', 'symbols']
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            print(f"⚠️ Sezioni mancanti: {missing_sections}")
        else:
            print("✅ Tutte le sezioni richieste presenti")
        
        # Valida parametri critici
        if 'magic_number' not in config:
            print("⚠️ magic_number mancante")
        
        if len(config.get('symbols', {})) == 0:
            print("⚠️ Nessun simbolo configurato")
        else:
            print(f"✅ {len(config['symbols'])} simboli configurati")


def main():
    """Funzione principale per uso da linea di comando"""
    
    if len(sys.argv) < 2:
        print("Usage: python config_converter.py <autonomous_config_path> [production_template_path]")
        sys.exit(1)
    
    autonomous_config_path = sys.argv[1]
    production_template_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(autonomous_config_path):
        print(f"❌ File non trovato: {autonomous_config_path}")
        sys.exit(1)
    
    converter = ConfigConverter(production_template_path)
    output_path = converter.convert_autonomous_to_production(autonomous_config_path)
    
    print(f"\n🎯 Conversione completata!")
    print(f"📁 File output: {output_path}")
    print(f"💡 Ora puoi usare questo file in produzione")


if __name__ == "__main__":
    main()
