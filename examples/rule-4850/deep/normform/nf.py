"""Library for the norm-form study of rule 4850 at m = 37 (and other m).

Models
  K  = F(2^18) = F2[y]/(y^18 + y^9 + 1),   y = zeta27        (ints < 2^18)
  L  = F(2^54) = F2[x]/(x^54 + x^27 + 1),  x = zeta81        (ints < 2^54)
  K embeds in L by y -> x^3 (spread bit i to bit 3i), since Phi81(x) = Phi27(x^3).

3-adic classes (canonical, generator-free):
  v27(z) for z in K*: z^((2^18-1)/27) = y^v27     (z is a ninth power iff v27 = 0 mod 9)
  v81(z) for z in L*: z^((2^54-1)/81) = x^v81     (and v81(z) = 3 v27(z) for z in K*)
  For z in L*, N_{L/K}(z) has v27 = v81(z) mod 27: a norm is a ninth power iff its argument is.

t_j = zeta37^j + zeta37^-j: the roots of Q37 (min poly of zeta37 + 1/zeta37) in K, with
t_{2^e} = t_1^(2^e) and t_0 = 0.  Values of a symmetric rule at character (j, k) are
F(t_j, t_k) with F the rule in a = x + 1/x, b = y + 1/y; or directly sums of orbit values.
"""
from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

DEG = 18
MODK = (1 << 18) | (1 << 9) | 1
NK = (1 << 18) - 1
MODL = (1 << 54) | (1 << 27) | 1
NL = (1 << 54) - 1
M = 37


# ---------------------------------------------------------------- scalar arithmetic in K
def kmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 18 & 1:
            a ^= MODK
    return r


def kpow(a: int, e: int) -> int:
    r = 1
    e %= NK
    while e:
        if e & 1:
            r = kmul(r, a)
        a, e = kmul(a, a), e >> 1
    return r


# ---------------------------------------------------------------- scalar arithmetic in L
def lmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 54 & 1:
            a ^= MODL
    return r


def lpow(a: int, e: int) -> int:
    r = 1
    e %= NL
    while e:
        if e & 1:
            r = lmul(r, a)
        a, e = lmul(a, a), e >> 1
    return r


def linv(a: int) -> int:
    return lpow(a, NL - 1)


def embed(a: int) -> int:
    """K -> L, y -> x^3."""
    r = 0
    i = 0
    while a:
        if a & 1:
            r |= 1 << (3 * i)
        a >>= 1
        i += 1
    return r


def in_K(z: int) -> bool:
    return lpow(z, 1 << 18) == z


def unembed(z: int) -> int:
    assert z & ~sum(1 << (3 * i) for i in range(18)) == 0, 'not in the image of K'
    r = 0
    for i in range(18):
        if z >> (3 * i) & 1:
            r |= 1 << i
    return r


@functools.cache
def _xpow81():
    d = {}
    v = 1
    for i in range(81):
        d[v] = i
        v = lmul(v, 2)
    return d


