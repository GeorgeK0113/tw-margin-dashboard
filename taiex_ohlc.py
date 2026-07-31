"""補齊 daily_metrics 裡的加權指數開高低收（月批次抓取，一個月一次請求）。"""
import logging
import time

import db
from fetch import fetch_taiex_ohlc_month, NoTradingDataError

logger = logging.getLogger(__name__)


def sync_taiex_ohlc(only_missing: bool = True):
    conn = db.get_conn()
    where = "WHERE taiex_open IS NULL" if only_missing else ""
    rows = conn.execute(f"SELECT date FROM daily_metrics {where} ORDER BY date").fetchall()
    conn.close()

    if not rows:
        logger.info("加權指數 OHLC already complete")
        return 0

    months = sorted({r[0][:6] for r in rows})
    updated = 0
    for ym in months:
        try:
            data = fetch_taiex_ohlc_month(f"{ym}01")
        except (NoTradingDataError, Exception) as e:  # noqa: BLE001
            logger.warning("OHLC %s 抓取失敗：%s", ym, e)
            continue

        conn = db.get_conn()
        conn.executemany(
            """UPDATE daily_metrics SET taiex_open=?, taiex_high=?, taiex_low=?
               WHERE date=?""",
            [(o, h, l, d) for d, (o, h, l, _c) in data.items()],
        )
        conn.commit()
        updated += conn.total_changes
        conn.close()
        time.sleep(0.5)

    logger.info("加權指數 OHLC 更新 %d 筆", updated)
    return updated


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    db.init_db()
    sync_taiex_ohlc()
