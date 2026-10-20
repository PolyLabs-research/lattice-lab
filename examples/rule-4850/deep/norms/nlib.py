"""Library for the 'norms' angle: N_{K/k}(W) for the mu6-Kloosterman sum W, at m = 37 and other primes.

Independent of the other investigators' field models:
  * group-ring arithmetic in Z[Z/p] and F2[Z/p] (exact convolution; F2[Z/p] -> F2[zeta_p] kills J = sum x^i);
  * a self-built GF(2^n) (irreducible polynomial found by search here), with zeta_p = g^((2^n-1)/p).

Notation (p prime, p = 1 mod 3, 2 of even order d = 2e mod p so -1 in <2>):
  zeta = zeta_p,  t_j = zeta^j + zeta^-j,  mu6 = 6th roots of 1 in F_p*,
  W(al, be) = sum_{u in mu6, e = +-1} zeta^(al u + e be / u)       (eigenvalue of h, the 12-point orbit)
  eta(x) = sum_{u in mu6} zeta^(x u)   (Gauss period of the subgroup mu6, index (p-1)/6)
"""
from __future__ import annotations

import functools
import itertools
import math
import random

import numpy as np


# ------------------------------------------------------------------ F_p helpers
def ordmod(a, m):
    x, k = a % m, 1
    while x != 1:
        x = x * a % m
        k += 1
    return k


def mu(n, p):
    return sorted(u for u in range(1, p) if pow(u, n, p) == 1)


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def log2_table(p):
    """discrete log base 2 on <2> (dict); only for elements of <2>."""
    d, x = {}, 1
    for k in range(ordmod(2, p)):
        d[x] = k
        x = 2 * x % p
    return d


# ------------------------------------------------------------------ group ring Z[Z/p]
def W_exps(al, be, p, mu6=None):
    mu6 = mu6 or mu(6, p)
    return [(u * al + e * be * pow(u, -1, p)) % p for u in mu6 for e in (1, -1)]


def conv(a, b, p):
    """cyclic convolution of integer vectors of length p."""
    out = np.zeros(p, dtype=np.int64)
    for i in np.nonzero(a)[0]:
        out += a[i] * np.roll(b, i)
    return out


def vec(exps, p):
    v = np.zeros(p, dtype=np.int64)
    for e in exps:
        v[e % p] += 1
    return v


def NW_groupring(al, be, p, sig_mult):
    """char-0 group-ring element prod_{c in <sig_mult>} W(c al, c be) as integer vector (exact),
    where sig_mult is the multiplier of the Frobenius power generating Gal(K/k) on indices."""
    orbit = []
    c = 1
    while True:
        orbit.append(c)
        c = c * sig_mult % p
        if c == 1:
            break
    v = None
    for c in orbit:
        w = vec(W_exps(c * al % p, c * be % p, p), p)
        v = w if v is None else conv(v, w, p)
    return v, orbit


