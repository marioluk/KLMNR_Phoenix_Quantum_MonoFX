
from core.quantum_risk_manager import QuantumRiskManager
from utils.utils import setup_logger, clean_old_logs
# RIMOSSO: importazione globale is_trading_hours, ora gestito solo come metodo della classe

import os
import csv
import json
import time
import threading
import datetime
from datetime import datetime, timedelta
from collections import defaultdict
import MetaTrader5 as mt5
from core.trading_metrics import TradingMetrics
from core.daily_drawdown_tracker import DailyDrawdownTracker
from core.quantum_engine import QuantumEngine


class QuantumTradingSystem:
    def is_trading_hours(self, symbol):
        """
        Restituisce True se il simbolo è in orario di trading secondo la config. Logga sempre la decisione.
        """
        try:
            from utils.utils import is_trading_hours as _is_trading_hours
            config_dict = self._config.config if hasattr(self._config, 'config') else self._config
            trading_hours = _is_trading_hours(symbol, config_dict)
            self.logger.info(f"[TRADING HOURS] {symbol}: {trading_hours}")
            return trading_hours
        except Exception as e:
            self.logger.warning(f"Errore calcolo trading_hours per {symbol}: {e}")
            return True  # fallback: consenti trading se errore
    def __init__(self, config_path: str):
        """Costruttore principale"""
        self.logger = setup_logger(config_path)
        self.symbols = []  # fallback sicuro
        self._config_path = config_path
        self.running = False
        self.logger.info(
            "\n==================== [AVVIO QUANTUM TRADING SYSTEM] ====================\n"
            f"File configurazione: {config_path}\n"
            "------------------------------------------------------\n"
        )
        self._load_configuration(config_path)  # Questo inizializza self._config
        self.logger.info("✅ Configurazione caricata")
        if not hasattr(self._config, 'config') or 'symbols' not in self._config.config:
            self.logger.error("Configurazione simboli non valida nel file di configurazione")
        else:
            self.symbols = list(self._config.config['symbols'].keys())
            self.logger.info(
                "\n-------------------- [SIMBOLI CONFIGURATI] ----------------------\n"
                f"Simboli trovati: {self.symbols}\n"
                "------------------------------------------------------\n"
            )
        self.logger.info("🔄 Inizializzazione componenti core...")
        if not self._initialize_mt5():
            raise RuntimeError("Inizializzazione MT5 fallita")
        self.logger.info("📡 Attivazione simboli in MT5...")
        self._activate_symbols()
        self.logger.info("✅ Simboli attivati")
        self.logger.info("🧠 Inizializzazione Quantum Engine...")
        self.engine = QuantumEngine(self._config.config)
        self.logger.info("✅ Quantum Engine pronto")
        self.risk_manager = QuantumRiskManager(self._config.config, self.engine, self)  # Passa il dict config
        self.max_positions = self._config.config.get('risk_parameters', {}).get('max_positions', 4)
        self.current_positions = 0
        self.trade_count = defaultdict(int)
        self._last_trade_count_reset = datetime.datetime.now().date()
        self._trade_count_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'trade_count_state.json')
        self.last_position_check = 0
        self.last_connection_check = 0
        self.last_account_update = 0
        self.last_tick_check = 0
        self.last_buffer_check = 0
        self.metrics_lock = threading.Lock()
        self.position_lock = threading.Lock()
        self.metrics = TradingMetrics()
        self.account_info = mt5.account_info()
        self.currency = (
            self.account_info.currency 
            if self.account_info 
            else self._config.config.get('account_currency', 'USD')
        )
        if not self.account_info:
            self.logger.warning(f"Usando valuta di fallback: {self.currency}")
        self.trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'symbol_stats': defaultdict(dict)
        }
        initial_equity = self.account_info.equity if self.account_info else 10000
        self.drawdown_tracker = DailyDrawdownTracker(
            initial_equity=initial_equity,
            config=self._config.config
        )
        self._load_trade_count_state()
        self.logger.info(
            "\n==================== [SISTEMA INIZIALIZZATO] ====================\n"
            f"Simboli configurati: {self.symbols}\n"
            f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}\n"
            "======================================================\n"
        )
        self.logger.info("Sistema inizializzato correttamente")
        self.logger.info(f"Simboli configurati: {self.symbols}")
        self.logger.info(f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}")

    def get_dynamic_risk_percent(self):
        """
        Restituisce il risk_percent dinamico in base al drawdown attuale.
        I limiti safe/soft sono ora presi dal file di configurazione (challenge_specific.drawdown_protection).
        """
        dd = None
        if hasattr(self, 'drawdown_tracker') and hasattr(self.drawdown_tracker, 'get_drawdown'):
            dd = self.drawdown_tracker.get_drawdown()
        if dd is None:
            dd = 0.0
        base_risk = self._config.config.get('risk_parameters', {}).get('risk_percent', 0.007)
        # Leggi limiti dal config
        challenge = self._config.config.get('challenge_specific', {})
        dd_prot = challenge.get('drawdown_protection', {})
        # safe_limit: soglia inferiore (default 1.0), soft_limit: soglia superiore (default 2.0)
        safe = float(dd_prot.get('safe_limit', 1.0))
        soft = float(dd_prot.get('soft_limit', 2.0))
        if dd < safe:
            return base_risk * 1.1  # acceleratore
        elif safe <= dd < soft:
            factor = 1 - 0.5 * ((dd - safe) / (soft - safe))
            return base_risk * factor
        else:
            return base_risk * 0.2  # freno massimo
