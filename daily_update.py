"""每日自動更新進入點，供 Windows 工作排程器呼叫。
會自動從資料庫最後一筆日期的隔天補到「今天」，因此就算某天電腦沒開機也能自動補齊。
"""
import logging
import sys
import time
from datetime import date, datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

import db
from dateutil_tw import daterange
from fetch import TemporarilyUnavailableError
from pipeline import process_with_retry
from taiex_ohlc import sync_taiex_ohlc
from dashboard import generate_dashboard
from publish import publish_dashboard

LOG_PATH = None  # 在 config 內設定實際路徑亦可，這裡先用 stdout，交給工作排程器導向檔案

# 留給重試機制的軟性時間預算：任務排程的執行上限是 30 分鐘，
# 若補跑天數多且每天都吃滿重試，要在被系統強制中止前自己停下來。
SOFT_TIME_BUDGET_SECONDS = 20 * 60


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    db.init_db()
    latest = db.get_latest_date()
    if latest:
        start = datetime.strptime(latest, "%Y%m%d").date() + timedelta(days=1)
    else:
        start = date.today() - timedelta(days=180)
    end = date.today()

    if start > end:
        logger.info("資料庫已是最新（%s），無需更新", latest)
    else:
        processed = 0
        start_time = time.monotonic()
        try:
            for d in daterange(start, end):
                if time.monotonic() - start_time > SOFT_TIME_BUDGET_SECONDS:
                    logger.warning("已耗時超過 %d 秒，本次先以已抓到的資料重新發布，剩餘天數留待下次執行",
                                   SOFT_TIME_BUDGET_SECONDS)
                    break
                if process_with_retry(d):
                    processed += 1
        except TemporarilyUnavailableError as e:
            logger.error("重試多次仍失敗，本次先以已抓到的資料重新發布：%s", e)
        logger.info("本次更新處理了 %d 個交易日", processed)

    sync_taiex_ohlc()
    generate_dashboard()
    logger.info("儀表板已重新產生")

    latest_after = db.get_latest_date()
    if latest_after:
        publish_dashboard(latest_after)


if __name__ == "__main__":
    main()
