#!/usr/bin/env python3
"""Test rapido del system report"""

from the5ers_integrated_launcher_complete import CompleteIntegratedLauncher

def test_system_report():
    print("🧪 TEST SYSTEM REPORT")
    print("="*30)
    
    launcher = CompleteIntegratedLauncher()
    launcher.system_report()

if __name__ == "__main__":
    test_system_report()
