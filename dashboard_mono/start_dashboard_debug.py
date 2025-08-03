#!/usr/bin/env python3
"""
Test di avvio dashboard con debug - MONO SYSTEM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_broker import The5ersGraphicalDashboard

def start_dashboard_debug():
    print("🚀 Avvio Dashboard con Debug...")
    # Inizializza dashboard con auto-detect configurazione aggiornata
    dashboard = The5ersGraphicalDashboard(
        config_file=None,  # Auto-detect dalla cartella config root
        use_mt5=True
    )
    print("📊 Metriche iniziali:")
    print(f"  Quantum Signals: {dashboard.current_metrics['quantum_signals']}")
    print(f"  Max Drawdown: {dashboard.current_metrics['max_drawdown']:.2f}%")
    print(f"  Config utilizzato: {dashboard.config_file}")
    # Avvia dashboard
    print("🌐 Avviando server Flask su http://localhost:5000")
    dashboard.start_dashboard(host='127.0.0.1', port=5000, debug=False)

if __name__ == "__main__":
    start_dashboard_debug()
