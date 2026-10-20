"""
A fast census of power confinement at m = 37, for families of symmetric square rules.

At 37, 2 is a primitive root, so a symmetric rule's nonzero characters fall into 11 classes: the
lines (0, 1) and (1, k) through the origin, up to k -> -k and k -> 1/k, each line a single
Frobenius orbit (all its eigenvalues are conjugate). A rule's value at a class is the xor of its
orbits' values, so the values of every union of orbits come from the orbits' by doubling
arrays. Values lie in F(2^18), the fixed field of Frob^18 in F(2^36); each is reduced to
coordinates in a basis of that subfield and looked up in a table of discrete logarithms mod 27.

    characters()                 one character per class: (0, 1), then (1, k) for ten k
    orbits(radius)               the D4 orbits (a, b), 0 <= b <= a <= radius, in bit order
    rule(n, radius)              rule n of that family, as a set of exponent pairs
    class_logs(radius)           (11, 2^n) array: each rule's log mod 27 at each class (ZERO: 0)
    logs_of(f)                   the 11 logs of one rule f (any symmetric set of exponents)
    confined(logs, q)            the rules whose nonzero eigenvalues are all q-th powers, q | 27

A value is a cube iff its log is 0 mod 3, a ninth power iff 0 mod 9, and so on. The family at
radius 4 has 32,767 rules (seconds); at radius 5, 2,097,151 (tens of seconds, 100 MB).
"""

from __future__ import annotations

from functools import cache

import numpy as np
from gf2 import Field

M = 37
F = Field(M)  # F(2^36), zeta = F.zeta
N18 = 2**18 - 1
ZERO = 255


def orbits(radius: int) -> list[tuple[int, int]]:
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def points(orbit: tuple[int, int]) -> set[tuple[int, int]]:
    a, b = orbit
    return {(sp * p, sq * q) for p, q in ((a, b), (b, a)) for sp in (1, -1) for sq in (1, -1)}


def rule(n: int, radius: int = 5) -> frozenset:
    out: set = set()
    for i, o in enumerate(orbits(radius)):
        if n >> i & 1:
            out ^= points(o)
    return frozenset(out)


def characters() -> list[tuple[int, int]]:
    seen, reps = set(), [(0, 1)]
    for k in range(M):
        if k in seen:
            continue
        orbit = {k, -k % M} | ({pow(k, -1, M), -pow(k, -1, M) % M} if k else set())
        seen |= orbit
        if 0 not in orbit:
            reps.append((1, k))
    return reps


@cache
def _basis() -> tuple[tuple[int, int], ...]:
    rows: list[int] = []
    for i in range(F.degree):
        x = 1 << i  # z^i, as a polynomial in the field's generator
        v = x ^ F.pow(x, 2**18)  # its trace to F(2^18)
        for r in rows:
            if v ^ r < v:
                v ^= r
        if v:
            rows = [r ^ v if r ^ v < r else r for r in rows] + [v]
            rows.sort(reverse=True)
    assert len(rows) == 18
    return tuple((r.bit_length() - 1, r) for r in rows)


def coord(v: int) -> int:
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
    def element(c: int) -> int:
        v = 0
        for i, (_, row) in enumerate(_basis()):
            if c >> i & 1:
                v ^= row
        return v

    g = next(v for v in map(element, range(1, 1 << 18))
             if all(F.pow(v, N18 // p) != 1 for p in (3, 7, 19, 73)))  # fmt: skip
    table = np.full(1 << 18, ZERO, dtype=np.uint8)
    x = 1
    for e in range(N18):
        table[coord(x)] = e % 27
        x = F.mul(x, g)
    return table


def _value(f, j: int, k: int) -> int:
    v = 0
    for p, q in f:
        v ^= F.pow(F.zeta, (p * j + q * k) % M)
    return v


def logs_of(f) -> list[int]:
    return [int(log_table()[coord(_value(f, j, k))]) for j, k in characters()]


def class_logs(radius: int) -> np.ndarray:
    chars, orbs = characters(), orbits(radius)
    values = np.zeros((len(chars), 1 << len(orbs)), dtype=np.uint32)
    for i, o in enumerate(orbs):
        ov = np.array([coord(_value(points(o), j, k)) for j, k in chars], dtype=np.uint32)
        values[:, 1 << i : 2 << i] = values[:, : 1 << i] ^ ov[:, None]
    return log_table()[values]


def confined(logs: np.ndarray, q: int) -> np.ndarray:
    return np.all((logs == ZERO) | (logs % q == 0), axis=0)
