"""
A registered test: does a coarse rule for movement stand in for the fine world, on a torus and
at a block it was not fitted on?

    uv run --no-sync python examples/scale-up-closure/study.py register
    uv run --no-sync python examples/scale-up-closure/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-closure

**The idea.** A first look (look.py, exploratory, side 1024) read Life against HighLife through
blocks, with the clock at the block, and found that what is left to describe when it is zoomed
out is where things still move. A supercell is then one bit: did any cell of the block change
over the last coarse generation. This asks whether what the first look saw of that bit holds on
a torus twice as wide, from fresh starts, and at a block twice as large as any it used.

**What is run.** Life against HighLife under the standoff on a wrapped grid of side 2048 for
1,024 generations, from sixteen fresh starts: eight to learn coarse rules from and eight to
try them on. Blocks of 4, 8, 16, 32 and 64. For the known answer alone, soup 19 under the
standoff (side 1024, four starts) and the pair read with the clock four blocks long.

**Predictions**, 45 in six families (the first look's numbers are in each claim):

- *S, stillness is stable.* A block whose 3 x 3 neighbourhood did not change over the last
  coarse generation does not change over the next: none does, in either world, at any block.
  That is exact where the world is a function of its grid and the clock is no longer than the
  block. The control: with the clock four blocks long, some do.
- *N, the neighbours sharpen the odds without changing the best guess.* After generation 256
  a rule that knows how many of a block's neighbours moved has less surprise than one that
  knows the block alone, by the share the first look found (within 0.02 at blocks 4 to 32; at
  block 64 a share between 0.02 and 0.08, by the trend); and it calls the next symbol wrong
  almost as often (it removes less than 2% of the errors).
- *T, one rule at every time.* The rule with neighbour counts learned up to generation 256
  has at most 2% more surprise after it than the rule learned after it; the rule that knows
  the block alone, learned the same way, has at least 30% more (blocks 4, 8 and 16).
- *X, a torus it was not fitted on.* The first look's rule, learned on side 1024, has at most
  0.2% more surprise on the new torus than the rule learned there (blocks 4 to 32).
- *E, one number at every scale.* The chance that a still block with exactly one moving
  neighbour moves next is between 0.006 and 0.011 at every block from 4 to 32 (the first look
  found 0.0076 to 0.0086), and between 0.005 and 0.012 at block 64, which gives fewer cases.
- *H, the horizon.* Run on by itself from generation 128, by draws: eight coarse generations
  on, the rule with neighbour counts has within 30% of the fine world's movement at every
  block; at the end of the run the rule that knows the block alone has at least 2.5 times the
  fine world's, and at blocks 4 and 8 the rule with neighbour counts has less than a tenth
  of it. So neighbours are what lets movement die, and at small blocks it then dies too fast.

Surprise is the mean of -log2 of the chance a rule gave to what came next, on the starts it
did not learn from. Every number is recomputed in `decide` from the tallies in the records.

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
sys.path.insert(0, str(HERE.parent / "scale-up-compete"))

import zoom  # noqa: E402
from first_look import HIGHLIFE, LIFE, soup_rules  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

LOOK = HERE / "look" / "summary.json"
RECORDS = HERE / "records.jsonl"
CACHE = Path.home() / "lattice-lab-runs" / "closure" / "cache"
WORLDS = {
    "pair standoff": {"rules": (LIFE, HIGHLIFE), "side": 2048, "generations": 1024,
                      "blocks": (4, 8, 16, 32, 64)},
    "soup standoff": {"rules": soup_rules(19), "side": 1024, "generations": 512,
                      "blocks": (4, 8, 16, 32)},
}  # fmt: skip
PAIR, SOUP = "pair standoff", "soup standoff"
LEARN = tuple(range(8001, 8009))
TRY = tuple(range(8009, 8017))
SOUP_STARTS = tuple(range(8001, 8005))
CONTROL = {"side": 1024, "generations": 1024, "block": 4, "clock": 16, "starts": (8001, 8002)}
SPLIT = 256  # the generation that parts the early period from the late one
FROM = 128  # the generation the coarse rule is run on from
DRAWS = 2
AHEAD = 8  # coarse generations ahead, for H1
RUN_ON = (4, 8, 16, 32)  # the blocks whose rule is run on by itself
MARKS = (128, 256, 512, 1024)

# what the first look found on side 1024 (look/summary.json), and the bands registered here
REMOVED = {4: 0.3752, 8: 0.2775, 16: 0.1751, 32: 0.0957}
REMOVED_BAND = 0.02
REMOVED_AT_64 = (0.02, 0.08)
ERRORS_REMOVED = 0.02
SAME_RULE = 1.02
SAME_RULE_UP_TO = 16  # at larger blocks the early period holds too few still blocks to learn from
OTHER_RULE = 1.30
SAME_TORUS = 1.002
ONE_NEIGHBOUR = (0.006, 0.011)
ONE_NEIGHBOUR_AT_64 = (0.005, 0.012)  # wider: a block of 64 gives far fewer cases to count
KEEPS_UP = (0.7, 1.3)
ALONE_ENDS = 2.5
DIES_EARLY = 0.1
DIES_UP_TO = 8  # at larger blocks the rule with neighbour counts keeps its movement to the end


# --- the fine runs -------------------------------------------------------------------------------


def cache_path(name: str, side: int, seed: int) -> Path:
    return CACHE / f"registered-{name.replace(' ', '-')}-{side}-{seed}.npz"


def tally(symbols: np.ndarray, first: int, last: int) -> np.ndarray:
    """How often a supercell moved next, by [was it moving][moving neighbours][does it move],
    over the coarse generations from `first` up to but not including `last`."""
    counts = np.zeros(36, dtype=np.int64)
    for own, around, after in zoom.transitions(symbols, first, last):
        view = zoom.codes("total", own, around, 2)
        counts += np.bincount((view * 2 + after).ravel(), minlength=36)
    return counts.reshape(2, 9, 2)


def quiet(history: zoom.History) -> int:
    """The supercell-generations in which neither a supercell nor any neighbour had moved:
    the places where stillness could have broken."""
    moved = history.moved[1:-1]
    return int((~(moved | zoom.ring(moved).any(axis=0))).sum())


def run_start(job: tuple[str, int]) -> dict:
    """One world from one start, read through every block: its record, and the zoomed-out
    movement kept on disk for the run-on."""
    name, seed = job
    w = WORLDS[name]
    start = zoom.mixed_start(w["side"], seed, len(w["rules"]))
    found = zoom.histories(
        w["rules"], "standoff", w["side"], start, w["generations"], w["blocks"], seed=seed
    )
    blocks, kept = {}, {}
    for block, history in found.items():
        symbols, _, first = zoom.states(history, "moved")
        cut, steps = SPLIT // block, w["generations"] // block
        blocks[str(block)] = {
            "quiet": quiet(history),
            "moved_from_stillness": zoom.unstable(history),
            "tally": {
                "early": tally(symbols, first, cut).tolist(),
                "late": tally(symbols, cut, steps).tolist(),
            },
            "moving": {
                str(g): round(float(symbols[g // block].mean()), 6)
                for g in MARKS
                if g <= w["generations"]
            },
        }
        kept[f"moved_{block}"] = history.moved
    path = cache_path(name, w["side"], seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **kept)
    return {
        "kind": "start",
        "world": name,
        "side": w["side"],
        "seed": seed,
        "generations": w["generations"],
        "blocks": blocks,
    }


def run_control(seed: int) -> dict:
    """The pair read with the clock four blocks long: stillness need not hold."""
    c = CONTROL
    start = zoom.mixed_start(c["side"], seed, 2)
    found = zoom.histories(
        (LIFE, HIGHLIFE), "standoff", c["side"], start, c["generations"], (c["block"],),
        {c["block"]: c["clock"]}, seed=seed,
    )  # fmt: skip
    history = found[c["block"]]
    return {
        "kind": "control",
        "world": PAIR,
        "side": c["side"],
        "seed": seed,
        "block": c["block"],
        "clock": c["clock"],
        "quiet": quiet(history),
        "moved_from_stillness": zoom.unstable(history),
    }


# --- rules from tallies --------------------------------------------------------------------------


def rule_of(counts) -> zoom.CoarseRule:
    """The coarse rule a [was it moving][moving neighbours][does it move] tally stands for."""
    counts = np.asarray(counts, dtype=np.int64)
    tables = {
        "nothing": zoom.Table(2, np.zeros(1, dtype=np.int64), counts.sum(axis=(0, 1))[None]),
        "own": zoom.Table(2, np.arange(2), counts.sum(axis=1)),
        "total": zoom.Table(2, np.arange(18), counts.reshape(18, 2)),
        "full": zoom.Table.empty(2),
    }
    return zoom.CoarseRule(2, tables)


def chances(rule: zoom.CoarseRule, kind: str) -> np.ndarray:
    """The chance `rule` gives to each next symbol, for every [was it moving][moving
    neighbours]: a 2 x 9 x 2 array."""
    own = np.repeat(np.arange(2)[:, None], 9, axis=1)
    around = (np.arange(8)[:, None, None] < np.arange(9)[None, None, :]).astype(np.int8)
    return rule.chances(kind, own, np.broadcast_to(around, (8, 2, 9)))


def score(rule_counts, trial_counts, kind: str) -> dict:
    """How the rule a tally stands for does on the transitions of another tally: how many
    there are, how many it calls right, and its surprise in bits."""
    trial = np.asarray(trial_counts, dtype=np.int64)
    chance = chances(rule_of(rule_counts), kind)
    likeliest = chance.argmax(axis=-1)
    right = np.take_along_axis(trial, likeliest[..., None], axis=-1).sum()
    return {
        "transitions": int(trial.sum()),
        "right": int(right),
        "bits": float(-(trial * np.log2(chance)).sum()),
    }


def run_ahead(job: tuple[int, int, list]) -> dict:
    """The rule learned from the learning starts run on by itself, from generation FROM of one
    trial start at one block: the share of blocks moving at each horizon, in the fine world,
    under the rule with neighbour counts and under the rule that knows the block alone."""
    seed, block, counts = job
    w = WORLDS[PAIR]
    path = cache_path(PAIR, w["side"], seed)
    if not path.exists():
        run_start((PAIR, seed))
    with np.load(path) as kept:
        symbols = kept[f"moved_{block}"].astype(np.int8)
    rule = rule_of(counts)
    out = {}
    for name, kind in (("with_neighbours", "total"), ("alone", "own")):
        rng = np.random.default_rng([20261124, seed, block, zoom.KINDS.index(kind)])
        out[name] = zoom.follow(rule, kind, symbols, FROM // block, rng, DRAWS)
    return {
        "kind": "ahead",
        "world": PAIR,
        "side": w["side"],
        "seed": seed,
        "block": block,
        "from_generation": FROM,
        "horizon": out["alone"]["horizon"],
        "fine": [round(v, 6) for v in out["alone"]["fine"]],
        "with_neighbours": [round(v, 6) for v in out["with_neighbours"]["drawn"]],
        "alone": [round(v, 6) for v in out["alone"]["drawn"]],
        "rule_sha256": hashlib.sha256(json.dumps(counts).encode()).hexdigest(),
    }


def pooled(rows: list[dict], seeds: tuple[int, ...], block: int, periods: tuple[str, ...]) -> list:
    """The tallies of the pair's starts `seeds` at `block`, over `periods`, added up."""
    total = np.zeros((2, 9, 2), dtype=np.int64)
    for row in rows:
        if row["kind"] == "start" and row["world"] == PAIR and row["seed"] in seeds:
            for period in periods:
                total += np.asarray(row["blocks"][str(block)]["tally"][period])
    return total.tolist()


