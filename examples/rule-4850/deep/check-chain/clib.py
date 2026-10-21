"""check-chain: independent tools (no imports from norms/, census, eigen, or other verifiers).

* F2[x] polynomials as Python int bitmasks.
* GF(2^36) = F2[x]/(P) with P a DENSE irreducible of degree 36 chosen by a seeded random search
  (so neither Phi_37, which census/eigen use, nor the low-weight tri/pentanomial that norms/nlib uses).
* zeta = an element of order 37 obtained as h^((2^36-1)/37) for a primitive element h.
* K = F(2^18) (fixed field of Frob^18), k = F(2^6) = F64 (fixed field of Frob^6); N = N_{K/k}(z) = z^(1+2^6+2^12).
"""
from __future__ import annotations

import random

# ------------------------------------------------------------------ F2[x]
def pmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length()
    while a and a.bit_length() >= dm:
        a ^= m << (a.bit_length() - dm)
    return a


def pdivmod(a: int, b: int):
    q = 0
    db = b.bit_length()
    while a and a.bit_length() >= db:
        s = a.bit_length() - db
        q ^= 1 << s
        a ^= b << s
    return q, a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def pmulmod(a: int, b: int, m: int) -> int:
    return pmod(pmul(a, b), m)


def ppowmod(a: int, e: int, m: int) -> int:
    r = 1
    a = pmod(a, m)
    while e:
        if e & 1:
            r = pmulmod(r, a, m)
        a = pmulmod(a, a, m)
        e >>= 1
    return r


def pstr(f: int) -> str:
    terms = []
    for i in range(f.bit_length() - 1, -1, -1):
        if f >> i & 1:
            terms.append('1' if i == 0 else ('x' if i == 1 else 'x^%d' % i))
    return ' + '.join(terms) if terms else '0'


def prime_factors(n: int) -> list[int]:
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


def is_irreducible(P: int) -> bool:
    """Rabin's test over F2."""
    n = P.bit_length() - 1
    x = 2

    def x_pow_2k(k):
        r = x
        for _ in range(k):
            r = pmulmod(r, r, P)
        return r

    if x_pow_2k(n) != x:
        return False
    for q in prime_factors(n):
        if pgcd(x_pow_2k(n // q) ^ x, P) != 1:
            return False
    return True


def irreducible_factors(f: int) -> list[int]:
    """Factor a squarefree f over F2 by trial division with irreducibles of increasing degree."""
    facs = []
    d = 1
    while f.bit_length() - 1 >= 2 * d:
        for c in range(1 << d, 1 << (d + 1)):
            if not (c & 1):
                continue
            if not is_irreducible(c):
                continue
            while pmod(f, c) == 0:
                facs.append(c)
                f = pdivmod(f, c)[0]
        d += 1
    if f != 1:
        facs.append(f)
    return facs


# ------------------------------------------------------------------ GF(2^36)
N36 = (1 << 36) - 1
N18 = (1 << 18) - 1
N6 = (1 << 6) - 1


def find_modulus(seed: int = 20261021) -> int:
    rng = random.Random(seed)
    while True:
        P = (1 << 36) | rng.getrandbits(36) | 1
        if bin(P).count('1') < 15:      # insist on a dense modulus
            continue
        if is_irreducible(P):
            return P


class GF36:
    def __init__(self, seed: int = 20261021):
        self.P = find_modulus(seed)
        assert self.P.bit_length() - 1 == 36
        # a primitive element h, and zeta = h^((2^36-1)/37)
        pf = prime_factors(N36)
        assert pf == [3, 5, 7, 13, 19, 37, 73, 109], pf
        rng = random.Random(seed + 1)
        while True:
            h = rng.getrandbits(36)
            if h and all(self.pow(h, N36 // q) != 1 for q in pf):
                break
        self.h = h
        self.zeta = self.pow(h, N36 // 37)
        assert self.zeta != 1 and self.pow(self.zeta, 37) == 1
        self.g18 = self.pow(h, N36 // N18)     # generator of F(2^18)*
        self.g6 = self.pow(h, N36 // N6)       # generator of F64*

    def mul(self, a: int, b: int) -> int:
        r = 0
        P = self.P
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> 36:
                a ^= P
        return r

    def pow(self, a: int, e: int) -> int:
        if a == 0:
            return 0 if e else 1
        e %= N36
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        assert a
        return self.pow(a, N36 - 1)

    def frob(self, a: int, k: int) -> int:
        for _ in range(k % 36):
            a = self.mul(a, a)
        return a

    def in_sub(self, a: int, deg: int) -> bool:
        return self.frob(a, deg) == a

    def norm_K_k(self, z: int) -> int:
        """N_{F(2^18)/F(2^6)}(z) = z * z^64 * z^4096 (z must lie in F(2^18))."""
        return self.mul(self.mul(z, self.frob(z, 6)), self.frob(z, 12))


# ------------------------------------------------------------------ F_37 helpers
p = 37


def mu(n: int) -> list[int]:
    return sorted(u for u in range(1, p) if pow(u, n, p) == 1)


LOG2 = {}
_x = 1
for _k in range(36):
    LOG2[_x] = _k
    _x = 2 * _x % p
assert len(LOG2) == 36


def legendre(a: int) -> int:
    a %= p
    return 0 if a == 0 else (1 if pow(a, 18, p) == 1 else -1)


RULE4850_ORBITS = [(1, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 3), (4, 2)]   # from the dossier


def orbit_points(a: int, b: int) -> set:
    return {(sp * u, sq * v) for u, v in ((a, b), (b, a)) for sp in (1, -1) for sq in (1, -1)}


def rule_points(orbs) -> set:
    s: set = set()
    for o in orbs:
        s ^= orbit_points(*o)
    return s
