"""
A registered test: does a coarse rule stand in for a world of territories, and is it one rule
for worlds that have never been zoomed out?

    uv run --no-sync python examples/scale-up-closure-territories/study.py register
    uv run --no-sync python examples/scale-up-closure-territories/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-closure-territories

**Why.** A first look (look.py, exploratory; step 4d of docs/scale-up-plan.md) zoomed out two
worlds in which two species with one rule between them sort into territories that keep
growing: B245678/S3678 against its copy (still grounds, only the walls move) and
B23467/S4568 against its copy (busy grounds). Read by who leads each block, it found four
things. A block changes hands by being surrounded. Run on by itself, a table of what blocks
with as many rival neighbours did next keeps the world's walls and says where most of its
territories will be three thousand generations on. The table of one world serves in the
other. And it changes from one block size to the next, less on the clock these worlds keep
(the square of the block) than on the clock that goes with the block. All of that was read
off the same runs it describes. This puts it to fresh starts, and to worlds no run has
zoomed out.

**What is run** (`WORLDS`). Each world is a rule against a copy of itself under the standoff
on a wrapped grid of side 1,024 for 4,096 generations, read through blocks of 4, 8, 16 and 32
(`ladder.py`). Coarse rules are learned from half of a world's starts and tried on the other
half. No two worlds share a start.

    still     B245678/S3678    the first look's two worlds, from eight fresh starts each
    busy      B23467/S4568
    near      B24678/S34678    three worlds that have never been zoomed out:
    another   B3568/S124678    a near relative of the still world's rule, a still world
    sparse    B2/S0            whose rule shares little with it, and a sparse busy world
                               that holds territories under the standoff only
    set       B2578/S135678    the control: its territories set and stop growing

**The reference rules** (`reference.json`, written by sizing.py before the registration) are
the first look's own: the tables its sixteen runs give for the still world and for the busy
one. They are fixed here and tried, unchanged, in worlds and from starts they have not seen.

**Predictions** (`claims`), in eight families. The first look's number is in every claim.

    N  a block changes hands by being surrounded: the neighbours remove over a third of the
       surprise, and a block with five neighbours under its rival changes hands with the
       chance the first look found
    T  one rule at every time: the rule learned before generation 1,024 serves after it
    R  rungs and clocks: the rule from blocks half the size serves better on the square
       clock than on the block clock, and better at the second rung than at the first, and
       is still not the rung's own; the chance of changing hands halves from rung to rung
       on the block clock and falls by less on the square clock
    X  the first look's rule for a world serves on that world's fresh starts
    B  the first look's rule for one of its worlds serves in the other, the two worlds'
       chances of changing hands agree, and the still world's rule runs the busy world on
    C  run on by itself from generation 1,024, a world's own rule keeps its walls and says
       where its territories will be: in the first look's worlds, and in the three worlds
       never zoomed out
    U  the still world's rule in the three worlds never zoomed out: it serves there as it
       is, or at another pace (a slower or a quicker tick), and it runs them on
    Z  the control: in the world whose territories set, the still world's rule does not
       serve as it is, and run on it takes the world further from itself than leaving it
       alone would

A claim holds if its number is inside its bound, fails if it is not, and is **not tested**
if it has nothing to stand on (`Measures.stands`). A claim about a world that keeps growing
says nothing of a world that does not; the control's claims say nothing unless the control
has set; and in a world that keeps growing a run-on is read only through blocks small beside
its territories (five blocks across or more when the rule is started), since through larger
ones the first look's rule did little better than supposing nothing moved.

**What "at another pace" can and cannot say.** The sizing look ran the control once: the
still world's rule is 93% to 191% worse there on the square clock, but at the shortest tick
it is kept at, where blocks change hands least, it comes within 5% at blocks of 16. A world
that has stopped looks like a world slowed right down. So a rule that serves "at some pace"
is evidence of one rule only beside a world that keeps growing and a run-on that keeps it,
and the claims of family U are three to a block for that reason.

Surprise is the mean of -log2 of the chance a rule gave to what came next, on starts the
rule did not learn from. Every number but those of the run-ons is worked out again in
`decide` from the tallies in the records; a run-on's record holds what it measured.

**What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ladder  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

RECORDS = HERE / "records.jsonl"
REFERENCE = HERE / "reference.json"
SIZING = HERE / "sizing.json"

WORLDS = {
    "still": {"rule": "B245678/S3678", "density": 1.0, "first": 16001, "starts": 8},
    "busy": {"rule": "B23467/S4568", "density": 1.0, "first": 16101, "starts": 8},
    "near": {"rule": "B24678/S34678", "density": 1.0, "first": 16201, "starts": 8},
    "another": {"rule": "B3568/S124678", "density": 1.0, "first": 16301, "starts": 8},
    "sparse": {"rule": "B2/S0", "density": 0.5, "first": 16401, "starts": 8},
    "set": {"rule": "B2578/S135678", "density": 1.0, "first": 16501, "starts": 4},
}
SEEN = ("still", "busy")  # the first look's worlds
UNSEEN = ("near", "another", "sparse")  # never zoomed out
CONTROL = "set"
OWN, STILLS = "its own", "the still world's"  # whose rule a run-on runs


def design(worlds: dict | None = None) -> dict:
    """Which starts each world learns from and which it is tried on: the first half and the
    second half of its starts."""
    out = {}
    for name, w in (worlds or WORLDS).items():
        seeds = list(range(w["first"], w["first"] + w["starts"]))
        out[name] = {"learn": seeds[: len(seeds) // 2], "try": seeds[len(seeds) // 2 :]}
    return out


# --- the bounds ----------------------------------------------------------------------------------
# Each is set between what the first look gave and what would mean the finding had gone; the
# first look's numbers, and how far they move from one set of its starts to another, are in
# sizing.json.

SHARE_REMOVED = 0.35  # N: at least this share of the surprise, at blocks of 4 and 8
AT_FIVE = (0.32, 0.42)  # N: the chance of changing hands at five rival neighbours, blocks of 4
SAME_LATE = {4: 0.006, 8: 0.02, 16: 0.05}  # T: at most this much more surprise late
STILL_OPEN = 0.015  # R: at blocks of 16 the rung below is at least this much worse
MATCHED_FALLS = 0.65  # R: at matched ages the second rung's gap over the first's, at most
HALVES = {"block": (1.8, 2.9), "square": (1.2, 1.75)}  # R: the chance at 4 over that at 8
SAME_WORLD = {8: 0.003, 16: 0.005}  # X: the first look's rule on fresh starts of its world
OTHER_WORLD = {4: 0.025, 8: 0.008, 16: 0.008}  # B: one world's rule in the other
CHANCES_AGREE = 0.12  # B: the two worlds' chances at 4, 5 and 6 rival neighbours, within
WHERE = 0.70  # C, B, U: blocks amiss in the rule's world over blocks that changed, at most
WALLS = (0.85, 1.12)  # C: the rule's walls over the world's at blocks of 16
TOO_FAST = 0.93  # C: at blocks of 4 the rule ends with at most this share of the walls
OWN_DICE = 1.4  # C: blocks amiss over what two runs of the rule differ by, at most
SERVES = 0.01  # U: the still world's rule serves, as it is or at its best tick
FAR_OFF = 0.25  # Z: in the world that has set, as it is, it is at least this much worse
FURTHER = 0.10  # Z: run on, it is amiss in at least this many more blocks than the start
# what a claim stands on (`Measures.stands`): a world that keeps growing, a world that has set,
# and a block small enough beside the territories for a run-on to be read through it
COARSENS = {"walls": 0.8, "moved": 0.05}
HAS_SET = {"walls": 0.95, "moved": 0.02}
BLOCK_FITS = 0.2
RUN_ON = {  # which rules are run on by themselves where: world -> (whose rule, block, tick)
    **{w: [(OWN, b, ladder.square(b)) for b in ladder.BLOCKS] + [(OWN, b, b) for b in (8, 16)]
       for w in SEEN},
    **{w: [(OWN, b, ladder.square(b)) for b in (8, 16)] for w in UNSEEN},
}  # fmt: skip
for _world in ("busy", *UNSEEN, CONTROL):
    RUN_ON.setdefault(_world, []).extend((STILLS, b, ladder.square(b)) for b in (8, 16))


# --- the runs ------------------------------------------------------------------------------------


def run_start(job: tuple[str, int]) -> dict:
    """One world from one start: its record, with the leaders kept on disk for the run-ons."""
    name, seed = job
    w = WORLDS[name]
    size = (ladder.SIDE, ladder.GENERATIONS, ladder.BLOCKS)
    found = ladder.fine(name, w["rule"], w["density"], seed, *size)
    return ladder.start_record(name, seed, found, *size)


def reference() -> dict:
    """The first look's rules: world -> block and tick -> tally over the whole run."""
    kept = json.loads(REFERENCE.read_text())
    return {world: {where: ladder.dense(rows) for where, rows in tallies.items()}
            for world, tallies in kept["rules"].items()}  # fmt: skip


