// Quantum codes: the gross code's checks, and a bivariate bicycle code's logical qubits counted
// two ways, as examples/qec-bb/bb.py counts them: by ranks over GF(2), and from the torus's
// characters. Nothing here computes distance.

// MATH-BEGIN
// A polynomial on the l x m torus is a list of exponent pairs [p, q], one per monomial x^p y^q.
const bbMod = (a, n) => ((a % n) + n) % n;
const bbGcd = (a, b) => { while (b) [a, b] = [b, a % b]; return a; };

// The monomials of a GF(2) polynomial on the torus, reduced mod (l, m); repeats cancel in pairs.
function bbMonomials(poly, l, m) {
  const set = new Set();
  for (const [p, q] of poly) {
    const key = bbMod(p, l) * m + bbMod(q, m);
    if (set.has(key)) set.delete(key); else set.add(key);
  }
  return [...set].sort((a, b) => a - b).map(key => [Math.floor(key / m), key % m]);
}

// ---- k by linear algebra: k = n - rank H_X - rank H_Z, H_X = [A | B], H_Z = [B^T | A^T] ----
// Row (i, j) of A reads the cells (i - p, j - q); of A^T, the cells (i + p, j + q).
function bbChecks(A, B, l, m) {
  const lm = l * m, W = Math.ceil((2 * lm) / 32);
  const hx = new Uint32Array(lm * W), hz = new Uint32Array(lm * W);
  const set = (M, row, bit) => { M[row * W + (bit >>> 5)] ^= 1 << (bit & 31); };
  const a = bbMonomials(A, l, m), b = bbMonomials(B, l, m);
  for (let i = 0; i < l; i++) for (let j = 0; j < m; j++) {
    const row = i * m + j;
    for (const [p, q] of a) {
      set(hx, row, bbMod(i - p, l) * m + bbMod(j - q, m));
      set(hz, row, lm + bbMod(i + p, l) * m + bbMod(j + q, m));
    }
    for (const [p, q] of b) {
      set(hx, row, lm + bbMod(i - p, l) * m + bbMod(j - q, m));
      set(hz, row, bbMod(i + p, l) * m + bbMod(j + q, m));
    }
  }
  return { hx, hz, rows: lm, W };
}
// The rank over GF(2) of a matrix stored as rows of W 32-bit words; the matrix is overwritten.
function bbRank(M, rows, W) {
  let rank = 0;
  for (let w = 0; w < W && rank < rows; w++) {
    for (let b = 0; b < 32 && rank < rows; b++) {
      const bit = 1 << b;
      let piv = rank;
      while (piv < rows && !(M[piv * W + w] & bit)) piv++;
      if (piv === rows) continue;
      if (piv !== rank) {
        for (let x = w; x < W; x++) { const t = M[piv * W + x]; M[piv * W + x] = M[rank * W + x]; M[rank * W + x] = t; }
      }
      for (let r = piv + 1; r < rows; r++) {
        if (M[r * W + w] & bit) for (let x = w; x < W; x++) M[r * W + x] ^= M[rank * W + x];
      }
      rank++;
    }
  }
  return rank;
}
function bbLinalg(A, B, l, m) {
  const { hx, hz, rows, W } = bbChecks(A, B, l, m);
  const rx = bbRank(hx, rows, W), rz = bbRank(hz, rows, W);
  return { n: 2 * l * m, rankX: rx, rankZ: rz, k: 2 * l * m - rx - rz };
}

