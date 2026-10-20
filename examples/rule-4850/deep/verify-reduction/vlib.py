"""Independent verification library (verify-reduction).  Written from scratch; imports nothing from the
investigators' directories.

Field:  E = F(2^36) = F2[z]/(Phi37(z)), Phi37 = 1 + z + ... + z^36 (irreducible over F2 since ord_37(2) = 36;
        checked by Rabin's test below).  zeta = z (the class of z) is a primitive 37th root of unity.
        K = F(2^18) = fixed field of Frob^18 inside E.
3-adic residue of lambda in K*: R(lambda) = lambda^9709 in mu27 (9709 = (2^18 - 1)/27), with log_omega in Z/27
        for a fixed primitive 27th root omega in K.
Group ring: F2[(Z/37)^2] as 37x37 uint8 arrays, A[p, q] = coefficient of x^p y^q.
"""
from __future__ import annotations

import functools
import math

import numpy as np

M = 37
DEG = 36
MOD = (1 << 37) - 1          # Phi37 as a bit mask (degree 36, all coefficients 1)
NE = (1 << 36) - 1           # |E*|
NK = (1 << 18) - 1           # |K*| = 262143 = 27 * 7 * 19 * 73
E27 = NK // 27               # 9709


# ----------------------------------------------------------------------------- polynomial arithmetic over F2
def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


# ----------------------------------------------------------------------------- E arithmetic
def mul(a: int, b: int) -> int:
    return pmod(clmul(a, b), MOD)


def power(a: int, e: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def inv(a: int) -> int:
    assert a
    return power(a, NE - 1)


def frob(a: int, k: int) -> int:
    for _ in range(k % 36):
        a = mul(a, a)
    return a


def rabin_irreducible() -> bool:
    """Rabin: f of degree n=36 irreducible iff z^(2^36) = z mod f and gcd(z^(2^(36/p)) - z, f) = 1, p in {2, 3}."""
    z = 2
    def zpow2k(k):
        a = z
        for _ in range(k):
            a = mul(a, a)
        return a
    if zpow2k(36) != z:
        return False
    for p in (2, 3):
        if pgcd(MOD, zpow2k(36 // p) ^ z) != 1:
            return False
    return True


ZETA = [power(2, n) for n in range(M)]       # zeta^n, zeta = z


def zeta(n: int) -> int:
    return ZETA[n % M]


def t(j: int) -> int:
    """rule-90 value t_j = zeta^j + zeta^-j."""
    return ZETA[j % M] ^ ZETA[(-j) % M]


def in_K(a: int) -> bool:
    return frob(a, 18) == a


@functools.cache
def omega() -> int:
    """a fixed primitive 27th root of unity in K: (some element)^9709 of order exactly 27."""
    for c in range(3, 1 << 20):
        # element of K: take an element of E and push it into K via the norm E -> K: a^(2^18 + 1)
        a = power(c, (1 << 18) + 1)
        if a == 0:
            continue
        w = power(a, E27)
        if power(w, 9) != 1:
            assert power(w, 27) == 1
            return w
    raise RuntimeError


@functools.cache
def mu27_log() -> dict:
    w = omega()
    d, x = {}, 1
    for i in range(27):
        d[x] = i
        x = mul(x, w)
    assert x == 1 and len(d) == 27
    return d


def res(lam: int) -> int:
    """log_omega of lambda^9709 in Z/27, or -1 for lambda = 0.  lambda must lie in K."""
    if lam == 0:
        return -1
    return mu27_log()[power(lam, E27)]


def order(a: int, N: int = NK) -> int:
    o = N
    for p in (3, 7, 19, 73) if N == NK else ():
        while o % p == 0 and power(a, o // p) == 1:
            o //= p
    return o


def legendre(j: int) -> int:
    j %= M
    if j == 0:
        return 0
    return 1 if pow(j, 18, M) == 1 else -1


IND = {pow(2, i, M): i for i in range(36)}   # discrete log base 2 mod 37


# ----------------------------------------------------------------------------- rules (Laurent supports)
def orbits(radius: int):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def d4(p: int, q: int):
    return {(sp * x, sq * y) for x, y in ((p, q), (q, p)) for sp in (1, -1) for sq in (1, -1)}


def rule(n: int, radius: int) -> frozenset:
    out = set()
    for i, o in enumerate(orbits(radius)):
        if n >> i & 1:
            out ^= d4(*o)
    return frozenset(out)


def lmul(A, B) -> frozenset:
    """exact Laurent product over F2 of two supports."""
    out = {}
    for p, q in A:
        for r, s in B:
            k = (p + r, q + s)
            out[k] = out.get(k, 0) ^ 1
    return frozenset(k for k, v in out.items() if v)


def eig(supp, j: int, k: int) -> int:
    v = 0
    for p, q in supp:
        v ^= ZETA[(p * j + q * k) % M]
    return v


def eig_all(supp) -> dict:
    return {(j, k): eig(supp, j, k) for j in range(M) for k in range(M)}


# ----------------------------------------------------------------------------- group ring F2[(Z/37)^2]
def gr(supp) -> np.ndarray:
    A = np.zeros((M, M), dtype=np.uint8)
    for p, q in supp:
        A[p % M, q % M] ^= 1
    return A


def grmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    out = np.zeros((M, M), dtype=np.uint8)
    for p, q in zip(*np.nonzero(A)):
        out ^= np.roll(np.roll(B, p, axis=0), q, axis=1)
    return out


def grdil(A: np.ndarray, s: int, u: int | None = None) -> np.ndarray:
    """A(x^s, y^u): support (p, q) -> (s p, u q)."""
    u = s if u is None else u
    out = np.zeros((M, M), dtype=np.uint8)
    for p, q in zip(*np.nonzero(A)):
        out[s * p % M, u * q % M] ^= 1
    return out


def grpow(A: np.ndarray, e: int) -> np.ndarray:
    """A^e, using A^2 = A(x^2, y^2) in characteristic 2."""
    r = np.zeros((M, M), dtype=np.uint8); r[0, 0] = 1
    sq = A.copy()
    while e:
        if e & 1:
            r = grmul(r, sq)
        sq = grdil(sq, 2)
        e >>= 1
    return r


# one-variable group ring F2[Z/37] as length-37 uint8 vectors
def g1(exps) -> np.ndarray:
    v = np.zeros(M, dtype=np.uint8)
    for n in exps:
        v[n % M] ^= 1
    return v


def g1mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.zeros(M, dtype=np.uint8)
    for p in np.nonzero(a)[0]:
        out ^= np.roll(b, p)
    return out


def g1dil(a: np.ndarray, s: int) -> np.ndarray:
    out = np.zeros(M, dtype=np.uint8)
    for p in np.nonzero(a)[0]:
        out[s * p % M] ^= 1
    return out


def g1pow(a: np.ndarray, e: int) -> np.ndarray:
    r = g1([0])
    sq = a.copy()
    while e:
        if e & 1:
            r = g1mul(r, sq)
        sq = g1dil(sq, 2)
        e >>= 1
    return r


def g1eval(a: np.ndarray, j: int = 1) -> int:
    v = 0
    for n in np.nonzero(a)[0]:
        v ^= ZETA[(int(n) * j) % M]
    return v


MU3 = sorted(u for u in range(1, M) if pow(u, 3, M) == 1)
MU6 = sorted(u for u in range(1, M) if pow(u, 6, M) == 1)
MU12 = sorted(u for u in range(1, M) if pow(u, 12, M) == 1)
