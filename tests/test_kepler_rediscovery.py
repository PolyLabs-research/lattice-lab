"""The rediscovery test (examples/kepler-rediscovery): with the 1D linear rules' periods in its
vocabulary, Kepler lists both laws on the discovery data, names the size that decides, and on
the data up to 200 keeps exactly the right one on each lattice."""

from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "kepler-rediscovery"


def test_the_ledger_is_intact_and_every_expectation_held():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == ["question"] + ["prediction"] * 8 + ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["confirmed"] == 8 and verdict["refuted"] == []
    outcomes = verdict["outcomes"]
    hexagon = outcomes["hexagon, odd part at least 5 | up to 200"]["found"]
    assert hexagon["laws"] == ["2*P90(n)"] and hexagon["predicts round 2"]
    assert hexagon["round 2 sizes"] == 98
    for name in ("triangle-edge", "triangle-edge+vertex"):
        found = outcomes[f"{name}, n not a power of 2 | up to 200"]["found"]
        assert found["laws"] == ["2*2^v(n)*(2^sord(n) - 1)"]
        assert outcomes[f"{name}, n not a power of 2 | discovery"]["found"]["decides at"] == 74
    square = outcomes["square, n not a power of 2 | discovery"]["found"]
    assert square["laws"][:2] == ["P90(n)", "2^v(n)*(2^sord(n) - 1)"] and square["decides at"] == 37
