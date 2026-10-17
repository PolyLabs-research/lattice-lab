"""Round 2 of the XOR period test (examples/xor-periods-algebra): the exact method agrees with the
simulations, its ledger is intact and ordered, and its verdict is what the write-up says."""

import importlib.util
import json
import sys
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "xor-periods-algebra"
ROUND_1 = LAB.parent / "xor-periods"


def _algebra():
    sys.path.insert(0, str(LAB))
    spec = importlib.util.spec_from_file_location("xor_algebra", LAB / "algebra.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_exact_method_matches_the_simulations():
    algebra = _algebra()
    simulated = {}
    for line in (ROUND_1 / "records.jsonl").read_text().splitlines():
        record = json.loads(line)
        if record["start"] == "soup":
            simulated[record["grid"]] = max(simulated.get(record["grid"], 0), record["period"])
    for n in (36, 55, 74, 99):
        assert algebra.torus_period(n)["period"] == simulated[n]
    assert algebra.torus_period(37)["period"] == 262143
    assert algebra.rule90_period(37) == 87381


def test_the_ledger_is_intact_and_the_verdict_holds():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    assert [e["kind"] for e in ledger.entries] == [
        "question",
        "prediction",
        "prediction",
        "run_started",
        "observations",
        "verdict",
    ]
    verdict = ledger.entries[-1]["body"]
    assert verdict["law"] == {
        "confirmed": 198,
        "refuted": 0,
        "refuted_at": [],
        "confirmed_new": 120,
    }
    assert verdict["rival_refuted_at"] == [37, 74, 95, 101, 111, 141, 148, 190, 197, 199]
    assert verdict["transients_within_bounds"]
    assert verdict["outcomes"]["199"]["period"] == 2**99 - 1
