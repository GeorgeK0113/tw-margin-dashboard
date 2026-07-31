"""歷史資料回補。用法：python backfill.py 2025-01-01 2026-07-30"""
import logging
import sys
from datetime import date, timedelta

import db
from dateutil_tw import daterange
from pipeline import process_date

sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    if len(sys.argv) >= 3:
        start = date.fromisoformat(sys.argv[1])
        end = date.fromisoformat(sys.argv[2])
    else:
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=180)
        print(f"未指定日期區間，預設回補最近半年：{start} ~ {end}")

    import time

    db.init_db()
    done, skipped = 0, 0
    for d in daterange(start, end):
        ok = process_date(d)
        if ok:
            done += 1
        else:
            skipped += 1
        time.sleep(0.5)  # 對免費公開端點客氣一點
    print(f"完成：處理 {done} 個交易日，略過(假日/無資料) {skipped} 天")


if __name__ == "__main__":
    main()
