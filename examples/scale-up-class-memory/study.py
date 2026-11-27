"""
A registered test: does a rule that remembers carry the class?

    uv run --no-sync python examples/scale-up-class-memory/study.py register
    uv run --no-sync python examples/scale-up-class-memory/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-class-memory

**Why.** Step 4f of docs/scale-up-plan.md (examples/scale-up-class) found that 29 of 38
worlds keep the still world's clock, but that the still world's coarse rule serves only the
fuller ones, and I read its failures in the thin ones as a table learning the flicker of a
block's leader. Steps 4h and 4i (examples/scale-up-memory) then found a rule that takes a
flicker back: one that keeps in view how long a block has had its leader. Decision D14 asked
whether that rule carries more of the class than the plain one did.

**Each world on its own clock** (clock.py). A rule that remembers counts in ticks, so the
tick has to mean the same in every world. Step 4f read every world at the still world's tick
and slowed the rule to the world; here the world is read at its own pace and the rule stays
as it is. A world's tick is the sixteenth part of the generation at which its walls, through
blocks of 8, have thinned to what the still world's are when its matched age begins; and it
is read and run on from 16 of its ticks to 64, as the still world is from generation 256 to
1,024. So every world gives 48 ticks, and "how long a block has had its leader" is the same
question in each.

**One rule, written down beforehand.** The look's rule for blocks of 8
(examples/scale-up-memory/reference.json), as it is and with how long in view, is tried
unchanged in every world: one tick ahead beside the world's own rule, and run on by itself
beside the world's own rules.

**The worlds** (`worlds.json`, by `select` from step 4f's registered verdict): the still
world, and the 29 of step 4f's worlds that kept its clock there, each against its copy under
the standoff on a wrapped grid of side 1,024 for 5,120 generations, from four fresh starts
(two to read its tick from and learn its own rules, two to try on). They are grouped by
what step 4f found: the 10 the still world's rule served within 1%, 4 within 2%, 5 it missed
by under 10%, and 10 it missed by more.

**Predictions** (`claims`). The sizing look (sizing.py) put eleven of these worlds and the
still world through every measure, from starts step 4f had run, and what it showed is what
is registered. It is not what I expected when the question was put (decision D14): the
rule that remembers does not reach the worlds the plain rule missed. It carries the worlds
the plain rule served, better.

    X  the still world, read this way, is the still world of steps 4g to 4i
    S  on its own clock every world is the same picture: its walls thin over its window as
       the still world's do over its matched age
    T  and its tick is the pace step 4f read off its walls
    K  the look's plain rule, run on on a world's own clock, keeps every one of them
    P  a block's past matters in the worlds step 4f found served, and not in those it found
       missed by a tenth or more
    O  one tick ahead the look's rule serves the first, as it is and with how long in view;
       it does not serve the second, and remembering makes it worse there
    J  nor does it serve, either way, any of the five worlds step 4f just missed
    D  in the worlds served, the look's remembering rule gains on its plain one, runs the
       world, and does it as the world's own remembering rule does
    W  in the worlds missed, remembering does not gain
    B  and there the look's rules run a world on better than the world's own, as it is and
       with how long in view
    G  over all of them: the more the old rule missed a world, the less its blocks' past
       matters, and the less remembering gains

A claim holds if its number is inside its bound and fails if it is not. It is **not
tested** where a world's walls give it no tick whose window ends inside a run, or one
species has all but taken the grid. The four worlds step 4f found nearly served carry only
S, T and K, and the five it just missed those and J: the sizing had one of the nine, and
they are where the gradient G is read.

**Every world against the same bars.** Whatever is claimed of a world, the verdict also
says where it stands against each bar of the study (`bars`), and counts the worlds that
meet each by group (`counted`): so "how many worlds does each rule serve" is read the same
way over all 29, the nine between included.

Every number but those of the run-ons is worked out again in `decide` from the tallies in
the records. **What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
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


clock = _module("scale_up_class_memory_clock", HERE / "clock.py")
look, ladder = clock.look, clock.ladder
memory = _module("scale_up_memory_study", clock.MEMORY / "study.py")

from lattice_lab.study import Study, append_records, main  # noqa: E402

RECORDS = HERE / "records.jsonl"
SIZING = HERE / "sizing.json"
WORLDS = HERE / "worlds.json"
STEP_4F = HERE.parent / "scale-up-class"

STILL = "B245678/S3678"  # the world the look's rule was learned in
FIRST_START, STARTS_EACH, STEP = 20001, 4, 20  # world i starts at 20001 + 20 i
STILL_FIRST = 20901
ON_THE_CLOCK = 0.40  # step 4f's bound: walls that thin as at least this power of time
EARLY, LATE = 1024, 4096  # the generations between which step 4f read a world's clock
Q = ladder.Q
PLAIN, HOW = memory.PLAIN, memory.HOW
READINGS = memory.READINGS  # as it is; with how long in view, up to 8 ticks
LONG = memory.LONG  # every tally is kept by how long, up to 16 ticks
OWN, LOOKS = "its own", "the look's"
PAIRS = 8  # run-ons of a rule from one start: this many pairs, sixteen runs
sparse, dense = memory.sparse, memory.dense


MISSED = "the still world's rule in step 4f, more surprise at its best pace"
AT_LEAST = 8  # a rank correlation is taken over at least this many worlds
SERVED, NEAR, JUST, FAR = "served", "nearly served", "just missed", "missed"
# how far the still world's rule was from a world's own in step 4f, at its best pace
GROUPS = ((0.01, SERVED), (0.02, NEAR), (0.10, JUST), (math.inf, FAR))


def group(world: dict) -> str:
    """Where step 4f left a world: the still world's rule served it within 1% there, within
    2%, missed it by under 10%, or by more."""
    return next(name for bound, name in GROUPS if world[MISSED] <= bound)


def select() -> list[dict]:
    """The worlds, from step 4f's registered run: the still world, and every one of step
    4f's 38 worlds that kept the still world's clock there (walls that thinned as a power of
    time of ON_THE_CLOCK or more: 29 of them). With what step 4f found of each: the share of
    its grid live at the end, the power its walls thinned by, the pace it read off them, how
    far the still world's rule was from the world's own at its best pace, and the group that
    puts it in here."""
    entries = [json.loads(line) for line in (STEP_4F / "ledger.jsonl").read_text().splitlines()]
    told = next(e["body"] for e in entries if e["kind"] == "verdict")["worlds"]
    before = json.loads((STEP_4F / "worlds.json").read_text())["worlds"]
    out = [{"rule": STILL, "first": STILL_FIRST, "group": "the still world",
            "live": round(told[STILL]["live at the end"], 4)}]  # fmt: skip
    for w in before:
        found = told[w["rule"]]
        power = found["walls thin as time to the power"]["8"]
        if power is None or power < ON_THE_CLOCK:
            continue
        world = {
            "rule": w["rule"], "first": FIRST_START + STEP * (len(out) - 1),
            "live": round(found["live at the end"], 4), "power in step 4f": round(power, 3),
            "pace by its walls in step 4f": round(found["pace by its walls"], 3),
            MISSED: round(found["least"]["8"], 4),
        }  # fmt: skip
        out.append({**world, "group": group(world)})
    return out


def worlds() -> dict[str, dict]:
    """The worlds by their rule, as worlds.json holds them."""
    return {w["rule"]: w for w in json.loads(WORLDS.read_text())["worlds"]}


def design(chosen: dict | None = None) -> dict:
    """Which starts each world learns from (its tick, and its own rules) and which it is
    tried on: the first half and the second half of its starts."""
    chosen = worlds() if chosen is None else chosen
    out = {}
    for rule, w in chosen.items():
        seeds = list(range(w["first"], w["first"] + STARTS_EACH))
        out[rule] = {"learn": seeds[: STARTS_EACH // 2], "try": seeds[STARTS_EACH // 2 :]}
    return out


def looks_rule() -> np.ndarray:
    """The look's rule for blocks of 8 (examples/scale-up-memory/reference.json): the tally
    of all eight of step 4g's starts of the still world on side 2,048 over the matched age
    of blocks of 8, by how long a block has had its leader."""
    return memory.reference()[("still", clock.BLOCK)]


# --- the runs ------------------------------------------------------------------------------------


def start_record(rule: str, seed: int, found: dict) -> dict:
    """What goes on record of one fine run before its world's tick is known: its walls at
    blocks of 8 every 64 generations, and the share of the grid live and the larger species'
    share at generations 1,024 (EARLY), 4,096 (LATE) and the last."""
    marks = (EARLY, LATE, clock.GENERATIONS)
    shares = found["shares"]
    return {
        "kind": "start",
        "world": rule,
        "seed": seed,
        "side": clock.SIDE,
        "generations": clock.GENERATIONS,
        "live": {str(g): round(float(shares[g // 64 - 1].sum()), 6) for g in marks},
        "larger": {str(g): round(float(shares[g // 64 - 1].max()), 6) for g in marks},
        "walls": clock.walls(found["leaders"]),
    }


def run_start(job: tuple[str, int]) -> dict:
    rule, seed = job
    return start_record(rule, seed, clock.fine(rule, seed))


def thinning(rows: list[dict], world: str, seeds) -> list[float] | None:
    """The mean walls of some of a world's starts, every 64 generations."""
    found = [r["walls"] for r in rows
             if r["kind"] == "start" and r["world"] == world and r["seed"] in seeds]  # fmt: skip
    if len(found) != len(list(seeds)) or not found:
        return None
    return [float(v) for v in np.mean(found, axis=0)]