def pooled(rows: list[dict], world: str, seeds, block: int, tick: int, windows) -> np.ndarray:
    """The tallies of a world's starts `seeds` at a block and tick, over `windows`, added up."""
    total = np.zeros((ladder.Q, 9, 9, ladder.Q), dtype=np.int64)
    for row in rows:
        if row["kind"] == "start" and row["world"] == world and row["seed"] in seeds:
            for window in windows:
                total += ladder.dense(row["tally"][ladder.key(block, tick)].get(window, []))
    return total


def run_ahead(job: tuple[str, int, str, int, int, list]) -> dict:
    """A rule run on by itself from generation 1,024 of one start of one world."""
    name, seed, whose, block, tick, rows = job
    w = WORLDS[name]
    size = (ladder.SIDE, ladder.GENERATIONS, ladder.BLOCKS)
    frames = ladder.fine(name, w["rule"], w["density"], seed, *size)[block]
    draws = (seed, block, tick, (OWN, STILLS).index(whose))
    found = ladder.ahead(frames, ladder.dense(rows), block, tick, draws, ladder.FROM,
                         ladder.GENERATIONS)  # fmt: skip
    return {"kind": "ahead", "world": name, "seed": seed, "rule": whose, **found}


def start_jobs(plan: dict | None = None) -> list[tuple[str, int]]:
    """Every fine run, the worlds taking turns so that a run that stops has some of each."""
    plan = plan or design()
    seeds = {name: plan[name]["learn"] + plan[name]["try"] for name in plan}
    longest = max(len(s) for s in seeds.values())
    return [(name, s[i]) for i in range(longest) for name, s in seeds.items() if i < len(s)]


