// Shared helpers for the census review pages: navigation, formats, filters, chart frames and
// tooltips. Everything the pages share hangs on window.CR.
(function () {
  const CR = (window.CR = window.CR || {});
  const SVG = 'http://www.w3.org/2000/svg';

  // ---------------------------------------------------------------- navigation
  CR.pages = [...document.querySelectorAll('#dash-root .cr-page')].map((s) => s.id);
  const fromHash = () => {
    const h = (location.hash || '').slice(1);
    return CR.pages.includes(h) ? h : null;
  };
  CR.page = fromHash() || 'overview';
  CR.prev = 'overview';
  CR.syncPages = () => {
    document.querySelectorAll('#dash-root .cr-page').forEach((s) => {
      s.hidden = s.id !== CR.page;
    });
    document.querySelectorAll('#dash-root .cr-tab').forEach((t) => {
      const on = t.getAttribute('aria-controls') === CR.page;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
    });
  };
  CR.show = (page) => {
    if (!CR.pages.includes(page)) return;
    if (page !== CR.page && CR.page !== 'code') CR.prev = CR.page;
    CR.page = page;
    CR.syncPages();
    dash.setLink(page);
  };
  CR.openCode = (id) => {
    dash.setParams({ code: id });
    CR.show('code');
    const top = document.getElementById('code');
    if (top && top.scrollIntoView) top.scrollIntoView({ block: 'start' });
  };
  document.querySelectorAll('#dash-root .cr-tab').forEach((t) => {
    t.addEventListener('click', () => CR.show(t.getAttribute('aria-controls')));
  });
  dash.onData(CR.syncPages);

  // ---------------------------------------------------------------- data
  CR.get = (id) => dash.data(id);
  CR.ok = (...ids) => ids.every((id) => dash.data(id).status === 'ok');
  CR.failed = (...ids) => ids.some((id) => dash.data(id).status === 'error');
  CR.rows = (id) => {
    const g = dash.data(id);
    return g.status === 'ok' ? g.data : [];
  };
  CR.num = (x) => (x === null || x === undefined || x === '' ? null : +x);
  CR.bool = (x) => x === true || x === 'true';
  CR.metric = (rows, name) => rows.find((r) => r.metric === name) || {};

  // A drawing that waits on datasets: on any status but "ok" it shows its placeholder (a dash
  // for a value, nothing for a chart, one line for a failed load) and returns false.
  CR.ready = (el, ids, { chart = false } = {}) => {
    const st = ids.map((id) => dash.data(id).status);
    if (st.every((s) => s === 'ok')) {
      el.classList.remove('dash-skeleton');
      return true;
    }
    if (st.includes('error')) {
      el.classList.remove('dash-skeleton');
      el.replaceChildren(CR.failLine());
    } else if (chart) {
      el.replaceChildren();
    } else {
      el.textContent = '—';
    }
    return false;
  };
  CR.failLine = () => {
    const p = document.createElement('span');
    p.className = 'cr-fail';
    const dot = document.createElement('span');
    dot.className = 'cr-fail-dot';
    p.append(dot, document.createTextNode('Failed to load'));
    return p;
  };

  // ---------------------------------------------------------------- formats
  CR.fmt = {
    int: d3.format(','),
    compact: (x) =>
      Math.abs(x) >= 10000
        ? new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(x)
        : d3.format(',')(x),
    score: d3.format('.2f'),
    score1: d3.format('.1f'),
    ratio: d3.format('.3f'),
    pct: d3.format('.1%'),
    signed: d3.format('+.1f'),
    seconds: (s) => {
      if (s === null || s === undefined) return '—';
      if (s < 1) return d3.format('.2f')(s) + ' s';
      if (s < 120) return d3.format('.0f')(s) + ' s';
      if (s < 7200) return d3.format('.0f')(s / 60) + ' min';
      if (s < 172800) return d3.format('.1f')(s / 3600) + ' h';
      return d3.format('.1f')(s / 86400) + ' days';
    },
  };
  // A value drawing: one summary metric's field, formatted
  CR.metricDraw = (name, metric, field, format) => {
    dash.draw(name, (el) => {
      if (!CR.ready(el, ['summary'])) return;
      const v = CR.metric(CR.rows('summary'), metric)[field];
      el.textContent = v === null || v === undefined ? '—' : format ? format(v) : String(v);
    });
  };

  // ---------------------------------------------------------------- filters (Frontier page)
  CR.filtered = (rows, p = dash.params()) => {
    const nmin = CR.num(p.nmin);
    const nmax = CR.num(p.nmax);
    return rows.filter(
      (e) =>
        (p.stage === 'all' || !p.stage || e.stage === p.stage) &&
        (p.k === 'all' || p.k === null || p.k === undefined || +e.k === +p.k) &&
        (p.gtype === 'all' || !p.gtype || e.group_type === p.gtype) &&
        (nmin === null || +e.n >= nmin) &&
        (nmax === null || +e.n <= nmax) &&
        (!CR.bool(p.merge) || CR.bool(e.primary)),
    );
  };

  // ---------------------------------------------------------------- colour
  CR.GROUPS = ['cyclic', 'non-cyclic', 'Z3×Z3 part'];
  CR.STAGES = ['3a', '3b/3c', '4'];
  CR.colorOf = (e, by) => {
    const keys = by === 'stage' ? CR.STAGES : CR.GROUPS;
    const i = keys.indexOf(by === 'stage' ? e.stage : e.group_type);
    return dash.colors[Math.max(0, i)];
  };
  // a token's computed colour, for ramps (d3 can't read var())
  const probe = document.createElement('span');
  CR.resolve = (host, color) => {
    probe.style.color = color;
    host.append(probe);
    const c = getComputedStyle(probe).color;
    probe.remove();
    return c;
  };
  CR.ramp = (host, color) => {
    const lo = CR.resolve(host, 'var(--color-panel)');
    const hi = CR.resolve(host, color);
    const mix = d3.interpolateRgb(lo, hi);
    return (t) => mix(0.12 + 0.88 * Math.max(0, Math.min(1, t)));
  };
  CR.diverging = (host) => {
    const neg = CR.resolve(host, dash.colors[1]);
    const mid = CR.resolve(host, 'var(--cds-chart-muted)');
    const pos = CR.resolve(host, dash.colors[0]);
    const a = d3.interpolateRgb(neg, mid);
    const b = d3.interpolateRgb(mid, pos);
    return (t) => (t < 0 ? a(1 + Math.max(-1, t)) : b(Math.min(1, t)));
  };

  // ---------------------------------------------------------------- chart frames
  CR.svg = (el, width, height, label) => {
    const svg = d3
      .select(el)
      .append('svg')
      .attr('width', '100%')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('role', 'img')
      .attr('aria-label', label || '')
      .attr('class', 'cr-svg');
    return svg;
  };
  // the width of a label as drawn, in the svg's own text style
  CR.measure = (svg, strings, cls = 'cr-tick') => {
    const t = svg.append('text').attr('class', cls).attr('x', -9999).attr('y', -9999);
    let w = 0;
    for (const s of strings) {
      t.text(s);
      w = Math.max(w, t.node().getComputedTextLength());
    }
    t.remove();
    return w;
  };
  // A frame with axes: margins come from the widest tick label as drawn.
  CR.frame = (el, { height = 300, x, y, xFormat, yFormat, xTicks, xValues, yTicks, yValues, xLabel, yLabel, label }) => {
    const width = Math.max(260, el.clientWidth || 600);
    const svg = CR.svg(el, width, height, label);
    const yt = yValues || y.ticks(yTicks || Math.max(3, Math.round(height / 60)));
    const yLabels = yt.map(yFormat || String);
    const left = Math.ceil(CR.measure(svg, yLabels)) + 10 + (yLabel ? 16 : 0);
    const m = { top: 12, right: 14, bottom: 30 + (xLabel ? 16 : 0), left };
    x.range([m.left, width - m.right]);
    y.range([height - m.bottom, m.top]);
    // x ticks: the most that fit side by side, measured as drawn
    const inner = width - m.left - m.right;
    const fits = (ts) => ts.reduce((s, t) => s + CR.measure(svg, [(xFormat || String)(t)]) + 12, 0) <= inner;
    let xt = [];
    if (xValues) {
      for (let step = 1; step <= xValues.length; step++) {
        xt = xValues.filter((_, i) => i % step === 0);
        if (fits(xt)) break;
      }
    } else {
      for (let c = xTicks || 14; c >= 2; c--) {
        xt = x.ticks(c);
        if (fits(xt)) break;
      }
    }
    const gGrid = svg.append('g').attr('class', 'cr-grid');
    gGrid
      .selectAll('line')
      .data(yt)
      .join('line')
      .attr('x1', m.left)
      .attr('x2', width - m.right)
      .attr('y1', (d) => y(d))
      .attr('y2', (d) => y(d));
    const ax = svg
      .append('g')
      .attr('class', 'cr-axis')
      .attr('transform', `translate(0,${height - m.bottom})`)
      .call(d3.axisBottom(x).tickValues(xt).tickFormat(xFormat || null).tickSizeOuter(0));
    const ay = svg
      .append('g')
      .attr('class', 'cr-axis')
      .attr('transform', `translate(${m.left},0)`)
      .call(d3.axisLeft(y).tickValues(yt).tickFormat(yFormat || null).tickSize(0).tickPadding(6));
    for (const a of [ax, ay]) a.attr('font-size', null).attr('font-family', null);
    ay.select('.domain').remove();
    if (xLabel)
      svg
        .append('text')
        .attr('class', 'cr-axis-label')
        .attr('x', (m.left + width - m.right) / 2)
        .attr('y', height - 4)
        .attr('text-anchor', 'middle')
        .text(xLabel);
    if (yLabel)
      svg
        .append('text')
        .attr('class', 'cr-axis-label')
        .attr('transform', `translate(11,${(m.top + height - m.bottom) / 2}) rotate(-90)`)
        .attr('text-anchor', 'middle')
        .text(yLabel);
    return { svg, width, height, m };
  };

  // ---------------------------------------------------------------- tooltip
  // One tooltip per chart drawing, inside it. Lines: [[strong, rest], ...]
  CR.tip = (el) => {
    let tip = el.querySelector(':scope > .cr-tip');
    if (!tip) {
      tip = document.createElement('div');
      tip.className = 'cr-tip';
      tip.hidden = true;
      el.append(tip);
    }
    const api = {
      show(event, title, lines) {
        tip.replaceChildren();
        const h = document.createElement('div');
        h.className = 'cr-tip-title';
        h.textContent = title;
        tip.append(h);
        for (const [strong, rest, swatch] of lines) {
          const row = document.createElement('div');
          row.className = 'cr-tip-row';
          if (swatch) {
            const s = document.createElement('span');
            s.className = 'cr-tip-key';
            s.style.background = swatch;
            row.append(s);
          }
          const b = document.createElement('b');
          b.textContent = strong;
          row.append(b, document.createTextNode(rest ? ' ' + rest : ''));
          tip.append(row);
        }
        tip.hidden = false;
        const box = el.getBoundingClientRect();
        const px = event.clientX - box.left;
        const py = event.clientY - box.top;
        const w = tip.offsetWidth;
        const h2 = tip.offsetHeight;
        let left = px + 14;
        if (left + w > box.width) left = Math.max(0, px - w - 14);
        let top = py - h2 - 10;
        if (top < 0) top = py + 16;
        tip.style.left = left + 'px';
        tip.style.top = top + 'px';
      },
      hide() {
        tip.hidden = true;
      },
    };
    return api;
  };

  // nearest-point hover and click over a set of {x, y, d} points
  CR.hover = (svg, pts, { tip, describe, onClick, radius = 28 }) => {
    const delaunay = d3.Delaunay.from(pts, (p) => p.x, (p) => p.y);
    const ring = svg.append('circle').attr('class', 'cr-hover-ring').attr('r', 7).attr('visibility', 'hidden');
    const node = svg.node();
    const find = (event) => {
      const [mx, my] = d3.pointer(event, node);
      if (!pts.length) return null;
      const i = delaunay.find(mx, my);
      const p = pts[i];
      return Math.hypot(p.x - mx, p.y - my) <= radius ? p : null;
    };
    svg
      .on('pointermove', (event) => {
        const p = find(event);
        if (!p) {
          ring.attr('visibility', 'hidden');
          tip.hide();
          node.style.cursor = '';
          return;
        }
        ring.attr('cx', p.x).attr('cy', p.y).attr('visibility', 'visible');
        const [title, lines] = describe(p.d);
        tip.show(event, title, lines);
        node.style.cursor = onClick && p.click !== false ? 'pointer' : '';
      })
      .on('pointerleave', () => {
        ring.attr('visibility', 'hidden');
        tip.hide();
      })
      .on('click', (event) => {
        const p = find(event);
        if (p && onClick && p.click !== false) onClick(p.d);
      });
  };

  // ---------------------------------------------------------------- tables
  // A sortable body: state {key, dir}; columns [{field, text(row), num}]
  CR.sortRows = (rows, state, cols) => {
    const col = cols.find((c) => c.field === state.key) || cols[0];
    const val = (r) => (col.sort ? col.sort(r) : r[col.field]);
    const out = rows.slice().sort((a, b) => {
      const x = val(a);
      const y = val(b);
      if (x === y) return 0;
      if (x === null || x === undefined) return 1;
      if (y === null || y === undefined) return -1;
      return (x < y ? -1 : 1) * (state.dir === 'asc' ? 1 : -1);
    });
    return out;
  };
  CR.wireSort = (table, state, redraw) => {
    table.querySelectorAll('th[data-field] button').forEach((b) => {
      b.addEventListener('click', () => {
        const key = b.closest('th').getAttribute('data-field');
        if (state.key === key) state.dir = state.dir === 'asc' ? 'desc' : 'asc';
        else {
          state.key = key;
          state.dir = b.closest('th').classList.contains('cr-num') ? 'desc' : 'asc';
        }
        table.querySelectorAll('th[data-field]').forEach((th) => {
          th.setAttribute(
            'aria-sort',
            th.getAttribute('data-field') === state.key ? (state.dir === 'asc' ? 'ascending' : 'descending') : 'none',
          );
        });
        redraw();
      });
    });
  };
  CR.fillBody = (tbody, rows, cols, key, onRow) => {
    tbody.replaceChildren();
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', r[key]);
      for (const c of cols) {
        const td = document.createElement('td');
        if (c.num) td.className = 'cr-num';
        const v = c.text ? c.text(r) : r[c.field];
        if (c.pill) {
          const s = document.createElement('span');
          s.className = 'cr-pill cr-pill-' + c.pill(r);
          s.textContent = v === null || v === undefined ? '' : String(v);
          td.append(s);
        } else td.textContent = v === null || v === undefined ? '' : String(v);
        tr.append(td);
      }
      if (onRow) {
        tr.tabIndex = 0;
        tr.className = 'cr-clickable';
        tr.addEventListener('click', () => onRow(r));
        tr.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter') onRow(r);
        });
      }
      tbody.append(tr);
    }
  };

  CR.SVG = SVG;
})();
