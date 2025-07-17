# ====================================================================================
# PARAMETER OPTIMIZER - THE5ERS QUANTUM ALGORITHM
# Sistema di ottimizzazione automatica parametri per The5ers Challenge
# ====================================================================================

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import itertools
from itertools import product
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import pickle
import os
from pathlib import Path

# Import del nostro sistema di backtest
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_backtest import (
    get_the5ers_config, BacktestConfig, The5ersRules, 
    WorkingBacktestEngine
)

# ====================================================================================
# CONFIGURAZIONE OTTIMIZZAZIONE
# ====================================================================================

@dataclass
class OptimizationConfig:
    """Configurazione per l'ottimizzazione parametri"""
    # Periodo di test
    start_date: str = "2024-01-01"
    end_date: str = "2024-01-31"  # 1 mese per iniziare
    initial_balance: float = 100000
    symbols: List[str] = None
    timeframe: str = "M15"
    
    # Parametri ottimizzazione
    optimization_method: str = "grid_search"  # grid_search, genetic, random
    max_iterations: int = 100
    population_size: int = 20  # Per genetic algorithm
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    
    # Obiettivi
    primary_objective: str = "the5ers_score"  # total_return, sharpe_ratio, the5ers_score
    minimize_drawdown: bool = True
    min_trades: int = 5  # Minimo trades per validità
    
    # Vincoli The5ers
    target_step: int = 1  # 1, 2, o scaling
    max_acceptable_drawdown: float = 8.0  # Sotto limite 10%
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["EURUSD", "GBPUSD", "XAUUSD"]

@dataclass 
class ParameterRange:
    """Range di un parametro da ottimizzare"""
    name: str
    min_value: float
    max_value: float
    step: float = None
    values: List[float] = None
    parameter_type: str = "float"  # float, int, choice
    
    def get_values(self) -> List[float]:
        """Ottieni lista valori per il parametro"""
        if self.values is not None:
            return self.values
        elif self.step is not None:
            if self.parameter_type == "int":
                return list(range(int(self.min_value), int(self.max_value) + 1, int(self.step)))
            else:
                return list(np.arange(self.min_value, self.max_value + self.step, self.step))
        else:
            # Default: 10 valori nel range
            return list(np.linspace(self.min_value, self.max_value, 10))

@dataclass
class OptimizationResult:
    """Risultato di una singola ottimizzazione"""
    parameters: Dict[str, float]
    backtest_results: Dict[str, Any]
    objective_score: float
    the5ers_score: float
    execution_time: float
    is_valid: bool = True
    error_message: str = ""

