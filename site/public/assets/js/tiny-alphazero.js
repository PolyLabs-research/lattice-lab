// Tiny AlphaZero: two charts from the project's own run logs
// (github.com/PolyLabs-research/Tiny-AlphaZero-v2, RUNLOG-p2_s.md to RUNLOG-p2_ab.md).

// Each round's two arms: mean score over 200-game reps against Stockfish 16 at skill 5, 10,000
// nodes a move (six reps an arm to p2_w; twelve in p2_aa; in p2_ab twelve against the 24 of the
// two four-million runs), and the round's registered test K1 (change − baseline, 95% interval).
// sep: 1 better and separated, −1 worse and separated, 0 not separated.
const ROUNDS = [
  { r: "p2_s", lever: "128 simulations again, then a step down", base: ["48", 0.330], arm: ["128", 0.325], d: "−0.005", ci: "−0.033 to +0.023", sep: 0 },
  { r: "p2_t", lever: "positions labelled by Stockfish, a quarter of each batch", base: ["no teacher", 0.310], arm: ["teacher", 0.360], d: "+0.050", ci: "+0.014 to +0.085", sep: 1 },
  { r: "p2_u", lever: "the teacher's positions labelled afresh", base: ["old labels", 0.3608], arm: ["fresh", 0.3563], d: "−0.005", ci: "−0.038 to +0.028", sep: 0 },
  { r: "p2_v", lever: "the teacher at half of each batch, not a quarter", base: ["quarter", 0.3779], arm: ["half", 0.3338], d: "−0.044", ci: "−0.078 to −0.010", sep: -1 },
  { r: "p2_w", lever: "256 more teacher rows on top of each batch", base: ["quarter", 0.3788], arm: ["wider", 0.3521], d: "−0.027", ci: "−0.061 to +0.007", sep: 0 },
  // RUNLOG-p2_aa.md §3 (K1), RUNLOG-p2_ab.md §3 (K1)
  { r: "p2_aa", lever: "the start trained on four million Stockfish-labelled positions alone, each seen about four times: the diagnostic's training, run again", base: ["the start, 12 reps", 0.3810], arm: ["4M, 12 reps", 0.4165], d: "+0.0354", ci: "+0.0112 to +0.0596", sep: 1 },
  { r: "p2_ab", lever: "twice the labelled positions, eight million", base: ["4M, two runs, 24 reps", 0.4214], arm: ["8M, 12 reps", 0.4446], d: "+0.0232", ci: "+0.0011 to +0.0451", sep: 1 },
];
const VERDICT = { 1: "better, separated", 0: "not separated", [-1]: "worse, separated" };

// p2_y: one network (p2_w_quarter_down/0010, 48 simulations a move) against seven opponents of
// published rating, 200 games each. Performance, with the 95% interval where the log gives one.
const BENCH = [
  { name: "Stockfish 16, UCI_Elo 1400", rating: 1400, wdl: "156-8-36", score: "0.800", perf: 1641 },
  { name: "Shallow Blue 2.0.0", rating: 1578, wdl: "12-8-180", score: "0.080", perf: 1154, ci: [1067, 1224] },
  { name: "Stockfish 16, UCI_Elo 1600", rating: 1600, wdl: "97-8-95", score: "0.505", perf: 1603 },
  { name: "Stockfish 16, UCI_Elo 1800", rating: 1800, wdl: "69-9-122", score: "0.368", perf: 1706 },
  { name: "HoiChess 0.22.0", rating: 1806, wdl: "10-40-150", score: "0.150", perf: 1505, ci: [1447, 1554] },
  { name: "Micro-Max 4.8", rating: 1854, wdl: "13-13-174", score: "0.098", perf: 1467, ci: [1376, 1535] },
  { name: "Stockfish 16, UCI_Elo 2000", rating: 2000, wdl: "40-8-152", score: "0.220", perf: 1780 },
];
const num = v => v.toLocaleString("en-US");

