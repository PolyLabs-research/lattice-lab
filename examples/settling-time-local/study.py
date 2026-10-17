"""
Round 2 of the B2/S34 settling-time study: what the local settling times say.

    uv run python examples/settling-time-local/study.py register
    uv run python examples/settling-time-local/study.py run --workers 4
    uv run lattice-lab verify --lab examples/settling-time-local

Study A (examples/settling-time-replication) found B2/S34's median settling time on hexagon tori
logarithmic in L, with a seed-to-seed spread too narrow for its slope: an interquartile range of
20.0 against a slope of 31.4 per ln L, a ratio of 0.64 where the largest of independent,
identically distributed local times gives 0.786 whatever their tail (docs/settling-time.md,
correction). A post-hoc idea was a tail prefactor, t^k e^(-t/tau) with k of about 3, fading as L
grows. That can bend the slope but cannot narrow the spread, and the global data alone do not fix
k (the quantile model prefers k = 0 but allows 3).

LatticeLife's local transients (experiments.local) measure the local times directly: for every
8 x 8 and 16 x 16 block of the torus, the generation it enters the soup's final cycle. This study
runs fresh soups (seeds from 101) on tori of 1024 (60 soups, 16384 blocks of 8 each) and 256
(320 soups, 1024 blocks each), and tests, with predictions fixed from Study A's
data before any local transient of B2/S34 was computed:

- k: the local tail's prefactor. Plain extreme values say k = 0; the fading correction says the
  hazard rises along the tail, k > 0 (its post-hoc size, 2.85, is reported, not tested: a fitted
  k depends on the exact form of the tail, while the hazard's rise does not).
- Which global number the local tail accounts for: its effective scale at the global settling
  time, 1 / hazard(210), against the spread (IQR / 1.5725 = 12.7) and the slope (slope / 2 = 15.7).
- Stationarity: the local tail is the same on tori of 256 and 1024 (any independent, identically
  distributed account needs it).
- Independence: the global settling time reconstructed from the local tail as the largest of
  16384 independent blocks matches Study A's measured median and spread at 1024.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from latticelife.config import DEFAULT_CONFIG_PATH, load_config
from latticelife.core.rules import Rule
from latticelife.experiments.local import run_local
from latticelife.experiments.observables import median_transient
from scipy import stats

from lattice_lab import extremes
from lattice_lab.ledger import Ledger
from lattice_lab.study import Study, main

HERE = Path(__file__).resolve().parent
STUDY_A = HERE.parent / "settling-time-replication" / "ledger.jsonl"
EXAMPLE_LAB = HERE.parent / "lab-b2s34" / "records" / "settling-time-hexagon-B2S34-0.jsonl"
RULE, SHAPE, DENSITY, STEPS = "B2/S34", "hexagon", 0.5, 4000
RUNS = {1024: list(range(101, 161)), 256: list(range(101, 421))}
BLOCKS = (8, 16)
ALPHA = 0.01
Z = stats.norm.isf(ALPHA / 2)
TAIL_QUANTILE = 0.99  # t_min: the 99th percentile of the pooled block transients at 1024
GLOBAL_T = 210.0  # Study A's median settling time at 1024
FADING_K = 2.85  # the post-hoc estimate (docs/settling-time.md)


def study_a_times() -> dict:
    """Every seed's settling time: the example lab (64 to 128) and Study A (192 to 1024)."""
    lab = [json.loads(line) for line in EXAMPLE_LAB.read_text().splitlines()]
    rows = Ledger(STUDY_A).entries[-2]["body"]["rows"]
    return {
        int(r.grid): r.settling_times
        for r in median_transient(lab + rows)
        if r.complete and int(r.grid) >= 64
    }


def study_a_numbers() -> dict:
    verdict = Ledger(STUDY_A).entries[-1]["body"]
    per = verdict["fluctuations"]
    sizes = sorted(int(n) for n in per)
    fl = extremes.fluctuations({n: study_a_times()[n] for n in sizes})
    slope, slope_se = extremes.weighted_slope(
        np.log(sizes), [fl[n]["median"] for n in sizes], [fl[n]["median_error"] for n in sizes]
    )
    iqr, iqr_se = extremes.weighted_mean(
        [fl[n]["iqr"] for n in sizes], [fl[n]["iqr_error"] for n in sizes]
    )
    return {
        "sizes": sizes,
        "slope": slope,
        "slope_se": slope_se,
        "iqr": iqr,
        "iqr_se": iqr_se,
        "median_1024": fl[1024]["median"],
        "median_1024_se": fl[1024]["median_error"],
        "iqr_1024": fl[1024]["iqr"],
        "iqr_1024_se": fl[1024]["iqr_error"],
    }


