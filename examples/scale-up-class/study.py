"""
A registered test: how wide is the class of worlds that one coarse rule runs?

    uv run --no-sync python examples/scale-up-class/study.py register
    uv run --no-sync python examples/scale-up-class/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-class

**Why.** Step 4e of docs/scale-up-plan.md (examples/scale-up-closure-territories) found that a
table of who leads a block next, read off one world of territories (B245678/S3678 against its
copy, the still world), serves in other worlds: in one as it is, in one at half its pace, and
in a sparse world not at all. The world it served at half its pace was also the world whose
walls, read with no coarse rule at all, said half the pace; and the world it did not serve
was the one whose walls thin on another clock. That is four worlds and a stranger. This asks
the same of thirty-eight worlds no run has zoomed out.

**The worlds** (`worlds.json`, chosen by `select` from the registered runs of step 4c, which
set 842 randomly drawn rules against copies of themselves on a small grid). 207 of those
rules grew territories under the standoff from a full start. What sets them apart at a
glance is how much of the grid is live at the end: 11 fill it (nine tenths or more), and
the rest stay busy, from a quarter live to nine tenths. The test takes all 11 that fill
and, of the 600 rules of step 4c's even draw, 27 of the 76 that do not: every one under
three tenths live, the first ten drawn between three and five tenths, the first ten between
five and seven, the first four between seven and nine. Each is run against its copy under
the standoff on a wrapped grid of side 1,024 for 4,096 generations, from four fresh starts
(two to learn its own rule from, two to try on). The still world is run again from eight,
and its rule here is the rule every other world is tried with.

**What is read** (the measures are step 4e's, `ladder.py` there). A block is whoever leads
it. Blocks of 8 are read every four generations and blocks of 16 every sixteen, so that the
still world's rule can be learned at eleven paces: for a coarse generation of a quarter to
four times the square clock's (`RATIOS`).

- **A world's clock** (`power`): the power of time by which its walls thin between
  generations 1,024 and 4,096, at blocks of 8. A half for walls that move by how they curve.
- **Whether the still world's rule serves it** (`least`): the least, over the eleven paces,
  of how much more surprise the still world's rule has on the world's trial starts than the
  world's own rule.
- **Its pace, two ways.** By its walls (`pace_by_walls`): the square of the still world's
  walls over the world's, which owes nothing to any coarse rule. And by the rule
  (`pace_by_rule`): the pace at which the still world's rule serves it best.
- **Run on** (`ahead`): from the zoomed-out world at generation 1,024 the still world's rule
  for the pace the world's walls give is run on by itself in the world's own time, and read
  as step 4e read a run-on: the blocks whose leader is not the real world's at generation
  4,096, over the blocks that changed leader meanwhile.

**Predictions** (`claims`), in six families.

    A  a world's clock says whether the rule serves it: where its walls thin as about the
       square root of the time (a power of 0.40 or more) the still world's rule serves at
       some pace, within 1%; where they thin as a power of 0.33 or less it does not, by 5%
       or more
    F  a world that fills its grid keeps the square-root clock or has set: its walls thin as
       a power of 0.40 or more, or of 0.10 or less, and never in between
    P  the pace two ways: where a world keeps the square-root clock, the pace at which the
       rule serves it best is within half again of the pace its walls give
    K  run on at the pace its walls give, the still world's rule keeps such a world: it is
       amiss in at most 0.70 of the share of blocks that changed leader
    R  over those worlds, the faster by its walls is the faster by the rule
    X  the still world's rule here is the first look's (the anchor)

A claim holds if its number is inside its bound, fails if it is not, and is **not tested**
if it has nothing to stand on (`Measures.stands`): a world in which one species has all but
taken the grid is not a world of territories; a clock between the two powers says neither;
P and K are about worlds on the square-root clock, at a pace the eleven reach; and a run-on
is read only through blocks small beside the world's territories, as in step 4e.

Every number but those of the run-ons is worked out again in `decide` from the tallies in
the records. **What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STEP_4E = HERE.parent / "scale-up-closure-territories"
sys.path.insert(0, str(STEP_4E))

import ladder  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

zoom = ladder.zoom

RECORDS = HERE / "records.jsonl"
WORLDS = HERE / "worlds.json"
SIZING = HERE / "sizing.json"
STEP_4C = HERE.parent / "scale-up-territories" / "records.jsonl"
FIRST_LOOK = STEP_4E / "reference.json"

STILL = "B245678/S3678"  # the world whose rule every other world is tried with
STILL_STARTS = tuple(range(17901, 17909))
FIRST_START, STARTS_EACH, STEP = 17001, 4, 20  # world i starts at 17001 + 20 i
BLOCKS = (8, 16)
EVERY = {8: 4, 16: 16}  # the generations between readings of each block
RATIOS = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0)  # paces a rule is kept at
OWN, AS_IT_IS, AT_PACE = "its own", "the still world's, as it is", "the still world's, at pace"

# --- how the worlds are chosen from step 4c's runs
FILLS = 0.9  # a world fills its grid: this share of it live at the end of step 4c's run
EVEN_DRAW = 1805  # the last number of step 4c's 600 rules of the even draw
BANDS = ((0.0, 0.3, None), (0.3, 0.5, 10), (0.5, 0.7, 10), (0.7, 0.9, 4))  # low, high, how many

# --- the bounds (what they were drawn from is in sizing.json)
SQUARE_ROOT = 0.40  # A: walls that thin as at least this power of time keep the class's clock
ANOTHER_CLOCK = 0.33  # A: walls that thin as at most this power do not
SERVES = 0.01  # A: the still world's rule serves: at most this much more surprise
DOES_NOT = 0.05  # A: it does not: at least this much more
HAS_SET = 0.10  # F: walls that thin as at most this power of time have set
REACH = (0.2, 5.0)  # a pace by the walls that the paces a rule is kept at come near
PACE_AGREES = 1.5  # P: the two paces are within this factor of each other
WHERE = 0.70  # K: blocks amiss over blocks that changed, at most
RANKS = 0.5  # R: the rank correlation of the two paces, at least
AT_LEAST = 8  # R: over at least this many worlds
SAME_RULE = {8: 0.003, 16: 0.005}  # X: the first look's rule on the still world's fresh starts
HOLDS_GROUND = 0.8  # the larger species has at most this share of the live cells at the end
BLOCK_FITS = 0.2  # at most this share of neighbouring blocks differ when a rule is run on


def ticks(block: int) -> tuple[int, ...]:
    """The ticks the still world's rule is kept at for blocks of `block`: RATIOS of the square
    clock's."""
    return tuple(int(r * ladder.square(block)) for r in RATIOS)


