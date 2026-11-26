"""
What else the registered run shows. Exploratory: nothing here was registered, and nothing is
run.

    uv run --no-sync python examples/scale-up-rung/extras.py

The registered test (study.py) read two worlds at four rungs, each at the age that matches
its block, and asked of each rung how far the rule of the rung below is from its own. Four
more things are read here from the same records.

- **The rule from further down** (`gaps`): the rule of every lower rung tried at every rung,
  not of the one below alone. If the ladder is coming to a rule that stops changing, a rule
  from two rungs down is about as far as the two steps between add up to, and no further.
- **The other world's rule** (`across`): at each rung, the rule one world learned tried in the
  other. Step 4d found the two worlds' rules within half a percent of each other from blocks
  of 8; here both are read on a grid twice as wide, with a rung more.
- **Start by start** (`starts`): each registered number is a mean over four trial starts. The
  least and the most of one start say how far it could move.
- **The chances, rung by rung** (`chances`): the chance that a block changes hands, by how
  many of its eight neighbours its rival leads, and each rung's chance over the rung below's.
- **Where the gap is** (`where`): the extra surprise of the rule from the rung below, shared
  out by how many rival neighbours the block it was wrong about had.

The summary goes to extras.json.
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

OUT = HERE / "extras.json"
RUNGS = study.BLOCKS[1:]  # the rungs that have a rung below


def gaps(m, world: str) -> dict:
    """At each rung, the rule of every lower rung with as much data: more surprise than the
    rung's own rule on the world's trial starts."""
    out: dict = {}
    for block in RUNGS:
        here, trial = m.rule(world, "learn", block), m.rule(world, "try", block)
        out[str(block)] = {
            str(lower): round(ladder.excess(
                ladder.as_much(m.rule(world, "learn", lower), here), here, trial), 5)
            for lower in study.BLOCKS if lower < block}  # fmt: skip
    below = [out[str(block)][str(block // 2)] for block in RUNGS]
    out["each step's gap over the one before"] = [
        round(b / a, 3) for a, b in zip(below, below[1:], strict=False)
    ]
    return out


def across(m, world: str, other: str) -> dict:
    """At each rung, the other world's rule with as much data: more surprise than the world's
    own rule on its trial starts."""
    out = {}
    for block in study.BLOCKS:
        here = m.rule(world, "learn", block)
        there = ladder.as_much(m.rule(other, "learn", block), here)
        out[str(block)] = round(ladder.excess(there, here, m.rule(world, "try", block)), 5)
    return out


def starts(m, world: str) -> dict:
    """The least and the most of one trial start, for the numbers the claims are judged on."""

    def span(values) -> list[float]:
        return [round(float(min(values)), 4), round(float(max(values)), 4)]

    out = {}
    for block in RUNGS:
        here = m.rule(world, "learn", block)
        lower = ladder.as_much(m.rule(world, "learn", block // 2), here)
        seeds = m.plan[world]["try"]
        runs = {whose: {r["seed"]: r for r in m.ahead[(world, block, whose)]}
                for whose in (study.OWN, study.BELOW)}  # fmt: skip
        out[str(block)] = {
            "gap: the rule from the rung below, more surprise": span(
                [ladder.excess(lower, here, study.pooled(m.rows, world, [s], block))
                 for s in seeds]),
            "run on, amiss over changed": {
                whose: span([runs[whose][s]["apart_rule"][-1] / runs[whose][s]["apart_start"][-1]
                             for s in seeds])
                for whose in runs},
            "amiss, the rule from below over the rung's own": span(
                [runs[study.BELOW][s]["apart_rule"][-1] / runs[study.OWN][s]["apart_rule"][-1]
                 for s in seeds]),
            "run on, walls kept, its own": span(
                [runs[study.OWN][s]["walls_rule"][-1] / runs[study.OWN][s]["walls_world"][-1]
                 for s in seeds]),
        }  # fmt: skip
    return out


def chances(m, world: str) -> dict:
    """The chance a block changes hands in one tick, by how many of its eight neighbours its
    rival leads, at every rung; and from three rival neighbours up, where blocks do change
    hands, each rung's chance over the rung below's."""
    table = {block: [float(c / b) if b else None
                     for b, c in ladder.hands(m.rule(world, "all", block))]
             for block in study.BLOCKS}  # fmt: skip
    out: dict = {}
    for block in study.BLOCKS:
        rung: dict = {"chance": [None if c is None else round(c, 4) for c in table[block]]}
        if block > study.BLOCKS[0]:
            rung["over the rung below, from three rival neighbours up"] = [
                round(table[block][n] / table[block // 2][n], 3) for n in range(3, 9)
            ]
        out[str(block)] = rung
    return out


def where(m, world: str) -> dict:
    """At each rung, the extra bits the rule from the rung below costs on the trial starts,
    shared out by how many of a block's eight neighbours its rival leads (blocks with no
    leader apart); and how the blocks themselves are shared out."""
    out = {}
    for block in RUNGS:
        here, trial = m.rule(world, "learn", block), m.rule(world, "try", block)
        lower = ladder.as_much(m.rule(world, "learn", block // 2), here)
        extra = (trial * (np.log2(ladder.chances(here)) - np.log2(ladder.chances(lower)))).sum(
            axis=-1
        )  # the extra bits, by [leader][neighbours of 1][neighbours of 2]
        seen = trial.sum(axis=-1)
        # for species 1 the rival's neighbours are the second count, for species 2 the first
        bits = [float(extra[1, :, n].sum() + extra[2, n, :].sum()) for n in range(9)]
        blocks = [float(seen[1, :, n].sum() + seen[2, n, :].sum()) for n in range(9)]
        out[str(block)] = {
            "share of the extra surprise, by rival neighbours": [
                round(b / float(extra.sum()), 3) for b in bits],
            "share of it at blocks with no leader": round(
                float(extra[0].sum()) / float(extra.sum()), 3),
            "share of the blocks, by rival neighbours": [
                round(b / float(seen.sum()), 4) for b in blocks],
        }  # fmt: skip
    return out


def main() -> None:
    rows = [json.loads(line) for line in study.RECORDS.read_text().splitlines()]
    m = study.Measures(rows, study.design())
    worlds = list(study.WORLDS)
    found = {
        world: {
            "the rule of each lower rung, more surprise": gaps(m, world),
            "the other world's rule, more surprise": across(
                m, world, worlds[1 - worlds.index(world)]),
            "the least and the most of one trial start": starts(m, world),
            "changing hands, by rival neighbours": chances(m, world),
            "where the gap is": where(m, world),
        }
        for world in worlds
    }  # fmt: skip
    OUT.write_text(json.dumps(found, indent=1) + "\n")
    print(json.dumps(found, indent=1))


if __name__ == "__main__":
    main()