// ---- the field F(2^d), d = ord_N(2), holding a primitive N-th root of unity zeta ----
// Chosen as bb.py chooses it (the smallest irreducible polynomial of degree d, then the first
// g = 2, 3, ... whose power g^((2^d - 1)/N) has order N), so the characters carry its labels.
function polyMod(a, p) {
  const dp = p.toString(2).length;
  let da = a.toString(2).length;
  while (a && da >= dp) { a ^= p << BigInt(da - dp); da = a ? a.toString(2).length : 0; }
  return a;
}
function polyGcd(a, b) { while (b) [a, b] = [b, polyMod(a, b)]; return a; }
// Rabin's test: f of degree d is irreducible iff x^(2^d) = x mod f and, for each prime q | d,
// x^(2^(d/q)) - x is prime to f.
function isIrreducible(f, d) {
  const top = 1n << BigInt(d);
  const frob = k => { let r = 2n; for (let i = 0; i < k; i++) r = gfMul(r, r, f, top); return r; };
  if (frob(d) !== 2n) return false;
  return primeFactors(d).every(q => polyGcd(frob(d / q) ^ 2n, f) === 1n);
}
const BB_FIELDS = {};
function bbField(N) {
  if (BB_FIELDS[N]) return BB_FIELDS[N];
  const d = N === 1 ? 1 : ordm(N);
  let poly = 3n;
  if (d > 1) for (poly = (1n << BigInt(d)) | 1n; !isIrreducible(poly, d); poly += 2n);
  const top = 1n << BigInt(d), order = top - 1n;
  const mul = (a, b) => gfMul(a, b, poly, top), pow = (a, e) => gfPow(a, BigInt(e), poly, top);
  const primes = primeFactors(N);
  let zeta = 1n;
  for (let g = d > 1 ? 2n : 1n; g <= (d > 1 ? order : 1n); g++) {
    const z = pow(g, order / BigInt(N));
    if (primes.every(p => pow(z, N / p) !== 1n)) { zeta = z; break; }
  }
  const roots = [1n];
  for (let e = 1; e < N; e++) roots.push(mul(roots[e - 1], zeta));
  return (BB_FIELDS[N] = { N, d, poly, mul, pow, inv: a => pow(a, order - 1n), roots });
}
function rankField(F, rows) {
  rows = rows.map(r => r.slice());
  let rank = 0;
  const cols = rows.length ? rows[0].length : 0;
  for (let c = 0; c < cols && rank < rows.length; c++) {
    let piv = rank;
    while (piv < rows.length && !rows[piv][c]) piv++;
    if (piv === rows.length) continue;
    [rows[rank], rows[piv]] = [rows[piv], rows[rank]];
    const inv = F.inv(rows[rank][c]);
    rows[rank] = rows[rank].map(v => F.mul(inv, v));
    for (let i = rank + 1; i < rows.length; i++) {
      const f = rows[i][c];
      if (f) rows[i] = rows[i].map((v, x) => v ^ F.mul(f, rows[rank][x]));
    }
    rank++;
  }
  return rank;
}

// ---- k from the characters ----
// l = 2^a l', m = 2^b m' with l', m' odd. Each character chi = (j, k) of the l' x m' odd part sends
// x to zeta^(j N/l') and y to zeta^(k N/m'), N = lcm(l', m'), and contributes the dimension of
// L/(A_chi, B_chi), L = F[s, t]/(s^(2^a) - 1, t^(2^b) - 1). A term is nonzero only where A and B
// both vanish (at s = t = 1), and at odd sizes it is then 1. k is twice the sum.
function twoPart(n) { const t = n & -n; return [t, n / t]; }
function bbCharacters(A, B, l, m) {
  const [sa, lo] = twoPart(l), [sb, mo] = twoPart(m);
  const N = (lo * mo) / bbGcd(lo, mo), F = bbField(N), size = sa * sb;
  const ma = bbMonomials(A, l, m), mb = bbMonomials(B, l, m);
  const local = (mons, j, k) => {
    const v = new Array(size).fill(0n);
    for (const [p, q] of mons) {
      const e = (j * (N / lo) * p + k * (N / mo) * q) % N;
      v[(p % sa) * sb + (q % sb)] ^= F.roots[e];
    }
    return v;
  };
  const shifts = v => {
    const out = [];
    for (let i = 0; i < sa; i++) for (let u = 0; u < sb; u++) {
      const w = new Array(size).fill(0n);
      v.forEach((c, idx) => { if (c) w[((Math.floor(idx / sb) + i) % sa) * sb + ((idx % sb) + u) % sb] = c; });
      out.push(w);
    }
    return out;
  };
  const chars = [];
  let total = 0;
  for (let j = 0; j < lo; j++) for (let k = 0; k < mo; k++) {
    const va = local(ma, j, k), vb = local(mb, j, k);
    const aZero = va.reduce((s, c) => s ^ c, 0n) === 0n, bZero = vb.reduce((s, c) => s ^ c, 0n) === 0n;
    let term = 0;
    if (aZero && bZero) term = size === 1 ? 1 : size - rankField(F, [...shifts(va), ...shifts(vb)]);
    total += term;
    chars.push({ j, k, aZero, bZero, term });
  }
  return { lo, mo, sa, sb, N, d: F.d, chars, k: 2 * total };
}
// The Frobenius orbit of a character: (j, k), (2j, 2k), (4j, 4k), ... mod the odd part.
function bbOrbit(j, k, lo, mo) {
  const out = [];
  let a = j, b = k;
  do { out.push([a, b]); a = (2 * a) % lo; b = (2 * b) % mo; } while (a !== j || b !== k);
  return out;
}

