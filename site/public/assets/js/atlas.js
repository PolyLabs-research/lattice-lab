// The linear atlas: the eigenvalue map, the identities, the census, and m = 37.
const SITE = window.SITE, RULES = SITE.rules;

// ---------------- eigenvalue map ----------------
const EV_RULES = ["m1", "m2", "m3", "m4", "m5", "m6", "ctrl", "xor", "n4", "n4self", "h1", "triE", "triEVOVS", "vot13", "cube", "dil"];
const ev = { rule: "ctrl", m: 37, mode: "cube", map: null };
const evRule = $("ev-rule"), evM = $("ev-m"), evCanvas = $("ev-canvas");
for (const key of EV_RULES) evRule.add(new Option(RULES[key].label, key));
for (const m of Object.keys(SITE.fields).map(Number).sort((a, b) => a - b)) evM.add(new Option(String(m), String(m)));
function evCompute() {
  ev.map = eigenMap(RULES[ev.rule].terms, ev.m);
  const M = ev.map;
  $("ev-field").textContent = `F(2^${M.d}), eigenvalues in F(2^${M.s})`;
  $("ev-full").textContent = `2^${M.s} − 1 = ${fmt(M.full)}`;
  $("ev-odd").textContent = fmt(M.lcm);
  $("ev-verdict").innerHTML = M.lcm === M.full
    ? `<span class="badge ok">reaches the full bound</span>`
    : `<span class="badge gold">falls short by ${fmt(M.full / M.lcm)}</span>`;
  const nz = M.info.filter(i => !i.zero), cubes = nz.filter(i => i.cube).length;
  let count = `${M.classes} distinct up to Frobenius, ${nz.length} orbits`;
  count += M.cubeExp !== null ? `; ${cubes} of ${nz.length} orbits are cubes` : "; every element of this field is a cube";
  $("ev-count").textContent = count;
  drawEv();
}
function mix(a, b, t) {
  const p = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
  const A = p(a), B = p(b);
  return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * t)).join(",")})`;
}
function drawEv(hoverOrbit = -1) {
  const M = ev.map, m = M.m, ctx = fitCanvas(evCanvas), W = evCanvas.width, cs = W / m;
  const line = css("--line"), cell = css("--cell"), soft = css("--cell-soft"), gold = css("--gold"), ink = css("--ink");
  ctx.fillStyle = css("--paper"); ctx.fillRect(0, 0, W, evCanvas.height);
  for (let j = 0; j < m; j++) for (let k = 0; k < m; k++) {
    const o = M.id[j * m + k], i = M.info[o];
    let c;
    if (i.zero) c = line;
    else if (ev.mode === "cube") c = i.cube === null ? soft : i.cube ? gold : cell;
    else c = mix(soft, cell, Math.max(0, Math.min(1, Math.log2(Number(i.ord)) / M.s)));
    ctx.fillStyle = c;
    const gap = cs > 7 ? 1 : 0;
    ctx.fillRect(Math.floor(k * cs), Math.floor(j * cs), Math.ceil(cs) - gap, Math.ceil(cs) - gap);
    if (o === hoverOrbit && cs > 3) {
      ctx.strokeStyle = ink; ctx.lineWidth = Math.max(1, cs / 8);
      ctx.strokeRect(Math.floor(k * cs) + 1, Math.floor(j * cs) + 1, Math.ceil(cs) - 3, Math.ceil(cs) - 3);
    }
  }
  $("ev-legend").innerHTML = ev.mode === "cube"
    ? (M.cubeExp === null
      ? `<span><i class="swatch" style="background: var(--cell-soft)"></i>every value is a cube here</span><span><i class="swatch" style="background: var(--line)"></i>zero</span>`
      : `<span><i class="swatch" style="background: var(--gold)"></i>cube</span><span><i class="swatch" style="background: var(--cell)"></i>not a cube</span><span><i class="swatch" style="background: var(--line)"></i>zero</span>`)
    : `<span><i class="swatch" style="background: var(--cell-soft)"></i>small order</span><span><i class="swatch" style="background: var(--cell)"></i>order near the full bound</span><span><i class="swatch" style="background: var(--line)"></i>zero</span>`;
}
evCanvas.addEventListener("pointermove", e => {
  const M = ev.map, rect = evCanvas.getBoundingClientRect();
  const k = Math.floor(((e.clientX - rect.left) / rect.width) * M.m), j = Math.floor(((e.clientY - rect.top) / rect.height) * M.m);
  if (j < 0 || k < 0 || j >= M.m || k >= M.m) return;
  const o = M.id[j * M.m + k], i = M.info[o];
  $("ev-hover").textContent = i.zero
    ? `(j, k) = (${j}, ${k}): zero`
    : `(j, k) = (${j}, ${k}): order ${fmt(i.ord)}${i.cube === null ? "" : i.cube ? ", a cube" : ", not a cube"}; orbit of ${i.size}`;
  drawEv(o);
});
evCanvas.addEventListener("pointerleave", () => drawEv());
function setMode(mode) {
  ev.mode = mode;
  $("ev-mode-order").setAttribute("aria-pressed", String(mode === "order"));
  $("ev-mode-cube").setAttribute("aria-pressed", String(mode === "cube"));
  drawEv();
}
$("ev-mode-order").addEventListener("click", () => setMode("order"));
$("ev-mode-cube").addEventListener("click", () => setMode("cube"));
evRule.addEventListener("change", e => { ev.rule = e.target.value; evCompute(); });
evM.addEventListener("change", e => { ev.m = Number(e.target.value); evCompute(); });
function showIdentity(i) {
  mechPick.value = String(i); showIdent(i);
  $("mech-pick").closest(".figure").scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
}
function showEv(rule, m, mode) {
  ev.rule = rule; ev.m = m; evRule.value = rule; evM.value = String(m);
  setMode(mode); evCompute();
  $("eigen").scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
}
$("open-show").addEventListener("click", () => showEv("m1", 37, "cube"));
$("open-ctrl").addEventListener("click", () => showEv("ctrl", 37, "cube"));

// ---------------- identities ----------------
const R90 = (dx, dy) => [[dx, dy], [-dx, -dy]];
const IDENTS = [
  {
    name: "Splitting: two hexagon steps are three passes of rule 90",
    text: "The hexagon's parity rule H1, squared, is the product of three one-dimensional rule-90 passes, x + 1/x, y + 1/y and x/y + y/x, one along each lattice direction. So the hexagon's eigenvalues are products of rule 90's, and its odd period is rule 90's: the corrected hexagon law.",
    left: [["H1", RULES.h1.terms], ["H1", RULES.h1.terms]],
    right: [["x + 1/x", R90(1, 0)], ["y + 1/y", R90(0, 1)], ["x/y + y/x", R90(1, -1)]],
  },
  {
    name: "Powers: N4 + K8 + C4 is a cube",
    text: "Square N4 + K8 + C4 is N4³. A cube's eigenvalues are cubes, so its period is N4's divided by gcd(P, 3). Round 2 found the cubes from its first failure: A4 + K8 + C4 + self, which is (N4 + self)³, fell to a third of the full bound at n = 197.",
    left: [["N4", RULES.n4.terms], ["N4", RULES.n4.terms], ["N4", RULES.n4.terms]],
    right: [["N4 + K8 + C4", RULES.cube.terms]],
  },
  {
    name: "Dilations: C4 + self lives on a smaller torus",
    text: "C4 + self is N4 + self with every translation tripled. When 3 divides n, it acts on the n-torus as N4 + self acts on the n/3-torus, so its period is the smaller torus's.",
    left: [["(N4 + self)(x³, y³)", ldil(RULES.n4self.terms, 3)]],
    right: [["C4 + self", RULES.dil.terms]],
  },
  {
    name: "Twisted powers: VO + T13",
    text: "The triangle rule VO + T13 has s equal to the edge rule's s times its own dilation by 3. Where 3 ≡ ±2^k (mod m), the dilation acts on eigenvalues as a Frobenius power, so they are λ^(1 + 2^k). Round 3 found this mechanism during its run, and it explained all seven of that rule's failures.",
    left: [["s of E", RULES.triE.terms], ["s of E, dilated by 3", ldil(RULES.triE.terms, 3)]],
    right: [["s of VO + T13", RULES.vot13.terms]],
  },
  {
    name: "Triangles: two steps are one step of s",
    text: "The edge rule's matrix is [[0, u], [d, 0]]: up cells read three down cells, and down cells three up cells. Its square is (u d) I, so two steps of the triangle rule are one step of the plane rule s = u d on each orientation.",
    left: [["u (up from down)", RULES.triE.ud], ["d (down from up)", RULES.triE.du]],
    right: [["s of E", RULES.triE.terms]],
  },
  {
    name: "Half-Frobenius at m = 37: A4 + K8 + B4 + self",
    text: "Found by the fourth pilot's agent. At m = 37, 2^9 ≡ −6 and 6² ≡ −1, so multiplying a character by 6 acts on eigenvalues as the Frobenius x ↦ x^(2^9). A rule whose cells are unchanged by ×6 has every eigenvalue in F(2^9), and every element of F(2^9) is a cube in F(2^18). W = A4 + K8 + B4 + self is not such a rule, but W(x², y²) times four rule-90 passes, whose eigenvalues are cubes at 37, is the shell of eight cells at (±7, ±5) and (±5, ±7), and ×6 maps that shell onto itself mod 37.",
    left: [["W(x², y²)", ldil(RULES.m1.terms, 2)], ["x + 1/x", R90(1, 0)], ["y + 1/y", R90(0, 1)], ["xy + 1/(xy)", R90(1, 1)], ["x/y + y/x", R90(1, -1)]],
    right: [["(±7, ±5), (±5, ±7)", [[7, 5], [7, -5], [-7, 5], [-7, -5], [5, 7], [5, -7], [-5, 7], [-5, -7]]]],
    extra(R) {
      const red = T => new Set(T.map(([x, y]) => `${((x % 37) + 37) % 37},${((y % 37) + 37) % 37}`));
      const a = red(R), b = red(R.map(([x, y]) => [6 * x, 6 * y]));
      const same = a.size === b.size && [...a].every(k => b.has(k));
      return `<span class="badge ${same ? "ok" : "bad"}">${same ? "unchanged by ×6 mod 37" : "changed by ×6 mod 37"}</span>`;
    },
  },
];
const mechPick = $("mech-pick");
IDENTS.forEach((d, i) => mechPick.add(new Option(d.name, String(i))));
function stencilSvg(terms) {
  const xs = terms.map(t => t[0]), ys = terms.map(t => t[1]);
  const x0 = Math.min(0, ...xs) - 1, x1 = Math.max(0, ...xs) + 1, y0 = Math.min(0, ...ys) - 1, y1 = Math.max(0, ...ys) + 1;
  const w = x1 - x0 + 1, h = y1 - y0 + 1, s = Math.max(8, Math.min(16, Math.floor(150 / Math.max(w, h))));
  const set = new Set(terms.map(t => t.join(",")));
  let out = `<svg viewBox="0 0 ${w * s} ${h * s}" width="${w * s}" height="${h * s}" aria-hidden="true">`;
  for (let y = y1; y >= y0; y--) for (let x = x0; x <= x1; x++) {
    const on = set.has(x + "," + y), px = (x - x0) * s, py = (y1 - y) * s;
    out += `<rect x="${px + 0.5}" y="${py + 0.5}" width="${s - 1}" height="${s - 1}" style="fill: ${on ? "var(--cell)" : "var(--paper)"}; stroke: var(--line); stroke-width: 0.6"/>`;
    if (x === 0 && y === 0) out += `<circle cx="${px + s / 2}" cy="${py + s / 2}" r="${s * 0.28}" style="fill: none; stroke: ${on ? "var(--panel)" : "var(--gold)"}; stroke-width: 1.4"/>`;
  }
  return out + "</svg>";
}
const stencil = (label, terms) => `<div class="stencil">${stencilSvg(terms)}<div class="cap">${label}<br>${terms.length} translations</div></div>`;
function showIdent(i) {
  const d = IDENTS[i];
  $("mech-text").textContent = d.text;
  const prod = side => side.reduce((acc, [, t]) => lmul(acc, t), [[0, 0]]);
  const L = prod(d.left), Rr = prod(d.right);
  const side = s => s.map(([lab, t]) => stencil(lab, t)).join(`<span class="op">×</span>`);
  let html = side(d.left);
  if (d.left.length > 1) html += `<span class="op">→</span>` + stencil("product", L);
  html += `<span class="op">=</span>` + side(d.right);
  if (d.right.length > 1) html += `<span class="op">→</span>` + stencil("product", Rr);
  $("mech-eq").innerHTML = html;
  const same = lsame(L, Rr);
  $("mech-check").innerHTML = `<span class="badge ${same ? "ok" : "bad"}">${same ? "both sides equal" : "the sides differ"}</span>${d.extra ? " " + d.extra(Rr) : ""} <span class="note">multiplied out in your browser: ${L.length} and ${Rr.length} translations</span>`;
}
mechPick.addEventListener("change", e => showIdent(Number(e.target.value)));

// ---------------- the census ----------------
function drawCensus() {
  const svg = $("census-chart"), C = SITE.census;
  const bars = [
    ...Object.entries(C.train).map(([m, r]) => ({ m: Number(m), rules: r, held: false, done: true })),
    ...C.heldout_sizes.map(m => ({ m, rules: C.heldout[m] || [], held: true, done: m in C.heldout })),
  ].sort((a, b) => a.m - b.m);
  const maxM = Math.max(...bars.map(b => b.m)) + 7;
  const F = frame({ H: 300, x: { min: 0, max: maxM, ticks: [0, 37, 100, 161, 225, 300].filter(t => t <= maxM), label: "odd part m" },
                    y: { min: 0, max: Math.sqrt(60), ticks: [0, 1, 6, 25, 51].map(Math.sqrt), fmt: t => String(Math.round(t * t)), label: "rules (square-root scale)" } });
  let s = F.markup;
  const base = F.sy(0);
  for (const b of bars) {
    const x = F.sx(b.m) - 2.2, n = b.rules.length;
    if (!b.done) { s += `<rect x="${x.toFixed(1)}" y="${(base - 10).toFixed(1)}" width="4.4" height="10" style="fill: none; stroke: var(--muted); stroke-width: 0.8; stroke-dasharray: 2 2"/>`; continue; }
    const top = F.sy(Math.sqrt(n));
    s += `<rect x="${x.toFixed(1)}" y="${top.toFixed(1)}" width="4.4" height="${Math.max(0, base - top).toFixed(1)}" style="fill: ${b.held ? "var(--gold)" : "var(--cell)"}"/>`;
    if (n === 0) s += `<rect x="${x.toFixed(1)}" y="${(base - 1.5).toFixed(1)}" width="4.4" height="1.5" style="fill: ${b.held ? "var(--gold)" : "var(--cell)"}; opacity: 0.6"/>`;
  }
  s += `<text x="${F.sx(37) + 8}" y="${F.sy(Math.sqrt(6)) - 4}" ${FONT} style="fill: var(--ink)">m = 37: six rules</text>`;
  s += `<line id="census-cursor" x1="0" x2="0" y1="${F.T}" y2="${F.H - F.B}" stroke="${css("--ink")}" stroke-width="1" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#census-cursor"), tip = $("census-tip");
  svg.onpointermove = ev => {
    const m = ((pointerX(svg, ev, F.W) - F.L) / (F.W - F.L - F.R)) * maxM;
    let best = bars[0];
    for (const b of bars) if (Math.abs(b.m - m) < Math.abs(best.m - m)) best = b;
    cursor.setAttribute("x1", F.sx(best.m)); cursor.setAttribute("x2", F.sx(best.m)); cursor.setAttribute("opacity", "0.35");
    const where = best.held ? "held-out" : "given to the agent";
    if (!best.done) { tip.textContent = `m = ${best.m} (held-out): registered, not yet computed.`; return; }
    const n = best.rules.length;
    tip.textContent = `m = ${best.m} (${where}): ${n === 0 ? "no unexplained rule" : n === 1 ? "1 rule, " + best.rules[0] : `${n} rules` + (n <= 6 ? ": " + best.rules.join("; ") : "")}.`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

// ---------------- the fourth pilot ----------------
const p37 = SITE.pilot37;
if (p37 && p37.html) {
  $("m37-pilot").innerHTML = p37.html;
  if (p37.eyebrow) $("m37-eyebrow").textContent = p37.eyebrow;
}
const identBtn = document.getElementById("m37-identity");
if (identBtn) identBtn.addEventListener("click", () => showIdentity(IDENTS.length - 1));

evRule.value = ev.rule; evM.value = String(ev.m);
evCompute();
showIdent(0);
drawCensus();
onRedraw(() => { drawEv(); drawCensus(); });
