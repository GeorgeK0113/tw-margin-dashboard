"""單一交易日的完整處理流程：抓資料 -> 計算 -> 寫入資料庫。"""
import logging
from datetime import date

import db
from compute import compute_stock_rows, compute_breadth, compute_day_metrics
from dateutil_tw import ad_to_compact, ad_to_roc
from fetch import fetch_all, NoTradingDataError

logger = logging.getLogger(__name__)


def process_date(d: date) -> bool:
    date_str = ad_to_compact(d)
    date_ad = ad_to_compact(d)
    date_roc = ad_to_roc(d)

    try:
        raw = fetch_all(date_ad, date_roc)
    except NoTradingDataError as e:
        logger.info("skip %s: %s", date_str, e)
        return False
    except Exception as e:  # noqa: BLE001
        logger.warning("skip %s: fetch error %s", date_str, e)
        return False

    conn = db.get_conn()
    try:
        prev_row = conn.execute(
            "SELECT MAX(date) FROM stock_daily WHERE date < ?", (date_str,)
        ).fetchone()
        prev_date = prev_row[0] if prev_row else None
        prev_stock_map = db.get_prev_stock_map(prev_date) if prev_date else {}

        stock_rows = compute_stock_rows(raw["margin"], raw["close"], prev_stock_map)
        if not stock_rows:
            logger.info("skip %s: no stock rows computed", date_str)
            return False

        stock_ids = [r["stock_id"] for r in stock_rows]
    finally:
        conn.close()

    # 先寫入個股資料，讓「站上均線/漲跌家數」的計算能讀到當天的收盤價
    db.save_stock_daily(date_str, stock_rows)

    conn = db.get_conn()
    try:
        breadth = compute_breadth(conn, date_str, stock_ids)
    finally:
        conn.close()
    metrics = compute_day_metrics(stock_rows, breadth, raw["taiex_close"], raw["taiex_change_pct"])
    db.save_metrics(date_str, metrics)
    logger.info("saved %s: %s檔<130%%, TAIEX=%s", date_str, metrics["count_below_130"], metrics["taiex_close"])
    return True
