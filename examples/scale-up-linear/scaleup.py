"""
The scale-up instrument: zoom out a LatticeLife torus, and test whether a coarse world predicts
the zoomed-out fine one.

A **world** is a rule on a torus, run by LatticeLife's own update rule (`LatticeGrid.step`) on an
adjacency array. A **projection** reads a coarse configuration off a fine one, one supercell for
each block of fine cells. A **closure test** takes both routes from the same start,

    fine route      run the fine world for s * clock generations, then project
    coarse route    project the start, then run the coarse world for s generations

and counts the supercells where the two differ, for s = 1, 2, ... A count of zero at every s says
the coarse world is an exact stand-in for the fine one at that scale. A count near half the
supercells says it knows nothing about it.

Worlds. `World(shape, rule, side)` is LatticeLife's wrapped side x side grid with its own
adjacency. `dilation = k` gives the same rule with every neighbour k cells away instead of one
(`adjacency`): geometry is data, so this is only another adjacency array. A dilated neighbour
that wraps onto another one is listed twice and counted twice, as the group ring counts it.

Projections, for a block b:

    identity    the configuration itself (b = 1)
    decimate    the fine cell at a fixed place in each block: one coset of the sublattice b Z^2
    parity      the sum mod 2 of the b * b fine cells of each block: every coset, added

On the square the block of supercell (R, C) is the rows b R .. b R + b - 1 and the columns
b C .. b C + b - 1, and an offset is (row, column) inside it. On the hexagon (LatticeLife's
odd-q offset columns) the sublattice is taken in axial coordinates (q, r) = (c, row - floor(c/2)),
where the six neighbours are +-(1, 0), +-(0, 1), +-(1, -1) and the torus is
Z^2 / <(n, -n/2), (0, n)>; the block is the rhombus q0 .. q0 + b - 1, r0 .. r0 + b - 1 and an
offset is (q, r) inside it. The coarse configuration is laid out as a LatticeLife grid of side
n / b, so a coarse world can run it. That needs b to divide n on the square, and b to divide
n / 2 on the hexagon (LatticeLife's hexagon torus has an even side).
"""

from __future__ import annotations

import functools
import hashlib
from dataclasses import dataclass

import numpy as np
from latticelife.core.geometries import build_adjacency, min_wrap_size
from latticelife.core.lattice import LatticeGrid
from latticelife.core.lifeform import Lifeform
from latticelife.core.rules import Rule

SHAPES = ("square", "hexagon")
# The neighbours as steps: (row, column) on the square, axial (q, r) on the hexagon.
MOORE_STEPS = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0))
AXIAL_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))
PROJECTIONS = ("identity", "decimate", "parity")


@dataclass(frozen=True)
class World:
    """A rule (a B/S string) on the wrapped side x side grid of `shape`, with every neighbour
    `dilation` cells away."""

    shape: str
    rule: str
    side: int
    dilation: int = 1

    def __post_init__(self) -> None:
        if self.shape not in SHAPES:
            raise ValueError(f"no scale-up geometry for shape {self.shape!r}")
        if self.dilation < 1:
            raise ValueError(f"a dilation is at least 1 (got {self.dilation})")
        if self.shape == "hexagon" and self.side % 2:
            raise ValueError(f"a wrapped hexagon grid has an even side (got {self.side})")
        width, height = min_wrap_size(self.shape)
        if self.side < max(width, height):
            raise ValueError(f"a wrapped {self.shape} grid has side at least {max(width, height)}")

    @property
    def cells(self) -> int:
        return self.side * self.side


@dataclass(frozen=True)
class Projection:
    kind: str
    block: int = 1
    offset: tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        if self.kind not in PROJECTIONS:
            raise ValueError(f"unknown projection {self.kind!r}")
        if self.block < 1 or (self.kind == "identity" and self.block != 1):
            raise ValueError(f"no {self.kind} projection with block {self.block}")
        if not all(0 <= a < self.block for a in self.offset):
            raise ValueError(f"offset {self.offset} lies outside a block of {self.block}")


# --- geometry ----------------------------------------------------------------------------------


