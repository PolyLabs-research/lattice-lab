// Confidence: checked codes and their tiers, instrument reruns, unsettled entries.
(function () {
  const CR = window.CR;
  const f = CR.fmt;
  const RANK = { contradicts: 5, error: 4, 'reached d': 3, consistent: 2, unfinished: 1 };

  // one row per checked code: the strongest result of each kind of check
  dash.calc('check_matrix', {
    title: 'Checks by code',
    description: 'For each checked code and each kind of check, the strongest outcome of its jobs (a contradiction or error outranks any agreement).',
    inputs: ['checks'],
    fn: (checks) => {
      const out = new Map();
      for (const c of checks) {
        if (c.source !== 'spot-check' && c.source !== '[[310,10,22]] check') continue;
        const r = out.get(c.code_key) || { code_key: c.code_key, code: c.code, torus: c.torus, tier: c.tier, source: c.source, C1: null, C2: null, C3: null, C4: null, C5: null, C6: null };
        if (!r[c.check] || ({ contradicts: 5, error: 4, 'reached d': 3, consistent: 2, unfinished: 1 }[c.status] || 0) > ({ contradicts: 5, error: 4, 'reached d': 3, consistent: 2, unfinished: 1 }[r[c.check]] || 0)) r[c.check] = c.status;
        out.set(c.code_key, r);
      }
      return [...out.values()];
    },
  });
  // instrument reruns, one row per torus
  dash.calc('rerun_summary', {
    title: 'Instrument reruns by torus',
    description: "Stage 3d's DistQLDPC reruns and the stage 4 instrument's validation, one row per torus: how many runs, and whether they all reached the recorded d.",
    inputs: ['checks'],
    fn: (checks) => {
      const out = new Map();
      for (const c of checks) {
        if (c.source !== 'stage 3d' && c.source !== 'stage 4 validation') continue;
        const key = `${c.source}|${c.torus}`;
        const r = out.get(key) || { key, source: c.source, torus: c.torus, jobs: 0, reached: 0, detail: c.variant };
        r.jobs += 1;
        if (c.status === 'reached d') r.reached += 1;
        out.set(key, r);
      }
      return [...out.values()].map((r) => ({ ...r, result: r.source === 'stage 3d' ? `${r.reached} of ${r.jobs} classes at d = 24` : `${r.detail}` }));
    },
  });

  const chipClass = (s) => (s === 'reached d' ? 'reached' : s || 'none');
  const tierClass = (r) => String(r.tier || 'none').replace(/\s+/g, '-');
  dash.draw('cf-matrix', (tbody) => {
    if (!CR.ok('checks')) {
      tbody.replaceChildren();
      return;
    }
    const rows = dash
      .data('check_matrix')
      .data.slice()
      .sort((a, b) => (RANK[b.C6] || 0) - (RANK[a.C6] || 0) || String(a.tier).localeCompare(String(b.tier)) || a.torus.localeCompare(b.torus));
    const cols = [{ field: 'code' }, { field: 'torus' }, { field: 'tier', pill: tierClass }];
    for (const c of ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']) cols.push({ field: c, chip: true });
    cols.push({ field: 'source' });
    tbody.replaceChildren();
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', r.code_key);
      for (const c of cols) {
        const td = document.createElement('td');
        const v = r[c.field];
        if (c.chip) {
          const s = document.createElement('span');
          s.className = 'cr-chip cr-chip-' + chipClass(v);
          s.textContent = v || '';
          td.append(s);
        } else if (c.pill) {
          const s = document.createElement('span');
          s.className = 'cr-pill cr-pill-' + c.pill(r);
          s.textContent = v || '';
          td.append(s);
        } else td.textContent = v === null || v === undefined ? '' : String(v);
        if (c.field === 'source') td.className = 'cr-hide-narrow';
        tr.append(td);
      }
      tbody.append(tr);
    }
  });

  dash.draw('cf-reruns', (tbody) => {
    if (!CR.ok('checks')) {
      tbody.replaceChildren();
      return;
    }
    const rows = dash
      .data('rerun_summary')
      .data.slice()
      .sort((a, b) => a.source.localeCompare(b.source) || a.torus.localeCompare(b.torus));
    CR.fillBody(tbody, rows, [{ field: 'source' }, { field: 'torus' }, { field: 'jobs', num: true }, { field: 'result' }], 'key');
  });

  dash.draw('cf-unsettled', (tbody) => {
    if (!CR.ok('frontier')) {
      tbody.replaceChildren();
      return;
    }
    const rows = CR.rows('frontier').filter((e) => !CR.bool(e.settled));
    CR.fillBody(
      tbody,
      rows,
      [{ field: 'code' }, { field: 'torus' }, { field: 'study_group' }, { field: 'iso_settled_torus' }, { field: 'iso_settled_d', num: true }],
      'id',
      (r) => CR.openCode(r.id),
    );
    void f;
  });
})();
