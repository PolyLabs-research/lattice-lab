"""
Twisted pairs and cube certificates: two structural reasons for the eigenvalues of a rule f on
the m-torus to be q-th powers.  See proposal.md for the statements and proofs.

    condition(f, m) -> q        every nonzero eigenvalue of f at m is a q-th power in F(2^d)*,
                                d = ord_m(2); 1 if no claim

Notation.  lambda_g(c) = g(zeta^c) is the eigenvalue of a Laurent polynomial g at the character c,
zeta a primitive m-th root of unity in F(2^d).  g^(a) = g(x^a, y^a), so lambda_{g^(a)}(c) =
lambda_g(a c), and lambda_g(2^k c) = lambda_g(c)^(2^k) (Frobenius).  t_w = x^w + x^-w is rule 90
along w; lambda_{t_w}(c) = t_{w.c} with t_j = zeta^j + zeta^-j.

Mechanism A (twisted pair).  f = C^(a) C^(b) exactly, with b = eps 2^k a (mod m), eps = +-1
(eps = -1 only if C is symmetric).  Then lambda_f(c) = mu^(1 + 2^k), mu = lambda_C(a c), so every
eigenvalue is a gcd(1 + 2^k, 2^d - 1)-th power.

Mechanism B (cube certificate; mechanism 5 with a q-th-power multiplier).  For a divisor g of d,
n = 2^g mod m, a polynomial M that is a product of rule-90 orbit products O_v and Psi-products
P_{e,v} (gcd(e, m) = 1), and an exponent E divisible by q, where q divides (2^d - 1)/(2^g - 1):

    B := f * M^E   (mod x^m - 1, y^m - 1)   is invariant under (x, y) -> (x^n, y^n).

Then lambda_f(c) = lambda_B(c) / lambda_M(c)^E with lambda_B(c) in F(2^g), a q-th power, wherever
lambda_M(c) != 0.  lambda_M vanishes only on the lines {c : w.c = 0 mod m}, w in the orbits of the
O_v; on each such line f restricts to a one-variable rule H(t_k), and the line criterion (below)
must show that its values are q-th powers.

Line criterion.  If H = t^i prod_e Psi_e^(k_e) with every divisor e' > 1 of every e congruent to
+-2^a(e') mod m, then H(t_j)^2 = t_j^A with A = 2i + sum_e k_e sum_{e'|e} mu(e/e') 2^a(e')
(a(1) = 0), for every j != 0; and H(t_0) is 0 or 1.  If q | A, every nonzero value is a q-th power.

The previous pilot's mechanism 5 (tools/halffrob.py) is also consulted.  condition returns the lcm
of the q's proved, together with (2^d - 1)/(2^s - 1) when f is symmetric (eigenvalues in F(2^s)),
but only if the result says more than that factor alone; otherwise 1.
"""

from __future__ import annotations

import functools
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

import halffrob  # noqa: E402
from halffrob import (  # noqa: E402
    _cldivmod,
    _half_orbit,
    _orbit_reps,
    _psi,
    _sym_to_t,
    ord2,
    pdiv,
    pmul,
    pscale,
    sord,
    symmetries,
    tfac,
)

M_RADIUS = 2  # O_v and P_{3,v} with v primitive, max(|v_1|, |v_2|) <= M_RADIUS
M_PSI = (3, 5)  # Psi_e used in P_{e,v}
MAX_ATOMS = 1  # M is a single atom (or 1)
MAX_K = 3  # exponents E = q k, k <= MAX_K
LINE_PSI = 61  # Psi_e with e < LINE_PSI tried on the lines
Q_BOUND = 200  # prime powers q < Q_BOUND tried in mechanism B
C_RADIUS = 1  # twisted pairs: C symmetric with support in [-C_RADIUS, C_RADIUS]^2 ...
C_ORBIT_RADIUS = 2  # ... or a union of symmetry orbits within this radius


# ---------------------------------------------------------------- number theory

@functools.cache
def _pow2_log(m: int) -> dict[int, int]:
    """{r: a} with r = +-2^a mod m, the least such a."""
    out, x = {}, 1 % m
    for a in range(ord2(m)):
        out.setdefault(x, a)
        out.setdefault((-x) % m, a)
        x = 2 * x % m
    return out


def _prime_powers_dividing(N: int, bound: int) -> list[int]:
    out = []
    p = 3
    while p < bound:
        if N % p == 0 and all(p % r for r in range(3, int(p**0.5) + 1, 2)):
            pk = p
            while N % pk == 0 and pk < bound:
                out.append(pk)
                pk *= p
        p += 2
    return out


def _mobius(n: int) -> int:
    out, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            out = -out
        p += 1
    return -out if n > 1 else out


# ---------------------------------------------------------------- the line criterion

