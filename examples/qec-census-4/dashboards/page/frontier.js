// Frontier: the scatter, the n x k grid, the trade-off plane, residuals and the leaderboard.
(function () {
  const CR = window.CR;
  const f = CR.fmt;
  const root = document.getElementById('frontier');
  const q = (s) => root.querySelector(s);

  // ------------------------------------------------------------ filters and view controls
  const DEFAULTS = { stage: 'all', k: 'all', gtype: 'all', nmin: null, nmax: null, merge: true };
  const stage = q('.f-stage');
  const gtype = q('.f-gtype');
  const nmin = q('.f-nmin');
  const nmax = q('.f-nmax');
  const merge = q('.f-merge');
  stage.addEventListener('change', () => dash.setParams({ stage: stage.value }));
  gtype.addEventListener('change', () => dash.setParams({ gtype: gtype.value }));
  merge.addEventListener('change', () => dash.setParams({ merge: merge.checked }));
  const numberParam = (input, name) => {
    input.addEventListener('change', () => {
      const v = input.value === '' ? null : +input.value;
      if (v === null || (Number.isFinite(v) && input.validity.valid)) dash.setParams({ [name]: v });
    });
    input.addEventListener('blur', () => {
      const v = dash.params()[name];
      input.value = v === null || v === undefined ? '' : String(v);
    });
  };
  numberParam(nmin, 'nmin');
  numberParam(nmax, 'nmax');
  q('.f-reset').addEventListener('click', () => dash.setParams({ ...DEFAULTS }));
  const radios = (name, param) => {
    root.querySelectorAll(`input[name="${name}"]`).forEach((r) => {
      r.addEventListener('change', () => {
        if (r.checked) dash.setParams({ [param]: r.value });
      });
    });
  };
  radios('cr-metric', 'metric');
  radios('cr-color', 'color');
  radios('cr-heat', 'heat');
  const checks = { '.f-laws': 'laws', '.f-fits': 'fits', '.f-pub': 'pub' };
  for (const [sel, name] of Object.entries(checks)) {
    const c = q(sel);
    c.addEventListener('change', () => dash.setParams({ [name]: c.checked }));
  }
  dash.onData(() => {
    const p = dash.params();
    stage.value = p.stage || 'all';
    gtype.value = p.gtype || 'all';
    merge.checked = CR.bool(p.merge);
    for (const [input, name] of [[nmin, 'nmin'], [nmax, 'nmax']]) {
      if (input !== document.activeElement) {
        const v = p[name];
        input.value = v === null || v === undefined ? '' : String(v);
      }
    }
    for (const [name, param, dflt] of [['cr-metric', 'metric', 'd'], ['cr-color', 'color', 'group'], ['cr-heat', 'heat', 'd']]) {
      root.querySelectorAll(`input[name="${name}"]`).forEach((r) => {
        r.checked = r.value === (p[param] || dflt);
      });
    }
    for (const [sel, name] of Object.entries(checks)) q(sel).checked = CR.bool(p[name]);
    const byStage = p.color === 'stage';
    q('#fr-legend-group').hidden = byStage;
    q('#fr-legend-stage').hidden = !byStage;
    root.querySelectorAll('.cr-key-pub').forEach((k) => {
      k.hidden = !CR.bool(p.pub);
    });
  });
  dash.draw('f-k', (s) => {
    const all = CR.rows('frontier');
    const ks = [...new Set(all.map((e) => +e.k))].sort((a, b) => a - b);
    s.replaceChildren(new Option('All', 'all'), ...ks.map((k) => new Option(String(k), String(k))));
    const p = dash.params();
    s.value = p.k === null || p.k === undefined ? 'all' : String(p.k);
    s.onchange = () => dash.setParams({ k: s.value === 'all' ? 'all' : +s.value });
  });

  // ------------------------------------------------------------ laws
  const evenDown = (x) => {
    const v = Math.floor(x);
    return v - (((v % 2) + 2) % 2);
  };
  const edgeOf = (n, a) => 2 * Math.floor((a * Math.sqrt(n * Math.log(n))) / 2);
  // each law's value for each measure; the constants come from the fits dataset
  const LAWS = {
    p2: { d: (n, F) => evenDown(F.a * Math.sqrt(n)), ratio: (n, F) => F.a, span: '3b/3c', step: true },
    p3: { score: (n, F) => F.a, span: '3b/3c' },
    e: { d: (n, F) => evenDown(F.a * n ** F.b), ratio: (n, F) => evenDown(F.a * n ** F.b) / Math.sqrt(n), span: '4', step: true },
    g: { ratio: (n, F) => F.a, span: '4' },
    s1: { score: (n, F) => F.a, span: '4' },
    s2: { score: (n, F) => F.a, span: '4' },
    edge: { d: (n, F) => edgeOf(n, F.a), ratio: (n, F) => edgeOf(n, F.a) / Math.sqrt(n), span: 'all', step: true },
    power: { d: (n, F) => F.a * n ** F.b, ratio: (n, F) => F.a * n ** (F.b - 0.5), span: 'all' },
    affine: { d: (n, F) => F.a * Math.sqrt(n) + F.b, ratio: (n, F) => F.a + F.b / Math.sqrt(n), span: 'n90' },
  };
  const spanOf = (span, all) => {
    const ns = (span === 'all' || span === 'n90' ? all : all.filter((e) => e.stage === span)).map((e) => +e.n);
    const lo = span === 'n90' ? 90 : d3.min(ns);
    return [lo, d3.max(ns)];
  };
  const lawsFor = (metric, p, fits, all) => {
    const out = [];
    for (const F of fits) {
      const L = LAWS[F.id];
      if (!L || !L[metric]) continue;
      const reg = F.kind === 'registered';
      if ((reg && !CR.bool(p.laws)) || (!reg && !CR.bool(p.fits))) continue;
      const [lo, hi] = spanOf(L.span, all);
      const pts = [];
      for (let n = lo + (lo % 2); n <= hi; n += 2) pts.push([n, L[metric](n, { a: +F.a, b: +F.b })]);
      out.push({ F, reg, pts, step: !!L.step && metric === 'd' });
    }
    return out;
  };
  const metricOf = (e, metric) => (metric === 'd' ? +e.d : metric === 'ratio' ? +e.ratio : +e.score);
  const METRIC_LABEL = { d: 'd', ratio: 'd/√n', score: 'k·d²/n' };
  const METRIC_FMT = { d: f.int, ratio: d3.format('.2f'), score: d3.format('.0f') };

  const describe = (e) => [
    `${e.code} on ${e.torus}`,
    [
      [f.score(+e.score), 'k·d²/n'],
      [f.ratio(+e.ratio), 'd/√n'],
      [e.group_name, `(${e.group_type})`],
      ['Stage ' + e.stage, CR.bool(e.settled) ? 'settled' : 'lower bound only'],
      [e.tier, ''],
    ],
  ];
  const describePub = (c) => [c.name, [[f.score(+c.score), 'k·d²/n'], [f.ratio(+c.ratio), 'd/√n'], ['published', '']]];

  // ------------------------------------------------------------ the scatter
  dash.draw('fr-scatter', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier', 'published', 'fits'], { chart: true })) return;
    const p = dash.params();
    const metric = p.metric || 'd';
    const all = CR.rows('frontier');
    const rows = CR.filtered(all, p);
    const pubs = CR.bool(p.pub) ? CR.rows('published').filter((c) => +c.n <= 410) : [];
    const laws = lawsFor(metric, p, CR.rows('fits'), all);
    const yMax = d3.max([
      ...all.map((e) => metricOf(e, metric)),
      ...pubs.map((c) => metricOf(c, metric)),
      ...laws.flatMap((l) => l.pts.map((q2) => q2[1])),
    ]);
    const x = d3.scaleLinear().domain([0, 410]);
    const y = d3.scaleLinear().domain([0, yMax * 1.04]).nice();
    const { svg } = CR.frame(el, {
      height: 380,
      x,
      y,
      xFormat: f.int,
      yFormat: METRIC_FMT[metric],
      xLabel: 'n (physical qubits)',
      yLabel: METRIC_LABEL[metric],
      label: `${METRIC_LABEL[metric]} against n for the census frontier`,
    });
    for (const l of laws) {
      const line = d3
        .line()
        .x((q2) => x(q2[0]))
        .y((q2) => y(q2[1]))
        .curve(l.step ? d3.curveStepAfter : d3.curveLinear);
      svg.append('path').attr('class', 'cr-law ' + (l.reg ? 'cr-law-reg' : 'cr-law-exp')).attr('d', line(l.pts));
    }
    const by = p.color === 'stage' ? 'stage' : 'group';
    svg
      .append('g')
      .selectAll('circle')
      .data(rows.slice().sort((a, b) => a.score - b.score))
      .join('circle')
      .attr('cx', (e) => x(+e.n))
      .attr('cy', (e) => y(metricOf(e, metric)))
      .attr('r', 4)
      .attr('stroke-width', 1.5)
      .style('fill', (e) => CR.colorOf(e, by))
      .style('stroke', 'var(--color-panel)');
    const sym = d3.symbol(d3.symbolDiamond, 72);
    svg
      .append('g')
      .selectAll('path')
      .data(pubs)
      .join('path')
      .attr('d', sym)
      .attr('transform', (c) => `translate(${x(+c.n)},${y(metricOf(c, metric))})`)
      .attr('stroke-width', 1.5)
      .style('fill', 'var(--color-fg)')
      .style('stroke', 'var(--color-panel)');
    const pts = [
      ...rows.map((e) => ({ x: x(+e.n), y: y(metricOf(e, metric)), d: e })),
      ...pubs.map((c) => ({ x: x(+c.n), y: y(metricOf(c, metric)), d: { pub: c }, click: false })),
    ];
    CR.hover(svg, pts, {
      tip: CR.tip(el),
      describe: (d) => (d.pub ? describePub(d.pub) : describe(d)),
      onClick: (d) => CR.openCode(d.id),
    });
  });

  // the laws drawn, named
  dash.draw('fr-law-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('fits', 'frontier')) return;
    const p = dash.params();
    const laws = lawsFor(p.metric || 'd', p, CR.rows('fits'), CR.rows('frontier'));
    for (const l of laws) {
      const s = document.createElement('span');
      s.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw ' + (l.reg ? 'cr-sw-line' : 'cr-sw-dash');
      s.append(sw, document.createTextNode(`${l.F.label} — ${l.F.status}`));
      el.append(s);
    }
  });

  // ------------------------------------------------------------ the n x k grid
  const pubIndex = () => {
    const m = new Map();
    for (const c of CR.rows('published')) {
      const key = `${c.n}|${c.k}`;
      m.set(key, Math.max(m.get(key) || 0, +c.d));
    }
    return m;
  };
  const heatValue = (e, mode) => (mode === 'score' ? +e.score : mode === 'resid' ? +e.resid_layer : +e.d);
  const heatScale = (host, mode, all) => {
    if (mode === 'resid') {
      const a = d3.max(all, (e) => Math.abs(+e.resid_layer));
      const div = CR.diverging(host);
      return { color: (v) => div(v / a), lo: -a, hi: a };
    }
    const vals = all.map((e) => heatValue(e, mode));
    const lo = d3.min(vals);
    const hi = d3.max(vals);
    const ramp = CR.ramp(host, dash.colors[0]);
    return { color: (v) => ramp((v - lo) / (hi - lo || 1)), lo, hi };
  };
  dash.draw('fr-heat', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier', 'published'], { chart: true })) return;
    const p = dash.params();
    const mode = p.heat || 'd';
    const all = CR.rows('frontier');
    const rows = CR.filtered(all, p);
    const best = new Map();
    const count = new Map();
    for (const e of rows) {
      const key = `${e.n}|${e.k}`;
      count.set(key, (count.get(key) || 0) + 1);
      const b = best.get(key);
      if (!b || +e.d > +b.d || (+e.d === +b.d && +e.score > +b.score)) best.set(key, e);
    }
    const cells = [...best.values()];
    const ns = [...new Set(cells.map((e) => +e.n))].sort((a, b) => a - b);
    const ks = [...new Set(all.map((e) => +e.k))].sort((a, b) => a - b);
    const width = Math.max(280, el.clientWidth || 600);
    const svg = CR.svg(el, width, 10, 'Best d for each n and k');
    const left = Math.ceil(CR.measure(svg, ks.map(String))) + 30;
    const m = { top: 8, right: 8, bottom: 44, left };
    const rowH = Math.max(14, Math.min(24, Math.floor(300 / ks.length)));
    const height = m.top + m.bottom + rowH * ks.length;
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    const x = d3.scaleBand().domain(ns).range([m.left, width - m.right]).paddingInner(ns.length > 60 ? 0.08 : 0.12);
    const y = d3.scaleBand().domain(ks).range([m.top, height - m.bottom]).paddingInner(0.12);
    const sc = heatScale(el, mode, all);
    const pubs = pubIndex();
    svg
      .append('g')
      .selectAll('rect')
      .data(cells)
      .join('rect')
      .attr('x', (e) => x(+e.n))
      .attr('y', (e) => y(+e.k))
      .attr('width', x.bandwidth())
      .attr('height', y.bandwidth())
      .attr('rx', Math.min(2, x.bandwidth() / 3))
      .style('fill', (e) => sc.color(heatValue(e, mode)))
      .style('stroke', (e) => {
        const pd = pubs.get(`${e.n}|${e.k}`);
        return pd !== undefined && +e.d >= pd ? 'var(--color-fg)' : 'none';
      })
      .attr('stroke-width', 1.5);
    // axes: every k labelled; n labelled as often as the labels fit
    const lw = CR.measure(svg, ['400']) + 8;
    const every = Math.max(1, Math.ceil(lw / x.step()));
    const ax = svg
      .append('g')
      .attr('class', 'cr-axis')
      .attr('transform', `translate(0,${height - m.bottom})`)
      .call(d3.axisBottom(x).tickValues(ns.filter((_, i) => i % every === 0)).tickSize(3).tickFormat(f.int));
    const ay = svg
      .append('g')
      .attr('class', 'cr-axis')
      .attr('transform', `translate(${m.left},0)`)
      .call(d3.axisLeft(y).tickSize(0).tickPadding(5));
    for (const a of [ax, ay]) a.attr('font-size', null).attr('font-family', null).select('.domain').remove();
    svg
      .append('text')
      .attr('class', 'cr-axis-label')
      .attr('x', (m.left + width - m.right) / 2)
      .attr('y', height - 6)
      .attr('text-anchor', 'middle')
      .text('n (physical qubits)');
    svg
      .append('text')
      .attr('class', 'cr-axis-label')
      .attr('transform', `translate(11,${(m.top + height - m.bottom) / 2}) rotate(-90)`)
      .attr('text-anchor', 'middle')
      .text('k');
    const pts = cells.map((e) => ({ x: x(+e.n) + x.bandwidth() / 2, y: y(+e.k) + y.bandwidth() / 2, d: e }));
    CR.hover(svg, pts, {
      tip: CR.tip(el),
      radius: Math.max(12, x.step()),
      describe: (e) => {
        const [title, lines] = describe(e);
        const c = count.get(`${e.n}|${e.k}`);
        const pd = pubs.get(`${e.n}|${e.k}`);
        const extra = [[`${c} ${c === 1 ? 'torus' : 'tori'}`, 'at this n and k']];
        if (pd !== undefined) extra.push([`published d = ${pd}`, '']);
        return [title, [[`d = ${e.d}`, ''], ...lines.slice(0, 2), ...extra]];
      },
      onClick: (e) => CR.openCode(e.id),
    });
  });
  dash.draw('fr-heat-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('frontier')) return;
    const mode = dash.params().heat || 'd';
    const sc = heatScale(el, mode, CR.rows('frontier'));
    const stops = d3.range(0, 1.0001, 0.125).map((t) => sc.color(sc.lo + t * (sc.hi - sc.lo)));
    const fmt = mode === 'd' ? f.int : f.signed;
    const lo = document.createElement('span');
    lo.textContent = mode === 'score' ? f.score1(sc.lo) : fmt(sc.lo);
    const bar = document.createElement('span');
    bar.className = 'cr-ramp';
    bar.style.background = `linear-gradient(90deg, ${stops.join(', ')})`;
    const hi = document.createElement('span');
    hi.textContent = mode === 'score' ? f.score1(sc.hi) : fmt(sc.hi);
    const name = document.createElement('span');
    name.textContent = mode === 'd' ? 'best d' : mode === 'score' ? 'k·d²/n of the best d' : 'd − (2.31·n^0.443 − k)';
    const key = document.createElement('span');
    key.className = 'cr-key';
    key.append(lo, bar, hi);
    el.append(name, key);
  });

  // ------------------------------------------------------------ the trade-off plane
  const BANDS = [
    [0, 100, 'n ≤ 100'],
    [101, 200, '100 < n ≤ 200'],
    [201, 300, '200 < n ≤ 300'],
    [301, 410, 'n > 300'],
  ];
  const tradeCurves = () => {
    const fits = CR.rows('fits');
    const pub = d3.greatest(CR.rows('published'), (c) => +c.score);
    const best = d3.greatest(CR.rows('frontier'), (e) => +e.score);
    const out = [];
    for (const id of ['s1', 's2']) {
      const F = fits.find((r) => r.id === id);
      if (F) out.push({ c: +F.a, label: `${f.score(+F.a)}, ${F.label.split(':')[0]} (${F.status})`, cls: 'cr-law-reg' });
    }
    if (best) out.push({ c: +best.score, label: `${f.score(+best.score)}, the census's best (${best.code})`, cls: 'cr-law-exp', accent: true });
    if (pub) out.push({ c: +pub.score, label: `${f.score(+pub.score)}, the best published (${pub.name})`, cls: 'cr-law-exp' });
    return out;
  };
  dash.draw('fr-trade', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier', 'published', 'fits'], { chart: true })) return;
    const p = dash.params();
    const all = CR.rows('frontier');
    const rows = CR.filtered(all, p);
    const pubs = CR.bool(p.pub) ? CR.rows('published') : [];
    const curves = tradeCurves();
    const kMax = d3.max(all, (e) => +e.k) + 2;
    const yMax = d3.max([...all.map((e) => +e.ratio), ...pubs.map((c) => +c.ratio)]) * 1.08;
    const by = p.color === 'stage' ? 'stage' : 'group';
    // lay the panels out first, so each is drawn at its own width
    const boxes = BANDS.map(([, , title]) => {
      const box = document.createElement('div');
      box.className = 'cr-chart';
      const h = document.createElement('div');
      h.className = 'cr-note';
      h.textContent = title;
      box.append(h);
      el.append(box);
      return box;
    });
    for (const [i, [lo, hi, title]] of BANDS.entries()) {
      const box = boxes[i];
      const x = d3.scaleLinear().domain([0, kMax]);
      const y = d3.scaleLinear().domain([0, yMax]).nice();
      const { svg } = CR.frame(box, {
        height: 210,
        x,
        y,
        xFormat: f.int,
        yFormat: d3.format('.1f'),
        xLabel: 'k',
        yLabel: 'd/√n',
        label: `k against d/√n, ${title}`,
      });
      for (const cv of curves) {
        const pts = d3.range(Math.max(2, cv.c / y.domain()[1] ** 2), kMax + 0.001, 0.25).map((k) => [k, Math.sqrt(cv.c / k)]);
        svg
          .append('path')
          .attr('class', 'cr-law ' + cv.cls)
          .attr('d', d3.line().x((q2) => x(q2[0])).y((q2) => y(q2[1]))(pts.filter((q2) => q2[1] <= y.domain()[1])));
      }
      const inBand = rows.filter((e) => +e.n >= lo && +e.n <= hi);
      svg
        .append('g')
        .selectAll('circle')
        .data(inBand)
        .join('circle')
        .attr('cx', (e) => x(+e.k))
        .attr('cy', (e) => y(+e.ratio))
        .attr('r', 4)
        .attr('stroke-width', 1.5)
        .style('fill', (e) => CR.colorOf(e, by))
        .style('stroke', 'var(--color-panel)');
      const pb = pubs.filter((c) => +c.n >= lo && +c.n <= hi);
      svg
        .append('g')
        .selectAll('path')
        .data(pb)
        .join('path')
        .attr('d', d3.symbol(d3.symbolDiamond, 72))
        .attr('transform', (c) => `translate(${x(+c.k)},${y(+c.ratio)})`)
        .attr('stroke-width', 1.5)
        .style('fill', 'var(--color-fg)')
        .style('stroke', 'var(--color-panel)');
      const pts = [
        ...inBand.map((e) => ({ x: x(+e.k), y: y(+e.ratio), d: e })),
        ...pb.map((c) => ({ x: x(+c.k), y: y(+c.ratio), d: { pub: c }, click: false })),
      ];
      CR.hover(svg, pts, {
        tip: CR.tip(box),
        describe: (d) => (d.pub ? describePub(d.pub) : describe(d)),
        onClick: (d) => CR.openCode(d.id),
      });
    }
  });
  dash.draw('fr-trade-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('frontier', 'published', 'fits')) return;
    const head = document.createElement('span');
    head.textContent = 'Curves of constant k·d²/n:';
    el.append(head);
    for (const cv of tradeCurves()) {
      const s = document.createElement('span');
      s.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw ' + (cv.cls === 'cr-law-reg' ? 'cr-sw-line' : 'cr-sw-dash');
      s.append(sw, document.createTextNode(cv.label));
      el.append(s);
    }
  });

  // the fits' formulas, where the notes name them
  for (const [name, id] of [['fr-f-edge', 'edge'], ['fr-f-layer', 'layer']]) {
    dash.draw(name, (el) => {
      if (!CR.ready(el, ['fits'])) return;
      const F = CR.rows('fits').find((r) => r.id === id);
      el.textContent = F ? F.formula : '—';
    });
  }

  // ------------------------------------------------------------ residuals
  const residChart = (el, pts, yField, label, colorBy) => {
    const vals = pts.map((e) => +e[yField]);
    const a = Math.max(2, d3.max(vals.map(Math.abs)) || 2);
    const x = d3.scaleLinear().domain([0, 410]);
    const y = d3.scaleLinear().domain([-a - 1, a + 1]).nice();
    const { svg, width, m } = CR.frame(el, {
      height: 250,
      x,
      y,
      xFormat: f.int,
      yFormat: d3.format('+d'),
      xLabel: 'n',
      yLabel: label,
      label,
    });
    svg.append('line').attr('class', 'cr-zero').attr('x1', m.left).attr('x2', width - m.right).attr('y1', y(0)).attr('y2', y(0));
    svg
      .append('g')
      .selectAll('circle')
      .data(pts)
      .join('circle')
      .attr('cx', (e) => x(+e.n))
      .attr('cy', (e) => y(+e[yField]))
      .attr('r', 4)
      .attr('stroke-width', 1.5)
      .style('fill', (e) => (colorBy ? CR.colorOf(e, colorBy) : dash.colors[0]))
      .style('stroke', 'var(--color-panel)');
    CR.hover(
      svg,
      pts.map((e) => ({ x: x(+e.n), y: y(+e[yField]), d: e })),
      {
        tip: CR.tip(el),
        describe: (e) => {
          const [title, lines] = describe(e);
          return [title, [[f.signed(+e[yField]), label], ...lines.slice(0, 2)]];
        },
        onClick: (e) => CR.openCode(e.id),
      },
    );
  };
  dash.draw('fr-resid-edge', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier'], { chart: true })) return;
    const rows = CR.filtered(CR.rows('frontier'));
    const top = d3.rollups(rows, (v) => d3.greatest(v, (e) => +e.d * 1000 + +e.score), (e) => +e.n).map((r) => r[1]);
    residChart(el, top, 'resid_edge', 'd − edge fit', null);
  });
  dash.draw('fr-resid-layer', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier'], { chart: true })) return;
    const p = dash.params();
    residChart(el, CR.filtered(CR.rows('frontier'), p), 'resid_layer', 'd − k-layer fit', p.color === 'stage' ? 'stage' : 'group');
  });

  // ------------------------------------------------------------ leaderboard
  const board = q('#fr-board');
  const sort = { key: 'score', dir: 'desc' };
  const search = q('.fr-search');
  const tierClass = (r) => String(r.tier).replace(/\s+/g, '-');
  const COLS = [
    { field: 'code', sort: (r) => +r.score },
    { field: 'torus', sort: (r) => +r.l * 1000 + +r.m },
    { field: 'group_name' },
    { field: 'score', num: true, text: (r) => f.score(+r.score), sort: (r) => +r.score },
    { field: 'ratio', num: true, text: (r) => f.ratio(+r.ratio), sort: (r) => +r.ratio },
    { field: 'stage' },
    { field: 'settled_by' },
    { field: 'tier', pill: tierClass },
  ];
  CR.wireSort(board, sort, () => dash.draw('fr-board'));
  search.addEventListener('input', () => dash.draw('fr-board'));
  dash.draw('fr-board', (tbody) => {
    if (!CR.ok('frontier')) {
      tbody.replaceChildren();
      return;
    }
    const term = search.value.trim().toLowerCase();
    let rows = CR.filtered(CR.rows('frontier'));
    if (term) rows = rows.filter((e) => [e.code, e.torus, e.group_name, e.group_type].join(' ').toLowerCase().includes(term));
    CR.fillBody(tbody, CR.sortRows(rows, sort, COLS), COLS, 'id', (r) => CR.openCode(r.id));
    tbody.querySelectorAll('tr').forEach((tr) => {
      [2, 5, 6].forEach((i) => tr.children[i].classList.add('cr-hide-narrow'));
    });
  });
})();