def question() -> dict:
    return {
        "id": "settling-time-hexagon-B2S34-local",
        "title": "Do B2/S34's local settling times explain its global spread and slope?",
        "rule": RULE,
        "shape": SHAPE,
        "density": DENSITY,
        "runs": {str(n): seeds for n, seeds in RUNS.items()},
        "blocks": list(BLOCKS),
        "steps": STEPS,
        "earlier": [
            "examples/lab-b2s34/ledger.jsonl",
            "examples/settling-time-replication/ledger.jsonl",
        ],
        "instrument": "latticelife.experiments.local (LatticeLife 256450b): each block's local "
        "transient, the largest of which is the global transient (checked on every run)",
        "tail": f"t_min = the {TAIL_QUANTILE:.0%} quantile (rounded down) of the pooled 8 x 8 "
        "local transients at 1024; the same t_min at 256. Tail model: survival "
        "(t/tau)^k e^(-t/tau), fitted by maximum likelihood on the discrete conditional "
        "distribution above t_min (lattice_lab.extremes.fit_tail); errors from resampling "
        "whole soups (400 resamples)",
        "alpha": ALPHA,
    }


def predictions() -> list[dict]:
    a = study_a_numbers()
    times = study_a_times()
    plain = extremes.fit_prefactor_model(times)
    fading = extremes.fit_prefactor_model(times, fix_k=FADING_K)
    spread_scale = a["iqr"] / extremes.GUMBEL_IQR
    spread_scale_se = a["iqr_se"] / extremes.GUMBEL_IQR
    slope_scale, slope_scale_se = a["slope"] / 2, a["slope_se"] / 2
    return [
        {
            "claim": "k, plain extreme values",
            "from": "the quantile model fitted to every seed at 64 to 1024, k free (best k = 0)",
            "global_fit": plain,
            "k": 0.0,
            "decision": "consistent when the local tail's k (8 x 8 blocks, 1024) is within 2.576 "
            "of its bootstrap errors of 0",
        },
        {
            "claim": "k, fading correction",
            "from": "the post-hoc estimate; the quantile model with k fixed at 2.85 has the tau "
            "given",
            "global_fit": fading,
            "k": FADING_K,
            "decision": "consistent when the local tail's k is above 0 by more than 2.326 of its "
            "bootstrap errors (one-sided at 1%): the hazard rises along the tail. Its size is "
            "compared with 2.85 for the record only",
        },
        {
            "claim": "the local tail accounts for the spread",
            "tau_eff_at": GLOBAL_T,
            "tau_eff": spread_scale,
            "tau_eff_se": spread_scale_se,
            "from": "Study A's interquartile range at 192 to 1024 divided by Gumbel's 1.5725",
            "decision": "consistent when the local tail's 1 / hazard at t = 210 equals tau_eff, "
            "two-sided at 1%, errors combined",
        },
        {
            "claim": "the local tail accounts for the slope",
            "tau_eff_at": GLOBAL_T,
            "tau_eff": slope_scale,
            "tau_eff_se": slope_scale_se,
            "from": "half of Study A's slope of the median in ln L at 192 to 1024",
            "decision": "as above, against tau_eff",
        },
        {
            "claim": "stationarity",
            "difference": 0.0,
            "decision": "the mean excess of the 8 x 8 local transients above t_min is the same at "
            "256 and 1024: consistent when their difference is within 2.576 of its error "
            "(both from resampling whole soups)",
        },
        {
            "claim": "independence",
            "median_1024": a["median_1024"],
            "median_1024_se": a["median_1024_se"],
            "iqr_1024": a["iqr_1024"],
            "iqr_1024_se": a["iqr_1024_se"],
            "decision": "the global settling time as the largest of 16384 independent 8 x 8 "
            "blocks, each with the measured tail (survival 1% at t_min, then the fitted form): "
            "its median and interquartile range equal Study A's at 1024 (each two-sided at 1%, "
            "bootstrap and Study A's errors combined)",
        },
    ]


def execute(path: Path, workers: int) -> None:
    config = load_config(DEFAULT_CONFIG_PATH)
    rule = Rule.from_bs_string(RULE)
    for size, seeds in RUNS.items():
        print(f"local transients: {size} x {size}, {len(seeds)} soups", file=sys.stderr)
        for _ in run_local(
            config, rule, SHAPE, [size], [DENSITY], seeds, STEPS, str(path), BLOCKS, workers
        ):
            pass


def _groups(rows: list[dict], size: int, block: int) -> list[np.ndarray]:
    return [
        np.asarray(r["local"][str(block)], dtype=float)
        for r in rows
        if r["grid"] == size and r["local"] is not None
    ]


