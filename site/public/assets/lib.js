// PolyLabs Research: shared code for every page. The mathematics is computed in the browser from
// the rules' polynomials in data.js, which site/build_data.py writes from lattice-lab's records.
"use strict";

// MATH-BEGIN
// ---- finite fields F(2^d), elements as BigInt polynomials over GF(2) in the generator z ----
function gfMul(a, b, mod, top) {
  let r = 0n;
  while (b) {
    if (b & 1n) r ^= a;
    b >>= 1n;
    a <<= 1n;
    if (a & top) a ^= mod;
  }
  return r;
}
function gfPow(a, e, mod, top) {
  let r = 1n;
  while (e > 0n) {
    if (e & 1n) r = gfMul(r, a, mod, top);
    a = gfMul(a, a, mod, top);
    e >>= 1n;
  }
  return r;
}
function primeFactors(n) {
  const out = [];
  let p = 2;
  while (p * p <= n) {
    if (n % p === 0) { out.push(p); while (n % p === 0) n /= p; }
    p += p === 2 ? 1 : 2;
  }
  if (n > 1) out.push(n);
  return out;
}
function ordm(m) { let j = 1, x = 2 % m; while (x !== 1) { x = (x * 2) % m; j++; } return j; }
function sord(m) { let j = 1, x = 2 % m; while (x !== 1 && x !== m - 1) { x = (x * 2) % m; j++; } return j; }
function gcdB(a, b) { while (b) { [a, b] = [b, a % b]; } return a; }
const FIELDS = {};
function field(m) {
  if (FIELDS[m]) return FIELDS[m];
  const [hex, d] = window.SITE.fields[m];
  const mod = BigInt(hex), top = 1n << BigInt(d), N = 2 ** d - 1;
  const zp = [];
  let z = 1n;
  for (let e = 0; e < m; e++) { zp.push(z); z = gfMul(z, 2n, mod, top); }
  return (FIELDS[m] = { m, d, mod, top, N, primes: primeFactors(N), zp });
}
function orderOf(F, a) {
  let n = BigInt(F.N);
  for (const p of F.primes) {
    const P = BigInt(p);
    while (n % P === 0n && gfPow(a, n / P, F.mod, F.top) === 1n) n /= P;
  }
  return n;
}
function orbitsOf(m) {
  const id = new Int32Array(m * m).fill(-1), reps = [];
  for (let j = 0; j < m; j++) for (let k = 0; k < m; k++) {
    if (id[j * m + k] >= 0) continue;
    const o = reps.length;
    let a = j, b = k, size = 0;
    while (id[a * m + b] < 0) { id[a * m + b] = o; a = (2 * a) % m; b = (2 * b) % m; size++; }
    reps.push({ j, k, size });
  }
  return { id, reps };
}
// Every eigenvalue of f at odd m, one per Frobenius orbit, with its order and whether it is a cube
// in F(2^sord(m)). The odd part is the lcm of the orders.
function eigenMap(terms, m) {
  const F = field(m), { id, reps } = orbitsOf(m), s = sord(m);
  const full = (1n << BigInt(s)) - 1n;
  const cubeExp = full % 3n === 0n ? full / 3n : null;
  const classes = new Set();
  const info = reps.map(r => {
    let v = 0n;
    for (const [x, y] of terms) v ^= F.zp[(((x * r.j + y * r.k) % m) + m) % m];
    if (v === 0n) return { zero: true, size: r.size, j: r.j, k: r.k };
    let c = v, w = v;
    for (let i = 1; i < F.d; i++) { w = gfMul(w, w, F.mod, F.top); if (w < c) c = w; }
    classes.add(c.toString());
    const ord = orderOf(F, v);
    return { zero: false, ord, cube: cubeExp === null ? null : cubeExp % ord === 0n, size: r.size, j: r.j, k: r.k };
  });
  let lcm = 1n;
  for (const i of info) if (!i.zero) lcm = (lcm / gcdB(lcm, i.ord)) * i.ord;
  return { m, d: F.d, s, full, lcm, id, info, cubeExp, classes: classes.size };
}

