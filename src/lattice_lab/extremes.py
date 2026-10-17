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


# --- the largest of many local times with tail t^k e^(-t/tau) ----------------------------------
#
# If each of about L^d local times has survival C (t/tau)^k e^(-t/tau) in its upper tail, the
# largest has P(T <= t) = exp(-L^d e^c (t/tau)^k e^(-t/tau)), c absorbing C and the unit of area.
# Its p-quantile solves t/tau - k ln(t/tau) = d ln L + c - ln(-ln p). The spread and the slope in
# ln L are both set by the tail's hazard rate at the location, 1/tau - k/t, so their ratio is the
# Gumbel value whatever k: a prefactor bends the slope but cannot narrow the spread relative to it.


def prefactor_quantile(p: float, size: float, tau: float, k: float, c: float, dimension: int = 2):
    from scipy import optimize

    rhs = dimension * math.log(size) + c - math.log(-math.log(p))
    lo = k * (1 + 1e-9) if k > 0 else 1e-12
    if lo - k * math.log(lo) - rhs > 0:
        raise ValueError("no quantile on the tail's branch")
    return tau * optimize.brentq(
        lambda x: x - k * math.log(x) - rhs, lo, abs(rhs) * 10 + 10 * abs(k) + 10
    )


def fit_prefactor_model(times: dict, fix_k: float | None = None, seed: int = 0) -> dict:
    """(tau, k, c) fitted to the 10/25/50/75/90% quantiles at every size by generalised least
    squares, each size's quantiles weighted by their bootstrap covariance."""
    from scipy import optimize

    rng = np.random.default_rng(seed)
    ps = np.array(QUANTILES)
    sizes = sorted(times)
    quantiles, whiten = {}, {}
    for n in sizes:
        t = np.asarray(times[n], dtype=float)
        quantiles[n] = np.quantile(t, ps)
        boot = np.quantile(t[rng.integers(0, len(t), (BOOTSTRAP, len(t)))], ps, axis=1).T
        whiten[n] = np.linalg.cholesky(np.linalg.inv(np.cov(boot.T))).T

    def unpack(theta):
        return (theta[0], fix_k, theta[1]) if fix_k is not None else tuple(theta)

    def residuals(theta):
        tau, k, c = unpack(theta)
        out = []
        for n in sizes:
            try:
                pred = np.array([prefactor_quantile(p, n, tau, k, c) for p in ps])
            except ValueError:
                pred = np.full(len(ps), 1e6)
            out.append(whiten[n] @ (quantiles[n] - pred))
        return np.concatenate(out)

    start = [14.0, 0.0] if fix_k is not None else [14.0, 1.0, 0.0]
    lower = [1.0, -60.0] if fix_k is not None else [1.0, 0.0, -60.0]
    upper = [200.0, 60.0] if fix_k is not None else [200.0, 20.0, 60.0]
    result = optimize.least_squares(residuals, start, bounds=(lower, upper))
    cov = np.linalg.pinv(result.jac.T @ result.jac)
    tau, k, c = unpack(result.x)
    se = np.sqrt(np.diag(cov))
    names = ["tau", "c"] if fix_k is not None else ["tau", "k", "c"]
    return {
        "tau": float(tau),
        "k": float(k),
        "c": float(c),
        "stderr": dict(zip(names, map(float, se), strict=True)),
        "chi2": float(2 * result.cost),
        "dof": int(len(sizes) * len(ps) - len(names)),
        "sizes": sizes,
    }


def _tail_loglik(theta, values, t_min):
    tau, k = theta
    if tau <= 0 or t_min <= k * tau:
        return -np.inf

    def log_s(t):
        return k * np.log(t / tau) - t / tau

    base = log_s(t_min)
    upper = log_s(values) - base
    lower = log_s(values + 1.0) - base
    with np.errstate(divide="ignore", invalid="ignore"):
        mass = np.exp(upper) - np.exp(lower)
    if np.any(mass <= 0):
        return -np.inf
    return float(np.sum(np.log(mass)))


def fit_tail(groups: list, t_min: float, bootstrap: int = 400, seed: int = 0) -> dict:
    """The tail of whole-number times above t_min, as survival (t/tau)^k e^(-t/tau): maximum
    likelihood on the discrete conditional distribution, P(T = t | T >= t_min) =
    [S(t) - S(t+1)] / S(t_min). `groups` holds one array per independent run; times within a run
    may be correlated, so the errors come from resampling whole runs."""
    from scipy import optimize

    def estimate(arrays):
        values = np.concatenate([a[a >= t_min] for a in arrays]).astype(float)
        if len(values) < 10:
            return None
        best = None
        for k0 in (0.0, 1.0, 3.0):
            tau0 = max(np.mean(values - t_min), 1.0)
            r = optimize.minimize(
                lambda th: -_tail_loglik(th, values, t_min),
                [tau0, k0],
                method="Nelder-Mead",
                options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 4000},
            )
            if best is None or r.fun < best.fun:
                best = r
        return best.x, len(values)

    arrays = [np.asarray(g, dtype=float) for g in groups]
    found = estimate(arrays)
    if found is None:
        return {"t_min": t_min, "n": 0}
    (tau, k), count = found
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(bootstrap):
        pick = rng.integers(0, len(arrays), len(arrays))
        again = estimate([arrays[i] for i in pick])
        if again is not None:
            draws.append(again[0])
    draws = np.array(draws)
    return {
        "t_min": t_min,
        "n": count,
        "tau": float(tau),
        "k": float(k),
        "tau_se": float(draws[:, 0].std(ddof=1)),
        "k_se": float(draws[:, 1].std(ddof=1)),
        "draws": draws,
    }


def tail_tau_eff(fit: dict, t: float) -> tuple[float, float]:
    """1 / hazard at t, and its bootstrap error: the local tail's effective scale at t."""

    def value(tau, k):
        return 1.0 / (1.0 / tau - k / t)

    draws = np.array([value(a, b) for a, b in fit["draws"]])
    return float(value(fit["tau"], fit["k"])), float(draws.std(ddof=1))


def mean_excess(groups: list, t_min: float, bootstrap: int = 2000, seed: int = 0) -> tuple:
    """E[T - t_min | T >= t_min] over runs, and its error from resampling whole runs."""
    arrays = [np.asarray(g, dtype=float) for g in groups]
    sums = np.array([np.sum(a[a >= t_min] - t_min) for a in arrays])
    counts = np.array([np.sum(a >= t_min) for a in arrays])
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(arrays), (bootstrap, len(arrays)))
    boot = sums[pick].sum(axis=1) / np.maximum(counts[pick].sum(axis=1), 1)
    return float(sums.sum() / counts.sum()), float(boot.std(ddof=1)), int(counts.sum())
