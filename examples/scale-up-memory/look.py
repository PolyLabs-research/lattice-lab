"""
A coarse rule that remembers: a first look. Exploratory: nothing here is registered, and no
world is run (only coarse rules are run on).

    uv run --no-sync python examples/scale-up-memory/look.py [--make]

Steps 4d to 4g read a world of territories as who leads each block, and learned its coarse
rule as a table: what a block did next, by its leader and by how many of its eight neighbours
each species leads. Step 4g climbed one rung more (examples/scale-up-rung) and found the rule
still changing from rung to rung, the same way each time, and that what changes is how often
a block on a wall changes hands. It also took a first number: a block that has just come over
to a leader goes back at the next tick far more often than one that has held, which that
table cannot know. Decision D12 of the plan chose to look at the reading that could know.

**A symbol that remembers.** The table is asked the same question of a block with more in
view. Three readings:

    its neighbours             the rule as it is: the leader, and how many of the eight
                               neighbours each species leads
    and its leader one tick    the same, and who led the block one tick ago (the reading
    before                     decision D12 named)
    and how long it has had    the same, and for how many ticks running the block has had
    its leader                 its present leader, counted up to a cap (4, 8 or 16 ticks)

A reading with more in view falls back on one with less where it has seen little, in the
instrument's own way: its tally with one pseudo-observation of the coarser reading's answer.
The coarser reading of "how long" is the same with a cap one tick lower.

**What is read.** The block leaders of step 4g's sixteen runs: the still world and the busy
world, each against its copy under the standoff from a full start, on a wrapped grid of side
2,048 to generation 16,384, eight starts each. Every rung is read at the age that matches its
block, on the square clock, at the instants step 4g's study read it. A matched age runs from
16 ticks of the rung's clock to 64 at every rung, so "how long" means the same at each. With
no past in view the tallies are the registered run's own, to the last count, and the run-ons
are its run-ons, to the last figure: both are checked on the way. The leaders are read from
the cache `study.fine` keeps; a run whose leaders are not there is made again only with
`--make` (an hour and forty minutes of one core).

**Little data at the top.** A grid of side 2,048 has 4,096 blocks of 32. A rule with more in
view has more to learn, and at blocks of 32 what a rule has not yet learned costs it about
as much surprise as the difference this look is after. So every surprise is measured twice,
from all the starts a rule may learn from and from half of them, and told as it is and as it
would be with endless data (what a rule lacks goes as one over how much it has seen: twice
the first less the second). That law is checked too, with a rule that learned from one
start: it holds roughly, and where it does not what a rule lacks falls more slowly, so the
correction is too small. And where step 4g chose four starts to learn from and four to try
on, here every such choice is made (70 of them), and the mean is told with the spread
between choices.

**What is measured.**

- **One tick ahead** (`one_tick`). The bits of surprise a block costs each reading's own rule
  on the starts it did not learn from.
- **Changing hands, by a block's past** (`changing`). The chance that a block has another
  leader, or none, one tick on: by how many of its eight neighbours its rival leads and by
  how long it has had its leader. This is the table itself, and the plainest answer to
  whether it is the same at every rung.
- **The mix of young and old** (`mix`). The rule as it is gives one chance to all blocks
  with as many rival neighbours, whatever their past, so it changes from rung to rung if the
  mix of blocks that have had their leader a short and a long while does, even where no
  block's chance does. For each rung: the chance the rule as it is has there, and the chance
  it would have with that rung's mix and the chances of the top rung.
- **Between rungs** (`rungs`). The question the ladder asks: the rule learned one rung down
  tried at a rung, beside the rule learned there, for each reading. As a share of the
  rung's own surprise (step 4g's "more surprise") and in bits a block.
- **Run on** (`run_on`). Each reading's rule run on by itself over a rung's matched age,
  with no cells: the share of blocks whose leader is not the real world's at the end, over
  the share that changed leader meanwhile; the walls it keeps; and how much of the changing
  of hands is going back (a block returning to the leader it had two ticks before), in the
  rule's world beside the real one. With the rung's own rule and with the rule from the rung
  below (the ladder's own test), sixteen runs of the rule from every trial start; and with
  the rung's own rule learned from half its starts, to see whether a rung has enough to
  learn from.
- **Between worlds** (`between`). One world's rule tried in the other, reading by reading:
  one tick ahead, and run on.

The summary goes to look/summary.json. `pictures.py` draws the table of changing hands from
it, a line for each rung.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RUNG = HERE.parent / "scale-up-rung"


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold several study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


study = _module("scale_up_rung_study", RUNG / "study.py")
ladder, zoom = study.ladder, study.zoom

OUT = HERE / "look" / "summary.json"
Q = ladder.Q
CAP = 16  # how long a block has had its leader is counted up to this many ticks
RUNGS = study.BLOCKS[1:]  # the rungs that have a rung below
OWN, BELOW = study.OWN, study.BELOW
PAIRS = 8  # run-ons of a rule from one start come in pairs that differ in their draws alone
DRAWS = 20261126  # the year, month and day step 4e's run-ons named their draws by
ENOUGH = 200  # a chance is told only where at least this many blocks stand behind it
# how long a block has had its leader, in ticks, as the tables of changing hands tell it
SPANS = {"1": (1, 1), "2": (2, 2), "3 or 4": (3, 4), "5 to 8": (5, 8), "9 to 15": (9, 15),
         "16 and more": (16, CAP)}  # fmt: skip


# --- readings: what a rule has in view of a block's past -----------------------------------------


class Plain:
    """The rule as it is: nothing of a block's past in view."""

    name = "its neighbours"
    size = 1

    def code(self, frames: np.ndarray, block: int, tick: int, at: np.ndarray) -> np.ndarray:
        """What this reading sees of the past of every block at the generations `at`, as one
        number below `size`. `frames` holds a run's leaders every `block` generations."""
        return np.zeros(frames[at // block].shape, dtype=np.int64)

    def of(self, counts: np.ndarray) -> np.ndarray:
        """This reading's tally from a tally with more of the past in view."""
        return np.asarray(counts).sum(axis=0, keepdims=True)

    def chances(self, counts: np.ndarray) -> np.ndarray:
        """The chance of each next leader for every view of this reading's tally."""
        return ladder.chances(np.asarray(counts, dtype=float)[0])[None]

    def moved(self, code: np.ndarray, old: np.ndarray, new: np.ndarray) -> np.ndarray:
        """The code of every block one tick on, when its leader went from `old` to `new`."""
        return code


class Before(Plain):
    """Who led the block one tick before."""

    name = "and its leader one tick before"
    size = Q

    def code(self, frames, block, tick, at):
        if at.size and at.min() < tick:
            raise ValueError(f"no leaders a tick of {tick} before generation {at.min()}")
        return frames[(at - tick) // block].astype(np.int64)

    def of(self, counts):
        counts = np.asarray(counts)
        if counts.shape[0] != Q:
            raise ValueError("only a tally by the leader one tick before holds this reading")
        return counts

    def chances(self, counts):
        counts = np.asarray(counts, dtype=float)
        coarser = ladder.chances(counts.sum(axis=0))
        return (counts + coarser) / (counts.sum(axis=-1, keepdims=True) + 1.0)

    def moved(self, code, old, new):
        return old.astype(np.int64)


class Age(Plain):
    """For how many ticks running the block has had its present leader, up to a cap: one
    less than that, so 0 is a block whose leader was another, or none, one tick before."""

    def __init__(self, cap: int = CAP):
        if cap < 1:
            raise ValueError("a block has had its leader for at least one tick")
        self.size = cap
        self.name = f"and how long it has had its leader, up to {cap} ticks"

    def code(self, frames, block, tick, at):
        now = frames[at // block]
        age = np.zeros(now.shape, dtype=np.int64)
        same = np.ones(now.shape, dtype=bool)
        for k in range(1, self.size):
            behind = at - k * tick
            if behind.min() < 0:
                break  # the run is younger than the cap: a block is as old as the run lets it be
            same &= frames[behind // block] == now
            age += same
        return age

    def of(self, counts):
        counts = np.asarray(counts)
        if counts.shape[0] < self.size:
            raise ValueError(f"the tally counts how long up to {counts.shape[0]} ticks only")
        return np.concatenate([counts[: self.size - 1],
                               counts[self.size - 1 :].sum(axis=0, keepdims=True)])  # fmt: skip

    def chances(self, counts):
        counts = np.asarray(counts, dtype=float)
        if self.size == 1:
            return ladder.chances(counts[0])[None]
        shorter = Age(self.size - 1)
        coarser = shorter.chances(shorter.of(counts))
        coarser = np.concatenate([coarser, coarser[-1:]])
        return (counts + coarser) / (counts.sum(axis=-1, keepdims=True) + 1.0)

    def moved(self, code, old, new):
        return np.where(new == old, np.minimum(code + 1, self.size - 1), 0)


PLAIN, BEFORE = Plain(), Before()
READINGS = (PLAIN, BEFORE, Age(4), Age(8))  # the readings whose rules are scored
RUN = (PLAIN, BEFORE, Age(8))  # and those whose rules are run on


def tally(reading, frames: np.ndarray, block: int, tick: int, first: int, last: int) -> np.ndarray:
    """The transitions of one run at one block and tick between two generations, counted by
    [what the reading sees of the block's past][leader][neighbours species 1 leads]
    [neighbours species 2 leads][leader one tick on]. With nothing of the past in view it is
    `ladder.tally`, with one more axis of length one in front."""
    at = np.array(ladder.instants(block, tick, first, last), dtype=np.int64)
    size = reading.size * Q * 81 * Q
    counts = np.zeros(size, dtype=np.int64)
    for a in range(0, at.size, 8):
        g = at[a : a + 8]
        own = frames[g // block]
        view = zoom.codes("total", own, zoom.ring(own), Q)
        past = reading.code(frames, block, tick, g)
        after = frames[(g + tick) // block]
        counts += np.bincount(((past * (Q * 81) + view) * Q + after).ravel(), minlength=size)
    return counts.reshape(reading.size, Q, 9, 9, Q)


def surprise(reading, rule: np.ndarray, trial: np.ndarray) -> float:
    """The bits a transition of the trial tally costs the rule of another tally, on average,
    both read as `reading` reads."""
    trial = reading.of(trial)
    return float(-(trial * np.log2(reading.chances(reading.of(rule)))).sum() / max(trial.sum(), 1))


def hands(counts: np.ndarray) -> np.ndarray:
    """Changing hands, from a tally of any reading: for each thing the reading sees of the
    past and each number of a block's eight neighbours that its rival leads, how many blocks
    with a leader there were and how many had another leader, or none, one tick on. An array
    of shape (size, 9, 2); summed over its first axis it is `ladder.hands`."""
    return np.stack([ladder.hands(part) for part in np.asarray(counts)])


# --- a rule run on by itself ---------------------------------------------------------------------


def step(chance: np.ndarray, code: np.ndarray, now: np.ndarray,
         rng: np.random.Generator) -> np.ndarray:  # fmt: skip
    """One coarse generation of a grid of leaders under a rule's chances: every block's next
    leader drawn from the row of its view, `code` being what the rule's reading sees of each
    block's past. The draw is the instrument's own (`zoom.CoarseRule.step`)."""
    around = zoom.ring(now)
    view = (code, now.astype(np.int64), (around == 1).sum(axis=0), (around == 2).sum(axis=0))
    rungs = chance[view].cumsum(axis=-1)
    draw = rng.random(now.shape)[..., None] * rungs[..., -1:]
    return np.minimum((draw >= rungs).sum(axis=-1), Q - 1).astype(np.int8)


def going_back(before: np.ndarray, now: np.ndarray, after: np.ndarray) -> tuple[int, int]:
    """Of three grids of leaders one tick apart: how many blocks have another leader in the
    last than in the middle one, and how many of those have the leader of the first again."""
    changed = after != now
    return int(changed.sum()), int((changed & (after == before)).sum())


def ahead(reading, frames: np.ndarray, counts: np.ndarray, block: int, tick: int,
          draws: tuple[int, ...], first: int, last: int, pair: int = 0) -> dict:  # fmt: skip
    """The rule of a tally run on by itself from generation `first` of one run's leaders at
    `block`, twice with draws of its own, as `ladder.ahead` does; a rule with a past in view
    starts from the real world's past. With nothing of the past in view and `pair` 0 it is
    `ladder.ahead` to the last figure. Besides what that reads at each horizon it counts, over
    the whole run-on, the blocks that changed leader in a tick and those that went back to
    the leader they had two ticks before, in the rule's world and in the real one; and at the
    end the second run's walls, and its blocks whose leader is not the real world's."""
    chance = reading.chances(reading.of(counts))
    steps = (last - first) // tick
    marks = zoom.horizons(steps)
    names = [[DRAWS, *draws, twin] if pair == 0 else [DRAWS, *draws, twin, pair]
             for twin in (0, 1)]  # fmt: skip
    rngs = [np.random.default_rng(name) for name in names]
    start = frames[first // block]
    behind = frames[(first - tick) // block]
    code = reading.code(frames, block, tick, np.array([first], dtype=np.int64))[0]
    grids, pasts, codes = [start, start], [behind, behind], [code, code]
    world_past, world_now = behind, start
    out: dict = {name: [] for name in ("walls_world", "walls_rule", "apart_rule", "apart_start",
                                       "apart_twin")}  # fmt: skip
    in_rule, in_world = np.zeros(2, dtype=np.int64), np.zeros(2, dtype=np.int64)
    for h in range(1, steps + 1):
        there = frames[(first + h * tick) // block]
        in_world += going_back(world_past, world_now, there)
        world_past, world_now = world_now, there
        for i in (0, 1):
            new = step(chance, codes[i], grids[i], rngs[i])
            in_rule += going_back(pasts[i], grids[i], new)
            codes[i] = reading.moved(codes[i], grids[i], new)
            pasts[i], grids[i] = grids[i], new
        if h in marks:
            out["walls_world"].append(round(ladder.walls(there), 6))
            out["walls_rule"].append(round(ladder.walls(grids[0]), 6))
            out["apart_rule"].append(round(float((grids[0] != there).mean()), 6))
            out["apart_start"].append(round(float((start != there).mean()), 6))
            out["apart_twin"].append(round(float((grids[0] != grids[1]).mean()), 6))
    blocks = start.size * steps
    return {
        "block": block,
        "tick": tick,
        "from_generation": first,
        "generations_on": [h * tick for h in marks],
        **out,
        "rule_sha256": ladder.digest(counts[0]) if reading.size == 1 else None,
        "apart_other": round(float((grids[1] != world_now).mean()), 6),
        "walls_other": round(ladder.walls(grids[1]), 6),
        "changes_world": round(float(in_world[0] / blocks), 6),
        "returns_world": round(float(in_world[1] / max(in_world[0], 1)), 6),
        "changes_rule": round(float(in_rule[0] / (2 * blocks)), 6),
        "returns_rule": round(float(in_rule[1] / max(in_rule[0], 1)), 6),
    }


# --- a world from its kept runs ------------------------------------------------------------------


class World:
    """One world of step 4g's run from the block leaders kept of it: every start's tallies at
    every rung over its matched age, by the leader one tick before and by how long the block
    has had its leader. Given the registered run's records it checks itself against them:
    with nothing of the past in view every tally is the record's, count for count."""

    def __init__(self, name: str, plan: dict | None = None, records: list[dict] | None = None):
        self.name = name
        self.plan = (plan or study.design())[name]
        self.seeds = [*self.plan["learn"], *self.plan["try"]]
        self.frames = {seed: study.fine(name, seed) for seed in self.seeds}
        self.tallies: dict = {}
        for seed in self.seeds:
            for block in study.BLOCKS:
                span = (block, ladder.square(block), *study.AGES[block])
                frames = self.frames[seed][block]
                self.tallies[seed, block] = {
                    "before": tally(BEFORE, frames, *span),
                    "age": tally(Age(CAP), frames, *span),
                }
        self.ran: dict = {}  # run-ons already made of this world, by rule (see `ran`)
        self.registered = {}
        for row in records or []:
            if row["world"] != name:
                continue
            if row["kind"] == "ahead":
                self.registered[row["seed"], row["block"], row["rule"]] = row
            elif row["seed"] in self.seeds:
                for block in study.BLOCKS:
                    kept = ladder.dense(row["tally"][str(block)])
                    for mine in self.tallies[row["seed"], block].values():
                        if not np.array_equal(mine.sum(axis=0), kept):
                            raise ValueError(
                                f"{name} from start {row['seed']}, blocks of {block}: the "
                                "leaders kept do not give the registered tally"
                            )

    def counts(self, reading, seeds, block: int) -> np.ndarray:
        """The tallies of some starts at one rung, together, as a reading reads them."""
        kind = "before" if isinstance(reading, Before) else "age"
        return reading.of(sum(self.tallies[seed, block][kind] for seed in seeds))

    def splits(self) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Every way of choosing half of the world's starts to learn from, with the other
        half to try on. The first is the registered run's own choice."""
        half = len(self.seeds) // 2
        return [(learn, tuple(s for s in self.seeds if s not in learn))
                for learn in combinations(self.seeds, half)]  # fmt: skip


def halves(seeds) -> list[tuple[int, ...]]:
    """Every way of taking half of some starts (all of them, if there is only one)."""
    seeds = tuple(seeds)
    return list(combinations(seeds, len(seeds) // 2)) if len(seeds) > 1 else [seeds]


def learned(world: World, reading, learn, block: int, trial: np.ndarray) -> tuple[float, float]:
    """The surprise of a reading's rule on a trial tally, learned at one rung from some
    starts: as it is, and as it would be with endless data (what a rule lacks goes as one
    over how much it has seen, so twice the surprise from all the starts less the mean
    surprise from half of them)."""
    whole = surprise(reading, world.counts(reading, learn, block), trial)
    half = float(np.mean([surprise(reading, world.counts(reading, part, block), trial)
                          for part in halves(learn)]))  # fmt: skip
    return whole, 2 * whole - half


def shed(world: World, reading, learn, block: int, trial: np.ndarray) -> tuple[float, float]:
    """A check on `learned`: the surprise a rule sheds when it learns from twice as much, from
    one of its starts to two of them and from two to four (means over the ways of taking
    them). Were what a rule lacks to go as one over how much it has seen, the first would be
    twice the second."""
    learn = tuple(learn)

    def from_some(many: int) -> float:
        return float(np.mean([surprise(reading, world.counts(reading, part, block), trial)
                              for part in combinations(learn, many)]))  # fmt: skip

    one, two, four = from_some(1), from_some(2), from_some(4)
    return one - two, two - four


def spread(values) -> dict:
    """The mean of a number over the choices of starts, and its spread between them."""
    values = np.asarray(list(values), dtype=float)
    return {"mean": round(float(values.mean()), 6), "spread": round(float(values.std()), 6)}


def one_tick(world: World) -> dict:
    """At each rung, for each reading: the bits a block costs the reading's own rule on the
    starts it did not learn from, as it is and with endless data; and the share of the plain
    rule's surprise that the block's past removes. Over every choice of starts."""
    out = {}
    for block in study.BLOCKS:
        found: dict = {r.name: [] for r in READINGS}
        sheds: dict = {r.name: [] for r in READINGS}
        for learn, held_out in world.splits():
            for reading in READINGS:
                trial = world.counts(reading, held_out, block)
                found[reading.name].append(learned(world, reading, learn, block, trial))
                if len(learn) == 4:
                    sheds[reading.name].append(shed(world, reading, learn, block, trial))
        told = {}
        plain = np.array(found[PLAIN.name]).T
        for reading in READINGS:
            as_is, endless = np.array(found[reading.name]).T
            told[reading.name] = {
                "bits a block": spread(as_is),
                "bits a block, with endless data": spread(endless),
                "share of the plain rule's surprise removed": spread(1 - as_is / plain[0]),
                "the same, with endless data": spread(1 - endless / plain[1]),
            }
            if sheds[reading.name]:
                first, second = np.mean(sheds[reading.name], axis=0)
                told[reading.name]["bits shed by learning from twice as much"] = {
                    "from one start to two": round(float(first), 6),
                    "from two starts to four": round(float(second), 6),
                    "the first over the second": round(float(first / second), 2),
                }
        first = world.splits()[0]
        learn = world.counts(PLAIN, first[0], block)[0]
        trial = world.counts(PLAIN, first[1], block)[0]
        out[str(block)] = {
            "transitions tried on": int(trial.sum()),
            "the registered choice, bits a block": {
                "nothing": round(ladder.surprise(learn, trial, "nothing"), 6),
                "the block alone": round(ladder.surprise(learn, trial, "own"), 6),
                PLAIN.name: round(ladder.surprise(learn, trial), 6)},
            "every choice": told,
        }  # fmt: skip
    return out


def changing(world: World) -> dict:
    """At each rung, from all of a world's starts: the chance that a block has another
    leader, or none, one tick on, by how many of its eight neighbours its rival leads: for
    all blocks with a leader (the rule as it is), by who led it one tick before, and by how
    long it has had its leader. Each with the blocks that stand behind it."""
    out = {}
    for block in study.BLOCKS:
        by_age = hands(world.counts(Age(CAP), world.seeds, block))
        before = world.counts(BEFORE, world.seeds, block)
        plain = by_age.sum(axis=0)
        held, came = np.zeros((9, 2), dtype=np.int64), np.zeros((9, 2), dtype=np.int64)
        for own in (1, 2):
            for found, was in ((held, own), (came, 3 - own)):
                mine = before[was, own]
                # for species 1 the rival's neighbours are the second count, for 2 the first
                by_rival = mine.sum(axis=0) if own == 1 else mine.sum(axis=1)
                found[:, 0] += by_rival.sum(axis=-1)
                found[:, 1] += by_rival.sum(axis=-1) - by_rival[:, own]
        rows = {"as it is": plain, "led by the same one tick before": held,
                "led by its rival one tick before": came}  # fmt: skip
        for name, (low, high) in SPANS.items():
            rows[f"has had its leader for {name} ticks"] = by_age[low - 1 : high].sum(axis=0)
        both = world.counts(PLAIN, world.seeds, block)[0]
        none = sum(int(both[own, :, :, 0].sum()) for own in (1, 2))
        out[str(block)] = {
            "chance": {name: [round(float(c / n), 4) if n >= ENOUGH else None for n, c in row]
                       for name, row in rows.items()},
            "blocks": {name: [int(n) for n in row[:, 0]] for name, row in rows.items()},
            "of the blocks that changed hands, the share left with no leader": round(
                none / max(int(plain[:, 1].sum()), 1), 4),
            "share of blocks, by how long they have had their leader": {
                name: round(float(by_age[low - 1 : high, :, 0].sum() / by_age[:, :, 0].sum()), 4)
                for name, (low, high) in SPANS.items()},
        }  # fmt: skip
    return out


def mix(world: World) -> dict:
    """How much of the change of the rule as it is from rung to rung is a change in the mix
    of young and old leads. For three to six rival neighbours and every rung: the chance of
    changing hands the rule as it is has there; and the chance it would have with that
    rung's mix of blocks by how long they have had their leader (in the spans of `SPANS`)
    and the top rung's chance for each span. Where the two agree, no block's chance has
    changed between that rung and the top: only the mix has."""
    top = study.BLOCKS[-1]
    spans = list(SPANS.values())

    def by_span(block: int) -> np.ndarray:
        found = hands(world.counts(Age(CAP), world.seeds, block))
        return np.stack([found[low - 1 : high].sum(axis=0) for low, high in spans])

    above = by_span(top)
    out: dict = {}
    for near in (3, 4, 5, 6):
        told = {}
        for block in study.BLOCKS:
            here = by_span(block)[:, near]  # by span: blocks, and those that changed hands
            there = above[:, near]
            known = there[:, 0] >= ENOUGH  # spans the top rung has seen enough of
            chance = np.where(known, there[:, 1] / np.maximum(there[:, 0], 1),
                              here[:, 1] / np.maximum(here[:, 0], 1))  # fmt: skip
            blocks = int(here[:, 0].sum())
            told[str(block)] = {
                "as it is": round(float(here[:, 1].sum() / blocks), 4) if blocks else None,
                "with this rung's mix and the top rung's chances": round(
                    float((here[:, 0] * chance).sum() / blocks), 4) if blocks else None,
            }  # fmt: skip
        out[str(near)] = told
    return out


def rungs(world: World) -> dict:
    """At each rung above the first, for each reading: the rule learned one rung down beside
    the rung's own, on the starts neither learned from. Step 4g's way (the lower rule's tally
    scaled to as many transitions) for the registered choice of starts, which for the plain
    reading is the registered gap; and with endless data for both rules, over every choice
    of starts: in bits a block, and as a share of the rung's own surprise."""
    out: dict = {}
    for block in RUNGS:
        told = {}
        for reading in READINGS:
            bits, share = [], []
            for learn, held_out in world.splits():
                trial = world.counts(reading, held_out, block)
                _, here = learned(world, reading, learn, block, trial)
                _, below = learned(world, reading, learn, block // 2, trial)
                bits.append(below - here)
                share.append(below / here - 1)
            learn, held_out = world.splits()[0]
            trial = world.counts(reading, held_out, block)
            own = world.counts(reading, learn, block)
            lower = ladder.as_much(world.counts(reading, learn, block // 2), own)
            told[reading.name] = {
                "step 4g's way, the registered choice, more surprise": round(
                    surprise(reading, lower, trial) / surprise(reading, own, trial) - 1, 5),
                "with endless data, extra bits a block": spread(bits),
                "with endless data, more surprise": spread(share),
            }  # fmt: skip
        out[str(block)] = told
    return out


def ran(world: World, reading, block: int, counts: np.ndarray, whose: str | None) -> dict:
    """A reading's rule, given as its tally, run on by itself at blocks of `block` over that
    rung's matched age from each trial start of a world, PAIRS times two runs each. Means
    over the starts and the runs, and each start's own figure. `whose` says which of the
    registered run-ons this is, if any (the rung's own rule or the rule from the rung below,
    both learned in this world): its draws are then the registered run's, and where the world
    holds the registered run-on the first run of the plain rule must be it, to the last
    figure."""
    made = (reading.name, block, whose, counts.tobytes())
    if made in world.ran:
        return world.ran[made]
    first, last = study.AGES[block]
    starts = []
    for seed in world.plan["try"]:
        draws = (seed, block, (OWN, BELOW, None).index(whose))
        runs = [ahead(reading, world.frames[seed][block], counts, block, ladder.square(block),
                      draws, first, last, pair) for pair in range(PAIRS)]  # fmt: skip
        on_record = world.registered.get((seed, block, whose))
        if reading.size == 1 and on_record is not None:
            if any(runs[0][key] != value for key, value in on_record.items() if key in runs[0]):
                raise ValueError(f"{world.name} from start {seed}, blocks of {block}, {whose}: "
                                 "not the registered run-on")  # fmt: skip
        starts.append({
            "amiss": float(np.mean([[r["apart_rule"][-1], r["apart_other"]] for r in runs])),
            "changed": runs[0]["apart_start"][-1],
            "walls_rule": float(np.mean([[r["walls_rule"][-1], r["walls_other"]] for r in runs])),
            "walls_world": runs[0]["walls_world"][-1],
            "twin": float(np.mean([r["apart_twin"][-1] for r in runs])),
            "changes_world": runs[0]["changes_world"],
            "returns_world": runs[0]["returns_world"],
            "changes_rule": float(np.mean([r["changes_rule"] for r in runs])),
            "returns_rule": float(np.mean([r["returns_rule"] for r in runs])),
        })  # fmt: skip
    mean = {name: float(np.mean([s[name] for s in starts])) for name in starts[0]}
    world.ran[made] = {
        "amiss over changed": round(mean["amiss"] / mean["changed"], 4),
        "amiss, start by start": [round(s["amiss"], 6) for s in starts],
        "changed, start by start": [round(s["changed"], 6) for s in starts],
        "walls kept": round(mean["walls_rule"] / mean["walls_world"], 4),
        "amiss over two runs of the rule": round(mean["amiss"] / mean["twin"], 4),
        "blocks that change hands in a tick": {
            "the world": round(mean["changes_world"], 5),
            "the rule's world": round(mean["changes_rule"], 5)},
        "of those, going back": {
            "the world": round(mean["returns_world"], 4),
            "the rule's world": round(mean["returns_rule"], 4)},
    }  # fmt: skip
    return world.ran[made]


def beside(found: dict, other: dict) -> dict:
    """One run-on's blocks amiss over another's, from the same starts: over the starts
    together, and the least and the most of one start."""
    mine, theirs = found["amiss, start by start"], other["amiss, start by start"]
    each = [a / b for a, b in zip(mine, theirs, strict=True)]
    return {
        "together": round(sum(mine) / sum(theirs), 4),
        "the least and the most of one start": [round(min(each), 4), round(max(each), 4)],
    }


def run_on(world: World) -> dict:
    """At each rung above the first: each reading's rule, learned at the rung and at the rung
    below, run on by itself. And set beside each other from the same starts: the rule from
    the rung below over the rung's own (the ladder's own test), and each rule with a past in
    view over the rule as it is. A rule with more in view has more to learn, so the rung's
    own rule is also run on having learned from half of its starts: if that does as well, the
    rung's own rule is not held back by how little a rung has to learn from."""
    out = {}
    learn = world.plan["learn"]
    for block in RUNGS:
        told = {
            reading.name: {
                whose: ran(world, reading, block, world.counts(reading, learn, source), whose)
                for whose, source in ((OWN, block), (BELOW, block // 2))}
            for reading in RUN}  # fmt: skip
        for reading in RUN:
            mine = told[reading.name]
            mine["blocks amiss, the rule from the rung below over the rung's own"] = beside(
                mine[BELOW], mine[OWN])  # fmt: skip
            if reading is not PLAIN:
                mine["blocks amiss, over the rule as it is"] = {
                    whose: beside(mine[whose], told[PLAIN.name][whose]) for whose in (OWN, BELOW)
                }
            if len(learn) > 1:
                half = world.counts(reading, learn[: len(learn) // 2], block)
                mine["blocks amiss, its own learned from half its starts over from all"] = beside(
                    ran(world, reading, block, half, None), mine[OWN])  # fmt: skip
        out[str(block)] = told
    return out


def between(world: World, other: World) -> dict:
    """At each rung, reading by reading: the other world's rule beside the world's own. One
    tick ahead, on the starts the world's own did not learn from, both with endless data
    (the other world's rule learned from as many of its starts, the first in its plan). And
    at the rungs above the first, run on by itself in this world from its trial starts,
    beside this world's own rule run on from the same starts."""
    out = {}
    lent = other.plan["learn"]
    for block in study.BLOCKS:
        told: dict = {}
        for reading in READINGS:
            bits, share = [], []
            for learn, held_out in world.splits():
                trial = world.counts(reading, held_out, block)
                _, here = learned(world, reading, learn, block, trial)
                _, there = learned(other, reading, lent, block, trial)
                bits.append(there - here)
                share.append(there / here - 1)
            told[reading.name] = {"extra bits a block": spread(bits),
                                  "more surprise": spread(share)}  # fmt: skip
        if block in RUNGS:
            for reading in RUN:
                theirs = ran(world, reading, block, other.counts(reading, lent, block), None)
                mine = ran(world, reading, block,
                           world.counts(reading, world.plan["learn"], block), OWN)  # fmt: skip
                told[reading.name]["run on, amiss over changed"] = theirs["amiss over changed"]
                told[reading.name]["run on, blocks amiss over the world's own rule's"] = beside(
                    theirs, mine)  # fmt: skip
        out[str(block)] = told
    return out


def missing() -> list[str]:
    """The runs of step 4g whose block leaders are not on this machine."""
    plan = study.design()
    return [f"{name} from start {seed}" for name in plan
            for seed in (*plan[name]["learn"], *plan[name]["try"])
            if not study.cache_path(name, seed).exists()]  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--make", action="store_true",
                        help="make again any run whose leaders are not kept here")  # fmt: skip
    args = parser.parse_args()
    lost = missing()
    if lost and not args.make:
        sys.exit("no block leaders kept of: " + "; ".join(lost) + " (--make makes them again)")
    records = [json.loads(line) for line in study.RECORDS.read_text().splitlines()]
    worlds = {name: World(name, records=records) for name in study.WORLDS}
    names = list(worlds)
    summary = {
        "what": "step 4g's sixteen runs read again with a block's past in view; exploratory",
        "worlds": {
            name: {
                "one tick ahead": one_tick(world),
                "changing hands, by a block's past": changing(world),
                "the mix of young and old leads": mix(world),
                "between rungs": rungs(world),
                "run on": run_on(world),
                "the other world's rule": between(world, worlds[names[1 - names.index(name)]]),
            }
            for name, world in worlds.items()
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"written {OUT}")


if __name__ == "__main__":
    main()
