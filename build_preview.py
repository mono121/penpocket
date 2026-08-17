#!/usr/bin/env python3
"""_pens/*.md と assets/ から、1ファイルの見た目確認用 HTML を生成する。

Jekyll のビルドではない。Liquid は解釈せず、index.html / pen.html と同じ
マークアップを Python 側で組み立てているだけ。見た目とJSの挙動の確認用。
"""
import glob, html, json, os, yaml
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))

brands = yaml.safe_load(open(os.path.join(ROOT, "_data/brands.yml"), encoding="utf-8"))

pens = []
for path in sorted(glob.glob(os.path.join(ROOT, "_pens/*.md"))):
    raw = open(path, encoding="utf-8").read()
    _, front, body = raw.split("---", 2)
    d = yaml.safe_load(front)
    b = brands.get(d["brand"], {})
    d["brand_name"] = b.get("name", d["brand"])
    d["country"] = b.get("country", "不明")
    d["acquired"] = str(d["acquired"])
    note = body.strip()
    d["note"] = note
    d["slug"] = os.path.basename(path)[:-3]
    pens.append(d)

pens.sort(key=lambda p: p["acquired"], reverse=True)

css = open(os.path.join(ROOT, "assets/css/style.css"), encoding="utf-8").read()

try:
    import markdown
    _about_raw = open(os.path.join(ROOT, "about.md"), encoding="utf-8").read().split("---", 2)[2]
    about_html = markdown.markdown(_about_raw)
except Exception:
    _about_raw = open(os.path.join(ROOT, "about.md"), encoding="utf-8").read().split("---", 2)[2]
    paragraphs = [html.escape(p.strip()).replace("\n", "<br>") for p in _about_raw.split("\n\n") if p.strip()]
    about_html = "".join("<p>%s</p>" % p for p in paragraphs)

# index.html と同じく本数の多い順。同数は最初に現れた順で安定させる。
types = [t for t, _ in Counter(p["type"] for p in pens).most_common()]
brand_keys = [k for k, _ in Counter(p["brand"] for p in pens).most_common()]

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>筆記具コレクション — 見た目の確認</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600&family=Zen+Kaku+Gothic+New:wght@400;500&family=Roboto+Mono:wght@400&display=swap" rel="stylesheet">
<style>
{css}
.view[hidden] {{ display: none !important; }}
.preview-note {{
  background: var(--paper-raised); border: 1px solid var(--rule-strong); border-radius: 4px;
  padding: .7rem 1rem; margin: 1.5rem 0 0; font-family: var(--font-data);
  font-size: .72rem; color: var(--muted); line-height: 1.7;
  display: flex; gap: 1rem; align-items: center; justify-content: space-between; flex-wrap: wrap;
}}
</style>
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <h1 class="masthead__title">筆記具コレクション</h1>
    <p class="masthead__sub">万年筆・ボールペン・シャープペンシルの収集記録</p>
    <svg class="masthead__stroke" viewBox="0 0 1000 34" preserveAspectRatio="none" aria-hidden="true">
      <path d="M2 22 C 150 6 300 28 460 16 C 620 4 780 26 998 12 L 998 18 C 780 32 620 10 460 22 C 300 34 150 12 2 28 Z" fill="var(--ink-blue)" opacity="0.8"/>
    </svg>
    <nav class="nav">
      <a href="#" data-view="list" aria-current="page">一覧</a>
      <a href="#" data-view="stats">収集の傾向</a>
      <a href="#" data-view="about">このサイトについて</a>
    </nav>
    <p class="preview-note">
      <span>見た目の確認用に1ファイルへまとめたものです。実際のサイトは Jekyll が同じマークアップを生成します。</span>
    </p>
  </div>
</header>

<main>

