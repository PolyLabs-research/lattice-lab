// Render the dashboard pages locally with the runtime stand-in (shim.js), run its checks, and
// screenshot each page.
//   node examples/qec-census-4/dashboards/dev/render.js <d3.min.js> <out dir> [pages] [widths] [theme]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname;
const PAGE = path.join(HERE, '..', 'page');
const DATA = path.join(HERE, '..', 'data');
const [d3Path, outDir, pagesArg, widthsArg, themeArg] = process.argv.slice(2);
const pages = (pagesArg || 'overview,frontier,code').split(',');
const widths = (widthsArg || '1280,420').split(',').map(Number);
const theme = themeArg || 'light';

const LIGHT = `--color-fg:#0b0b0b;--color-fg-muted:#6b6a65;--color-bg:#f9f9f7;--color-panel:#ffffff;--color-border-line:rgba(11,11,11,.10);--color-ok:#006c10;--color-warn:#794c02;--color-bad:#a42528;--cds-chart-grid:rgba(11,11,11,.08);--cds-chart-axis:#c3c2b7;--cds-chart-reference:#898781;--cds-chart-muted:#c3c2b7;--cds-chart-status-critical:#d03b3b;--cds-surface-popover:#ffffff;--cds-border:rgba(0,0,0,.08);--cds-text-secondary:#52514e;--cds-chart-categorical-1:#2a78d6;--cds-chart-categorical-2:#eb6834;--cds-chart-categorical-3:#1baf7a;--cds-chart-categorical-4:#eda100;--cds-chart-categorical-5:#e87ba4;--cds-chart-categorical-6:#008300;--cds-chart-categorical-7:#6250d6;--cds-chart-categorical-8:#e34948;`;
const DARK = `--color-fg:#f0efec;--color-fg-muted:#a3a29b;--color-bg:#0d0d0d;--color-panel:#1a1a19;--color-border-line:rgba(255,255,255,.10);--color-ok:#53c556;--color-warn:#e49c06;--color-bad:#f17778;--cds-chart-grid:rgba(255,255,255,.08);--cds-chart-axis:#383835;--cds-chart-reference:#898781;--cds-chart-muted:#5f5e5a;--cds-chart-status-critical:#dc3c3d;--cds-surface-popover:#303030;--cds-border:rgba(255,255,255,.08);--cds-text-secondary:#c3c2b7;--cds-chart-categorical-1:#3987e5;--cds-chart-categorical-2:#d95926;--cds-chart-categorical-3:#199e70;--cds-chart-categorical-4:#c98500;--cds-chart-categorical-5:#d55181;--cds-chart-categorical-6:#008300;--cds-chart-categorical-7:#9085e9;--cds-chart-categorical-8:#e66767;`;
const COMMON = `--cds-radius:.5rem;--cds-pad-xs:.25rem;--cds-pad-sm:.375rem;--cds-pad-md:.5rem;--cds-pad-lg:.75rem;--cds-pad-xl:1.25rem;--cds-gap-xs:.375rem;--cds-gap-sm:.5rem;--cds-gap-md:.75rem;--cds-gap-lg:1.25rem;--cds-gap-xl:2rem;--cds-font-size-caption:.75rem;--cds-font-size-body:.875rem;--cds-font-size-heading:.9375rem;--cds-font-size-title:1.375rem;--cds-font-weight-medium:500;--cds-shadow-popover:0 8px 24px #0000001f,0 2px 6px #00000014;--cds-dur-slow:.45s;--cds-ease-out:cubic-bezier(0,0,.2,1);--font-anthropic-sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--font-anthropic-serif:ui-serif,Georgia,"Times New Roman",serif;`;

function build(page) {
  const html = fs.readFileSync(path.join(PAGE, 'index.html'), 'utf8');
  const srcs = [...html.matchAll(/<script src="([^"]+)"><\/script>/g)].map((m) => m[1]);
  const body = html.replace(/<script src="[^"]+"><\/script>\s*/g, '');
  const data = {};
  for (const f of fs.readdirSync(DATA)) if (f.endsWith('.json') && !f.includes('cache')) data[f.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
  const params = JSON.parse(fs.readFileSync(path.join(PAGE, 'params.json'), 'utf8'));
  const tokens = (theme === 'dark' ? DARK : LIGHT) + COMMON;
  const inline = (code) => `<script>${code.replace(/<\/script>/g, '<\\/script>')}</script>`;
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{${tokens}} body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);} #dash-root{padding:16px clamp(16px,3vw,40px);} .dash-skeleton{background:var(--cds-chart-grid);border-radius:4px;min-height:1em}</style></head>
<body><div id="dash-root">${body}</div>
${inline(fs.readFileSync(d3Path, 'utf8'))}
${inline(`window.__DATA=${JSON.stringify(data)};window.__PARAMS=${JSON.stringify(params)};`)}
${inline(fs.readFileSync(path.join(HERE, 'shim.js'), 'utf8'))}
${inline('window.__boot();')}
${srcs.map((s) => inline(fs.readFileSync(path.join(PAGE, s), 'utf8'))).join('\n')}
</body></html>`;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const file = path.join(outDir, `harness-${theme}.html`);
  fs.writeFileSync(file, build());
  const browser = await chromium.launch();
  for (const w of widths) {
    for (const p of pages) {
      const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, colorScheme: theme });
      const pg = await ctx.newPage();
      const logs = [];
      pg.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') logs.push(m.text()); });
      pg.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
      await pg.goto('file://' + file + '#' + p);
      await pg.waitForTimeout(1200);
      const rep = await pg.evaluate(() => window.__report());
      const shot = path.join(outDir, `${p}-${w}-${theme}.png`);
      await pg.screenshot({ path: shot, fullPage: true });
      const brief = { page: p, width: w, logs, ...rep };
      console.log(JSON.stringify(brief, null, 1));
      await ctx.close();
    }
  }
  await browser.close();
})();
