"""Fitting, the joint held-out test, the decision, fragility and the planner."""

import math

import numpy as np
import pytest
from helpers import obs
from kepler import rank

from lattice_lab.analysis import (
    choose_space,
    decide,
    fit_laws,
    fragility,
    judge_prediction,
    predictions_for,
    standard_error,
)
from lattice_lab.planner import plan_heldout
from lattice_lab.question import Question

Q = Question(
    id="t",
    rule="B2/S34",
    shape="hexagon",
    fit_sizes=(8, 10, 12, 16, 20, 24, 32),
    heldout_pool=(40, 48, 64, 96, 128),
)
SIZES = Q.fit_sizes


def power(L):
    return 27.0 * L**0.6


def test_choose_space():
    assert choose_space(Q, [obs(8, 10.0)]) == "log"
    zero = obs(8, 10.0)
    zero = zero.__class__(**{**zero.to_json(), "y": 0.0, "low": 0.0})
    assert choose_space(Q, [zero]) == "linear"


def test_standard_error_has_a_floor():
    flat = obs(8, 60.0, rel=0.0)  # every seed agreed: a zero-width interval
    assert standard_error(flat, "log") == pytest.approx(0.01)
    assert standard_error(flat, "linear") == pytest.approx(0.6)
    one = obs(8, 1.0, rel=0.0)
    assert standard_error(one, "log") == pytest.approx(0.5)  # half a generation in one
    assert standard_error(obs(8, 60.0, rel=0.1), "log") == pytest.approx(0.1, rel=1e-4)


def _predictions(f=power, sizes=SIZES, labels=(48, 64)):
    fit_obs = [obs(L, f(L)) for L in sizes]
    return fit_obs, predictions_for(Q, fit_laws(Q.laws, fit_obs, "log"), list(labels))


def test_a_law_meeting_its_predictions_is_consistent_and_one_missing_them_is_rejected():
    fit_obs, predictions = _predictions()
    held = [obs(48, power(48)), obs(64, power(64))]
    result = judge_prediction(predictions["power"], held, "log", 0.05)
    assert result["status"] == "consistent" and result["p"] > 0.5 and result["inside"] == 2
    far = [obs(48, 3 * power(48)), obs(64, 3 * power(64))]
    result = judge_prediction(predictions["power"], far, "log", 0.05)
    assert result["status"] == "rejected" and result["p"] < 1e-6 and result["inside"] == 0


def test_the_joint_test_uses_the_prediction_covariance():
    # Two points each just inside their own band, both on the same side, err together: that is
    # what shared constants do, and it is milder than two independent misses.
    fit_obs, predictions = _predictions()
    p = predictions["power"]
    se = standard_error(obs(48, power(48)), "log")
    sd = [math.sqrt(p["cov"][i][i] + se**2) for i in (0, 1)]
    shifted = [obs(L, math.exp(p["centre"][i] + 1.5 * sd[i])) for i, L in enumerate((48, 64))]
    joint = judge_prediction(p, shifted, "log", 0.05)
    independent = math.exp(-0.5 * (1.5**2 + 1.5**2))  # chi2(2) survival at d2 = 4.5
    assert joint["inside"] == 2 and joint["p"] > independent


def test_decide_names_the_law_that_passes_decisively():
    fit_obs, predictions = _predictions()
    held = [obs(48, power(48)), obs(64, power(64))]
    decision = decide(Q, fit_obs, held, predictions, "log")
    assert decision["verdict"] == "found" and decision["law"] == "power"
    assert "power" in decision["survivors"] and decision["combined_ranking"]["best"] == "power"


def test_decide_none_fits_and_nothing_measured():
    fit_obs, predictions = _predictions()
    far = [obs(48, 50 * power(48)), obs(64, 80 * power(64))]
    assert decide(Q, fit_obs, far, predictions, "log")["verdict"] == "none fits"
    unmeasured = [obs(48, None, complete=False), obs(64, None, complete=False)]
    decision = decide(Q, fit_obs, unmeasured, predictions, "log")
    assert decision["verdict"] == "inconclusive" and "nothing was tested" in decision["note"]


def test_fragility_flags_a_verdict_carried_by_the_smallest_sizes():
    # The two smallest tori sit on another curve: the full fit leads with a law the larger
    # sizes do not support, and dropping them says so.
    fit_obs = [obs(L, power(L) * (2.0 if L <= 10 else 1.0)) for L in SIZES]
    held = [obs(48, power(48)), obs(64, power(64))]
    fits = fit_laws(Q.laws, fit_obs, "log")
    leading = rank(fits).best.name
    assert leading != "power"
    variants = fragility(Q, fit_obs, held, {"law": leading}, "log")
    dropped = next(v for v in variants if v["variant"] == "without the 2 smallest")
    assert not dropped["agrees"]


def test_fragility_agrees_on_clean_data():
    fit_obs, predictions = _predictions()
    held = [obs(48, power(48)), obs(64, power(64))]
    decision = decide(Q, fit_obs, held, predictions, "log")
    variants = fragility(Q, fit_obs, held, decision, "log")
    assert len(variants) == 2 + len(SIZES) and all(v["agrees"] for v in variants)


def test_planner_spends_runs_where_laws_disagree_within_budget():
    fit_obs = [obs(L, power(L)) for L in SIZES]
    ranking = rank(fit_laws(Q.laws, fit_obs, "log"))
    plan = plan_heldout(Q, ranking, fit_obs, list(Q.heldout_pool), "log", 1e15)
    assert len(plan["chosen"]) == Q.heldout_per_round
    scores = {c["label"]: c["score"] for c in plan["candidates"]}
    chosen_min = min(scores[label] for label in plan["chosen"])
    assert all(scores[label] <= chosen_min for label in scores if label not in plan["chosen"])
    # Extrapolating further separates the laws more.
    assert scores[128] > scores[40]
    cheap = plan_heldout(Q, ranking, fit_obs, list(Q.heldout_pool), "log", 1.0)
    assert cheap["chosen"] == []


def test_planner_with_one_contender_prefers_the_longest_extrapolation():
    fit_obs = [obs(L, math.exp(0.4 * L)) for L in SIZES]  # only an exponential fits this
    ranking = rank(fit_laws(Q.laws, fit_obs, "log"))
    q = Question(
        **{
            **Q.to_dict(),
            "contender_window": 0.0,
            "fit_sizes": SIZES,
            "heldout_pool": (40, 48, 64),
            "laws": tuple(Q.laws),
        }
    )
    plan = plan_heldout(q, ranking, fit_obs, [40, 48, 64], "log", 1e30)
    assert plan["contenders"] == ["exponential"] and plan["chosen"] == [40, 48, 64]
    assert np.argmax([c["score"] for c in plan["candidates"]]) == 2
