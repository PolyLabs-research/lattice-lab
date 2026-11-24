"""
The zoom-out instrument for worlds of several species (step 4 of docs/scale-up-plan.md).

A fine world is run once. Every `clock` generations each b x b block of it is read into one
supercell, which gives the zoomed-out run: a sequence of small grids. A **coarse rule** is then
learned from zoomed-out runs as a table: for each thing a supercell and its eight neighbours
can look like, how often the supercell was each thing one coarse generation later. The rule is
then tried on starts it was not learned from.

**What a supercell records** (an alphabet):

    leader   the species with the most cells in the block (0: none, or a tie)
    moved    whether any cell of the block differs from one coarse generation before
    live     whether the block holds any live cell
    and pairs of these: leader+moved, live+moved

**The clock is the block** (clock = b) unless told otherwise. A rule whose neighbours are one
step away moves information at most one cell a generation, so in b generations nothing from
outside a block's eight neighbours can reach it: what a block does next is a function of the
fine cells of its 3 x 3 neighbourhood. A table replaces those 9 b^2 cells by nine symbols, and
its errors are what that loses.

**What a table may look at** (a kind), each a coarser view of the one before:

    full      the supercell and its eight neighbours in place, up to the square's symmetries
    total     the supercell, and how many of its neighbours are each symbol
    own       the supercell alone
    nothing   nothing: how often each symbol comes next at all

A table that has not seen a neighbourhood falls back on the next coarser view, and one that
has seen it a few times leans on it (one pseudo-observation of the coarser view's answer).

**Known answers.**

- *Stillness is stable.* In a world that is a function of its grid (one species, or several
  under the standoff), a block whose 3 x 3 neighbourhood did not change over the last coarse
  generation does not change over the next: the same cells give the same cells. So in the
  `moved` alphabet the all-still neighbourhood is followed by still, every time (`unstable`
  counts the exceptions, which must be none).
- *A world that is its own zoom-out.* With every neighbour b steps away (dilation b) the fine
  grid is b^2 interleaved copies of the rule on the grid b times smaller. From a start that is
  uniform on every block the copies stay equal, the blocks stay uniform, and with clock 1 the
  zoomed-out run is the same rule on the small grid, cell for cell. The table learned from it
  is that rule.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass

import numpy as np
from latticelife.core.geometries import build_adjacency
from latticelife.core.lattice import LatticeGrid, TieBreak
from latticelife.core.lifeform import Lifeform
from latticelife.core.rules import Rule
from latticelife.experiments.competition import species_start

ALPHABETS = ("leader", "moved", "live", "leader+moved", "live+moved")
KINDS = ("nothing", "own", "total", "full")  # each a coarser view than the next
# the eight neighbours around the ring: N, NE, E, SE, S, SW, W, NW, as (row step, column step)
RING = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
MIRROR = (0, 7, 6, 5, 4, 3, 2, 1)  # the ring seen in a mirror that keeps N and S in place


# --- fine worlds ---------------------------------------------------------------------------------


def lattice(rules: Sequence[str], kind: str, side: int, dilation: int = 1) -> LatticeGrid:
    """A wrapped square grid of `side` running one B/S rule per species under the tie-break
    `kind`, with every neighbour `dilation` steps away."""
    lifeforms = [Lifeform(i + 1, Rule.from_bs_string(rule)) for i, rule in enumerate(rules)]
    adjacency = None
    if dilation != 1:
        adjacency = build_adjacency("square", side, side, True, dilation=dilation)
    return LatticeGrid(
        lifeforms, "square", side, side, True, adjacency=adjacency, tie_break=TieBreak(kind, 2, 1.0)
    )


def mixed_start(side: int, seed: int, species: int, density: float = 0.5) -> np.ndarray:
    """LatticeLife's own start for several species: every cell live with probability `density`,
    a live cell each species with equal chance."""
    return species_start("square", side, density, seed, None, species)


def uniform_blocks(side: int, block: int, seed: int, species: int) -> np.ndarray:
    """A start that is one thing on every block: `mixed_start` on the grid `block` times
    smaller, each of its cells spread over a block."""
    small = mixed_start(side // block, seed, species).reshape(side // block, side // block)
    return np.repeat(np.repeat(small, block, axis=0), block, axis=1).reshape(-1)


def read(occupancy: np.ndarray, side: int, block: int, species: int) -> np.ndarray:
    """Each species' cells in every block: a (species, n, n) array for the n x n supercells."""
    n = side // block
    blocks = occupancy.reshape(n, block, n, block)
    return np.stack(
        [(blocks == s).sum(axis=(1, 3), dtype=np.uint16) for s in range(1, species + 1)]
    )


