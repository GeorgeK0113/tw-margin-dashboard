# -*- coding: utf-8 -*-
"""儀表板 HTML 模板。__DATA__ / __META__ 由 dashboard.py 以 JSON 取代。"""

HTML = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>台股市場廣度儀表板</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
:root{
  --bg:#05070f;
  --ink:#e8ecf6;
  --muted:#8b96b0;
  --line:rgba(255,255,255,.09);
  --card:rgba(255,255,255,.045);
  --up:#ff4d6d;      /* 台股：紅漲 */
  --down:#22c55e;    /* 台股：綠跌 */
  --danger:#ff3b5c;
  --cyan:#22d3ee;
  --violet:#a78bfa;
  --amber:#fbbf24;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--ink); overflow-x:hidden;
  font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  line-height:1.75; -webkit-font-smoothing:antialiased;
}
/* ---------- 動態背景 ---------- */
.bg{position:fixed;inset:0;z-index:-2;overflow:hidden;background:
  radial-gradient(1200px 700px at 12% -10%, #101838 0%, transparent 60%),
  radial-gradient(1000px 600px at 88% 0%, #2a0c27 0%, transparent 58%),
  radial-gradient(900px 700px at 50% 110%, #042026 0%, transparent 62%),
  var(--bg);}
/* 壓低背景亮度，確保圖表與內文對比 */
.bg::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(5,7,15,.30) 0%,rgba(5,7,15,.66) 46%,rgba(5,7,15,.80) 100%)}
.orb{position:absolute;border-radius:50%;filter:blur(96px);opacity:.30;mix-blend-mode:screen;
  animation:drift 26s ease-in-out infinite alternate}
.orb.a{width:520px;height:520px;left:-90px;top:-110px;background:#3b5bff;animation-duration:24s}
.orb.b{width:460px;height:460px;right:-80px;top:60px;background:#ff2e63;animation-duration:31s;animation-delay:-6s}
.orb.c{width:600px;height:600px;left:34%;bottom:-260px;background:#00e0b8;animation-duration:37s;animation-delay:-12s}
@keyframes drift{
  0%{transform:translate(0,0) scale(1)}
  50%{transform:translate(60px,-40px) scale(1.12)}
  100%{transform:translate(-50px,50px) scale(.94)}
}
.grid{position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:.35;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:64px 64px;
  mask-image:radial-gradient(circle at 50% 30%,#000 0%,transparent 78%);
  -webkit-mask-image:radial-gradient(circle at 50% 30%,#000 0%,transparent 78%);}
@media (prefers-reduced-motion:reduce){.orb{animation:none}}

.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}

/* ---------- 頁首 ---------- */
header{padding:64px 0 26px;text-align:center}
.kicker{font-size:11px;letter-spacing:.42em;color:var(--muted);text-transform:uppercase;margin-bottom:14px}
h1{margin:0;font-size:clamp(30px,5.2vw,52px);font-weight:800;letter-spacing:-.02em;
  background:linear-gradient(100deg,#fff 10%,#8fd3ff 45%,#ff9ec4 80%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.badge{display:inline-flex;align-items:center;gap:9px;margin-top:18px;padding:7px 16px;
  border:1px solid var(--line);border-radius:999px;background:var(--card);
  font-size:13px;color:var(--muted);backdrop-filter:blur(10px)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--cyan);box-shadow:0 0 12px var(--cyan);
  animation:pulse 2.2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.8)}}

/* ---------- 主結論 ---------- */
.hero{margin:42px 0 10px;padding:36px 30px;border:1px solid var(--line);border-radius:22px;
  background:linear-gradient(160deg,rgba(255,77,109,.10),rgba(255,255,255,.03) 55%);
  backdrop-filter:blur(16px);text-align:center;position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;
  background:radial-gradient(560px 200px at 50% 0%,rgba(255,77,109,.20),transparent 70%);pointer-events:none}
.hero p{margin:0;color:#c4cde3;font-size:clamp(14px,2.1vw,17px);position:relative}
.hero-num{font-size:clamp(58px,13vw,116px);font-weight:900;line-height:1.02;margin:10px 0 4px;
  font-variant-numeric:tabular-nums;letter-spacing:-.03em;position:relative;
  background:linear-gradient(180deg,#fff,var(--danger));
  -webkit-background-clip:text;background-clip:text;color:transparent;
  text-shadow:0 0 60px rgba(255,59,92,.35)}
.hero-num .unit{font-size:.3em;font-weight:700;color:var(--muted);
  -webkit-text-fill-color:var(--muted);margin-left:10px;letter-spacing:0}
.pbar{margin:22px auto 0;max-width:560px;position:relative}
.pbar-track{height:9px;border-radius:99px;overflow:hidden;
  background:linear-gradient(90deg,#1c7a4e,#c9a227 55%,var(--danger))}
.pbar-track i{display:block;height:100%;background:rgba(5,7,15,.72);float:right}
.pbar-lab{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted);margin-top:8px}

/* ---------- 數據卡 ---------- */
.stats{display:grid;gap:14px;margin:26px 0 8px;
  grid-template-columns:repeat(auto-fit,minmax(196px,1fr))}
.card{padding:20px 20px 18px;border:1px solid var(--line);border-radius:18px;background:var(--card);
  backdrop-filter:blur(14px);position:relative;overflow:hidden;
  transition:transform .25s ease,border-color .25s ease}
.card:hover{transform:translateY(-4px);border-color:rgba(255,255,255,.22)}
.card::after{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--accent,var(--cyan));opacity:.85}
.card .lab{font-size:12px;color:var(--muted);letter-spacing:.06em;margin-bottom:9px}
.card .val{font-size:clamp(25px,3.6vw,34px);font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.card .sub{font-size:12px;color:var(--muted);margin-top:7px}
.up{color:var(--up)} .down{color:var(--down)}

/* ---------- 控制列 ---------- */
.controls{display:flex;flex-wrap:wrap;gap:22px;justify-content:space-between;align-items:center;
  margin:30px 0 14px;padding:16px 18px;border:1px solid var(--line);border-radius:16px;
  background:var(--card);backdrop-filter:blur(14px);position:sticky;top:12px;z-index:20}
.grp{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.grp>span{font-size:12px;color:var(--muted);letter-spacing:.08em;white-space:nowrap}
.btn{padding:7px 15px;border:1px solid var(--line);border-radius:999px;background:transparent;
  color:var(--muted);font-size:13px;font-family:inherit;cursor:pointer;transition:all .18s ease;white-space:nowrap}
.btn:hover{color:var(--ink);border-color:rgba(255,255,255,.3)}
.btn.on{background:var(--ink);color:#05070f;border-color:var(--ink);font-weight:700}
.btn.on.risk{background:var(--danger);border-color:var(--danger);color:#fff}

.chartcard{margin:6px 0 4px;padding:16px 10px 8px;border:1px solid var(--line);border-radius:20px;
  background:rgba(4,6,14,.62);backdrop-filter:blur(18px)}
#chart{height:940px}
.hint{text-align:center;font-size:12px;color:var(--muted);margin:10px 0 36px}

/* ---------- 說明區 ---------- */
section.doc{margin:34px 0;padding:32px 30px;border:1px solid var(--line);border-radius:20px;
  background:var(--card);backdrop-filter:blur(14px)}
section.doc h2{margin:0 0 8px;font-size:22px;font-weight:800;display:flex;align-items:center;gap:11px}
section.doc h2 .ic{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;font-size:16px;
  background:linear-gradient(140deg,var(--cyan),var(--violet));color:#05070f;font-weight:900}
section.doc .tag{font-size:11px;letter-spacing:.3em;color:var(--muted);text-transform:uppercase;margin-bottom:20px}
section.doc p{color:#bcc6dc;margin:0 0 15px}
.panelrow{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));margin:20px 0}
.panel{padding:17px 18px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.03)}
.panel h3{margin:0 0 8px;font-size:14.5px;display:flex;align-items:center;gap:9px}
.panel h3 b{width:23px;height:23px;border-radius:7px;display:grid;place-items:center;
  font-size:12px;background:var(--pc,var(--cyan));color:#05070f}
.panel p{font-size:13.5px;margin:0;color:#a9b4cc;line-height:1.7}
.eq{margin:14px 0;padding:15px 17px;border-radius:12px;overflow-x:auto;
  border:1px solid var(--line);border-left:3px solid var(--violet);background:rgba(0,0,0,.32);
  font-family:ui-monospace,"Cascadia Code",Consolas,monospace;font-size:13px;color:#cfe4ff;white-space:nowrap}
.eq em{color:var(--muted);font-style:normal;display:block;font-size:11.5px;margin-bottom:6px;
  font-family:inherit;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;margin:16px 0;font-size:13.5px}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600;font-size:12px;letter-spacing:.05em}
td{font-variant-numeric:tabular-nums}
.note{padding:15px 17px;border-radius:12px;border:1px solid rgba(251,191,36,.28);
  background:rgba(251,191,36,.07);font-size:13.5px;color:#e2d4ae}
.note b{color:var(--amber)}
footer{text-align:center;padding:44px 0 10px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);margin-top:42px}
@media(max-width:640px){
  #chart{height:780px}
  .chartcard{padding:12px 2px 4px}
  .controls{position:static}
  .hero{padding:28px 18px}
  section.doc{padding:24px 19px}
}
</style>
</head>
<body>
<div class="bg"><div class="orb a"></div><div class="orb b"></div><div class="orb c"></div></div>
<div class="grid"></div>

<div class="wrap">
  <header>
    <div class="kicker">Margin Maintenance &amp; Market Breadth</div>
    <h1>台股市場廣度儀表板</h1>
    <div class="badge"><span class="dot"></span><span id="updBadge"></span></div>
  </header>

  <div class="hero">
    <p id="heroLead"></p>
    <div class="hero-num"><span id="heroCount">—</span><span class="unit">檔</span></div>
    <p id="heroSub"></p>
    <div class="pbar">
      <div class="pbar-track"><i id="pbarMask"></i></div>
      <div class="pbar-lab"><span>壓力最輕</span><span id="pbarTxt"></span><span>壓力最重</span></div>
    </div>
  </div>

  <div class="stats" id="stats"></div>

  <div class="controls">
    <div class="grp"><span>期間</span><div id="periodBtns"></div></div>
    <div class="grp"><span>維持率門檻</span><div id="thBtns"></div></div>
  </div>

  <div class="chartcard"><div id="chart"></div></div>
  <div class="hint">滑鼠移到圖上顯示當日完整數字｜滾輪縮放、按住拖曳平移｜手機雙指縮放</div>

  <section class="doc">
    <h2><span class="ic">?</span>這張圖怎麼看</h2>
    <div class="tag">How to read</div>
    <p>四格圖由上而下，是把「指數在哪裡」拆解成「誰在撐、誰快撐不住」的四個角度。</p>
    <div class="panelrow">
      <div class="panel" style="--pc:#ff4d6d">
        <h3><b>1</b>加權指數 K 線</h3>
        <p>紅漲綠跌的日 K。它只告訴你結果，不告訴你這個結果是多健康——下面三格才是體質檢查。</p>
      </div>
      <div class="panel" style="--pc:#ff3b5c">
        <h3><b>2</b>維持率跌破門檻家數</h3>
        <p>這格是重點。柱子越高，代表越多融資戶的擔保品已經不夠，隨時可能被券商追繳；補不進來就會被斷頭賣出，形成「越跌越賣」的螺旋。這是融資戶被迫賣壓的直接讀數。</p>
      </div>
      <div class="panel" style="--pc:#22d3ee">
        <h3><b>3</b>市場廣度</h3>
        <p>全市場有多少比例的股票還站在 20 日與 60 日均線上方。指數還在高位、站上均線比例卻一路下滑，代表漲勢只剩少數權值股在撐——這是廣度惡化的典型型態。</p>
      </div>
      <div class="panel" style="--pc:#a78bfa">
        <h3><b>4</b>大盤整體維持率</h3>
        <p>全市場融資部位合起來的健康度，畫上 130% 追繳線與 150% 警戒線。這條線用的是證交所口徑，可與官方公布值對照（見下方驗證）。跌向 130% 代表壓力已是整體性的，而非個別族群。</p>
      </div>
    </div>
    <p>上方按鈕可切換觀察期間，以及改變「跌破多少維持率」的認定門檻——把門檻從 130% 拉到 160%，看的就是「連還沒到追繳、但已經接近的族群有多大」。</p>
  </section>

  <section class="doc">
    <h2><span class="ic">∑</span>算法與驗證</h2>
    <div class="tag">Method &amp; validation</div>
    <p>個股融資維持率沒有任何官方或第三方資料源直接提供。原因是維持率＝擔保品市值 ÷ 融資金額，而融資金額是每個投資人各自在不同價位借的錢，交易所無從得知，因此只公布全市場加總。本站的個股維持率是依公開算法逐日遞推：</p>
    <div class="eq"><em>個股融資成本</em>成本 = (昨日成本 × (今日餘額 − 今日融資買進) + 今日收盤價 × 今日融資買進) ÷ 今日餘額</div>
    <div class="eq"><em>個股融資維持率</em>維持率 = 收盤價 ÷ (融資成本 × 0.6) × 100%</div>
    <div class="eq"><em>大盤整體維持率（官方口徑）</em>大盤維持率 = Σ(收盤價 × 融資餘額張數) ÷ 上市融資金額餘額 × 100%</div>

    <h3 style="font-size:16px;margin:26px 0 10px">怎麼知道算得對不對</h3>
    <p>第三條公式的分子與分母都來自交易所公開資料，算出來的結果可以直接對照證交所公布的大盤維持率。實測 2026-07-29：</p>
    <div class="eq"><em>驗證</em>本站計算 157.99%　vs　證交所公布 158.00%　→　誤差 0.01 個百分點</div>
    <p>這條驗證成立，代表「收盤價 × 融資餘額」這個市值推算是對的。個股維持率用的是同一組收盤價與融資餘額，只是再多一層成本遞推，因此個股層級的推算也建立在已驗證的基礎上。</p>
    <p>成本線是遞推的：今天的成本建立在昨天的成本上。起算頭幾個月的成本會等於當日收盤價、維持率一律是 166.67%，屬於失真值，因此<b>暖機期的資料不會進到圖表</b>。</p>
    <table id="metaTable"></table>
    <div class="note">
      <b>已知限制（誠實揭露）：</b>
      ① 成本線暖機期比原始參考站短，慢週轉個股的成本可能偏低、維持率偏高，跌破門檻家數會略微低估。
      ② 大盤維持率為上市口徑（與證交所公布值一致），不含上櫃；個股家數統計則含上市＋上櫃。
      ③ 個股範圍以代號規則近似（四碼、排除 ETF/ETN/TDR），與官方清單可能有極少數落差。
    </div>
    <p style="margin-top:16px">資料來源：台灣證券交易所（TWSE）與證券櫃檯買賣中心（TPEx）公開端點，每個交易日晚間自動抓取重算，無需任何付費資料源。</p>
  </section>

  <footer>
    <div id="footMeta"></div>
    <div style="margin-top:8px;opacity:.7">本頁為研究用途，不構成任何投資建議。</div>
  </footer>
</div>

<script>
const DATA = __DATA__;
const META = __META__;

const PERIODS = [["3個月",3],["半年",6],["1年",12],["2年",24],["5年",60]];
const THS = [130,140,150,160];
let state = { months: 12, th: 130 };

const fmt = (n,d=0)=> n==null||isNaN(n) ? "—"
  : Number(n).toLocaleString("zh-TW",{minimumFractionDigits:d,maximumFractionDigits:d});
const parseD = s => new Date(+s.slice(0,4), +s.slice(4,6)-1, +s.slice(6,8));

function sliceIdx(){
  const end = parseD(DATA.dates[DATA.dates.length-1]);
  const cut = new Date(end); cut.setMonth(cut.getMonth() - state.months);
  let i = DATA.dates.findIndex(d => parseD(d) >= cut);
  return i < 0 ? 0 : i;
}
const cut = a => a.slice(sliceIdx());

function buildBtns(){
  document.getElementById("periodBtns").innerHTML = PERIODS.map(([l,m])=>
    `<button class="btn${m===state.months?" on":""}" data-m="${m}">${l}</button>`).join(" ");
  document.getElementById("thBtns").innerHTML = THS.map(t=>
    `<button class="btn risk${t===state.th?" on":""}" data-t="${t}">&lt; ${t}%</button>`).join(" ");
  document.querySelectorAll("[data-m]").forEach(b=>b.onclick=()=>{state.months=+b.dataset.m;render()});
  document.querySelectorAll("[data-t]").forEach(b=>b.onclick=()=>{state.th=+b.dataset.t;render()});
}

function renderHero(){
  const n = DATA.dates.length-1;
  const series = DATA.below[state.th];
  const cur = series[n], total = DATA.total[n];
  const pct = total ? cur/total*100 : null;

  // 百分位：在「目前選定期間」內，今天的壓力排在哪
  const win = cut(series).filter(v=>v!=null);
  const pr = win.length ? win.filter(v=>v<=cur).length/win.length*100 : null;
  const label = PERIODS.find(p=>p[1]===state.months)[0];

  const chg = DATA.chg[n];
  const cls = chg>=0 ? "up":"down";
  document.getElementById("heroLead").innerHTML =
    `最新交易日 <b>${META.latestPretty}</b>，加權指數收 <b>${fmt(DATA.close[n])}</b>`+
    `（<b class="${cls}">${chg>=0?"+":""}${fmt(chg,2)}%</b>）。`+
    `融資維持率跌破 <b>${state.th}%</b> 的個股家數：`;
  document.getElementById("heroCount").textContent = fmt(cur);
  document.getElementById("heroSub").innerHTML =
    `占全部 <b>${fmt(total)}</b> 檔有融資標的的 <b>${fmt(pct,1)}%</b>，`+
    `位於<b>${label}</b>以來的第 <b>${fmt(pr,1)}</b> 百分位（數字越高＝壓力越大）`;
  document.getElementById("pbarMask").style.width = (100-(pr||0)) + "%";
  document.getElementById("pbarTxt").textContent = `第 ${fmt(pr,1)} 百分位`;
}

function renderStats(){
  const n = DATA.dates.length-1;
  const cur = DATA.below[state.th][n], total = DATA.total[n];
  const up = DATA.up[n], dn = DATA.down[n];
  const upPct = (up!=null&&dn!=null&&(up+dn)>0) ? up/(up+dn)*100 : null;
  const chg = DATA.chg[n];
  const cards = [
    ["加權指數 TAIEX", fmt(DATA.close[n]),
     `<span class="${chg>=0?"up":"down"}">${chg>=0?"+":""}${fmt(chg,2)}%</span>　${META.latestPretty}`, "#ff4d6d"],
    [`維持率 &lt; ${state.th}% 家數`, fmt(cur),
     `占有融資標的 ${fmt(total?cur/total*100:null,1)}%`, "#ff3b5c"],
    ["大盤整體維持率", fmt(DATA.ratio[n],2)+"%",
     `證交所口徑　期間最高 ${fmt(Math.max(...cut(DATA.ratio).filter(v=>v!=null)),2)}%`, "#a78bfa"],
    ["上漲 / 下跌家數", `${fmt(up)} / ${fmt(dn)}`,
     `漲家數占比 ${fmt(upPct,1)}%`, "#22c55e"],
    ["站上 20 日均線", fmt(DATA.ma20[n],1)+"%",
     `60 日均線 ${fmt(DATA.ma60[n],1)}%`, "#22d3ee"],
  ];
  document.getElementById("stats").innerHTML = cards.map(([l,v,s,c])=>
    `<div class="card" style="--accent:${c}"><div class="lab">${l}</div>`+
    `<div class="val">${v}</div><div class="sub">${s}</div></div>`).join("");
}

function renderChart(){
  const i = sliceIdx();
  const x = DATA.dates.slice(i).map(d=>`${d.slice(0,4)}-${d.slice(4,6)}-${d.slice(6,8)}`);
  const series = DATA.below[state.th].slice(i);
  const mx = Math.max(...series.filter(v=>v!=null));
  const colors = series.map(v=>{
    const t = mx ? (v||0)/mx : 0;
    return `rgba(${Math.round(120+135*t)},${Math.round(90-60*t)},${Math.round(120-40*t)},${.55+.45*t})`;
  });

  const price = DATA.hasOHLC
    ? {type:"candlestick",x,open:DATA.open.slice(i),high:DATA.high.slice(i),
       low:DATA.low.slice(i),close:DATA.close.slice(i),name:"加權指數",
       increasing:{line:{color:"#ff4d6d",width:1},fillcolor:"#ff4d6d"},
       decreasing:{line:{color:"#22c55e",width:1},fillcolor:"#22c55e"},
       xaxis:"x",yaxis:"y"}
    : {type:"scatter",mode:"lines",x,y:DATA.close.slice(i),name:"加權指數",
       line:{color:"#ff4d6d",width:2},xaxis:"x",yaxis:"y"};

  const traces = [price,
    {type:"bar",x,y:series,name:`維持率<${state.th}%`,marker:{color:colors},xaxis:"x",yaxis:"y2"},
    {type:"scatter",mode:"lines",x,y:DATA.ma20.slice(i),name:"站上20日均線",
     line:{color:"#22d3ee",width:2},xaxis:"x",yaxis:"y3"},
    {type:"scatter",mode:"lines",x,y:DATA.ma60.slice(i),name:"站上60日均線",
     line:{color:"#a78bfa",width:1.6,dash:"dot"},xaxis:"x",yaxis:"y3"},
    {type:"scatter",mode:"lines",x,y:DATA.ratio.slice(i),name:"大盤整體維持率",
     line:{color:"#5eead4",width:2.2},fill:"tozeroy",fillcolor:"rgba(94,234,212,.08)",
     xaxis:"x",yaxis:"y4"},
  ];

  const ax = {gridcolor:"rgba(255,255,255,.06)",zeroline:false,
              tickfont:{color:"#8b96b0",size:11},linecolor:"rgba(255,255,255,.12)"};
  const title = (t,y,c)=>({text:t,x:0,xref:"paper",y,yref:"paper",xanchor:"left",yanchor:"bottom",
                           showarrow:false,font:{size:13,color:c,family:"inherit"}});

  const rr = DATA.ratio.slice(i).filter(v=>v!=null);
  const lo = rr.length ? Math.min(...rr,128) : 120, hi = rr.length ? Math.max(...rr,152) : 200;

  Plotly.react("chart", traces, {
    paper_bgcolor:"rgba(0,0,0,0)", plot_bgcolor:"rgba(255,255,255,.015)",
    font:{family:'"Noto Sans TC",sans-serif',color:"#e8ecf6"},
    margin:{l:60,r:26,t:26,b:44},
    hovermode:"x unified",
    hoverlabel:{bgcolor:"rgba(8,12,24,.94)",bordercolor:"rgba(255,255,255,.2)",
                font:{color:"#e8ecf6",size:12}},
    dragmode:"pan",
    showlegend:true,
    legend:{orientation:"h",y:1.055,x:0,font:{size:11,color:"#8b96b0"},bgcolor:"rgba(0,0,0,0)"},
    xaxis:Object.assign({},ax,{domain:[0,1],anchor:"y4",rangeslider:{visible:false},
      type:"date",showspikes:true,spikecolor:"rgba(255,255,255,.28)",spikethickness:1,
      spikemode:"across",spikedash:"dot"}),
    yaxis:Object.assign({},ax,{domain:[.77,1],anchor:"x",title:{text:"指數",font:{size:11,color:"#8b96b0"}}}),
    yaxis2:Object.assign({},ax,{domain:[.525,.735],anchor:"x",title:{text:"家數",font:{size:11,color:"#8b96b0"}}}),
    yaxis3:Object.assign({},ax,{domain:[.28,.49],anchor:"x",range:[0,100],
      title:{text:"% 站上均線",font:{size:11,color:"#8b96b0"}}}),
    yaxis4:Object.assign({},ax,{domain:[0,.245],anchor:"x",range:[lo-4,hi+4],
      title:{text:"維持率 %",font:{size:11,color:"#8b96b0"}}}),
    shapes:[
      {type:"line",xref:"paper",x0:0,x1:1,yref:"y4",y0:130,y1:130,
       line:{color:"#ff3b5c",width:1.2,dash:"dash"}},
      {type:"line",xref:"paper",x0:0,x1:1,yref:"y4",y0:150,y1:150,
       line:{color:"#fbbf24",width:1,dash:"dot"}},
    ],
    annotations:[
      title("加權指數 TAIEX（紅漲綠跌）",1.005,"#ff8fa3"),
      title(`融資維持率 < ${state.th}% 個股家數　← 融資戶被迫賣壓`,.742,"#ff6b85"),
      title("市場廣度：站上 20 / 60 日均線比例",.497,"#67e8f9"),
      title("大盤整體維持率（證交所口徑）　紅線 130% 追繳・黃線 150% 警戒",.252,"#5eead4"),
    ],
  }, {responsive:true, scrollZoom:true, displayModeBar:false});
}

function render(){ buildBtns(); renderHero(); renderStats(); renderChart(); }

document.getElementById("updBadge").textContent =
  `資料更新至 ${META.latestPretty}　｜　共 ${fmt(META.days)} 個交易日　｜　每交易日自動更新`;
document.getElementById("metaTable").innerHTML =
  `<tr><th>項目</th><th>內容</th></tr>`+
  `<tr><td>展示區間</td><td>${META.startPretty} ～ ${META.latestPretty}（${fmt(META.days)} 個交易日）</td></tr>`+
  `<tr><td>成本線暖機</td><td>另有 ${fmt(META.warmupDays)} 個交易日先行累積成本，不進圖表</td></tr>`+
  `<tr><td>納入統計的有融資標的</td><td>${fmt(META.totalStocks)} 檔（上市＋上櫃普通股，排除 ETF/ETN）</td></tr>`+
  `<tr><td>維持率計算基準</td><td>融資自備款 40%，即成本 × 0.6 為融資金額</td></tr>`+
  `<tr><td>頁面產出時間</td><td>${META.generated}</td></tr>`;
document.getElementById("footMeta").textContent =
  `資料來源：TWSE／TPEx 公開端點　｜　產出時間 ${META.generated}`;

render();
</script>
</body>
</html>
"""
