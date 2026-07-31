"""從資料庫產生互動式 HTML 儀表板。"""
import json
from datetime import datetime

import pandas as pd

import db
from config import DASHBOARD_HTML_PATH, MAINTENANCE_THRESHOLDS, DISPLAY_START
from template import HTML


def _col(df, name, nd=None):
    """把欄位轉成 JSON 可用的 list，NaN -> None，並依需要 round。"""
    out = []
    for v in df[name]:
        if pd.isna(v):
            out.append(None)
        elif nd is None:
            out.append(int(v))
        else:
            out.append(round(float(v), nd))
    return out


def _pretty(date_str: str) -> str:
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"


def generate_dashboard():
    conn = db.get_conn()
    # 只展示暖機期之後的資料，初始化偏差不進圖表
    df = pd.read_sql_query(
        "SELECT * FROM daily_metrics WHERE date >= ? ORDER BY date", conn, params=[DISPLAY_START]
    )
    warmup_days = conn.execute(
        "SELECT COUNT(*) FROM daily_metrics WHERE date < ?", (DISPLAY_START,)
    ).fetchone()[0]
    conn.close()

    DASHBOARD_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        DASHBOARD_HTML_PATH.write_text(
            "<h1>尚無資料，請先執行 backfill.py</h1>", encoding="utf-8"
        )
        return

    has_ohlc = df["taiex_open"].notna().all() if "taiex_open" in df else False

    data = {
        "dates": df["date"].tolist(),
        "close": _col(df, "taiex_close", 2),
        "chg": _col(df, "taiex_change_pct", 2),
        "total": _col(df, "total_margin_stocks"),
        "ratio": _col(df, "market_maintenance_ratio", 2),
        "up": _col(df, "up_count"),
        "down": _col(df, "down_count"),
        "ma20": _col(df, "pct_above_ma20", 2),
        "ma60": _col(df, "pct_above_ma60", 2),
        "below": {str(t): _col(df, f"count_below_{t}") for t in MAINTENANCE_THRESHOLDS},
        "hasOHLC": bool(has_ohlc),
    }
    if has_ohlc:
        data["open"] = _col(df, "taiex_open", 2)
        data["high"] = _col(df, "taiex_high", 2)
        data["low"] = _col(df, "taiex_low", 2)

    latest = df.iloc[-1]
    meta = {
        "latestPretty": _pretty(str(latest["date"])),
        "startPretty": _pretty(str(df.iloc[0]["date"])),
        "days": int(len(df)),
        "totalStocks": int(latest["total_margin_stocks"]),
        "warmupDays": int(warmup_days),
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    html = (HTML
            .replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__META__", json.dumps(meta, ensure_ascii=False)))
    DASHBOARD_HTML_PATH.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    generate_dashboard()
