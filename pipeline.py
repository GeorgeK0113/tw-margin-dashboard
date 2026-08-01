"""單一交易日的完整處理流程：抓資料 -> 計算 -> 寫入資料庫。"""
import logging
import time
from datetime import date

import db
from compute import compute_stock_rows, compute_breadth, compute_day_metrics
from dateutil_tw import ad_to_compact, ad_to_roc, ad_to_slash
from fetch import fetch_all, NoTradingDataError, TemporarilyUnavailableError

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
COOLDOWN_SECONDS = 90


def process_date(d: date) -> bool:
    date_str = ad_to_compact(d)
    date_ad = ad_to_compact(d)
    date_roc = ad_to_roc(d)
    date_slash = ad_to_slash(d)

    try:
        raw = fetch_all(date_ad, date_roc, date_slash)
    except NoTradingDataError as e:
        logger.info("skip %s: %s", date_str, e)
        return False
    # TemporarilyUnavailableError 不在這裡吞掉，交給呼叫端決定重試，
    # 否則暫時性失敗會被誤當成「這天沒有資料」而永久缺漏。

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
    metrics = compute_day_metrics(
        stock_rows, breadth, raw["taiex_close"], raw["taiex_change_pct"],
        raw.get("market_value"), raw.get("margin_money"),
    )
    db.save_metrics(date_str, metrics)
    logger.info("saved %s: %s檔<130%%, TAIEX=%s", date_str, metrics["count_below_130"], metrics["taiex_close"])
    return True


def process_with_retry(d: date) -> bool:
    """暫時性失敗（維護時段、流量限制）會等待後重試，不會被當成沒資料。"""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return process_date(d)
        except TemporarilyUnavailableError as e:
            if attempt == MAX_ATTEMPTS:
                logger.error("%s 重試 %d 次仍失敗：%s", ad_to_compact(d), MAX_ATTEMPTS, e)
                raise
            logger.warning("%s 暫時無法取得（%s），%d 秒後重試 (%d/%d)",
                           ad_to_compact(d), str(e)[:60], COOLDOWN_SECONDS, attempt, MAX_ATTEMPTS)
            time.sleep(COOLDOWN_SECONDS)
    return False
