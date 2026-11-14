// Protocell: the cell's wiring, and stage 4a's world from the project's own records
// (docs/prereg/stage4b.md, stage4d.md, stage4e.md, stage5.md, stage5c.md; private repository).

// ---- the cell, drawn to its wiring: 16 wall nodes in a ring, 8 core neurons, spokes both ways ----
function drawCell() {
  const svg = $("cell-fig"), cx = 190, cy = 170, Rw = 112, Rc = 40, N = 16, K = 8, alpha = 0.35;
  const light = { x: 10, y: 20 };  // where the light comes from, for shading the wall nodes
  let s = "";
  // light, falling from the upper left
  s += `<defs><radialGradient id="pc-glow" cx="${light.x}" cy="${light.y}" r="370" gradientUnits="userSpaceOnUse">
    <stop offset="0" style="stop-color: var(--gold); stop-opacity: 0.35"/><stop offset="1" style="stop-color: var(--gold); stop-opacity: 0"/></radialGradient></defs>`;
  s += `<rect x="0" y="0" width="380" height="340" style="fill: url(#pc-glow)"/>`;
  const wall = [], core = [];
  for (let i = 0; i < N; i++) {
    const t = (2 * Math.PI * i) / N - Math.PI / 2;
    wall.push({ x: cx + Rw * Math.cos(t), y: cy + Rw * Math.sin(t), t });
  }
  for (let j = 0; j < K; j++) {
    const t = (2 * Math.PI * j) / K - Math.PI / 2 + Math.PI / K;
    core.push({ x: cx + Rc * Math.cos(t), y: cy + Rc * Math.sin(t) });
  }
  // the core's own links (all to all) and the spokes, both faint
  for (const a of core) for (const b of core) if (a !== b) s += `<line x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" style="stroke: var(--cell); stroke-width: 0.6; opacity: 0.35"/>`;
  wall.forEach((w, i) => {
    const c = core[Math.floor(i / 2)];
    s += `<line x1="${w.x.toFixed(1)}" y1="${w.y.toFixed(1)}" x2="${c.x.toFixed(1)}" y2="${c.y.toFixed(1)}" style="stroke: var(--muted); stroke-width: 0.8; opacity: 0.6"/>`;
  });
  // the ring's links
  s += `<circle cx="${cx}" cy="${cy}" r="${Rw}" style="fill: none; stroke: var(--cell); stroke-width: 2"/>`;
  // cilia, each along its node's radius turned by one shared angle
  for (const w of wall) {
    const a = w.t + alpha, x0 = w.x + 11 * Math.cos(w.t), y0 = w.y + 11 * Math.sin(w.t);
    const x1 = x0 + 20 * Math.cos(a), y1 = y0 + 20 * Math.sin(a);
    const mx = (x0 + x1) / 2 + 4 * Math.cos(a + Math.PI / 2), my = (y0 + y1) / 2 + 4 * Math.sin(a + Math.PI / 2);
    s += `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} Q${mx.toFixed(1)} ${my.toFixed(1)} ${x1.toFixed(1)} ${y1.toFixed(1)}" style="fill: none; stroke: var(--muted); stroke-width: 1.4; stroke-linecap: round"/>`;
  }
  // wall nodes, shaded by the light where they sit
  for (const w of wall) {
    const d = Math.hypot(w.x - light.x, w.y - light.y), lit = Math.max(0, Math.min(1, (330 - d) / 200));
    s += `<circle cx="${w.x.toFixed(1)}" cy="${w.y.toFixed(1)}" r="9" style="fill: var(--panel); stroke: var(--cell); stroke-width: 1.6"/>`;
    s += `<circle cx="${w.x.toFixed(1)}" cy="${w.y.toFixed(1)}" r="9" style="fill: var(--gold); opacity: ${(0.15 + 0.8 * lit).toFixed(2)}"/>`;
  }
  for (const c of core) s += `<circle cx="${c.x.toFixed(1)}" cy="${c.y.toFixed(1)}" r="7" style="fill: var(--cell); stroke: var(--panel); stroke-width: 1.2"/>`;
  // labels
  const notes = [
    [52, "16 wall nodes", "each senses the light at its place and beats a cilium"],
    [104, "ring links", "each node to its two neighbours, in a closed loop"],
    [156, "8 core neurons", "fully connected, with time constants of a second to an hour"],
    [208, "spokes, both ways", "every wall node to the core and back"],
    [260, "one network", "wall and core are one recurrent network; evolution sets"],
  ];
  for (const [y, head, body] of notes) {
    s += `<text x="400" y="${y}" font-family="IBM Plex Mono, monospace" font-size="13" style="fill: var(--ink)">${head}</text>`;
    s += `<text x="400" y="${y + 19}" font-family="STIX Two Text, serif" font-size="14" style="fill: var(--muted)">${body}</text>`;
  }
  s += `<text x="400" y="298" font-family="STIX Two Text, serif" font-size="14" style="fill: var(--muted)">its weights through a genome of 103 or 135 numbers</text>`;
  svg.innerHTML = s;
}

