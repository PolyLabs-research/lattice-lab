"""Independent library for the specificity / soundness / calibration verification (verify-specificity).

Nothing here imports the investigators' code.  Two independent models of the arithmetic:
  * exact group-ring arithmetic in F2[x, y]/(x^m - 1, y^m - 1) (m x m uint8 arrays, FFT convolution, exact
    for these sizes), powers by Frobenius dilations;
  * eigenvalues f(zeta^j, zeta^k) in an explicitly constructed F(2^d), d = ord_m(2), with a modulus that is a
    sparse irreducible polynomial chosen here (NOT a factor of Phi_m), zeta = x^((2^d-1)/m) for an element x
    of order divisible by m found by search.
Rules: own construction of the square family (D4-orbits (a, b), 0 <= b <= a <= r, lexicographic bit order).
"""
from __future__ import annotations

import functools
import math

import numpy as np
import sympy

# ---------------------------------------------------------------- rules


def orbits(r):
    return sorted((a, b) for a in range(r + 1) for b in range(a + 1))


def orbit_points(a, b):
    return {(sa * p, sb * q) for p, q in ((a, b), (b, a)) for sa in (1, -1) for sb in (1, -1)}


def rule(n, r):
    out = set()
    for i, o in enumerate(orbits(r)):
        if n >> i & 1:
            out |= orbit_points(*o)
    return frozenset(out)


def rule_number(pts):
    """inverse of rule(): (n, r) for a D4-symmetric exponent set."""
    pts = set(pts)
    r = max(max(abs(p), abs(q)) for p, q in pts)
    n = 0
    for i, o in enumerate(orbits(r)):
        op = orbit_points(*o)
        if op <= pts:
            n |= 1 << i
            pts -= op
        else:
            assert not (op & pts), "not D4-symmetric"
    assert not pts
    return n, r


# ---------------------------------------------------------------- Laurent polynomials over F2 (exponent sets)


def lmul(A, B):
    out = set()
    for p, q in A:
        for r, s in B:
            out ^= {(p + r, q + s)}
    return frozenset(out)


def ladd(A, B):
    return frozenset(set(A) ^ set(B))


def ldiv(N, D):
    """exact division N / D of Laurent polynomials over F2 by leading-term elimination (lex order on (p, q)).
    Quotient terms must lie in the box [min N - min D, max N - max D] (coordinatewise); leaving it means D does
    not divide N.  Returns (Q, R) with R empty iff D divides N (then N = D * Q exactly)."""
    N = set(N)
    if not N:
        return frozenset(), frozenset()
    dl = max(D)
    lo = (min(p for p, q in N) - min(p for p, q in D), min(q for p, q in N) - min(q for p, q in D))
    hi = (max(p for p, q in N) - max(p for p, q in D), max(q for p, q in N) - max(q for p, q in D))
    Q = set()
    while N:
        lead = max(N)
        sh = (lead[0] - dl[0], lead[1] - dl[1])
        if not (lo[0] <= sh[0] <= hi[0] and lo[1] <= sh[1] <= hi[1]):
            return frozenset(Q), frozenset(N)
        Q ^= {sh}
        for p, q in D:
            N ^= {(p + sh[0], q + sh[1])}
    return frozenset(Q), frozenset()


S_POLY = frozenset({(1, 0), (-1, 0), (0, 1), (0, -1)})  # s = a + b = x + 1/x + y + 1/y
PI_POLY = frozenset({(1, 1), (1, -1), (-1, 1), (-1, -1)})  # pi = ab


def radius_of(pts):
    return max(max(abs(p), abs(q)) for p, q in pts)


# ---------------------------------------------------------------- group ring F2[Z/m x Z/m]


