"""
A registered test: does the birth tie-break change what a world of several species does?

    uv run --no-sync python examples/scale-up-tie-break/study.py register
    uv run --no-sync python examples/scale-up-tie-break/study.py run --workers 1
    uv run --no-sync lattice-lab verify --lab examples/scale-up-tie-break

**The idea.** With several species a dead cell can be due a birth of more than one of them, and
LatticeLife's tie-break says who gets it (docs/scale-up-plan.md). It always was a random draw;
since 2026-11-23 it can also be a standoff, in which the cell stays empty and the world becomes
a function of its grid. Before the standoff is used as a second world, this asks whether the
choice changes anything that can be measured, in the two kinds of world a first look found
(examples/scale-up-compete, exploratory, the draw only):

- **Life-like pairs**, where a contest is rare (0.4% of births): Conway's Life against itself
  and against HighLife;
- **soups**, where it need not be: five species with rules drawn as `latticelife autorun` draws
  them, in which contests were from 0.3% to 75% of births.

Every world is a wrapped square grid, half full at the start, the species in equal shares, run
under the draw (`random`) and under the standoff from the same starts.

**Predictions**, one ledger entry each:

- *S, a known answer.* Two species with the same rule are interchangeable, so under either
  tie-break species 1's share of the live cells averages one half. Tested on Life against
  itself at generation 600, at the 99.9% level.
- *A, no difference where contests are rare.* For both pairs the standoff's mean and the draw's
  differ by less than a margin: for the live fraction at generations 100, 300 and 600 (a tenth
  of what the first look found), for species 1's share at 600 (0.07) and for the unlike share
  of adjacent live pairs at 600 (0.0075). A claim holds when the 99% interval of the difference
  lies inside the margin.
- *B, a clear difference where contests are common.* The 24 soups are sorted by the share of
  births that are contested under the draw, in this run: common (a fifth or more) or rare (a
  hundredth or less).
  - B0: in every soup where contests are rare, the live fraction at generation 200 differs by
    less than 0.02.
  - B1: in at least three quarters of the soups where contests are common, it differs (the
    99% interval excludes 0).
  - B2: in at least half of those, the standoff lowers it by more than 0.02.

Reported without a prediction: every soup's difference against its contested share, and the
species left under each tie-break.

Intervals are Welch's, for two means with unequal spreads. Both tie-breaks run from the same
starts, which the interval ignores; that can only make it wider.

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

from latticelife.experiments.competition import CompetitionTask, competition_point
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scale-up-compete"))

from first_look import HIGHLIFE, LIFE, soup_rules  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

KINDS = ("random", "standoff")
PAIRS = {"life-life": (LIFE, LIFE), "life-highlife": (LIFE, HIGHLIFE)}
PAIR_SIDE, PAIR_STEPS, PAIR_SEEDS = 128, 600, tuple(range(101, 229))  # 128 starts
SOUP_SIDE, SOUP_STEPS, SOUP_SEEDS = 64, 200, tuple(range(101, 165))  # 64 starts
SOUP_SETS = tuple(range(1, 25))
SAMPLE_EVERY = 100

LEVEL, KNOWN_LEVEL = 0.99, 0.999
# A: the margins. For the live fraction, a tenth of the first look's mean under the draw.
MARGINS = {
    "life-life": {"live@100": 0.0105, "live@300": 0.0070, "live@600": 0.0060},
    "life-highlife": {"live@100": 0.0109, "live@300": 0.0067, "live@600": 0.0055},
}
SHARE_MARGIN, UNLIKE_MARGIN = 0.07, 0.0075
# B: what counts as common and as rare, and as a difference.
COMMON, RARE, EFFECT = 0.20, 0.01, 0.02
B1_SHARE, B2_SHARE = 0.75, 0.5
MIN_COMMON, MIN_RARE = 6, 2


def worlds() -> dict[str, dict]:
    """Every world of the study, by name: its rules, its side, its length and its starts."""
    out = {
        name: {"rules": list(rules), "side": PAIR_SIDE, "steps": PAIR_STEPS, "seeds": PAIR_SEEDS}
        for name, rules in PAIRS.items()
    }
    for index in SOUP_SETS:
        out[f"soup-{index:02d}"] = {
            "rules": list(soup_rules(index)),
            "side": SOUP_SIDE,
            "steps": SOUP_STEPS,
            "seeds": SOUP_SEEDS,
        }
    return out


def run_one(job: tuple[str, str, int]) -> dict:
    """One world under one tie-break from one start, as its record."""
    name, kind, seed = job
    world = worlds()[name]
    task = CompetitionTask(
        tuple(world["rules"]),
        "square",
        world["side"],
        0.5,
        seed,
        world["steps"],
        tie_break=kind,
        sample_every=SAMPLE_EVERY,
    )
    record = competition_point(task)
    return {
        "world": name,
        "kind": kind,
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


def jobs() -> list[tuple[str, str, int]]:
    """Every run, the pairs (the slowest) first."""
    return [
        (name, kind, seed)
        for name, world in worlds().items()
        for kind in KINDS
        for seed in world["seeds"]
    ]


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {
            (r["world"], r["kind"], r["seed"])
            for r in map(json.loads, path.read_text().splitlines())
        }
    todo = [job for job in jobs() if job not in done]
    if workers <= 1:
        for job in todo:
            append_records(path, [run_one(job)])
        return
    with ProcessPoolExecutor(workers) as pool:
        for record in pool.map(run_one, todo, chunksize=8):
            append_records(path, [record])


# --- what a record measures ----------------------------------------------------------------------


def observe(record: dict, observable: str) -> float:
    """`live@g`, the live fraction at generation g; `share_1@g`, species 1's share of the live
    cells; `unlike@g`, the share of adjacent live pairs that are of two species; `contested`,
    the share of the run's births that were contested."""
    if observable == "contested":
        return record["contested"] / max(sum(record["births"]), 1)
    name, generation = observable.split("@")
    at = record["generations"].index(int(generation))
    alive = [series[at] for series in record["alive"]]
    if name == "live":
        return sum(alive) / record["cells"]
    if name == "share_1":
        return alive[0] / max(sum(alive), 1)
    if name == "unlike":
        return record["unlike"][at] / max(record["unlike"][at] + record["like"][at], 1)
    raise ValueError(f"unknown observable {observable!r}")


