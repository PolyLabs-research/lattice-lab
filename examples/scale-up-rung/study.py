"""
A registered test: does the ladder come to a fixed point? One more rung.

    uv run --no-sync python examples/scale-up-rung/study.py register
    uv run --no-sync python examples/scale-up-rung/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-rung

**Why.** The ladder of docs/scale-up-plan.md looks for a coarse rule that stops changing from
one block size to the next: that rule would be the large-scale law. Steps 4d and 4e read two
worlds of territories through blocks of 4, 8 and 16 and found the rule still changing, but by
less at each rung when each rung is read at the age that matches its block (these worlds are
the same picture four times later through blocks twice the size). The rule from blocks of 4
had 9% and 6% more surprise at blocks of 8 than the rung's own rule; the rule from blocks of
8 had 3% at blocks of 16. Two steps make no trend. This reads one rung more, blocks of 32,
which at their matched age need a grid twice as wide run four times as long.

**What is run.** The first look's two worlds, B245678/S3678 against its copy (still grounds)
and B23467/S4568 against its copy (busy grounds), under the standoff from a full start, on a
wrapped grid of side 2,048 for 16,384 generations, from eight fresh starts each (four to
learn from, four to try on). Each block is read on the square clock over the generations
that match it (`AGES`): blocks of 4 over 64 to 256, of 8 over 256 to 1,024, of 16 over 1,024
to 4,096, of 32 over 4,096 to 16,384. That is 48 coarse generations at every rung.

**What is read** (the measures are step 4e's, `ladder.py` there).

- **The gap** (`gap`): how much more surprise the rule learned at blocks half the size has,
  tried at this rung with as much data as the rung's own rule, than the rung's own.
- **The chance of changing hands** at five rival neighbours, rung by rung.
- **The ladder's own test** (`ahead`): the rule of the rung below is used as the rule of this
  rung and run on by itself over the rung's 48 coarse generations, beside the rung's own.
  Read as step 4e read a run-on: the blocks whose leader is not the real world's at the
  end, over the blocks that changed leader meanwhile.

**Predictions** (`claims`), in six families.

    S  scaling: at matched ages a world is the same picture at every rung (as many walls)
    X  another grid: the rule step 4e learned on side 1,024 serves on side 2,048
    G  the gap: at blocks of 16 it is what it was, and at blocks of 32 it is smaller again
    H  the chance of changing hands falls from blocks of 16 to 32 by no more than a fifth
    C  at the new rung a world's own rule, run on by itself, keeps the world
    L  the ladder's own test: the rule from the rung below runs this rung on, nearly as well
       as the rung's own rule, at blocks of 16 and at blocks of 32

A claim holds if its number is inside its bound and fails if it is not. A run-on is read
only through blocks small beside the world's territories when it starts (as in step 4e), and
is **not tested** otherwise.

Every number but those of the run-ons is worked out again in `decide` from the tallies in
the records. **What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import json
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
SIZING = HERE / "sizing.json"
BEFORE = STEP_4E / "records.jsonl"  # step 4e's registered records, for the rule of side 1,024

SIDE, GENERATIONS = 2048, 16384
WORLDS = {
    "still": {"rule": "B245678/S3678", "first": 18001, "before": 16001},
    "busy": {"rule": "B23467/S4568", "first": 18101, "before": 16101},
}
STARTS = 8  # a world's starts: the first half to learn from, the second to try on
BLOCKS = (4, 8, 16, 32)
AGES = {4: (64, 256), 8: (256, 1024), 16: (1024, 4096), 32: (4096, 16384)}  # a block's matched age
OWN, BELOW = "its own", "the rung below's"

# --- the bounds (what they were drawn from is in sizing.json)
SAME_PICTURE = 0.10  # S: the walls at the start of each rung's age, within this of each other
SAME_GRID = 0.005  # X: step 4e's rule on the wider grid, at most this much more surprise
GAP_AT_16 = (0.015, 0.045)  # G: the gap at blocks of 16, as steps 4d and 4e found it
LEVELS = 0.80  # H: the chance at blocks of 32 over the chance at blocks of 16, at least
WHERE = 0.70  # C: blocks amiss over blocks that changed, the rung's own rule, at most
WALLS = (0.80, 1.15)  # C: the walls the rung's own rule keeps over the world's
BELOW_WHERE = 0.75  # L: blocks amiss over blocks that changed, the rule from below, at most
BELOW_OVER_OWN = 1.30  # L: blocks amiss with the rule from below over with the rung's own
BLOCK_FITS = 0.2  # at most this share of neighbouring blocks differ when a rule is run on


def design() -> dict:
    out = {}
    for name, w in WORLDS.items():
        seeds = list(range(w["first"], w["first"] + STARTS))
        out[name] = {"learn": seeds[: STARTS // 2], "try": seeds[STARTS // 2 :]}
    return out


# --- the runs ------------------------------------------------------------------------------------


def cache_path(name: str, seed: int) -> Path:
    return ladder.CACHE / f"rung-{name}-{SIDE}-{GENERATIONS}-{seed}.npz"


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


def run_start(job: tuple[str, int]) -> dict:
    """One world from one start: on record, for each block, its tally on the square clock over
    its matched age and its walls at the ends of it; and the share of the grid live, and the
    larger species' share, at every end."""
    name, seed = job
    found = fine(name, seed)
    marks = sorted({g for span in AGES.values() for g in span if g <= GENERATIONS})
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
        "tally": {str(b): ladder.sparse(ladder.tally(found[b], b, ladder.square(b), *AGES[b]))
                  for b in BLOCKS},
    }  # fmt: skip


