"""
What else the registered run shows. Exploratory: nothing here was registered.

    uv run --no-sync python examples/scale-up-closure-territories/extras.py [--workers 2]

The registered test (study.py) asked whether the still world's rule serves in three worlds
that had never been zoomed out, as it is or "at another pace". It served in one as it is, in
one at half its tick, and in one not at all. Three things are read here from the same
records, and one small thing is run, to say what those three answers are answers to.

- **Each world's pace, read off its walls** (`paces`). If territories grow as the square root
  of the time, the walls between them thin as one over it, and a world whose walls move at a
  share p of the still world's pace has, at any generation, the still world's walls divided
  by the square root of p. So p is the square of (the still world's walls over the world's)
  at the same generation. That is a second way to a world's pace, which owes nothing to the
  coarse rule. It is set beside the tick at which the still world's rule serves best.
- **How each world's territories grow** (`growth`): the power of time its walls thin by
  between generations 1,024 and 4,096, which is a half for walls that move by how they curve.
- **The chances of changing hands, side by side** (`chances`): each world at its square tick
  beside the still world at the tick that serves it best.
- **The still world's rule at its best pace, run on** (`at_pace`): the registered run-ons
  used the still world's rule at the world's own tick. Where another tick serves better, the
  rule for that tick is run on here in the world's own time. This needs the world's leaders,
  which stayed on the pod, so its four trial starts are run again on this machine
  (`ladder.fine`: about ten minutes each).

The summary goes to extras.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ladder  # noqa: E402


def _module(name: str, path: Path):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


study = _module("scale_up_closure_territories_study", HERE / "study.py")

OUT = HERE / "extras.json"
GROWING = (*study.SEEN, *study.UNSEEN)


def walls(rows: list[dict], world: str, block: int) -> dict[str, float]:
    """A world's walls at blocks of `block` at every generation they were recorded at: the
    mean over all its starts."""
    records = [r for r in rows if r["kind"] == "start" and r["world"] == world]
    return {g: float(np.mean([r["walls"][str(block)][g] for r in records]))
            for g in records[0]["walls"][str(block)]}  # fmt: skip


def growth(rows: list[dict], world: str, block: int) -> float:
    """The power of time by which a world's walls thin between the generation a rule is run
    on from and the last."""
    first, last = ladder.WINDOWS["C"]
    found = walls(rows, world, block)
    return -math.log(found[str(last)] / found[str(first)]) / math.log(last / first)


def paces(rows: list[dict], world: str, block: int) -> dict[str, float]:
    """A world's pace beside the still world's, read off its walls at each generation: the
    square of the still world's walls over the world's."""
    mine, still = walls(rows, world, block), walls(rows, "still", block)
    return {g: (still[g] / mine[g]) ** 2 for g in mine if int(g) >= ladder.FROM}


def chances(m, world: str, block: int, tick: int) -> list[float | None]:
    """A world's chance of changing hands by rival-led neighbours at one block and tick."""
    found = ladder.hands(m.tally(world, "all", block, tick, ladder.WHOLE))
    return [round(float(c / b), 4) if b else None for b, c in found]


def run_fine(job: tuple[str, int]) -> tuple[str, int]:
    name, seed = job
    w = study.WORLDS[name]
    ladder.fine(name, w["rule"], w["density"], seed)
    return job


def at_pace(world: str, block: int, tick: int, plan: dict, kept: dict) -> dict:
    """The still world's rule for `tick`, run on in `world` with the world's own clock."""
    w = study.WORLDS[world]
    own = ladder.square(block)
    runs = []
    for seed in plan[world]["try"]:
        frames = ladder.fine(world, w["rule"], w["density"], seed)[block]
        runs.append(ladder.ahead(frames, kept["still"][ladder.key(block, tick)], block, own,
                                 (seed, block, tick, 2)))  # fmt: skip
    read = ("apart_rule", "apart_start", "apart_twin", "walls_rule", "walls_world")
    end = {what: float(np.mean([r[what][-1] for r in runs])) for what in read}
    return {"the still world's rule for a tick of": tick, "run on with a tick of": own,
            "amiss over changed": round(end["apart_rule"] / end["apart_start"], 4),
            "walls kept": round(end["walls_rule"] / end["walls_world"], 4),
            "amiss over two runs": round(end["apart_rule"] / end["apart_twin"], 4)}  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    rows = [json.loads(line) for line in study.RECORDS.read_text().splitlines()]
    entries = [json.loads(line) for line in (HERE / "ledger.jsonl").read_text().splitlines()]
    verdict = next(e["body"] for e in entries if e["kind"] == "verdict")
    plan, kept = study.design(), study.reference()
    m = study.Measures(rows, plan, kept)
    out: dict = {}
    for world in GROWING:
        told: dict = {"rule": study.WORLDS[world]["rule"], "blocks": {}}
        for block in (8, 16):
            own = ladder.square(block)
            best, tick = m.best_tick(world, "still", block)
            pace = paces(rows, world, block)
            told["blocks"][str(block)] = {
                "walls": {g: round(v, 4) for g, v in walls(rows, world, block).items()},
                "walls thin as time to the power": round(growth(rows, world, block), 3),
                "pace by its walls": {g: round(v, 3) for g, v in pace.items()},
                "the still world's rule serves best at a tick of": tick,
                "which is this share of its own tick": tick / own,
                "more surprise there": round(best, 5),
                "more surprise as it is": round(m.from_elsewhere(world, "still", block), 5),
                "changes hands, at its own tick": chances(m, world, block, own),
                "the still world, at that tick": chances(m, "still", block, tick),
                "run on, registered": {
                    "its own rule": verdict["measured"].get(
                        f"C {world}, block {block}: where", {}).get("value"),
                    "the still world's rule, as it is": verdict["measured"].get(
                        f"U {world}, block {block}: run on", {}).get("value")
                    if world in study.UNSEEN else None,
                },
            }  # fmt: skip
        out[world] = told
    # the still world's rule at its best pace, run on, where that is not its own tick
    wanted = [(world, int(block), told["the still world's rule serves best at a tick of"])
              for world in study.UNSEEN for block, told in out[world]["blocks"].items()
              if told["which is this share of its own tick"] != 1
              and told["more surprise there"] <= study.SERVES]  # fmt: skip
    jobs = sorted({(world, seed) for world, _, _ in wanted for seed in plan[world]["try"]})
    with ProcessPoolExecutor(max(args.workers, 1)) as pool:
        for name, seed in pool.map(run_fine, jobs):
            print(f"{name} from start {seed}: its leaders are here", flush=True)
    for world, block, tick in wanted:
        out[world]["blocks"][str(block)]["run on, at its best pace"] = at_pace(
            world, block, tick, plan, kept)  # fmt: skip
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    for world, told in out.items():
        for block, found in told["blocks"].items():
            brief = {k: v for k, v in found.items()
                     if not k.startswith(("changes", "the still world,"))}  # fmt: skip
            print(world, "block", block, brief)


if __name__ == "__main__":
    main()
