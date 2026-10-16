"""The loop end to end on synthetic data: the ledger it writes, the order it keeps, the report."""

import numpy as np
from helpers import TableExperimenter

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.loop import ask
from lattice_lab.question import Question
from lattice_lab.report import render
from lattice_lab.selfcheck import TRUE_LAWS, SyntheticExperimenter, synthetic_question

Q = Question(
    id="loop",
    rule="B2/S34",
    shape="hexagon",
    fit_sizes=(8, 10, 12, 16, 20, 24, 32),
    heldout_pool=(40, 48, 64, 96, 128),
)


def test_an_exponential_is_found_and_every_step_is_in_the_ledger(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    experimenter = TableExperimenter(lambda L: 20.0 * np.exp(0.05 * L))
    outcome = ask(Q, experimenter, ledger, provenance={"python": "3"})
    assert (outcome.verdict, outcome.law, outcome.rounds) == ("found", "exponential", 1)
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[:4] == ["question", "run_started", "observations", "plan"]
    assert kinds[-3:] == ["run_started", "observations", "verdict"]
    assert kinds.count("prediction") >= 1
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    # Predictions were made before the held-out sizes were measured.
    assert experimenter.calls == [list(Q.fit_sizes), ledger.entries[-3]["body"]["labels"]]
    verdict = ledger.entries[-1]["body"]
    assert verdict["final"] and all(v["agrees"] for v in verdict["robustness"])
    report = render(ledger, outcome.question_hash)
    assert "**Verdict: found**: exponential" in report
    assert "recorded before the run" in report


def test_an_inconclusive_round_feeds_the_next():
    def settling(L):  # linear and power with b ~ 1 are hard to tell apart
        return 2.5 * L + 10.0

    ledger = Ledger(None)
    q = Question(
        **{
            **Q.to_dict(),
            "laws": tuple(Q.laws),
            "fit_sizes": Q.fit_sizes,
            "heldout_pool": Q.heldout_pool,
            "max_rounds": 2,
        }
    )
    outcome = ask(q, TableExperimenter(settling, rel=0.1), ledger)
    plans = [e for e in ledger.entries if e["kind"] == "plan"]
    if outcome.rounds == 2:
        first, second = plans[0]["body"], plans[1]["body"]
        assert set(first["chosen"]).isdisjoint(second["chosen"])
        assert set(first["chosen"]) <= set(second["fit_labels"])
    assert outcome.verdict != "found" or outcome.law in ("linear", "power")


def test_too_small_a_budget_stops_before_running():
    q = Question(
        **{
            **Q.to_dict(),
            "laws": tuple(Q.laws),
            "fit_sizes": Q.fit_sizes,
            "heldout_pool": Q.heldout_pool,
            "budget_cell_steps": 10.0,
        }
    )
    experimenter = TableExperimenter(lambda L: L)
    ledger = Ledger(None)
    outcome = ask(q, experimenter, ledger)
    assert outcome.verdict == "inconclusive" and experimenter.calls == []
    assert "budget" in render(ledger, outcome.question_hash)


def test_too_few_settled_fit_sizes():
    experimenter = TableExperimenter(lambda L: L, unsettled={8, 10, 12, 16})
    ledger = Ledger(None)
    outcome = ask(Q, experimenter, ledger)
    assert outcome.verdict == "inconclusive" and "sizes settled" in outcome.note
    report = render(ledger, outcome.question_hash)
    assert "unsettled" in report and "Round 1: inconclusive" in report


def test_none_fits_is_reported():
    # Settling time that jumps at one size: no smooth law predicts the held-out sizes.
    ledger = Ledger(None)
    outcome = ask(Q, TableExperimenter(lambda L: 50.0 if L < 40 else 5000.0, rel=0.03), ledger)
    assert outcome.verdict == "none fits"
    report = render(ledger, outcome.question_hash)
    assert "**Verdict: none fits**" in report and "rejected" in report


def test_synthetic_experimenter_censors_like_real_runs():
    q = synthetic_question("exponential", seeds=10)
    experimenter = SyntheticExperimenter(
        "exponential", {"a": 20.0, "b": 0.12}, q, 0.35, np.random.default_rng(0)
    )
    measured = experimenter.measure([16, 96], 1e30)
    small, large = measured.observations
    assert small.complete and small.y > 0
    # 20 e^(0.12 * 96) ~ 2e6 generations: beyond max_cap, so only a bound.
    assert not large.complete and large.y is None and large.max_cap == q.max_cap - 1


def test_every_true_law_has_constants():
    for law, params in TRUE_LAWS.items():
        q = synthetic_question(law, 4)
        experimenter = SyntheticExperimenter(law, params, q, 0.35, np.random.default_rng(1))
        assert experimenter.truth(64.0) > 0
