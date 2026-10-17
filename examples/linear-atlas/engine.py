"""
Exact periods of linear (XOR) rules built from symmetric neighbour shells.

A rule here is a set of shells, plus optionally the cell itself: a cell's next state is the
parity of the live cells in those shells. Every such rule is linear over GF(2) and commutes with
the torus's translations, so it is multiplication by a polynomial in the group ring F2[T] of the
torus (a 2 x 2 matrix of them on the triangular lattice, whose up and down cells are two copies of
one translation group). The group rings, the hexagon's axial coordinates and the triangle's
offsets are those of examples/parity-lattices/lattices.py, which reproduced LatticeLife cell for
cell.

    square    shells N4 (the four nearest), D4 (the four diagonals), A4 (the four at distance 2)
    hexagon   shells H1 (six nearest), H2 (six at distance sqrt 3), H3 (six at distance 2)
    triangle  shells E (the three across an edge), VO (the three across a vertex, opposite
              orientation), VS (the six that share a vertex, same orientation)

LatticeLife's own parity rules are among them: the square's eight-neighbour XOR rule is N4 + D4,
the hexagon's is H1, the triangle's are E and E + VO + VS, and "+ self" adds the cell.

The period of the torus is the period of the rule's matrix M: the least p with M^(t0 + p) = M^t0,
with t0 = 4n past any transient. Every period divides a bound C = 2^(e + 2) (2^(k m) - 1), where
2^e is the 2-part of the torus group's exponent, m the order of 2 modulo its odd part and k the
matrix size, because M's eigenvalues lie in F(2^(k m)) and its nilpotent part dies within 2^e
steps (twice that for a 2 x 2 matrix). The primes of 2^(k m) - 1 come from its cyclotomic parts,
so C's primes are known without factoring C. `period` divides them out of C; `check` decides
whether a predicted period is the period, using only C's primes: a prediction that does not divide
C, does not repeat, or repeats at a proper divisor is not the period.
"""

from __future__ import annotations

import functools
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import sympy

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "parity-lattices"))

from lattices import AXIAL_STEPS, GroupRing, Matrix, _tau  # noqa: E402


def _pm(*vectors):
    return tuple(v for a, b in vectors for v in ((a, b), (-a, -b)))


SQUARE_SHELLS = {"N4": _pm((1, 0), (0, 1)), "D4": _pm((1, 1), (1, -1)), "A4": _pm((2, 0), (0, 2))}
HEXAGON_SHELLS = {
    "H1": tuple(AXIAL_STEPS),
    "H2": _pm((1, 1), (2, -1), (1, -2)),
    "H3": _pm((2, 0), (0, 2), (2, -2)),
}
# The triangle's shells, as LatticeLife's (row, column) offsets of an up cell and of a down cell.
TRIANGLE_SHELLS = {
    "E": {"up": ((0, -1), (0, 1), (1, 0)), "down": ((-1, 0), (0, -1), (0, 1))},
    "VO": {"up": ((-1, 0), (1, -2), (1, 2)), "down": ((-1, -2), (-1, 2), (1, 0))},
    "VS": {
        "up": ((-1, -1), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 1)),
        "down": ((-1, -1), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 1)),
    },
}
SHELLS = {"square": SQUARE_SHELLS, "hexagon": HEXAGON_SHELLS, "triangle": TRIANGLE_SHELLS}
LATTICELIFE = {
    ("square", ("N4", "D4")): "B1357/S1357",
    ("square", ("N4", "D4", "self")): "B1357/S02468",
    ("hexagon", ("H1",)): "B135/S135",
    ("hexagon", ("H1", "self")): "B135/S0246",
    ("triangle", ("E",)): "B13/S13",
    ("triangle", ("E", "self")): "B13/S02",
    ("triangle", ("E", "VO", "VS")): "B1,3,5,7,9,11/S1,3,5,7,9,11",
    ("triangle", ("E", "VO", "VS", "self")): "B1,3,5,7,9,11/S0,2,4,6,8,10,12",
}


def rules() -> list[tuple[str, tuple[str, ...]]]:
    """Every non-empty set of shells, with and without the cell itself (the cell alone, the
    identity, left out): 14 per lattice."""
    out = []
    for lattice, shells in SHELLS.items():
        names = list(shells)
        for r in range(1, len(names) + 1):
            for combo in itertools.combinations(names, r):
                out.append((lattice, combo))
                out.append((lattice, (*combo, "self")))
    return out


def name(lattice: str, shells: tuple[str, ...]) -> str:
    return f"{lattice} {'+'.join(shells)}"


