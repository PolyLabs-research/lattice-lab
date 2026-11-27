"""
Sizing for the registered test of a coarse rule that remembers. Exploratory: nothing is
registered, and no world is run.

    uv run --no-sync python examples/scale-up-memory/sizing.py

Two things are done here before the test is registered, both from runs that exist.

- **The look's rules are written down** (reference.json): for each world, at blocks of 8 and
  16, the tally of all eight of step 4g's starts on side 2,048 over the block's matched age,
  by how long a block has had its leader. The registered test tries them, unchanged, on its
  fresh starts.
- **The bounds are sized on seen runs of the test's own size.** Step 4d's first look kept
  the leaders of its sixteen runs (the two worlds on side 1,024 to generation 4,096, starts
  15001 to 15008). They are put through the study's own measures here, every claim of it,
  with four starts to learn from and four to try on, both ways round. That is half of what
  the registered run will have, on a grid and from starts the look did not use: so it is
  also the look repeated once, on runs I had seen.

The summary goes to sizing.json, which the registration carries.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold several study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


study = _module("scale_up_memory_study", HERE / "study.py")
look, ladder = study.look, study.ladder
first = _module("scale_up_closure_territories_look", study.STEP_4E / "look.py")

SEEN = tuple(range(15001, 15009))  # step 4d's starts, in both worlds
WAYS = {"the first four to learn from": (SEEN[:4], SEEN[4:]),
        "the last four to learn from": (SEEN[4:], SEEN[:4])}  # fmt: skip


def write_reference() -> None:
    """The look's rules, from the leaders kept of step 4g's runs."""
    worlds = {}
    for name in study.WORLDS:
        world = look.World(name)
        worlds[name] = {
            str(block): study.sparse(sum(world.tallies[seed, block]["age"]
                                         for seed in world.seeds))
            for block in study.RUNGS}  # fmt: skip
    study.REFERENCE.write_text(json.dumps({
        "what": "the look's rules (look.py, step 4h): for each world and block, the tally of "
                "all eight of step 4g's starts (18001 to 18008, 18101 to 18108) on side "
                "2,048 over the block's matched age, counted by [how long a block has had its "
                "leader, up to 16 ticks][leader][neighbours species 1 leads][neighbours "
                "species 2 leads][leader one tick on], as study.sparse writes a tally",
        "worlds": worlds,
    }) + "\n")  # fmt: skip


def kept(name: str, seed: int) -> dict:
    """The leaders step 4d kept of one run, as the study's `fine` gives them."""
    found = first.load(name, seed, first.SIDE, first.GENERATIONS)
    return {"shares": found["shares"], **{b: first.LEADER[found[b]] for b in study.BLOCKS}}


def seen(learn: tuple[int, ...], held_out: tuple[int, ...]) -> study.Measures:
    """Step 4d's runs as the study would have them on record: start records, and the run-ons
    of every rule the study runs on, from the starts held out."""
    plan = {name: {"learn": list(learn), "try": list(held_out)} for name in study.WORLDS}
    frames = {(name, seed): kept(name, seed) for name in plan for seed in (*learn, *held_out)}
    rows = [study.start_record(name, seed, found) for (name, seed), found in frames.items()]
    for name in plan:
        for block in study.RUNGS:
            for reading, whose, counts in study.rules(rows, plan, name, block):
                rows += [study.ahead_record(name, seed, block, reading, whose,
                                            frames[name, seed][block], counts)
                         for seed in held_out]  # fmt: skip
    return study.Measures(rows, plan)