<section class="view" id="view-list">
<div class="wrap">
  <section class="filters">
    <div class="filters__group" data-facet="type">
      <span class="filters__label" id="label-type">TYPE</span>
      <button type="button" class="filters__toggle" id="toggle-type"
              aria-expanded="true" aria-controls="chips-type" aria-labelledby="label-type toggle-type">
        <span class="filters__state"></span>
        <span class="filters__marker" aria-hidden="true">▾</span>
      </button>
      <div class="filters__chips" id="chips-type">
      {"".join(f'<button type="button" class="chip" data-facet="type" data-value="{t}" aria-pressed="false">{t}</button>' for t in types)}
      </div>
    </div>
    <div class="filters__group" data-facet="brand">
      <span class="filters__label" id="label-brand">BRAND</span>
      <button type="button" class="filters__toggle" id="toggle-brand"
              aria-expanded="true" aria-controls="chips-brand" aria-labelledby="label-brand toggle-brand">
        <span class="filters__state"></span>
        <span class="filters__marker" aria-hidden="true">▾</span>
      </button>
      <div class="filters__chips" id="chips-brand">
      {"".join(f'<button type="button" class="chip" data-facet="brand" data-value="{k}" aria-pressed="false">{brands.get(k, {}).get("name", k)}</button>' for k in brand_keys)}
      </div>
    </div>
    <div class="toolbar">
      <div class="toolbar__left">
        <p class="tally"><b id="tally-count">{len(pens)}</b> / {len(pens)} 点</p>
        <button type="button" class="reset" id="reset" hidden>絞り込みを解除</button>
      </div>
      <label class="tally">並び順
        <select class="sort" id="sort">
          <option value="acquired-desc">入手が新しい順</option>
          <option value="acquired-asc">入手が古い順</option>
          <option value="brand">ブランド順</option>
        </select>
      </label>
    </div>
  </section>
  <div class="ledger" id="ledger"></div>
</div>
</section>

<section class="view" id="view-detail" hidden><div class="wrap detail" id="detail-body"></div></section>

<section class="view" id="view-about" hidden>
<article class="page"><div class="wrap">
  <h2 class="page__title">このサイトについて</h2>
  <div class="note">{about_html}</div>
</div></article>
</section>

<section class="view" id="view-stats" hidden>
<div class="wrap stats">
  <p class="stats__summary" id="summary"></p>
  <div class="stats__grid">
    <section class="panel" id="p-type"><h2 class="panel__title">種類の内訳</h2><div class="panel__chart"><canvas id="chart-type"></canvas></div></section>
    <section class="panel" id="p-country"><h2 class="panel__title">国別の本数</h2><div class="panel__chart"><canvas id="chart-country"></canvas></div></section>
    <section class="panel panel--wide" id="p-brand">
      <div class="panel__heading">
        <h2 class="panel__title">ブランド別の本数</h2>
        <p class="panel__note">上位3ブランドと、全ブランドの順位</p>
      </div>
      <div class="brand-leaders" id="brand-leaders"></div>
      <ol class="brand-list" id="brand-list"></ol>
    </section>
    <section class="panel" id="p-tag"><h2 class="panel__title">タグの頻度</h2><div class="panel__chart"><canvas id="chart-tag"></canvas></div></section>
    <section class="panel" id="p-year"><h2 class="panel__title">入手した年</h2><div class="panel__chart"><canvas id="chart-year"></canvas></div></section>
    <section class="panel" id="p-cum"><h2 class="panel__title">累計本数の推移</h2><div class="panel__chart"><canvas id="chart-cum"></canvas></div></section>
  </div>
</div>
</section>

</main>

<footer class="foot"><div class="wrap">所蔵 {len(pens)} 点</div></footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const PENS = {json.dumps(pens, ensure_ascii=False)};
</script>
<script>
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));

