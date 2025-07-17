# ====================================================================================
# RESULTS ANALYZER - THE5ERS QUANTUM OPTIMIZATION
# Sistema di analisi e visualizzazione risultati backtest
# ====================================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configurazione matplotlib per Windows
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class ResultsAnalyzer:
    """Analizzatore avanzato dei risultati di ottimizzazione"""
    
    def __init__(self, results_file: str = None, results_data: list = None):
        self.logger = logging.getLogger(__name__)
        
        if results_file:
            self.results = self._load_results_from_file(results_file)
        elif results_data:
            self.results = results_data
        else:
            raise ValueError("Fornire results_file o results_data")
            
        self.df = self._create_dataframe()
        
    def _load_results_from_file(self, file_path: str) -> list:
        """Carica risultati da file JSON"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Errore nel caricamento file: {e}")
            return []
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Crea DataFrame dai risultati per analisi più facile"""
        if not self.results:
            return pd.DataFrame()
            
        data = []
        for result in self.results:
            row = {
                'fitness_score': result['fitness_score'],
                'the5ers_score': result['the5ers_score'],
                'total_return_pct': result['performance']['total_return_pct'],
                'win_rate': result['performance']['win_rate'],
                'max_drawdown': result['performance']['max_drawdown'],
                'total_trades': result['performance']['total_trades'],
                'sharpe_ratio': result['performance']['sharpe_ratio'],
                'step1_achieved': result['the5ers_compliance']['step1_achieved'],
                'step2_achieved': result['the5ers_compliance']['step2_achieved'],
                'scaling_achieved': result['the5ers_compliance']['scaling_achieved'],
                'daily_loss_violated': result['the5ers_compliance']['daily_loss_violated'],
                'total_loss_violated': result['the5ers_compliance']['total_loss_violated'],
                'min_profitable_days': result['the5ers_compliance']['min_profitable_days']
            }
            
            # Aggiungi parametri
            for param, value in result['parameters'].items():
                row[f'param_{param}'] = value
                
            data.append(row)
            
        return pd.DataFrame(data)
    
    def generate_comprehensive_report(self, output_dir: str = "reports"):
        """Genera un report completo con grafici e analisi"""
        
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Report Performance Overview
        self._create_performance_overview(output_dir, timestamp)
        
        # 2. Parameter Analysis
        self._create_parameter_analysis(output_dir, timestamp)
        
        # 3. The5ers Compliance Analysis
        self._create_compliance_analysis(output_dir, timestamp)
        
        # 4. Risk Analysis
        self._create_risk_analysis(output_dir, timestamp)
        
        # 5. Correlation Analysis
        self._create_correlation_analysis(output_dir, timestamp)
        
        # 6. Best Parameters Analysis
        self._create_best_parameters_analysis(output_dir, timestamp)
        
        # 7. Generate HTML Report
        self._create_html_report(output_dir, timestamp)
        
        self.logger.info(f"Report completo generato in: {output_dir}")
        
    def _create_performance_overview(self, output_dir: str, timestamp: str):
        """Crea overview delle performance"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Distribution of Returns
        axes[0, 0].hist(self.df['total_return_pct'], bins=30, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Distribuzione Return (%)')
        axes[0, 0].set_xlabel('Return %')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(x=0, color='red', linestyle='--', label='Break-even')
        axes[0, 0].axvline(x=8, color='green', linestyle='--', label='Step1 Target')
        axes[0, 0].legend()
        
        # 2. Win Rate vs Return
        scatter = axes[0, 1].scatter(self.df['win_rate'], self.df['total_return_pct'], 
                                   c=self.df['max_drawdown'], cmap='RdYlBu', alpha=0.6)
        axes[0, 1].set_title('Win Rate vs Return (colore = Drawdown)')
        axes[0, 1].set_xlabel('Win Rate %')
        axes[0, 1].set_ylabel('Return %')
        plt.colorbar(scatter, ax=axes[0, 1])
        
        # 3. Drawdown Distribution
        axes[1, 0].hist(self.df['max_drawdown'], bins=25, alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Distribuzione Max Drawdown')
        axes[1, 0].set_xlabel('Max Drawdown %')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].axvline(x=5, color='red', linestyle='--', label='Daily Loss Limit')
        axes[1, 0].axvline(x=10, color='orange', linestyle='--', label='Total Loss Limit')
        axes[1, 0].legend()
        
        # 4. Fitness Score Distribution
        axes[1, 1].hist(self.df['fitness_score'], bins=25, alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('Distribuzione Fitness Score')
        axes[1, 1].set_xlabel('Fitness Score')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_overview_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def _create_parameter_analysis(self, output_dir: str, timestamp: str):
        """Analizza l'importanza dei parametri"""
        param_cols = [col for col in self.df.columns if col.startswith('param_')]
        
        if not param_cols:
            return
            
        # Calcola correlazioni con fitness score
        correlations = {}
        for param in param_cols:
            if self.df[param].dtype in ['int64', 'float64']:
                corr = self.df[param].corr(self.df['fitness_score'])
                if not np.isnan(corr):
                    correlations[param.replace('param_', '')] = corr
        
        # Plot correlazioni
        if correlations:
            plt.figure(figsize=(12, 8))
            params = list(correlations.keys())
            values = list(correlations.values())
            
            # Ordina per valore assoluto
            sorted_items = sorted(zip(params, values), key=lambda x: abs(x[1]), reverse=True)
            params, values = zip(*sorted_items)
            
            colors = ['red' if v < 0 else 'green' for v in values]
            
            plt.barh(params, values, color=colors, alpha=0.7)
            plt.title('Correlazione Parametri con Fitness Score')
            plt.xlabel('Correlazione')
            plt.axvline(x=0, color='black', linestyle='-', alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/parameter_correlations_{timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        # Heatmap parametri top performers
        top_results = self.df.nlargest(20, 'fitness_score')
        param_data = top_results[[col for col in param_cols if top_results[col].dtype in ['int64', 'float64']]]
        
        if not param_data.empty:
            plt.figure(figsize=(15, 10))
            # Normalizza i dati per la heatmap
            param_data_norm = (param_data - param_data.mean()) / param_data.std()
            
            sns.heatmap(param_data_norm.T, annot=False, cmap='RdYlBu', center=0)
            plt.title('Heatmap Parametri - Top 20 Performer')
            plt.xlabel('Rank')
            plt.ylabel('Parametri')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/parameters_heatmap_{timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_compliance_analysis(self, output_dir: str, timestamp: str):
        """Analizza la compliance The5ers"""
        compliance_cols = ['step1_achieved', 'step2_achieved', 'scaling_achieved', 
                          'daily_loss_violated', 'total_loss_violated', 'min_profitable_days']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Compliance rates
        compliance_rates = {}
        for col in compliance_cols:
            if col in self.df.columns:
                compliance_rates[col] = self.df[col].mean() * 100
        
        if compliance_rates:
            axes[0, 0].bar(compliance_rates.keys(), compliance_rates.values(), 
                          color=['green', 'blue', 'orange', 'red', 'red', 'purple'])
            axes[0, 0].set_title('Tassi di Compliance (%)')
            axes[0, 0].set_ylabel('Percentage')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
        # 2. Return by Step Achievement
        step_groups = self.df.groupby(['step1_achieved', 'step2_achieved', 'scaling_achieved'])
        group_means = step_groups['total_return_pct'].mean()
        
        if not group_means.empty:
            axes[0, 1].bar(range(len(group_means)), group_means.values)
            axes[0, 1].set_title('Return Medio per Step Achievement')
            axes[0, 1].set_ylabel('Return %')
            axes[0, 1].set_xticks(range(len(group_means)))
            axes[0, 1].set_xticklabels([str(idx) for idx in group_means.index], rotation=45)
        
        # 3. Violazioni vs Performance
        violations = self.df['daily_loss_violated'] | self.df['total_loss_violated']
        
        no_violations = self.df[~violations]['total_return_pct']
        with_violations = self.df[violations]['total_return_pct']
        
        axes[1, 0].hist([no_violations, with_violations], bins=20, alpha=0.7, 
                       label=['No Violations', 'With Violations'], color=['green', 'red'])
        axes[1, 0].set_title('Return Distribution by Violations')
        axes[1, 0].set_xlabel('Return %')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        
        # 4. Compliance Score
        compliance_score = (
            self.df['step1_achieved'].astype(int) * 3 +
            self.df['step2_achieved'].astype(int) * 2 +
            self.df['scaling_achieved'].astype(int) * 5 +
            self.df['min_profitable_days'].astype(int) * 1 -
            self.df['daily_loss_violated'].astype(int) * 5 -
            self.df['total_loss_violated'].astype(int) * 10
        )
        
        axes[1, 1].scatter(compliance_score, self.df['total_return_pct'], alpha=0.6)
        axes[1, 1].set_title('Compliance Score vs Return')
        axes[1, 1].set_xlabel('Compliance Score')
        axes[1, 1].set_ylabel('Return %')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/compliance_analysis_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_risk_analysis(self, output_dir: str, timestamp: str):
        """Analizza i profili di rischio"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Risk-Return Profile
        axes[0, 0].scatter(self.df['max_drawdown'], self.df['total_return_pct'], 
                          c=self.df['win_rate'], cmap='viridis', alpha=0.6)
        axes[0, 0].set_title('Risk-Return Profile (colore = Win Rate)')
        axes[0, 0].set_xlabel('Max Drawdown %')
        axes[0, 0].set_ylabel('Return %')
        
        # Linee di riferimento
        axes[0, 0].axhline(y=8, color='green', linestyle='--', alpha=0.5, label='Step1 Target')
        axes[0, 0].axvline(x=5, color='red', linestyle='--', alpha=0.5, label='Daily Loss Limit')
        axes[0, 0].legend()
        
        # 2. Sharpe Ratio Distribution
        axes[0, 1].hist(self.df['sharpe_ratio'], bins=25, alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Distribuzione Sharpe Ratio')
        axes[0, 1].set_xlabel('Sharpe Ratio')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].axvline(x=self.df['sharpe_ratio'].median(), color='red', 
                          linestyle='--', label=f'Mediana: {self.df["sharpe_ratio"].median():.2f}')
        axes[0, 1].legend()
        
        # 3. Trades vs Return
        axes[1, 0].scatter(self.df['total_trades'], self.df['total_return_pct'], 
                          c=self.df['max_drawdown'], cmap='RdYlBu', alpha=0.6)
        axes[1, 0].set_title('Numero Trades vs Return (colore = Drawdown)')
        axes[1, 0].set_xlabel('Total Trades')
        axes[1, 0].set_ylabel('Return %')
        
        # 4. Efficient Frontier
        # Raggruppa per livelli di drawdown
        drawdown_bins = pd.cut(self.df['max_drawdown'], bins=5)
        grouped = self.df.groupby(drawdown_bins).agg({
            'total_return_pct': 'mean',
            'max_drawdown': 'mean',
            'win_rate': 'mean'
        })
        
        axes[1, 1].plot(grouped['max_drawdown'], grouped['total_return_pct'], 
                       marker='o', linestyle='-', linewidth=2, markersize=8)
        axes[1, 1].set_title('Efficient Frontier (Return vs Risk)')
        axes[1, 1].set_xlabel('Average Max Drawdown %')
        axes[1, 1].set_ylabel('Average Return %')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/risk_analysis_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_correlation_analysis(self, output_dir: str, timestamp: str):
        """Crea analisi delle correlazioni"""
        # Seleziona solo colonne numeriche
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return
            
        # Calcola matrice di correlazione
        corr_matrix = self.df[numeric_cols].corr()
        
        # Crea heatmap
        plt.figure(figsize=(20, 16))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdYlBu', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .5})
        
        plt.title('Matrice di Correlazione - Tutti i Parametri')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/correlation_matrix_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_best_parameters_analysis(self, output_dir: str, timestamp: str):
        """Analizza i parametri dei migliori performer"""
        top_performers = self.df.nlargest(10, 'fitness_score')
        param_cols = [col for col in self.df.columns if col.startswith('param_')]
        
        if not param_cols:
            return
            
        # Analisi dei parametri ottimali
        param_analysis = {}
        for param in param_cols:
            if top_performers[param].dtype in ['int64', 'float64']:
                param_analysis[param.replace('param_', '')] = {
                    'mean': top_performers[param].mean(),
                    'std': top_performers[param].std(),
                    'min': top_performers[param].min(),
                    'max': top_performers[param].max(),
                    'median': top_performers[param].median()
                }
        
        # Crea boxplot dei parametri principali
        key_params = ['quantum_params.buffer_size', 'quantum_params.spin_window', 
                     'quantum_params.signal_cooldown', 'risk_parameters.risk_percent']
        
        available_params = [f'param_{param}' for param in key_params if f'param_{param}' in param_cols]
        
        if available_params:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            axes = axes.flatten()
            
            for i, param in enumerate(available_params[:4]):
                if i < 4:
                    # Confronta top 10 vs bottom 10
                    top_10 = self.df.nlargest(10, 'fitness_score')[param]
                    bottom_10 = self.df.nsmallest(10, 'fitness_score')[param]
                    
                    axes[i].boxplot([top_10, bottom_10], labels=['Top 10', 'Bottom 10'])
                    axes[i].set_title(f'{param.replace("param_", "")}')
                    axes[i].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/best_parameters_{timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_html_report(self, output_dir: str, timestamp: str):
        """Crea report HTML consolidato"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>The5ers Quantum Algorithm - Optimization Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
                .image {{ text-align: center; margin: 20px 0; }}
                .table {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>The5ers Quantum Algorithm</h1>
                <h2>Optimization Report</h2>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Best Return</h3>
                        <p>{self.df['total_return_pct'].max():.2f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>Average Return</h3>
                        <p>{self.df['total_return_pct'].mean():.2f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>Best Fitness Score</h3>
                        <p>{self.df['fitness_score'].max():.4f}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Step1 Success Rate</h3>
                        <p>{self.df['step1_achieved'].mean()*100:.1f}%</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Performance Overview</h2>
                <div class="image">
                    <img src="performance_overview_{timestamp}.png" alt="Performance Overview" style="max-width: 100%;">
                </div>
            </div>
            
            <div class="section">
                <h2>Parameter Analysis</h2>
                <div class="image">
                    <img src="parameter_correlations_{timestamp}.png" alt="Parameter Correlations" style="max-width: 100%;">
                </div>
            </div>
            
            <div class="section">
                <h2>Compliance Analysis</h2>
                <div class="image">
                    <img src="compliance_analysis_{timestamp}.png" alt="Compliance Analysis" style="max-width: 100%;">
                </div>
            </div>
            
            <div class="section">
                <h2>Risk Analysis</h2>
                <div class="image">
                    <img src="risk_analysis_{timestamp}.png" alt="Risk Analysis" style="max-width: 100%;">
                </div>
            </div>
            
            <div class="section">
                <h2>Best Parameters</h2>
                <div class="image">
                    <img src="best_parameters_{timestamp}.png" alt="Best Parameters" style="max-width: 100%;">
                </div>
            </div>
            
            <div class="section">
                <h2>Top 10 Configurations</h2>
                <div class="table">
                    {self._generate_top_configurations_table()}
                </div>
            </div>
            
        </body>
        </html>
        """
        
        with open(f"{output_dir}/report_{timestamp}.html", 'w') as f:
            f.write(html_content)
    
    def _generate_top_configurations_table(self) -> str:
        """Genera tabella HTML delle top configurazioni"""
        top_10 = self.df.nlargest(10, 'fitness_score')
        
        html = "<table>\n"
        html += "<tr><th>Rank</th><th>Fitness Score</th><th>Return %</th><th>Win Rate %</th><th>Drawdown %</th><th>Trades</th><th>Step1</th><th>Step2</th></tr>\n"
        
        for i, (idx, row) in enumerate(top_10.iterrows(), 1):
            html += f"<tr>"
            html += f"<td>{i}</td>"
            html += f"<td>{row['fitness_score']:.4f}</td>"
            html += f"<td>{row['total_return_pct']:.2f}</td>"
            html += f"<td>{row['win_rate']:.1f}</td>"
            html += f"<td>{row['max_drawdown']:.2f}</td>"
            html += f"<td>{row['total_trades']}</td>"
            html += f"<td>{'✓' if row['step1_achieved'] else '✗'}</td>"
            html += f"<td>{'✓' if row['step2_achieved'] else '✗'}</td>"
            html += f"</tr>\n"
        
        html += "</table>"
        return html
    
    def get_optimization_recommendations(self) -> List[str]:
        """Genera raccomandazioni basate sui risultati"""
        recommendations = []
        
        # Analisi success rate
        step1_success = self.df['step1_achieved'].mean()
        step2_success = self.df['step2_achieved'].mean()
        
        if step1_success < 0.3:
            recommendations.append("Basso tasso di successo Step1 (<30%). Considerare parametri più conservativi.")
        elif step1_success > 0.7:
            recommendations.append("Alto tasso di successo Step1 (>70%). Possibile aumentare aggressività per Step2.")
        
        # Analisi drawdown
        avg_drawdown = self.df['max_drawdown'].mean()
        if avg_drawdown > 7:
            recommendations.append(f"Drawdown medio alto ({avg_drawdown:.1f}%). Ridurre risk_percent o aumentare stop loss.")
        
        # Analisi trade frequency
        avg_trades = self.df['total_trades'].mean()
        if avg_trades < 10:
            recommendations.append("Bassa frequenza di trading. Considerare rilassamento dei filtri di segnale.")
        elif avg_trades > 50:
            recommendations.append("Alta frequenza di trading. Possibile over-trading, considerare filtri più rigidi.")
        
        # Analisi correlazioni parametri
        param_cols = [col for col in self.df.columns if col.startswith('param_')]
        if param_cols:
            most_important = None
            best_corr = 0
            
            for param in param_cols:
                if self.df[param].dtype in ['int64', 'float64']:
                    corr = abs(self.df[param].corr(self.df['fitness_score']))
                    if not np.isnan(corr) and corr > best_corr:
                        best_corr = corr
                        most_important = param
            
            if most_important:
                recommendations.append(f"Parametro più influente: {most_important.replace('param_', '')} (correlazione: {best_corr:.3f})")
        
        return recommendations
    
    def export_best_config(self, output_file: str, n_best: int = 1):
        """Esporta la migliore configurazione"""
        best_result = self.df.nlargest(n_best, 'fitness_score').iloc[0]
        
        best_config = {}
        for col in self.df.columns:
            if col.startswith('param_'):
                param_name = col.replace('param_', '')
                best_config[param_name] = best_result[col]
        
        with open(output_file, 'w') as f:
            json.dump(best_config, f, indent=2)
        
        self.logger.info(f"Migliore configurazione salvata in: {output_file}")
        
        return best_config

# ====================================================================================
# UTILITY FUNCTIONS
# ====================================================================================

def compare_optimization_results(results_files: List[str], output_dir: str = "comparisons"):
    """Confronta risultati di diverse ottimizzazioni"""
    Path(output_dir).mkdir(exist_ok=True)
    
    all_results = {}
    for i, file_path in enumerate(results_files):
        try:
            with open(file_path, 'r') as f:
                results = json.load(f)
            all_results[f"Scenario_{i+1}"] = results
        except Exception as e:
            print(f"Errore nel caricamento {file_path}: {e}")
    
    if not all_results:
        return
    
    # Crea confronto visivo
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    scenario_names = list(all_results.keys())
    
    # 1. Confronto Return
    returns = []
    for scenario, results in all_results.items():
        scenario_returns = [r['performance']['total_return_pct'] for r in results]
        returns.extend([(scenario, ret) for ret in scenario_returns])
    
    df_returns = pd.DataFrame(returns, columns=['Scenario', 'Return'])
    
    axes[0, 0].boxplot([df_returns[df_returns['Scenario'] == scenario]['Return'] 
                       for scenario in scenario_names], labels=scenario_names)
    axes[0, 0].set_title('Confronto Return per Scenario')
    axes[0, 0].set_ylabel('Return %')
    
    # 2. Confronto Win Rate
    win_rates = []
    for scenario, results in all_results.items():
        scenario_wr = [r['performance']['win_rate'] for r in results]
        win_rates.extend([(scenario, wr) for wr in scenario_wr])
    
    df_wr = pd.DataFrame(win_rates, columns=['Scenario', 'WinRate'])
    
    axes[0, 1].boxplot([df_wr[df_wr['Scenario'] == scenario]['WinRate'] 
                       for scenario in scenario_names], labels=scenario_names)
    axes[0, 1].set_title('Confronto Win Rate per Scenario')
    axes[0, 1].set_ylabel('Win Rate %')
    
    # 3. Confronto Drawdown
    drawdowns = []
    for scenario, results in all_results.items():
        scenario_dd = [r['performance']['max_drawdown'] for r in results]
        drawdowns.extend([(scenario, dd) for dd in scenario_dd])
    
    df_dd = pd.DataFrame(drawdowns, columns=['Scenario', 'Drawdown'])
    
    axes[1, 0].boxplot([df_dd[df_dd['Scenario'] == scenario]['Drawdown'] 
                       for scenario in scenario_names], labels=scenario_names)
    axes[1, 0].set_title('Confronto Drawdown per Scenario')
    axes[1, 0].set_ylabel('Max Drawdown %')
    
    # 4. Confronto Fitness Score
    fitness_scores = []
    for scenario, results in all_results.items():
        scenario_fs = [r['fitness_score'] for r in results]
        fitness_scores.extend([(scenario, fs) for fs in scenario_fs])
    
    df_fs = pd.DataFrame(fitness_scores, columns=['Scenario', 'FitnessScore'])
    
    axes[1, 1].boxplot([df_fs[df_fs['Scenario'] == scenario]['FitnessScore'] 
                       for scenario in scenario_names], labels=scenario_names)
    axes[1, 1].set_title('Confronto Fitness Score per Scenario')
    axes[1, 1].set_ylabel('Fitness Score')
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f"{output_dir}/scenarios_comparison_{timestamp}.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Confronto salvato in: {output_dir}/scenarios_comparison_{timestamp}.png")

if __name__ == "__main__":
    # Test del sistema di analisi
    print("Testing Results Analyzer...")
    
    # Genera dati di test
    test_results = []
    for i in range(100):
        test_results.append({
            'fitness_score': np.random.uniform(0, 100),
            'the5ers_score': np.random.uniform(-50, 200),
            'parameters': {
                'quantum_params.buffer_size': np.random.randint(200, 800),
                'quantum_params.spin_window': np.random.randint(30, 120),
                'risk_parameters.risk_percent': np.random.uniform(0.008, 0.020)
            },
            'performance': {
                'total_return_pct': np.random.uniform(-5, 15),
                'win_rate': np.random.uniform(30, 80),
                'max_drawdown': np.random.uniform(1, 15),
                'total_trades': np.random.randint(5, 100),
                'sharpe_ratio': np.random.uniform(-1, 3)
            },
            'the5ers_compliance': {
                'step1_achieved': np.random.choice([True, False]),
                'step2_achieved': np.random.choice([True, False]),
                'scaling_achieved': np.random.choice([True, False]),
                'daily_loss_violated': np.random.choice([True, False]),
                'total_loss_violated': np.random.choice([True, False]),
                'min_profitable_days': np.random.choice([True, False])
            }
        })
    
    # Test analyzer
    analyzer = ResultsAnalyzer(results_data=test_results)
    
    # Genera report
    analyzer.generate_comprehensive_report("test_reports")
    
    # Genera raccomandazioni
    recommendations = analyzer.get_optimization_recommendations()
    print("Raccomandazioni generate:")
    for rec in recommendations:
        print(f"- {rec}")
    
    print("Test completato!")
