"""
Round 2 of the linear-rule atlas: the rules, the pattern's predictions, a faster exact check.

The pattern (examples/linear-atlas/factor.py, found after round 1's verdict): a rule whose
polynomial splits completely into one-dimensional factors (on the triangle, whose matrix's
square does) has a 1D rule's period; a rule that does not split reaches the full bound. Round 2
registers it in two parts.

- **A.** The 34 atlas rules with a law, at sizes beyond round 1 where the two families part. Each
  rule's predicted law is the one its factorisation assigns, among the laws Kepler proposed.
- **B.** 112 square rules never computed here, built with three more shells: K8 (the eight at
  distance sqrt 5), B4 (the four at distance 2 sqrt 2) and C4 (the four at distance 3). At odd n
  the pattern predicts each period from the factorisation alone:
  - a rule that does not split completely has period 2^sord(n) - 1, the full bound;
  - one that splits into factors 1 + u only has rule 90's period, P90(n);
  - one that splits into factors 1 + u + u^2 only has rule 150's, P150(n);
  - one that splits into copies of another single factor g has the period of the symmetric 1D
    rule made from g (`p_1d`);
  - one whose factors are of more than one kind is computed and reported, with no prediction.
  The rule was checked, before registration, on round 1's discovery data: the 14 atlas square
  rules at every odd n from 9 to 59, the four without a law included. It held at all of them.

Sizes are chosen by where rule 90's or rule 150's period differs from the full bound, which
never looks at a 2D rule's period.
"""

from __future__ import annotations

import functools
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import sympy

ATLAS = Path(__file__).resolve().parent.parent / "linear-atlas"
sys.path.insert(0, str(ATLAS))

import engine  # noqa: E402
import factor  # noqa: E402
from kepler.integer_laws import rule_period  # noqa: E402
from lattices import GroupRing, Matrix  # noqa: E402

EXTRA = {
    "K8": engine._pm((1, 2), (2, 1), (1, -2), (2, -1)),
    "B4": engine._pm((2, 2), (2, -2)),
    "C4": engine._pm((3, 0), (0, 3)),
}
SQUARE = {**engine.SQUARE_SHELLS, **EXTRA}


def sord(m: int) -> int:
    """The suborder of 2 modulo odd m: the least j with 2^j = +-1 (mod m)."""
    if m == 1:
        return 1
    order = int(sympy.n_order(2, m))
    return order // 2 if order % 2 == 0 and pow(2, order // 2, m) == m - 1 else order