def mean_interval(values: list[float], level: float) -> dict:
    """The mean of `values` and its Student interval at `level`."""
    n, mean = len(values), statistics.fmean(values)
    se = statistics.stdev(values) / math.sqrt(n)
    reach = stats.t.ppf(1 - (1 - level) / 2, n - 1) * se
    return {"n": n, "mean": mean, "se": se, "low": mean - reach, "high": mean + reach}


def difference(first: list[float], second: list[float], level: float) -> dict:
    """mean(second) - mean(first) and its Welch interval at `level`."""
    na, nb = len(first), len(second)
    va, vb = statistics.variance(first) / na, statistics.variance(second) / nb
    delta, se = statistics.fmean(second) - statistics.fmean(first), math.sqrt(va + vb)
    if se == 0:
        return {"difference": delta, "se": 0.0, "low": delta, "high": delta}
    freedom = (va + vb) ** 2 / (va**2 / (na - 1) + vb**2 / (nb - 1))
    reach = stats.t.ppf(1 - (1 - level) / 2, freedom) * se
    return {"difference": delta, "se": se, "low": delta - reach, "high": delta + reach}


def _round(result: dict) -> dict:
    return {k: round(v, 6) if isinstance(v, float) else v for k, v in result.items()}


# --- the predictions -----------------------------------------------------------------------------


