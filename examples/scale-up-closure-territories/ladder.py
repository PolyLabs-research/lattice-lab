"""
The design the registered test of worlds of territories shares with its sizing look.

`study.py` registers and runs the test; `sizing.py` puts the first look's own runs through the
same measures, to see how far each moves from one set of starts to another before any bound
is drawn. Both read a world as the first look did (look.py): two species with one rule
between them, on a wrapped grid, zoomed out by blocks, a block being whoever leads it.

**A fine run** (`fine`) is read through blocks of 4, 8, 16 and 32 every `block` generations
and kept on disk outside the repository. What goes on record is not the grids but tallies.

**A tally** (`tally`) counts transitions at one block and one tick (the fine generations in a
coarse generation): for every [leader of the block][neighbours species 1 leads][neighbours
species 2 leads], how often the block was led by nobody, species 1 or species 2 one tick
later. A coarse rule is a tally (`rule_of`), a rule is scored on another tally (`surprise`,
`excess`), and the chance of changing hands is read off one (`hands`), so every number but
those of a run-on can be worked out again from the records.

**Windows.** Transitions are tallied apart over three stretches of the run, so that the same
records give a rule learned early and tried late, and the rungs at matched ages:

    A   generations 64 to 256       blocks of 4 at their matched age
    B   256 to 1,024                blocks of 8
    C   1,024 to 4,096              blocks of 16; and the stretch a rule is run on over

**Ticks.** Every block is read on the block clock (tick = block) and the square clock (tick =
block x block / 4). Blocks of 8 and 16 are read at further ticks as well, so that one world's
rule can be tried in another world at a slower or a quicker pace.

**A run-on** (`ahead`) starts from the zoomed-out world at generation 1,024 and draws every
block's next leader from a rule's table, with no fine cells under it, to the last generation
its tick reaches. It is read as the first look read it: the walls it keeps beside the real
world's, and the blocks whose leader is not the real world's, beside the same for the start
had nothing moved and for a second run of the rule with other draws.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scale-up-closure"))

import zoom  # noqa: E402

CACHE = Path.home() / "lattice-lab-runs" / "closure-territories" / "cache"
SIDE, GENERATIONS = 1024, 4096
BLOCKS = (4, 8, 16, 32)
Q = 3  # a block is led by nobody (0), species 1 or species 2
WINDOWS = {"A": (64, 256), "B": (256, 1024), "C": (1024, 4096)}
EARLY, LATE, WHOLE = ("A", "B"), ("C",), ("A", "B", "C")
MATCHED = {4: ("A",), 8: ("B",), 16: ("C",)}  # the stretch each block has its matched age in
EVERY = 16  # a transition is read every so many generations at least
TICKS = {4: (4,), 8: (8, 16, 32, 64), 16: (16, 32, 64, 128, 256), 32: (32, 256)}
FROM = WINDOWS["C"][0]  # the generation a coarse rule is run on from
NEAR = (4, 5, 6)  # the numbers of rival-led neighbours at which two worlds' chances are compared


def square(block: int) -> int:
    """The tick of the square clock at blocks of `block`."""
    return block * block // 4


def key(block: int, tick: int) -> str:
    return f"{block} {tick}"


# --- fine runs -----------------------------------------------------------------------------------


def cache_path(tag: str, seed: int, side: int, generations: int) -> Path:
    return CACHE / f"registered-{tag}-{side}-{generations}-{seed}.npz"


def fine(
    tag: str,
    rule: str,
    density: float,
    seed: int,
    side: int = SIDE,
    generations: int = GENERATIONS,
    blocks: tuple[int, ...] = BLOCKS,
) -> dict:
    """`rule` against a copy of itself under the standoff, from one start (every cell live
    with chance `density`, a live cell either species with equal chance), read through every
    block every `block` generations: for each block the leader of every block at every
    reading, and every 64 generations each species' share of the grid. Kept on disk under
    `tag`, and read from there if it is."""
    path = cache_path(tag, seed, side, generations)
    if path.exists():
        with np.load(path) as kept:
            return {"shares": kept["shares"], **{b: kept[f"leaders_{b}"] for b in blocks}}
    grid = zoom.lattice((rule, rule), "standoff", side)
    start = zoom.mixed_start(side, seed, 2, density=density)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])  # the standoff draws nothing
    frames = {b: [zoom.leaders(zoom.read(grid.occupancy, side, b, 2))] for b in blocks}
    shares = []
    for generation in range(1, generations + 1):
        grid.step(rng)
        for b in blocks:
            if generation % b == 0:
                frames[b].append(zoom.leaders(zoom.read(grid.occupancy, side, b, 2)))
        if generation % 64 == 0:
            shares.append([float((grid.occupancy == s).mean()) for s in (1, 2)])
    out = {"shares": np.array(shares), **{b: np.stack(frames[b]) for b in blocks}}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, shares=out["shares"],
                        **{f"leaders_{b}": out[b] for b in blocks})  # fmt: skip
    return out


# --- tallies -------------------------------------------------------------------------------------


def instants(block: int, tick: int, first: int, last: int) -> list[int]:
    """The generations at which a transition of `tick` generations is read between `first`
    and `last`: one after another, but no more often than every EVERY generations."""
    start = -(-first // block) * block
    return list(range(start, last - tick + 1, max(tick, EVERY)))


def tally(frames: np.ndarray, block: int, tick: int, first: int, last: int) -> np.ndarray:
    """The transitions of one run at one block and tick between two generations, counted by
    [leader][neighbours species 1 leads][neighbours species 2 leads][leader one tick on]: a
    3 x 9 x 9 x 3 array. `frames` holds the run's leaders every `block` generations."""
    at = np.array(instants(block, tick, first, last), dtype=np.int64)
    counts = np.zeros(Q * 81 * Q, dtype=np.int64)
    for a in range(0, at.size, 8):
        own = frames[at[a : a + 8] // block]
        after = frames[(at[a : a + 8] + tick) // block]
        view = zoom.codes("total", own, zoom.ring(own), Q)
        counts += np.bincount((view * Q + after).ravel(), minlength=counts.size)
    return counts.reshape(Q, 9, 9, Q)


def sparse(counts: np.ndarray) -> list[list[int]]:
    """A tally as its rows that hold anything: [view, then the count of each next leader]."""
    flat = np.asarray(counts).reshape(Q * 81, Q)
    return [[int(i), *map(int, flat[i])] for i in np.flatnonzero(flat.sum(axis=1))]


def dense(rows: list[list[int]]) -> np.ndarray:
    """The tally `sparse` wrote down."""
    counts = np.zeros((Q * 81, Q), dtype=np.int64)
    for view, *after in rows:
        counts[view] = after
    return counts.reshape(Q, 9, 9, Q)


def tallies(leaders: dict, generations: int = GENERATIONS, blocks=BLOCKS) -> dict:
    """Every tally of one run: by block and tick, then by window (those the run reaches)."""
    out: dict = {}
    for block in blocks:
        for tick in TICKS[block]:
            out[key(block, tick)] = {
                name: sparse(tally(leaders[block], block, tick, first, last))
                for name, (first, last) in WINDOWS.items()
                if last <= generations
            }
    return out


def walls(grid: np.ndarray) -> float:
    """The share of neighbouring pairs of blocks, across and down the wrapped grid, whose
    leaders differ."""
    across = grid != np.roll(grid, -1, axis=-1)
    down = grid != np.roll(grid, -1, axis=-2)
    return float((across.mean() + down.mean()) / 2)


def start_record(
    world: str, seed: int, found: dict, side: int = SIDE, generations: int = GENERATIONS,
    blocks: tuple[int, ...] = BLOCKS,
) -> dict:  # fmt: skip
    """What goes on record of one fine run: its tallies, and at the first and the last
    generation of each window the share of the grid that is live, the larger species' share
    of it, and the walls at every block."""
    marks = sorted({g for window in WINDOWS.values() for g in window if g <= generations})
    shares = found["shares"]
    return {
        "kind": "start",
        "world": world,
        "seed": seed,
        "side": side,
        "generations": generations,
        "live": {str(g): round(float(shares[g // 64 - 1].sum()), 6) for g in marks},
        "larger": {str(g): round(float(shares[g // 64 - 1].max()), 6) for g in marks},
        "walls": {str(b): {str(g): round(walls(found[b][g // b]), 6) for g in marks}
                  for b in blocks},
        "tally": tallies(found, generations, blocks),
    }  # fmt: skip


# --- rules from tallies --------------------------------------------------------------------------


def rule_of(counts: np.ndarray) -> zoom.CoarseRule:
    """The instrument's coarse rule that a tally stands for: its tables that know nothing,
    the block alone, and the block with its neighbour counts."""
    counts = np.asarray(counts, dtype=np.int64)
    tables = {
        "nothing": zoom.Table(Q, np.zeros(1, dtype=np.int64), counts.sum(axis=(0, 1, 2))[None]),
        "own": zoom.Table(Q, np.arange(Q), counts.sum(axis=(1, 2))),
        "total": zoom.Table(Q, np.arange(Q * 81), counts.reshape(Q * 81, Q)),
        "full": zoom.Table.empty(Q),
    }
    return zoom.CoarseRule(Q, tables)


def chances(counts: np.ndarray, kind: str = "total") -> np.ndarray:
    """The chance the rule of a tally gives each next leader, for every [leader][neighbours
    of 1][neighbours of 2]: the instrument's own arithmetic (`zoom.CoarseRule.chances`: each
    view's tally with one pseudo-observation of the coarser view's answer), on the whole
    table at once. The tally may be scaled down, for a rule that has learned from less."""
    counts = np.asarray(counts, dtype=float)
    answer = np.full(counts.shape, 1.0 / Q)
    nothing = counts.sum(axis=(0, 1, 2))
    answer = (nothing + answer) / (nothing.sum() + 1.0)
    if kind == "nothing":
        return answer
    own = counts.sum(axis=(1, 2))[:, None, None, :]
    answer = (own + answer) / (own.sum(axis=-1, keepdims=True) + 1.0)
    if kind == "own":
        return answer
    if kind != "total":
        raise ValueError(f"a tally holds no table of kind {kind!r}")
    return (counts + answer) / (counts.sum(axis=-1, keepdims=True) + 1.0)


def score(rule_counts: np.ndarray, trial_counts: np.ndarray, kind: str = "total") -> dict:
    """How the rule of one tally does on the transitions of another: how many there are, how
    many it calls right (its likeliest next leader came), and its surprise in bits in all."""
    trial = np.asarray(trial_counts, dtype=np.int64)
    chance = chances(rule_counts, kind)
    right = np.take_along_axis(trial, chance.argmax(axis=-1)[..., None], axis=-1).sum()
    return {
        "transitions": int(trial.sum()),
        "right": int(right),
        "bits": float(-(trial * np.log2(chance)).sum()),
    }


def surprise(rule_counts: np.ndarray, trial_counts: np.ndarray, kind: str = "total") -> float:
    """The bits a transition of the trial tally costs the rule, on average."""
    found = score(rule_counts, trial_counts, kind)
    return found["bits"] / max(found["transitions"], 1)


def excess(rule_counts, own_counts, trial_counts, kind: str = "total") -> float:
    """The surprise of a rule from elsewhere on a trial tally, over that of the rule learned
    where the trial comes from, less one: 0 for a rule that serves as well. Not a number if
    the trial tally is empty."""
    own = surprise(own_counts, trial_counts, kind)
    return surprise(rule_counts, trial_counts, kind) / own - 1 if own > 0 else float("nan")


def as_much(rule_counts: np.ndarray, own_counts: np.ndarray) -> np.ndarray:
    """A rule's tally scaled down to as many transitions as another rule learned from, so that
    it does not win by having seen more. Left as it is if it has seen no more."""
    rule_counts = np.asarray(rule_counts, dtype=float)
    keep = np.asarray(own_counts).sum() / max(rule_counts.sum(), 1.0)
    return rule_counts * min(keep, 1.0)


def hands(counts: np.ndarray) -> np.ndarray:
    """Changing hands, from a tally: for each number of a block's eight neighbours that its
    rival leads, how many blocks with a leader there were and how many had another leader,
    or none, one tick on. A (9, 2) array."""
    counts = np.asarray(counts, dtype=np.int64)
    out = np.zeros((9, 2), dtype=np.int64)
    for own in (1, 2):
        # for species 1 the rival's neighbours are the second count, for species 2 the first
        by_rival = counts[own].sum(axis=0) if own == 1 else counts[own].sum(axis=1)
        out[:, 0] += by_rival.sum(axis=-1)
        out[:, 1] += by_rival.sum(axis=-1) - by_rival[:, own]
    return out


def changes(counts: np.ndarray, near: int) -> float | None:
    """The chance that a block with `near` rival-led neighbours changes hands in one tick."""
    blocks, changed = hands(counts)[near]
    return float(changed / blocks) if blocks else None


# --- a rule run on by itself ---------------------------------------------------------------------


def digest(counts: np.ndarray) -> str:
    return hashlib.sha256(json.dumps(sparse(counts)).encode()).hexdigest()


def ahead(
    frames: np.ndarray,
    counts: np.ndarray,
    block: int,
    tick: int,
    draws: tuple[int, ...],
    first: int = FROM,
    generations: int = GENERATIONS,
) -> dict:
    """The rule of a tally run on by itself from generation `first` of one run's leaders at
    `block`, a coarse generation being `tick` fine ones. At each horizon (1, 2, 4, ... coarse
    generations and the last): the walls of the real world and of the rule's; and the share of
    blocks whose leader is not the real world's, in the rule's world, in the start had
    nothing moved, and between two runs of the rule that differ in their draws alone.
    `draws` names the two runs' draws."""
    rule = rule_of(counts)
    steps = (generations - first) // tick
    marks = zoom.horizons(steps)
    rng = np.random.default_rng([20261126, *draws, 0])
    again = np.random.default_rng([20261126, *draws, 1])
    start = frames[first // block]
    grid = twin = start
    out: dict = {name: [] for name in ("walls_world", "walls_rule", "apart_rule", "apart_start",
                                       "apart_twin")}  # fmt: skip
    for h in range(1, steps + 1):
        grid = rule.step("total", grid, rng)
        twin = rule.step("total", twin, again)
        if h in marks:
            there = frames[(first + h * tick) // block]
            out["walls_world"].append(round(walls(there), 6))
            out["walls_rule"].append(round(walls(grid), 6))
            out["apart_rule"].append(round(float((grid != there).mean()), 6))
            out["apart_start"].append(round(float((start != there).mean()), 6))
            out["apart_twin"].append(round(float((grid != twin).mean()), 6))
    return {
        "block": block,
        "tick": tick,
        "from_generation": first,
        "generations_on": [h * tick for h in marks],
        **out,
        "rule_sha256": digest(counts),
    }
