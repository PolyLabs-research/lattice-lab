// The model: the loop, the ledger check, and the agents' timelines.
const SITE = window.SITE;

// ---------------- the loop ----------------
const STAGES = [
  {
    name: "Experiment", tool: "LatticeLife",
    what: "Runs Life-like and linear cellular automata on square, hexagonal and triangular tori, and says what each number means. A run that has not settled by its cap gives a bound, not a value, and is recorded as one.",
    guards: "Reading a bound as a measurement; quietly dropping runs that did not finish.",
    example: "Settling times for B2/S34 soups on hexagon tori up to side 1024, 100 soups per size, every run settled.",
    href: "settling.html", link: "Settling time",
  },
  {
    name: "Law", tool: "Kepler",
    what: "Fits, ranks and predicts closed-form laws with error bars: continuous laws ranked by BIC, exact integer laws built from number theory, and matches of fitted constants to known numbers. It also says when the data cannot separate two laws.",
    guards: "A law picked by eye; a winner that its rivals fit almost as well.",
    example: "Kepler found the square parity law, 2^v (2^sord(m) − 1), from simulations, and proposed laws for 42 linear rules nobody had studied.",
    href: "parity.html", link: "Parity laws",
  },
  {
    name: "Registered test", tool: "lattice-lab",
    what: "Writes each law's predictions at sizes nobody has computed to an append-only, hash-chained ledger. The harness refuses to start the run until the registration is committed and pushed, and the verifier checks that every prediction precedes the run.",
    guards: "Choosing the test after seeing the data; moving the goalposts after a miss.",
    example: "The hexagon law was refuted at n = 74, 148 and 190. The corrected law was then registered at 100 new sizes, and held at all of them.",
    href: "#ledger", link: "Check a ledger",
  },
  {
    name: "Proof", tool: "Lean 4 + mathlib",
    what: "What survives is proved. A theorem counts when it builds against the library and #print axioms lists only Lean's standard three: propext, Classical.choice and Quot.sound.",
    guards: "A proof that only looks right; a gap papered over with sorry.",
    example: "The bridge: on an odd torus, a rule's period is the lcm of the orders of its nonzero eigenvalues. Every confinement mechanism of the atlas rests on it.",
    href: "proofs.html", link: "The proof library",
  },
  {
    name: "Agents", tool: "Claude Code sessions",
    what: "A fresh agent gets a problem card, the Lean library and generic tools, in a container that holds nothing to look the answer up in. It proposes a mechanism, checks it numerically and writes the proof. A judge, not the agent, decides whether it counts.",
    guards: "Taking a model's account of its own work as evidence.",
    example: "Seven pilots, seven proofs accepted: six in the judge's first round, and the seventh in its second, after its Lean file failed to build in the first. In the third the agent found its law from data; in the fourth it answered an open question, in the fifth part of a harder one, in the sixth the question the fifth's registered test raised, and in the seventh four of five ninth-power rules at m = 37. Their conditions held at every claim the judge checked.",
    href: "#pilots", link: "The agents, step by step",
  },
];
const loopSvg = $("loop-svg");
let stageIx = 0;
function drawLoop() {
  const cx = 230, cy = 208, r = 150, w = 138, h = 50;
  const pos = STAGES.map((_, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / STAGES.length;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  });
  let s = `<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" style="fill: var(--muted)"/></marker></defs>`;
  for (let i = 0; i < STAGES.length; i++) {
    const a0 = -Math.PI / 2 + ((i + 0.3) * 2 * Math.PI) / STAGES.length;
    const a1 = -Math.PI / 2 + ((i + 0.7) * 2 * Math.PI) / STAGES.length;
    const p0 = [cx + r * Math.cos(a0), cy + r * Math.sin(a0)], p1 = [cx + r * Math.cos(a1), cy + r * Math.sin(a1)];
    s += `<path d="M${p0[0].toFixed(1)} ${p0[1].toFixed(1)} A${r} ${r} 0 0 1 ${p1[0].toFixed(1)} ${p1[1].toFixed(1)}" style="fill: none; stroke: var(--muted); stroke-width: 1.4" marker-end="url(#arrow)"/>`;
  }
  s += `<text x="${cx}" y="${cy - 6}" text-anchor="middle" style="fill: var(--muted); font-family: var(--serif); font-size: 15px; font-style: italic">a claim goes round</text>`;
  s += `<text x="${cx}" y="${cy + 14}" text-anchor="middle" style="fill: var(--muted); font-family: var(--serif); font-size: 15px; font-style: italic">until it is proved or refuted</text>`;
  STAGES.forEach((st, i) => {
    const [x, y] = pos[i], on = i === stageIx;
    s += `<g class="node" tabindex="0" role="button" aria-pressed="${on}" aria-label="${st.name}: ${st.tool}" data-i="${i}">`;
    s += `<rect x="${(x - w / 2).toFixed(1)}" y="${(y - h / 2).toFixed(1)}" width="${w}" height="${h}" rx="6" style="fill: ${on ? "var(--cell)" : "var(--panel)"}; stroke: ${on ? "var(--cell)" : "var(--line)"}; stroke-width: 1.4"/>`;
    s += `<text x="${x.toFixed(1)}" y="${(y - 3).toFixed(1)}" text-anchor="middle" style="fill: ${on ? "var(--panel)" : "var(--ink)"}; font-family: var(--serif); font-size: 16px; font-weight: 600">${st.name}</text>`;
    s += `<text x="${x.toFixed(1)}" y="${(y + 15).toFixed(1)}" text-anchor="middle" style="fill: ${on ? "var(--panel)" : "var(--muted)"}; font-family: var(--mono); font-size: 11px">${st.tool}</text>`;
    s += `</g>`;
  });
  loopSvg.innerHTML = s;
  const st = STAGES[stageIx];
  $("loop-stage").innerHTML = `
    <div class="eyebrow">Stage ${stageIx + 1} of 5 · ${st.tool}</div>
    <h3>${st.name}</h3>
    <p>${st.what}</p>
    <p><strong>Guards against:</strong> ${st.guards}</p>
    <p><strong>From the record:</strong> ${st.example}</p>
    <p><a href="${st.href}">${st.link}</a></p>`;
}
loopSvg.addEventListener("click", e => {
  const g = e.target.closest(".node");
  if (g) { stageIx = Number(g.dataset.i); drawLoop(); loopSvg.querySelector(`[data-i="${stageIx}"]`).focus(); }
});
loopSvg.addEventListener("keydown", e => {
  const g = e.target.closest(".node");
  if (!g) return;
  let i = Number(g.dataset.i);
  if (e.key === "Enter" || e.key === " ") e.preventDefault();
  else if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); i = (i + 1) % STAGES.length; }
  else if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); i = (i + STAGES.length - 1) % STAGES.length; }
  else return;
  stageIx = i; drawLoop(); loopSvg.querySelector(`[data-i="${i}"]`).focus();
});
drawLoop();