// ---- the group ring F2[(Z/n)^2] for n <= 32: an element is n rows of n bits ----
function ring(n) {
  const mask = n === 32 ? 0xffffffff : 2 ** n - 1;
  const rotl = (w, s) => (s === 0 ? w : (((w << s) | (w >>> (n - s))) & mask) >>> 0);
  const zero = () => new Uint32Array(n);
  const fromTerms = terms => {
    const e = zero();
    for (const [x, y] of terms) {
      const r = ((y % n) + n) % n, c = ((x % n) + n) % n;
      e[r] ^= 1 << c;
    }
    for (let r = 0; r < n; r++) e[r] >>>= 0;
    return e;
  };
  const bits = w => { const out = []; for (let c = 0; c < n; c++) if ((w >>> c) & 1) out.push(c); return out; };
  const mul = (A, B) => {
    const C = zero();
    for (let r1 = 0; r1 < n; r1++) {
      if (!A[r1]) continue;
      const cs = bits(A[r1]);
      for (let r2 = 0; r2 < n; r2++) {
        const b = B[r2];
        if (!b) continue;
        let acc = 0;
        for (const c of cs) acc ^= rotl(b, c);
        C[(r1 + r2) % n] ^= acc;
      }
    }
    for (let r = 0; r < n; r++) C[r] >>>= 0;
    return C;
  };
  const one = () => { const e = zero(); e[0] = 1; return e; };
  const pow = (A, e) => {
    let r = one(), b = A;
    while (e > 0) { if (e % 2 === 1) r = mul(r, b); e = Math.floor(e / 2); if (e > 0) b = mul(b, b); }
    return r;
  };
  const eq = (A, B) => { for (let r = 0; r < n; r++) if (A[r] !== B[r]) return false; return true; };
  const isZero = A => A.every(w => w === 0);
  return { n, zero, one, fromTerms, mul, pow, eq, isZero };
}
// The exact eventual period of a rule on the n-torus, from a bound it must repeat at.
function exactPeriod(terms, n) {
  const R = ring(n), f = R.fromTerms(terms);
  const late = R.pow(f, 4 * n);
  if (R.isZero(late)) return { dies: true, period: 1 };
  let v = 0, m = n;
  while (m % 2 === 0) { m /= 2; v++; }
  const o = m > 1 ? ordm(m) : 1;
  const C = 2 ** (v + 2) * (2 ** o - 1);
  const primes = [...new Set([2, ...primeFactors(2 ** o - 1)])];
  const repeats = p => R.eq(R.mul(late, R.pow(f, p)), late);
  if (!repeats(C)) throw new Error("the bound fails");
  let p = C;
  for (const q of primes) while (p % q === 0 && repeats(p / q)) p /= q;
  return { dies: false, period: p };
}
function xorLaw(n) {
  let v = 0, m = n;
  while (m % 2 === 0) { m /= 2; v++; }
  if (m === 1) return { dies: true, v, m, s: 0, period: 1 };
  const s = sord(m);
  return { dies: false, v, m, s, period: 2 ** v * (2 ** s - 1) };
}
// ---- Laurent polynomials over GF(2) as sets of exponent pairs ----
function lmul(A, B) {
  const count = new Map();
  for (const [a, b] of A) for (const [c, d] of B) {
    const key = (a + c) + "," + (b + d);
    count.set(key, (count.get(key) || 0) ^ 1);
  }
  return [...count].filter(([, v]) => v).map(([k]) => k.split(",").map(Number));
}
function lpow(A, k) { let r = [[0, 0]]; for (let i = 0; i < k; i++) r = lmul(r, A); return r; }
function ldil(A, k) { return A.map(([x, y]) => [k * x, k * y]); }
function lsame(A, B) {
  const key = S => S.map(t => t.join(",")).sort().join(";");
  return key(A) === key(B);
}
// MATH-END


// ---- SHA-256 of a string's UTF-8 bytes, for checking the ledger's hash chain ----
const SHA_K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);
function sha256(text) {
  const bytes = new TextEncoder().encode(text), l = bytes.length;
  const size = Math.ceil((l + 9) / 64) * 64, buf = new Uint8Array(size);
  buf.set(bytes);
  buf[l] = 0x80;
  const dv = new DataView(buf.buffer);
  dv.setUint32(size - 8, Math.floor((l * 8) / 2 ** 32));
  dv.setUint32(size - 4, (l * 8) >>> 0);
  const H = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
  const W = new Uint32Array(64), ror = (x, n) => (x >>> n) | (x << (32 - n));
  for (let off = 0; off < size; off += 64) {
    for (let i = 0; i < 16; i++) W[i] = dv.getUint32(off + 4 * i);
    for (let i = 16; i < 64; i++) {
      const a = W[i - 15], b = W[i - 2];
      W[i] = W[i - 16] + (ror(a, 7) ^ ror(a, 18) ^ (a >>> 3)) + W[i - 7] + (ror(b, 17) ^ ror(b, 19) ^ (b >>> 10));
    }
    let [a, b, c, d, e, f, g, h] = H;
    for (let i = 0; i < 64; i++) {
      const t1 = (h + (ror(e, 6) ^ ror(e, 11) ^ ror(e, 25)) + ((e & f) ^ (~e & g)) + SHA_K[i] + W[i]) | 0;
      const t2 = ((ror(a, 2) ^ ror(a, 13) ^ ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0;
      h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
    }
    H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
  }
  return [...H].map(x => x.toString(16).padStart(8, "0")).join("");
}

// ---- page helpers ----
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const fmt = x => BigInt(x).toLocaleString("en-US");
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const $ = id => document.getElementById(id);
function fitCanvas(canvas) {
  const rect = canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(rect.width * dpr));
  canvas.height = Math.max(1, Math.round(rect.height * dpr));
  return canvas.getContext("2d");
}
function log2Big(s) {
  const b = BigInt(s), len = b.toString(2).length, shift = Math.max(0, len - 53);
  return Math.log2(Number(b >> BigInt(shift))) + shift;
}
// Call redraw whenever the colours or the size may have changed.
function onRedraw(redraw) {
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", redraw);
  new MutationObserver(redraw).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  let timer;
  window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(redraw, 120); });
}