function drawLevers() {
  const svg = $("levers-chart"), W = chartWidth(svg), narrow = W < 560, H = narrow ? 300 : 360;
  const L = narrow ? 40 : 58, R = narrow ? 6 : 16, T = 24, B = narrow ? 30 : 42;
  sizeChart(svg, W, H);
  const n = ROUNDS.length, slot = (W - L - R) / n, dx = narrow ? 7 : 10;
  const F = frame({ W, H, L, R, T, B, x: { min: 0, max: n, ticks: [] },
                    y: { min: 0.30, max: 0.46, ticks: [0.30, 0.32, 0.34, 0.36, 0.38, 0.40, 0.42, 0.44, 0.46], fmt: v => v.toFixed(2), label: narrow ? "" : "score against skill 5" } });
  let s = F.markup;
  ROUNDS.forEach((r, i) => {
    const cx = L + slot * (i + 0.5), xb = cx - dx, xa = cx + dx, yb = F.sy(r.base[1]), ya = F.sy(r.arm[1]);
    s += `<line x1="${xb.toFixed(1)}" y1="${yb.toFixed(1)}" x2="${xa.toFixed(1)}" y2="${ya.toFixed(1)}" style="stroke: var(--muted); stroke-width: 1.5"/>`;
    // the baseline arm is a hollow ring; the change is a shape that says how the test came out
    s += `<circle cx="${xb.toFixed(1)}" cy="${yb.toFixed(1)}" r="4.5" style="fill: var(--panel); stroke: var(--muted); stroke-width: 2"/>`;
    const ring = "stroke: var(--panel); stroke-width: 1.5";
    if (r.sep > 0) s += `<path d="M${xa.toFixed(1)} ${(ya - 8).toFixed(1)} l7.5 13.5 h-15 Z" style="fill: var(--ok); ${ring}"/>`;
    else if (r.sep < 0) s += `<path d="M${xa.toFixed(1)} ${(ya + 8).toFixed(1)} l7.5 -13.5 h-15 Z" style="fill: var(--bad); ${ring}"/>`;
    else s += `<circle cx="${xa.toFixed(1)}" cy="${ya.toFixed(1)}" r="5.5" style="fill: var(--cell); ${ring}"/>`;
    // only the changes that separated carry their difference as a label
    if (r.sep) s += `<text x="${xa.toFixed(1)}" y="${(ya + (r.sep > 0 ? -13 : 23)).toFixed(1)}" text-anchor="middle" ${FONT} style="fill: var(--ink)">${r.d}</text>`;
    s += `<text x="${cx.toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${r.r}</text>`;
  });
  s += `<rect id="lv-cursor" x="0" y="${T}" width="${slot.toFixed(1)}" height="${H - T - B}" style="fill: var(--ink)" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#lv-cursor");
  svg.onpointermove = ev => {
    const i = Math.max(0, Math.min(n - 1, Math.floor((pointerX(svg, ev, W) - L) / slot))), r = ROUNDS[i];
    cursor.setAttribute("x", (L + slot * i).toFixed(1));
    cursor.setAttribute("opacity", "0.06");
    $("levers-tip").textContent = `${r.r}: ${r.lever}. ${r.base[0]} ${r.base[1]}, ${r.arm[0]} ${r.arm[1]}; registered test ${r.d} (${r.ci}), ${VERDICT[r.sep]}.`;
  };
  svg.onpointerdown = svg.onpointermove;  // a tap reads a round too
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

function drawBench() {
  const svg = $("bench-chart"), W = chartWidth(svg), narrow = W < 560;
  const L = narrow ? 8 : 196, R = narrow ? 14 : 20, T = 12, B = 42, rowH = narrow ? 44 : 39;
  const H = T + B + rowH * BENCH.length;
  sizeChart(svg, W, H);
  const x0 = narrow ? 1000 : 940, x1 = 2050, sx = v => L + ((v - x0) / (x1 - x0)) * (W - L - R);
  const muted = css("--muted"), line = css("--line");
  let s = "";
  for (let t = 1000; t <= 2000; t += 100) {
    s += `<line x1="${sx(t).toFixed(1)}" x2="${sx(t).toFixed(1)}" y1="${T}" y2="${H - B}" stroke="${line}" stroke-width="1"/>`;
    if (t % (narrow ? 400 : 200) === 0) s += `<text x="${sx(t).toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} fill="${muted}">${num(t)}</text>`;
  }
  s += `<text x="${((L + W - R) / 2).toFixed(1)}" y="${H - 6}" text-anchor="middle" ${FONT} fill="${muted}">rating, CCRL scale</text>`;
  const fit = [1644, 1704];
  s += `<rect x="${sx(fit[0]).toFixed(1)}" y="${T}" width="${(sx(fit[1]) - sx(fit[0])).toFixed(1)}" height="${H - T - B}" style="fill: var(--cell-soft); opacity: 0.45"/>`;
  BENCH.forEach((b, i) => {
    // on a phone the opponent's name sits above its row, with the performance at the right
    const y = T + rowH * (i + (narrow ? 0.7 : 0.5));
    if (narrow) {
      s += `<text x="${L}" y="${(y - 14).toFixed(1)}" ${FONT} style="fill: var(--ink)">${b.name}</text>`;
      s += `<text x="${W - R}" y="${(y - 14).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--muted)">${num(b.perf)}</text>`;
    } else {
      s += `<text x="${L - 12}" y="${(y + 4).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--ink)">${b.name}</text>`;
    }
    s += `<line x1="${sx(Math.min(b.rating, b.perf)).toFixed(1)}" x2="${sx(Math.max(b.rating, b.perf)).toFixed(1)}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" style="stroke: var(--line); stroke-width: 2"/>`;
    if (b.ci) s += `<line x1="${sx(b.ci[0]).toFixed(1)}" x2="${sx(b.ci[1]).toFixed(1)}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" style="stroke: var(--cell); stroke-width: 3; opacity: 0.55"/>`;
    s += `<circle cx="${sx(b.rating).toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" style="fill: var(--panel); stroke: var(--muted); stroke-width: 2"/>`;
    s += `<circle cx="${sx(b.perf).toFixed(1)}" cy="${y.toFixed(1)}" r="5.5" style="fill: var(--cell); stroke: var(--panel); stroke-width: 1.5"/>`;
    if (!narrow) {
      // the performance, on the side away from the opponent's rating and past the interval
      const below = b.perf < b.rating, edge = b.ci ? b.ci[below ? 0 : 1] : b.perf;
      s += `<text x="${(sx(edge) + (below ? -10 : 10)).toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="${below ? "end" : "start"}" ${FONT} style="fill: var(--muted)">${num(b.perf)}</text>`;
    }
  });
  svg.innerHTML = s;
}

numbersTable("levers-table", ["Round", "The change", "Baseline arm", "Changed arm", "Registered test (95% interval)", "Outcome"],
  ROUNDS.map(r => [r.r, r.lever, `${r.base[0]}: ${r.base[1]}`, `${r.arm[0]}: ${r.arm[1]}`, `${r.d} (${r.ci})`, VERDICT[r.sep]]));
numbersTable("bench-table", ["Opponent", "Its rating", "Won-drawn-lost", "Score", "Performance (95% interval)"],
  BENCH.map(b => [b.name, num(b.rating), b.wdl, b.score, num(b.perf) + (b.ci ? ` (${num(b.ci[0])} to ${num(b.ci[1])})` : "")]));

function draw() { drawLevers(); drawBench(); }
draw();
onRedraw(draw);
