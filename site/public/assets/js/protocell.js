// Protocell: the cell's wiring, and stage 4a's world from the project's own records
// (docs/prereg/stage4b.md, stage4d.md, stage4e.md, stage5.md, stage5c.md, stage6.md and
// stage6b.md, and docs/data/stage6/test/stage6.json for stage 6's B0; private repository).

// ---- the cell, drawn to its wiring: 16 wall nodes in a ring, 8 core neurons, spokes both ways ----
function drawCell() {
  const svg = $("cell-fig"), cx = 190, cy = 172, Rw = 112, Rc = 40, N = 16, K = 8, alpha = 0.35;
  const light = { x: 96, y: 78 };  // where the light is brightest, for the glow and the wall's shading
  let s = "";
  // a glow that has faded out before the picture's edges
  s += `<defs><radialGradient id="pc-glow" cx="${light.x}" cy="${light.y}" r="150" gradientUnits="userSpaceOnUse">
    <stop offset="0" style="stop-color: var(--gold); stop-opacity: 0.38"/><stop offset="0.5" style="stop-color: var(--gold); stop-opacity: 0.12"/>
    <stop offset="0.62" style="stop-color: var(--gold); stop-opacity: 0"/></radialGradient></defs>`;
  s += `<circle cx="${light.x}" cy="${light.y}" r="150" style="fill: url(#pc-glow)"/>`;
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
    const d = Math.hypot(w.x - light.x, w.y - light.y), lit = Math.max(0, Math.min(1, (250 - d) / 200));
    s += `<circle cx="${w.x.toFixed(1)}" cy="${w.y.toFixed(1)}" r="9" style="fill: var(--panel); stroke: var(--cell); stroke-width: 1.6"/>`;
    s += `<circle cx="${w.x.toFixed(1)}" cy="${w.y.toFixed(1)}" r="9" style="fill: var(--gold); opacity: ${(0.1 + 0.85 * lit).toFixed(2)}"/>`;
  }
  for (const c of core) s += `<circle cx="${c.x.toFixed(1)}" cy="${c.y.toFixed(1)}" r="7" style="fill: var(--cell); stroke: var(--panel); stroke-width: 1.2"/>`;
  s += `<text x="${light.x - 60}" y="${light.y - 44}" font-family="IBM Plex Mono, monospace" font-size="12" style="fill: var(--muted)">light</text>`;
  svg.innerHTML = s;
}

