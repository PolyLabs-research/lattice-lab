"""
Three readings made after the verdict of the registered test of this folder. Exploratory:
nothing here was registered.

    uv run --no-sync python examples/scale-up-class-memory/extras.py

**What marks the worlds where a block's past matters?** The registered test groups its
worlds by what step 4f found of each, and step 4f took the class to be marked by how full a
world is. This sets three things a world could be told by beside what the test measured,
over all the worlds that have a clock, and asks which of them goes with it:

- how full it is (the share of its grid live at generation 4,096);
- how often its blocks change hands whatever their past: the chance that a block which has
  had its leader for 16 ticks or more, with three of its eight neighbours under the rival
  (so beside a nearly flat wall), has another leader one tick on;
- how much a young lead differs from an old one: at four rival neighbours, the chance for a
  block that has had its leader one tick over the chance for one that has had it 16 or more.

That part is read from the verdict in ledger.jsonl (what `study.told` says of each world).

**Is a missed world's table the look's table with one more number?** In the worlds step 4f
missed, a block changes hands whatever its past. So the look's plain rule is given one
number more, fitted on the starts a world learns from and scored on the starts it is tried
on, as the world's own rule is:

- *a neighbour's leader:* with a chance e the block takes the leader of one of its eight
  neighbours, picked at random; otherwise it does as the look's rule says;
- *the rule taken several times:* the look's rule taken k times in a tick as if nothing
  around the block moved (its chance of keeping its leader raised to the power k). This is
  the nearest thing to a pace within the tick, set beside the first for contrast;
- and both together.

**How much of "with how long in view it serves" is the yardstick?** The registered test
sets the look's rule beside a world's own rule learned from two starts. A rule with more in
view has more to learn, so a world's own remembering rule is the further from what it would
be with endless data, and the look's remembering rule, which learned from sixteen times as
much, is flattered beside it: in the still world itself it comes out better than the still
world's own. Here the own rule's surprise is told as it would be with endless data (twice
its surprise having learned from both starts, less its mean surprise having learned from
one: the 1/N rule of step 4h, which under-corrects a little), and the look's rules are set
beside that.

The last two parts are read from the tallies in records.jsonl. The summary of all three
goes to extras.json.
"""

from __future__ import annotations

import importlib.util
import json
import sys
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


study = _module("scale_up_class_memory_study", HERE / "study.py")
look, ladder = study.look, study.ladder

OUT = HERE / "extras.json"
PLAIN = look.PLAIN
CHANCES = np.round(np.arange(0.0, 0.801, 0.005), 3)  # the values tried for e
TIMES = np.round(np.arange(0.4, 8.01, 0.1), 1)  # and for k
NEIGHBOUR, TAKEN, BOTH = "a neighbour's leader", "the rule taken several times", "both"
TABLE = "chance of another leader one tick on, at 3, 4 and 5 rival neighbours"
OLD, NEW = "a lead of 16 ticks or more", "a lead of one tick"
FULL, FLICKER, YOUNG = "live", "an old lead beside a flat wall", "a young lead over an old one"
MISSED, REMOVED, GAIN = "missed in step 4f", "how long removes", "remembering over plain"
SERVE = "the look's rule as it is, more surprise"


def read(told: dict, world: dict) -> dict | None:
    """One world's numbers, from what the verdict says of it. None if it has no clock."""
    if told.get("tick") is None or not told["stands"]:
        return None
    table = told[TABLE]
    old, new = table[OLD], table[NEW]
    return {
        "group": told["group"],
        MISSED: world.get(study.MISSED),
        FULL: told["live at generation 4,096"],
        FLICKER: old[0],
        YOUNG: None if not old[1] or new[1] is None else round(new[1] / old[1], 3),
        REMOVED: told["share of the plain rule's surprise that how long removes"],
        SERVE: told["the look's rule, more surprise"][study.PLAIN],
        GAIN: told["blocks amiss, the look's remembering rule over its plain one"],
    }


def ranks(worlds: dict, first: str, second: str) -> dict:
    """The rank correlation of two of the numbers over the worlds that have both."""
    both = [(w[first], w[second]) for w in worlds.values()
            if w[first] is not None and w[second] is not None]  # fmt: skip
    found = study.rank_correlation([a for a, _ in both], [b for _, b in both])
    return {"worlds": len(both), "rank correlation": None if found is None else round(found, 3)}


