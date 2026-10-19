"""
Which shell rules have every nonzero eigenvalue in the subgroup of q-th powers, at odd part m.

    confined(f, m, q)     whether every nonzero eigenvalue f(zeta^j, zeta^k) is a q-th power in
                          F(2^d)*, d = ord_m(2): that is, the odd part of the period divides
                          (2^d - 1) / q
    explained(f, m, q)    whether the atlas's procedure (atlas3.predict: splitting, powers,
                          dilations) already accounts for it: its predicted odd part divides
                          (2^d - 1) / q, or it makes no prediction (mixed factors)
    unexplained(m, q)     every rule of the atlas that is confined at m and not explained

The rules are all 1,274 shell rules of the three lattices (atlas3.all_rules); on the triangle the
polynomial is s, with M^2 = s I. Eigenvalues come from linear-atlas-3/eigen.py's field and
arithmetic, which agreed with all 11,662 exact records of round 3. This is the orchestrator's
check; the agent's tools are separate.
"""

from __future__ import annotations

import functools
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "linear-atlas-3"))

import atlas3  # noqa: E402
import eigen  # noqa: E402

LATTICES = ("square", "triangle", "hexagon")


@functools.cache
def rules() -> tuple[tuple[str, tuple[str, ...], frozenset], ...]:
    return tuple(
        (lattice, shells, atlas3.polynomial(lattice, shells))
        for lattice in LATTICES
        for shells in atlas3.all_rules(lattice)
    )


@functools.cache
def setup(m: int) -> tuple[int, int, int, list[int], list[tuple[int, int]]]:
    """(mod, d, N, zeta powers, one (j, k) per Frobenius orbit) at odd m."""
    mod, d = eigen.field(m)
    zeta = [eigen._pow(2, e, mod, d) for e in range(m)]
    reps, seen = [], set()
    for j in range(m):
        for k in range(m):
            if (j, k) in seen:
                continue
            a, b = j, k
            while (a, b) not in seen:
                seen.add((a, b))
                a, b = 2 * a % m, 2 * b % m
            reps.append((j, k))
    return mod, d, 2**d - 1, zeta, reps


def confined(f: frozenset, m: int, q: int) -> bool:
    """Every nonzero eigenvalue is a q-th power (and at least one is nonzero)."""
    mod, d, N, zeta, reps = setup(m)
    if N % q:
        return False
    nonzero = False
    for j, k in reps:
        value = 0
        for x, y in f:
            value ^= zeta[(x * j + y * k) % m]
        if value == 0:
            continue
        nonzero = True
        if eigen._pow(value, N // q, mod, d) != 1:
            return False
    return nonzero


# Round 3's twisted power, which atlas3.predict does not include: VO + T13's s is E's s times
# its own dilation by 3, so where 3 = +-2^k mod m its eigenvalues are powers lambda^(1 + 2^k)
# (Periods.lean, atlasTriPeriod_twisted).
TWISTED = {("triangle", ("VO", "T13"))}


def _twisted(m: int) -> int | None:
    """The odd part the twisted power predicts for VO + T13 at m, if 3 = +-2^k mod m."""
    for k in range(1, m):
        if pow(2, k, m) in (3 % m, (-3) % m):
            edge = eigen.odd_part(atlas3.polynomial("triangle", ("E",)), m)
            return edge // math.gcd(edge, 1 + 2**k)
    return None


def explained(f: frozenset, m: int, q: int, key: tuple | None = None) -> bool:
    _, _, N, _, _ = setup(m)
    if key in TWISTED and (predicted := _twisted(m)) is not None:
        return (N // q) % predicted == 0
    predicted, _ = atlas3.predict(f, m)
    return predicted is None or (N // q) % predicted == 0


def unexplained(m: int, q: int = 3) -> list[dict]:
    out = []
    for lattice, shells, f in rules():
        if confined(f, m, q) and not explained(f, m, q, (lattice, shells)):
            out.append({"m": m, "q": q, "lattice": lattice, "shells": "+".join(shells),
                        "call": atlas3.predict(f, m)[1]})  # fmt: skip
    return out


def cube_sizes(lo: int, hi: int) -> list[int]:
    """The odd m in [lo, hi] at which cubes are a proper subgroup: d = ord_m(2) even."""
    return [m for m in range(lo | 1, hi + 1, 2) if m > 1 and eigen.field(m)[1] % 2 == 0]
