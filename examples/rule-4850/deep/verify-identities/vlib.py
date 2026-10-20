"""Independent verifier library (written from scratch; imports nothing from the investigators).

 * Laurent polynomials over GF(2) in x, y: frozensets of exponent pairs (a, b).
 * Exact division in F2[x^+-1, y^+-1] by long division (lex leading terms).
 * The group ring F2[(Z/37)^2]: frozensets of exponent pairs reduced mod 37.
 * F(2^36) built from a degree-36 irreducible TRINOMIAL (not Phi_37, which the project's
   eigen.py / gf2.py / census37 all use), with zeta = h^((2^36-1)/37) found by search.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache

M = 37

# ----------------------------------------------------------------- Laurent polynomials


def lp(points) -> frozenset:
    c = Counter()
    for p in points:
        c[tuple(p)] ^= 1
    return frozenset(k for k, v in c.items() if v)


def lmul(f, g) -> frozenset:
    c = Counter()
    for a, b in f:
        for p, q in g:
            c[(a + p, b + q)] ^= 1
    return frozenset(k for k, v in c.items() if v)


def ladd(*fs) -> frozenset:
    out = set()
    for f in fs:
        out ^= set(f)
    return frozenset(out)


def ldiv(num, den):
    """Exact long division in F2[x^+-1, y^+-1] using lex order on (a, b).
    Returns (quotient, remainder). If den | num the remainder is empty: the lex-leading terms
    of q*den are peeled off in descending order. The loop stops once the needed quotient
    monomial has x-degree below min_a(num) - min_a(den), which no true quotient can have
    (F2[y^+-1] is a domain, so min_a(q*den) = min_a(q) + min_a(den))."""
    den = frozenset(den)
    lead = max(den)
    r = set(num)
    q = set()
    if not r:
        return frozenset(), frozenset()
    floor = min(a for a, _ in r) - min(a for a, _ in den)
    while r:
        t = max(r)
        mono = (t[0] - lead[0], t[1] - lead[1])
        if mono[0] < floor:
            break
        q ^= {mono}
        for a, b in den:
            r ^= {(a + mono[0], b + mono[1])}
    return frozenset(q), frozenset(r)


def orbits(radius: int):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def orbit_points(a, b):
    return {(sa * p, sb * q) for p, q in ((a, b), (b, a)) for sa in (1, -1) for sb in (1, -1)}


def rule(n: int, radius: int) -> frozenset:
    out = set()
    for i, o in enumerate(orbits(radius)):
        if n >> i & 1:
            out ^= orbit_points(*o)
    assert n >> len(orbits(radius)) == 0, "n has bits beyond the family"
    return frozenset(out)


def shell(a, b):
    return frozenset(orbit_points(a, b))


def shells_of(S):
    c = Counter(tuple(sorted((abs(p), abs(q)), reverse=True)) for p, q in S)
    return dict(c)


def is_d4(S):
    S = set(S)
    return all({(-a, b), (a, -b), (b, a)} <= S for a, b in S)


# ----------------------------------------------------------------- group ring mod 37


def red(S, m=M) -> frozenset:
    return lp(((a % m, b % m) for a, b in S))


def gmul(f, g, m=M) -> frozenset:
    c = Counter()
    for a, b in f:
        for p, q in g:
            c[((a + p) % m, (b + q) % m)] ^= 1
    return frozenset(k for k, v in c.items() if v)


def gdil(S, A, m=M) -> frozenset:
    """exponent column vector e -> A e (mod m)."""
    (a11, a12), (a21, a22) = A
    return lp((((a11 * a + a12 * b) % m, (a21 * a + a22 * b) % m) for a, b in S))


# ----------------------------------------------------------------- GF(2)[z] and F(2^36)


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def pmulmod(a, b, m):
    return pmod(pmul(a, b), m)


def ppowmod(a, e, m):
    r = 1
    a = pmod(a, m)
    while e:
        if e & 1:
            r = pmulmod(r, a, m)
        a = pmulmod(a, a, m)
        e >>= 1
    return r


def x_2k(k, m):
    """x^(2^k) mod m by repeated squaring."""
    v = 2
    for _ in range(k):
        v = pmulmod(v, v, m)
    return v


def rabin_irreducible(m):
    n = m.bit_length() - 1
    if x_2k(n, m) != pmod(2, m):
        return False
    for p in {p for p in range(2, n + 1) if n % p == 0 and all(p % d for d in range(2, p))}:
        if pgcd(x_2k(n // p, m) ^ 2, m) != 1:
            return False
    return True


D = 36
N36 = 2**D - 1
N18 = 2**18 - 1


def _find_modulus():
    for k in range(1, 18):
        m = (1 << 36) | (1 << k) | 1
        if rabin_irreducible(m):
            return m
    raise RuntimeError


MOD = _find_modulus()


def fmul(a, b):
    return pmulmod(a, b, MOD)


def fpow(a, e):
    return ppowmod(a, e, MOD)


def finv(a):
    return fpow(a, N36 - 1)


def _find_zeta():
    h = 2
    while True:
        z = fpow(h, N36 // M)
        if z != 1:
            assert fpow(z, M) == 1
            return z
        h += 1


ZETA = _find_zeta()
ZP = [1]
for _ in range(M - 1):
    ZP.append(fmul(ZP[-1], ZETA))
assert fmul(ZP[-1], ZETA) == 1 and len(set(ZP)) == M


def value(S, j, k):
    v = 0
    for a, b in S:
        v ^= ZP[(a * j + b * k) % M]
    return v


def t(n):
    return ZP[n % M] ^ ZP[(-n) % M]


PRIMES36 = (3, 5, 7, 13, 19, 37, 73, 109)
assert all(N36 % p == 0 for p in PRIMES36)
_r = N36
for _p in PRIMES36:
    while _r % _p == 0:
        _r //= _p
assert _r == 1


def order(v):
    assert v != 0
    o = N36
    for p in PRIMES36:
        while o % p == 0 and fpow(v, o // p) == 1:
            o //= p
    return o


def in_f18(v):
    return fpow(v, 2**18) == v


def is_power(v, q, field='36'):
    """v a q-th power in F(2^36)* (field='36') or in F(2^18)* (field='18', v must lie in F(2^18))."""
    if field == '18':
        assert in_f18(v)
        assert N18 % q == 0
        return fpow(v, N18 // q) == 1
    assert N36 % q == 0
    return fpow(v, N36 // q) == 1


def classes():
    """Frobenius orbits of nonzero characters (j, k) in (Z/37)^2: list of representatives."""
    seen, reps = set(), []
    for j in range(M):
        for k in range(M):
            if (j, k) == (0, 0) or (j, k) in seen:
                continue
            reps.append((j, k))
            c = (j, k)
            while c not in seen:
                seen.add(c)
                c = (2 * c[0] % M, 2 * c[1] % M)
    return reps


def period(S):
    """lcm of multiplicative orders of the nonzero eigenvalues over all characters (incl. trivial)."""
    from math import lcm
    per = 1
    zeros = 0
    for j, k in classes() + [(0, 0)]:
        v = value(S, j, k)
        if v == 0:
            zeros += 1
            continue
        per = lcm(per, order(v))
    return per, zeros
