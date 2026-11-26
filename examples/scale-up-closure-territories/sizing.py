"""
Sizing for the registered test of worlds of territories. Exploratory: nothing is registered.

    uv run --no-sync python examples/scale-up-closure-territories/sizing.py

The registered test (study.py) sets a bound on every number the first look gave. A bound is
worth something only if it is drawn knowing how far the number moves when nothing has
changed but the starts. So before any bound is drawn, three things are done here with runs
that already exist, and one small new one:

- **The first look's runs through the study's own measures** (`look_rows`): its sixteen runs
  are tallied as the study tallies a run (`ladder.py`: three windows, every tick), and every
  claim the study makes of the first look's two worlds is worked out by the code that will
  judge it (`study.Measures`, `study.claims`). So the measures are exercised before they are
  registered, and the first look's numbers are restated in the form the claims use.
- **The same with the starts dealt differently** (`SPLITS`): the first look learned from
  starts 15001 to 15004 and tried on 15005 to 15008. Here that is done six ways. The spread
  over the six is how far a number moves from one set of starts to another.
- **The reference rules** (`reference.json`): the tables all eight runs of each of the first
  look's worlds give, at every block and tick. The registered test tries them, unchanged,
  in worlds and from starts they have not seen. To see what a rule from other starts of the
  same world costs with fresh data, two further splits take the rule from four starts and
  learn and try on two each.
- **The control, looked at once** (`control`): B2578/S135678 against its copy on side 512
  from starts 15101 and 15102, read through blocks. The search found its territories set
  after generation 512; this checks that its leaders stop changing, and what the still
  world's rule makes of it. The three worlds the test is about are not run here or anywhere.

The summary goes to sizing.json, which the registration carries. The bounds stand beside the
numbers there; `--bounds` writes them in again from study.py without running anything, for
when a bound has been moved after the numbers were seen (which is what they are for).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ladder  # noqa: E402


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold more than one
    look.py and more than one study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


look = _module("scale_up_closure_territories_look", HERE / "look.py")
study = _module("scale_up_closure_territories_study", HERE / "study.py")

STARTS = (*look.LEARN, *look.TRY)  # 15001 to 15008
# the starts a rule is learned from, by their place among the eight; it is tried on the rest
SPLITS = {
    "as the first look": (0, 1, 2, 3),
    "exchanged": (4, 5, 6, 7),
    "odd": (0, 2, 4, 6),
    "even": (1, 3, 5, 7),
    "outer": (0, 1, 6, 7),
    "inner": (2, 3, 4, 5),
}
# the reference rule from four starts, a fresh rule from two more, tried on the last two
FRESH = {
    "rule from 1-4, learn 5-6, try 7-8": ((0, 1, 2, 3), (4, 5), (6, 7)),
    "rule from 5-8, learn 1-2, try 3-4": ((4, 5, 6, 7), (0, 1), (2, 3)),
}
CONTROL = {"side": 512, "starts": (15101, 15102)}


def look_frames(world: str, seed: int) -> dict:
    """One of the first look's runs as the study reads a run: leaders, and shares."""
    kept = look.load(world, seed, look.SIDE, look.GENERATIONS)
    return {"shares": kept["shares"], **{b: look.LEADER[kept[b]] for b in ladder.BLOCKS}}


def look_rows() -> tuple[list[dict], dict]:
    """The first look's sixteen runs as the study's records, and their leaders."""
    rows, frames = [], {}
    for world in study.SEEN:
        for seed in STARTS:
            frames[(world, seed)] = look_frames(world, seed)
            rows.append(ladder.start_record(world, seed, frames[(world, seed)]))
    return rows, frames


def rules_of(rows: list[dict], seeds_at: tuple[int, ...]) -> dict:
    """The rule each of the first look's worlds gives from some of its starts, at every block
    and tick, over the whole run."""
    seeds = [STARTS[i] for i in seeds_at]
    return {world: {ladder.key(b, t): study.pooled(rows, world, seeds, b, t, ladder.WHOLE)
                    for b in ladder.BLOCKS for t in ladder.TICKS[b]}
            for world in study.SEEN}  # fmt: skip


def run_ons(rows: list[dict], frames: dict, plan: dict, kept: dict) -> list[dict]:
    """The run-ons the study would make in the first look's two worlds under one plan."""
    out = []
    for name, seed, whose, block, tick, counts in study.ahead_jobs(rows, plan, kept):
        draws = (seed, block, tick, (study.OWN, study.STILLS).index(whose))
        found = ladder.ahead(frames[(name, seed)][block], ladder.dense(counts), block, tick, draws)
        out.append({"kind": "ahead", "world": name, "seed": seed, "rule": whose, **found})
    return out


def measured(rows: list[dict], frames: dict, plan: dict, kept: dict) -> dict:
    """Every claim of the first look's worlds under one plan: its label to its number."""
    every = rows + run_ons(rows, frames, plan, kept)
    m = study.Measures(every, plan, kept)
    worlds = {w: study.WORLDS[w] for w in study.SEEN}
    out = {c["label"]: m.value(c) for c in study.claims(worlds)}
    out.update({f"coarsens: {w}": m.coarsens(w) for w in plan})
    for w in plan:  # each trial start by itself, for the spread from start to start
        for (world, whose, block, tick), runs in m.ahead.items():
            if world == w and whose == study.OWN and tick == ladder.square(block):
                out[f"by start: {w}, block {block}: amiss over changed"] = [
                    round(r["apart_rule"][-1] / r["apart_start"][-1], 4) for r in runs]  # fmt: skip
                out[f"by start: {w}, block {block}: walls kept"] = [
                    round(r["walls_rule"][-1] / r["walls_world"][-1], 4) for r in runs]  # fmt: skip
    return out


