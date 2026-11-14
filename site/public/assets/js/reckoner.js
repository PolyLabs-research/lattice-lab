// Reckoner: two charts from the project's own records (github.com/PolyLabs-research/reckoner).

// Beat-par count out of the 600 registered problems, per ladder pass of the first campaign (M1).
// Anchor: PREREG-m1.md; iterations 4, 9, 14, 19: RUNLOG-m1.md §3.
const M1 = [["anchor", 101], ["iteration 4", 182], ["iteration 9", 199], ["iteration 14", 199], ["iteration 19", 209]];

// SWEEP-m3, attempt 2 (2026-11-13): gate-10b hits out of 1,229 by rehearsal fraction and seed,
// and the control with the policy target withheld (f = 0, seeds 0 and 1). SWEEP-m3.md, readings.
const SWEEP = [
  [0.00, [1211, 1211, 1211]], [0.10, [1212, 1209, 1208]], [0.15, [1210, 1212, 1211]],
  [0.25, [1191, 1191, 1207]], [0.35, [1193, 1191, 1191]], [0.50, [1192, 1192, 1190]],
  [0.65, [1192, 1191, 1192]], [0.75, [1193, 1193, 1192]],
];
const CONTROL = [1088, 1089], ANCHOR = 1192, BAND = 1190;

function drawM1() {
  const svg = $("m1-chart"), W = 760, H = 320, L = 58, R = 16, T = 18, B = 42;
  const n = M1.length, slot = (W - L - R) / n;
  const F = frame({ W, H, L, R, T, B, x: { min: 0, max: n, ticks: [] },
                    y: { min: 0, max: 250, ticks: [0, 50, 100, 150, 200, 250], label: "under par, of 600" } });
  let s = F.markup;
  M1.forEach(([label, v], i) => {
    const x = L + slot * i + slot * 0.22, w = slot * 0.56, y = F.sy(v);
    const fill = i === 0 ? "var(--cell-soft)" : i === n - 1 ? "var(--cell)" : "var(--cell)";
    s += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${(F.sy(0) - y).toFixed(1)}" rx="2" style="fill: ${fill}; opacity: ${i === 0 || i === n - 1 ? 1 : 0.55}"/>`;
    s += `<text x="${(x + w / 2).toFixed(1)}" y="${(y - 6).toFixed(1)}" text-anchor="middle" ${FONT} style="fill: var(--ink)">${v}</text>`;
    s += `<text x="${(x + w / 2).toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${label}</text>`;
  });
  const ya = F.sy(M1[0][1]).toFixed(1);
  s += `<line x1="${L}" x2="${W - R}" y1="${ya}" y2="${ya}" style="stroke: var(--muted); stroke-dasharray: 4 4"/>`;
  svg.innerHTML = s;
}

function drawSweep() {
  const svg = $("sw-chart"), W = 760, H = 320, L = 58, R = 16, T = 14, B = 42;
  const cols = [{ label: "control", pts: CONTROL, control: true }, ...SWEEP.map(([f, pts]) => ({ label: f.toFixed(2), f, pts }))];
  const slot = (W - L - R) / cols.length;
  const F = frame({ W, H, L, R, T, B, x: { min: 0, max: cols.length, ticks: [], label: "rehearsal fraction f" },
                    y: { min: 1080, max: 1220, ticks: [1080, 1100, 1120, 1140, 1160, 1180, 1200, 1220], label: "hits, of 1,229" } });
  let s = F.markup;
  const hline = (v, color, dash) => {
    const y = F.sy(v).toFixed(1);
    s += `<line x1="${L}" x2="${W - R}" y1="${y}" y2="${y}" style="stroke: var(${color}); stroke-width: 1.5; ${dash ? "stroke-dasharray: 5 4" : ""}"/>`;
  };
  hline(ANCHOR, "--muted", false);
  hline(BAND, "--gold", true);
  cols.forEach((c, i) => {
    const cx = L + slot * (i + 0.5);
    s += `<text x="${cx.toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} style="fill: var(${c.control ? "--bad" : "--muted"})">${c.label}</text>`;
    c.pts.forEach((v, k) => {
      const off = (k - (c.pts.length - 1) / 2) * 9;
      s += `<circle cx="${(cx + off).toFixed(1)}" cy="${F.sy(v).toFixed(1)}" r="4.5" style="fill: var(${c.control ? "--bad" : "--cell"}); stroke: var(--panel); stroke-width: 1.2"/>`;
    });
  });
  s += `<rect id="sw-cursor" x="0" y="${T}" width="${slot.toFixed(1)}" height="${H - T - B}" style="fill: var(--ink)" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#sw-cursor");
  svg.onpointermove = ev => {
    const i = Math.max(0, Math.min(cols.length - 1, Math.floor((pointerX(svg, ev, W) - L) / slot)));
    const c = cols[i];
    cursor.setAttribute("x", (L + slot * i).toFixed(1));
    cursor.setAttribute("opacity", "0.06");
    $("sw-tip").textContent = c.control
      ? `Control, policy target withheld, f = 0: ${c.pts.join(" and ")} hits (seeds 0 and 1), ${ANCHOR - Math.max(...c.pts)} or more below the anchor's ${ANCHOR}.`
      : `f = ${c.label}: seeds read ${c.pts.join(", ")}; the anchor reads ${ANCHOR}, the pass line is ${BAND}.`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

function draw() { drawM1(); drawSweep(); }
draw();
onRedraw(draw);
