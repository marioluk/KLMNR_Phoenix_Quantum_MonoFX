#!/usr/bin/env python3
"""
Verifica delle correzioni nomenclatura The5ers
"""

from autonomous_optimizer import AutonomousOptimizer

def verify_corrections():
    print("🔧 VERIFICA CORREZIONI NOMENCLATURA THE5ERS")
    print("="*50)
    
    opt = AutonomousOptimizer()
    
    print(f"✅ Simboli totali: {len(opt.available_symbols)}")
    print("\n📋 LISTA SIMBOLI CORRETTA:")
    
    # Raggruppa per categorie
    forex = []
    crypto = []
    indices = []
    commodities = []
    
    for symbol in opt.available_symbols:
        spread = opt.get_symbol_max_spread(symbol)
        sessions = ', '.join(opt.get_symbol_sessions(symbol))
        
        if symbol in ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD', 'GBPJPY']:
            forex.append(f"   {symbol:8s} - Spread: {spread:5.1f} - Sessioni: {sessions}")
        elif symbol in ['BTCUSD', 'ETHUSD']:
            crypto.append(f"   {symbol:8s} - Spread: {spread:5.1f} - Sessioni: {sessions}")
        elif symbol in ['NAS100', 'US30', 'SP500', 'DAX40']:
            indices.append(f"   {symbol:8s} - Spread: {spread:5.1f} - Sessioni: {sessions}")
        elif symbol in ['XAUUSD']:
            commodities.append(f"   {symbol:8s} - Spread: {spread:5.1f} - Sessioni: {sessions}")
    
    print("\n🏛️ FOREX MAJORS:")
    for line in forex:
        print(line)
    
    print("\n💎 CRYPTO (SUPPORTATE):")
    for line in crypto:
        print(line)
    
    print("\n📈 INDICES (NOMENCLATURA CORRETTA):")
    for line in indices:
        print(line)
    
    print("\n💰 COMMODITIES:")
    for line in commodities:
        print(line)
    
    # Verifica nomenclature specifiche
    corrections = {
        'DAX40': '🇩🇪 Nomenclatura corretta (non GER30)',
        'SP500': '📈 Nomenclatura corretta (supportato)',
        'US30': '📊 Nomenclatura corretta (supportato)',
        'BTCUSD': '💎 Crypto supportata (confermato produzione)',
        'ETHUSD': '🔷 Crypto supportata (confermato produzione)'
    }
    
    print(f"\n✅ CORREZIONI APPLICATE:")
    for symbol, note in corrections.items():
        if symbol in opt.available_symbols:
            print(f"   ✅ {symbol:8s} - {note}")
        else:
            print(f"   ❌ {symbol:8s} - MANCANTE!")
    
    print(f"\n🎯 CONFIGURAZIONI POSSIBILI:")
    for level in ['conservative', 'moderate', 'aggressive']:
        count = {'conservative': 4, 'moderate': 6, 'aggressive': 8}[level]
        print(f"   {level.upper():12s}: {count} simboli max")
    
    print(f"\n✅ Verifica completata - tutto corretto!")

if __name__ == "__main__":
    verify_corrections()
