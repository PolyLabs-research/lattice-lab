"""The spot-check runner (examples/qec-census-3b/spotcheck/run.py): the sample rule on the
committed records, the job list, the judging of results, and every check run once on the
[[72,12,6]] code, at its true d and at a wrong one. The instrument runs are skipped when the
tools (CaDiCaL, drat-trim, DistQLDPC) or pyscipopt are missing."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RUN_PY = ROOT / "examples" / "qec-census-3b" / "spotcheck" / "run.py"
spec = importlib.util.spec_from_file_location("spotcheck_run", RUN_PY)
R = importlib.util.module_from_spec(spec)
sys.modules["spotcheck_run"] = R
spec.loader.exec_module(R)

A72, B72 = [[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]]
W72 = [0, 5, 4, 1, 21, 23]  # a Z-logical of weight 6, found by the packing search


def code72(d=6):
    return {"torus": [6, 6], "n": 72, "k": 12, "d": d, "A": A72, "B": B72, "witness": W72,
            "group": "test", "why": "test"}  # fmt: skip


def tools_ready():
    pack, sat, distq = R._instruments()
    try:
        import pyscipopt  # noqa: F401
    except ImportError:
        return False
    return sat.CADICAL.exists() and sat.DRAT_TRIM.exists() and distq.BINARY.exists()


# ---------------------------------------------------------------- the sample


@pytest.fixture(scope="module")
def drawn():
    return R.sample()


def test_sample_is_deterministic(drawn):
    assert R.sample() == drawn


def test_sample_follows_the_plan(drawn):
    codes = drawn["codes"]
    names = [R._name(c) for c in codes]
    assert len(names) == len(set(names))
    tori = R.judged(R.records())
    assert {r["group"] for r in tori} <= {"random", "extrapolation"}
    largest = sorted({r["n"] for r in tori}, reverse=True)
    assert [c["n"] for c in codes[:6]] == sorted((c["n"] for c in codes[:6]), reverse=True)
    assert codes[0]["n"] == largest[0]
    whys = [c["why"] for c in codes]
    assert whys.count("largest n") == 6 and whys.count("P2 counterexample") <= 4
    assert whys.count("random frontier entry") == 6
    p2 = [c for c in codes if c["why"] == "P2 counterexample"]
    assert len({R.iso(*c["torus"]) for c in p2}) == len(p2)
    assert [tuple(c["torus"]) for c in p2[:2]] == [(2, 51), (3, 40)]  # the plan's two
    for c in codes:
        if c["why"] == "random frontier entry":
            assert c["d"] >= 14
        if c["why"] == "P2 counterexample":
            assert c["d"] > 2 * int(1.40 * c["n"] ** 0.5 / 2)
    amended = {(tuple(c["torus"]), c["k"], c["d"]) for c in codes if c["why"].startswith("amend")}
    assert amended <= set(R.AMENDED)
    for c in drawn["c6_extra"]:
        assert 12 <= c["d"] <= 16 and R._name(c) not in names


def test_sampled_codes_are_as_recorded(drawn):
    # each code is a complete, connected class of its record, and its witness is a logical
    D = R._instruments()[0].distance
    by_torus = {(r["l"], r["m"]): r for r in R.judged(R.records())}
    for c in drawn["codes"] + drawn["c6_extra"]:
        rec = by_torus[tuple(c["torus"])]
        row = R._first_code(rec, c["k"], c["d"])
        assert row["A"] == c["A"] and row["B"] == c["B"]
        A, B = R._ab(c)
        check = D.verify_witness(A, B, *c["torus"], "Z", c["witness"])
        assert check["logical"] and check["weight"] == c["d"]


def test_jobs(drawn):
    js = R.jobs(drawn)
    keys = [j["key"] for j in js]
    assert len(keys) == len(set(keys))
    assert [j["check"] for j in js] == sorted((j["check"] for j in js), key=R.ORDER.index)
    n_codes = len(drawn["codes"])
    assert sum(j["check"] == "C4" for j in js) == 16 * n_codes
    small = sum(c["d"] <= 16 for c in drawn["codes"])
    assert sum(j["check"] == "C6" for j in js) == small + len(drawn["c6_extra"])


def test_caps():
    run = [{"check": "C1"}] * R.SCIP_CAP
    assert R.capped({"check": "C1"}, run) and not R.capped({"check": "C4"}, run)
    assert R.capped({"check": "C6"}, [{"check": "C6"}] * R.SAT_CAP)


# ---------------------------------------------------------------- judging


def rec(check, result, d=20, **extra):
    return {"check": check, "code": {**code72(d)}, "result": result, **extra}


def test_assess():
    a = R.assess
    assert a(rec("C4", {"upper": 22}))["consistent"] and a(rec("C4", {"upper": None}))["consistent"]
    assert a(rec("C4", {"upper": 18}))["consistent"] is False
    for c in ("C2", "C3"):
        assert a(rec(c, {"status": "complete", "d": 20, "lower": 20}))["reaches"] == "exact"
        assert a(rec(c, {"status": "complete", "d": 22, "lower": 22}))["consistent"] is False
        assert a(rec(c, {"status": "timelimit", "d": None, "lower": 19}))["consistent"]
        assert a(rec(c, {"status": "timelimit", "d": None, "lower": 21}))["consistent"] is False
    ilp = {"status": "timelimit", "d": None, "lower": 9, "upper": 24}
    assert a(rec("C1", ilp)) == {"consistent": True, "reaches": None}
    assert a(rec("C1", {**ilp, "upper": 18}))["consistent"] is False
    assert a(rec("C1", {"status": "optimal", "d": 20, "lower": 20, "upper": 20}))["reaches"]
    dq = {"lower": 12, "d": None, "upper": 26}
    assert a(rec("C5", dq, engine="cc"))["consistent"]
    assert a(rec("C5", {**dq, "d": 20}, engine="cc"))["reaches"] == "exact"
    assert a(rec("C5", {**dq, "d": 18, "upper": 18}, engine="cc"))["consistent"] is False
    good = {"logical": True, "weight": 20}
    assert a(rec("C6", {"status": "verified", "witness_check": good}))["reaches"] == "certified"
    assert a(rec("C6", {"status": "timelimit", "witness_check": good}))["consistent"] is None
    assert a(rec("C6", {"status": "unverified", "witness_check": good}))["consistent"] is None
    lighter = {"status": "sat", "witness_check": good, "support_check": {"logical": True}}
    assert a(rec("C6", lighter))["consistent"] is False
    assert a({"check": "C1", "code": code72(), "error": "x"})["consistent"] is None


def test_tiers():
    def r(check, reaches, engine=None):
        res = {"status": "complete", "d": 20 if reaches else None, "lower": 20 if reaches else 10}
        return rec(check, res, **({"engine": engine} if engine else {}))

    assert R.tier([r("C3", True), r("C2", False)]) == "search only"
    assert R.tier([r("C2", True)]) == "second implementation"
    dq = rec("C5", {"lower": 20, "d": 20, "upper": 20}, engine="cc")
    assert R.tier([dq]) == "second implementation"
    assert R.tier([{**dq, "engine": "maxsat"}]) == "second method"
    ilp = rec("C1", {"status": "optimal", "d": 20, "lower": 20, "upper": 20})
    assert R.tier([dq, ilp]) == "second method"
    cert = rec("C6", {"status": "verified", "witness_check": {"logical": True, "weight": 20}})
    assert R.tier([dq, ilp, cert]) == "certified"


# ---------------------------------------------------------------- the instruments, once each


JOBS = [{"check": "C4", "kind": "Z", "seed": 0}, {"check": "C4", "kind": "X", "seed": 1},
        {"check": "C3"}, {"check": "C2"}, {"check": "C1"}, {"check": "C5", "engine": "cc"},
        {"check": "C5", "engine": "maxsat"}, {"check": "C6"}]  # fmt: skip


@pytest.fixture
def short(monkeypatch):
    monkeypatch.setattr(R, "WINDOW_SECONDS", 3.0)
    monkeypatch.setattr(R, "LIMITS", {k: 120 for k in R.LIMITS})


@pytest.mark.skipif(not tools_ready(), reason="spot-check tools or pyscipopt missing")
@pytest.mark.parametrize("job", JOBS, ids=lambda j: R.key({**j, "code": code72()})[:12])
def test_each_check_agrees_at_the_true_d(job, short):
    j = {**job, "code": code72(6)}
    j["key"] = R.key(j)
    out = R.execute(j)
    assert "error" not in out, out.get("error")
    a = R.assess(out)
    assert a["consistent"] is True
    if job["check"] != "C4":
        assert a["reaches"] in ("exact", "certified")
    json.dumps(out)


@pytest.mark.skipif(not tools_ready(), reason="spot-check tools or pyscipopt missing")
@pytest.mark.parametrize("job", [j for j in JOBS if j["check"] != "C4"],
                         ids=lambda j: R.key({**j, "code": code72()})[:12])  # fmt: skip
def test_each_exact_check_rejects_a_wrong_d(job, short):
    # claim d = 8 for the d = 6 code: each check that finishes must contradict it
    j = {**job, "code": code72(8)}
    j["key"] = R.key(j)
    out = R.execute(j)
    assert "error" not in out, out.get("error")
    assert R.assess(out)["consistent"] is False


@pytest.mark.skipif(not tools_ready(), reason="spot-check tools or pyscipopt missing")
def test_run_writes_and_resumes(tmp_path, short, monkeypatch):
    js = []
    for job in ({"check": "C3"}, {"check": "C4", "kind": "Z", "seed": 0}):
        j = {**job, "code": code72()}
        j["key"] = R.key(j)
        js.append(j)
    monkeypatch.setattr(R, "jobs", lambda s: js)
    monkeypatch.setattr(R, "sample", lambda: {"codes": [], "c6_extra": []})
    out = tmp_path / "records.jsonl"
    R.run(2, out)
    assert R.done_keys(out) == {j["key"] for j in js}
    lines = out.read_text().splitlines()
    R.run(2, out)  # nothing left: no new lines
    assert out.read_text().splitlines() == lines
    verdict = R.judge(out)
    assert verdict["agreement"] and verdict["done"] == 2 and not verdict["errors"]


def test_a_dying_job_is_retried_then_recorded(tmp_path, monkeypatch):
    import os

    js = [{"check": "C4", "kind": "Z", "seed": s, "code": code72()} for s in (0, 1)]
    for j in js:
        j["key"] = R.key(j)
    monkeypatch.setattr(R, "jobs", lambda s: js)
    monkeypatch.setattr(R, "sample", lambda: {"codes": [], "c6_extra": []})

    def execute(j):
        if j["seed"] == 1:
            os._exit(9)  # as an out-of-memory kill would
        return {"key": j["key"], **{k: v for k, v in j.items() if k != "key"},
                "result": {"upper": 6}}  # fmt: skip

    monkeypatch.setattr(R, "execute", execute)
    out = tmp_path / "records.jsonl"
    R.run(2, out, retries=2)
    recs = {r["key"]: r for r in map(json.loads, out.read_text().splitlines())}
    assert set(recs) == {j["key"] for j in js}
    assert "error" not in recs[js[0]["key"]]
    assert "died 3 times" in recs[js[1]["key"]]["error"]
