"""Self-contained F(2^18) arithmetic at m = 37 for the 3-adic / quadratic-character study.

Model: F(2^18) = F2[x]/(x^18 + x^9 + 1)  (Phi_27, irreducible since ord_27(2) = 18).
t_1 = zeta + 1/zeta is a root of Q37(T), where Phi_37(z) = z^18 Q37(z + 1/z); t_n = D_n(t_1)
(Dickson), t_0 = 0.  A symmetric rule's eigenvalue at the character c = (j, k) is computed from
its D4-orbits: orbit (a, b) contributes t_aj t_bk + t_bj t_ak (a > b > 0), t_aj t_ak (a = b > 0),
t_aj + t_ak (b = 0 < a), 1 (a = b = 0).

    LOG, EXP           discrete-log tables to a fixed generator G (LOG[0] = -1)
    T                  numpy array, T[n] = t_n for n in Z/37
    orbits(r), rule_orbits(n, r)
    values(orbs)       37 x 37 array of eigenvalues (as field ints) of the union of orbits
    logs(vals)         37 x 37 array of discrete logs (-1 at zero)
    LINES              the 38 projective lines: representatives (1, k), k = 0..36, and (0, 1)
    chi                Legendre symbol mod 37 as an int array (chi[0] = 0)
"""
from __future__ import annotations

import os
import functools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
M = 37
DEG = 18
MODP = (1 << 18) | (1 << 9) | 1
N = (1 << 18) - 1  # 262143 = 27 * 7 * 19 * 73


def mul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> DEG & 1:
            a ^= MODP
    return r


def pw(a: int, e: int) -> int:
    r = 1
    e %= N
    while e:
        if e & 1:
            r = mul(r, a)
        a, e = mul(a, a), e >> 1
    return r


def _gen() -> int:
    for g in range(2, 1 << 18):
        if all(pw(g, N // p) != 1 for p in (3, 7, 19, 73)):
            return g


def _tables():
    path = os.path.join(HERE, "f18_tables.npz")
    if os.path.exists(path):
        z = np.load(path)
        return int(z["g"]), z["EXP"], z["LOG"]
    g = _gen()
    EXP = np.zeros(N, dtype=np.int64)
    LOG = np.full(1 << 18, -1, dtype=np.int64)
    x = 1
    for e in range(N):
        EXP[e] = x
        LOG[x] = e
        x = mul(x, g)
    assert x == 1 and (LOG >= 0).sum() == N
    np.savez(path, g=g, EXP=EXP, LOG=LOG)
    return g, EXP, LOG


G, EXP, LOG = _tables()


def vmul(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    out = EXP[(LOG[a] + LOG[b]) % N]
    return np.where((a == 0) | (b == 0), 0, out)


def vpow(a, e):
    a = np.asarray(a)
    out = EXP[(LOG[a] * (np.asarray(e) % N)) % N]
    return np.where(a == 0, 0 if np.all(np.asarray(e) > 0) else -1, out)


def vinv(a):
    a = np.asarray(a)
    assert np.all(a != 0)
    return EXP[(-LOG[a]) % N]


# --- t_1 and the Dickson values ------------------------------------------------------------
def _poly_eval_all(coeffs):
    """evaluate the GF(2) polynomial sum_i coeffs[i] T^i at every element of F(2^18)."""
    xs = np.arange(1 << 18, dtype=np.int64)
    acc = np.zeros_like(xs)
    for c in reversed(coeffs):
        acc = vmul(acc, xs) ^ c
    return acc


def _q37():
    # D_0 = 0, D_1 = T, D_{n+1} = T D_n + D_{n-1}, as bitmask polynomials over GF(2)
    D = [0, 0b10]
    for n in range(1, 18):
        D.append((D[n] << 1) ^ D[n - 1])
    q = 1
    for n in range(1, 19):
        q ^= D[n]
    return q, D


@functools.cache
def t_values() -> np.ndarray:
    q, D = _q37()
    coeffs = [(q >> i) & 1 for i in range(q.bit_length())]
    assert len(coeffs) == 19
    ev = _poly_eval_all(coeffs)
    roots = np.flatnonzero(ev == 0)
    assert len(roots) == 18, len(roots)
    t1 = int(roots.min())  # a fixed choice; the others are its Frobenius conjugates
    T = np.zeros(M, dtype=np.int64)
    T[1] = t1
    for n in range(1, M - 1):
        # t_{n+1} = t_1 t_n + t_{n-1}
        T[n + 1] = mul(t1, int(T[n])) ^ int(T[n - 1])
    assert T[M - 1] == T[1] and all(T[n] == T[(M - n) % M] for n in range(M))
    assert all(T[2 * n % M] == mul(int(T[n]), int(T[n])) for n in range(M))
    return T


T = t_values()


def orbits(radius: int):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def rule_orbits(n: int, radius: int):
    return [o for i, o in enumerate(orbits(radius)) if n >> i & 1]


JJ, KK = np.meshgrid(np.arange(M), np.arange(M), indexing="ij")


def orbit_values(o, J=JJ, K=KK) -> np.ndarray:
    a, b = o
    if a == 0 and b == 0:
        return np.ones_like(J)
    if b == 0:
        return T[a * J % M] ^ T[a * K % M]
    if a == b:
        return vmul(T[a * J % M], T[a * K % M])
    return vmul(T[a * J % M], T[b * K % M]) ^ vmul(T[b * J % M], T[a * K % M])


def values(orbs, J=JJ, K=KK) -> np.ndarray:
    v = np.zeros_like(J)
    for o in orbs:
        v = v ^ orbit_values(o, J, K)
    return v


def rule_values(n: int, radius: int) -> np.ndarray:
    return values(rule_orbits(n, radius))


def logs(vals) -> np.ndarray:
    return LOG[np.asarray(vals)]


# --- characters and lines -------------------------------------------------------------------
def legendre(n: int) -> int:
    n %= M
    if n == 0:
        return 0
    return 1 if pow(n, (M - 1) // 2, M) == 1 else -1


chi = np.array([legendre(n) for n in range(M)], dtype=np.int64)
LINES = [(1, k) for k in range(M)] + [(0, 1)]
LOG2 = {pow(2, i, M): i for i in range(36)}  # discrete log base 2 mod 37


def line_of(j: int, k: int):
    """(line index, u) with (j, k) = u * LINES[index], for (j, k) != 0."""
    j %= M
    k %= M
    if j == 0:
        return M, k
    return (k * pow(j, -1, M)) % M, j


# the census classes: representatives in census order and class of each line
CENSUS_REPS = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]


def line_class() -> list[int]:
    """for each of the 38 lines its census class index (0..10)."""
    out = []
    for L in LINES:
        j, k = L
        found = None
        for ci, (rj, rk) in enumerate(CENSUS_REPS):
            # the class of (rj, rk): D4 images (+-rj, +-rk), (+-rk, +-rj), up to scaling
            for p, q in ((rj, rk), (rk, rj)):
                for sp in (1, -1):
                    for sq in (1, -1):
                        if (j * sq * q - k * sp * p) % M == 0:
                            found = ci
        assert found is not None
        out.append(found)
    return out


LINE_CLASS = line_class()


def line_vector(arr) -> np.ndarray:
    """the values of a 37 x 37 array at the 38 line representatives."""
    return np.array([arr[j, k] for j, k in LINES])
