"""融資成本／維持率計算核心。

個股融資成本 = (昨日融資成本 x (今日餘額 - 今日買進) + 收盤價 x 今日買進) / 今日餘額
個股融資維持率 = 收盤價 / (融資成本 x 0.6) x 100%
大盤整體維持率（本站估算版）= 以各股融資餘額(張)加權平均的個股維持率
    (原站的「官方公布值」是交易所另外公布的加總數字，無公開、免費、每日更新的 API 可取得，
     這裡改用「餘額加權平均」近似，方法自洽、不依賴任何需要付費/註冊的資料源。)
"""
import pandas as pd

from config import MAINTENANCE_DIVISOR, MAINTENANCE_THRESHOLDS, MA_WINDOWS, is_ordinary_share


def compute_stock_rows(margin: dict, close: dict, prev_stock_map: dict) -> list[dict]:
    rows = []
    for stock_id, m in margin.items():
        if not is_ordinary_share(stock_id):
            continue
        c = close.get(stock_id)
        balance = m.get("balance")
        if c is None or balance is None:
            continue
        buy = m.get("buy") or 0

        prev_cost, _prev_balance = prev_stock_map.get(stock_id, (None, None))
        if prev_cost is None:
            prev_cost = c  # 新出現的個股，以當日收盤價作為起始成本（冷啟動近似，會隨後續交易日收斂）

        if balance and balance > 0:
            carried = max(balance - buy, 0)
            margin_cost = (prev_cost * carried + c * buy) / balance
            maintenance_ratio = c / (margin_cost * MAINTENANCE_DIVISOR) * 100
        else:
            margin_cost = prev_cost
            maintenance_ratio = None

        rows.append({
            "stock_id": stock_id,
            "name": m.get("name"),
            "close": c,
            "margin_balance": balance,
            "margin_buy": buy,
            "margin_cost": margin_cost,
            "maintenance_ratio": maintenance_ratio,
        })
    return rows


def compute_breadth(conn, date_str: str, stock_ids: list[str]) -> dict:
    """計算漲跌家數與站上 20/60 日均線比例，需要資料庫裡已有的歷史收盤價。"""
    if not stock_ids:
        return {"up_count": None, "down_count": None, "pct_above_ma20": None, "pct_above_ma60": None}

    max_window = max(MA_WINDOWS)
    # 只撈計算均線需要的最近 N 個交易日，避免歷史表越長越慢
    recent = conn.execute(
        "SELECT DISTINCT date FROM stock_daily WHERE date <= ? ORDER BY date DESC LIMIT ?",
        (date_str, max_window + 1),
    ).fetchall()
    if not recent:
        return {"up_count": None, "down_count": None, "pct_above_ma20": None, "pct_above_ma60": None}
    since = recent[-1][0]

    df = pd.read_sql_query(
        """SELECT date, stock_id, close FROM stock_daily
           WHERE date >= ? AND date <= ?""",
        conn,
        params=[since, date_str],
    )
    if df.empty:
        return {"up_count": None, "down_count": None, "pct_above_ma20": None, "pct_above_ma60": None}

    wanted = set(stock_ids)
    df = df[df["stock_id"].isin(wanted)]
    pivot = df.pivot(index="date", columns="stock_id", values="close").sort_index()
    if date_str not in pivot.index:
        return {"up_count": None, "down_count": None, "pct_above_ma20": None, "pct_above_ma60": None}

    today = pivot.loc[date_str]
    prev_rows = pivot.loc[:date_str].iloc[:-1]
    prev_close = prev_rows.iloc[-1] if not prev_rows.empty else None

    result = {}
    if prev_close is not None:
        diff = today - prev_close
        valid = diff.dropna()
        result["up_count"] = int((valid > 0).sum())
        result["down_count"] = int((valid < 0).sum())
    else:
        result["up_count"] = None
        result["down_count"] = None

    for w in MA_WINDOWS:
        window_df = pivot.tail(w)
        if len(window_df) < w:
            result[f"pct_above_ma{w}"] = None
            continue
        ma = window_df.mean()
        above = (today > ma).dropna()
        result[f"pct_above_ma{w}"] = float(above.mean() * 100) if len(above) else None

    return result


def compute_day_metrics(stock_rows: list[dict], breadth: dict, taiex_close, taiex_change_pct) -> dict:
    margined = [
        r for r in stock_rows
        if r["margin_balance"] and r["margin_balance"] > 0 and r["maintenance_ratio"] is not None
    ]
    total_margin_stocks = len(margined)

    counts = {}
    for th in MAINTENANCE_THRESHOLDS:
        counts[f"count_below_{th}"] = sum(1 for r in margined if r["maintenance_ratio"] < th)

    pct_below_130 = (
        counts["count_below_130"] / total_margin_stocks * 100 if total_margin_stocks else None
    )

    total_balance = sum(r["margin_balance"] for r in margined)
    market_ratio = (
        sum(r["maintenance_ratio"] * r["margin_balance"] for r in margined) / total_balance
        if total_balance else None
    )

    return {
        "taiex_close": taiex_close,
        "taiex_change_pct": taiex_change_pct,
        "total_margin_stocks": total_margin_stocks,
        **counts,
        "pct_below_130": pct_below_130,
        "market_maintenance_ratio": market_ratio,
        "up_count": breadth.get("up_count"),
        "down_count": breadth.get("down_count"),
        "pct_above_ma20": breadth.get("pct_above_ma20"),
        "pct_above_ma60": breadth.get("pct_above_ma60"),
    }
