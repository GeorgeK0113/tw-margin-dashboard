import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "dashboard.db"
DASHBOARD_HTML_PATH = BASE_DIR / "data" / "dashboard.html"

TWSE_MARGIN_URL = "https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN"
TWSE_PRICE_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
TPEX_MARGIN_URL = "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php"
TPEX_PRICE_URL = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"

REQUEST_TIMEOUT = 20
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) dashboard-bot/1.0"
}

# 融資維持率門檻公式：收盤價 / (融資成本 * MAINTENANCE_DIVISOR) * 100
MAINTENANCE_DIVISOR = 0.6
MAINTENANCE_THRESHOLDS = [130, 140, 150, 160]

MA_WINDOWS = [20, 60]

# 個股代號篩選：上市/上櫃普通股，排除 ETF(00開頭)/ETN/TDR(91開頭)等
def is_ordinary_share(stock_id: str) -> bool:
    if not stock_id or len(stock_id) != 4 or not stock_id.isdigit():
        return False
    if stock_id.startswith("00"):
        return False
    if stock_id.startswith("91"):
        return False
    return True
