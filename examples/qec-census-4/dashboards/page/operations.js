// Operations: the pod, the cost of an exact distance, compute per torus, and check durations.
(function () {
  const CR = window.CR;
  const f = CR.fmt;

  for (const [name, key] of [['op-phase', 'phase'], ['op-torus', 'torus'], ['op-records', 'records'], ['op-updated', 'updated'], ['op-pod', 'pod'], ['op-detail', 'detail'], ['op-cpu', 'cpu'], ['op-vcpus', 'vcpus'], ['op-mem', 'memory']]) {
    dash.draw(name, (el) => {
      if (!CR.ready(el, ['runstatus'])) return;
      const r = CR.rows('runstatus').find((x) => x.key === key);
      el.textContent = r && r.value !== '' ? String(r.value) : '—';
    });
  }

  // time ticks a reader knows, about a factor of ten apart
  const TIME_TICKS = [0.001, 0.01, 0.1, 1, 10, 60, 600, 3600, 36000, 360000];
  const TIME_NAMES = ['1 ms', '10 ms', '0.1 s', '1 s', '10 s', '1 min', '10 min', '1 h', '10 h', '100 h'];
  const secFmt = (s) => {
    const i = TIME_TICKS.indexOf(s);
    return i >= 0 ? TIME_NAMES[i] : f.seconds(s);
  };
  const logTicks = (lo, hi) => TIME_TICKS.filter((v) => v >= lo && v <= hi);

  // ------------------------------------------------------------ the cost of an exact distance
  const SERIES = [
    { stage: '3b/3c', engine: 'packing search', label: 'Packing search, stages 3b/3c', fit: 'cost_3b/3c' },
    { stage: '4', engine: 'DistQLDPC cluster', label: 'DistQLDPC cluster engine, stage 4', fit: 'cost_4' },
    { stage: '3a', engine: 'packing search', label: 'Packing search, stage 3a' },
  ];
  dash.draw('op-cost', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['run_cost', 'fits'], { chart: true })) return;
    const rc = CR.rows('run_cost').filter((r) => r.d !== null && r.d !== undefined && !CR.bool(r.timelimit) && +r.median_s > 0);
    const fits = CR.rows('fits');
    const pts = rc.filter((r) => SERIES.some((s) => s.stage === r.stage && s.engine === r.engine));
    const lo = d3.min(pts, (r) => Math.max(1e-3, +r.p10_s || +r.median_s));
    const hi = d3.max(pts, (r) => +r.p90_s || +r.median_s);
    const x = d3.scaleLinear().domain([0, d3.max(pts, (r) => +r.d) + 2]);
    const y = d3.scaleLog().domain([lo / 1.5, hi * 1.5]);
    const { svg } = CR.frame(el, { height: 280, x, y, yValues: logTicks(lo / 1.5, hi * 1.5), xFormat: f.int, yFormat: secFmt, xLabel: 'd found', yLabel: 'Time per run (log)', label: 'Time per exact run against d' });
    SERIES.forEach((s, i) => {
      const rows = pts.filter((r) => r.stage === s.stage && r.engine === s.engine).sort((a, b) => a.d - b.d);
      if (!rows.length) return;
      const band = d3.area().x((r) => x(+r.d)).y0((r) => y(Math.max(lo / 1.5, +r.p10_s))).y1((r) => y(+r.p90_s));
      svg.append('path').attr('d', band(rows)).style('fill', dash.colors[i]).attr('fill-opacity', 0.1);
      svg.append('path').attr('d', d3.line().x((r) => x(+r.d)).y((r) => y(+r.median_s))(rows)).attr('fill', 'none').attr('stroke-width', 2).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round').style('stroke', dash.colors[i]);
      svg.append('g').selectAll('circle').data(rows).join('circle').attr('cx', (r) => x(+r.d)).attr('cy', (r) => y(+r.median_s)).attr('r', 3.5).attr('stroke-width', 1.5).style('fill', dash.colors[i]).style('stroke', 'var(--color-panel)');
      const F = s.fit && fits.find((r) => r.id === s.fit);
      if (F) {
        const ds = d3.range(14, d3.max(rows, (r) => +r.d) + 0.1, 0.5);
        svg.append('path').attr('class', 'cr-law cr-law-exp').attr('d', d3.line().x((d) => x(d)).y((d) => y(+F.a * (+F.b) ** (d / 2)))(ds.filter((d) => +F.a * (+F.b) ** (d / 2) >= lo / 1.5)));
      }
    });
    // stage 3d: the reruns, as diamonds on the DistQLDPC colour
    const r3d = rc.filter((r) => r.stage === '3d');
    svg.append('g').selectAll('path').data(r3d).join('path').attr('d', d3.symbol(d3.symbolDiamond, 72)).attr('transform', (r) => `translate(${x(+r.d)},${y(+r.median_s)})`).attr('stroke-width', 1.5).style('fill', dash.colors[1]).style('stroke', 'var(--color-panel)');
    CR.hover(svg, [...pts, ...r3d].map((r) => ({ x: x(+r.d), y: y(+r.median_s), d: r, click: false })), {
      tip: CR.tip(el),
      describe: (r) => [`${r.engine}, stage ${r.stage}, d = ${r.d}`, [[secFmt(+r.median_s), 'median'], [`${secFmt(+r.p10_s)} to ${secFmt(+r.p90_s)}`, '10th to 90th percentile'], [f.int(+r.runs), 'runs']]],
    });
  });
  dash.draw('op-cost-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('fits')) return;
    const fits = CR.rows('fits');
    SERIES.forEach((s, i) => {
      const k = document.createElement('span');
      k.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw';
      sw.style.background = dash.colors[i];
      const F = s.fit && fits.find((r) => r.id === s.fit);
      k.append(sw, document.createTextNode(s.label + (F ? `: fit ${F.formula}` : '')));
      el.append(k);
    });
    const k = document.createElement('span');
    k.className = 'cr-key';
    const sw = document.createElement('span');
    sw.className = 'cr-sw cr-sw-dia';
    sw.style.background = dash.colors[1];
    k.append(sw, document.createTextNode('DistQLDPC, stage 3d reruns'));
    el.append(k);
  });

  // ------------------------------------------------------------ compute per torus
  dash.draw('op-torus-time', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tori'], { chart: true })) return;
    const tori = CR.rows('tori').filter((t) => +t.exact_seconds > 0);
    const lo = d3.min(tori, (t) => +t.exact_seconds);
    const hi = d3.max(tori, (t) => +t.exact_seconds);
    const x = d3.scaleLinear().domain([0, 410]);
    const y = d3.scaleLog().domain([lo / 1.5, hi * 1.5]);
    const { svg } = CR.frame(el, { height: 250, x, y, yValues: logTicks(lo / 1.5, hi * 1.5), xFormat: f.int, yFormat: secFmt, xLabel: 'n', yLabel: 'Exact-run time (log)', label: 'Summed exact-run time per torus' });
    svg.append('g').selectAll('circle').data(tori).join('circle').attr('cx', (t) => x(+t.n)).attr('cy', (t) => y(+t.exact_seconds)).attr('r', 3.5).attr('stroke-width', 1.5).style('fill', (t) => dash.colors[Math.max(0, CR.STAGES.indexOf(t.stage))]).style('stroke', 'var(--color-panel)');
    CR.hover(svg, tori.map((t) => ({ x: x(+t.n), y: y(+t.exact_seconds), d: t, click: false })), {
      tip: CR.tip(el),
      describe: (t) => [t.torus, [[f.seconds(+t.exact_seconds), 'of exact runs'], [f.int(+t.exact_runs), 'exact runs'], [`stage ${t.stage}`, '']]],
    });
  });

  // ------------------------------------------------------------ check durations
  const KINDS = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'V'];
  const NAMES = { C1: 'C1 integer program', C2: 'C2 unpruned search', C3: 'C3 other kind', C4: 'C4 windows', C5: 'C5 DistQLDPC', C6: 'C6 SAT proof', D1: 'Stage 3d reruns', V: 'Stage 4 validation' };
  const STATUS_FILL = { 'reached d': 'var(--color-ok)', contradicts: 'var(--color-bad)', error: 'var(--color-bad)' };
  dash.draw('op-checks', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['checks'], { chart: true })) return;
    const rows = CR.rows('checks').filter((c) => +c.seconds > 0);
    const kinds = KINDS.filter((k) => rows.some((c) => c.check === k));
    const width = Math.max(300, el.clientWidth || 600);
    const svg = CR.svg(el, width, 10, 'Check job times by kind');
    const left = Math.ceil(CR.measure(svg, kinds.map((k) => NAMES[k]))) + 12;
    const m = { top: 6, right: 14, bottom: 34, left };
    const height = m.top + m.bottom + kinds.length * 26;
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    const lo = d3.min(rows, (c) => +c.seconds);
    const hi = d3.max(rows, (c) => +c.seconds);
    const x = d3.scaleLog().domain([lo / 1.5, hi * 1.5]).range([m.left, width - m.right]);
    const y = d3.scaleBand().domain(kinds).range([m.top, height - m.bottom]).paddingInner(0.2);
    let xt = logTicks(lo / 1.5, hi * 1.5);
    for (let step = 1; step <= xt.length; step++) {
      const sub = xt.filter((_, i) => i % step === 0);
      if (sub.reduce((acc, v) => acc + CR.measure(svg, [secFmt(v)]) + 14, 0) <= width - m.left - m.right) {
        xt = sub;
        break;
      }
    }
    svg.append('g').attr('class', 'cr-grid').selectAll('line').data(xt).join('line').attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', m.top).attr('y2', height - m.bottom);
    const ax = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(0,${height - m.bottom})`).call(d3.axisBottom(x).tickValues(xt).tickFormat(secFmt).tickSize(3));
    const ay = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(${m.left},0)`).call(d3.axisLeft(y).tickFormat((k) => NAMES[k]).tickSize(0).tickPadding(6));
    for (const a of [ax, ay]) a.attr('font-size', null).attr('font-family', null).select('.domain').remove();
    // a deterministic jitter within each row
    const jit = (c, i) => ((i * 37) % 11) / 10 - 0.5;
    const pts = rows.map((c, i) => ({ x: x(+c.seconds), y: y(c.check) + y.bandwidth() / 2 + jit(c, i) * y.bandwidth() * 0.7, d: c, click: false }));
    svg
      .append('g')
      .selectAll('circle')
      .data(pts)
      .join('circle')
      .attr('cx', (p) => p.x)
      .attr('cy', (p) => p.y)
      .attr('r', 3)
      .attr('stroke-width', 1.2)
      .style('fill', (p) => STATUS_FILL[p.d.status] || 'none')
      .style('stroke', (p) => (STATUS_FILL[p.d.status] ? 'var(--color-panel)' : p.d.status === 'consistent' ? 'var(--color-ok)' : 'var(--color-fg-muted)'));
    CR.hover(svg, pts, {
      tip: CR.tip(el),
      describe: (c) => [`${c.code} ${c.torus}`, [[f.seconds(+c.seconds), NAMES[c.check]], [c.status, c.variant || c.engine || '']]],
    });
  });
})();
