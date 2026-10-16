"""Choosing the next experiment: which held-out sizes to run.

Runs are spent where the laws still in play disagree. For each size left in the pool, every
contender (an eligible law within `contender_window` BIC points of the best) predicts the median
with an uncertainty; the size's score is the largest separation between two contenders, in units
of their combined prediction and expected measurement error:

    score(x) = max over pairs |mu_i(x) - mu_j(x)| / sqrt(var_i(x) + var_j(x) + 2 var_obs)

where var_obs is a typical squared error of one measured median (from the fitted sizes). With a
single contender there is nothing to separate, and the largest sizes, the longest extrapolation
and so the hardest test, come first. Sizes are taken by score while the budget allows; each
costs cells x an estimated cap x seeds, the cap being twice the largest predicted median (the
runs stop at their first repeated state, so this is an upper bound).

Before the run, the plan also says whether it can decide (`design`): for the two leading
contenders, Kepler's `separation` gives the BIC difference expected between them over every
size measured so far plus the chosen ones, each with its expected error, taking each law in
turn as the truth and keeping the harder case. Below the decisive margin, the round can still
reject laws but is unlikely to name one; `seed_factor` says how many times the seeds would
reach the margin.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence

import numpy as np
from kepler import LAWS, Ranking, predict_covariance, separation

from lattice_lab.analysis import MEDIAN_EFFICIENCY, MIN_LOG_SE, pooled_spread, standard_error
from lattice_lab.experiment import Observation
from lattice_lab.question import Question, cells_of, size_of


def contenders(question: Question, ranking: Ranking) -> list:
    eligible = [e for e in ranking.entries if e.eligible]
    if not eligible:
        return []
    best = min(e.bic for e in eligible)
    return [e for e in eligible if e.bic - best <= question.contender_window]


def design_check(question: Question, entries, fit_obs, chosen, space: str) -> dict | None:
    """Whether the fit sizes plus `chosen` can separate the two leading contenders (module
    docstring). None when there are fewer than two named contenders or nothing to add."""
    named = [e for e in entries if e.name in LAWS]
    if len(named) < 2 or not chosen:
        return None
    a, b = named[0], named[1]
    pooled = pooled_spread(fit_obs)
    xs = [o.x for o in fit_obs] + [size_of(label) for label in chosen]
    if space == "log":
        new = MEDIAN_EFFICIENCY * pooled / math.sqrt(question.seeds) if pooled else MIN_LOG_SE
        errors = [standard_error(o, space, pooled) for o in fit_obs] + [max(new, MIN_LOG_SE)] * len(
            chosen
        )
        kwargs = {"relative": errors}
    else:
        relative = [standard_error(o, space, pooled) / abs(o.y) for o in fit_obs if o.y]
        rel = float(np.median(relative)) if relative else 0.1
        errors = [standard_error(o, space, pooled) for o in fit_obs]
        kwargs = None  # linear space: sigma depends on the truth's curve at new sizes
    results = []
    for truth, rival in ((a, b), (b, a)):
        try:
            if kwargs is None:
                centre, _ = predict_covariance(truth.fit, [size_of(label) for label in chosen])
                sigma = errors + [max(rel * abs(c), 0.5) for c in centre]
                sep = separation(
                    truth.fit,
                    rival.name,
                    xs,
                    sigma=sigma,
                    space=space,
                    margin=question.decisive_bic,
                )
            else:
                sep = separation(
                    truth.fit, rival.name, xs, space=space, margin=question.decisive_bic, **kwargs
                )
        except ValueError:
            return None
        results.append(sep)
    worst = min(results, key=lambda s: s.expected_delta_bic)
    factors = [s.seed_factor for s in results]
    return {
        "pair": [a.name, b.name],
        "expected_delta_bic": worst.expected_delta_bic,
        "margin": question.decisive_bic,
        "sufficient": all(s.sufficient for s in results),
        "seed_factor": None if any(f is None for f in factors) else max(factors),
        "n_sizes": len(xs),
    }


def plan_heldout(
    question: Question,
    ranking: Ranking,
    fit_obs: Sequence[Observation],
    pool: Sequence,
    space: str,
    budget_left: float,
) -> dict:
    """The held-out sizes for the next round, with every size's score and cost."""
    entries = contenders(question, ranking)
    usable = [o for o in fit_obs if o.complete]
    pooled = pooled_spread(usable)
    errors = [standard_error(o, space, pooled) for o in usable]
    if space == "log":
        var_obs = float(np.median(np.square(errors))) if errors else 0.0
        relative = None
    else:
        relative = (
            float(np.median([e / abs(o.y) for e, o in zip(errors, usable, strict=True) if o.y]))
            if usable
            else 0.0
        )
        var_obs = None
    largest = max((size_of(label) for label in pool), default=1.0)

    candidates = []
    for label in pool:
        x = size_of(label)
        predicted = {}
        for entry in entries:
            centre, cov = predict_covariance(entry.fit, [x])
            if np.isfinite(centre[0]) and np.isfinite(cov[0, 0]):
                predicted[entry.name] = (float(centre[0]), float(cov[0, 0]))
        if not predicted:
            continue
        values = [math.exp(c) if space == "log" else c for c, _ in predicted.values()]
        if len(predicted) >= 2:
            score = 0.0
            for (ci, vi), (cj, vj) in itertools.combinations(predicted.values(), 2):
                if space == "log":
                    noise = 2 * var_obs
                else:
                    noise = 2 * (relative * (abs(ci) + abs(cj)) / 2) ** 2
                score = max(score, abs(ci - cj) / math.sqrt(max(vi + vj + noise, 1e-300)))
        else:
            score = x / largest
        finite = [v for v in values if math.isfinite(v)]
        expected = max(finite) if finite else math.inf
        cap = min(question.max_cap, max(question.cap, 2 * expected))
        cost = cells_of(label) * cap * question.seeds
        candidates.append(
            {
                "label": label,
                "x": x,
                "score": score,
                "cost": cost,
                "predicted": {name: v for name, v in zip(predicted, values, strict=True)},
            }
        )

    chosen, spent = [], 0.0
    for c in sorted(candidates, key=lambda c: (-c["score"], -c["x"])):
        if len(chosen) == question.heldout_per_round:
            break
        if spent + c["cost"] <= budget_left:
            chosen.append(c["label"])
            spent += c["cost"]
    chosen.sort(key=size_of)
    return {
        "chosen": chosen,
        "estimated_cost": spent,
        "contenders": [e.name for e in entries],
        "design": design_check(question, entries, usable, chosen, space),
        "candidates": candidates,
        "measurement_error": {"log_variance": var_obs}
        if space == "log"
        else {"relative": relative},
    }
