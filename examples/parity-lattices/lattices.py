"""
Exact periods of the parity rules on LatticeLife's hexagonal and triangular tori.

Every rule here is linear over GF(2) and commutes with the torus's translations, so it lives in
the group ring F2[T] of the translation group T = Z^2 / Lambda (a finite abelian group):

- hexagon (odd-q offset columns): in axial coordinates (q, r) = (c, row - floor(c/2)) the
  neighbours are the six steps +-(1, 0), +-(0, 1), +-(1, -1), and the n x n torus is
  Z^2 / <(n, -n/2), (0, n)>. One generation multiplies by the sum of the six steps.
- triangle: up and down triangles are two copies of T = {(dr, dc) : dr + dc even} (coordinates
  u = (dr + dc)/2, v = (dc - dr)/2), and the n x n torus is T / <(n/2, -n/2), (n/2, n/2)>. One
  generation multiplies the pair (up cells, down cells) by a 2 x 2 matrix over F2[T], read off
  LatticeLife's own neighbour offsets.

Products in F2[Z^2 / Lambda] are 2D convolutions, done by FFT on a fundamental domain from the
Hermite normal form of Lambda, folded back, and checked to round exactly. The longest period of
the torus is the period of the rule's matrix M: the least p with M^(t0 + p) = M^t0 past the
transient, found by checking a candidate P and dividing out each of its primes while that still
holds. The candidate is the law under test; if M^(t0 + P) != M^t0, a bound valid for every torus
is used instead, so a wrong law is reported as wrong, with the true period where it can be found.
"""

from __future__ import annotations

import math

import numpy as np
import sympy
from latticelife.core.geometries import _triangle_offsets


