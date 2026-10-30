"""Census stage 3d (examples/qec-census-3d/study.py): the listed classes, prediction T, the
verdict logic on synthetic records, and one job on [[72,12,6]] (skipped without DistQLDPC)."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "qec_census_3d", ROOT / "examples/qec-census-3d/study.py"
)
S = importlib.util.module_from_spec(spec)
sys.modules["qec_census_3d"] = S
spec.loader.exec_module(S)


def test_classes():
    cs = S.classes()
    assert len(cs) == 154
    assert len({S.key(c) for c in cs}) == 154
    assert {tuple(c["torus"]) for c in cs} == set(S.TORI)
    assert all(c["lower"] == 23 and c["upper"] == 24 and c["best_recorded"] == 22 for c in cs)
    assert {c["k"] for c in cs} == {4, 6}
    assert [len(S.torus_records())] == [9]


def test_t_expected():
    t = S.t_expected()
    assert set(t) == {f"{a}x{b}" for a, b in S.TORI}
    for name, v in t.items():
        if name == "3x49":
            assert v == {"P1": "pass", "P2": "pass", "P3": "fail"}
        else:
            assert v == {"P1": "pass", "P2": "fail", "P3": "pass"}


def test_amended_keeps_unsettled_when_a_class_is_missing():
    _, _, _, rec = S.torus_records()[0]
    k = min(S.unsettled(rec))
    out = S.amended(rec, {k: [24, None]})
    assert out["best"]["connected"][str(k)] == {**rec["best"]["connected"][str(k)], "d": 24}
    assert not out["best"]["connected"][str(k)]["settled"]


def fake(c, d=24, w=24, logical=True, rc=0):
    return {"key": S.key(c), "class": c, "seconds": 1.0,
            "distqldpc": {"d": d, "lower": d, "upper": d, "returncode": rc,
                          "commit": S.DISTQLDPC_COMMIT},
            "witness_check": {"weight": w, "logical": logical}}  # fmt: skip


@pytest.fixture
def registered(monkeypatch):
    monkeypatch.setattr(S, "consistency", lambda: [])
    return S.predictions()


def test_decide_pass(registered):
    v = S.decide([fake(c) for c in S.classes()], registered)
    assert v["verdict"] == "pass" and v["D1"] == "pass" and v["T"] == "pass"
    assert v["settled_at_24"] == 154


def test_decide_contradiction(registered):
    cs = S.classes()
    rows = [fake(c) for c in cs[1:]] + [fake(cs[0], d=22, w=24)]
    v = S.decide(rows, registered)
    assert v["D1"] == "fail" and v["verdict"] == "fail" and v["contradictions"] == [S.key(cs[0])]
    rows = [fake(c) for c in cs[1:]] + [fake(cs[0], d=24, w=22)]
    assert S.decide(rows, registered)["D1"] == "fail"


def test_decide_incomplete(registered):
    cs = S.classes()
    v = S.decide([fake(c) for c in cs[1:]], registered)
    assert v["D1"] == "incomplete" and v["verdict"] == "incomplete" and v["T"] == "incomplete"
    timed = {**fake(cs[0]), "distqldpc": {"d": None, "lower": 20, "upper": 24, "returncode": 1,
                                          "commit": S.DISTQLDPC_COMMIT}}  # fmt: skip
    assert S.decide([fake(c) for c in cs[1:]] + [timed], registered)["D1"] == "incomplete"


@pytest.mark.skipif(not S.distq.BINARY.exists(), reason="DistQLDPC not built")
def test_job_on_a_small_code(monkeypatch):
    monkeypatch.setattr(S, "WINDOW_FIRST", ((0,), 5.0))
    monkeypatch.setattr(S, "D_EXPECTED", 6)
    c = {"torus": [6, 6], "n": 72, "k": 12, "A": [[3, 0], [0, 1], [0, 2]],
         "B": [[0, 3], [1, 0], [2, 0]], "lower": 5, "upper": 6, "best_recorded": 4}  # fmt: skip
    rec = S.job(c)
    assert "error" not in rec, rec.get("error")
    assert rec["distqldpc"]["d"] == 6 and rec["witness_check"]["logical"]
    assert rec["witness_check"]["weight"] == 6 and S.assess(rec) == "24"  # i.e. "the expected d"