// ---- polynomials as text: "x^3 + y + y^2", "1 + π + π^2" with π = xy, "0" ----
function parsePoly(text) {
  const s = text.toLowerCase().replace(/\s+/g, "").replace(/[−–]/g, "-").replace(/\*/g, "").replace(/pi/gi, "π");
  if (s === "0") return [];
  if (!s) throw new Error("empty");
  return s.split("+").map(t => {
    if (t === "1") return [0, 0];
    const re = /([xyπ])(?:\^(-?\d+))?/y;
    let p = 0, q = 0, at = 0;
    if (!t) throw new Error("empty term");
    while (at < t.length) {
      re.lastIndex = at;
      const f = re.exec(t);
      if (!f) throw new Error(`cannot read "${t}"`);
      const e = f[2] === undefined ? 1 : Number(f[2]);
      if (f[1] !== "y") p += e;
      if (f[1] !== "x") q += e;
      at = re.lastIndex;
    }
    return [p, q];
  });
}
// MATH-END

function polyHtml(mons) {
  if (!mons.length) return "0";
  const pw = (v, e) => (e === 0 ? "" : e === 1 ? v : `${v}<sup>${e}</sup>`);
  return mons.map(([p, q]) => (p === 0 && q === 0 ? "1" : pw("x", p) + pw("y", q))).join(" + ");
}
const fmtN = x => Number(x).toLocaleString("en-US");

