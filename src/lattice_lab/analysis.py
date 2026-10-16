"""Fit, predict, judge, and check that a verdict does not hang on a few sizes.

Fitting. Each candidate law is fitted with Kepler to the complete observations: x is the torus
size, y the median settling time, and each point is weighted by its own uncertainty. A median's
standard error is 1.2533 s / sqrt(n) (the median of n normal draws), where s is the robust
spread of the seeds' log settling times: the larger of that size's own spread and the median
spread over all sizes. Pooling keeps the error honest at 4 seeds and when a size's seeds happen
to bunch; the size's own spread still counts where it is wider. The bootstrap interval of the
median, alone, ran about 10% narrow with heavy tails on synthetic data (a true law then failed
the 1% level 5% of the time). Those errors are taken as absolute,
and the constants' covariance is widened when the points scatter more than they allow, never
narrowed when they scatter less (Kepler's `inflate`): on 5 to 20 points the reduced chi-square
is itself too noisy to shrink error bars with. In log space (the default when every
value is positive) residuals are relative, which suits settling times spanning decades and
seed scatter that grows with the median.

Predictions. Before a held-out size is run, every eligible law's prediction there is written to
the ledger: the value, a 95% band, and the covariance of its predictions at all the chosen
sizes (Kepler's `predict_covariance`), since predictions at neighbouring sizes share the same
constants and err together.

Judging. A law's held-out test compares its recorded predictions with the measured medians,
jointly: d^2 = r^T (P + S)^-1 r, where r is observed minus predicted (in the fit space), P the
prediction covariance and S the measurements' own squared errors. Under the law, d^2 follows a
chi-square distribution with one degree of freedom per held-out size; a p-value below `alpha`
(0.01 by default) rejects it. "3 of 4 inside the 95% band" is reported too, for people. A
held-out size whose seeds did not all settle is left out of every test: an unsettled run never
counts against a law.

The decision (`decide`). No held-out size measured: inconclusive. Every law rejected: none fits
(the true law is outside the library, or the data are odd). Otherwise the surviving laws are
refitted to all the data and ranked by BIC with an Occam window; the best is named, "found",
only when every other survivor is either `decisive_bic` points worse, or richer and practically
the same law over the measured sizes: its prediction stays within +-`equivalence` (50%) of the
best's at every measured size, with 95% confidence. Otherwise inconclusive. The Occam window
alone would name a constant whenever the data are too noisy to show a trend; failing to see a
trend is not evidence that there is none, so a richer law that passed must itself pin the trend
down before the simpler one is named. Held-out tests decide which laws stay in play; BIC on
all the data then picks among those that passed, and a narrow margin is reported as such.

Fragility. A found law is recomputed with the smallest size dropped, the two smallest dropped,
and each fitted size left out in turn (fits, predictions, tests and ranking all redone). If any
variant leads with another law, or rejects the found one, the verdict is "fragile", not found:
on the settling-time prototype the smallest tori alone produced a false "logarithmic" for every
rule. A variant that keeps the same leading law but less decisively does not flip it.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from kepler import Fit, fit, predict, predict_covariance, rank
from scipy import stats

from lattice_lab.experiment import LOG_FLOOR, Observation
from lattice_lab.question import Question, size_of

Z95 = 1.959963984540054
MEDIAN_EFFICIENCY = 1.2533  # sd of a median of n normal draws, in units of sd / sqrt(n)
MIN_LOG_SE = 0.01  # a 1% floor on any one median's relative error
# A median of whole numbers moves in steps of half a generation; a rounding error that wide has
# a standard deviation of 0.5 / sqrt(12). That, not half a generation itself, is the floor.
QUANTUM_SE = 0.5 / math.sqrt(12)
MIN_LINEAR_SE = QUANTUM_SE


def choose_space(question: Question, observations: Sequence[Observation]) -> str:
    if question.space != "auto":
        return question.space
    values = [o.y for o in observations if o.complete]
    return "log" if values and all(v > 0 for v in values) else "linear"


def _y(o: Observation, space: str) -> float:
    return max(o.y, LOG_FLOOR) if space == "log" else o.y


def pooled_spread(observations: Sequence[Observation]) -> float | None:
    """The median robust spread of log settling times over the complete sizes, or None."""
    spreads = [
        o.spread_log
        for o in observations
        if o.complete and o.spread_log is not None and o.seeds >= 2
    ]
    return float(np.median(spreads)) if spreads else None


def standard_error(o: Observation, space: str, pooled: float | None = None) -> float:
    """One median's standard error in the fit space (see the module docstring), with floors:
    every seed agreeing does not make a median exact. Without a recorded spread, the half-width
    of the 95% interval is used."""
    root_n = math.sqrt(max(o.seeds, 1))
    if space == "log":
        y = _y(o, space)
        spreads = [v for v in (o.spread_log, pooled) if v is not None]
        if spreads:
            se = MEDIAN_EFFICIENCY * max(spreads) / root_n
        else:
            low, high = max(o.low, LOG_FLOOR), max(o.high, LOG_FLOOR)
            se = (math.log(high) - math.log(low)) / (2 * Z95)
        return max(se, MIN_LOG_SE, QUANTUM_SE / y)
    if o.spread is not None and o.y:
        # A spread of log t is a relative spread of t: pool it as one.
        relative = [o.spread / abs(o.y)] + ([pooled] if pooled is not None else [])
        se = MEDIAN_EFFICIENCY * max(relative) * abs(o.y) / root_n
    elif o.spread is not None:
        se = MEDIAN_EFFICIENCY * o.spread / root_n
    else:
        se = (o.high - o.low) / (2 * Z95)
    return max(se, MIN_LINEAR_SE, 0.01 * abs(o.y))


def fit_laws(
    laws: Sequence[str],
    observations: Sequence[Observation],
    space: str,
    pooled: float | None = None,
) -> list[Fit]:
    usable = sorted((o for o in observations if o.complete), key=lambda o: o.x)
    if pooled is None:
        pooled = pooled_spread(usable)
    x = np.array([o.x for o in usable])
    y = np.array([_y(o, space) for o in usable])
    se = np.array([standard_error(o, space, pooled) for o in usable])
    sigma = se * y if space == "log" else se  # Kepler takes sigma in y's units
    # The sigmas are real error estimates: absolute, widened (never narrowed) by excess scatter.
    return [
        fit(law, x, y, sigma=sigma, space=space, absolute_sigma=True, inflate=True) for law in laws
    ]


def prediction_body(law_fit: Fit, labels: Sequence) -> dict:
    """A law's predictions at the held-out sizes, as the ledger records them."""
    xs = [size_of(label) for label in labels]
    centre, cov = predict_covariance(law_fit, xs)
    y, low, high = predict(law_fit, xs)
    return {
        "law": law_fit.name,
        "formula": law_fit.formula,
        "space": law_fit.space,
        "labels": list(labels),
        "x": xs,
        "centre": centre,
        "cov": cov,
        "y": y,
        "low": low,
        "high": high,
        "params": dict(zip(law_fit.param_names, law_fit.params, strict=True)),
        "stderr": dict(zip(law_fit.param_names, law_fit.stderr, strict=True)),
        "covariance": law_fit.covariance,
        "fit_n": law_fit.n,
        "bic": law_fit.bic,
        "r2_fit": law_fit.r2_fit,
    }


