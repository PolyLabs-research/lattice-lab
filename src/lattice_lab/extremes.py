"""Extreme-value predictions for settling times, and the quantile statistics that test them.

A soup settles when its last region does, so its settling time is the largest of about L^d
local times (d = 2 on these lattices). The two classic limits for the largest of many
independent times give two mechanisms, each tying the seed-to-seed fluctuations to how the median
grows with L, with no constant fitted to the fluctuations:

- light tails (Gumbel): location tau ln(L^d) + c, so the median grows as d tau ln L; the
  interquartile range is 1.5725 tau at every size, and the shape (Kelly's quantile skewness) is
  0.2215 whatever the rule.
- heavy tails of index alpha (Frechet): scale proportional to (L^d)^(1/alpha), so the median grows
  as L^(d/alpha); the interquartile range is a fixed fraction of the median, and the shape a
  function of alpha alone.

Spread and shape are measured by quantiles, not moments: a Frechet tail of index 5 has no finite
sixth moment, so a sample's moment skewness has no usable error bar, while quantiles have honest
bootstrap errors for light and heavy tails alike. Kelly's skewness is
(Q90 + Q10 - 2 Q50) / (Q90 - Q10), which depends on neither location nor scale.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)
BOOTSTRAP = 2000


def gumbel_quantile(p: float) -> float:
    return -math.log(-math.log(p))


def kelly(q10: float, q50: float, q90: float) -> float:
    return (q90 + q10 - 2 * q50) / (q90 - q10)


GUMBEL_IQR = gumbel_quantile(0.75) - gumbel_quantile(0.25)  # 1.5725 per unit scale
GUMBEL_KELLY = kelly(*(gumbel_quantile(p) for p in (0.10, 0.50, 0.90)))  # 0.2215


def gumbel_iqr_per_slope(dimension: int = 2) -> float:
    """Interquartile range per unit slope of the median in ln L, for the largest of L^d times."""
    return GUMBEL_IQR / dimension


def frechet(alpha: float) -> tuple[float, float]:
    """(interquartile range / median, Kelly skewness) of a Frechet variable of shape alpha:
    quantiles (-ln p)^(-1/alpha) times the scale, which cancels."""

    def q(p: float) -> float:
        return (-math.log(p)) ** (-1 / alpha)

    return (q(0.75) - q(0.25)) / q(0.5), kelly(q(0.10), q(0.50), q(0.90))


def frechet_with_errors(alpha: float, alpha_se: float, h: float = 1e-4) -> dict:
    ratio, shape = frechet(alpha)
    up, down = frechet(alpha + h), frechet(alpha - h)
    return {
        "iqr_over_median": ratio,
        "iqr_over_median_se": abs(up[0] - down[0]) / (2 * h) * alpha_se,
        "kelly_skewness": shape,
        "kelly_skewness_se": abs(up[1] - down[1]) / (2 * h) * alpha_se,
    }


def fluctuations(
    times: dict, seed: int = 0, bootstrap: int = BOOTSTRAP, jitter: bool = False
) -> dict:
    """Per size: the median, interquartile range, their ratio and Kelly's skewness, each with a
    bootstrap error (seeds resampled within the size; seeded, so reproducible), and the moments
    for the record.

    Settling times are whole generations. Where the spread is only a few generations, quantiles
    of whole numbers are biased by the rounding; with `jitter`, each time first gets a uniform
    offset in [-1/2, 1/2) (seeded), which makes the sample continuous and adds a variance of
    1/12 generation^2, negligible against any spread worth measuring."""
    rng = np.random.default_rng(seed)
    out = {}
    for n in sorted(times):
        t = np.asarray(times[n], dtype=float)
        if jitter:
            t = t + rng.uniform(-0.5, 0.5, size=len(t))
        samples = t[rng.integers(0, len(t), size=(bootstrap, len(t)))]
        q10, q25, q50, q75, q90 = np.quantile(samples, QUANTILES, axis=1)
        iqr, ratio, shape = q75 - q25, (q75 - q25) / q50, (q90 + q10 - 2 * q50) / (q90 - q10)
        Q10, Q25, Q50, Q75, Q90 = np.quantile(t, QUANTILES)
        out[n] = {
            "seeds": len(t),
            "median": float(Q50),
            "median_error": float(q50.std(ddof=1)),
            "iqr": float(Q75 - Q25),
            "iqr_error": float(iqr.std(ddof=1)),
            "iqr_over_median": float((Q75 - Q25) / Q50),
            "iqr_over_median_error": float(ratio.std(ddof=1)),
            "kelly_skewness": float(kelly(Q10, Q50, Q90)),
            "kelly_skewness_error": float(shape.std(ddof=1)),
            "mean": float(t.mean()),
            "sd": float(t.std(ddof=1)),
            "moment_skewness": float(stats.skew(t, bias=False)) if len(t) > 2 else None,
        }
    return out


def weighted_mean(values, errors) -> tuple[float, float]:
    w = 1 / np.asarray(errors, dtype=float) ** 2
    return float(np.sum(w * np.asarray(values)) / np.sum(w)), float(1 / math.sqrt(np.sum(w)))


def weighted_slope(x, y, errors) -> tuple[float, float]:
    """The weighted least-squares slope of y on x, and its standard error."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    w = 1 / np.asarray(errors, dtype=float) ** 2
    xbar = np.sum(w * x) / np.sum(w)
    sxx = np.sum(w * (x - xbar) ** 2)
    return float(np.sum(w * (x - xbar) * y) / sxx), float(1 / math.sqrt(sxx))


def z_test(
    observed: float, error: float, predicted: float, predicted_se: float = 0.0, alpha: float = 0.01
) -> dict:
    """A two-sided test of observed against predicted, their errors combined."""
    total = math.hypot(error, predicted_se)
    z = (observed - predicted) / total
    return {
        "observed": observed,
        "error": error,
        "predicted": predicted,
        "predicted_se": predicted_se,
        "z": z,
        "passes": abs(z) <= stats.norm.isf(alpha / 2),
    }
