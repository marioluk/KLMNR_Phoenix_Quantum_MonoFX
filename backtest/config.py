# ====================================================================================
# BACKTEST CONFIGURATION - THE5ERS HIGH STAKES CHALLENGE
# Configurazioni specifiche per il backtest dell'algoritmo quantum
# ====================================================================================

import json
from datetime import datetime, timedelta
from pathlib import Path

# ====================================================================================
# CONFIGURAZIONI BACKTEST
# ====================================================================================

# Configurazione base per backtest
BACKTEST_CONFIG = {
    "data_settings": {
        "timeframe": "M1",  # M1, M5, M15, H1, H4, D1
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "symbols": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100"],
        "data_source": "synthetic",  # synthetic, mt5, csv
        "data_directory": "data/"
    },
    
    "account_settings": {
        "initial_balance": 100000,
        "currency": "USD",
        "leverage": 100,
        "commission": 0.0,
        "spread": {
            "EURUSD": 1.5,
            "GBPUSD": 2.0,
            "USDJPY": 1.0,
            "XAUUSD": 3.0,
            "NAS100": 10.0
        }
    },
    
    "the5ers_rules": {
        "step1": {
            "target_profit_pct": 8.0,
            "max_daily_loss_pct": 5.0,
            "max_total_loss_pct": 10.0,
            "min_profitable_days": 3,
            "max_trading_period_days": None  # Unlimited
        },
        "step2": {
            "target_profit_pct": 5.0,
            "max_daily_loss_pct": 5.0,
            "max_total_loss_pct": 10.0,
            "min_profitable_days": 3,
            "max_trading_period_days": None  # Unlimited
        },
        "scaling": {
            "target_profit_pct": 10.0,
            "max_daily_loss_pct": 5.0,
            "max_total_loss_pct": 10.0,
            "min_profitable_days": 3,
            "profit_share_pct": 80.0
        }
    },
    
    "optimization_settings": {
        "method": "grid_search",  # grid_search, genetic_algorithm, bayesian
        "max_combinations": 1000,
        "parallel_jobs": 4,
        "timeout_seconds": 3600,
        "save_intermediate_results": True
    }
}

# ====================================================================================
# PARAMETER RANGES FOR OPTIMIZATION
# ====================================================================================

OPTIMIZATION_RANGES = {
    "quantum_params": {
        "buffer_size": {
            "min": 200,
            "max": 800,
            "step": 100,
            "type": "int",
            "description": "Dimensione buffer tick per analisi quantum"
        },
        "spin_window": {
            "min": 30,
            "max": 120,
            "step": 10,
            "type": "int",
            "description": "Finestra di calcolo spin quantistico"
        },
        "min_spin_samples": {
            "min": 10,
            "max": 50,
            "step": 5,
            "type": "int",
            "description": "Minimo numero di campioni per calcolo spin"
        },
        "spin_threshold": {
            "min": 0.15,
            "max": 0.45,
            "step": 0.05,
            "type": "float",
            "description": "Soglia per attivazione segnale spin"
        },
        "signal_cooldown": {
            "min": 300,
            "max": 1800,
            "step": 300,
            "type": "int",
            "description": "Cooldown tra segnali in secondi"
        },
        "entropy_buy_threshold": {
            "min": 0.50,
            "max": 0.70,
            "step": 0.02,
            "type": "float",
            "description": "Soglia entropia per segnali BUY"
        },
        "entropy_sell_threshold": {
            "min": 0.30,
            "max": 0.50,
            "step": 0.02,
            "type": "float",
            "description": "Soglia entropia per segnali SELL"
        },
        "volatility_scale": {
            "min": 0.5,
            "max": 2.0,
            "step": 0.1,
            "type": "float",
            "description": "Scala volatilità per adattamento dinamico"
        }
    },
    
    "risk_parameters": {
        "position_cooldown": {
            "min": 600,
            "max": 1800,
            "step": 300,
            "type": "int",
            "description": "Cooldown tra posizioni in secondi"
        },
        "max_daily_trades": {
            "min": 3,
            "max": 8,
            "step": 1,
            "type": "int",
            "description": "Massimo numero di trade giornalieri"
        },
        "profit_multiplier": {
            "min": 1.5,
            "max": 3.0,
            "step": 0.2,
            "type": "float",
            "description": "Moltiplicatore per Take Profit"
        },
        "max_position_hours": {
            "min": 3,
            "max": 12,
            "step": 1,
            "type": "int",
            "description": "Massimo ore di mantenimento posizione"
        },
        "risk_percent": {
            "min": 0.008,
            "max": 0.020,
            "step": 0.002,
            "type": "float",
            "description": "Percentuale di rischio per trade"
        }
    },
    
    "trailing_stop": {
        "activation_pips": {
            "min": 50,
            "max": 150,
            "step": 20,
            "type": "int",
            "description": "Pips di attivazione trailing stop"
        },
        "step_pips": {
            "min": 25,
            "max": 75,
            "step": 10,
            "type": "int",
            "description": "Step pips trailing stop"
        },
        "lock_percentage": {
            "min": 0.3,
            "max": 0.8,
            "step": 0.1,
            "type": "float",
            "description": "Percentuale di blocco profitto"
        }
    }
}

