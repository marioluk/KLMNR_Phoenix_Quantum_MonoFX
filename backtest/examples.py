#!/usr/bin/env python3
# ====================================================================================
# EXAMPLE USAGE - THE5ERS QUANTUM OPTIMIZATION
# Esempio di utilizzo del sistema di ottimizzazione
# ====================================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json
import logging

# Import nostri moduli
from backtest_engine import BacktestConfig, The5ersRules, QuantumBacktestEngine
from parameter_optimizer import QuantumParameterOptimizer
from results_analyzer import ResultsAnalyzer
from config import get_default_config, OPTIMIZATION_SCENARIOS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_single_backtest():
    """Esempio di singolo backtest"""
    logger.info("=== ESEMPIO: Singolo Backtest ===")
    
    # Configurazione
    config = get_default_config()
    
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-31",  # Solo un mese per test rapido
        initial_balance=100000,
        symbols=["EURUSD"],
        timeframe="M1",
        commission=0.0,
        spread=2.0
    )
    
    the5ers_rules = The5ersRules(
        step1_target=8.0,
        step2_target=5.0,
        scaling_target=10.0,
        max_daily_loss=5.0,
        max_total_loss=10.0,
        min_profitable_days=3
    )
    
    # Esegui backtest
    engine = QuantumBacktestEngine(config, backtest_config, the5ers_rules)
    results = engine.run_backtest()
    
    # Mostra risultati
    logger.info(f"Risultati Backtest:")
    logger.info(f"- Saldo finale: ${results['final_balance']:,.2f}")
    logger.info(f"- Return: {results['total_return_pct']:.2f}%")
    logger.info(f"- Win Rate: {results['win_rate']:.1f}%")
    logger.info(f"- Max Drawdown: {results['max_drawdown']:.2f}%")
    logger.info(f"- Trades totali: {results['total_trades']}")
    logger.info(f"- Step1 raggiunto: {results['the5ers_compliance']['step1_achieved']}")
    
    return results

def example_quick_optimization():
    """Esempio di ottimizzazione rapida"""
    logger.info("=== ESEMPIO: Ottimizzazione Rapida ===")
    
    # Configurazione base
    config = get_default_config()
    
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-02-28",  # Due mesi per test
        initial_balance=100000,
        symbols=["EURUSD", "GBPUSD"],  # Solo 2 simboli
        timeframe="M1",
        commission=0.0,
        spread=2.0
    )
    
    the5ers_rules = The5ersRules(
        step1_target=8.0,
        step2_target=5.0,
        scaling_target=10.0,
        max_daily_loss=5.0,
        max_total_loss=10.0,
        min_profitable_days=3
    )
    
    # Inizializza optimizer
    optimizer = QuantumParameterOptimizer(config, backtest_config, the5ers_rules)
    
    # Esegui ottimizzazione rapida (solo 20 combinazioni)
    logger.info("Avvio ottimizzazione (20 combinazioni)...")
    results = optimizer.optimize_grid_search(max_combinations=20)
    
    # Mostra risultati
    logger.info(f"Ottimizzazione completata! {len(results)} risultati ottenuti")
    
    if results:
        best = results[0]
        logger.info(f"Migliore configurazione:")
        logger.info(f"- Fitness Score: {best.fitness_score:.4f}")
        logger.info(f"- Return: {best.performance['total_return_pct']:.2f}%")
        logger.info(f"- Win Rate: {best.performance['win_rate']:.1f}%")
        logger.info(f"- Drawdown: {best.performance['max_drawdown']:.2f}%")
        logger.info(f"- Step1 raggiunto: {best.performance['the5ers_compliance']['step1_achieved']}")
        
        # Salva risultati
        optimizer.save_optimization_results("example_results.json")
        logger.info("Risultati salvati in: example_results.json")
        
        return results
    else:
        logger.warning("Nessun risultato ottenuto")
        return []

def example_results_analysis():
    """Esempio di analisi risultati"""
    logger.info("=== ESEMPIO: Analisi Risultati ===")
    
    # Prima esegui un'ottimizzazione rapida
    results = example_quick_optimization()
    
    if not results:
        logger.warning("Nessun risultato da analizzare")
        return
    
    # Analizza i risultati
    analyzer = ResultsAnalyzer(results_data=results)
    
    # Genera report completo
    logger.info("Generazione report completo...")
    analyzer.generate_comprehensive_report("example_reports")
    
    # Ottieni raccomandazioni
    recommendations = analyzer.get_optimization_recommendations()
    
    logger.info("Raccomandazioni:")
    for i, rec in enumerate(recommendations, 1):
        logger.info(f"{i}. {rec}")
    
    # Esporta migliore configurazione
    best_config = analyzer.export_best_config("example_best_config.json")
    
    logger.info("Analisi completata!")
    logger.info("Files generati:")
    logger.info("- example_reports/ (grafici e report)")
    logger.info("- example_best_config.json (migliore configurazione)")
    
    return analyzer