def ahead_jobs(rows: list[dict], plan: dict | None = None, kept: dict | None = None) -> list:
    plan = plan or design()
    kept = kept or reference()
    out = []
    for name, runs in RUN_ON.items():
        if name not in plan:
            continue
        for whose, block, tick in runs:
            if whose == OWN:
                counts = pooled(rows, name, plan[name]["learn"], block, tick, ladder.WHOLE)
            else:
                counts = kept["still"][ladder.key(block, tick)]
            for seed in plan[name]["try"]:
                out.append((name, seed, whose, block, tick, ladder.sparse(counts)))
    return out


def execute(path: Path, workers: int) -> None:
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    done = {(r["kind"], r["world"], r["seed"], r.get("rule"), r.get("block"), r.get("tick"))
            for r in rows}  # fmt: skip
    starts = [job for job in start_jobs() if ("start", *job, None, None, None) not in done]
    with ProcessPoolExecutor(max(workers, 1)) as pool:
        for record in pool.map(run_start, starts):
            append_records(path, [record])
            rows.append(record)
        ahead = [job for job in ahead_jobs(rows) if ("ahead", *job[:5]) not in done]
        for record in pool.map(run_ahead, ahead):
            append_records(path, [record])


# --- what is measured ----------------------------------------------------------------------------


def over(top: float | None, bottom: float | None) -> float | None:
    """One number over another, where the other is a number above nought."""
    if top is None or bottom is None or not np.isfinite(top) or not np.isfinite(bottom):
        return None
    return top / bottom if bottom > 0 else None