class QuantumParameterOptimizer:
    """Ottimizzatore avanzato di parametri per l'algoritmo quantum"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.results_dir = Path("optimization_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Definisce i parametri da ottimizzare
        self.parameter_ranges = self._define_parameter_ranges()
        
        # Risultati ottimizzazione
        self.optimization_results = []
        
        # Configurazione base e regole The5ers
        self.base_config = get_the5ers_config()
        self.backtest_config = BacktestConfig(
            start_date=config.start_date,
            end_date=config.end_date,
            initial_balance=config.initial_balance,
            symbols=config.symbols,
            timeframe=config.timeframe
        )
        self.the5ers_rules = The5ersRules()
        
    def _define_parameter_ranges(self) -> List[ParameterRange]:
        """Definisce i range dei parametri da ottimizzare"""
        return [
            # Parametri Quantum Engine
            ParameterRange('quantum_params.buffer_size', 200, 800, 100, 'int'),
            ParameterRange('quantum_params.spin_window', 30, 120, 10, 'int'),
            ParameterRange('quantum_params.min_spin_samples', 10, 50, 5, 'int'),
            ParameterRange('quantum_params.spin_threshold', 0.15, 0.45, 0.05, 'float'),
            ParameterRange('quantum_params.signal_cooldown', 300, 1800, 300, 'int'),
            ParameterRange('quantum_params.entropy_thresholds.buy_signal', 0.50, 0.70, 0.02, 'float'),
            ParameterRange('quantum_params.entropy_thresholds.sell_signal', 0.30, 0.50, 0.02, 'float'),
            ParameterRange('quantum_params.volatility_scale', 0.5, 2.0, 0.1, 'float'),
            
            # Parametri Risk Management
            ParameterRange('risk_parameters.position_cooldown', 600, 1800, 300, 'int'),
            ParameterRange('risk_parameters.max_daily_trades', 3, 8, 1, 'int'),
            ParameterRange('risk_parameters.profit_multiplier', 1.5, 3.0, 0.2, 'float'),
            ParameterRange('risk_parameters.max_position_hours', 3, 12, 1, 'int'),
            ParameterRange('risk_parameters.risk_percent', 0.008, 0.020, 0.002, 'float'),
            
            # Parametri Trailing Stop
            ParameterRange('risk_parameters.trailing_stop.activation_pips', 50, 150, 20, 'int'),
            ParameterRange('risk_parameters.trailing_stop.step_pips', 25, 75, 10, 'int'),
            ParameterRange('risk_parameters.trailing_stop.lock_percentage', 0.3, 0.8, 0.1, 'float'),
        ]
        
    def optimize_grid_search(self, max_combinations: int = 1000) -> List[OptimizationResult]:
        """
        Ottimizzazione tramite grid search
        
        Args:
            max_combinations: Numero massimo di combinazioni da testare
            
        Returns:
            Lista di risultati ordinati per performance
        """
        self.logger.info("Avvio ottimizzazione Grid Search...")
        
        # Genera tutte le combinazioni possibili
        param_combinations = self._generate_parameter_combinations(max_combinations)
        
        self.logger.info(f"Testing {len(param_combinations)} combinazioni di parametri")
        
        # Esegue il backtest per ogni combinazione
        results = []
        
        # Utilizzo ProcessPoolExecutor per parallelizzazione
        with ProcessPoolExecutor(max_workers=4) as executor:
            # Invia tutti i job
            future_to_params = {
                executor.submit(self._evaluate_parameters, params): params 
                for params in param_combinations
            }
            
            # Raccogli i risultati
            for i, future in enumerate(as_completed(future_to_params)):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    
                    # Progress report
                    if (i + 1) % 50 == 0:
                        self.logger.info(f"Completate {i + 1}/{len(param_combinations)} combinazioni")
                        
                except Exception as e:
                    self.logger.error(f"Errore nella valutazione parametri: {e}")
                    
        # Ordina per objective score
        results.sort(key=lambda x: x.objective_score if x.is_valid else -999999, reverse=True)
        self.optimization_results = results
        
        self.logger.info(f"Ottimizzazione completata! Migliori {len(results)} risultati trovati.")
        
        return results
        
    def optimize_genetic_algorithm(self, population_size: int = 50, generations: int = 20,
                                 mutation_rate: float = 0.1) -> List[OptimizationResult]:
        """
        Ottimizzazione tramite algoritmo genetico
        
        Args:
            population_size: Dimensione della popolazione
            generations: Numero di generazioni
            mutation_rate: Tasso di mutazione
            
        Returns:
            Lista di risultati ordinati per performance
        """
        self.logger.info("Avvio ottimizzazione Genetic Algorithm...")
        
        # Genera popolazione iniziale
        population = self._generate_initial_population(population_size)
        
        best_results = []
        
        for generation in range(generations):
            self.logger.info(f"Generazione {generation + 1}/{generations}")
            
            # Valuta la popolazione
            generation_results = []
            for individual in population:
                result = self._evaluate_parameters(individual)
                if result:
                    generation_results.append(result)
                    
            # Ordina per objective score
            generation_results.sort(key=lambda x: x.objective_score if x.is_valid else -999999, reverse=True)
            
            # Salva il miglior risultato
            if generation_results:
                best_results.append(generation_results[0])
                self.logger.info(f"Miglior score generazione {generation + 1}: {generation_results[0].objective_score:.4f}")
                
            # Selezione e riproduzione
            if generation < generations - 1:
                population = self._evolve_population(generation_results, population_size, mutation_rate)
                
        # Ordina tutti i risultati
        best_results.sort(key=lambda x: x.objective_score if x.is_valid else -999999, reverse=True)
        self.optimization_results = best_results
        
        self.logger.info("Ottimizzazione genetica completata!")
        
        return best_results
        
    def _generate_parameter_combinations(self, max_combinations: int) -> List[Dict]:
        """Genera combinazioni di parametri per grid search"""
        # Crea liste di valori per ogni parametro
        param_values = {}
        for param_range in self.parameter_ranges:
            if param_range.param_type == 'int':
                values = list(range(int(param_range.min_value), 
                                  int(param_range.max_value) + 1, 
                                  int(param_range.step)))
            else:
                values = list(np.arange(param_range.min_value, 
                                      param_range.max_value + param_range.step, 
                                      param_range.step))
            param_values[param_range.name] = values
            
        # Genera tutte le combinazioni
        param_names = list(param_values.keys())
        param_combinations = list(product(*param_values.values()))
        
        # Limita il numero di combinazioni
        if len(param_combinations) > max_combinations:
            # Campiona casualmente
            indices = np.random.choice(len(param_combinations), max_combinations, replace=False)
            param_combinations = [param_combinations[i] for i in indices]
            
        # Converte in dizionari
        combinations = []
        for combination in param_combinations:
            param_dict = dict(zip(param_names, combination))
            combinations.append(param_dict)
            
        return combinations
        
    def _generate_initial_population(self, population_size: int) -> List[Dict]:
        """Genera popolazione iniziale per algoritmo genetico"""
        population = []
        
        for _ in range(population_size):
            individual = {}
            for param_range in self.parameter_ranges:
                if param_range.param_type == 'int':
                    value = np.random.randint(param_range.min_value, param_range.max_value + 1)
                else:
                    value = np.random.uniform(param_range.min_value, param_range.max_value)
                individual[param_range.name] = value
                
            population.append(individual)
            
        return population
        
    def _evolve_population(self, generation_results: List[OptimizationResult], 
                          population_size: int, mutation_rate: float) -> List[Dict]:
        """Evolve la popolazione per la prossima generazione"""
        new_population = []
        
        # Mantieni i migliori 20%
        elite_size = int(population_size * 0.2)
        for i in range(elite_size):
            new_population.append(generation_results[i].parameters.copy())
            
        # Genera il resto tramite crossover e mutazione
        while len(new_population) < population_size:
            # Selezione dei genitori (tournament selection)
            parent1 = self._tournament_selection(generation_results)
            parent2 = self._tournament_selection(generation_results)
            
            # Crossover
            child = self._crossover(parent1.parameters, parent2.parameters)
            
            # Mutazione
            if np.random.random() < mutation_rate:
                child = self._mutate(child)
                
            new_population.append(child)
            
        return new_population
        
    def _tournament_selection(self, generation_results: List[OptimizationResult]) -> OptimizationResult:
        """Selezione tournament per algoritmo genetico"""
        tournament_size = 3
        tournament = np.random.choice(generation_results, tournament_size, replace=False)
        return max(tournament, key=lambda x: x.objective_score if x.is_valid else -999999)
        
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Crossover di due genitori"""
        child = {}
        for key in parent1.keys():
            if np.random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
        
    def _mutate(self, individual: Dict) -> Dict:
        """Mutazione di un individuo"""
        mutated = individual.copy()
        
        # Seleziona parametro casuale da mutare
        param_to_mutate = np.random.choice(list(mutated.keys()))
        
        # Trova il range del parametro
        param_range = next(p for p in self.parameter_ranges if p.name == param_to_mutate)
        
        # Applica mutazione
        if param_range.param_type == 'int':
            mutated[param_to_mutate] = np.random.randint(param_range.min_value, 
                                                        param_range.max_value + 1)
        else:
            mutated[param_to_mutate] = np.random.uniform(param_range.min_value, 
                                                        param_range.max_value)
            
        return mutated
        
    def _evaluate_parameters(self, parameters: Dict) -> OptimizationResult:
        """Valuta un set di parametri"""
        try:
            start_time = time.time()
            
            # Crea configurazione con i nuovi parametri
            config = self._apply_parameters_to_config(parameters)
            
            # Esegue il backtest
            backtest_engine = WorkingBacktestEngine(config, self.backtest_config, self.the5ers_rules)
            results = backtest_engine.run_backtest()
            
            execution_time = time.time() - start_time
            
            # Verifica validità risultati
            if results['total_trades'] < self.config.min_trades:
                return OptimizationResult(
                    parameters=parameters,
                    backtest_results=results,
                    objective_score=0,
                    the5ers_score=0,
                    execution_time=execution_time,
                    is_valid=False,
                    error_message=f"Troppi pochi trades: {results['total_trades']}"
                )
            
            # Calcola score The5ers
            the5ers_score = self._calculate_the5ers_score(results)
            
            # Calcola objective score
            if self.config.primary_objective == "the5ers_score":
                objective_score = the5ers_score
            elif self.config.primary_objective == "total_return":
                objective_score = results['total_return_pct']
            elif self.config.primary_objective == "sharpe_ratio":
                objective_score = results.get('sharpe_ratio', 0)
            else:
                objective_score = the5ers_score
            
            return OptimizationResult(
                parameters=parameters,
                backtest_results=results,
                objective_score=objective_score,
                the5ers_score=the5ers_score,
                execution_time=execution_time,
                is_valid=True
            )
            
        except Exception as e:
            self.logger.error(f"Errore nella valutazione parametri: {e}")
            return OptimizationResult(
                parameters=parameters,
                backtest_results={},
                objective_score=0,
                the5ers_score=0,
                execution_time=0,
                is_valid=False,
                error_message=str(e)
            )
            
    def _apply_parameters_to_config(self, parameters: Dict) -> Dict:
        """Applica i parametri alla configurazione base"""
        config = self.base_config.copy()
        
        for param_name, value in parameters.items():
            # Naviga nella struttura annidata
            keys = param_name.split('.')
            current = config
            
            # Naviga fino al penultimo livello
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
                
            # Imposta il valore
            current[keys[-1]] = value
            
        return config
        
    def _calculate_the5ers_score(self, results: Dict) -> float:
        """
        Calcola uno score specifico per The5ers Challenge
        
        Criteri:
        - Step 1 achieved: +100 punti
        - Step 2 achieved: +50 punti (solo se Step 1 ok)
        - Scaling achieved: +200 punti (solo se Step 1 e 2 ok)
        - Daily loss violation: -500 punti
        - Total loss violation: -1000 punti
        - Min profitable days: +50 punti se raggiunto
        - Win rate bonus: +1 punto per ogni % sopra 50%
        - Drawdown penalty: -10 punti per ogni % di drawdown
        """
        score = 0
        compliance = results['the5ers_compliance']
        
        # Premi per target raggiunti
        if compliance['step1_achieved']:
            score += 100
            if compliance['step2_achieved']:
                score += 50
                if compliance['scaling_achieved']:
                    score += 200
                    
        # Penalità per violazioni
        if compliance['daily_loss_violated']:
            score -= 500
        if compliance['total_loss_violated']:
            score -= 1000
            
        # Bonus per giorni profittevoli
        if compliance['min_profitable_days']:
            score += 50
            
        # Bonus win rate
        win_rate = results['win_rate']
        if win_rate > 50:
            score += (win_rate - 50)
            
        # Penalità drawdown
        score -= results['max_drawdown'] * 10
        
        # Bonus per return elevato (ma sostenibile)
        if results['total_return_pct'] > 0:
            score += min(results['total_return_pct'], 20)  # Cap a 20%
            
        return score
        
    def _calculate_fitness_score(self, results: Dict) -> float:
        """Calcola un fitness score generale (deprecato - usa objective_score)"""
        # Combina diversi fattori
        return_score = results.get('total_return_pct', 0) * 0.3
        win_rate_score = results.get('win_rate', 0) * 0.2
        drawdown_score = max(0, (20 - results.get('max_drawdown', 0))) * 0.2
        trades_score = min(results.get('total_trades', 0), 100) * 0.1
        sharpe_score = results.get('sharpe_ratio', 0) * 0.2
        
        return return_score + win_rate_score + drawdown_score + trades_score + sharpe_score
        
    def _calculate_fitness_score(self, results: Dict) -> float:
        """Calcola un fitness score generale"""
        # Combina diversi fattori
        return_score = results['total_return_pct'] * 0.3
        win_rate_score = results['win_rate'] * 0.2
        drawdown_score = max(0, (20 - results['max_drawdown'])) * 0.2
        trades_score = min(results['total_trades'], 100) * 0.1
        sharpe_score = results['sharpe_ratio'] * 0.2
        
        return return_score + win_rate_score + drawdown_score + trades_score + sharpe_score
        
    def save_optimization_results(self, filename: str):
        """Salva i risultati dell'ottimizzazione"""
        results_data = []
        
        for result in self.optimization_results:
            results_data.append({
                'parameters': result.parameters,
                'performance': {
                    'total_return_pct': result.backtest_results.get('total_return_pct', 0),
                    'win_rate': result.backtest_results.get('win_rate', 0),
                    'max_drawdown': result.backtest_results.get('max_drawdown', 0),
                    'total_trades': result.backtest_results.get('total_trades', 0),
                    'sharpe_ratio': result.backtest_results.get('sharpe_ratio', 0)
                },
                'the5ers_score': result.the5ers_score,
                'objective_score': result.objective_score,
                'the5ers_compliance': result.backtest_results.get('the5ers_compliance', {}),
                'is_valid': result.is_valid,
                'execution_time': result.execution_time
            })
            
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
            
        self.logger.info(f"Risultati salvati in {filename}")
        
    def get_best_parameters(self, n: int = 5) -> List[Dict]:
        """Restituisce i migliori N set di parametri"""
        if not self.optimization_results:
            return []
            
        best_results = self.optimization_results[:n]
        return [result.parameters for result in best_results]
        
    def analyze_parameter_sensitivity(self) -> Dict:
        """Analizza la sensibilità dei parametri"""
        if not self.optimization_results:
            return {}
            
        sensitivity_analysis = {}
        
        for param_range in self.parameter_ranges:
            param_name = param_range.name
            
            # Raccogli tutti i valori e performance
            param_values = []
            objective_scores = []
            
            for result in self.optimization_results:
                if param_name in result.parameters:
                    param_values.append(result.parameters[param_name])
                    objective_scores.append(result.objective_score)
                    
            if param_values:
                # Calcola correlazione
                correlation = np.corrcoef(param_values, objective_scores)[0, 1]
                
                # Trova valore ottimale
                best_idx = np.argmax(objective_scores)
                optimal_value = param_values[best_idx]
                
                sensitivity_analysis[param_name] = {
                    'correlation': correlation,
                    'optimal_value': optimal_value,
                    'range': (min(param_values), max(param_values)),
                    'importance': abs(correlation)
                }
                
        return sensitivity_analysis