def tick_of(rows: list[dict], plan: dict, world: str) -> int | None:
    """A world's tick, from the walls of the starts it learns from."""
    thin = thinning(rows, world, plan[world]["learn"])
    return clock.tick_of(thin) if thin else None


def tally_record(rule: str, seed: int, tick: int, found: dict) -> dict:
    """What goes on record of one fine run once its world's tick is known: its tally by how
    long a block has had its leader, read every tick over the world's window, and its walls
    at the ends of the window."""
    first, last = clock.window(tick)
    leaders = found["leaders"]
    return {
        "kind": "tally",
        "world": rule,
        "seed": seed,
        "tick": tick,
        "window": [first, last],
        "walls": [round(ladder.walls(leaders[g // clock.EVERY]), 6) for g in (first, last)],
        "tally": sparse(clock.tally(LONG, leaders, tick)),
    }


def no_clock(kind: str, world: str, seed: int, **more) -> dict:
    """What goes on record where a world's walls gave it no tick: that, and nothing else.
    So a run always leaves as many records as the question says."""
    return {"kind": kind, "world": world, "seed": seed, "tick": None, **more}


def run_tally(job: tuple[str, int, int | None]) -> dict:
    rule, seed, tick = job
    if tick is None:
        return no_clock("tally", rule, seed)
    return tally_record(rule, seed, tick, clock.fine(rule, seed))


def pooled(rows: list[dict], world: str, seeds) -> np.ndarray:
    """The tallies of a world's starts `seeds` over its window, by how long (up to 16)."""
    total = np.zeros((LONG.size, Q, 9, 9, Q), dtype=np.int64)
    for row in rows:
        if (row["kind"] == "tally" and row["world"] == world and row["seed"] in seeds
                and row["tick"] is not None):  # fmt: skip
            total += dense(row["tally"], LONG.size)
    return total


def ahead_record(rule: str, seed: int, tick: int, reading: str, whose: str,
                 leaders: np.ndarray, counts: np.ndarray) -> dict:  # fmt: skip
    """A rule run on by itself over a world's window from one of its trial starts, on the
    world's own clock, PAIRS times two runs (`look.ahead`): on record what step 4i kept of a
    run-on."""
    draws = (seed, clock.BLOCK, (OWN, LOOKS).index(whose))
    first, last = clock.window(tick)
    runs = [look.ahead(READINGS[reading], leaders, counts, clock.EVERY, tick, draws, first,
                       last, pair) for pair in range(PAIRS)]  # fmt: skip
    return {
        "kind": "ahead",
        "world": rule,
        "seed": seed,
        "tick": tick,
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


def run_ahead(job: tuple[str, int, int | None, str, str, list | None]) -> dict:
    rule, seed, tick, reading, whose, rows = job
    if tick is None:
        return no_clock("ahead", rule, seed, reading=reading, rule=whose)
    counts = dense(rows, READINGS[reading].size)
    return ahead_record(rule, seed, tick, reading, whose, clock.fine(rule, seed)["leaders"],
                        counts)  # fmt: skip


def start_jobs(plan: dict) -> list[tuple[str, int]]:
    """Every fine run, the worlds taking turns."""
    seeds = {w: plan[w]["learn"] + plan[w]["try"] for w in plan}
    longest = max(len(s) for s in seeds.values())
    return [(w, s[i]) for i in range(longest) for w, s in seeds.items() if i < len(s)]


def tally_jobs(rows: list[dict], plan: dict) -> list[tuple[str, int, int | None]]:
    """For every world, the tally of each of its starts at the world's tick (None where its
    walls give it none: the record then says so)."""
    out = []
    for world in plan:
        tick = tick_of(rows, plan, world)
        out += [(world, seed, tick) for seed in plan[world]["learn"] + plan[world]["try"]]
    return out


def rules(rows: list[dict], plan: dict, world: str) -> list[tuple[str, str, np.ndarray]]:
    """The rules run on in one world, each as its reading, whose it is and its tally: as it
    is and with how long in view, the world's own (learned from the starts it learns from,
    on its own clock) and the look's."""
    own, lent = pooled(rows, world, plan[world]["learn"]), looks_rule()
    return [(reading, whose, sees.of(counts))
            for reading, sees in READINGS.items()
            for whose, counts in ((OWN, own), (LOOKS, lent))]  # fmt: skip


def ahead_jobs(rows: list[dict], plan: dict) -> list:
    """Every run-on: in each world its four rules, from each start it is tried on."""
    out = []
    for world in plan:
        tick = tick_of(rows, plan, world)
        if tick is None:
            out += [(world, seed, None, reading, whose, None)
                    for reading in READINGS for whose in (OWN, LOOKS)
                    for seed in plan[world]["try"]]  # fmt: skip
            continue
        for reading, whose, counts in rules(rows, plan, world):
            out += [(world, seed, tick, reading, whose, sparse(counts))
                    for seed in plan[world]["try"]]  # fmt: skip
    return out


def execute(path: Path, workers: int, plan: dict | None = None) -> None:
    """The fine runs; then, for each world whose walls give it a tick, its tallies at that
    tick; then the run-ons. Each stage needs the records of the one before. (`plan` is the
    registered design unless the sizing look says otherwise.)"""
    plan = design() if plan is None else plan
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    done = {(r["kind"], r["world"], r["seed"], r.get("reading"), r.get("rule")) for r in rows}

    def left(kind: str, jobs: list) -> list:
        return [job for job in jobs if (kind, job[0], job[1], None, None) not in done]

    with ProcessPoolExecutor(max(workers, 1)) as pool:
        for record in pool.map(run_start, left("start", start_jobs(plan))):
            append_records(path, [record])
            rows.append(record)
        for record in pool.map(run_tally, left("tally", tally_jobs(rows, plan))):
            append_records(path, [record])
            rows.append(record)
        ahead = [job for job in ahead_jobs(rows, plan)
                 if ("ahead", job[0], job[1], job[3], job[4]) not in done]  # fmt: skip
        for record in pool.map(run_ahead, ahead):
            append_records(path, [record])


# --- what is measured ----------------------------------------------------------------------------

over, less = memory.over, memory.less


class Measures:
    """Every number a claim is judged on, from the records of a run."""

    def __init__(self, rows: list[dict], plan: dict, lent: np.ndarray | None = None,
                 chosen: dict | None = None):  # fmt: skip
        self.rows, self.plan = rows, plan
        self.lent = looks_rule() if lent is None else lent
        self.chosen = worlds() if chosen is None else chosen
        self.starts: dict = {}
        self.tallies: dict = {}
        self.ahead: dict = {}
        for r in rows:
            if r["kind"] == "start":
                self.starts.setdefault(r["world"], {})[r["seed"]] = r
            elif r["tick"] is None:
                continue  # a world without a clock: nothing was read or run on
            elif r["kind"] == "tally":
                self.tallies.setdefault(r["world"], {})[r["seed"]] = r
            else:
                self.ahead.setdefault((r["world"], r["reading"], r["rule"]), []).append(r)
        self._pooled: dict = {}

    def seeds(self, world: str, part: str) -> list[int]:
        return self.plan[world]["learn"] + self.plan[world]["try"] if part == "all" else (
            self.plan[world][part])  # fmt: skip

    # --- a world's clock

    def tick(self, world: str) -> int | None:
        return tick_of(self.rows, self.plan, world)

    def pace(self, world: str) -> float | None:
        """A world's pace beside the still world's: the still world's tick over its own."""
        return over(clock.STILL_TICK, self.tick(world))

    def walls_at(self, world: str, generation: int) -> float | None:
        thin = thinning(self.rows, world, self.seeds(world, "all"))
        return thin[generation // clock.WALLS_EVERY - 1] if thin else None

    def power(self, world: str) -> float | None:
        """The power of time by which a world's walls thin between generations 1,024 and
        4,096, as step 4f read a world's clock."""
        thins = over(self.walls_at(world, LATE), self.walls_at(world, EARLY))
        return -math.log(thins) / math.log(LATE / EARLY) if thins else None

    def held(self, world: str) -> float | None:
        """The larger species' share of the live cells at generation 4,096."""
        mine = list(self.starts.get(world, {}).values())
        if not mine:
            return None
        return float(np.mean([r["larger"][str(LATE)] / r["live"][str(LATE)] for r in mine]))

    def window_walls(self, world: str, which: int) -> float | None:
        """A world's walls at the start (0) or the end (1) of its window."""
        mine = list(self.tallies.get(world, {}).values())
        return float(np.mean([r["walls"][which] for r in mine])) if mine else None

    # --- one tick ahead

    def tally(self, world: str, part: str) -> np.ndarray:
        key = (world, part)
        if key not in self._pooled:
            self._pooled[key] = pooled(self.rows, world, self.seeds(world, part))
        return self._pooled[key]

    def bits(self, world: str, reading: str) -> float | None:
        own, trial = self.tally(world, "learn"), self.tally(world, "try")
        if not own.sum() or not trial.sum():
            return None
        return look.surprise(READINGS[reading], own, trial)

    def removed(self, world: str) -> float | None:
        return less(1.0, over(self.bits(world, HOW), self.bits(world, PLAIN)))

    def from_look(self, world: str, reading: str) -> float | None:
        """The look's rule, its tally scaled to as many transitions as the world's own rule
        learned from, on the world's trial starts: more surprise than the world's own."""
        sees = READINGS[reading]
        own, trial = self.tally(world, "learn"), self.tally(world, "try")
        here = self.bits(world, reading)
        if not here:
            return None
        there = look.surprise(sees, ladder.as_much(sees.of(self.lent), sees.of(own)), trial)
        return there / here - 1

    def chance(self, world: str, span: str | None, near: int) -> float | None:
        """The chance of another leader one tick on, from all of a world's starts, for blocks
        with `near` rival neighbours that have had their leader for `span` ticks (None:
        whatever their past)."""
        return chance_of(self.tally(world, "all"), span, near)

    # --- run on

    def end(self, world: str, reading: str, whose: str, what: str) -> float | None:
        runs = self.ahead.get((world, reading, whose), [])
        if not runs or sorted(r["seed"] for r in runs) != sorted(self.plan[world]["try"]):
            return None
        return float(np.mean([np.mean(r[what]) for r in runs]))

    def amiss(self, world: str, reading: str, whose: str) -> float | None:
        """Blocks amiss at the end of a rule's run-ons over blocks that changed leader."""
        return over(self.end(world, reading, whose, "amiss"),
                    self.end(world, reading, whose, "changed"))  # fmt: skip

    # --- what a claim stands on, and its number

    def gain(self, world: str) -> float | None:
        """Blocks amiss with the look's remembering rule over those with its plain rule."""
        return over(self.end(world, HOW, LOOKS, "amiss"), self.end(world, PLAIN, LOOKS, "amiss"))

    def stands(self, world: str | None) -> bool:
        """A claim about a world stands if its walls give it a tick and two species hold
        ground in it (the larger has at most HOLDS_GROUND of the live cells at generation
        4,096). A claim about all the worlds stands if there are worlds to rank."""
        if world is None:
            return len(self.ranked()) >= AT_LEAST
        held = self.held(world)
        return self.tick(world) is not None and held is not None and held <= HOLDS_GROUND

    def ranked(self) -> list[str]:
        """The worlds a rank correlation is taken over: every world but the still one that
        stands and has its numbers."""
        return [w for w in self.plan if w != STILL and self.stands(w)
                and self.removed(w) is not None and self.gain(w) is not None]  # fmt: skip

    def value(self, claim: dict) -> float | None:
        q, world = claim["quantity"], claim["world"]
        if q == "tick":
            tick = self.tick(world)
            return None if tick is None else float(tick)
        if q == "surprise removed":
            return self.removed(world)
        if q == "walls at the end of its window over the start":
            return over(self.window_walls(world, 1), self.window_walls(world, 0))
        if q == "pace here over the pace in step 4f":
            return over(self.pace(world), claim["before"])
        if q == "amiss over changed":
            return self.amiss(world, claim["reading"], claim["rule_of"])
        if q == "the look's rule":
            return self.from_look(world, claim["reading"])
        if q == "the look's rule, with how long in view less as it is":
            return less(self.from_look(world, HOW), self.from_look(world, PLAIN))
        if q == "amiss, the look's remembering rule over its plain one":
            return self.gain(world)
        if q == "amiss, the look's remembering rule over the world's own":
            return over(self.end(world, HOW, LOOKS, "amiss"), self.end(world, HOW, OWN, "amiss"))
        if q == "amiss, the look's plain rule over the world's own":
            return over(self.end(world, PLAIN, LOOKS, "amiss"),
                        self.end(world, PLAIN, OWN, "amiss"))  # fmt: skip
        if q == "ranks: missed in step 4f against surprise removed":
            mine = self.ranked()
            return rank_correlation([self.chosen[w][MISSED] for w in mine],
                                    [self.removed(w) for w in mine])  # fmt: skip
        if q == "ranks: surprise removed against the gain from remembering":
            mine = self.ranked()
            return rank_correlation([self.removed(w) for w in mine],
                                    [self.gain(w) for w in mine])  # fmt: skip
        raise ValueError(f"unknown quantity {q!r}")


def rank_correlation(first: list[float], second: list[float]) -> float | None:
    """Spearman's: the correlation of the two lists' ranks."""
    if len(first) < 3 or len(set(first)) < 2 or len(set(second)) < 2:
        return None

    def ranks(values: list[float]) -> np.ndarray:
        order = np.argsort(values)
        out = np.empty(len(values))
        out[order] = np.arange(len(values))
        return out

    return float(np.corrcoef(ranks(first), ranks(second))[0, 1])


def chance_of(counts: np.ndarray, span: str | None, near: int) -> float | None:
    """From a tally by how long: the chance of another leader one tick on for blocks with
    `near` rival neighbours that have had their leader for `span` ticks (None: all)."""
    found = look.hands(counts)
    low, high = (1, LONG.size) if span is None else memory.SPANS[span]
    blocks, changed = found[low - 1 : high].sum(axis=0)[near]
    return float(changed / blocks) if blocks >= memory.ENOUGH else None


# --- the predictions -----------------------------------------------------------------------------

# the bounds (sizing.json says what the sized worlds gave beside each)
STILL_TICKS = (14, 18)  # X: the still world's tick, by its walls
ANCHOR = (0.93, 1.07)  # X: the look's remembering rule over the still world's own (step 4i's)
SAME_PICTURE = (0.44, 0.62)  # S: walls at the end of a world's window over those at its start
TICK_AGREES = 1.3  # T: a world's pace here and step 4f's pace by its walls, within this factor
KEEPS = 0.80  # K: the look's plain rule on a world's own clock, amiss over changed, at most
PAST_MATTERS = 0.06  # P: how long removes at least this share of surprise, where served
PAST_DOES_NOT = 0.05  # P: and at most this share where missed
SERVES = 0.025  # O, J: one tick ahead a rule serves a world within this much more surprise
DOES_NOT = 0.05  # O: the look's plain rule where missed, more surprise, at least
GAINS = 0.85  # D: blocks amiss, the look's remembering rule over its plain one, where served
RUNS_IT = 0.55  # D: the look's remembering rule where served, amiss over changed, at most
AS_ITS_OWN = (0.90, 1.12)  # D: the look's remembering rule over the world's own
NO_GAIN = 0.88  # W: the look's remembering rule over its plain one where missed, at least
BEATS_OWN = 0.95  # B: the look's plain rule over the world's own plain rule, where missed
BEATS_TOO = 0.97  # B: and its remembering rule over the world's own remembering rule
RANKS = 0.5  # G: the rank correlations, at least this strong
HOLDS_GROUND = 0.8  # the larger species has at most this share of the live cells


def claims(chosen: dict | None = None) -> list[dict]:
    chosen = worlds() if chosen is None else chosen
    out = []

    def claim(family, label, text, quantity, world, at_least=None, at_most=None, **more):
        out.append({"label": label, "family": family, "claim": text, "quantity": quantity,
                    "world": world, "at_least": at_least, "at_most": at_most, **more})  # fmt: skip

    for rule, w in chosen.items():
        if rule == STILL:
            claim("X", "X the still world's tick",
                  "the still world's tick, read off its walls, is between "
                  f"{STILL_TICKS[0]} and {STILL_TICKS[1]} generations",
                  "tick", rule, at_least=STILL_TICKS[0], at_most=STILL_TICKS[1])  # fmt: skip
            claim("X", "X the still world's past matters",
                  f"in the still world how long removes at least {PAST_MATTERS:.0%} of the "
                  "plain rule's surprise",
                  "surprise removed", rule, at_least=PAST_MATTERS)  # fmt: skip
            claim("X", "X the look's remembering rule runs the still world better",
                  "run on by itself over the still world's window, the look's rule with how "
                  f"long in view ends amiss in at most {GAINS} times as many blocks as the "
                  "look's rule as it is",
                  "amiss, the look's remembering rule over its plain one", rule,
                  at_most=GAINS)  # fmt: skip
            claim("X", "X and as well as the still world's own",
                  f"and in between {ANCHOR[0]} and {ANCHOR[1]} times as many as the "
                  "remembering rule learned from these starts",
                  "amiss, the look's remembering rule over the world's own", rule,
                  at_least=ANCHOR[0], at_most=ANCHOR[1])  # fmt: skip
            continue
        mine = group(w)
        # every world: the same picture on its own clock, at the pace step 4f read, and kept
        claim("S", f"S {rule}: the same picture on its own clock",
              f"through blocks of 8, {rule} against its copy has between {SAME_PICTURE[0]} "
              f"and {SAME_PICTURE[1]} of its walls left at the end of its window (64 of its "
              "ticks) of those it had at the start (16 ticks), as the still world has over "
              "its matched age",
              "walls at the end of its window over the start", rule,
              at_least=SAME_PICTURE[0], at_most=SAME_PICTURE[1])  # fmt: skip
        claim("T", f"T {rule}: its tick is the pace step 4f read",
              f"the pace its tick gives (the still world's tick over its own) is within a "
              f"factor of {TICK_AGREES} of the pace step 4f read off its walls, "
              f"{w['pace by its walls in step 4f']}",
              "pace here over the pace in step 4f", rule, at_least=round(1 / TICK_AGREES, 4),
              at_most=TICK_AGREES, before=w["pace by its walls in step 4f"])  # fmt: skip
        claim("K", f"K {rule}: the look's plain rule keeps it",
              f"run on by itself on the world's own clock, the look's rule as it is ends "
              f"with another leader than the real world's in at most {KEEPS} of the share of "
              "blocks that changed leader meanwhile",
              "amiss over changed", rule, at_most=KEEPS, reading=PLAIN, rule_of=LOOKS)  # fmt: skip
        if mine == SERVED:
            claim("P", f"P {rule}: a block's past matters",
                  f"how long a block has had its leader removes at least {PAST_MATTERS:.0%} "
                  "of the surprise of the world's own plain rule",
                  "surprise removed", rule, at_least=PAST_MATTERS)  # fmt: skip
            for reading in (PLAIN, HOW):
                claim("O", f"O {rule}: the look's rule {reading} serves",
                      f"one tick ahead, on the world's own clock, the look's rule {reading} "
                      f"has at most {SERVES:.1%} more surprise than the world's own",
                      "the look's rule", rule, at_most=SERVES, reading=reading)  # fmt: skip
            claim("D", f"D {rule}: remembering gains",
                  "run on, the look's rule with how long in view ends amiss in at most "
                  f"{GAINS} times as many blocks as the look's rule as it is",
                  "amiss, the look's remembering rule over its plain one", rule,
                  at_most=GAINS)  # fmt: skip
            claim("D", f"D {rule}: and runs the world",
                  f"in at most {RUNS_IT} of the share of blocks that changed leader",
                  "amiss over changed", rule, at_most=RUNS_IT, reading=HOW,
                  rule_of=LOOKS)  # fmt: skip
            claim("D", f"D {rule}: as well as the world's own",
                  f"and in between {AS_ITS_OWN[0]} and {AS_ITS_OWN[1]} times as many blocks "
                  "as the world's own remembering rule",
                  "amiss, the look's remembering rule over the world's own", rule,
                  at_least=AS_ITS_OWN[0], at_most=AS_ITS_OWN[1])  # fmt: skip
        elif mine == JUST:
            for reading in (PLAIN, HOW):
                claim("J", f"J {rule}: the look's rule {reading} does not serve it",
                      f"one tick ahead, on the world's own clock, the look's rule {reading} "
                      f"has at least {SERVES:.1%} more surprise than the world's own",
                      "the look's rule", rule, at_least=SERVES, reading=reading)  # fmt: skip
        elif mine == FAR:
            claim("P", f"P {rule}: a block's past does not matter",
                  f"how long a block has had its leader removes at most {PAST_DOES_NOT:.0%} "
                  "of the surprise of the world's own plain rule",
                  "surprise removed", rule, at_most=PAST_DOES_NOT)  # fmt: skip
            claim("O", f"O {rule}: the look's plain rule does not serve",
                  "one tick ahead, on the world's own clock, the look's rule as it is has at "
                  f"least {DOES_NOT:.0%} more surprise than the world's own",
                  "the look's rule", rule, at_least=DOES_NOT, reading=PLAIN)  # fmt: skip
            claim("O", f"O {rule}: and remembering makes it worse",
                  "and the look's rule with how long in view more than that",
                  "the look's rule, with how long in view less as it is", rule,
                  at_least=0.0)  # fmt: skip
            claim("W", f"W {rule}: remembering does not gain",
                  "run on, the look's rule with how long in view ends amiss in at least "
                  f"{NO_GAIN} times as many blocks as the look's rule as it is",
                  "amiss, the look's remembering rule over its plain one", rule,
                  at_least=NO_GAIN)  # fmt: skip
            claim("B", f"B {rule}: the look's plain rule beats the world's own",
                  f"run on, the look's rule as it is ends amiss in at most {BEATS_OWN} times "
                  "as many blocks as the world's own plain rule",
                  "amiss, the look's plain rule over the world's own", rule,
                  at_most=BEATS_OWN)  # fmt: skip
            claim("B", f"B {rule}: and its remembering rule the world's own remembering rule",
                  f"and the look's rule with how long in view in at most {BEATS_TOO} times "
                  "as many as the world's own remembering rule",
                  "amiss, the look's remembering rule over the world's own", rule,
                  at_most=BEATS_TOO)  # fmt: skip
    claim("G", "G the more the old rule missed a world, the less its blocks' past matters",
          "over the worlds that keep the clock, the rank correlation between how far the "
          "still world's rule was from a world's own in step 4f and the share of surprise "
          f"that how long removes here is {-RANKS} or below",
          "ranks: missed in step 4f against surprise removed", None, at_most=-RANKS)  # fmt: skip
    claim("G", "G the more a block's past matters, the more remembering gains",
          "and between the share of surprise that how long removes and the look's "
          "remembering rule's blocks amiss over its plain rule's it is "
          f"{-RANKS} or below",
          "ranks: surprise removed against the gain from remembering", None,
          at_most=-RANKS)  # fmt: skip
    return out


def predictions() -> list[dict]:
    return claims()


# --- the verdict ---------------------------------------------------------------------------------

number = memory.number


def judge(value: float | None, claim: dict, stands: bool) -> str:
    if not stands or value is None or not np.isfinite(value):
        return "not tested"
    if claim["at_least"] is not None and value < claim["at_least"]:
        return "fails"
    if claim["at_most"] is not None and value > claim["at_most"]:
        return "fails"
    return "holds"


def told(m: Measures, world: str) -> dict:
    """What a reader wants of one world beside the verdicts."""
    w = m.chosen.get(world, {})
    out: dict = {
        "group": "the still world" if world == STILL else group(w),
        "live at generation 4,096": number(float(np.mean(
            [r["live"][str(LATE)] for r in m.starts[world].values()])), 4) if m.starts.get(world)
        else None,
        "the larger species' share of the live": number(m.held(world), 4),
        "walls thin as time to the power": number(m.power(world), 3),
        "tick": m.tick(world),
        "pace": number(m.pace(world), 3),
        "stands": m.stands(world),
    }  # fmt: skip
    if m.tick(world) is None:
        return out
    out["window"] = list(clock.window(m.tick(world)))
    out["walls at the start and the end of its window"] = [
        number(m.window_walls(world, i), 4) for i in (0, 1)]  # fmt: skip
    out["bits a block"] = {reading: number(m.bits(world, reading), 6) for reading in READINGS}
    out["share of the plain rule's surprise that how long removes"] = number(m.removed(world), 4)
    out["the look's rule, more surprise"] = {
        reading: number(m.from_look(world, reading), 4) for reading in READINGS}  # fmt: skip
    out["chance of another leader one tick on, at 3, 4 and 5 rival neighbours"] = {
        "whatever its past": [number(m.chance(world, None, n), 4) for n in (3, 4, 5)],
        "a lead of one tick": [number(m.chance(world, memory.NEW, n), 4) for n in (3, 4, 5)],
        "a lead of 16 ticks or more": [number(m.chance(world, memory.OLD, n), 4)
                                       for n in (3, 4, 5)],
    }  # fmt: skip
    ran = {}
    for reading in READINGS:
        for whose in (OWN, LOOKS):
            end = lambda what, r=reading, w=whose: m.end(world, r, w, what)  # noqa: E731
            ran[f"{reading}, {whose}"] = {
                "amiss over changed": number(m.amiss(world, reading, whose), 4),
                "walls kept": number(over(end("walls_rule"), end("walls_world")), 4),
                "going back, the world and the rule's world": [
                    number(end("returns_world"), 4), number(end("returns_rule"), 4)],
                "blocks that change hands in a tick, the world and the rule's world": [
                    number(end("changes_world"), 5), number(end("changes_rule"), 5)],
            }  # fmt: skip
    out["run on"] = ran
    out["blocks amiss, the look's remembering rule over its plain one"] = number(m.gain(world), 4)
    out["against the bars"] = bars(m, world)
    return out


def bars(m: Measures, world: str) -> dict:
    """Where a world stands against the study's bars, whatever its group and whether or not
    a claim was made of it: so that the worlds a rule serves can be counted the same way
    over all of them. None where the world has no such number."""

    def most(value: float | None, bound: float) -> bool | None:
        return None if value is None else bool(value <= bound)

    def least(value: float | None, bound: float) -> bool | None:
        return None if value is None else bool(value >= bound)

    beside = over(m.end(world, HOW, LOOKS, "amiss"), m.end(world, HOW, OWN, "amiss"))
    return {
        "a block's past matters": least(m.removed(world), PAST_MATTERS),
        "one tick ahead, the look's rule as it is serves": most(
            m.from_look(world, PLAIN), SERVES),
        "one tick ahead, the look's rule with how long in view serves": most(
            m.from_look(world, HOW), SERVES),
        "run on, the look's plain rule keeps it": most(m.amiss(world, PLAIN, LOOKS), KEEPS),
        "run on, the look's remembering rule runs it": most(
            m.amiss(world, HOW, LOOKS), RUNS_IT),
        "run on, remembering gains": most(m.gain(world), GAINS),
        "run on, the look's remembering rule does as the world's own": (
            None if beside is None else bool(AS_ITS_OWN[0] <= beside <= AS_ITS_OWN[1])),
    }  # fmt: skip


def counted(m: Measures) -> dict:
    """For each bar and each group of worlds, how many meet it, of those that stand and have
    the number (the still world apart)."""
    out: dict = {}
    for world in m.plan:
        if world == STILL or not m.stands(world):
            continue
        for bar, met in bars(m, world).items():
            if met is not None:
                cell = out.setdefault(bar, {}).setdefault(group(m.chosen[world]), [0, 0])
                cell[0] += int(met)
                cell[1] += 1
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    plan = design()
    have = {(r["kind"], r["world"], r["seed"], r.get("tick")) for r in rows
            if r["kind"] != "ahead"}  # fmt: skip
    missing = [f"{world} from start {seed}" for world, seed in start_jobs(plan)
               if ("start", world, seed, None) not in have]  # fmt: skip
    if not missing:  # a tally counts only at the tick the world's walls give
        missing = [f"the tally of {world} from start {seed} at a tick of {tick}"
                   for world, seed, tick in tally_jobs(rows, plan)
                   if ("tally", world, seed, tick) not in have]  # fmt: skip
    if not missing:
        done = {(r["world"], r["seed"], r["tick"], r["reading"], r["rule"]) for r in rows
                if r["kind"] == "ahead"}  # fmt: skip
        missing = [f"the run-on of the rule {job[3]}, {job[4]}, in {job[0]} from start {job[1]}"
                   for job in ahead_jobs(rows, plan)
                   if (job[0], job[1], job[2], job[3], job[4]) not in done]  # fmt: skip
    outcomes, measured, reported, met = {}, {}, {}, {}
    if missing:
        outcomes = {c["label"]: "missing" for c in registered}
    else:
        m = Measures(rows, plan)
        for c in registered:
            value = m.value(c)
            outcomes[c["label"]] = judge(value, c, m.stands(c["world"]))
            measured[c["label"]] = {"value": number(value)}
        reported = {world: told(m, world) for world in plan}
        met = counted(m)

    def overall(family: str) -> str:
        words = {outcomes[c["label"]] for c in registered if c["family"] == family}
        for word in ("missing", "fails", "holds"):
            if word in words:
                return word
        return "not tested"

    counts: dict = {}
    for c in registered:
        counts.setdefault(c["family"], {}).setdefault(outcomes[c["label"]], 0)
        counts[c["family"]][outcomes[c["label"]]] += 1
    return {
        "verdict": {f: overall(f) for f in sorted({c["family"] for c in registered})},
        "counts": counts,
        "outcomes": outcomes,
        "measured": measured,
        "missing": missing[:20],
        "worlds met a bar, of those with the number, by group": met,
        "worlds": reported,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    if record["kind"] == "start":
        return run_start((record["world"], record["seed"]))
    if record["kind"] == "tally":
        return run_tally((record["world"], record["seed"], record["tick"]))
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    wanted = (record["world"], record["seed"], record["reading"], record["rule"])
    for job in ahead_jobs(rows, design()):
        if (job[0], job[1], job[3], job[4]) == wanted:
            return run_ahead(job)
    raise ValueError(f"no run-on {wanted} in this design")


def question() -> dict:
    plan = design()
    chosen = worlds()
    sizing = json.loads(SIZING.read_text())
    sized = sizing["the sized worlds"]
    return {
        "id": "scale-up-class-memory",
        "title": "Does a rule that remembers carry the class?",
        "statement": "The still world and 29 worlds that keep its clock are each read on "
        "their own clock: a tick set by their walls, and a window from 16 of those ticks to "
        "64. Read so, the still world is the still world of steps 4g to 4i (X); every world "
        "is the same picture (S) at the pace step 4f read (T); and the look's plain rule, "
        "unchanged, keeps every one when run on (K). A block's past matters in the worlds "
        "step 4f found served and not in those it missed by a tenth or more (P); one tick "
        "ahead the look's rule serves the first and not the second, where remembering makes "
        "it worse (O), nor does it serve any of the five worlds step 4f just missed, as it "
        "is or with how long in view (J). In the worlds served the look's remembering rule "
        "gains on its plain one, runs the world, and does it as the world's own does (D); "
        "in the worlds missed it does not gain (W), though there the look's rules run a "
        "world on better than the world's own (B). Over all of them, the more the old rule "
        "missed a world the less its blocks' past matters and the less remembering gains "
        "(G). So the rule that remembers does not reach the worlds the plain rule missed: it "
        "carries the worlds the plain rule served, better. Of the four worlds step 4f found "
        "nearly served nothing more is claimed; every world is counted against the same "
        "bars in the verdict.",
        "source": "docs/scale-up-plan.md, steps 4f, 4h, 4i and decision D14",
        "worlds": {rule: {"rules": [rule] * 2, "tie_break": "standoff", "density": 1.0,
                          "group": w["group"], "in_the_sizing_look": rule in sized,
                          "learned_from": plan[rule]["learn"], "tried_on": plan[rule]["try"]}
                   for rule, w in chosen.items()},  # fmt: skip
        "side": clock.SIDE,
        "generations": clock.GENERATIONS,
        "block": clock.BLOCK,
        "a world's clock": "its tick is a sixteenth of the generation at which the mean walls "
        f"of the starts it learns from thin to {clock.STARTS_AT}, to the nearest "
        f"{clock.EVERY} generations; its window runs from {clock.FIRST_TICK} ticks to "
        f"{clock.LAST_TICK}",
        "readings": {PLAIN: "the leader, and how many of the eight neighbours each species "
                     "leads", HOW: "the same, and for how many ticks running the block has "
                     "had its leader, up to 8"},  # fmt: skip
        "runs": len(start_jobs(plan)) * 2 + 4 * (STARTS_EACH // 2) * len(plan),
        "run_ons_of_a_rule_from_a_start": 2 * PAIRS,
        "not_tested": "A claim about a world is not tested where its walls give it no tick "
        f"whose window ends inside a run of {clock.GENERATIONS} generations, or the larger "
        f"species has more than {HOLDS_GROUND} of the live cells at generation 4,096. A "
        f"rank correlation is not tested over fewer than {AT_LEAST} worlds. And no claim is "
        "tested without a number to judge.",
        "sizing": sizing["what the bounds were drawn from"],
        "sha256": {
            "study.py": sha(HERE / "study.py"),
            "clock.py": sha(HERE / "clock.py"),
            "worlds.json": sha(WORLDS),
            "sizing.json": sha(SIZING),
            "sizing.py": sha(HERE / "sizing.py"),
            "../scale-up-memory/look.py": sha(clock.MEMORY / "look.py"),
            "../scale-up-memory/study.py": sha(clock.MEMORY / "study.py"),
            "../scale-up-memory/reference.json": sha(memory.REFERENCE),
            "../scale-up-class/ledger.jsonl": sha(STEP_4F / "ledger.jsonl"),
            "../scale-up-closure-territories/ladder.py": sha(memory.STEP_4E / "ladder.py"),
        },
        "excluded_seen": [
            "Step 4f (examples/scale-up-class) ran these 29 worlds and the still world on "
            "side 1,024 to generation 4,096 from starts 17001 to 17744 and 17901 to 17908, "
            "and read them at the still world's tick with nothing of a block's past in "
            "view. The worlds and their groups here are chosen from its verdict.",
            "The sizing look (sizing.py here, exploratory, on a rented pod): eleven of "
            "these worlds and the still world run again from starts step 4f had used (two or "
            "four each, among 17001 to 17664 and 17901 to 17904), read every two generations, "
            "and put through this study's own run and every measure of it, both ways round. "
            "Every bound here was drawn from it; the bound of J, of worlds it did not see, "
            "from what it showed of the others. The worlds it saw are marked in `worlds`: "
            "five of the ten that step 4f found served, one of the four nearly served, none "
            "of the five just missed, and five of the ten missed. Eighteen were not in it.",
            "Steps 4g to 4i read the still and the busy world with a block's past in view; "
            "the look's rule tried here was learned in the still world on side 2,048 from "
            "starts 18001 to 18008.",
            "No start from 20001 on has been generated or run on a grid of this size (the "
            "study's tests run three of these worlds from theirs on side 128).",
        ],
    }  # fmt: skip


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
