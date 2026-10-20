"""
Forced subfields, and the chance that a rule's eigenvalues are all cubes, at odd m.

Frobenius gives lambda(2c) = lambda(c)^2, and a matrix M that maps a rule's translations onto
themselves mod m gives lambda(M^T c) = lambda(c). So if 2^i c = M^T c for such an M, lambda(c) lies
in F(2^i) whatever the rule: the forced degree of the class of c. A forced field whose nonzero
elements are all cubes in F(2^d) makes the class a cube by structure; the other classes are free.
The chance model takes each free class's value uniform over its forced field, independently, so
the chance that a rule is confined to the cubes is the product of gcd(2^i - 1, (2^d - 1)/3) /
(2^i - 1) over its nonzero classes.

    symmetries(f, m)        the lattice's symmetries (entries -1, 0, 1) times powers of 2, mod m
    full_symmetries(f, m)   every matrix in GL2(Z/m) preserving f mod m (small m)
    classes(f, m, sym)      the classes of characters: representative, size, forced degree, value
    analyse(f, m, full)     free classes, distinct free values, forced?, chance, all cubes?

The model is approximate: in small fields free classes are cubes more often than one time in
three (about 37 to 40% at m = 13), and it treats classes as independent.
"""

from __future__ import annotations

import functools
import itertools
import math

import sympy
from eigen import Field

UNIT = [A for A in itertools.product((-1, 0, 1), repeat=4) if A[0] * A[3] - A[1] * A[2] in (1, -1)]


def _keeps(M, m, pts):
    return all(((M[0] * x + M[1] * y) % m, (M[2] * x + M[3] * y) % m) in pts for x, y in pts)


@functools.cache
def _degree(m: int) -> int:
    return Field(m).degree


def symmetries(f, m: int) -> tuple:
    support = {(x % m, y % m) for x, y in f}
    powers = sorted({pow(2, e, m) for e in range(_degree(m))})
    out = set()
    for s in powers:
        for a, b, c, d in UNIT:
            M = ((s * a) % m, (s * b) % m, (s * c) % m, (s * d) % m)
            if _keeps(M, m, support):
                out.add(M)
    return tuple(sorted(out))


def full_symmetries(f, m: int) -> tuple:
    support = {(x % m, y % m) for x, y in f}
    P = max(p**e for p, e in sympy.factorint(m).items())
    Q = m // P

    def inv(M, n):
        return math.gcd((M[0] * M[3] - M[1] * M[2]) % n, n) == 1

    small = {(x % P, y % P) for x, y in support}
    mod_p = [M for M in itertools.product(range(P), repeat=4) if inv(M, P) and _keeps(M, P, small)]
    mod_q = [M for M in itertools.product(range(Q), repeat=4) if inv(M, Q)]
    lift = {(a, b): next(x for x in range(m) if x % P == a and x % Q == b)
            for a in range(P) for b in range(Q)}  # fmt: skip
    out = []
    for Mp, Mq in itertools.product(mod_p, mod_q):
        M = tuple(lift[(a, b)] for a, b in zip(Mp, Mq, strict=True))
        if _keeps(M, m, support):
            out.append(M)
    return tuple(sorted(out))


@functools.cache
def partition(m: int, sym: tuple) -> tuple:
    d = _degree(m)

    def act(M, a, b):
        return (M[0] * a + M[2] * b) % m, (M[1] * a + M[3] * b) % m

    seen, out = set(), []
    for j, k in itertools.product(range(m), repeat=2):
        if (j, k) == (0, 0) or (j, k) in seen:
            continue
        orbit, stack = {(j, k)}, [(j, k)]
        while stack:
            a, b = stack.pop()
            for nxt in [(2 * a % m, 2 * b % m)] + [act(M, a, b) for M in sym]:
                if nxt not in orbit:
                    orbit.add(nxt)
                    stack.append(nxt)
        seen |= orbit
        images, stack = {(j, k)}, [(j, k)]
        while stack:
            a, b = stack.pop()
            for M in sym:
                nxt = act(M, a, b)
                if nxt not in images:
                    images.add(nxt)
                    stack.append(nxt)
        degree = next(
            i for i in range(1, d + 1) if (pow(2, i, m) * j % m, pow(2, i, m) * k % m) in images
        )
        out.append(((j, k), len(orbit), degree))
    return tuple(out)


@functools.cache
def cube_chance(i: int, m: int) -> float:
    N = 2 ** _degree(m) - 1
    return math.gcd(2**i - 1, N // 3) / (2**i - 1)


def classes(f, m: int, sym: tuple | None = None) -> list[dict]:
    F = Field(m)
    zeta = [F.pow(F.zeta, e) for e in range(m)]
    sym = symmetries(f, m) if sym is None else sym
    out = []
    for (j, k), size, degree in partition(m, sym):
        value = 0
        for x, y in f:
            value ^= zeta[(x * j + y * k) % m]
        out.append({"rep": (j, k), "size": size, "degree": degree, "value": value})
    return out


def analyse(f, m: int, full: bool = False) -> dict:
    F = Field(m)
    sym = full_symmetries(f, m) if full else symmetries(f, m)
    cs = classes(f, m, sym)
    nonzero = [c for c in cs if c["value"]]
    free = [c for c in nonzero if cube_chance(c["degree"], m) < 1]

    def canon(v):
        best = w = v
        for _ in range(F.degree):
            w = F.mul(w, w)
            best = min(best, w)
        return best

    return {
        "symmetries": len(sym),
        "classes": len(cs),
        "free": len(free),
        "distinct_free": len({canon(c["value"]) for c in free}),
        "forced": not free and bool(nonzero),
        "chance": math.prod(cube_chance(c["degree"], m) for c in nonzero),
        "cubes": bool(nonzero) and all(F.pow(c["value"], F.order // 3) == 1 for c in nonzero),
    }