# ====================================================================================
# SYMBOL-SPECIFIC CONFIGURATIONS
# ====================================================================================

SYMBOL_CONFIGS = {
    "EURUSD": {
        "pip_size": 0.0001,
        "contract_size": 100000,
        "typical_spread": 1.5,
        "min_stop_distance": 120,
        "optimization_priority": "high",
        "trading_sessions": ["London", "New York"],
        "volatility_factor": 1.0
    },
    
    "GBPUSD": {
        "pip_size": 0.0001,
        "contract_size": 100000,
        "typical_spread": 2.0,
        "min_stop_distance": 130,
        "optimization_priority": "high",
        "trading_sessions": ["London", "New York"],
        "volatility_factor": 1.2
    },
    
    "USDJPY": {
        "pip_size": 0.01,
        "contract_size": 100000,
        "typical_spread": 1.0,
        "min_stop_distance": 80,
        "optimization_priority": "medium",
        "trading_sessions": ["Tokyo", "London"],
        "volatility_factor": 0.8
    },
    
    "XAUUSD": {
        "pip_size": 0.01,
        "contract_size": 100,
        "typical_spread": 3.0,
        "min_stop_distance": 150,
        "optimization_priority": "medium",
        "trading_sessions": ["London", "New York"],
        "volatility_factor": 2.0
    },
    
    "NAS100": {
        "pip_size": 0.01,
        "contract_size": 1,
        "typical_spread": 10.0,
        "min_stop_distance": 180,
        "optimization_priority": "low",
        "trading_sessions": ["New York"],
        "volatility_factor": 3.0
    }
}

# ====================================================================================
# OPTIMIZATION SCENARIOS
# ====================================================================================