// ---- stage 4a's world: each test against its own B0 and B8, on its own fresh starts ----
const ROWS = [
  { name: "evolved from nothing", detail: "stage 4b, the best of the pilots, 24 validation starts", b0: 0.148, b8: 0.567, cells: [[0.241, 0]] },
  { name: "fitted to B8's beats", detail: "stage 4d, the better of two modes", b0: 0.144, b8: 0.555, cells: [[0.142, 0]] },
  { name: "written weight by weight", detail: "stage 4e, the better of two modes", b0: 0.156, b8: 0.554, cells: [[0.152, 0]] },
  { name: "the same, sensing relative light", detail: "stage 5b, design 16: 0.909 of the gap", b0: 0.163, b8: 0.563, cells: [[0.527, 0]] },
  { name: "searched from design 16", detail: "stage 5c, three champions; design 16 scored 0.537 on these starts", b0: 0.168, b8: 0.557, cells: [[0.610, 1], [0.593, 1], [0.574, 0]] },
];
function drawChart() {
  const svg = $("pc-chart"), W = 760, H = 330, L = 230, R = 20, T = 12, B = 42;
  const x0 = 0.1, x1 = 0.65, sx = v => L + ((v - x0) / (x1 - x0)) * (W - L - R);
  const rowH = (H - T - B) / ROWS.length, muted = css("--muted"), line = css("--line");
  let s = "";
  for (let t = 0.1; t <= 0.651; t += 0.05) {
    const x = sx(t).toFixed(1);
    s += `<line x1="${x}" x2="${x}" y1="${T}" y2="${H - B}" stroke="${line}" stroke-width="1"/>`;
    if (Math.round(t * 100) % 10 === 0) s += `<text x="${x}" y="${H - B + 18}" text-anchor="middle" ${FONT} fill="${muted}">${t.toFixed(1)}</text>`;
  }
  s += `<text x="${((L + W - R) / 2).toFixed(1)}" y="${H - 6}" text-anchor="middle" ${FONT} fill="${muted}">fitness: mean energy reserve over a lifetime</text>`;
  ROWS.forEach((r, i) => {
    const y = T + rowH * (i + 0.5);
    s += `<text x="${L - 12}" y="${(y + 4).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--ink)">${r.name}</text>`;
    s += `<line x1="${sx(r.b0).toFixed(1)}" x2="${sx(r.b8).toFixed(1)}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" style="stroke: var(--line); stroke-width: 6; stroke-linecap: round"/>`;
    s += `<circle cx="${sx(r.b0).toFixed(1)}" cy="${y.toFixed(1)}" r="5" style="fill: var(--panel); stroke: var(--muted); stroke-width: 2"/>`;
    const bx = sx(r.b8);
    s += `<rect x="${(bx - 5).toFixed(1)}" y="${(y - 5).toFixed(1)}" width="10" height="10" transform="rotate(45 ${bx.toFixed(1)} ${y.toFixed(1)})" style="fill: var(--gold)"/>`;
    for (const [v, beat] of r.cells) {
      s += `<circle cx="${sx(v).toFixed(1)}" cy="${y.toFixed(1)}" r="6" style="fill: var(${beat ? "--ok" : "--cell"}); stroke: var(--panel); stroke-width: 1.2"/>`;
    }
  });
  s += `<rect id="pc-cursor" x="0" y="0" width="${W}" height="${rowH.toFixed(1)}" style="fill: var(--ink)" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#pc-cursor");
  svg.onpointermove = ev => {
    const r = svg.getBoundingClientRect(), yv = ((ev.clientY - r.top) / r.height) * H;
    const i = Math.max(0, Math.min(ROWS.length - 1, Math.floor((yv - T) / rowH))), row = ROWS[i];
    cursor.setAttribute("y", (T + rowH * i).toFixed(1));
    cursor.setAttribute("opacity", "0.05");
    const cells = row.cells.map(c => c[0].toFixed(3)).join(", ");
    $("pc-tip").textContent = `${row.name} (${row.detail}): cell ${cells}; B0 ${row.b0.toFixed(3)}; B8 ${row.b8.toFixed(3)}.`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

function draw() { drawCell(); drawChart(); }
draw();
onRedraw(draw);