def start_jobs() -> list[tuple[str, int]]:
    return [(PAIR, seed) for seed in LEARN + TRY] + [(SOUP, seed) for seed in SOUP_STARTS]


def execute(path: Path, workers: int) -> None:
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    done = {(r["kind"], r["world"], r["seed"], r.get("block")) for r in rows}
    starts = [job for job in start_jobs() if ("start", job[0], job[1], None) not in done]
    controls = [
        seed for seed in CONTROL["starts"] if ("control", PAIR, seed, CONTROL["block"]) not in done
    ]
    with ProcessPoolExecutor(max(workers, 1)) as pool:
        for record in pool.map(run_start, starts):
            append_records(path, [record])
            rows.append(record)
        for record in pool.map(run_control, controls):
            append_records(path, [record])
            rows.append(record)
        ahead = [
            (seed, block, pooled(rows, LEARN, block, ("early", "late")))
            for seed in TRY
            for block in RUN_ON
            if ("ahead", PAIR, seed, block) not in done
        ]
        for record in pool.map(run_ahead, ahead):
            append_records(path, [record])


# --- the predictions -----------------------------------------------------------------------------


def first_look() -> dict:
    """What the first look found on side 1024: per block, its late rule's tally."""
    blocks = json.loads(LOOK.read_text())["worlds"][PAIR]["blocks"]
    return {
        int(b): found["moved"]["rule_for_movement"]["late"]["tally"] for b, found in blocks.items()
    }