def example_genetic_optimization():
    """Esempio di ottimizzazione genetica"""
    logger.info("=== ESEMPIO: Ottimizzazione Genetica ===")
    
    # Configurazione più semplice per test rapido
    config = get_default_config()
    
    backtest_config = BacktestConfig(
        start_date="2024-01-01",
        end_date="2024-01-31",  # Solo un mese
        initial_balance=100000,
        symbols=["EURUSD"],  # Solo 1 simbolo
        timeframe="M1",
        commission=0.0,
        spread=2.0
    )
    
    the5ers_rules = The5ersRules(
        step1_target=8.0,
        step2_target=5.0,
        scaling_target=10.0,
        max_daily_loss=5.0,
        max_total_loss=10.0,
        min_profitable_days=3
    )
    
    # Inizializza optimizer
    optimizer = QuantumParameterOptimizer(config, backtest_config, the5ers_rules)
    
    # Esegui ottimizzazione genetica (piccola per test)
    logger.info("Avvio ottimizzazione genetica...")
    results = optimizer.optimize_genetic_algorithm(
        population_size=10,  # Piccola popolazione
        generations=5,       # Poche generazioni
        mutation_rate=0.1
    )
    
    # Mostra risultati
    logger.info(f"Ottimizzazione genetica completata! {len(results)} risultati")
    
    if results:
        best = results[0]
        logger.info(f"Migliore configurazione:")
        logger.info(f"- Fitness Score: {best.fitness_score:.4f}")
        logger.info(f"- Return: {best.performance['total_return_pct']:.2f}%")
        logger.info(f"- Win Rate: {best.performance['win_rate']:.1f}%")
        
        # Salva risultati
        optimizer.save_optimization_results("example_genetic_results.json")
        logger.info("Risultati salvati in: example_genetic_results.json")
    
    return results

def example_scenario_comparison():
    """Esempio di confronto scenari"""
    logger.info("=== ESEMPIO: Confronto Scenari ===")
    
    # Simula diversi scenari salvando risultati
    scenarios = ["conservative", "balanced", "aggressive"]
    result_files = []
    
    for scenario in scenarios:
        logger.info(f"Simulazione scenario: {scenario}")
        
        # Ottimizzazione rapida per scenario
        config = get_default_config()
        
        backtest_config = BacktestConfig(
            start_date="2024-01-01",
            end_date="2024-01-31",
            initial_balance=100000,
            symbols=["EURUSD"],
            timeframe="M1",
            commission=0.0,
            spread=2.0
        )
        
        the5ers_rules = The5ersRules(
            step1_target=8.0,
            step2_target=5.0,
            scaling_target=10.0,
            max_daily_loss=5.0,
            max_total_loss=10.0,
            min_profitable_days=3
        )
        
        optimizer = QuantumParameterOptimizer(config, backtest_config, the5ers_rules)
        results = optimizer.optimize_grid_search(max_combinations=10)
        
        if results:
            filename = f"example_{scenario}_results.json"
            optimizer.save_optimization_results(filename)
            result_files.append(filename)
            logger.info(f"Scenario {scenario} completato - {len(results)} risultati")
    
    # Confronta risultati
    if len(result_files) > 1:
        logger.info("Confronto scenari...")
        from results_analyzer import compare_optimization_results
        compare_optimization_results(result_files, "example_comparisons")
        logger.info("Confronto salvato in: example_comparisons/")
    
    return result_files

def main():
    """Funzione principale con menu interattivo"""
    logger.info("=== THE5ERS QUANTUM OPTIMIZATION - EXAMPLES ===")
    
    examples = {
        "1": ("Singolo Backtest", example_single_backtest),
        "2": ("Ottimizzazione Rapida", example_quick_optimization),
        "3": ("Analisi Risultati", example_results_analysis),
        "4": ("Ottimizzazione Genetica", example_genetic_optimization),
        "5": ("Confronto Scenari", example_scenario_comparison)
    }
    
    print("\nEsempi disponibili:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    print("\nSeleziona un esempio (1-5) o 'all' per eseguire tutti:")
    choice = input("> ").strip().lower()
    
    if choice == 'all':
        for key, (name, func) in examples.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Esecuzione: {name}")
            logger.info(f"{'='*60}")
            try:
                func()
            except Exception as e:
                logger.error(f"Errore in {name}: {e}")
                
    elif choice in examples:
        name, func = examples[choice]
        logger.info(f"Esecuzione: {name}")
        try:
            func()
        except Exception as e:
            logger.error(f"Errore: {e}")
    else:
        logger.error("Scelta non valida")

if __name__ == "__main__":
    main()
