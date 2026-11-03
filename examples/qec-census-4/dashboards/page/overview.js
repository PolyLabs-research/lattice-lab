// Overview: headline figures, the registered laws, the stage 4 run, new frontier entries.
(function () {
  const CR = window.CR;
  const f = CR.fmt;

  // legend swatches take the series colours (a style, set once)
  ['.cr-c0', '.cr-c1', '.cr-c2'].forEach((sel, i) => {
    document.querySelectorAll('#dash-root ' + sel).forEach((e) => {
      e.style.background = dash.colors[i];
    });
  });

  // header and tiles: one summary value each
  const M = CR.metricDraw;
  M('h-best-code', 'best_score', 'text');
  M('h-best-torus', 'best_score_torus', 'text');
  M('h-best-score', 'best_score', 'value', f.score1);
  M('h-s4-done', 'stage4_done', 'value', f.int);
  M('h-s4-total', 'stage4_total', 'value', f.int);
  M('h-commit', 'commit', 'text');
  M('h-built', 'built_at', 'text');
  M('t-score', 'best_score', 'value', f.score1);
  M('t-score-code', 'best_score', 'text');
  M('t-pub-n', 'published_best_at_or_below_n', 'value', f.int);
  M('t-pub-score', 'published_best_at_or_below', 'value', f.score1);
  M('t-pub-name', 'published_best_at_or_below', 'text');
  M('t-ratio', 'best_ratio', 'value', f.ratio);
  M('t-ratio-code', 'best_ratio', 'text');
  M('t-distinct', 'distinct_entries', 'value', f.int);
  M('t-entries', 'frontier_entries', 'value', f.int);
  M('t-tori', 'tori_computed', 'value', f.int);
  M('t-tori-total', 'tori_total', 'value', f.int);
  M('t-tori-pending', 'tori_pending', 'value', f.int);
  M('t-settled', 'settled_share', 'value', f.pct);
  M('t-settled-n', 'tori_settled', 'value', f.int);
  M('t-codes-n', 'tori_with_codes', 'value', f.int);
  M('t-classes', 'classes', 'value', f.compact);
  M('t-runs', 'exact_runs', 'value', f.int);
  M('ov-done', 'stage4_done', 'value', f.int);
  M('ov-total', 'stage4_total', 'value', f.int);
  M('ov-started', 'stage4_started', 'text');
  M('ov-stop', 'stage4_stop', 'text');

  // the registered laws
  const outcomeClass = (r) =>
    r.outcome === 'held' ? 'held' : r.outcome === 'failed' ? 'failed' : r.outcome ? 'pending' : 'none';
  dash.draw('ov-laws', (tbody) => {
    if (!CR.ok('fits')) {
      tbody.replaceChildren();
      return;
    }
    const rows = CR.rows('fits').filter((r) => r.kind === 'registered');
    CR.fillBody(tbody, rows, [
      { field: 'label' },
      { field: 'status', pill: outcomeClass },
      { field: 'decided_by' },
    ], 'id');
    tbody.querySelectorAll('tr').forEach((tr) => {
      tr.lastElementChild.classList.add('cr-hide-narrow');
    });
  });

  // the stage 4 run: a meter and a burn-up against the stop rule
  dash.draw('ov-meter', (el) => {
    if (!CR.ok('summary')) {
      el.style.width = '0';
      return;
    }
    const s = CR.rows('summary');
    const done = +CR.metric(s, 'stage4_done').value;
    const total = +CR.metric(s, 'stage4_total').value;
    el.style.width = (100 * done) / total + '%';
    el.style.background = dash.colors[0];
  });

  // '2026-10-30 19:45 UTC' -> a Date
  const parseUTC = (s) => new Date(s.replace(' UTC', '').replace(' ', 'T') + ':00Z');
  dash.draw('ov-burnup', (el) => {
    el.replaceChildren();
    if (!CR.ready(el, ['progress', 'summary'], { chart: true })) return;
    const s = CR.rows('summary');
    const total = +CR.metric(s, 'stage4_total').value;
    const start = parseUTC(CR.metric(s, 'stage4_started').text);
    const stop = parseUTC(CR.metric(s, 'stage4_stop').text);
    const pts = CR.rows('progress')
      .filter((r) => r.run === 'stage 4' && r.unit === 'tori')
      .map((r) => ({ t: new Date(r.time), v: +r.done, r }))
      .sort((a, b) => a.t - b.t);
    pts.unshift({ t: start, v: 0, r: null });
    const x = d3.scaleUtc().domain([start, stop]);
    const y = d3.scaleLinear().domain([0, total]).nice();
    const fmtDay = d3.utcFormat('%b %-d');
    const { svg, width, m } = CR.frame(el, {
      height: 240,
      x,
      y,
      xFormat: fmtDay,
      yFormat: f.int,
      yLabel: 'Tori done',
      label: 'Stage 4 tori done against time',
    });
    // the total, as a reference line
    svg
      .append('line')
      .attr('class', 'cr-zero')
      .attr('x1', m.left)
      .attr('x2', width - m.right)
      .attr('y1', y(total))
      .attr('y2', y(total));
    svg
      .append('text')
      .attr('class', 'cr-tick')
      .attr('x', m.left + 4)
      .attr('y', y(total) - 5)
      .text(`all ${f.int(total)} tori`);
    svg
      .append('line')
      .attr('class', 'cr-zero')
      .attr('x1', x(stop))
      .attr('x2', x(stop))
      .attr('y1', y(total))
      .attr('y2', y(0));
    svg
      .append('text')
      .attr('class', 'cr-tick')
      .attr('x', x(stop) - 4)
      .attr('y', y(total) - 5)
      .attr('text-anchor', 'end')
      .text('stop rule');
    const line = d3
      .line()
      .x((p) => x(p.t))
      .y((p) => y(p.v))
      .curve(d3.curveStepAfter);
    svg
      .append('path')
      .attr('d', line(pts))
      .attr('fill', 'none')
      .attr('stroke-width', 2)
      .attr('stroke-linejoin', 'round')
      .attr('stroke-linecap', 'round')
      .style('stroke', dash.colors[0]);
    const last = pts[pts.length - 1];
    svg
      .append('circle')
      .attr('cx', x(last.t))
      .attr('cy', y(last.v))
      .attr('r', 4)
      .attr('stroke-width', 2)
      .style('fill', dash.colors[0])
      .style('stroke', 'var(--color-panel)');
    const tip = CR.tip(el);
    const hp = pts.filter((p) => p.r).map((p) => ({ x: x(p.t), y: y(p.v), d: p }));
    CR.hover(svg, hp, {
      tip,
      describe: (p) => [
        d3.utcFormat('%b %-d, %H:%M UTC')(p.t),
        [[f.int(p.v) + ' tori', 'done, commit ' + p.r.commit]],
      ],
    });
  });

  // new frontier entries since a date (default: the last 7 days)
  const since = document.querySelector('#dash-root .cr-since');
  const lastWeek = () => d3.utcFormat('%Y-%m-%d')(d3.utcDay.offset(new Date(), -7));
  if (!dash.params().since) dash.setParams({ since: lastWeek() });
  since.addEventListener('change', () => {
    if (since.value && since.validity.valid) dash.setParams({ since: since.value });
  });
  since.addEventListener('blur', () => {
    since.value = dash.params().since || '';
  });
  document.querySelector('#dash-root .cr-since-reset').addEventListener('click', () => {
    dash.setParams({ since: lastWeek() });
  });
  dash.onData(() => {
    if (since !== document.activeElement) since.value = dash.params().since || '';
  });
  dash.draw('ov-new', (tbody) => {
    if (!CR.ok('frontier')) {
      tbody.replaceChildren();
      return;
    }
    const from = dash.params().since || '';
    const rows = CR.rows('frontier')
      .filter((e) => (e.first_seen || '') >= from)
      .sort((a, b) => b.score - a.score || a.n - b.n);
    CR.fillBody(
      tbody,
      rows,
      [
        { field: 'code' },
        { field: 'torus' },
        { field: 'score', num: true, text: (r) => f.score(r.score) },
        { field: 'ratio', num: true, text: (r) => f.ratio(r.ratio) },
        { field: 'tier' },
        { field: 'first_seen' },
      ],
      'id',
      (r) => CR.openCode(r.id),
    );
    tbody.querySelectorAll('tr').forEach((tr) => {
      tr.children[3].classList.add('cr-hide-narrow');
      tr.children[4].classList.add('cr-hide-narrow');
    });
  });
})();
