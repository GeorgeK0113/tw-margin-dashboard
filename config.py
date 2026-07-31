import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "dashboard.db"
DASHBOARD_HTML_PATH = BASE_DIR / "data" / "dashboard.html"

# GitHub Pages 發布用（gh-pages 分支的 git worktree）
PAGES_WORKTREE_DIR = BASE_DIR / ".worktree-gh-pages"
PAGES_BRANCH = "gh-pages"

TWSE_MARGIN_URL = "https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN"
TWSE_PRICE_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
TWSE_TAIEX_OHLC_URL = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST"
TPEX_MARGIN_URL = "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php"
# 注意：舊的 stk_quote_result.php 會忽略日期參數、永遠回傳最新交易日，不可使用。
TPEX_PRICE_URL = "https://www.tpex.org.tw/www/zh-tw/afterTrading/dailyQuotes"

REQUEST_TIMEOUT = 20
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) dashboard-bot/1.0"
}

# 融資維持率門檻公式：收盤價 / (融資成本 * MAINTENANCE_DIVISOR) * 100
MAINTENANCE_DIVISOR = 0.6
MAINTENANCE_THRESHOLDS = [130, 140, 150, 160]

MA_WINDOWS = [20, 60]

# 成本線是遞推的，起算初期的成本＝當日收盤價，維持率會失真。
# 因此資料從 WARMUP_START 開始累積，但只展示 DISPLAY_START 之後的部分。
WARMUP_START = "20220801"
DISPLAY_START = "20230801"

# 個股代號篩選：上市/上櫃普通股，排除 ETF(00開頭)/ETN/TDR(91開頭)等
def is_ordinary_share(stock_id: str) -> bool:
    if not stock_id or len(stock_id) != 4 or not stock_id.isdigit():
        return False
    if stock_id.startswith("00"):
        return False
    if stock_id.startswith("91"):
        return False
    return True
