"""Census stage 4d (examples/qec-census-4d/study.py): the selection rule on synthetic stage 4
files, the verdict logic on synthetic records, the amended frontier, and one job on [[72,12,6]]
(skipped without DistQLDPC)."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "qec_census_4d", ROOT / "examples/qec-census-4d/study.py"
)
S = importlib.util.module_from_spec(spec)
sys.modules["qec_census_4d"] = S
spec.loader.exec_module(S)

GROSS_A = [[3, 0], [0, 1], [0, 2]]
GROSS_B = [[0, 3], [1, 0], [2, 0]]


def row(A, B, k, status, d=None, lower=None, upper=None, connected=True, dq=None):
    e = {"status": status, "d": d, "lower": lower}
    if dq is not None:
        e["distqldpc"] = {"d": dq}
    return {"A": A, "B": B, "k": k, "key": [A, B], "connected": connected, "upper": upper,
            "exact": e}  # fmt: skip


def torus(ell, m, rows, best):
    return {"job": "torus", "l": ell, "m": m, "n": 2 * ell * m, "rows": rows,
            "best": {"connected": best, "all": best}, "classes": len(rows), "criterion_e": True,
            "k_sample": {"disagree": 0, "sampled": 50}, "class_errors": 0}  # fmt: skip


@pytest.fixture
def stage4(tmp_path, monkeypatch):
    rec, cp, led = tmp_path / "records.jsonl", tmp_path / "exact-checkpoint.jsonl", \
        tmp_path / "ledger.jsonl"  # fmt: skip
    monkeypatch.setattr(S, "S4_RECORDS", rec)
    monkeypatch.setattr(S, "S4_CHECKPOINT", cp)
    monkeypatch.setattr(S, "S4_LEDGER", led)
    S._SELECTED.clear()

    def write(records=(), checkpoint=(), ended=False):
        rec.write_text("".join(json.dumps(r) + "\n" for r in records))
        cp.write_text("".join(json.dumps(r) + "\n" for r in checkpoint))
        kinds = ["question", "run_started"] + (["verdict"] if ended else [])
        led.write_text("".join(json.dumps({"kind": k, "hash": S.STAGE4_RUN if k == "run_started"
                                           else "h", "time": "2026-10-30T19:45:04+00:00",
                                           "body": {}}) + "\n" for k in kinds))  # fmt: skip
        S._SELECTED.clear()

    return write


def cline(ell, m, A, B, status, lower=None, run=S.STAGE4_RUN, d=None):
    return {"l": ell, "m": m, "key": json.dumps([A, B]), "A": A, "B": B, "run": run,
            "exact": {"status": status, "lower": lower, "d": d}}  # fmt: skip


def test_selection(stage4):
    a1, a2, a3 = [[0, 0], [0, 1], [1, 2]], [[0, 0], [1, 1], [2, 3]], [[0, 0], [0, 5], [1, 1]]
    b = [[0, 0], [0, 7], [1, 23]]
    recs = [torus(3, 64, [row(a1, b, 4, "complete", d=28, lower=28, upper=28),
                          row(a2, b, 4, "timelimit", lower=28, upper=30),
                          row(a3, b, 8, "unverified", lower=26, upper=28, dq=26)],
                  {"4": {"d": 28, "settled": False, "unresolved": 1},
                   "8": {"d": 26, "settled": True, "unresolved": 0}})]  # fmt: skip
    cps = [
        cline(6, 33, a1, b, "timelimit", lower=28),  # a torus still running
        cline(6, 33, a2, b, "timelimit", lower=28, run="another run"),  # a foreign run
        cline(6, 33, a3, b, "complete", d=26),
        cline(3, 64, a2, b, "timelimit", lower=28),
    ]  # its torus record decides
    stage4(recs, cps)
    sel = {S.key(c): c for c in S.selected()}
    assert set(sel) == {f"3x64:{json.dumps([a2, b])}", f"3x64:{json.dumps([a3, b])}",
                        f"6x33:{json.dumps([a1, b])}"}  # fmt: skip
    t = sel[f"3x64:{json.dumps([a2, b])}"]
    assert (t["status"], t["lower"], t["upper"], t["k"], t["from"]) == ("timelimit", 28, 30, 4,
                                                                        "records")  # fmt: skip
    u = sel[f"3x64:{json.dumps([a3, b])}"]
    assert (u["status"], u["d4"]) == ("unverified", 26)
    assert sel[f"6x33:{json.dumps([a1, b])}"]["from"] == "checkpoint"
    # a class the checkpoint calls unfinished but its torus record calls complete is dropped
    stage4(recs, [cline(3, 64, a1, b, "timelimit", lower=26)])
    assert f"3x64:{json.dumps([a1, b])}" not in {S.key(c) for c in S.selected()}


def fake(c, d, w=None, logical=True, error=False, lower=None):
    r = {"key": S.key(c), "class": c, "seconds": 1.0, "d": d,
         "distqldpc": {"d": d, "lower": d if lower is None else lower, "upper": d,
                       "returncode": 0 if d is not None else 1, "commit": S.DISTQLDPC_COMMIT},
         "witness_check": None if w is None else {"weight": w, "logical": logical}}  # fmt: skip
    if error:
        r["error"] = "Traceback"
    return r


@pytest.fixture
def two(stage4, monkeypatch):
    monkeypatch.setattr(S, "consistency", lambda: [])
    a1, a2, b = [[0, 0], [0, 1], [1, 2]], [[0, 0], [1, 1], [2, 3]], [[0, 0], [0, 7], [1, 23]]
    recs = [torus(3, 64, [row(a1, b, 4, "timelimit", lower=28, upper=30),
                          row(a2, b, 4, "timelimit", lower=27, upper=30)],
                  {"4": {"d": 28, "settled": False, "unresolved": 2}})]  # fmt: skip
    stage4(recs, [], ended=True)
    return S.selected()


def test_decide_pass_and_report(two):
    v = S.decide([fake(two[0], 30, 30), fake(two[1], 28, 28)], S.predictions())
    assert (v["D1"], v["B"], v["verdict"], v["settled"]) == ("pass", "pass", "pass", 2)
    assert v["R"]["3x64"]["best"]["4"] == {"d": 30, "settled": True}


def test_decide_contradictions(two):
    P = S.predictions()
    # a verified logical lighter than the exact d
    assert S.decide([fake(two[0], 30, 28), fake(two[1], 28, 28)], P)["D1"] == "fail"
    # a d above stage 4's verified window bound
    assert S.decide([fake(two[0], 32, 32), fake(two[1], 28, 28)], P)["D1"] == "fail"
    # DistQLDPC's lower bound above a verified logical
    v = S.decide([fake(two[0], None, 28, lower=30), fake(two[1], 28, 28)], P)
    assert v["D1"] == "fail"


def test_decide_bounds_and_incomplete(two):
    P = S.predictions()
    # below stage 4's lower bound rounded up to even (28): B fails
    v = S.decide([fake(two[0], 26, 26), fake(two[1], 28, 28)], P)
    assert v["B"] == "fail" and v["verdict"] == "fail"
    # no witness, or no exact d, or a missing class: incomplete
    assert S.decide([fake(two[0], 30, None), fake(two[1], 28, 28)], P)["verdict"] == "incomplete"
    assert S.decide([fake(two[1], 28, 28)], P)["verdict"] == "incomplete"
    # an errored attempt is outweighed by a clean record of the same class
    rows = [fake(two[0], None, None, error=True), fake(two[0], 30, 30), fake(two[1], 28, 28)]
    assert S.decide(rows, P)["verdict"] == "pass"


def test_not_applicable_and_invalid(stage4, monkeypatch):
    stage4([], [], ended=True)
    monkeypatch.setattr(S, "consistency", lambda: [])
    assert S.decide([], S.predictions())["verdict"] == "not applicable"
    monkeypatch.setattr(S, "consistency", lambda: ["the code differs from the registration"])
    assert S.decide([], S.predictions())["verdict"] == "invalid"


def test_done_retries(tmp_path):
    p = tmp_path / "r.jsonl"
    p.write_text(json.dumps({"key": "a", "error": "x"}) + "\n")
    assert S._done(p) == set()
    p.write_text(p.read_text() + json.dumps({"key": "a", "error": "x"}) + "\n")
    assert S._done(p) == {"a"}


def test_registration_shape():
    q = S.question()
    assert q["stage4_run"] == S.STAGE4_RUN and q["limit"] == 14 * 86400
    assert [p["id"] for p in S.predictions()] == ["D1", "B", "R"]


@pytest.mark.skipif(not S.distq.BINARY.exists(), reason="DistQLDPC is not built here")
def test_one_job_gross_code():
    c = {"torus": [6, 6], "n": 72, "k": 12, "A": GROSS_A, "B": GROSS_B,
         "class_key": json.dumps([GROSS_A, GROSS_B]), "status": "timelimit", "lower": 4,
         "d4": None, "upper": 6, "connected": True, "from": "records"}  # fmt: skip
    r = S.job(c, limit=600, schedule=(((0,), 10.0),))
    assert "error" not in r, r.get("error")
    assert r["d"] == 6 and r["distqldpc"]["returncode"] == 0
    assert r["witness_check"]["logical"] and r["witness_check"]["weight"] == 6
    assert S.assess(r, c) == "settled" and S.in_bounds(6, c)