def predictions() -> list[dict]:
    seen = first_look()
    out = []

    def claim(family: str, label: str, text: str, **body) -> None:
        out.append({"label": label, "family": family, "claim": text, **body})

    for name, starts in ((PAIR, len(LEARN + TRY)), (SOUP, len(SOUP_STARTS))):
        for block in WORLDS[name]["blocks"]:
            claim("S", f"S {name}, block {block}",
                  f"no block of {block} moves out of stillness in the {name.split()[0]} under "
                  f"the standoff: none of the supercells whose neighbourhood was still, over "
                  f"{starts} starts", world=name, block=block)  # fmt: skip
    claim("S", "S control",
          f"read with the clock at {CONTROL['clock']} for blocks of {CONTROL['block']}, some "
          "blocks do move out of stillness: movement reaches them from beyond their neighbours",
          world=PAIR, block=CONTROL["block"], clock=CONTROL["clock"])  # fmt: skip
    for block in WORLDS[PAIR]["blocks"]:
        if block in REMOVED:
            low, high = REMOVED[block] - REMOVED_BAND, REMOVED[block] + REMOVED_BAND
            where = f"as on side 1024, where it was {REMOVED[block]}"
        else:
            low, high = REMOVED_AT_64
            where = "a block no run has been read through: the trend of blocks 4 to 32"
        claim("N", f"N block {block}: surprise",
              f"after generation {SPLIT}, knowing how many neighbours moved removes between "
              f"{low:.4f} and {high:.4f} of the surprise of knowing the block alone ({where})",
              block=block, low=round(low, 4), high=round(high, 4))  # fmt: skip
        claim("N", f"N block {block}: errors",
              f"and removes less than {ERRORS_REMOVED:.0%} of its errors: the likeliest next "
              "symbol is still that the block stays as it is",
              block=block, below=ERRORS_REMOVED)  # fmt: skip
    for block in [b for b in WORLDS[PAIR]["blocks"] if b <= SAME_RULE_UP_TO]:
        claim("T", f"T block {block}: with neighbours",
              f"the rule with neighbour counts learned up to generation {SPLIT} has at most "
              f"{SAME_RULE - 1:.0%} more surprise after it than the rule learned after it",
              block=block, view="total", at_most=SAME_RULE)  # fmt: skip
        claim("T", f"T block {block}: alone",
              f"the rule that knows the block alone, learned up to generation {SPLIT}, has at "
              f"least {OTHER_RULE - 1:.0%} more surprise after it than the one learned after it",
              block=block, view="own", at_least=OTHER_RULE)  # fmt: skip
    for block in [b for b in WORLDS[PAIR]["blocks"] if b in seen]:
        claim("X", f"X block {block}",
              "the first look's rule with neighbour counts, learned on side 1024, has at most "
              f"{SAME_TORUS - 1:.1%} more surprise on side 2048 than the rule learned there",
              block=block, at_most=SAME_TORUS, rule_tally=seen[block])  # fmt: skip
    for block in WORLDS[PAIR]["blocks"]:
        low, high = ONE_NEIGHBOUR if block in REMOVED else ONE_NEIGHBOUR_AT_64
        claim("E", f"E block {block}",
              "a still block with exactly one moving neighbour moves next with a chance "
              f"between {low} and {high}, after generation {SPLIT}",
              block=block, low=low, high=high)  # fmt: skip
    for block in RUN_ON:
        claim("H", f"H block {block}: keeps up",
              f"run on by itself from generation {FROM}, the rule with neighbour counts has "
              f"between {KEEPS_UP[0]} and {KEEPS_UP[1]} of the fine world's moving blocks "
              f"{AHEAD} coarse generations on",
              block=block, view="with_neighbours", horizon=AHEAD, low=KEEPS_UP[0],
              high=KEEPS_UP[1])  # fmt: skip
        claim("H", f"H block {block}: alone",
              "at the end of the run the rule that knows the block alone has at least "
              f"{ALONE_ENDS} times the fine world's moving blocks: it cannot let movement die",
              block=block, view="alone", horizon="end", at_least=ALONE_ENDS)  # fmt: skip
    for block in [b for b in RUN_ON if b <= DIES_UP_TO]:
        claim("H", f"H block {block}: dies early",
              "at the end of the run the rule with neighbour counts has less than "
              f"{DIES_EARLY} of the fine world's moving blocks: its movement dies too fast",
              block=block, view="with_neighbours", horizon="end", below=DIES_EARLY)  # fmt: skip
    return out


