"""Shared tools for the hexagon-family study (deep dive on rule 4850, angle: the family and other sizes).

  hex_rule(p, q)       exact Laurent polynomial f_{p,q} = (Hex_{p,q} + Hex_{p,q}^T) / s as an exponent set,
                       Hex_{p,q} = {+-(2p,0), +-(p,+-q)},  s = x + 1/x + y + 1/y
  rule_number(f)       the square-family rule number and radius of a D4-symmetric exponent set
  GF(m)                fast F(2^d), d = ord_m(2), with zeta = z (same modulus as linear-atlas-3/eigen.field),
                       windowed carry-less multiplication, and 3-adic logarithms (log mod 3^A, A = v3(2^d - 1))
  odd_part(f, m)       re-export of the independent checker linear-atlas-3/eigen.odd_part
"""
from __future__ import annotations

import functools
import math
import sys

sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import eigen  # noqa: E402
import sympy  # noqa: E402

odd_part = eigen.odd_part


# ---------------------------------------------------------------- exact polynomials
def hex_pts(p, q):
    return {(2 * p, 0), (-2 * p, 0), (p, q), (-p, -q), (p, -q), (-p, q)}


def _div_poly(H: dict[int, int], R: int) -> dict[int, int]:
    """H: dict x-exponent -> int (bits = y-exponents), all exponents >= 0.  Return Q = H / ((x+y)(1+xy))."""
    H = dict(H)
    # divide by (x + y), monic in x: from the top x-degree down
    Q1 = {}
    top = max(H)
    for n in range(top, 0, -1):
        c = H.get(n, 0)
        if c:
            Q1[n - 1] = c
            H[n - 1] = H.get(n - 1, 0) ^ (c << 1)
            H[n] = 0
    assert H.get(0, 0) == 0, 'not divisible by x + y'
    # divide by (1 + x y): from the bottom x-degree up
    H = Q1
    Q2 = {}
    top = max(H)
    for n in range(0, top + 1):
        c = H.get(n, 0)
        if c:
            Q2[n] = c
            H[n + 1] = H.get(n + 1, 0) ^ (c << 1)
            H[n] = 0
    assert all(v == 0 for v in H.values()), 'not divisible by 1 + x y'
    return Q2


def quotient_by_s(G: set) -> frozenset:
    """Exponent set G (a Laurent polynomial divisible by s = (x+y)(1+xy)/(xy)) -> G / s."""
    R = max(max(abs(a), abs(b)) for a, b in G) + 1
    H = {}
    for a, b in G:
        H[a + R] = H.get(a + R, 0) ^ (1 << (b + R))
    Q = _div_poly(H, R)  # = (G/s) * (xy)^(R-1)
    out = set()
    for i, bits in Q.items():
        j = 0
        while bits:
            if bits & 1:
                out.add((i - (R - 1), j - (R - 1)))
            bits >>= 1
            j += 1
    return frozenset(out)


@functools.cache
def hex_rule(p: int, q: int) -> frozenset:
    G = hex_pts(p, q) ^ {(b, a) for a, b in hex_pts(p, q)}
    return quotient_by_s(G)


def mul_sets(A, B):
    out = {}
    for a in A:
        for b in B:
            e = (a[0] + b[0], a[1] + b[1])
            out[e] = out.get(e, 0) ^ 1
    return frozenset(e for e, c in out.items() if c)


def rule_number(f) -> tuple[int, int] | None:
    """(n, radius) if f is a union of D4 orbits of the square family, else None."""
    f = set(f)
    if not f:
        return (0, 0)
    radius = max(max(abs(a), abs(b)) for a, b in f)
    orbs = sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})
    idx = {o: i for i, o in enumerate(orbs)}
    n = 0
    used = set()
    for a, b in f:
        o = (max(abs(a), abs(b)), min(abs(a), abs(b)))
        if o in used:
            continue
        used.add(o)
        pts = {(sp * x, sq * y) for x, y in (o, o[::-1]) for sp in (1, -1) for sq in (1, -1)}
        if not pts <= f:
            return None
        n |= 1 << idx[o]
    return n, radius


