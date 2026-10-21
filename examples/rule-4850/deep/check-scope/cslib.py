"""check-scope: an independent field model for the scope/soundness check of the 'norms' proof.

Own construction (shares no code with nlib, famlib, census, f18):
  * GF(2^n) = F2[x]/(P) with P a *dense random* irreducible polynomial (seeded), tested by Rabin's test
    with our own F2[x] gcd / modular powering;
  * zeta_m = h^((2^n - 1)/m) for a seeded random h, accepted when it has exact order m;
  * Gauss periods, W, t, norms written from the definitions in the task text.
Hexagon rules are built from the definition Hex_{p,q} = {+-(2p,0), +-(p,+-q)}, G = Hex + Hex^T, and their
eigenvalues off s = 0 are computed as G(c)/s(c); on s = 0 from an explicit exact quotient polynomial
(our own long division in F2[x, y] with Laurent shift)."""
from __future__ import annotations

import math
import random


# ----------------------------------------------------------------------------- F2[x] on ints
def clmul(a: int, b: int) -> int:
    if a.bit_length() < b.bit_length():
        a, b = b, a
    r = 0
    while b:
        lo = b & -b
        r ^= a << (lo.bit_length() - 1)
        b ^= lo
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def ppowmod(a: int, e: int, m: int) -> int:
    r = 1
    a = pmod(a, m)
    while e:
        if e & 1:
            r = pmod(clmul(r, a), m)
        a = pmod(clmul(a, a), m)
        e >>= 1
    return r


def primefactors(n: int) -> list[int]:
    out, q = [], 2
    while q * q <= n:
        if n % q == 0:
            out.append(q)
            while n % q == 0:
                n //= q
        q += 1 if q == 2 else 2
    if n > 1:
        out.append(n)
    return out


