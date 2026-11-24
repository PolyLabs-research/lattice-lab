"""
How far a world is organised: the correlation area, read off block sums.

Take a field of 0s and 1s on the grid (the live cells, or one species' cells) with mean p, cut
the grid into b x b blocks and add up each block. Were the cells independent, the sums would
scatter with variance b² p (1 - p). The **correlation area** at block b is how many times more
they scatter than that:

    area(b) = variance of the block sums / (b² p (1 - p))

- 1 where cells are independent;
- level, at the number of cells that go together, once blocks are larger than whatever
  structure there is. Life against HighLife levels at about 6 cells, which is also what the
  spread of its live fraction over starts gave in step 3, where spread x side was
  sqrt(area p (1 - p));
- growing as b², the block's own area, while blocks are smaller than the domains.

So two numbers say how a world is organised at one moment, the area at the largest block and
how it scales with the block (a power of 0 for patches, 2 for domains larger than the blocks),
and a third says whether it is still organising: the power of time the area grows as.

A pattern can be ordered without its block sums scattering: a chequerboard puts the same sum
in every block. So the live cells are also read against three masks of +1 and -1 by turns
(chequered, rows, columns), with the sums taken about zero. A chequerboard domain then has
area b², as it should.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence

import numpy as np
from latticelife.core.lattice import LatticeGrid, TieBreak
from latticelife.core.lifeform import Lifeform
from latticelife.core.rules import Rule
from latticelife.experiments.competition import species_start

BLOCKS = (2, 4, 8, 16, 32)
MASKS = ("chequered", "rows", "columns")
RARE = 0.01  # a field emptier or fuller than this has no area to speak of


def signs(side: int, mask: str) -> np.ndarray:
    """The mask as +1 and -1 on the side x side grid."""
    row, column = np.indices((side, side))
    turn = {"chequered": row + column, "rows": row, "columns": column}[mask]
    return 1 - 2 * (turn % 2)


def area(field: np.ndarray, block: int, mask: str | None = None) -> float | None:
    """The correlation area of a square field of 0s and 1s at blocks of `block`: the variance
    of the block sums over what independent cells would give. Against a mask the sums are
    signed and taken about zero. None for a field that is all but empty or all but full."""
    side = field.shape[0]
    share = float(field.mean())
    if not RARE <= share <= 1 - RARE:
        return None
    n = side // block
    if mask is None:
        sums = field.reshape(n, block, n, block).sum(axis=(1, 3), dtype=np.int64)
        scatter = float(sums.var(ddof=1))
    else:
        signed = field * signs(side, mask)
        sums = signed.reshape(n, block, n, block).sum(axis=(1, 3), dtype=np.int64)
        scatter = float((sums.astype(float) ** 2).mean())
    return scatter / (block * block * share * (1 - share))


def fields(occupancy: np.ndarray, species: int) -> dict[str, np.ndarray]:
    """The fields a grid of several species is read as: its live cells, and each species'."""
    out = {"live": (occupancy > 0).astype(np.int8)}
    if species > 1:
        for s in range(1, species + 1):
            out[f"species {s}"] = (occupancy == s).astype(np.int8)
    return out


def world(
    rules: Sequence[str], kind: str, side: int, seed: int, density: float = 0.5
) -> tuple[LatticeGrid, np.random.Generator]:
    """A wrapped square grid of `side`, one species to a rule, at a mixed start: each cell live
    with chance `density` and then one species or another with equal chances. With it, the
    generator its steps draw from."""
    species = len(rules)
    lifeforms = [Lifeform(i + 1, Rule.from_bs_string(rule)) for i, rule in enumerate(rules)]
    grid = LatticeGrid(lifeforms, "square", side, side, True, tie_break=TieBreak(kind, 2, 1.0))
    start = species_start("square", side, density, seed, None, species)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    return grid, np.random.default_rng([20261123, 2, int(seed)])