# --- the verdict ---------------------------------------------------------------------------------


def surprise(rule_counts, trial_counts, kind: str) -> float:
    found = score(rule_counts, trial_counts, kind)
    return found["bits"] / max(found["transitions"], 1)


def decide(rows: list[dict], registered: list[dict]) -> dict:
    starts = {(r["world"], r["seed"]): r for r in rows if r["kind"] == "start"}
    controls = [r for r in rows if r["kind"] == "control"]
    ahead: dict[int, list[dict]] = {}
    for r in rows:
        if r["kind"] == "ahead":
            ahead.setdefault(r["block"], []).append(r)
    missing = [f"{name} from start {seed}" for name, seed in start_jobs()
               if (name, seed) not in starts]  # fmt: skip
    if {r["seed"] for r in controls} != set(CONTROL["starts"]):
        missing.append("the control")
    for block in RUN_ON:
        if sorted(r["seed"] for r in ahead.get(block, [])) != list(TRY):
            missing.append(f"the run-on at block {block}")
    outcomes, measured = {}, {}
    if missing:
        outcomes = {claim["label"]: "missing" for claim in registered}
    else:
        pair = [r for (name, _), r in starts.items() if name == PAIR]
        for claim in registered:
            label, family, block = claim["label"], claim["family"], claim.get("block")
            if family == "S" and "clock" in claim:
                broke = sum(r["moved_from_stillness"] for r in controls)
                tried = sum(r["quiet"] for r in controls)
                holds, found = broke > 0, {"moved_from_stillness": broke, "of": tried}
            elif family == "S":
                mine = [r["blocks"][str(block)] for (name, _), r in starts.items()
                        if name == claim["world"]]  # fmt: skip
                broke = sum(b["moved_from_stillness"] for b in mine)
                tried = sum(b["quiet"] for b in mine)
                holds, found = (
                    broke == 0 and tried > 0,
                    {"moved_from_stillness": broke, "of": tried},
                )
            elif family in ("N", "T", "X"):
                late = pooled(pair, LEARN, block, ("late",))
                early = pooled(pair, LEARN, block, ("early",))
                trial = pooled(pair, TRY, block, ("late",))
                if family == "N" and "low" in claim:
                    value = 1 - surprise(late, trial, "total") / surprise(late, trial, "own")
                    holds = claim["low"] <= value <= claim["high"]
                elif family == "N":
                    own, total = score(late, trial, "own"), score(late, trial, "total")
                    wrong = own["transitions"] - own["right"]
                    value = 1 - (total["transitions"] - total["right"]) / max(wrong, 1)
                    holds = value < claim["below"]
                elif family == "T":
                    view = claim["view"]
                    value = surprise(early, trial, view) / surprise(late, trial, view)
                    holds = value <= claim["at_most"] if "at_most" in claim else (
                        value >= claim["at_least"])  # fmt: skip
                else:
                    value = surprise(claim["rule_tally"], trial, "total") / surprise(
                        late, trial, "total")  # fmt: skip
                    holds = value <= claim["at_most"]
                found = {"measured": round(float(value), 5)}
            elif family == "E":
                every = np.asarray(pooled(pair, LEARN + TRY, block, ("late",)))
                value = float(every[0, 1, 1] / max(every[0, 1].sum(), 1))
                holds = claim["low"] <= value <= claim["high"]
                found = {"measured": round(value, 5), "of": int(every[0, 1].sum())}
            else:
                mine = ahead[block]
                at = -1 if claim["horizon"] == "end" else mine[0]["horizon"].index(claim["horizon"])
                fine = float(np.mean([r["fine"][at] for r in mine]))
                coarse = float(np.mean([r[claim["view"]][at] for r in mine]))
                value = coarse / fine if fine > 0 else float("inf")
                if "at_least" in claim:
                    holds = value >= claim["at_least"]
                elif "below" in claim:
                    holds = value < claim["below"]
                else:
                    holds = claim["low"] <= value <= claim["high"]
                found = {"measured": round(value, 4), "fine": round(fine, 6),
                         "coarse": round(coarse, 6),
                         "generation": FROM + mine[0]["horizon"][at] * block}  # fmt: skip
            outcomes[label] = "holds" if holds else "fails"
            measured[label] = found

    def overall(family: str) -> str:
        found = {outcomes[c["label"]] for c in registered if c["family"] == family}
        for word in ("missing", "fails"):
            if word in found:
                return word
        return "holds"

    families = sorted({c["family"] for c in registered})
    reported = {}
    if not missing:
        pair = [r for (name, _), r in starts.items() if name == PAIR]
        for block in WORLDS[PAIR]["blocks"]:
            late = np.asarray(pooled(pair, LEARN + TRY, block, ("late",)), dtype=float)
            with np.errstate(invalid="ignore", divide="ignore"):
                chance = late[..., 1] / late.sum(axis=-1)
            reported[str(block)] = {
                "moves_next_after_still": [None if np.isnan(v) else round(float(v), 5)
                                           for v in chance[0]],
                "moves_next_after_moved": [None if np.isnan(v) else round(float(v), 5)
                                           for v in chance[1]],
                "moving": {g: round(float(np.mean([r["blocks"][str(block)]["moving"][g]
                                                   for r in pair])), 6)
                           for g in pair[0]["blocks"][str(block)]["moving"]},
            }  # fmt: skip
    return {
        "verdict": {family: overall(family) for family in families},
        "outcomes": outcomes,
        "measured": measured,
        "missing": missing,
        "rule_for_movement": reported,
    }


