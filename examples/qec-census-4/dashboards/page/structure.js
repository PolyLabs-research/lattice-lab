// Structure: the census map, the arithmetic skeleton, the groups and the stencil gallery.
(function () {
  const CR = window.CR;
  const f = CR.fmt;
  const root = document.getElementById('structure');
  const q = (s) => root.querySelector(s);

  // controls
  root.querySelectorAll('input[name="cr-stmap"]').forEach((r) =>
    r.addEventListener('change', () => r.checked && dash.setParams({ st_map: r.value })),
  );
  root.querySelectorAll('input[name="cr-stsort"]').forEach((r) =>
    r.addEventListener('change', () => r.checked && dash.setParams({ st_sort: r.value })),
  );
  const gsel = q('.st-gtype');
  gsel.addEventListener('change', () => dash.setParams({ st_gtype: gsel.value }));
  dash.onData(() => {
    const p = dash.params();
    root.querySelectorAll('input[name="cr-stmap"]').forEach((r) => (r.checked = r.value === (p.st_map || 'status')));
    root.querySelectorAll('input[name="cr-stsort"]').forEach((r) => (r.checked = r.value === (p.st_sort || 'score')));
    gsel.value = p.st_gtype || 'all';
    const byD = p.st_map === 'dmax';
    q('#st-map-status').hidden = byD;
    q('[data-draw="st-map-ramp"]').hidden = !byD;
  });

  // lm at which stages 3a, 3b/3c and 4 end: one constant, drawn on the map and named in its note
  const STAGE_ENDS = [100, 150, 200];
  dash.draw('st-bounds', (el) => {
    el.textContent = `${STAGE_ENDS.slice(0, -1).join(', ')} and ${STAGE_ENDS[STAGE_ENDS.length - 1]}`;
  });

  // the best entry of a torus, for its code card
  const bestOf = (torus) => d3.greatest(CR.rows('frontier').filter((e) => e.torus === torus), (e) => +e.score);
  const openTorus = (t) => {
    if (!CR.ok('frontier')) return;
    const e = bestOf(t.torus);
    if (e) CR.openCode(e.id);
  };

  // ------------------------------------------------------------ the census map
  dash.draw('st-map', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tori'], { chart: true })) return;
    const tori = CR.rows('tori');
    const mode = dash.params().st_map || 'status';
    const ls = [...new Set(tori.map((t) => +t.l))].sort((a, b) => a - b);
    const mMax = d3.max(tori, (t) => +t.m);
    const ms = d3.range(2, mMax + 1);
    const width = Math.max(300, el.clientWidth || 700);
    const svg = CR.svg(el, width, 10, 'The census map: every torus by l and m');
    const left = Math.ceil(CR.measure(svg, ls.map(String))) + 30;
    const m = { top: 8, right: 8, bottom: 44, left };
    const x = d3.scaleBand().domain(ms).range([m.left, width - m.right]).paddingInner(0.1);
    const rowH = Math.max(16, Math.min(20, x.step() * 1.3));
    const height = m.top + m.bottom + rowH * ls.length;
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    const y = d3.scaleBand().domain(ls).range([m.top, height - m.bottom]).paddingInner(0.15);
    const ramp = CR.ramp(el, dash.colors[0]);
    const dmax = d3.max(tori, (t) => +t.d_max || 0);
    const fill = (t) => {
      if (t.status === 'pending') return 'none';
      if (t.status === 'no codes') return 'var(--cds-chart-muted)';
      if (mode === 'dmax') return ramp((+t.d_max || 0) / dmax);
      if (t.status === 'unsettled') return 'var(--color-warn)';
      if (t.status === 'error') return 'var(--color-bad)';
      return dash.colors[0];
    };
    const g = svg.append('g');
    for (const t of tori) {
      const cx = x(+t.m);
      const cy = y(+t.l);
      if (cx === undefined || cy === undefined) continue;
      if (t.status === 'no codes') {
        g.append('circle')
          .attr('cx', cx + x.bandwidth() / 2)
          .attr('cy', cy + y.bandwidth() / 2)
          .attr('r', Math.max(1.2, Math.min(2.5, x.bandwidth() / 4)))
          .style('fill', fill(t));
      } else {
        g.append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .attr('rx', Math.min(2, x.bandwidth() / 3))
          .attr('stroke-width', t.status === 'pending' ? 1 : 0)
          .style('stroke', t.status === 'pending' ? 'var(--color-fg-muted)' : 'none')
          .style('fill', fill(t));
      }
    }
    // where the stages end
    for (const c of STAGE_ENDS) {
      const pts = ms.filter((mm) => c / mm >= ls[0] - 0.5 && c / mm <= ls[ls.length - 1] + 0.5).map((mm) => [mm, c / mm]);
      const yl = d3.scaleLinear().domain([ls[0], ls[ls.length - 1]]).range([y(ls[0]) + y.bandwidth() / 2, y(ls[ls.length - 1]) + y.bandwidth() / 2]);
      svg
        .append('path')
        .attr('class', 'cr-law cr-law-exp')
        .attr('d', d3.line().x((p2) => x(p2[0]) + x.bandwidth() / 2).y((p2) => yl(p2[1]))(pts));
    }
    const lw = CR.measure(svg, ['100']) + 8;
    const every = Math.max(1, Math.ceil(lw / x.step()));
    const ax = svg
      .append('g')
      .attr('class', 'cr-axis')
      .attr('transform', `translate(0,${height - m.bottom})`)
      .call(d3.axisBottom(x).tickValues(ms.filter((mm) => mm % ([2, 5, 10, 20, 50].find((st) => st >= every) || 50) === 0)).tickSize(3));
    const ay = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(${m.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(5));
    for (const a of [ax, ay]) a.attr('font-size', null).attr('font-family', null).select('.domain').remove();
    svg.append('text').attr('class', 'cr-axis-label').attr('x', (m.left + width - m.right) / 2).attr('y', height - 6).attr('text-anchor', 'middle').text('m');
    svg
      .append('text')
      .attr('class', 'cr-axis-label')
      .attr('transform', `translate(11,${(m.top + height - m.bottom) / 2}) rotate(-90)`)
      .attr('text-anchor', 'middle')
      .text('l');
    const pts = tori
      .filter((t) => x(+t.m) !== undefined && y(+t.l) !== undefined)
      .map((t) => ({ x: x(+t.m) + x.bandwidth() / 2, y: y(+t.l) + y.bandwidth() / 2, d: t, click: t.status === 'settled' || t.status === 'unsettled' }));
    CR.hover(svg, pts, {
      tip: CR.tip(el),
      radius: Math.max(10, x.step()),
      describe: (t) => {
        const lines = [[t.status, `stage ${t.stage}`], [`n = ${t.n}`, t.group_name]];
        if (t.d_max !== null && t.d_max !== undefined) lines.push([`best d = ${t.d_max}`, `k values ${t.k_values}`]);
        if (t.classes) lines.push([f.int(+t.classes), 'classes']);
        return [`${t.torus}`, lines];
      },
      onClick: openTorus,
    });
  });
  dash.draw('st-map-ramp', (el) => {
    el.replaceChildren();
    if (!CR.ok('tori')) return;
    const dmax = d3.max(CR.rows('tori'), (t) => +t.d_max || 0);
    const ramp = CR.ramp(el, dash.colors[0]);
    const lo = document.createElement('span');
    lo.textContent = '0';
    const bar = document.createElement('span');
    bar.className = 'cr-ramp';
    bar.style.background = `linear-gradient(90deg, ${d3.range(0, 1.0001, 0.125).map(ramp).join(', ')})`;
    const hi = document.createElement('span');
    hi.textContent = f.int(dmax);
    const name = document.createElement('span');
    name.textContent = 'best d on the torus';
    const key = document.createElement('span');
    key.className = 'cr-key';
    key.append(lo, bar, hi);
    el.append(name, key);
  });

  // ------------------------------------------------------------ the arithmetic skeleton
  const catOf = (t) => (t.e_first === 3 || t.e_first === '3' ? 0 : t.e_first === 7 || t.e_first === '7' ? 1 : 2);
  dash.draw('st-skeleton', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tori', 'frontier'], { chart: true })) return;
    const tori = CR.rows('tori');
    const fr = CR.rows('frontier');
    // per n: whether codes exist (criterion E), its category, and whether it is still pending
    const byN = d3.group(tori, (t) => +t.n);
    const cols = [];
    for (const [n, ts] of byN) {
      const withCodes = ts.filter((t) => t.status !== 'no codes' && t.e_first !== null && t.e_first !== undefined && t.e_first !== '');
      if (!withCodes.length) continue;
      const done = withCodes.filter((t) => t.status !== 'pending');
      cols.push({ n, cat: catOf(withCodes[0]), pending: done.length === 0, k_top_theory: +withCodes[0].k_top_theory });
    }
    const ks = [...new Set(fr.map((e) => +e.k))].sort((a, b) => a - b);
    const kAt = d3.rollup(fr, (v) => [...new Set(v.map((e) => +e.k))], (e) => +e.n);
    const topAt = d3.rollup(fr, (v) => +d3.greatest(v, (e) => +e.d * 100 - +e.k).k, (e) => +e.n);
    const width = Math.max(300, el.clientWidth || 700);
    const svg = CR.svg(el, width, 10, 'Which n have codes, and the k at each');
    const left = Math.ceil(CR.measure(svg, ks.map(String))) + 30;
    const m = { top: 8, right: 10, bottom: 44, left };
    const stripH = 10;
    const rowH = 14;
    const height = m.top + rowH * ks.length + 8 + stripH + m.bottom;
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    const x = d3.scaleLinear().domain([0, 410]).range([m.left, width - m.right]);
    const y = d3.scaleBand().domain(ks).range([m.top, m.top + rowH * ks.length]).paddingInner(0.2);
    const stripY = m.top + rowH * ks.length + 8;
    const w = Math.max(1.5, ((x(6) - x(0)) / 3) * 2);
    svg
      .append('g')
      .selectAll('rect')
      .data(cols)
      .join('rect')
      .attr('x', (c) => x(c.n) - w / 2)
      .attr('y', stripY)
      .attr('width', w)
      .attr('height', stripH)
      .attr('rx', 1)
      .attr('stroke-width', (c) => (c.pending ? 1 : 0))
      .style('fill', (c) => (c.pending ? 'none' : dash.colors[c.cat]))
      .style('stroke', (c) => (c.pending ? dash.colors[c.cat] : 'none'));
    const dots = [];
    for (const c of cols) for (const k of kAt.get(c.n) || []) dots.push({ n: c.n, k, cat: c.cat, top: topAt.get(c.n) === k });
    const r = Math.max(1.5, Math.min(3.5, w / 2));
    svg
      .append('g')
      .selectAll('circle')
      .data(dots)
      .join('circle')
      .attr('cx', (d) => x(d.n))
      .attr('cy', (d) => y(d.k) + y.bandwidth() / 2)
      .attr('r', r)
      .style('fill', (d) => dash.colors[d.cat]);
    svg
      .append('g')
      .selectAll('circle')
      .data(dots.filter((d) => d.top))
      .join('circle')
      .attr('cx', (d) => x(d.n))
      .attr('cy', (d) => y(d.k) + y.bandwidth() / 2)
      .attr('r', r + 2.5)
      .attr('fill', 'none')
      .attr('stroke-width', 1.2)
      .style('stroke', 'var(--color-fg)');
    let xt = [];
    for (let c = 14; c >= 2; c--) {
      xt = x.ticks(c);
      if (xt.reduce((s, t) => s + CR.measure(svg, [String(t)]) + 12, 0) <= width - m.left - m.right) break;
    }
    const ax = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(0,${stripY + stripH + 4})`).call(d3.axisBottom(x).tickValues(xt).tickSize(3));
    const ay = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(${m.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(5));
    for (const a of [ax, ay]) a.attr('font-size', null).attr('font-family', null).select('.domain').remove();
    svg.append('text').attr('class', 'cr-axis-label').attr('x', (m.left + width - m.right) / 2).attr('y', height - 6).attr('text-anchor', 'middle').text('n (physical qubits)');
    svg
      .append('text')
      .attr('class', 'cr-axis-label')
      .attr('transform', `translate(11,${m.top + (rowH * ks.length) / 2}) rotate(-90)`)
      .attr('text-anchor', 'middle')
      .text('k');
    const hov = cols.map((c) => ({ x: x(c.n), y: stripY + stripH / 2, d: c, click: false }));
    for (const d of dots) hov.push({ x: x(d.n), y: y(d.k) + y.bandwidth() / 2, d: { ...cols.find((c) => c.n === d.n), k: d.k, top: d.top }, click: false });
    CR.hover(svg, hov, {
      tip: CR.tip(el),
      radius: 14,
      describe: (c) => {
        const why = ['3 divides lm', 'only 7 divides lm', 'only 31, 85 or 73 divides lm'][c.cat];
        const lines = [[why, ''], [`k values: ${(kAt.get(c.n) || []).join(', ') || 'none yet'}`, '']];
        if (c.k !== undefined) lines.unshift([`k = ${c.k}`, c.top ? 'the column’s best d' : '']);
        if (c.pending) lines.push(['not yet run', '']);
        return [`n = ${c.n}`, lines];
      },
    });
  });

  // the skeleton's legend: each colour's divisors of lm, and the k at their columns' tops
  dash.draw('st-skel-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('tori')) return;
    const cats = [[], [], []];
    for (const t of CR.rows('tori')) {
      if (t.e_first === null || t.e_first === undefined || t.e_first === '') continue;
      const c = catOf(t);
      if (!cats[c].some((x) => +x.t === +t.e_first)) cats[c].push({ t: +t.e_first, k: +t.k_top_theory });
    }
    cats.forEach((list, i) => {
      if (!list.length) return;
      list.sort((a, b) => a.k - b.k);
      const k = document.createElement('span');
      k.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw';
      sw.style.background = dash.colors[i];
      const ts = list.map((x) => x.t);
      const ks = list.map((x) => x.k);
      const words = (xs) => (xs.length === 1 ? String(xs[0]) : `${xs.slice(0, -1).join(', ')} or ${xs[xs.length - 1]}`);
      k.append(sw, document.createTextNode(`${i === 0 ? '' : 'only '}${words(ts)} divides lm (top k = ${words(ks)})`));
      el.append(k);
    });
  });

  // ------------------------------------------------------------ groups
  const gTable = q('#st-groups');
  const gSort = { key: 'best_score', dir: 'desc' };
  const gSearch = q('.st-search');
  const GCOLS = [
    { field: 'group_name' },
    { field: 'tori' },
    { field: 'n', num: true },
    { field: 'd_max', num: true },
    { field: 'k_values' },
    { field: 'best_score', num: true, text: (r) => f.score(+r.best_score), sort: (r) => +r.best_score },
    { field: 'group_type' },
  ];
  CR.wireSort(gTable, gSort, () => dash.draw('st-groups'));
  gSearch.addEventListener('input', () => dash.draw('st-groups'));
  dash.draw('st-groups', (tbody) => {
    if (!CR.ok('groups')) {
      tbody.replaceChildren();
      return;
    }
    const term = gSearch.value.trim().toLowerCase();
    let rows = CR.rows('groups');
    if (term) rows = rows.filter((r) => [r.group_name, r.tori, r.group_type].join(' ').toLowerCase().includes(term));
    CR.fillBody(tbody, CR.sortRows(rows, gSort, GCOLS), GCOLS, 'iso_key', (r) => {
      if (!CR.ok('frontier')) return;
      const e = bestOf(r.primary);
      if (e) CR.openCode(e.id);
    });
    tbody.querySelectorAll('tr').forEach((tr) => {
      [4, 6].forEach((i) => tr.children[i].classList.add('cr-hide-narrow'));
    });
  });

  // ------------------------------------------------------------ stencil gallery
  dash.draw('st-gallery', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['stencils'], { chart: true })) return;
    const p = dash.params();
    const key = p.st_sort === 'ratio' ? 'ratio' : 'score';
    const rows = CR.rows('stencils')
      .filter((r) => r.A_lift && (p.st_gtype === 'all' || !p.st_gtype || r.group_type === p.st_gtype))
      .sort((a, b) => b[key] - a[key] || a.n - b.n)
      .slice(0, 24);
    for (const r of rows) {
      const A = JSON.parse(r.A_lift);
      const B = JSON.parse(r.B_lift);
      const all = [...A, ...B];
      const lo = d3.min(all.flat()) - 0.6;
      const hi = d3.max(all.flat()) + 0.6;
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'cr-gal-item';
      item.addEventListener('click', () => CR.openCode(r.id));
      const size = 108;
      const sc = d3.scaleLinear().domain([lo, hi]).range([6, size - 6]);
      const svg = d3.select(item).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${size} ${size}`).attr('role', 'img').attr('aria-label', `The stencil of ${r.code}`);
      const grid = [];
      for (let a = Math.ceil(lo); a <= Math.floor(hi); a++) for (let b = Math.ceil(lo); b <= Math.floor(hi); b++) grid.push([a, b]);
      svg.append('g').selectAll('circle').data(grid).join('circle').attr('cx', (g2) => sc(g2[1])).attr('cy', (g2) => sc(g2[0])).attr('r', 1.2).style('fill', 'var(--cds-chart-muted)');
      const rr = Math.max(3, Math.min(7, (sc(1) - sc(0)) * 0.3));
      svg.append('polygon').attr('points', A.map((q2) => `${sc(q2[1])},${sc(q2[0])}`).join(' ')).attr('fill', 'none').attr('stroke-width', 1).style('stroke', dash.colors[0]);
      svg.append('polygon').attr('points', B.map((q2) => `${sc(q2[1])},${sc(q2[0])}`).join(' ')).attr('fill', 'none').attr('stroke-width', 1).style('stroke', dash.colors[1]);
      svg.append('g').selectAll('circle').data(A).join('circle').attr('cx', (q2) => sc(q2[1])).attr('cy', (q2) => sc(q2[0])).attr('r', rr).attr('stroke-width', 1.5).style('fill', dash.colors[0]).style('stroke', 'var(--color-panel)');
      svg.append('g').selectAll('rect').data(B).join('rect').attr('x', (q2) => sc(q2[1]) - rr * 0.85).attr('y', (q2) => sc(q2[0]) - rr * 0.85).attr('width', rr * 1.7).attr('height', rr * 1.7).attr('rx', 1.5).attr('stroke-width', 1.5).style('fill', dash.colors[1]).style('stroke', 'var(--color-panel)');
      const cap = document.createElement('div');
      cap.className = 'cr-gal-cap';
      const b = document.createElement('b');
      b.textContent = r.code;
      const s1 = document.createElement('span');
      s1.textContent = ` ${r.torus}`;
      const s2 = document.createElement('div');
      s2.textContent = `diameter ${r.diameter} · k·d²/n ${f.score(+r.score)}`;
      s2.style.color = 'var(--color-fg-muted)';
      cap.append(b, s1, s2);
      item.append(cap);
      el.append(item);
    }
  });
})();
