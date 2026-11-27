"""
A registered test: the coarse rule of a world of territories has a memory.

    uv run --no-sync python examples/scale-up-memory/study.py register
    uv run --no-sync python examples/scale-up-memory/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-memory

**Why.** The first look in this folder (look.py, step 4h of docs/scale-up-plan.md) read step
4g's runs again with more of a block in view: for how many ticks running it has had its
leader. It found that this says a great deal about what the block does next; that with it in
view the top of the coarse rule's table is the same at every rung, and what had looked like
the table changing there was the mix of blocks that had just changed hands and blocks that
had not; that along the walls the table still changes; and that a rule which keeps it in view
runs the world on better, keeps its walls, and is nearly the same rule from one rung to the
next by the ladder's own test. All of that was read off runs that had been seen, with the
readings chosen after the first numbers. This puts it on the record.

**What is run.** The two worlds, B245678/S3678 against its copy (still grounds) and
B23467/S4568 against its copy (busy grounds), under the standoff from a full start, on a
wrapped grid of side 1,024 for 4,096 generations, from sixteen fresh starts each: eight to
learn from and eight to try on. Each block is read on the square clock over the generations
that match it (`AGES`): blocks of 4 over 64 to 256, of 8 over 256 to 1,024, of 16 over 1,024
to 4,096. That is step 4e's size; blocks of 32, where the look's last word came from, are
out of its reach.

**Two rules.** *As it is*: what a block does next by its leader and by how many of its eight
neighbours each species leads. *With how long in view*: the same, and for how many ticks
running the block has had its present leader, counted up to 8 ticks (`look.Age(8)`; the
look's best reading, and the only one registered). The table itself is told in six spans of
time, up to 16 ticks and more.

**What is read** (the measures are the look's, `look.py` here, and step 4e's, `ladder.py`).

- **The table** (`chance`): the chance that a block has another leader, or none, one tick
  on, by how many of its neighbours its rival leads and by how long it has had its leader,
  from all sixteen starts of a world.
- **The mix** (`mixed`): the chance the rule as it is would have at one rung with that
  rung's mix of young and old leads and the next rung's chance for each span of time.
- **One tick ahead** (`bits`, `gap`): the bits of surprise a block costs a rule on the trial
  starts; and step 4g's gap, the rule learned one rung down (its tally scaled to as many
  transitions) beside the rung's own.
- **Run on** (`ahead`): a rule run on by itself over a rung's matched age from each trial
  start, sixteen runs each: the blocks whose leader is not the real world's at the end; the
  walls it keeps; and of the blocks that change hands in a tick, the share going back to
  the leader they had two ticks before, in the rule's world and in the real one.
- **The look's own rules** (reference.json): the tables the look learned on side 2,048,
  unchanged, tried and run on here beside the rules learned from these starts.

**Predictions** (`claims`), in seven families.

    A  a block's past says what it does next: young leads change hands several times as
       often as old ones, and the past removes a share of the plain rule's surprise
    B  the top of the table is the same from blocks of 8 to 16 once the past is in view,
       and the plain rule's fall there is the mix of young and old leads
    C  along the walls the table still changes, at every age of the lead, and one tick
       ahead the remembering rule changes from rung to rung nearly as much as the plain one
    D  run on, the rule with how long in view ends with fewer blocks amiss, does not lose
       walls as the plain rule does, and goes back as often as the world
    E  the ladder's own test: the remembering rule from the rung below runs a rung on
       nearly as well as the rung's own, where the plain rule from below pays
    R  the look's rules, learned on another grid from other starts, serve here unchanged
    X  the anchor: with nothing of the past in view these are the worlds of steps 4e and 4g

A claim holds if its number is inside its bound and fails if it is not. A claim about a
chance is **not tested** where fewer than 200 blocks stand behind either chance it compares,
and a run-on only where blocks are small beside the world's territories when it starts (as
in steps 4e and 4g).

Every number but those of the run-ons is worked out again in `decide` from the tallies in
the records. **What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold several study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


look = _module("scale_up_memory_look", HERE / "look.py")
ladder, zoom = look.ladder, look.zoom

from lattice_lab.study import Study, append_records, main  # noqa: E402

RECORDS = HERE / "records.jsonl"
SIZING = HERE / "sizing.json"
REFERENCE = HERE / "reference.json"
STEP_4E = HERE.parent / "scale-up-closure-territories"
STEP_4G = HERE.parent / "scale-up-rung"

SIDE, GENERATIONS = 1024, 4096
WORLDS = {
    "still": {"rule": "B245678/S3678", "first": 19001},
    "busy": {"rule": "B23467/S4568", "first": 19101},
}
STARTS = 16  # a world's starts: the first half to learn from, the second to try on
BLOCKS = (4, 8, 16)
AGES = {4: (64, 256), 8: (256, 1024), 16: (1024, 4096)}  # a block's matched age
RUNGS = BLOCKS[1:]  # the rungs that have a rung below
Q = ladder.Q

PLAIN, HOW = "as it is", "with how long in view"
READINGS = {PLAIN: look.PLAIN, HOW: look.Age(8)}
LONG = look.Age(look.CAP)  # every tally is kept by how long, up to 16 ticks
SPANS = look.SPANS  # the spans of time the table is told in
NEW, OLD = "1", "16 and more"
OWN, BELOW, LOOKS = "its own", "the rung below's", "the look's"
PAIRS = 8  # run-ons of a rule from one start: this many pairs, sixteen runs
ENOUGH = 200  # a chance is judged only where this many blocks stand behind it
BLOCK_FITS = 0.2  # at most this share of neighbouring blocks differ when a rule is run on

# the bounds, family by family (sizing.py says what each was drawn from)
YOUNG_OVER_OLD = 4.0  # A: a lead of one tick over a lead of 16 and more, four rival neighbours
REMOVES = 0.04  # A: the share of the plain rule's surprise that how long removes, at least
SAME_TOP = 0.10  # B: an old lead at five rival neighbours, blocks of 16 within this of 8
PLAIN_FALLS = 0.93  # B: the rule as it is at five, blocks of 16 over 8, at most
MIX_IS_IT = 0.05  # B: the rule as it is at 8, from the mix and blocks of 16's chances, within
OLD_AT_THREE = 0.60  # C: an old lead at three rival neighbours, blocks of 16 over 8, at most
NEW_AT_THREE = 0.90  # C: a lead of one tick at three, blocks of 16 over 8, at most
OLD_AT_FOUR = 0.92  # C: an old lead at four, blocks of 16 over 8, at most
MIX_IS_NOT = 0.30  # C: the share of the plain rule's fall at three that is the mix, at most
STILL_A_GAP = 0.04  # C: the remembering rule from blocks of 4 at blocks of 8, more surprise
GAP_OVER_PLAIN = 0.60  # C: that gap over the plain rule's, at least
FEWER_AMISS = {8: 0.90, 16: 0.96}  # D: blocks amiss with how long over as it is, at most
PLAIN_LOSES = {8: 0.95, 16: 0.98}  # D: the walls the plain rule keeps, at most
KEEPS = (0.95, 1.14)  # D: the walls the remembering rule keeps
GOES_BACK = 0.06  # D: going back, the remembering rule's world within this of the real one
PLAIN_DOES_NOT = 0.60  # D: going back, the plain rule's world over the real one, at most
LADDER = {8: 1.22, 16: 1.10}  # E: blocks amiss, the remembering rule from below over own
PLAIN_PAYS = {8: 0.02, 16: 0.04}  # E: the plain rule's ratio less the remembering one's
BEATS_PLAIN = 0.97  # E: the remembering rule from below over the rung's own plain rule
SERVES = 0.005  # R: the look's rule one tick ahead, more surprise than this run's, at most
RUNS_AS_WELL = (0.93, 1.07)  # R: blocks amiss, the look's rule over this run's own
GAP_AT_16 = (0.015, 0.045)  # X: step 4g's bound for the plain gap at blocks of 16
WHERE = 0.70  # X: step 4g's bound for the plain rule's own run-on


def design() -> dict:
    out = {}
    for name, w in WORLDS.items():
        seeds = list(range(w["first"], w["first"] + STARTS))
        out[name] = {"learn": seeds[: STARTS // 2], "try": seeds[STARTS // 2 :]}
    return out


# --- tallies on record ---------------------------------------------------------------------------


def sparse(counts: np.ndarray) -> list[list[int]]:
    """A tally of any reading as its rows that hold anything: [view, then the count of each
    next leader], the view numbered over [the block's past][leader][neighbours of 1]
    [neighbours of 2]."""
    flat = np.asarray(counts).reshape(-1, Q)
    return [[int(i), *map(int, flat[i])] for i in np.flatnonzero(flat.sum(axis=1))]


def dense(rows: list[list[int]], size: int) -> np.ndarray:
    """The tally `sparse` wrote down, of a reading that sees `size` things of the past."""
    counts = np.zeros((size * Q * 81, Q), dtype=np.int64)
    for view, *after in rows:
        counts[view] = after
    return counts.reshape(size, Q, 9, 9, Q)


# --- the runs ------------------------------------------------------------------------------------


def cache_path(name: str, seed: int) -> Path:
    return ladder.CACHE / f"memory-{name}-{SIDE}-{GENERATIONS}-{seed}.npz"


def fine(name: str, seed: int) -> dict:
    """One world from one start, read through every block every `block` generations up to the
    end of that block's matched age: the leader of every block at every reading, and every 64
    generations each species' share of the grid. Kept on disk, and read from there if it is."""
    path = cache_path(name, seed)
    if path.exists():
        with np.load(path) as kept:
            return {"shares": kept["shares"], **{b: kept[f"leaders_{b}"] for b in BLOCKS}}
    rule = WORLDS[name]["rule"]
    grid = zoom.lattice((rule, rule), "standoff", SIDE)
    start = zoom.mixed_start(SIDE, seed, 2, density=1.0)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])  # the standoff draws nothing
    frames = {b: [zoom.leaders(zoom.read(grid.occupancy, SIDE, b, 2))] for b in BLOCKS}
    shares = []
    for generation in range(1, GENERATIONS + 1):
        grid.step(rng)
        for b in BLOCKS:
            if generation % b == 0 and generation <= AGES[b][1]:
                frames[b].append(zoom.leaders(zoom.read(grid.occupancy, SIDE, b, 2)))
        if generation % 64 == 0:
            shares.append([float((grid.occupancy == s).mean()) for s in (1, 2)])
    out = {"shares": np.array(shares), **{b: np.stack(frames[b]) for b in BLOCKS}}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, shares=out["shares"],
                        **{f"leaders_{b}": out[b] for b in BLOCKS})  # fmt: skip
    return out