def apart(worlds: dict, what: str) -> dict:
    """Does a number tell the worlds step 4f found served from those it found missed? Its
    range in each group, and whether the two ranges stand clear of each other."""
    spans = {}
    for group in (study.SERVED, study.NEAR, study.JUST, study.FAR):
        values = [w[what] for w in worlds.values() if w["group"] == group and w[what] is not None]
        spans[group] = [min(values), max(values)] if values else None
    served, missed = spans[study.SERVED], spans[study.FAR]
    clear = None
    if served and missed:
        clear = bool(served[1] < missed[0] or missed[1] < served[0])
    return {"range by group": spans, "served and missed stand clear": clear}


def summary(verdict: dict, chosen: dict) -> dict:
    worlds = {}
    for rule, told in verdict["worlds"].items():
        if rule == study.STILL:
            continue
        found = read(told, chosen[rule])
        if found is not None:
            worlds[rule] = found
    marks = (FULL, FLICKER, YOUNG)
    return {
        "what": "read after the verdict (extras.py, exploratory): over the worlds with a "
                "clock, three things a world could be told by, set beside what the "
                "registered test measured of it",
        "the still world": read(verdict["worlds"][study.STILL], {}),
        "worlds": worlds,
        "do they tell served from missed": {what: apart(worlds, what) for what in marks},
        "rank correlations": {
            f"{mark}, against {measured}": ranks(worlds, mark, measured)
            for mark in marks for measured in (MISSED, REMOVED, SERVE, GAIN)},
    }  # fmt: skip


# --- one more number -----------------------------------------------------------------------------


def neighbours() -> np.ndarray:
    """[leader][neighbours species 1 leads][neighbours species 2 leads][next leader]: the
    chance that one of a block's eight neighbours, picked at random, is led by `next` (0
    for nobody)."""
    first, second = np.meshgrid(np.arange(9), np.arange(9), indexing="ij")
    nobody = 8 - first - second
    counts = np.stack([nobody, first, second], axis=-1).astype(float)
    counts[nobody < 0] = 0.0  # a block has eight neighbours: no such view
    share = counts / np.maximum(counts.sum(axis=-1, keepdims=True), 1.0)
    return np.broadcast_to(share, (3, 9, 9, 3)).copy()


def taken(chances: np.ndarray, times: float) -> np.ndarray:
    """A rule taken `times` times in a tick as if nothing around the block moved: its chance
    of keeping its leader raised to that power, and the rest shared out as before."""
    out = chances.copy()
    for leader in range(3):
        stay = chances[leader, :, :, leader]
        kept = stay**times
        scale = np.where(stay < 1, (1 - kept) / np.maximum(1 - stay, 1e-12), 0.0)
        for after in range(3):
            out[leader, :, :, after] = (
                kept if after == leader else chances[leader, :, :, after] * scale
            )
    return out


def bits(chances: np.ndarray, trial: np.ndarray) -> float:
    """The bits a transition of a plain tally costs a table of chances, on average."""
    return float(-(trial * np.log2(np.maximum(chances, 1e-12))).sum() / max(trial.sum(), 1))


def families(base: np.ndarray) -> dict:
    """Each family as the numbers it may take and the table each gives."""
    around = neighbours()
    powers = {k: taken(base, k) for k in TIMES}
    return {
        NEIGHBOUR: ([(e,) for e in CHANCES], lambda e: (1 - e) * base + e * around),
        TAKEN: ([(k,) for k in TIMES], lambda k: powers[k]),
        BOTH: ([(k, e) for k in TIMES for e in CHANCES[::2]],
               lambda k, e: (1 - e) * powers[k] + e * around),
    }  # fmt: skip


def one_more_number(rows: list[dict], plan: dict, chosen: dict, lent: np.ndarray) -> dict:
    """For each world with a clock: how much more surprise the look's plain rule has than
    the world's own on its trial starts, as it is and with each family's number fitted on
    the starts the world learns from."""
    base = PLAIN.chances(PLAIN.of(lent))[0]
    tried = families(base)
    out = {}
    for world in plan:
        learn = PLAIN.of(study.pooled(rows, world, plan[world]["learn"]))
        trial = PLAIN.of(study.pooled(rows, world, plan[world]["try"]))
        if not learn.sum() or not trial.sum():
            continue
        own = bits(PLAIN.chances(learn)[0], trial[0])
        as_it_is = look.surprise(PLAIN, ladder.as_much(PLAIN.of(lent), learn), trial) / own - 1
        found = {"group": chosen[world]["group"], "the look's rule as it is": round(as_it_is, 4)}
        for name, (values, table) in tried.items():
            best = min(values, key=lambda v, t=table: bits(t(*v), learn[0]))
            more = bits(table(*best), trial[0]) / own - 1
            found[name] = {"fitted": [float(v) for v in best], "more surprise": round(more, 4)}
        out[world] = found
    return out