def rabin_irreducible(P: int) -> bool:
    n = P.bit_length() - 1
    x = 2

    def x2k(k):
        r = x
        for _ in range(k):
            r = pmod(clmul(r, r), P)
        return r

    if x2k(n) != x:
        return False
    for q in primefactors(n):
        if pgcd(x2k(n // q) ^ x, P) != 1:
            return False
    return True


def ordmod(a: int, m: int) -> int:
    if math.gcd(a, m) != 1:
        return 0
    x, k = a % m, 1
    while x != 1:
        x = x * a % m
        k += 1
    return k


# ----------------------------------------------------------------------------- the field
class Field:
    def __init__(self, n: int, seed: int = 20261021):
        self.n = n
        self.N = (1 << n) - 1
        rng = random.Random(seed * 1000 + n)
        while True:
            P = (1 << n) | rng.getrandbits(n) | 1
            if bin(P).count('1') < n // 3:      # insist on a dense modulus (unlike the others' trinomials)
                continue
            if rabin_irreducible(P):
                break
        self.P = P
        self.rng = rng
        # reduction table for 8-bit chunks above degree n
        self.top = n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.P) if a and b else 0

    def sq(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        if a == 0:
            return 0 if e else 1
        e %= self.N
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        assert a
        return self.pow(a, self.N - 1)

    def frob(self, a: int, k: int) -> int:
        for _ in range(k % self.n):
            a = self.mul(a, a)
        return a

    def in_sub(self, a: int, g: int) -> bool:
        return self.frob(a, g) == a

    def order(self, a: int) -> int:
        o = self.N
        for q in primefactors(self.N):
            while o % q == 0 and self.pow(a, o // q) == 1:
                o //= q
        return o

    def root_of_unity(self, m: int) -> int:
        assert self.N % m == 0
        qs = primefactors(m)
        while True:
            h = self.rng.getrandbits(self.n) or 1
            z = self.pow(h, self.N // m)
            if all(self.pow(z, m // q) != 1 for q in qs):
                return z

    def level3(self, a: int, g: int | None = None) -> int:
        """largest k with a a 3^k-th power in F(2^g)* (g = self.n by default); a must lie in F(2^g)."""
        g = g or self.n
        Ng = (1 << g) - 1
        A = 0
        while Ng % 3 ** (A + 1) == 0:
            A += 1
        # a is a 3^k-th power in F(2^g)* iff a^(Ng / 3^k) = 1  (for 3^k | Ng)
        k = 0
        while k < A and self.pow(a, Ng // 3 ** (k + 1)) == 1:
            k += 1
        return k


# ----------------------------------------------------------------------------- the setting at a size m
class Setting:
    """zeta of order m in GF(2^d), d = ord_m(2); requires -1 in <2>, 2e = d, 3 | e, and
    -2^(e/3) = w a primitive cube root of 1 mod m."""

    def __init__(self, m: int, seed: int = 7):
        self.m = m
        self.d = ordmod(2, m)
        assert self.d % 2 == 0 and pow(2, self.d // 2, m) == m - 1, '-1 not in <2>'
        self.e = self.d // 2
        assert self.e % 3 == 0
        self.f = self.e // 3
        self.w = (-pow(2, self.f, m)) % m
        assert (self.w * self.w + self.w + 1) % m == 0, 'Frob^f is not -(primitive cube root)'
        self.F = Field(self.d, seed)
        self.zeta = self.F.root_of_unity(m)
        self.zp = [1]
        for _ in range(m - 1):
            self.zp.append(self.F.mul(self.zp[-1], self.zeta))
        w = self.w
        self.mu6 = sorted({s * pow(w, i, m) % m for s in (1, m - 1) for i in range(3)})
        self.mu3 = sorted({pow(w, i, m) for i in range(3)})
        self.t = [self.zp[j] ^ self.zp[(-j) % m] for j in range(m)]
        self._eta = {}

    def eta(self, x: int) -> int:
        x %= self.m
        if x not in self._eta:
            v = 0
            for u in self.mu6:
                v ^= self.zp[x * u % self.m]
            self._eta[x] = v
        return self._eta[x]

    def W(self, al: int, be: int) -> int:
        """sum_{u in mu3} t_{u al} t_{be/u}."""
        m = self.m
        v = 0
        for u in self.mu3:
            v ^= self.F.mul(self.t[u * al % m], self.t[be * pow(u, -1, m) % m])
        return v

    def W_def(self, al: int, be: int) -> int:
        """sum_{u in mu6, e = +-1} zeta^(al u + e be / u)  (the definition)."""
        m = self.m
        v = 0
        for u in self.mu6:
            ui = pow(u, -1, m)
            for s in (1, -1):
                v ^= self.zp[(al * u + s * be * ui) % m]
        return v

    def norm(self, z: int) -> int:
        """N_{K/k}, K = F(2^e), k = F(2^f): z sigma(z) sigma^2(z), sigma = Frob^f."""
        F = self.F
        a = F.frob(z, self.f)
        b = F.frob(a, self.f)
        return F.mul(F.mul(z, a), b)

    def star(self, al: int, be: int) -> int:
        """formula (*) of the norms investigator, written from the task text."""
        F, m, w = self.F, self.m, self.w
        mul = F.mul
        X, Y = self.eta(al), self.eta(be)
        Xa, Ya = self.eta((1 - w) * al), self.eta((1 - w) * be)
        Xb, Yb = self.eta((2 - w) * al), self.eta((2 - w) * be)
        Xc, Yc = self.eta((2 - w * w) * al), self.eta((2 - w * w) * be)
        XY = mul(X, Y)
        v = mul(mul(XY, XY), 1 ^ X ^ Y)
        v ^= mul(XY, mul(X, Ya) ^ mul(Xa, Y))
        v ^= mul(XY, mul(Xa, Ya))
        v ^= mul(mul(Xa, Ya), X ^ Y)
        v ^= mul(Xb, Yb) ^ mul(Xc, Yc)
        return v


# ----------------------------------------------------------------------------- hexagon rules
def hex_G(p: int, q: int) -> set:
    H = {(2 * p, 0), (-2 * p, 0), (p, q), (-p, -q), (p, -q), (-p, q)}
    T = {(b, a) for a, b in H}
    return H ^ T


def divide_by_s(G: set) -> frozenset:
    """exact quotient G / s, s = x + 1/x + y + 1/y, in F2[x^+-1, y^+-1]; asserts exactness.
    Work with s' = x y s = x^2 y + y + x y^2 + x  =  (x + y)(1 + x y)."""
    R = max(max(abs(a), abs(b)) for a, b in G) + 2
    # polynomial as dict: x-exponent -> int bitmask of y-exponents, shifted by R
    P = {}
    for a, b in G:
        P[a + R] = P.get(a + R, 0) ^ (1 << (b + R))
    # divide by (y + x): treat as polynomial in x with coefficients in F2[y]; (x + y) monic in x
    Q1 = {}
    for n in range(max(P), 0, -1):
        c = P.get(n, 0)
        if c:
            Q1[n - 1] = Q1.get(n - 1, 0) ^ c
            P[n] = 0
            P[n - 1] = P.get(n - 1, 0) ^ (c << 1)     # c x^n = c x^(n-1) (x + y) + c y x^(n-1)
    assert P.get(0, 0) == 0, 'not divisible by x + y'
    # divide Q1 by (1 + x y), from low x-degree up
    P = dict(Q1)
    Q2 = {}
    top = max(P)
    for n in range(0, top + 1):
        c = P.get(n, 0)
        if c:
            Q2[n] = Q2.get(n, 0) ^ c
            P[n] = 0
            P[n + 1] = P.get(n + 1, 0) ^ (c << 1)
    assert all(v == 0 for v in P.values()), 'not divisible by 1 + x y'
    # G/s = x y * Q2 / (shift): G shifted by (R, R) = s' * Q2 * ... ; s = s'/(x y)
    out = set()
    for i, bits in Q2.items():
        j = 0
        while bits:
            if bits & 1:
                out.add((i - R + 1, j - R + 1))
            bits >>= 1
            j += 1
    return frozenset(out)


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1