// ---------------- the ledger ----------------
const GENESIS = "0".repeat(64);
const PUBLISHED = SITE.ledger.entries.map(e => e.hash);
const ledger = {
  entries: SITE.ledger.entries.map(e => ({ seq: e.seq, kind: e.kind, text: e.text, stored: e.hash })),
  sel: 1,
};
const short = h => h.slice(0, 12) + "…";
const HEX = /[0-9a-f]{64}/g;
function parsed(text) { try { return JSON.parse(text); } catch { return null; } }
function checkLedger() {
  const E = ledger.entries, stored = new Set(E.map(e => e.stored));
  return E.map((e, i) => {
    const recomputed = sha256(e.text), obj = parsed(e.text);
    const prev = obj ? obj.prev : null, want = i === 0 ? GENESIS : E[i - 1].stored;
    const cites = obj && obj.body && obj.body.cites ? JSON.stringify(obj.body.cites).match(HEX) || [] : [];
    return {
      recomputed, json: !!obj, hashOk: recomputed === e.stored, linkOk: prev === want,
      citesOk: cites.every(h => stored.has(h)), published: e.stored === PUBLISHED[i], time: obj ? obj.time : null,
      kind: obj ? obj.kind : e.kind,
    };
  });
}
function renderLedger() {
  const E = ledger.entries, C = checkLedger();
  const chain = $("ledger-chain");
  chain.innerHTML = E.map((e, i) => {
    const c = C[i], ok = c.hashOk && c.linkOk && c.citesOk;
    const mark = !ok ? `<span class="badge bad">${!c.hashOk ? "hash" : !c.linkOk ? "link" : "cites"}</span>`
      : !c.published ? `<span class="badge gold">rewritten</span>` : `<span class="badge ok">ok</span>`;
    return `<div role="listitem"><button type="button" class="entry${ok ? "" : " broken"}" data-i="${i}" aria-pressed="${i === ledger.sel}">
      <span class="seq">${e.seq}</span><span class="kind">${c.kind}${c.time ? " · " + c.time.slice(11, 19) : ""}</span>${mark}
      <span class="h">${short(e.stored)}</span></button></div>`;
  }).join("");
  const i = ledger.sel, e = E[i], c = C[i];
  $("ledger-which").textContent = `${e.seq}, ${c.kind}`;
  $("ledger-stored").textContent = e.stored;
  $("ledger-recomputed").innerHTML = `${c.recomputed} <span class="badge ${c.hashOk ? "ok" : "bad"}">${c.hashOk ? "matches" : "differs"}</span>`;
  $("ledger-link").innerHTML = !c.json ? `<span class="badge bad">not valid JSON</span>`
    : `<span class="badge ${c.linkOk ? "ok" : "bad"}">${c.linkOk ? "matches" : "broken"}</span> ${i === 0 ? "the first entry links to 64 zeros" : "prev = the stored hash of entry " + E[i - 1].seq}`;
  const text = $("ledger-text");
  if (text.value !== e.text) text.value = e.text;

  const broken = C.findIndex(c => !(c.hashOk && c.linkOk));
  const badCites = C.filter(c => !c.citesOk).length, rewritten = C.filter(c => !c.published).length;
  const status = $("ledger-status");
  if (broken >= 0) status.innerHTML = `<span class="badge bad">chain broken at entry ${E[broken].seq}</span>`;
  else if (badCites) status.innerHTML = `<span class="badge bad">links hold; ${badCites} entry cites hashes no longer in the chain</span>`;
  else if (rewritten) status.innerHTML = `<span class="badge gold">links hold; ${rewritten} entries differ from the pushed ledger</span>`;
  else status.innerHTML = `<span class="badge ok">all ${E.length} entries check</span>`;

  // The order: every prediction before the run starts, every observation after.
  const at = k => C.map((c, j) => [c, j]).filter(([c]) => c.kind === k && c.time).map(([c]) => Date.parse(c.time));
  const preds = at("prediction"), start = at("run_started")[0], obs = at("observations");
  const t = ms => new Date(ms).toISOString().slice(11, 19);
  const orderOk = preds.every(p => p < start) && obs.every(o => o > start);
  $("ledger-order").innerHTML = `
    <div class="kv"><span class="k">predictions</span><span class="v">${preds.length}, the last at ${preds.length ? t(Math.max(...preds)) : "–"} UTC</span></div>
    <div class="kv"><span class="k">run started</span><span class="v">${start ? t(start) : "–"} UTC</span></div>
    <div class="kv"><span class="k">order</span><span class="v"><span class="badge ${orderOk ? "ok" : "bad"}">${orderOk ? "every prediction precedes the run" : "a prediction does not precede the run"}</span></span></div>`;
}
$("ledger-chain").addEventListener("click", e => {
  const b = e.target.closest(".entry");
  if (b) { ledger.sel = Number(b.dataset.i); renderLedger(); }
});
$("ledger-text").addEventListener("input", e => { ledger.entries[ledger.sel].text = e.target.value; renderLedger(); });
$("ledger-tamper").addEventListener("click", () => {
  ledger.sel = 1;
  const e = ledger.entries[1];
  e.text = e.text.replace(/"predicted":(\d+)/, (_, v) => `"predicted":${Number(v) * 2}`);
  renderLedger();
});
$("ledger-forge").addEventListener("click", () => {
  const E = ledger.entries;
  for (let i = 0; i < E.length; i++) {
    if (i > 0) E[i].text = E[i].text.replace(/"prev":"[0-9a-f]{64}"/, `"prev":"${E[i - 1].stored}"`);
    E[i].stored = sha256(E[i].text);
  }
  renderLedger();
});
$("ledger-restore").addEventListener("click", () => {
  ledger.entries = SITE.ledger.entries.map(e => ({ seq: e.seq, kind: e.kind, text: e.text, stored: e.hash }));
  renderLedger();
});
renderLedger();

