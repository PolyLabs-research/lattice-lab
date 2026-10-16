"""The capabilities example (examples/capabilities/run.py) imports against the pinned libraries,
and its committed results say what docs/capabilities.md says they do."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "capabilities"


def test_the_example_imports_against_the_pinned_libraries():
    spec = importlib.util.spec_from_file_location("capabilities_run", EXAMPLE / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in (
        "survival_study",
        "censored_study",
        "joint_study",
        "time_study",
        "distribution_study",
        "integer_study",
        "invariant_study",
    ):
        assert callable(getattr(module, name))
    assert module.clean({"a": float("nan"), "b": [1.23456789]}) == {"a": None, "b": [1.234568]}


def test_the_committed_results_hold_the_headline_findings():
    results = json.loads((EXAMPLE / "results.json").read_text())
    xor = results["integer"]["xor"]
    assert xor["laws"][0]["expression"] == "2^v(n)*(2^sord(n) - 1)"
    assert all(v["predicted"] == v["measured"] for v in xor["held_out"].values())
    assert results["integer"]["glider"]["laws"][0]["expression"] == "4*n"
    for rule, entry in results["invariants"].items():
        assert entry["all"]["known_identities_found"] and entry["all"]["beyond_bookkeeping"] == 0, (
            rule
        )
