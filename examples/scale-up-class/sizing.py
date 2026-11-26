"""
Sizing for the registered test of how wide the class is. Exploratory: nothing is registered,
and nothing is run.

    uv run --no-sync python examples/scale-up-class/sizing.py

Two things are done here before the test is registered, both from runs that exist.

- **The worlds are chosen** (`study.select`, from step 4c's registered records) and written
  to worlds.json, with how many rules of step 4c's even draw each band stands for.
- **The bounds are sized on the six worlds step 4e ran** (examples/scale-up-closure-
  territories: its registered records). For each: the power of time its walls thin by, start
  by start; how much more surprise the still world's rule has there than its own, at the
  paces step 4e kept it at; its pace by its walls; and what step 4e's run-ons measured. And
  for the pace two ways, which step 4e could only read at paces a factor of two apart, the
  first look's still world is read again from its kept runs at blocks of 16 at the eleven
  paces of this study, and the pace at which that rule serves each of step 4e's worlds best
  is set beside the pace its walls give.

The summary goes to sizing.json, which the registration carries.
"""

from __future__ import annotations

import importlib.util
import json
import math
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


study = _module("scale_up_class_study", HERE / "study.py")
ladder = study.ladder
before = _module("scale_up_closure_territories_study", study.STEP_4E / "study.py")
look = _module("scale_up_closure_territories_look", study.STEP_4E / "look.py")

KNOWN = ("still", "busy", "near", "another", "sparse", "set")


def still_at_every_pace(block: int = 16) -> dict[float, np.ndarray]:
    """The first look's still world at one block, at every pace this study keeps a rule at:
    the tally of its eight kept runs over the whole run."""
    out = {ratio: np.zeros((ladder.Q, 9, 9, ladder.Q), dtype=np.int64) for ratio in study.RATIOS}
    for seed in (*look.LEARN, *look.TRY):
        frames = look.LEADER[look.load("still", seed, look.SIDE, look.GENERATIONS)[block]]
        for ratio in study.RATIOS:
            for first, last in ladder.WINDOWS.values():
                out[ratio] += ladder.tally(frames, block, int(ratio * ladder.square(block)),
                                           first, last)  # fmt: skip
    return out


def known() -> dict:
    """Step 4e's six worlds through this study's measures, as far as its records reach."""
    rows = [json.loads(line) for line in before.RECORDS.read_text().splitlines()]
    plan = before.design()
    m = before.Measures(rows, plan, before.reference())
    entries = [json.loads(line) for line in (study.STEP_4E / "ledger.jsonl").read_text()
               .splitlines()]  # fmt: skip
    verdict = next(e["body"] for e in entries if e["kind"] == "verdict")
    extras = json.loads((study.STEP_4E / "extras.json").read_text())
    fine = still_at_every_pace(16)
    first, last = (str(g) for g in ladder.WINDOWS["C"])
    out: dict = {}
    for world in KNOWN:
        records = [r for r in rows if r["kind"] == "start" and r["world"] == world]
        powers = [-math.log(r["walls"]["8"][last] / r["walls"]["8"][first]) / math.log(4)
                  for r in records]  # fmt: skip
        held = [r["larger"][last] / r["live"][last] for r in records]

        def walls(name, generation):
            mine = [r for r in rows if r["kind"] == "start" and r["world"] == name]
            return float(np.mean([r["walls"]["8"][generation] for r in mine]))

        pace = math.sqrt(math.prod((walls("still", g) / walls(world, g)) ** 2
                                   for g in (first, last)))  # fmt: skip
        coarse = {tick / ladder.square(8): m.from_elsewhere(world, "still", 8, tick)
                  for tick in ladder.TICKS[8]}  # fmt: skip
        here, trial = m.own(world, 16)
        by_pace = {ratio: ladder.excess(fine[ratio], here, trial) for ratio in study.RATIOS}
        rule_pace = study.vertex(by_pace)
        told = {
            "rule": before.WORLDS[world]["rule"],
            "walls thin as time to the power, blocks of 8": {
                "the mean over its starts": round(float(np.mean(powers)), 3),
                "least and most of one start": [round(min(powers), 3), round(max(powers), 3)],
            },
            "larger species' share of the live, most of one start": round(max(held), 3),
            "walls at blocks of 8, generation 1,024": round(walls(world, first), 4),
            "more surprise than its own rule at blocks of 8, by pace (step 4e's paces)": {
                str(ratio): round(value, 5) for ratio, value in coarse.items()},
            "least of those": round(min(coarse.values()), 5),
            "pace by its walls": round(pace, 3),
            "more surprise at blocks of 16, by pace (this study's paces)": {
                str(ratio): round(value, 5) for ratio, value in by_pace.items()},
            "pace by the rule, blocks of 16": round(rule_pace, 3),
            "the two paces apart by a factor of": round(max(rule_pace / pace, pace / rule_pace), 3),
            "run on at blocks of 8, amiss over changed": {
                "its own rule": verdict["measured"].get(
                    f"C {world}, block 8: where", {}).get("value"),
                "the still world's rule, as it is": verdict["measured"].get(
                    f"U {world}, block 8: run on", verdict["measured"].get(
                        f"B the still world's rule runs the {world} world on, block 8", {})
                ).get("value"),
                "the still world's rule, at half its pace": extras.get(world, {}).get(
                    "blocks", {}).get("8", {}).get("run on, at its best pace", {}).get(
                    "amiss over changed"),
            },
        }  # fmt: skip
        out[world] = told
    return out


