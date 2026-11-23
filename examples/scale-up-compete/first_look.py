"""
A first look at worlds of several species, as they are. Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-compete/first_look.py [--workers 1]

Step 2 of the scale-up plan (docs/scale-up-plan.md) starts by looking. Everything here runs
under the random draw, the tie-break LatticeLife has always had, so that what is seen is the
world as it is and nothing about what another tie-break would do.

Two kinds of world, each from mixed starts with equal shares on a half-full wrapped square grid:

- **pairs**: Conway's Life against itself, and against HighLife, on 128 x 128 for 600
  generations, sampled every 50;
- **soups**: five species with rules drawn as `autorun` draws them (a birth set and a survival
  set of one to four counts each), on 64 x 64 for 200 generations, sampled every 20.

The starts are seeds 9001 and up and the soups' rules are sets 9001 and up: a registered study
must use others. Records go to look/records.jsonl (LatticeLife's own, resumable) and the summary
to look/summary.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import numpy as np
from latticelife.experiments.competition import CompetitionTask, run_competition
from latticelife.experiments.harness import read_jsonl

HERE = Path(__file__).resolve().parent
OUT = HERE / "look"

LIFE, HIGHLIFE = "B3/S23", "B36/S23"
PAIRS = {"life-life": (LIFE, LIFE), "life-highlife": (LIFE, HIGHLIFE)}
PAIR_SEEDS = range(9001, 9017)
SOUP_SETS = range(9001, 9013)
SOUP_SEEDS = range(9001, 9009)


def soup_rules(index: int, species: int = 5, degree: int = 8) -> tuple[str, ...]:
    """Rule set `index`: for each species a birth set and a survival set, each a random sample
    of one to four neighbour counts from 0 to `degree`, as `latticelife autorun` draws them."""
    rng = np.random.default_rng([20261123, 3, index])
    rules = []
    for _ in range(species):
        birth = sorted(rng.choice(degree + 1, size=int(rng.integers(1, 5)), replace=False).tolist())
        survive = sorted(
            rng.choice(degree + 1, size=int(rng.integers(1, 5)), replace=False).tolist()
        )
        rules.append(f"B{''.join(map(str, birth))}/S{''.join(map(str, survive))}")
    return tuple(rules)


def tasks() -> list[CompetitionTask]:
    out = [
        CompetitionTask(rules, "square", 128, 0.5, seed, 600, sample_every=50)
        for rules in PAIRS.values()
        for seed in PAIR_SEEDS
    ]
    out += [
        CompetitionTask(soup_rules(index), "square", 64, 0.5, seed, 200, sample_every=20)
        for index in SOUP_SETS
        for seed in SOUP_SEEDS
    ]
    return out


def describe(records: list[dict]) -> dict:
    """Per world: at each sampled generation the mean and spread over the starts of the live
    fraction, of species 1's share of the live cells and of the unlike share of live pairs; the
    contested share of births over the run; and the species left at the end."""
    worlds: dict[tuple, list[dict]] = {}
    for record in records:
        worlds.setdefault(tuple(record["rules"]), []).append(record)
    out = {}
    for rules, runs in worlds.items():
        generations = runs[0]["generations"]
        rows = []
        for g, generation in enumerate(generations):
            live = [sum(a[g] for a in r["alive"]) / r["cells"] for r in runs]
            share = [r["alive"][0][g] / max(sum(a[g] for a in r["alive"]), 1) for r in runs]
            mixed = [r["unlike"][g] / max(r["unlike"][g] + r["like"][g], 1) for r in runs]
            rows.append(
                {
                    "generation": generation,
                    "live": [round(statistics.mean(live), 5), round(statistics.stdev(live), 5)],
                    "share_1": [
                        round(statistics.mean(share), 4),
                        round(statistics.stdev(share), 4),
                    ],
                    "unlike": [round(statistics.mean(mixed), 4), round(statistics.stdev(mixed), 4)],
                }
            )
        births = sum(sum(sum(b) for b in r["births"]) for r in runs)
        contested = sum(sum(r["contested"]) for r in runs)
        left = [sum(e is None for e in r["extinct_at"]) for r in runs]
        out[" v ".join(rules)] = {
            "runs": len(runs),
            "cells": runs[0]["cells"],
            "contested_share_of_births": round(contested / max(births, 1), 4),
            "species_left": [min(left), statistics.median(left), max(left)],
            "samples": rows,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    path = OUT / "records.jsonl"
    for _ in run_competition(tasks(), str(path), args.workers):
        pass
    summary = describe(read_jsonl(path))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    for world, row in summary.items():
        first, last = row["samples"][0], row["samples"][-1]
        contested = 100 * row["contested_share_of_births"]
        print(
            f"{world}: runs {row['runs']}, contested {contested:.1f}% of births, species left "
            f"{row['species_left']}, live {first['live'][0]:.3f} -> {last['live'][0]:.4f} "
            f"(sd {last['live'][1]:.4f})"
        )


if __name__ == "__main__":
    main()