// ---- SVG charts: a frame with axes, and scales from data to the frame ----
const FONT = 'font-family="IBM Plex Mono, monospace" font-size="11"';
function frame({ W = 760, H = 330, L = 58, R = 16, T = 14, B = 42, x, y }) {
  const sx = v => L + ((x.log ? Math.log(v) - Math.log(x.min) : v - x.min) / (x.log ? Math.log(x.max) - Math.log(x.min) : x.max - x.min)) * (W - L - R);
  const sy = v => H - B - ((y.log ? Math.log(v) - Math.log(y.min) : v - y.min) / (y.log ? Math.log(y.max) - Math.log(y.min) : y.max - y.min)) * (H - T - B);
  const muted = css("--muted"), line = css("--line");
  let s = "";
  for (const t of y.ticks) {
    s += `<line x1="${L}" x2="${W - R}" y1="${sy(t).toFixed(1)}" y2="${sy(t).toFixed(1)}" stroke="${line}" stroke-width="1"/>`;
    s += `<text x="${L - 8}" y="${(sy(t) + 4).toFixed(1)}" text-anchor="end" ${FONT} fill="${muted}">${(y.fmt || String)(t)}</text>`;
  }
  for (const t of x.ticks) {
    s += `<text x="${sx(t).toFixed(1)}" y="${H - B + 18}" text-anchor="middle" ${FONT} fill="${muted}">${(x.fmt || String)(t)}</text>`;
  }
  if (x.label) s += `<text x="${(L + W - R) / 2}" y="${H - 6}" text-anchor="middle" ${FONT} fill="${muted}">${x.label}</text>`;
  if (y.label) s += `<text x="14" y="${(T + H - B) / 2}" text-anchor="middle" ${FONT} fill="${muted}" transform="rotate(-90 14 ${(T + H - B) / 2})">${y.label}</text>`;
  return { W, H, L, R, T, B, sx, sy, markup: s };
}
// The x position in chart units under a pointer event.
function pointerX(svg, ev, W) {
  const r = svg.getBoundingClientRect();
  return ((ev.clientX - r.left) / r.width) * W;
}

// ---- the live torus: one cell, run under a rule, with its exact period ----
function makeSim({ canvas, terms, n, onStep, onPeriod }) {
  const sim = { n, terms, R: null, f: null, state: null, gen: 0, playing: false, last: 0, timer: 0 };
  sim.reset = () => {
    sim.R = ring(sim.n);
    sim.f = sim.R.fromTerms(sim.terms);
    sim.state = sim.R.one();
    sim.gen = 0;
    sim.draw();
    if (onPeriod) {
      clearTimeout(sim.timer);
      onPeriod(null);
      sim.timer = setTimeout(() => {
        const t0 = performance.now(), res = exactPeriod(sim.terms, sim.n);
        onPeriod(res, Math.round(performance.now() - t0));
      }, 10);
    }
  };
  sim.step = () => { sim.state = sim.R.mul(sim.f, sim.state); sim.gen++; sim.draw(); };
  sim.draw = () => {
    const ctx = fitCanvas(canvas), N = sim.n, W = canvas.width, cs = W / N;
    ctx.fillStyle = css("--paper"); ctx.fillRect(0, 0, W, canvas.height);
    ctx.fillStyle = css("--cell");
    const off = Math.floor(N / 2), gap = cs > 6 ? 1 : 0;
    let live = 0;
    for (let r = 0; r < N; r++) {
      const w = sim.state[r];
      if (!w) continue;
      for (let c = 0; c < N; c++) if ((w >>> c) & 1) {
        live++;
        const x = (c + off) % N, y = (r + off) % N;
        ctx.fillRect(Math.floor(x * cs), Math.floor(y * cs), Math.ceil(cs) - gap, Math.ceil(cs) - gap);
      }
    }
    if (onStep) onStep(sim.gen, live);
  };
  const tick = t => {
    if (!sim.playing) return;
    if (t - sim.last > 75) { sim.step(); sim.last = t; }
    requestAnimationFrame(tick);
  };
  sim.play = on => { sim.playing = on; if (on) requestAnimationFrame(tick); };
  return sim;
}

// Mark the current page in the navigation.
document.addEventListener("DOMContentLoaded", () => {
  const here = (location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "") || "index";
  for (const a of document.querySelectorAll(".nav a")) {
    const to = a.getAttribute("href").replace(/\.html$/, "").replace(/^\.\//, "") || "index";
    if (to === here) a.setAttribute("aria-current", "page");
  }
});
