"""The machine check of the triangular lattices' odd part (examples/parity-lattices-proof): the
verifier finds the hexagon's known shortfalls, agrees with the exact periods, and the committed
scan is what docs/parity-lattices.md reports."""

import importlib.util
import json
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
LAB = EXAMPLES / "parity-lattices-proof"
TRIANGLES = ("triangle-edge", "triangle-edge+vertex")


def _checker():
    spec = importlib.util.spec_from_file_location("check_triangles", LAB / "check_triangles.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_the_hexagon_control_is_left_unresolved_exactly_at_rule_90s_shortfalls():
    """The hexagon's eigenvalues generate rule 90's group (proved), so a working verifier must
    fail to rescue it where rule 90 falls short, and only there."""
    check = _checker().check
    rule90 = {
        r["N"]: r["rule90_obstructed_by"]
        for r in _rows(EXAMPLES / "xor-periods-proof" / "results.jsonl")
    }
    for N in (37, 41, 95, 101, 111, 199):
        result = check(N, rules=("hexagon", *TRIANGLES))
        assert result["complete"]
        assert result["hexagon"]["unresolved"] == rule90[N]
        assert result["triangle-edge+vertex"]["first_line_obstructed_by"] == rule90[N]
        assert all(result[rule]["unresolved"] == [] for rule in TRIANGLES)


def test_the_scan_agrees_with_the_exact_periods():
    scan = {r["N"]: r for r in _rows(LAB / "results.jsonl")}
    rows = []
    for name in (
        "parity-lattices/discovery.jsonl",
        "parity-lattices/records.jsonl",
        "parity-lattices-hexagon/records.jsonl",
    ):
        rows += _rows(EXAMPLES / name)
    checked = set()
    for row in rows:
        if row["lattice"] not in TRIANGLES:
            continue
        n, m = row["n"], row["n"]
        while m % 2 == 0:
            m //= 2
        if m < 3:
            continue
        holds = scan[m]["complete"] and not scan[m][row["lattice"]]["unresolved"]
        full = 2 * (n // m) * (2 ** scan[m]["s"] - 1)
        assert holds == (row["period"] == full)
        checked.add(m)
    assert len(checked) == 54


def test_the_scan_leaves_nothing_unresolved():
    rows = _rows(LAB / "results.jsonl")
    assert [r["N"] for r in rows] == list(range(3, 1000, 2))
    assert not any("error" in r for r in rows)
    assert not any(r[rule]["unresolved"] for r in rows for rule in TRIANGLES)
    incomplete = [r["N"] for r in rows if not r["complete"]]
    assert incomplete == [529, 587, 719, 827, 839, 859, 883, 947, 983, 991]  # as the write-up says
    # the 1D lines fall short where rule 150 (edge) and rule 90 (edge+vertex) do
    assert sum(1 for r in rows if r["triangle-edge"]["first_line_obstructed_by"]) == 87
    assert sum(1 for r in rows if r["triangle-edge+vertex"]["first_line_obstructed_by"]) == 50
