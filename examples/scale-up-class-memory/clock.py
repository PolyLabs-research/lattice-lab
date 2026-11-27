"""
A world read on its own clock: the runs and the reading shared by the sizing look and the
registered test of this folder (study.py).

Step 4f read every world at the still world's tick and slowed the still world's rule to each
world's pace. With a rule that remembers, "how long a block has had its leader" is counted in
ticks, so the tick has to mean the same thing in every world. Here it is the world that is
read at its own pace, and the rule that stays as it is:

- **A world's tick.** The still world, through blocks of 8, has a share `STARTS_AT` of its
  neighbouring blocks under different leaders at generation 256, when the matched age of
  blocks of 8 begins (16 ticks of 16 generations). A world's tick is the sixteenth part of
  the generation at which its own walls have thinned to that share: a world whose walls move
  at half the pace gets a tick twice as long.
- **Its window.** From 16 of its ticks to 64, as the still world's matched age runs from 16
  ticks to 64: 48 ticks in every world, and "how long" means the same in each.

A world whose walls have not thinned to that share by the generation a window can still
start at has no tick here, and no claim is made of it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MEMORY = HERE.parent / "scale-up-memory"


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold several study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


look = _module("scale_up_memory_look", MEMORY / "look.py")
ladder, zoom = look.ladder, look.zoom

SIDE, GENERATIONS = 1024, 5120
BLOCK = 8  # every world is read through blocks of 8
EVERY = 2  # the generations between readings of a block: a tick is a whole number of these
WALLS_EVERY = 64  # the generations between readings of a world's walls
FIRST_TICK, LAST_TICK = 16, 64  # a window runs from this many of a world's ticks to this many
STARTS_AT = 0.1655  # the still world's walls at blocks of 8 when its matched age begins
STILL_TICK = ladder.square(BLOCK)  # the still world's tick at blocks of 8: 16 generations
LONGEST = GENERATIONS // LAST_TICK  # the longest tick whose window ends inside a run


def cache_path(rule: str, seed: int) -> Path:
    tag = rule.replace("/", "-")
    return ladder.CACHE / f"clock-{tag}-{SIDE}-{GENERATIONS}-{seed}.npz"


def fine(rule: str, seed: int) -> dict:
    """`rule` against a copy of itself under the standoff from a full start, read through
    blocks of 8 every two generations: the leader of every block at every reading, and every
    64 generations each species' share of the grid. Kept on disk, and read from there if it
    is."""
    path = cache_path(rule, seed)
    if path.exists():
        with np.load(path) as kept:
            return {"shares": kept["shares"], "leaders": kept["leaders"]}
    grid = zoom.lattice((rule, rule), "standoff", SIDE)
    start = zoom.mixed_start(SIDE, seed, 2, density=1.0)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])  # the standoff draws nothing
    frames = [zoom.leaders(zoom.read(grid.occupancy, SIDE, BLOCK, 2))]
    shares = []
    for generation in range(1, GENERATIONS + 1):
        grid.step(rng)
        if generation % EVERY == 0:
            frames.append(zoom.leaders(zoom.read(grid.occupancy, SIDE, BLOCK, 2)))
        if generation % 64 == 0:
            shares.append([float((grid.occupancy == s).mean()) for s in (1, 2)])
    out = {"shares": np.array(shares), "leaders": np.stack(frames)}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, shares=out["shares"], leaders=out["leaders"])
    return out


def walls(leaders: np.ndarray) -> list[float]:
    """A run's walls at blocks of 8 every WALLS_EVERY generations, from the first such
    generation on: the share of neighbouring blocks under different leaders."""
    return [round(ladder.walls(leaders[g // EVERY]), 6)
            for g in range(WALLS_EVERY, GENERATIONS + 1, WALLS_EVERY)]  # fmt: skip


def reaches(thinning: list[float], share: float = STARTS_AT) -> float | None:
    """The generation at which walls read every WALLS_EVERY generations first thin to a
    share, between two readings as a power of time. None if they start below it or never
    get there."""
    if not thinning or thinning[0] <= share:
        return None
    for i in range(1, len(thinning)):
        if thinning[i] <= share:
            before, after = WALLS_EVERY * i, WALLS_EVERY * (i + 1)
            high, low = thinning[i - 1], thinning[i]
            if high <= low:
                return float(after)
            part = np.log(high / share) / np.log(high / low)
            return float(before * (after / before) ** part)
    return None


def tick_of(thinning: list[float]) -> int | None:
    """A world's tick, from its walls: the sixteenth part of the generation at which they
    have thinned to the still world's share at the start of its matched age, to the nearest
    reading. None where a window of that tick would not end inside a run, or the walls say
    no tick."""
    at = reaches(thinning)
    if at is None:
        return None
    tick = max(EVERY, EVERY * round(at / FIRST_TICK / EVERY))
    return tick if tick <= LONGEST else None


def window(tick: int) -> tuple[int, int]:
    """The generations a world of this tick is read and run on over."""
    return FIRST_TICK * tick, LAST_TICK * tick


def tally(reading, leaders: np.ndarray, tick: int) -> np.ndarray:
    """One run's transitions of one tick over its window, read every tick, as a reading sees
    them (`look.tally` on leaders kept every EVERY generations)."""
    first, last = window(tick)
    at = np.arange(first, last - tick + 1, tick, dtype=np.int64)
    size = reading.size * ladder.Q * 81 * ladder.Q
    counts = np.zeros(size, dtype=np.int64)
    for a in range(0, at.size, 8):
        g = at[a : a + 8]
        own = leaders[g // EVERY]
        view = zoom.codes("total", own, zoom.ring(own), ladder.Q)
        past = reading.code(leaders, EVERY, tick, g)
        after = leaders[(g + tick) // EVERY]
        counts += np.bincount(((past * (ladder.Q * 81) + view) * ladder.Q + after).ravel(),
                              minlength=size)  # fmt: skip
    return counts.reshape(reading.size, ladder.Q, 9, 9, ladder.Q)
