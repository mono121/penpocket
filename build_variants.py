#!/usr/bin/env python3
"""同じデータで、一覧UIの方向性を3案つくる。

candidate-1-catalog.html  カタログ型（カード格子）
candidate-2-table.html    表型（高密度）
candidate-3-gallery.html  図録型（余白広め）

比較しやすいよう、各案は「ヘッダ + 絞り込み + 一覧」だけに絞ってある。
詳細ページ・統計・並び替えは共通なので入れていない。
"""
import glob, json, os, yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
brands = yaml.safe_load(open(os.path.join(ROOT, "_data/brands.yml"), encoding="utf-8"))

pens = []
for path in sorted(glob.glob(os.path.join(ROOT, "_pens/*.md"))):
    _, front, _ = open(path, encoding="utf-8").read().split("---", 2)
    d = yaml.safe_load(front)
    b = brands.get(d["brand"], {})
    d["brand_name"] = b.get("name", d["brand"])
    d["acquired"] = str(d["acquired"])
    pens.append(d)
pens.sort(key=lambda p: p["acquired"], reverse=True)

types = sorted({p["type"] for p in pens})
brand_keys = list(dict.fromkeys(p["brand"] for p in pens))
DATA = json.dumps(pens, ensure_ascii=False)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600'
         '&family=Zen+Kaku+Gothic+New:wght@400;500&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">')

# 各案の絞り込みロジックは共通。描画だけ render() で差し替える。
SCRIPT = """
const PENS = %s;
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const active = { type: [], brand: [] };
const listEl = document.getElementById('list');
const countEl = document.getElementById('count');

function visible() {
  return PENS.filter(p => Object.keys(active).every(f => {
    const chosen = active[f];
    const val = f === 'brand' ? p.brand : p[f];
    return !chosen.length || chosen.includes(val);
  }));
}
function paint() {
  const rows = visible();
  countEl.textContent = rows.length;
  listEl.innerHTML = rows.length ? render(rows) : '<p class="empty">条件に合う筆記具はありません。</p>';
  if (typeof afterPaint === 'function') afterPaint();
}
document.querySelectorAll('.chip').forEach(chip => chip.addEventListener('click', () => {
  const list = active[chip.dataset.facet];
  const at = list.indexOf(chip.dataset.value);
  at === -1 ? list.push(chip.dataset.value) : list.splice(at, 1);
  chip.setAttribute('aria-pressed', String(at === -1));
  paint();
}));
paint();
"""


def chips():
    a = "".join(
        '<button type="button" class="chip" data-facet="type" data-value="%s" aria-pressed="false">%s</button>' % (t, t)
        for t in types)
    b = "".join(
        '<button type="button" class="chip" data-facet="brand" data-value="%s" aria-pressed="false">%s</button>'
        % (k, brands.get(k, {}).get("name", k)) for k in brand_keys)
    return a, b


def page(name, label, blurb, css, body, render_js):
    a, b = chips()
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{label} — 筆記具コレクション</title>{FONTS}
<style>{css}</style></head><body>
<div class="banner">{label}　<span>{blurb}</span></div>
{body.replace('__CHIPS_TYPE__', a).replace('__CHIPS_BRAND__', b).replace('__COUNT__', str(len(pens)))}
<script>{render_js}</script>
<script>{SCRIPT % DATA}</script>
</body></html>"""


BANNER = """
.banner{font-family:"Roboto Mono",monospace;font-size:11px;letter-spacing:.1em;padding:.55rem 1.5rem;
background:var(--accent);color:#fff;position:sticky;top:0;z-index:9}
.banner span{opacity:.75;letter-spacing:.04em}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;-webkit-font-smoothing:antialiased}
[hidden]{display:none!important}
.wrap{max-width:1040px;margin:0 auto;padding:0 1.5rem}
.empty{color:var(--muted);padding:3rem 0}
"""

# ---------------------------------------------------------------- 候補1 カタログ型
CSS1 = BANNER + """
:root{--bg:#edeeef;--card:#fff;--line:#dcdee0;--ink:#16181b;--muted:#6b7075;--accent:#2f5d50}
body{background:var(--bg);color:var(--ink);font-family:"Zen Kaku Gothic New",sans-serif;font-size:15px;line-height:1.7}
.head{padding:3rem 0 1.5rem}
.head h1{font-size:1.5rem;font-weight:500;letter-spacing:.08em;margin:0}
.head p{color:var(--muted);font-size:.8rem;margin:.3rem 0 0}
.bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;padding:1rem 0;border-top:1px solid var(--line)}
.bar b{font-family:"Roboto Mono",monospace;font-size:.7rem;letter-spacing:.14em;color:var(--muted);font-weight:400;margin-right:.4rem}
.chip{font:inherit;font-size:.8rem;background:var(--card);color:var(--ink);border:1px solid var(--line);
 border-radius:3px;padding:.2rem .7rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.tally{font-family:"Roboto Mono",monospace;font-size:.75rem;color:var(--muted);padding:.2rem 0 1rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(238px,1fr));gap:1rem;padding-bottom:4rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:1rem 1.1rem}
