"""
Unit-times-power confinement.  See proposal.md for the statement and the proof.

    condition(f, m) -> q        every nonzero eigenvalue of f at m is a q-th power in F(2^d)*,
                                d = ord_m(2); 1 if no claim

Notation.  m is odd, d = ord_m(2), s = sord(m), and R = (2^d - 1)/(2^s - 1) (1 or 2^s + 1).  A
rule f is a Laurent polynomial over GF(2) with f(1/x, 1/y) = f; its eigenvalue at a character c is
lambda_f(c) = f(zeta^c), in F(2^s).  t_j = zeta^j + zeta^-j are rule 90's eigenvalues.  For a
primitive w in Z^2, X_w = x^w1 y^w2, and for odd e >= 1, Phi_e is the e-th cyclotomic polynomial.

The mechanism.  Factor f over GF(2).  Its irreducible factors are of two kinds:

  * "line" factors pi(X_w), a polynomial in one monomial.  Every such pi (other than X) divides
    Phi_e(X_w) for exactly one odd e (e = the multiplicative order of X modulo pi).  The factors
    of Phi_e(X_w) over GF(2) form one "unit group" (w, e).
  * genuinely two-dimensional factors.

Let q be a prime power dividing 2^s - 1.  Suppose

  1. every two-dimensional factor occurs with multiplicity divisible by q (the product of the
     two-dimensional factors is h^q for a Laurent polynomial h), and
  2. for each unit group (w, e), all factors of Phi_e(X_w) (counting those absent from f, with
     multiplicity 0) occur with multiplicities congruent to one k modulo q, and if k != 0 mod q,
     the values Psi_e(t_j) (e > 1), resp. t_j (e = 1), j in Z/m, are q-th powers in F(2^s)*
     whenever nonzero.  This holds
       (a) if every t_j (j != 0) is a q-th power (rule 90's own confinement at m) and
           e = 1, or e is prime, or gcd(e, m) = 1, or
       (b) if every divisor e' > 1 of e is congruent to +-2^a(e') mod m, and q divides
           A_e = sum_{e' | e} mu(e/e') 2^a(e')   (a(1) = 0),  since then Psi_e(t_j)^2 = t_j^A_e.

So f = x^v * prod_(w,e) Phi_e(X_w)^k(w,e) * h'^q, and every nonzero eigenvalue of f is a q-th power
in F(2^s)*.  condition returns the product of the largest such prime powers, times R, if it is
more than R; it also consults the two previous pilots' conditions (tools/certificate.py, which
includes tools/halffrob.py) and returns the lcm.

The only field computation is rule 90's confinement (halffrob._rule90_powers, the input of the
splitting mechanism), used in 2(a); no eigenvalue of f is computed.
"""

from __future__ import annotations

import functools
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "tools"))

from sympy import ZZ  # noqa: E402
from sympy.polys import galoistools as _gt  # noqa: E402

import certificate  # noqa: E402
import halffrob  # noqa: E402
from halffrob import _clmul, _cldivmod, ord2, sord  # noqa: E402

USE_PREVIOUS = True  # also consult the previous pilots' conditions


# ---------------------------------------------------------------- GF(2)[X] as int bitmasks

def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, _cldivmod(a, b)[1]
    return a


def _to_list(a: int) -> list:
    return [(a >> i) & 1 for i in range(a.bit_length() - 1, -1, -1)]


def _from_list(c) -> int:
    out = 0
    for x in c:
        out = (out << 1) | (int(x) % 2)
    return out


def _clpow(a: int, k: int) -> int:
    r = 1
    while k:
        if k & 1:
            r = _clmul(r, a)
        a, k = _clmul(a, a), k >> 1
    return r


@functools.cache
def _factor1(a: int) -> tuple:
    """Irreducible factors of a in GF(2)[X] (a(0) != 0), with multiplicities."""
    _, fl = _gt.gf_factor(_to_list(a), 2, ZZ)
    return tuple((_from_list(g), e) for g, e in fl)


def _divisors(n: int):
    return [d for d in range(1, n + 1) if n % d == 0]


