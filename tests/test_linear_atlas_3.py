"""Round 3 of the linear-rule atlas (examples/linear-atlas-3): the refined statement as a fixed
procedure, registered on 344 new rules; the run resumed after a time limit; the failures
analysed afterwards."""

import json
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "linear-atlas-3"


def _ledger() -> Ledger:
    return Ledger(LAB / "ledger.jsonl")


def test_the_ledger_is_intact_including_the_resumed_run():
    ledger = _ledger()
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == (
        ["question"]
        + ["prediction"] * 344
        + ["run_started", "run_resumed", "observations", "verdict"]
    )
    verdict = ledger.entries[-1]["body"]
    assert verdict["cites"]["run_started"] == ledger.entries[345]["hash"]


def test_43_of_11358_predictions_failed_and_every_mechanism_but_one_split_held():
    verdict = _ledger().entries[-1]["body"]
    assert (verdict["predictions"], verdict["failed"]) == (11358, 43)
    assert verdict["strict"] == "refuted" and verdict["accidents"] == "refuted"
    for lattice, steps in verdict["summary"].items():
        for step, counts in steps.items():
            if step.startswith(("dilation", "power")):
                assert counts["failed"] == 0, (lattice, step)
    assert verdict["summary"]["hexagon"]["splits into 1+u"] == {"held": 66, "failed": 1}
    large = {(f["rule"], f["m"]) for f in verdict["failures"] if f["m"] > 37}
    assert {rule for rule, _ in large} == {"triangle VO+T13"}


def test_vo_t13_failed_where_expectation_version_3_said():
    verdict = _ledger().entries[-1]["body"]
    expectation = json.loads((LAB / "expectation.json").read_text())["version 3"]
    failed = sorted(f["m"] for f in verdict["failures"] if f["rule"] == "triangle VO+T13")
    assert failed == expectation["expected failures"] == [25, 29, 35, 53, 55, 95, 101]
    analysis = json.loads((LAB / "analysis.json").read_text())["VO+T13 expectations"]
    assert analysis["version 3"]["match"] == 34
    assert (
        analysis["version 3"]["of those, match"]
        == analysis["version 3"]["sizes computed after it was written"]
        == 29
    )
    assert analysis["s(VO+T13) = s_E(x, y) s_E(x^3, y^3)"] is True


def test_every_record_agrees_with_the_eigenvalue_computation():
    check = json.loads((LAB / "eigen.json").read_text())
    assert check["records"] == check["agree"] == 11662 and check["disagree"] == []
