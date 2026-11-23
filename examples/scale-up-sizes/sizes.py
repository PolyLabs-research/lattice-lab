"""
The registered scale-up test (step 3 of docs/scale-up-plan.md): what the laws found on grids
of side 32 to 256 say about larger ones.

Step 2 fitted laws against time and size for two worlds of several species
(examples/scale-up-compete/laws.py, exploratory): Conway's Life against HighLife under the
standoff, and a five-species soup under the random draw and under the standoff. They say that
bigger is more of the same: no mean depends on the side, and every spread over the starts falls
as one over the side. The one thing that changed with size, the soup's rare species surviving
only on large grids, turned out to be more of the same too: what is left of it is 2 x 2 blocks
that nothing can break, as dense on a small grid as on a large one, and a small grid often has
none. This asks whether all of that holds at sides nobody has run. It is registered in two
parts from one set of laws, before either is run, so that neither part's predictions can lean
on the other's results:

    examples/scale-up-sizes          sides 512 and 1024, 32 starts each, run here
    examples/scale-up-sizes-large    sides 2048 and 4096, 16 starts each, for a pod

**Predictions**, for each world at each side, all read from the step-2 fits
(examples/scale-up-compete/laws/results.json, hashed into the question):

- *mean*: the mean over the starts, at the last generation, of the live fraction, of species
  1's share of the live cells and of the unlike share of adjacent live pairs is the constant
  fitted at sides 32 to 256. In the soup, so is the rare species' share of the grid.
- *spread*: the spread of each over the starts is its amplitude over the side, the amplitude
  fitted at sides 32 to 256. For the rare species no amplitude is fitted: its blocks form
  independently, so their number is a Poisson one and the spread follows from the density.
- *survival*: every species is alive at the end in at least as many starts as the blocks'
  density allows (in every start, for the pair, which lost no species at any size).
- *time*: the live fraction's law against time, refitted at this side, settles where it did at
  side 256 and as fast: c and b of c + a (1 + t/tau)^-b for the pair, c and tau of
  c + a exp(-t/tau) for the soup.

A claim holds when the new measurement is within Z = 3.29 combined standard errors of the
law's value (the 99.9% level). The level is strict because each part makes 62 claims: at it,
laws that are exactly right fail a claim in about one part in sixteen. Spreads are compared in
logarithms, where a spread over n starts has the standard error 1 / sqrt(2 (n - 1)). The
survival claim is a one-sided binomial test at the same level against the lower end of the
law's 95% band.

**What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import kepler
import numpy as np
from latticelife.experiments.competition import CompetitionTask, competition_point
from scipy import stats

HERE = Path(__file__).resolve().parent
COMPETE = HERE.parent / "scale-up-compete"
sys.path.insert(0, str(COMPETE))

import laws  # noqa: E402

from lattice_lab.study import Study, append_records  # noqa: E402

RESULTS = COMPETE / "laws" / "results.json"
LEVEL = 0.999
Z = float(stats.norm.ppf(1 - (1 - LEVEL) / 2))
FAMILIES = ("mean", "spread", "survival", "time")
TIME_CONSTANTS = {
    "pair standoff": ("algebraic_relaxation", ("c", "b")),
    "soup random": ("relaxation", ("c", "tau")),
    "soup standoff": ("relaxation", ("c", "tau")),
}
NAMES = {
    "live": "the live fraction",
    "share": "species 1's share of the live cells",
    "unlike": "the unlike share of adjacent live pairs",
}


def load_results() -> dict:
    return json.loads(RESULTS.read_text())


def at_least(starts: int, chance: float, level: float = LEVEL) -> int:
    """The fewest successes in `starts` tries that a chance of `chance` each allows: fewer
    than this has probability at most 1 - level."""
    if chance >= 1:
        return starts
    k = 0
    while stats.binom.cdf(k, starts, chance) <= 1 - level:
        k += 1
    return k


def band(value: float, se_log: float, starts: int) -> list[float]:
    """Where a spread over `starts` starts may lie when the law gives `value`, with the standard
    error `se_log` in logarithms: within Z combined standard errors, in logarithms."""
    width = Z * math.sqrt(se_log**2 + 1.0 / (2 * (starts - 1)))
    return [laws.signif(value * math.exp(-width)), laws.signif(value * math.exp(width))]


def predictions(sides: tuple[int, ...], starts: int, results: dict | None = None) -> list[dict]:
    """The registered claims for these sides, from the step-2 fits."""
    worlds = (results or load_results())["worlds"]
    out = []
    for world in laws.WORLDS:
        fitted = worlds[world]
        blocks = fitted.get("blocks")
        if blocks is not None and blocks["law"] is None:
            raise AssertionError(f"{world}: the lost species has no law")
        for side in sides:

            def claim(family: str, what: str, text: str, world=world, side=side, **body) -> dict:
                return {
                    "label": f"{world}, side {side}: {family} {what}".strip(),
                    "family": family,
                    "world": world,
                    "side": side,
                    "starts": starts,
                    "level": LEVEL,
                    "claim": text,
                    **body,
                }

            # the means: the constants
            for quantity, name in NAMES.items():
                mean = fitted["against_size"][quantity]["mean"]
                if mean["law"] != "constant":
                    raise AssertionError(f"{world} {quantity}: the mean's law is {mean['law']}")
                value, error = mean["constants"]["a"]
                text = f"the mean of {name} is {value}, as at sides 32 to 256"
                out.append(
                    claim("mean", quantity, text, quantity=quantity, predicted=value, se=error)
                )
            if blocks:
                species, (density, error) = blocks["species"], blocks["density"]
                text = (
                    f"species {species} ({blocks['rule']}) holds a share {density} of the grid "
                    f"at the end, as at sides 32 to 256: its blocks of {blocks['unit']} cells "
                    "are as dense on a large grid as on a small one"
                )
                out.append(
                    claim("mean", "rare", text, quantity="rare", species=species,
                          predicted=density, se=error)
                )  # fmt: skip
            # the spreads: amplitude / side
            for quantity, name in NAMES.items():
                inverse = fitted["against_size"][quantity]["spread"]["inverse"]
                value = laws.signif(inverse["a"] / side)
                text = (
                    f"the spread of {name} over the starts is {inverse['a']} / side = {value}: "
                    "it falls as one over the side"
                )
                out.append(
                    claim("spread", quantity, text, quantity=quantity, predicted=value,
                          se_log=inverse["se_log"],
                          accept=band(value, inverse["se_log"], starts))
                )  # fmt: skip
            if blocks:
                value = laws.signif(laws.block_spread(density, blocks["unit"], side))
                se_log = laws.signif(0.5 * error / density)
                text = (
                    f"the blocks of species {species} form independently, so their number over "
                    "the starts is a Poisson one and the spread of the species' share of the "
                    f"grid is sqrt({blocks['unit']} x density) / side = {value}"
                )
                out.append(
                    claim("spread", "rare", text, quantity="rare", species=species,
                          predicted=value, se_log=se_log, accept=band(value, se_log, starts))
                )  # fmt: skip
            # survival
            if blocks:
                chance, low = (
                    round(p, 6) for p in laws.block_survival(density, error, blocks["unit"], side)
                )
                fewest = at_least(starts, low)
                text = (
                    f"every species is alive at the end in at least {fewest} of the {starts} "
                    f"starts: a start keeps species {species} when at least one block forms, a "
                    f"chance of {chance} at this density (at least {low})"
                )
            else:
                if fitted["survival"]["law"] is not None:
                    raise AssertionError(f"{world}: starts lose a species, with no law for it")
                chance, low, fewest = 1.0, 1.0, starts
                text = "no species is lost in any start, as at every side from 32 to 256"
            out.append(claim("survival", "", text, predicted=chance, low=low, at_least=fewest))
            # the law against time
            law, names = TIME_CONSTANTS[world]
            timed = fitted["against_time"]["live"]
            if timed["law"] != law:
                raise AssertionError(f"{world}: the live fraction against time is {timed['law']}")
            for name in names:
                value, error = timed["constants"][name]
                text = (
                    f"the live fraction against time follows {timed['formula']} with "
                    f"{name} = {value}, as at side 256"
                )
                out.append(
                    claim("time", name, text, constant=name, law=law, predicted=value, se=error)
                )
    return out


# --- running -------------------------------------------------------------------------------------


def run_one(job: tuple[str, int, int]) -> dict:
    """One world at one side from one start, as its record."""
    world, side, seed = job
    rules, kind, steps, every = laws.WORLDS[world]
    task = CompetitionTask(
        tuple(rules), "square", side, 0.5, seed, steps, tie_break=kind, sample_every=every
    )
    record = competition_point(task)
    return {
        "world": world,
        "side": side,
        "seed": seed,
        "cells": record.cells,
        "generations": record.generations,
        "alive": record.alive,
        "unlike": record.unlike,
        "like": record.like,
        "births": [sum(series) for series in record.births],
        "contested": sum(record.contested),
        "extinct_at": record.extinct_at,
        "start_sha256": record.start_sha256,
        "final_sha256": record.final_sha256,
    }


def jobs(sides: tuple[int, ...], seeds: tuple[int, ...]) -> list[tuple[str, int, int]]:
    """Every run, the smaller grids first, so that a run cut short has whole sides."""
    return [
        (world, side, seed) for side in sorted(sides) for world in laws.WORLDS for seed in seeds
    ]


def execute(path: Path, workers: int, sides: tuple[int, ...], seeds: tuple[int, ...]) -> None:
    done = set()
    if path.exists():
        done = {
            (r["world"], r["side"], r["seed"])
            for r in map(json.loads, path.read_text().splitlines())
        }
    todo = [job for job in jobs(sides, seeds) if job not in done]
    if workers <= 1:
        for job in todo:
            append_records(path, [run_one(job)])
        return
    with ProcessPoolExecutor(workers) as pool:
        for record in pool.map(run_one, todo):
            append_records(path, [record])


# --- judging -------------------------------------------------------------------------------------


def measured(record: dict, claim: dict) -> float:
    """What a mean or a spread claim measures of one run, at its last generation."""
    if claim["quantity"] == "rare":
        return laws.measure(record, "density", -1, claim["species"] - 1)
    return laws.measure(record, claim["quantity"], -1)


def time_constants(runs: list[dict], law: str) -> dict | None:
    """The live fraction's law against time refitted to `runs`: {constant: (value, error)}, the
    errors from resampling whole starts. None when the fit does not succeed."""
    generations = np.array(runs[0]["generations"][1:], dtype=float)
    curves = np.array(
        [[laws.measure(r, "live", at) for at in range(1, len(r["generations"]))] for r in runs]
    )
    try:
        fitted = kepler.fit_replicates(law, generations, curves, resamples=200)
    except ValueError:
        return None
    values = {
        name: (float(value), float(error))
        for name, value, error in zip(
            fitted.fit.param_names, fitted.fit.params, fitted.fit.stderr, strict=True
        )
    }
    if not fitted.fit.success or not all(math.isfinite(e) for _, e in values.values()):
        return None
    return values


def judge(claim: dict, runs: list[dict], refits: dict) -> dict:
    """One claim against the runs of its world at its side."""
    family = claim["family"]
    if family == "survival":
        alive = sum(all(e is None for e in r["extinct_at"]) for r in runs)
        return {
            "outcome": "holds" if alive >= claim["at_least"] else "fails",
            "measured": alive,
            "of": len(runs),
        }
    if family == "time":
        key = (claim["world"], claim["side"])
        if key not in refits:
            refits[key] = time_constants(runs, claim["law"])
        if refits[key] is None:
            return {"outcome": "not tested", "why": "the law could not be refitted at this side"}
        value, error = refits[key][claim["constant"]]
        score = (value - claim["predicted"]) / math.sqrt(claim["se"] ** 2 + error**2)
        return {
            "outcome": "holds" if abs(score) <= Z else "fails",
            "measured": laws.signif(value),
            "se": laws.signif(error),
            "score": round(score, 2),
        }
    values = [measured(r, claim) for r in runs]
    if family == "mean":
        mean, error = statistics.fmean(values), statistics.stdev(values) / math.sqrt(len(values))
        score = (mean - claim["predicted"]) / math.sqrt(claim["se"] ** 2 + error**2)
        return {
            "outcome": "holds" if abs(score) <= Z else "fails",
            "measured": laws.signif(mean),
            "se": laws.signif(error),
            "score": round(score, 2),
        }
    spread = statistics.stdev(values)
    low, high = claim["accept"]
    result = {"outcome": "holds" if low <= spread <= high else "fails", "measured": spread}
    if spread > 0:
        own = 1.0 / (2 * (len(values) - 1))
        result["measured"] = laws.signif(spread)
        result["score"] = round(
            math.log(spread / claim["predicted"]) / math.sqrt(claim["se_log"] ** 2 + own), 2
        )
    return result


def reported(runs: list[dict], refit: dict | None, rare: int | None) -> dict:
    """What is reported of one world at one side without a prediction: the starts that lost each
    species, the contested share of births, the law against time as refitted (every constant),
    and of the rare species (number `rare`, from 1) the range of its cells at the end, what
    divides every count (4 for blocks) and the sampled generation its counts last changed
    before."""
    out = {
        "starts": len(runs),
        "starts_losing_each_species": [
            sum(r["extinct_at"][i] is not None for r in runs) for i in range(len(runs[0]["alive"]))
        ],
        "contested_share_of_births": round(
            sum(r["contested"] for r in runs) / max(sum(sum(r["births"]) for r in runs), 1), 4
        ),
    }
    if refit is not None:
        out["live_against_time"] = {
            name: [laws.signif(value), laws.signif(error)] for name, (value, error) in refit.items()
        }
    if rare is not None:
        series = [r["alive"][rare - 1] for r in runs]
        finals = [s[-1] for s in series]
        settled = [max((k for k, v in enumerate(s) if v != s[-1]), default=-1) + 1 for s in series]
        out["rare_species"] = {
            "species": rare,
            "cells_at_the_end": [min(finals), max(finals)],
            "every_count_a_multiple_of": math.gcd(*finals),
            "unchanged_from_generation": runs[0]["generations"][max(settled)],
        }
    return out


def decide(rows: list[dict], registered: list[dict], seeds: tuple[int, ...]) -> dict:
    runs: dict[tuple[str, int], list[dict]] = {}
    for row in rows:
        runs.setdefault((row["world"], row["side"]), []).append(row)
    complete = {key for key, have in runs.items() if sorted(r["seed"] for r in have) == list(seeds)}
    outcomes, details, refits, missing = {}, {}, {}, []
    rare: dict[tuple[str, int], int] = {}
    for claim in registered:
        key = (claim["world"], claim["side"])
        if "species" in claim:
            rare[key] = claim["species"]
        if key not in complete:
            outcomes[claim["label"]] = "missing"
            if f"{key[0]}, side {key[1]}" not in missing:
                missing.append(f"{key[0]}, side {key[1]}")
            continue
        result = judge(claim, runs[key], refits)
        outcomes[claim["label"]] = result.pop("outcome")
        details[claim["label"]] = {"predicted": claim["predicted"], **result}

    def summary(select) -> dict:
        found = [outcomes[c["label"]] for c in registered if select(c)]
        return {word: found.count(word) for word in ("holds", "fails", "not tested", "missing")}

    def word(counts: dict) -> str:
        for name in ("missing", "fails", "not tested"):
            if counts[name]:
                return name
        return "holds"

    families = {f: summary(lambda c, f=f: c["family"] == f) for f in FAMILIES}
    sides = sorted({c["side"] for c in registered})
    return {
        "verdict": {family: word(counts) for family, counts in families.items()},
        "claims": families,
        "by_side": {str(side): summary(lambda c, side=side: c["side"] == side) for side in sides},
        "outcomes": outcomes,
        "details": details,
        "missing": missing,
        "reported": {
            f"{world}, side {side}": reported(
                runs[world, side], refits.get((world, side)), rare.get((world, side))
            )
            for world, side in sorted(complete)
        },
    }


# --- the two studies -----------------------------------------------------------------------------


def build(directory: Path, sides: tuple[int, ...], seeds: tuple[int, ...], where: str) -> Study:
    """The registered study of `sides` from `seeds`, in `directory`."""

    def question() -> dict:
        return {
            "id": Path(directory).name,
            "title": "Do the laws found on grids of side 32 to 256 hold at sides "
            + " and ".join(map(str, sides))
            + "?",  # fmt: skip
            "statement": "Life against HighLife under the standoff, and a five-species soup "
            "under the random draw and under the standoff, each from half-full mixed starts with "
            "equal shares on a wrapped square grid. At each new side the means of the live "
            "fraction, of the species balance, of the mixing and of the rare species' share of "
            "the grid are the constants found at sides 32 to 256; their spreads over the starts "
            "are the fitted amplitudes over the side; every species survives as often as the "
            "density of the rare species' blocks allows; and the live fraction's law against "
            "time settles where it did and as fast.",
            "source": "docs/scale-up-plan.md, step 3; the laws of examples/scale-up-compete",
            "part": where,
            "sides": list(sides),
            "starts": [seeds[0], seeds[-1]],
            "worlds": {
                world: {
                    "rules": list(rules),
                    "tie_break": kind,
                    "generations": steps,
                    "sampled_every": every,
                }
                for world, (rules, kind, steps, every) in laws.WORLDS.items()
            },  # fmt: skip
            "runs": len(jobs(sides, seeds)),
            "level": LEVEL,
            "z": round(Z, 4),
            "laws_sha256": hashlib.sha256(RESULTS.read_bytes()).hexdigest(),
            "sha256": {
                "study.py": hashlib.sha256((Path(directory) / "study.py").read_bytes()).hexdigest(),
                "sizes.py": hashlib.sha256((HERE / "sizes.py").read_bytes()).hexdigest(),
                "laws.py": hashlib.sha256((COMPETE / "laws.py").read_bytes()).hexdigest(),
            },
            "excluded_seen": [
                "The laws themselves (examples/scale-up-compete/laws.py, exploratory): these "
                "worlds at sides 32 to 256 from starts 2001 to 2032. Everything predicted here "
                "comes from them, including the rare species' blocks and the spreads as an "
                "amplitude over the side, which were worked out from the same records on the "
                "day of registration.",
                "The tie-break test and the first look ran the pair on 128 x 128 and this soup "
                "on 64 x 64 (examples/scale-up-tie-break, examples/scale-up-compete).",
                "For timing and memory, Life against HighLife under the standoff and a "
                "five-species soup with other rules (rule set 9001) were stepped a few "
                "generations (16 at most) at sides 512, 1024, 2048 and 4096 from start 9001. "
                "Nothing of their grids was read.",
                "Neither world has been run at any side above 256 beyond that, and this soup "
                "at none. Both parts of this test were registered before either was run.",
            ],
        }

    return Study(
        directory=directory,
        question=question,
        predictions=lambda: predictions(sides, len(seeds)),
        execute=lambda path, workers: execute(path, workers, sides, seeds),
        decide=lambda rows, registered: decide(rows, registered, seeds),
        rerun=lambda record: run_one((record["world"], record["side"], record["seed"])),
    )
