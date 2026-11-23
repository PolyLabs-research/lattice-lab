"""
A registered test: do the large grids agree with each other?

    uv run --no-sync python examples/scale-up-gap/study.py register
    uv run --no-sync python examples/scale-up-gap/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-gap

**Why.** The scale-up test (examples/scale-up-sizes, examples/scale-up-sizes-large) compared
each large grid with a constant fitted on small grids, whose error is several times the large
grid's own, and every claim held. Set against each other instead, the large grids agreed on
eight of nine means. The ninth was the live fraction of Life against HighLife: the registered
sixteen starts at side 2048 came out five of their own standard errors above side 4096's.
Sixteen fresh starts at side 2048 did not, and with both samples together a gap of 0.0002
remained, 0.4% of the value (docs/scale-up-plan.md). The next step of the ladder compares a
world with its zoomed-out self, and a mean that crept with the size of the grid would be in
the way of that, so this settles it first.

**What is run.** Life against HighLife under the standoff, exactly as in the scale-up test:
half-full mixed starts with equal shares on a wrapped square grid, 1,000 generations. Sides
1024, 2048 and 4096, from starts no earlier run used: 384, 96 and 32 of them, which gives the
three sides' mean live fractions about the same standard error (0.000025).

**Predictions**, nine. For each pair of sides, the two sides' means at generation 1,000
differ by less than a margin:

- the live fraction, by less than 0.0002 (0.4% of its value: the gap seen);
- species 1's share of the live cells, by less than 0.0028 (0.5%);
- the unlike share of adjacent live pairs, by less than 0.00053 (2%).

A claim holds when the 99% interval of the difference lies inside its margin (Welch's interval,
for two means with unequal spreads). The numbers of starts were chosen so that sides that
truly agree pass all nine about 98 times in 100, while a real gap of 0.0002 in the live
fraction fails its claim more than 99 times in 100 (`design()`).

Reported without a prediction: each side's mean and spread, every difference, and the live
fraction at generation 200, where the gap first showed.

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

from scipy import stats

HERE = Path(__file__).resolve().parent
SIZES = HERE.parent / "scale-up-sizes"
sys.path.insert(0, str(SIZES))

import sizes  # noqa: E402
from sizes import laws  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

WORLD = "pair standoff"
STARTS = {1024: 384, 2048: 96, 4096: 32}
FIRST = 6001
PAIRS = ((2048, 4096), (1024, 4096), (1024, 2048))
MARGINS = {"live": 0.0002, "share": 0.0028, "unlike": 0.00053}
LEVEL = 0.99
NAMES = {
    "live": "the live fraction",
    "share": "species 1's share of the live cells",
    "unlike": "the unlike share of adjacent live pairs",
}
EARLY = 200  # the generation at which the gap first showed


def seeds(side: int) -> tuple[int, ...]:
    return tuple(range(FIRST, FIRST + STARTS[side]))


def jobs() -> list[tuple[str, int, int]]:
    """Every run, the largest grids first: they are what a rented machine is for, and a run cut
    short can finish the small ones anywhere."""
    return [(WORLD, side, seed) for side in sorted(STARTS, reverse=True) for seed in seeds(side)]


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {
            (r["world"], r["side"], r["seed"])
            for r in map(json.loads, path.read_text().splitlines())
        }
    todo = [job for job in jobs() if job not in done]
    if workers <= 1:
        for job in todo:
            append_records(path, [sizes.run_one(job)])
        return
    with ProcessPoolExecutor(workers) as pool:
        for record in pool.map(sizes.run_one, todo):
            append_records(path, [record])


# --- the statistics ------------------------------------------------------------------------------


def difference(first: list[float], second: list[float], level: float) -> dict:
    """mean(first) - mean(second) and its Welch interval at `level`."""
    na, nb = len(first), len(second)
    va, vb = statistics.variance(first) / na, statistics.variance(second) / nb
    delta, se = statistics.fmean(first) - statistics.fmean(second), math.sqrt(va + vb)
    if se == 0:
        return {"difference": delta, "se": 0.0, "low": delta, "high": delta}
    freedom = (va + vb) ** 2 / (va**2 / (na - 1) + vb**2 / (nb - 1))
    reach = float(stats.t.ppf(1 - (1 - level) / 2, freedom)) * se
    return {"difference": delta, "se": se, "low": delta - reach, "high": delta + reach}


def design() -> dict:
    """What the numbers of starts were chosen to give, from the spreads the scale-up test
    found: each difference's standard error, and the chance that two sides that truly agree
    pass their claim. A real gap as large as a margin passes its claim once in 200 tries,
    whatever the standard error: that is what a 99% interval means."""
    spreads = {  # one start's spread at side 1024: the laws' amplitude over the side, or what
        "live": 0.536047 / 1024,  # the larger sides measured where that was more
        "share": 0.0065,
        "unlike": 0.00112,
    }
    z = float(stats.norm.ppf(1 - (1 - LEVEL) / 2))
    out: dict = {"passes_if_the_gap_is_the_margin": round(float(stats.norm.cdf(-z)), 4)}
    for quantity, at_1024 in spreads.items():
        row = {}
        for a, b in PAIRS:
            se = math.hypot(
                at_1024 * 1024 / a / math.sqrt(STARTS[a]), at_1024 * 1024 / b / math.sqrt(STARTS[b])
            )
            room = (MARGINS[quantity] - z * se) / se
            row[f"{a} and {b}"] = {
                "se": laws.signif(se, 3),
                "passes_if_the_sides_agree": round(2 * float(stats.norm.cdf(room)) - 1, 4),
            }
        out[quantity] = row
    return out


# --- the predictions and the verdict -------------------------------------------------------------


def predictions() -> list[dict]:
    out = []
    for quantity, margin in MARGINS.items():
        for a, b in PAIRS:
            out.append(
                {
                    "label": f"{quantity}, sides {a} and {b}",
                    "quantity": quantity,
                    "sides": [a, b],
                    "claim": f"the means of {NAMES[quantity]} at generation 1,000 at sides {a} "
                    f"and {b} differ by less than {margin}: the {LEVEL:.0%} interval of the "
                    "difference lies inside that margin",
                    "margin": margin,
                    "level": LEVEL,
                }
            )
    return out


def at_generation(record: dict, quantity: str, generation: int) -> float:
    return laws.measure(record, quantity, record["generations"].index(generation))


def _round(result: dict) -> dict:
    return {k: laws.signif(v) if isinstance(v, float) else v for k, v in result.items()}


def decide(rows: list[dict], registered: list[dict]) -> dict:
    runs: dict[int, list[dict]] = {}
    for row in rows:
        runs.setdefault(row["side"], []).append(row)
    complete = {
        side
        for side, have in runs.items()
        if side in STARTS and sorted(r["seed"] for r in have) == list(seeds(side))
    }
    missing = [f"side {side}" for side in sorted(STARTS) if side not in complete]
    outcomes, differences = {}, {}
    for claim in registered:
        a, b = claim["sides"]
        if a not in complete or b not in complete:
            outcomes[claim["label"]] = "missing"
            continue
        first = [laws.measure(r, claim["quantity"], -1) for r in runs[a]]
        second = [laws.measure(r, claim["quantity"], -1) for r in runs[b]]
        result = difference(first, second, claim["level"])
        inside = -claim["margin"] < result["low"] and result["high"] < claim["margin"]
        outcomes[claim["label"]] = "holds" if inside else "fails"
        differences[claim["label"]] = {**_round(result), "margin": claim["margin"]}

    def overall(quantity: str) -> str:
        found = {outcomes[c["label"]] for c in registered if c["quantity"] == quantity}
        for word in ("missing", "fails"):
            if word in found:
                return word
        return "holds"

    means, early = {}, {}
    for side in sorted(complete):
        for quantity in MARGINS:
            values = [laws.measure(r, quantity, -1) for r in runs[side]]
            means.setdefault(quantity, {})[str(side)] = {
                "starts": len(values),
                "mean": laws.signif(statistics.fmean(values)),
                "se": laws.signif(statistics.stdev(values) / math.sqrt(len(values))),
                "spread": laws.signif(statistics.stdev(values)),
            }
        values = [at_generation(r, "live", EARLY) for r in runs[side]]
        early[str(side)] = [
            laws.signif(statistics.fmean(values)),
            laws.signif(statistics.stdev(values) / math.sqrt(len(values))),
        ]
    early_gaps = {
        f"sides {a} and {b}": _round(
            difference(
                [at_generation(r, "live", EARLY) for r in runs[a]],
                [at_generation(r, "live", EARLY) for r in runs[b]],
                LEVEL,
            )
        )
        for a, b in PAIRS
        if a in complete and b in complete
    }
    return {
        "verdict": {quantity: overall(quantity) for quantity in MARGINS},
        "outcomes": outcomes,
        "differences": differences,
        "missing": missing,
        "means": means,
        "reported": {
            "live_fraction_at_generation": EARLY,
            "means": early,
            "differences": early_gaps,
            "starts_losing_a_species": {
                str(side): sum(any(e is not None for e in r["extinct_at"]) for r in runs[side])
                for side in sorted(complete)
            },
        },
    }


def question() -> dict:
    rules, kind, steps, every = laws.WORLDS[WORLD]
    return {
        "id": "scale-up-gap",
        "title": "Do the large grids agree with each other?",
        "statement": "Life against HighLife under the standoff, from half-full mixed starts with "
        "equal shares on a wrapped square grid, at sides 1024, 2048 and 4096 from fresh starts. "
        "At generation 1,000 the three sides' means agree, pair by pair, within a margin: 0.0002 "
        "for the live fraction (the gap the scale-up test showed between sides 2048 and 4096), "
        "0.0028 for species 1's share of the live cells and 0.00053 for the unlike share of "
        "adjacent live pairs.",
        "source": "docs/scale-up-plan.md, decision D7; examples/scale-up-sizes-large",
        "world": {
            "name": WORLD,
            "rules": list(rules),
            "tie_break": kind,
            "generations": steps,
            "sampled_every": every,
        },  # fmt: skip
        "starts": {str(side): [seeds(side)[0], seeds(side)[-1]] for side in sorted(STARTS)},
        "runs": len(jobs()),
        "margins": MARGINS,
        "level": LEVEL,
        "interval": "Welch's interval for the difference of two means, the smaller side minus "
        "the larger",
        "design": design(),
        "sha256": {
            "study.py": hashlib.sha256((HERE / "study.py").read_bytes()).hexdigest(),
            "sizes.py": hashlib.sha256((SIZES / "sizes.py").read_bytes()).hexdigest(),
            "laws.py": hashlib.sha256(
                (SIZES.parent / "scale-up-compete" / "laws.py").read_bytes()
            ).hexdigest(),
        },  # fmt: skip
        "excluded_seen": [
            "The scale-up test's registered runs of this world: sides 512 and 1024 from starts "
            "3001 to 3032, sides 2048 and 4096 from starts 4001 to 4016. They are what prompted "
            "this test: the side-2048 sample's live fraction at generation 1,000 was 0.04861 "
            "against 0.04827 at side 4096, five of their own standard errors apart.",
            "The re-check (examples/scale-up-sizes/recheck.py): sixteen starts at side 2048, "
            "5001 to 5016, which gave 0.04833. With them the gap between sides 2048 and 4096 is "
            "0.0002, which is the margin registered here for the live fraction.",
            "The laws at sides 32 to 256 from starts 2001 to 2032, the tie-break test and the "
            "first look (starts 101 to 228 and 9001 on). The spreads seen in all of these set "
            "the numbers of starts and the margins for the species balance and the mixing.",
            "For timing, and to check the rented machine, a few generations at these sides from "
            "start 9001, and registered records of the scale-up test computed again.",
            "No start of this test (6001 on) has been generated or run at any side.",
        ],
    }


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    return sizes.run_one((record["world"], record["side"], record["seed"]))


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
