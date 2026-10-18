"""
Exact periods of triangle rules built from round 3's shells, which the base engine does not know.

    period(shells, n)              the eventual period on the atlas's triangular torus of side n
    check(shells, n, predicted)    whether `predicted` is it, and the period itself

The step comes from atlas3.build; the bound and its primes from engine.bound, as in
engine.Torus.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "linear-atlas-3"))

import atlas3  # noqa: E402

engine = atlas3.engine


class Torus:
    def __init__(self, shells: tuple[str, ...], n: int):
        self.shells, self.n = shells, n
        _, self.M = atlas3.build("triangle", shells, n)
        self.late = self.M.power(4 * n)
        self.C, self.primes = engine.bound("triangle", n)

    def repeats(self, p: int) -> bool:
        return self.late * self.M.power(p) == self.late

    def period(self) -> int:
        if self.late.is_zero():
            return 1
        if not self.repeats(self.C):
            raise ArithmeticError(f"{self.shells} at {self.n}: bound fails")
        p = self.C
        for q in self.primes:
            while p % q == 0 and self.repeats(p // q):
                p //= q
        return p


def period(shells: tuple[str, ...], n: int) -> int:
    return Torus(shells, n).period()


def check(shells: tuple[str, ...], n: int, predicted: int) -> dict:
    p = period(shells, n)
    return {"is_period": p == predicted, "period": p}