.card h2{font-size:1rem;font-weight:500;margin:0;line-height:1.4}
.card .brand{font-family:"Roboto Mono",monospace;font-size:.68rem;letter-spacing:.12em;color:var(--accent);
 text-transform:uppercase;display:block;margin-bottom:.5rem}
.spec{display:grid;grid-template-columns:4.2rem 1fr;gap:.15rem .6rem;margin-top:.8rem;padding-top:.7rem;
 border-top:1px solid var(--line);font-family:"Roboto Mono",monospace;font-size:.7rem;color:var(--muted)}
.spec i{font-style:normal;color:#9aa0a5}
"""
BODY1 = """<header class="head"><div class="wrap"><h1>筆記具コレクション</h1>
<p>万年筆・ボールペン・シャープペンシルの収集記録</p></div></header>
<div class="wrap">
<div class="bar"><b>TYPE</b>__CHIPS_TYPE__</div>
<div class="bar"><b>BRAND</b>__CHIPS_BRAND__</div>
<p class="tally"><span id="count">__COUNT__</span> 点</p>
<div class="grid" id="list"></div></div>"""
RENDER1 = """
function render(rows){return rows.map(p=>`
<article class="card">
  <span class="brand">${esc(p.brand)}</span>
  <h2>${esc(p.title)}</h2>
  <div class="spec">
    <i>種類</i><span>${esc(p.type)}</span>
    ${p.nib?`<i>ペン先</i><span>${esc(p.nib)}</span>`:''}
    <i>線幅</i><span>${p.line_width} mm</span>
    <i>機構</i><span>${esc(p.mechanism)}</span>
    <i>入手</i><span>${p.acquired}</span>
  </div>
</article>`).join('')}
"""

# ---------------------------------------------------------------- 候補2 表型
CSS2 = BANNER + """
:root{--bg:#fafaf9;--zebra:#f2f2f0;--line:#e0e0dc;--ink:#1a1c1e;--muted:#75797d;--accent:#1f4fa3}
body{background:var(--bg);color:var(--ink);font-family:"Zen Kaku Gothic New",sans-serif;font-size:14px;line-height:1.6}
.head{padding:2.5rem 0 1rem}
.head h1{font-size:1.3rem;font-weight:500;letter-spacing:.08em;margin:0}
.bar{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;padding:.5rem 0}
.bar b{font-family:"Roboto Mono",monospace;font-size:.68rem;letter-spacing:.14em;color:var(--muted);font-weight:400;width:4.5rem}
.chip{font-family:"Roboto Mono",monospace;font-size:.72rem;background:transparent;color:var(--ink);
 border:1px solid var(--line);border-radius:2px;padding:.15rem .55rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.tally{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);margin:.8rem 0 .4rem}
table{width:100%;border-collapse:collapse;margin-bottom:4rem}
thead th{position:sticky;top:29px;background:var(--bg);text-align:left;font-family:"Roboto Mono",monospace;
 font-size:.66rem;font-weight:500;letter-spacing:.12em;color:var(--muted);padding:.5rem .6rem;
 border-bottom:1px solid var(--ink)}
td{padding:.42rem .6rem;border-bottom:1px solid var(--line);white-space:nowrap;
 overflow:hidden;text-overflow:ellipsis}
tbody tr:nth-child(even){background:var(--zebra)}
td.num{font-family:"Roboto Mono",monospace;text-align:right;color:var(--muted)}
td.mono{font-family:"Roboto Mono",monospace;color:var(--muted);font-size:.78rem}
td.name{font-weight:500}
td.brand{color:var(--accent);font-size:.8rem}
"""
BODY2 = """<header class="head"><div class="wrap"><h1>筆記具コレクション</h1>
<div class="bar"><b>TYPE</b>__CHIPS_TYPE__</div>
<div class="bar"><b>BRAND</b>__CHIPS_BRAND__</div>
<p class="tally"><span id="count">__COUNT__</span> 点</p></div></header>
<div class="wrap" id="list"></div>"""
RENDER2 = """
function render(rows){return `<table><thead><tr>
<th>名前</th><th>ブランド</th><th>種類</th><th>ペン先</th><th style="text-align:right">線幅</th><th>機構</th><th style="text-align:right">入手</th>
</tr></thead><tbody>${rows.map(p=>`<tr>
<td class="name">${esc(p.title)}</td>
<td class="brand">${esc(p.brand_name)}</td>
<td class="mono">${esc(p.type)}</td>
<td class="mono">${esc(p.nib||'—')}</td>
<td class="num">${p.line_width}</td>
<td class="mono">${esc(p.mechanism)}</td>
<td class="num">${p.acquired}</td>
</tr>`).join('')}</tbody></table>`}
"""

# ---------------------------------------------------------------- 候補3 図録型
CSS3 = BANNER + """
:root{--bg:#e9ebe6;--line:#c9cdc3;--ink:#212420;--muted:#666b63;--accent:#3a4a3f}
body{background:var(--bg);color:var(--ink);font-family:"Zen Kaku Gothic New",sans-serif;font-size:15px;line-height:1.9}
.head{padding:5rem 0 2rem}
.head h1{font-family:"Shippori Mincho",serif;font-size:clamp(1.8rem,5vw,2.6rem);font-weight:600;
 letter-spacing:.14em;margin:0}
.head p{color:var(--muted);font-size:.82rem;letter-spacing:.1em;margin:.6rem 0 0}
.bar{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;padding:.5rem 0}
.bar b{font-family:"Roboto Mono",monospace;font-size:.66rem;letter-spacing:.18em;color:var(--muted);font-weight:400;width:5rem}
.chip{font:inherit;font-size:.8rem;background:transparent;color:var(--ink);border:1px solid var(--line);
 border-radius:999px;padding:.2rem .9rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.tally{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);margin:1.5rem 0 0;
 padding-top:1.2rem;border-top:1px solid var(--line)}
.item{display:grid;grid-template-columns:minmax(0,1fr) 15rem;gap:2rem;align-items:baseline;
 padding:2.4rem .2rem;border-bottom:1px solid var(--line)}
.item:last-child{margin-bottom:4rem}
.item h2{font-family:"Shippori Mincho",serif;font-size:1.5rem;font-weight:600;letter-spacing:.06em;
 margin:0;line-height:1.45}
.item .brand{display:block;font-family:"Roboto Mono",monospace;font-size:.68rem;letter-spacing:.16em;
 color:var(--muted);text-transform:uppercase;margin-bottom:.5rem}
.item dl{margin:0;font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);
 display:grid;grid-template-columns:4.5rem 1fr;gap:.2rem .8rem}
.item dt{color:#9aa096}.item dd{margin:0}
@media(max-width:720px){.item{grid-template-columns:minmax(0,1fr);gap:1.2rem}}
"""
BODY3 = """<header class="head"><div class="wrap"><h1>筆記具コレクション</h1>
<p>万年筆・ボールペン・シャープペンシルの収集記録</p>
<div class="bar" style="margin-top:2.5rem"><b>TYPE</b>__CHIPS_TYPE__</div>
<div class="bar"><b>BRAND</b>__CHIPS_BRAND__</div>
<p class="tally">所蔵 <span id="count">__COUNT__</span> 点</p></div></header>
<div class="wrap" id="list"></div>"""
RENDER3 = """
function render(rows){return rows.map(p=>`
<article class="item">
  <div><span class="brand">${esc(p.brand)}</span><h2>${esc(p.title)}</h2></div>
  <dl>
    <dt>種類</dt><dd>${esc(p.type)}</dd>
    ${p.nib?`<dt>ペン先</dt><dd>${esc(p.nib)}</dd>`:''}
    <dt>線幅</dt><dd>${p.line_width} mm</dd>
    <dt>機構</dt><dd>${esc(p.mechanism)}</dd>
    <dt>入手</dt><dd>${p.acquired}年</dd>
  </dl>
</article>`).join('')}
"""

# ---------------------------------------------------------------- 候補4 索引型
CSS4 = BANNER + """
:root{--bg:#fff;--line:#e8e8e4;--ink:#1c1a1d;--muted:#78747a;--accent:#8a3b4f}
body{background:var(--bg);color:var(--ink);font-family:"Zen Kaku Gothic New",sans-serif;font-size:14px;line-height:1.7}
.head{padding:3.5rem 0 1rem}
.head h1{font-family:"Shippori Mincho",serif;font-size:1.7rem;font-weight:600;letter-spacing:.1em;margin:0}
.bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;padding:.4rem 0}
.bar b{font-family:"Roboto Mono",monospace;font-size:.66rem;letter-spacing:.16em;color:var(--muted);font-weight:400;width:4.5rem}
.chip{font:inherit;font-size:.78rem;background:transparent;color:var(--ink);border:1px solid var(--line);
 border-radius:2px;padding:.18rem .7rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.tally{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);margin:1rem 0 0}
.group{margin-bottom:2.5rem}
.ghead{font-family:"Shippori Mincho",serif;font-size:1.15rem;font-weight:600;letter-spacing:.08em;
 margin:0 0 .3rem;padding:.5rem 0 .4rem;border-bottom:2px solid var(--accent);position:sticky;top:29px;background:var(--bg);
 display:flex;justify-content:space-between;align-items:baseline}
.ghead span{font-family:"Roboto Mono",monospace;font-size:.7rem;color:var(--muted);font-weight:400}
.rows{list-style:none;margin:0;padding:0}
.rows li{display:grid;grid-template-columns:minmax(0,13rem) minmax(0,1fr) 3rem;gap:1rem;align-items:baseline;
 padding:.5rem .2rem;border-bottom:1px solid var(--line)}
.rows .nm{font-weight:500}
.rows .sp{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rows .yr{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);text-align:right}
#list{padding-bottom:4rem}
@media(max-width:640px){.rows li{grid-template-columns:minmax(0,1fr) 3rem}.rows .sp{grid-column:1/3}}
"""
BODY4 = """<header class="head"><div class="wrap"><h1>筆記具コレクション</h1>
<div class="bar" style="margin-top:1.5rem"><b>TYPE</b>__CHIPS_TYPE__</div>
<div class="bar"><b>BRAND</b>__CHIPS_BRAND__</div>
<p class="tally"><span id="count">__COUNT__</span> 点</p></div></header>
<div class="wrap" id="list"></div>"""
RENDER4 = """
function render(rows){
  const g={}; rows.forEach(p=>(g[p.brand_name]=g[p.brand_name]||[]).push(p));
  return Object.keys(g).sort((a,b)=>a.localeCompare(b,'ja')).map(k=>`
  <section class="group">
    <h2 class="ghead">${esc(k)}<span>${g[k].length}</span></h2>
    <ul class="rows">${g[k].map(p=>`<li>
      <span class="nm">${esc(p.title)}</span>
      <span class="sp">${esc(p.type)}／${esc(p.nib||'—')}／${p.line_width}mm／${esc(p.mechanism)}</span>
      <span class="yr">${p.acquired}</span></li>`).join('')}</ul>
  </section>`).join('')}
"""

# ---------------------------------------------------------------- 候補5 年表型
CSS5 = BANNER + """
:root{--bg:#eff1f3;--card:#fff;--line:#d7dbe0;--ink:#181b1f;--muted:#6d747c;--accent:#2a4e6e}
body{background:var(--bg);color:var(--ink);font-family:"Zen Kaku Gothic New",sans-serif;font-size:14px;line-height:1.7}
.head{padding:3rem 0 1rem}
.head h1{font-size:1.4rem;font-weight:500;letter-spacing:.08em;margin:0}
.bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;padding:.4rem 0}
.bar b{font-family:"Roboto Mono",monospace;font-size:.66rem;letter-spacing:.16em;color:var(--muted);font-weight:400;width:4.5rem}
.chip{font:inherit;font-size:.78rem;background:var(--card);color:var(--ink);border:1px solid var(--line);
 border-radius:3px;padding:.18rem .7rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.tally{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);margin:1rem 0 1.5rem}
.yrow{display:grid;grid-template-columns:5.5rem minmax(0,1fr);gap:1.5rem;align-items:start}
.yr{font-family:"Roboto Mono",monospace;font-size:1.5rem;color:var(--accent);position:sticky;top:60px;
 padding-top:.9rem;letter-spacing:.02em}
.items{border-left:2px solid var(--line);padding:0 0 2.2rem 1.5rem;position:relative}
.it{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:.8rem 1rem;margin-bottom:.6rem;position:relative}
.it::before{content:"";position:absolute;left:-1.9rem;top:1.15rem;width:8px;height:8px;border-radius:50%;
 background:var(--accent)}
.it h3{font-size:.98rem;font-weight:500;margin:0}
.it .mt{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);margin:.25rem 0 0}
#list{padding-bottom:3rem}
@media(max-width:640px){.yrow{grid-template-columns:minmax(0,1fr);gap:.3rem}.yr{position:static;font-size:1.2rem}
 .items{padding-left:1.2rem}.it::before{left:-1.6rem}}
"""
BODY5 = """<header class="head"><div class="wrap"><h1>筆記具コレクション</h1>
<div class="bar" style="margin-top:1.2rem"><b>TYPE</b>__CHIPS_TYPE__</div>
<div class="bar"><b>BRAND</b>__CHIPS_BRAND__</div>
<p class="tally"><span id="count">__COUNT__</span> 点</p></div></header>
<div class="wrap" id="list"></div>"""
RENDER5 = """
function render(rows){
  const g={}; rows.forEach(p=>(g[p.acquired]=g[p.acquired]||[]).push(p));
  return Object.keys(g).sort((a,b)=>b-a).map(y=>`
  <section class="yrow">
    <div class="yr">${y}</div>
    <div class="items">${g[y].map(p=>`
      <div class="it"><h3>${esc(p.title)}</h3>
      <p class="mt">${esc(p.brand_name)}／${esc(p.type)}${p.nib?'／'+esc(p.nib):''}／${p.line_width}mm</p></div>`).join('')}</div>
  </section>`).join('')}
"""

# ---------------------------------------------------------------- 候補6 2ペイン型
CSS6 = BANNER + """
:root{--bg:#f5f5f3;--card:#fff;--line:#e2e2dd;--ink:#1a1c17;--muted:#727569;--accent:#4a5d23}
body{background:var(--bg);color:var(--ink);font-family:"Zen Kaku Gothic New",sans-serif;font-size:14px;line-height:1.7}
.head{padding:2.5rem 0 .8rem}
.head h1{font-size:1.35rem;font-weight:500;letter-spacing:.08em;margin:0}
.bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;padding:.35rem 0}
.bar b{font-family:"Roboto Mono",monospace;font-size:.66rem;letter-spacing:.16em;color:var(--muted);font-weight:400;width:4.5rem}
.chip{font:inherit;font-size:.78rem;background:var(--card);color:var(--ink);border:1px solid var(--line);
 border-radius:3px;padding:.18rem .7rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.tally{font-family:"Roboto Mono",monospace;font-size:.72rem;color:var(--muted);margin:.8rem 0}
.pane{display:grid;grid-template-columns:17rem minmax(0,1fr);gap:1.5rem;padding-bottom:4rem;align-items:start}
.side{list-style:none;margin:0;padding:0;border:1px solid var(--line);border-radius:5px;background:var(--card);
 max-height:66vh;overflow-y:auto}
.side li{padding:.55rem .9rem;border-bottom:1px solid var(--line);cursor:pointer}
.side li:last-child{border-bottom:0}
.side li:hover{background:var(--bg)}
.side li.on{background:var(--accent)}
.side li.on .nm,.side li.on .br{color:#fff}
.side .nm{display:block;font-weight:500}
.side .br{display:block;font-family:"Roboto Mono",monospace;font-size:.68rem;color:var(--muted);letter-spacing:.08em}
.detail{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:1.8rem 2rem;position:sticky;top:60px}
.detail .brand{font-family:"Roboto Mono",monospace;font-size:.68rem;letter-spacing:.16em;color:var(--accent);
 text-transform:uppercase}
.detail h2{font-size:1.4rem;font-weight:500;margin:.3rem 0 1.4rem}
.detail dl{margin:0;display:grid;grid-template-columns:5.5rem minmax(0,1fr);gap:.35rem 1rem;
 font-family:"Roboto Mono",monospace;font-size:.75rem}
.detail dt{color:var(--muted)}.detail dd{margin:0}
@media(max-width:760px){.pane{grid-template-columns:minmax(0,1fr)}.side{max-height:15rem}.detail{position:static}}
"""
BODY6 = """<header class="head"><div class="wrap"><h1>筆記具コレクション</h1>
<div class="bar" style="margin-top:1rem"><b>TYPE</b>__CHIPS_TYPE__</div>
<div class="bar"><b>BRAND</b>__CHIPS_BRAND__</div>
<p class="tally"><span id="count">__COUNT__</span> 点</p></div></header>
<div class="wrap" id="list"></div>"""
RENDER6 = """
function render(rows){
  return `<div class="pane">
    <ul class="side">${rows.map((p,i)=>`<li data-i="${i}">
      <span class="nm">${esc(p.title)}</span><span class="br">${esc(p.brand_name)}</span></li>`).join('')}</ul>
    <div class="detail" id="detail"></div></div>`;
}
function afterPaint(){
  const rows = visible();
  const side = document.querySelector('.side');
  if (!side) return;
  const row = (k,v) => v ? `<dt>${k}</dt><dd>${esc(v)}</dd>` : '';
  const show = i => {
    const p = rows[i];
    side.querySelectorAll('li').forEach(li => li.classList.toggle('on', Number(li.dataset.i) === i));
    document.getElementById('detail').innerHTML = `
      <span class="brand">${esc(p.brand)}</span>
      <h2>${esc(p.title)}</h2>
      <dl>${row('種類',p.type)}${row('ペン先',p.nib)}${row('線幅',p.line_width+' mm')}
      ${row('機構',p.mechanism)}${row('軸',p.body)}${row('インク・芯',p.ink_name)}
      ${row('入手',p.acquired+'年')}${row('タグ',(p.tags||[]).join(' / '))}</dl>`;
  };
  side.querySelectorAll('li').forEach(li => li.addEventListener('click', () => show(Number(li.dataset.i))));
  show(0);
}
"""

VARIANTS = [
    ("candidate-1-catalog.html", "候補1　カタログ型", "カード格子。1枚に全スペック。写真を足す枠が自然にある", CSS1, BODY1, RENDER1),
    ("candidate-2-table.html", "候補2　表型", "1行1本の表。100本でも一画面に多く入る。列で見比べられる", CSS2, BODY2, RENDER2),
    ("candidate-3-gallery.html", "候補3　図録型", "余白広め。1本ずつ大きく。所蔵数が少なくても間が持つ", CSS3, BODY3, RENDER3),
    ("candidate-4-index.html", "候補4　索引型", "ブランドごとに章分け。増えるほど構造が効く", CSS4, BODY4, RENDER4),
    ("candidate-5-timeline.html", "候補5　年表型", "入手年で時系列に。集めてきた経過が読める", CSS5, BODY5, RENDER5),
    ("candidate-6-twopane.html", "候補6　2ペイン型", "左に一覧、右に詳細。ページ遷移なしで次々見られる", CSS6, BODY6, RENDER6),
]

for fname, label, blurb, css, body, render_js in VARIANTS:
    out = os.path.join(ROOT, fname)
    open(out, "w", encoding="utf-8").write(page(fname, label, blurb, css, body, render_js))
    print("wrote", fname)