OPTIMIZATION_SCENARIOS = {
    "conservative_step1": {
        "description": "Ottimizzazione conservativa per Step 1 (8% target)",
        "target": "step1",
        "risk_tolerance": "low",
        "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
        "parameter_ranges": {
            "risk_percent": {"min": 0.008, "max": 0.015, "step": 0.001},
            "max_daily_trades": {"min": 3, "max": 5, "step": 1},
            "profit_multiplier": {"min": 1.8, "max": 2.5, "step": 0.1}
        },
        "fitness_weights": {
            "return": 0.3,
            "drawdown": 0.4,
            "win_rate": 0.2,
            "compliance": 0.1
        }
    },
    
    "aggressive_step2": {
        "description": "Ottimizzazione aggressiva per Step 2 (5% target)",
        "target": "step2",
        "risk_tolerance": "medium",
        "symbols": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
        "parameter_ranges": {
            "risk_percent": {"min": 0.010, "max": 0.020, "step": 0.002},
            "max_daily_trades": {"min": 4, "max": 6, "step": 1},
            "profit_multiplier": {"min": 2.0, "max": 2.8, "step": 0.1}
        },
        "fitness_weights": {
            "return": 0.4,
            "drawdown": 0.3,
            "win_rate": 0.2,
            "compliance": 0.1
        }
    },
    
    "scaling_optimized": {
        "description": "Ottimizzazione per Scaling (10% target)",
        "target": "scaling",
        "risk_tolerance": "high",
        "symbols": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100"],
        "parameter_ranges": {
            "risk_percent": {"min": 0.012, "max": 0.025, "step": 0.002},
            "max_daily_trades": {"min": 5, "max": 8, "step": 1},
            "profit_multiplier": {"min": 2.2, "max": 3.0, "step": 0.2}
        },
        "fitness_weights": {
            "return": 0.5,
            "drawdown": 0.2,
            "win_rate": 0.2,
            "compliance": 0.1
        }
    },
    
    "balanced_all_steps": {
        "description": "Ottimizzazione bilanciata per tutti gli step",
        "target": "all_steps",
        "risk_tolerance": "medium",
        "symbols": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
        "parameter_ranges": {
            "risk_percent": {"min": 0.010, "max": 0.018, "step": 0.002},
            "max_daily_trades": {"min": 3, "max": 6, "step": 1},
            "profit_multiplier": {"min": 1.8, "max": 2.6, "step": 0.2}
        },
        "fitness_weights": {
            "return": 0.35,
            "drawdown": 0.35,
            "win_rate": 0.2,
            "compliance": 0.1
        }
    }
}

# ====================================================================================
# GENETIC ALGORITHM SETTINGS
# ====================================================================================

GENETIC_ALGORITHM_CONFIG = {
    "population_size": 50,
    "generations": 25,
    "mutation_rate": 0.1,
    "crossover_rate": 0.8,
    "selection_method": "tournament",
    "tournament_size": 3,
    "elite_percentage": 0.2,
    "convergence_threshold": 0.001,
    "max_stagnation_generations": 5
}

# ====================================================================================
# UTILITY FUNCTIONS
# ====================================================================================

def get_config_for_scenario(scenario_name: str) -> dict:
    """Restituisce la configurazione per uno scenario specifico"""
    if scenario_name not in OPTIMIZATION_SCENARIOS:
        raise ValueError(f"Scenario '{scenario_name}' non trovato")
    
    base_config = BACKTEST_CONFIG.copy()
    scenario_config = OPTIMIZATION_SCENARIOS[scenario_name]
    
    # Aggiorna configurazione base con scenario specifico
    base_config['symbols'] = scenario_config['symbols']
    base_config['optimization_settings'].update(scenario_config.get('optimization_settings', {}))
    
    return base_config

def get_parameter_ranges_for_scenario(scenario_name: str) -> dict:
    """Restituisce i range di parametri per uno scenario specifico"""
    if scenario_name not in OPTIMIZATION_SCENARIOS:
        raise ValueError(f"Scenario '{scenario_name}' non trovato")
    
    base_ranges = OPTIMIZATION_RANGES.copy()
    scenario_config = OPTIMIZATION_SCENARIOS[scenario_name]
    
    # Aggiorna range con configurazione scenario
    if 'parameter_ranges' in scenario_config:
        for param_category, params in scenario_config['parameter_ranges'].items():
            if param_category not in base_ranges:
                base_ranges[param_category] = {}
            base_ranges[param_category].update(params)
    
    return base_ranges

def save_config_to_file(config: dict, filename: str):
    """Salva la configurazione su file"""
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)

def load_config_from_file(filename: str) -> dict:
    """Carica la configurazione da file"""
    with open(filename, 'r') as f:
        return json.load(f)

