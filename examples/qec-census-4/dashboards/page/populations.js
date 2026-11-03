// Populations: the distribution of d on one torus, class counts, the depth of the top, the bulk
// against the edge, and how tight the window bound is.
(function () {
  const CR = window.CR;
  const f = CR.fmt;
  const root = document.getElementById('populations');
  const q = (s) => root.querySelector(s);

  const conn = q('.po-conn');
  const weight = q('.po-weight');
  conn.addEventListener('change', () => dash.setParams({ po_conn: conn.checked }));
  weight.addEventListener('change', () => dash.setParams({ po_weight: weight.checked }));
  dash.onData(() => {
    const p = dash.params();
    conn.checked = CR.bool(p.po_conn);
    weight.checked = CR.bool(p.po_weight);
  });

  // the torus shown: the one picked, else the one holding the census's best k d^2/n
  const torusNow = (tori) => {
    const want = dash.params().po_torus;
    const withCodes = tori.filter((t) => t.status === 'settled' || t.status === 'unsettled');
    return withCodes.find((t) => t.torus === want) || d3.greatest(withCodes, (t) => +t.best_score);
  };
  dash.draw('po-torus', (s) => {
    const tori = CR.rows('tori')
      .filter((t) => t.status === 'settled' || t.status === 'unsettled')
      .sort((a, b) => a.n - b.n || a.l - b.l);
    s.replaceChildren(...tori.map((t) => new Option(`${t.torus} (n = ${t.n}, best d ${t.d_max})`, t.torus)));
    const t = tori.length ? torusNow(tori) : null;
    if (t) s.value = t.torus;
    s.onchange = () => dash.setParams({ po_torus: s.value, po_k: 'all' });
  });
  dash.draw('po-k', (s) => {
    const tori = CR.rows('tori');
    const t = tori.length ? torusNow(tori) : null;
    const ks = t ? [...new Set(CR.rows('class_hist').filter((r) => r.torus === t.torus).map((r) => +r.k))].sort((a, b) => a - b) : [];
    s.replaceChildren(new Option('All', 'all'), ...ks.map((k) => new Option(String(k), String(k))));
    const pk = dash.params().po_k;
    s.value = pk === null || pk === undefined || !ks.includes(+pk) ? 'all' : String(pk);
    s.onchange = () => dash.setParams({ po_k: s.value === 'all' ? 'all' : +s.value });
  });

  // ------------------------------------------------------------ one torus's distribution
  dash.draw('po-hist', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['class_hist', 'tori'], { chart: true })) return;
    const p = dash.params();
    const t = torusNow(CR.rows('tori'));
    if (!t) return;
    const useWeight = CR.bool(p.po_weight) && t.stage === '3a';
    const rows = CR.rows('class_hist').filter(
      (r) => r.torus === t.torus && (!CR.bool(p.po_conn) || CR.bool(r.connected)) && (p.po_k === 'all' || p.po_k === null || p.po_k === undefined || +r.k === +p.po_k),
    );
    const sum = (kind) => d3.rollup(rows.filter((r) => r.kind === kind), (v) => d3.sum(v, (r) => +(useWeight ? r.codes : r.classes) || 0), (r) => +r.value);
    const exact = sum('exact');
    const windowed = sum('window');
    const values = [...new Set([...exact.keys(), ...windowed.keys()])].sort((a, b) => a - b);
    if (!values.length) return;
    const series = windowed.size ? ['exact', 'window'] : ['exact'];
    const x0 = d3.scaleBand().domain(values);
    const yMax = d3.max([...exact.values(), ...windowed.values()]);
    const y = d3.scaleLinear().domain([0, yMax]).nice();
    // a band scale has no ticks(): draw the frame with a linear stand-in, then place bands
    const xl = d3.scaleLinear().domain([d3.min(values) - 1, d3.max(values) + 1]);
    const { svg, width, m } = CR.frame(el, {
      height: 270,
      x: xl,
      xValues: values,
      y,
      xFormat: f.int,
      yFormat: f.compact,
      xLabel: series.length > 1 ? 'd, or the window bound on d' : 'd',
      yLabel: useWeight ? 'Codes' : 'Classes',
      label: `The distribution of d on ${t.torus}`,
    });
    x0.range([xl(d3.min(values) - 1), xl(d3.max(values) + 1)]).paddingInner(0.25).paddingOuter(0.5);
    const x1 = d3.scaleBand().domain(series).range([0, x0.bandwidth()]).padding(0.08);
    const bw = Math.min(24, x1.bandwidth());
    const bars = [];
    for (const v of values)
      for (const s of series) {
        const c = (s === 'exact' ? exact : windowed).get(v) || 0;
        if (c) bars.push({ v, s, c });
      }
    svg
      .append('g')
      .selectAll('path')
      .data(bars)
      .join('path')
      .attr('d', (b) => {
        const bx = x0(b.v) + x1(b.s) + (x1.bandwidth() - bw) / 2;
        const top = y(b.c);
        const bottom = y(0);
        const r = Math.min(4, bw / 2, bottom - top);
        return `M${bx},${bottom}V${top + r}Q${bx},${top} ${bx + r},${top}H${bx + bw - r}Q${bx + bw},${top} ${bx + bw},${top + r}V${bottom}Z`;
      })
      .style('fill', (b) => dash.colors[b.s === 'exact' ? 0 : 1]);
    // the best d and two below it
    const dm = +t.d_max;
    for (const [v, label] of [[dm, 'best d'], [dm - 2, 'best − 2']]) {
      if (!values.includes(v) && v !== dm) continue;
      const cx = xl(v);
      svg.append('line').attr('class', 'cr-zero').attr('x1', cx).attr('x2', cx).attr('y1', m.top).attr('y2', y(0));
      svg
        .append('text')
        .attr('class', 'cr-tick')
        .attr('x', cx + (v === dm ? 4 : -4))
        .attr('y', m.top + 10)
        .attr('text-anchor', v === dm ? 'start' : 'end')
        .text(label);
    }
    const hov = bars.map((b) => ({ x: x0(b.v) + x1(b.s) + x1.bandwidth() / 2, y: y(b.c / 2), d: b, click: false }));
    CR.hover(svg, hov, {
      tip: CR.tip(el),
      radius: Math.max(16, x0.step()),
      describe: (b) => [
        `${t.torus}, ${b.s === 'exact' ? 'd' : 'window bound'} = ${b.v}`,
        [[f.int(b.c), `${useWeight ? 'codes' : 'classes'}${b.s === 'exact' ? ' with this exact d' : ' bounded at this value'}`]],
      ],
    });
    void width;
  });

  // ------------------------------------------------------------ classes per torus
  const stageColor = (t) => dash.colors[Math.max(0, CR.STAGES.indexOf(t.stage))];
  dash.draw('po-classes', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tori', 'fits'], { chart: true })) return;
    const tori = CR.rows('tori').filter((t) => +t.classes > 0);
    const F = CR.rows('fits').find((r) => r.id === 'classes');
    const x = d3.scaleLinear().domain([0, 410]);
    const lo = 1;
    const hi = d3.max(tori, (t) => +t.classes);
    const y = d3.scaleLog().domain([lo, hi * 1.5]);
    const yv = d3.range(0, Math.ceil(Math.log10(hi * 1.5)) + 1).map((e) => 10 ** e).filter((v) => v <= hi * 1.5);
    const { svg } = CR.frame(el, { height: 260, x, y, yValues: yv, xFormat: f.int, yFormat: f.compact, xLabel: 'n', yLabel: 'Classes (log)', label: 'Classes per torus against n' });
    if (F) {
      const pts = d3.range(12, 401, 4).map((n) => [n, +F.a * n ** +F.b]).filter((p2) => p2[1] >= lo);
      svg.append('path').attr('class', 'cr-law cr-law-exp').attr('d', d3.line().x((p2) => x(p2[0])).y((p2) => y(p2[1]))(pts));
    }
    svg
      .append('g')
      .selectAll('circle')
      .data(tori)
      .join('circle')
      .attr('cx', (t) => x(+t.n))
      .attr('cy', (t) => y(+t.classes))
      .attr('r', 3.5)
      .attr('stroke-width', 1.5)
      .style('fill', stageColor)
      .style('stroke', 'var(--color-panel)');
    CR.hover(svg, tori.map((t) => ({ x: x(+t.n), y: y(+t.classes), d: t, click: false })), {
      tip: CR.tip(el),
      describe: (t) => [t.torus, [[f.int(+t.classes), 'classes'], [`n = ${t.n}`, `stage ${t.stage}`]]],
    });
  });
  dash.draw('po-classes-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('fits')) return;
    for (const [i, s] of CR.STAGES.entries()) {
      const k = document.createElement('span');
      k.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw';
      sw.style.background = dash.colors[i];
      k.append(sw, document.createTextNode(`Stage ${s}`));
      el.append(k);
    }
    const F = CR.rows('fits').find((r) => r.id === 'classes');
    if (F) {
      const k = document.createElement('span');
      k.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw cr-sw-dash';
      k.append(sw, document.createTextNode(`${F.label} (exploratory)`));
      el.append(k);
    }
  });

  // ------------------------------------------------------------ the depth of the top
  dash.draw('po-depth', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tori'], { chart: true })) return;
    const tori = CR.rows('tori').filter((t) => +t.top_count > 0 && CR.bool(t.primary));
    const x = d3.scaleLinear().domain([0, 410]);
    const hi = d3.max(tori, (t) => Math.max(+t.top_count, +t.next_count || 0));
    const y = d3.scaleLog().domain([0.8, hi * 1.5]);
    const yv = d3.range(0, Math.ceil(Math.log10(hi * 1.5)) + 1).map((e) => 10 ** e).filter((v) => v <= hi * 1.5);
    const { svg } = CR.frame(el, { height: 260, x, y, yValues: yv, xFormat: f.int, yFormat: f.compact, xLabel: 'n', yLabel: 'Classes (log)', label: 'Classes at and below the best d, per torus' });
    const pts = [];
    for (const t of tori) {
      pts.push({ x: x(+t.n), y: y(+t.top_count), d: { t, which: 'top' }, click: false });
      if (+t.next_count > 0) pts.push({ x: x(+t.n), y: y(+t.next_count), d: { t, which: 'next' }, click: false });
    }
    svg
      .append('g')
      .selectAll('circle')
      .data(pts)
      .join('circle')
      .attr('cx', (p2) => p2.x)
      .attr('cy', (p2) => p2.y)
      .attr('r', 3.5)
      .attr('stroke-width', 1.5)
      .style('fill', (p2) => dash.colors[p2.d.which === 'top' ? 0 : 1])
      .style('stroke', 'var(--color-panel)');
    CR.hover(svg, pts, {
      tip: CR.tip(el),
      describe: (d) => [
        `${d.t.torus}, best d = ${d.t.d_max}`,
        [[f.int(d.which === 'top' ? +d.t.top_count : +d.t.next_count), d.which === 'top' ? 'classes at the best d' : `classes at d = ${d.t.d_max - 2}${d.t.stage === '3a' ? '' : ' (at least)'}`]],
      ],
    });
  });

  // ------------------------------------------------------------ the bulk against the edge
  const BULK = [['median', 'Median d', 'bulk_median'], ['p90', '90th percentile', 'bulk_p90'], ['max', 'Largest d', 'bulk_max']];
  dash.draw('po-bulk', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['bulk', 'fits'], { chart: true })) return;
    const rows = CR.rows('bulk');
    const fits = CR.rows('fits');
    const x = d3.scaleLinear().domain([0, d3.max(rows, (r) => +r.n) + 4]);
    const y = d3.scaleLinear().domain([0, d3.max(rows, (r) => +r.max) + 2]).nice();
    const { svg } = CR.frame(el, { height: 260, x, y, xFormat: f.int, yFormat: f.int, xLabel: 'n (stage 3a)', yLabel: 'd', label: 'The median, 90th percentile and largest d at each n' });
    for (const [i, [col, , fid]] of BULK.entries()) {
      const F = fits.find((r) => r.id === fid);
      if (F) {
        const pts = d3.range(30, d3.max(rows, (r) => +r.n) + 1, 2).map((n) => [n, +F.a * n ** +F.b]);
        svg.append('path').attr('class', 'cr-law cr-law-exp').attr('d', d3.line().x((p2) => x(p2[0])).y((p2) => y(p2[1]))(pts));
      }
      svg
        .append('path')
        .attr('d', d3.line().x((r) => x(+r.n)).y((r) => y(+r[col]))(rows))
        .attr('fill', 'none')
        .attr('stroke-width', 2)
        .attr('stroke-linejoin', 'round')
        .attr('stroke-linecap', 'round')
        .style('stroke', dash.colors[i]);
    }
    const hov = rows.map((r) => ({ x: x(+r.n), y: y(+r.p90), d: r, click: false }));
    CR.hover(svg, hov, {
      tip: CR.tip(el),
      radius: 40,
      describe: (r) => [
        `n = ${r.n}, ${f.int(+r.classes)} classes`,
        BULK.map(([col, name], i) => [d3.format('.1f')(+r[col]), name, dash.colors[i]]),
      ],
    });
  });
  dash.draw('po-bulk-legend', (el) => {
    el.replaceChildren();
    if (!CR.ok('fits')) return;
    const fits = CR.rows('fits');
    for (const [i, [, name, fid]] of BULK.entries()) {
      const k = document.createElement('span');
      k.className = 'cr-key';
      const sw = document.createElement('span');
      sw.className = 'cr-sw cr-sw-line';
      sw.style.borderTopColor = dash.colors[i];
      sw.style.borderTopWidth = '2px';
      const F = fits.find((r) => r.id === fid);
      k.append(sw, document.createTextNode(F ? `${name}: fit ${F.formula}` : name));
      el.append(k);
    }
    const F0 = fits.find((r) => r.id === 'bulk_median');
    const k = document.createElement('span');
    k.className = 'cr-key';
    const sw = document.createElement('span');
    sw.className = 'cr-sw cr-sw-dash';
    k.append(sw, document.createTextNode(`the fits: exploratory, ${F0 ? F0.study.replace(/^this dashboard \(|\)$/g, '') : ''}`));
    el.append(k);
  });

  // ------------------------------------------------------------ window tightness
  dash.draw('po-tight', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tightness'], { chart: true })) return;
    const rows = CR.rows('tightness');
    const stages = ['3b/3c', '4'];
    const tot = d3.rollup(rows, (v) => d3.sum(v, (r) => +r.classes), (r) => r.stage);
    const gaps = [...new Set(rows.map((r) => +r.gap))].sort((a, b) => a - b);
    const share = (s, g) => {
      const r = rows.find((x2) => x2.stage === s && +x2.gap === g);
      return r ? +r.classes / tot.get(s) : 0;
    };
    const xl = d3.scaleLinear().domain([gaps[0] - 1, gaps[gaps.length - 1] + 1]);
    const y = d3.scaleLinear().domain([0, 1]);
    const { svg } = CR.frame(el, { height: 200, x: xl, xValues: gaps, y, xFormat: f.int, yFormat: d3.format('.0%'), xLabel: 'window bound − exact d', yLabel: 'Share', label: 'Window bound minus exact d' });
    const x0 = d3.scaleBand().domain(gaps).range([xl(gaps[0] - 1), xl(gaps[gaps.length - 1] + 1)]).paddingInner(0.3).paddingOuter(0.5);
    const x1 = d3.scaleBand().domain(stages).range([0, x0.bandwidth()]).padding(0.08);
    const bw = Math.min(24, x1.bandwidth());
    const bars = [];
    for (const g of gaps) for (const s of stages) bars.push({ g, s, v: share(s, g), c: (rows.find((x2) => x2.stage === s && +x2.gap === g) || {}).classes || 0 });
    svg
      .append('g')
      .selectAll('rect')
      .data(bars.filter((b) => b.v > 0))
      .join('rect')
      .attr('x', (b) => x0(b.g) + x1(b.s) + (x1.bandwidth() - bw) / 2)
      .attr('y', (b) => y(b.v))
      .attr('width', bw)
      .attr('height', (b) => Math.max(1, y(0) - y(b.v)))
      .attr('rx', 2)
      .style('fill', (b) => dash.colors[stages.indexOf(b.s)]);
    CR.hover(svg, bars.filter((b) => b.v > 0).map((b) => ({ x: x0(b.g) + x1(b.s) + x1.bandwidth() / 2, y: y(b.v / 2), d: b, click: false })), {
      tip: CR.tip(el),
      radius: 30,
      describe: (b) => [`Stage ${b.s}, bound − d = ${b.g}`, [[f.pct(b.v), `${f.int(+b.c)} classes`]]],
    });
  });
  dash.draw('po-share', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['tori'], { chart: true })) return;
    const tori = CR.rows('tori').filter((t) => t.stage !== '3a' && +t.classes > 0 && t.exact_share !== null);
    const x = d3.scaleLinear().domain([Math.floor((d3.min(tori, (t) => +t.n) - 10) / 20) * 20, 410]);
    const y = d3.scaleLinear().domain([0, 1]);
    const { svg } = CR.frame(el, { height: 220, x, y, xFormat: f.int, yFormat: d3.format('.0%'), xLabel: 'n', yLabel: 'Classes run exactly', label: 'Share of classes run exactly, per torus' });
    svg
      .append('g')
      .selectAll('circle')
      .data(tori)
      .join('circle')
      .attr('cx', (t) => x(+t.n))
      .attr('cy', (t) => y(+t.exact_share))
      .attr('r', 3.5)
      .attr('stroke-width', 1.5)
      .style('fill', (t) => dash.colors[t.stage === '4' ? 1 : 0])
      .style('stroke', 'var(--color-panel)');
    CR.hover(svg, tori.map((t) => ({ x: x(+t.n), y: y(+t.exact_share), d: t, click: false })), {
      tip: CR.tip(el),
      describe: (t) => [t.torus, [[f.pct(+t.exact_share), `of ${f.int(+t.classes)} classes run exactly`], [`stage ${t.stage}`, '']]],
    });
  });
})();
