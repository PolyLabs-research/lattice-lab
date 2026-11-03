// Code card: one frontier entry in full.
(function () {
  const CR = window.CR;
  const f = CR.fmt;

  document.querySelector('#dash-root .cr-back').addEventListener('click', () => CR.show(CR.prev || 'frontier'));

  // the entry shown: the one picked, else the census's best by k d^2/n
  const current = () => {
    const rows = CR.rows('frontier');
    const id = dash.params().code;
    return rows.find((e) => e.id === id) || d3.greatest(rows, (e) => +e.score);
  };
  const at = (el, e) => el.setAttribute('data-where', 'id=' + e.id);

  dash.draw('c-pick', (s) => {
    const rows = CR.rows('frontier').slice().sort((a, b) => b.score - a.score || a.n - b.n);
    s.replaceChildren(...rows.map((e) => new Option(`${e.code} on ${e.torus} (k·d²/n ${f.score(+e.score)})`, e.id)));
    const e = rows.length ? current() : null;
    if (e) s.value = e.id;
    s.onchange = () => dash.setParams({ code: s.value });
  });

  // one field of the entry
  const field = (name, col, format) =>
    dash.draw(name, (el) => {
      if (!CR.ready(el, ['frontier'])) return;
      const e = current();
      if (!e) {
        el.textContent = '—';
        return;
      }
      at(el, e);
      const v = e[col];
      el.textContent = v === null || v === undefined || v === '' ? '—' : format ? format(v) : String(v);
    });
  field('c-name', 'code');
  field('c-torus', 'torus');
  field('c-group', 'group_name');
  field('c-score', 'score', (v) => f.score(+v));
  field('c-ratio', 'ratio', (v) => f.ratio(+v));
  field('c-stage', 'stage');
  field('c-settled', 'settled_by');
  field('c-tier', 'tier');
  field('c-sgroup', 'study_group');
  field('c-A', 'A_text');
  field('c-B', 'B_text');
  field('c-file', 'source_file');
  field('c-line', 'source_line', (v) => String(v));
  field('c-instr', 'instrument');
  field('c-seen', 'first_seen');
  field('c-tsrc', 'tier_source');
  field('c-iso', 'iso_rep');

  dash.draw('c-near', (el) => {
    if (!CR.ready(el, ['frontier', 'published'])) return;
    const e = current();
    const pubs = CR.rows('published');
    const near = e && d3.least(pubs, (c) => Math.abs(+c.n - +e.n) * 1000 - +c.score);
    if (!near) {
      el.textContent = '—';
      return;
    }
    const enc = (v) => String(v).replace(/%/g, '%25').replace(/&/g, '%26').replace(/=/g, '%3D');
    el.setAttribute('data-where', 'name=' + enc(near.name));
    el.textContent = near.name;
  });

  // the torus grid, l rows by m columns, cell size from the width
  const grid = (el, ell, m, height0) => {
    const width = Math.max(240, el.clientWidth || 500);
    const cell = Math.max(4, Math.min(22, Math.floor((width - 40) / m)));
    const gw = cell * m;
    const gh = cell * ell;
    return { width, cell, gw, gh, ox: Math.max(28, (width - gw) / 2), height: height0 + gh };
  };
  const cellDots = (g, ell, m, cell, ox, oy) => {
    const pts = [];
    for (let i = 0; i < ell; i++) for (let j = 0; j < m; j++) pts.push([i, j]);
    g.append('g')
      .selectAll('circle')
      .data(pts)
      .join('circle')
      .attr('cx', (p) => ox + p[1] * cell + cell / 2)
      .attr('cy', (p) => oy + p[0] * cell + cell / 2)
      .attr('r', Math.max(0.8, cell / 9))
      .style('fill', 'var(--cds-chart-muted)');
  };

  dash.draw('c-stencil', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier'], { chart: true })) return;
    const e = current();
    if (!e || !e.A) return;
    const ell = +e.l;
    const m = +e.m;
    const G = grid(el, ell, m, 34);
    const svg = CR.svg(el, G.width, G.height, `The stencils of A and B on the ${e.torus} torus`);
    const oy = 6;
    cellDots(svg, ell, m, G.cell, G.ox, oy);
    const A = JSON.parse(e.A);
    const B = JSON.parse(e.B);
    const r = Math.max(2.5, G.cell * 0.38);
    svg
      .append('g')
      .selectAll('circle')
      .data(A)
      .join('circle')
      .attr('cx', (q) => G.ox + q[1] * G.cell + G.cell / 2)
      .attr('cy', (q) => oy + q[0] * G.cell + G.cell / 2)
      .attr('r', r)
      .attr('stroke-width', 1.5)
      .style('fill', dash.colors[0])
      .style('stroke', 'var(--color-panel)');
    svg
      .append('g')
      .selectAll('rect')
      .data(B)
      .join('rect')
      .attr('x', (q) => G.ox + q[1] * G.cell + G.cell / 2 - r * 0.85)
      .attr('y', (q) => oy + q[0] * G.cell + G.cell / 2 - r * 0.85)
      .attr('width', r * 1.7)
      .attr('height', r * 1.7)
      .attr('rx', 1.5)
      .attr('stroke-width', 1.5)
      .style('fill', dash.colors[1])
      .style('stroke', 'var(--color-panel)');
    svg
      .append('text')
      .attr('class', 'cr-axis-label')
      .attr('x', G.ox)
      .attr('y', oy + G.gh + 18)
      .text(`${ell} × ${m}: rows are the l direction (x), columns the m direction (y)`);
  });

  dash.draw('c-witness', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier'], { chart: true })) return;
    const e = current();
    if (!e || !e.witness) return;
    const ell = +e.l;
    const m = +e.m;
    const lm = ell * m;
    const W = JSON.parse(e.witness);
    const G = grid(el, ell, m, 0);
    const gap = 30;
    const height = 6 + 2 * G.gh + gap + 26;
    const svg = CR.svg(el, G.width, height, `A weight-${e.d} logical of ${e.code}`);
    const blocks = [
      [0, 6, 'Left block'],
      [lm, 6 + G.gh + gap, 'Right block'],
    ];
    for (const [base, oy, name] of blocks) {
      cellDots(svg, ell, m, G.cell, G.ox, oy);
      const on = W.filter((t) => t >= base && t < base + lm).map((t) => [Math.floor((t - base) / m), (t - base) % m]);
      svg
        .append('g')
        .selectAll('rect')
        .data(on)
        .join('rect')
        .attr('x', (q) => G.ox + q[1] * G.cell + 1)
        .attr('y', (q) => oy + q[0] * G.cell + 1)
        .attr('width', Math.max(2, G.cell - 2))
        .attr('height', Math.max(2, G.cell - 2))
        .attr('rx', Math.min(3, G.cell / 4))
        .style('fill', dash.colors[0]);
      svg
        .append('text')
        .attr('class', 'cr-axis-label')
        .attr('x', G.ox)
        .attr('y', oy + G.gh + 14)
        .text(`${name}: ${on.length} of the ${W.length} qubits`);
    }
  });

  dash.draw('c-profile', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['frontier', 'published'], { chart: true })) return;
    const e = current();
    if (!e) return;
    const mine = CR.rows('frontier')
      .filter((r) => r.torus === e.torus)
      .sort((a, b) => a.k - b.k);
    const pubs = CR.rows('published').filter((c) => +c.n === +e.n);
    const kMax = d3.max([...mine.map((r) => +r.k), ...pubs.map((c) => +c.k)]) + 2;
    const dMax = d3.max([...mine.map((r) => +r.d), ...pubs.map((c) => +c.d)]) + 2;
    const x = d3.scaleLinear().domain([0, kMax]);
    const y = d3.scaleLinear().domain([0, dMax]).nice();
    const { svg } = CR.frame(el, {
      height: 250,
      x,
      y,
      xFormat: f.int,
      yFormat: f.int,
      xLabel: 'k',
      yLabel: 'd',
      label: `Best d against k on ${e.torus}`,
    });
    svg
      .append('path')
      .attr('d', d3.line().x((r) => x(+r.k)).y((r) => y(+r.d))(mine))
      .attr('fill', 'none')
      .attr('stroke-width', 2)
      .attr('stroke-linejoin', 'round')
      .attr('stroke-linecap', 'round')
      .style('stroke', dash.colors[0]);
    svg
      .append('g')
      .selectAll('circle')
      .data(mine)
      .join('circle')
      .attr('cx', (r) => x(+r.k))
      .attr('cy', (r) => y(+r.d))
      .attr('r', (r) => (r.id === e.id ? 6 : 4))
      .attr('stroke-width', (r) => (r.id === e.id ? 2.5 : 1.5))
      .style('fill', dash.colors[0])
      .style('stroke', (r) => (r.id === e.id ? 'var(--color-fg)' : 'var(--color-panel)'));
    svg
      .append('g')
      .selectAll('path')
      .data(pubs)
      .join('path')
      .attr('d', d3.symbol(d3.symbolDiamond, 72))
      .attr('transform', (c) => `translate(${x(+c.k)},${y(+c.d)})`)
      .attr('stroke-width', 1.5)
      .style('fill', 'var(--color-fg)')
      .style('stroke', 'var(--color-panel)');
    CR.hover(
      svg,
      [
        ...mine.map((r) => ({ x: x(+r.k), y: y(+r.d), d: r })),
        ...pubs.map((c) => ({ x: x(+c.k), y: y(+c.d), d: { pub: c }, click: false })),
      ],
      {
        tip: CR.tip(el),
        describe: (d) =>
          d.pub
            ? [d.pub.name, [['published', ''], [f.score(+d.pub.score), 'k·d²/n']]]
            : [d.code, [[`k = ${d.k}, d = ${d.d}`, ''], [f.score(+d.score), 'k·d²/n']]],
        onClick: (d) => CR.openCode(d.id),
      },
    );
  });
})();