def validate_config(config: dict) -> bool:
    """Valida la configurazione"""
    required_sections = ['data_settings', 'account_settings', 'the5ers_rules']
    
    for section in required_sections:
        if section not in config:
            print(f"Sezione mancante: {section}")
            return False
    
    # Valida date
    try:
        start_date = datetime.strptime(config['data_settings']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(config['data_settings']['end_date'], '%Y-%m-%d')
        
        if start_date >= end_date:
            print("Data di inizio deve essere precedente alla data di fine")
            return False
    except ValueError:
        print("Formato date non valido (utilizzare YYYY-MM-DD)")
        return False
    
    # Valida simboli
    if not config['data_settings']['symbols']:
        print("Almeno un simbolo deve essere specificato")
        return False
    
    return True

# ====================================================================================
# REPORT TEMPLATES
# ====================================================================================

REPORT_TEMPLATES = {
    "summary": {
        "title": "Riassunto Ottimizzazione",
        "sections": [
            "optimization_info",
            "best_parameters",
            "performance_metrics",
            "the5ers_compliance",
            "recommendations"
        ]
    },
    
    "detailed": {
        "title": "Report Dettagliato",
        "sections": [
            "optimization_info",
            "parameter_analysis",
            "performance_distribution",
            "trade_analysis",
            "risk_analysis",
            "the5ers_compliance",
            "sensitivity_analysis",
            "recommendations"
        ]
    },
    
    "comparison": {
        "title": "Confronto Scenari",
        "sections": [
            "scenario_comparison",
            "performance_comparison",
            "parameter_comparison",
            "risk_comparison",
            "recommendations"
        ]
    }
}

if __name__ == "__main__":
    # Test della configurazione
    print("Testing configuration...")
    
    # Test scenario loading
    for scenario_name in OPTIMIZATION_SCENARIOS.keys():
        try:
            config = get_config_for_scenario(scenario_name)
            ranges = get_parameter_ranges_for_scenario(scenario_name)
            
            print(f"✓ Scenario '{scenario_name}' caricato correttamente")
            print(f"  - Simboli: {config['symbols']}")
            print(f"  - Parametri da ottimizzare: {len(ranges)}")
            
        except Exception as e:
            print(f"✗ Errore nel caricamento scenario '{scenario_name}': {e}")
    
    # Test validation
    test_config = get_config_for_scenario("balanced_all_steps")
    is_valid = validate_config(test_config)
    print(f"✓ Validazione configurazione: {'OK' if is_valid else 'FAILED'}")
    
    print("Configuration testing completed.")

def get_default_config():
    """Restituisce la configurazione predefinita per il backtest"""
    return {
        "logging": {
            "log_file": "logs/backtest.log",
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
        "quantum_params": {
            "buffer_size": 500,
            "spin_window": 80,
            "min_spin_samples": 30,
            "spin_threshold": 0.32,
            "signal_cooldown": 600,
            "entropy_thresholds": {
                "buy_signal": 0.58,
                "sell_signal": 0.42
            },
            "volatility_scale": 1.0
        },
        "risk_parameters": {
            "magic_number": 147251,
            "position_cooldown": 900,
            "max_daily_trades": 5,
            "max_positions": 1,
            "min_sl_distance_pips": {
                "EURUSD": 120,
                "GBPUSD": 130,
                "USDJPY": 80,
                "XAUUSD": 150,
                "NAS100": 180,
                "default": 150
            },
            "base_sl_pips": {
                "EURUSD": 180,
                "GBPUSD": 190,
                "USDJPY": 120,
                "XAUUSD": 220,
                "NAS100": 250,
                "default": 200
            },
            "profit_multiplier": 2.2,
            "max_position_hours": 6,
            "risk_percent": 0.012,
            "trailing_stop": {
                "enable": True,
                "activation_pips": 100,
                "step_pips": 50,
                "lock_percentage": 0.5
            },
            "max_spread": {
                "EURUSD": 12,
                "GBPUSD": 15,
                "USDJPY": 10,
                "XAUUSD": 40,
                "NAS100": 180,
                "default": 20
            }
        },
        "symbols": {
            "EURUSD": {
                "risk_management": {
                    "contract_size": 0.01,
                    "min_sl_distance_pips": 120,
                    "base_sl_pips": 180,
                    "profit_multiplier": 2.2,
                    "risk_percent": 0.012,
                    "trailing_stop": {
                        "activation_pips": 90,
                        "step_pips": 45
                    }
                },
                "trading_hours": ["09:00-10:30", "14:00-16:00"],
                "comment": "Major pair - high liquidity - avoid spread peaks",
                "quantum_params_override": {
                    "buffer_size": 600,
                    "spin_window": 70,
                    "min_spin_samples": 25,
                    "signal_cooldown": 800,
                    "entropy_thresholds": {
                        "buy_signal": 0.56,
                        "sell_signal": 0.44
                    }
                }
            },
            "GBPUSD": {
                "risk_management": {
                    "contract_size": 0.01,
                    "min_sl_distance_pips": 130,
                    "base_sl_pips": 190,
                    "profit_multiplier": 2.3,
                    "risk_percent": 0.012,
                    "trailing_stop": {
                        "activation_pips": 100,
                        "step_pips": 50
                    }
                },
                "trading_hours": ["09:00-10:30", "14:00-16:00"],
                "comment": "Volatile major - avoid early morning spread spikes",
                "quantum_params_override": {
                    "buffer_size": 500,
                    "spin_window": 65,
                    "min_spin_samples": 25,
                    "signal_cooldown": 900,
                    "entropy_thresholds": {
                        "buy_signal": 0.60,
                        "sell_signal": 0.40
                    }
                }
            },
            "USDJPY": {
                "risk_management": {
                    "contract_size": 0.01,
                    "min_sl_distance_pips": 80,
                    "base_sl_pips": 120,
                    "profit_multiplier": 2.1,
                    "risk_percent": 0.012,
                    "trailing_stop": {
                        "activation_pips": 70,
                        "step_pips": 35
                    }
                },
                "trading_hours": ["02:00-04:00", "09:00-10:30"],
                "comment": "Asian session specialist - adjusted hours",
                "quantum_params_override": {
                    "buffer_size": 400,
                    "spin_window": 60,
                    "min_spin_samples": 20,
                    "signal_cooldown": 700,
                    "entropy_thresholds": {
                        "buy_signal": 0.55,
                        "sell_signal": 0.45
                    }
                }
            },
            "XAUUSD": {
                "risk_management": {
                    "contract_size": 0.01,
                    "min_sl_distance_pips": 150,
                    "base_sl_pips": 220,
                    "profit_multiplier": 2.4,
                    "risk_percent": 0.0010,
                    "trailing_stop": {
                        "activation_pips": 120,
                        "step_pips": 60
                    }
                },
                "trading_hours": ["09:30-10:30", "14:30-15:30"],
                "comment": "Gold - avoid high spread periods",
                "quantum_params_override": {
                    "buffer_size": 300,
                    "spin_window": 50,
                    "min_spin_samples": 20,
                    "signal_cooldown": 1200,
                    "entropy_thresholds": {
                        "buy_signal": 0.62,
                        "sell_signal": 0.38
                    }
                }
            },
            "NAS100": {
                "risk_management": {
                    "contract_size": 0.01,
                    "min_sl_distance_pips": 180,
                    "base_sl_pips": 250,
                    "profit_multiplier": 2.5,
                    "risk_percent": 0.010,
                    "trailing_stop": {
                        "activation_pips": 150,
                        "step_pips": 75
                    }
                },
                "trading_hours": ["14:30-16:00"],
                "comment": "US tech index - high volatility",
                "quantum_params_override": {
                    "buffer_size": 250,
                    "spin_window": 45,
                    "min_spin_samples": 15,
                    "signal_cooldown": 1500,
                    "entropy_thresholds": {
                        "buy_signal": 0.65,
                        "sell_signal": 0.35
                    }
                }
            }
        },
        "THE5ERS_specific": {
            "step1_target": 8,
            "max_daily_loss_percent": 5,
            "max_total_loss_percent": 10,
            "drawdown_protection": {
                "soft_limit": 0.02,
                "hard_limit": 0.05
            }
        },
        "initial_balance": 100000
    }
