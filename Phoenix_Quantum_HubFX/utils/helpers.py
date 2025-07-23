from log_utils.setup import setup_logger
"""
Funzioni utility per il Quantum Trading System
"""

from datetime import datetime, time as dt_time
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger('QuantumTradingSystem')


def parse_time(time_str: str) -> Tuple[dt_time, dt_time]:
    """
    Converte una stringa 'HH:MM-HH:MM' in due oggetti time
    
    Args:
        time_str: Stringa nel formato "HH:MM-HH:MM" o lista già parsata
        
    Returns:
        Tupla con (ora_inizio, ora_fine)
    """
    try:
        if isinstance(time_str, list):  # Se già parsato
            # Assicurati che gli elementi siano oggetti time
            start = time_str[0]
            end = time_str[1]
            if isinstance(start, str):
                start = datetime.strptime(start, "%H:%M").time()
            if isinstance(end, str):
                end = datetime.strptime(end, "%H:%M").time()
            return start, end
            
        if "-" not in time_str:  # Formato singolo
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            return time_obj, time_obj
            
        start_str, end_str = time_str.split('-')
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        return start, end
        
    except ValueError as e:
        logger.error(f"Formato orario non valido: {time_str} | Errore: {str(e)}")
        return dt_time(0, 0), dt_time(23, 59)  # Default 24h


def is_trading_hours(symbol: str, config: Dict) -> bool:
    """
    Verifica se il simbolo è in orario di trading
    
    Args:
        symbol: Simbolo da verificare (es. "EURUSD")
        config: Configurazione completa del sistema
        
    Returns:
        True se è orario di trading, False altrimenti
    """
    try:
        symbol_config = config.get('symbols', {}).get(symbol, {})
        trading_hours = symbol_config.get('trading_hours', ["00:00-23:59"])
        now = datetime.now().time()
        
        for time_range in trading_hours:
            if isinstance(time_range, str):  # Formato legacy "HH:MM-HH:MM"
                start, end = parse_time(time_range)
                if start <= end:
                    if start <= now <= end:
                        return True
                else:  # Overnight (es. 22:00-02:00)
                    if now >= start or now <= end:
                        return True
                        
            elif isinstance(time_range, list):  # Nuovo formato ["HH:MM", "HH:MM"]
                start, end = parse_time("-".join(time_range))
                if start <= now <= end:
                    return True
                    
        return False
        
    except Exception as e:
        logger.error(f"Errore controllo orari {symbol}: {str(e)}")
        return True  # Fallback: assume sempre trading


def load_config(config_path: str = "PRO-THE5ERS-QM-PHOENIX-GITCOP-config-STEP1.json") -> Dict:
    """
    Carica il file di configurazione JSON
    
    Args:
        config_path: Percorso del file di configurazione
        
    Returns:
        Dizionario con la configurazione
    """
    import json
    with open(config_path) as f:
        return json.load(f)


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Formatta un importo in valuta
    
    Args:
        amount: Importo da formattare
        currency: Codice valuta (default USD)
        
    Returns:
        Stringa formattata (es. "$1,234.56")
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Divisione sicura che evita divisione per zero
    
    Args:
        a: Numeratore
        b: Denominatore  
        default: Valore di default se b è zero
        
    Returns:
        Risultato della divisione o default
    """
    try:
        return a / b if b != 0 else default
    except (TypeError, ValueError):
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limita un valore tra min e max
    
    Args:
        value: Valore da limitare
        min_val: Valore minimo
        max_val: Valore massimo
        
    Returns:
        Valore limitato nell'intervallo [min_val, max_val]
    """
    return max(min_val, min(value, max_val))