def valid_size(lattice: str, n: int) -> bool:
    return n >= 3 and (lattice == "square" or n % 2 == 0)


def build(lattice: str, shells: tuple[str, ...], n: int) -> tuple[GroupRing, Matrix]:
    if not valid_size(lattice, n):
        raise ValueError(f"no {lattice} torus of side {n}")
    if lattice in ("square", "hexagon"):
        ring = (
            GroupRing((n, 0), (0, n)) if lattice == "square" else GroupRing((n, -(n // 2)), (0, n))
        )
        poly = ring.zero()
        for shell in shells:
            steps = ((0, 0),) if shell == "self" else SHELLS[lattice][shell]
            for i, j in steps:
                poly[ring.index(i, j)] += 1
        return ring, Matrix(ring, [[poly % 2]])
    ring = GroupRing((n // 2, -(n // 2)), (n // 2, n // 2))
    uu, ud, du, dd = (ring.zero() for _ in range(4))
    for shell in shells:
        if shell == "self":
            uu[ring.index(0, 0)] += 1
            dd[ring.index(0, 0)] += 1
            continue
        for dr, dc in TRIANGLE_SHELLS[shell]["up"]:
            if (dr + dc) % 2 == 0:
                i, j = _tau(dr, dc)
                uu[ring.index(-i, -j)] += 1
            else:
                i, j = _tau(dr, dc - 1)
                ud[ring.index(-i, -j)] += 1
        for dr, dc in TRIANGLE_SHELLS[shell]["down"]:
            if (dr + dc) % 2 == 0:
                i, j = _tau(dr, dc)
                dd[ring.index(-i, -j)] += 1
            else:
                i, j = _tau(dr, dc + 1)
                du[ring.index(-i, -j)] += 1
    return ring, Matrix(ring, [[uu % 2, ud % 2], [du % 2, dd % 2]])


def odd_part(n: int) -> int:
    while n % 2 == 0:
        n //= 2
    return n


@functools.cache
def mersenne_primes(order: int) -> tuple[int, ...]:
    found = set()
    for d in sympy.divisors(order):
        found |= set(sympy.factorint(int(sympy.cyclotomic_poly(d, 2))))
    return tuple(sorted(found))


def bound(lattice: str, n: int) -> tuple[int, tuple[int, ...]]:
    """C, a multiple of every period on this torus, and the primes of C."""
    exponent = {"square": n, "hexagon": 2 * n, "triangle": n}[lattice]
    k = 2 if lattice == "triangle" else 1
    odd = odd_part(exponent)
    m = int(sympy.n_order(2, odd)) if odd > 1 else 1
    e = int(math.log2(exponent // odd))
    primes = (2, *mersenne_primes(k * m)) if k * m > 1 else (2,)
    return 2 ** (e + 2) * (2 ** (k * m) - 1), tuple(sorted(set(primes)))


class Torus:
    """One rule on one torus: its matrix, the state past the transient, and powers of M."""

    def __init__(self, lattice: str, shells: tuple[str, ...], n: int):
        self.lattice, self.shells, self.n = lattice, shells, n
        self.ring, self.M = build(lattice, shells, n)
        self.late = self.M.power(4 * n)
        self.C, self.primes = bound(lattice, n)

    def dies(self) -> bool:
        return self.late.is_zero()

    def repeats(self, p: int) -> bool:
        return self.late * self.M.power(p) == self.late

    def period(self) -> int:
        if self.dies():
            return 1
        if not self.repeats(self.C):
            raise ArithmeticError(f"{name(self.lattice, self.shells)} at {self.n}: bound fails")
        p = self.C
        for q in self.primes:
            while p % q == 0 and self.repeats(p // q):
                p //= q
        return p

    def check(self, predicted: int) -> dict:
        """Is `predicted` the period? Decided from C's primes alone."""
        if self.dies():
            return {"is_period": predicted == 1, "reason": "the torus dies: period 1"}
        if predicted < 1 or self.C % predicted:
            return {"is_period": False, "reason": "does not divide the bound"}
        if not self.repeats(predicted):
            return {"is_period": False, "reason": "M does not repeat after it"}
        for q in self.primes:
            if predicted % q == 0 and self.repeats(predicted // q):
                return {"is_period": False, "reason": f"M already repeats after predicted / {q}"}
        return {"is_period": True, "reason": "repeats, and at no proper divisor"}


def period(lattice: str, shells: tuple[str, ...], n: int) -> int:
    return Torus(lattice, shells, n).period()


def _sanity() -> None:
    assert len(rules()) == 42
    assert np.array_equal(build("square", ("N4",), 6)[1].e[0][0].sum(), 4)