// ---------------- the agents' timelines ----------------
const CATS = {
  setup: ["setup", "--muted"], read: ["read", "--cell-soft"], compute: ["Python", "--cell"],
  write: ["write a file", "--gold"], lean: ["compile Lean", "--ok"], wait: ["a gap between calls", "--line"],
  commit: ["commit and push", "--ink"], shell: ["other shell", "--muted"],
};
$("tl-legend").innerHTML = Object.values(CATS).filter(([n]) => n !== "other shell")
  .map(([n, c]) => `<span><i class="swatch sq" style="background: var(${c})"></i>${n}</span>`).join("");
const ms = s => Date.parse(s.replace(/(\.\d{3})\d+/, "$1"));
function drawTimelines() {
  const lanes = SITE.timelines, svg = $("tl-chart");
  const H = 60 + lanes.length * 62;
  svg.setAttribute("viewBox", `0 0 760 ${H}`);
  let maxMin = 60;
  const rows = lanes.map(l => {
    const t0 = ms(l.start), calls = l.calls.map(([t, cat, label]) => ({ min: (ms(t) - t0) / 60000, cat, label }));
    for (const c of calls) maxMin = Math.max(maxMin, Math.ceil(c.min / 10) * 10);
    return { name: l.name, pending: l.pending, calls };
  });
  const L = 86, R = 16, T = 12, B = 40, W = 760;
  const X = m => L + (m / maxMin) * (W - L - R);
  const muted = css("--muted"), line = css("--line");
  let s = "";
  for (let m = 0; m <= maxMin; m += 10) {
    s += `<line x1="${X(m)}" x2="${X(m)}" y1="${T}" y2="${H - B}" stroke="${line}" stroke-width="1"/>`;
    s += `<text x="${X(m)}" y="${H - B + 18}" text-anchor="middle" ${FONT} fill="${muted}">${m}</text>`;
  }
  s += `<text x="${(L + W - R) / 2}" y="${H - 6}" text-anchor="middle" ${FONT} fill="${muted}">minutes after launch</text>`;
  rows.forEach((row, k) => {
    const y = T + 10 + k * 62;
    s += `<text x="0" y="${y + 18}" ${FONT} fill="${css("--ink")}">${row.name.split(":")[0]}</text>`;
    if (row.pending) {
      s += `<text x="${L + 8}" y="${y + 18}" ${FONT} fill="${muted}">transcript being audited</text>`;
      return;
    }
    s += `<text x="0" y="${y + 34}" ${FONT} fill="${muted}">${row.calls.length} calls</text>`;
    row.calls.forEach((c, i) => {
      const next = i + 1 < row.calls.length ? row.calls[i + 1].min : c.min + 0.5;
      if (c.cat === "wait" || next - c.min > 3) {
        const end = next;
        s += `<rect x="${X(c.min).toFixed(1)}" y="${y + 6}" width="${Math.max(2, X(end) - X(c.min)).toFixed(1)}" height="20" style="fill: var(--line)"/>`;
      }
    });
    row.calls.forEach(c => {
      if (c.cat === "wait") return;
      s += `<rect x="${(X(c.min) - 1.5).toFixed(1)}" y="${y}" width="3" height="32" style="fill: var(${CATS[c.cat][1]})"/>`;
    });
  });
  s += `<line id="tl-cursor" x1="0" x2="0" y1="${T}" y2="${H - B}" stroke="${css("--ink")}" stroke-width="1" opacity="0"/>`;
  svg.innerHTML = s;
  const cursor = svg.querySelector("#tl-cursor"), tip = $("tl-tip");
  svg.onpointermove = ev => {
    const xv = pointerX(svg, ev, W), r = svg.getBoundingClientRect();
    const yv = ((ev.clientY - r.top) / r.height) * H;
    const k = Math.max(0, Math.min(rows.length - 1, Math.floor((yv - T) / 62)));
    const row = rows[k];
    if (!row || row.pending || !row.calls.length) return;
    const min = ((xv - L) / (W - L - R)) * maxMin;
    let best = row.calls[0];
    for (const c of row.calls) if (Math.abs(c.min - min) < Math.abs(best.min - min)) best = c;
    const j = row.calls.indexOf(best), gap = j + 1 < row.calls.length ? row.calls[j + 1].min - best.min : 0;
    cursor.setAttribute("x1", X(best.min)); cursor.setAttribute("x2", X(best.min)); cursor.setAttribute("opacity", "0.35");
    tip.textContent = `${row.name}, ${best.min.toFixed(1)} min: ${best.label}${gap > 3 ? `; the next call came ${Math.round(gap)} minutes later` : ""}`;
  };
  svg.onpointerleave = () => cursor.setAttribute("opacity", "0");
}
drawTimelines();
onRedraw(() => { drawLoop(); drawTimelines(); });

// ---------------- the fourth pilot's row ----------------
const p37 = SITE.pilot37;
if (p37) {
  if (p37.time) $("p4-time").textContent = p37.time;
  if (p37.judge) $("p4-judge").innerHTML = p37.judge;
  if (p37.test) $("p4-test").innerHTML = p37.test;
}
