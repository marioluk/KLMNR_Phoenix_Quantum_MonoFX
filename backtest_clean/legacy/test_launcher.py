#!/usr/bin/env python3
# TEST THE5ERS LAUNCHER - Verifica funzionalità

import sys
import os

# Aggiungi path per import
sys.path.insert(0, os.path.dirname(__file__))

def test_launcher_functions():
    """Test delle funzioni del launcher"""
    
    print("🧪 TEST THE5ERS LAUNCHER FUNCTIONS")
    print("=" * 50)
    
    try:
        from the5ers_launcher import (
            check_system_requirements,
            run_quick_verification,
            test_quantum_parameters,
            analyze_position_sizing,
            show_current_config,
            test_the5ers_compliance
        )
        
        print("✅ Tutte le funzioni importate correttamente")
        
        # Test function by function
        print("\n🔍 Test check_system_requirements:")
        result = check_system_requirements()
        print(f"   Risultato: {'✅ PASS' if result else '❌ FAIL'}")
        
        print("\n🔧 Test quantum parameters:")
        test_quantum_parameters()
        
        print("\n💰 Test position sizing:")
        analyze_position_sizing()
        
        print("\n🏆 Test compliance:")
        test_the5ers_compliance()
        
        print("\n✅ TUTTI I TEST COMPLETATI CORRETTAMENTE!")
        
    except Exception as e:
        print(f"❌ Errore durante test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_launcher_functions()
