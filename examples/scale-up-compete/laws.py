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
- **the species some starts lose** (added before step 3 was registered, from the same records):
  its cells at the end, start by start. In the soup it is species 4 (B4/S3), and what is left
  of it by generation 20 never changes again and is always a multiple of four: 2 x 2 blocks,
  which no other species can break, since a cell is only ever born into an empty place and a
  species counts its own kind alone. So whether the species survives is settled by the start:
  it does when at least one block forms. The blocks' density, how their number scatters over
  the starts, and the survival that density gives if they form independently
  (1 - exp(-density x cells)) are in `blocks`.
- **the spread as amplitude / side** (added at the same time): the power law's exponent held
  at -1, the amplitude from the seven sides in logarithms. This is the form step 3 tests.

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
LARGER = (512, 1024, 2048, 4096)


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


def measure(record: dict, quantity: str, at: int, species: int = 0) -> float:
    """One quantity of a record at sample `at`: `live`, the live fraction; `share`, the share of
    the live cells that species number `species` holds (counted from 0, so species 1 unless
    told otherwise); `density`, that species' cells as a share of the grid; `unlike`, the share
    of adjacent live pairs that are of two species; `left`, the species alive (at the end of
    the run, whatever `at` is)."""
    if quantity == "left":
        return float(sum(e is None for e in record["extinct_at"]))
    alive = [series[at] for series in record["alive"]]
    if quantity == "live":
        return sum(alive) / record["cells"]
    if quantity == "share":
        return alive[species] / max(sum(alive), 1)
    if quantity == "density":
        return alive[species] / record["cells"]
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
        "inverse": inverse_law(sides, spreads, [len(by_side[s]) for s in sides]),
    }


def inverse_law(sides: list[int], spreads: list[float], starts: list[int]) -> dict:
    """The spread as amplitude / side: the power law with its exponent held at -1, which is what
    independent patches give. Fitted in logarithms, where a spread over n starts has the
    standard error 1 / sqrt(2 (n - 1)) whatever its size; `se_log` is the amplitude's, widened
    by sqrt(chi2 / dof) when the sides scatter more than that."""
    logs = [math.log(sd * side) for side, sd in zip(sides, spreads, strict=True)]
    weights = [2.0 * (n - 1) for n in starts]
    centre = sum(w * v for w, v in zip(weights, logs, strict=True)) / sum(weights)
    chi2 = sum(w * (v - centre) ** 2 for w, v in zip(weights, logs, strict=True))
    dof = len(sides) - 1
    se = math.sqrt(1.0 / sum(weights)) * max(1.0, math.sqrt(chi2 / dof))
    amplitude = math.exp(centre)
    return {
        "formula": "a / side",
        "a": signif(amplitude),
        "se_log": signif(se),
        "chi2_per_dof": round(chi2 / dof, 2),
        "at_larger_sides": {
            str(side): [
                signif(amplitude / side),
                signif(amplitude / side * math.exp(-1.959964 * se)),
                signif(amplitude / side * math.exp(1.959964 * se)),
            ]
            for side in LARGER
        },
    }


def signif(value: float, digits: int = 6) -> float:
    """`value` to `digits` significant figures."""
    return float(f"{value:.{digits - 1}e}")


def block_spread(density: float, unit: int, side: int) -> float:
    """The spread over the starts of a species' share of the grid, when what is left of it is
    independent units of `unit` cells at `density` cells per grid cell: a Poisson number of
    units, so sqrt(unit x density) / side."""
    return math.sqrt(unit * density) / side


def block_survival(density: float, error: float, unit: int, side: int) -> tuple[float, float]:
    """The chance that a start keeps such a species, 1 - exp(-density x cells / unit), and the
    same at the lower end of the density's 95% band (taken in logarithms)."""
    low = density * math.exp(-1.959964 * error / density)
    return (
        1.0 - math.exp(-density * side * side / unit),
        1.0 - math.exp(-low * side * side / unit),
    )


def blocks_law(by_side: dict[int, list[dict]], species: int) -> dict:
    """A species that some starts lose, by its cells at the end of each run (species number
    `species`, from 0).

    `unit` is the largest number that divides every count (4 when what is left is 2 x 2
    blocks), `settled_by` the first sampled generation from which no run's count changes again,
    and `density` its cells as a share of the grid over all runs, with a standard error from
    the scatter of the runs about it. `dispersion` is the variance of the number of units over
    its mean, pooled over the sides: 1 when units form independently (a Poisson number), which
    gives the spread of the density as sqrt(unit x density) / side and the chance that a start
    keeps the species as 1 - exp(-density x cells / unit)."""
    sides = sorted(by_side)
    counts = {s: [r["alive"][species][-1] for r in by_side[s]] for s in sides}
    cells = {s: by_side[s][0]["cells"] for s in sides}
    unit = math.gcd(*[c for s in sides for c in counts[s]])
    out: dict = {"species": species + 1, "sides": sides, "unit": unit}
    out["cells_at_end"] = [round(statistics.fmean(counts[s]), 3) for s in sides]
    if unit == 0:  # the species is lost in every run
        return {**out, "law": None}
    settled = 0
    for s in sides:
        for r in by_side[s]:
            series = r["alive"][species]
            last = max((i for i, v in enumerate(series) if v != series[-1]), default=-1)
            settled = max(settled, last + 1)
    area = sum(len(counts[s]) * cells[s] for s in sides)
    density = sum(sum(counts[s]) for s in sides) / area
    scatter = sum((c - density * cells[s]) ** 2 for s in sides for c in counts[s])
    error = math.sqrt(scatter) / area
    runs = sum(len(counts[s]) for s in sides)
    pearson = sum(
        (c / unit - density * cells[s] / unit) ** 2 / (density * cells[s] / unit)
        for s in sides
        for c in counts[s]
    )
    return {
        **out,
        "law": "independent units",
        "rule": by_side[sides[0]][0]["rules"][species],
        "settled_by_generation": by_side[sides[0]][0]["generations"][settled],
        "units": sum(sum(counts[s]) for s in sides) // unit,
        "grid_cells": area,
        "density": [signif(density), signif(error)],
        "dispersion": round(pearson / (runs - 1), 3),
        "survival_from_density": [
            round(block_survival(density, error, unit, s)[0], 4) for s in sides
        ],
        "survived": [sum(c > 0 for c in counts[s]) for s in sides],
        "starts": [len(counts[s]) for s in sides],
        "at_larger_sides": {
            str(side): {
                "spread": signif(block_spread(density, unit, side)),
                "survival": [round(p, 6) for p in block_survival(density, error, unit, side)],
            }
            for side in LARGER
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
        lost = sorted(
            {
                i
                for r in runs[world, largest]
                for i, gone in enumerate(r["extinct_at"])
                if gone is not None
            }
        )
        if len(lost) == 1:  # one species that starts still lose on the largest grid
            out["worlds"][world]["blocks"] = blocks_law(
                {side: runs[world, side] for side in sides}, lost[0]
            )
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
