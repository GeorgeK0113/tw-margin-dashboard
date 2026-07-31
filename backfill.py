"""歷史資料回補。用法：python backfill.py 2022-08-01 2026-07-29

可重複執行：已存在於資料庫的日期會直接跳過，因此中斷或漏抓後再跑一次即可補齊。
"""
import logging
import sys
import time
from datetime import date, timedelta

import db
from dateutil_tw import daterange, ad_to_compact
from fetch import TemporarilyUnavailableError
from pipeline import process_date

sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
COOLDOWN_SECONDS = 90


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


def existing_dates() -> set:
    conn = db.get_conn()
    rows = conn.execute("SELECT date FROM daily_metrics").fetchall()
    conn.close()
    return {r[0] for r in rows}


def main():
    if len(sys.argv) >= 3:
        start = date.fromisoformat(sys.argv[1])
        end = date.fromisoformat(sys.argv[2])
    else:
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=180)
        print(f"未指定日期區間，預設回補最近半年：{start} ~ {end}")

    db.init_db()
    have = existing_dates()
    done = skipped = cached = 0
    for d in daterange(start, end):
        if ad_to_compact(d) in have:
            cached += 1
            continue
        if process_with_retry(d):
            done += 1
        else:
            skipped += 1
        time.sleep(1.0)  # 對免費公開端點客氣一點，也降低被限流的機會

    print(f"完成：新增 {done} 個交易日｜已存在 {cached} 日｜非交易日 {skipped} 天")


if __name__ == "__main__":
    main()
