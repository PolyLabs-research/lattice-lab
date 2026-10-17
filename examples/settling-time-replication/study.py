"""
A registered replication: B2/S34 settling times on hexagon tori up to 1024 x 1024.

    uv run python examples/settling-time-replication/study.py register
    uv run python examples/settling-time-replication/study.py run --workers 4
    uv run lattice-lab verify --lab examples/settling-time-replication

The example lab (examples/lab-b2s34) found the median settling time of B2/S34 soups (density
0.5) on hexagon tori of side 8 to 128 to be logarithmic in the side, T = 37.6 ln L - 36.3, with a
power law T = 22.3 L^0.398 8.4 BIC points behind; a later study of first repeats up to 64 could
not tell them apart (docs/capabilities.md, section 3). This study tests both at six new sides,
192 to 1024, with 100 seeds each, and adds two mechanisms that tie the growth of the median to the
seed-to-seed fluctuations, with no constant fitted to the fluctuations:

- Extreme value, light tails. A soup settles when its last region does: the settling time is
  the largest of about L^2 local times. If those have exponential tails of scale tau, the largest
  is Gumbel-distributed with location tau ln(L^2) + c, so the median grows as 2 tau ln L (the log
  law, with tau = a / 2), the standard deviation is pi tau / sqrt 6 at every size, and the
  skewness is 12 sqrt(6) zeta(3) / pi^3 = 1.1395.
- Extreme value, heavy tails. If the local times have power-law tails of index alpha, the
  largest is Frechet-distributed with scale proportional to (L^2)^(1/alpha): the power law, with
  alpha = 2 / b; the standard deviation is then a fixed fraction of the median, and the skewness
  a function of alpha alone.

The laws' predictions come from fits to the example lab's ten sizes, recorded there in 2026-10-16;
the mechanisms' from those fits' constants. No run at any of these six sizes existed before the
registration was committed and pushed.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from latticelife.experiments.observables import median_transient
from scipy import stats
from scipy.special import zeta

from lattice_lab.analysis import fit_laws, judge_prediction, pooled_spread, prediction_body
from lattice_lab.experiment import LatticeExperimenter, Observation, observation_from_row
from lattice_lab.question import Question
from lattice_lab.study import Study, main

HERE = Path(__file__).resolve().parent
EARLIER = HERE.parent / "lab-b2s34" / "ledger.jsonl"
SIZES = [192, 256, 384, 512, 768, 1024]
ALPHA = 0.01
Z = stats.norm.isf(ALPHA / 2)  # 2.576: every mechanism test is two-sided at the 1% level
BOOTSTRAP = 2000
# Spread and shape are measured by quantiles, which have honest bootstrap errors for light and
# heavy tails alike (a Frechet tail of index 5 has no finite sixth moment, so the sample's moment
# skewness has no usable error bar): the interquartile range, and Kelly's quantile skewness
# (Q90 + Q10 - 2 Q50) / (Q90 - Q10), which does not depend on location or scale.
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)


def gumbel_quantile(p: float) -> float:
    return -math.log(-math.log(p))


def kelly(q10: float, q50: float, q90: float) -> float:
    return (q90 + q10 - 2 * q50) / (q90 - q10)


GUMBEL_IQR = gumbel_quantile(0.75) - gumbel_quantile(0.25)  # 1.5725 per unit scale
GUMBEL_KELLY = kelly(*(gumbel_quantile(p) for p in (0.10, 0.50, 0.90)))  # 0.2216
GUMBEL_SD = math.pi / math.sqrt(6)  # reported, not tested
GUMBEL_SKEW = 12 * math.sqrt(6) * float(zeta(3)) / math.pi**3  # reported, not tested


def earlier_observations() -> list[Observation]:
    rows = []
    for line in EARLIER.read_text().splitlines():
        entry = json.loads(line)
        if entry["kind"] == "observations":
            rows += entry["body"]["rows"]
    return [Observation.from_json(r) for r in rows]


EARLIER_SIZES = sorted(o.label for o in earlier_observations())
QUESTION = Question(
    id="settling-time-hexagon-B2S34-replication",
    rule="B2/S34",
    shape="hexagon",
    density=0.5,
    seeds=100,
    fit_sizes=tuple(EARLIER_SIZES),
    heldout_pool=tuple(SIZES),
    cap=2000,
    max_cap=64000,
    budget_cell_steps=5e11,
)


def fits():
    observations = earlier_observations()
    return {f.name: f for f in fit_laws(QUESTION.laws, observations, "log")}


def frechet(alpha: float) -> tuple[float, float]:
    """(interquartile range / median, Kelly skewness) of a Frechet variable of shape alpha:
    quantiles (-ln p)^(-1/alpha) times the scale, which cancels."""

    def q(p: float) -> float:
        return (-math.log(p)) ** (-1 / alpha)

    return (q(0.75) - q(0.25)) / q(0.5), kelly(q(0.10), q(0.50), q(0.90))


def question() -> dict:
    return {
        "id": QUESTION.id,
        "title": "Do B2/S34 settling times on hexagon tori of side 192 to 1024 follow the "
        "logarithmic law, and do their fluctuations follow from it?",
        "spec": QUESTION.to_dict(),
        "earlier": {
            "ledger": "examples/lab-b2s34/ledger.jsonl",
            "sizes": EARLIER_SIZES,
            "verdict": "found: logarithmic (T = 37.6 ln L - 36.3), power law 8.4 BIC points behind",
        },
        "sizes": SIZES,
        "seeds": "1 to 100 at every size",
        "quantity": "settling time: the generation each seed's final cycle begins (LatticeLife's "
        "median_transient), the median over seeds for the laws, every seed's for the mechanisms",
        "alpha": ALPHA,
    }


def predictions() -> list[dict]:
    found = fits()
    out = []
    for name in QUESTION.laws:
        out.append(
            {
                "role": "law",
                **prediction_body(found[name], SIZES),
                "decision": "the loop's joint held-out test of the medians (judge_prediction): "
                f"rejected when p < {ALPHA}",
            }
        )
    log_fit, power_fit = found["logarithmic"], found["power"]
    a, a_se = log_fit.params[0], log_fit.stderr[0]
    out.append(
        {
            "role": "mechanism",
            "mechanism": "extreme value, light tails (Gumbel)",
            "from": "the logarithmic law's slope a: scale tau = a / 2",
            "a": a,
            "a_se": a_se,
            "tau": a / 2,
            "iqr": GUMBEL_IQR * a / 2,
            "iqr_se": GUMBEL_IQR * a_se / 2,
            "kelly_skewness": GUMBEL_KELLY,
            "iqr_trend_per_ln_L": 0.0,
            "also_implied": {"sd": GUMBEL_SD * a / 2, "moment_skewness": GUMBEL_SKEW},
            "decision": "three tests, each two-sided at 1%: (1) the seeds' interquartile range, "
            "averaged over sizes with inverse-variance weights, equals iqr (error: the bootstrap "
            "error of the average and iqr_se combined); (2) the weighted slope of the "
            "interquartile range against ln L is 0; (3) Kelly's quantile skewness, averaged over "
            "sizes the same way, equals kelly_skewness. Consistent when all three pass. The "
            "standard deviation and moment skewness are reported, not tested.",
        }
    )
    b, b_se = power_fit.params[1], power_fit.stderr[1]
    shape, shape_se = 2 / b, 2 * b_se / b**2
    ratio, skew = frechet(shape)
    h = 1e-4
    up, down = frechet(shape + h), frechet(shape - h)
    out.append(
        {
            "role": "mechanism",
            "mechanism": "extreme value, heavy tails (Frechet)",
            "from": "the power law's exponent b: tail index alpha = 2 / b",
            "b": b,
            "b_se": b_se,
            "alpha": shape,
            "alpha_se": shape_se,
            "iqr_over_median": ratio,
            "iqr_over_median_se": abs(up[0] - down[0]) / (2 * h) * shape_se,
            "kelly_skewness": skew,
            "kelly_skewness_se": abs(up[1] - down[1]) / (2 * h) * shape_se,
            "decision": "two tests, each two-sided at 1%: (1) the seeds' interquartile range "
            "over their median, averaged over sizes with inverse-variance weights, equals "
            "iqr_over_median (bootstrap and prediction errors combined); (2) Kelly's quantile "
            "skewness, averaged the same way, equals kelly_skewness. Consistent when both "
            "pass.",
        }
    )
    return out


def execute(path: Path, workers: int) -> None:
    experimenter = LatticeExperimenter(
        QUESTION, path, workers=workers, progress=lambda m: print(m, file=sys.stderr, flush=True)
    )
    experimenter.measure(SIZES, QUESTION.budget_cell_steps)


def _times(rows: list[dict]) -> dict[int, np.ndarray]:
    return {
        int(row.grid): np.asarray(row.settling_times, dtype=float)
        for row in median_transient(rows)
        if row.complete
    }


def _weighted(values, errors) -> tuple[float, float]:
    w = 1 / np.asarray(errors) ** 2
    return float(np.sum(w * values) / np.sum(w)), float(1 / math.sqrt(np.sum(w)))


def _test(observed: float, error: float, predicted: float, predicted_se: float = 0.0) -> dict:
    total = math.hypot(error, predicted_se)
    z = (observed - predicted) / total
    return {
        "observed": observed,
        "error": error,
        "predicted": predicted,
        "predicted_se": predicted_se,
        "z": z,
        "passes": abs(z) <= Z,
    }


def fluctuations(times: dict[int, np.ndarray], seed: int = 0) -> dict:
    """Per-size quantile spread and shape, with bootstrap errors (seeds resampled within each
    size; seeded, so the verdict is reproducible), and the moments for the record."""
    rng = np.random.default_rng(seed)
    per_size = {}
    for n in sorted(times):
        t = times[n]
        samples = t[rng.integers(0, len(t), size=(BOOTSTRAP, len(t)))]
        q10, q25, q50, q75, q90 = np.quantile(samples, QUANTILES, axis=1)
        iqr, ratio, k = q75 - q25, (q75 - q25) / q50, (q90 + q10 - 2 * q50) / (q90 - q10)
        Q10, Q25, Q50, Q75, Q90 = np.quantile(t, QUANTILES)
        per_size[n] = {
            "seeds": len(t),
            "median": float(Q50),
            "iqr": float(Q75 - Q25),
            "iqr_error": float(iqr.std(ddof=1)),
            "iqr_over_median": float((Q75 - Q25) / Q50),
            "iqr_over_median_error": float(ratio.std(ddof=1)),
            "kelly_skewness": float(kelly(Q10, Q50, Q90)),
            "kelly_skewness_error": float(k.std(ddof=1)),
            "mean": float(t.mean()),
            "sd": float(t.std(ddof=1)),
            "moment_skewness": float(stats.skew(t, bias=False)),
        }
    return per_size


def decide(rows: list[dict], registered: list[dict]) -> dict:
    new = [observation_from_row(r) for r in median_transient(rows)]
    pooled = pooled_spread([*earlier_observations(), *new])
    laws = {}
    for p in registered:
        if p["role"] == "law":
            laws[p["law"]] = judge_prediction(p, new, "log", ALPHA, pooled)
    per_size = fluctuations(_times(rows))
    sizes = sorted(per_size)

    def column(key):
        return np.array([per_size[n][key] for n in sizes])

    iqr, iqr_err = column("iqr"), column("iqr_error")
    mechanisms = {}
    for p in registered:
        if p["role"] != "mechanism":
            continue
        if p["mechanism"].startswith("extreme value, light"):
            x = np.log(sizes)
            w = 1 / iqr_err**2
            xbar = np.sum(w * x) / np.sum(w)
            slope = float(np.sum(w * (x - xbar) * iqr) / np.sum(w * (x - xbar) ** 2))
            slope_err = float(1 / math.sqrt(np.sum(w * (x - xbar) ** 2)))
            tests = {
                "iqr": _test(*_weighted(iqr, iqr_err), p["iqr"], p["iqr_se"]),
                "iqr_trend": _test(slope, slope_err, 0.0),
                "kelly_skewness": _test(
                    *_weighted(column("kelly_skewness"), column("kelly_skewness_error")),
                    p["kelly_skewness"],
                ),
            }
        else:
            tests = {
                "iqr_over_median": _test(
                    *_weighted(column("iqr_over_median"), column("iqr_over_median_error")),
                    p["iqr_over_median"],
                    p["iqr_over_median_se"],
                ),
                "kelly_skewness": _test(
                    *_weighted(column("kelly_skewness"), column("kelly_skewness_error")),
                    p["kelly_skewness"],
                    p["kelly_skewness_se"],
                ),
            }
        mechanisms[p["mechanism"]] = {
            "tests": tests,
            "status": "consistent" if all(t["passes"] for t in tests.values()) else "rejected",
        }
    return {
        "laws": {name: {k: v for k, v in t.items() if k != "points"} for name, t in laws.items()},
        "points": {name: t.get("points", []) for name, t in laws.items()},
        "survivors": sorted(name for name, t in laws.items() if t["status"] == "consistent"),
        "fluctuations": per_size,
        "mechanisms": mechanisms,
        "unsettled": [o.label for o in new if not o.complete],
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