# --- the worlds ----------------------------------------------------------------------------------


def grew() -> list[dict]:
    """Every rule of step 4c's runs that grew territories against its copy under the standoff
    from a full start, in the order drawn: its rule, the number it was drawn at, the share of
    the grid live at the end of that run, and its band."""
    out = []
    for line in STEP_4C.read_text().splitlines():
        r = json.loads(line)
        if (r["kind"] == "contest" and r["tie_break"] == "standoff" and r["density"] == 1.0
                and r["verdict"] == "growing territories"):  # fmt: skip
            live = round(sum(r["shares"]), 4)
            band = "fills" if live >= FILLS else next(
                f"{low} to {high}" for low, high, _ in BANDS if low <= live < high)  # fmt: skip
            out.append({"rule": r["rule"], "drawn": r["index"], "live": live, "band": band})
    return sorted(out, key=lambda w: w["drawn"])


def select() -> list[dict]:
    """The worlds: every rule of `grew` that fills the grid, and from the 600 rules of step
    4c's even draw a share of those that do not, band by band, the first drawn first."""
    found = grew()
    out = [w for w in found if w["band"] == "fills"]
    for low, high, most in BANDS:
        band = [w for w in found if w["band"] == f"{low} to {high}" and w["drawn"] <= EVEN_DRAW]
        out += band[:most]
    return [{**w, "first": FIRST_START + STEP * i} for i, w in enumerate(out)]


def population() -> dict[str, int]:
    """How many rules of step 4c's even draw each band stands for: its 600 rules are a fair
    sample of rules, which the 242 it added for its second cut are not."""
    out: dict[str, int] = {}
    for w in grew():
        if w["drawn"] <= EVEN_DRAW:
            out[w["band"]] = out.get(w["band"], 0) + 1
    return out


def worlds() -> dict[str, dict]:
    """The chosen worlds by their rule, as worlds.json holds them."""
    return {w["rule"]: w for w in json.loads(WORLDS.read_text())["worlds"]}