// ---------------- the gross code's checks ----------------
const GROSS = { l: 12, m: 6, A: [[3, 0], [0, 1], [0, 2]], B: [[0, 3], [1, 0], [2, 0]] };
const chk = { kind: "X", i: 1, j: 1, geom: null };
const chkCanvas = $("chk-canvas");
// The qubits a check reads, on each copy, with whether it reached them across an edge.
function checkReads(kind, i, j) {
  const { l, m, A, B } = GROSS;
  const read = (poly, sign) => poly.map(([p, q]) => {
    const x = i + sign * p, y = j + sign * q;
    return { x: bbMod(x, l), y: bbMod(y, m), wrap: x < 0 || x >= l || y < 0 || y >= m };
  });
  return kind === "X" ? { left: read(A, -1), right: read(B, -1) } : { left: read(B, 1), right: read(A, 1) };
}
function drawChecks() {
  const { l, m } = GROSS, ctx = fitCanvas(chkCanvas), W = chkCanvas.width, H = chkCanvas.height;
  const dpr = window.devicePixelRatio || 1, band = 24 * dpr, gap = 16 * dpr;
  const cs = Math.min(W / l, (H - 2 * band - gap) / (2 * m)), gw = cs * l, x0 = (W - gw) / 2;
  const tops = [band, band + m * cs + gap + band];
  chk.geom = { cs, x0, tops };
  ctx.clearRect(0, 0, W, H);
  const reads = checkReads(chk.kind, chk.i, chk.j);
  const labels = chk.kind === "X"
    ? ["left copy, A = x³ + y + y²", "right copy, B = y³ + x + x²"]
    : ["left copy, Bᵀ", "right copy, Aᵀ"];
  const fills = [css("--cell"), css("--gold")], ink = css("--ink"), muted = css("--muted"), line = css("--line");
  ctx.font = `${12 * dpr}px "IBM Plex Mono", monospace`;
  ctx.textBaseline = "alphabetic";
  const g = cs > 8 * dpr ? Math.max(1, Math.round(dpr)) : 0;
  // a cell's box from rounded edges, so the gap between cells shows at any cell size
  const box = (px, py) => {
    const x = Math.round(px), y = Math.round(py);
    return [x, y, Math.round(px + cs) - x - g, Math.round(py + cs) - y - g];
  };
  [reads.left, reads.right].forEach((cells, side) => {
    const top = tops[side];
    ctx.fillStyle = muted;
    ctx.fillText(labels[side], x0, top - 8 * dpr);
    const hit = new Map(cells.map(c => [c.x * m + c.y, c]));
    for (let x = 0; x < l; x++) for (let y = 0; y < m; y++) {
      const [bx, by, bw, bh] = box(x0 + x * cs, top + (m - 1 - y) * cs), c = hit.get(x * m + y);
      ctx.fillStyle = c ? fills[side] : line;
      ctx.fillRect(bx, by, bw, bh);
      if (c && c.wrap) {
        ctx.save();
        ctx.setLineDash([3 * dpr, 2 * dpr]);
        ctx.strokeStyle = ink; ctx.lineWidth = Math.max(1, dpr);
        ctx.strokeRect(bx + 2 * dpr, by + 2 * dpr, bw - 4 * dpr, bh - 4 * dpr);
        ctx.restore();
      }
    }
    const [bx, by, bw, bh] = box(x0 + chk.i * cs, top + (m - 1 - chk.j) * cs);
    ctx.strokeStyle = ink; ctx.lineWidth = Math.max(2, 2 * dpr);
    ctx.strokeRect(bx + dpr, by + dpr, bw - 2 * dpr, bh - 2 * dpr);
  });
  const list = cells => cells.map(c => `(${c.x}, ${c.y})`).join(", ");
  $("chk-at").textContent = `${chk.kind} check at (${chk.i}, ${chk.j})`;
  $("chk-row").innerHTML = chk.kind === "X"
    ? `row (${chk.i}, ${chk.j}) of H<sub>X</sub> = [A | B]`
    : `row (${chk.i}, ${chk.j}) of H<sub>Z</sub> = [B<sup>T</sup> | A<sup>T</sup>]`;
  $("chk-left").textContent = list(reads.left);
  $("chk-right").textContent = list(reads.right);
}
function moveCheck(i, j) {
  chk.i = bbMod(i, GROSS.l); chk.j = bbMod(j, GROSS.m);
  drawChecks();
}
chkCanvas.addEventListener("click", e => {
  const G = chk.geom, rect = chkCanvas.getBoundingClientRect(), dpr = chkCanvas.width / rect.width;
  const px = (e.clientX - rect.left) * dpr, py = (e.clientY - rect.top) * dpr;
  const x = Math.floor((px - G.x0) / G.cs);
  if (x < 0 || x >= GROSS.l) return;
  for (const top of G.tops) {
    const r = Math.floor((py - top) / G.cs);
    if (r >= 0 && r < GROSS.m) { moveCheck(x, GROSS.m - 1 - r); return; }
  }
});
chkCanvas.addEventListener("keydown", e => {
  const step = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
  if (!step) return;
  e.preventDefault();
  moveCheck(chk.i + step[0], chk.j + step[1]);
});
function setCheckKind(kind) {
  chk.kind = kind;
  $("chk-x").setAttribute("aria-pressed", String(kind === "X"));
  $("chk-z").setAttribute("aria-pressed", String(kind === "Z"));
  drawChecks();
}
$("chk-x").addEventListener("click", () => setCheckKind("X"));
$("chk-z").addEventListener("click", () => setCheckKind("Z"));

