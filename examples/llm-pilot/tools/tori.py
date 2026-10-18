"""
Tori as the Lean library models them, and two numeric checks.

A torus is a finite abelian group G = Z/a x Z/b with a map omega from the lattice's translations
Z^2 to it (LatticeProofs.GroupRing). A rule with neighbourhood D makes every cell v the sum mod 2
of the cells v + omega(d) (`gstep`).

    square(n)        Z/n x Z/n,      omega(p, q) = (p mod n, q mod n)            (offsetHom n)
    hexagon(n)       Z/2n x Z/(n/2), omega(q, r) = (q + 2r mod 2n, r mod n/2)    (hexHom n)
    torus(a, b, f)   Z/a x Z/b with omega(d) = f(d) reduced mod (a, b)

    H1               the hexagon's parity rule B135/S135 (hexH1Offsets), axial coordinates

    period(T, D)                         the exact eventual period of D on T (small tori only)
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


def step_matrix(T: Torus, D) -> np.ndarray:
    """The rule as a 0/1 matrix acting on column vectors of cell values."""
    cells = T.cells()
    index = {c: i for i, c in enumerate(cells)}
    M = np.zeros((len(cells), len(cells)), dtype=np.int64)
    for v in cells:
        for d in D:
            M[index[v], index[T.add(v, T.image(d))]] += 1
    return M % 2


def period(T: Torus, D, limit: int = 100000) -> int:
    """The least p > 0 with M^(t + p) = M^t for some t (exact; for small tori)."""
    M = step_matrix(T, D)
    seen, P = {}, np.eye(M.shape[0], dtype=np.int64)
    for t in range(limit):
        key = np.packbits(P.astype(np.uint8)).tobytes()
        if key in seen:
            return t - seen[key]
        seen[key] = t
        P = (M @ P) % 2
    raise RuntimeError("no repeat within the limit")


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
