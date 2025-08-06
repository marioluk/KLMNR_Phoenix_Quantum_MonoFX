# constants.py
# Tutte le costanti globali del progetto Phoenix Quantum MonoFX

# Costanti logging
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5
LOG_ENCODING = 'utf-8'

# Parametri di default QuantumEngine
DEFAULT_CACHE_TIMEOUT = 60
DEFAULT_WARNING_COOLDOWN = 300
DEFAULT_BUFFER_SIZE = 100
DEFAULT_SPIN_WINDOW = 20
DEFAULT_MIN_SPIN_SAMPLES = 10
DEFAULT_SPIN_THRESHOLD = 0.25
DEFAULT_SIGNAL_COOLDOWN = 300
DEFAULT_ENTROPY_THRESHOLDS = {'buy_signal': 0.55, 'sell_signal': 0.45}

# Spread di default per simboli
DEFAULT_SPREADS = {
    'SP500': 10.0,
    'NAS100': 15.0,
    'XAUUSD': 30.0,
    'BTCUSD': 50.0,
    'ETHUSD': 40.0,
    'default': 20.0
}

# Intervallo orario di default (esempio: 00:00-23:59)
DEFAULT_TIME_RANGE = (0, 0, 23, 59)
# Orario di trading di default (esempio: 09:00-17:30)
DEFAULT_TRADING_HOURS = "09:00-17:30"