def control() -> dict:
    """The control world once, small: whether its leaders stop changing, and what the still
    world's rule makes of it, learned from one start and tried on the other."""
    name = study.CONTROL
    w = study.WORLDS[name]
    side, (first, second) = CONTROL["side"], CONTROL["starts"]
    frames = {seed: ladder.fine(f"sizing-{name}", w["rule"], w["density"], seed, side)
              for seed in (first, second)}  # fmt: skip
    rows = [ladder.start_record(name, seed, frames[seed], side) for seed in frames]
    kept = study.reference()
    plan = {name: {"learn": [first], "try": [second]}}
    out: dict = {"side": side, "starts": [first, second], "live": rows[1]["live"],
                 "walls": rows[1]["walls"], "blocks": {}}  # fmt: skip
    m = study.Measures(rows, plan, kept)
    for block in (8, 16):
        tick = ladder.square(block)
        late = study.pooled(rows, name, [first, second], block, tick, ladder.LATE)
        found = ladder.hands(late)
        ran = ladder.ahead(frames[second][block], kept["still"][ladder.key(block, tick)],
                           block, tick, (second, block, tick, 1))  # fmt: skip
        out["blocks"][str(block)] = {
            "changed leader per thousand, a coarse generation, after generation 1,024": round(
                1000 * float(found[:, 1].sum() / max(found[:, 0].sum(), 1)), 4),
            "the still world's rule, by tick": {
                str(t): round(m.from_elsewhere(name, "still", block, t), 4)
                for t in ladder.TICKS[block]},
            "run on: amiss at the end": ran["apart_rule"][-1],
            "run on: changed meanwhile": ran["apart_start"][-1],
            "run on: walls, world and rule": [ran["walls_world"][-1], ran["walls_rule"][-1]],
        }  # fmt: skip
    return out


def bounds() -> dict:
    """The bound each claim of the first look's worlds carries, by its label."""
    worlds = {w: study.WORLDS[w] for w in study.SEEN}
    return {c["label"]: [c["at_least"], c["at_most"]] for c in study.claims(worlds)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--bounds", action="store_true",
                        help="write the bounds in again from study.py; run nothing")  # fmt: skip
    if parser.parse_args().bounds:
        summary = json.loads(study.SIZING.read_text())
        drawn, limits = summary["what the bounds were drawn from"], bounds()
        if set(drawn) != set(limits):
            raise SystemExit("the claims are not the ones sizing.json was written for")
        for label, (at_least, at_most) in limits.items():
            drawn[label]["bound"] = {"at_least": at_least, "at_most": at_most}
        study.SIZING.write_text(json.dumps(summary, indent=1) + "\n")
        return
    rows, frames = look_rows()
    whole = rules_of(rows, tuple(range(len(STARTS))))
    study.REFERENCE.write_text(json.dumps({
        "what": "the first look's rules: for each of its two worlds, the tally of all eight "
                "of its runs (starts 15001 to 15008) over generations 64 to 4,096, at every "
                "block and tick, as rows of [view, then the count of each next leader]",
        "rules": {world: {where: ladder.sparse(counts) for where, counts in found.items()}
                  for world, found in whole.items()},
    }, indent=None, separators=(",", ":")) + "\n")  # fmt: skip
    found: dict = {}
    for name, learn in SPLITS.items():
        plan = {w: {"learn": [STARTS[i] for i in learn],
                    "try": [s for i, s in enumerate(STARTS) if i not in learn]}
                for w in study.SEEN}  # fmt: skip
        # the rule "from elsewhere" is here the rule of the starts learned from, so X is nought
        found[name] = measured(rows, frames, plan, rules_of(rows, learn))
        print(name, "done", flush=True)
    fresh: dict = {}
    for name, (rule, learn, tried) in FRESH.items():
        plan = {w: {"learn": [STARTS[i] for i in learn], "try": [STARTS[i] for i in tried]}
                for w in study.SEEN}  # fmt: skip
        fresh[name] = measured(rows, frames, plan, rules_of(rows, rule))
        print(name, "done", flush=True)
    limits = bounds()
    drawn = {}
    for label, (at_least, at_most) in limits.items():
        values = [found[name][label] for name in SPLITS]
        drawn[label] = {
            "bound": {"at_least": at_least, "at_most": at_most},
            "the first look's starts dealt six ways": [
                None if v is None else round(float(v), 5) for v in values],
            "a rule from four starts, fresh rules from two": [
                None if fresh[name][label] is None else round(float(fresh[name][label]), 5)
                for name in FRESH],
        }  # fmt: skip
    by_start = {label: {name: found[name][label] for name in SPLITS}
                for label in found["as the first look"]
                if label.startswith("by start")}  # fmt: skip
    summary = {
        "splits": {name: [STARTS[i] for i in learn] for name, learn in SPLITS.items()},
        "fresh": {name: [[STARTS[i] for i in part] for part in parts]
                  for name, parts in FRESH.items()},
        "what the bounds were drawn from": drawn,
        "run-ons by trial start": by_start,
        "the control": control(),
    }  # fmt: skip
    study.SIZING.write_text(json.dumps(summary, indent=1) + "\n")
    for label, row in drawn.items():
        values = [v for v in row["the first look's starts dealt six ways"] if v is not None]
        low, high = (min(values), max(values)) if values else (None, None)
        fresh_values = row["a rule from four starts, fresh rules from two"]
        print(f"{label}: {low} to {high}; fresh {fresh_values}; bound {row['bound']}")
    print(json.dumps(summary["the control"], indent=1))


if __name__ == "__main__":
    main()
