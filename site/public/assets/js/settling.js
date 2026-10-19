// Settling time: every B2/S34 soup against the two laws, and the universality ratio.
const SITE = window.SITE, ST = SITE.settling;
const logLaw = L => ST.log[0] * Math.log(L) + ST.log[1];
const powLaw = L => ST.power[0] * L ** ST.power[1];

// ---- the soups ----
let showPower = true;
function medians() {
  const by = new Map();
  for (const [L, t, study] of ST.seeds) {
    if (!by.has(L)) by.set(L, { L, study, ts: [] });
    by.get(L).ts.push(t);
  }
  return [...by.values()].sort((a, b) => a.L - b.L).map(g => {
    const s = g.ts.slice().sort((a, b) => a - b), k = s.length;
    return { L: g.L, study: g.study, n: k, median: k % 2 ? s[(k - 1) / 2] : (s[k / 2 - 1] + s[k / 2]) / 2 };
  });
}
const MED = medians();
function drawSoups() {
  const svg = $("st-chart"), top = Math.ceil(Math.max(...ST.seeds.map(s => s[1]), powLaw(1024)) / 50) * 50;
  const yt = []; for (let t = 0; t <= top; t += 100) yt.push(t);
  const F = frame({ H: 360, x: { min: 6, max: 1400, log: true, ticks: [8, 16, 32, 64, 128, 256, 512, 1024], label: "torus side L (log scale)" },
                    y: { min: 0, max: top, ticks: yt, label: "settling time, generations" } });
  let s = "";
  const band = (a, b, label) => {
    const x0 = F.sx(a), x1 = F.sx(b);
    s += `<rect x="${x0.toFixed(1)}" y="${F.T}" width="${(x1 - x0).toFixed(1)}" height="${F.H - F.T - F.B}" style="fill: var(--gold-soft); opacity: 0.35"/>`;
    s += `<text x="${((x0 + x1) / 2).toFixed(1)}" y="${F.T + 14}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${label}</text>`;
  };
  band(7, 36, "fitted");
  band(56, 145, "loop's test");
  band(170, 1150, "registered replication");
  s += F.markup;
  // a fixed jitter per soup, so redraws do not move the points
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (const [L, t] of ST.seeds) {
    const x = F.sx(L * Math.exp((rnd() - 0.5) * 0.12));
    s += `<circle cx="${x.toFixed(1)}" cy="${F.sy(t).toFixed(1)}" r="1.7" style="fill: var(--cell-soft)"/>`;
  }
  const curve = (f, color) => {
    let d = "";
    for (let i = 0; i <= 120; i++) {
      const L = 8 * (1024 / 8) ** (i / 120);
      d += `${i ? "L" : "M"}${F.sx(L).toFixed(1)} ${F.sy(f(L)).toFixed(1)} `;
    }
    s += `<path d="${d}" style="fill: none; stroke: var(${color}); stroke-width: 2"/>`;
  };
  curve(logLaw, "--ok");
  if (showPower) curve(powLaw, "--bad");
  for (const m of MED) {
    s += `<circle cx="${F.sx(m.L).toFixed(1)}" cy="${F.sy(m.median).toFixed(1)}" r="4.5" style="fill: var(${m.study ? "--gold" : "--cell"}); stroke: var(--panel); stroke-width: 1.2"/>`;
  }
  s += `<line id="st-cursor" x1="0" x2="0" y1="${F.T}" y2="${F.H - F.B}" stroke="${css("--ink")}" stroke-width="1" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#st-cursor");
  svg.onpointermove = ev => {
    const xv = pointerX(svg, ev, F.W);
    let best = MED[0];
    for (const m of MED) if (Math.abs(F.sx(m.L) - xv) < Math.abs(F.sx(best.L) - xv)) best = m;
    cursor.setAttribute("x1", F.sx(best.L)); cursor.setAttribute("x2", F.sx(best.L)); cursor.setAttribute("opacity", "0.35");
    $("st-tip").textContent = `L = ${best.L}: median of ${best.n} soups ${best.median.toFixed(1)}; log law ${logLaw(best.L).toFixed(1)}, power law ${powLaw(best.L).toFixed(1)}${best.study ? " (registered replication)" : ""}.`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}
function setPower(on) {
  showPower = on;
  $("st-both").setAttribute("aria-pressed", String(on));
  $("st-log").setAttribute("aria-pressed", String(!on));
  drawSoups();
}
$("st-both").addEventListener("click", () => setPower(true));
$("st-log").addEventListener("click", () => setPower(false));

// ---- the ratio ----
function drawRatio() {
  const svg = $("ratio-chart");
  const rows = [...ST.universality.map(([lat, rule, v, e]) => ({ name: `${lat} ${rule}`, v, e, own: false })),
                { name: "hexagon B2/S34, all data", v: 0.765, e: 0.042, own: true }];
  const W = 760, L = 290, R = 20, T = 16, rowH = 32, H = T + rows.length * rowH + 42;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const lo = 0.4, hi = 1.1, X = v => L + ((v - lo) / (hi - lo)) * (W - L - R);
  const [sv, se] = ST.shared;
  let s = `<rect x="${X(sv - se).toFixed(1)}" y="${T}" width="${(X(sv + se) - X(sv - se)).toFixed(1)}" height="${rows.length * rowH}" style="fill: var(--cell-soft); opacity: 0.7"/>`;
  for (let t = 0.4; t <= 1.1001; t += 0.1) {
    s += `<line x1="${X(t).toFixed(1)}" x2="${X(t).toFixed(1)}" y1="${T}" y2="${T + rows.length * rowH}" style="stroke: var(--line)"/>`;
    s += `<text x="${X(t).toFixed(1)}" y="${T + rows.length * rowH + 18}" text-anchor="middle" ${FONT} style="fill: var(--muted)">${t.toFixed(1)}</text>`;
  }
  s += `<line x1="${X(ST.gumbel)}" x2="${X(ST.gumbel)}" y1="${T - 6}" y2="${T + rows.length * rowH}" style="stroke: var(--ink); stroke-width: 1.6"/>`;
  s += `<text x="${X(ST.gumbel) + 6}" y="${T + rows.length * rowH + 36}" ${FONT} style="fill: var(--ink)">Gumbel 0.786</text>`;
  rows.forEach((r, i) => {
    const y = T + i * rowH + rowH / 2, c = r.own ? "--gold" : "--cell";
    s += `<text x="${L - 12}" y="${y + 4}" text-anchor="end" ${FONT} style="fill: var(--ink)">${r.name.length > 40 ? r.name.slice(0, 39) + "…" : r.name}</text>`;
    s += `<line x1="${X(r.v - r.e).toFixed(1)}" x2="${X(r.v + r.e).toFixed(1)}" y1="${y}" y2="${y}" style="stroke: var(${c}); stroke-width: 2"/>`;
    s += `<circle cx="${X(r.v).toFixed(1)}" cy="${y}" r="5" style="fill: var(${c})"/>`;
    s += `<rect class="hit" data-i="${i}" x="0" y="${y - rowH / 2}" width="${W}" height="${rowH}" style="fill: transparent"/>`;
  });
  svg.innerHTML = s;
  svg.onpointermove = ev => {
    const hit = ev.target.closest && ev.target.closest(".hit");
    if (!hit) return;
    const r = rows[Number(hit.dataset.i)], z = (r.v - ST.gumbel) / r.e;
    $("ratio-tip").textContent = `${r.name}: ${r.v.toFixed(2)} ± ${r.e.toFixed(2)}, ${Math.abs(z).toFixed(1)} standard errors ${z < 0 ? "below" : "above"} Gumbel's 0.786.`;
  };
}

drawSoups();
drawRatio();
onRedraw(() => { drawSoups(); drawRatio(); });
