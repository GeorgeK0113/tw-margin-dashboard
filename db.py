import sqlite3
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS daily_metrics (
    date TEXT PRIMARY KEY,
    taiex_close REAL,
    taiex_change_pct REAL,
    total_margin_stocks INTEGER,
    count_below_130 INTEGER,
    count_below_140 INTEGER,
    count_below_150 INTEGER,
    count_below_160 INTEGER,
    pct_below_130 REAL,
    market_maintenance_ratio REAL,
    up_count INTEGER,
    down_count INTEGER,
    pct_above_ma20 REAL,
    pct_above_ma60 REAL
);

CREATE TABLE IF NOT EXISTS stock_daily (
    date TEXT,
    stock_id TEXT,
    name TEXT,
    close REAL,
    margin_balance REAL,
    margin_buy REAL,
    margin_cost REAL,
    maintenance_ratio REAL,
    PRIMARY KEY(date, stock_id)
);
CREATE INDEX IF NOT EXISTS idx_stock_daily_stock ON stock_daily(stock_id, date);
"""


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_latest_date() -> str | None:
    conn = get_conn()
    row = conn.execute("SELECT MAX(date) FROM daily_metrics").fetchone()
    conn.close()
    return row[0] if row and row[0] else None


def get_prev_stock_map(date_str: str) -> dict:
    """回傳指定日期(通常是「前一交易日」)的 {stock_id: (margin_cost, margin_balance)}"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT stock_id, margin_cost, margin_balance FROM stock_daily WHERE date = ?",
        (date_str,),
    ).fetchall()
    conn.close()
    return {r[0]: (r[1], r[2]) for r in rows}


def save_stock_daily(date_str: str, stock_rows: list[dict]):
    conn = get_conn()
    conn.execute("DELETE FROM stock_daily WHERE date = ?", (date_str,))
    conn.executemany(
        """INSERT INTO stock_daily
           (date, stock_id, name, close, margin_balance, margin_buy, margin_cost, maintenance_ratio)
           VALUES (?,?,?,?,?,?,?,?)""",
        [
            (
                date_str, r["stock_id"], r["name"], r["close"],
                r["margin_balance"], r["margin_buy"], r["margin_cost"], r["maintenance_ratio"],
            )
            for r in stock_rows
        ],
    )
    conn.commit()
    conn.close()


def save_metrics(date_str: str, metrics: dict):
    conn = get_conn()
    cols = ["date"] + list(metrics.keys())
    placeholders = ",".join(["?"] * len(cols))
    conn.execute(
        f"INSERT OR REPLACE INTO daily_metrics ({','.join(cols)}) VALUES ({placeholders})",
        [date_str] + list(metrics.values()),
    )
    conn.commit()
    conn.close()