def predictions() -> list[dict]:
    out = []
    for kind in KINDS:
        out.append(
            {
                "label": f"S {kind}",
                "claim": "S",
                "world": "life-life",
                "kind": kind,
                "observable": "share_1@600",
                "predicted": "two species with the same rule end level: species 1's share of the "
                "live cells averages one half",
                "level": KNOWN_LEVEL,
            }
        )
    for name in PAIRS:
        margins = {**MARGINS[name], "share_1@600": SHARE_MARGIN, "unlike@600": UNLIKE_MARGIN}
        for observable, margin in margins.items():
            out.append(
                {
                    "label": f"A {name} {observable}",
                    "claim": "A",
                    "world": name,
                    "observable": observable,
                    "predicted": "no difference: the standoff's mean and the draw's differ by "
                    "less than the margin",
                    "margin": margin,
                    "level": LEVEL,
                }
            )
    soups = [name for name in worlds() if name.startswith("soup-")]
    common = {
        "claim": "B",
        "worlds": soups,
        "observable": "live@200",
        "sorted_by": "the share of births contested under the draw, in this run",
        "level": LEVEL,
        "effect": EFFECT,
    }
    out.append(
        {
            **common,
            "label": "B0",
            "predicted": "in every soup where contests are rare (a hundredth of births or "
            "less), the live fraction differs by less than the effect",
            "rare": RARE,
            "at_least_soups": MIN_RARE,
        }
    )
    out.append(
        {
            **common,
            "label": "B1",
            "predicted": "in at least three quarters of the soups where contests are common (a "
            "fifth of births or more), the live fraction differs: the interval excludes 0",
            "common": COMMON,
            "share_of_soups": B1_SHARE,
            "at_least_soups": MIN_COMMON,
        }
    )
    out.append(
        {
            **common,
            "label": "B2",
            "predicted": "in at least half of the soups where contests are common, the standoff "
            "lowers the live fraction by more than the effect",
            "common": COMMON,
            "share_of_soups": B2_SHARE,
            "at_least_soups": MIN_COMMON,
        }
    )
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    runs: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        runs.setdefault((row["world"], row["kind"]), []).append(row)
    expected = worlds()
    missing = [
        f"{name} {kind}"
        for name, world in expected.items()
        for kind in KINDS
        if {r["seed"] for r in runs.get((name, kind), [])} != set(world["seeds"])
    ]

    def values(name: str, kind: str, observable: str) -> list[float]:
        return [observe(r, observable) for r in runs[name, kind]]

    def complete(name: str) -> bool:
        return not any(m.startswith(name + " ") for m in missing)

    outcomes: dict[str, str] = {}
    known, pairs = {}, {}
    for claim in registered:
        label = claim["label"]
        if claim["claim"] == "S":
            if not complete(claim["world"]):
                outcomes[label] = "missing"
                continue
            result = mean_interval(
                values(claim["world"], claim["kind"], claim["observable"]), claim["level"]
            )
            outcomes[label] = "holds" if result["low"] <= 0.5 <= result["high"] else "fails"
            known[claim["kind"]] = _round(result)
        elif claim["claim"] == "A":
            if not complete(claim["world"]):
                outcomes[label] = "missing"
                continue
            result = difference(
                values(claim["world"], "random", claim["observable"]),
                values(claim["world"], "standoff", claim["observable"]),
                claim["level"],
            )
            inside = -claim["margin"] < result["low"] and result["high"] < claim["margin"]
            outcomes[label] = "holds" if inside else "fails"
            pairs.setdefault(claim["world"], {})[claim["observable"]] = {
                **_round(result),
                "margin": claim["margin"],
            }

    soups = []
    for name in (n for n in expected if n.startswith("soup-")):
        if not complete(name):
            continue
        result = difference(
            values(name, "random", "live@200"), values(name, "standoff", "live@200"), LEVEL
        )
        left = {
            kind: statistics.fmean(
                sum(e is None for e in r["extinct_at"]) for r in runs[name, kind]
            )
            for kind in KINDS
        }
        soups.append(
            {
                "world": name,
                "rules": expected[name]["rules"],
                "contested": statistics.fmean(values(name, "random", "contested")),
                "live_random": statistics.fmean(values(name, "random", "live@200")),
                **result,
                "species_left": {kind: round(v, 2) for kind, v in left.items()},
            }
        )
    all_soups = len(soups) == sum(name.startswith("soup-") for name in expected)
    rare = [s for s in soups if s["contested"] <= RARE]
    common = [s for s in soups if s["contested"] >= COMMON]
    differs = [s for s in common if s["low"] > 0 or s["high"] < 0]
    lowered = [s for s in common if s["high"] < -EFFECT]
    level = [s for s in rare if -EFFECT < s["low"] and s["high"] < EFFECT]

    def soup_claim(enough: bool, holds: bool) -> str:
        if not all_soups:
            return "missing"
        if not enough:
            return "not tested"
        return "holds" if holds else "fails"

    outcomes["B0"] = soup_claim(len(rare) >= MIN_RARE, len(level) == len(rare))
    outcomes["B1"] = soup_claim(len(common) >= MIN_COMMON, len(differs) >= B1_SHARE * len(common))
    outcomes["B2"] = soup_claim(len(common) >= MIN_COMMON, len(lowered) >= B2_SHARE * len(common))

    def overall(claim: str) -> str:
        found = {outcomes[c["label"]] for c in registered if c["claim"] == claim}
        for word in ("missing", "fails", "not tested"):
            if word in found:
                return word
        return "holds"

    return {
        "verdict": {claim: overall(claim) for claim in ("S", "A", "B")},
        "outcomes": outcomes,
        "missing": missing,
        "known_answer": known,
        "pairs": pairs,
        "soups": {
            "rare": len(rare),
            "rare_level": len(level),
            "common": len(common),
            "common_differ": len(differs),
            "common_lowered": len(lowered),
            "table": [_round(s) for s in sorted(soups, key=lambda s: s["contested"])],
        },
    }