class GroupRing:
    """F2[Z^2 / Lambda], elements as a x d arrays over the fundamental domain of the Hermite
    basis (a, b), (0, d) of Lambda."""

    def __init__(self, g1, g2):
        (x1, y1), (x2, y2) = g1, g2
        g, s, t = _egcd(x1, x2)
        row = (g, s * y1 + t * y2)
        d = abs((x2 // g) * y1 - (x1 // g) * y2)
        if g <= 0 or d <= 0:
            raise ValueError("Lambda must have rank 2")
        self.a, self.d = g, d
        self.b = row[1] % d

    def index(self, i: int, j: int) -> tuple[int, int]:
        k = i // self.a
        return i - k * self.a, (j - k * self.b) % self.d

    def zero(self) -> np.ndarray:
        return np.zeros((self.a, self.d))

    def monomial(self, i: int, j: int) -> np.ndarray:
        e = self.zero()
        e[self.index(i, j)] = 1
        return e

    def mul(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        a, d = self.a, self.d
        shape = (2 * a, 2 * d)
        c = np.fft.irfft2(np.fft.rfft2(x, shape) * np.fft.rfft2(y, shape), shape)
        r = np.rint(c)
        if np.max(np.abs(c - r)) >= 0.25:
            raise ArithmeticError("FFT rounding not exact")
        r = r.astype(np.int64)
        folded = r[:a] + np.roll(r[a:], -self.b, axis=1)
        out = folded[:, :d] + folded[:, d:]
        return (out & 1).astype(np.float64)


def _egcd(x: int, y: int) -> tuple[int, int, int]:
    if y == 0:
        return (abs(x), 1 if x >= 0 else -1, 0)
    g, s, t = _egcd(y, x % y)
    return g, t, s - (x // y) * t


class Matrix:
    """k x k matrices over a GroupRing (k = 1 for the hexagon, 2 for the triangle)."""

    def __init__(self, ring: GroupRing, entries):
        self.ring, self.e = ring, entries

    def __mul__(self, other: Matrix) -> Matrix:
        k = len(self.e)
        out = []
        for i in range(k):
            row = []
            for j in range(k):
                acc = self.ring.zero()
                for m in range(k):
                    acc = (acc + self.ring.mul(self.e[i][m], other.e[m][j])) % 2
                row.append(acc)
            out.append(row)
        return Matrix(self.ring, out)

    def __eq__(self, other) -> bool:
        return all(
            np.array_equal(x, y)
            for rx, ry in zip(self.e, other.e, strict=True)
            for x, y in zip(rx, ry, strict=True)
        )

    def is_zero(self) -> bool:
        return not any(x.any() for row in self.e for x in row)

    def identity(self) -> Matrix:
        k = len(self.e)
        one = self.ring.monomial(0, 0)
        return Matrix(
            self.ring, [[one if i == j else self.ring.zero() for j in range(k)] for i in range(k)]
        )

    def power(self, n: int) -> Matrix:
        result, base = self.identity(), self
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result


# --- the three rules ---------------------------------------------------------------------------

AXIAL_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))


def hexagon(n: int) -> tuple[GroupRing, Matrix]:
    ring = GroupRing((n, -(n // 2)), (0, n))
    sigma = ring.zero()
    for q, r in AXIAL_STEPS:
        sigma[ring.index(q, r)] += 1
    return ring, Matrix(ring, [[sigma % 2]])


def _tau(dr: int, dc: int) -> tuple[int, int]:
    return (dr + dc) // 2, (dc - dr) // 2


def triangle(n: int, mode: str) -> tuple[GroupRing, Matrix]:
    ring = GroupRing((n // 2, -(n // 2)), (n // 2, n // 2))
    up, down = _triangle_offsets(mode)
    uu, ud, du, dd = (ring.zero() for _ in range(4))
    # new up at g:   up neighbours at g + tau(o) (o even), down ones at g + tau(dr, dc - 1)
    # new down at g: down neighbours at g + tau(o) (o even), up ones at g + tau(dr, dc + 1);
    # in the ring, X[g + k] is the product with the monomial at -k.
    for dr, dc in up:
        if (dr + dc) % 2 == 0:
            i, j = _tau(dr, dc)
            uu[ring.index(-i, -j)] += 1
        else:
            i, j = _tau(dr, dc - 1)
            ud[ring.index(-i, -j)] += 1
    for dr, dc in down:
        if (dr + dc) % 2 == 0:
            i, j = _tau(dr, dc)
            dd[ring.index(-i, -j)] += 1
        else:
            i, j = _tau(dr, dc + 1)
            du[ring.index(-i, -j)] += 1
    return ring, Matrix(ring, [[uu % 2, ud % 2], [du % 2, dd % 2]])


def build(lattice: str, n: int) -> tuple[GroupRing, Matrix]:
    if lattice == "hexagon":
        return hexagon(n)
    if lattice == "triangle-edge":
        return triangle(n, "edge")
    if lattice == "triangle-edge+vertex":
        return triangle(n, "edge+vertex")
    raise ValueError(lattice)


# --- the laws ----------------------------------------------------------------------------------


def odd_part(n: int) -> int:
    while n % 2 == 0:
        n //= 2
    return n


def suborder(m: int) -> int:
    if m <= 3:
        return 1
    k, v = 1, 2 % m
    while v not in (1, m - 1):
        v, k = v * 2 % m, k + 1
    return k


def law(lattice: str, n: int) -> int:
    """The registered prediction: 2 * 2^v(n) * (2^sord(n) - 1), with the two small families
    seen in discovery: odd part 1 (hexagon and edge+vertex die; edge has period n) and, on the
    hexagon only, odd part 3 (period 2^v(n))."""
    two_v, odd = n // odd_part(n), odd_part(n)
    if odd == 1:
        return n if lattice == "triangle-edge" else 1
    if odd == 3 and lattice == "hexagon":
        return two_v
    return 2 * two_v * (2 ** suborder(odd) - 1)


def fallback(lattice: str, n: int) -> int:
    """A multiple of every torus's period: eigenvalues of a k x k matrix over F2[T] lie in
    F(2^(k m)), m = ord of 2 modulo the odd part of T's exponent, and the 2-part is bounded by the
    nilpotent part, at most 2^(v + 2) here."""
    exponent = 2 * n
    m = sympy.n_order(2, odd_part(exponent)) if odd_part(exponent) > 1 else 1
    k = 1 if lattice == "hexagon" else 2
    return 2 ** (int(math.log2(exponent // odd_part(exponent))) + 2) * (2 ** (k * m) - 1)


def period(lattice: str, n: int) -> dict:
    """The exact longest period and transient of the rule on the n x n torus."""
    ring, M = build(lattice, n)
    t0 = 4 * n
    late = M.power(t0)
    if late.is_zero():
        transient = next(t for t in range(t0 + 1) if M.power(t).is_zero())
        return {"period": 1, "transient": transient, "dies": True, "candidate": "zero"}

    def repeats(p: int) -> bool:
        return late * M.power(p) == late

    for label, value in (("law", law(lattice, n)), ("fallback", fallback(lattice, n))):
        if value >= 1 and repeats(value):
            p = value
            for q in sorted(sympy.factorint(value)):
                while p % q == 0 and repeats(p // q):
                    p //= q
            shift = M.power(p)
            state, transient = M.identity(), 0
            while not state * shift == state:
                state, transient = state * M, transient + 1
            return {"period": p, "transient": transient, "dies": False, "candidate": label}
    raise RuntimeError(f"{lattice} n={n}: no candidate is a multiple of the period")
