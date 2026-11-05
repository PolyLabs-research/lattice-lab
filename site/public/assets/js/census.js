// The code census: the best distance and the best k d^2/n at each size, from SITE.qec_census
// (site/build_data.py: aggregates of the census dashboards' data, no polynomials).
const QC = window.SITE.qec_census;
const STAGE_COLOR = { "3a": "--cell-soft", "3b/3c": "--cell", "4": "--gold" };
const color = st => `var(${STAGE_COLOR[st] || "--muted"})`;
const num = x => Number(x).toLocaleString("en-US");

// ---- the numbers ----
const T = QC.totals;
$("cn-tori").textContent = num(T.tori_total);
$("cn-with").textContent = num(T.tori_with_codes);
$("cn-classes").textContent = num(T.classes);
$("cn-runs").textContent = num(T.exact_runs);
$("cn-entries").textContent = num(T.frontier_entries);
$("cn-distinct").textContent = num(T.distinct_entries);
const S4D = QC.stage4d;
if (S4D.verdict) {
  $("cn-4d-badge").textContent = S4D.verdict;
  $("cn-4d-badge").className = `badge ${S4D.verdict === "pass" ? "ok" : S4D.verdict === "fail" ? "bad" : "muted"}`;
  $("cn-4d-text").textContent = `${S4D.recorded} of ${S4D.selected} classes recorded`;
} else if (S4D.recorded) {
  const all = S4D.d.length === 1 ? `, every one d = ${S4D.d[0]}` : "";
  $("cn-4d-text").textContent = `${S4D.recorded} of ${S4D.selected} recorded so far${all}`;
}

// ---- the entries by size ----
// [n, k, d, stage, settled]; at n = 396, k = 4 the census's own d is a lower bound, and stage 4d
// has found d = 30 there.
const PTS = QC.points.map(([n, k, d, stage, settled]) => ({ n, k, d, stage, settled }));
const byN = new Map();
for (const p of PTS) {
  if (!byN.has(p.n)) byN.set(p.n, []);
  byN.get(p.n).push(p);
}
const SIZES = [...byN.keys()].sort((a, b) => a - b);
const D4 = S4D.recorded && S4D.d.length === 1 ? { n: 396, k: 4, d: S4D.d[0] } : null;
function topAt(n) {
  const ps = byN.get(n);
  let best = ps[0];
  for (const p of ps) if (p.d > best.d || (p.d === best.d && p.settled && !best.settled)) best = p;
  return best;
}
const code = p => `[[${p.n},${p.k},${p.d}]]`;
const score = p => (p.k * p.d * p.d) / p.n;

// nearest size to a pointer position
function nearest(F, svg, ev) {
  const xv = pointerX(svg, ev, F.W);
  let best = SIZES[0];
  for (const n of SIZES) if (Math.abs(F.sx(n) - xv) < Math.abs(F.sx(best) - xv)) best = n;
  return best;
}
function cursorLine(F) {
  return `<line class="cursor" x1="0" x2="0" y1="${F.T}" y2="${F.H - F.B}" stroke="${css("--ink")}" stroke-width="1" opacity="0"/>`;
}
function moveCursor(svg, x) {
  const c = svg.querySelector(".cursor");
  c.setAttribute("x1", x); c.setAttribute("x2", x); c.setAttribute("opacity", "0.35");
}

