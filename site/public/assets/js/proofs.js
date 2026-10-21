// Proofs: the library's files, their imports, and what each proves.
const MODS = window.SITE.proofs;
const INFO = {
  Identities: { by: "generated", text: "The polynomial identities behind the atlas's mechanisms, with certificates generated from the atlas code: two hexagon steps are three rule-90 passes, N4 + K8 + C4 = N4³, C4 + self = 1 + N4(x³, y³), each triangle rule's s, and VO + T13's twisted factorisation.", key: ["hexagon_two_steps", "square_N4K8C4_cube", "square_C4self_dilation", "triangle_VOT13_twisted"] },
  Eigen: { by: "orchestrator", text: "The order lemma, and the cube and twisted-power mechanisms at the level of eigenvalues.", key: [] },
  Bridge: { by: "orchestrator", text: "The bridge: on an odd torus a rule's period is the lcm of the orders of its nonzero eigenvalues. And the bound: the period divides 2<sup>ord(m)</sup> − 1, or 2<sup>sord(m)</sup> − 1 for a symmetric rule.", key: ["period_eq_eigenLcm", "isPeriod_iff", "period_dvd_two_pow_sub_one_of_symm"] },
  GroupRing: { by: "orchestrator", text: "Every rule acts on every finite torus through the group ring F<sub>2</sub>[Z²]. Frobenius, powers of rules, and the restriction lemma that moves periods between tori.", key: ["gstep_eq_iterate", "gperiod_eq_of_grp_eq_pow", "isEventualPeriod_restrict_iff"] },
  Triangle: { by: "orchestrator", text: "Triangular tori, whose rules are 2 × 2 matrices. If the matrix squares to S times the identity, two steps are one step of S, and the period is exactly 2 P(S) when the rule swaps the layers' parities.", key: ["gtriStep_twice", "gtriPeriod_eq_two_mul"] },
  Rules: { by: "generated", text: "The atlas's own rules as the translations each cell reads, generated from its code, with their Laurent polynomials.", key: [] },
  Tori: { by: "orchestrator", text: "The even-size reduction, on the square and on the atlas's own triangular and hexagonal tori: the odd part of the period is the odd quotient's period, and the 2-part is bounded.", key: ["period_eq_two_pow_mul", "triPeriod_div_gcd", "hexPeriod_div_gcd"] },
  Periods: { by: "orchestrator", text: "The mechanisms as theorems about the atlas's own rules: round 2's cubes and dilation at every size, the triangle rules' periods, and round 3's twisted power.", key: ["period_sqN4K8C4", "period_sqC4self", "atlasTriPeriod_twisted"] },
  TwoPart: { by: "orchestrator", text: "The square law's 2-part: P(2<sup>v</sup>m) = 2<sup>v</sup>P(m) for B1357/S1357 and for N4, at every odd m > 1, through a Jordan block of rule 90 along y.", key: ["period_sqN4D4", "period_two_mul_of_proj"] },
  HexTwoPart: { by: "pilot 1's agent", text: "The hexagon law's 2-part, exactly 2<sup>v+1</sup>P(m) for m ≥ 5. The agent's idea: stop one Frobenius step early, on the sub-torus Z/2m × Z/m, which keeps the Z/2 factor where the extra 2 lives, and find a Jordan block there. Its route differs from the hand proof.", key: ["hexPeriod_hexH1_exact", "hexSub_even"] },
  TriTwoPart: { by: "pilot 2's agent", text: "Both triangle laws' 2-part, exactly 2<sup>v+1</sup>P(m) for m ≥ 3. The same route as the hand proof, which the agent never saw: the sub-torus at level 2<sup>v−1</sup>, and a Jordan block for each rule.", key: ["atlasTriPeriod_triE_exact", "atlasTriPeriod_triEVOVS_exact", "triSub_even"] },
  Cubes37: { by: "pilot 4's agent", text: "The cubes at m = 37, an open question until the agent answered it. At 37, 2<sup>9</sup> ≡ −6, so the dilation by 6 acts on eigenvalues as half a Frobenius: each of six rules, multiplied by rule-90 factors, becomes invariant under it, with eigenvalues in F(2<sup>9</sup>). Each of the six has period dividing 87,381, and so does rule 90, by an explicit cube root.", key: ["period_w_dvd_87381", "period_tri_dvd_87381", "period_r90_dvd", "w_identity"] },
  Cubes25: { by: "pilot 5's agent", text: "The cubes at m = 25, for five of the seventeen rules a census left unexplained. Two have a cube certificate: multiplied by the cube of rule 90 along both axes, each becomes a union of shells that the dilation by 7 = 2<sup>5</sup> maps onto itself, so off the axes its eigenvalues are an element of F(2<sup>5</sup>) over a cube. Three are twisted pairs C(x, y) C(x<sup>3</sup>, y<sup>3</sup>), with 3 = 2<sup>7</sup> mod 25. Each of the five has period dividing 341.", key: ["period_r3096_dvd", "period_r23608_dvd", "period_r1227_dvd", "twisted_val"] },
  UnitCubes: { by: "pilot 6's agent", text: "Unit times cube. Nine square-family rules are exactly U · g<sup>3</sup> over GF(2), with U a product of rule-90 factors or of t + 1 along the axes. The cube needs no reason, and the unit's values are cubes: at 37 because rule 90 is confined there, and at 61, for U = (a + 1)(b + 1), because 3 = 2<sup>6</sup> makes (t + 1)<sup>2</sup> = t<sup>63</sup>. Nine periods divide 87,381 at 37, and three divide (2<sup>30</sup> − 1)/3 at 61.", key: ["period_r1112_dvd_37", "period_r3461_dvd_61", "psi3_val61", "sum_split"] },
  Ninth37: { by: "pilot 7's agent", text: "Ninth powers at m = 37, for the four radius-5 rules that a registered census found and no known mechanism explained. Each is exactly line units times one of the fourth pilot's half-Frobenius cores, W = A4 + K8 + B4 + self or V = C4 + L8 + M8 + E4, with a = x + 1/x and b = y + 1/y: for example 1968276 = a<sup>2</sup>b<sup>2</sup> · V. The cores' values lie in F(2<sup>9</sup>) up to rule-90 factors. Counting each unit's exponent exactly, rather than bounding it by rule 90's cubes, gives one more factor of 3: Ψ<sub>5</sub>(t)<sup>2</sup> = t<sup>2<sup>23</sup> − 1</sup> at 37, since 5 ≡ 2<sup>23</sup>. Each of the four has period dividing 29,127 = (2<sup>18</sup> − 1)/9. The agent's first file did not build; it fixed it in a second round, over the API.", key: ["period_r1968276_dvd", "period_r985232_dvd", "period_r1431278_dvd", "period_r699738_dvd"] },
  VOT13Law: { by: "pilot 3's agent", text: "VO + T13's law, which the agent first found from data. For m ≥ 3 a Jordan block, as for the other triangle rules. For m = 1, which had no proof of any kind, a fibre lemma and three finite facts checked by the kernel.", key: ["atlasTriPeriod_triVOT13_law", "gstep_eq_self_of_fibers"] },
};
const names = Object.keys(MODS).filter(n => INFO[n]);
// depth: the longest chain of imports below a file
const depth = {};
const dep = n => depth[n] ?? (depth[n] = Math.max(-1, ...MODS[n].imports.filter(i => MODS[i]).map(dep)) + 1);
names.forEach(dep);
// keep only the imports not implied by others
const reach = n => { const seen = new Set(), st = [...MODS[n].imports]; while (st.length) { const x = st.pop(); if (!seen.has(x) && MODS[x]) { seen.add(x); st.push(...MODS[x].imports); } } return seen; };
const edges = [];
for (const n of names) {
  const direct = MODS[n].imports.filter(i => MODS[i]);
  for (const i of direct) if (!direct.some(j => j !== i && reach(j).has(i))) edges.push([n, i]);
}
let selected = "Bridge";
const libSvg = $("lib-svg");
function drawLib() {
  const maxD = Math.max(...Object.values(depth)), W = 440, H = 520, rowH = (H - 40) / (maxD + 1), h = 34;
  const rows = {};
  for (const n of names) (rows[depth[n]] ||= []).push(n);
  // pos[n] = [x, y, box width]; a crowded row gets narrower boxes
  const pos = {};
  for (const [d, ns] of Object.entries(rows)) ns.forEach((n, i) => { pos[n] = [((i + 1) * W) / (ns.length + 1), H - 26 - Number(d) * rowH, Math.min(124, W / (ns.length + 1) - 10)]; });
  let s = "";
  for (const [a, b] of edges) s += `<line x1="${pos[a][0]}" y1="${pos[a][1] + h / 2}" x2="${pos[b][0]}" y2="${pos[b][1] - h / 2}" style="stroke: var(--line); stroke-width: 1.4"/>`;
  for (const n of names) {
    const [x, y, w] = pos[n], on = n === selected, by = INFO[n].by;
    const fill = on ? (by.startsWith("pilot") ? "var(--gold)" : "var(--cell)") : "var(--panel)";
    const stroke = by.startsWith("pilot") ? "var(--gold)" : by === "generated" ? "var(--muted)" : "var(--cell)";
    s += `<g class="node" tabindex="0" role="button" aria-pressed="${on}" aria-label="${n}.lean, ${by}" data-n="${n}">`;
    s += `<rect x="${x - w / 2}" y="${y - h / 2}" width="${w}" height="${h}" rx="5" style="fill: ${fill}; stroke: ${stroke}; stroke-width: 1.6${by === "generated" ? "; stroke-dasharray: 3 2" : ""}"/>`;
    s += `<text x="${x}" y="${y + 4}" text-anchor="middle" style="fill: ${on ? "var(--panel)" : "var(--ink)"}; font-family: var(--mono); font-size: 12px">${n}</text></g>`;
  }
  libSvg.innerHTML = s;
  const m = MODS[selected], info = INFO[selected];
  const imps = m.imports.filter(i => MODS[i]);
  $("lib-stage").innerHTML = `
    <div class="eyebrow">${info.by} · ${m.lines} lines · ${m.theorems} theorems</div>
    <h3><code>LatticeProofs/${selected}.lean</code></h3>
    <p>${info.text}</p>
    ${info.key.length ? `<p><strong>Main results:</strong> ${info.key.map(k => `<code>${k}</code>`).join(", ")}</p>` : ""}
    <p class="note">${imps.length ? (m.core ? "Imports " + imps.join(", ") + "." : "Imports the whole core library" + (imps.some(i => !MODS[i].core) ? ", and " + imps.filter(i => !MODS[i].core).join(", ") : "") + ".") : "Imports only mathlib."}</p>`;
}
libSvg.addEventListener("click", e => {
  const g = e.target.closest(".node");
  if (g) { selected = g.dataset.n; drawLib(); libSvg.querySelector(`[data-n="${selected}"]`).focus(); }
});
libSvg.addEventListener("keydown", e => {
  const g = e.target.closest(".node");
  if (g && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); selected = g.dataset.n; drawLib(); libSvg.querySelector(`[data-n="${selected}"]`).focus(); }
});
drawLib();
