// Tiny AlphaZero: two charts from the project's own run logs
// (github.com/PolyLabs-research/Tiny-AlphaZero-v2, RUNLOG-p2_q.md to RUNLOG-p2_y.md).

// Each round's two arms: mean score over six 200-game reps against Stockfish 16 at skill 5,
// 10,000 nodes a move, and the round's registered test K1 (change − baseline, 95% interval).
// sep: 1 better and separated, −1 worse and separated, 0 not separated.
const ROUNDS = [
  { r: "p2_q", lever: "40 more iterations at learning rate 2e-6", base: ["the start", 0.306], arm: ["after 40", 0.315], k1: "+0.009 [−0.018, +0.035]", sep: 0 },
  { r: "p2_r", lever: "128 self-play simulations a move, not 48", base: ["48", 0.341], arm: ["128", 0.321], k1: "−0.020 [−0.055, +0.015]", sep: 0 },
  { r: "p2_s", lever: "128 simulations again, then a step down", base: ["48", 0.330], arm: ["128", 0.325], k1: "−0.005 [−0.033, +0.023]", sep: 0 },
  { r: "p2_t", lever: "positions labelled by Stockfish, a quarter of each batch", base: ["no teacher", 0.310], arm: ["teacher", 0.360], k1: "+0.050 [+0.014, +0.085]", sep: 1 },
  { r: "p2_u", lever: "the teacher's positions labelled afresh", base: ["old labels", 0.3608], arm: ["fresh", 0.3563], k1: "−0.005 [−0.038, +0.028]", sep: 0 },
  { r: "p2_v", lever: "the teacher at half of each batch, not a quarter", base: ["quarter", 0.3779], arm: ["half", 0.3338], k1: "−0.044 [−0.078, −0.010]", sep: -1 },
  { r: "p2_w", lever: "256 more teacher rows on top of each batch", base: ["quarter", 0.3788], arm: ["wider", 0.3521], k1: "−0.027 [−0.061, +0.007]", sep: 0 },
];

// p2_y: one network (p2_w_quarter_down/0010, 48 simulations a move) against seven opponents of
// published rating, 200 games each. Performance, with the 95% interval where the log gives one.
const BENCH = [
  { name: "Stockfish 16, UCI_Elo 1400", rating: 1400, wdl: "156-8-36", score: 0.800, perf: 1641 },
  { name: "Shallow Blue 2.0.0", rating: 1578, wdl: "12-8-180", score: 0.080, perf: 1154, ci: [1067, 1224] },
  { name: "Stockfish 16, UCI_Elo 1600", rating: 1600, wdl: "97-8-95", score: 0.505, perf: 1603 },
  { name: "Stockfish 16, UCI_Elo 1800", rating: 1800, wdl: "69-9-122", score: 0.368, perf: 1706 },
  { name: "HoiChess 0.22.0", rating: 1806, wdl: "10-40-150", score: 0.150, perf: 1505, ci: [1447, 1554] },
  { name: "Micro-Max 4.8", rating: 1854, wdl: "13-13-174", score: 0.098, perf: 1467, ci: [1376, 1535] },
  { name: "Stockfish 16, UCI_Elo 2000", rating: 2000, wdl: "40-8-152", score: 0.220, perf: 1780 },
];

