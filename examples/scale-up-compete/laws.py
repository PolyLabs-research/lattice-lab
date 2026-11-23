"""
Laws against time and size for two worlds of several species. Exploratory: nothing here is
registered.

    uv run --no-sync python examples/scale-up-compete/laws.py [--workers 1]

What is left of the scale-up plan's step 2 (docs/scale-up-plan.md): how a world's live fraction,
species balance, mixing and surviving species depend on time and on the grid's size, at seven
sizes from 32 to 256, with laws fitted by Kepler. Step 3 is to test what they say at 1024 to
4096.

Two worlds, chosen after the tie-break test (examples/scale-up-tie-break), each from a
half-full mixed start with the species in equal shares, 32 starts at each size:

- **pair**: Conway's Life against HighLife under the standoff, which makes the world a function
  of its grid and made no measurable difference to it; 1,000 generations, sampled every 25.
- **soup**: soup 19 of the tie-break test, five species, under the random draw and under the
  standoff; 400 generations, sampled every 20. It is the soup with the most contested births
  (68% under the draw) among those in which the standoff did not cost a species.

What is fitted:

- **against time**, at side 256: the live fraction (both worlds) and the mixing (the pair).
  Kepler's `compare_replicates` chooses among its laws over resamples of whole starts, and
  `fit_replicates` gives the chosen law's constants with intervals from the same resampling.
- **against size**, at the last generation: the mean of each quantity over the starts, with
  its standard error (`fit` and `rank` among `constant`, `logarithmic` and `power`), and the
  spread of each quantity over the starts (`power`: independent patches would give an exponent
  of -1, the spread falling as one over the side).
- **survival against size**: the share of starts in which every species is alive at the end,
  with a binomial likelihood, as a logistic curve in the logarithm of the side and as
  1 - exp(-(side / L0)^d), which is what independent patches give with d = 2.

Records go to laws/records.jsonl (LatticeLife's own, resumable) and the fits to
laws/results.json. The starts are 2001 to 2032; a registered study must use others.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

import kepler
import numpy as np
from first_look import HIGHLIFE, LIFE, soup_rules
from latticelife.experiments.competition import CompetitionTask, run_competition
from latticelife.experiments.harness import read_jsonl

HERE = Path(__file__).resolve().parent
OUT = HERE / "laws"

SIDES = (32, 48, 64, 96, 128, 192, 256)
SEEDS = tuple(range(2001, 2033))
PAIR_RULES, PAIR_STEPS, PAIR_EVERY = (LIFE, HIGHLIFE), 1000, 25
SOUP_RULES, SOUP_STEPS, SOUP_EVERY = soup_rules(19), 400, 20
WORLDS = {
    "pair standoff": (PAIR_RULES, "standoff", PAIR_STEPS, PAIR_EVERY),
    "soup random": (SOUP_RULES, "random", SOUP_STEPS, SOUP_EVERY),
    "soup standoff": (SOUP_RULES, "standoff", SOUP_STEPS, SOUP_EVERY),
}
TIME_LAWS = ("power", "logarithmic", "shifted_power", "relaxation", "algebraic_relaxation")
SIZE_LAWS = ("constant", "logarithmic", "power")
LARGER = (1024, 2048, 4096)


def tasks(sides=SIDES, seeds=SEEDS) -> list[CompetitionTask]:
    """Every run, the largest grids first."""
    return [
        CompetitionTask(rules, "square", side, 0.5, seed, steps, tie_break=kind, sample_every=every)
        for side in sorted(sides, reverse=True)
        for rules, kind, steps, every in WORLDS.values()
        for seed in seeds
    ]


def world_of(record: dict) -> str:
    return ("pair " if len(record["rules"]) == 2 else "soup ") + record["tie_break"]


def measure(record: dict, quantity: str, at: int) -> float:
    """One quantity of a record at sample `at`: `live`, the live fraction; `share`, species 1's
    share of the live cells; `unlike`, the share of adjacent live pairs that are of two species;
    `left`, the species alive (at the end of the run, whatever `at` is)."""
    if quantity == "left":
        return float(sum(e is None for e in record["extinct_at"]))
    alive = [series[at] for series in record["alive"]]
    if quantity == "live":
        return sum(alive) / record["cells"]
    if quantity == "share":
        return alive[0] / max(sum(alive), 1)
    if quantity == "unlike":
        return record["unlike"][at] / max(record["unlike"][at] + record["like"][at], 1)
    raise ValueError(f"unknown quantity {quantity!r}")


def constants(fit) -> dict:
    return {
        name: [round(float(value), 6), round(float(error), 6)]
        for name, value, error in zip(fit.param_names, fit.params, fit.stderr, strict=True)
    }


def time_law(runs: list[dict], quantity: str, first: int = 1) -> dict:
    """The law of `quantity` against the generation, over `runs` (one world at one size), from
    sample `first` on: which of TIME_LAWS the resamples of whole starts choose, and the chosen
    law's constants with their intervals."""
    generations = np.array(runs[0]["generations"][first:], dtype=float)
    curves = np.array(
        [[measure(r, quantity, at) for at in range(first, len(r["generations"]))] for r in runs]
    )
    chosen = kepler.compare_replicates(TIME_LAWS, generations, curves, resamples=100)
    best = kepler.fit_replicates(chosen.best, generations, curves, resamples=200)
    return {
        "quantity": quantity,
        "starts": len(runs),
        "generations": [int(generations[0]), int(generations[-1])],
        "mean": [round(float(v), 6) for v in curves.mean(axis=0)],
        "chosen": {law: round(float(share), 3) for law, share in chosen.shares.items()},
        "law": best.fit.name,
        "formula": best.fit.formula,
        "constants": constants(best.fit),
        "intervals": {
            name: [round(float(low), 6), round(float(high), 6)]
            for name, (low, high) in best.intervals.items()
        },
        "r2": round(float(best.fit.r2), 5),
        "ill_conditioned": bool(best.fit.ill_conditioned),
    }


