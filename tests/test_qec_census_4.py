"""Census stage 4's instrument (examples/qec-census-4/fast4.py): the parity helpers, census4.c's
two changed lines, the guard, the parity path of `exact`, and the frontier against stage 3b's on
two tori stage 3b already computed (skipped without DistQLDPC)."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FAST4 = ROOT / "examples" / "qec-census-4" / "fast4.py"
spec = importlib.util.spec_from_file_location("qec_census_stage4_fast", FAST4)
F = importlib.util.module_from_spec(spec)
sys.modules["qec_census_stage4_fast"] = F
spec.loader.exec_module(F)


def test_parity_helpers():
    assert [F.even_down(u) for u in (None, 23, 24, 3)] == [None, 22, 24, 2]
    assert [F.even_up(x) for x in (None, 23, 24, 1)] == [None, 24, 24, 2]


def test_census4_differs_only_in_capacity():
    old = (ROOT / "examples/qec-census/census.c").read_text().splitlines()
    new = F.CENSUS4_C.read_text().splitlines()
    diff = [(a, b) for a, b in zip(old, new, strict=True) if a != b]
    assert [b.split()[:3] for _, b in diff] == [
        ["#define", "MAXLM", "200"],
        ["#define", "WORDS", "7"],
    ]


def test_opened_lets_through_only_its_tori_and_restores():
    guard, c = F.census.guard, F.census.CENSUS_C
    with F.opened([(2, 28)]):
        F.census.guard(2, 28)
        with pytest.raises(F.census.HeldOut):
            F.census.guard(3, 49)
        assert F.census.CENSUS_C == F.CENSUS4_C
    assert F.census.guard is guard and F.census.CENSUS_C == c
    with pytest.raises(F.census.HeldOut):
        F.census.guard(2, 28)


def test_exact_parity_path(monkeypatch):
    # DistQLDPC stops at lower 23; the window's verified witness has weight 24: d = 24 by parity
    A, B = [[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]]  # [[72,12,6]] on 6 x 6
    witness = [0, 5, 4, 1, 21, 23]
    fake = {"d": None, "lower": 5, "upper": 6, "returncode": 1, "withdrawn": False, "seconds": 1}
    monkeypatch.setattr(F.distq, "run", lambda *a, **k: fake)
    row = {"A": A, "B": B, "k": 12, "upper": 6, "witness": witness}
    r = F.exact(row, 6, 6)
    assert r["status"] == "complete" and r["by"] == "parity" and r["d"] == 6
    monkeypatch.setattr(F.distq, "run", lambda *a, **k: fake | {"lower": 3})
    assert F.exact(row, 6, 6)["status"] == "timelimit"
    monkeypatch.setattr(F.distq, "run", lambda *a, **k: fake | {"lower": 7})
    with pytest.raises(RuntimeError):
        F.exact(row, 6, 6)


def test_exact_finds_a_witness_when_the_window_has_none(monkeypatch):
    # DistQLDPC says d = 6; the first window found nothing of weight 6: longer windows must
    A, B = [[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]]
    fake = {"d": 6, "lower": 6, "upper": 6, "returncode": 0, "withdrawn": False, "seconds": 1}
    monkeypatch.setattr(F.distq, "run", lambda *a, **k: fake)
    monkeypatch.setattr(F, "WITNESS_WINDOWS", [[[1, 2], 5.0]])
    for row in ({"A": A, "B": B, "k": 12, "upper": 8, "witness": None},
                {"A": A, "B": B, "k": 12, "upper": None, "witness": None}):  # fmt: skip
        r = F.exact(row, 6, 6)
        assert r["status"] == "complete" and r["by"] == "distqldpc" and len(r["witness"]) == 6


def test_exact_survives_a_distqldpc_failure(monkeypatch):
    A, B = [[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]]

    def boom(*a, **k):
        raise RuntimeError("distqldpc exited -9")

    monkeypatch.setattr(F.distq, "run", boom)
    r = F.exact({"A": A, "B": B, "k": 12, "upper": 8, "witness": None}, 6, 6)
    assert r["status"] == "timelimit" and "exited -9" in r["error"]
    killed = {"engine": "cc", "k": 12, "lower": None, "d": None, "upper": None, "seconds": 1,
              "returncode": None, "tail": "killed"}  # fmt: skip
    monkeypatch.setattr(F.distq, "run", lambda *a, **k: killed)
    assert F.exact({"A": A, "B": B, "k": 12, "upper": 8, "witness": None}, 6, 6)["status"] == \
        "timelimit"  # fmt: skip


@pytest.mark.skipif(not F.distq.BINARY.exists(), reason="DistQLDPC not built")
@pytest.mark.parametrize("torus", [(2, 28), (3, 21)])
def test_frontier_matches_stage3b(torus):
    with F.opened([torus]):
        a = F.frontier(*torus, workers=4, limit=300, log=lambda s: None)
        b = F.fast.frontier(*torus, workers=4, limit=300, log=lambda s: None)
    assert a["best"] == b["best"]
    # a rerun from the checkpoint gives the same, with no new exact run
    seen = {}
    with F.opened([torus]):
        c = F.frontier(*torus, workers=4, limit=300, log=lambda s: None,
                       on_exact=lambda key, res, row: seen.setdefault(key, res))  # fmt: skip
        calls = []
        d = F.frontier(*torus, workers=4, limit=300, log=lambda s: None, cache=seen,
                       on_exact=lambda key, res, row: calls.append(key))  # fmt: skip
    assert c["best"] == d["best"] == a["best"] and not calls
    for r in a["classes"]:
        if "exact" in r and r["exact"]["status"] == "complete":
            check = F.distance.verify_witness([tuple(t) for t in r["A"]],
                                              [tuple(t) for t in r["B"]], *torus, "Z",
                                              r["exact"]["witness"])  # fmt: skip
            assert check["logical"] and check["weight"] == r["exact"]["d"]