# --- the yardstick -------------------------------------------------------------------------------


def with_endless_data(rows: list[dict], plan: dict, chosen: dict, lent: np.ndarray) -> dict:
    """For each world with a clock and each reading: how much more surprise the look's rule
    has on the world's trial starts than the world's own rule, as registered (the own rule
    learned from both of its starts) and beside the own rule as it would be with endless
    data; and the share of the plain rule's surprise that how long removes, both ways."""
    out = {}
    for world in plan:
        first, second = plan[world]["learn"]
        trial = study.pooled(rows, world, plan[world]["try"])
        both = study.pooled(rows, world, [first, second])
        halves = [study.pooled(rows, world, [seed]) for seed in (first, second)]
        if not trial.sum() or not all(half.sum() for half in halves):
            continue
        found: dict = {"group": chosen[world]["group"]}
        endless = {}
        for name, sees in study.READINGS.items():
            learned = look.surprise(sees, both, trial)
            from_one = float(np.mean([look.surprise(sees, half, trial) for half in halves]))
            endless[name] = (learned, 2 * learned - from_one)
            lends = look.surprise(sees, ladder.as_much(sees.of(lent), sees.of(both)), trial)
            found[name] = {"as registered": round(lends / learned - 1, 4),
                           "beside its own with endless data": round(
                               lends / endless[name][1] - 1, 4)}  # fmt: skip
        found["how long removes"] = {
            "as registered": round(1 - endless[study.HOW][0] / endless[study.PLAIN][0], 4),
            "with endless data": round(1 - endless[study.HOW][1] / endless[study.PLAIN][1], 4),
        }  # fmt: skip
        out[world] = found
    return out


def served(worlds: dict, how: str) -> dict:
    """How many worlds each of the look's rules serves within the study's bar, by group."""
    out: dict = {}
    for found in worlds.values():
        for name in study.READINGS:
            cell = out.setdefault(name, {}).setdefault(found["group"], [0, 0])
            cell[0] += int(found[name][how] <= study.SERVES)
            cell[1] += 1
    return out


def main() -> None:
    entries = [json.loads(line) for line in (HERE / "ledger.jsonl").read_text().splitlines()]
    verdict = next(e["body"] for e in entries if e["kind"] == "verdict")
    chosen = study.worlds()
    found = summary(verdict, chosen)
    rows = [json.loads(line) for line in study.RECORDS.read_text().splitlines()]
    found["one more number"] = {
        "what": "the look's plain rule with one number more (or two), fitted on the starts a "
                "world learns from: how much more surprise it has on the world's trial starts "
                "than the world's own plain rule. `fitted` is e for a neighbour's leader, k "
                "for the rule taken several times, and [k, e] for both",
        "worlds": one_more_number(rows, study.design(), chosen, study.looks_rule()),
    }  # fmt: skip
    beside = with_endless_data(rows, study.design(), chosen, study.looks_rule())
    found["the yardstick"] = {
        "what": "the look's rule beside a world's own, one tick ahead: more surprise as "
                "registered (the own rule learned from two starts), and beside the own rule "
                "as it would be with endless data (the 1/N rule); and the worlds each of "
                "the look's rules serves within the study's bar, each way, by group as "
                "[served, of]",
        "worlds": beside,
        "served, as registered": served(beside, "as registered"),
        "served, beside its own with endless data": served(
            beside, "beside its own with endless data"),
    }  # fmt: skip
    OUT.write_text(json.dumps(found, indent=1) + "\n")
    for name, part in found["do they tell served from missed"].items():
        print(name, json.dumps(part))
    for name, part in found["rank correlations"].items():
        print(name, json.dumps(part))
    for world, part in found["one more number"]["worlds"].items():
        print(world, json.dumps(part))
    for world, part in beside.items():
        print(world, json.dumps(part))
    for name in ("served, as registered", "served, beside its own with endless data"):
        print(name, json.dumps(found["the yardstick"][name]))


if __name__ == "__main__":
    main()
