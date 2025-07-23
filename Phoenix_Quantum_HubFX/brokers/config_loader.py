"""
Multi-Broker Configuration Loader
Carica e gestisce configurazioni per multipli broker
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

from brokers.connection import BrokerConfig

logger = logging.getLogger('QuantumTradingSystem')


class MultiBrokerConfigLoader:
    """
    Carica configurazioni per multipli broker da file JSON
    Supporta configurazioni separate o unificate
    """
    
    def __init__(self, config_path: str):
        """
        Inizializza il loader con il percorso di configurazione
        
        Args:
            config_path: Percorso file configurazione principale
        """
        self.config_path = Path(config_path)
        self.base_config = self._load_base_config()
        
    def _load_base_config(self) -> Dict:
        """Carica la configurazione base"""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Errore caricamento config base: {str(e)}")
            raise

    def load_multi_broker_configs(self) -> List[BrokerConfig]:
        """
        Carica tutte le configurazioni broker disponibili
        
        Returns:
            Lista di BrokerConfig per ogni broker
        """
        broker_configs = []
        
        # 1. Cerca configurazioni multi-broker nel file principale
        if 'brokers' in self.base_config:
            broker_configs.extend(self._load_from_main_config())
        
        # 2. Cerca file di configurazione separati
        logger.info("🔍 Ricerca file di configurazione separati...")
        broker_configs.extend(self._load_from_separate_files())
        
        # 3. Se non trovate configurazioni multi-broker, usa quella principale
        if not broker_configs:
            logger.warning("Nessuna configurazione multi-broker trovata, uso configurazione singola")
            broker_configs.append(self._create_single_broker_config())
            
        logger.info(f"📊 Caricate {len(broker_configs)} configurazioni broker")
        for config in broker_configs:
            logger.info(f"   🏢 {config.name}: {config.server} (login: {config.login})")
            
        return broker_configs

    def _load_from_main_config(self) -> List[BrokerConfig]:
        """Carica configurazioni dalla sezione 'brokers' del file principale"""
        configs = []
        
        try:
            brokers_section = self.base_config['brokers']
            
            for broker_name, broker_data in brokers_section.items():
                # Merge con configurazione base
                merged_config = self._merge_with_base(broker_data)
                
                config = BrokerConfig(
                    name=broker_name,
                    mt5_path=merged_config['metatrader5']['path'],
                    login=int(merged_config['metatrader5']['login']),
                    password=merged_config['metatrader5']['password'],
                    server=merged_config['metatrader5']['server'],
                    port=int(merged_config['metatrader5'].get('port', 18889)),
                    timeout=int(merged_config['metatrader5'].get('timeout', 60000)),
                    symbols=list(merged_config.get('symbols', {}).keys()),
                    account_currency=merged_config.get('account_currency', 'USD'),
                    magic_base=merged_config.get('magic_number', 100000)
                )
                
                configs.append(config)
                logger.info(f"✅ Configurazione {broker_name} caricata da file principale")
                
        except Exception as e:
            logger.error(f"Errore caricamento configurazioni da file principale: {str(e)}")
            
        return configs

    def _load_from_separate_files(self) -> List[BrokerConfig]:
        """Cerca e carica file di configurazione separati per broker"""
        logger.info("🔍 DEBUG: Inizio _load_from_separate_files()")
        configs = []
        config_dir = self.config_path.parent
        logger.info(f"🗂️  DEBUG: Cerco in directory: {config_dir}")
        
        # Pattern di ricerca per file broker
        patterns = [
            "broker_*.json"  # Pattern principale per i nostri file
        ]
        
        found_files = []
        for pattern in patterns:
            pattern_files = list(config_dir.glob(pattern))
            logger.info(f"🔍 Pattern '{pattern}' in '{config_dir}': trovati {len(pattern_files)} file")
            for pf in pattern_files:
                logger.info(f"   📄 {pf.name}")
            found_files.extend(pattern_files)
            
        logger.info(f"🗂️  Totale file broker trovati: {len(found_files)}")
        
        if not found_files:
            logger.warning(f"❌ NESSUN FILE broker_*.json trovato in {config_dir}")
            # Elenchiamo tutti i file nella directory
            all_files = list(config_dir.glob("*.json"))
            logger.info(f"📁 File JSON presenti ({len(all_files)}):")
            for af in all_files:
                logger.info(f"   📄 {af.name}")
            return configs
            
        for config_file in found_files:
            try:
                with open(config_file) as f:
                    broker_config = json.load(f)
                    
                # 🎯 FILTRO BROKER ATTIVI - Salta se active = false
                if not broker_config.get('active', True):
                    logger.info(f"⏸️  Broker {config_file.name} disattivato (active: false)")
                    continue
                    
                # Determina nome broker dal filename o config
                broker_name = self._extract_broker_name(config_file, broker_config)
                
                # Merge con configurazione base se necessario
                merged_config = self._merge_with_base(broker_config)
                
                # Gestisci entrambi i formati: 'metatrader5' e 'mt5_config'
                mt5_section = merged_config.get('metatrader5') or merged_config.get('mt5_config', {})
                
                config = BrokerConfig(
                    name=broker_name,
                    mt5_path=mt5_section['path'],
                    login=int(mt5_section['login']),
                    password=mt5_section['password'],
                    server=mt5_section['server'],
                    port=int(mt5_section.get('port', 18889)),
                    symbols=self._extract_symbols(merged_config),
                    account_currency=merged_config.get('account_currency', 'USD'),
                    magic_base=merged_config.get('magic_number', merged_config.get('connection_config', {}).get('magic_base', 100000))
                )
                
                configs.append(config)
                logger.info(f"✅ Configurazione {broker_name} caricata da {config_file.name}")
                
            except Exception as e:
                logger.error(f"Errore caricamento {config_file}: {str(e)}")
                
        return configs

    def _extract_symbols(self, config: Dict) -> List[str]:
        """Estrae la lista symbols da vari formati di configurazione"""
        
        # 1. Formato standard: symbols come dizionario
        if 'symbols' in config and isinstance(config['symbols'], dict):
            return list(config['symbols'].keys())
            
        # 2. Formato trading_config: symbols come lista
        if 'trading_config' in config and 'symbols' in config['trading_config']:
            symbols = config['trading_config']['symbols']
            if isinstance(symbols, list):
                return symbols
            elif isinstance(symbols, dict):
                return list(symbols.keys())
                
        # 3. Formato risk_management con symbols
        if 'risk_management' in config and 'symbols' in config['risk_management']:
            symbols = config['risk_management']['symbols']
            if isinstance(symbols, list):
                return symbols
            elif isinstance(symbols, dict):
                return list(symbols.keys())
                
        # 4. Default symbols
        return ['EURUSD', 'GBPUSD', 'XAUUSD']

    def _extract_broker_name(self, config_file: Path, broker_config: Dict) -> str:
        """Estrae il nome del broker dal file o configurazione"""
        
        # 1. Cerca nel config
        if 'broker_name' in broker_config:
            return broker_config['broker_name']
            
        # 2. Estrai dal filename
        filename = config_file.stem.upper()
        
        if 'FTMO' in filename:
            return 'FTMO'
        elif 'THE5ERS' in filename or '5ERS' in filename:
            return 'The5ers'
        elif 'TOPSTEP' in filename:
            return 'TopStep'
        elif 'DARWINEX' in filename:
            return 'Darwinex'
        elif 'BROKER' in filename:
            # Cerca pattern broker-NOME o NOME-broker
            parts = filename.split('-')
            for i, part in enumerate(parts):
                if 'BROKER' in part and i > 0:
                    return parts[i-1].title()
                elif 'BROKER' in part and i < len(parts)-1:
                    return parts[i+1].title()
                    
        # 3. Default con timestamp
        return f"Broker_{int(time.time())}"

    def _merge_with_base(self, broker_config: Dict) -> Dict:
        """
        Merge configurazione broker con quella base
        
        Args:
            broker_config: Configurazione specifica del broker
            
        Returns:
            Configurazione merged
        """
        # Copia base
        merged = self.base_config.copy()
        
        # Override con configurazione broker
        for key, value in broker_config.items():
            if isinstance(value, dict) and key in merged:
                # Merge ricorsivo per dizionari
                merged[key].update(value)
            else:
                # Override diretto
                merged[key] = value
                
        return merged

    def _create_single_broker_config(self) -> BrokerConfig:
        """Crea configurazione broker singolo dalla config principale"""
        
        # Determina nome broker dal server
        server = self.base_config['metatrader5']['server']
        if 'FivePercent' in server or 'The5ers' in server:
            broker_name = 'The5ers'
        elif 'FTMO' in server:
            broker_name = 'FTMO'
        else:
            broker_name = 'MainBroker'
            
        return BrokerConfig(
            name=broker_name,
            mt5_path=self.base_config['metatrader5']['path'],
            login=int(self.base_config['metatrader5']['login']),
            password=self.base_config['metatrader5']['password'],
            server=self.base_config['metatrader5']['server'],
            port=int(self.base_config['metatrader5'].get('port', 18889)),
            symbols=list(self.base_config.get('symbols', {}).keys()),
            account_currency=self.base_config.get('account_currency', 'USD'),
            magic_base=self.base_config.get('magic_number', 100000)
        )

    def create_sample_multi_broker_config(self, output_path: str) -> None:
        """
        Crea un file di esempio per configurazione multi-broker
        
        Args:
            output_path: Percorso file di output
        """
        sample_config = {
            "brokers": {
                "The5ers": {
                    "metatrader5": {
                        "login": 25437097,
                        "password": "password_the5ers",
                        "server": "FivePercentOnline-Real",
                        "path": "C:/MT5_The5ers/terminal64.exe",
                        "port": 18889
                    },
                    "account_currency": "USD",
                    "magic_number": 177251,
                    "symbols": {
                        "EURUSD": {"risk_management": {"contract_size": 0.01}},
                        "GBPUSD": {"risk_management": {"contract_size": 0.01}},
                        "XAUUSD": {"risk_management": {"contract_size": 0.01}}
                    }
                },
                "FTMO": {
                    "metatrader5": {
                        "login": 12345678,
                        "password": "password_ftmo",
                        "server": "FTMO-Server01",
                        "path": "C:/MT5_FTMO/terminal64.exe",
                        "port": 443
                    },
                    "account_currency": "USD", 
                    "magic_number": 277251,
                    "symbols": {
                        "EURUSD": {"risk_management": {"contract_size": 0.01}},
                        "USDJPY": {"risk_management": {"contract_size": 0.01}},
                        "NAS100": {"risk_management": {"contract_size": 0.01}}
                    }
                }
            },
            "global_settings": {
                "max_total_positions": 10,
                "max_positions_per_broker": 5,
                "enable_cross_broker_hedging": True,
                "preferred_execution_order": ["The5ers", "FTMO"]
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(sample_config, f, indent=4)
            
        logger.info(f"📝 Configurazione di esempio creata: {output_path}")


# Helper per import
import time