const ledger = document.getElementById('ledger');
ledger.innerHTML = PENS.map(p => `
  <a class="entry" href="#" data-slug="${{p.slug}}" data-type="${{esc(p.type)}}" data-brand="${{p.brand}}"
     data-brand-name="${{esc(p.brand_name)}}" data-acquired="${{p.acquired}}">
    <p class="entry__name"><span class="entry__title">${{esc(p.title)}}</span><span class="entry__brand">${{esc(p.brand_name)}}</span></p>
    <div class="entry__meta">
      <p class="entry__spec"><span class="entry__type">${{esc(p.type)}}</span>${{p.nib ? `<span class="entry__nib">${{esc(p.nib)}}</span>` : ''}}${{p.line_width ? `<span class="entry__nib">${{p.line_width}}mm</span>` : ''}}${{p.mechanism ? `<span class="entry__mech">${{esc(p.mechanism)}}</span>` : ''}}</p>
      ${{(p.tags||[]).length ? `<p class="entry__tags">${{(p.tags||[]).map(t=>`<span>${{esc(t)}}</span>`).join('')}}</p>` : ''}}
    </div>
  </a>`).join('') + `<p class="empty" id="empty"${{PENS.length ? ' hidden' : ''}}>${{PENS.length ? '条件に合う筆記具はありません。絞り込みを外してください。' : 'まだ筆記具が登録されていません。'}}</p>`;

const entries = [...ledger.querySelectorAll('.entry')];
const empty = document.getElementById('empty');
const tally = document.getElementById('tally-count');
const active = {{ type: [], brand: [] }};

function apply() {{
  let shown = 0;
  entries.forEach(e => {{
    const ok = Object.keys(active).every(f => !active[f].length || active[f].includes(e.dataset[f]));
    e.hidden = !ok;
    if (ok) shown++;
  }});
  tally.textContent = shown;
  empty.hidden = PENS.length === 0 ? false : shown !== 0;
  heads();
}}

const groups = [...document.querySelectorAll('.filters__group')];
const resetButton = document.getElementById('reset');
const narrow = window.matchMedia('(max-width: 640px)');

function heads() {{
  groups.forEach(group => {{
    const state = group.querySelector('.filters__state');
    if (!state) return;
    const chosen = active[group.dataset.facet] || [];
    const total = group.querySelectorAll('.chip').length;
    state.textContent = chosen.length ? chosen.length + '件選択' : total + '件';
  }});
  if (resetButton) resetButton.hidden = !Object.keys(active).some(f => active[f].length);
}}

function setOpen(group, open) {{
  const toggle = group.querySelector('.filters__toggle');
  const box = group.querySelector('.filters__chips');
  if (!toggle || !box) return;
  toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  box.hidden = !open;
}}

// 狭い画面では未選択のグループを畳む。選択中のものは開いたまま。
function syncGroups() {{
  groups.forEach(group => {{
    const chosen = active[group.dataset.facet] || [];
    setOpen(group, !narrow.matches || chosen.length > 0);
  }});
}}

groups.forEach(group => {{
  const toggle = group.querySelector('.filters__toggle');
  if (toggle) toggle.addEventListener('click', () => setOpen(group, toggle.getAttribute('aria-expanded') !== 'true'));
}});

if (resetButton) resetButton.addEventListener('click', () => {{
  Object.keys(active).forEach(f => {{ active[f].length = 0; }});
  document.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', 'false'));
  apply();
}});

narrow.addEventListener('change', syncGroups);

document.querySelectorAll('.chip').forEach(chip => chip.addEventListener('click', () => {{
  const list = active[chip.dataset.facet];
  const at = list.indexOf(chip.dataset.value);
  at === -1 ? list.push(chip.dataset.value) : list.splice(at, 1);
  chip.setAttribute('aria-pressed', at === -1);
  apply();
}}));

const cmp = {{
  'acquired-desc': (a,b) => b.dataset.acquired - a.dataset.acquired,
  'acquired-asc':  (a,b) => a.dataset.acquired - b.dataset.acquired,
  'brand':         (a,b) => a.dataset.brandName.localeCompare(b.dataset.brandName, 'ja')
}};
document.getElementById('sort').addEventListener('change', e => {{
  entries.slice().sort(cmp[e.target.value]).forEach(n => ledger.insertBefore(n, empty));
}});