def snapshots(
    rules: Sequence[str], kind: str, side: int, seed: int, times: Sequence[int],
    density: float = 0.5,
) -> dict[int, np.ndarray]:  # fmt: skip
    """The grid of one world at each generation in `times` (0 is the start), as side x side
    arrays of 0 for an empty cell and a species' number for a live one."""
    grid, rng = world(rules, kind, side, seed, density)
    out = {}
    for generation in range(max(times) + 1):
        if generation in times:
            out[generation] = grid.occupancy.reshape(side, side).copy()
        if generation < max(times):
            grid.step(rng)
    return out


def profile(
    rules: Sequence[str],
    kind: str,
    side: int,
    seed: int,
    times: Sequence[int],
    blocks: Sequence[int] = BLOCKS,
    density: float = 0.5,
) -> dict:
    """One world run from a mixed start, read at each generation in `times`: for every field
    its share of the grid and its correlation area at each block, and for the live cells the
    areas against the three masks as well. Also the share of cells that differ between the
    last generation and two before it (nothing, in a world that has stopped or blinks)."""
    species = len(rules)
    grid, rng = world(rules, kind, side, seed, density)
    read: dict[str, dict[str, list]] = {}
    before = last = grid.occupancy.copy()
    marks = sorted(times)
    for generation in range(1, marks[-1] + 1):
        before, last = last, grid.occupancy.copy()
        grid.step(rng)
        if generation not in marks:
            continue
        now = grid.occupancy.reshape(side, side)
        for name, field in fields(now, species).items():
            entry = read.setdefault(name, {"share": [], "area": []})
            entry["share"].append(round(float(field.mean()), 6))
            entry["area"].append([_tidy(area(field, b)) for b in blocks])
            if name == "live":
                for mask in MASKS:
                    masked = read.setdefault(f"live, {mask}", {"share": [], "area": []})
                    masked["share"].append(round(float(field.mean()), 6))
                    masked["area"].append([_tidy(area(field, b, mask)) for b in blocks])
    return {
        "times": list(marks),
        "blocks": list(blocks),
        "fields": read,
        "changed": round(float((grid.occupancy != before).mean()), 6),
        "final_sha256": hashlib.sha256(grid.occupancy.astype(np.int8).tobytes()).hexdigest(),
    }


def _tidy(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def scaling(
    areas: Sequence[float | None], blocks: Sequence[int], low: int, high: int
) -> float | None:
    """The power of the block the area grows as between blocks `low` and `high`: 0 for patches
    smaller than `low`, 2 for domains larger than `high`."""
    a, b = areas[list(blocks).index(low)], areas[list(blocks).index(high)]
    if not a or not b:
        return None
    return math.log(b / a) / math.log(high / low)


def growth(areas: Sequence[float | None], times: Sequence[int]) -> float | None:
    """The power of time the area grows as, by least squares over the logarithms. None unless
    every area is there."""
    if len(areas) < 2 or any(not a for a in areas):
        return None
    x = np.log(np.asarray(times, dtype=float))
    y = np.log(np.asarray(areas, dtype=float))
    x = x - x.mean()
    return float((x * (y - y.mean())).sum() / (x * x).sum())


def clock(
    areas: Sequence[Sequence[float | None]],
    blocks: Sequence[int],
    times: Sequence[int],
    wait: int,
    least: float = 8.0,
) -> list[float]:
    """Does a zoom-out by two go with waiting `wait` times as long? `areas[time][block]` is one
    field's correlation area. If the world seen through blocks twice the size, `wait` times
    later, is the same picture, each block's cells go together as they did: the area, which
    counts cells, is four times what it was. This gives, for every pair of readings `wait`
    apart and every pair of blocks a factor of two apart,

        area(2 b, wait x t) / (4 area(b, t))

    which is 1 where the pictures match, below 1 where the wait was too short and above where
    it was too long. Pairs whose earlier area is under `least` are left out: so few cells are
    the grain of the world, which no zoom-out keeps."""
    out = []
    for i, time in enumerate(times):
        if wait * time not in times:
            continue
        j = list(times).index(wait * time)
        for k, block in enumerate(blocks[:-1]):
            if blocks[k + 1] != 2 * block:
                continue
            early, late = areas[i][k], areas[j][k + 1]
            if early and late and early >= least:
                out.append(late / (4 * early))
    return out
