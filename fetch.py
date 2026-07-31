"""從 TWSE(上市) / TPEx(上櫃) 免費公開端點抓取指定日期的融資餘額與收盤價資料。"""
import time
import requests

from config import (
    TWSE_MARGIN_URL, TWSE_PRICE_URL, TPEX_MARGIN_URL, TPEX_PRICE_URL,
    TWSE_TAIEX_OHLC_URL, REQUEST_TIMEOUT, REQUEST_HEADERS,
)


class NoTradingDataError(Exception):
    """指定日期非交易日或資料尚未產生。"""


def _get_json(url: str, params: dict, retries: int = 3):
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (i + 1))
    raise last_err


def _first_index(fields: list) -> dict:
    """TWSE 表格的欄位名稱會重複（融資、融券各一組同名欄位，融資在前）。
    必須保留「第一次出現」的位置，否則會誤讀成融券資料。"""
    idx = {}
    for i, name in enumerate(fields):
        if name not in idx:
            idx[name] = i
    return idx


def _to_float(s):
    if s is None:
        return None
    s = str(s).replace(",", "").strip()
    if s in ("", "--", "X"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def fetch_twse_margin(date_ad: str) -> dict:
    """date_ad: YYYYMMDD。回傳 {stock_id: {"name":.., "buy":.., "balance":..}}"""
    j = _get_json(TWSE_MARGIN_URL, {"date": date_ad, "selectType": "ALL", "response": "json"})
    if j.get("stat") != "OK":
        raise NoTradingDataError(f"TWSE margin {date_ad}: {j.get('stat')}")
    table = next(t for t in j["tables"] if "融資融券彙總" in t.get("title", ""))
    idx = _first_index(table["fields"])
    out = {}
    for row in table["data"]:
        stock_id = row[idx["代號"]]
        out[stock_id] = {
            "name": row[idx["名稱"]],
            "buy": _to_float(row[idx["買進"]]),
            "balance": _to_float(row[idx["今日餘額"]]),
        }
    return out


def fetch_tpex_margin(date_roc: str) -> dict:
    """date_roc: YYY/MM/DD (民國年)。回傳同 fetch_twse_margin 格式。"""
    j = _get_json(TPEX_MARGIN_URL, {"l": "zh-tw", "d": date_roc, "o": "json"})
    tables = j.get("tables")
    if not tables:
        raise NoTradingDataError(f"TPEx margin {date_roc}: empty response")
    table = tables[0]
    idx = _first_index(table["fields"])
    out = {}
    for row in table["data"]:
        stock_id = row[idx["代號"]]
        out[stock_id] = {
            "name": row[idx["名稱"]],
            "buy": _to_float(row[idx["資買"]]),
            "balance": _to_float(row[idx["資餘額"]]),
        }
    return out


def fetch_twse_price(date_ad: str):
    """回傳 (taiex_close, taiex_change_pct, {stock_id: close_price})"""
    j = _get_json(TWSE_PRICE_URL, {"date": date_ad, "type": "ALL", "response": "json"})
    if j.get("stat") != "OK":
        raise NoTradingDataError(f"TWSE price {date_ad}: {j.get('stat')}")

    idx_table = next(t for t in j["tables"] if t.get("title", "").endswith("價格指數(臺灣證券交易所)"))
    idx_fields = _first_index(idx_table["fields"])
    taiex_row = next(r for r in idx_table["data"] if r[idx_fields["指數"]] == "發行量加權股價指數")
    taiex_close = _to_float(taiex_row[idx_fields["收盤指數"]])
    taiex_change_pct = _to_float(taiex_row[idx_fields["漲跌百分比(%)"]])

    close_table = next(t for t in j["tables"] if t.get("title") and "每日收盤行情" in t["title"])
    cf = _first_index(close_table["fields"])
    closes = {}
    for row in close_table["data"]:
        stock_id = row[cf["證券代號"]]
        closes[stock_id] = _to_float(row[cf["收盤價"]])
    return taiex_close, taiex_change_pct, closes


def fetch_tpex_price(date_roc: str):
    """回傳 {stock_id: close_price}（上櫃）"""
    j = _get_json(TPEX_PRICE_URL, {"l": "zh-tw", "d": date_roc, "o": "json"})
    tables = j.get("tables")
    if not tables:
        raise NoTradingDataError(f"TPEx price {date_roc}: empty response")
    table = tables[0]
    fields = _first_index(table["fields"])
    closes = {}
    for row in table["data"]:
        stock_id = row[fields["代號"]]
        closes[stock_id] = _to_float(row[fields["收盤"]])
    return closes


def fetch_taiex_ohlc_month(date_ad: str) -> dict:
    """抓取某個月份的加權指數開高低收。date_ad 給該月任一天(YYYYMMDD)。
    回傳 {YYYYMMDD: (open, high, low, close)}"""
    j = _get_json(TWSE_TAIEX_OHLC_URL, {"date": date_ad, "response": "json"})
    if j.get("stat") != "OK":
        raise NoTradingDataError(f"TAIEX OHLC {date_ad}: {j.get('stat')}")
    out = {}
    for row in j["data"]:
        roc_date = row[0]  # 例如 115/07/01
        y, m, d = roc_date.split("/")
        key = f"{int(y) + 1911}{int(m):02d}{int(d):02d}"
        out[key] = (
            _to_float(row[1]), _to_float(row[2]), _to_float(row[3]), _to_float(row[4]),
        )
    return out


def fetch_all(date_ad: str, date_roc: str):
    """整合單一交易日所需的全部原始資料。任何一段抓不到就整體視為非交易日。"""
    twse_margin = fetch_twse_margin(date_ad)
    tpex_margin = fetch_tpex_margin(date_roc)
    taiex_close, taiex_change_pct, twse_close = fetch_twse_price(date_ad)
    tpex_close = fetch_tpex_price(date_roc)
    return {
        "taiex_close": taiex_close,
        "taiex_change_pct": taiex_change_pct,
        "margin": {**twse_margin, **tpex_margin},
        "close": {**twse_close, **tpex_close},
    }
