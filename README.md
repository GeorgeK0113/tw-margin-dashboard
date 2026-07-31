# 台股市場廣度儀表板（本地自動版）

參考 mofiinvestment.com 的公開算法重建的本地版本，資料完全來自 TWSE／TPEx 免費公開端點，
不需要任何帳號或 API Token。

**公開網址（自動每日更新）：https://georgek0113.github.io/tw-margin-dashboard/**

## 檔案說明

- `fetch.py` — 從 TWSE(上市)/TPEx(上櫃) 抓取每日融資餘額與收盤價
- `compute.py` — 融資成本／維持率遞迴公式、家數統計、均線廣度
- `db.py` / `config.py` — SQLite 資料庫與設定
- `pipeline.py` — 單日「抓取→計算→存檔」流程
- `backfill.py` — 歷史回補：`python backfill.py 2025-08-01 2026-07-29`
- `daily_update.py` — 每日自動更新進入點（會自動補齊漏掉的天數），供工作排程器呼叫
- `dashboard.py` — 產生離線可開啟的 `data/dashboard.html`
- `publish.py` — 把 `data/dashboard.html` 發布到 GitHub Pages（`gh-pages` 分支，每天覆蓋同一個 commit）
- `setup_task_scheduler.ps1` — 註冊 Windows 每日排程（平日 21:45，會依序執行抓取／計算／產生頁面／發布）

## 首次使用

```bash
python -m pip install -r requirements.txt
python backfill.py 2025-08-01 2026-07-29   # 回補約一年歷史（暖機成本基礎）
python dashboard.py                          # 產生 data/dashboard.html
```

## 每日自動化

```powershell
.\setup_task_scheduler.ps1
```

之後每個平日 21:45 會自動執行 `daily_update.py`：抓當天資料、更新資料庫、重新產生
`data/dashboard.html`。log 在 `data/daily_update.log`。

## 已知限制（相對原站的簡化）

1. **成本基礎需要暖機期**：融資成本是用「前一日成本」遞迴推算，回補的第一天會把所有
   個股的起始成本設為當天收盤價（此時維持率一律=166.67%），需要幾週到幾個月的真實
   交易資料，數字才會貼近實際狀況。回補區間越長，早期資料越準。
2. **大盤整體維持率是本地估算值**，不是交易所另外公布的官方數字（那個數字沒有找到
   免費、每日更新的公開 API）。改用「所有個股維持率以融資餘額(張)加權平均」，方法
   自洽，但無法逐年比對誤差。
3. **TAIEX 只有收盤價，沒有真正的開高低（K線）**：免費端點沒有找到大盤日內 OHLC，
   目前用收盤價折線圖代替原站的 K 線圖。
4. **個股篩選用代號規則近似**（4碼、非00開頭、非91開頭 視為普通股），排除 ETF/ETN/TDR，
   跟官方股票清單可能有極少數落差。