// ---------------- a code's logical qubits, two ways ----------------
// The twelve published entries, transcribed in examples/qec-bb/codes.json (π = xy).
const PUBLISHED = [
  { name: "[[72,12,6]]", source: "Bravyi et al. 2024", l: 6, m: 6, A: "x^3 + y + y^2", B: "y^3 + x + x^2", k: 12, d: 6 },
  { name: "[[90,8,10]]", source: "Bravyi et al. 2024", l: 15, m: 3, A: "x^9 + y + y^2", B: "1 + x^2 + x^7", k: 8, d: 10 },
  { name: "[[108,8,10]]", source: "Bravyi et al. 2024", l: 9, m: 6, A: "x^3 + y + y^2", B: "y^3 + x + x^2", k: 8, d: 10 },
  { name: "[[144,12,12]], the gross code", source: "Bravyi et al. 2024", l: 12, m: 6, A: "x^3 + y + y^2", B: "y^3 + x + x^2", k: 12, d: 12 },
  { name: "[[288,12,18]]", source: "Bravyi et al. 2024", l: 12, m: 12, A: "x^3 + y^2 + y^7", B: "y^3 + x + x^2", k: 12, d: 18 },
  { name: "[[30,4,6]]", source: "Wang and Mueller (v4)", l: 3, m: 5, A: "1 + π + π^2", B: "π + π^3 + π^8", k: 4, d: 6 },
  { name: "[[42,6,6]]", source: "Wang and Mueller (v4)", l: 3, m: 7, A: "1 + π^2 + π^3", B: "π + π^3 + π^11", k: 6, d: 6 },
  { name: "[[70,6,8]]", source: "Wang and Mueller (v4)", l: 5, m: 7, A: "1 + π + π^5", B: "1 + π + π^12", k: 6, d: 8 },
  { name: "[[108,12,6]], poster version", source: "Wang and Mueller, QCE 2024 poster", l: 2, m: 27, A: "π^2 + π^5 + π^44", B: "π^8 + π^14 + π^47", k: 12, d: 6 },
  { name: "[[108,12,6]], Quantum version", source: "Wang and Mueller, Quantum (2026)", l: 2, m: 27, A: "1 + π^3 + π^42", B: "1 + π^6 + π^39", k: 12, d: 6 },
  { name: "[[126,12,10]], poster version", source: "Wang and Mueller, QCE 2024 poster", l: 7, m: 9, A: "1 + π + π^58", B: "π^3 + π^16 + π^44", k: 12, d: 10 },
  { name: "[[126,12,10]], Quantum version", source: "Wang and Mueller, Quantum (2026)", l: 7, m: 9, A: "1 + π + π^58", B: "1 + π^13 + π^41", k: 12, d: 10 },
];
const MAX_SIDE = 32, MAX_CELLS = 256;
const code = { res: null, hover: -1 };
let randomRun = 0;
const codePick = $("code-pick"), codeCanvas = $("code-canvas");
const inputs = { l: $("code-l"), m: $("code-m"), A: $("code-a"), B: $("code-b") };
PUBLISHED.forEach((c, i) => codePick.add(new Option(c.name, String(i))));
codePick.add(new Option("your own code", "own"));

