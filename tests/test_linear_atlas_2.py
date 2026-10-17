"""Round 2 of the linear-rule atlas (examples/linear-atlas-2): the factorisation pattern,
registered, then judged on 34 atlas rules at new sizes and on 112 rules never computed before."""

import sys
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "linear-atlas-2"
sys.path.insert(0, str(LAB))


def _ledger() -> Ledger:
    return Ledger(LAB / "ledger.jsonl")


def test_the_ledger_is_intact_and_registered_before_the_run():
    ledger = _ledger()
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == ["question"] + ["prediction"] * 150 + ["run_started", "observations", "verdict"]
    parts = [e["body"]["part"] for e in ledger.entries if e["kind"] == "prediction"]
    assert parts.count("A") == 34 and parts.count("B") == 116


def test_the_pairs_seen_before_registration_are_not_test_sizes():
    seen = {"hexagon H1+self", "triangle E+VO+VS"}
    for entry in _ledger().entries:
        if entry["kind"] == "prediction" and entry["body"]["rule"] in seen:
            assert "394" not in entry["body"]["predictions"]


def test_the_factor_search_finds_known_factorisations():
    import atlas2
    import factor

    hexagon = factor.split(factor.polynomial("hexagon", ("H1",)))
    assert hexagon["splits"] and [f["factor"] for f in hexagon["factors"]] == ["1+u"] * 3
    assert atlas2.classify(("K8",))["call"] == "P90"  # K8 = N4 D4
    assert atlas2.classify(("A4", "B4", "self"))["call"] == "P150"  # (N4 + D4 + self)^2
    assert atlas2.classify(("N4", "self"))["call"] == "full bound"


def test_part_a_held_everywhere_and_part_b_failed_seven_times():
    verdict = _ledger().entries[-1]["body"]
    assert verdict["pattern"] == "refuted"
    assert verdict["summary"]["A"] == {"1D: held": 11, "full bound: held": 21, "constant: held": 2}
    assert verdict["summary"]["B"] == {
        "full bound: held": 100,
        "full bound: failed": 6,
        "P90: held": 4,
        "P90: failed": 1,
        "P150: held": 1,
        "1D rule: held": 1,
        "no prediction": 3,
    }
    assert sorted(verdict["failed"]) == sorted(
        [
            "square C4+self",
            "square A4+C4",
            "square A4+C4+self",
            "square N4+K8+C4",
            "square A4+K8+B4+self",
            "square A4+K8+C4+self",
            "square A4+K8+B4+C4+self",
        ]
    )


def test_the_cubes_and_the_dilation_fail_exactly_where_written_down():
    import json

    analysis = json.loads((LAB / "analysis.json").read_text())
    explained = analysis["explained"]
    assert {k: v["registered prediction failed"] for k, v in explained.items()} == {
        "square N4+K8+C4": 22,
        "square A4+K8+C4+self": 25,
        "square C4+self": 8,
    }
    assert all(v["every size as expected"] for v in explained.values())
    expectation = json.loads((LAB / "cube-expectation.json").read_text())
    verdict = _ledger().entries[-1]["body"]["rules"]
    written = {**expectation["rules"], expectation["dilation"]["rule"]: expectation["dilation"]}
    for rule, entry in written.items():
        assert sorted(f["n"] for f in verdict[rule]["failures"]) == entry["expected failures"]
        for f in verdict[rule]["failures"]:
            assert str(f["period"]) == entry["expected period there"][str(f["n"])]
    assert sorted((f["rule"], f["n"]) for f in analysis["unforeseen failures"]) == [
        ("square A4+C4", 13),
        ("square A4+C4+self", 13),
        ("square A4+K8+B4+C4+self", 13),
        ("square A4+K8+B4+self", 37),
    ]
