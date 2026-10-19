// Parity laws: the simulator, the square law's chart, and the hexagon's two laws.
const SITE = window.SITE, RULES = SITE.rules;
const SIM_RULES = {
  xor: RULES.xor.terms,
  xorself: [...RULES.xor.terms, [0, 0]],
  n4: RULES.n4.terms,
  n4self: RULES.n4self.terms,
  h1: RULES.h1.terms,
};

// ---- the simulator ----
let rule = "xor";
const sim = makeSim({
  canvas: $("sim-canvas"), terms: SIM_RULES.xor, n: 31,
  onStep(gen, live) {
    $("sim-gen").textContent = gen.toLocaleString("en-US");
    $("sim-live").textContent = live.toLocaleString("en-US");
  },
  onPeriod(res, ms) {
    const out = $("sim-period"), law = $("sim-law");
    if (!res) { out.textContent = "…"; return; }
    out.textContent = res.dies ? "dies" : res.period.toLocaleString("en-US");
    if (rule === "xor") {
      const L = xorLaw(sim.n), agree = L.dies === res.dies && L.period === res.period;
      const formula = L.dies
        ? `n = 2<sup>${L.v}</sup>: the torus dies`
        : `2<sup>${L.v}</sup> · (2<sup>${L.s}</sup> − 1) = ${L.period.toLocaleString("en-US")}, with m = ${L.m}, sord(m) = ${L.s}`;
      law.innerHTML = `${formula} <span class="badge ${agree ? "ok" : "bad"}">${agree ? "agrees" : "differs"}</span> <span class="note">(${ms} ms)</span>`;
    } else {
      law.innerHTML = `<span class="note">The square law is for B1357/S1357; this rule's period is exact only (${ms} ms).</span>`;
    }
  },
});
sim.reset();
const playBtn = $("sim-play");
function setPlaying(on) { sim.play(on); playBtn.textContent = on ? "Pause" : "Play"; }
playBtn.addEventListener("click", () => setPlaying(!sim.playing));
$("sim-step").addEventListener("click", () => sim.step());
$("sim-reset").addEventListener("click", () => sim.reset());
$("sim-rule").addEventListener("change", e => { rule = e.target.value; sim.terms = SIM_RULES[rule]; sim.reset(); });
$("sim-n").addEventListener("input", e => {
  sim.n = Number(e.target.value);
  $("sim-n-out").textContent = sim.n;
  sim.reset();
});

