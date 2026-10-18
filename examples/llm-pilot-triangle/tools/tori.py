"""
Tori as the Lean library models them, and numeric checks.

A torus is a finite abelian group G = Z/a x Z/b with a map omega from the lattice's translations
Z^2 to it (LatticeProofs.GroupRing). A plane rule with neighbourhood D makes every cell v the sum
mod 2 of the cells v + omega(d) (`gstep`). A triangle rule (`TriRule`) has two layers of cells
over G, up and down, and four neighbourhoods (uu, ud, du, dd): an up cell reads uu among up cells
and ud among down cells, a down cell reads du among up cells and dd among down cells
(`gtriStep`).

    square(n)        Z/n x Z/n,      omega(p, q) = (p mod n, q mod n)            (offsetHom n)
    hexagon(n)       Z/2n x Z/(n/2), omega(q, r) = (q + 2r mod 2n, r mod n/2)    (hexHom n)
    triangle(n)      Z/n x Z/(n/2),  omega(x, y) = (x - y mod n, y mod n/2)      (triHom n)
    torus(a, b, f)   Z/a x Z/b with omega(d) = f(d) reduced mod (a, b)

    H1               the hexagon's parity rule B135/S135 (hexH1Offsets)
    TRI_E            the triangle edge rule B13/S13 (triE), as a TriRule
    TRI_EVOVS        the triangle edge+vertex rule B1,3,...,11/S1,3,...,11 (triEVOVS)
    S_E, S_EVOVS     the plane rules their squares reduce to (triSEOffsets, triSEVOVSOffsets)

    period(T, D)                the exact eventual period of the plane rule D on T (small tori)
    tri_period(T, R)            the exact eventual period of the triangle rule R over T
                                (gtriPeriod; small tori)
    check_jordan(T, D, psi1, psi2, lam, mu, F)
        whether adj psi1 = lam psi1 and adj psi2 = lam psi2 + mu psi1 at every cell, with lam
        and mu nonzero and psi1 not identically zero. Here adj psi (w) = sum over d in D of
        psi(w - omega(d)) (LatticeProofs.TwoPart.adj), and psi1, psi2 map cells (pairs of ints,
        reduced) to elements of the gf2.Field F.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

H1 = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]


@dataclass(frozen=True)
class TriRule:
    uu: tuple
    ud: tuple
    du: tuple
    dd: tuple


TRI_E = TriRule(uu=(), ud=((-1, -1), (0, -1), (0, 0)), du=((0, 0), (0, 1), (1, 1)), dd=())
TRI_EVOVS = TriRule(
    uu=((-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)),
    ud=((-1, -2), (-1, -1), (-1, 0), (0, -1), (0, 0), (1, 0)),
    du=((-1, 0), (0, 0), (0, 1), (1, 0), (1, 1), (1, 2)),
    dd=((-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)),
)
S_E = [(-1, -1), (-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (1, 1)]
S_EVOVS = [
    (-2, -1), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (0, -1),
    (0, 1), (1, -1), (1, 0), (1, 1), (1, 2), (2, 1),
]  # fmt: skip


@dataclass(frozen=True)
class Torus:
    a: int
    b: int
    omega: Callable[[tuple[int, int]], tuple[int, int]]

    def cells(self) -> list[tuple[int, int]]:
        return [(x, y) for x in range(self.a) for y in range(self.b)]

    def add(self, u, v):
        return ((u[0] + v[0]) % self.a, (u[1] + v[1]) % self.b)

    def sub(self, u, v):
        return ((u[0] - v[0]) % self.a, (u[1] - v[1]) % self.b)

    def image(self, d):
        x, y = self.omega(d)
        return (x % self.a, y % self.b)


def torus(a: int, b: int, f) -> Torus:
    return Torus(a, b, f)


def square(n: int) -> Torus:
    return Torus(n, n, lambda d: (d[0], d[1]))


def hexagon(n: int) -> Torus:
    if n % 2:
        raise ValueError("the atlas's hexagonal torus has even side")
    return Torus(2 * n, n // 2, lambda d: (d[0] + 2 * d[1], d[1]))


def triangle(n: int) -> Torus:
    if n % 2:
        raise ValueError("the atlas's triangular torus has even side")
    return Torus(n, n // 2, lambda d: (d[0] - d[1], d[1]))


def step_matrix(T: Torus, D) -> np.ndarray:
    """The plane rule as a 0/1 matrix acting on column vectors of cell values."""
    cells = T.cells()
    index = {c: i for i, c in enumerate(cells)}
    M = np.zeros((len(cells), len(cells)), dtype=np.int64)
    for v in cells:
        for d in D:
            M[index[v], index[T.add(v, T.image(d))]] += 1
    return M % 2


def tri_step_matrix(T: Torus, R: TriRule) -> np.ndarray:
    """The triangle rule as a block matrix on (up cells, down cells)."""
    return np.block(
        [
            [step_matrix(T, R.uu), step_matrix(T, R.ud)],
            [step_matrix(T, R.du), step_matrix(T, R.dd)],
        ]
    )


def _eventual_period(M: np.ndarray, limit: int) -> int:
    seen, P = {}, np.eye(M.shape[0], dtype=np.int64)
    for t in range(limit):
        key = np.packbits(P.astype(np.uint8)).tobytes()
        if key in seen:
            return t - seen[key]
        seen[key] = t
        P = (M @ P) % 2
    raise RuntimeError("no repeat within the limit")


def period(T: Torus, D, limit: int = 100000) -> int:
    """The least p > 0 with M^(t + p) = M^t for some t (exact; for small tori)."""
    return _eventual_period(step_matrix(T, D), limit)


def tri_period(T: Torus, R: TriRule, limit: int = 100000) -> int:
    """The triangle rule's eventual period over T (exact; for small tori)."""
    return _eventual_period(tri_step_matrix(T, R), limit)


def adj(T: Torus, D, psi, F):
    return {w: F.sum(psi(T.sub(w, T.image(d))) for d in D) for w in T.cells()}


def check_jordan(T: Torus, D, psi1, psi2, lam: int, mu: int, F) -> dict:
    """Whether psi1, psi2 form a Jordan block of the rule's adjoint, with lam, mu nonzero."""
    a1, a2 = adj(T, D, psi1, F), adj(T, D, psi2, F)
    cells = T.cells()
    bad1 = [w for w in cells if a1[w] != F.mul(lam, psi1(w))]
    bad2 = [w for w in cells if a2[w] != F.add(F.mul(lam, psi2(w)), F.mul(mu, psi1(w)))]
    nonzero = any(psi1(w) != 0 for w in cells)
    ok = not bad1 and not bad2 and lam != 0 and mu != 0 and nonzero
    return {
        "ok": ok,
        "eigen_fails_at": bad1[:5],
        "block_fails_at": bad2[:5],
        "lam_nonzero": lam != 0,
        "mu_nonzero": mu != 0,
        "psi1_nonzero": nonzero,
    }
