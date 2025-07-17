#!/usr/bin/env python3
# ====================================================================================
# MAIN OPTIMIZATION SCRIPT - THE5ERS QUANTUM ALGORITHM
# Script principale per l'ottimizzazione parametri High Stakes Challenge
# ====================================================================================

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest_engine import BacktestConfig, The5ersRules, HistoricalDataHandler
from parameter_optimizer import QuantumParameterOptimizer, OptimizationAnalyzer

# ====================================================================================
# CONFIGURAZIONE LOGGING
# ====================================================================================

def setup_logging():
    """Configura il logging per l'ottimizzazione"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# ====================================================================================
# CONFIGURAZIONI PREDEFINITE
# ====================================================================================

def get_default_config():
    """Restituisce la configurazione base per l'ottimizzazione"""
    return {
        "logging": {
            "log_file": "logs/optimization.log",
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

def get_optimization_scenarios():
    """Definisce diversi scenari di ottimizzazione"""
    return {
        "conservative": {
            "description": "Ottimizzazione conservativa per Step 1",
            "backtest_config": BacktestConfig(
                start_date="2024-01-01",
                end_date="2024-06-30",
                initial_balance=100000,
                symbols=["EURUSD", "GBPUSD", "USDJPY"],
                timeframe="M1",
                commission=0.0,
                spread=2.0
            ),
            "the5ers_rules": The5ersRules(
                step1_target=8.0,
                step2_target=5.0,
                scaling_target=10.0,
                max_daily_loss=5.0,
                max_total_loss=10.0,
                min_profitable_days=3,
                max_trading_period_days=999
            ),
            "optimization_params": {
                "method": "grid_search",
                "max_combinations": 500
            }
        },
        "aggressive": {
            "description": "Ottimizzazione aggressiva per Scaling",
            "backtest_config": BacktestConfig(
                start_date="2024-01-01",
                end_date="2024-06-30",
                initial_balance=100000,
                symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100"],
                timeframe="M1",
                commission=0.0,
                spread=2.0
            ),
            "the5ers_rules": The5ersRules(
                step1_target=8.0,
                step2_target=5.0,
                scaling_target=10.0,
                max_daily_loss=5.0,
                max_total_loss=10.0,
                min_profitable_days=3,
                max_trading_period_days=999
            ),
            "optimization_params": {
                "method": "genetic_algorithm",
                "population_size": 30,
                "generations": 15,
                "mutation_rate": 0.1
            }
        },
        "balanced": {
            "description": "Ottimizzazione bilanciata per Step 1 e 2",
            "backtest_config": BacktestConfig(
                start_date="2024-01-01",
                end_date="2024-06-30",
                initial_balance=100000,
                symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
                timeframe="M1",
                commission=0.0,
                spread=2.0
            ),
            "the5ers_rules": The5ersRules(
                step1_target=8.0,
                step2_target=5.0,
                scaling_target=10.0,
                max_daily_loss=5.0,
                max_total_loss=10.0,
                min_profitable_days=3,
                max_trading_period_days=999
            ),
            "optimization_params": {
                "method": "grid_search",
                "max_combinations": 800
            }
        }
    }

# ====================================================================================
# FUNZIONI PRINCIPALI
# ====================================================================================

def run_optimization(scenario_name: str, config: dict, logger: logging.Logger):
    """Esegue l'ottimizzazione per uno scenario specifico"""
    
    scenarios = get_optimization_scenarios()
    
    if scenario_name not in scenarios:
        logger.error(f"Scenario {scenario_name} non trovato")
        return None
        
    scenario = scenarios[scenario_name]
    logger.info(f"Avvio ottimizzazione scenario: {scenario_name}")
    logger.info(f"Descrizione: {scenario['description']}")
    
    # Inizializza optimizer
    optimizer = QuantumParameterOptimizer(
        base_config=config,
        backtest_config=scenario['backtest_config'],
        the5ers_rules=scenario['the5ers_rules']
    )
    
    # Esegui ottimizzazione
    opt_params = scenario['optimization_params']
    
    if opt_params['method'] == 'grid_search':
        results = optimizer.optimize_grid_search(
            max_combinations=opt_params['max_combinations']
        )
    elif opt_params['method'] == 'genetic_algorithm':
        results = optimizer.optimize_genetic_algorithm(
            population_size=opt_params['population_size'],
            generations=opt_params['generations'],
            mutation_rate=opt_params['mutation_rate']
        )
    else:
        logger.error(f"Metodo di ottimizzazione non supportato: {opt_params['method']}")
        return None
    
    # Salva risultati
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"optimization_{scenario_name}_{timestamp}.json"
    
    optimizer.save_optimization_results(str(results_file))
    
    # Genera report
    analyzer = OptimizationAnalyzer(results)
    report = analyzer.generate_report()
    
    report_file = results_dir / f"report_{scenario_name}_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report salvato in: {report_file}")
    
    return {
        'results': results,
        'report': report,
        'results_file': str(results_file),
        'report_file': str(report_file)
    }

def print_optimization_summary(results: list, scenario_name: str, logger: logging.Logger):
    """Stampa un riassunto dei risultati di ottimizzazione"""
    
    if not results:
        logger.warning("Nessun risultato da mostrare")
        return
    
    logger.info(f"\n{'='*80}")
    logger.info(f"RIASSUNTO OTTIMIZZAZIONE - SCENARIO: {scenario_name.upper()}")
    logger.info(f"{'='*80}")
    
    # Migliori 5 risultati
    best_results = results[:5]
    
    logger.info(f"Migliori {len(best_results)} combinazioni di parametri:")
    logger.info("-" * 80)
    
    for i, result in enumerate(best_results, 1):
        perf = result.performance
        logger.info(f"\n#{i} - Fitness Score: {result.fitness_score:.4f} | The5ers Score: {result.the5ers_score:.2f}")
        logger.info(f"    Return: {perf['total_return_pct']:.2f}% | Win Rate: {perf['win_rate']:.1f}% | Drawdown: {perf['max_drawdown']:.2f}%")
        logger.info(f"    Trades: {perf['total_trades']} | Sharpe: {perf['sharpe_ratio']:.2f}")
        
        # Compliance The5ers
        comp = perf['the5ers_compliance']
        compliance_status = []
        if comp['step1_achieved']: compliance_status.append("Step1✓")
        if comp['step2_achieved']: compliance_status.append("Step2✓")
        if comp['scaling_achieved']: compliance_status.append("Scaling✓")
        if comp['daily_loss_violated']: compliance_status.append("DailyLoss✗")
        if comp['total_loss_violated']: compliance_status.append("TotalLoss✗")
        if comp['min_profitable_days']: compliance_status.append("ProfDays✓")
        
        logger.info(f"    Compliance: {' | '.join(compliance_status)}")
        
        # Parametri chiave
        params = result.parameters
        key_params = []
        for key, value in params.items():
            if 'quantum_params' in key:
                key_params.append(f"{key.split('.')[-1]}={value}")
        
        if key_params:
            logger.info(f"    Key Params: {' | '.join(key_params[:3])}")
    
    logger.info(f"\n{'='*80}")

def main():
    """Funzione principale"""
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("Avvio sistema di ottimizzazione The5ers Quantum Algorithm")
    logger.info("=" * 60)
    
    # Carica configurazione base
    config = get_default_config()
    
    # Scenarios disponibili
    scenarios = get_optimization_scenarios()
    scenario_names = list(scenarios.keys())
    
    logger.info(f"Scenari disponibili: {', '.join(scenario_names)}")
    
    # Esegui ottimizzazione per scenario selezionato
    scenario_to_run = "balanced"  # Cambia questo per testare diversi scenari
    
    if scenario_to_run not in scenario_names:
        logger.error(f"Scenario '{scenario_to_run}' non valido")
        return
    
    logger.info(f"Esecuzione scenario: {scenario_to_run}")
    
    try:
        # Esegui ottimizzazione
        optimization_result = run_optimization(scenario_to_run, config, logger)
        
        if optimization_result:
            results = optimization_result['results']
            report = optimization_result['report']
            
            # Stampa riassunto
            print_optimization_summary(results, scenario_to_run, logger)
            
            # Stampa raccomandazioni
            recommendations = report.get('recommendations', [])
            if recommendations:
                logger.info("\nRACCOMANDAZIONI:")
                for i, rec in enumerate(recommendations, 1):
                    logger.info(f"{i}. {rec}")
            
            # Stampa percorsi file
            logger.info(f"\nFile risultati: {optimization_result['results_file']}")
            logger.info(f"File report: {optimization_result['report_file']}")
            
        else:
            logger.error("Ottimizzazione fallita")
            
    except Exception as e:
        logger.error(f"Errore durante l'ottimizzazione: {str(e)}", exc_info=True)
    
    logger.info("Ottimizzazione completata")

if __name__ == "__main__":
    main()