class Measures:
    """Every number a claim is judged on, from the records of a run, the starts each world
    learns from and is tried on, and the reference rules."""

    def __init__(self, rows: list[dict], plan: dict, kept: dict):
        self.rows, self.plan, self.kept = rows, plan, kept
        self.ahead: dict = {}
        for r in rows:
            if r["kind"] == "ahead":
                where = (r["world"], r["rule"], r["block"], r["tick"])
                self.ahead.setdefault(where, []).append(r)

    def tally(self, world: str, part: str, block: int, tick: int, windows) -> np.ndarray:
        seeds = self.plan[world]["learn"] + self.plan[world]["try"] if part == "all" else (
            self.plan[world][part])  # fmt: skip
        return pooled(self.rows, world, seeds, block, tick, windows)

    def own(self, world: str, block: int, tick: int | None = None, windows=ladder.WHOLE):
        """A world's own rule and the transitions it is tried on."""
        tick = tick or ladder.square(block)
        return (self.tally(world, "learn", block, tick, windows),
                self.tally(world, "try", block, tick, windows))  # fmt: skip

    # N
    def share_removed(self, world: str, block: int) -> float | None:
        rule, trial = self.own(world, block)
        alone = ladder.surprise(rule, trial, "own")
        return 1 - ladder.surprise(rule, trial, "total") / alone if alone > 0 else None

    def changes(self, world: str, block: int, tick: int, near: int = 5) -> float | None:
        return ladder.changes(self.tally(world, "all", block, tick, ladder.WHOLE), near)

    # T
    def early_rule_late(self, world: str, block: int) -> float:
        tick = ladder.square(block)
        early = self.tally(world, "learn", block, tick, ladder.EARLY)
        late, trial = self.own(world, block, tick, ladder.LATE)
        return ladder.excess(early, late, trial)

    # R
    def rung_below(self, world: str, block: int, clock: str) -> float:
        """The rule from blocks half the size, scaled to as much data, tried at this block."""
        tick = ladder.square(block) if clock == "square" else block
        below = ladder.square(block // 2) if clock == "square" else block // 2
        lower = self.tally(world, "learn", block // 2, below, ladder.WHOLE)
        here, trial = self.own(world, block, tick)
        return ladder.excess(ladder.as_much(lower, here), here, trial)

    def rung_below_matched(self, world: str, block: int) -> float:
        """The same on the square clock, each rung over the stretch it has its matched age in."""
        lower = self.tally(world, "learn", block // 2, ladder.square(block // 2),
                           ladder.MATCHED[block // 2])  # fmt: skip
        here, trial = self.own(world, block, None, ladder.MATCHED[block])
        return ladder.excess(ladder.as_much(lower, here), here, trial)

    def halves(self, world: str, clock: str) -> float | None:
        """The chance of changing hands at five rival neighbours, blocks of 4 over blocks of 8."""
        tick = ladder.square(8) if clock == "square" else 8
        return over(self.changes(world, 4, 4), self.changes(world, 8, tick))

    # X, B, U, Z
    def from_elsewhere(self, world: str, whose: str, block: int, tick: int | None = None) -> float:
        """The reference rule of `whose` world at `tick`, tried in `world` at its square tick."""
        rule = self.kept[whose][ladder.key(block, tick or ladder.square(block))]
        here, trial = self.own(world, block)
        return ladder.excess(rule, here, trial)

    def best_tick(self, world: str, whose: str, block: int) -> tuple[float, int]:
        """The least of `from_elsewhere` over the ticks the reference rule is kept at, and the
        tick that gives it."""
        found = {tick: self.from_elsewhere(world, whose, block, tick)
                 for tick in ladder.TICKS[block]}  # fmt: skip
        tick = min(found, key=found.get)
        return found[tick], tick

    def chances_apart(self, first: str, second: str, block: int) -> float | None:
        """How far apart two worlds' chances of changing hands are at 4, 5 and 6 rival
        neighbours on the square clock: the largest of |one over the other, less one|."""
        tick = ladder.square(block)
        pairs = [(self.changes(first, block, tick, k), self.changes(second, block, tick, k))
                 for k in ladder.NEAR]  # fmt: skip
        if any(not a or not b for a, b in pairs):
            return None
        return max(abs(a / b - 1) for a, b in pairs)

    # C: the run-ons
    def end(self, world: str, whose: str, block: int, tick: int, what: str) -> float | None:
        """The mean over a world's trial starts of what a run-on measured at its last horizon."""
        runs = self.ahead.get((world, whose, block, tick), [])
        seeds = sorted(r["seed"] for r in runs)
        if not runs or seeds != sorted(self.plan[world]["try"]):
            return None
        return float(np.mean([r[what][-1] for r in runs]))

    def ratio(self, world, whose, block, tick, top: str, bottom: str) -> float | None:
        return over(self.end(world, whose, block, tick, top),
                    self.end(world, whose, block, tick, bottom))  # fmt: skip

    def walls(self, world: str, block: int) -> tuple[float, float] | None:
        """The world's walls at blocks of `block`, at the generation a rule is run on from and
        at the last: the mean over its trial starts."""
        records = [r for r in self.rows if r["kind"] == "start" and r["world"] == world
                   and r["seed"] in self.plan[world]["try"]]  # fmt: skip
        if not records:
            return None
        first, last = (str(g) for g in ladder.WINDOWS["C"])
        return (float(np.mean([r["walls"][str(block)][first] for r in records])),
                float(np.mean([r["walls"][str(block)][last] for r in records])))  # fmt: skip

    def moved(self, world: str) -> float | None:
        """The share of blocks of 16 with another leader at the last generation than at the
        one a rule is run on from, on the world's trial starts."""
        whose = OWN if (OWN, 16, ladder.square(16)) in RUN_ON.get(world, []) else STILLS
        return self.end(world, whose, 16, ladder.square(16), "apart_start")

    def coarsens(self, world: str) -> bool:
        """Whether a world keeps growing over the stretch a rule is run on: at blocks of 16,
        on its trial starts, the walls at the last generation are at most 0.8 of those at
        generation 1,024, and at least a twentieth of the blocks have another leader."""
        walls, moved = self.walls(world, 16), self.moved(world)
        if walls is None or moved is None or walls[0] <= 0:
            return False
        return walls[1] <= COARSENS["walls"] * walls[0] and moved >= COARSENS["moved"]

    def has_set(self, world: str) -> bool:
        """Whether a world has stopped: at blocks of 16 its walls at the last generation are
        at least 0.95 of those at generation 1,024, and at most a fiftieth of the blocks have
        another leader."""
        walls, moved = self.walls(world, 16), self.moved(world)
        if walls is None or moved is None or walls[0] <= 0:
            return False
        return walls[1] >= HAS_SET["walls"] * walls[0] and moved <= HAS_SET["moved"]

    def fits(self, world: str, block: int) -> bool:
        """Whether a block is small beside the world's territories when a rule is run on from
        it: at generation 1,024 at most a fifth of neighbouring blocks have different leaders,
        so that a territory is five blocks across or more."""
        walls = self.walls(world, block)
        return walls is not None and walls[0] <= BLOCK_FITS

    def stands(self, claim: dict) -> bool:
        """Whether a claim has what it needs to be tested: its world in the state the claim
        is about, and, for a run-on, a block that fits."""
        needs = claim["needs"]
        state = self.has_set if needs["state"] == "has set" else self.coarsens
        return state(needs["world"]) and (
            needs["block"] is None or self.fits(needs["world"], needs["block"]))  # fmt: skip

    def value(self, claim: dict) -> float | None:
        """The number one claim is judged on."""
        q, world, block = claim["quantity"], claim["world"], claim.get("block")
        whose, clock = claim.get("rule"), claim.get("clock", "square")
        tick = (ladder.square(block) if clock == "square" else block) if block else None
        if q == "share removed":
            return self.share_removed(world, block)
        if q == "changes at five":
            return self.changes(world, block, tick)
        if q == "early rule late":
            return self.early_rule_late(world, block)
        if q == "rung below, square less block":
            return self.rung_below(world, block, "square") - self.rung_below(world, block, "block")
        if q == "rung below":
            return self.rung_below(world, block, "square")
        if q == "rung below, second over first":
            return over(self.rung_below(world, 16, "square"), self.rung_below(world, 8, "square"))
        if q == "rung below at matched ages, second over first":
            return over(self.rung_below_matched(world, 16), self.rung_below_matched(world, 8))
        if q == "chance at 4 over chance at 8":
            return self.halves(world, clock)
        if q == "rule from elsewhere":
            return self.from_elsewhere(world, whose, block)
        if q == "rule from elsewhere, best tick":
            return self.best_tick(world, whose, block)[0]
        if q == "chances apart":
            return self.chances_apart(world, claim["other"], block)
        whose = STILLS if whose == "still" else OWN
        if q == "amiss over changed":
            return self.ratio(world, whose, block, tick, "apart_rule", "apart_start")
        if q == "walls kept":
            return self.ratio(world, whose, block, tick, "walls_rule", "walls_world")
        if q == "amiss over two runs":
            return self.ratio(world, whose, block, tick, "apart_rule", "apart_twin")
        if q == "amiss, square over block":
            return over(self.end(world, whose, block, ladder.square(block), "apart_rule"),
                        self.end(world, whose, block, block, "apart_rule"))  # fmt: skip
        if q == "amiss less changed":
            a = self.end(world, whose, block, tick, "apart_rule")
            b = self.end(world, whose, block, tick, "apart_start")
            return a - b if a is not None and b is not None else None
        raise ValueError(f"unknown quantity {q!r}")


# --- the predictions -----------------------------------------------------------------------------


def rule_text(name: str) -> str:
    return f"{WORLDS[name]['rule']} against its copy (the {name} world)"


def claims(worlds: dict | None = None) -> list[dict]:
    """Every claim: its label and family, the quantity it is judged on and where, its bound
    (`at_least`, `at_most`), and `needs`, what it stands on: the world that has to keep
    growing (or, for the control, to have set) and, where a rule is run on, the block that
    has to be small beside the world's territories."""
    worlds = worlds or WORLDS
    seen = [w for w in SEEN if w in worlds]
    unseen = [w for w in UNSEEN if w in worlds]
    out = []

    def claim(family, label, text, quantity, world, at_least=None, at_most=None, **more):
        # a run-on in a world that keeps growing is read only through a block that fits; in
        # the control nothing should move, whatever the size of its territories
        run_on = quantity.startswith(("amiss", "walls kept")) and world != CONTROL
        needs = {"world": world, "state": "has set" if world == CONTROL else "keeps growing",
                 "block": more.get("block") if run_on else None}  # fmt: skip
        out.append({"label": label, "family": family, "claim": text, "quantity": quantity,
                    "world": world, "at_least": at_least, "at_most": at_most, "needs": needs,
                    **more})  # fmt: skip

    for w in seen:
        for b in (4, 8):
            claim("N", f"N {w}, block {b}: the neighbours",
                  f"in {rule_text(w)}, knowing how many of a block of {b}'s neighbours each "
                  f"species leads removes at least {SHARE_REMOVED:.0%} of the surprise of "
                  "knowing the block alone, on the square clock",
                  "share removed", w, at_least=SHARE_REMOVED, block=b)  # fmt: skip
        claim("N", f"N {w}: surrounded",
              f"in the {w} world a block of 4 with five of its eight neighbours under its "
              f"rival changes hands in four generations with a chance between {AT_FIVE[0]} "
              f"and {AT_FIVE[1]}",
              "changes at five", w, at_least=AT_FIVE[0], at_most=AT_FIVE[1], block=4)  # fmt: skip
        for b, bound in SAME_LATE.items():
            claim("T", f"T {w}, block {b}",
                  f"in the {w} world the rule learned before generation 1,024 has at most "
                  f"{bound:.1%} more surprise after it than the rule learned after it, at "
                  f"blocks of {b} on the square clock",
                  "early rule late", w, at_most=bound, block=b)  # fmt: skip
        for b in (8, 16):
            claim("R", f"R {w}, block {b}: the clock",
                  f"in the {w} world the rule from blocks of {b // 2}, tried at blocks of {b} "
                  "with as much data as the rung's own rule, has less surprise over the "
                  "rung's own on the square clock than on the block clock",
                  "rung below, square less block", w, at_most=0.0, block=b)  # fmt: skip
        claim("R", f"R {w}: the gap shrinks",
              f"in the {w} world, on the square clock, the rule from the rung below is "
              "nearer the rung's own at blocks of 16 than at blocks of 8",
              "rung below, second over first", w, at_most=1.0)  # fmt: skip
        claim("R", f"R {w}: no fixed point yet",
              f"in the {w} world, on the square clock, the rule from blocks of 8 still has "
              f"at least {STILL_OPEN:.1%} more surprise at blocks of 16 than the rung's own",
              "rung below", w, at_least=STILL_OPEN, block=16)  # fmt: skip
        claim("R", f"R {w}: at matched ages",
              f"in the {w} world, with each rung read over the generations that match its "
              "block (4: 64 to 256; 8: 256 to 1,024; 16: 1,024 to 4,096), the gap at blocks "
              f"of 16 is at most {MATCHED_FALLS} of the gap at blocks of 8",
              "rung below at matched ages, second over first", w,
              at_most=MATCHED_FALLS)  # fmt: skip
        for clock, (low, high) in HALVES.items():
            claim("R", f"R {w}: changing hands, {clock} clock",
                  f"in the {w} world a block of 4 with five neighbours under its rival changes "
                  f"hands between {low} and {high} times as often as a block of 8 does, with "
                  f"the clock at {'the block' if clock == 'block' else 'its square'}",
                  "chance at 4 over chance at 8", w, at_least=low, at_most=high,
                  clock=clock)  # fmt: skip
        for b, bound in SAME_WORLD.items():
            claim("X", f"X {w}, block {b}",
                  f"the first look's rule for the {w} world has at most {bound:.1%} more "
                  f"surprise on fresh starts of it than the rule learned from fresh starts, at "
                  f"blocks of {b} on the square clock",
                  "rule from elsewhere", w, at_most=bound, block=b, rule=w)  # fmt: skip
    if len(seen) == 2:
        first, second = seen
        for w, other in ((second, first), (first, second)):
            for b, bound in OTHER_WORLD.items():
                claim("B", f"B the {other} world's rule in the {w} world, block {b}",
                      f"the first look's rule for the {other} world has at most {bound:.1%} "
                      f"more surprise in the {w} world than the rule learned there, at "
                      f"blocks of {b} on the square clock",
                      "rule from elsewhere", w, at_most=bound, block=b, rule=other)  # fmt: skip
        for b in (8, 16):
            claim("B", f"B the two worlds' chances, block {b}",
                  f"at blocks of {b} on the square clock, a block with 4, 5 or 6 neighbours "
                  f"under its rival changes hands with chances within {CHANCES_AGREE:.0%} of "
                  "each other in the two worlds",
                  "chances apart", first, at_most=CHANCES_AGREE, block=b, other=second)  # fmt: skip
            claim("B", f"B the still world's rule runs the busy world on, block {b}",
                  "run on by itself in the busy world from generation 1,024, the first "
                  "look's rule for the still world ends with another leader than the real "
                  f"world's in at most {WHERE} of the share of blocks that changed leader "
                  f"meanwhile, at blocks of {b} on the square clock",
                  "amiss over changed", "busy", at_most=WHERE, block=b, rule="still")  # fmt: skip
    for w in (*seen, *unseen):
        for b in (4, 8, 16) if w in seen else (8, 16):
            claim("C", f"C {w}, block {b}: where",
                  f"run on by itself from generation 1,024, the {w} world's own rule ends "
                  "with another leader than the real world's in at most "
                  f"{WHERE} of the share of blocks that changed leader meanwhile, at blocks "
                  f"of {b} on the square clock",
                  "amiss over changed", w, at_most=WHERE, block=b)  # fmt: skip
        claim("C", f"C {w}: walls",
              f"and at blocks of 16 it ends with between {WALLS[0]} and {WALLS[1]} of the "
              f"{w} world's walls",
              "walls kept", w, at_least=WALLS[0], at_most=WALLS[1], block=16)  # fmt: skip
    for w in seen:
        claim("C", f"C {w}: too fast at blocks of 4",
              f"at blocks of 4 the {w} world's rule loses walls too fast: it ends with at "
              f"most {TOO_FAST} of them",
              "walls kept", w, at_most=TOO_FAST, block=4)  # fmt: skip
        for b in (8, 16):
            claim("C", f"C {w}, block {b}: its own dice",
                  f"at blocks of {b} the {w} world's rule ends at most {OWN_DICE} times as "
                  "far from the real world as two runs of it end from each other",
                  "amiss over two runs", w, at_most=OWN_DICE, block=b)  # fmt: skip
            claim("C", f"C {w}, block {b}: the clock",
                  f"at blocks of {b} the {w} world's rule ends nearer the real world run on "
                  "with the square clock than with the block clock",
                  "amiss, square over block", w, at_most=1.0, block=b)  # fmt: skip
    for w in unseen:
        for b in (8, 16):
            claim("U", f"U {w}, block {b}: as it is",
                  f"the first look's rule for the still world has at most {SERVES:.0%} more "
                  f"surprise in {rule_text(w)} than the rule learned there, at blocks of {b} "
                  "on the square clock",
                  "rule from elsewhere", w, at_most=SERVES, block=b, rule="still")  # fmt: skip
            claim("U", f"U {w}, block {b}: at some pace",
                  f"and at the best of the ticks it is kept at "
                  f"({', '.join(map(str, ladder.TICKS[b]))} generations), at most "
                  f"{SERVES:.0%} more",
                  "rule from elsewhere, best tick", w, at_most=SERVES, block=b,
                  rule="still")  # fmt: skip
            claim("U", f"U {w}, block {b}: run on",
                  f"run on by itself in the {w} world from generation 1,024, the still "
                  "world's rule ends with another leader than the real world's in at most "
                  f"{WHERE} of the share of blocks that changed leader meanwhile, at blocks "
                  f"of {b} on the square clock",
                  "amiss over changed", w, at_most=WHERE, block=b, rule="still")  # fmt: skip
    if CONTROL in worlds:
        for b in (8, 16):
            claim("Z", f"Z block {b}: as it is",
                  f"in {rule_text(CONTROL)}, whose territories set, the still world's rule "
                  f"has at least {FAR_OFF:.0%} more surprise than the rule learned there, at "
                  f"blocks of {b} on the square clock",
                  "rule from elsewhere", CONTROL, at_least=FAR_OFF, block=b,
                  rule="still")  # fmt: skip
            claim("Z", f"Z block {b}: run on",
                  "and run on by itself there from generation 1,024 it ends with another "
                  f"leader than the real world's in at least {FURTHER:.0%} of the blocks more "
                  "than changed leader meanwhile: further from the world than leaving it "
                  "alone",
                  "amiss less changed", CONTROL, at_least=FURTHER, block=b,
                  rule="still")  # fmt: skip
    return out


def predictions() -> list[dict]:
    return claims()


# --- the verdict ---------------------------------------------------------------------------------


def judge(value: float | None, claim: dict, stands: bool) -> str:
    """holds, fails, or not tested: where the claim has nothing to stand on (`Measures.stands`)
    or there is no number to judge."""
    if not stands or value is None or not np.isfinite(value):
        return "not tested"
    if claim["at_least"] is not None and value < claim["at_least"]:
        return "fails"
    if claim["at_most"] is not None and value > claim["at_most"]:
        return "fails"
    return "holds"


def number(value, places: int = 5) -> float | None:
    """A number as the verdict holds it: rounded, and nothing where there is none."""
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), places)


def reported(m: Measures, worlds) -> dict:
    """What a reader wants beside the verdicts, world by world."""
    out: dict = {}
    for w in worlds:
        records = [r for r in m.rows if r["kind"] == "start" and r["world"] == w]
        first, last = (str(g) for g in ladder.WINDOWS["C"])
        told: dict = {
            "keeps growing": m.coarsens(w),
            "has set": m.has_set(w),
            "blocks small beside its territories": [b for b in ladder.BLOCKS if m.fits(w, b)],
            "blocks of 16 with another leader by the end": number(m.moved(w)),
            "live": {g: round(float(np.mean([r["live"][g] for r in records])), 4)
                     for g in records[0]["live"]},
            "larger species": {g: round(float(np.mean([r["larger"][g] for r in records])), 4)
                               for g in records[0]["larger"]},
            "walls": {b: [round(float(np.mean([r["walls"][b][g] for r in records])), 4)
                          for g in (first, last)] for b in records[0]["walls"]},
            "changes hands": {},
            "the still world's rule": {},
            "run on": {},
        }  # fmt: skip
        for block in ladder.BLOCKS:
            for tick in ladder.TICKS[block]:
                found = ladder.hands(m.tally(w, "all", block, tick, ladder.WHOLE))
                told["changes hands"][ladder.key(block, tick)] = [
                    round(float(c / b), 5) if b else None for b, c in found]  # fmt: skip
        for block in (4, 8, 16):
            told["the still world's rule"][str(block)] = {
                str(tick): number(m.from_elsewhere(w, "still", block, tick))
                for tick in ladder.TICKS[block]}  # fmt: skip
        for (world, whose, block, tick), runs in sorted(m.ahead.items()):
            if world == w:
                told["run on"][f"{whose}, {ladder.key(block, tick)}"] = {
                    what: [round(float(v), 5) for v in np.mean([r[what] for r in runs], axis=0)]
                    for what in ("walls_world", "walls_rule", "apart_rule", "apart_start",
                                 "apart_twin")}  # fmt: skip
        out[w] = told
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    plan = design()
    kept = reference()
    have = {(r["world"], r["seed"]) for r in rows if r["kind"] == "start"}
    missing = [f"{name} from start {seed}" for name, seed in start_jobs(plan)
               if (name, seed) not in have]  # fmt: skip
    if not missing:
        done = {(r["world"], r["seed"], r["rule"], r["block"], r["tick"])
                for r in rows if r["kind"] == "ahead"}  # fmt: skip
        missing = [f"the run-on of {job[2]} rule in the {job[0]} world from start {job[1]} at "
                   f"block {job[3]}, tick {job[4]}"
                   for job in ahead_jobs(rows, plan, kept)
                   if tuple(job[:5]) not in done]  # fmt: skip
    outcomes, measured = {}, {}
    if missing:
        outcomes = {c["label"]: "missing" for c in registered}
    else:
        m = Measures(rows, plan, kept)
        for c in registered:
            value = m.value(c)
            outcomes[c["label"]] = judge(value, c, m.stands(c))
            found = {"value": number(value)}
            if c["quantity"] == "rule from elsewhere, best tick":
                found["tick"] = m.best_tick(c["world"], c["rule"], c["block"])[1]
            measured[c["label"]] = found

    def overall(family: str) -> str:
        words = {outcomes[c["label"]] for c in registered if c["family"] == family}
        for word in ("missing", "fails", "holds"):
            if word in words:
                return word
        return "not tested"

    return {
        "verdict": {
            family: overall(family) for family in sorted({c["family"] for c in registered})
        },
        "outcomes": outcomes,
        "measured": measured,
        "missing": missing[:20],
        "worlds": {} if missing else reported(Measures(rows, plan, kept), plan),
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def question() -> dict:
    plan = design()
    return {
        "id": "scale-up-closure-territories",
        "title": "Does a coarse rule stand in for a world of territories, and is it one rule "
        "for worlds never zoomed out?",
        "statement": "Two species with one rule between them, each counting only its own "
        "kind, sort into territories that keep growing. Read through blocks by who leads "
        "each block: a block changes hands by being surrounded (N); it is the same rule early "
        "and late (T); from one block size to the next the rule changes, less on the square "
        "clock than on the block clock and less at each rung (R); the first look's rule for a "
        "world serves on fresh starts of it (X) and in the other world (B); run on by itself "
        "a world's own rule keeps its walls and says where its territories will be (C); the "
        "still world's rule serves in three worlds never zoomed out, as it is or at another "
        "pace, and runs them on (U); and in a world whose territories set it does not (Z).",
        "source": "docs/scale-up-plan.md, step 4d and decision D10; the first look in "
        "examples/scale-up-closure-territories/look.py",
        "worlds": {
            name: {"rules": [w["rule"]] * 2, "tie_break": "standoff", "density": w["density"],
                   "learned_from": plan[name]["learn"], "tried_on": plan[name]["try"],
                   "seen_zoomed_out": name in SEEN or name == CONTROL}
            for name, w in WORLDS.items()
        },  # fmt: skip
        "side": ladder.SIDE,
        "generations": ladder.GENERATIONS,
        "blocks": list(ladder.BLOCKS),
        "ticks": {str(b): list(t) for b, t in ladder.TICKS.items()},
        "windows": {name: list(span) for name, span in ladder.WINDOWS.items()},
        "run_on": {"from_generation": ladder.FROM,
                   "rules": {w: [list(r) for r in runs] for w, runs in RUN_ON.items()}},
        "runs": len(start_jobs(plan)) + sum(len(plan[w]["try"]) * len(r)
                                            for w, r in RUN_ON.items()),
        "not_tested": "On a world's trial starts, at blocks of 16: it keeps growing if its "
        f"walls at generation 4,096 are at most {COARSENS['walls']} of those at generation "
        f"1,024 and at least {COARSENS['moved']:.0%} of its blocks have another leader; it "
        f"has set if its walls are at least {HAS_SET['walls']} of them and at most "
        f"{HAS_SET['moved']:.0%} of its blocks have another leader. A claim about a world that "
        "keeps growing is not tested where the world does not; the control's claims are not "
        "tested unless the control has set; a claim about a rule run on in a world that "
        f"keeps growing is not tested through blocks of a size at which more than {BLOCK_FITS} "
        "of neighbouring blocks have different leaders at generation 1,024 (territories under "
        "five blocks across); and no claim is tested without a number to judge.",
        "sizing": json.loads(SIZING.read_text())["what the bounds were drawn from"],
        "sha256": {name: sha(HERE / name) for name in
                   ("study.py", "ladder.py", "reference.json", "sizing.json", "look/summary.json")},
        "excluded_seen": [
            "The first look (look.py, exploratory): the still world and the busy world on "
            "side 1,024 from starts 15001 to 15008, read through blocks of 4 to 32. Every "
            "bound here was drawn from it, and its rules are the reference rules.",
            "The sizing look (sizing.py, exploratory): the first look's runs again through "
            "this study's measures, with the starts learned from and tried on exchanged and "
            "halved; and the control world (B2578/S135678) on side 512 from starts 15101 "
            "and 15102, read by who leads each block, to see that its leaders stop changing "
            "and what the still world's rule makes of it. Its claims were drawn from that.",
            "The search (examples/scale-up-search, exploratory) ran all six rules against "
            "their copies on sides 256, 512 and 1,024 from starts 11001, 12001 to 12003 and "
            "13001, and read them by their correlation area and their species' shares: that "
            "is how they were chosen. B2/S0 was seen to hold territories from a half-full "
            "start only, which is why it starts half full here. Neither the registered test "
            "of step 4c nor its sizing ran any of the six.",
            "No run of B24678/S34678, B3568/S124678 or B2/S0 has been read by who leads a "
            "block, no coarse rule has been learned from one, and no start from 16001 on has "
            "been generated or run.",
        ],
    }  # fmt: skip


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`). A run-on is computed from
    the tallies the records file holds, or from the reference rule."""
    if record["kind"] == "start":
        return run_start((record["world"], record["seed"]))
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    wanted = (record["world"], record["seed"], record["rule"], record["block"], record["tick"])
    for job in ahead_jobs(rows):
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