@functools.cache
def _xorder(pi: int) -> int:
    """Multiplicative order of X modulo the irreducible pi != X (odd)."""
    if pi == 0b11:
        return 1
    n = 2 ** (pi.bit_length() - 1) - 1
    e = n
    for p in _primes(n):
        while e % p == 0 and _clmul_mod_pow(e // p, pi) == 1:
            e //= p
    return e


def _clmul_mod_pow(e: int, pi: int) -> int:
    r, a = 1, 0b10
    while e:
        if e & 1:
            r = _cldivmod(_clmul(r, a), pi)[1]
        a = _cldivmod(_clmul(a, a), pi)[1]
        e >>= 1
    return r


@functools.cache
def _npieces(e: int) -> int:
    """Number of irreducible factors of Phi_e over GF(2) (e odd)."""
    if e == 1:
        return 1
    phi = sum(1 for k in range(1, e + 1) if math.gcd(k, e) == 1)
    return phi // ord2(e)


# ---------------------------------------------------------------- the factorisation (m-free)

def _hull_dirs(S):
    """Primitive directions (up to sign) of the edges of the Newton polygon of S."""
    pts = sorted(set(S))
    if len(pts) < 2:
        return []

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    if len(hull) == 1:
        hull = pts[:1] + pts[-1:]
    out = set()
    for i in range(len(hull)):
        a, b = hull[i], hull[(i + 1) % len(hull)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        g = math.gcd(dx, dy)
        if g == 0:
            continue
        dx, dy = dx // g, dy // g
        if dx < 0 or (dx == 0 and dy < 0):
            dx, dy = -dx, -dy
        out.add((dx, dy))
    return sorted(out)


def _complete(w):
    """w' with det [w, w'] = 1."""
    a, b = w
    # extended gcd: a u + b v = 1
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    while r:
        qq = old_r // r
        old_r, r = r, old_r - qq * r
        old_s, s = s, old_s - qq * s
        old_t, t = t, old_t - qq * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    assert old_r == 1
    # a*old_s + b*old_t = 1  ->  det [[a, -old_t], [b, old_s]] = 1
    return (-old_t, old_s)


def _line_content(S, w):
    """The content of f with respect to the line direction w: f as a polynomial in
    Y = X_{w'} with coefficients in GF(2)[X_w^+-1]; returns the gcd of the coefficients (an int in
    X = X_w, normalised by powers of X)."""
    wp = _complete(w)
    # v = alpha w + beta w'  ->  alpha = det[v, w'], beta = det[w, v]
    rows = {}
    for v in S:
        al = v[0] * wp[1] - v[1] * wp[0]
        be = w[0] * v[1] - w[1] * v[0]
        rows.setdefault(be, []).append(al)
    g = 0
    for als in rows.values():
        lo = min(als)
        c = 0
        for al in als:
            c ^= 1 << (al - lo)
        while c and not c & 1:
            c >>= 1
        g = _gcd(g, c) if g else c
        if g == 1:
            return 1
    return g


def _line_poly(pi: int, w):
    """pi(X_w) as a Laurent polynomial (frozenset)."""
    return frozenset((i * w[0], i * w[1]) for i in range(pi.bit_length()) if pi >> i & 1)


def _qth_root(P, q):
    """h with h^q = P (Laurent polynomials over GF(2), up to a monomial), or None."""
    if len(P) == 1:
        return frozenset({(0, 0)})
    ax, ay = min(p for p, _ in P), min(r for _, r in P)
    N = max(p for p, _ in P) - ax + 1
    u = 0
    for p, r in P:
        u ^= 1 << (p - ax + N * (r - ay))
    _, sq = _gt.gf_sqf_list(_to_list(u), 2, ZZ)
    root = 1
    for g, e in sq:
        if e % q:
            return None
        root = _clmul(root, _clpow(_from_list(g), e // q))
    if _clpow(root, q) != u:
        return None
    H, i, x = set(), 0, root
    while x:
        if x & 1:
            H.add((i % N, i // N))
        x >>= 1
        i += 1
    if max(p for p, _ in H) * q > N - 1:
        return None
    return frozenset(H)


@functools.cache
def structure(f):
    """m-independent data: (groups, core) where groups maps (w, e) to the list of multiplicities of
    the factors of Phi_e(X_w) present in f (and the number of factors of Phi_e), and core is the
    product of the two-dimensional factors, f divided by all line factors (up to a monomial)."""
    S = frozenset(f)
    groups = {}
    core = S
    for w in _hull_dirs(S):
        c = _line_content(S, w)
        if c == 1:
            continue
        for pi, n in _factor1(c):
            e = _xorder(pi)
            groups.setdefault((w, e), []).append(n)
            core = halffrob.pdiv(core, _pow_poly(_line_poly(pi, w), n))
            assert core is not None
    return {k: (tuple(v), _npieces(k[1])) for k, v in groups.items()}, core


def _pow_poly(A, n):
    out = frozenset({(0, 0)})
    for _ in range(n):
        out = halffrob.pmul(out, A)
    return out


@functools.cache
def _core_gcd(core) -> int:
    """gcd of the multiplicities in the square-free decomposition of the core's Kronecker image:
    a multiple of every q for which the core is a q-th power."""
    ax, ay = min(p for p, _ in core), min(r for _, r in core)
    N = max(p for p, _ in core) - ax + 1
    u = 0
    for p, r in core:
        u ^= 1 << (p - ax + N * (r - ay))
    _, sq = _gt.gf_sqf_list(_to_list(u), 2, ZZ)
    g2 = 0
    for _, e in sq:
        g2 = math.gcd(g2, e)
    return g2


@functools.cache
def _core_root_ok(core, q):
    return _qth_root(core, q) is not None


# ---------------------------------------------------------------- the unit test at m

@functools.cache
def _pow2_log(m: int) -> dict:
    out, x = {}, 1 % m
    for a in range(ord2(m)):
        out.setdefault(x, a)
        out.setdefault((-x) % m, a)
        x = 2 * x % m
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


def _lemma3_exponent(e: int, m: int):
    """A_e with Psi_e(t_j)^2 = t_j^A_e for j != 0, if every divisor e' > 1 of e is +-2^a mod m."""
    logs = _pow2_log(m)
    A = 0
    for d in _divisors(e):
        if d == 1:
            a = 0
        else:
            if d % m == 0 or d % m not in logs:
                return None
            a = logs[d % m]
        A += _mobius(e // d) * 2**a
    return A


def _unit_ok(e: int, m: int, q: int) -> bool:
    """Are the nonzero values of the unit (Psi_e(t_j), or t_j for e = 1) all q-th powers?"""
    p = _prime_of(q)
    r90 = halffrob._rule90_powers(m)
    if (e == 1 or _is_prime(e) or math.gcd(e, m) == 1) and r90.get(p, 1) % q == 0:
        return True
    if e > 1:
        A = _lemma3_exponent(e, m)
        if A is not None and A % q == 0:
            return True
    return False


def _is_prime(n: int) -> bool:
    return n > 1 and all(n % p for p in range(2, int(n**0.5) + 1))


def _prime_of(q: int) -> int:
    p = 2
    while q % p:
        p += 1
    return p


def _valid(f, m: int, q: int) -> bool:
    groups, core = structure(f)
    if not _core_root_ok(core, q):
        return False
    for (w, e), (mults, npieces) in groups.items():
        ms = list(mults) + [0] * (npieces - len(mults))
        k = ms[0] % q
        if any(x % q != k for x in ms):
            return False
        if k and not _unit_ok(e, m, q):
            return False
    return True


def _primes(n: int):
    out, p = [], 2
    while p * p <= n:
        if n % p == 0:
            out.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def explain(f, m: int):
    """The unit-times-power witness: {'q_s': q in F(2^s)*, 'q': q in F(2^d)*, 'groups', 'core'}, or
    None."""
    f = frozenset(f)
    if m < 3 or m % 2 == 0 or frozenset((-x, -y) for x, y in f) != f or len(f) < 2:
        return None
    s, d = sord(m), ord2(m)
    Ns = 2**s - 1
    groups, core = structure(f)
    # candidate primes: those dividing a multiplicity, or rule 90's confinement, or a Lemma-3 exponent
    G = 0
    for mults, npieces in groups.values():
        ms = list(mults) + [0] * (npieces - len(mults))
        for x in ms:
            G = math.gcd(G, x - ms[0])
    cand = set()
    if len(core) > 1:
        g2 = _core_gcd(core)
        cand |= set(_primes(g2)) if g2 > 1 else set()
        if not cand:
            return None
    else:
        cand |= set(_primes(G)) if G > 1 else set()
        cand |= {p for p, pk in halffrob._rule90_powers(m).items() if pk > 1}
        for (w, e) in groups:
            if e > 1:
                A = _lemma3_exponent(e, m)
                if A:
                    cand |= set(_primes(math.gcd(abs(A), Ns)))
    q_s = 1
    for p in sorted(cand):
        if p == 2 or Ns % p:
            continue
        pk = 1
        while Ns % (pk * p) == 0 and _valid(f, m, pk * p):
            pk *= p
        q_s *= pk
    if q_s == 1:
        return None
    return {"q_s": q_s, "q": q_s * ((2**d - 1) // Ns), "groups": groups, "core": core}


def condition(f, m: int) -> int:
    f = frozenset(f)
    lift = (2 ** ord2(m) - 1) // (2 ** sord(m) - 1) if m > 1 else 1
    w = explain(f, m)
    q = w["q"] if w else 1
    if USE_PREVIOUS:
        q = math.lcm(q, certificate.condition(f, m))
    if q == 1 or q == lift:
        return 1
    return q