def judge_prediction(
    prediction: dict,
    heldout: Sequence[Observation],
    space: str,
    alpha: float,
    pooled: float | None = None,
) -> dict:
    """The joint held-out test of one recorded prediction (see the module docstring)."""
    index = {_key(label): i for i, label in enumerate(prediction["labels"])}
    usable = [o for o in heldout if o.complete and _key(o.label) in index]
    skipped = [o.label for o in heldout if not o.complete]
    result = {"law": prediction["law"], "m": len(usable), "skipped": skipped}
    if not usable:
        return {**result, "status": "untested", "d2": None, "p": None, "inside": 0, "points": []}
    rows = [index[_key(o.label)] for o in usable]
    centre = np.array([prediction["centre"][i] for i in rows], dtype=float)
    cov = np.array([[prediction["cov"][i][j] for j in rows] for i in rows], dtype=float)
    if not (np.all(np.isfinite(centre)) and np.all(np.isfinite(cov))):
        return {
            **result,
            "status": "untested",
            "d2": None,
            "p": None,
            "inside": 0,
            "points": [],
            "note": "the prediction was not finite at these sizes",
        }
    observed = np.array([_y(o, space) for o in usable], dtype=float)
    if space == "log":
        observed = np.log(observed)
    if pooled is None:
        pooled = pooled_spread(usable)
    se = np.array([standard_error(o, space, pooled) for o in usable])
    total = cov + np.diag(se**2)
    r = observed - centre
    d2 = float(r @ np.linalg.lstsq(total, r, rcond=None)[0])
    p = float(stats.chi2.sf(d2, len(r)))
    sd = np.sqrt(np.diag(total))
    inside = np.abs(r) <= Z95 * sd
    points = []
    for k, o in enumerate(usable):
        i = rows[k]
        points.append(
            {
                "label": o.label,
                "observed": o.y,
                "observed_low": o.low,
                "observed_high": o.high,
                "predicted": prediction["y"][i],
                "band_low": prediction["low"][i],
                "band_high": prediction["high"][i],
                "z": float(r[k] / sd[k]),
                "inside": bool(inside[k]),
            }
        )
    status = "consistent" if p >= alpha else "rejected"
    return {
        **result,
        "status": status,
        "d2": d2,
        "p": p,
        "inside": int(inside.sum()),
        "points": points,
    }


def _key(label) -> str:
    return str(label)