function show(view) {{
  ['list','detail','stats','about'].forEach(v => document.getElementById('view-' + v).hidden = v !== view);
  document.querySelectorAll('.nav a').forEach(a => a.toggleAttribute('aria-current', a.dataset.view === view));
  window.scrollTo(0, 0);
}}
document.querySelectorAll('.nav a').forEach(a => a.addEventListener('click', e => {{
  e.preventDefault(); show(a.dataset.view); if (a.dataset.view === 'stats') drawCharts();
}}));

const row = (k, v) => v ? `<div class="specs__row"><dt class="specs__key">${{k}}</dt><dd style="margin:0">${{esc(v)}}</dd></div>` : '';
entries.forEach(e => e.addEventListener('click', ev => {{
  ev.preventDefault();
  const p = PENS.find(x => x.slug === e.dataset.slug);
  document.getElementById('detail-body').innerHTML = `
    <a class="detail__back" href="#" onclick="event.preventDefault();document.querySelector('.nav a').click()">&larr; 一覧に戻る</a>
    <h2 class="detail__title">${{esc(p.title)}}</h2>
    <p class="detail__brand">${{esc(p.brand_name)}} — ${{esc(p.country)}}</p>
    <dl class="specs">
      ${{row('種類', p.type)}}${{row('カラー', p.color)}}${{row('字幅・ペン先', p.nib)}}${{row('芯径・線幅', p.line_width ? p.line_width + ' mm' : '')}}
      ${{row('機構', p.mechanism)}}${{row('軸・外装', p.body)}}${{row('限定数', p.limited)}}${{row('記念内容', p.commemoration)}}
      ${{row('付属品', (p.accessories || []).join(' / '))}}${{row('インク・芯', p.ink_name)}}
      ${{row('入手', p.acquired + '年')}}${{row('タグ', (p.tags || []).join(' / '))}}
      ${{(p.custom_fields || []).map(x => row(x.label, x.value)).join('')}}
    </dl>
    <div class="note"><p>${{esc(p.note).replace(/\\n/g, '<br>')}}</p></div>`;
  show('detail');
}}));

