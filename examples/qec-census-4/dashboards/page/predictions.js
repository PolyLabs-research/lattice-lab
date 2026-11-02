// Predictions: the scorecard of every registered study, one study's predictions, the census laws
// against their data, and the timeline.
(function () {
  const CR = window.CR;
  const f = CR.fmt;
  const root = document.getElementById('predictions');
  const area = root.querySelector('.pr-area');
  area.addEventListener('change', () => dash.setParams({ pr_area: area.value, pr_study: null }));
  dash.onData(() => {
    area.value = dash.params().pr_area || 'all';
  });
  const slug = (s) => String(s || 'none').replace(/\s+/g, '-');
  const inArea = (s, a) => !a || a === 'all' || (a === 'codes' ? CR.bool(s.codes) : s.area === a);
  const shown = () => {
    const a = dash.params().pr_area;
    return CR.rows('studies')
      .filter((s) => inArea(s, a))
      .sort((x, y) => String(x.registered).localeCompare(String(y.registered)));
  };
  const picked = () => {
    const list = shown();
    const want = dash.params().pr_study;
    return list.find((s) => s.study === want) || list.find((s) => s.study === 'qec-census-4') || list[list.length - 1];
  };

  dash.draw('pr-studies', (tbody) => {
    if (!CR.ok('studies')) {
      tbody.replaceChildren();
      return;
    }
    const cur = picked();
    CR.fillBody(
      tbody,
      shown(),
      [
        { field: 'title' },
        { field: 'outcome', pill: (r) => slug(r.outcome === 'pending' ? 'incomplete' : r.outcome) },
        { field: 'claims_held', num: true },
        { field: 'claims_failed', num: true },
        { field: 'claims_other', num: true },
        { field: 'candidates_rejected', num: true },
        { field: 'registered' },
        { field: 'summary' },
      ],
      'study',
      (r) => dash.setParams({ pr_study: r.study }),
    );
    tbody.querySelectorAll('tr').forEach((tr) => {
      [4, 5, 6, 7].forEach((i) => tr.children[i].classList.add('cr-hide-narrow'));
      tr.children[0].classList.add('cr-wrap');
      tr.children[7].classList.add('cr-wrap');
      if (cur && tr.getAttribute('data-key') === cur.study) tr.setAttribute('aria-selected', 'true');
    });
  });
  dash.draw('pr-study-name', (el) => {
    if (!CR.ready(el, ['studies'])) return;
    const s = picked();
    if (!s) {
      el.textContent = '—';
      return;
    }
    el.setAttribute('data-where', 'study=' + s.study);
    el.textContent = s.title;
  });
  dash.draw('pr-preds', (tbody) => {
    if (!CR.ok('predictions', 'studies')) {
      tbody.replaceChildren();
      return;
    }
    const s = picked();
    const rows = s ? CR.rows('predictions').filter((p) => p.study === s.study) : [];
    CR.fillBody(
      tbody,
      rows,
      [{ field: 'label' }, { field: 'role' }, { field: 'outcome', pill: (r) => slug(r.outcome) }, { field: 'note' }, { field: 'text' }],
      'key',
    );
    tbody.querySelectorAll('tr').forEach((tr) => {
      [3, 4].forEach((i) => tr.children[i].classList.add('cr-hide-narrow', 'cr-wrap'));
    });
  });

  // ------------------------------------------------------------ the census laws against the data
  const evenDown = (x) => {
    const v = Math.floor(x);
    return v - (((v % 2) + 2) % 2);
  };
  dash.draw('pr-laws', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier', 'fits', 'studies'], { chart: true })) return;
    const fr = CR.rows('frontier').filter((e) => !CR.bool(e.exposed));
    const fits = CR.rows('fits');
    const F = (id) => fits.find((r) => r.id === id);
    const studies = CR.rows('studies');
    const reg = (id) => (studies.find((s) => s.study === id) || {}).registered || '';
    // one point per torus: its best d, or its best k d^2/n
    const perTorus = (rows, key) => [...d3.group(rows, (e) => e.torus).values()].map((v) => d3.greatest(v, (e) => +e[key]));
    const panels = [];
    if (F('p2'))
      panels.push({
        title: `${F('p2').label}: ${F('p2').status}`, sub: `registered ${reg('qec-census-3b')} UTC in qec-census-3b`,
        rows: perTorus(fr.filter((e) => e.stage === '3b/3c'), 'd'), y: (e) => +e.d, yLabel: 'best d',
        lines: [{ fn: (n) => evenDown(+F('p2').a * Math.sqrt(n)), step: true }],
        breaks: (e) => +e.d > evenDown(+F('p2').a * Math.sqrt(+e.n)),
      });
    if (F('e'))
      panels.push({
        title: `${F('e').label}: ${F('e').status}`, sub: `registered ${reg('qec-census-4')} UTC in qec-census-4`,
        rows: perTorus(fr.filter((e) => e.stage === '4'), 'd'), y: (e) => +e.d, yLabel: 'best d',
        lines: [{ fn: (n) => evenDown(+F('e').a * n ** +F('e').b), step: true }],
        breaks: (e) => +e.d > evenDown(+F('e').a * (+e.n) ** +F('e').b),
      });
    if (F('s1') && F('s2'))
      panels.push({
        title: `S1 and S2 on k·d²/n: ${F('s1').status}, ${F('s2').status}`, sub: `registered ${reg('qec-census-4')} UTC in qec-census-4`,
        rows: perTorus(fr.filter((e) => e.stage === '4'), 'score'), y: (e) => +e.score, yLabel: 'best k·d²/n',
        lines: [{ fn: () => +F('s1').a }, { fn: () => +F('s2').a }],
        breaks: (e) => +e.score > +F('s2').a,
      });
    const boxes = panels.map((pn) => {
      const box = document.createElement('div');
      box.className = 'cr-chart';
      const h = document.createElement('div');
      h.className = 'cr-note';
      h.textContent = `${pn.title} (${pn.sub})`;
      box.append(h);
      el.append(box);
      return box;
    });
    panels.forEach((pn, i) => {
      const box = boxes[i];
      const ns = pn.rows.map((e) => +e.n);
      const lo = d3.min(ns) - 6;
      const hi = d3.max(ns) + 6;
      const x = d3.scaleLinear().domain([lo, hi]);
      const yMax = d3.max([...pn.rows.map(pn.y), ...pn.lines.map((l) => l.fn(hi))]);
      const y = d3.scaleLinear().domain([0, yMax * 1.08]).nice();
      const { svg } = CR.frame(box, { height: 220, x, y, xFormat: f.int, yFormat: d3.format('~f'), xLabel: 'n', yLabel: pn.yLabel, label: pn.title });
      for (const l of pn.lines) {
        const pts = d3.range(lo + (lo % 2), hi + 1, 2).map((n) => [n, l.fn(n)]);
        svg.append('path').attr('class', 'cr-law cr-law-reg').attr('d', d3.line().x((q) => x(q[0])).y((q) => y(q[1])).curve(l.step ? d3.curveStepAfter : d3.curveLinear)(pts));
      }
      svg
        .append('g')
        .selectAll('circle')
        .data(pn.rows)
        .join('circle')
        .attr('cx', (e) => x(+e.n))
        .attr('cy', (e) => y(pn.y(e)))
        .attr('r', 3.5)
        .attr('stroke-width', 1.5)
        .style('fill', dash.colors[0])
        .style('stroke', 'var(--color-panel)');
      svg
        .append('g')
        .selectAll('circle')
        .data(pn.rows.filter(pn.breaks))
        .join('circle')
        .attr('cx', (e) => x(+e.n))
        .attr('cy', (e) => y(pn.y(e)))
        .attr('r', 7)
        .attr('fill', 'none')
        .attr('stroke-width', 1.5)
        .style('stroke', 'var(--cds-chart-status-critical)');
      CR.hover(svg, pn.rows.map((e) => ({ x: x(+e.n), y: y(pn.y(e)), d: e })), {
        tip: CR.tip(box),
        describe: (e) => [`${e.code} on ${e.torus}`, [[d3.format('~f')(pn.y(e)), pn.yLabel], [pn.breaks(e) ? 'breaks the law' : 'within the law', '']]],
        onClick: (e) => CR.openCode(e.id),
      });
    });
  });

  // ------------------------------------------------------------ timeline
  const OUT_COLOR = { held: 'var(--color-ok)', failed: 'var(--color-bad)', mixed: 'var(--color-warn)' };
  dash.draw('pr-timeline', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['studies', 'summary'], { chart: true })) return;
    const rows = shown();
    if (!rows.length) return;
    const built = new Date(CR.metric(CR.rows('summary'), 'built_at').text.replace(' UTC', '').replace(' ', 'T') + ':00Z');
    const t = (s) => (s ? new Date(s.replace(' ', 'T') + ':00Z') : null);
    const width = Math.max(300, el.clientWidth || 700);
    const svg = CR.svg(el, width, 10, 'Studies from registration to verdict');
    const left = Math.ceil(CR.measure(svg, rows.map((r) => r.study))) + 12;
    const m = { top: 6, right: 16, bottom: 30, left };
    const rowH = 18;
    const height = m.top + m.bottom + rowH * rows.length;
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    const x = d3.scaleUtc().domain([d3.min(rows, (r) => t(r.registered)), built]).range([m.left, width - m.right]).nice();
    const y = d3.scaleBand().domain(rows.map((r) => r.study)).range([m.top, height - m.bottom]).paddingInner(0.3);
    const fmtDay = d3.utcFormat('%b %-d');
    let xt = [];
    for (let c = 10; c >= 2; c--) {
      xt = x.ticks(c);
      if (xt.reduce((s, v) => s + CR.measure(svg, [fmtDay(v)]) + 14, 0) <= width - m.left - m.right) break;
    }
    svg.append('g').attr('class', 'cr-grid').selectAll('line').data(xt).join('line').attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', m.top).attr('y2', height - m.bottom);
    const ax = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(0,${height - m.bottom})`).call(d3.axisBottom(x).tickValues(xt).tickFormat(fmtDay).tickSize(3));
    const ay = svg.append('g').attr('class', 'cr-axis').attr('transform', `translate(${m.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(6));
    for (const a of [ax, ay]) a.attr('font-size', null).attr('font-family', null).select('.domain').remove();
    const end = (r) => t(r.verdict_time) || built;
    svg
      .append('g')
      .selectAll('line')
      .data(rows)
      .join('line')
      .attr('x1', (r) => x(t(r.registered)))
      .attr('x2', (r) => Math.max(x(t(r.registered)) + 2, x(end(r))))
      .attr('y1', (r) => y(r.study) + y.bandwidth() / 2)
      .attr('y2', (r) => y(r.study) + y.bandwidth() / 2)
      .attr('stroke-width', 2)
      .attr('stroke-linecap', 'round')
      .style('stroke', 'var(--cds-chart-muted)');
    svg
      .append('g')
      .selectAll('circle')
      .data(rows)
      .join('circle')
      .attr('cx', (r) => x(end(r)))
      .attr('cy', (r) => y(r.study) + y.bandwidth() / 2)
      .attr('r', 5)
      .attr('stroke-width', 1.5)
      .style('fill', (r) => OUT_COLOR[r.outcome] || 'var(--color-panel)')
      .style('stroke', (r) => (OUT_COLOR[r.outcome] ? 'var(--color-panel)' : 'var(--color-fg-muted)'));
    CR.hover(svg, rows.map((r) => ({ x: x(end(r)), y: y(r.study) + y.bandwidth() / 2, d: r })), {
      tip: CR.tip(el),
      radius: 20,
      describe: (r) => [r.title, [[r.outcome, r.summary.slice(0, 80)], [`registered ${r.registered}`, r.verdict_time ? `verdict ${r.verdict_time}` : 'no verdict yet']]],
      onClick: (r) => dash.setParams({ pr_study: r.study }),
    });
  });
})();