def design(chosen: dict | None = None) -> dict:
    """Which starts each world learns its own rule from and which it is tried on: the first
    half and the second half of its starts. The still world has eight, the others four."""
    chosen = worlds() if chosen is None else chosen
    half = len(STILL_STARTS) // 2
    out = {STILL: {"learn": list(STILL_STARTS[:half]), "try": list(STILL_STARTS[half:])}}
    for rule, w in chosen.items():
        seeds = list(range(w["first"], w["first"] + STARTS_EACH))
        out[rule] = {"learn": seeds[: STARTS_EACH // 2], "try": seeds[STARTS_EACH // 2 :]}
    return out


# --- the runs ------------------------------------------------------------------------------------


def cache_path(rule: str, seed: int) -> Path:
    tag = rule.replace("/", "-")
    return ladder.CACHE / f"class-{tag}-{ladder.SIDE}-{ladder.GENERATIONS}-{seed}.npz"


def fine(rule: str, seed: int) -> dict:
    """`rule` against a copy of itself under the standoff from a full start, read through
    blocks of 8 every four generations and blocks of 16 every sixteen: the leader of every
    block at every reading, and every 64 generations each species' share of the grid. Kept on
    disk, and read from there if it is."""
    path = cache_path(rule, seed)
    if path.exists():
        with np.load(path) as kept:
            return {"shares": kept["shares"], **{b: kept[f"leaders_{b}"] for b in BLOCKS}}
    side, generations = ladder.SIDE, ladder.GENERATIONS
    grid = zoom.lattice((rule, rule), "standoff", side)
    start = zoom.mixed_start(side, seed, 2, density=1.0)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])  # the standoff draws nothing
    frames = {b: [zoom.leaders(zoom.read(grid.occupancy, side, b, 2))] for b in BLOCKS}
    shares = []
    for generation in range(1, generations + 1):
        grid.step(rng)
        for b in BLOCKS:
            if generation % EVERY[b] == 0:
                frames[b].append(zoom.leaders(zoom.read(grid.occupancy, side, b, 2)))
        if generation % 64 == 0:
            shares.append([float((grid.occupancy == s).mean()) for s in (1, 2)])
    out = {"shares": np.array(shares), **{b: np.stack(frames[b]) for b in BLOCKS}}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, shares=out["shares"],
                        **{f"leaders_{b}": out[b] for b in BLOCKS})  # fmt: skip
    return out