// ---- the best distance at each size ----
let allK = true;
function drawD() {
  const svg = $("d-chart");
  const F = frame({ H: 360, x: { min: 0, max: 410, ticks: [0, 50, 100, 150, 200, 250, 300, 350, 400], label: "physical qubits n" },
                    y: { min: 0, max: 32, ticks: [0, 4, 8, 12, 16, 20, 24, 28, 32], label: "best distance d" } });
  let s = F.markup;
  // the registered envelopes: stage 3's 1.40 sqrt(n), and stage 4's 0.8011 n^0.6074 over its range
  const curve = (f, a, b, dash) => {
    let d = "";
    for (let i = 0; i <= 80; i++) {
      const n = a + ((b - a) * i) / 80;
      d += `${i ? "L" : "M"}${F.sx(n).toFixed(1)} ${F.sy(f(n)).toFixed(1)} `;
    }
    s += `<path d="${d}" style="fill: none; stroke: var(--muted); stroke-width: 1.4; stroke-dasharray: ${dash}"/>`;
  };
  curve(n => 1.4 * Math.sqrt(n), 8, 300, "5 4");
  curve(n => 0.8011 * n ** 0.6074, 300, 400, "2 3");
  s += `<text x="${F.sx(120).toFixed(1)}" y="${F.sy(1.4 * Math.sqrt(120) + 2.4).toFixed(1)}" text-anchor="middle" ${FONT} style="fill: var(--muted)">1.40 √n</text>`;
  s += `<text x="${F.sx(400).toFixed(1)}" y="${(F.sy(0.8011 * 400 ** 0.6074) - 8).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--muted)">0.80 n^0.61</text>`;
  const shown = allK ? PTS : SIZES.map(topAt);
  if (!allK) {
    let d = "";
    shown.forEach((p, i) => { d += `${i ? "L" : "M"}${F.sx(p.n).toFixed(1)} ${F.sy(p.d).toFixed(1)} `; });
    s += `<path d="${d}" style="fill: none; stroke: var(--line); stroke-width: 1.5"/>`;
  }
  for (const p of shown) {
    const r = allK ? 2.6 : 3.6, x = F.sx(p.n).toFixed(1), y = F.sy(p.d).toFixed(1);
    s += p.settled
      ? `<circle cx="${x}" cy="${y}" r="${r}" style="fill: ${color(p.stage)}"/>`
      : `<circle cx="${x}" cy="${y}" r="${r}" style="fill: var(--panel); stroke: ${color(p.stage)}; stroke-width: 1.4"/>`;
  }
  if (D4) s += `<circle cx="${F.sx(D4.n).toFixed(1)}" cy="${F.sy(D4.d).toFixed(1)}" r="4.6" style="fill: var(--ok); stroke: var(--panel); stroke-width: 1.2"/>`;
  s += cursorLine(F);
  svg.innerHTML = s;
  svg.onpointermove = ev => {
    const n = nearest(F, svg, ev);
    moveCursor(svg, F.sx(n));
    const ps = byN.get(n).slice().sort((a, b) => a.k - b.k);
    const top = topAt(n);
    let text = `n = ${n}: the best is ${code(top)}${top.settled ? "" : " (a lower bound)"}`;
    if (D4 && n === D4.n) text += `; stage 4d has found ${code(D4)}`;
    const rest = ps.filter(p => p !== top).map(p => `${code(p)}${p.settled ? "" : "+"}`);
    if (rest.length) text += `. Other k: ${rest.slice(0, 8).join(", ")}${rest.length > 8 ? ", …" : ""}`;
    $("d-tip").textContent = text + ".";
  };
  svg.onpointerleave = () => svg.querySelector(".cursor").setAttribute("opacity", "0");
}
function setAll(on) {
  allK = on;
  $("d-all").setAttribute("aria-pressed", String(on));
  $("d-top").setAttribute("aria-pressed", String(!on));
  drawD();
}
$("d-all").addEventListener("click", () => setAll(true));
$("d-top").addEventListener("click", () => setAll(false));

// ---- the best k d^2/n at each size ----
function bestScore(n) {
  let best = null;
  for (const p of byN.get(n)) if (!best || score(p) > score(best)) best = p;
  return best;
}
const LABELLED = new Set(["[[144,12,12]]", "[[360,12,≤24]]"]);
function drawS() {
  const svg = $("s-chart");
  const F = frame({ H: 340, x: { min: 0, max: 410, ticks: [0, 50, 100, 150, 200, 250, 300, 350, 400], label: "physical qubits n" },
                    y: { min: 0, max: 21, ticks: [0, 3, 6, 9, 12, 15, 18, 21], label: "best k d²/n" } });
  let s = F.markup;
  const hline = (v, a, b, label) => {
    s += `<line x1="${F.sx(a).toFixed(1)}" x2="${F.sx(b).toFixed(1)}" y1="${F.sy(v).toFixed(1)}" y2="${F.sy(v).toFixed(1)}" style="stroke: var(--muted); stroke-width: 1.4; stroke-dasharray: 5 4"/>`;
    s += `<text x="${F.sx(a).toFixed(1)}" y="${(F.sy(v) - 6).toFixed(1)}" ${FONT} style="fill: var(--muted)">${label}</text>`;
  };
  hline(13.5, 202, 300, "stage 3's bound");
  hline(17, 302, 400, "stage 4's ceiling");
  const best = SIZES.map(bestScore);
  for (const p of best) {
    s += `<circle cx="${F.sx(p.n).toFixed(1)}" cy="${F.sy(score(p)).toFixed(1)}" r="3.4" style="fill: ${color(p.stage)}"/>`;
  }
  for (const [name, n, k, d] of QC.published) {
    const v = (k * d * d) / n, x = F.sx(n).toFixed(1), y = F.sy(v).toFixed(1);
    s += `<circle cx="${x}" cy="${y}" r="4.2" style="fill: var(--panel); stroke: var(--bad); stroke-width: 1.8"/>`;
    const label = n === 360 ? "[[360,12,≤24]]" : `[[${n},${k},${d}]]`;
    if (LABELLED.has(label)) s += `<text x="${(+x - 8).toFixed(1)}" y="${(+y - 8).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--bad)">${label}</text>`;
  }
  s += cursorLine(F);
  svg.innerHTML = s;
  svg.onpointermove = ev => {
    const n = nearest(F, svg, ev);
    moveCursor(svg, F.sx(n));
    const p = bestScore(n);
    const pub = QC.published.filter(q => q[1] === n).map(q => `${q[0]} (${((q[2] * q[3] * q[3]) / q[1]).toFixed(2)})`);
    $("s-tip").textContent = `n = ${n}: the best k d²/n is ${score(p).toFixed(2)}, ${code(p)}${p.settled ? "" : " (a lower bound)"}` +
      (pub.length ? `; published: ${pub.join(", ")}` : "") + ".";
  };
  svg.onpointerleave = () => svg.querySelector(".cursor").setAttribute("opacity", "0");
}

function redraw() { drawD(); drawS(); }
redraw();
onRedraw(redraw);
