"""
Sizing for the registered test of the next rung. Exploratory: nothing is registered, and
nothing is run.

    uv run --no-sync python examples/scale-up-rung/sizing.py

The registered test (study.py) reads two worlds at four rungs, each at the age that matches
its block. Three of those rungs can be read already, from the first look's kept runs (side
1,024, generations 64 to 4,096, starts 15001 to 15008): blocks of 4 over 64 to 256, of 8 over
256 to 1,024, of 16 over 1,024 to 4,096. Here they are read as the study will read them, the
rule from each rung below is run on at the rung above, and the bounds for the fourth rung are
drawn from what the three give. Step 4e's registered records add the walls at blocks of 32
at generation 4,096, which is where the fourth rung starts.

The summary goes to sizing.json, which the registration carries.
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


study = _module("scale_up_rung_study", HERE / "study.py")
ladder = study.ladder
look = _module("scale_up_closure_territories_look", study.STEP_4E / "look.py")

RUNGS = (4, 8, 16)  # the rungs the first look's runs reach at their matched ages


def known(world: str) -> dict:
    """One world's first three rungs at matched ages, from the first look's kept runs."""
    runs = {seed: {b: look.LEADER[look.load(world, seed, look.SIDE, look.GENERATIONS)[b]]
                   for b in RUNGS} for seed in (*look.LEARN, *look.TRY)}  # fmt: skip

    def rule(block: int, seeds) -> np.ndarray:
        return sum(ladder.tally(runs[s][block], block, ladder.square(block), *study.AGES[block])
                   for s in seeds)  # fmt: skip

    out: dict = {"rungs": {}}
    for block in RUNGS:
        first, last = study.AGES[block]
        rung: dict = {
            "matched age": [first, last],
            "walls at its start and its end": [
                round(float(np.mean([ladder.walls(runs[s][block][g // block]) for s in runs])), 4)
                for g in (first, last)],
            "chance of changing hands at five rival neighbours": round(
                ladder.changes(rule(block, list(runs)), 5), 4),
        }  # fmt: skip
        if block > RUNGS[0]:
            own, below = rule(block, look.LEARN), rule(block // 2, look.LEARN)
            rung["gap: the rule from the rung below, more surprise"] = round(ladder.excess(
                ladder.as_much(below, own), own, rule(block, look.TRY)), 5)  # fmt: skip
            ends = {}
            for whose, counts in ((study.OWN, own), (study.BELOW, below)):
                found = [ladder.ahead(runs[s][block], counts, block, ladder.square(block),
                                      (s, block, (study.OWN, study.BELOW).index(whose)),
                                      first, last) for s in look.TRY]  # fmt: skip
                ends[whose] = {what: float(np.mean([f[what][-1] for f in found]))
                               for what in ("apart_rule", "apart_start", "walls_rule",
                                            "walls_world")}  # fmt: skip
            rung["run on, amiss over changed"] = {
                whose: round(e["apart_rule"] / e["apart_start"], 4) for whose, e in ends.items()
            }
            rung["run on, walls kept"] = {
                whose: round(e["walls_rule"] / e["walls_world"], 4) for whose, e in ends.items()
            }
            rung["amiss, the rule from below over the rung's own"] = round(
                ends[study.BELOW]["apart_rule"] / ends[study.OWN]["apart_rule"], 4
            )
        out["rungs"][str(block)] = rung
    five = [out["rungs"][str(b)]["chance of changing hands at five rival neighbours"]
            for b in RUNGS]  # fmt: skip
    out["chance at five, each rung over the one below"] = [
        round(b / a, 3) for a, b in zip(five, five[1:], strict=False)
    ]
    # where the fourth rung starts: blocks of 32 at generation 4,096, from step 4e's records
    rows = [json.loads(line) for line in study.BEFORE.read_text().splitlines()]
    mine = [r for r in rows if r["kind"] == "start" and r["world"] == world]
    out["walls at blocks of 32, generation 4,096 (step 4e, side 1,024)"] = round(
        float(np.mean([r["walls"]["32"]["4096"] for r in mine])), 4
    )
    return out


def main() -> None:
    found = {world: known(world) for world in study.WORLDS}
    bounds = {
        "S, the same picture": {
            "within": study.SAME_PICTURE,
            "drawn from": "the walls at the start of each rung's matched age on side 1,024, in "
            "the first look's runs and step 4e's: 0.167, 0.175 and 0.170 at blocks of 8, 16 "
            "and 32 in the still world, 0.164, 0.162 and 0.166 in the busy one. They are "
            "within 5% of each other.",
        },
        "X, another grid": {
            "at most": study.SAME_GRID,
            "drawn from": "step 4e's anchor: the first look's rule on fresh starts was within "
            "0.03% of a rule learned from them. The grid here is twice as wide, and step 4's "
            "pair gave 0.02% across that step.",
        },
        "G, the gap": {
            "at blocks of 16": list(study.GAP_AT_16),
            "drawn from": "the gap at blocks of 16 at matched ages: 2.6% and 2.5% in the first "
            "look's runs, and by step 4e's registered ratio about 2.6% and 3.4% on its fresh "
            "starts. At blocks of 8 it was 8.7% and 5.7%. What it is at blocks of 32 nobody "
            "has seen: the claim there is only that it is smaller than at 16.",
        },
        "H, the chances": {
            "at least": study.LEVELS,
            "drawn from": "the chance of changing hands at five rival neighbours at matched "
            "ages: 0.310, 0.238, 0.200 at blocks of 4, 8, 16 in the still world (each 0.77 and "
            "0.84 of the one before), 0.296, 0.257, 0.224 in the busy one (0.87 and 0.87).",
        },
        "C, the new rung": {
            "amiss over changed, at most": study.WHERE, "walls kept": list(study.WALLS),
            "drawn from": "a rung's own rule, learned at its matched age and run on over it: "
            "0.62 and 0.53 of the changed blocks amiss at blocks of 8 and 16 in the still "
            "world, 0.51 and 0.50 in the busy one; 0.83 to 0.91 of the walls kept. With other "
            "draws these move by 0.02 or so.",
        },
        "L, the ladder's own test": {
            "amiss over changed, at most": study.BELOW_WHERE,
            "over the rung's own, at most": study.BELOW_OVER_OWN,
            "drawn from": "the rule of the rung below run on at the rung above: 0.72 and 0.62 "
            "of the changed blocks amiss at blocks of 8 and 16 in the still world (1.16 and "
            "1.18 times the rung's own rule), 0.54 and 0.53 in the busy one (1.05 and 1.07). "
            "With other draws the still world's gave 0.75 and 0.63 (1.25 and 1.16 times).",
        },
    }  # fmt: skip
    study.SIZING.write_text(json.dumps(
        {"what the bounds were drawn from": bounds, "the first three rungs": found},
        indent=1) + "\n")  # fmt: skip
    print(json.dumps(found, indent=1))


if __name__ == "__main__":
    main()