def hexagon_axial(side: int) -> tuple[np.ndarray, np.ndarray]:
    """Axial (q, r) of every cell of LatticeLife's hexagon grid, by cell index."""
    index = np.arange(side * side)
    row, column = index // side, index % side
    return column, row - column // 2


def hexagon_cell(q: np.ndarray, r: np.ndarray, side: int) -> np.ndarray:
    """The cell index at axial (q, r) on the torus of `side`. The row is taken from the
    unreduced q: (q + n, r - n/2) is the same cell as (q, r)."""
    q, r = np.asarray(q), np.asarray(r)
    return ((r + q // 2) % side) * side + q % side


def dilated_adjacency(shape: str, side: int, k: int) -> np.ndarray:
    """The (cells, degree) adjacency array with every neighbour `k` steps away, built from the
    steps above. At k = 1 it is LatticeLife's own array, up to the order of a cell's
    neighbours."""
    if shape == "square":
        index = np.arange(side * side)
        row, column = index // side, index % side
        columns = [
            ((row + k * dr) % side) * side + (column + k * dc) % side for dr, dc in MOORE_STEPS
        ]
    else:
        q, r = hexagon_axial(side)
        columns = [hexagon_cell(q + k * dq, r + k * dr, side) for dq, dr in AXIAL_STEPS]
    return np.stack(columns, axis=1).astype(np.int32)


@functools.lru_cache(maxsize=8)
def adjacency(world: World) -> np.ndarray:
    """The adjacency array of `world`: LatticeLife's own at dilation 1, `dilated_adjacency`
    otherwise. Read-only, and shared by every run of the world."""
    if world.dilation == 1:
        neighbours = build_adjacency(world.shape, world.side, world.side, True)
    else:
        neighbours = dilated_adjacency(world.shape, world.side, world.dilation)
    neighbours.setflags(write=False)
    return neighbours


def coarse_side(shape: str, side: int, block: int) -> int:
    """The side of the grid a block-`block` projection of a side-`side` grid lands on."""
    if side % block:
        raise ValueError(f"a block of {block} does not divide a side of {side}")
    coarse = side // block
    if shape == "hexagon" and coarse % 2:
        raise ValueError(
            f"on the hexagon a block of {block} needs a side divisible by {2 * block} (got {side})"
        )
    World(shape, "B/S", coarse)  # raises when LatticeLife has no wrapped grid that small
    return coarse


@functools.lru_cache(maxsize=64)
def sample_cells(shape: str, side: int, block: int, offset: tuple[int, int] = (0, 0)) -> np.ndarray:
    """For every supercell, in the coarse grid's own cell order, the index of the fine cell at
    `offset` in its block."""
    coarse = coarse_side(shape, side, block)
    index = np.arange(coarse * coarse)
    row, column = index // coarse, index % coarse
    if shape == "square":
        cells = ((block * row + offset[0]) % side) * side + (block * column + offset[1]) % side
    else:
        q, r = column, row - column // 2
        cells = hexagon_cell(block * q + offset[0], block * r + offset[1], side)
    cells.setflags(write=False)
    return cells


@functools.lru_cache(maxsize=16)
def block_cells(shape: str, side: int, block: int) -> np.ndarray:
    """A (block * block, supercells) array: every fine cell of every supercell's block."""
    cells = np.stack(
        [sample_cells(shape, side, block, (i, j)) for i in range(block) for j in range(block)]
    )
    cells.setflags(write=False)
    return cells


def project(shape: str, side: int, projection: Projection, cells: np.ndarray) -> np.ndarray:
    """The coarse configuration `projection` reads off the fine configuration `cells` (0/1 by
    cell index), as 0/1 by the coarse grid's cell index."""
    cells = np.asarray(cells)
    if cells.shape != (side * side,):
        raise ValueError(f"expected {side * side} cells, got an array of shape {cells.shape}")
    if projection.kind == "identity":
        return cells.astype(np.int8)
    if projection.kind == "decimate":
        chosen = sample_cells(shape, side, projection.block, tuple(projection.offset))
        return cells[chosen].astype(np.int8)
    blocks = cells[block_cells(shape, side, projection.block)].astype(np.int8)
    return np.bitwise_xor.reduce(blocks, axis=0)


# --- running -----------------------------------------------------------------------------------


class Run:
    """One world running from a given configuration, on LatticeLife's update rule."""

    def __init__(self, world: World, cells: np.ndarray, neighbours: np.ndarray | None = None):
        cells = np.asarray(cells)
        if cells.shape != (world.cells,) or not np.isin(cells, (0, 1)).all():
            raise ValueError(f"expected {world.cells} cells of 0 and 1")
        self.world = world
        self.grid = LatticeGrid(
            [Lifeform(id=1, rule=Rule.from_bs_string(world.rule))],
            world.shape,
            world.side,
            world.side,
            True,
            adjacency=adjacency(world) if neighbours is None else neighbours,
        )
        self.grid.occupancy = cells.astype(np.int8)
        # One species: the update draws tie-break keys and never needs them.
        self._rng = np.random.default_rng(0)
        self.generation = 0

    def advance(self, generations: int) -> np.ndarray:
        for _ in range(generations):
            self.grid.step(self._rng)
        self.generation += generations
        return self.cells

    @property
    def cells(self) -> np.ndarray:
        return self.grid.occupancy


def random_start(shape: str, side: int, seed: int) -> np.ndarray:
    """A uniformly random configuration (every cell 0 or 1 with probability 1/2, independently),
    reproducible from the shape, the side and the seed."""
    entropy = [20261123, SHAPES.index(shape), side, seed]
    return np.random.default_rng(entropy).integers(0, 2, size=side * side, dtype=np.int8)


def digest(cells: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(cells, dtype=np.int8).tobytes()).hexdigest()


@dataclass(frozen=True)
class Diagram:
    """One closure test, as the square of maps that should commute: the fine world's `clock`
    generations against one generation of the coarse world, through `projection`."""

    fine: World
    coarse: World
    projection: Projection
    clock: int

    def __post_init__(self) -> None:
        if self.fine.shape != self.coarse.shape:
            raise ValueError("the fine and coarse worlds must share a shape")
        expected = coarse_side(self.fine.shape, self.fine.side, self.projection.block)
        if self.coarse.side != expected:
            raise ValueError(
                f"a block of {self.projection.block} on side {self.fine.side} gives side "
                f"{expected}, not the coarse world's {self.coarse.side}"
            )
        if self.clock < 1:
            raise ValueError("the clock is at least one generation")


@dataclass(frozen=True)
class Closure:
    """What one closure test showed: for s = 1, 2, ... coarse generations, the supercells where
    the two routes differ, and the live supercells on the fine route (a test of two dead grids
    says nothing)."""

    mismatches: tuple[int, ...]
    live: tuple[int, ...]
    supercells: int


def closure(
    tests: list[Diagram], start: np.ndarray, coarse_steps: int
) -> tuple[list[Closure], str]:
    """Run the tests from `start` for `coarse_steps` coarse generations. They must share their
    fine world and clock, which is then run once. Returns each test's Closure, and the sha256 of
    the fine world's last configuration."""
    if not tests:
        raise ValueError("no tests to run")
    fine, clock = tests[0].fine, tests[0].clock
    if any(t.fine != fine or t.clock != clock for t in tests):
        raise ValueError("tests run together must share their fine world and clock")
    shape, side = fine.shape, fine.side
    coarse_runs = [Run(t.coarse, project(shape, side, t.projection, start)) for t in tests]
    fine_run = Run(fine, start)
    mismatches: list[list[int]] = [[] for _ in tests]
    live: list[list[int]] = [[] for _ in tests]
    for _ in range(coarse_steps):
        zoomed = fine_run.advance(clock)
        for i, (test, run) in enumerate(zip(tests, coarse_runs, strict=True)):
            seen = project(shape, side, test.projection, zoomed)
            mismatches[i].append(int(np.count_nonzero(seen != run.advance(1))))
            live[i].append(int(np.count_nonzero(seen)))
    results = [
        Closure(tuple(m), tuple(v), t.coarse.cells)
        for m, v, t in zip(mismatches, live, tests, strict=True)
    ]
    return results, digest(fine_run.cells)
