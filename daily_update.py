"""每日自動更新進入點，供 Windows 工作排程器呼叫。
會自動從資料庫最後一筆日期的隔天補到「今天」，因此就算某天電腦沒開機也能自動補齊。
"""
import logging
import sys
from datetime import date, datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

import db
from dateutil_tw import daterange
from pipeline import process_date
from dashboard import generate_dashboard
from publish import publish_dashboard

LOG_PATH = None  # 在 config 內設定實際路徑亦可，這裡先用 stdout，交給工作排程器導向檔案


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
        for d in daterange(start, end):
            if process_date(d):
                processed += 1
        logger.info("本次更新處理了 %d 個交易日", processed)

    generate_dashboard()
    logger.info("儀表板已重新產生")

    publish_dashboard(date.today().strftime("%Y%m%d"))


if __name__ == "__main__":
    main()