// ---- the square law ----
function drawLaw() {
  const svg = $("law-chart"), rows = SITE.xor.rows;
  const F = frame({ x: { min: 0, max: 200, ticks: [0, 25, 50, 75, 100, 125, 150, 175, 200], label: "torus side n" },
                    y: { min: 0, max: 100, ticks: [0, 25, 50, 75, 100], fmt: t => `2^${t}`, label: "period" } });
  const cell = css("--cell"), muted = css("--muted"), gold = css("--gold");
  let s = F.markup;
  for (const [n, period, dies, , rival] of rows) {
    s += `<circle cx="${F.sx(n).toFixed(1)}" cy="${F.sy(log2Big(period)).toFixed(1)}" r="3" fill="${dies ? muted : cell}"/>`;
    if (rival !== period) s += `<circle cx="${F.sx(n).toFixed(1)}" cy="${F.sy(log2Big(rival)).toFixed(1)}" r="4.5" fill="none" stroke="${gold}" stroke-width="1.6"/>`;
  }
  s += `<line id="law-cursor" x1="0" x2="0" y1="${F.T}" y2="${F.H - F.B}" stroke="${css("--ink")}" stroke-width="1" opacity="0"/>`;
  svg.innerHTML = s;
  const byN = new Map(rows.map(r => [r[0], r])), cursor = svg.querySelector("#law-cursor");
  svg.onpointermove = ev => {
    const n = Math.max(3, Math.min(200, Math.round(((pointerX(svg, ev, F.W) - F.L) / (F.W - F.L - F.R)) * 200)));
    const r = byN.get(n);
    if (!r) return;
    cursor.setAttribute("x1", F.sx(n)); cursor.setAttribute("x2", F.sx(n)); cursor.setAttribute("opacity", "0.35");
    const L = xorLaw(n);
    let text = `n = ${n} = 2^${L.v} · ${L.m}: `;
    text += r[2] ? "the torus dies (period 1), as the law says." : `measured ${fmt(r[1])}; the law gives ${fmt(r[3])}.`;
    if (r[4] !== r[1]) text += ` The rival law would give ${fmt(r[4])}.`;
    $("law-tip").textContent = text;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

// ---- the hexagon's two laws ----
let hexLaw = "first";
function drawHex() {
  const svg = $("hex-chart"), rows = SITE.hexagon.rows, col = hexLaw === "first" ? 3 : 4;
  const maxN = Math.max(...rows.map(r => r[0])), top = Math.ceil(Math.max(...rows.map(r => log2Big(r[1]))) / 50) * 50;
  const xt = []; for (let t = 0; t <= maxN; t += 50) xt.push(t);
  const yt = []; for (let t = 0; t <= top; t += 50) yt.push(t);
  const F = frame({ x: { min: 0, max: maxN, ticks: xt, label: "torus side n" },
                    y: { min: 0, max: top, ticks: yt, fmt: t => `2^${t}`, label: "period" } });
  const ok = css("--ok"), bad = css("--bad");
  const r2 = rows.filter(r => r[5] === 2).map(r => r[0]), x0 = F.sx(Math.min(...r2) - 1), x1 = F.sx(maxN);
  let s = `<rect x="${x0.toFixed(1)}" y="${F.T}" width="${(x1 - x0).toFixed(1)}" height="${F.H - F.T - F.B}" style="fill: var(--gold-soft); opacity: 0.55"/>` + F.markup;
  let misses = 0;
  for (const r of rows) {
    const agree = r[1] === r[col];
    if (!agree) misses++;
    const cx = F.sx(r[0]).toFixed(1);
    s += `<circle cx="${cx}" cy="${F.sy(log2Big(r[1])).toFixed(1)}" r="${agree ? 2.6 : 4}" fill="${agree ? ok : bad}"/>`;
    if (!agree) s += `<circle cx="${cx}" cy="${F.sy(log2Big(r[col])).toFixed(1)}" r="5" fill="none" stroke="${bad}" stroke-width="1.4"/>`;
  }
  s += `<line id="hex-cursor" x1="0" x2="0" y1="${F.T}" y2="${F.H - F.B}" stroke="${css("--ink")}" stroke-width="1" opacity="0"/>`;
  svg.innerHTML = s;
  const r1 = rows.filter(r => r[5] === 1 && r[1] !== r[col]).length, r2m = rows.filter(r => r[5] === 2 && r[1] !== r[col]).length;
  $("hex-tip").textContent = hexLaw === "first"
    ? `The first law misses ${misses} of ${rows.length} sizes: ${r1} in the registered round, and ${r2m} more among the round 2 sizes it was never registered for. Point at a size to read it.`
    : `The corrected law agrees at all ${rows.length - misses} of ${rows.length} sizes. Point at a size to read it.`;
  const byN = new Map(rows.map(r => [r[0], r])), cursor = svg.querySelector("#hex-cursor");
  svg.onpointermove = ev => {
    const n = Math.round(((pointerX(svg, ev, F.W) - F.L) / (F.W - F.L - F.R)) * maxN);
    let best = null;
    for (let d = 0; d <= 4 && !best; d++) best = byN.get(n - d) || byN.get(n + d);
    if (!best) return;
    cursor.setAttribute("x1", F.sx(best[0])); cursor.setAttribute("x2", F.sx(best[0])); cursor.setAttribute("opacity", "0.35");
    let v = 0, m = best[0]; while (m % 2 === 0) { m /= 2; v++; }
    const agree = best[1] === best[col];
    $("hex-tip").textContent = `n = ${best[0]} = 2^${v} · ${m} (round ${best[5]}): measured ${fmt(best[1])}; the ${hexLaw === "first" ? "first" : "corrected"} law gives ${fmt(best[col])}${agree ? "." : `, off by a factor of ${(BigInt(best[col]) / BigInt(best[1])).toString()}.`}`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}
function setHex(which) {
  hexLaw = which;
  $("hex-first").setAttribute("aria-pressed", String(which === "first"));
  $("hex-corr").setAttribute("aria-pressed", String(which === "corrected"));
  drawHex();
}
$("hex-first").addEventListener("click", () => setHex("first"));
$("hex-corr").addEventListener("click", () => setHex("corrected"));

drawLaw();
drawHex();
onRedraw(() => { sim.draw(); drawLaw(); drawHex(); });
if (!reducedMotion()) setPlaying(true);
