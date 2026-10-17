"""The pre-registered XOR period test (examples/xor-periods): its ledger is intact, its predictions
precede its run, and its verdict says what docs/xor-periods.md says it does."""

import importlib.util
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "xor-periods"


def test_the_ledger_is_intact_and_the_predictions_came_first():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == [
        "question",
        "prediction",
        "prediction",
        "prediction",
        "run_started",
        "observations",
        "verdict",
    ]
    verdict = ledger.entries[-1]["body"]
    assert verdict["law"] == {"confirmed": 45, "short": 0, "refuted": 0}
    assert verdict["rival_refuted_at"] == [74]
    assert verdict["controls_pass"] and verdict["odd_transients_ok"]
    assert verdict["outcomes"]["74"]["soups"] == [524286] * 3
    assert verdict["outcomes"]["74"]["column"] == 174762


def test_the_registered_predictions_are_the_laws():
    spec = importlib.util.spec_from_file_location("xor_study", LAB / "study.py")
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    ledger = Ledger(LAB / "ledger.jsonl")
    law, rival = ledger.entries[1]["body"]["predictions"], ledger.entries[2]["body"]["predictions"]
    assert law == {str(n): study.law(n) for n in study.sizes()}
    assert rival == {str(n): study.rule90_period(n) for n in study.sizes()}
    assert study.rule90_period(37) == 87381  # rule 90's published first shortfall