# ------------------------------------------------------------------ GF(2^n)
class GF2n:
    """GF(2^n) = F2[x]/(P), P irreducible found by deterministic search (low-weight first)."""

    def __init__(self, n, seed=0):
        self.n = n
        self.order = (1 << n) - 1
        self.P = self._find_irreducible(n)

    @staticmethod
    def _pmulmod(a, b, P, n):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> n & 1:
                a ^= P
        return r

    def _is_irreducible(self, P, n):
        # Rabin test: x^(2^n) = x mod P and gcd(x^(2^(n/q)) - x, P) = 1 for prime q | n
        def powx2k(k):
            r = 2  # x
            for _ in range(k):
                r = self._pmulmod(r, r, P, n)
            return r

        if powx2k(n) != 2:
            return False
        for q in sympy_primefactors(n):
            h = powx2k(n // q) ^ 2
            if poly_gcd(h, P) != 1:
                return False
        return True

    def _find_irreducible(self, n):
        # trinomials, then pentanomials
        for k in range(1, n):
            P = (1 << n) | (1 << k) | 1
            if self._is_irreducible(P, n):
                return P
        for a, b, c in itertools.combinations(range(1, n), 3):
            P = (1 << n) | (1 << c) | (1 << b) | (1 << a) | 1
            if self._is_irreducible(P, n):
                return P
        raise RuntimeError

    def mul(self, a, b):
        return self._pmulmod(a, b, self.P, self.n)

    def pow(self, a, e):
        e %= self.order
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a):
        assert a
        return self.pow(a, self.order - 1)

    def frob(self, a, k):
        for _ in range(k % self.n):
            a = self.mul(a, a)
        return a

    @functools.cache
    def element_of_order(self, q):
        """an element of exact order q (q | 2^n - 1), deterministic."""
        assert self.order % q == 0
        qf = sympy_primefactors(q)
        for g in range(2, 1 << min(self.n, 20)):
            z = self.pow(g, self.order // q)
            if all(self.pow(z, q // r) != 1 for r in qf):
                return z
        raise RuntimeError


def poly_gcd(a, b):
    while b:
        while a and a.bit_length() >= b.bit_length():
            a ^= b << (a.bit_length() - b.bit_length())
        a, b = b, a
    return a


def sympy_primefactors(n):
    out, q = [], 2
    while q * q <= n:
        if n % q == 0:
            out.append(q)
            while n % q == 0:
                n //= q
        q += 1
    if n > 1:
        out.append(n)
    return out


# ------------------------------------------------------------------ the setting at a prime p
class Setting:
    """zeta_p in GF(2^d), d = ord_p(2); t_j, W, eta; K = F(2^e), e = d/2; k = fixed field of the
    Frobenius power that acts on indices by an element of mu6 \\ mu2 (when one exists)."""

    def __init__(self, p):
        self.p = p
        self.d = ordmod(2, p)
        assert self.d % 2 == 0, 'need -1 in <2>'
        self.e = self.d // 2
        self.F = GF2n(self.d)
        self.zeta = self.F.element_of_order(p)
        self.zp = [1]
        for _ in range(p - 1):
            self.zp.append(self.F.mul(self.zp[-1], self.zeta))
        self.t = [self.zp[j] ^ self.zp[(-j) % p] for j in range(p)]
        self.mu6 = mu(6, p)
        self.mu3 = mu(3, p)
        self.two = log2_table(p)  # logs of <2>
        # Frobenius powers acting on indices as elements of mu6 (mod +-1: of mu3)
        self.sig_k = None
        for k in range(1, self.e):
            if pow(2, k, p) in self.mu6 and pow(2, k, p) not in (1, p - 1):
                self.sig_k = k  # sigma = Frob^k, generates Gal(K/k) of order 3
                break
        self.kdeg = self.sig_k  # [k : F2] = sig_k (then [K:k] = 3), when sig_k exists

    def W(self, al, be):
        v = 0
        for x in W_exps(al, be, self.p, self.mu6):
            v ^= self.zp[x]
        return v

    def eta(self, x):
        v = 0
        for u in self.mu6:
            v ^= self.zp[x * u % self.p]
        return v

    def norm_Kk(self, z):
        """N_{K/k}(z) = z * sigma(z) * sigma^2(z)."""
        k = self.sig_k
        a = z
        b = self.F.frob(z, k)
        c = self.F.frob(b, k)
        return self.F.mul(self.F.mul(a, b), c)

    def in_subfield(self, z, deg):
        return self.F.frob(z, deg) == z

    def three_class(self, z, q):
        """z^(|F*|/q) as an exponent of a fixed primitive q-th root (q | 2^d - 1): z is a q-th power iff 0."""
        g = self.F.element_of_order(q)
        w = self.F.pow(z, self.F.order // q)
        x = 1
        for i in range(q):
            if x == w:
                return i
            x = self.F.mul(x, g)
        raise ValueError