function drawLevers() {
  const svg = $("levers-chart"), W = 760, H = 360, L = 58, R = 16, T = 16, B = 42;
  const n = ROUNDS.length, slot = (W - L - R) / n;
  const F = frame({ W, H, L, R, T, B, x: { min: 0, max: n, ticks: [] },
                    y: { min: 0.30, max: 0.40, ticks: [0.30, 0.32, 0.34, 0.36, 0.38, 0.40], fmt: v => v.toFixed(2), label: "score against skill 5" } });
  let s = F.markup;
  const col = r => (r.sep > 0 ? "--ok" : r.sep < 0 ? "--bad" : "--cell");
  ROUNDS.forEach((r, i) => {
    const cx = L + slot * (i + 0.5), yb = F.sy(r.base[1]), ya = F.sy(r.arm[1]);
    s += `<line x1="${(cx - 9).toFixed(1)}" y1="${yb.toFixed(1)}" x2="${(cx + 9).toFixed(1)}" y2="${ya.toFixed(1)}" style="stroke: var(--muted); stroke-width: 1.5"/>`;
    s += `<circle cx="${(cx - 9).toFixed(1)}" cy="${yb.toFixed(1)}" r="5" style="fill: var(--muted); stroke: var(--panel); stroke-width: 1.2"/>`;
    s += `<circle cx="${(cx + 9).toFixed(1)}" cy="${ya.toFixed(1)}" r="6" style="fill: var(${col(r)}); stroke: var(--panel); stroke-width: 1.2"/>`;
    s += `<text x="${cx.toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${r.r}</text>`;
  });
  s += `<rect id="lv-cursor" x="0" y="${T}" width="${slot.toFixed(1)}" height="${H - T - B}" style="fill: var(--ink)" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#lv-cursor");
  svg.onpointermove = ev => {
    const i = Math.max(0, Math.min(n - 1, Math.floor((pointerX(svg, ev, W) - L) / slot))), r = ROUNDS[i];
    cursor.setAttribute("x", (L + slot * i).toFixed(1));
    cursor.setAttribute("opacity", "0.06");
    $("levers-tip").textContent = `${r.r}: ${r.lever}. ${r.base[0]} ${r.base[1]}, ${r.arm[0]} ${r.arm[1]}; registered test ${r.k1}${r.sep ? "" : ", not separated"}.`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

function drawBench() {
  const svg = $("bench-chart"), W = 760, H = 330, L = 196, R = 20, T = 12, B = 42;
  const x0 = 1000, x1 = 2050, sx = v => L + ((v - x0) / (x1 - x0)) * (W - L - R);
  const rowH = (H - T - B) / BENCH.length;
  const muted = css("--muted"), line = css("--line");
  let s = "";
  for (let t = 1000; t <= 2000; t += 100) {
    s += `<line x1="${sx(t).toFixed(1)}" x2="${sx(t).toFixed(1)}" y1="${T}" y2="${H - B}" stroke="${line}" stroke-width="1"/>`;
    if (t % 200 === 0) s += `<text x="${sx(t).toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} fill="${muted}">${t.toLocaleString("en-US")}</text>`;
  }
  s += `<text x="${((L + W - R) / 2).toFixed(1)}" y="${H - 6}" text-anchor="middle" ${FONT} fill="${muted}">rating, CCRL scale</text>`;
  const fit = [1644, 1704];
  s += `<rect x="${sx(fit[0]).toFixed(1)}" y="${T}" width="${(sx(fit[1]) - sx(fit[0])).toFixed(1)}" height="${H - T - B}" style="fill: var(--cell-soft); opacity: 0.45"/>`;
  BENCH.forEach((b, i) => {
    const y = T + rowH * (i + 0.5);
    s += `<text x="${L - 12}" y="${(y + 4).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--ink)">${b.name}</text>`;
    s += `<line x1="${sx(Math.min(b.rating, b.perf)).toFixed(1)}" x2="${sx(Math.max(b.rating, b.perf)).toFixed(1)}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" style="stroke: var(--line); stroke-width: 2"/>`;
    if (b.ci) s += `<line x1="${sx(b.ci[0]).toFixed(1)}" x2="${sx(b.ci[1]).toFixed(1)}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" style="stroke: var(--cell); stroke-width: 3; opacity: 0.55"/>`;
    s += `<circle cx="${sx(b.rating).toFixed(1)}" cy="${y.toFixed(1)}" r="5" style="fill: var(--panel); stroke: var(--muted); stroke-width: 2"/>`;
    s += `<circle cx="${sx(b.perf).toFixed(1)}" cy="${y.toFixed(1)}" r="5.5" style="fill: var(--cell); stroke: var(--panel); stroke-width: 1.2"/>`;
    s += `<text x="${(sx(b.perf) + (b.perf < b.rating ? -10 : 10)).toFixed(1)}" y="${(y - 9).toFixed(1)}" text-anchor="${b.perf < b.rating ? "end" : "start"}" ${FONT} style="fill: var(--muted)">${b.perf.toLocaleString("en-US")}</text>`;
  });
  s += `<text x="${((sx(fit[0]) + sx(fit[1])) / 2).toFixed(1)}" y="${H - B - 4}" text-anchor="middle" ${FONT} style="fill: var(--muted)">Stockfish fit</text>`;
  svg.innerHTML = s;
}

function draw() { drawLevers(); drawBench(); }
draw();
onRedraw(draw);
