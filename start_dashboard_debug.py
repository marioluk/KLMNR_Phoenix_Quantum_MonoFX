#!/usr/bin/env python3
"""
Test di avvio dashboard con debug
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_the5ers import The5ersGraphicalDashboard

def start_dashboard_debug():
    print("🚀 Avvio Dashboard con Debug...")
    
    # Inizializza dashboard
    dashboard = The5ersGraphicalDashboard(
        config_file="PRO-THE5ERS-QM-PHOENIX-GITCOP-config-140725-STEP1.json",
        use_mt5=True
    )
    
    print("📊 Metriche iniziali:")
    print(f"  Quantum Signals: {dashboard.current_metrics['quantum_signals']}")
    print(f"  Max Drawdown: {dashboard.current_metrics['max_drawdown']:.2f}%")
    
    # Avvia dashboard
    print("🌐 Avviando server Flask su http://localhost:5000")
    dashboard.start_dashboard(host='127.0.0.1', port=5000, debug=False)

if __name__ == "__main__":
    start_dashboard_debug()