def v81(z: int) -> int:
    assert z
    return _xpow81()[lpow(z, NL // 81)]


# ---------------------------------------------------------------- tables for K
@functools.cache
def gen() -> int:
    for g in range(2, 1 << 18):
        if all(kpow(g, NK // p) != 1 for p in (3, 7, 19, 73)):
            return g


@functools.cache
def tables():
    g = gen()
    EXP = np.zeros(2 * NK + 2, dtype=np.int64)
    LOG = np.full(1 << 18, -1, dtype=np.int64)
    x = 1
    for e in range(NK):
        EXP[e] = x
        LOG[x] = e
        x = kmul(x, g)
    assert x == 1
    EXP[NK:2 * NK] = EXP[:NK]
    return EXP, LOG


@functools.cache
def V27():
    """v27 of every element of K (index = element), -1 for zero."""
    EXP, LOG = tables()
    # y = zeta27 = element 2; y^((NK)/27)... v27(z) = log(z) * c mod 27 where log(y) = ly,
    # y^(NK/27) = y^9709 -> need z^(NK/27) = y^v: log(z)*NK/27 = v*ly mod NK
    # i.e. log(z) = v * ly * 27 / ... simpler: brute-force map g^(NK/27) -> exponent of y
    g27 = kpow(gen(), NK // 27)  # a primitive 27th root
    y = 2
    # g27 = y^s
    s = next(s for s in range(27) if kpow(y, s) == g27)
    # z^(NK/27) = g27^(log z mod 27) = y^(s * log z mod 27)
    v = (LOG % 27) * s % 27
    v[0] = -1
    return v.astype(np.int64)


def v27(z: int) -> int:
    return int(V27()[z])


def vmul(a, b):
    EXP, LOG = tables()
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    out = EXP[(LOG[a] + LOG[b]) % NK]
    return np.where((a == 0) | (b == 0), 0, out)


def vpow(a, e):
    EXP, LOG = tables()
    a = np.asarray(a, dtype=np.int64)
    out = EXP[(LOG[a] * (int(e) % NK)) % NK]
    if e == 0:
        return np.ones_like(a)
    return np.where(a == 0, 0, out)


def vinv(a):
    return vpow(a, NK - 1)


def kinv(a: int) -> int:
    return kpow(a, NK - 1)


# ---------------------------------------------------------------- t_j
def _pmul2(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


@functools.cache
def Q37() -> int:
    D = [0, 0b10]
    for n in range(1, 18):
        D.append(_pmul2(0b10, D[n]) ^ D[n - 1])
    q = 1
    for n in range(1, 19):
        q ^= D[n]
    return q


def _peval(mask, a):
    r = 0
    for i in range(mask.bit_length() - 1, -1, -1):
        r = kmul(r, a)
        if mask >> i & 1:
            r ^= 1
    return r


def ind37(j: int) -> int:
    j %= 37
    x = 1
    for e in range(36):
        if x == j:
            return e
        x = 2 * x % 37
    raise ValueError(j)


@functools.cache
def t1() -> int:
    # find one root of Q37: search the elements with order dividing 2^18-1 ... brute force by
    # testing the Frobenius-orbit of a root of the cyclotomic structure; use the vectorised eval.
    q = Q37()
    A = np.arange(1 << 18, dtype=np.int64)
    r = np.zeros_like(A)
    for i in range(q.bit_length() - 1, -1, -1):
        r = vmul(r, A)
        if q >> i & 1:
            r ^= 1
    roots = sorted(int(a) for a in np.nonzero(r == 0)[0])
    assert len(roots) == 18
    return roots[0]


@functools.cache
def tvec():
    out = [0] * 37
    for j in range(1, 37):
        out[j] = kpow(t1(), 1 << ind37(j))
    T = tuple(out)
    # sanity: t_{j+k} + t_{j-k} = t_j t_k
    for j in range(37):
        for k in range(37):
            assert T[(j + k) % 37] ^ T[(j - k) % 37] == kmul(T[j], T[k])
    return T


def legendre(j: int, p: int = 37) -> int:
    j %= p
    if j == 0:
        return 0
    return 1 if pow(j, (p - 1) // 2, p) == 1 else -1


# ---------------------------------------------------------------- rules
def orbits(radius):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def rule_orbits(n, radius):
    return [o for i, o in enumerate(orbits(radius)) if n >> i & 1]


def orbit_value(o, j, k, T=None):
    T = T or tvec()
    a, b = o
    if a == 0 and b == 0:
        return 1
    if b == 0:
        return T[a * j % 37] ^ T[a * k % 37]
    if a == b:
        return kmul(T[a * j % 37], T[a * k % 37])
    return kmul(T[a * j % 37], T[b * k % 37]) ^ kmul(T[b * j % 37], T[a * k % 37])


def rule_value(n, radius, j, k):
    v = 0
    for o in rule_orbits(n, radius):
        v ^= orbit_value(o, j, k)
    return v


@functools.cache
def grid():
    """J, K index arrays over all (j, k) in (Z/37)^2, flattened (1369)."""
    J, Kk = np.meshgrid(np.arange(37), np.arange(37), indexing='ij')
    return J.ravel(), Kk.ravel()


def vt(idx):
    T = np.array(tvec(), dtype=np.int64)
    return T[np.asarray(idx) % 37]


def vorbit(o):
    J, Kk = grid()
    a, b = o
    if a == 0 and b == 0:
        return np.ones(J.shape, dtype=np.int64)
    if b == 0:
        return vt(a * J) ^ vt(a * Kk)
    if a == b:
        return vmul(vt(a * J), vt(a * Kk))
    return vmul(vt(a * J), vt(b * Kk)) ^ vmul(vt(b * J), vt(a * Kk))


def vrule(n, radius):
    J, _ = grid()
    v = np.zeros(J.shape, dtype=np.int64)
    for o in rule_orbits(n, radius):
        v ^= vorbit(o)
    return v


CLASSES = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]


def cls_index(j, k):
    return (j % 37) * 37 + (k % 37)


def class_v27(vals):
    """v27 at the 11 census classes of a 1369-vector of values."""
    return [int(V27()[vals[cls_index(j, k)]]) for j, k in CLASSES]


def is_ninth_confined(vals):
    v = V27()[vals]
    J, Kk = grid()
    nz = ~((J == 0) & (Kk == 0))
    vv = v[nz]
    return bool(np.all((vv < 0) | (vv % 9 == 0)))
