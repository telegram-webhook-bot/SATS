import sqlite3
from typing import List, Dict, Any, Optional

class SATSDatabase:
    def __init__(self, db_path: str = "sats_trades.db"):
        self.db_path = db_path
        self._conn = None
        self._cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        self._conn = sqlite3.connect(self.db_path)
        self._cursor = self._conn.cursor()

    def _create_tables(self):
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                direction TEXT NOT NULL,
                price REAL NOT NULL,
                sl REAL NOT NULL,
                tp1 REAL NOT NULL,
                tp2 REAL NOT NULL,
                tp3 REAL NOT NULL,
                tp1_r REAL NOT NULL,
                tp2_r REAL NOT NULL,
                tp3_r REAL NOT NULL,
                score REAL NOT NULL,
                tqi REAL NOT NULL,
                er REAL NOT NULL,
                rsi REAL NOT NULL,
                vol_z REAL NOT NULL,
                preset TEXT NOT NULL,
                tp_mode TEXT NOT NULL,
                dyn_scale REAL NOT NULL,
                bar_index INTEGER NOT NULL,
                sent BOOLEAN NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                exit_price REAL NOT NULL,
                pnl REAL,
                is_win BOOLEAN,
                bars_open INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(id)
            )
        """)
        self._conn.commit()

    def record_signal(self, signal_data: Dict[str, Any], sent: bool) -> int:
        columns = ", ".join(signal_data.keys()) + ", sent"
        placeholders = ", ".join([":" + key for key in signal_data.keys()]) + ", :sent"
        query = f"INSERT INTO signals ({columns}) VALUES ({placeholders})"
        self._cursor.execute(query, {**signal_data, "sent": sent})
        self._conn.commit()
        return self._cursor.lastrowid

    def update_symbol_stats(self, symbol: str, interval: str, **kwargs):
        # This is a placeholder. In a real scenario, this would update a separate stats table
        # or aggregate from signals/trade_events. For now, we'll just log it.
        pass

    def update_trade_event(self, signal_id: int, event_type: str, exit_price: float, pnl: Optional[float] = None, is_win: Optional[bool] = None, bars_open: Optional[int] = None):
        self._cursor.execute("""
            INSERT INTO trade_events (signal_id, event_type, exit_price, pnl, is_win, bars_open)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (signal_id, event_type, exit_price, pnl, is_win, bars_open))
        self._conn.commit()

    def get_recent_signals(self, symbol: str, limit: int = 1) -> List[Dict[str, Any]]:
        self._cursor.execute("SELECT * FROM signals WHERE symbol = ? ORDER BY id DESC LIMIT ?", (symbol, limit))
        rows = self._cursor.fetchall()
        columns = [description[0] for description in self._cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
