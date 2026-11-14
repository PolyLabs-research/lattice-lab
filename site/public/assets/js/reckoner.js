// Reckoner: two charts from the project's own records (github.com/PolyLabs-research/reckoner).

// Beat-par count out of the 600 registered problems, per ladder pass of the first campaign (M1).
// Anchor: PREREG-m1.md; iterations 4, 9, 14, 19: RUNLOG-m1.md §3.
const M1 = [["anchor", 101], ["4", 182], ["9", 199], ["14", 199], ["19", 209]];

// SWEEP-m3, attempt 2 (2026-11-13): gate-10b hits out of 1,229 by rehearsal fraction and seed,
// and the control with the policy target withheld (f = 0, seeds 0 and 1). SWEEP-m3.md, readings.
const SWEEP = [
  [0.00, [1211, 1211, 1211]], [0.10, [1212, 1209, 1208]], [0.15, [1210, 1212, 1211]],
  [0.25, [1191, 1191, 1207]], [0.35, [1193, 1191, 1191]], [0.50, [1192, 1192, 1190]],
  [0.65, [1192, 1191, 1192]], [0.75, [1193, 1193, 1192]],
];
const CONTROL = [1088, 1089], ANCHOR = 1192, BAND = 1190;
const num = v => v.toLocaleString("en-US");

function drawM1() {
  const svg = $("m1-chart"), W = chartWidth(svg), narrow = W < 560, H = narrow ? 280 : 320;
  const L = narrow ? 40 : 58, R = narrow ? 6 : 16, T = 22, B = 44;
  sizeChart(svg, W, H);
  const n = M1.length, slot = (W - L - R) / n;
  const F = frame({ W, H, L, R, T, B, x: { min: 0, max: n, ticks: [], label: "after iteration" },
                    y: { min: 0, max: 250, ticks: [0, 50, 100, 150, 200, 250], label: narrow ? "" : "under par, of 600" } });
  let s = F.markup;
  const ya = F.sy(M1[0][1]).toFixed(1);
  s += `<line x1="${L}" x2="${W - R}" y1="${ya}" y2="${ya}" style="stroke: var(--muted); stroke-width: 1"/>`;
  M1.forEach(([label, v], i) => {
    const w = Math.min(slot * 0.56, 84), x = L + slot * (i + 0.5) - w / 2, y = F.sy(v), y0 = F.sy(0);
    // the anchor is where the campaign started, so it is drawn soft; each bar is rounded at its top
    const d = `M${x.toFixed(1)} ${y0.toFixed(1)} V${(y + 4).toFixed(1)} q0 -4 4 -4 h${(w - 8).toFixed(1)} q4 0 4 4 V${y0.toFixed(1)} Z`;
    s += `<path d="${d}" style="fill: var(${i === 0 ? "--cell-soft" : "--cell"})"/>`;
    s += `<text x="${(x + w / 2).toFixed(1)}" y="${(y - 6).toFixed(1)}" text-anchor="middle" ${FONT} style="fill: var(--ink)">${v}</text>`;
    s += `<text x="${(x + w / 2).toFixed(1)}" y="${H - B + 17}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${label}</text>`;
  });
  svg.innerHTML = s;
}

function drawSweep() {
  const svg = $("sw-chart"), W = chartWidth(svg), narrow = W < 560, H = narrow ? 290 : 320;
  const L = narrow ? 44 : 58, R = narrow ? 4 : 16, T = 14, B = 44;
  sizeChart(svg, W, H);
  const short = f => (f === 0 ? "0" : f.toFixed(2).slice(1));
  const cols = [{ label: narrow ? "ctl" : "control", pts: CONTROL, control: true },
                ...SWEEP.map(([f, pts]) => ({ label: narrow ? short(f) : f.toFixed(2), name: f.toFixed(2), pts }))];
  const slot = (W - L - R) / cols.length, spread = narrow ? 7 : 9, r = narrow ? 3.6 : 4.5;
  const F = frame({ W, H, L, R, T, B, x: { min: 0, max: cols.length, ticks: [], label: "rehearsal fraction f" },
                    y: { min: 1080, max: 1220, ticks: [1080, 1100, 1120, 1140, 1160, 1180, 1200, 1220], fmt: num, label: narrow ? "" : "hits, of 1,229" } });
  let s = F.markup;
  const hline = (v, color, dash) => {
    const y = F.sy(v).toFixed(1);
    s += `<line x1="${L}" x2="${W - R}" y1="${y}" y2="${y}" style="stroke: var(${color}); stroke-width: 1.5; ${dash ? "stroke-dasharray: 5 4" : ""}"/>`;
  };
  hline(ANCHOR, "--muted", false);
  hline(BAND, "--gold", true);
  cols.forEach((c, i) => {
    const cx = L + slot * (i + 0.5);
    s += `<text x="${cx.toFixed(1)}" y="${H - B + 17}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${c.label}</text>`;
    c.pts.forEach((v, k) => {
      const off = (k - (c.pts.length - 1) / 2) * spread;
      s += `<circle cx="${(cx + off).toFixed(1)}" cy="${F.sy(v).toFixed(1)}" r="${r}" style="fill: var(${c.control ? "--bad" : "--cell"}); stroke: var(--panel); stroke-width: 1.2"/>`;
    });
  });
  // the control is named where it sits, so it is not told apart by its colour alone
  const c0 = L + slot * 0.5, yc = F.sy(CONTROL[0]);
  s += `<text x="${(c0 + spread + 6).toFixed(1)}" y="${(yc - 9).toFixed(1)}" ${FONT} style="fill: var(--ink)">policy target withheld</text>`;
  s += `<rect id="sw-cursor" x="0" y="${T}" width="${slot.toFixed(1)}" height="${H - T - B}" style="fill: var(--ink)" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#sw-cursor");
  svg.onpointermove = ev => {
    const i = Math.max(0, Math.min(cols.length - 1, Math.floor((pointerX(svg, ev, W) - L) / slot)));
    const c = cols[i];
    cursor.setAttribute("x", (L + slot * i).toFixed(1));
    cursor.setAttribute("opacity", "0.06");
    $("sw-tip").textContent = c.control
      ? `Control, policy target withheld, f = 0: ${c.pts.map(num).join(" and ")} hits (seeds 0 and 1), ${ANCHOR - Math.max(...c.pts)} or more below the anchor's ${num(ANCHOR)}.`
      : `f = ${c.name}: seeds read ${c.pts.map(num).join(", ")}; the anchor reads ${num(ANCHOR)}, the pass line is ${num(BAND)}.`;
  };
  svg.onpointerdown = svg.onpointermove;  // a tap reads a column too
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

numbersTable("sw-table", ["Rehearsal fraction f", "Seed 0", "Seed 1", "Seed 2"],
  [["0.00, policy target withheld (control)", ...CONTROL.map(num), "no arm"], ...SWEEP.map(([f, pts]) => [f.toFixed(2), ...pts.map(num)])]);

function draw() { drawM1(); drawSweep(); }
draw();
onRedraw(draw);
