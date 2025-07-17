#!/usr/bin/env python3
# ====================================================================================
# DEBUG QUANTUM ENGINE - THE5ERS
# Debug per capire perché non si generano segnali
# ====================================================================================

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configurazione logging dettagliato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DebugQuantumEngine:
    """Versione debug del quantum engine per diagnostica"""
    
    def __init__(self, config):
        self.config = config
        self.quantum_params = config.get('quantum_params', {})
        self.logger = logging.getLogger(__name__)
        
        # Parametri ultra permissivi per debug
        self.entropy_threshold = self.quantum_params.get('entropy_threshold', 0.05)  # MOLTO basso
        self.coherence_threshold = self.quantum_params.get('coherence_threshold', 0.2)  # MOLTO basso
        self.entanglement_strength = self.quantum_params.get('entanglement_strength', 0.5)  # Basso
        self.buffer_size = self.quantum_params.get('buffer_size', 10)  # Piccolo
        
        # Buffer per calcoli
        self.price_buffer = []
        self.entropy_buffer = []
        self.coherence_buffer = []
        
        self.logger.info(f"🔧 DEBUG ENGINE INIT:")
        self.logger.info(f"   entropy_threshold: {self.entropy_threshold}")
        self.logger.info(f"   coherence_threshold: {self.coherence_threshold}")
        self.logger.info(f"   entanglement_strength: {self.entanglement_strength}")
        self.logger.info(f"   buffer_size: {self.buffer_size}")
    
    def calculate_entropy(self, prices):
        """Calcola entropia (versione debug)"""
        if len(prices) < 2:
            entropy = 0.0
        else:
            returns = np.diff(prices) / prices[:-1]
            # Versione semplificata per garantire valori
            entropy = np.std(returns) * 10  # Amplifica per debug
            
        self.logger.debug(f"🔢 Entropy: {entropy:.4f} (threshold: {self.entropy_threshold})")
        return entropy
    
    def calculate_coherence(self, prices):
        """Calcola coerenza (versione debug)"""
        if len(prices) < 3:
            coherence = 0.0
        else:
            # Coerenza basata su trend
            diff1 = np.diff(prices)
            diff2 = np.diff(diff1)
            coherence = 1.0 / (1.0 + np.std(diff2))  # Inverso della volatilità
            
        self.logger.debug(f"🔗 Coherence: {coherence:.4f} (threshold: {self.coherence_threshold})")
        return coherence
    
    def generate_signal(self, symbol, current_price, timestamp):
        """Genera segnale con debug dettagliato"""
        
        self.logger.debug(f"\n📊 GENERATING SIGNAL for {symbol} at {current_price}")
        
        # Aggiungi al buffer
        self.price_buffer.append(current_price)
        if len(self.price_buffer) > self.buffer_size:
            self.price_buffer.pop(0)
        
        self.logger.debug(f"📋 Buffer size: {len(self.price_buffer)}/{self.buffer_size}")
        
        # Serve almeno 5 prezzi per calcoli
        if len(self.price_buffer) < 5:
            self.logger.debug(f"❌ Buffer too small ({len(self.price_buffer)} < 5)")
            return None
        
        # Calcola metriche quantum
        entropy = self.calculate_entropy(self.price_buffer)
        coherence = self.calculate_coherence(self.price_buffer)
        
        self.entropy_buffer.append(entropy)
        self.coherence_buffer.append(coherence)
        
        # Mantieni buffer
        if len(self.entropy_buffer) > 10:
            self.entropy_buffer.pop(0)
        if len(self.coherence_buffer) > 10:
            self.coherence_buffer.pop(0)
        
        # Log delle condizioni
        entropy_ok = entropy > self.entropy_threshold
        coherence_ok = coherence > self.coherence_threshold
        
        self.logger.debug(f"✅ Entropy check: {entropy:.4f} > {self.entropy_threshold} = {entropy_ok}")
        self.logger.debug(f"✅ Coherence check: {coherence:.4f} > {self.coherence_threshold} = {coherence_ok}")
        
        # Verifica condizioni
        if not entropy_ok:
            self.logger.debug(f"❌ SIGNAL REJECTED: Entropy too low")
            return None
            
        if not coherence_ok:
            self.logger.debug(f"❌ SIGNAL REJECTED: Coherence too low")
            return None
        
        # Calcola entanglement per direzione
        if len(self.price_buffer) >= 3:
            recent_trend = self.price_buffer[-1] - self.price_buffer[-3]
            entanglement = recent_trend * self.entanglement_strength
            
            self.logger.debug(f"🔄 Recent trend: {recent_trend:.6f}")
            self.logger.debug(f"🔗 Entanglement: {entanglement:.6f}")
            
            if entanglement > 0.00001:  # Soglia molto bassa
                signal_type = "BUY"
                confidence = min(0.8, abs(entanglement) * 1000)
            elif entanglement < -0.00001:
                signal_type = "SELL" 
                confidence = min(0.8, abs(entanglement) * 1000)
            else:
                self.logger.debug(f"❌ SIGNAL REJECTED: Entanglement too weak")
                return None
        else:
            self.logger.debug(f"❌ SIGNAL REJECTED: Not enough price history")
            return None
        
        signal = {
            'symbol': symbol,
            'signal': signal_type,
            'confidence': confidence,
            'timestamp': timestamp,
            'entropy': entropy,
            'coherence': coherence,
            'entanglement': entanglement,
            'price': current_price
        }
        
        self.logger.info(f"🚀 SIGNAL GENERATED: {signal_type} {symbol} conf:{confidence:.3f}")
        return signal

def test_debug_engine():
    """Test del debug engine"""
    
    print("🔍 DEBUG TEST QUANTUM ENGINE")
    print("="*50)
    
    # Configurazione debug
    config = {
        'quantum_params': {
            'entropy_threshold': 0.01,    # ULTRA basso
            'coherence_threshold': 0.1,   # ULTRA basso  
            'entanglement_strength': 0.3, # Basso
            'buffer_size': 8               # Piccolo
        }
    }
    
    engine = DebugQuantumEngine(config)
    
    # Dati di test sintetici con trend
    print("\n📊 Testing con dati sintetici...")
    
    # Genera prezzi con trend per EURUSD
    base_price = 1.1000
    prices = []
    
    # Trend crescente poi decrescente
    for i in range(15):
        if i < 8:
            # Trend crescente
            noise = np.random.normal(0, 0.0002)
            trend = i * 0.0005
            price = base_price + trend + noise
        else:
            # Trend decrescente
            noise = np.random.normal(0, 0.0002)
            trend = (15-i) * 0.0003
            price = base_price + 0.004 - trend + noise
        
        prices.append(price)
        timestamp = datetime.now() + timedelta(minutes=i*15)
        
        print(f"\n--- Tick {i+1}: Price = {price:.6f} ---")
        signal = engine.generate_signal("EURUSD", price, timestamp)
        
        if signal:
            print(f"🎯 SEGNALE: {signal['signal']} con confidenza {signal['confidence']:.3f}")
        else:
            print(f"⭕ Nessun segnale generato")
    
    print(f"\n🎉 Test completato!")

if __name__ == "__main__":
    test_debug_engine()
