"""AD/ROC 日期轉換工具（避免與標準庫 datetime 混淆，故取名 dateutil_tw）。"""
from datetime import date, timedelta


def ad_to_roc(d: date) -> str:
    return f"{d.year - 1911}/{d.month:02d}/{d.day:02d}"


def ad_to_compact(d: date) -> str:
    return d.strftime("%Y%m%d")


def ad_to_slash(d: date) -> str:
    return d.strftime("%Y/%m/%d")


def daterange(start: date, end: date):
    """含頭尾，只吐出週一到週五（假日仍可能無資料，由呼叫端捕捉例外略過）。"""
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)
