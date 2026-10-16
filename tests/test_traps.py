"""Regression tests for the settling-time prototype's three traps (2026-10-16)."""

import sympy
from helpers import TableExperimenter
from kepler import LAWS
from kepler.refine import parametrize

from lattice_lab.ledger import Ledger
from lattice_lab.loop import ask
from lattice_lab.question import Question

Q = Question(
    id="trap",
    rule="B2/S34",
    shape="hexagon",
    fit_sizes=(8, 10, 12, 16, 20, 24, 32),
    heldout_pool=(40, 48, 64, 96, 128),
)


def test_trap_1_a_zero_starting_constant_must_not_vanish():
    # SymPy drops Float(0.0) + x to x. Every law the loop fits keeps all its constants, even
    # when its data-driven starting guess is exactly zero.
    sizes = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    for law in LAWS.values():
        # Laws of several variables (survival over density and size) take x as a dict.
        x = sizes if law.variables == ("x",) else {v: sizes for v in law.variables}
        for y in ([0.0] * 6, [5.0] * 6, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]):
            skeleton = law.skeleton(x, y)
            assert len(parametrize(sympy.sympify(skeleton))[1]) == len(law.params), skeleton


def test_trap_2_a_verdict_must_survive_dropping_the_smallest_sizes():
    # The two smallest tori follow another curve. Whatever the loop answers, it must not name
    # a law the larger sizes do not support.
    def settling(L):
        return 27.0 * L**0.6 * (2.0 if L <= 10 else 1.0)

    for rel in (0.03, 0.08):
        outcome = ask(Q, TableExperimenter(settling, rel), Ledger(None))
        assert not (outcome.verdict == "found" and outcome.law != "power"), outcome


def test_trap_3_an_unsettled_run_never_counts_against_a_law():
    # Every held-out size has seeds that never repeated: nothing can be tested, so nothing is
    # rejected, and the answer is inconclusive, not "none fits".
    unsettled = set(Q.heldout_pool)
    outcome = ask(Q, TableExperimenter(lambda L: 27.0 * L**0.6, unsettled=unsettled), Ledger(None))
    assert outcome.verdict == "inconclusive"
    ledger_entry = outcome.note
    assert "nothing was tested" in ledger_entry


def test_trap_3_only_settled_held_out_sizes_are_judged():
    ledger = Ledger(None)
    outcome = ask(Q, TableExperimenter(lambda L: 27.0 * L**0.6, unsettled={128, 96}), ledger)
    verdict = ledger.get(outcome.verdict_hash)["body"]
    for test in verdict["tests"]:
        judged = {p["label"] for p in test["points"]}
        assert judged.isdisjoint({96, 128})
    assert outcome.verdict in ("found", "inconclusive", "fragile")
