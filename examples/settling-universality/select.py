"""
Choose the rules for the universality study, by criteria fixed before any of them is run.

    uv run python examples/settling-universality/select.py --workers 2

On each lattice (square, hexagon, triangle in both neighbourhoods), rules are drawn from the
whole outer-totalistic space with a seeded generator (birth on 0 excluded: such rules strobe
the empty background). Each is run from 10 soups (density 0.5, seeds 1 to 10, cap 2000) on a
16 x 16 torus, then, if it passes there, on 64 x 64. A rule is kept when

    - every seed settles (a state repeats, or the grid empties) within the cap at both sizes;
    - the median settling time at 64 is at least 20 generations (something happens);
    - it is larger at 64 than at 16 (settling takes longer on a larger torus);
    - it is at most 1000 at 64 (so tori of 512 are affordable).

Nothing about the shape of the growth or the spread across seeds is looked at. The first two
rules drawn on each lattice that pass are kept, in the order drawn; every rule tried is
written to selection.jsonl with the reason it was kept or not.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from latticelife.config import DEFAULT_CONFIG_PATH, load_config
from latticelife.core.rules import Rule
from latticelife.experiments.observables import median_transient
from latticelife.experiments.sweeps import SweepTask, sweep_point

HERE = Path(__file__).resolve().parent
LATTICES = {
    "square": ("square", None, 8),
    "hexagon": ("hexagon", None, 6),
    "triangle-edge": ("triangle", "edge", 3),
    "triangle-edge+vertex": ("triangle", "edge+vertex", 12),
}
SEED = 20261017
KEEP = 2
MAX_TRIED = 200
SEEDS = range(1, 11)
CAP = 2000


def config_for(mode: str | None):
    config = load_config(DEFAULT_CONFIG_PATH)
    if mode is None:
        return config
    return replace(config, grid=replace(config.grid, triangle_mode=mode))


def draw(lattice: str, rng: np.random.Generator) -> Rule:
    n = LATTICES[lattice][2]
    birth = {k for k in range(1, n + 1) if rng.random() < 0.5}
    survive = {k for k in range(n + 1) if rng.random() < 0.5}
    return Rule(birth=birth, survive=survive)


def _run(task: SweepTask) -> dict:
    return sweep_point(task).to_json()


def medians(records: list[dict]) -> dict:
    return {row.grid: row for row in median_transient(records)}


def judge(lattice: str, rule: Rule, pool) -> dict:
    shape, mode, n = LATTICES[lattice]
    config = config_for(mode)
    text = rule.to_bs_string(n)
    out = {"lattice": lattice, "rule": text}
    records = []
    for size in (16, 64):
        tasks = [SweepTask(config, text, shape, size, 0.5, seed, CAP) for seed in SEEDS]
        records += pool.map(_run, tasks)
        row = medians(records)[size]
        out[f"median_{size}"] = row.median
        if not row.complete:
            out["kept"], out["reason"] = False, f"unsettled seeds at {size}"
            return out
    m16, m64 = out["median_16"], out["median_64"]
    if m64 < 20:
        out["kept"], out["reason"] = False, "median below 20 at 64"
    elif m64 <= m16:
        out["kept"], out["reason"] = False, "no growth from 16 to 64"
    elif m64 > 1000:
        out["kept"], out["reason"] = False, "median above 1000 at 64"
    else:
        out["kept"], out["reason"] = True, "passes"
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    log = HERE / "selection.jsonl"
    log.write_text("")
    chosen = {}
    with Pool(args.workers) as pool:
        for index, lattice in enumerate(LATTICES):
            rng = np.random.default_rng([SEED, index])
            seen, kept = set(), []
            while len(kept) < KEEP and len(seen) < MAX_TRIED:
                rule = draw(lattice, rng)
                text = rule.to_bs_string(LATTICES[lattice][2])
                if text in seen:
                    continue
                seen.add(text)
                result = judge(lattice, rule, pool)
                with log.open("a") as f:
                    f.write(json.dumps(result) + "\n")
                print(json.dumps(result), flush=True)
                if result["kept"]:
                    kept.append(text)
            chosen[lattice] = {"rules": kept, "tried": len(seen)}
    (HERE / "selected.json").write_text(json.dumps(chosen, indent=1) + "\n")
    print(json.dumps(chosen))


if __name__ == "__main__":
    main()