# ====================================================================================
# ANALISI RISULTATI
# ====================================================================================

class OptimizationAnalyzer:
    """Analizza i risultati dell'ottimizzazione"""
    
    def __init__(self, results: List[OptimizationResult]):
        self.results = results
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self) -> Dict:
        """Genera un report completo dell'ottimizzazione"""
        if not self.results:
            return {}
            
        report = {
            'summary': self._generate_summary(),
            'best_parameters': self._get_best_parameters(),
            'performance_distribution': self._analyze_performance_distribution(),
            'parameter_analysis': self._analyze_parameter_importance(),
            'the5ers_compliance': self._analyze_the5ers_compliance(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
        
    def _generate_summary(self) -> Dict:
        """Genera un riassunto generale"""
        objective_scores = [r.objective_score for r in self.results if r.is_valid]
        the5ers_scores = [r.the5ers_score for r in self.results if r.is_valid]
        returns = [r.backtest_results.get('total_return_pct', 0) for r in self.results if r.is_valid]
        
        if not objective_scores:
            return {
                'total_combinations_tested': len(self.results),
                'valid_results': 0,
                'message': 'Nessun risultato valido trovato'
            }
        
        return {
            'total_combinations_tested': len(self.results),
            'valid_results': len(objective_scores),
            'best_objective_score': max(objective_scores),
            'average_objective_score': np.mean(objective_scores),
            'best_the5ers_score': max(the5ers_scores),
            'average_the5ers_score': np.mean(the5ers_scores),
            'best_return_pct': max(returns),
            'average_return_pct': np.mean(returns),
            'positive_return_rate': len([r for r in returns if r > 0]) / len(returns) * 100 if returns else 0
        }
        
    def _get_best_parameters(self, n: int = 5) -> List[Dict]:
        """Restituisce i migliori parametri"""
        valid_results = [r for r in self.results if r.is_valid][:n]
        return [
            {
                'parameters': result.parameters,
                'performance': {
                    'total_return_pct': result.backtest_results.get('total_return_pct', 0),
                    'win_rate': result.backtest_results.get('win_rate', 0),
                    'max_drawdown': result.backtest_results.get('max_drawdown', 0),
                    'total_trades': result.backtest_results.get('total_trades', 0)
                },
                'objective_score': result.objective_score,
                'the5ers_score': result.the5ers_score,
                'execution_time': result.execution_time
            }
            for result in valid_results
        ]
        
    def _analyze_performance_distribution(self) -> Dict:
        """Analizza la distribuzione delle performance"""
        valid_results = [r for r in self.results if r.is_valid]
        
        if not valid_results:
            return {'message': 'Nessun risultato valido per l\'analisi'}
        
        returns = [r.backtest_results.get('total_return_pct', 0) for r in valid_results]
        win_rates = [r.backtest_results.get('win_rate', 0) for r in valid_results]
        drawdowns = [r.backtest_results.get('max_drawdown', 0) for r in valid_results]
        
        return {
            'return_distribution': {
                'mean': np.mean(returns),
                'std': np.std(returns),
                'min': np.min(returns),
                'max': np.max(returns),
                'percentiles': {
                    '25th': np.percentile(returns, 25),
                    '50th': np.percentile(returns, 50),
                    '75th': np.percentile(returns, 75),
                    '90th': np.percentile(returns, 90)
                }
            },
            'win_rate_distribution': {
                'mean': np.mean(win_rates),
                'std': np.std(win_rates),
                'min': np.min(win_rates),
                'max': np.max(win_rates)
            },
            'drawdown_distribution': {
                'mean': np.mean(drawdowns),
                'std': np.std(drawdowns),
                'min': np.min(drawdowns),
                'max': np.max(drawdowns)
            }
        }
        
    def _analyze_parameter_importance(self) -> Dict:
        """Analizza l'importanza dei parametri"""
        parameter_importance = {}
        
        # Filtra solo risultati validi
        valid_results = [r for r in self.results if r.is_valid]
        
        if not valid_results:
            return {}
        
        # Estrai tutti i nomi dei parametri
        param_names = list(valid_results[0].parameters.keys())
        
        for param_name in param_names:
            param_values = [r.parameters[param_name] for r in valid_results]
            objective_scores = [r.objective_score for r in valid_results]
            
            # Calcola correlazione
            if len(set(param_values)) > 1:  # Solo se ci sono valori diversi
                correlation = np.corrcoef(param_values, objective_scores)[0, 1]
                
                # Trova valore ottimale
                best_idx = np.argmax(objective_scores)
                optimal_value = param_values[best_idx]
                
                parameter_importance[param_name] = {
                    'correlation': correlation,
                    'optimal_value': optimal_value,
                    'importance_score': abs(correlation)
                }
                    
        # Ordina per importanza
        sorted_params = sorted(parameter_importance.items(), 
                             key=lambda x: x[1]['importance_score'], 
                             reverse=True)
        
        return dict(sorted_params)
        
    def _analyze_the5ers_compliance(self) -> Dict:
        """Analizza la conformità alle regole The5ers"""
        compliant_results = []
        valid_results = [r for r in self.results if r.is_valid]
        
        for result in valid_results:
            compliance = result.backtest_results.get('the5ers_compliance', {})
            
            # Verifica se è conforme per Step 1
            step1_compliant = (
                compliance.get('step1_achieved', False) and
                not compliance.get('daily_loss_violated', True) and
                not compliance.get('total_loss_violated', True) and
                compliance.get('min_profitable_days', False)
            )
            
            # Verifica se è conforme per Step 2
            step2_compliant = (
                step1_compliant and
                compliance.get('step2_achieved', False)
            )
            
            # Verifica se è conforme per Scaling
            scaling_compliant = (
                step2_compliant and
                compliance.get('scaling_achieved', False)
            )
            
            compliant_results.append({
                'result': result,
                'step1_compliant': step1_compliant,
                'step2_compliant': step2_compliant,
                'scaling_compliant': scaling_compliant
            })
            
        total_valid = len(valid_results)
        if total_valid == 0:
            return {'message': 'Nessun risultato valido per l\'analisi compliance'}
            
        return {
            'step1_compliant_count': len([r for r in compliant_results if r['step1_compliant']]),
            'step2_compliant_count': len([r for r in compliant_results if r['step2_compliant']]),
            'scaling_compliant_count': len([r for r in compliant_results if r['scaling_compliant']]),
            'step1_compliant_rate': len([r for r in compliant_results if r['step1_compliant']]) / total_valid * 100,
            'step2_compliant_rate': len([r for r in compliant_results if r['step2_compliant']]) / total_valid * 100,
            'scaling_compliant_rate': len([r for r in compliant_results if r['scaling_compliant']]) / total_valid * 100
        }
        
    def _generate_recommendations(self) -> List[str]:
        """Genera raccomandazioni basate sui risultati"""
        recommendations = []
        
        if not self.results:
            return ["Nessun risultato disponibile per generare raccomandazioni"]
        
        # Filtra risultati validi
        valid_results = [r for r in self.results if r.is_valid]
        
        if not valid_results:
            return ["Nessun risultato valido trovato - rivedere parametri di ottimizzazione"]
            
        # Analizza i migliori risultati
        best_results = valid_results[:10]
        
        # Raccomandazioni sui parametri
        param_importance = self._analyze_parameter_importance()
        top_params = list(param_importance.keys())[:5]
        
        if top_params:
            recommendations.append(f"Parametri più importanti da ottimizzare: {', '.join(top_params)}")
            
        # Raccomandazioni sulle performance
        avg_return = np.mean([r.backtest_results.get('total_return_pct', 0) for r in best_results])
        avg_drawdown = np.mean([r.backtest_results.get('max_drawdown', 0) for r in best_results])
        
        if avg_return > 10:
            recommendations.append("I parametri ottimizzati mostrano buon potenziale di profitto")
        else:
            recommendations.append("Considerare di aumentare l'aggressività dei parametri per migliorare i ritorni")
            
        if avg_drawdown > 8:
            recommendations.append("Considerare parametri più conservativi per ridurre il drawdown")
            
        # Raccomandazioni The5ers
        compliance = self._analyze_the5ers_compliance()
        
        if isinstance(compliance, dict) and 'step1_compliant_rate' in compliance:
            if compliance['step1_compliant_rate'] < 50:
                recommendations.append("Bassa conformità Step 1 - rivedere risk management")
            if compliance['step2_compliant_rate'] < 30:
                recommendations.append("Bassa conformità Step 2 - considerare strategie più conservative")
        
        return recommendations