def main() -> None:
    assert (first.SIDE, first.GENERATIONS) == (study.SIDE, study.GENERATIONS)
    write_reference()
    found: dict = {}
    fewest = None
    for way, (learn, held_out) in WAYS.items():
        m = seen(learn, held_out)
        behind = min(int(m.by_span(name, block)[:, near, 0].min())
                     for name in study.WORLDS for block in study.RUNGS
                     for near in (3, 4, 5))  # fmt: skip
        fewest = behind if fewest is None else min(fewest, behind)
        for claim in study.claims():
            value = m.value(claim)
            found.setdefault(
                claim["label"], {"at least": claim["at_least"], "at most": claim["at_most"]}
            )[way] = {
                "value": study.number(value),
                "would": study.judge(value, claim, m.stands(claim)),
            }
        print(way, "done", flush=True)
    bounds = {
        "A, a block's past": {
            "a young lead over an old one, at least": study.YOUNG_OVER_OLD,
            "surprise removed, at least": study.REMOVES,
            "drawn from": "the look (side 2,048): with four rival neighbours a block of 8 "
            "that has had its leader one tick changes hands 6.2 and 7.0 times as often as "
            "one that has had it 16 ticks or more (still, busy), a block of 16 7.9 and 8.1 "
            "times; how long, up to 8 ticks, removes 7% to 11% of the plain rule's surprise "
            "at blocks of 4 to 16. Step 4d's runs on side 1,024 give the same: 6.2 and 7.0, "
            "7.9 and 8.1; 7% to 11%.",
        },
        "B, the top of the table": {
            "an old lead at five, blocks of 16 within this of 8": study.SAME_TOP,
            "the rule as it is at five, blocks of 16 over 8, at most": study.PLAIN_FALLS,
            "the mix alone, within this of the rule as it is": study.MIX_IS_IT,
            "drawn from": "the look: a lead of 16 ticks or more at five rival neighbours "
            "changes hands 0.96 and 1.00 times as often at blocks of 16 as at blocks of 8, "
            "where the rule as it is gives 0.85 and 0.87. On side 1,024: 0.93 and 0.97, "
            "0.84 and 0.87; and the rule as it is at blocks of 8, made from its own mix of "
            "young and old leads and the chances of blocks of 16, comes out at 0.99 of what "
            "it is in both worlds. The still world's old leads do fall a little: this is the "
            "bound most likely to be missed.",
        },
        "C, along the walls": {
            "an old lead at three, blocks of 16 over 8, at most": study.OLD_AT_THREE,
            "a lead of one tick at three, at most": study.NEW_AT_THREE,
            "an old lead at four, at most": study.OLD_AT_FOUR,
            "the share of the fall at three that is the mix, at most": study.MIX_IS_NOT,
            "the remembering rule's gap at blocks of 8, at least": study.STILL_A_GAP,
            "that gap over the plain rule's, at least": study.GAP_OVER_PLAIN,
            "drawn from": "the look: at three rival neighbours an old lead changes hands "
            "0.38 and 0.32 times as often at blocks of 16 as at 8, a lead of one tick 0.75 "
            "and 0.67 times; an old lead at four 0.75 and 0.80 times. On side 1,024: 0.38 "
            "and 0.40, 0.77 and 0.71, 0.76 and 0.80; a fifth of the plain rule's fall at "
            "three is the mix; and the remembering rule from blocks of 4 has 6.4% to 6.6% "
            "and 5.2% to 5.4% more surprise at blocks of 8, which is 0.75 and 0.92 to 0.96 "
            "of what the plain rule has.",
        },
        "D, run on": {
            "blocks amiss, with how long over as it is, at most": study.FEWER_AMISS,
            "the walls the plain rule keeps, at most": study.PLAIN_LOSES,
            "the walls the remembering rule keeps": list(study.KEEPS),
            "going back, within this of the world": study.GOES_BACK,
            "going back, the plain rule over the world, at most": study.PLAIN_DOES_NOT,
            "drawn from": "the look: 0.73 and 0.77 of the plain rule's blocks amiss at "
            "blocks of 8, 0.80 and 0.89 at 16; walls kept 0.86 and 0.89 by the plain rule "
            "at blocks of 8, 0.89 and 0.93 at 16, and 1.01 to 1.07 by the remembering one; "
            "going back in 0.26 and 0.27 of changes of hands in the world at blocks of 8, "
            "0.25 and 0.24 at 16, within 0.03 of that in the remembering rule's world and "
            "0.3 to 0.45 of it in the plain rule's. On side 1,024, from four trial starts "
            "each way: 0.72 and 0.77 to 0.78, 0.82 and 0.90 to 0.91; plain walls 0.84 to "
            "0.90 at blocks of 8 and 0.88 to 0.94 at 16, where one way and the other differ "
            "by up to 0.04; remembering walls 1.00 to 1.07; going back within 0.01 to 0.03. "
            "The walls at blocks of 16 are what moves most between one choice of starts and "
            "another, so their bounds are the widest.",
        },
        "E, the ladder's own test": {
            "the remembering rule from below over the rung's own, at most": study.LADDER,
            "what the plain rule from below pays more, at least": study.PLAIN_PAYS,
            "over the rung's own plain rule, at most": study.BEATS_PLAIN,
            "drawn from": "the look: the remembering rule from the rung below ends amiss in "
            "1.14 and 1.03 times as many blocks as the rung's own at blocks of 8, 1.03 and "
            "0.98 at 16; the plain rule from below in 1.20 and 1.09, 1.15 and 1.13. On side "
            "1,024: 1.13 to 1.14 and 1.03, 1.02 and 0.97 to 1.00; the plain rule pays 0.05 "
            "to 0.07 more at blocks of 8 and 0.14 to 0.19 more at 16; and the remembering "
            "rule from blocks of 8 ends with 0.84 and 0.87 to 0.91 of the blocks the rung's "
            "own plain rule gets amiss at blocks of 16.",
        },
        "R, the look's rules": {
            "one tick ahead, more surprise, at most": study.SERVES,
            "run on, blocks amiss over this run's own": list(study.RUNS_AS_WELL),
            "drawn from": "the look's rules tried on step 4d's runs, which the look never "
            "saw: as it is they have 0.03% to 0.3% less surprise than the rule learned "
            "from four of those starts, and with how long in view 0.5% to 2.8% less, having "
            "learned from far more; run on, they end amiss in 0.98 to 1.01 times as many "
            "blocks. Step 4g's rule of side 1,024 served on side 2,048 within 0.1%.",
        },
        "X, the anchor": {
            "the plain gap at blocks of 16": list(study.GAP_AT_16),
            "the plain rule's own run-on, amiss over changed, at most": study.WHERE,
            "drawn from": "step 4g's registered bounds for the same two numbers, which "
            "held there (2.8% and 3.0%; 0.54 and 0.46). On side 1,024 here: 2.3% to 2.7%; "
            "0.47 to 0.54.",
        },
        "what a claim stands on": {
            "blocks behind a chance, at least": study.ENOUGH,
            "a block fits": study.BLOCK_FITS,
            "drawn from": "steps 4e and 4g: a run-on is read only where at most a fifth of "
            "neighbouring blocks differ when the rule is started (0.16 to 0.18 at every "
            "rung at its matched age). The fewest blocks behind a chance any claim compares "
            f"were {fewest} in step 4d's eight starts; the registered run has sixteen.",
        },
    }
    study.SIZING.write_text(json.dumps({
        "what the bounds were drawn from": bounds,
        "step 4d's runs through the study's measures": found,
    }, indent=1) + "\n")  # fmt: skip
    failed = [label for label, told in found.items()
              if any(told[way]["would"] != "holds" for way in WAYS)]  # fmt: skip
    print(len(found), "claims;", "all would hold both ways" if not failed else failed)


if __name__ == "__main__":
    main()
