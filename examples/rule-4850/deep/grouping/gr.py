"""
Group-ring arithmetic in A = F2[x, y]/(x^37 - 1, y^37 - 1), for the grouping angle on rule 4850.

Elements are 37x37 uint8 arrays a[i, j] = coefficient of x^i y^j.  Products are 2-D cyclic
convolutions mod 2 (via an integer-exact FFT: entries <= 1369 so float64 rounding is exact).

    rule_array(n)        family rule n (census.rule), as an element
    mul(a, b), power(a, e), dilate(a, n), act(a, M)   (M a 2x2 matrix mod 37: x^v -> x^(M v))
    weight(a), JJ        (JJ = sum of all monomials, the idempotent of the trivial character)
    u_of(f)              f^511 + JJ: the dilation ratio f(x^6,y^6)/f on nontrivial characters, 1 at 0
    eig(a, j, k)         a(zeta^j, zeta^k) in F(2^36) (census37's field), the independent check
    gl2()                all 1,822,176 elements of GL2(Z/37) as an (N, 4) int array
    stabiliser(a)        the elements of GL2(Z/37) fixing a (exact, by pruning on support points)
"""
from __future__ import annotations

import functools
import os
import sys

import numpy as np

M = 37
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/user/lattice-lab"
sys.path.insert(0, os.path.join(ROOT, "examples", "rule-4850"))
sys.path.insert(0, "/home/user/pilot-37c-round2/tools")

import census  # noqa: E402  (examples/rule-4850/census.py)

JJ = np.ones((M, M), dtype=np.uint8)
ONE = np.zeros((M, M), dtype=np.uint8)
ONE[0, 0] = 1


def from_points(pts) -> np.ndarray:
    a = np.zeros((M, M), dtype=np.uint8)
    for p, q in pts:
        a[p % M, q % M] ^= 1
    return a


def rule_array(n: int, radius: int = 7) -> np.ndarray:
    return from_points(census.rule(n, radius))


def mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    fa = np.fft.rfft2(a.astype(np.float64))
    fb = np.fft.rfft2(b.astype(np.float64))
    c = np.fft.irfft2(fa * fb, s=(M, M))
    return (np.rint(c).astype(np.int64) & 1).astype(np.uint8)


def dilate(a: np.ndarray, n: int) -> np.ndarray:
    """a(x^n, y^n)."""
    n %= M
    out = np.zeros_like(a)
    idx = (np.arange(M) * n) % M
    # out[n i, n j] ^= a[i, j]  (n invertible: a permutation; n = 0 collapses, use xor)
    if n == 0:
        out[0, 0] = int(a.sum()) & 1
        return out
    out[np.ix_(idx, idx)] = a
    return out


def act(a: np.ndarray, Mx) -> np.ndarray:
    """x^v -> x^(M v) for an invertible M = [[p, q], [r, s]] mod 37 (v a column vector)."""
    (p, q), (r, s) = Mx
    i, j = np.nonzero(a)
    out = np.zeros_like(a)
    out[(p * i + q * j) % M, (r * i + s * j) % M] = 1
    return out


def square(a):
    return dilate(a, 2)


def power(a: np.ndarray, e: int) -> np.ndarray:
    """a^e (e >= 0) using squaring = dilation by 2."""
    result = ONE.copy()
    base = a.copy()
    while e:
        if e & 1:
            result = mul(result, base)
        base = square(base)
        e >>= 1
    return result


def weight(a) -> int:
    return int(a.sum())


def support_idempotent(f: np.ndarray) -> np.ndarray:
    """e_f = f^(2^18 - 1) for symmetric f: 1 where lambda != 0, 0 where lambda = 0."""
    return power(f, 2**18 - 1)


def u_of(f: np.ndarray) -> np.ndarray:
    """f^511 with every component where f vanishes (at least the trivial one) set to 1:
    u = f^511 + (1 + e_f).  On the other characters u = lambda^511 = lambda(6c)/lambda(c)."""
    v = power(f, 511)
    return v ^ ONE ^ support_idempotent(f)


def unitise(a: np.ndarray, f: np.ndarray) -> np.ndarray:
    """a with its components where f vanishes set to 1 (a = f^k, k >= 1)."""
    return a ^ ONE ^ support_idempotent(f)