def start_record(name: str, seed: int, found: dict) -> dict:
    """What goes on record of one run, from its leaders: for each block its tally by how long
    a block has had its leader, on the square clock over its matched age, and its walls at
    the ends of it; and the share of the grid live, and the larger species' share, at every
    end."""
    marks = sorted({g for span in AGES.values() for g in span})
    shares = found["shares"]
    return {
        "kind": "start",
        "world": name,
        "seed": seed,
        "side": SIDE,
        "generations": GENERATIONS,
        "live": {str(g): round(float(shares[g // 64 - 1].sum()), 6) for g in marks},
        "larger": {str(g): round(float(shares[g // 64 - 1].max()), 6) for g in marks},
        "walls": {str(b): {str(g): round(ladder.walls(found[b][g // b]), 6) for g in AGES[b]}
                  for b in BLOCKS},
        "tally": {str(b): sparse(look.tally(LONG, found[b], b, ladder.square(b), *AGES[b]))
                  for b in BLOCKS},
    }  # fmt: skip


def run_start(job: tuple[str, int]) -> dict:
    name, seed = job
    return start_record(name, seed, fine(name, seed))


def pooled(rows: list[dict], world: str, seeds, block: int) -> np.ndarray:
    """The tallies of a world's starts `seeds` at one block, over its matched age, by how
    long a block has had its leader (up to 16 ticks)."""
    total = np.zeros((LONG.size, Q, 9, 9, Q), dtype=np.int64)
    for row in rows:
        if row["kind"] == "start" and row["world"] == world and row["seed"] in seeds:
            total += dense(row["tally"][str(block)], LONG.size)
    return total


def reference() -> dict:
    """The look's rules: for each world and block, the tally of all eight of step 4g's
    starts on side 2,048 over the block's matched age, by how long (up to 16 ticks)."""
    kept = json.loads(REFERENCE.read_text())["worlds"]
    return {(world, int(block)): dense(rows, LONG.size)
            for world, blocks in kept.items() for block, rows in blocks.items()}  # fmt: skip


def ahead_record(name: str, seed: int, block: int, reading: str, whose: str,
                 frames: np.ndarray, counts: np.ndarray) -> dict:  # fmt: skip
    """A rule run on by itself at one rung of one start of one world over the rung's matched
    age, PAIRS times two runs (`look.ahead`). On record, pair by pair: at the end the blocks
    whose leader is not the real world's in each of the two runs, the blocks that changed
    leader in the real world, the blocks in which the two runs differ, and the walls of the
    world and of each run; and over the whole run-on the share of blocks that change hands
    in a tick and the share of those going back, in the real world and in the rule's."""
    draws = (seed, block, (OWN, BELOW, LOOKS).index(whose))
    first, last = AGES[block]
    runs = [look.ahead(READINGS[reading], frames, counts, block, ladder.square(block), draws,
                       first, last, pair) for pair in range(PAIRS)]  # fmt: skip
    return {
        "kind": "ahead",
        "world": name,
        "seed": seed,
        "block": block,
        "reading": reading,
        "rule": whose,
        "from_generation": first,
        "generations_on": runs[0]["generations_on"][-1],
        "amiss": [[r["apart_rule"][-1], r["apart_other"]] for r in runs],
        "changed": runs[0]["apart_start"][-1],
        "twin": [r["apart_twin"][-1] for r in runs],
        "walls_world": runs[0]["walls_world"][-1],
        "walls_rule": [[r["walls_rule"][-1], r["walls_other"]] for r in runs],
        "changes_world": runs[0]["changes_world"],
        "returns_world": runs[0]["returns_world"],
        "changes_rule": [r["changes_rule"] for r in runs],
        "returns_rule": [r["returns_rule"] for r in runs],
    }


def run_ahead(job: tuple[str, int, int, str, str, list]) -> dict:
    name, seed, block, reading, whose, rows = job
    counts = dense(rows, READINGS[reading].size)
    return ahead_record(name, seed, block, reading, whose, fine(name, seed)[block], counts)


def start_jobs(plan: dict) -> list[tuple[str, int]]:
    seeds = {name: plan[name]["learn"] + plan[name]["try"] for name in plan}
    longest = max(len(s) for s in seeds.values())
    return [(name, s[i]) for i in range(longest) for name, s in seeds.items() if i < len(s)]


def rules(rows: list[dict], plan: dict, name: str, block: int) -> list[tuple[str, str, np.ndarray]]:
    """The rules run on at one rung of one world, each as its reading, whose it is and its
    tally: as it is and with how long in view, the rung's own and the rung below's, each
    learned from the starts the world learns from; and the look's rule with how long in
    view."""
    out = []
    for reading, sees in READINGS.items():
        for whose, source in ((OWN, block), (BELOW, block // 2)):
            out.append((reading, whose, sees.of(pooled(rows, name, plan[name]["learn"], source))))
    out.append((HOW, LOOKS, READINGS[HOW].of(reference()[name, block])))
    return out


def ahead_jobs(rows: list[dict], plan: dict) -> list:
    return [(name, seed, block, reading, whose, sparse(counts))
            for name in plan for block in RUNGS
            for reading, whose, counts in rules(rows, plan, name, block)
            for seed in plan[name]["try"]]  # fmt: skip


def execute(path: Path, workers: int) -> None:
    plan = design()
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    done = {(r["kind"], r["world"], r["seed"], r.get("block"), r.get("reading"), r.get("rule"))
            for r in rows}  # fmt: skip
    starts = [job for job in start_jobs(plan) if ("start", *job, None, None, None) not in done]
    with ProcessPoolExecutor(max(workers, 1)) as pool:
        for record in pool.map(run_start, starts):
            append_records(path, [record])
            rows.append(record)
        ahead = [job for job in ahead_jobs(rows, plan) if ("ahead", *job[:5]) not in done]
        for record in pool.map(run_ahead, ahead):
            append_records(path, [record])


# --- what is measured ----------------------------------------------------------------------------


def over(top: float | None, bottom: float | None) -> float | None:
    """One number over another, where the other is a number above nought."""
    if top is None or bottom is None or not np.isfinite(top) or not np.isfinite(bottom):
        return None
    return top / bottom if bottom > 0 else None


def less(top: float | None, bottom: float | None) -> float | None:
    """One number less another, where both are numbers."""
    if top is None or bottom is None or not np.isfinite(top) or not np.isfinite(bottom):
        return None
    return top - bottom


class Measures:
    """Every number a claim is judged on, from the records of a run."""

    def __init__(self, rows: list[dict], plan: dict, looks: dict | None = None):
        self.rows, self.plan = rows, plan
        self.looks = reference() if looks is None else looks
        self.ahead: dict = {}
        for r in rows:
            if r["kind"] == "ahead":
                key = (r["world"], r["block"], r["reading"], r["rule"])
                self.ahead.setdefault(key, []).append(r)
        self._tally: dict = {}

    def seeds(self, world: str, part: str) -> list[int]:
        return self.plan[world]["learn"] + self.plan[world]["try"] if part == "all" else (
            self.plan[world][part])  # fmt: skip

    def tally(self, world: str, part: str, block: int) -> np.ndarray:
        """A world's tallies at one block from the starts of `part`, by how long (to 16)."""
        key = (world, part, block)
        if key not in self._tally:
            self._tally[key] = pooled(self.rows, world, self.seeds(world, part), block)
        return self._tally[key]

    # --- the table

    def by_span(self, world: str, block: int) -> np.ndarray:
        """Changing hands from all of a world's starts at one block: for each span of time
        and each number of rival neighbours, the blocks there were and those that had
        another leader, or none, one tick on. Shape (spans, 9, 2)."""
        found = look.hands(self.tally(world, "all", block))
        return np.stack([found[low - 1 : high].sum(axis=0) for low, high in SPANS.values()])

    def chance(self, world: str, block: int, span: str | None, near: int) -> float | None:
        """The chance of another leader one tick on for blocks with `near` rival neighbours
        that have had their leader for `span` ticks (None: whatever their past, which is
        the rule as it is). Not a number where fewer than ENOUGH blocks stand behind it."""
        found = self.by_span(world, block)
        blocks, changed = (found.sum(axis=0) if span is None
                           else found[list(SPANS).index(span)])[near]  # fmt: skip
        return float(changed / blocks) if blocks >= ENOUGH else None

    def mixed(self, world: str, block: int, near: int) -> float | None:
        """The chance the rule as it is would have at one rung with that rung's mix of young
        and old leads and the next rung's chance for each span of time."""
        here, above = self.by_span(world, block)[:, near], self.by_span(world, 2 * block)[:, near]
        if here[:, 0].sum() < ENOUGH or (above[:, 0] < ENOUGH).any():
            return None
        return float((here[:, 0] * above[:, 1] / above[:, 0]).sum() / here[:, 0].sum())

    def mix_share(self, world: str, block: int, near: int) -> float | None:
        """Of the fall of the rule as it is from one rung to the next, the share that is the
        mix: the fall there would be were only the mix to change, over the fall there is."""
        here, above = self.chance(world, block, None, near), self.chance(world, 2 * block,
                                                                         None, near)  # fmt: skip
        return over(less(self.mixed(world, block, near), above), less(here, above))

    # --- one tick ahead

    def bits(self, world: str, block: int, reading: str) -> float:
        """The bits a block costs a reading's own rule, learned from the starts the world
        learns from, on its trial starts."""
        return look.surprise(READINGS[reading], self.tally(world, "learn", block),
                             self.tally(world, "try", block))  # fmt: skip

    def removed(self, world: str, block: int) -> float | None:
        plain = self.bits(world, block, PLAIN)
        return 1 - self.bits(world, block, HOW) / plain if plain > 0 else None

    def serves(self, world: str, block: int, reading: str, rule: np.ndarray) -> float | None:
        """A rule from elsewhere, its tally scaled to as many transitions as the rung's own
        rule learned from, on the trial starts: more surprise than the rung's own."""
        sees = READINGS[reading]
        own, trial = self.tally(world, "learn", block), self.tally(world, "try", block)
        here = look.surprise(sees, own, trial)
        there = look.surprise(sees, ladder.as_much(sees.of(rule), sees.of(own)), trial)
        return there / here - 1 if here > 0 else None

    def gap(self, world: str, block: int, reading: str) -> float | None:
        """Step 4g's gap: the rule of the rung below, with as much data, tried at this rung."""
        return self.serves(world, block, reading, self.tally(world, "learn", block // 2))

    def from_look(self, world: str, block: int, reading: str) -> float | None:
        """The look's rule of side 2,048, unchanged, tried at this rung."""
        return self.serves(world, block, reading, self.looks[world, block])

    # --- run on

    def end(self, world: str, block: int, reading: str, whose: str, what: str) -> float | None:
        """A number of the run-ons of one rule, its mean over the runs of a start and then
        over the world's trial starts."""
        runs = self.ahead.get((world, block, reading, whose), [])
        if sorted(r["seed"] for r in runs) != sorted(self.plan[world]["try"]):
            return None
        return float(np.mean([np.mean(r[what]) for r in runs]))

    def fits(self, world: str, block: int) -> bool:
        mine = [r for r in self.rows if r["kind"] == "start" and r["world"] == world
                and r["seed"] in self.plan[world]["try"]]  # fmt: skip
        if not mine:
            return False
        first = str(AGES[block][0])
        return float(np.mean([r["walls"][str(block)][first] for r in mine])) <= BLOCK_FITS

    def stands(self, claim: dict) -> bool:
        return claim["fits"] is None or self.fits(claim["world"], claim["fits"])

    def value(self, claim: dict) -> float | None:
        q, world, block = claim["quantity"], claim["world"], claim.get("block")
        near = claim.get("near")
        amiss = lambda reading, whose: self.end(world, block, reading, whose, "amiss")  # noqa: E731
        if q == "a young lead over an old one":
            return over(self.chance(world, block, NEW, near), self.chance(world, block, OLD, near))
        if q == "surprise removed":
            return self.removed(world, block)
        if q == "chance, this rung over the one below":
            span = claim["span"]
            return over(self.chance(world, block, span, near),
                        self.chance(world, block // 2, span, near))  # fmt: skip
        if q == "the mix alone over the rule as it is":
            return over(self.mixed(world, block, near), self.chance(world, block, None, near))
        if q == "the share of the fall that is the mix":
            return self.mix_share(world, block, near)
        if q == "gap":
            return self.gap(world, block, claim["reading"])
        if q == "gap, with how long in view over as it is":
            return over(self.gap(world, block, HOW), self.gap(world, block, PLAIN))
        if q == "amiss, with how long in view over as it is":
            return over(amiss(HOW, OWN), amiss(PLAIN, OWN))
        if q == "walls kept":
            return over(self.end(world, block, claim["reading"], OWN, "walls_rule"),
                        self.end(world, block, claim["reading"], OWN, "walls_world"))  # fmt: skip
        if q == "going back, the rule's world less the real one":
            return less(self.end(world, block, HOW, OWN, "returns_rule"),
                        self.end(world, block, HOW, OWN, "returns_world"))  # fmt: skip
        if q == "going back, the rule's world over the real one":
            return over(self.end(world, block, PLAIN, OWN, "returns_rule"),
                        self.end(world, block, PLAIN, OWN, "returns_world"))  # fmt: skip
        if q == "amiss, the rule from below over the rung's own":
            return over(amiss(claim["reading"], BELOW), amiss(claim["reading"], OWN))
        if q == "what the plain rule from below pays, less what the remembering one does":
            return less(over(amiss(PLAIN, BELOW), amiss(PLAIN, OWN)),
                        over(amiss(HOW, BELOW), amiss(HOW, OWN)))  # fmt: skip
        if q == "amiss, the remembering rule from below over the rung's own plain rule":
            return over(amiss(HOW, BELOW), amiss(PLAIN, OWN))
        if q == "the look's rule":
            return self.from_look(world, block, claim["reading"])
        if q == "amiss, the look's rule over the rung's own":
            return over(amiss(HOW, LOOKS), amiss(HOW, OWN))
        if q == "amiss over changed":
            return over(amiss(claim["reading"], OWN),
                        self.end(world, block, claim["reading"], OWN, "changed"))  # fmt: skip
        raise ValueError(f"unknown quantity {q!r}")


# --- the predictions -----------------------------------------------------------------------------


def claims() -> list[dict]:
    out = []

    def claim(family, label, text, quantity, world, at_least=None, at_most=None, **more):
        out.append({"label": label, "family": family, "claim": text, "quantity": quantity,
                    "world": world, "at_least": at_least, "at_most": at_most,
                    "fits": more.pop("fits", None), **more})  # fmt: skip

    for w in WORLDS:
        # A: a block's past says what it does next
        for block in RUNGS:
            claim("A", f"A {w}, block {block}: a young lead changes hands far more often",
                  f"in the {w} world a block of {block} with four rival neighbours that has "
                  "had its leader for one tick has another leader one tick on at least "
                  f"{YOUNG_OVER_OLD:g} times as often as one that has had it for 16 ticks or "
                  "more",
                  "a young lead over an old one", w, at_least=YOUNG_OVER_OLD, block=block,
                  near=4)  # fmt: skip
        for block in BLOCKS:
            claim("A", f"A {w}, block {block}: its past removes surprise",
                  f"in the {w} world at blocks of {block} the rule with how long in view has "
                  f"at least {REMOVES:.0%} less surprise on the trial starts than the rule as "
                  "it is",
                  "surprise removed", w, at_least=REMOVES, block=block)  # fmt: skip
        # B: the top of the table is the same once the past is in view
        claim("B", f"B {w}: an old lead at five is the same at both rungs",
              f"in the {w} world a block with five rival neighbours that has had its leader "
              "for 16 ticks or more changes hands at blocks of 16 within "
              f"{SAME_TOP:.0%} as often as at blocks of 8",
              "chance, this rung over the one below", w, at_least=1 - SAME_TOP,
              at_most=1 + SAME_TOP, block=16, near=5, span=OLD)  # fmt: skip
        claim("B", f"B {w}: the rule as it is falls at five",
              f"while the rule as it is gives a block of 16 with five rival neighbours at "
              f"most {PLAIN_FALLS} of the chance it gives a block of 8",
              "chance, this rung over the one below", w, at_most=PLAIN_FALLS, block=16, near=5,
              span=None)  # fmt: skip
        claim("B", f"B {w}: and the fall is the mix",
              "and with the mix of young and old leads of blocks of 8 and the chances of "
              "blocks of 16 for each span of time, the rule as it is at blocks of 8 comes out "
              f"within {MIX_IS_IT:.0%} of what it is, at five rival neighbours",
              "the mix alone over the rule as it is", w, at_least=1 - MIX_IS_IT,
              at_most=1 + MIX_IS_IT, block=8, near=5)  # fmt: skip
        # C: along the walls it still changes
        for label, span, near, bound in (
            ("an old lead at three still falls", OLD, 3, OLD_AT_THREE),
            ("a young lead at three still falls", NEW, 3, NEW_AT_THREE),
            ("an old lead at four still falls", OLD, 4, OLD_AT_FOUR),
        ):
            ticks = "one tick" if span == NEW else "16 ticks or more"
            claim("C", f"C {w}: {label}",
                  f"in the {w} world a block with {near} rival neighbours that has had its "
                  f"leader for {ticks} changes hands at blocks of 16 at most {bound} times as "
                  "often as at blocks of 8",
                  "chance, this rung over the one below", w, at_most=bound, block=16,
                  near=near, span=span)  # fmt: skip
        claim("C", f"C {w}: at three the fall is not the mix",
              f"in the {w} world at most {MIX_IS_NOT:.0%} of the fall of the rule as it is "
              "from blocks of 8 to 16, at three rival neighbours, is the mix of young and old "
              "leads",
              "the share of the fall that is the mix", w, at_most=MIX_IS_NOT, block=8,
              near=3)  # fmt: skip
        claim("C", f"C {w}: one tick ahead the remembering rule still changes",
              f"in the {w} world the rule with how long in view learned at blocks of 4 has at "
              f"least {STILL_A_GAP:.0%} more surprise at blocks of 8 than the one learned "
              "there",
              "gap", w, at_least=STILL_A_GAP, block=8, reading=HOW)  # fmt: skip
        claim("C", f"C {w}: nearly as much as the plain rule",
              f"and at least {GAP_OVER_PLAIN} times as much more as the rule as it is has",
              "gap, with how long in view over as it is", w, at_least=GAP_OVER_PLAIN,
              block=8)  # fmt: skip
        # D: run on, the rule that remembers is the better rule
        for block in RUNGS:
            claim("D", f"D {w}, block {block}: fewer blocks amiss",
                  f"run on by itself over the matched age of blocks of {block}, the {w} "
                  "world's rule with how long in view ends with another leader than the real "
                  f"world's in at most {FEWER_AMISS[block]} times as many blocks as its rule "
                  "as it is",
                  "amiss, with how long in view over as it is", w,
                  at_most=FEWER_AMISS[block], block=block, fits=block)  # fmt: skip
            claim("D", f"D {w}, block {block}: the plain rule loses walls",
                  f"the rule as it is ends with at most {PLAIN_LOSES[block]} of the world's "
                  "walls",
                  "walls kept", w, at_most=PLAIN_LOSES[block], block=block, reading=PLAIN,
                  fits=block)  # fmt: skip
            claim("D", f"D {w}, block {block}: the remembering rule keeps them",
                  f"and the rule with how long in view with between {KEEPS[0]} and {KEEPS[1]}",
                  "walls kept", w, at_least=KEEPS[0], at_most=KEEPS[1], block=block,
                  reading=HOW, fits=block)  # fmt: skip
            claim("D", f"D {w}, block {block}: it goes back as often as the world",
                  "of the blocks that change hands in a tick, the share going back to the "
                  "leader they had two ticks before is within "
                  f"{GOES_BACK} in the remembering rule's world of what it is in the real one",
                  "going back, the rule's world less the real one", w, at_least=-GOES_BACK,
                  at_most=GOES_BACK, block=block, fits=block)  # fmt: skip
            claim("D", f"D {w}, block {block}: the plain rule does not",
                  f"and in the plain rule's world at most {PLAIN_DOES_NOT} of it",
                  "going back, the rule's world over the real one", w,
                  at_most=PLAIN_DOES_NOT, block=block, fits=block)  # fmt: skip
        # E: the ladder's own test
        for block in RUNGS:
            claim("E", f"E {w}, block {block}: the remembering rule from below runs it on",
                  f"in the {w} world the rule with how long in view learned at blocks of "
                  f"{block // 2}, used as the rule at blocks of {block} and run on by itself, "
                  f"ends with another leader than the real world's in at most {LADDER[block]} "
                  "times as many blocks as the rung's own such rule",
                  "amiss, the rule from below over the rung's own", w,
                  at_most=LADDER[block], block=block, reading=HOW, fits=block)  # fmt: skip
            claim("E", f"E {w}, block {block}: where the plain rule from below pays more",
                  "and that ratio is at least "
                  f"{PLAIN_PAYS[block]} less than the same for the rule as it is",
                  "what the plain rule from below pays, less what the remembering one does", w,
                  at_least=PLAIN_PAYS[block], block=block, fits=block)  # fmt: skip
        claim("E", f"E {w}: and it beats the rung's own plain rule",
              f"in the {w} world the remembering rule from blocks of 8, run on at blocks of "
              f"16, ends with at most {BEATS_PLAIN} times as many blocks amiss as the rule as "
              "it is learned at blocks of 16",
              "amiss, the remembering rule from below over the rung's own plain rule", w,
              at_most=BEATS_PLAIN, block=16, fits=16)  # fmt: skip
        # R: the look's rules, unchanged
        for block in RUNGS:
            for reading in (PLAIN, HOW):
                claim("R", f"R {w}, block {block}: the look's rule {reading} serves",
                      f"the rule {reading} that the look learned for the {w} world at blocks "
                      f"of {block} on side 2,048 has at most {SERVES:.1%} more surprise on "
                      "the trial starts here than the rule learned here",
                      "the look's rule", w, at_most=SERVES, block=block,
                      reading=reading)  # fmt: skip
            claim("R", f"R {w}, block {block}: and runs the world on",
                  "and with how long in view, run on by itself, it ends with between "
                  f"{RUNS_AS_WELL[0]} and {RUNS_AS_WELL[1]} times as many blocks amiss as "
                  "the rule learned here",
                  "amiss, the look's rule over the rung's own", w, at_least=RUNS_AS_WELL[0],
                  at_most=RUNS_AS_WELL[1], block=block, fits=block)  # fmt: skip
        # X: the anchor
        claim("X", f"X {w}: the plain gap at blocks of 16",
              f"in the {w} world the rule as it is from blocks of 8 has between "
              f"{GAP_AT_16[0]:.1%} and {GAP_AT_16[1]:.1%} more surprise at blocks of 16 than "
              "the rung's own, as steps 4e and 4g found",
              "gap", w, at_least=GAP_AT_16[0], at_most=GAP_AT_16[1], block=16,
              reading=PLAIN)  # fmt: skip
        claim("X", f"X {w}: the plain rule's own run-on at blocks of 16",
              f"and run on by itself it ends amiss in at most {WHERE} of the share of blocks "
              "that changed leader meanwhile, as there",
              "amiss over changed", w, at_most=WHERE, block=16, reading=PLAIN, fits=16)  # fmt: skip
    return out


def predictions() -> list[dict]:
    return claims()


# --- the verdict ---------------------------------------------------------------------------------


def number(value, places: int = 5) -> float | None:
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), places)


def judge(value: float | None, claim: dict, stands: bool) -> str:
    if not stands or value is None or not np.isfinite(value):
        return "not tested"
    if claim["at_least"] is not None and value < claim["at_least"]:
        return "fails"
    if claim["at_most"] is not None and value > claim["at_most"]:
        return "fails"
    return "holds"


def told(m: Measures, world: str) -> dict:
    """What a reader wants of one world beside the verdicts: the table, one tick ahead and
    the run-ons, rung by rung."""
    out: dict = {"rungs": {}}
    for block in BLOCKS:
        rung: dict = {
            "matched age": list(AGES[block]),
            "chance of another leader one tick on, by rival neighbours": {
                "the rule as it is": [number(m.chance(world, block, None, n), 4)
                                      for n in range(9)],
                **{f"has had its leader for {span} ticks": [
                    number(m.chance(world, block, span, n), 4) for n in range(9)]
                   for span in SPANS}},
            "bits a block": {reading: number(m.bits(world, block, reading), 6)
                             for reading in READINGS},
            "share of the plain rule's surprise that how long removes": number(
                m.removed(world, block), 4),
        }  # fmt: skip
        if block in RUNGS:
            rung["gap: the rule from the rung below, more surprise"] = {
                reading: number(m.gap(world, block, reading)) for reading in READINGS
            }
            rung["the look's rule, more surprise"] = {
                reading: number(m.from_look(world, block, reading)) for reading in READINGS
            }
            rung["a block fits"] = m.fits(world, block)
            ran = {}
            for name, size, reading, whose in sorted(m.ahead):
                if (name, size) != (world, block):
                    continue
                end = lambda what, b=block, r=reading, w=whose: m.end(  # noqa: E731
                    world, b, r, w, what)  # fmt: skip
                ran[f"{reading}, {whose}"] = {
                    "amiss over changed": number(over(end("amiss"), end("changed")), 4),
                    "walls kept": number(over(end("walls_rule"), end("walls_world")), 4),
                    "amiss over two runs of the rule": number(over(end("amiss"), end("twin")), 4),
                    "going back, the world and the rule's world": [
                        number(end("returns_world"), 4), number(end("returns_rule"), 4)],
                    "blocks that change hands in a tick, the world and the rule's world": [
                        number(end("changes_world"), 5), number(end("changes_rule"), 5)],
                }  # fmt: skip
            rung["run on"] = ran
        out["rungs"][str(block)] = rung
    for near in (3, 4, 5):
        out[f"the mix alone over the rule as it is, blocks of 8, {near} rival neighbours"] = (
            number(over(m.mixed(world, 8, near), m.chance(world, 8, None, near)), 4))  # fmt: skip
        out[f"the share of the fall from blocks of 8 to 16 that is the mix, {near}"] = number(
            m.mix_share(world, 8, near), 4)  # fmt: skip
    records = [r for r in m.rows if r["kind"] == "start" and r["world"] == world]
    out["live"] = {g: round(float(np.mean([r["live"][g] for r in records])), 4)
                   for g in records[0]["live"]}  # fmt: skip
    out["walls at the start of each rung's age"] = {
        str(b): round(float(np.mean([r["walls"][str(b)][str(AGES[b][0])] for r in records])), 4)
        for b in BLOCKS}  # fmt: skip
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    plan = design()
    have = {(r["world"], r["seed"]) for r in rows if r["kind"] == "start"}
    missing = [f"{name} from start {seed}" for name, seed in start_jobs(plan)
               if (name, seed) not in have]  # fmt: skip
    if not missing:
        done = {(r["world"], r["seed"], r["block"], r["reading"], r["rule"]) for r in rows
                if r["kind"] == "ahead"}  # fmt: skip
        missing = [f"the run-on of the rule {job[3]}, {job[4]}, in the {job[0]} world from "
                   f"start {job[1]}, blocks of {job[2]}" for job in ahead_jobs(rows, plan)
                   if tuple(job[:5]) not in done]  # fmt: skip
    outcomes, measured, reported = {}, {}, {}
    if missing:
        outcomes = {c["label"]: "missing" for c in registered}
    else:
        m = Measures(rows, plan)
        for c in registered:
            value = m.value(c)
            outcomes[c["label"]] = judge(value, c, m.stands(c))
            measured[c["label"]] = {"value": number(value)}
        reported = {world: told(m, world) for world in plan}

    def overall(family: str) -> str:
        words = {outcomes[c["label"]] for c in registered if c["family"] == family}
        for word in ("missing", "fails", "holds"):
            if word in words:
                return word
        return "not tested"

    counts = {}
    for c in registered:
        word = outcomes[c["label"]]
        counts.setdefault(c["family"], {}).setdefault(word, 0)
        counts[c["family"]][word] += 1
    return {
        "verdict": {f: overall(f) for f in sorted({c["family"] for c in registered})},
        "counts": counts,
        "outcomes": outcomes,
        "measured": measured,
        "missing": missing[:20],
        "worlds": reported,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def question() -> dict:
    plan = design()
    return {
        "id": "scale-up-memory",
        "title": "The coarse rule of a world of territories has a memory.",
        "statement": "Two worlds of territories are read through blocks of 4, 8 and 16, each "
        "on the square clock over the generations that match it, from sixteen fresh starts. "
        "How long a block has had its leader says what it does next (A). With that in view "
        "the top of the coarse rule's table is the same from blocks of 8 to 16, and the fall "
        "of the rule as it is there is the mix of young and old leads (B); along the walls "
        "the table still changes at every age of the lead, and one tick ahead the "
        "remembering rule changes from rung to rung nearly as much as the plain one (C). Run "
        "on by itself, the rule with how long in view ends with fewer blocks amiss, does not "
        "lose walls, and goes back as often as the world does (D); and learned one rung "
        "down it runs a rung on nearly as well as the rung's own, where the plain rule from "
        "below pays (E). The rules the look learned on another grid serve here unchanged "
        "(R), and with nothing of the past in view these are the worlds of steps 4e and 4g "
        "(X).",
        "source": "docs/scale-up-plan.md, step 4h and decision D13",
        "worlds": {name: {"rules": [w["rule"]] * 2, "tie_break": "standoff", "density": 1.0,
                          "learned_from": plan[name]["learn"], "tried_on": plan[name]["try"]}
                   for name, w in WORLDS.items()},  # fmt: skip
        "side": SIDE,
        "generations": GENERATIONS,
        "matched_ages": {str(b): {"generations": list(AGES[b]), "tick": ladder.square(b)}
                         for b in BLOCKS},  # fmt: skip
        "readings": {PLAIN: "the leader, and how many of the eight neighbours each species "
                     "leads", HOW: "the same, and for how many ticks running the block has "
                     "had its leader, up to 8"},  # fmt: skip
        "runs": len(start_jobs(plan)) + 5 * len(RUNGS) * (STARTS // 2) * len(WORLDS),
        "run_ons_of_a_rule_from_a_start": 2 * PAIRS,
        "not_tested": "A claim about a chance is not tested where fewer than "
        f"{ENOUGH} blocks stand behind a chance it compares. A claim about a rule run on "
        "through blocks of some size is not tested where more than "
        f"{BLOCK_FITS} of neighbouring blocks of that size have different leaders when the "
        "rule is started, on the world's trial starts. And no claim is tested without a "
        "number to judge.",
        "sizing": json.loads(SIZING.read_text())["what the bounds were drawn from"],
        "sha256": {
            "study.py": sha(HERE / "study.py"),
            "look.py": sha(HERE / "look.py"),
            "sizing.json": sha(SIZING),
            "reference.json": sha(REFERENCE),
            "../scale-up-rung/study.py": sha(STEP_4G / "study.py"),
            "../scale-up-closure-territories/ladder.py": sha(STEP_4E / "ladder.py"),
        },
        "excluded_seen": [
            "The look (look.py here, step 4h): step 4g's sixteen runs on side 2,048 from "
            "starts 18001 to 18108, read with a block's past in view. Every claim here was "
            "read off it, and reference.json holds its rules.",
            "The sizing look (sizing.py here, exploratory): step 4d's kept runs on side "
            "1,024 from starts 15001 to 15008 through this study's measures, four starts to "
            "learn from and four to try on, with the look's rules tried and run on there. "
            "Every bound here was drawn from it and from the look. It ran no world.",
            "Steps 4d, 4e and 4g ran these two worlds on sides 1,024 and 2,048 from starts "
            "15001 to 15008, 16001 to 16108 and 18001 to 18108, and read them with nothing "
            "of a block's past in view.",
            "No start from 19001 on has been generated or run.",
        ],
    }  # fmt: skip


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    if record["kind"] == "start":
        return run_start((record["world"], record["seed"]))
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    wanted = (record["world"], record["seed"], record["block"], record["reading"], record["rule"])
    for job in ahead_jobs(rows, design()):
        if tuple(job[:5]) == wanted:
            return run_ahead(job)
    raise ValueError(f"no run-on {wanted} in this design")


STUDY = Study(
    directory=HERE,
    question=question,
    predictions=predictions,
    execute=execute,
    decide=decide,
    rerun=rerun,
)

if __name__ == "__main__":
    main(STUDY)
