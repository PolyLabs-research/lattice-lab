// A stand-in for the dashboard runtime, for rendering the pages locally: dash.data, onData,
// draw, calc, params, setLink and colors, plus the runtime's own checks of a page (stray
// writes outside drawings, drawings stored non-empty, nested or without a function, labels
// that overlap or are cut, empty charts, NaN, and marks whose shown value differs from the data).
(function () {
  const DATA = window.__DATA || {};
  const DEFAULTS = Object.assign({}, window.__PARAMS || {});
  let params = Object.assign({}, DEFAULTS);
  const draws = new Map();
  const onData = [];
  const calcs = new Map();
  const errors = [];
  const root = () => document.getElementById('dash-root');
  const EMPTY = /^[\s–—−\-·.…]*$|^n\/?a$/i;
  const ALLOWED = new Set(['class', 'style', 'hidden', 'open', 'disabled', 'tabindex', 'value', 'checked', 'selected']);
  const allowed = (a) => ALLOWED.has(a) || a.startsWith('aria-');

  // ---- the stored page, before any script: drawings must be empty and not nested
  const stored = { notEmpty: [], nested: 0, names: new Set() };
  const scanStored = () => {
    const all = [...root().querySelectorAll('[data-draw]')];
    for (const el of all) {
      stored.names.add(el.getAttribute('data-draw'));
      if (el.parentElement.closest('[data-draw]')) stored.nested++;
      if (!(el.childElementCount === 0 && EMPTY.test((el.textContent || '').trim()))) stored.notEmpty.push(el.getAttribute('data-draw'));
    }
  };

  // ---- stray writes: every element outside a drawing is watched, without its subtree
  const stray = [];
  let observer = null;
  const watch = (node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      observer.observe(node, { characterData: true });
      return;
    }
    if (!(node instanceof Element)) return;
    const isDraw = node.hasAttribute('data-draw');
    observer.observe(node, isDraw ? { attributes: true, attributeFilter: ['data-draw'] } : { attributes: true, childList: true });
    if (!isDraw) for (const c of node.childNodes) watch(c);
  };
  const startWatch = () => {
    observer = new MutationObserver((records) => {
      for (const r of records) {
        if (r.type === 'attributes' && allowed(r.attributeName || '')) continue;
        const t = r.type === 'characterData' ? r.target.parentNode : r.target;
        stray.push({ type: r.type, attr: r.attributeName, el: t && t.outerHTML ? t.outerHTML.slice(0, 160) : String(t) });
      }
    });
    for (const c of root().childNodes) watch(c);
  };

  // ---- running drawings
  const visible = (el) => !el.closest('[hidden]');
  let scheduled = false;
  const runAll = () => {
    scheduled = false;
    for (const fn of onData) {
      try { fn(); } catch (e) { errors.push('onData: ' + e.stack); }
    }
    for (const [name, fn] of draws) {
      for (const el of root().querySelectorAll(`[data-draw="${CSS.escape(name)}"]`)) {
        if (!visible(el)) continue;
        try {
          if (typeof fn === 'function') fn(el);
          else {
            if (!el.__made) el.__made = fn.mount ? fn.mount(el) : null;
            if (fn.update) fn.update(el, el.__made);
          }
        } catch (e) {
          errors.push(`draw ${name}: ${e.stack}`);
        }
      }
    }
  };
  const schedule = () => {
    if (!scheduled) {
      scheduled = true;
      setTimeout(runAll, 0);
    }
  };

  const data = (id) => {
    if (calcs.has(id)) {
      const c = calcs.get(id);
      const ins = c.inputs.map((i) => data(i));
      if (ins.some((g) => g.status !== 'ok')) return { status: 'loading', data: [], meta: [] };
      return { status: 'ok', data: c.fn(...ins.map((g) => g.data)), meta: [] };
    }
    const rows = DATA[id];
    if (!rows) return { status: 'missing', data: [], meta: [] };
    return { status: 'ok', data: rows, columns: rows.length ? Object.keys(rows[0]) : [], meta: [], refreshing: false };
  };

  window.dash = {
    data,
    onData(fn) {
      onData.push(fn);
      try { fn(); } catch (e) { errors.push('onData: ' + e.stack); }
    },
    draw(name, fn) {
      if (fn === undefined) {
        const f = draws.get(name);
        if (f) for (const el of root().querySelectorAll(`[data-draw="${CSS.escape(name)}"]`)) if (visible(el)) {
          try { typeof f === 'function' ? f(el) : f.update && f.update(el, el.__made); } catch (e) { errors.push(`draw ${name}: ${e.stack}`); }
        }
        return;
      }
      draws.set(name, fn);
      schedule();
    },
    calc(id, spec) { calcs.set(id, spec); },
    loader() {},
    params: () => Object.assign({}, params),
    setParams(p) { Object.assign(params, p); schedule(); },
    resetParams() { params = Object.assign({}, DEFAULTS); schedule(); },
    setLink(name) { history.replaceState(null, '', '#' + name); },
    refresh() {},
    colors: [1, 2, 3, 4, 5, 6, 7, 8].map((i) => `var(--cds-chart-categorical-${i})`),
  };

  // re-run when a section is shown, or the width changes
  const hiddenWatch = new MutationObserver((rs) => { if (rs.some((r) => r.attributeName === 'hidden')) schedule(); });
  window.addEventListener('resize', schedule);
  window.addEventListener('error', (e) => errors.push('error: ' + (e.error && e.error.stack || e.message)));

  // ---- the output checks, as the runtime runs them
  const box = (el) => el.getBoundingClientRect();
  const shown = (el) => {
    if (el.closest('[hidden]')) return false;
    const r = box(el);
    if (r.width === 0 && r.height === 0) return false;
    const cs = getComputedStyle(el);
    return cs.visibility !== 'hidden' && cs.display !== 'none';
  };
  const turned = (el) => /rotate\((?!0)/.test(el.getAttribute('transform') || '') || /rotate\((?!0)/.test((el.parentElement && el.parentElement.getAttribute('transform')) || '');
  const overlapBig = (a, b) => {
    const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    const area = (x) => (x.right - x.left) * (x.bottom - x.top);
    return w > 2 && h > 2 && w * h >= 0.25 * Math.min(area(a), area(b));
  };
  const checks = () => {
    const out = { overlap: [], cut: [], empty: [], nan: [] };
    const svgs = [...root().querySelectorAll('svg')].filter((s) => !s.parentElement.closest('svg') && shown(s));
    for (const s of svgs) {
      const r = box(s);
      if (r.width < 120 || r.height < 80) continue;
      const texts = [...s.querySelectorAll('text')]
        .filter((t) => (t.textContent || '').trim() && shown(t) && !turned(t))
        .map((t) => ({ box: box(t), words: t.textContent.trim() }));
      for (let i = 0; i < texts.length; i++)
        for (let j = i + 1; j < texts.length; j++) {
          const a = texts[i];
          const b = texts[j];
          const same = a.words === b.words && Math.abs(a.box.left - b.box.left) <= 2 && Math.abs(a.box.top - b.box.top) <= 2;
          if (overlapBig(a.box, b.box) && !same) out.overlap.push(`${a.words} / ${b.words} in ${s.getAttribute('aria-label')}`);
        }
      const clips = getComputedStyle(s).overflow !== 'visible';
      if (clips)
        for (const t of texts)
          if (t.box.left - r.left < -4 || t.box.right - r.right > 4 || t.box.top - r.top < -4 || t.box.bottom - r.bottom > 4)
            out.cut.push(`${t.words} in ${s.getAttribute('aria-label')}`);
      const marks = [...s.querySelectorAll('rect,circle,ellipse,path,line,polyline,polygon,image,use,text')].filter((m) => {
        const b = box(m);
        return b.width + b.height > 0;
      });
      if (!marks.length) out.empty.push(s.getAttribute('aria-label'));
    }
    const walker = document.createTreeWalker(root(), NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const n = walker.currentNode;
      if (/(^|[^A-Za-z0-9_])NaN(?![0-9_]|s(?![A-Za-z])|[A-Za-z]{4})/.test(n.nodeValue) && !n.parentElement.closest('script,style') && shown(n.parentElement)) out.nan.push(n.nodeValue.slice(0, 60));
    }
    for (const el of root().querySelectorAll('svg [d*="NaN"], svg [x="NaN"], svg [y="NaN"], svg [cx="NaN"], svg [cy="NaN"], svg [width="NaN"], svg [height="NaN"], svg [transform*="NaN"]')) out.nan.push(el.outerHTML.slice(0, 80));
    return out;
  };

  // ---- marks: a shown value must be the data's (numbers to their shown precision)
  const decode = (s) => decodeURIComponent(s.replace(/\+/g, '%2B'));
  const parseWhere = (w) => w.split('&').map((kv) => kv.split('=').map(decode));
  const close = (shownText, value) => {
    if (value === null || value === undefined) return EMPTY.test(shownText);
    if (typeof value === 'number') {
      let t = shownText.replace(/,/g, '').trim();
      let scale = 1;
      if (t.endsWith('%')) { scale = 0.01; t = t.slice(0, -1); }
      else if (/[KMB]$/.test(t)) { scale = { K: 1e3, M: 1e6, B: 1e9 }[t.slice(-1)]; t = t.slice(0, -1); }
      if (!/^[+−-]?\d*\.?\d+$/.test(t)) return false;
      const x = parseFloat(t.replace('−', '-')) * scale;
      const decimals = (t.split('.')[1] || '').length;
      const step = Math.pow(10, -decimals) * scale;
      return Math.abs(x - value) <= step / 2 + 1e-9;
    }
    return String(value).trim() === shownText.trim();
  };
  const marks = () => {
    const bad = [];
    for (const el of root().querySelectorAll('[data-source][data-field]')) {
      if (!shown(el) || el.closest('table') || el.tagName === 'TH') continue;
      const id = el.getAttribute('data-source');
      const g = data(id);
      if (g.status !== 'ok') continue;
      let row = null;
      if (el.hasAttribute('data-row')) row = g.data[+el.getAttribute('data-row')];
      else if (el.hasAttribute('data-where')) {
        const conds = parseWhere(el.getAttribute('data-where'));
        const hits = g.data.filter((r) => conds.every(([k, v]) => String(r[k]) === v));
        if (hits.length !== 1) { bad.push(`${el.getAttribute('data-draw')}: ${hits.length} rows match ${el.getAttribute('data-where')}`); continue; }
        row = hits[0];
      } else if (g.data.length === 1) row = g.data[0];
      if (!row) { bad.push(`${el.getAttribute('data-draw')}: no row`); continue; }
      const v = row[el.getAttribute('data-field')];
      if (!close(el.textContent.trim(), v)) bad.push(`${el.getAttribute('data-draw')}: shows "${el.textContent.trim()}", data ${JSON.stringify(v)}`);
    }
    for (const table of root().querySelectorAll('table[data-source][data-row-key]')) {
      if (!shown(table)) continue;
      const g = data(table.getAttribute('data-source'));
      if (g.status !== 'ok') continue;
      const keys = table.getAttribute('data-row-key').split(',');
      const fields = [...table.querySelectorAll('thead th')].map((th) => th.getAttribute('data-field'));
      for (const tr of table.querySelectorAll('tbody tr')) {
        const key = tr.getAttribute('data-key');
        const row = g.data.find((r) => keys.map((k) => String(r[k])).join(',') === key);
        if (!row) { bad.push(`table ${table.id}: no row for key ${key}`); continue; }
        [...tr.children].forEach((td, i) => {
          const fld = fields[i];
          if (!fld) return;
          if (!close(td.textContent.trim(), row[fld])) bad.push(`table ${table.id} ${key} ${fld}: shows "${td.textContent.trim()}", data ${JSON.stringify(row[fld])}`);
        });
      }
    }
    return bad;
  };

  window.__report = () => ({
    errors,
    stray: stray.slice(0, 20),
    strayCount: stray.length,
    notEmpty: stored.notEmpty,
    nested: stored.nested,
    noFunction: [...stored.names].filter((n) => !draws.has(n)),
    ...checks(),
    marks: marks().slice(0, 40),
  });
  window.__boot = () => {
    scanStored();
    startWatch();
    hiddenWatch.observe(root(), { attributes: true, subtree: true, attributeFilter: ['hidden'] });
  };
})();
