"""The machine-checked parts of docs/xor-periods-proof.md: the odd-N verifier on known cases, the
committed scan, and Theorems 3 and 4 against round 2's exact periods."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "examples"


def _checker():
    spec = importlib.util.spec_from_file_location(
        "check_odd", ROOT / "xor-periods-proof" / "check_odd.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_verifier_finds_rule_90s_shortfalls_and_the_2d_rescue():
    check = _checker().check
    at37, at199 = check(37), check(199)
    assert at37["complete"] and at37["rule90_obstructed_by"] == [3] and at37["unresolved"] == []
    assert at199["complete"] and at199["rule90_obstructed_by"] == [7] and at199["unresolved"] == []
    assert check(41)["rule90_obstructed_by"] == []


def test_the_scan_leaves_nothing_unresolved():
    rows = [
        json.loads(line)
        for line in (ROOT / "xor-periods-proof" / "results.jsonl").read_text().splitlines()
    ]
    assert [r["N"] for r in rows] == list(range(3, 1000, 2))
    assert not any("error" in r or r["unresolved"] for r in rows)
    incomplete = [r["N"] for r in rows if not r["complete"]]
    assert incomplete == [529, 587, 719, 827, 839, 859, 883, 947, 983, 991]  # as the write-up says
    assert sum(1 for r in rows if r["rule90_obstructed_by"]) == 50


def test_theorems_3_and_4_hold_at_every_exact_size():
    rows = {}
    for line in (ROOT / "xor-periods-algebra" / "records.jsonl").read_text().splitlines():
        record = json.loads(line)
        rows[record["n"]] = record
    for n, record in rows.items():
        k, odd = 0, n
        while odd % 2 == 0:
            odd, k = odd // 2, k + 1
        if odd == 1:
            assert record["period"] == 1 and record["transient"] == n // 2  # Theorem 3
        elif k:
            assert record["period"] == 2**k * rows[odd]["period"]  # Theorem 4
            assert record["transient"] <= 2**k
        else:
            assert record["transient"] == 1  # Theorem 2
