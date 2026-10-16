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
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence

import numpy as np
from kepler import Ranking, predict_covariance

from lattice_lab.analysis import pooled_spread, standard_error
from lattice_lab.experiment import Observation
from lattice_lab.question import Question, cells_of, size_of


def contenders(question: Question, ranking: Ranking) -> list:
    eligible = [e for e in ranking.entries if e.eligible]
    if not eligible:
        return []
    best = min(e.bic for e in eligible)
    return [e for e in eligible if e.bic - best <= question.contender_window]


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
        "candidates": candidates,
        "measurement_error": {"log_variance": var_obs}
        if space == "log"
        else {"relative": relative},
    }