class GroupRing:
    def __init__(self, m):
        self.m = m
        self.d = sympy.n_order(2, m)
        self.ONE = np.zeros((m, m), dtype=np.uint8)
        self.ONE[0, 0] = 1

    def elem(self, pts):
        a = np.zeros((self.m, self.m), dtype=np.uint8)
        for p, q in pts:
            a[p % self.m, q % self.m] ^= 1
        return a

    def mul(self, a, b):
        fa = np.fft.rfft2(a.astype(np.float64))
        fb = np.fft.rfft2(b.astype(np.float64))
        c = np.fft.irfft2(fa * fb, s=(self.m, self.m))
        ci = np.rint(c).astype(np.int64)
        assert np.max(np.abs(c - ci)) < 0.2
        return (ci & 1).astype(np.uint8)

    def dil(self, a, u):
        m = self.m
        u %= m
        assert math.gcd(u, m) == 1
        idx = (np.arange(m) * u) % m
        out = np.zeros_like(a)
        out[np.ix_(idx, idx)] = a
        return out

    def power(self, a, e):
        """a^e using a^(2^i) = a(x^(2^i), y^(2^i)) (characteristic 2)."""
        res = self.ONE.copy()
        i = 0
        while e:
            if e & 1:
                res = self.mul(res, self.dil(a, pow(2, i, self.m)))
            e >>= 1
            i += 1
        return res

    def confined(self, a, q):
        """all nonzero eigenvalues are q-th powers in F(2^d)*: a^((2^d-1)/q) == a^(2^d-1) (the support idempotent)."""
        N = 2 ** self.d - 1
        assert N % q == 0
        E = self.power(a, N)
        return bool(np.array_equal(self.power(a, N // q), E))


# ---------------------------------------------------------------- F(2^d), vectorised


def _poly_int(expr_coeffs):
    return sum(1 << e for e in expr_coeffs)


@functools.cache
def modulus(d):
    """a sparse irreducible polynomial of degree d over F2 (trinomial if one exists, else pentanomial),
    chosen with the largest middle exponents so that it differs from vlib's / eigen's choices."""
    x = sympy.Symbol("x")
    for k in range(d - 1, 0, -1):
        P = sympy.Poly(x ** d + x ** k + 1, x, modulus=2)
        if P.is_irreducible:
            return (1 << d) | (1 << k) | 1
    for a in range(d - 1, 2, -1):
        for b in range(a - 1, 1, -1):
            for c in range(b - 1, 0, -1):
                P = sympy.Poly(x ** d + x ** a + x ** b + x ** c + 1, x, modulus=2)
                if P.is_irreducible:
                    return (1 << d) | (1 << a) | (1 << b) | (1 << c) | 1
    raise ValueError(d)


class Field:
    """F(2^d) = F2[z]/(modulus(d)); elements as Python ints or numpy uint64 arrays."""

    def __init__(self, d, mod=None):
        self.d = d
        self.mod = mod if mod is not None else modulus(d)
        self.N = 2 ** d - 1

    def mul(self, a, b):
        d, mod = self.d, self.mod
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> d & 1:
                a ^= mod
        return r

    def pow(self, a, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    # vectorised
    def vmul(self, a, b):
        a = np.asarray(a, dtype=np.uint64).copy()
        b = np.asarray(b, dtype=np.uint64).copy()
        a, b = np.broadcast_arrays(a, b)
        a = a.copy(); b = b.copy()
        r = np.zeros_like(a)
        top = np.uint64(1) << np.uint64(self.d)
        mod = np.uint64(self.mod)
        one = np.uint64(1)
        for _ in range(self.d):
            r ^= np.where(b & one, a, np.uint64(0))
            b >>= one
            a <<= one
            a ^= np.where(a & top, mod, np.uint64(0))
        return r

    def vpow(self, a, e):
        a = np.asarray(a, dtype=np.uint64)
        r = np.ones_like(a)
        while e:
            if e & 1:
                r = self.vmul(r, a)
            a = self.vmul(a, a)
            e >>= 1
        return r


@functools.cache
def setup(m):
    """(Field, zeta) for size m: zeta a primitive m-th root of unity in F(2^d), d = ord_m(2)."""
    d = sympy.n_order(2, m)
    F = Field(d)
    N = F.N
    assert N % m == 0
    pf = sympy.primefactors(m)
    for x in range(2, 1 << min(d, 20)):
        z = F.pow(x, N // m)
        if z != 1 and all(F.pow(z, m // p) != 1 for p in pf):
            return F, z
    raise ValueError(m)


class Eig:
    """eigenvalues of rules at size m, at every character (j, k), in setup(m)'s field."""

    def __init__(self, m):
        self.m = m
        self.F, self.zeta = setup(m)
        zp = [1]
        for _ in range(m - 1):
            zp.append(self.F.mul(zp[-1], self.zeta))
        assert self.F.mul(zp[-1], self.zeta) == 1
        self.zp = np.array(zp, dtype=np.uint64)
        J, K = np.meshgrid(np.arange(m), np.arange(m), indexing="ij")
        self.J, self.K = J, K

    def values(self, pts):
        """m x m array of f(zeta^j, zeta^k)."""
        m = self.m
        v = np.zeros((m, m), dtype=np.uint64)
        for p, q in pts:
            v ^= self.zp[(p * self.J + q * self.K) % m]
        return v

    def qth_power_mask(self, v, q):
        """boolean array: v is a nonzero q-th power in F(2^d)*."""
        N = self.F.N
        w = self.F.vpow(v, N // q)
        return (v != 0) & (w == 1)

    def confined(self, v, q):
        nz = v != 0
        nz[0, 0] = nz[0, 0]  # the trivial character is included like any other
        return bool(np.all(self.qth_power_mask(v, q)[nz]))


# ---------------------------------------------------------------- 37-specific: logs mod 27 and mod 19 in F(2^18)


class Logs37:
    """discrete-log residues mod 27 and mod 19 of elements of F(2^18)* inside setup(37)'s F(2^36).
    log_r(v) = i where v^((2^18-1)/r) = h_r^i, h_r = gamma^((2^18-1)/r), gamma = g^(2^18+1), g primitive in F(2^36)*."""

    def __init__(self):
        self.E = Eig(37)
        F = self.E.F
        N = F.N
        primes = sympy.primefactors(N)
        g = next(x for x in range(2, 5000) if all(F.pow(x, N // p) != 1 for p in primes))
        self.g = g
        gamma = F.pow(g, 2 ** 18 + 1)
        self.N18 = 2 ** 18 - 1
        self.tab = {}
        for r in (27, 19, 9, 3):
            h = F.pow(gamma, self.N18 // r)
            pw = [1]
            for _ in range(r - 1):
                pw.append(F.mul(pw[-1], h))
            assert F.mul(pw[-1], h) == 1 and len(set(pw)) == r
            self.tab[r] = {int(x): i for i, x in enumerate(pw)}

    def log(self, v, r):
        """array of logs mod r (-1 for zero); v must lie in F(2^18)."""
        F = self.E.F
        v = np.asarray(v, dtype=np.uint64)
        assert np.all(F.vpow(v, 2 ** 18) == v), "not in F(2^18)"
        w = F.vpow(v, self.N18 // r)
        lut = self.tab[r]
        out = np.array([lut.get(int(x), -2) for x in w.ravel()], dtype=np.int64).reshape(v.shape)
        out[v == 0] = -1
        assert not np.any(out == -2)
        return out