def decide(
    question: Question,
    fit_obs: Sequence[Observation],
    heldout: Sequence[Observation],
    predictions: dict[str, dict],
    space: str,
) -> dict:
    """A round's verdict from the recorded predictions and the held-out measurements."""
    pooled = pooled_spread([*fit_obs, *heldout])
    tests = [
        judge_prediction(p, heldout, space, question.alpha, pooled) for p in predictions.values()
    ]
    base = {
        "tests": tests,
        "survivors": [],
        "rivals": [],
        "leading": None,
        "law": None,
        "combined_ranking": None,
        "combined_fits": {},
    }
    if not any(o.complete for o in heldout):
        return {
            **base,
            "verdict": "inconclusive",
            "note": "no held-out size settled within the caps, so nothing was tested",
        }
    survivors = [t["law"] for t in tests if t["status"] == "consistent"]
    if not survivors:
        return {
            **base,
            "verdict": "none fits",
            "note": "every candidate's held-out predictions were rejected "
            f"(p < {question.alpha:g})",
        }
    combined = fit_laws(survivors, [*fit_obs, *heldout], space, pooled)
    ranking = rank(combined)
    base.update(
        survivors=survivors,
        combined_ranking=ranking.to_dict(),
        combined_fits={f.name: f.to_dict() for f in combined},
    )
    if ranking.best is None:
        return {
            **base,
            "verdict": "inconclusive",
            "note": "the laws that passed held-out tests do not fit all the data together",
        }
    best = ranking.best
    xs = sorted({o.x for o in [*fit_obs, *heldout] if o.complete})
    rivals = [
        e.name
        for e in ranking.entries
        if e is not best
        and e.eligible
        and e.bic - best.bic < question.decisive_bic
        and (
            e.n_constants <= best.n_constants
            or not equivalent(e.fit, best.fit, xs, space, question.equivalence)
        )
    ]
    base.update(leading=best.name, rivals=rivals)
    if rivals:
        gaps = ", ".join(
            f"{e.name} {e.bic - best.bic:+.1f}" for e in ranking.entries if e.name in rivals
        )
        return {
            **base,
            "verdict": "inconclusive",
            "note": f"{best.name} leads, but {len(rivals)} rival(s) that also passed are too "
            f"close to rule out on all the data (BIC {gaps})",
        }
    also = []
    for e in ranking.entries:
        if e is best or e.name not in survivors:
            continue
        if not e.eligible:
            also.append(f"{e.name} also passed but does not fit all the data ({e.reason})")
            continue
        gap = e.bic - best.bic
        if gap >= question.decisive_bic:
            also.append(f"{e.name} also passed but fits all the data {gap:.1f} BIC points worse")
        else:
            also.append(
                f"{e.name} also passed and stays within {question.equivalence:.0%} of it "
                "at every measured size"
            )
    note = f"{best.name} passed its held-out test; " + (
        "; ".join(also) if also else "every other law was rejected"
    )
    return {**base, "verdict": "found", "law": best.name, "note": note}


def equivalent(
    richer: Fit, simpler: Fit, xs: Sequence[float], space: str, tolerance: float
) -> bool:
    """Whether `richer` stays within +-`tolerance` (relative) of `simpler` at every x, with
    95% confidence: the richer law's extra freedom makes no practical difference there."""
    c_r, cov_r = predict_covariance(richer, xs)
    c_s, cov_s = predict_covariance(simpler, xs)
    sd = np.sqrt(np.maximum(np.diag(cov_r) + np.diag(cov_s), 0.0))
    if space == "log":
        diff, bound = c_r - c_s, math.log1p(tolerance)
    else:
        scale = np.abs(c_s)
        with np.errstate(all="ignore"):
            diff, sd, bound = (c_r - c_s) / scale, sd / scale, tolerance
    worst = np.abs(diff) + Z95 * sd
    return bool(np.all(np.isfinite(worst)) and np.all(worst <= bound))


def predictions_for(question: Question, fits: Sequence[Fit], labels: Sequence) -> dict[str, dict]:
    """Predictions of every law eligible in the ranking of `fits` (in rank order)."""
    ranking = rank(fits)
    return {e.name: prediction_body(e.fit, labels) for e in ranking.entries if e.eligible}


def fragility(
    question: Question,
    fit_obs: Sequence[Observation],
    heldout: Sequence[Observation],
    decision: dict,
    space: str,
) -> list[dict]:
    """The found law's verdict recomputed on reduced fit sets (see the module docstring)."""
    usable = sorted((o for o in fit_obs if o.complete), key=lambda o: o.x)
    labels = [o.label for o in heldout]
    n = len(usable)
    variants: list[tuple[str, list[Observation], list]] = []
    for k in (1, 2):
        if n - k >= question.min_points:
            dropped = [o.label for o in usable[:k]]
            variants.append((f"without the {k} smallest", usable[k:], dropped))
    if n - 1 >= question.min_points:
        for o in usable:
            variants.append((f"without {o.label}", [u for u in usable if u is not o], [o.label]))
    out = []
    for name, subset, dropped in variants:
        fits = fit_laws(question.laws, subset, space)
        variant = decide(question, subset, heldout, predictions_for(question, fits, labels), space)
        agrees = variant["leading"] == decision["law"] and decision["law"] in variant["survivors"]
        out.append(
            {
                "variant": name,
                "left_out": dropped,
                "verdict": variant["verdict"],
                "leading": variant["leading"],
                "survivors": variant["survivors"],
                "agrees": agrees,
            }
        )
    return out
