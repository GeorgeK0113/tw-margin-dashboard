"""從資料庫產生靜態離線 HTML 儀表板（Plotly 圖表內嵌，開啟不需網路）。"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import db
from config import DASHBOARD_HTML_PATH


def generate_dashboard():
    conn = db.get_conn()
    df = pd.read_sql_query("SELECT * FROM daily_metrics ORDER BY date", conn)
    conn.close()

    if df.empty:
        DASHBOARD_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
        DASHBOARD_HTML_PATH.write_text("<h1>尚無資料，請先執行 backfill.py 或 daily_update.py</h1>", encoding="utf-8")
        return

    df["date_fmt"] = pd.to_datetime(df["date"], format="%Y%m%d")
    latest = df.iloc[-1]

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        row_heights=[0.34, 0.22, 0.22, 0.22],
        subplot_titles=(
            "加權指數 TAIEX 收盤",
            "融資維持率 < 130% 個股家數",
            "市場廣度：站上 20/60 日均線比例 (%)",
            "大盤整體維持率（餘額加權估算，%）",
        ),
    )

    fig.add_trace(
        go.Scatter(x=df["date_fmt"], y=df["taiex_close"], name="TAIEX", line=dict(color="#d62728")),
        row=1, col=1,
    )

    fig.add_trace(
        go.Bar(x=df["date_fmt"], y=df["count_below_130"], name="<130%家數", marker_color="#c0392b"),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(x=df["date_fmt"], y=df["pct_above_ma20"], name="站上20日均線%", line=dict(color="#2980b9")),
        row=3, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["date_fmt"], y=df["pct_above_ma60"], name="站上60日均線%", line=dict(color="#8e44ad")),
        row=3, col=1,
    )

    fig.add_trace(
        go.Scatter(x=df["date_fmt"], y=df["market_maintenance_ratio"], name="大盤維持率(估)", line=dict(color="#16a085")),
        row=4, col=1,
    )
    fig.add_hline(y=130, line_dash="dot", line_color="red", row=4, col=1)
    fig.add_hline(y=150, line_dash="dot", line_color="orange", row=4, col=1)

    fig.update_layout(
        height=1100,
        title=(
            f"台股市場廣度儀表板（本地自動版）｜資料更新至 {latest['date']}｜"
            f"融資維持率<130%家數：{int(latest['count_below_130']) if pd.notna(latest['count_below_130']) else '—'}"
        ),
        showlegend=True,
        hovermode="x unified",
    )

    DASHBOARD_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(DASHBOARD_HTML_PATH), include_plotlyjs=True, full_html=True)


if __name__ == "__main__":
    generate_dashboard()
