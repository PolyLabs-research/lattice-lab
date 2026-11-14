// Home: one check running, and the record's cells.

// ---- the parity rule from one cell, with its exact period against the registered law ----
// B1357/S1357: a cell's next state is the parity of its eight neighbours (lattice-lab's rule "xor").
const TERMS = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];
const heroCanvas = $("hero-canvas");
const hero = makeSim({
  canvas: heroCanvas,
  terms: TERMS,
  n: 31,
  onStep(gen) { $("hero-gen").textContent = gen.toLocaleString("en-US"); },
  onPeriod(res, ms) {
    const out = $("hero-period"), law = $("hero-law");
    if (!res) { out.textContent = "…"; law.textContent = ""; return; }
    out.textContent = res.dies ? "dies" : res.period.toLocaleString("en-US");
    const L = xorLaw(hero.n), agree = L.dies === res.dies && L.period === res.period;
    const formula = L.dies
      ? `n = 2<sup>${L.v}</sup>, so the torus dies`
      : `2<sup>${L.v}</sup> · (2<sup>${L.s}</sup> − 1) = ${L.period.toLocaleString("en-US")}`;
    law.innerHTML = `${formula} <span class="badge ${agree ? "ok" : "bad"}">${agree ? "agrees" : "differs"}</span> <span class="note">${ms} ms</span>`;
  },
});
function heroStart() { hero.reset(); for (let i = 0; i < Math.floor(hero.n / 2) - 1; i++) hero.step(); }
heroStart();
$("hero-n").addEventListener("input", e => {
  hero.n = Number(e.target.value);
  $("hero-n-out").textContent = hero.n;
  heroStart();
});
onRedraw(() => hero.draw());
if (!reducedMotion()) hero.play(true);
heroCanvas.addEventListener("click", () => hero.play(!hero.playing));

// ---- the record: a cell shows the result it stands for, in a note beside it ----
const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const tip = document.createElement("div");
tip.className = "cell-tip";
tip.hidden = true;
tip.setAttribute("role", "status");
document.body.append(tip);
let shown = null;
function show(cell, touch) {
  if (shown) shown.classList.remove("on");
  shown = cell;
  tip.hidden = !cell;
  if (!cell) return;
  cell.classList.add("on");
  const d = cell.dataset;
  tip.classList.toggle("touch", touch);
  tip.innerHTML = `<span><span class="badge ${d.kind}">${esc(d.label)}</span></span><b>${esc(d.claim)}</b>` +
    (d.outcome ? `<span>${esc(d.outcome)}</span>` : "") +
    (touch ? `<a href="${cell.getAttribute("href")}">See it on its page →</a>` : "");
  // above the cell where there is room, otherwise below it, and kept inside the page
  const r = cell.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
  const left = Math.max(12, Math.min(r.left + r.width / 2 - w / 2, document.documentElement.clientWidth - w - 12));
  const top = r.top > h + 16 ? r.top - h - 10 : r.bottom + 10;
  tip.style.left = `${left + scrollX}px`;
  tip.style.top = `${top + scrollY}px`;
}
for (const cell of document.querySelectorAll(".strip .c")) {
  cell.setAttribute("aria-label", `${cell.dataset.label}: ${cell.dataset.claim}`);
  cell.addEventListener("pointerenter", ev => { if (ev.pointerType === "mouse") show(cell, false); });
  cell.addEventListener("pointerleave", ev => { if (ev.pointerType === "mouse") show(null); });
  // a tap shows the result first, with a link to its row; a click with a mouse goes straight there
  cell.addEventListener("click", ev => {
    if (ev.pointerType === "mouse" || shown === cell && tip.classList.contains("touch")) return;
    ev.preventDefault();
    show(cell, true);
  });
}
document.addEventListener("click", ev => { if (shown && !ev.target.closest(".strip .c, .cell-tip")) show(null); });