@dataclass
class History:
    """A fine run read through blocks of `block` every `clock` generations: at each coarse
    generation every species' cells per block, and whether any cell of the block differs from
    one coarse generation before (all False at generation 0, where there is no before)."""

    block: int
    clock: int
    counts: np.ndarray  # (steps + 1, species, n, n)
    moved: np.ndarray  # (steps + 1, n, n)

    @property
    def steps(self) -> int:
        return self.counts.shape[0] - 1


def histories(
    rules: Sequence[str],
    kind: str,
    side: int,
    start: np.ndarray,
    generations: int,
    blocks: Sequence[int],
    clocks: dict[int, int] | None = None,
    dilation: int = 1,
    seed: int = 0,
) -> dict[int, History]:
    """Run the fine world once from `start` and read it through every block in `blocks`, each
    at its own clock (the block itself unless `clocks` says otherwise). `seed` names the
    tie-break's draws, as `latticelife.experiments.competition` names them."""
    clocks = {b: (clocks or {}).get(b, b) for b in blocks}
    for b in blocks:
        if side % b or generations % clocks[b]:
            raise ValueError(
                f"block {b} (clock {clocks[b]}) does not divide {side} x {generations}"
            )
    species = len(rules)
    grid = lattice(rules, kind, side, dilation)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])
    counts = {b: [read(grid.occupancy, side, b, species)] for b in blocks}
    moved = {b: [np.zeros((side // b, side // b), dtype=bool)] for b in blocks}
    before = {b: grid.occupancy.copy() for b in blocks}
    for generation in range(1, generations + 1):
        grid.step(rng)
        for b in blocks:
            if generation % clocks[b]:
                continue
            n = side // b
            counts[b].append(read(grid.occupancy, side, b, species))
            changed = (grid.occupancy != before[b]).reshape(n, b, n, b).any(axis=(1, 3))
            moved[b].append(changed)
            before[b] = grid.occupancy.copy()
    return {b: History(b, clocks[b], np.stack(counts[b]), np.stack(moved[b])) for b in blocks}


# --- alphabets -----------------------------------------------------------------------------------


def leaders(counts: np.ndarray) -> np.ndarray:
    """The species with the most cells in each block, from counts with the species on axis -3:
    0 where no species has a cell, and where two or more share the top."""
    top = counts.max(axis=-3)
    alone = (counts == np.expand_dims(top, -3)).sum(axis=-3) == 1
    return np.where((top > 0) & alone, counts.argmax(axis=-3) + 1, 0).astype(np.int8)


def states(history: History, alphabet: str) -> tuple[np.ndarray, int, int]:
    """The zoomed-out run in `alphabet`: a (steps + 1, n, n) array of symbols, how many symbols
    there are, and the first coarse generation at which they are all defined (1 for an alphabet
    that looks at `moved`)."""
    species = history.counts.shape[1]
    moved = history.moved.astype(np.int8)
    if alphabet == "leader":
        return leaders(history.counts), species + 1, 0
    if alphabet == "live":
        return (history.counts.sum(axis=1) > 0).astype(np.int8), 2, 0
    if alphabet == "moved":
        return moved, 2, 1
    if alphabet == "leader+moved":
        return (2 * leaders(history.counts) + moved).astype(np.int8), 2 * (species + 1), 1
    if alphabet == "live+moved":
        return (2 * (history.counts.sum(axis=1) > 0) + moved).astype(np.int8), 4, 1
    raise ValueError(f"unknown alphabet {alphabet!r} (one of {', '.join(ALPHABETS)})")


# --- what a table looks at -----------------------------------------------------------------------


def ring(symbols: np.ndarray) -> np.ndarray:
    """The eight neighbours of every supercell on the wrapped grid, around the ring: an array
    with a leading axis of 8 over `symbols`, whose last two axes are the grid."""
    return np.stack([np.roll(symbols, (-dr, -dc), axis=(-2, -1)) for dr, dc in RING])


def codes(kind: str, own: np.ndarray, around: np.ndarray, q: int) -> np.ndarray:
    """One number per supercell for what a table of `kind` sees there: equal numbers, equal
    views."""
    own = own.astype(np.int64)
    if kind == "nothing":
        return np.zeros_like(own)
    if kind == "own":
        return own
    if kind == "total":
        code = own
        for symbol in range(1, q):
            code = code * 9 + (around == symbol).sum(axis=0)
        return code
    if kind == "full":
        weights = q ** np.arange(8, dtype=np.int64)
        best = None
        for order in (around, around[list(MIRROR)]):
            for turn in range(4):  # a quarter turn moves the ring on by two places
                turned = np.roll(order, 2 * turn, axis=0).astype(np.int64)
                code = np.tensordot(weights, turned, axes=(0, 0))
                best = code if best is None else np.minimum(best, code)
        return own * q**8 + best
    raise ValueError(f"unknown kind {kind!r} (one of {', '.join(KINDS)})")


def transitions(
    symbols: np.ndarray, first: int = 0, last: int | None = None, chunk: int = 8
) -> Iterator[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Every (supercell, its eight neighbours, the supercell one coarse generation later) of a
    zoomed-out run, from coarse generation `first` up to but not including `last`, a few
    generations at a time."""
    end = symbols.shape[0] - 1 if last is None else min(last, symbols.shape[0] - 1)
    for a in range(first, end, chunk):
        b = min(a + chunk, end)
        yield symbols[a:b], ring(symbols[a:b]), symbols[a + 1 : b + 1]


# --- tables --------------------------------------------------------------------------------------


@dataclass
class Table:
    """How often each symbol came next, for every view seen: `rows` are the views' codes in
    order, `counts[i]` the tally after `rows[i]`."""

    q: int
    rows: np.ndarray
    counts: np.ndarray

    @classmethod
    def empty(cls, q: int) -> Table:
        return cls(q, np.zeros(0, dtype=np.int64), np.zeros((0, q), dtype=np.int64))

    def add(self, view: np.ndarray, after: np.ndarray) -> Table:
        """This table with more transitions tallied in."""
        keys, tally = np.unique(view.ravel() * self.q + after.ravel(), return_counts=True)
        rows = np.union1d(self.rows, keys // self.q)
        counts = np.zeros((rows.size, self.q), dtype=np.int64)
        counts[np.searchsorted(rows, self.rows)] = self.counts
        np.add.at(counts, (np.searchsorted(rows, keys // self.q), keys % self.q), tally)
        return Table(self.q, rows, counts)

    def plus(self, other: Table) -> Table:
        """The two tables' tallies together."""
        rows = np.union1d(self.rows, other.rows)
        counts = np.zeros((rows.size, self.q), dtype=np.int64)
        counts[np.searchsorted(rows, self.rows)] += self.counts
        counts[np.searchsorted(rows, other.rows)] += other.counts
        return Table(self.q, rows, counts)

    def after(self, view: np.ndarray) -> np.ndarray:
        """The tallies after each view in `view` (zeros for a view never seen): shape
        view.shape + (q,)."""
        flat = view.ravel()
        if self.rows.size == 0:
            return np.zeros(view.shape + (self.q,), dtype=np.int64)
        at = np.minimum(np.searchsorted(self.rows, flat), self.rows.size - 1)
        found = self.counts[at] * (self.rows[at] == flat)[:, None]
        return found.reshape(view.shape + (self.q,))


@dataclass
class CoarseRule:
    """A coarse rule in one alphabet: the same transitions tallied by each kind of view."""

    q: int
    tables: dict[str, Table]

    @classmethod
    def empty(cls, q: int) -> CoarseRule:
        return cls(q, {kind: Table.empty(q) for kind in KINDS})

    def learn(self, symbols: np.ndarray, first: int = 0, last: int | None = None) -> CoarseRule:
        """This rule with one more zoomed-out run tallied in."""
        tables = dict(self.tables)
        for own, around, after in transitions(symbols, first, last):
            for kind in KINDS:
                tables[kind] = tables[kind].add(codes(kind, own, around, self.q), after)
        return CoarseRule(self.q, tables)

    def plus(self, other: CoarseRule) -> CoarseRule:
        """The rule learned from both rules' runs."""
        return CoarseRule(self.q, {k: self.tables[k].plus(other.tables[k]) for k in KINDS})

    def chances(self, kind: str, own: np.ndarray, around: np.ndarray) -> np.ndarray:
        """For every supercell the chance of each symbol next, as a table of `kind` gives it:
        its own tally, with one pseudo-observation of the next coarser view's answer."""
        answer = np.full(own.shape + (self.q,), 1.0 / self.q)
        for level in KINDS[: KINDS.index(kind) + 1]:
            tally = self.tables[level].after(codes(level, own, around, self.q)).astype(float)
            answer = (tally + answer) / (tally.sum(axis=-1, keepdims=True) + 1.0)
        return answer

    def step(
        self, kind: str, symbols: np.ndarray, rng: np.random.Generator | None = None
    ) -> np.ndarray:
        """One coarse generation of the n x n grid `symbols` under the table of `kind`: the
        likeliest symbol for every supercell, or with `rng` a draw from the table's chances."""
        chance = self.chances(kind, symbols, ring(symbols))
        if rng is None:
            return chance.argmax(axis=-1).astype(np.int8)
        ladder = chance.cumsum(axis=-1)
        draw = rng.random(symbols.shape)[..., None] * ladder[..., -1:]
        return np.minimum((draw >= ladder).sum(axis=-1), self.q - 1).astype(np.int8)

    def score(
        self, kind: str, symbols: np.ndarray, first: int = 0, last: int | None = None
    ) -> dict:
        """How well the table of `kind` foretells a zoomed-out run it may not have seen: the
        transitions, how many it called right (its likeliest symbol came), and the bits of
        surprise it had in all (the sum of -log2 of the chance it gave to what came)."""
        seen = right = 0
        bits = 0.0
        for own, around, after in transitions(symbols, first, last):
            chance = self.chances(kind, own, around)
            seen += after.size
            right += int((chance.argmax(axis=-1) == after).sum())
            given = np.take_along_axis(chance, after[..., None].astype(np.int64), axis=-1)
            bits += float(-np.log2(given).sum())
        return {"transitions": seen, "right": right, "bits": bits}


def horizons(steps: int) -> list[int]:
    """The coarse generations ahead at which a run-on is read: 1, 2, 4, ... and the last."""
    out, h = [], 1
    while h < steps:
        out.append(h)
        h *= 2
    return [*out, steps]


def follow(
    rule: CoarseRule,
    kind: str,
    symbols: np.ndarray,
    first: int,
    rng: np.random.Generator,
    draws: int = 2,
) -> dict:
    """The coarse rule run on by itself from coarse generation `first` of a zoomed-out run, by
    its likeliest symbol and by `draws` draws. At each horizon: the share of supercells whose
    symbol is odd (moved, in an alphabet that ends in it), in the fine world, in the
    likeliest-symbol run and on average in the drawn ones; the share of supercells where the
    likeliest-symbol run differs from the fine world; and the share where the fine world
    differs from where it started."""
    truth = symbols[first:]
    steps = truth.shape[0] - 1
    marks = set(horizons(steps))
    likely = truth[0]
    drawn = [truth[0]] * draws
    out: dict = {"horizon": [], "fine": [], "likely": [], "drawn": [], "differ": [], "drifted": []}
    for h in range(1, steps + 1):
        likely = rule.step(kind, likely)
        drawn = [rule.step(kind, grid, rng) for grid in drawn]
        if h in marks:
            out["horizon"].append(h)
            out["fine"].append(float((truth[h] % 2).mean()))
            out["likely"].append(float((likely % 2).mean()))
            out["drawn"].append(float(np.mean([(grid % 2).mean() for grid in drawn])))
            out["differ"].append(float((likely != truth[h]).mean()))
            out["drifted"].append(float((truth[0] != truth[h]).mean()))
    return out


def unstable(history: History) -> int:
    """The supercells that moved in a coarse generation although neither they nor any of their
    eight neighbours had moved in the one before. None, in a world that is a function of its
    grid read with a clock no longer than the block."""
    moved = history.moved
    quiet = ~(moved[1:-1] | ring(moved[1:-1]).any(axis=0))
    return int((quiet & moved[2:]).sum())