def question() -> dict:
    return {
        "id": "scale-up-tie-break",
        "title": "Does the birth tie-break change what a world of several species does?",
        "statement": "Life-like pairs and five-species soups on wrapped square grids, half full "
        "at the start with the species in equal shares, are run under the random draw and under "
        "the standoff from the same starts. Identical species end level under both (S). Where "
        "contests are rare the two tie-breaks give the same live fraction, species balance and "
        "mixing (A, and B0 for soups). Where contests are common the standoff changes the live "
        "fraction, and lowers it (B1, B2).",
        "source": "docs/scale-up-plan.md, decision D1; the first look in examples/scale-up-compete",
        "worlds": {
            name: {
                "rules": w["rules"],
                "side": w["side"],
                "generations": w["steps"],
                "starts": [w["seeds"][0], w["seeds"][-1]],
            }
            for name, w in worlds().items()
        },  # fmt: skip
        "tie_breaks": list(KINDS),
        "runs": len(jobs()),
        "intervals": "Welch's interval for the difference of two means (standoff minus draw), "
        "Student's for one mean; 99%, and 99.9% for the known answer S",
        "sha256": {
            "study.py": hashlib.sha256((HERE / "study.py").read_bytes()).hexdigest(),
            "first_look.py": hashlib.sha256(
                (HERE.parent / "scale-up-compete" / "first_look.py").read_bytes()
            ).hexdigest(),
        },
        "excluded_seen": [
            "The first look (examples/scale-up-compete, exploratory), under the draw only: the "
            "two pairs on 128 x 128 from starts 9001 to 9016, and soups from rule sets 9001 to "
            "9012 and starts 9001 to 9008. The margins and thresholds here were set from its "
            "means and spreads. No registered start or rule set is among them.",
            "Two earlier counts of contested births, under the draw only: Life against itself "
            "and against HighLife on 256 x 256, and 24 autorun sessions with autorun's own "
            "random rules.",
            "Under the standoff: one run of Life against HighLife on 128 x 128 from start 1 for "
            "500 generations (the example in LatticeLife's docs), of which only that neither "
            "species died out was read; and three autorun sessions with autorun's own random "
            "rules, of which only the schema and the total of contested cells were read. "
            "LatticeLife's tests and this study's run both tie-breaks on grids of side 16 to 32 "
            "from other starts.",
            "No registered world has been run under either tie-break. The registered soups' "
            "rules (sets 1 to 24) were generated to write this entry, and nothing was run on "
            "them.",
        ],
    }


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    return run_one((record["world"], record["kind"], record["seed"]))


STUDY = Study(
    directory=HERE,
    question=question,
    predictions=predictions,
    execute=execute,
    decide=decide,
    rerun=rerun,
)

if __name__ == "__main__":
    main(STUDY)
