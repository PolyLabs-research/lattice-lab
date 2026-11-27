"""
A quick number against one account of step 4j's sizing look. Exploratory: nothing here was
registered, and no world is run that the sizing look had not run.

    uv run --no-sync python examples/scale-up-class-memory/held.py

In the worlds step 4f missed, a block changes hands whatever its past. One account of that
is a flicker within the tick: the block's leader is read at an instant, and in a thin world
it may change many times between one reading and the next. If so, the leader who held the
block for most of the tick would be a steadier thing to read, and its table nearer the
look's.

The sizing look's runs keep every block's leader every two generations, so that reading
costs nothing: for each tick, who led the block at most of the readings in the tick just
ended (a tie goes to the leader at its end). The sized worlds are put through the same
measures both ways, one way round (the first half of a world's starts to learn from), with
the run-ons twice from each trial start.

It needs the sizing look's kept runs and its records (sizing.py), and makes a run again if
it is not kept, about seven minutes of one core each. The summary goes to held.json.
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


sizing = _module("scale_up_class_memory_sizing", HERE / "sizing.py")
study = sizing.study
clock, look, ladder = study.clock, study.look, study.ladder

OUT = HERE / "held.json"
AT, MOST = "at an instant", "held for most of the tick"
PAIRS = 1  # run-ons of a rule from one start: this many pairs, two runs


def instant(leaders: np.ndarray, tick: int) -> np.ndarray:
    """A run's leaders at 0, one tick, two ticks ... 64 ticks."""
    return leaders[:: tick // clock.EVERY][: clock.LAST_TICK + 1]


def held_most(leaders: np.ndarray, tick: int) -> np.ndarray:
    """At 0, one tick ... 64 ticks: who led each block at most of the readings of the tick
    just ended (at 0, who leads it then). A tie goes to whoever leads at the end of it."""
    frames = [leaders[0]]
    readings = tick // clock.EVERY
    for k in range(1, clock.LAST_TICK + 1):
        last = k * readings
        part = leaders[last - readings + 1 : last + 1]
        counts = np.stack([(part == leader).sum(axis=0) for leader in range(ladder.Q)])
        at_end = np.take_along_axis(counts, leaders[last][None].astype(np.int64), axis=0)[0]
        most = np.where(at_end == counts.max(axis=0), leaders[last], counts.argmax(axis=0))
        frames.append(most.astype(leaders.dtype))
    return np.stack(frames)


def measures(frames: dict, plan: dict, tick: int, lent: np.ndarray) -> dict:
    """One world read one way: `frames` gives each start's leaders tick by tick."""
    first, last = clock.window(tick)
    tallies = {seed: look.tally(study.LONG, frames[seed], tick, tick, first, last)
               for seed in frames}  # fmt: skip
    own = sum(tallies[seed] for seed in plan["learn"])
    trial = sum(tallies[seed] for seed in plan["try"])
    bits = {name: look.surprise(sees, own, trial) for name, sees in study.READINGS.items()}
    out = {"share of the plain rule's surprise that how long removes": round(
        1 - bits[study.HOW] / bits[study.PLAIN], 4)}  # fmt: skip
    for name, sees in study.READINGS.items():
        lends = look.surprise(sees, ladder.as_much(sees.of(lent), sees.of(own)), trial)
        out[f"the look's rule {name}, more surprise"] = round(lends / bits[name] - 1, 4)
    out["an old lead beside a flat wall changes hands"] = study.number(
        study.chance_of(own + trial, study.memory.OLD, 3), 4)  # fmt: skip
    for name, sees in study.READINGS.items():
        for whose, counts in ((study.OWN, own), (study.LOOKS, lent)):
            amiss, changed = [], []
            for seed in plan["try"]:
                for pair in range(PAIRS):
                    ran = look.ahead(sees, frames[seed], sees.of(counts), tick, tick,
                                     (seed, clock.BLOCK, (study.OWN, study.LOOKS).index(whose)),
                                     first, last, pair)  # fmt: skip
                    amiss += [ran["apart_rule"][-1], ran["apart_other"]]
                    changed.append(ran["apart_start"][-1])
            out[f"run on, {whose} rule {name}"] = round(
                float(np.mean(amiss) / np.mean(changed)), 4)  # fmt: skip
    return out


def main() -> None:
    way = sizing.WAYS[0]
    plans = sizing.plans()[way]
    rows = [json.loads(line) for line in sizing.records(way).read_text().splitlines()]
    ticks = {r["world"]: r["tick"] for r in rows if r["kind"] == "tally"}
    lent, sized = study.looks_rule(), sizing.chosen()
    out = {}
    for world, plan in plans.items():
        tick = ticks[world]
        runs = {seed: clock.fine(world, seed)["leaders"] for seed in plan["learn"] + plan["try"]}
        found = {"group": sized[world]["group"], "tick": tick}
        for name, read in ((AT, instant), (MOST, held_most)):
            frames = {seed: read(runs[seed], tick) for seed in runs}
            found[name] = measures(frames, plan, tick, lent)
        out[world] = found
        print(world, json.dumps(found), flush=True)
    OUT.write_text(json.dumps({
        "what": "the sizing look's worlds read two ways (held.py, exploratory): who leads a "
                "block at an instant, once a tick, and who led it for most of the tick just "
                "ended; one way round, the first half of a world's starts to learn from",
        "worlds": out}, indent=1) + "\n")  # fmt: skip


if __name__ == "__main__":
    main()
