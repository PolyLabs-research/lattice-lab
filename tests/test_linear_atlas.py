"""The linear-rule atlas (examples/linear-atlas): Kepler's registered laws for 42 shell-built
linear rules, judged at new sizes. Every rule with a law kept one at every size, and the
analysis afterwards (factors.json) sorts the rules into the two families that held."""

import json
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "linear-atlas"


def _verdict() -> dict:
    return Ledger(LAB / "ledger.jsonl").entries[-1]["body"]


def test_the_ledger_is_intact_and_registered_before_the_run():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == ["question"] + ["prediction"] * 42 + ["run_started", "observations", "verdict"]


def test_every_rule_with_a_law_kept_one_at_every_size():
    verdict = _verdict()
    assert verdict["summary"] == {
        "blind": {"first law confirmed": 17, "a rival confirmed": 13, "no law": 8},
        "studied": {"first law confirmed": 2, "a rival confirmed": 2},
    }
    rules = verdict["rules"]
    assert len(rules) == 42
    for rule in rules.values():
        if rule["status"] != "no law":
            assert rule["survivors"]
    assert rules["square N4"]["survivors"] == ["P90(n)"]  # Vadali and Turner's theorem
    assert rules["square D4+A4+self"]["survivors"] == ["P150(n)"]
    assert "2*P90(n)" in rules["hexagon H1"]["survivors"]
    assert rules["hexagon H1+self"]["survivors"] == ["2*2^v(n)*(2^sord(n) - 1)"]
    assert rules["hexagon H1+self"]["laws"]["2*P90(n)"]["first_failure"]["n"] == 74


def test_the_rules_that_split_are_the_ones_with_a_1d_period():
    factors = json.loads((LAB / "factors.json").read_text())
    one_d = factors["one-dimensional factors"]
    assert len(one_d) == 42
    kinds = {
        (r["splits"], r["registered law that held"])
        for r in one_d.values()
        if r["registered law that held"] not in (None, "constant")
    }
    assert kinds == {(True, "a 1D rule's period"), (False, "the full bound")}
    assert sum(r["splits"] for r in one_d.values() if r["registered law that held"]) == 12
    quadratics = factors["quadratics"]
    no_law = {k for k, r in _verdict()["rules"].items() if r["status"] == "no law"}
    assert no_law <= set(quadratics)
    assert quadratics["square A4"]["period is the root's halved when even"]