function readCode() {
  const l = Math.floor(Number(inputs.l.value)), m = Math.floor(Number(inputs.m.value));
  if (!(l >= 1 && l <= MAX_SIDE && m >= 1 && m <= MAX_SIDE)) throw new Error(`l and m must be whole numbers from 1 to ${MAX_SIDE}`);
  if (l * m > MAX_CELLS) throw new Error(`this page computes tori of up to ${MAX_CELLS} cells; ${l} × ${m} has ${l * m}`);
  let A, B;
  try { A = parsePoly(inputs.A.value); } catch (err) { throw new Error(`cannot read A: ${err.message}`); }
  try { B = parsePoly(inputs.B.value); } catch (err) { throw new Error(`cannot read B: ${err.message}`); }
  return { l, m, A, B };
}
function computeCode() {
  randomRun++;
  $("code-random-out").textContent = "";
  let c;
  try { c = readCode(); } catch (err) {
    code.res = null;
    $("code-error").innerHTML = `<span class="badge bad">${err.message}</span>`;
    drawChars();
    return;
  }
  $("code-error").textContent = "";
  const t0 = performance.now();
  const lin = bbLinalg(c.A, c.B, c.l, c.m), ch = bbCharacters(c.A, c.B, c.l, c.m);
  const ms = Math.round(performance.now() - t0);
  code.res = { ...c, lin, ch };
  const pub = codePick.value === "own" ? null : PUBLISHED[Number(codePick.value)];
  const terms = ch.chars.filter(x => x.term > 0);
  $("code-code").textContent = `[[${lin.n}, ${lin.k}, ${pub ? pub.d : "?"}]]`;
  $("code-mons").innerHTML = `A = ${polyHtml(bbMonomials(c.A, c.l, c.m))}; B = ${polyHtml(bbMonomials(c.B, c.l, c.m))}`;
  $("code-n").textContent = `2 · ${c.l} · ${c.m} = ${fmtN(lin.n)}`;
  $("code-lin").textContent = `${lin.k} = ${lin.n} − ${lin.rankX} − ${lin.rankZ}`;
  $("code-chars").textContent = `${ch.k} = 2 × ${terms.length ? "(" + terms.map(x => x.term).join(" + ") + ")" : "0"}`;
  $("code-agree").innerHTML = lin.k === ch.k
    ? `<span class="badge ok">the two methods agree</span> <span class="note">(${ms} ms)</span>`
    : `<span class="badge bad">the two methods differ</span>`;
  $("code-pub").innerHTML = pub
    ? `k = ${pub.k}, d = ${pub.d} (${pub.source}) <span class="badge ${pub.k === ch.k ? "ok" : "bad"}">${pub.k === ch.k ? "k reproduced" : "k differs"}</span>`
    : `<span class="note">none: the distance d of this code is not computed here</span>`;
  $("code-parts").textContent = ch.sa * ch.sb === 1
    ? `${ch.lo} × ${ch.mo}, the whole torus; F(2^${ch.d})`
    : `${ch.lo} × ${ch.mo}, with a ${ch.sa} × ${ch.sb} 2-part; F(2^${ch.d})`;
  $("code-hover").textContent = "point at a square";
  drawChars();
}
function charGeom() {
  const ch = code.res.ch, W = codeCanvas.width, H = codeCanvas.height;
  const cs = Math.min(W / ch.mo, H / ch.lo, W / 4);
  return { cs, x0: (W - cs * ch.mo) / 2, y0: (H - cs * ch.lo) / 2 };
}
function drawChars() {
  const ctx = fitCanvas(codeCanvas), W = codeCanvas.width, H = codeCanvas.height;
  ctx.clearRect(0, 0, W, H);
  if (!code.res) return;
  const ch = code.res.ch, { cs, x0, y0 } = charGeom(), dpr = window.devicePixelRatio || 1;
  const col = { both: css("--gold"), a: css("--cell-soft"), b: css("--gold-soft"), none: css("--line") };
  const ink = css("--ink"), onGold = css("--panel"), g = cs > 7 ? Math.max(1, Math.round(dpr)) : 0;
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.font = `600 ${Math.max(9, Math.min(15 * dpr, cs * 0.5))}px "IBM Plex Mono", monospace`;
  ch.chars.forEach((c, idx) => {
    const px = Math.round(x0 + c.k * cs), py = Math.round(y0 + c.j * cs);
    const w = Math.round(x0 + (c.k + 1) * cs) - px - g, h = Math.round(y0 + (c.j + 1) * cs) - py - g;
    ctx.fillStyle = c.aZero && c.bZero ? col.both : c.aZero ? col.a : c.bZero ? col.b : col.none;
    ctx.fillRect(px, py, w, h);
    if (c.term && cs > 9 * dpr) { ctx.fillStyle = onGold; ctx.fillText(String(c.term), px + w / 2, py + h / 2 + dpr); }
    if (idx === code.hover && cs > 3) {
      ctx.strokeStyle = ink; ctx.lineWidth = Math.max(1, cs / 10);
      ctx.strokeRect(px + 1, py + 1, w - 2, h - 2);
    }
  });
}
codeCanvas.addEventListener("pointermove", e => {
  if (!code.res) return;
  const ch = code.res.ch, rect = codeCanvas.getBoundingClientRect(), dpr = codeCanvas.width / rect.width;
  const { cs, x0, y0 } = charGeom();
  const k = Math.floor(((e.clientX - rect.left) * dpr - x0) / cs), j = Math.floor(((e.clientY - rect.top) * dpr - y0) / cs);
  if (j < 0 || k < 0 || j >= ch.lo || k >= ch.mo) return;
  const idx = j * ch.mo + k, c = ch.chars[idx], orbit = bbOrbit(j, k, ch.lo, ch.mo).length;
  const what = c.aZero && c.bZero
    ? `A and B both vanish; counts ${c.term}`
    : c.aZero ? "A vanishes, B does not" : c.bZero ? "B vanishes, A does not" : "neither vanishes";
  $("code-hover").textContent = `χ = (${j}, ${k}): ${what}; Frobenius orbit of ${orbit}`;
  code.hover = idx;
  drawChars();
});
codeCanvas.addEventListener("pointerleave", () => { code.hover = -1; drawChars(); });

