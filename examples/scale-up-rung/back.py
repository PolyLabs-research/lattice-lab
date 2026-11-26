"""
A first number for decision D12 of the plan. Exploratory: nothing here was registered.

    uv run --no-sync python examples/scale-up-rung/back.py [--leaders DIR]

The coarse rule of steps 4d to 4g knows who leads a block now, and how many of its eight
neighbours each species leads. It does not know who led the block one tick ago. Step 4g found
that what still changes from rung to rung is how often a block on a wall changes hands, and
this asks one thing of that: of the blocks a leader holds with as many rival neighbours, does
one that has just come over from the rival go back at the next tick more often than one that
has held since the tick before? If it does, the symbol leaves something out that a block's
own past would carry.

Each rung is read at its matched age on the square clock, at the instants the study reads it,
on each world's four trial starts.

This needs the block leaders of those eight runs (`study.fine`), which the registered records
do not hold. They were brought home from the pod; `--leaders` names the folder they are in
(by default the cache `study.fine` keeps). A run whose leaders are not there is made again,
about three hours of one core each.

The summary goes to back.json.
"""

from __future__ import annotations

import argparse
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
ladder, zoom = study.ladder, study.zoom

OUT = HERE / "back.json"
HELD, CAME = "held since the tick before", "just come over from the rival"
ENOUGH = 100  # a chance is told only where at least this many blocks stand behind it


def read(frames: np.ndarray, block: int) -> dict[str, np.ndarray]:
    """One run at one rung over its matched age. For the blocks a species leads, by how many
    of their eight neighbours its rival leads: how many there were and how many the rival led
    one tick on, apart for those the species also led one tick before and those the rival
    did. Two (9, 2) arrays."""
    first, last = study.AGES[block]
    tick = ladder.square(block)
    out = {HELD: np.zeros((9, 2), dtype=np.int64), CAME: np.zeros((9, 2), dtype=np.int64)}
    for g in ladder.instants(block, tick, first + tick, last):
        before, now, after = (frames[(g + k * tick) // block] for k in (-1, 0, 1))
        around = zoom.ring(now)
        for kind in (1, 2):
            rival = 3 - kind
            near = (around == rival).sum(axis=0)
            goes = after == rival
            for name, was in ((HELD, kind), (CAME, rival)):
                which = (now == kind) & (before == was)
                out[name][:, 0] += np.bincount(near[which], minlength=9)
                out[name][:, 1] += np.bincount(near[which & goes], minlength=9)
    return out


def told(found: dict[str, np.ndarray]) -> dict:
    over = {name: int(found[name][:, 1].sum()) for name in found}
    return {
        "of the blocks that went over to the rival, the share that had come from it one tick "
        "before": round(over[CAME] / max(over[HELD] + over[CAME], 1), 4),
        "blocks, by rival neighbours": {
            name: [int(n) for n in found[name][:, 0]] for name in found},
        "chance of going over to the rival at the next tick, by rival neighbours": {
            name: [round(float(c / n), 4) if n >= ENOUGH else None for n, c in found[name]]
            for name in found},
    }  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--leaders", type=Path, default=None,
                        help="the folder the runs' block leaders are kept in")  # fmt: skip
    args = parser.parse_args()
    if args.leaders is not None:
        ladder.CACHE = args.leaders
    plan = study.design()
    summary: dict = {}
    for world in plan:
        runs = [study.fine(world, seed) for seed in plan[world]["try"]]
        summary[world] = {}
        for block in study.BLOCKS:
            total = {HELD: np.zeros((9, 2), dtype=np.int64),
                     CAME: np.zeros((9, 2), dtype=np.int64)}  # fmt: skip
            for run in runs:
                for name, counts in read(run[block], block).items():
                    total[name] += counts
            summary[world][str(block)] = told(total)
    OUT.write_text(json.dumps(summary, indent=1) + "\n")
    for world, rungs in summary.items():
        for block, rung in rungs.items():
            print(world, block, json.dumps(rung))


if __name__ == "__main__":
    main()
