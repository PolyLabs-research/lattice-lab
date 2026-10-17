"""The extreme-value predictions and the quantile statistics that test them."""

import math

import numpy as np
import pytest

from lattice_lab import extremes


def test_the_gumbel_constants():
    assert extremes.GUMBEL_IQR == pytest.approx(math.log(math.log(4) / math.log(4 / 3)))
    assert extremes.GUMBEL_KELLY == pytest.approx(0.22154, abs=1e-5)
    assert extremes.gumbel_iqr_per_slope(2) == pytest.approx(0.78627, abs=1e-5)


def test_frechet_shape_tends_to_gumbel_as_the_tail_lightens():
    ratios, shapes = zip(*(extremes.frechet(a) for a in (3, 5, 10, 100, 10_000)), strict=True)
    assert all(x > y for x, y in zip(ratios, ratios[1:], strict=False))  # narrower as alpha grows
    assert shapes[-1] == pytest.approx(extremes.GUMBEL_KELLY, abs=1e-3)
    assert shapes[0] > shapes[-1]  # heavier tails are more skewed


def test_fluctuations_recover_a_known_gumbel_sample():
    rng = np.random.default_rng(3)
    times = {n: 100 + rng.gumbel(0, 20, size=4000) for n in (64, 128)}
    out = extremes.fluctuations(times, bootstrap=300)
    for f in out.values():
        assert f["iqr"] == pytest.approx(20 * extremes.GUMBEL_IQR, rel=0.06)
        assert f["kelly_skewness"] == pytest.approx(
            extremes.GUMBEL_KELLY, abs=4 * f["kelly_skewness_error"]
        )
        assert f["iqr_error"] > 0


def test_weighted_slope_and_z_test():
    slope, err = extremes.weighted_slope([0, 1, 2], [1, 3, 5], [0.1, 0.1, 0.1])
    assert slope == pytest.approx(2) and err > 0
    assert extremes.z_test(1.0, 0.1, 1.2)["passes"]
    assert not extremes.z_test(1.0, 0.1, 1.5)["passes"]


def test_jitter_removes_the_rounding_bias_of_a_narrow_sample():
    rng = np.random.default_rng(4)
    times = {64: np.round(30 + rng.gumbel(0, 2.5, size=20000))}
    plain = extremes.fluctuations(times, bootstrap=50)[64]["kelly_skewness"]
    jittered = extremes.fluctuations(times, bootstrap=50, jitter=True)[64]["kelly_skewness"]
    assert abs(jittered - extremes.GUMBEL_KELLY) < 0.02
    assert abs(jittered - extremes.GUMBEL_KELLY) < abs(plain - extremes.GUMBEL_KELLY)


def _tail_sample(rng, tau, k, t_min, n):
    from scipy import optimize

    def log_s(x):
        return k * math.log(x / tau) - x / tau

    out = []
    for u in rng.random(n):
        target = log_s(t_min) + math.log(u)
        x = optimize.brentq(lambda x, g=target: log_s(x) - g, t_min, t_min + 400 * tau)
        out.append(math.floor(x))
    return np.array(out)


@pytest.mark.parametrize(("tau", "k"), [(14.5, 0.0), (12.7, 2.85)])
def test_fit_tail_recovers_a_known_tail(tau, k):
    rng = np.random.default_rng(7)
    groups = [_tail_sample(rng, tau, k, 120.0, 150) for _ in range(20)]
    fit = extremes.fit_tail(groups, 120.0, bootstrap=60)
    assert fit["n"] == 3000
    assert abs(fit["k"] - k) < 3 * fit["k_se"] + 0.05
    assert abs(fit["tau"] - tau) < 3 * fit["tau_se"] + 0.05
    eff, eff_se = extremes.tail_tau_eff(fit, 200.0)
    assert abs(eff - 1 / (1 / tau - k / 200.0)) < 3 * eff_se + 0.05


def test_the_prefactor_model_keeps_the_gumbel_ratio():
    """Spread over slope stays 0.786 whatever k: the reason a prefactor cannot narrow the spread."""
    for k in (0.0, 3.0):
        q = [extremes.prefactor_quantile(p, 1024, 12.0, k, -3.0) for p in (0.25, 0.5, 0.75)]
        h = 1e-3
        slope = (
            extremes.prefactor_quantile(0.5, 1024 * math.exp(h), 12.0, k, -3.0)
            - extremes.prefactor_quantile(0.5, 1024 * math.exp(-h), 12.0, k, -3.0)
        ) / (2 * h)
        assert (q[2] - q[0]) / slope == pytest.approx(extremes.gumbel_iqr_per_slope(2), abs=0.002)


def test_mean_excess_of_an_exponential_tail():
    rng = np.random.default_rng(2)
    groups = [100 + rng.exponential(10.0, 500) for _ in range(10)]
    value, error, count = extremes.mean_excess(groups, 100.0)
    assert count == 5000 and abs(value - 10.0) < 3 * error