def main() -> None:
    chosen = study.select()
    study.WORLDS.write_text(json.dumps({
        "what": "the worlds of the registered test, chosen by study.select from the registered "
                "records of examples/scale-up-territories: every rule that grew territories "
                "against its copy under the standoff from a full start and filled the grid "
                "(nine tenths or more of it live at the end), and of the 600 rules of the even "
                "draw a share of those that did not, band by band of how much was live, the "
                "first drawn first. `first` is the first of a world's four starts",
        "of the even draw's rules that grow territories, each band stands for": study.population(),
        "worlds": chosen,
    }, indent=1) + "\n")  # fmt: skip
    found = known()
    bounds = {
        "A, the clock": {
            "square root": study.SQUARE_ROOT, "another clock": study.ANOTHER_CLOCK,
            "serves": study.SERVES, "does not": study.DOES_NOT,
            "drawn from": "the powers of step 4e's worlds: four at 0.46 to 0.49 that the "
            "still world's rule serves within 0.7% at some pace, one at 0.27 that it does not "
            "serve within 59%, and the control at 0 that it does not serve within 119%. The "
            "least and the most of one start are 0.40 and 0.55 for the four, 0.21 and 0.31 "
            "for the fifth; this study reads four starts a world.",
        },
        "F, a filling world's clock": {
            "has set": study.HAS_SET, "square root": study.SQUARE_ROOT,
            "drawn from": "the filling worlds step 4e ran: the still world, its near relative "
            "and the other still world thin their walls as the 0.46th to 0.49th power of "
            "time, and the control, which fills as they do, as the 0.00th. That is four "
            "worlds. A fifth that the search followed on a large grid by another measure "
            "(B03458/S035678) started late and had not come to a steady clock by generation "
            "2,048; it has not been read this way, and it is the kind of world that could "
            "fall between.",
        },
        "P, the pace two ways": {
            "within a factor of": study.PACE_AGREES,
            "drawn from": "the still world's rule at this study's eleven paces, at blocks of "
            "16, in the busy, the near and the other still world: the pace by the rule is "
            "0.95, 1.28 and 1.05 of the pace by the walls. Blocks of 8 could not be read at "
            "these paces from runs that exist.",
        },
        "K, run on at its walls' pace": {
            "at most": study.WHERE,
            "drawn from": "step 4e's run-ons at blocks of 8 with the still world's rule: 0.37 "
            "in the busy world and 0.55 in the near one as it is (their paces by their walls "
            "are 1.09 and 0.73), 0.75 in the other still world as it is and 0.57 at half its "
            "pace (0.54 by its walls); each world's own rule gives 0.36, 0.58 and 0.61.",
        },
        "X, the anchor": {
            "at most": study.SAME_RULE,
            "drawn from": "step 4e's own anchor: the first look's rule was within 0.03% of a "
            "rule learned from fresh starts, against bounds of 0.3% and 0.5%.",
        },
        "what a claim stands on": {
            "two species hold ground": study.HOLDS_GROUND, "a block fits": study.BLOCK_FITS,
            "a pace within reach": list(study.REACH),
            "drawn from": "in step 4e's worlds the larger species has 0.52 to 0.55 of the "
            "live cells at the end, 0.64 at most in one start; a block of 8 fits where at "
            "most a fifth of neighbouring blocks differ at generation 1,024, as in step 4e "
            "(0.09 to 0.12 in the four worlds served, 0.22 in the sparse one, 0.26 in the "
            "control). The paces a rule is kept at run from a quarter to four times the still "
            "world's, so a pace by the walls under 0.2 or over 5 is one no rule here is near.",
        },
    }  # fmt: skip
    summary = {"what the bounds were drawn from": bounds, "step 4e's worlds": found}
    study.SIZING.write_text(json.dumps(summary, indent=1) + "\n")
    print(len(chosen), "worlds;", study.population())
    for w in chosen:
        print(" ", w)
    for world, told in found.items():
        print(world, {k: v for k, v in told.items() if "by pace" not in k})


if __name__ == "__main__":
    main()