def size_law(by_side: dict[int, list[float]]) -> dict:
    """The law of a quantity's mean against the side, among SIZE_LAWS, each side weighted by
    its standard error; and what the best law gives at the larger sides."""
    sides = sorted(by_side)
    means = [statistics.fmean(by_side[s]) for s in sides]
    errors = [statistics.stdev(by_side[s]) / len(by_side[s]) ** 0.5 for s in sides]
    if max(errors) == 0:  # the same value from every start at every side
        return {"sides": sides, "mean": means, "se": errors, "law": "constant", "exact": True}
    floor = max(errors) * 1e-6  # a side whose starts all agree still needs a weight
    weights = [max(e, floor) for e in errors]
    fits = [
        kepler.fit(law, sides, means, sigma=weights, absolute_sigma=True, inflate=True)
        for law in SIZE_LAWS
    ]
    ranking = kepler.rank(fits)
    best = ranking.best.fit if ranking.best is not None else fits[0]
    value, low, high = kepler.predict(best, list(LARGER), level=0.95)
    return {
        "sides": sides,
        "mean": [round(m, 6) for m in means],
        "se": [round(e, 6) for e in errors],
        "ranking": [
            {"law": e.name, "delta_bic": round(float(e.delta_bic), 2), "eligible": e.eligible}
            for e in ranking.entries
        ],
        "law": best.name,
        "formula": best.formula,
        "constants": constants(best),
        "ill_conditioned": bool(best.ill_conditioned),
        "at_larger_sides": {
            str(side): [round(float(v), 6), round(float(lo), 6), round(float(hi), 6)]
            for side, v, lo, hi in zip(LARGER, value, low, high, strict=True)
        },
    }


def spread_law(by_side: dict[int, list[float]]) -> dict:
    """The spread of a quantity over the starts against the side, as a power law. The spread's
    own standard error is taken as spread / sqrt(2 (starts - 1))."""
    sides = sorted(by_side)
    spreads = [statistics.stdev(by_side[s]) for s in sides]
    if min(spreads) <= 0:
        return {"sides": sides, "spread": spreads, "law": None}
    errors = [sd / (2 * (len(by_side[s]) - 1)) ** 0.5 for s, sd in zip(sides, spreads, strict=True)]
    fit = kepler.fit("power", sides, spreads, sigma=errors, absolute_sigma=True, inflate=True)
    value, low, high = kepler.predict(fit, list(LARGER), level=0.95)
    return {
        "sides": sides,
        "spread": [round(sd, 6) for sd in spreads],
        "se": [round(e, 6) for e in errors],
        "law": "power",
        "constants": constants(fit),
        "ill_conditioned": bool(fit.ill_conditioned),
        "at_larger_sides": {
            str(side): [round(float(v), 6), round(float(lo), 6), round(float(hi), 6)]
            for side, v, lo, hi in zip(LARGER, value, low, high, strict=True)
        },
    }