def question() -> dict:
    return {
        "id": "scale-up-closure",
        "title": "Does a coarse rule for movement stand in for the fine world?",
        "statement": "Life against HighLife under the standoff is read through blocks with the "
        "clock at the block, and a supercell records whether its block moved. On a torus twice "
        "as wide as the first look's, from fresh starts and at blocks up to twice as large: "
        "stillness is stable (S); the neighbours sharpen the odds without changing the best "
        "guess (N); the rule with neighbour counts is the same rule early and late, and the "
        "rule without them is not (T); the rule learned on the smaller torus serves on the "
        "larger (X); one of its chances is the same at every block (E); and run on by itself "
        "it keeps up with the fine world for eight coarse generations and then loses it (H).",
        "source": "docs/scale-up-plan.md, step 4; the first look in examples/scale-up-closure",
        "worlds": {
            name: {
                "rules": list(w["rules"]),
                "tie_break": "standoff",
                "side": w["side"],
                "generations": w["generations"],
                "blocks": list(w["blocks"]),
            }
            for name, w in WORLDS.items()
        },  # fmt: skip
        "starts": {
            "learned_from": [LEARN[0], LEARN[-1]],
            "tried_on": [TRY[0], TRY[-1]],
            "soup": [SOUP_STARTS[0], SOUP_STARTS[-1]],
        },  # fmt: skip
        "control": {**CONTROL, "starts": list(CONTROL["starts"])},
        "runs": len(start_jobs()) + len(CONTROL["starts"]) + len(TRY) * len(RUN_ON),
        "clock": "the block",
        "periods": {"early": [0, SPLIT], "late": [SPLIT, 1024]},
        "run_on": {"from_generation": FROM, "draws": DRAWS, "blocks": list(RUN_ON)},
        "sha256": {
            "study.py": hashlib.sha256((HERE / "study.py").read_bytes()).hexdigest(),
            "zoom.py": hashlib.sha256((HERE / "zoom.py").read_bytes()).hexdigest(),
            "look/summary.json": hashlib.sha256(LOOK.read_bytes()).hexdigest(),
        },
        "excluded_seen": [
            "The first look (look.py, exploratory): the pair on side 1024 and soup 19 on side "
            "512, from starts 7001 to 7016, read through blocks of 4 to 32. Every number "
            "predicted here comes from it, and its late rule is the one tried in X.",
            "The instrument's tests: the pair and soups on sides 32 to 128 from starts 9001 on.",
            "The earlier studies of this world (starts 101 to 228, 2001 to 2032, 3001 to 3032, "
            "4001 to 4016, 5001 to 5016, 6001 to 6384), none of them read through blocks.",
            "Nothing has been read through blocks on side 2048, or through blocks of 64 on any "
            "side, and no start from 8001 on has been generated or run.",
        ],
    }


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`). A run-on is computed from
    the learning starts' tallies as the records file holds them."""
    if record["kind"] == "start":
        return run_start((record["world"], record["seed"]))
    if record["kind"] == "control":
        return run_control(record["seed"])
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    counts = pooled(rows, LEARN, record["block"], ("early", "late"))
    return run_ahead((record["seed"], record["block"], counts))


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