def _reconstruct(fit: dict, n_blocks: int, tail_mass: float) -> dict:
    """Median and interquartile range of the largest of n_blocks independent blocks whose
    survival is tail_mass at t_min and follows the fitted form beyond it."""

    def quantile(p, tau, k):
        target = -math.log(p) / (n_blocks * tail_mass)  # S(t) / S(t_min)

        def log_ratio(t):
            return k * math.log(t / fit["t_min"]) - (t - fit["t_min"]) / tau

        from scipy import optimize

        return optimize.brentq(lambda t: log_ratio(t) - math.log(target), fit["t_min"], 5000.0)

    def stats_for(tau, k):
        q25, q50, q75 = (quantile(p, tau, k) for p in (0.25, 0.5, 0.75))
        return q50, q75 - q25

    median, iqr = stats_for(fit["tau"], fit["k"])
    draws = np.array([stats_for(t, k) for t, k in fit["draws"]])
    return {
        "median": median,
        "median_se": float(draws[:, 0].std(ddof=1)),
        "iqr": iqr,
        "iqr_se": float(draws[:, 1].std(ddof=1)),
    }


def decide(rows: list[dict], registered: list[dict]) -> dict:
    claims = {p["claim"]: p for p in registered}
    big, small = _groups(rows, 1024, 8), _groups(rows, 256, 8)
    pooled = np.concatenate(big)
    t_min = float(math.floor(np.quantile(pooled, TAIL_QUANTILE)))
    tail = extremes.fit_tail(big, t_min)
    tail_small = extremes.fit_tail(small, t_min)
    big16 = _groups(rows, 1024, 16)
    t_min16 = float(math.floor(np.quantile(np.concatenate(big16), TAIL_QUANTILE)))
    tail16 = extremes.fit_tail(big16, t_min16)
    eff, eff_se = extremes.tail_tau_eff(tail, GLOBAL_T)
    out = {"t_min": t_min, "blocks_1024": int(len(pooled)), "blocks_256": int(sum(map(len, small)))}

    def summary(fit):
        return {k: v for k, v in fit.items() if k != "draws"}

    out["tail"] = {
        "1024, 8": summary(tail),
        "256, 8": summary(tail_small),
        "1024, 16": summary(tail16),
    }
    out["tau_eff_at_210"] = {"value": eff, "error": eff_se}
    tests = {}
    tests["k, plain extreme values"] = extremes.z_test(tail["k"], tail["k_se"], 0.0)
    rises = tail["k"] / tail["k_se"]
    tests["k, fading correction"] = {
        "observed": tail["k"],
        "error": tail["k_se"],
        "z_above_0": rises,
        "passes": rises > stats.norm.isf(ALPHA),
        "against_2.85": extremes.z_test(tail["k"], tail["k_se"], FADING_K),
    }
    for name in ("the local tail accounts for the spread", "the local tail accounts for the slope"):
        c = claims[name]
        tests[name] = extremes.z_test(eff, eff_se, c["tau_eff"], c["tau_eff_se"])
    me_big = extremes.mean_excess(big, t_min)
    me_small = extremes.mean_excess(small, t_min)
    tests["stationarity"] = extremes.z_test(
        me_big[0] - me_small[0], math.hypot(me_big[1], me_small[1]), 0.0
    )
    out["mean_excess"] = {"1024": me_big, "256": me_small}
    tail_mass = float(np.mean(pooled >= t_min))
    rebuilt = _reconstruct(tail, 1024 * 1024 // 64, tail_mass)
    c = claims["independence"]
    tests["independence: median"] = extremes.z_test(
        rebuilt["median"], rebuilt["median_se"], c["median_1024"], c["median_1024_se"]
    )
    tests["independence: iqr"] = extremes.z_test(
        rebuilt["iqr"], rebuilt["iqr_se"], c["iqr_1024"], c["iqr_1024_se"]
    )
    out["reconstructed_1024"] = {**rebuilt, "tail_mass": tail_mass}
    out["tests"] = tests
    out["global_transients"] = {
        str(n): sorted(r["transient"] for r in rows if r["grid"] == n) for n in RUNS
    }
    # clustering of late blocks: of the 8 x 8 blocks above t_min, the share with a neighbouring
    # block (left, right, up or down, on the torus) also above t_min, against the share overall
    side = 1024 // 8
    late = [g.reshape(side, side) >= t_min for g in big]
    neighbour = [
        np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1) for m in late
    ]
    share = sum(int((m & n).sum()) for m, n in zip(late, neighbour, strict=True)) / max(
        sum(int(m.sum()) for m in late), 1
    )
    out["late_block_neighbours"] = {
        "share_with_a_late_neighbour": share,
        "if_independent": 1 - (1 - tail_mass) ** 4,
    }
    statuses = {}
    for name in claims:
        if name == "independence":
            statuses[name] = (
                "consistent"
                if tests["independence: median"]["passes"] and tests["independence: iqr"]["passes"]
                else "rejected"
            )
        else:
            statuses[name] = "consistent" if tests[name]["passes"] else "rejected"
    out["statuses"] = statuses
    return out


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