// ---- stage 4a's world: each test against its own B0 and B8, on its own fresh starts ----
// cells: [fitness, 1 if above B8 with an interval clear of zero]
const ROWS = [
  { name: "evolved from nothing", detail: "stage 4b, the best of the pilots, 24 validation starts", b0: 0.148, b8: 0.567, cells: [[0.241, 0]] },
  { name: "fitted to B8's beats", detail: "stage 4d, the better of two modes", b0: 0.144, b8: 0.555, cells: [[0.142, 0]] },
  { name: "written weight by weight", detail: "stage 4e, the better of two modes", b0: 0.156, b8: 0.554, cells: [[0.152, 0]] },
  { name: "the same, sensing relative light", detail: "stage 5b, design 16: 0.909 of the gap", b0: 0.163, b8: 0.563, cells: [[0.527, 0]] },
  { name: "searched from design 16", detail: "stage 5c, three champions; design 16 scored 0.537 on these starts", b0: 0.168, b8: 0.557, cells: [[0.610, 1], [0.593, 1], [0.574, 0]] },
  { name: "evolved, relative sensing", detail: "stage 6, three runs from random genomes, 200 generations; design 16 scored 0.509 on these starts", b0: 0.165, b8: 0.538, cells: [[0.588, 1], [0.510, 0], [0.165, 0]] },
  { name: "the same, 400 generations", detail: "stage 6b, five fresh runs from random genomes; design 16 scored 0.560 on these starts", b0: 0.166, b8: 0.558, cells: [[0.642, 1], [0.623, 1], [0.569, 0], [0.556, 0], [0.425, 0]] },
];
function drawChart() {
  const svg = $("pc-chart"), W = chartWidth(svg), narrow = W < 560;
  const L = narrow ? 10 : 230, R = narrow ? 14 : 20, T = 12, B = 42, rowH = narrow ? 48 : 55;
  const H = T + B + rowH * ROWS.length;
  sizeChart(svg, W, H);
  const x0 = 0.1, x1 = 0.65, sx = v => L + ((v - x0) / (x1 - x0)) * (W - L - R);
  const muted = css("--muted"), line = css("--line");
  let s = "";
  for (let t = 0.1; t <= 0.651; t += 0.05) {
    const x = sx(t).toFixed(1);
    s += `<line x1="${x}" x2="${x}" y1="${T}" y2="${H - B}" stroke="${line}" stroke-width="1"/>`;
    if (Math.round(t * 100) % 10 === 0) s += `<text x="${x}" y="${H - B + 18}" text-anchor="middle" ${FONT} fill="${muted}">${t.toFixed(1)}</text>`;
  }
  s += `<text x="${((L + W - R) / 2).toFixed(1)}" y="${H - 6}" text-anchor="middle" ${FONT} fill="${muted}">${narrow ? "fitness" : "fitness: mean energy reserve over a lifetime"}</text>`;
  ROWS.forEach((r, i) => {
    // on a phone the row's name sits above its track
    const y = T + rowH * (i + (narrow ? 0.68 : 0.5));
    if (narrow) s += `<text x="${L}" y="${(y - 15).toFixed(1)}" ${FONT} style="fill: var(--ink)">${r.name}</text>`;
    else s += `<text x="${L - 12}" y="${(y + 4).toFixed(1)}" text-anchor="end" ${FONT} style="fill: var(--ink)">${r.name}</text>`;
    s += `<line x1="${sx(r.b0).toFixed(1)}" x2="${sx(r.b8).toFixed(1)}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" style="stroke: var(--line); stroke-width: 6; stroke-linecap: round"/>`;
    s += `<circle cx="${sx(r.b0).toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" style="fill: var(--panel); stroke: var(--muted); stroke-width: 2"/>`;
    const bx = sx(r.b8);
    s += `<rect x="${(bx - 5).toFixed(1)}" y="${(y - 5).toFixed(1)}" width="10" height="10" transform="rotate(45 ${bx.toFixed(1)} ${y.toFixed(1)})" style="fill: var(--gold)"/>`;
    for (const [v, beat] of r.cells) {
      const x = sx(v).toFixed(1);
      // a cell that clears the criterion is green and ringed, so it is not told by colour alone
      if (beat) s += `<circle cx="${x}" cy="${y.toFixed(1)}" r="${narrow ? 7 : 8.5}" style="fill: var(--panel); stroke: var(--ok); stroke-width: 1.5"/><circle cx="${x}" cy="${y.toFixed(1)}" r="${narrow ? 4 : 5}" style="fill: var(--ok)"/>`;
      else s += `<circle cx="${x}" cy="${y.toFixed(1)}" r="5.5" style="fill: var(--cell); stroke: var(--panel); stroke-width: 1.5"/>`;
    }
  });
  s += `<rect id="pc-cursor" x="0" y="0" width="${W}" height="${rowH}" style="fill: var(--ink)" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#pc-cursor");
  svg.onpointermove = ev => {
    const box = svg.getBoundingClientRect(), yv = ((ev.clientY - box.top) / box.height) * H;
    const i = Math.max(0, Math.min(ROWS.length - 1, Math.floor((yv - T) / rowH))), row = ROWS[i];
    cursor.setAttribute("y", (T + rowH * i).toFixed(1));
    cursor.setAttribute("opacity", "0.05");
    const cells = row.cells.map(c => c[0].toFixed(3)).join(", ");
    $("pc-tip").textContent = `${row.name} (${row.detail}): cell ${cells}; B0 ${row.b0.toFixed(3)}; B8 ${row.b8.toFixed(3)}.`;
  };
  svg.onpointerdown = svg.onpointermove;  // a tap reads a row too
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}

numbersTable("pc-table", ["Approach", "Where it is from", "B0, a still cell", "The cell", "B8, the best simple rule"],
  ROWS.map(r => [r.name, r.detail, r.b0.toFixed(3),
                 r.cells.map(c => c[0].toFixed(3) + (c[1] ? " (above B8, interval clear of zero)" : "")).join("; "), r.b8.toFixed(3)]));

function draw() { drawCell(); drawChart(); }
draw();
onRedraw(draw);