def inverse_nontrivial(f: np.ndarray) -> np.ndarray:
    """The inverse of a symmetric f on the nontrivial characters (values in F(2^18)), with the
    trivial component set to 1.  f^(2^18 - 2) there."""
    v = power(f, 2**18 - 2)
    if (int(f.sum()) & 1) == 0:
        v = v ^ JJ
    return v


def pts(a):
    i, j = np.nonzero(a)
    return [(int(p) if p <= 18 else int(p) - M, int(q) if q <= 18 else int(q) - M) for p, q in zip(i, j)]


# ------------------------------------------------------------------ eigenvalues (independent)

@functools.cache
def _field():
    from census37 import F  # noqa: E402  (F(2^36), zeta = F.zeta)
    return F


@functools.cache
def _zeta_pows():
    F = _field()
    return tuple(F.pow(F.zeta, e) for e in range(M))


def eig(a: np.ndarray, j: int, k: int) -> int:
    z = _zeta_pows()
    i, l = np.nonzero(a)
    v = 0
    for p, q in zip(i.tolist(), l.tolist()):
        v ^= z[(p * j + q * k) % M]
    return v


# ------------------------------------------------------------------ GL2(Z/37)

@functools.cache
def gl2() -> np.ndarray:
    r = np.arange(M)
    p, q, s, t = np.meshgrid(r, r, r, r, indexing="ij")
    g = np.stack([p.ravel(), q.ravel(), s.ravel(), t.ravel()], axis=1)
    det = (g[:, 0] * g[:, 3] - g[:, 1] * g[:, 2]) % M
    return g[det != 0].astype(np.int64)


def stabiliser(a: np.ndarray, target: np.ndarray | None = None, group: np.ndarray | None = None):
    """All g in GL2(Z/37) (or in `group`) with act(a, g) == target (default a).  Exact."""
    if target is None:
        target = a
    g = gl2() if group is None else group
    i, j = np.nonzero(a)
    if len(i) != int(target.sum()):
        return g[:0]
    tb = target.astype(bool)
    # prune: points in a fixed order, keep the matrices that send each point into the target
    order = np.argsort((i * 7 + j * 13) % 101)  # arbitrary but deterministic
    for idx in order:
        if len(g) == 0:
            break
        p, q = int(i[idx]), int(j[idx])
        x = (g[:, 0] * p + g[:, 1] * q) % M
        y = (g[:, 2] * p + g[:, 3] * q) % M
        g = g[tb[x, y]]
    return g


def affine_stabiliser(a: np.ndarray):
    """All (g, b): x^v -> x^(g v + b) mapping supp a onto itself.  Returns list of (g, b)."""
    out = []
    i, j = np.nonzero(a)
    tb = a.astype(bool)
    n = len(i)
    for b0 in range(M):
        for b1 in range(M):
            g = gl2()
            for idx in range(n):
                if len(g) == 0:
                    break
                p, q = int(i[idx]), int(j[idx])
                x = (g[:, 0] * p + g[:, 1] * q + b0) % M
                y = (g[:, 2] * p + g[:, 3] * q + b1) % M
                g = g[tb[x, y]]
            for row in g:
                out.append((tuple(int(v) for v in row), (b0, b1)))
    return out


def scalar_orbit_sums(H):
    """The orbit sums of the scalar subgroup H <= (Z/37)* acting on (Z/37)^2 \\ 0: a list of
    elements (each an orbit indicator)."""
    seen = np.zeros((M, M), dtype=bool)
    seen[0, 0] = True
    out = []
    for p in range(M):
        for q in range(M):
            if seen[p, q]:
                continue
            o = np.zeros((M, M), dtype=np.uint8)
            for h in H:
                o[h * p % M, h * q % M] = 1
                seen[h * p % M, h * q % M] = True
            out.append(o)
    return out


def subgroup(order: int):
    """The subgroup of (Z/37)* of the given order (2 is a primitive root)."""
    g = pow(2, 36 // order, M)
    return sorted({pow(g, e, M) for e in range(order)})


def invariant_under(a, n) -> bool:
    return bool(np.array_equal(dilate(a, n), a))
