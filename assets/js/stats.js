(function () {
  var css = getComputedStyle(document.documentElement);
  var v = function (n) { return css.getPropertyValue(n).trim(); };
  var ink = v('--ink'), muted = v('--muted'), rule = v('--rule');
  var blue = v('--ink-blue'), accent2 = v('--accent-2');

  Chart.defaults.color = muted;
  Chart.defaults.borderColor = rule;
  Chart.defaults.font.family = '"Roboto Mono", monospace';
  Chart.defaults.font.size = 11;

  function tally(rows, pick) {
    return rows.reduce(function (acc, row) {
      var k = typeof pick === 'function' ? pick(row) : row[pick];
      if (k === null || k === undefined || k === '') return acc;
      acc[k] = (acc[k] || 0) + 1;
      return acc;
    }, {});
  }

  // byValue: 件数の多い順。false なら見出しの昇順。
  function pairs(counts, byValue) {
    return Object.keys(counts)
      .map(function (k) { return [k, counts[k]]; })
      .sort(function (a, b) { return byValue ? b[1] - a[1] : String(a[0]).localeCompare(String(b[0]), 'ja'); });
  }

  // データが空のパネルは丸ごと隠す（万年筆が0本ならペン先の欄は出さない等）
  function panel(id, ok) {
    var el = document.getElementById(id);
    if (el && !ok) el.hidden = true;
    return ok;
  }

  function bar(canvasId, panelId, ps, color, horizontal) {
    if (!panel(panelId, ps.length > 0)) return;
    var canvas = document.getElementById(canvasId);
    if (horizontal && canvas && canvas.parentElement) {
      // 横棒グラフは項目数に応じて高さを確保し、ラベルの自動省略を防ぐ。
      canvas.parentElement.style.height = Math.max(260, ps.length * 28 + 32) + 'px';
    }
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ps.map(function (p) { return p[0]; }),
        datasets: [{ data: ps.map(function (p) { return p[1]; }), backgroundColor: color, borderRadius: 2, barPercentage: 0.7 }]
      },
      options: {
        indexAxis: horizontal ? 'y' : 'x',
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: !horizontal }, ticks: { precision: 0 } },
          y: { grid: { display: horizontal }, ticks: { precision: 0, autoSkip: horizontal ? false : undefined } }
        }
      }
    });
  }


  var TOP_BRANDS = 10;

  function brandRanking(ps) {
    if (!panel('p-brand', ps.length > 0)) return;

    var leaders = document.getElementById('brand-leaders');
    var list = document.getElementById('brand-list');
    if (!leaders || !list) return;

    leaders.innerHTML = ps.slice(0, 3).map(function (p, i) {
      return '<div class="brand-leader">' +
        '<span class="brand-leader__rank">' + String(i + 1).padStart(2, '0') + '</span>' +
        '<span class="brand-leader__name" title="' + p[0] + '">' + p[0] + '</span>' +
        '<span class="brand-leader__count"><b>' + p[1] + '</b><small>本</small></span>' +
      '</div>';
    }).join('');

    // 上位10まで。残りは1〜2本のブランドが並ぶだけで順位として読む意味が薄い。
    list.innerHTML = ps.slice(3, TOP_BRANDS).map(function (p, i) {
      return '<li class="brand-list__item">' +
        '<span class="brand-list__rank">' + String(i + 4).padStart(2, '0') + '</span>' +
        '<span class="brand-list__name" title="' + p[0] + '">' + p[0] + '</span>' +
        '<span class="brand-list__count">' + p[1] + '</span>' +
      '</li>';
    }).join('');

    // 打ち切ったことを黙って隠さず、残りの数を書いておく
    var rest = document.getElementById('brand-rest');
    if (rest) {
      var omitted = ps.length - TOP_BRANDS;
      rest.hidden = omitted <= 0;
      rest.textContent = omitted > 0 ? 'ほか ' + omitted + ' ブランド' : '';
    }
  }

  function doughnut(canvasId, panelId, ps) {
    if (!panel(panelId, ps.length > 0)) return;
    new Chart(document.getElementById(canvasId), {
      type: 'doughnut',
      data: {
        labels: ps.map(function (p) { return p[0]; }),
        datasets: [{ data: ps.map(function (p) { return p[1]; }), backgroundColor: [blue, accent2, muted, ink, rule], borderWidth: 0 }]
      },
      options: {
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 14 } } }
      }
    });
  }

  fetch((window.SITE_BASEURL || '') + '/pens.json')
    .then(function (res) { return res.json(); })
    .then(function (pens) {

      doughnut('chart-type', 'p-type', pairs(tally(pens, 'type'), true));
      brandRanking(pairs(tally(pens, 'brand_name'), true));
      doughnut('chart-country', 'p-country', pairs(tally(pens, 'country'), true));

      var tagCounts = pens.reduce(function (acc, p) {
        (p.tags || []).forEach(function (t) { acc[t] = (acc[t] || 0) + 1; });
        return acc;
      }, {});
      bar('chart-tag', 'p-tag', pairs(tagCounts, true), accent2, true);

      var byYear = pairs(tally(pens, 'acquired'), false);
      bar('chart-year', 'p-year', byYear, blue, false);

      // 累計。間の空白年も埋めて、増えていない期間が見えるようにする
      var cum = [], running = 0;
      if (byYear.length) {
        var first = Number(byYear[0][0]), last = Number(byYear[byYear.length - 1][0]);
        var lookup = byYear.reduce(function (a, p) { a[p[0]] = p[1]; return a; }, {});
        for (var y = first; y <= last; y++) {
          running += lookup[y] || 0;
          cum.push([String(y), running]);
        }
      }
      if (panel('p-cum', cum.length > 1)) {
        new Chart(document.getElementById('chart-cum'), {
          type: 'line',
          data: {
            labels: cum.map(function (p) { return p[0]; }),
            datasets: [{
              data: cum.map(function (p) { return p[1]; }),
              borderColor: blue, backgroundColor: blue,
              borderWidth: 2, pointRadius: 3, tension: 0.15, fill: false
            }]
          },
          options: {
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
          }
        });
      }

      var years = pens.map(function (p) { return p.acquired; }).filter(Boolean);
      var summary = document.getElementById('summary');
      if (summary) {
        var span = years.length ? Math.min.apply(null, years) + '–' + Math.max.apply(null, years) : '—';
        summary.innerHTML = [
          ['所蔵', pens.length + ' 点'],
          ['ブランド', Object.keys(tally(pens, 'brand_name')).length + ' 社'],
          ['種類', Object.keys(tally(pens, 'type')).length + ' 分類'],
          ['期間', span]
        ].map(function (p) { return p[0] + ' <b>' + p[1] + '</b>'; }).join('');
      }
    })
    .catch(function (err) {
      console.error('pens.json を読み込めませんでした', err);
    });
})();
