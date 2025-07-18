"""
ConfigManager - Gestione centralizzata della configurazione del sistema
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger('QuantumTradingSystem')


class ConfigManager:
    """
    Gestisce la configurazione del sistema di trading quantistico
    """
    
    def __init__(self, config_path: str):
        """
        Inizializza il ConfigManager
        
        Args:
            config_path: Percorso del file di configurazione JSON o dict già caricato
        """
        if isinstance(config_path, dict):
            self._config = config_path
        else:
            self._config = self._load_config(config_path)
        
        # Valida la configurazione
        self._validate_config()
        
        # Estrae la lista dei simboli
        self.symbols = list(self._config.get('symbols', {}).keys())

    def _validate_config(self) -> None:
        """Valida la struttura base del file di configurazione"""
        required_sections = ['symbols', 'risk_parameters']
        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"Sezione {section} mancante nella configurazione")
        
        # Validazione simboli
        symbols_section = self._config.get('symbols', {})
        if not isinstance(symbols_section, dict) or len(symbols_section) == 0:
            raise ValueError("Sezione symbols deve contenere almeno un simbolo configurato")
        
        # Validazione parametri di rischio
        risk_params = self._config.get('risk_parameters', {})
        if not isinstance(risk_params, dict):
            raise ValueError("Sezione risk_parameters deve essere un dizionario")
    
    def _load_config(self, path: str) -> Dict:
        """
        Carica e normalizza il file di configurazione
        
        Args:
            path: Percorso del file JSON
            
        Returns:
            Dizionario con la configurazione normalizzata
        """
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                return self._normalize_config(config)
        except Exception as e:
            logger.error(f"Errore nel caricamento del config: {str(e)}", exc_info=True)
            raise
    
    def _normalize_config(self, config: Dict) -> Dict:
        """
        Normalizza la struttura della configurazione per gestire le duplicazioni
        
        Args:
            config: Configurazione grezza
            
        Returns:
            Configurazione normalizzata
        """
        # Unisci risk_parameters e risk_management
        if 'risk_management' in config and 'risk_parameters' in config:
            config['risk_parameters'].update(config['risk_management'])
            del config['risk_management']
        
        # Sposta le impostazioni di trailing stop da features a risk_parameters
        if 'features' in config and 'trailing_stop' in config['features']:
            if 'trailing_stop' not in config['risk_parameters']:
                config['risk_parameters']['trailing_stop'] = {}
            config['risk_parameters']['trailing_stop'].update(
                config['features']['trailing_stop'])
        
        return config
        
    @property
    def config(self) -> Dict:
        """Accesso alla configurazione completa"""
        return self._config
        
    def get(self, key: str, default=None):
        """
        Ottiene un valore dalla configurazione
        
        Args:
            key: Chiave da cercare
            default: Valore di default se la chiave non esiste
            
        Returns:
            Valore della configurazione o default
        """
        return self._config.get(key, default)
        
    def get_risk_params(self, symbol: Optional[str] = None) -> Dict:
        """
        Ottiene i parametri di rischio per un simbolo
        
        Args:
            symbol: Simbolo specifico (opzionale)
            
        Returns:
            Dizionario con i parametri di rischio
        """
        base = self.config.get('risk_parameters', {})
        if not symbol:
            return base
            
        symbol_config = self.config.get('symbols', {}).get(symbol, {}).get('risk_management', {})
        trailing_base = base.get('trailing_stop', {})
        trailing_symbol = symbol_config.get('trailing_stop', {})
        
        return {
            **base,
            **symbol_config,
            'trailing_stop': {
                **trailing_base,
                **trailing_symbol
            }
        }
        
    def get_max_allowed_spread(self, symbol: str) -> float:
        """
        Restituisce lo spread massimo consentito per un simbolo
        
        Args:
            symbol: Simbolo di trading
            
        Returns:
            Spread massimo in pips
        """
        try:
            DEFAULT_SPREADS = {
                'SP500': 10.0,
                'NAS100': 15.0,
                'XAUUSD': 30.0,
                'BTCUSD': 50.0,
                'ETHUSD': 40.0,
                'default': 20.0
            }
            
            risk_params = self.config.get('risk_parameters', {})
            spread_config = risk_params.get('max_spread', {})
            
            if isinstance(spread_config, dict):
                symbol_spread = spread_config.get(symbol, spread_config.get('default', 'auto'))
            else:
                symbol_spread = spread_config
                
            if isinstance(symbol_spread, str):
                symbol_spread = symbol_spread.lower()
                if symbol_spread in ('adaptive', 'auto'):
                    return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
            
            return float(symbol_spread)
            
        except Exception as e:
            logger.error(f"Errore determinazione spread per {symbol}: {str(e)}")
            return float(DEFAULT_SPREADS.get(symbol, DEFAULT_SPREADS['default']))
            
    def get_symbol_config(self, symbol: str) -> Dict:
        """
        Ottiene la configurazione completa per un simbolo
        
        Args:
            symbol: Simbolo di trading
            
        Returns:
            Configurazione del simbolo
        """
        return self.config.get('symbols', {}).get(symbol, {})