def survival_law(by_side: dict[int, tuple[int, int]]) -> dict:
    """The share of starts in which every species survives, against the side: (survived,
    starts) at each side, fitted with a binomial likelihood."""
    sides = sorted(by_side)
    survived, starts = [by_side[s][0] for s in sides], [by_side[s][1] for s in sides]
    out = {"sides": sides, "survived": survived, "starts": starts}
    if sum(survived) in (0, sum(starts)):  # every start alike: nothing to fit
        return {**out, "law": None}
    logistic = kepler.fit(
        "logistic_p", [math.log(s) for s in sides], survived, likelihood="binomial", trials=starts
    )
    patches = kepler.fit(
        "1 - exp(-(x/120.0)**2.0)",
        [float(s) for s in sides],
        survived,
        likelihood="binomial",
        trials=starts,
    )
    value, low, high = kepler.predict(logistic, [math.log(s) for s in LARGER], level=0.95)
    return {
        **out,
        "law": "logistic in the logarithm of the side",
        "constants": constants(logistic),
        "half_survive_at_side": round(math.exp(logistic.value("x0")), 1),
        "bic": round(float(logistic.bic), 2),
        "patches": {
            "formula": "1 - exp(-(side / L0)^d)",
            "d": [round(float(patches.params[-1]), 4), round(float(patches.stderr[-1]), 4)],
            "bic": round(float(patches.bic), 2),
        },
        "at_larger_sides": {
            str(side): [round(float(v), 5), round(float(lo), 5), round(float(hi), 5)]
            for side, v, lo, hi in zip(LARGER, value, low, high, strict=True)
        },
    }


def analyse(records: list[dict]) -> dict:
    runs: dict[tuple[str, int], list[dict]] = {}
    for record in records:
        side = int(record["cells"] ** 0.5)
        runs.setdefault((world_of(record), side), []).append(record)
    largest = max(side for _, side in runs)
    out: dict = {"sides": sorted({side for _, side in runs}), "worlds": {}}
    for world in sorted({w for w, _ in runs}):
        sides = sorted(side for w, side in runs if w == world)
        against_size = {}
        for quantity in ("live", "share", "unlike"):
            by_side = {s: [measure(r, quantity, -1) for r in runs[world, s]] for s in sides}
            against_size[quantity] = {"mean": size_law(by_side), "spread": spread_law(by_side)}
        timed = ("live", "unlike") if world.startswith("pair") else ("live",)
        out["worlds"][world] = {
            "starts": {str(s): len(runs[world, s]) for s in sides},
            "rules": runs[world, largest][0]["rules"],
            "contested_share_of_births": {
                str(s): round(
                    sum(sum(r["contested"]) for r in runs[world, s])
                    / max(sum(sum(sum(b) for b in r["births"]) for r in runs[world, s]), 1),
                    4,
                )
                for s in sides
            },
            "against_time": {q: time_law(runs[world, largest], q) for q in timed},
            "against_size": against_size,
            "survival": survival_law(
                {
                    side: (
                        sum(measure(r, "left", -1) == len(r["rules"]) for r in runs[world, side]),
                        len(runs[world, side]),
                    )
                    for side in sides
                }
            ),
            "deaths_by_species": {
                str(side): [
                    sum(r["extinct_at"][i] is not None for r in runs[world, side])
                    for i in range(len(runs[world, side][0]["rules"]))
                ]
                for side in sides
            },
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--quick", action="store_true", help="four small sides, four starts")
    args = parser.parse_args()
    out = OUT.with_name("laws-quick") if args.quick else OUT
    out.mkdir(exist_ok=True)
    todo = tasks(SIDES[:4], SEEDS[:4]) if args.quick else tasks()
    for _ in run_competition(todo, str(out / "records.jsonl"), args.workers):
        pass
    results = analyse(read_jsonl(out / "records.jsonl"))
    (out / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    for world, row in results["worlds"].items():
        for quantity, law in row["against_time"].items():
            print(f"{world}: {quantity} against time: {law['law']} {law['constants']}")
        for quantity, laws in row["against_size"].items():
            mean, spread = laws["mean"], laws["spread"]
            print(
                f"{world}: {quantity} against size: mean {mean['law']} "
                f"{mean.get('constants', '')}; spread {spread.get('constants', '')}"
            )
        survival = row["survival"]
        print(f"{world}: all species survive in {survival['survived']} of {survival['starts']}")


if __name__ == "__main__":
    main()
