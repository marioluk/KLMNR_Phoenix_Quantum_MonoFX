#!/usr/bin/env python3
# ====================================================================================
# THE5ERS MASTER ANALYZER - SISTEMA COMPLETO DI ANALISI
# Combina analisi configurazioni + simboli + sessioni + step
# ====================================================================================

import json
import os
import logging
import numpy as np
from datetime import datetime
import subprocess
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class The5ersMasterAnalyzer:
    def __init__(self):
        """Inizializza master analyzer"""
        self.results = {
            'configs': {},
            'symbols': {},
            'recommendations': {}
        }
        
        logger.info("🎯 The5ers Master Analyzer inizializzato")
    
    def run_comparative_analysis(self):
        """Esegue analisi comparativa configurazioni"""
        
        print("🔥 FASE 1: ANALISI CONFIGURAZIONI")
        print("="*50)
        
        try:
            from comparative_backtest import The5ersComparativeBacktest
            
            backtest = The5ersComparativeBacktest()
            configs_loaded = backtest.load_all_configs()
            
            if configs_loaded > 0:
                print(f"📂 Configurazioni caricate: {configs_loaded}")
                results = backtest.run_comparative_backtest(days=30)
                rankings = backtest.generate_comparative_report()
                
                self.results['configs'] = {
                    'results': results,
                    'rankings': rankings,
                    'best_config': rankings[0][0] if rankings else None
                }
                
                print("✅ Analisi configurazioni completata!")
                return True
            else:
                print("❌ Nessuna configurazione trovata!")
                return False
                
        except Exception as e:
            print(f"❌ Errore analisi configurazioni: {e}")
            return False
    
    def run_symbol_analysis(self):
        """Esegue analisi simboli"""
        
        print("\n🔍 FASE 2: ANALISI SIMBOLI STRATEGICA")
        print("="*50)
        
        try:
            from symbol_analyzer import The5ersSymbolAnalyzer
            
            analyzer = The5ersSymbolAnalyzer()
            results = analyzer.analyze_all_symbols_all_steps(days=30)
            rankings = analyzer.generate_symbol_report(results)
            
            self.results['symbols'] = {
                'results': results,
                'rankings': rankings,
                'best_symbol': rankings[0][0] if rankings else None
            }
            
            print("✅ Analisi simboli completata!")
            return True
            
        except Exception as e:
            print(f"❌ Errore analisi simboli: {e}")
            return False
    
    def generate_master_recommendations(self):
        """Genera raccomandazioni finali integrate"""
        
        print("\n🎯 FASE 3: RACCOMANDAZIONI MASTER")
        print("="*50)
        
        config_results = self.results.get('configs', {})
        symbol_results = self.results.get('symbols', {})
        
        best_config = config_results.get('best_config', 'N/A')
        best_symbol = symbol_results.get('best_symbol', 'N/A')
        
        # Analisi integrata
        recommendations = {
            'optimal_setup': {
                'config': best_config,
                'primary_symbol': best_symbol,
                'secondary_symbols': [],
                'trading_sessions': [],
                'step_strategy': {}
            },
            'risk_assessment': {
                'success_probability': 0,
                'expected_return': 0,
                'max_drawdown_estimate': 0
            },
            'implementation_plan': {
                'week_1': {},
                'week_2': {},
                'week_3': {},
                'week_4': {}
            }
        }
        
        # Estrai dati da analisi simboli
        if symbol_results.get('rankings'):
            top_symbols = symbol_results['rankings'][:3]
            recommendations['optimal_setup']['primary_symbol'] = top_symbols[0][0]
            if len(top_symbols) > 1:
                recommendations['optimal_setup']['secondary_symbols'] = [s[0] for s in top_symbols[1:]]
        
        # Estrai performance configurazioni
        if config_results.get('results'):
            best_config_data = config_results['results'].get(best_config, {})
            totals = best_config_data.get('totals', {})
            
            recommendations['risk_assessment']['expected_return'] = totals.get('total_return', 0)
            recommendations['risk_assessment']['max_drawdown_estimate'] = totals.get('max_drawdown', 0)
            
            # Calcola probabilità successo
            return_score = min(100, max(0, totals.get('total_return', 0) * 1000))
            risk_score = max(0, 100 - (totals.get('max_drawdown', 0) * 1000))
            win_rate_score = totals.get('win_rate', 0) * 100
            
            success_prob = (return_score * 0.4 + risk_score * 0.4 + win_rate_score * 0.2) / 100
            recommendations['risk_assessment']['success_probability'] = success_prob
        
        # Piano implementazione step-by-step
        recommendations['implementation_plan'] = {
            'week_1': {
                'focus': 'System validation',
                'symbols': [recommendations['optimal_setup']['primary_symbol']],
                'daily_trades': 2,
                'target': 'Break-even + system confidence'
            },
            'week_2': {
                'focus': 'Gradual scaling',
                'symbols': [recommendations['optimal_setup']['primary_symbol']] + recommendations['optimal_setup']['secondary_symbols'][:1],
                'daily_trades': 3,
                'target': '2-3% portfolio growth'
            },
            'week_3': {
                'focus': 'Target pursuit',
                'symbols': [recommendations['optimal_setup']['primary_symbol']] + recommendations['optimal_setup']['secondary_symbols'],
                'daily_trades': 4,
                'target': '5-6% total growth'
            },
            'week_4': {
                'focus': 'Final push',
                'symbols': 'Full portfolio if on track, conservative if ahead',
                'daily_trades': 'Adaptive 2-5',
                'target': '8% Step 1 completion'
            }
        }
        
        self.results['recommendations'] = recommendations
        
        # Print recommendations
        print(f"\n🏆 SETUP OTTIMALE THE5ERS:")
        print(f"   📊 Best Config: {recommendations['optimal_setup']['config']}")
        print(f"   💱 Primary Symbol: {recommendations['optimal_setup']['primary_symbol']}")
        print(f"   📈 Secondary Symbols: {', '.join(recommendations['optimal_setup']['secondary_symbols'])}")
        
        print(f"\n📊 RISK ASSESSMENT:")
        print(f"   🎯 Success Probability: {recommendations['risk_assessment']['success_probability']:.1%}")
        print(f"   💰 Expected Return: {recommendations['risk_assessment']['expected_return']:.2%}")
        print(f"   📉 Max Drawdown Est: {recommendations['risk_assessment']['max_drawdown_estimate']:.2%}")
        
        print(f"\n📅 IMPLEMENTATION ROADMAP:")
        for week, plan in recommendations['implementation_plan'].items():
            print(f"   {week.upper()}: {plan['focus']} - Target: {plan['target']}")
        
        # Final verdict
        success_prob = recommendations['risk_assessment']['success_probability']
        expected_return = recommendations['risk_assessment']['expected_return']
        
        print(f"\n🚀 VERDETTO FINALE:")
        if success_prob > 0.75 and expected_return > 0.08:
            print("   ✅ SETUP ECCELLENTE - Probabilità alta di successo Step 1")
            verdict = "EXCELLENT"
        elif success_prob > 0.60 and expected_return > 0.06:
            print("   ⚠️  SETUP BUONO - Richiede disciplina e precisione")
            verdict = "GOOD"
        elif success_prob > 0.45:
            print("   🔧 SETUP MIGLIORABILE - Considera ottimizzazioni aggiuntive")
            verdict = "NEEDS_OPTIMIZATION"
        else:
            print("   ❌ SETUP RISCHIOSO - Rivedi strategia completamente")
            verdict = "HIGH_RISK"
        
        recommendations['final_verdict'] = verdict
        
        return recommendations
    
    def save_complete_analysis(self):
        """Salva analisi completa su file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"THE5ERS_COMPLETE_ANALYSIS_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n💾 ANALISI SALVATA: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Errore salvataggio: {e}")
            return None
    
    def run_complete_analysis(self):
        """Esegue analisi completa end-to-end"""
        
        print("🎯 THE5ERS MASTER ANALYZER - ANALISI COMPLETA")
        print("="*60)
        print("🚀 Avvio analisi integrata configurazioni + simboli + strategia")
        print("⏱️  Durata stimata: 8-12 minuti")
        print()
        
        # Fase 1: Analisi configurazioni
        config_success = self.run_comparative_analysis()
        
        # Fase 2: Analisi simboli  
        symbol_success = self.run_symbol_analysis()
        
        # Fase 3: Raccomandazioni integrate
        if config_success or symbol_success:
            recommendations = self.generate_master_recommendations()
            
            # Salva risultati
            saved_file = self.save_complete_analysis()
            
            print(f"\n" + "="*80)
            print("🏆 ANALISI MASTER COMPLETATA!")
            print("="*80)
            
            if recommendations:
                verdict = recommendations.get('final_verdict', 'UNKNOWN')
                best_config = recommendations['optimal_setup']['config']
                best_symbol = recommendations['optimal_setup']['primary_symbol']
                success_prob = recommendations['risk_assessment']['success_probability']
                
                print(f"🎯 VERDETTO: {verdict}")
                print(f"📊 Setup Raccomandato: {best_config} + {best_symbol}")
                print(f"🏆 Probabilità Successo Step 1: {success_prob:.1%}")
                
                if saved_file:
                    print(f"💾 Report salvato: {saved_file}")
            
            return True
        else:
            print("❌ ANALISI FALLITA - Controllare configurazioni e dipendenze")
            return False

def main():
    """Funzione principale master analyzer"""
    
    print("🎯 THE5ERS MASTER ANALYZER")
    print("🔧 Sistema completo di analisi e ottimizzazione")
    print()
    
    # Inizializza master analyzer
    analyzer = The5ersMasterAnalyzer()
    
    # Esegui analisi completa
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n✅ MASTER ANALYSIS COMPLETATA CON SUCCESSO!")
        print("🚀 Usa i risultati per configurare il tuo sistema The5ers")
    else:
        print("\n❌ Analisi incompleta - Controlla configurazioni")
    
    return analyzer.results

if __name__ == "__main__":
    main()