# =============================================================
# CORRELAZIONE TRA TIPOLOGIA DI TRADING E CALCOLO SL/TP/TS
# =============================================================
# | Tipologia   | Stop Loss (SL)         | Take Profit (TP)         | Trailing Stop (TS)                | Note operative                       |
# |-------------|------------------------|--------------------------|------------------------------------|--------------------------------------|
# | Scalping    | 6-12 pips (molto stretto) | 10-20 pips (stretto)      | Attivazione rapida, step piccoli   | Protezione immediata, trade brevi    |
# | Intraday    | 15-30 pips (medio)     | 30-60 pips (medio)       | Attivazione media, step medi       | Nessuna posizione overnight          |
# | Swing       | 50-120 pips (ampio)    | 100-250 pips (ampio)     | Attivazione solo dopo movimenti ampi, step larghi | Posizioni multi-day, oscillazioni ampie |
# | Position    | 150-400 pips (molto ampio) | 300-800 pips (molto ampio) | Attivazione tardiva, step molto larghi | Segue trend di fondo, trade lunghi   |
#
# Il calcolo di SL/TP/TS avviene in QuantumRiskManager:
#   - SL/TP sono calcolati dinamicamente in base a parametri di config, volatilità e tipologia trading.
#   - Trailing Stop viene configurato per ogni simbolo e tipologia, con step e attivazione coerenti.
#   - La logica segue la stessa struttura dell'optimizer: per operatività più lunga, parametri più ampi; per operatività breve, parametri più stretti e reattivi.
#   - Esempio: sl_price, tp_price = self.risk_manager.calculate_dynamic_levels(symbol, order_type, price)
# =============================================================

    
    
    
    def debug_trade_decision(self, symbol):
        """Debug step-by-step della decisione di trading per un simbolo: logga ogni condizione e mostra il motivo per cui un ordine viene o non viene messo. Esporta anche i motivi in un file CSV."""
        def write_report_row(step, detail, extra=None):
            try:
                report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'trade_decision_report.csv')
                file_exists = os.path.isfile(report_path)
                with open(report_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow(['timestamp', 'symbol', 'step', 'detail', 'extra'])
                    
                    writer.writerow([
                        datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
                        symbol,
                        step,
                        detail,
                        extra if extra is not None else ''
                    ])
            except Exception as e:
                logger.error(f"Errore scrittura report trade decision: {str(e)}")
        try:
            logger.info(f"\n==================== [DEBUG TRADE DECISION] ====================\nSymbol: {symbol}\n--------------------")
            # 1. Può fare trading?
            can_trade = self.engine.can_trade(symbol)
            logger.info(f"can_trade: {can_trade}")
            if not can_trade:
                msg = "Motivo: can_trade() = False (cooldown, spread, max posizioni, ecc.)"
                # Dettagli tecnici anche qui
                ticks = list(self.engine.get_tick_buffer(symbol))
                buffer_tick = len(ticks)
                spin = None
                confidence = None
                entropy = None
                spin_window = min(getattr(self.engine, 'spin_window', 20), buffer_tick)
                recent_ticks = ticks[-spin_window:]
                deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10) if recent_ticks else ()
                try:
                    if deltas:
                        entropy = self.engine.calculate_entropy(deltas)
                    if recent_ticks:
                        spin, confidence = self.engine.calculate_spin(recent_ticks)
                except Exception as e:
                    logger.warning(f"Errore calcolo diagnostica can_trade: {e}")
                motivi = []
                if confidence is not None:
                    motivi.append(f"Confidence: {confidence:.3f}")
                else:
                    motivi.append("Confidence: N/A")
                if entropy is not None:
                    motivi.append(f"Entropia: {entropy:.3f}")
                else:
                    motivi.append("Entropia: N/A")
                if spin is not None:
                    motivi.append(f"Spin: {spin:.3f}")
                else:
                    motivi.append("Spin: N/A")
                motivi.append(f"Buffer tick: {buffer_tick}")
                extra = "; ".join(motivi)
                logger.info(msg + (f" | Dettaglio: {extra}" if extra else ""))
                write_report_row('can_trade', msg, extra)
                return

            # 2. Orari di trading
            trading_hours = self.is_trading_hours(symbol)
            logger.info(f"trading_hours: {trading_hours}")
            if not trading_hours:
                msg = "Motivo: fuori orario di trading"
                # Dettagli tecnici anche qui
                ticks = list(self.engine.get_tick_buffer(symbol))
                buffer_tick = len(ticks)
                spin = None
                confidence = None
                entropy = None
                spin_window = min(getattr(self.engine, 'spin_window', 20), buffer_tick)
                recent_ticks = ticks[-spin_window:]
                deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10) if recent_ticks else ()
                try:
                    if deltas:
                        entropy = self.engine.calculate_entropy(deltas)
                    if recent_ticks:
                        spin, confidence = self.engine.calculate_spin(recent_ticks)
                except Exception as e:
                    logger.warning(f"Errore calcolo diagnostica trading_hours: {e}")
                motivi = []
                if confidence is not None:
                    motivi.append(f"Confidence: {confidence:.3f}")
                else:
                    motivi.append("Confidence: N/A")
                if entropy is not None:
                    motivi.append(f"Entropia: {entropy:.3f}")
                else:
                    motivi.append("Entropia: N/A")
                if spin is not None:
                    motivi.append(f"Spin: {spin:.3f}")
                else:
                    motivi.append("Spin: N/A")
                motivi.append(f"Buffer tick: {buffer_tick}")
                extra = "; ".join(motivi)
                logger.info(msg + (f" | Dettaglio: {extra}" if extra else ""))
                write_report_row('trading_hours', msg, extra)
                return

            # 3. Posizioni già aperte
            existing_positions = mt5.positions_get(symbol=symbol)
            has_position = existing_positions and len(existing_positions) > 0
            logger.info(f"has_position: {has_position}")
            if has_position:
                msg = "Motivo: posizione già aperta su questo simbolo"
                logger.info(msg)
                write_report_row('has_position', msg)
                return

            # 4. Limite posizioni totali
            current_positions = len(mt5.positions_get() or [])
            logger.info(f"current_positions: {current_positions} / max_positions: {self.max_positions}")
            if current_positions >= self.max_positions:
                msg = "Motivo: raggiunto limite massimo posizioni totali"
                logger.info(msg)
                write_report_row('max_positions', msg)
                return

            # 5. Limite trade giornalieri
            risk_params = self._config.config.get('risk_parameters', {})
            daily_limit = risk_params.get('max_daily_trades', 5)
            limit_mode = risk_params.get('daily_trade_limit_mode', 'global')
            if limit_mode == 'global':
                total_trades_today = sum(self.trade_count.values())
                logger.info(f"total_trades_today: {total_trades_today} / daily_limit: {daily_limit}")
                if total_trades_today >= daily_limit:
                    msg = f"Motivo: raggiunto limite trade giornalieri globali ({total_trades_today}/{daily_limit})"
                    logger.info(msg)
                    write_report_row('daily_limit_global', msg)
                    return
            else:
                trades_for_symbol = self.trade_count.get(symbol, 0)
                logger.info(f"trades_for_symbol: {trades_for_symbol} / daily_limit: {daily_limit}")
                if trades_for_symbol >= daily_limit:
                    msg = f"Motivo: raggiunto limite trade giornalieri per simbolo ({trades_for_symbol}/{daily_limit})"
                    logger.info(msg)
                    write_report_row('daily_limit_symbol', msg)
                    return

            # 6. Buffer tick sufficiente
            buffer_size = len(self.engine.get_tick_buffer(symbol))
            min_samples = getattr(self.engine, 'min_spin_samples', 0)
            logger.info(f"buffer_size: {buffer_size} / min_spin_samples: {min_samples}")
            if buffer_size < min_samples:
                msg = "Motivo: buffer tick insufficiente per generare segnale"
                logger.info(msg)
                write_report_row('buffer_tick', msg)
                return

            # 7. Ottieni segnale
            motivi_hold = []
            signal, price = self.engine.get_signal(symbol, for_trading=False, motivo_for_csv=motivi_hold)
            logger.info(f"Segnale calcolato: {signal} (Price: {price})")
            if signal not in ["BUY", "SELL"]:
                msg = "Motivo: nessun segnale BUY/SELL valido (HOLD o None)"
                # Inserisci sempre i dettagli tecnici nella colonna extra
                entropy = None
                spin = None
                confidence = None
                ticks = list(self.engine.get_tick_buffer(symbol))
                spin_window = min(getattr(self.engine, 'spin_window', 20), len(ticks))
                recent_ticks = ticks[-spin_window:]
                deltas = tuple(t['delta'] for t in recent_ticks if abs(t['delta']) > 1e-10) if recent_ticks else ()
                try:
                    if deltas:
                        entropy = self.engine.calculate_entropy(deltas)
                    if recent_ticks:
                        spin, confidence = self.engine.calculate_spin(recent_ticks)
                except Exception as e:
                    logger.warning(f"Errore calcolo diagnostica HOLD: {e}")
                motivi = []
                if confidence is not None:
                    motivi.append(f"Confidence: {confidence:.3f}")
                    if confidence < 0.8:
                        motivi.append(f"Confidence troppo bassa")
                else:
                    motivi.append("Confidence: N/A")
                if entropy is not None:
                    buy_thresh = getattr(self.engine, 'entropy_thresholds', {'buy_signal': 0.55}).get('buy_signal', 0.55)
                    sell_thresh = getattr(self.engine, 'entropy_thresholds', {'sell_signal': 0.45}).get('sell_signal', 0.45)
                    motivi.append(f"Entropia: {entropy:.3f}")
                    if entropy <= buy_thresh:
                        motivi.append(f"Entropia bassa (<= {buy_thresh:.3f})")
                    if entropy >= sell_thresh:
                        motivi.append(f"Entropia alta (>= {sell_thresh:.3f})")
                else:
                    motivi.append("Entropia: N/A")
                if spin is not None:
                    motivi.append(f"Spin: {spin:.3f}")
                else:
                    motivi.append("Spin: N/A")
                motivi.append(f"Buffer tick: {len(ticks)}")
                # Aggiungi il motivo tecnico preciso del HOLD in cima
                if motivi_hold:
                    motivi.insert(0, f"Motivo tecnico: {motivi_hold[0]}")
                extra = "; ".join(motivi)
                logger.info(msg + (f" | Dettaglio: {extra}" if extra else ""))
                write_report_row('signal', msg, extra)
                return

            # 8. Cooldown segnale
            if hasattr(self.engine, 'last_signal_time') and symbol in self.engine.last_signal_time:
                time_since_last = time.time() - self.engine.last_signal_time[symbol]
                if time_since_last < self.engine.signal_cooldown:
                    msg = f"Motivo: cooldown segnale attivo ({self.engine.signal_cooldown - time_since_last:.1f}s rimanenti)"
                    logger.info(msg)
                    write_report_row('signal_cooldown', msg)
                    return

            # 9. Conferma segnale per trading
            trading_signal, trading_price = self.engine.get_signal(symbol, for_trading=True)
            logger.info(f"Segnale confermato per trading: {trading_signal} (Price: {trading_price})")
            if trading_signal not in ["BUY", "SELL"]:
                msg = "Motivo: segnale non confermato per trading effettivo"
                logger.info(msg)
                write_report_row('signal_confirm', msg)
                return

            # 10. Calcola size
            size = self.risk_manager.calculate_position_size(symbol, trading_price, trading_signal)
            logger.info(f"Size calcolata: {size}")
            if size <= 0:
                msg = "Motivo: size calcolata nulla o negativa"
                logger.info(msg)
                write_report_row('size', msg)
                return

            # 11. Pronto per esecuzione trade
            msg = f"TUTTE LE CONDIZIONI OK: pronto per esecuzione trade {trading_signal} su {symbol} (size: {size})"
            logger.info(msg)
            write_report_row('ok', msg)
            # (Non esegue realmente il trade, solo debug)
        except Exception as e:
            logger.error(f"[DEBUG TRADE DECISION] Errore per {symbol}: {str(e)}", exc_info=True)
            # Caso: self._config è un dict
            return list(self._config['symbols'].keys())
        return []
    
    def _main_loop(self):
        """
        cuore pulsante
        Loop principale con variabili di tempo come attributi di istanza
        Loop principale di trading
        """
        # NB: KeyboardInterrupt viene gestito SOLO nel ciclo esterno (start)
        while self.running:
            try:
                # Verifica connessione MT5
                if not mt5.terminal_info() or not mt5.terminal_info().connected:
                    logger.warning("Connessione MT5 persa, tentativo di riconnessione...")
                    if self._verify_connection():
                        logger.info("Riconnessione MT5 riuscita.")
                    else:
                        logger.error("Riconnessione MT5 fallita. Attendo 5 secondi e riprovo.")
                        self._safe_sleep(5)
                        continue
                else:
                    logger.debug("Connessione MT5 OK")
                current_time = time.time()
                # Controlli periodici
                if current_time - self.last_connection_check > 30:  # Check più frequente
                    if not self._verify_connection():
                        self._safe_sleep(5)
                        continue
                    self.last_connection_check = current_time
                if current_time - self.last_connection_check > 60:
                    self._verify_connection()
                    self.last_connection_check = current_time
                if current_time - self.last_account_update > 60:
                    self._update_account_info()
                    self.last_account_update = current_time
                    self._check_drawdown_limits()
                if current_time - self.last_tick_check > 300:
                    self.engine.check_tick_activity()  # Qui viene chiamato check_tick_activity()
                    self.last_tick_check = current_time
                    # Debug periodico dello stato trading (ogni 5 minuti, per tutti i simboli)
                    for symbol in self.symbols:
                        self.debug_trade_status(symbol)
                if time.time() - self.last_buffer_check > 300:  # 5 minuti
                    self.check_buffers()
                    self.last_buffer_check = time.time()
                if current_time - self.last_position_check > 30:
                    self._monitor_open_positions()
                    self._validate_positions()
                    self.close_positions_before_weekend()  # <--- AGGIUNTO QUI
                    self.last_position_check = current_time
                for symbol in self.symbols:
                    tick = mt5.symbol_info_tick(symbol)
                    logger.debug(
                        "\n-------------------- [DEBUG TICK] ----------------------\n"
                        f"Symbol: {symbol}\n"
                        f"Tick: {tick}\n"
                        "------------------------------------------------------\n"
                    )
                    if tick:
                        logger.debug(
                            "\n-------------------- [DEBUG TICK] ----------------------\n"
                            f"Symbol: {symbol}\n"
                            f"Tick.bid: {getattr(tick, 'bid', None)}\n"
                            "------------------------------------------------------\n"
                        )
                        self.engine.process_tick(symbol, tick.bid)
                        buffer_size = len(self.engine.get_tick_buffer(symbol))
                        logger.debug(
                            "\n-------------------- [BUFFER-DEBUG] --------------------\n"
                            f"Symbol: {symbol}\n"
                            f"Buffer Size: {buffer_size}\n"
                            "------------------------------------------------------\n"
                        )
                # Gestione errori SOLO per _process_symbols, non per KeyboardInterrupt
                start_time = time.time()
                self._process_symbols()
                process_time = time.time() - start_time
                if process_time > 5:
                    logger.warning(f"Processamento simboli lento: {process_time:.2f}s")
                self._safe_sleep(0.5)
            except Exception as e:
                logger.error(f"Errore nel processamento simboli: {str(e)}", exc_info=True)
                self._safe_sleep(5)
    """
    Sistema completo di trading algoritmico quantistico
    """

    def get_live_status(self):
        """Restituisce lo stato live del sistema per la dashboard (tick, equity, bilancio, P&L, drawdown, posizioni)"""
        try:
            # Info account
            account = mt5.account_info()
            equity = account.equity if account else None
            balance = account.balance if account else None
            currency = account.currency if account else 'USD'
            # Drawdown
            drawdown = None
            if hasattr(self, 'drawdown_tracker'):
                drawdown = self.drawdown_tracker.get_drawdown() if hasattr(self.drawdown_tracker, 'get_drawdown') else None
            # P&L
            total_profit = self.trade_metrics.get('total_profit', 0.0)
            # Posizioni aperte
            open_positions = []
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    open_positions.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'price_current': pos.price_current,
                        'profit': pos.profit,
                        'sl': pos.sl,
                        'tp': pos.tp,
                        'time': pos.time
                    })
            # Tick e dati di mercato per ogni simbolo
            symbols_data = {}
            for symbol in self._config.config['symbols']:
                tick = mt5.symbol_info_tick(symbol)
                symbols_data[symbol] = {
                    'bid': getattr(tick, 'bid', None),
                    'ask': getattr(tick, 'ask', None),
                    'last': getattr(tick, 'last', None),
                    'spread': getattr(tick, 'ask', 0) - getattr(tick, 'bid', 0) if tick else None,
                    'time': getattr(tick, 'time', None)
                }
            return {
                'equity': equity,
                'balance': balance,
                'currency': currency,
                'drawdown': drawdown,
                'total_profit': total_profit,
                'open_positions': open_positions,
                'symbols_data': symbols_data
            }
        except Exception as e:
            logger.error(f"Errore get_live_status: {str(e)}")
            return {}

    def get_trade_history(self):
        """Restituisce lo storico operazioni reali da MT5 (ultimi 30 giorni)"""
        
        try:
            date_to = datetime.now()
            date_from = date_to - timedelta(days=30)
            deals = mt5.history_deals_get(date_from, date_to)
            history = []
            if deals:
                for d in deals:
                    history.append({
                        'ticket': d.ticket,
                        'symbol': d.symbol,
                        'type': 'BUY' if d.type == mt5.ORDER_TYPE_BUY else 'SELL',
                        'volume': d.volume,
                        'price': d.price,
                        'profit': d.profit,
                        'time': d.time,
                        'comment': d.comment
                    })
            return history
        except Exception as e:
            logger.error(f"Errore get_trade_history: {str(e)}")
            return []

    def send_manual_order(self, symbol, type_, size, sl=None, tp=None):
        """
        Invia un ordine manuale buy/sell su MT5
        Args:
            symbol: str
            type_: 'BUY' o 'SELL'
            size: float
            sl: float (prezzo stop loss)
            tp: float (prezzo take profit)
        Returns:
            dict: risultato operazione
        """
        try:
            if type_ == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
            elif type_ == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
            else:
                return {'success': False, 'error': 'Tipo ordine non valido'}

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {'success': False, 'error': f'Simbolo {symbol} non trovato'}

            price = symbol_info.ask if order_type == mt5.ORDER_TYPE_BUY else symbol_info.bid
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': float(size),
                'type': order_type,
                'price': price,
                'sl': sl if sl else 0.0,
                'tp': tp if tp else 0.0,
                'deviation': 10,
                'magic': 123456,
                'comment': 'Manual order from dashboard',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'ticket': result.order, 'result': str(result)}
            else:
                return {'success': False, 'error': str(result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def modify_order(self, ticket, sl=None, tp=None):
        """
        Modifica SL/TP di una posizione aperta
        Args:
            ticket: int
            sl: float
            tp: float
        Returns:
            dict: risultato operazione
        """
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'error': f'Posizione {ticket} non trovata'}
            pos = position[0]
            request = {
                'action': mt5.TRADE_ACTION_SLTP,
                'position': ticket,
                'sl': sl if sl else pos.sl,
                'tp': tp if tp else pos.tp,
                'symbol': pos.symbol,
                'magic': pos.magic,
                'comment': 'Modify SL/TP from dashboard'
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'result': str(result)}
            else:
                return {'success': False, 'error': str(result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def close_order(self, ticket):
        """
        Chiude manualmente una posizione aperta
        Args:
            ticket: int
        Returns:
            dict: risultato operazione
        """
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'error': f'Posizione {ticket} non trovata'}
            pos = position[0]
            symbol = pos.symbol
            volume = pos.volume
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info(symbol).ask
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': volume,
                'type': order_type,
                'position': ticket,
                'price': price,
                'deviation': 10,
                'magic': pos.magic,
                'comment': 'Manual close from dashboard',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'result': str(result)}
            else:
                return {'success': False, 'error': str(result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        
    def _load_trade_count_state(self):
        
        try:
            if os.path.isfile(self._trade_count_file):
                with open(self._trade_count_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                file_date = data.get('date')
                today = datetime.now().strftime('%Y-%m-%d')
                if file_date == today:
                    self.trade_count = defaultdict(int, data.get('trade_count', {}))
                    self._last_trade_count_reset = datetime.strptime(file_date, '%Y-%m-%d').date()
                else:
                    self.trade_count = defaultdict(int)
                    self._last_trade_count_reset = datetime.now().date()
        except Exception as e:
            logger.error(f"Errore caricamento stato trade_count: {e}")

    def _save_trade_count_state(self):
        
        try:
            os.makedirs(os.path.dirname(self._trade_count_file), exist_ok=True)
            data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trade_count': dict(self.trade_count)
            }
            with open(self._trade_count_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Errore salvataggio stato trade_count: {e}")
        # Inizializza qui tutte le variabili di tempo per evitare AttributeError
        self.last_position_check = 0
        self.last_connection_check = 0
        self.last_account_update = 0
        self.last_tick_check = 0
        self.last_buffer_check = 0
        self.metrics_lock = threading.Lock()
        self.position_lock = threading.Lock()
        self.metrics = TradingMetrics()
        self.account_info = mt5.account_info()
        self.currency = (
            self.account_info.currency 
            if self.account_info 
            else self._config.config.get('account_currency', 'USD')
        )
        if not self.account_info:
            logger.warning(f"Usando valuta di fallback: {self.currency}")
        self.trade_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'symbol_stats': defaultdict(dict)
        }
        initial_equity = self.account_info.equity if self.account_info else 10000
        self.drawdown_tracker = DailyDrawdownTracker(
            initial_equity=initial_equity,
            config=self._config.config
        )
        # Imposta la lista dei simboli come attributo di istanza
        self.symbols = list(self._config.config['symbols'].keys())
        logger.info(
            "\n==================== [SISTEMA INIZIALIZZATO] ====================\n"
            f"Simboli configurati: {self.symbols}\n"
            f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}\n"
            "======================================================\n"
        )
        logger.info("Sistema inizializzato correttamente")
        logger.info(f"Simboli configurati: {self.symbols}")
        logger.info(f"Parametri buffer: size={self.engine.buffer_size}, min_samples={self.engine.min_spin_samples}")

    def _reset_trade_count_if_new_day(self):
        """Resetta il trade_count se è iniziato un nuovo giorno e logga lo stato precedente. Salva su file."""
        today = datetime.now().date()
        if getattr(self, '_last_trade_count_reset', None) != today:
            old_counts = dict(self.trade_count)
            logger.info(f"🔄 [TRADE_COUNT RESET] Nuovo giorno {today}. Stato precedente: {old_counts}")
            self.trade_count = defaultdict(int)
            self._last_trade_count_reset = today
            self._save_trade_count_state()
    def _safe_sleep(self, seconds):
        """Sleep sicuro che ignora eventuali eccezioni"""
        try:
            time.sleep(seconds)
        except Exception:
            pass
    
    def _activate_symbols(self):
        """Attiva automaticamente i simboli richiesti in MT5"""
        try:
            symbols_to_activate = list(self._config.config['symbols'].keys())
            logger.info(f"Attivazione simboli in MT5: {symbols_to_activate}")
            for symbol in symbols_to_activate:
                # Verifica se il simbolo esiste
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    logger.warning(f"Simbolo {symbol} non trovato nel broker")
                    continue
                # Attiva il simbolo se non è già attivo
                if not symbol_info.visible:
                    if mt5.symbol_select(symbol, True):
                        logger.info(f"Simbolo {symbol} attivato con successo")
                    else:
                        logger.error(f"Impossibile attivare il simbolo {symbol}")
                else:
                    logger.info(f"Simbolo {symbol} già attivo")
        except Exception as e:
            logger.error(f"Errore durante l'attivazione dei simboli: {str(e)}")
   
   
    def _setup_logger(self, config_path: str):
        """Configura il sistema di logging"""
        global logger
        logger = setup_logger(config_path)
        clean_old_logs()
        
        
    def _load_configuration(self, config_path: str):
        """Carica il file di configurazione"""
        try:
            logger.info(f"Caricamento configurazione da {config_path}")
            # Carica la configurazione usando ConfigManager
            self._config = load_config(config_path)
            # Verifica di base
            if not hasattr(self._config, 'config'):
                raise ValueError("Struttura config non valida")
            if 'symbols' not in self._config.config:
                raise ValueError("Sezione 'symbols' mancante nel file di configurazione")
            logger.info(f"Configurazione caricata con {len(self._config.config['symbols'])} simboli")
        except Exception as e:
            logger.error(f"Errore caricamento configurazione: {str(e)}")
            raise
            
            

    def _initialize_mt5(self) -> bool:
        """Connessione a MetaTrader 5 con configurazione specifica challenge"""
        try:
            # Chiudi eventuali connessioni precedenti
            mt5.shutdown()
            
            # Ottieni configurazione MT5 specifica
            mt5_config = self._config.config.get('metatrader5', {})
            
            # Inizializza con parametri specifici challenge
            if not mt5.initialize(
                path=mt5_config.get('path', 'C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe'),
                login=int(mt5_config.get('login', 0)),
                password=mt5_config.get('password', ''),
                server=mt5_config.get('server', 'FivePercentOnline-Real'),
                timeout=60000,
                port=int(mt5_config.get('port', 18889))
            ):
                logger.error(f"Inizializzazione MT5 challenge fallita: {mt5.last_error()}")
                return False
            
            terminal_info = mt5.terminal_info()
            if not terminal_info:
                logger.error("Impossibile ottenere info terminal MT5")
                return False
                
            logger.info(f"MT5 challenge inizializzato: {terminal_info.company} - {terminal_info.name}")
            logger.info(f"Server: {mt5_config.get('server')} | Porta: {mt5_config.get('port')} | Login: {mt5_config.get('login')}")
            return True
            
        except Exception as e:
            logger.error(f"Errore inizializzazione MT5 challenge: {str(e)}")
            return False

    """
    2. Gestione Connessione e Ambiente
    """

    def _verify_connection(self) -> bool:
        """Verifica/connessione MT5 - Verifica la connessione MT5 con ripristino automatico"""
        try:
            if not mt5.terminal_info() or not mt5.terminal_info().connected:
                logger.warning("Connessione MT5 challenge persa, tentativo di riconnessione...")
                mt5.shutdown()
                self._safe_sleep(2)
                
                # Usa la stessa logica di _initialize_mt5 per riconnessione
                mt5_config = self._config.config.get('metatrader5', {})
                return mt5.initialize(
                    path=mt5_config.get('path', 'C:/MT5/FivePercentOnlineMetaTrader5/terminal64.exe'),
                    login=int(mt5_config.get('login', 0)),
                    password=mt5_config.get('password', ''),
                    server=mt5_config.get('server', 'FivePercentOnline-Real'),
                    timeout=60000,
                    port=int(mt5_config.get('port', 18889))
                )
            return True
        except Exception as e:
            logger.error(f"Errore verifica connessione challenge: {str(e)}")
            return False

    """
    3. Core del Trading System            
    """        
        
    def start(self):
        """Avvia il sistema"""
        print("🚀 ==> AVVIO QUANTUM TRADING SYSTEM <== 🚀")
        try:
            # Controllo robusto presenza simboli su self._config
            symbols = None
            if hasattr(self, '_config'):
                # Caso attributo symbols
                if hasattr(self._config, 'symbols') and self._config.symbols:
                    symbols = self._config.symbols
                # Caso _config.config['symbols']
                elif hasattr(self._config, 'config') and isinstance(self._config.config, dict) and 'symbols' in self._config.config:
                    symbols = self._config.config['symbols']
                # Caso dict puro
                elif isinstance(self._config, dict) and 'symbols' in self._config:
                    symbols = self._config['symbols']
            if not symbols or not isinstance(symbols, (dict, list)) or len(symbols) == 0:
                raise RuntimeError("Configurazione non valida - simboli mancanti")

            print(f"📋 Sistema con {len(symbols)} simboli configurati: {symbols}")
            logger.info(f"Sistema con {len(symbols)} simboli configurati")
            logger.info(f"Simboli configurati: {symbols}")
            logger.info(f"Avvio sistema con {len(symbols)} simboli")

            if not hasattr(self, 'engine') or not hasattr(self, 'risk_manager'):
                raise RuntimeError("Componenti critici non inizializzati")

            print("✅ Componenti critici inizializzati correttamente")
            self.running = True
            logger.info("Sistema di trading avviato correttamente")

            print("🔄 Inizio loop principale...")

            while self.running:
                try:
                    self._main_loop()
                    self._safe_sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("Arresto richiesto dall'utente")
                    self.running = False
                except Exception as e:
                    logger.error(f"Errore durante l'esecuzione: {str(e)}", exc_info=True)
                    print(f"❌ Errore nel loop: {e}")
                    self._safe_sleep(5)

        except Exception as e:
            logger.critical(f"Errore fatale: {str(e)}", exc_info=True)
            print(f"💀 Errore fatale: {e}")
            import traceback
            traceback.print_exc()
        # finally:  # RIMOSSO: non serve più chiamare self.stop() qui
        #     self.stop()

    def stop(self):
        """Ferma il sistema e fa cleanup"""
        self.running = False
        logger.info("Sistema di trading fermato. Cleanup completato.")

    def _process_symbols(self):
        """Processa tutti i simboli configurati"""
        current_positions = len(mt5.positions_get() or [])
        
        for symbol in self._config.config['symbols']:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    continue

                if not self._validate_tick(tick):
                    continue

                if hasattr(self, 'engine') and hasattr(self.engine, 'process_tick'):
                    price = (tick.bid + tick.ask) / 2 if tick.bid and tick.ask else tick.bid
                    self.engine.process_tick(symbol, price)

                self._process_single_symbol(symbol, tick, current_positions)

            except Exception as e:
                logger.error(f"Errore processamento {symbol}: {str(e)}", exc_info=True)
           
    def _process_single_symbol(self, symbol: str, tick, current_positions: int):
        """Processa un singolo simbolo per segnali di trading"""
        try:
            # --- DEBUG avanzato: raccolta motivi blocco trade ---
            motivi_blocco = []
            # 1. Verifica se possiamo fare trading
            if not self.engine.can_trade(symbol):
                # Diagnostica dettagliata sul tipo di cooldown
                position_cooldown = self.engine.config.get('risk_parameters', {}).get('position_cooldown', 1800)
                last_close = self.engine.get_position_cooldown(symbol)
                signal_cooldown = self.engine.config.get('quantum_params', {}).get('signal_cooldown', 900)
                last_signal = self.engine.get_last_signal_time(symbol)
                now = time.time()
                msg = None
                if now - last_close < position_cooldown:
                    remaining = int(position_cooldown - (now - last_close))
                    msg = f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: position cooldown attivo ({remaining}s rimanenti)"
                elif now - last_signal < signal_cooldown:
                    remaining = int(signal_cooldown - (now - last_signal))
                    msg = f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: signal cooldown attivo ({remaining}s rimanenti)"
                else:
                    msg = f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: can_trade=False (motivo generico)"
                motivi_blocco.append('can_trade=False')
                self.debug_trade_decision(symbol)
                logger.info(msg)
                return

            # 1.1. Controllo limite trade giornalieri (opzionale: globale o per simbolo)
            # Reset trade_count se nuovo giorno
            self._reset_trade_count_if_new_day()
            risk_params = self._config.config['risk_parameters']
            daily_limit = risk_params.get('max_daily_trades', 5)
            limit_mode = risk_params.get('daily_trade_limit_mode', 'global')
            if limit_mode == 'global':
                total_trades_today = sum(self.trade_count.values())
                if total_trades_today >= daily_limit:
                    motivi_blocco.append('max_daily_trades_global')
                    logger.info(f"🚫 Limite totale trade giornalieri raggiunto: {total_trades_today}/{daily_limit}. Nessun nuovo trade verrà aperto oggi.")
                    self.debug_trade_decision(symbol)
                    logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: max_daily_trades_global")
                    return
            else:  # per_symbol
                trades_for_symbol = self.trade_count.get(symbol, 0)
                if trades_for_symbol >= daily_limit:
                    motivi_blocco.append('max_daily_trades_per_symbol')
                    logger.info(f"🚫 Limite trade giornalieri per {symbol} raggiunto: {trades_for_symbol}/{daily_limit}. Nessun nuovo trade su questo simbolo oggi.")
                    self.debug_trade_decision(symbol)
                    logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: max_daily_trades_per_symbol")
                    return

            # 2. Verifica orari di trading
            if not self.is_trading_hours(symbol):
                motivi_blocco.append('fuori_orario')
                self.debug_trade_decision(symbol)
                logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: fuori_orario")
                return

            # 3. Verifica posizioni esistenti
            existing_positions = mt5.positions_get(symbol=symbol)
            if existing_positions and len(existing_positions) > 0:
                motivi_blocco.append('posizioni_aperte_su_symbol')
                self.debug_trade_decision(symbol)
                logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: posizioni_aperte_su_symbol")
                return

            # 4. Verifica limite posizioni totali
            if current_positions >= self.max_positions:
                motivi_blocco.append('max_positions_totali')
                self.debug_trade_decision(symbol)
                logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: max_positions_totali")
                return

            # 5. Ottieni segnale (senza attivare cooldown)
            signal, price = self.engine.get_signal(symbol, for_trading=False)

            logger.debug(f"🔍 Segnale per {symbol}: {signal} (Price: {price})")

            if signal in ["BUY", "SELL"]:
                logger.info(f"🎯 SEGNALE ATTIVO {signal} per {symbol} - Controllo condizioni trading")

                # 5.1 Verifica cooldown segnale PRIMA di procedere
                if hasattr(self.engine, 'last_signal_time') and symbol in self.engine.last_signal_time:
                    time_since_last = time.time() - self.engine.last_signal_time[symbol]
                    if time_since_last < self.engine.signal_cooldown:
                        motivi_blocco.append('cooldown_attivo')
                        logger.info(f"⏰ {symbol}: In cooldown, salto trade (tempo rimanente: {self.engine.signal_cooldown - time_since_last:.1f}s)")
                        self.debug_trade_decision(symbol)
                        logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: cooldown_attivo")
                        return

                # 5.2 Se tutto ok, ottieni segnale per trading (questo attiva il cooldown)
                trading_signal, trading_price = self.engine.get_signal(symbol, for_trading=True)

                if trading_signal in ["BUY", "SELL"]:
                    logger.info(f"✅ Segnale confermato per trading: {trading_signal}")

                    # 6. Calcola dimensione posizione
                    dynamic_risk = self.get_dynamic_risk_percent()
                    size = self.risk_manager.calculate_position_size(symbol, trading_price, trading_signal, risk_percent=dynamic_risk)

                    logger.info(f"💰 Size calcolata per {symbol}: {size} lots")

                    if size > 0:
                        logger.info(f"✅ Esecuzione trade autorizzata per {symbol} - Size: {size}")
                        # 7. Esegui il trade
                        success = self._execute_trade(symbol, trading_signal, tick, trading_price, size)
                        if not success:
                            motivi_blocco.append('errore_esecuzione_trade')
                            self.debug_trade_decision(symbol)
                            logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: errore_esecuzione_trade")
                        else:
                            logger.info(f"🎉 Trade {symbol} eseguito con successo!")
                    else:
                        motivi_blocco.append('size_zero')
                        logger.warning(f"⚠️ Trade {symbol} bloccato: size = 0")
                        self.debug_trade_decision(symbol)
                        logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: size_zero")
                else:
                    motivi_blocco.append('segnale_non_confermato')
                    logger.warning(f"🚫 {symbol}: Segnale non confermato per trading effettivo")
                    self.debug_trade_decision(symbol)
                    logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: segnale_non_confermato")
            else:
                motivi_blocco.append(f'segnale_non_operativo_{signal}')
                logger.debug(f"💤 {symbol}: HOLD - nessuna azione")
                self.debug_trade_decision(symbol)
                logger.info(f"[DEBUG-TRADE-DECISION] {symbol} | Blocco: segnale_non_operativo_{signal}")

        except Exception as e:
            logger.error(f"Errore processo simbolo {symbol}: {str(e)}", exc_info=True)

    def _execute_trade(self, symbol: str, signal: str, tick, price: float, size: float) -> bool:
        """Esegue un trade con gestione completa degli errori"""
        try:
            logger.info(f"🚀 INIZIO ESECUZIONE TRADE: {signal} {symbol} | Size: {size} | Price: {price}")
            
            # 1. Nota: can_trade() già verificato in _process_single_symbol()
            # Rimuoviamo il controllo ridondante che causa il blocco
            
            # 2. Determina tipo ordine
            order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
            
            # 3. Calcola livelli SL/TP
            sl_price, tp_price = self.risk_manager.calculate_dynamic_levels(
                symbol, order_type, price
            )
            
            # 4. Prepara richiesta ordine
            symbol_info = mt5.symbol_info(symbol)
            execution_price = symbol_info.ask if signal == "BUY" else symbol_info.bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": size,
                "type": order_type,
                "price": execution_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 10,
                "magic": self._config['magic_number'] if isinstance(self._config, dict) else self._config.config['magic_number'],
                "comment": "QTS-AUTO",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,  # Prova FOK prima, poi IOC se fallisce
            }
            
            # 5. Esegui ordine con fallback per filling mode
            logger.info(f"Esecuzione {signal} {symbol}: {size} lots @ {execution_price}")
            logger.info(f"[ORDER_REQUEST_DEBUG] Request inviato a MT5: {request}")
            result = mt5.order_send(request)
            
            # Se fallisce per filling mode, prova con metodo alternativo
            if result.retcode == 10030:  # Unsupported filling mode
                logger.warning(f"Filling mode FOK non supportato per {symbol}, provo con IOC")
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                logger.info(f"[ORDER_REQUEST_DEBUG] Request IOC: {request}")
                result = mt5.order_send(request)
                
                if result.retcode == 10030:  # Ancora problemi
                    logger.warning(f"Filling mode IOC non supportato per {symbol}, provo Return")
                    request["type_filling"] = mt5.ORDER_FILLING_RETURN
                    logger.info(f"[ORDER_REQUEST_DEBUG] Request RETURN: {request}")
                    result = mt5.order_send(request)
            
            # 6. Verifica risultato
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Trade fallito {symbol}: {result.retcode} - {result.comment}")
                return False
                
            logger.info(f"Trade eseguito {symbol} {size} lots a {execution_price} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")
            logger.info(f"Ticket: {result.order} | Deal: {result.deal}")

            # Aggiorna il cooldown segnale SOLO dopo trade effettivo
            try:
                self.engine.set_last_signal_time(symbol, time.time())
            except Exception as e:
                logger.error(f"Errore aggiornamento cooldown segnale per {symbol}: {str(e)}")

            # 7. Aggiornamento metriche con timeout
            try:
                with self.metrics_lock:
                    self.trade_count[symbol] += 1
                    self._save_trade_count_state()
                    self.engine.record_trade_close(symbol)
                logger.info(f"Metriche aggiornate per {symbol}")
            except Exception as e:
                logger.error(f"Errore aggiornamento metriche per {symbol}: {str(e)}")

            # 8. Pausa di sicurezza post-trade
            self._safe_sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Errore esecuzione trade {symbol}: {str(e)}", exc_info=True)
            return False

    """
    4. Gestione Ordini e Posizioni
    """

    def _close_position(self, position):
        if self._check_position_closed(position.ticket):
            return True
            
        # Aggiungere controllo durata minima
        min_duration = 300  # 5 minuti
        
        # Converti position.time in datetime se necessario
        if isinstance(position.time, (int, float)):
            position_time = datetime.fromtimestamp(position.time)
        else:
            position_time = position.time
        
        if (datetime.now() - position_time) < timedelta(seconds=min_duration):
            logger.warning(f"Posizione {position.ticket} chiusa troppo presto")
            return False
        
        """Versione migliorata con verifica dello stato"""
        if self._check_position_closed(position.ticket):
            logger.debug(f"Posizione {position.ticket} già chiusa")
            return True
            
        if not position or not hasattr(position, 'ticket'):
            logger.error("Posizione non valida per la chiusura")
            return False
            
        existing_positions = mt5.positions_get(ticket=position.ticket)
        if not existing_positions or len(existing_positions) == 0:
            logger.info(f"Posizione {position.ticket} già chiusa o non esistente")
            return True
            
        try:
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                logger.error(f"Impossibile ottenere info simbolo {position.symbol}")
                return False
                
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": symbol_info.ask if position.type == mt5.ORDER_TYPE_BUY else symbol_info.bid,
                "deviation": 10,
                "magic": self.config.config['magic_number'],
                "comment": "QTS-CLOSE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            if not self._validate_close_request(close_request, position):
                return False
                
            result = mt5.order_send(close_request)
                
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                profit = (position.price_current - position.price_open) * position.volume
                self._update_trade_metrics(
                    success=True, 
                    symbol=position.symbol, 
                    profit=profit
                )
                return True
                
            logger.info(f"Posizione {position.ticket} chiusa con successo a {close_request['price']}")
            return True
            
        except Exception as e:
            logger.error(f"Eccezione durante chiusura posizione {position.ticket if hasattr(position, 'ticket') else 'N/A'}: {str(e)}", exc_info=True)
            return False

    """
    5. Monitoraggio Posizioni
    """
    
    def _monitor_open_positions(self):
        """Monitoraggio avanzato delle posizioni aperte"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
                
            for position in positions:
                try:
                    # Verifica che la posizione esista ancora
                    current_pos = mt5.positions_get(ticket=position.ticket)
                    if not current_pos or len(current_pos) == 0:
                        continue
                        
                    tick = mt5.symbol_info_tick(position.symbol)
                    if not tick:
                        logger.debug(f"Nessun tick per {position.symbol}")
                        continue
                    
                    current_price = tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask
                    
                    # Gestione trailing stop
                    self._manage_trailing_stop(position, current_price)
                    
                    # Gestione timeout
                    self._check_position_timeout(position)
                    
                except Exception as e:
                    logger.error(f"Errore monitoraggio posizione {position.ticket}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Errore critico in _monitor_open_positions: {str(e)}")

    def _check_position_closed(self, ticket: int) -> bool:
        """Verifica se una posizione è stata chiusa"""
        try:
            positions = mt5.positions_get(ticket=ticket)
            return positions is None or len(positions) == 0
        except Exception as e:
            logger.error(f"Errore verifica posizione {ticket}: {str(e)}")
            return False

    def _manage_trailing_stop(self, position, current_price: float) -> bool:
        """Gestione avanzata del trailing stop con gestione errori migliorata"""
        try:
            # Verifica se trailing stop è abilitato
            risk_config = self.risk_manager.get_risk_config(position.symbol)
            trailing_config = risk_config.get('trailing_stop', {})
            
            if not trailing_config.get('enable', False):
                return False
                
            # Calcola profit corrente in pips
            pip_size = self.engine._get_pip_size(position.symbol)
            if position.type == mt5.ORDER_TYPE_BUY:
                profit_pips = (current_price - position.price_open) / pip_size
            else:
                profit_pips = (position.price_open - current_price) / pip_size
                
            # Verifica soglia di attivazione
            activation_pips = trailing_config.get('activation_pips', 150)
            if profit_pips < activation_pips:
                return False
                
            # Calcola nuovo SL
            trailing_distance = trailing_config.get('distance_pips', 100)
            
            if position.type == mt5.ORDER_TYPE_BUY:
                new_sl = current_price - (trailing_distance * pip_size)
                # Solo se migliore del SL attuale
                if position.sl == 0 or new_sl > position.sl:
                    return self._modify_position(position, sl=new_sl)
            else:
                new_sl = current_price + (trailing_distance * pip_size)
                # Solo se migliore del SL attuale
                if position.sl == 0 or new_sl < position.sl:
                    return self._modify_position(position, sl=new_sl)
                    
            return False
            
        except Exception as e:
            logger.error(f"Errore trailing stop posizione {position.ticket}: {str(e)}")
            return False

    def _check_position_timeout(self, position):
        """Controlla timeout posizione con gestione robusta dei timestamp"""
        try:
            # Ottieni configurazione timeout
            risk_config = self.risk_manager.get_risk_config(position.symbol)
            max_hours = risk_config.get('position_timeout_hours', 24)
            
            # Gestione robusta dei timestamp
            if hasattr(position, 'time_setup'):
                timestamp = position.time_setup
            elif hasattr(position, 'time'):
                timestamp = position.time
            else:
                logger.error(f"Posizione {position.ticket} senza timestamp valido")
                return
                
            # Converti timestamp in datetime
            if isinstance(timestamp, (int, float)):
                if timestamp > 1e10:  # Assume milliseconds
                    position_dt = datetime.fromtimestamp(timestamp / 1000)
                else:  # Assume seconds
                    position_dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, datetime):
                position_dt = timestamp
            else:
                logger.error(f"Formato tempo non supportato per posizione {position.ticket}: {type(position.time)}")
                return

            # Calcolo della durata CORRETTO
            current_dt = datetime.now()
            duration = current_dt - position_dt
            duration_hours = duration.total_seconds() / 3600

            # DEBUG: Log dei tempi calcolati
            logger.debug(f"Position {position.ticket} opened at: {position_dt}, current: {current_dt}, duration: {duration_hours:.2f}h")

            if duration_hours > max_hours:
                logger.info(f"Chiusura posizione {position.ticket} per timeout ({duration_hours:.1f}h > {max_hours}h)")
                self._close_position(position)
                
        except Exception as e:
            logger.error(f"Errore controllo timeout posizione {position.ticket}: {str(e)}", exc_info=True)

    def _modify_position(self, position, sl=None, tp=None) -> bool:
        """Modifica SL/TP di una posizione esistente con controlli avanzati"""
        try:
            # Verifica che la posizione esista ancora
            current_pos = mt5.positions_get(ticket=position.ticket)
            if not current_pos or len(current_pos) == 0:
                logger.debug(f"Posizione {position.ticket} non più esistente")
                return False
                
            # Prepara richiesta di modifica
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": sl if sl is not None else position.sl,
                "tp": tp if tp is not None else position.tp,
            }
            
            # Validazione livelli
            symbol_info = mt5.symbol_info(position.symbol)
            if not symbol_info:
                return False
                
            # Arrotonda ai decimali corretti
            if request["sl"] != 0:
                request["sl"] = round(request["sl"], symbol_info.digits)
            if request["tp"] != 0:
                request["tp"] = round(request["tp"], symbol_info.digits)
                
            # Esegui modifica
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Posizione {position.ticket} modificata: SL={request['sl']}, TP={request['tp']}")
                return True
            else:
                logger.warning(f"Modifica posizione {position.ticket} fallita: {result.retcode}")
                return False
                
        except Exception as e:
            logger.error(f"Errore modifica posizione {position.ticket}: {str(e)}")
            return False

    def _validate_positions(self):
        """Verifica posizioni duplicate"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
                
            symbol_positions = defaultdict(list)
            for pos in positions:
                symbol_positions[pos.symbol].append(pos)
                
            for symbol, pos_list in symbol_positions.items():
                if len(pos_list) > 1:
                    logger.warning(f"Posizioni duplicate per {symbol}: {[p.ticket for p in pos_list]}")
                    
        except Exception as e:
            logger.error(f"Errore validazione posizioni: {str(e)}")

    """
    6. Risk Management
    """

    def _update_account_info(self):
        """Aggiorna info account"""
        try:
            self.account_info = mt5.account_info()
            if self.account_info and hasattr(self, 'drawdown_tracker'):
                self.drawdown_tracker.update(
                    self.account_info.equity,
                    self.account_info.balance
                )
        except Exception as e:
            logger.error(f"Errore aggiornamento account: {str(e)}")
                    
    def _check_drawdown_limits(self):
        """Controlla limiti drawdown"""
        if not hasattr(self, 'drawdown_tracker') or not self.account_info:
            return
        
        soft_hit, hard_hit = self.drawdown_tracker.check_limits(self.account_info.equity)
        
        if hard_hit:
            logger.critical("Hard drawdown limit raggiunto!")
            raise RuntimeError("Hard drawdown limit raggiunto")
        
        if soft_hit and not self.drawdown_tracker.protection_active:
            logger.warning("Soft drawdown limit - riduzione esposizione")
            self.drawdown_tracker.protection_active = True
            self.max_positions = max(1, self.max_positions // 2)
            logger.info(f"Max posizioni ridotto a {self.max_positions}")

    """
    7. Metriche e Reporting
    """

    def _update_trade_metrics(self, success: bool, symbol: str, profit: float = 0.0) -> None:
        """Aggiorna metriche con controllo del limite giornaliero"""
        try:
            with self.metrics_lock:
                self.trade_metrics['total_trades'] += 1
                
                if success:
                    self.trade_metrics['successful_trades'] += 1
                else:
                    self.trade_metrics['failed_trades'] += 1
                    
                self.trade_metrics['total_profit'] += profit
                
                # Aggiorna statistiche per simbolo
                if symbol not in self.trade_metrics['symbol_stats']:
                    self.trade_metrics['symbol_stats'][symbol] = {
                        'trades': 0,
                        'profit': 0.0,
                        'wins': 0,
                        'losses': 0
                    }
                    
                stats = self.trade_metrics['symbol_stats'][symbol]
                stats['trades'] += 1
                stats['profit'] += profit
                
                if profit > 0:
                    stats['wins'] += 1
                else:
                    stats['losses'] += 1
                    
                logger.info(f"Metriche aggiornate: {symbol} P/L={profit:.2f}")
                
        except Exception as e:
            logger.error(f"Errore aggiornamento metriche: {str(e)}")

    """
    8. Validazioni
    """
    
    def _validate_tick(self, tick) -> bool:
        """Aggiungi controllo per evitare bias di direzione"""
        if not tick:
            return False
            
        # Verifica che il prezzo sia valido
        if tick.bid <= 0 or tick.ask <= 0:
            return False
            
        # Verifica spread ragionevole
        spread = tick.ask - tick.bid
        if spread <= 0 or spread > tick.bid * 0.1:  # Max 10% spread
            return False
            
        return True

    def _validate_symbol(self, symbol: str) -> bool:
        """Validazione avanzata per strategia tick-based"""
        # 1. Verifica base simbolo
        if not symbol or len(symbol) < 3:
            return False
            
        # 2. Verifica MT5 info
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.debug(f"Simbolo {symbol} non disponibile in MT5")
            return False
            
        # 3. Verifica tick corrente
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.info(f"Nessun tick disponibile per {symbol}")
            return False
        
        if tick.time_msc < (time.time() - 60)*1000:  # Se il tick è più vecchio di 60s
            logger.debug(f"Dati tick obsoleti per {symbol} ({(time.time()*1000 - tick.time_msc)/1000:.1f}s)")
            return False

        # 4. Controllo spread e liquidità
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return False
            
        spread = (symbol_info.ask - symbol_info.bid) / self.engine._get_pip_size(symbol)
        max_spread = self._config._get_max_allowed_spread(symbol)
        
        if spread > max_spread * 1.2:  # Tolleranza +20%
            logger.debug(f"Spread {spread:.1f}p troppo alto per {symbol} (max {max_spread:.1f}p)")
            return False

        # 6. Verifica buffer dati sufficiente
        if len(self.engine.tick_buffer.get(symbol, [])) < self.engine.min_spin_samples:
            if is_trading_hours(symbol, self._config.config):
                logger.debug(f"Dati insufficienti nel buffer per {symbol}")
                return False
            # Se il mercato è chiuso, non bloccare per buffer insufficiente

        return True

    """
    6. Utility e Helper Methods
    """

    def debug_trade_status(self, symbol: str):
        """Debug dello stato di trading per un simbolo specifico"""
        try:
            # Verifica can_trade
            can_trade = self.engine.can_trade(symbol)
            # Verifica orari (usa config_dict per compatibilità)
            config_dict = None
            if hasattr(self, 'config_manager') and self.config_manager is not None:
                if hasattr(self.config_manager, 'config_dict'):
                    config_dict = self.config_manager.config_dict
                elif hasattr(self.config_manager, 'config'):
                    config = self.config_manager.config
                    config_dict = config.config if hasattr(config, 'config') else config
            else:
                config_dict = self._config.config if hasattr(self._config, 'config') else self._config
            trading_hours = is_trading_hours(symbol, config_dict)
            # Verifica posizioni esistenti
            positions = mt5.positions_get(symbol=symbol)
            has_position = positions and len(positions) > 0
            # Verifica limite trades giornalieri
            daily_count = self.trade_count.get(symbol, 0)
            daily_limit = 0
            try:
                daily_limit = config_dict.get('risk_parameters', {}).get('max_daily_trades', 0)
            except Exception:
                daily_limit = 0
            # Verifica buffer (usa getter thread-safe)
            buffer_size = len(self.engine.get_tick_buffer(symbol)) if hasattr(self.engine, 'get_tick_buffer') else 0
            min_samples = getattr(self.engine, 'min_spin_samples', 0)
            # Log informativo sullo stato trading
            logger.info(f"🔍 TRADE STATUS {symbol}: can_trade={can_trade}, trading_hours={trading_hours}, "
                        f"has_position={has_position}, daily_trades={daily_count}/{daily_limit}, "
                        f"buffer={buffer_size}/{min_samples}")
        except Exception as e:
            logger.error(f"Errore debug_trade_status per {symbol}: {str(e)}")
    
    def check_challenge_limits(self):
        """Controlla i limiti imposti dal broker challenge"""
        account_info = mt5.account_info()
        if not account_info:
            logger.error("Impossibile ottenere info account MT5")
            return False

        # Calcola equity, balance, drawdown, profit
        equity = account_info.equity
        balance = account_info.balance
        initial_balance = self._config.config.get('initial_balance', balance)
        max_daily_loss = initial_balance * self._config.config.get('challenge_specific', {}).get('max_daily_loss_percent', 0) / 100
        max_total_loss = initial_balance * self._config.config.get('challenge_specific', {}).get('max_total_loss_percent', 0) / 100
        profit_target = initial_balance * self._config.config.get('challenge_specific', {}).get('step1_target', 0) / 100

        # Daily loss check
        today = datetime.now().date()
        daily_loss = self.get_daily_loss(today)
        if daily_loss < -max_daily_loss:
            logger.warning(f"Limite di perdita giornaliera superato: {daily_loss} < {-max_daily_loss}")
            return False

        # Total loss check
        total_loss = balance - initial_balance
        if total_loss < -max_total_loss:
            logger.warning(f"Limite di perdita totale superato: {total_loss} < {-max_total_loss}")
            return False

        # Profit target check
        if total_loss >= profit_target:
            logger.info(f"Profit target raggiunto: {total_loss} >= {profit_target}")
            return False

        return True

    def get_daily_loss(self, day):
        """Calcola la perdita giornaliera sommando i profitti dei deals chiusi nella data specificata."""
       
        try:
            # Inizio e fine giornata
            date_from = datetime.combine(day, datetime.min.time())
            date_to = datetime.combine(day, datetime.max.time())
            deals = mt5.history_deals_get(date_from, date_to)
            if not deals:
                logger.info(f"Nessun deal trovato per la data {day}")
                return 0.0
            daily_loss = sum(d.profit for d in deals)
            logger.debug(f"Perdita/profitto totale del {day}: {daily_loss}")
            return daily_loss
        except Exception as e:
            logger.error(f"Errore nel calcolo della perdita giornaliera per {day}: {str(e)}")
            return 0.0

    def close_positions_before_weekend(self):
        """Chiude tutte le posizioni aperte il venerdì sera prima della chiusura dei mercati"""
        now = datetime.now()
        # Venerdì = 4 (lunedì=0), chiusura alle 21:00
        if now.weekday() == 4 and now.hour >= 21:
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    try:
                        self._close_position(pos)
                        logger.info(f"Chiusura automatica posizione {pos.ticket} su {pos.symbol} per fine settimana.")
                    except Exception as e:
                        logger.error(f"Errore chiusura automatica {pos.ticket}: {str(e)}")

    def check_buffers(self):
        """Controlla lo stato dei buffer di ogni simbolo"""
        for symbol in self._config.config['symbols']:
            buffer = self.engine.get_tick_buffer(symbol)
            logger.debug(f"Buffer {symbol}: {len(buffer)} ticks")

    # ================== GESTIONE LIMITI TRADE COUNT E POSIZIONI ==================
    def can_open_trade(self, symbol=None):
        """
        Verifica se è possibile aprire un nuovo trade (limiti giornalieri e posizioni).
        Args:
            symbol: opzionale, se None controlla limiti globali, altrimenti per simbolo.
        Returns:
            (bool, motivo): True se si può aprire, False e motivo se bloccato.
        """
        risk_params = self._config.config.get('risk_parameters', {})
        max_daily_trades = risk_params.get('max_daily_trades', 8)
        max_positions = risk_params.get('max_positions', 1)
        daily_trade_limit_mode = risk_params.get('daily_trade_limit_mode', 'global')
        # Carica trade_count
        trade_count = self.get_trade_count(symbol)
        # Posizioni aperte
        all_positions = mt5.positions_get()
        total_open_positions = len(all_positions) if all_positions else 0
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
            symbol_positions = len(positions) if positions else 0
        else:
            symbol_positions = None
        # Logica limiti
        if daily_trade_limit_mode == 'symbol' and symbol:
            if trade_count >= max_daily_trades:
                return False, f"max_daily_trades_symbol ({trade_count}/{max_daily_trades})"
            elif symbol_positions is not None and symbol_positions >= max_positions:
                return False, f"max_positions_per_symbol ({symbol_positions}/{max_positions})"
        else:
            total_trades = sum(self.get_trade_count().values())
            if total_trades >= max_daily_trades:
                return False, f"max_daily_trades_global ({total_trades}/{max_daily_trades})"
            elif total_open_positions >= max_positions:
                return False, f"max_total_positions ({total_open_positions}/{max_positions})"
        return True, None

    def get_trade_count(self, symbol=None):
        """
        Restituisce il trade count per simbolo o globale.
        Args:
            symbol: opzionale, se None restituisce dict completo, altrimenti solo per simbolo.
        Returns:
            int o dict
        """
        # Carica da file se necessario
        try:
            if os.path.isfile(self._trade_count_file):
                with open(self._trade_count_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if symbol:
                    return data.get('trade_count', {}).get(symbol, 0)
                else:
                    return data.get('trade_count', {})
            else:
                return 0 if symbol else {}
        except Exception:
            return 0 if symbol else {}

    def reset_trade_count_if_new_day(self):
        """
        Reset giornaliero del trade_count con backup.
        """
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            if os.path.isfile(self._trade_count_file):
                with open(self._trade_count_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                file_date = data.get('date', '')
                if file_date != today:
                    # Backup
                    import shutil
                    backup_path = self._trade_count_file.replace('.json', f'_{file_date}_backup.json')
                    try:
                        shutil.copy2(self._trade_count_file, backup_path)
                    except Exception as e:
                        self.logger.warning(f"Impossibile creare backup trade_count_state: {e}")
                    # Reset
                    new_data = {'date': today, 'trade_count': {}}
                    with open(self._trade_count_file, 'w', encoding='utf-8') as f2:
                        json.dump(new_data, f2)
                    self.logger.info(f"[TRADE COUNT RESET] Reset giornaliero effettuato, backup creato.")
        except Exception as e:
            self.logger.warning(f"Errore reset trade_count giornaliero: {e}")