def run_start(job: tuple[str, int]) -> dict:
    """One world from one start: on record its tallies (at every pace for the still world, at
    the square clock for the others), and at the ends of each window the share of the grid
    live, the larger species' share of it and the walls at each block."""
    rule, seed = job
    found = fine(rule, seed)
    generations = ladder.GENERATIONS
    marks = sorted({g for span in ladder.WINDOWS.values() for g in span if g <= generations})
    shares = found["shares"]
    tally = {}
    for block in BLOCKS:
        for tick in ticks(block) if rule == STILL else (ladder.square(block),):
            # frames are kept every EVERY[block] generations, which is what `tally` steps by
            tally[ladder.key(block, tick)] = {
                name: ladder.sparse(ladder.tally(found[block], EVERY[block], tick, first, last))
                for name, (first, last) in ladder.WINDOWS.items() if last <= generations
            }  # fmt: skip
    return {
        "kind": "start",
        "world": rule,
        "seed": seed,
        "side": ladder.SIDE,
        "generations": generations,
        "live": {str(g): round(float(shares[g // 64 - 1].sum()), 6) for g in marks},
        "larger": {str(g): round(float(shares[g // 64 - 1].max()), 6) for g in marks},
        "walls": {str(b): {str(g): round(ladder.walls(found[b][g // EVERY[b]]), 6)
                           for g in marks} for b in BLOCKS},
        "tally": tally,
    }  # fmt: skip


def pooled(rows: list[dict], world: str, seeds, block: int, tick: int) -> np.ndarray:
    """The tallies of a world's starts `seeds` at a block and tick over the whole run."""
    total = np.zeros((ladder.Q, 9, 9, ladder.Q), dtype=np.int64)
    for row in rows:
        if row["kind"] == "start" and row["world"] == world and row["seed"] in seeds:
            for window in row["tally"][ladder.key(block, tick)].values():
                total += ladder.dense(window)
    return total


def run_ahead(job: tuple[str, int, str, int, int, list]) -> dict:
    """A rule run on by itself from generation 1,024 of one start of one world, in the
    world's own time. `rule_tick` is the tick the rule was learned at, where it is the still
    world's."""
    rule, seed, whose, block, rule_tick, rows = job
    frames = fine(rule, seed)[block]
    draws = (seed, block, (OWN, AS_IT_IS, AT_PACE).index(whose), rule_tick)
    found = ladder.ahead(frames, ladder.dense(rows), EVERY[block], ladder.square(block), draws,
                         ladder.FROM, ladder.GENERATIONS)  # fmt: skip
    return {"kind": "ahead", "world": rule, "seed": seed, "rule": whose,
            **found, "block": block, "rule_tick": rule_tick}  # fmt: skip


def start_jobs(plan: dict) -> list[tuple[str, int]]:
    """Every fine run: the still world's, then the others taking turns."""
    others = {w: plan[w]["learn"] + plan[w]["try"] for w in plan if w != STILL}
    jobs = [(STILL, seed) for seed in plan[STILL]["learn"] + plan[STILL]["try"]]
    for i in range(max((len(s) for s in others.values()), default=0)):
        jobs += [(w, seeds[i]) for w, seeds in others.items() if i < len(seeds)]
    return jobs


def ahead_jobs(rows: list[dict], plan: dict) -> list:
    """The run-ons: in every world but the still one, at each block, its own rule, the still
    world's as it is, and the still world's for the pace the world's walls give."""
    m = Measures(rows, plan)
    out = []
    for world in plan:
        if world == STILL:
            continue
        # a world whose walls give no pace (one species gone) is run on at the still world's
        ratio = m.grid_pace(world) or 1.0
        for block in BLOCKS:
            own = ladder.square(block)
            rules = [(OWN, own, m.tally(world, "learn", block, own)),
                     (AS_IT_IS, own, m.reference(block, 1.0)),
                     (AT_PACE, int(ratio * own), m.reference(block, ratio))]  # fmt: skip
            for whose, rule_tick, counts in rules:
                for seed in plan[world]["try"]:
                    out.append((world, seed, whose, block, rule_tick, ladder.sparse(counts)))
    return out


def execute(path: Path, workers: int) -> None:
    plan = design()
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    done = {(r["kind"], r["world"], r["seed"], r.get("rule"), r.get("block")) for r in rows}
    starts = [job for job in start_jobs(plan) if ("start", *job, None, None) not in done]
    with ProcessPoolExecutor(max(workers, 1)) as pool:
        for record in pool.map(run_start, starts):
            append_records(path, [record])
            rows.append(record)
        ahead = [job for job in ahead_jobs(rows, plan) if ("ahead", *job[:4]) not in done]
        for record in pool.map(run_ahead, ahead):
            append_records(path, [record])


# --- what is measured ----------------------------------------------------------------------------


def over(top: float | None, bottom: float | None) -> float | None:
    """One number over another, where the other is a number above nought."""
    if top is None or bottom is None or not np.isfinite(top) or not np.isfinite(bottom):
        return None
    return top / bottom if bottom > 0 else None


def nearest(pace: float) -> float:
    """The pace a rule is kept at that is nearest a given pace, as a ratio."""
    return min(RATIOS, key=lambda r: abs(math.log2(r / pace)))


def vertex(found: dict[float, float]) -> float | None:
    """Where a curve read at a few paces is least: the bottom of the parabola through its
    lowest point and that point's neighbours, against the logarithm of the pace. The lowest
    point itself if it is the first or the last pace, or the three do not make a bowl."""
    paces = sorted(p for p, v in found.items() if v is not None and np.isfinite(v))
    if not paces:
        return None
    i = min(range(len(paces)), key=lambda j: found[paces[j]])
    if i in (0, len(paces) - 1):
        return paces[i]
    x = [math.log2(paces[j]) for j in (i - 1, i, i + 1)]
    y = [found[paces[j]] for j in (i - 1, i, i + 1)]
    a, b, _ = np.polyfit(x, y, 2)
    if a <= 0:
        return paces[i]
    return float(2.0 ** min(max(-b / (2 * a), x[0]), x[2]))


def ranks(values: list[float]) -> np.ndarray:
    order = np.argsort(values)
    out = np.empty(len(values))
    out[order] = np.arange(len(values))
    return out


def rank_correlation(first: list[float], second: list[float]) -> float | None:
    """Spearman's: the correlation of the two lists' ranks."""
    if len(first) < 3 or len(set(first)) < 2 or len(set(second)) < 2:
        return None
    return float(np.corrcoef(ranks(first), ranks(second))[0, 1])


class Measures:
    """Every number a claim is judged on, from the records of a run and the starts each world
    learns from and is tried on."""

    def __init__(self, rows: list[dict], plan: dict):
        self.rows, self.plan = rows, plan
        self.starts: dict = {}
        self.ahead: dict = {}
        for r in rows:
            if r["kind"] == "start":
                self.starts.setdefault(r["world"], {})[r["seed"]] = r
            else:
                self.ahead.setdefault((r["world"], r["rule"], r["block"]), []).append(r)

    def seeds(self, world: str, part: str) -> list[int]:
        return self.plan[world]["learn"] + self.plan[world]["try"] if part == "all" else (
            self.plan[world][part])  # fmt: skip

    def tally(self, world: str, part: str, block: int, tick: int) -> np.ndarray:
        return pooled(self.rows, world, self.seeds(world, part), block, tick)

    def reference(self, block: int, ratio: float) -> np.ndarray:
        """The still world's rule here, at a pace: all eight of its starts."""
        return self.tally(STILL, "all", block, int(ratio * ladder.square(block)))

    # the clock, and the pace by the walls
    def mean(self, world: str, part: str, what: str, *where: str) -> float | None:
        """The mean over some of a world's starts of something its records hold."""
        values = []
        for seed in self.seeds(world, part):
            found = self.starts.get(world, {}).get(seed)
            if found is None:
                return None
            for step in (what, *where):
                found = found[step]
            values.append(found)
        return float(np.mean(values)) if values else None

    def walls(self, world: str, part: str, block: int, generation: int) -> float | None:
        return self.mean(world, part, "walls", str(block), str(generation))

    def power(self, world: str, block: int = 8) -> float | None:
        """The power of time by which a world's walls thin over the stretch a rule is run on."""
        first, last = ladder.WINDOWS["C"]
        thins = over(self.walls(world, "all", block, last), self.walls(world, "all", block, first))
        return -math.log(thins) / math.log(last / first) if thins else None

    def pace_by_walls(self, world: str, block: int = 8) -> float | None:
        """A world's pace beside the still world's, from walls alone: the square of the still
        world's walls over the world's, at the generation a rule is run on from and at the
        last (their geometric mean). The world's walls are those of the starts it learns
        from, so that its trial starts' ends are not in it."""
        found = []
        for generation in ladder.WINDOWS["C"]:
            ratio = over(self.walls(STILL, "all", block, generation),
                         self.walls(world, "learn", block, generation))  # fmt: skip
            if ratio is None:
                return None
            found.append(ratio**2)
        return math.sqrt(found[0] * found[1])

    def grid_pace(self, world: str) -> float | None:
        """The pace the still world's rule is kept at that is nearest the world's walls'."""
        pace = self.pace_by_walls(world)
        return nearest(pace) if pace else None

    # whether the still world's rule serves, and at what pace
    def own(self, world: str, block: int) -> tuple[np.ndarray, np.ndarray]:
        tick = ladder.square(block)
        return self.tally(world, "learn", block, tick), self.tally(world, "try", block, tick)

    def by_pace(self, world: str, block: int) -> dict[float, float | None]:
        """How much more surprise the still world's rule has than the world's own, on the
        world's trial starts, at every pace it is kept at."""
        here, trial = self.own(world, block)
        out = {}
        for ratio in RATIOS:
            found = ladder.excess(self.reference(block, ratio), here, trial)
            out[ratio] = found if np.isfinite(found) else None
        return out

    def least(self, world: str, block: int = 8) -> float | None:
        found = [v for v in self.by_pace(world, block).values() if v is not None]
        return min(found) if found else None

    def pace_by_rule(self, world: str, block: int = 8) -> float | None:
        return vertex(self.by_pace(world, block))

    def paces_apart(self, world: str) -> float | None:
        """The factor between the pace by the rule and the pace by the walls, 1 or more."""
        ratio = over(self.pace_by_rule(world), self.pace_by_walls(world))
        return max(ratio, 1 / ratio) if ratio else None

    # the run-ons
    def end(self, world: str, whose: str, block: int, what: str) -> float | None:
        runs = self.ahead.get((world, whose, block), [])
        if sorted(r["seed"] for r in runs) != sorted(self.plan[world]["try"]):
            return None
        return float(np.mean([r[what][-1] for r in runs]))

    def amiss(self, world: str, whose: str, block: int = 8) -> float | None:
        """Blocks whose leader is not the real world's at the end of a run-on, over blocks
        that changed leader meanwhile."""
        return over(self.end(world, whose, block, "apart_rule"),
                    self.end(world, whose, block, "apart_start"))  # fmt: skip

    # what a claim stands on
    def holds_ground(self, world: str) -> bool:
        """Two species still share the grid at the end: the larger has at most 0.8 of the
        live cells, on average over the world's starts."""
        last = str(ladder.WINDOWS["C"][1])
        share = over(self.mean(world, "all", "larger", last), self.mean(world, "all", "live", last))
        return share is not None and share <= HOLDS_GROUND

    def square_root(self, world: str) -> bool:
        """Walls that thin as about the square root of the time, at a pace the paces a rule
        is kept at come near."""
        power, pace = self.power(world), self.pace_by_walls(world)
        return (power is not None and power >= SQUARE_ROOT
                and pace is not None and REACH[0] <= pace <= REACH[1])  # fmt: skip

    def fits(self, world: str, block: int = 8) -> bool:
        walls = self.walls(world, "try", block, ladder.WINDOWS["C"][0])
        return walls is not None and walls <= BLOCK_FITS

    def stands(self, claim: dict) -> bool:
        world, needs = claim["world"], claim["needs"]
        if needs == "nothing":
            return True
        if not self.holds_ground(world):
            return False
        if needs == "two species":
            return True
        if needs == "a clock that says":
            power = self.power(world)
            return power is not None and (self.square_root(world) or power <= ANOTHER_CLOCK)
        if needs == "the square-root clock":
            return self.square_root(world)
        if needs == "the square-root clock and a block that fits":
            return self.square_root(world) and self.fits(world)
        raise ValueError(f"unknown need {needs!r}")

    def on_the_clock(self) -> list[str]:
        """The worlds claims P, K and R are about: two species, the square-root clock."""
        return [w for w in self.plan if w != STILL and self.holds_ground(w)
                and self.square_root(w)]  # fmt: skip

    def value(self, claim: dict) -> float | None:
        q, world = claim["quantity"], claim["world"]
        if q == "served, by its clock":
            # judged against the bound its clock picks: see `judge`
            return self.least(world)
        if q == "its clock":
            return self.power(world)
        if q == "paces apart":
            return self.paces_apart(world)
        if q == "amiss over changed, at its walls' pace":
            return self.amiss(world, AT_PACE)
        if q == "the paces' ranks":
            pairs = [(self.pace_by_walls(w), self.pace_by_rule(w)) for w in self.on_the_clock()]
            pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
            if len(pairs) < AT_LEAST:
                return None
            return rank_correlation([a for a, _ in pairs], [b for _, b in pairs])
        if q == "the first look's rule":
            block = claim["block"]
            kept = json.loads(FIRST_LOOK.read_text())["rules"]["still"]
            rule = ladder.dense(kept[ladder.key(block, ladder.square(block))])
            here, trial = self.own(STILL, block)
            return ladder.excess(rule, here, trial)
        raise ValueError(f"unknown quantity {q!r}")


# --- the predictions -----------------------------------------------------------------------------


def claims(chosen: dict | None = None) -> list[dict]:
    """Every claim: its label and family, the world and the quantity it is judged on, its
    bound, and what it needs to be tested."""
    chosen = worlds() if chosen is None else chosen
    out = []

    def claim(family, label, text, quantity, world, needs, at_least=None, at_most=None, **more):
        out.append({"label": label, "family": family, "claim": text, "quantity": quantity,
                    "world": world, "needs": needs, "at_least": at_least, "at_most": at_most,
                    **more})  # fmt: skip

    for rule, w in chosen.items():
        claim("A", f"A {rule}: its clock says",
              f"in {rule} against its copy, if the walls thin as the {SQUARE_ROOT}th power of "
              f"time or more the still world's rule serves at some pace (at most {SERVES:.0%} "
              f"more surprise than the world's own rule, at blocks of 8), and if they thin as "
              f"the {ANOTHER_CLOCK}th power or less it does not (at least {DOES_NOT:.0%} more)",
              "served, by its clock", rule, "a clock that says")  # fmt: skip
        if w["band"] == "fills":
            claim("F", f"F {rule}: fills, and grows by the square root or has set",
                  f"{rule} against its copy fills its grid, and its walls thin as the "
                  f"{SQUARE_ROOT}th power of time or more, or as the {HAS_SET}th or less: no "
                  "filling world keeps a clock between",
                  "its clock", rule, "two species", between=[HAS_SET, SQUARE_ROOT])  # fmt: skip
        claim("P", f"P {rule}: the pace, two ways",
              f"if {rule} keeps the square-root clock, the pace at which the still world's "
              f"rule serves it best is within a factor of {PACE_AGREES} of the pace its walls "
              "give",
              "paces apart", rule, "the square-root clock", at_most=PACE_AGREES)  # fmt: skip
        claim("K", f"K {rule}: run on at its walls' pace",
              f"if {rule} keeps the square-root clock, the still world's rule for the pace its "
              "walls give, run on by itself from generation 1,024, ends with another leader "
              f"than the real world's in at most {WHERE} of the share of blocks that changed "
              "leader meanwhile, at blocks of 8",
              "amiss over changed, at its walls' pace", rule,
              "the square-root clock and a block that fits", at_most=WHERE)  # fmt: skip
    claim("R", "R the faster by its walls is the faster by the rule",
          "over the worlds that keep the square-root clock, the rank correlation between the "
          f"pace by the walls and the pace by the rule is at least {RANKS} (not tested over "
          f"fewer than {AT_LEAST} worlds)",
          "the paces' ranks", STILL, "nothing", at_least=RANKS)  # fmt: skip
    for block, bound in SAME_RULE.items():
        claim("X", f"X the still world, block {block}",
              f"the first look's rule for the still world has at most {bound:.1%} more surprise "
              f"on its fresh starts here than the rule learned from them, at blocks of {block} "
              "on the square clock",
              "the first look's rule", STILL, "nothing", at_most=bound, block=block)  # fmt: skip
    return out


def predictions() -> list[dict]:
    return claims()


# --- the verdict ---------------------------------------------------------------------------------


def number(value, places: int = 5) -> float | None:
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), places)


def judge(value: float | None, claim: dict, stands: bool, power: float | None = None) -> str:
    """holds, fails, or not tested where the claim has nothing to stand on or no number. A
    claim of family A is judged against the bound the world's clock picks."""
    if not stands or value is None or not np.isfinite(value):
        return "not tested"
    at_least, at_most = claim["at_least"], claim["at_most"]
    if claim["quantity"] == "served, by its clock":
        if power is None:
            return "not tested"
        at_least, at_most = (None, SERVES) if power >= SQUARE_ROOT else (DOES_NOT, None)
    if claim["quantity"] == "its clock":  # fails only between the two
        low, high = claim["between"]
        return "fails" if low < value < high else "holds"
    if at_least is not None and value < at_least:
        return "fails"
    if at_most is not None and value > at_most:
        return "fails"
    return "holds"


def told(m: Measures, world: str, chosen: dict) -> dict:
    """What a reader wants of one world beside the verdicts."""
    last = str(ladder.WINDOWS["C"][1])
    by_pace = m.by_pace(world, 8)
    out = {
        **{k: chosen[world][k] for k in ("band", "drawn", "live") if world in chosen},
        "live at the end": number(m.mean(world, "all", "live", last), 4),
        "larger species' share of the live": number(over(
            m.mean(world, "all", "larger", last), m.mean(world, "all", "live", last)), 4),
        "two species hold ground": m.holds_ground(world),
        "walls at blocks of 8, generations 1,024 and 4,096": [
            number(m.walls(world, "all", 8, g), 4) for g in ladder.WINDOWS["C"]],
        "walls thin as time to the power": {
            str(b): number(m.power(world, b), 3) for b in BLOCKS},
        "a block of 8 fits": m.fits(world),
        "pace by its walls": number(m.pace_by_walls(world), 3),
        "pace by the rule": {str(b): number(m.pace_by_rule(world, b), 3) for b in BLOCKS},
        "more surprise than its own rule, by pace": {
            str(r): number(v) for r, v in by_pace.items()},
        "least": {str(b): number(m.least(world, b)) for b in BLOCKS},
        "as it is": number(by_pace[1.0]),
        "changes hands, blocks of 8": [
            round(float(c / b), 4) if b else None
            for b, c in ladder.hands(m.tally(world, "all", 8, ladder.square(8)))],
        "run on, amiss over changed": {
            f"{whose}, blocks of {b}": number(m.amiss(world, whose, b), 4)
            for b in BLOCKS for whose in (OWN, AS_IT_IS, AT_PACE)},
    }  # fmt: skip
    runs = m.ahead.get((world, AT_PACE, 8), [])
    out["run on at a pace of"] = runs[0]["rule_tick"] / ladder.square(8) if runs else None
    return out


def summary(m: Measures, chosen: dict) -> dict:
    """How wide the class is, in counts: of the worlds chosen, band by band; and of the
    rules of step 4c's even draw that grow territories, each band of the sample weighted by
    how many such rules it stands for. Reported, not judged."""

    def served(world: str) -> bool:
        least = m.least(world)
        return m.holds_ground(world) and least is not None and least <= SERVES

    by_band: dict = {}
    for world, w in chosen.items():
        row = by_band.setdefault(w["band"], {"worlds": 0, "two species hold ground": 0,
                                             "square-root clock": 0, "served": 0})  # fmt: skip
        row["worlds"] += 1
        row["two species hold ground"] += int(m.holds_ground(world))
        row["square-root clock"] += int(m.holds_ground(world) and m.square_root(world))
        row["served"] += int(served(world))
    stands_for = population()
    share = 0.0
    for band, size in stands_for.items():
        mine = [w for w, told in chosen.items()
                if told["band"] == band and told["drawn"] <= EVEN_DRAW]  # fmt: skip
        if mine:
            share += size * sum(served(w) for w in mine) / len(mine)
    return {
        "by band": by_band,
        "served": sum(row["served"] for row in by_band.values()),
        "of": len(chosen),
        "of the even draw's rules that grow territories": sum(stands_for.values()),
        "of which each band stands for": stands_for,
        "served, by the sample weighted": round(share / max(sum(stands_for.values()), 1), 3),
    }


def decide(rows: list[dict], registered: list[dict]) -> dict:
    chosen = worlds()
    plan = design(chosen)
    have = {(r["world"], r["seed"]) for r in rows if r["kind"] == "start"}
    missing = [f"{world} from start {seed}" for world, seed in start_jobs(plan)
               if (world, seed) not in have]  # fmt: skip
    if not missing:
        done = {(r["world"], r["seed"], r["rule"], r["block"]) for r in rows
                if r["kind"] == "ahead"}  # fmt: skip
        missing = [f"the run-on of {job[2]} rule in {job[0]} from start {job[1]}, blocks of "
                   f"{job[3]}" for job in ahead_jobs(rows, plan)
                   if tuple(job[:4]) not in done]  # fmt: skip
    outcomes, measured, reported, wide = {}, {}, {}, {}
    if missing:
        outcomes = {c["label"]: "missing" for c in registered}
    else:
        m = Measures(rows, plan)
        for c in registered:
            value = m.value(c)
            power = m.power(c["world"])
            outcomes[c["label"]] = judge(value, c, m.stands(c), power)
            measured[c["label"]] = {"value": number(value)}
            if c["family"] == "A":
                measured[c["label"]]["power"] = number(power, 3)
        reported = {world: told(m, world, chosen) for world in plan}
        wide = summary(m, chosen)

    def overall(family: str) -> str:
        words = {outcomes[c["label"]] for c in registered if c["family"] == family}
        for word in ("missing", "fails", "holds"):
            if word in words:
                return word
        return "not tested"

    def tally(family: str) -> dict:
        words = [outcomes[c["label"]] for c in registered if c["family"] == family]
        return {word: words.count(word) for word in ("holds", "fails", "not tested", "missing")
                if word in words}  # fmt: skip

    families = sorted({c["family"] for c in registered})
    return {
        "verdict": {family: overall(family) for family in families},
        "counts": {family: tally(family) for family in families},
        "outcomes": outcomes,
        "measured": measured,
        "missing": missing[:20],
        "how wide": wide,
        "worlds": reported,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def question() -> dict:
    chosen = worlds()
    plan = design(chosen)
    return {
        "id": "scale-up-class",
        "title": "How wide is the class of worlds that one coarse rule runs?",
        "statement": "A table of who leads a block next, read off one world of territories "
        "(the still world), is tried in 38 worlds no run has zoomed out: every rule of step "
        "4c's runs that fills its grid, and a share of those that hold territories without "
        "filling it. A world's clock says whether the rule serves it (A); a world that fills "
        "keeps the square-root clock or has set (F); where a world keeps the square-root "
        "clock the pace at which the "
        "rule serves it is the pace its walls give (P, R) and the rule for that pace, run on "
        "by itself, keeps the world (K); and the still world's rule here is the first look's "
        "(X).",
        "source": "docs/scale-up-plan.md, step 4e and decision D11; the worlds from the "
        "registered runs of examples/scale-up-territories",
        "worlds": {rule: {"band": w["band"], "drawn": w["drawn"],
                          "live_in_step_4c": w["live"], "learned_from": plan[rule]["learn"],
                          "tried_on": plan[rule]["try"]}
                   for rule, w in chosen.items()},  # fmt: skip
        "the still world": {"rule": STILL, "starts": list(STILL_STARTS)},
        "tie_break": "standoff",
        "density": 1.0,
        "side": ladder.SIDE,
        "generations": ladder.GENERATIONS,
        "blocks": {str(b): {"read every": EVERY[b], "square tick": ladder.square(b),
                            "the still world's rule kept at ticks": list(ticks(b))}
                   for b in BLOCKS},  # fmt: skip
        "windows": {name: list(span) for name, span in ladder.WINDOWS.items()},
        "runs": len(start_jobs(plan)) + 3 * len(BLOCKS) * (STARTS_EACH // 2) * len(chosen),
        "not_tested": "No claim about a world is tested unless two species hold ground at "
        f"the end (the larger has at most {HOLDS_GROUND} of the live cells). A: not tested "
        f"where the walls thin as a power of time between {ANOTHER_CLOCK} and {SQUARE_ROOT}. "
        f"P, K: not tested unless the power is {SQUARE_ROOT} or more and the pace by the "
        f"walls is between {REACH[0]} and {REACH[1]} (so too A, where the power is "
        f"{SQUARE_ROOT} or more); K also not unless at "
        f"most {BLOCK_FITS} of neighbouring blocks of 8 have different leaders at generation "
        f"1,024. R: not tested over fewer than {AT_LEAST} worlds. And no claim is tested "
        "without a number to judge.",
        "sizing": json.loads(SIZING.read_text())["what the bounds were drawn from"],
        "sha256": {
            "study.py": sha(HERE / "study.py"),
            "worlds.json": sha(WORLDS),
            "sizing.json": sha(SIZING),
            "../scale-up-closure-territories/ladder.py": sha(STEP_4E / "ladder.py"),
            "../scale-up-closure-territories/reference.json": sha(FIRST_LOOK),
            "../scale-up-territories/records.jsonl": sha(STEP_4C),
        },
        "excluded_seen": [
            "Step 4e (examples/scale-up-closure-territories, registered and run): the still "
            "world, B23467/S4568, B24678/S34678, B3568/S124678, B2/S0 and B2578/S135678 read "
            "by who leads a block on side 1,024 from starts 15001 to 15008, 15101, 15102 and "
            "16001 to 16504. Every bound here was drawn from those records.",
            "The sizing look (sizing.py here, exploratory): those records again through this "
            "study's measures, with the first look's still world read at finer ticks for "
            "blocks of 16. It ran nothing.",
            "Step 4c (examples/scale-up-territories, registered and run) ran each of the 38 "
            "rules against its copy on side 256 for 512 generations from start 14001, and "
            "read them by their correlation area and their species' shares: that is how they "
            "were chosen. None has been run on a larger grid, for longer, or read by who "
            "leads a block, and no coarse rule has been learned from one.",
            "No start from 17001 on has been generated or run.",
        ],
    }  # fmt: skip


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    if record["kind"] == "start":
        return run_start((record["world"], record["seed"]))
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    wanted = (record["world"], record["seed"], record["rule"], record["block"])
    for job in ahead_jobs(rows, design()):
        if tuple(job[:4]) == wanted:
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
