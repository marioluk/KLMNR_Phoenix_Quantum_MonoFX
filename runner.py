"""
Modulo runner.py: avvio e setup del sistema Phoenix Quantum MonoFX
"""
from phoenix_quantum_monofx_program import (
    set_config, auto_correct_symbols, load_config, set_log_file, get_log_file, set_logger, setup_logger, get_logger,
    QuantumEngine, threading, datetime, time
)
from utils.constants import DEFAULT_CONFIG_RELOAD_INTERVAL

def start_system():
    set_config(auto_correct_symbols(load_config()))

    def periodic_reload_config(interval: int = DEFAULT_CONFIG_RELOAD_INTERVAL) -> None:
        while True:
            time.sleep(interval)
            try:
                new_config = load_config()
                set_config(auto_correct_symbols(new_config))
                print(f"[{datetime.now()}] Configurazione ricaricata.")
            except Exception as e:
                print(f"Errore reload config: {e}")

    reload_thread = threading.Thread(target=periodic_reload_config, daemon=True)
    reload_thread.start()

    set_log_file(get_log_file())
    set_logger(setup_logger())
    # clean_old_logs()  # Funzione non implementata, rimuovere o implementare se necessario
    global logger
    logger = get_logger()

    try:
        config_obj = globals().get('_GLOBAL_CONFIG', None)
        if config_obj is not None:
            conf = getattr(config_obj, 'config', config_obj)
        else:
            conf = {}
        engine = QuantumEngine(conf)
        def tick_acquisition_worker():
            logger.info("[THREAD] Avvio thread acquisizione tick QuantumEngine ogni 1s.")
            while True:
                try:
                    # ...tick acquisition logic...
                    pass
                except Exception as e:
                    logger.error(f"[THREAD] Errore tick acquisition: {e}")
                time.sleep(1)
        tick_thread = threading.Thread(target=tick_acquisition_worker, daemon=True)
        tick_thread.start()
    except Exception as e:
        logger.critical(f"[MAIN] Errore avvio thread acquisizione tick: {e}", exc_info=True)

if __name__ == "__main__":
    start_system()
