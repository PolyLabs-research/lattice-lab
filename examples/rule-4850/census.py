"""
The ninth-power census at m = 37, fast enough for the radius-5 family (2^21 - 1 rules).

At 37, 2 is a primitive root, so a symmetric rule's eigenvalues fall into 11 classes: the lines
(1, k) and (0, 1) through the origin, up to k -> -k and k -> 1/k, each line one Frobenius orbit.
A rule's value at a class is the sum, that is the XOR, of its orbits' values, so the values of
every rule of the family come from the orbits' by doubling arrays. The values lie in F(2^18),
the fixed field of Frob^18 in F(2^36) = F2[z]/(eigen.field(37)); each is reduced to coordinates
in a basis of that subfield and looked up in a table of discrete logarithms mod 27, from which
cube, ninth- and 27th-power confinement are read. Zero values are allowed (they leave the lcm).

    uv run --no-sync python examples/rule-4850/census.py     # the check on the radius-4 family
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "linear-atlas-3"))

import eigen  # noqa: E402

M = 37
MOD, D = eigen.field(M)  # F(2^36)
N18 = 2**18 - 1
ZERO = 255  # the table's mark for a zero value


def mul(a: int, b: int) -> int:
    return eigen._mul(a, b, MOD, D)


def power(a: int, e: int) -> int:
    return eigen._pow(a, e, MOD, D)


def orbits(radius: int) -> list[tuple[int, int]]:
    """The D4 orbits (a, b), 0 <= b <= a <= radius, in the family's bit order."""
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def points(orbit: tuple[int, int]) -> set[tuple[int, int]]:
    a, b = orbit
    return {(sp * p, sq * q) for p, q in ((a, b), (b, a)) for sp in (1, -1) for sq in (1, -1)}


def rule(n: int, radius: int = 5) -> frozenset:
    """Family rule n as a set of exponents (the union of the orbits its bits select)."""
    out: set = set()
    for i, o in enumerate(orbits(radius)):
        if n >> i & 1:
            out ^= points(o)
    return frozenset(out)


def characters() -> list[tuple[int, int]]:
    """One character per class: (0, 1) for the axes, (1, k) for the other ten."""
    seen, reps = set(), [(0, 1)]
    for k in range(M):
        if k in seen:
            continue
        orbit = {k, -k % M} | ({pow(k, -1, M), -pow(k, -1, M) % M} if k else set())
        if 0 in orbit:  # k = 0 is the axis line again, (1, 0) ~ (0, 1)
            seen |= orbit
            continue
        seen |= orbit
        reps.append((1, k))
    return reps


@cache
def _basis() -> tuple[tuple[int, int], ...]:
    """A row-reduced basis of F(2^18) inside F(2^36): (pivot bit, row) pairs."""
    rows: list[int] = []
    for i in range(D):
        x = power(2, i)  # z^i
        v = x ^ power(x, 2**18)  # its trace to F(2^18)
        for r in rows:
            if v ^ r < v:
                v ^= r
        if v:
            rows = [r ^ v if r ^ v < r else r for r in rows] + [v]
            rows.sort(reverse=True)
    assert len(rows) == 18, len(rows)
    return tuple((r.bit_length() - 1, r) for r in rows)


def coord(v: int) -> int:
    """The 18-bit coordinates of v in F(2^18) (v must lie in the subfield)."""
    c = 0
    for i, (pivot, row) in enumerate(_basis()):
        if v >> pivot & 1:
            v ^= row
            c |= 1 << i
    if v:
        raise ValueError("not in F(2^18)")
    return c


@cache
def log_table() -> np.ndarray:
    """For each coordinate vector, the discrete log mod 27 of its element (ZERO for zero)."""

    def element(c: int) -> int:  # the element with coordinates c
        v = 0
        for i, (_, row) in enumerate(_basis()):
            if c >> i & 1:
                v ^= row
        return v

    g = next(v for v in map(element, range(1, 1 << 18))  # a generator of F(2^18)*
             if all(power(v, N18 // p) != 1 for p in (3, 7, 19, 73)))  # fmt: skip
    table = np.full(1 << 18, ZERO, dtype=np.uint8)
    x = 1
    for e in range(N18):
        table[coord(x)] = e % 27
        x = mul(x, g)
    assert x == 1 and (table == ZERO).sum() == 1
    return table


def class_logs(radius: int) -> np.ndarray:
    """(11, 2^n) array: the log mod 27 of every rule's value at each class (ZERO for zero)."""
    zeta = [power(2, e) for e in range(M)]
    chars = characters()
    orbs = orbits(radius)
    values = np.zeros((len(chars), 1 << len(orbs)), dtype=np.uint32)
    for i, o in enumerate(orbs):
        ov = []
        for j, k in chars:
            v = 0
            for p, q in points(o):
                v ^= zeta[(p * j + q * k) % M]
            ov.append(coord(v))
        values[:, 1 << i : 2 << i] = values[:, : 1 << i] ^ np.array(ov, dtype=np.uint32)[:, None]
    return log_table()[values]


def confined(logs: np.ndarray, q: int) -> np.ndarray:
    """Rules all of whose nonzero eigenvalues are q-th powers (q in 3, 9, 27)."""
    return np.all((logs == ZERO) | (logs % q == 0), axis=0)


if __name__ == "__main__":
    logs = class_logs(4)
    counts = {q: int(confined(logs, q)[1:].sum()) for q in (3, 9, 27)}
    nine = [int(n) for n in np.flatnonzero(confined(logs, 9)) if n]
    print("radius 4 at 37:", counts, "ninth-power rules:", nine)
