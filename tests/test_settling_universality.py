"""The settling-time universality test (examples/settling-universality): the rules are the ones
the seeded selection kept, the ledger is intact and ordered, and the verdict is what
docs/settling-time.md reports."""

import json
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "settling-universality"


def test_the_selection_kept_the_first_two_passing_rules_per_lattice():
    log = [json.loads(line) for line in (LAB / "selection.jsonl").read_text().splitlines()]
    chosen = json.loads((LAB / "selected.json").read_text())
    for lattice, entry in chosen.items():
        kept = [r["rule"] for r in log if r["lattice"] == lattice and r["kept"]]
        assert kept == entry["rules"] and len(kept) == 2
    assert len(log) == 79


def test_the_ledger_is_intact_and_the_verdict_holds():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == ["question"] + ["prediction"] * 66 + ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    rules = verdict["rules"]
    assert len(rules) == 8
    assert all(r["survivors"] == ["logarithmic"] and r["unsettled"] == [] for r in rules.values())
    assert all(r["mechanisms"]["frechet"]["status"] == "rejected" for r in rules.values())
    gumbel = {k: r["mechanisms"]["gumbel"]["status"] for k, r in rules.items()}
    assert [k for k, s in gumbel.items() if s == "rejected"] == ["triangle-edge B123/S012"]
    u1, u2 = verdict["U1 shape"], verdict["U2 amplitude ratio"]
    assert u1["status"] == "confirmed" and u1["sharing"]["best"] == ["a"]
    assert abs(u1["shared_value"] - 0.177) < 0.001
    assert u2["status"] == "confirmed" and u2["left_out"] == []
    assert abs(u2["shared_value"] - 0.765) < 0.001 and u2["p_same"] > 0.5
