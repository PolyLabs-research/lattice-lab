"""
What a closure test of a linear rule must show, from the group ring alone.

A linear rule on a torus is multiplication by a polynomial f in the group ring F2[G], G the
torus's translations (examples/linear-atlas/engine.py, examples/parity-lattices/lattices.py). A
closure test (scaleup.py) by decimation with block b, clock T and coarse rule g compares, at the
supercell whose sampled cell is v,

    fine route      the coefficient sum of f^T around v
    coarse route    the coefficient sum of g(x^b, y^b) around v      (g's neighbours, b apart)

so the two routes differ at v by the functional delta = f^T + g(x^b, y^b), read around v. The
supercells' functionals are the translates of delta by the sublattice b G.

- If delta = 0 the routes agree at every supercell from every start. That is the case T = b = 2^k
  and g = f: Frobenius gives f^(2^k) = f(x^(2^k), y^(2^k)) (proofs: `gstep_iterate_two_pow`), and
  the sublattice's cosets each carry a copy of the coarse world (`restrict_iterate`).
- If delta != 0, every supercell's mismatch is a non-zero linear functional of the start, so from
  a uniformly random start it is a fair coin. The N supercells' coins are jointly uniform on a
  space of dimension `rank`, the rank over F2 of the N translates. With rank = N they are N
  independent fair coins, and the number of mismatches is exactly Binomial(N, 1/2). With
  rank = N - 1 the one constraint is invariant under the sublattice's translations, which move
  any supercell to any other, so it is the sum of all N coins: the mismatch vector is a
  uniformly random vector of even weight. Below that the distribution is not worked out here.

`law` returns which case a test is in, with the rank computed by elimination. Nothing here runs
LatticeLife.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "linear-atlas"))

import engine  # noqa: E402

# LatticeLife's parity rules, as the atlas's shells (engine.LATTICELIFE, inverted).
SHELLS = {
    ("square", "B1357/S1357"): ("N4", "D4"),
    ("square", "B1357/S02468"): ("N4", "D4", "self"),
    ("hexagon", "B135/S135"): ("H1",),
    ("hexagon", "B135/S0246"): ("H1", "self"),
}
assert all(engine.LATTICELIFE[shape, shells] == rule for (shape, rule), shells in SHELLS.items())


def steps(shape: str, rule: str) -> list[tuple[int, int]]:
    """The rule's neighbourhood as translations (the cell itself is (0, 0)), in the ring's
    coordinates: (i, j) on the square, axial (q, r) on the hexagon."""
    out = []
    for shell in SHELLS[shape, rule]:
        out += [(0, 0)] if shell == "self" else list(engine.SHELLS[shape][shell])
    return out


def power(shape: str, rule: str, side: int, exponent: int) -> tuple[engine.GroupRing, np.ndarray]:
    """f^exponent in the group ring of the side x side torus, as a 0/1 array over the ring's
    fundamental domain."""
    ring, matrix = engine.build(shape, SHELLS[shape, rule], side)
    return ring, matrix.power(exponent).e[0][0].astype(np.int64)


def delta(shape: str, rule: str, side: int, block: int, clock: int, coarse_rule: str) -> tuple:
    """(ring, f^clock + g(x^block, y^block)) for fine rule f and coarse rule g."""
    ring, fine = power(shape, rule, side, clock)
    coarse = np.zeros_like(fine)
    for i, j in steps(shape, coarse_rule):
        coarse[ring.index(block * i, block * j)] += 1
    return ring, (fine + coarse) % 2


def translates(ring, element: np.ndarray, block: int, coarse_side: int) -> list[int]:
    """The translates of `element` by block * (u, v), 0 <= u, v < coarse_side (the sublattice's
    elements, once each), each as a bit mask over the ring's cells."""
    support = [(int(i), int(j)) for i, j in zip(*np.nonzero(element), strict=True)]
    rows = []
    for u in range(coarse_side):
        for v in range(coarse_side):
            row = 0
            for i, j in support:
                a, b = ring.index(i + block * u, j + block * v)
                row ^= 1 << (a * ring.d + b)
            rows.append(row)
    return rows


def rank(rows: list[int]) -> int:
    """The rank over F2 of bit-mask rows, by elimination."""
    pivots: dict[int, int] = {}
    for row in rows:
        while row:
            top = row.bit_length() - 1
            if top not in pivots:
                pivots[top] = row
                break
            row ^= pivots[top]
    return len(pivots)


def law(shape: str, rule: str, side: int, block: int, clock: int, coarse_rule: str) -> dict:
    """What a decimation closure test must show after one coarse generation: `zero` (the routes
    agree everywhere), or the number of supercells and the rank of their mismatch functionals.
    `even` says the functionals add up to zero, so the number of mismatches is always even;
    with rank = supercells - 1 that is the only constraint on them."""
    coarse_side = side // block
    ring, d = delta(shape, rule, side, block, clock, coarse_rule)
    supercells = coarse_side * coarse_side
    if not d.any():
        return {"zero": True, "supercells": supercells}
    rows = translates(ring, d, block, coarse_side)
    total = 0
    for row in rows:
        total ^= row
    return {
        "zero": False,
        "supercells": supercells,
        "terms": int(d.sum()),
        "rank": rank(rows),
        "even": total == 0,
    }


def acceptance(trials: int, alpha: float) -> tuple[int, int]:
    """The integers [low, high] with P(X < low) <= alpha / 2 and P(X > high) <= alpha / 2 for
    X ~ Binomial(trials, 1/2): the narrowest such interval."""
    coin = stats.binom(trials, 0.5)
    low = int(coin.ppf(alpha / 2))
    while low > 0 and coin.cdf(low - 1) > alpha / 2:
        low -= 1
    while coin.cdf(low) <= alpha / 2:
        low += 1
    return low, trials - low


def pooled_acceptance(
    supercells: int, deficiency: int, seeds: int, alpha: float
) -> tuple[int, int]:
    """An interval the mismatches of `seeds` independent uniform starts, added up, leave with
    probability at most `alpha`, for a test whose functionals have rank supercells - deficiency.

    deficiency 0: the total is Binomial(seeds * supercells, 1/2), and this is its interval.
    deficiency 1: each start's mismatches are a uniform even-weight vector, which is a uniform
    vector on supercells - 1 coordinates and one more bit that makes the weight even. So the
    total is W + c with W ~ Binomial(seeds * (supercells - 1), 1/2) and 0 <= c <= seeds, and
    W's interval, widened by `seeds` at the top, holds it."""
    if deficiency == 0:
        return acceptance(seeds * supercells, alpha)
    if deficiency == 1:
        low, high = acceptance(seeds * (supercells - 1), alpha)
        return low, high + seeds
    raise ValueError("no exact interval for a rank deficiency above 1")