# ---------------------------------------------------------------- fast F(2^d)
class GF:
    """F(2^d) = F2[z]/(g), g = eigen.field(m)'s irreducible factor of Phi_m, zeta = z = 2."""

    def __init__(self, m: int):
        self.m = m
        if sympy.isprime(m) and sympy.n_order(2, m) == m - 1:
            # Phi_m is irreducible over F2: the same modulus eigen.field(m) returns, without factoring
            self.mod, self.d = (1 << m) - 1, m - 1
        else:
            self.mod, self.d = eigen.field(m)
        d = self.d
        self.N = 2 ** d - 1
        self.A = sympy.multiplicity(3, self.N) if self.N % 3 == 0 else 0
        # reduction tables: chunk i covers bits d + 8i .. d + 8i + 7 of a product (< 2^(2d-1))
        self.nch = (d - 1 + 7) // 8 + 1
        self.T = []
        R0 = [self._slow_red(c << d) for c in range(256)]
        T0 = [(c << d) ^ R0[c] for c in range(256)]
        R = R0
        for i in range(self.nch):
            if i:
                Rn = []
                for c in range(256):
                    v = R[c] << 8
                    Rn.append(v ^ T0[v >> d])
                R = Rn
            self.T.append([(c << (d + 8 * i)) ^ R[c] for c in range(256)])
        self.SP = [0] * 256
        for c in range(256):
            s = 0
            for b in range(8):
                if c >> b & 1:
                    s |= 1 << (2 * b)
            self.SP[c] = s
        self.zeta = 2
        self.zp = [1]
        for _ in range(m - 1):
            self.zp.append(self.mul(self.zp[-1], 2))
        self.t = [self.zp[i] ^ self.zp[(-i) % m] for i in range(m)]
        if self.A:
            self._init3()

    def _slow_red(self, v):
        d, mod = self.d, self.mod
        while v.bit_length() > d:
            v ^= mod << (v.bit_length() - 1 - d)
        return v

    def red(self, r):
        d = self.d
        if r >> d == 0:
            return r
        T = self.T
        i = (r.bit_length() - 1 - d) // 8
        while i >= 0:
            c = (r >> (d + 8 * i)) & 255
            if c:
                r ^= T[i][c]
            i -= 1
        return r

    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        if a.bit_length() < b.bit_length():
            a, b = b, a
        a2 = a << 1
        a4 = a << 2
        a8 = a << 3
        tab = (0, a, a2, a2 ^ a, a4, a4 ^ a, a4 ^ a2, a4 ^ a2 ^ a,
               a8, a8 ^ a, a8 ^ a2, a8 ^ a2 ^ a, a8 ^ a4, a8 ^ a4 ^ a, a8 ^ a4 ^ a2, a8 ^ a4 ^ a2 ^ a)
        r = 0
        sh = 0
        while b:
            r ^= tab[b & 15] << sh
            b >>= 4
            sh += 4
        return self.red(r)

    def sqr(self, a):
        SP = self.SP
        r = 0
        sh = 0
        while a:
            r |= SP[a & 255] << sh
            a >>= 8
            sh += 16
        return self.red(r)

    def pow(self, a, e):
        if e == 0:
            return 1
        if a == 0:
            return 0
        # 4-bit fixed window, left to right
        pw = [1, a]
        for _ in range(14):
            pw.append(self.mul(pw[-1], a))
        nb = (e.bit_length() + 3) // 4
        r = 1
        for i in range(nb - 1, -1, -1):
            r = self.sqr(self.sqr(self.sqr(self.sqr(r))))
            w = (e >> (4 * i)) & 15
            if w:
                r = self.mul(r, pw[w])
        return r

    def inv(self, a):
        return self.pow(a, self.N - 1)

    # ---- 3-adic logs
    def _init3(self):
        A = self.A
        self.Q = 3 ** A
        e = self.N // self.Q
        x = 3
        while True:
            g = self.pow(x, e)
            if self.pow(g, 3 ** (A - 1)) != 1:
                break
            x += 1
        self.g3 = g
        self.dlog3 = {}
        y = 1
        for i in range(self.Q):
            self.dlog3[y] = i
            y = self.mul(y, g)
        self.e3 = e

    def log3(self, v):
        """log of v mod 3^A (None for v = 0)."""
        if v == 0:
            return None
        return self.dlog3[self.pow(v, self.e3)]

    def order(self, v, primes=None):
        if v == 0:
            return 0
        primes = primes or sympy.primefactors(self.N)
        o = self.N
        for p in primes:
            while o % p == 0 and self.pow(v, o // p) == 1:
                o //= p
        return o


def v3(n, A):
    """3-adic valuation of n mod 3^A (A if n = 0 mod 3^A)."""
    n %= 3 ** A
    if n == 0:
        return A
    k = 0
    while n % 3 == 0:
        n //= 3
        k += 1
    return k


def legendre(a, p):
    return int(sympy.legendre_symbol(a % p, p)) if a % p else 0


def sqrt_minus3(m):
    """All r mod m with r^2 = -3 mod m, up to sign (one of each +-pair)."""
    out = []
    for r in range(1, m):
        if (r * r + 3) % m == 0 and (m - r) not in out:
            out.append(r)
    return out
