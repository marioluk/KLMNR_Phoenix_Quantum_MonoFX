#!/usr/bin/env python3
# TEST PARAMETER OPTIMIZER

import sys
import os

# Aggiungi path per import
sys.path.insert(0, os.path.dirname(__file__))

def test_parameter_optimizer():
    """Test del parameter optimizer"""
    
    print("🧪 TEST PARAMETER OPTIMIZER")
    print("=" * 50)
    
    try:
        from parameter_optimizer import (
            OptimizationConfig, 
            ParameterRange, 
            OptimizationResult,
            QuantumParameterOptimizer,
            OptimizationAnalyzer
        )
        
        print("✅ Tutte le classi importate correttamente")
        
        # Test configurazione
        config = OptimizationConfig(
            start_date="2024-01-01",
            end_date="2024-01-07",  # Solo 1 settimana per test
            symbols=["EURUSD"],
            max_iterations=5
        )
        
        print(f"✅ Configurazione creata: {config.symbols}")
        
        # Test ParameterRange
        param_range = ParameterRange(
            name="test_param",
            min_value=0.1,
            max_value=1.0,
            step=0.1
        )
        
        values = param_range.get_values()
        print(f"✅ Parameter range creato: {len(values)} valori")
        
        # Test OptimizationResult
        result = OptimizationResult(
            parameters={"test": 1.0},
            backtest_results={"total_return_pct": 5.0},
            objective_score=10.0,
            the5ers_score=15.0,
            execution_time=1.0,
            is_valid=True
        )
        
        print(f"✅ OptimizationResult creato: score={result.objective_score}")
        
        # Test Optimizer (senza eseguire ottimizzazione)
        optimizer = QuantumParameterOptimizer(config)
        print(f"✅ Optimizer creato con {len(optimizer.parameter_ranges)} parametri")
        
        # Test Analyzer
        analyzer = OptimizationAnalyzer([result])
        report = analyzer.generate_report()
        print(f"✅ Analyzer creato, report keys: {list(report.keys())}")
        
        print("\n🎉 TUTTI I TEST COMPLETATI CORRETTAMENTE!")
        
    except Exception as e:
        print(f"❌ Errore durante test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parameter_optimizer()