def pooled(rows: list[dict], world: str, seeds, block: int) -> np.ndarray:
    """The tallies of a world's starts `seeds` at one block, over its matched age."""
    total = np.zeros((ladder.Q, 9, 9, ladder.Q), dtype=np.int64)
    for row in rows:
        if row["kind"] == "start" and row["world"] == world and row["seed"] in seeds:
            total += ladder.dense(row["tally"][str(block)])
    return total


def run_ahead(job: tuple[str, int, int, str, list]) -> dict:
    """A rule run on by itself at one rung of one start of one world, over the rung's matched
    age."""
    name, seed, block, whose, rows = job
    frames = fine(name, seed)[block]
    draws = (seed, block, (OWN, BELOW).index(whose))
    found = ladder.ahead(frames, ladder.dense(rows), block, ladder.square(block), draws,
                         *AGES[block])  # fmt: skip
    return {"kind": "ahead", "world": name, "seed": seed, "rule": whose, **found}


def start_jobs(plan: dict) -> list[tuple[str, int]]:
    seeds = {name: plan[name]["learn"] + plan[name]["try"] for name in plan}
    return [(name, s[i]) for i in range(STARTS) for name, s in seeds.items() if i < len(s)]


def ahead_jobs(rows: list[dict], plan: dict) -> list:
    """At blocks of 8, 16 and 32, on each world's trial starts: the rung's own rule and the
    rule of the rung below, each learned from the starts the world learns from."""
    out = []
    for name in plan:
        for block in BLOCKS[1:]:
            for whose, source in ((OWN, block), (BELOW, block // 2)):
                counts = pooled(rows, name, plan[name]["learn"], source)
                for seed in plan[name]["try"]:
                    out.append((name, seed, block, whose, ladder.sparse(counts)))
    return out


def execute(path: Path, workers: int) -> None:
    plan = design()
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    done = {(r["kind"], r["world"], r["seed"], r.get("block"), r.get("rule")) for r in rows}
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


def before(world: str) -> np.ndarray:
    """The rule step 4e learned for a world at blocks of 16 at their matched age, on side
    1,024: the tally of all eight of its starts there over generations 1,024 to 4,096."""
    first = WORLDS[world]["before"]
    total = np.zeros((ladder.Q, 9, 9, ladder.Q), dtype=np.int64)
    for line in BEFORE.read_text().splitlines():
        r = json.loads(line)
        if r["kind"] == "start" and r["world"] == world and first <= r["seed"] < first + 8:
            total += ladder.dense(r["tally"][ladder.key(16, ladder.square(16))]["C"])
    return total


class Measures:
    """Every number a claim is judged on, from the records of a run."""

    def __init__(self, rows: list[dict], plan: dict):
        self.rows, self.plan = rows, plan
        self.ahead: dict = {}
        for r in rows:
            if r["kind"] == "ahead":
                self.ahead.setdefault((r["world"], r["block"], r["rule"]), []).append(r)

    def seeds(self, world: str, part: str) -> list[int]:
        return self.plan[world]["learn"] + self.plan[world]["try"] if part == "all" else (
            self.plan[world][part])  # fmt: skip

    def rule(self, world: str, part: str, block: int) -> np.ndarray:
        return pooled(self.rows, world, self.seeds(world, part), block)

    def walls(self, world: str, part: str, block: int, which: int) -> float | None:
        """A world's walls at one block at the start (0) or the end (1) of its matched age."""
        mine = [r for r in self.rows if r["kind"] == "start" and r["world"] == world
                and r["seed"] in self.seeds(world, part)]  # fmt: skip
        if not mine:
            return None
        return float(np.mean([r["walls"][str(block)][str(AGES[block][which])] for r in mine]))

    def same_picture(self, world: str) -> float | None:
        """How far apart the walls at the start of each rung's matched age are, blocks of 8,
        16 and 32: the largest over the smallest, less one."""
        found = [self.walls(world, "all", block, 0) for block in BLOCKS[1:]]
        if any(not w for w in found):
            return None
        return max(found) / min(found) - 1

    def gap(self, world: str, block: int) -> float:
        """The rule of the rung below, with as much data, tried at this rung."""
        here = self.rule(world, "learn", block)
        lower = ladder.as_much(self.rule(world, "learn", block // 2), here)
        return ladder.excess(lower, here, self.rule(world, "try", block))

    def five(self, world: str, block: int) -> float | None:
        return ladder.changes(self.rule(world, "all", block), 5)

    def from_before(self, world: str) -> float:
        """Step 4e's rule of side 1,024 at blocks of 16, tried here."""
        return ladder.excess(before(world), self.rule(world, "learn", 16),
                             self.rule(world, "try", 16))  # fmt: skip

    def end(self, world: str, block: int, whose: str, what: str) -> float | None:
        runs = self.ahead.get((world, block, whose), [])
        if sorted(r["seed"] for r in runs) != sorted(self.plan[world]["try"]):
            return None
        return float(np.mean([r[what][-1] for r in runs]))

    def amiss(self, world: str, block: int, whose: str) -> float | None:
        return over(self.end(world, block, whose, "apart_rule"),
                    self.end(world, block, whose, "apart_start"))  # fmt: skip

    def fits(self, world: str, block: int) -> bool:
        walls = self.walls(world, "try", block, 0)
        return walls is not None and walls <= BLOCK_FITS

    def stands(self, claim: dict) -> bool:
        return claim["fits"] is None or self.fits(claim["world"], claim["fits"])

    def value(self, claim: dict) -> float | None:
        q, world, block = claim["quantity"], claim["world"], claim.get("block")
        if q == "walls at matched ages apart":
            return self.same_picture(world)
        if q == "step 4e's rule":
            return self.from_before(world)
        if q == "gap":
            return self.gap(world, block)
        if q == "gap, this rung less the one below":
            return self.gap(world, block) - self.gap(world, block // 2)
        if q == "chance at five, this rung over the one below":
            return over(self.five(world, block), self.five(world, block // 2))
        if q == "amiss over changed":
            return self.amiss(world, block, claim["rule"])
        if q == "walls kept":
            return over(self.end(world, block, OWN, "walls_rule"),
                        self.end(world, block, OWN, "walls_world"))  # fmt: skip
        if q == "amiss, the rule from below over the rung's own":
            return over(self.end(world, block, BELOW, "apart_rule"),
                        self.end(world, block, OWN, "apart_rule"))  # fmt: skip
        raise ValueError(f"unknown quantity {q!r}")


# --- the predictions -----------------------------------------------------------------------------


def claims() -> list[dict]:
    out = []

    def claim(family, label, text, quantity, world, at_least=None, at_most=None, **more):
        out.append({"label": label, "family": family, "claim": text, "quantity": quantity,
                    "world": world, "at_least": at_least, "at_most": at_most,
                    "fits": more.pop("fits", None), **more})  # fmt: skip

    for w in WORLDS:
        claim("S", f"S {w}: the same picture at matched ages",
              f"in the {w} world the share of neighbouring blocks under different leaders at "
              "the start of each rung's matched age (blocks of 8 at generation 256, of 16 at "
              f"1,024, of 32 at 4,096) is the same within {SAME_PICTURE:.0%}",
              "walls at matched ages apart", w, at_most=SAME_PICTURE)  # fmt: skip
        claim("X", f"X {w}: another grid",
              f"the rule step 4e learned for the {w} world at blocks of 16 on side 1,024 has at "
              f"most {SAME_GRID:.1%} more surprise on side 2,048 than the rule learned there",
              "step 4e's rule", w, at_most=SAME_GRID)  # fmt: skip
        claim("G", f"G {w}: the gap at blocks of 16",
              f"in the {w} world the rule from blocks of 8 has between {GAP_AT_16[0]:.1%} and "
              f"{GAP_AT_16[1]:.1%} more surprise at blocks of 16 than the rung's own rule, at "
              "matched ages, as steps 4d and 4e found",
              "gap", w, at_least=GAP_AT_16[0], at_most=GAP_AT_16[1], block=16)  # fmt: skip
        claim("G", f"G {w}: the gap shrinks again",
              f"in the {w} world the rule from blocks of 16 is nearer the rung's own at blocks "
              "of 32 than the rule from blocks of 8 is at blocks of 16",
              "gap, this rung less the one below", w, at_most=0.0, block=32)  # fmt: skip
        claim("H", f"H {w}: the chances level off",
              f"in the {w} world a block of 32 with five neighbours under its rival changes "
              f"hands at least {LEVELS} times as often as a block of 16 does, each at its "
              "matched age",
              "chance at five, this rung over the one below", w, at_least=LEVELS,
              block=32)  # fmt: skip
        claim("C", f"C {w}: the new rung, where",
              f"run on by itself over generations 4,096 to 16,384, the {w} world's own rule at "
              "blocks of 32 ends with another leader than the real world's in at most "
              f"{WHERE} of the share of blocks that changed leader meanwhile",
              "amiss over changed", w, at_most=WHERE, block=32, rule=OWN, fits=32)  # fmt: skip
        claim("C", f"C {w}: the new rung, walls",
              f"and ends with between {WALLS[0]} and {WALLS[1]} of the world's walls",
              "walls kept", w, at_least=WALLS[0], at_most=WALLS[1], block=32, fits=32)  # fmt: skip
        for block in (16, 32):
            claim("L", f"L {w}, block {block}: the rule from below runs it on",
                  f"in the {w} world the rule learned at blocks of {block // 2}, used as the "
                  f"rule at blocks of {block} and run on by itself over the rung's matched "
                  "age, ends with another leader than the real world's in at most "
                  f"{BELOW_WHERE} of the share of blocks that changed leader meanwhile",
                  "amiss over changed", w, at_most=BELOW_WHERE, block=block, rule=BELOW,
                  fits=block)  # fmt: skip
            claim("L", f"L {w}, block {block}: nearly as well as the rung's own",
                  f"and in at most {BELOW_OVER_OWN} times as many blocks as the rung's own "
                  "rule does",
                  "amiss, the rule from below over the rung's own", w,
                  at_most=BELOW_OVER_OWN, block=block, fits=block)  # fmt: skip
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
    """What a reader wants of one world beside the verdicts: the ladder, rung by rung."""
    out: dict = {"rungs": {}}
    for block in BLOCKS:
        rung: dict = {
            "matched age": list(AGES[block]),
            "walls at its start and its end": [number(m.walls(world, "all", block, i), 4)
                                               for i in (0, 1)],
            "changes hands, by rival neighbours": [
                round(float(c / b), 4) if b else None
                for b, c in ladder.hands(m.rule(world, "all", block))],
        }  # fmt: skip
        if block > BLOCKS[0]:
            rung["gap: the rule from the rung below, more surprise"] = number(m.gap(world, block))
            rung["a block fits"] = m.fits(world, block)
            rung["run on, amiss over changed"] = {
                whose: number(m.amiss(world, block, whose), 4) for whose in (OWN, BELOW)
            }
            rung["run on, walls kept"] = {
                whose: number(over(m.end(world, block, whose, "walls_rule"),
                                   m.end(world, block, whose, "walls_world")), 4)
                for whose in (OWN, BELOW)}  # fmt: skip
            rung["run on, amiss over two runs"] = number(
                over(
                    m.end(world, block, OWN, "apart_rule"), m.end(world, block, OWN, "apart_twin")
                ),
                4,
            )
        out["rungs"][str(block)] = rung
    records = [r for r in m.rows if r["kind"] == "start" and r["world"] == world]
    out["live"] = {g: round(float(np.mean([r["live"][g] for r in records])), 4)
                   for g in records[0]["live"]}  # fmt: skip
    out["larger species"] = {g: round(float(np.mean([r["larger"][g] for r in records])), 4)
                             for g in records[0]["larger"]}  # fmt: skip
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    plan = design()
    have = {(r["world"], r["seed"]) for r in rows if r["kind"] == "start"}
    missing = [f"{name} from start {seed}" for name, seed in start_jobs(plan)
               if (name, seed) not in have]  # fmt: skip
    if not missing:
        done = {(r["world"], r["seed"], r["block"], r["rule"]) for r in rows
                if r["kind"] == "ahead"}  # fmt: skip
        missing = [f"the run-on of {job[3]} rule in the {job[0]} world from start {job[1]}, "
                   f"blocks of {job[2]}" for job in ahead_jobs(rows, plan)
                   if tuple(job[:4]) not in done]  # fmt: skip
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

    return {
        "verdict": {f: overall(f) for f in sorted({c["family"] for c in registered})},
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
        "id": "scale-up-rung",
        "title": "Does the ladder come to a fixed point? One more rung.",
        "statement": "Two worlds of territories are read through blocks of 4, 8, 16 and 32, "
        "each block on the square clock over the generations that match it, on a grid twice "
        "as wide as before run four times as long. At matched ages the world is the same "
        "picture at every rung (S); the rule learned on the smaller grid serves on the larger "
        "(X); the rule from the rung below is as far from the rung's own at blocks of 16 as "
        "it was, and nearer at blocks of 32 (G); the chance of changing hands levels off (H); "
        "at the new rung a world's own rule keeps the world (C); and the rule from the rung "
        "below, used as this rung's rule, runs the world on nearly as well as the rung's own "
        "(L).",
        "source": "docs/scale-up-plan.md, steps 4d and 4e and decision D11",
        "worlds": {name: {"rules": [w["rule"]] * 2, "tie_break": "standoff", "density": 1.0,
                          "learned_from": plan[name]["learn"], "tried_on": plan[name]["try"]}
                   for name, w in WORLDS.items()},  # fmt: skip
        "side": SIDE,
        "generations": GENERATIONS,
        "matched_ages": {str(b): {"generations": list(AGES[b]), "tick": ladder.square(b)}
                         for b in BLOCKS},  # fmt: skip
        "runs": len(start_jobs(plan)) + 2 * 3 * (STARTS // 2) * len(WORLDS),
        "not_tested": "A claim about a rule run on through blocks of some size is not tested "
        f"where more than {BLOCK_FITS} of neighbouring blocks of that size have different "
        "leaders when the rule is started (territories under five blocks across), on the "
        "world's trial starts; and no claim is tested without a number to judge.",
        "sizing": json.loads(SIZING.read_text())["what the bounds were drawn from"],
        "sha256": {
            "study.py": sha(HERE / "study.py"),
            "sizing.json": sha(SIZING),
            "../scale-up-closure-territories/ladder.py": sha(STEP_4E / "ladder.py"),
            "../scale-up-closure-territories/records.jsonl": sha(BEFORE),
        },
        "excluded_seen": [
            "Steps 4d and 4e (examples/scale-up-closure-territories): these two worlds on "
            "side 1,024 to generation 4,096 from starts 15001 to 15008 and 16001 to 16108, "
            "read through blocks of 4 to 32. Blocks of 32 were read there at ages that do not "
            "match (generations 64 to 4,096), never at 4,096 to 16,384.",
            "The sizing look (sizing.py here, exploratory): the first look's kept runs at "
            "matched ages, blocks of 4, 8 and 16, with the rule from the rung below run on. "
            "Every bound here was drawn from it and from step 4e's records. It ran nothing.",
            "The search (examples/scale-up-search) ran both worlds on side 1,024 to "
            "generation 2,048 and read them by their correlation area.",
            "Neither world has been run on side 2,048, or past generation 4,096 on a grid "
            "this large or larger, and no start from 18001 on has been generated or run.",
        ],
    }  # fmt: skip


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    if record["kind"] == "start":
        return run_start((record["world"], record["seed"]))
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    wanted = (record["world"], record["seed"], record["block"], record["rule"])
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