def line_exponent(H: int, m: int):
    """For H(t) over GF(2) (int bitmask), nonzero: the integer A with H(t_j)^2 = t_j^A for every
    j != 0 mod m, if H = t^i prod Psi_e^(k_e) with all divisors e' > 1 of each e of the form
    +-2^a mod m; otherwise None."""
    logs = _pow2_log(m)
    A = 0
    while H & 1 == 0:
        H >>= 1
        A += 2
    for e in range(3, LINE_PSI, 2):
        if H == 1:
            break
        divs = [e2 for e2 in range(1, e + 1) if e % e2 == 0]
        if any(e2 % m not in logs or math.gcd(e2, m) != 1 for e2 in divs[1:]):
            continue
        weight = sum(_mobius(e // e2) * 2 ** (logs[e2 % m] if e2 > 1 else 0) for e2 in divs)
        while True:
            Q, rem = _cldivmod(H, _psi(e))
            if rem:
                break
            H, A = Q, A + weight
    return A if H == 1 else None


def line_ok(f, w, m, q) -> bool:
    """On the line {c : w.c = 0 mod m} (w primitive), whether every nonzero eigenvalue of f is a
    q-th power, by the line criterion."""
    c0 = (w[1], -w[0])
    H = _sym_to_t([p * c0[0] + r * c0[1] for p, r in f])
    if H is None:
        return False
    if H == 0:
        return True
    A = line_exponent(H, m)
    return A is not None and A % q == 0


# ---------------------------------------------------------------- dense polynomials mod m

def _dense(P, m):
    D = np.zeros((m, m), dtype=np.uint8)
    for p, r in P:
        D[p % m, r % m] ^= 1
    return D


def _invariant(D, n, m) -> bool:
    idx = (np.arange(m) * n) % m
    return np.array_equal(D[np.ix_(idx, idx)], D)


# ---------------------------------------------------------------- mechanism B

@functools.cache
def _atoms(group, m):
    """Atoms of M: (name, polynomial, rule-90 directions where it vanishes)."""
    out = []
    for v in _orbit_reps(group, M_RADIUS):
        _, half = _half_orbit(v, group)
        P = frozenset({(0, 0)})
        for w in half:
            P = pmul(P, tfac(w))
        out.append((("O", v), P, tuple(half)))
        for e in M_PSI:
            if math.gcd(e, m) != 1:
                continue
            P = frozenset({(0, 0)})
            for w in half:
                term, power, T, i = frozenset(), frozenset({(0, 0)}), _psi(e), 0
                while T >> i:
                    if T >> i & 1:
                        term = term ^ power
                    power = pmul(power, tfac(w))
                    i += 1
                P = pmul(P, term)
            out.append((("P%d" % e, v), P, ()))
    return tuple(out)


def _levels(m):
    """(g, n = 2^g mod m, [q]) for proper divisors g of d, q prime powers dividing
    (2^d - 1)/(2^g - 1) and 2^s - 1."""
    d, s = ord2(m), sord(m)
    out = []
    for g in range(1, d):
        if d % g:
            continue
        N = (2**d - 1) // (2**g - 1)
        qs = [q for q in _prime_powers_dividing(N, Q_BOUND) if (2**s - 1) % q == 0]
        if qs:
            out.append((g, pow(2, g, m), qs))
    return out


def certificate(f, m):
    """Mechanism B: the best (q, witness) found, or (1, None)."""
    f = frozenset(map(tuple, f))
    levels = _levels(m)
    if not levels:
        return 1, None
    group = symmetries(f)
    atoms = _atoms(group, m)
    probes = [_Probe(f, v, m) for v in PROBES]
    best = (1, None)
    combos = [()] + [c for k in range(1, MAX_ATOMS + 1)
                     for c in itertools.combinations_with_replacement(range(len(atoms)), k)]
    qs_all = sorted({q for _, _, qs in levels for q in qs}, reverse=True)
    for combo in combos:
        M = frozenset({(0, 0)})
        zero_dirs = []
        for i in combo:
            M = pmul(M, atoms[i][1])
            zero_dirs += atoms[i][2]
        for q in qs_all:
            if q <= best[0]:
                break
            Es = [0] if not combo else [q * k for k in range(1, MAX_K + 1)]
            for E in Es:
                gs = [(g, n) for g, n, qs in levels if q in qs]
                gs = [(g, n) for g, n in gs if all(P.invariant(M, E, n) for P in probes)]
                if not gs or not all(line_ok(f, w, m, q) for w in zero_dirs):
                    continue
                B = _dense_product(f, M, E, m)
                for g, n in gs:
                    if _invariant(B, n, m):
                        best = (q, dict(M=[atoms[i][0] for i in combo], E=E, g=g, n=n, q=q))
                        break
                if best[0] == q:
                    break
    return best


PROBES = ((1, 0), (0, 1), (1, 1), (1, 2), (2, 1), (1, 3))


def _fold(x, m, mask):
    while x >> m:
        x = (x & mask) ^ (x >> m)
    return x


class _Probe:
    """The image of polynomials under x^(p, r) -> z^(v_1 p + v_2 r) mod z^m - 1, a ring
    homomorphism commuting with the dilations: a cheap necessary condition for invariance."""

    def __init__(self, f, v, m):
        self.v, self.m, self.mask = v, m, (1 << m) - 1
        self.f = self.image(f)
        self.cache = {}

    def image(self, P):
        x = 0
        for p, r in P:
            x ^= 1 << ((self.v[0] * p + self.v[1] * r) % self.m)
        return x

    def mul(self, a, b):
        return _fold(halffrob._clmul(a, b), self.m, self.mask)

    def invariant(self, M, E, n):
        key = (M, E)
        if key not in self.cache:
            b, base, e = self.f, self.image(M), E
            while e:
                if e & 1:
                    b = self.mul(b, base)
                base, e = self.mul(base, base), e >> 1
            bits = bin(b)[:1:-1]
            self.cache[key] = frozenset(i for i, ch in enumerate(bits) if ch == "1")
        S, m = self.cache[key], self.m
        return all(i * n % m in S for i in S)


def _dense_product(f, M, E, m):
    """f * M^E (mod x^m - 1, y^m - 1) as a dense 0/1 array, by repeated squaring with exact
    integer FFT convolution (entries are counts < 2^53, reduced mod 2 after each product)."""

    def mul(A, B):
        C = np.fft.ifft2(np.fft.fft2(A) * np.fft.fft2(B)).real
        return (np.rint(C).astype(np.int64) & 1).astype(np.float64)

    R = _dense(f, m).astype(np.float64)
    base, e = _dense(M, m).astype(np.float64), E
    while e:
        if e & 1:
            R = mul(R, base)
        e >>= 1
        if e:
            base = mul(base, base)
    return R.astype(np.uint8)


# ---------------------------------------------------------------- mechanism A

@functools.cache
def _pair_candidates(group):
    """Symmetric C: every symmetric subset of [-C_RADIUS, C_RADIUS]^2, and unions of symmetry
    orbits within C_ORBIT_RADIUS."""
    out = set()
    half = [v for v in itertools.product(range(-C_RADIUS, C_RADIUS + 1), repeat=2) if v > (0, 0)]
    for k in range(len(half) + 1):
        for S in itertools.combinations(half, k):
            for center in (0, 1):
                C = set(S) | {(-a, -b) for a, b in S} | ({(0, 0)} if center else set())
                if len(C) > 1:
                    out.add(frozenset(C))
    orbs = []
    seen = set()
    for v in itertools.product(range(-C_ORBIT_RADIUS, C_ORBIT_RADIUS + 1), repeat=2):
        if v in seen:
            continue
        o = frozenset(halffrob._apply(M, v) for M in group) | {(-v[0], -v[1])}
        seen |= o
        if max(max(abs(a), abs(b)) for a, b in o) <= C_ORBIT_RADIUS:
            orbs.append(o)
    for k in range(1, len(orbs) + 1):
        for S in itertools.combinations(orbs, k):
            C = frozenset().union(*S)
            if len(C) > 1:
                out.add(C)
    return tuple(sorted(out, key=lambda C: (len(C), sorted(C))))


def _width(P):
    xs = [p for p, _ in P]
    ys = [r for _, r in P]
    return max(xs) - min(xs), max(ys) - min(ys)


def twisted_pair(f, m):
    """Mechanism A: (q, witness) for f = C^(a) C^(b), or (1, None)."""
    f = frozenset(map(tuple, f))
    d = ord2(m)
    logs = {}
    x = 1 % m
    for k in range(d):
        logs.setdefault(x, k)
        x = 2 * x % m
    W = _width(f)
    best = (1, None)
    for C in _pair_candidates(symmetries(f)):
        Wc = _width(C)
        for a in range(1, max(W) + 1):
            for b in range(a + 1, max(W) + 1):
                if (Wc[0] * (a + b), Wc[1] * (a + b)) != W:
                    continue
                if math.gcd(a, m) != 1 or math.gcd(b, m) != 1:
                    continue
                r = b * pow(a, -1, m) % m
                ks = [logs[r]] if r in logs else []
                if (-r) % m in logs:  # C is symmetric by construction
                    ks.append(logs[(-r) % m])
                if not ks:
                    continue
                if pmul(pscale(C, a), pscale(C, b)) != f:
                    continue
                q = max(math.gcd(1 + 2**k, 2**d - 1) for k in ks)
                if q > best[0]:
                    best = (q, dict(C=sorted(C), a=a, b=b, q=q))
    return best


# ---------------------------------------------------------------- the condition

def explain(f, m):
    f = frozenset(map(tuple, f))
    if m < 3 or m % 2 == 0 or not f:
        return None
    d, s = ord2(m), sord(m)
    symmetric = frozenset((-p, -r) for p, r in f) == f
    lift = (2**d - 1) // (2**s - 1) if symmetric else 1
    found = []
    qa, wa = twisted_pair(f, m)
    if qa > 1:
        found.append(("twisted pair", qa, wa))
    if symmetric:
        qb, wb = certificate(f, m)
        if qb > 1:
            found.append(("certificate", qb, wb))
        qh = halffrob.condition(f, m)
        if qh > 1:
            found.append(("half-Frobenius", qh, None))
    q = lift
    for _, qi, _ in found:
        q = math.lcm(q, qi)
    if q == lift:
        return None
    return dict(q=q, found=found)


def condition(f, m: int) -> int:
    w = explain(f, m)
    return w["q"] if w else 1
