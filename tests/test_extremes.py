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
