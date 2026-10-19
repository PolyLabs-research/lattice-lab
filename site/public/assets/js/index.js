// Home: the parity rule from one cell, with its exact period against the registered law.
const heroCanvas = $("hero-canvas");
const hero = makeSim({
  canvas: heroCanvas,
  terms: window.SITE.rules.xor.terms,
  n: 31,
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

// The m = 37 card follows the fourth pilot's state.
const p37 = window.SITE.pilot37;
if (p37 && p37.status) {
  $("m37-status").textContent = p37.status;
  if (p37.card) $("m37-text").textContent = p37.card;
}