def full_bound(n: int) -> int:
    m = engine.odd_part(n)
    return (n // m) * (2 ** sord(m) - 1)


@functools.cache
def p90(n: int) -> int:
    return rule_period(90, n)


@functools.cache
def p150(n: int) -> int:
    return rule_period(150, n)


def new_rules() -> list[tuple[str, ...]]:
    """Every set of the six square shells using at least one new one, with and without the
    cell: 112 rules."""
    out = []
    names = list(SQUARE)
    for r in range(1, len(names) + 1):
        for combo in itertools.combinations(names, r):
            if set(combo) & set(EXTRA):
                out.append(combo)
                out.append((*combo, "self"))
    return out


def square_polynomial(shells: tuple[str, ...]) -> set[tuple[int, int]]:
    terms: set[tuple[int, int]] = set()
    for shell in shells:
        terms ^= {(0, 0)} if shell == "self" else set(SQUARE[shell])
    return terms


def classify(shells: tuple[str, ...]) -> dict:
    """The pattern's call for a new square rule, from its polynomial alone."""
    result = factor.split(square_polynomial(shells))
    types = sorted({f["factor"] for f in result["factors"]})
    out = {"factor types": types, "factors": len(result["factors"]), "splits": result["splits"]}
    if not result["splits"]:
        return {"call": "full bound", **out}
    if types == ["1+u"]:
        return {"call": "P90", **out}
    if types == ["1+u+u^2"]:
        return {"call": "P150", **out}
    if len(types) == 1:
        return {"call": "1D rule", "g": result["factors"][0]["g"], **out}
    return {"call": "no prediction", **out}


@functools.cache
def p_1d(g: tuple[int, ...], n: int) -> int:
    """For odd n, the period of the symmetric 1D rule made from g: multiplication by
    u^(-deg(g)/2) g(u) on a ring of n cells, with 1/2 = (n + 1)/2 modulo n. For g = 1 + u its
    square is rule 90, so at odd n its period is P90(n); for g = 1 + u + u^2 it is rule 150."""
    if n % 2 == 0:
        raise ValueError("p_1d is for odd n")
    ring = GroupRing((n, 0), (0, 1))
    shift = (-max(g) * (n + 1) // 2) % n
    poly = ring.zero()
    for e in g:
        poly[ring.index((e + shift) % n, 0)] += 1
    return Exact("square", ring, Matrix(ring, [[poly % 2]]), n).period()


def predict(classification: dict, n: int) -> int | None:
    call = classification["call"]
    if call == "full bound":
        return full_bound(n)
    if call == "P90":
        return p90(n)
    if call == "P150":
        return p150(n)
    if call == "1D rule":
        return p_1d(tuple(classification["g"]), n)
    return None


def build_square(shells: tuple[str, ...], n: int) -> tuple[GroupRing, Matrix]:
    ring = GroupRing((n, 0), (0, n))
    poly = ring.zero()
    for i, j in square_polynomial(shells):
        poly[ring.index(i, j)] += 1
    return ring, Matrix(ring, [[poly % 2]])


def decisive(n: int) -> bool:
    """Do rule 90's or rule 150's period differ from the full bound here?"""
    return n & (n - 1) != 0 and (p90(n) != full_bound(n) or p150(n) != full_bound(n))


class Exact:
    """engine.Torus's exact check, with one change: the tests at p / q, one for each prime q of
    p, share their work through a product tree, so they cost about log(number of primes) powers
    instead of one each. Agreement with engine.Torus.check is tested on round 1's records."""

    def __init__(self, lattice: str, ring: GroupRing, M: Matrix, n: int):
        self.lattice, self.n, self.M = lattice, n, M
        self.late = M.power(4 * n)
        self.C, self.primes = engine.bound(lattice, n)

    @classmethod
    def atlas(cls, lattice: str, shells: tuple[str, ...], n: int) -> Exact:
        return cls(lattice, *engine.build(lattice, shells, n), n)

    @classmethod
    def square(cls, shells: tuple[str, ...], n: int) -> Exact:
        return cls("square", *build_square(shells, n), n)

    def _fixes(self, X: Matrix) -> bool:
        return self.late * X == self.late

    def _proper(self, X: Matrix, primes: list[int]) -> int | None:
        """X = M^(p / prod(primes)); returns a prime q with late M^(p/q) = late, if any."""
        if len(primes) == 1:
            return primes[0] if self._fixes(X) else None
        half = len(primes) // 2
        left, right = primes[:half], primes[half:]
        return self._proper(X.power(math.prod(right)), left) or self._proper(
            X.power(math.prod(left)), right
        )

    def check(self, predicted: int) -> dict:
        if self.late.is_zero():
            return {"is_period": predicted == 1, "reason": "the torus dies: period 1"}
        if predicted < 1 or self.C % predicted:
            return {"is_period": False, "reason": "does not divide the bound"}
        if not self._fixes(self.M.power(predicted)):
            return {"is_period": False, "reason": "M does not repeat after it"}
        primes = [q for q in self.primes if predicted % q == 0]
        if primes:
            q = self._proper(self.M.power(predicted // math.prod(primes)), primes)
            if q is not None:
                return {"is_period": False, "reason": f"M already repeats after predicted / {q}"}
        return {"is_period": True, "reason": "repeats, and at no proper divisor"}

    def period(self) -> int:
        if self.late.is_zero():
            return 1
        p = self.C
        if not self._fixes(self.M.power(p)):
            raise ArithmeticError("bound fails")
        for q in self.primes:
            while p % q == 0 and self._fixes(self.M.power(p // q)):
                p //= q
        return p


def _sanity() -> None:
    assert len(new_rules()) == 112
    assert np.isclose(build_square(("K8",), 9)[1].e[0][0].sum(), 8)