let drawn = false;
function drawCharts() {{
  if (drawn) return; drawn = true;
  const css = getComputedStyle(document.documentElement), v = n => css.getPropertyValue(n).trim();
  Chart.defaults.color = v('--muted');
  Chart.defaults.borderColor = v('--rule');
  Chart.defaults.font.family = '"Roboto Mono", monospace';
  Chart.defaults.font.size = 11;
  const blue = v('--ink-blue'), acc2 = v('--accent-2'), muted = v('--muted'), ink = v('--ink'), rule = v('--rule');

  const tallyBy = (rows, pick) => rows.reduce((a,p) => {{
    const k = typeof pick === 'function' ? pick(p) : p[pick];
    if (k === null || k === undefined || k === '') return a;
    a[k] = (a[k]||0)+1; return a;
  }}, {{}});
  const pairs = (o, byVal) => Object.entries(o)
    .sort((a,b) => byVal ? b[1]-a[1] : String(a[0]).localeCompare(String(b[0]), 'ja'));
  const panel = (id, ok) => {{ const el = document.getElementById(id); if (el && !ok) el.hidden = true; return ok; }};

  const bar = (cid, pid, ps, color, horiz) => {{
    if (!panel(pid, ps.length > 0)) return;
    const canvas = document.getElementById(cid);
    if (horiz && canvas && canvas.parentElement) {{
      // 横棒グラフは項目数に応じて高さを確保し、ラベルの自動省略を防ぐ。
      canvas.parentElement.style.height = Math.max(260, ps.length * 28 + 32) + 'px';
    }}
    new Chart(canvas, {{
      type: 'bar',
      data: {{ labels: ps.map(p=>p[0]), datasets: [{{ data: ps.map(p=>p[1]), backgroundColor: color, borderRadius: 2, barPercentage: .7 }}] }},
      options: {{ indexAxis: horiz ? 'y' : 'x', maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }},
        scales: {{ x: {{ grid: {{ display: !horiz }}, ticks: {{ precision: 0 }} }}, y: {{ grid: {{ display: horiz }}, ticks: {{ precision: 0, autoSkip: horiz ? false : undefined }} }} }} }}
    }});
  }};

  const brandRanking = ps => {{
    if (!panel('p-brand', ps.length > 0)) return;
    const leaders = document.getElementById('brand-leaders');
    const list = document.getElementById('brand-list');
    leaders.innerHTML = ps.slice(0, 3).map((p, i) => `
      <div class="brand-leader">
        <span class="brand-leader__rank">${{String(i + 1).padStart(2, '0')}}</span>
        <span class="brand-leader__name" title="${{esc(p[0])}}">${{esc(p[0])}}</span>
        <span class="brand-leader__count"><b>${{p[1]}}</b><small>本</small></span>
      </div>`).join('');
    list.innerHTML = ps.slice(3).map((p, i) => `
      <li class="brand-list__item">
        <span class="brand-list__rank">${{String(i + 4).padStart(2, '0')}}</span>
        <span class="brand-list__name" title="${{esc(p[0])}}">${{esc(p[0])}}</span>
        <span class="brand-list__count">${{p[1]}}</span>
      </li>`).join('');
  }};

  const dough = (cid, pid, ps) => {{
    if (!panel(pid, ps.length > 0)) return;
    new Chart(document.getElementById(cid), {{
      type: 'doughnut',
      data: {{ labels: ps.map(p=>p[0]), datasets: [{{ data: ps.map(p=>p[1]), backgroundColor: [blue, acc2, muted, ink, rule], borderWidth: 0 }}] }},
      options: {{ maintainAspectRatio: false, cutout: '62%', plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 10, padding: 14 }} }} }} }}
    }});
  }};

  dough('chart-type', 'p-type', pairs(tallyBy(PENS,'type'), true));
  brandRanking(pairs(tallyBy(PENS,'brand_name'), true));
  dough('chart-country', 'p-country', pairs(tallyBy(PENS,'country'), true));

  const tagCounts = PENS.reduce((a,p) => {{ (p.tags||[]).forEach(t => a[t]=(a[t]||0)+1); return a; }}, {{}});
  bar('chart-tag', 'p-tag', pairs(tagCounts, true), acc2, true);

  const byYear = pairs(tallyBy(PENS,'acquired'), false);
  bar('chart-year', 'p-year', byYear, blue, false);

  let cum = [], running = 0;
  if (byYear.length) {{
    const lookup = Object.fromEntries(byYear);
    for (let y = Number(byYear[0][0]); y <= Number(byYear[byYear.length-1][0]); y++) {{
      running += lookup[y] || 0; cum.push([String(y), running]);
    }}
  }}
  if (panel('p-cum', cum.length > 1)) {{
    new Chart(document.getElementById('chart-cum'), {{
      type: 'line',
      data: {{ labels: cum.map(p=>p[0]), datasets: [{{ data: cum.map(p=>p[1]),
        borderColor: blue, backgroundColor: blue, borderWidth: 2, pointRadius: 3, tension: .15, fill: false }}] }},
      options: {{ maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }},
        scales: {{ y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }} }} }}
    }});
  }}

  const years = PENS.map(p=>Number(p.acquired)).filter(Boolean);
  document.getElementById('summary').innerHTML = [
    ['所蔵', PENS.length + ' 点'],
    ['ブランド', Object.keys(tallyBy(PENS,'brand_name')).length + ' 社'],
    ['種類', Object.keys(tallyBy(PENS,'type')).length + ' 分類'],
    ['期間', years.length ? Math.min(...years) + '–' + Math.max(...years) : '—']
  ].map(p => p[0] + ' <b>' + p[1] + '</b>').join('');
}}

apply();
syncGroups();
</script>
</body>
</html>
"""

out = os.path.join(ROOT, "preview.html")
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, len(html), "bytes,", len(pens), "pens")