function showPublished(i) {
  const c = PUBLISHED[i];
  codePick.value = String(i);
  inputs.l.value = c.l; inputs.m.value = c.m; inputs.A.value = c.A; inputs.B.value = c.B;
  computeCode();
}
codePick.addEventListener("change", e => { if (e.target.value !== "own") showPublished(Number(e.target.value)); });
for (const el of Object.values(inputs)) {
  el.addEventListener("input", () => { codePick.value = "own"; computeCode(); });
}
for (const el of [inputs.A, inputs.B]) el.addEventListener("keydown", e => { if (e.key === "Enter") e.preventDefault(); });

// Random codes at the current size, of the registered test's two kinds: 100 in the published
// trinomial form, A = x^a + y^b + y^c and B = y^d + x^e + x^f, and 50 with two to six random terms.
function randomCodes(l, m) {
  const r = n => Math.floor(Math.random() * n);
  const three = n => {
    if (n < 3) return [r(n), r(n), r(n)];
    const s = new Set();
    while (s.size < 3) s.add(r(n));
    return [...s];
  };
  const out = [];
  for (let t = 0; t < 100; t++) {
    const [a, e, f] = three(l), [d, b, c] = three(m);
    out.push([[[a, 0], [0, b], [0, c]], [[0, d], [e, 0], [f, 0]]]);
  }
  for (let t = 0; t < 50; t++) {
    const poly = () => Array.from({ length: 2 + r(5) }, () => [r(l), r(m)]);
    out.push([poly(), poly()]);
  }
  return out;
}
$("code-random").addEventListener("click", () => {
  if (!code.res) return;
  const { l, m } = code.res, codes = randomCodes(l, m), out = $("code-random-out"), run = ++randomRun;
  let i = 0, agree = 0, positive = 0;
  const t0 = performance.now();
  const chunk = () => {
    if (run !== randomRun) return;
    const stop = performance.now() + 30;
    while (i < codes.length && performance.now() < stop) {
      const [A, B] = codes[i++];
      const kl = bbLinalg(A, B, l, m).k, kc = bbCharacters(A, B, l, m).k;
      agree += kl === kc;
      positive += kl > 0;
    }
    if (i < codes.length) { out.textContent = `${i} of ${codes.length} codes…`; setTimeout(chunk, 0); return; }
    const ok = agree === codes.length;
    out.innerHTML = `<span class="badge ${ok ? "ok" : "bad"}">${agree} of ${codes.length} agree</span> k by ranks and by characters, for random codes on the ${l} × ${m} torus; ${positive} of them have k &gt; 0 (${fmtN(Math.round(performance.now() - t0))} ms)`;
  };
  out.textContent = "computing…";
  setTimeout(chunk, 0);
});

drawChecks();
showPublished(3);
onRedraw(() => { drawChecks(); drawChars(); });
