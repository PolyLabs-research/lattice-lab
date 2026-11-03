"""Census stage 4d (examples/qec-census-4d/study.py): the selection rule on synthetic stage 4
files, the polling run with a stand-in job, the verdict logic on synthetic records, the amended
frontier, and jobs on [[72,12,6]] (skipped without DistQLDPC)."""

import importlib.util
import json
import sys
import threading
import time
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
A1, A2, A3 = [[0, 0], [0, 1], [1, 2]], [[0, 0], [1, 1], [2, 3]], [[0, 0], [0, 5], [1, 1]]
B0 = [[0, 0], [0, 7], [1, 23]]


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


def cline(ell, m, A, B, status, lower=None, run=S.STAGE4_RUN, d=None):
    return {"l": ell, "m": m, "key": json.dumps([A, B]), "A": A, "B": B, "run": run,
            "exact": {"status": status, "lower": lower, "d": d}}  # fmt: skip


@pytest.fixture
def stage4(tmp_path, monkeypatch):
    rec, cp, led = tmp_path / "records.jsonl", tmp_path / "exact-checkpoint.jsonl", \
        tmp_path / "ledger.jsonl"  # fmt: skip
    monkeypatch.setattr(S, "S4_RECORDS", rec)
    monkeypatch.setattr(S, "S4_CHECKPOINT", cp)
    monkeypatch.setattr(S, "S4_LEDGER", led)
    monkeypatch.delenv("S4_SYNC_LOCK", raising=False)
    S._CACHE.clear()

    def write(records=(), checkpoint=(), ended=False):
        rec.write_text("".join(json.dumps(r) + "\n" for r in records))
        cp.write_text("".join(json.dumps(r) + "\n" for r in checkpoint))
        kinds = ["question", "run_started"] + (["verdict"] if ended else [])
        # the keys sorted, as the ledger writes them: "kind" after a long body
        led.write_text("".join(json.dumps({"body": {"rows": "x" * 70000} if k == "verdict"
                                           else {}, "hash": S.STAGE4_RUN if k == "run_started"
                                           else "h", "kind": k,
                                           "time": "2026-10-30T19:45:04+00:00"},
                                          sort_keys=True) + "\n" for k in kinds))  # fmt: skip

    return write


def test_selection(stage4):
    recs = [torus(3, 64, [row(A1, B0, 4, "complete", d=28, lower=28, upper=28),
                          row(A2, B0, 4, "timelimit", lower=28, upper=30),
                          row(A3, B0, 8, "unverified", lower=26, upper=28, dq=26)],
                  {"4": {"d": 28, "settled": False, "unresolved": 1},
                   "8": {"d": 26, "settled": True, "unresolved": 0}})]  # fmt: skip
    cps = [
        cline(6, 33, A1, B0, "timelimit", lower=28),  # a torus still running
        cline(6, 33, A2, B0, "timelimit", lower=28, run="another run"),  # a foreign run
        cline(6, 33, A3, B0, "complete", d=26),
    ]
    stage4(recs, cps)
    sel = {S.key(c): c for c in S.selected()}
    assert set(sel) == {f"3x64:{json.dumps([A2, B0])}", f"3x64:{json.dumps([A3, B0])}",
                        f"6x33:{json.dumps([A1, B0])}"}  # fmt: skip
    t = sel[f"3x64:{json.dumps([A2, B0])}"]
    assert (t["status"], t["lower"], t["upper"], t["k"], t["from"]) == ("timelimit", 28, 30, 4,
                                                                        "records")  # fmt: skip
    u = sel[f"3x64:{json.dumps([A3, B0])}"]
    assert (u["status"], u["d4"]) == ("unverified", 26)
    assert sel[f"6x33:{json.dumps([A1, B0])}"]["from"] == "checkpoint"
    # priority: the connected class on the unsettled entry first, then the torus in progress
    order = sorted(sel.values(), key=lambda c: (S.priority(c), S.key(c)))
    assert [S.key(c) for c in order][:2] == [f"3x64:{json.dumps([A2, B0])}",
                                            f"6x33:{json.dumps([A1, B0])}"]  # fmt: skip


def test_the_torus_record_decides(stage4):
    recs = [torus(3, 64, [row(A1, B0, 4, "complete", d=28, lower=28, upper=28)],
                  {"4": {"d": 28, "settled": True, "unresolved": 0}})]  # fmt: skip
    stage4(recs, [cline(3, 64, A1, B0, "timelimit", lower=26)])
    assert S.selected() == []


def test_the_cache_follows_the_files(stage4):
    stage4([], [cline(6, 33, A1, B0, "timelimit", lower=28)])
    assert len(S.selected()) == 1
    with S.S4_CHECKPOINT.open("a") as fh:  # stage 4 appends; the cache is not cleared by hand
        fh.write(json.dumps(cline(6, 33, A2, B0, "timelimit", lower=26)) + "\n")
    assert len(S.selected()) == 2
    assert not S.stage4_ended()
    stage4([], [], ended=True)
    assert S.stage4_ended() and S.selected() == []


def fake(c, d, w=None, logical=True, error=False, lower=None, upper=None, rc=None):
    rc = (0 if d is not None else 1) if rc is None else rc
    r = {"key": S.key(c), "class": c, "seconds": 1.0, "d": d, "sha256": S.code_hashes(),
         "distqldpc": {"d": d, "lower": d if lower is None else lower,
                       "upper": d if upper is None else upper, "returncode": rc,
                       "commit": S.DISTQLDPC_COMMIT},
         "witness_check": None if w is None else {"weight": w, "logical": logical}}  # fmt: skip
    if error:
        r["error"] = "Traceback"
    return r


@pytest.fixture
def two(stage4, monkeypatch):
    monkeypatch.setattr(S, "consistency", lambda: [])
    recs = [torus(3, 64, [row(A1, B0, 4, "timelimit", lower=28, upper=30),
                          row(A2, B0, 4, "timelimit", lower=27, upper=30)],
                  {"4": {"d": 28, "settled": False, "unresolved": 2}})]  # fmt: skip
    stage4(recs, [], ended=True)
    return S.selected()


def test_decide_pass_and_report(two):
    v = S.decide([fake(two[0], 30, 30), fake(two[1], 28, 28)], S.predictions())
    assert (v["D1"], v["B"], v["verdict"], v["settled"]) == ("pass", "pass", "pass", 2)
    assert v["R"]["3x64"]["best"]["4"] == {"d": 30, "settled": True}
    assert v["selected"] == [S.key(c) for c in two] and "records.jsonl" in v["stage4_files"]


def test_decide_contradictions(two):
    P = S.predictions()
    # a verified logical lighter than the exact d
    assert S.decide([fake(two[0], 30, 28), fake(two[1], 28, 28)], P)["D1"] == "fail"
    # a d above stage 4's verified window bound
    assert S.decide([fake(two[0], 32, 32), fake(two[1], 28, 28)], P)["D1"] == "fail"
    # DistQLDPC stopped at its own limit, with a lower bound above stage 4's window bound: no d
    # and no witness, still a contradiction
    at_limit = {**fake(two[0], None, None, lower=32, upper=None), "witness_check": None}
    assert S.assess(at_limit, two[0]) == "contradiction"
    assert S.decide([at_limit, fake(two[1], 28, 28)], P)["D1"] == "fail"
    # DistQLDPC's upper bound below stage 4's lower bound rounded up to even (28)
    low = {**fake(two[0], None, None, lower=20, upper=26), "witness_check": None}
    assert S.assess(low, two[0]) == "contradiction"


def test_decide_bounds_and_incomplete(two):
    P = S.predictions()
    # below stage 4's lower bound rounded up to even (28): B fails
    v = S.decide([fake(two[0], 26, 26), fake(two[1], 28, 28)], P)
    assert v["B"] == "fail" and v["verdict"] == "fail"
    # an exact d without a witness: D1 incomplete, B judged on the d's
    v = S.decide([fake(two[0], 30, None), fake(two[1], 28, 28)], P)
    assert (v["D1"], v["B"], v["verdict"]) == ("incomplete", "pass", "incomplete")
    # a missing class: incomplete
    assert S.decide([fake(two[1], 28, 28)], P)["verdict"] == "incomplete"
    # an errored attempt is outweighed by a clean record of the same class
    rows = [fake(two[0], None, None, error=True), fake(two[0], 30, 30), fake(two[1], 28, 28)]
    assert S.decide(rows, P)["verdict"] == "pass"
    # a record made by other code makes the run invalid
    other = {**fake(two[0], 30, 30), "sha256": {"study_py": "another"}}
    assert S.decide([other, fake(two[1], 28, 28)], P)["verdict"] == "invalid"


def test_not_applicable_and_invalid(stage4, monkeypatch):
    stage4([], [], ended=True)
    monkeypatch.setattr(S, "consistency", lambda: [])
    assert S.decide([], S.predictions())["verdict"] == "not applicable"
    monkeypatch.setattr(S, "consistency", lambda: ["the code differs from the registration"])
    assert S.decide([], S.predictions())["verdict"] == "invalid"


def test_done_retries_and_prior(tmp_path):
    p = tmp_path / "r.jsonl"
    attempt = {"key": "a", "error": "x", "distqldpc": {"returncode": 0, "d": 30,
                                                       "commit": S.DISTQLDPC_COMMIT}}  # fmt: skip
    p.write_text(json.dumps(attempt) + "\n")
    assert S._done(p) == set() and S._prior(p, "a")["d"] == 30
    p.write_text(p.read_text() + json.dumps({"key": "a", "error": "x"}) + "\n")
    assert S._done(p) == {"a"}
    assert S._prior(p, "b") is None


def stand_in(c, prior=None):
    """A job for the polling test: settles any class at its window bound at once."""
    return {"key": S.key(c), "class": c, "d": c["upper"] or 28, "seconds": 0.0,
            "sha256": S.code_hashes(),
            "witness_check": {"weight": c["upper"] or 28, "logical": True}}  # fmt: skip


def test_execute_polls_until_stage4_ends(stage4, tmp_path, monkeypatch):
    monkeypatch.setattr(S, "consistency", lambda: [])
    monkeypatch.setattr(S, "distqldpc_commit", lambda: S.DISTQLDPC_COMMIT)
    out = tmp_path / "4d.jsonl"
    stage4([], [cline(6, 33, A1, B0, "timelimit", lower=28)])
    errors = []

    def go():
        try:
            S.execute(out, 2, run_job=stand_in, poll=0.05)
        except Exception as exc:
            errors.append(exc)

    t = threading.Thread(target=go)
    t.start()
    deadline = time.time() + 30
    while not (out.exists() and out.read_text().strip()) and time.time() < deadline:
        time.sleep(0.05)
    time.sleep(0.5)
    assert t.is_alive(), "the run ended while stage 4 was still running"
    # stage 4 finishes the torus (a second class at the limit) and writes its verdict
    recs = [torus(6, 33, [row(A1, B0, 4, "timelimit", lower=28, upper=30),
                          row(A2, B0, 4, "timelimit", lower=28, upper=28)],
                  {"4": {"d": 28, "settled": False, "unresolved": 2}})]  # fmt: skip
    stage4(recs, [cline(6, 33, A1, B0, "timelimit", lower=28)], ended=True)
    t.join(30)
    assert not t.is_alive() and not errors
    keys = [json.loads(x)["key"] for x in out.read_text().splitlines()]
    assert sorted(keys) == sorted(S.key(c) for c in S.selected()) and len(keys) == 2


def test_registration_shape(stage4):
    stage4([torus(3, 64, [row(A1, B0, 4, "complete", d=28, lower=28, upper=28)],
                  {"4": {"d": 28, "settled": True, "unresolved": 0}})], [])  # fmt: skip
    q = S.question()
    st = q["stage4_at_registration"]
    assert (st["tori"], st["exact_runs"], st["selected"]) == (1, 1, [])
    assert set(st["files"]) == {"records.jsonl", "exact-checkpoint.jsonl", "ledger.jsonl"}
    assert q["stage4_run"] == S.STAGE4_RUN and q["limit"] == 14 * 86400
    assert [p["id"] for p in S.predictions()] == ["D1", "B", "R"]


def gross(status, d4=None):
    return {"torus": [6, 6], "n": 72, "k": 12, "A": GROSS_A, "B": GROSS_B,
            "class_key": json.dumps([GROSS_A, GROSS_B]), "status": status, "lower": 4,
            "d4": d4, "upper": 6, "connected": True, "entry_settled": False,
            "from": "records"}  # fmt: skip


def test_job_at_distqldpcs_own_limit(monkeypatch):
    stopped = {"engine": "cc", "k": 12, "lower": 4, "d": None, "upper": 6, "withdrawn": False,
               "seconds": 1.0, "returncode": 1, "tail": ""}  # fmt: skip
    monkeypatch.setattr(S.distq, "run", lambda *a, **k: dict(stopped))
    monkeypatch.setattr(S, "distqldpc_commit", lambda: S.DISTQLDPC_COMMIT)
    r = S.job(gross("timelimit"))
    assert r["d"] is None and "witness_check" not in r and "error" not in r
    assert S.assess(r, gross("timelimit")) == "open"


SKIP = pytest.mark.skipif(not S.distq.BINARY.exists(), reason="DistQLDPC is not built here")


@SKIP
def test_one_job_gross_code():
    c = gross("timelimit")
    r = S.job(c, limit=600, schedule=(((0,), 10.0),))
    assert "error" not in r, r.get("error")
    assert r["d"] == 6 and r["distqldpc"]["returncode"] == 0
    assert r["witness_check"]["logical"] and r["witness_check"]["weight"] == 6
    assert S.assess(r, c) == "settled" and S.in_bounds(6, c)


@SKIP
def test_unverified_and_prior_jobs_skip_distqldpc(monkeypatch):
    def never(*a, **k):
        raise AssertionError("DistQLDPC should not run")

    monkeypatch.setattr(S.distq, "run", never)
    r = S.job(gross("unverified", d4=6), schedule=(((0,), 10.0),))
    assert r["d_from"] == "stage 4" and S.assess(r, gross("unverified", d4=6)) == "settled"
    prior = {"d": 6, "lower": 6, "upper": 6, "returncode": 0, "commit": S.DISTQLDPC_COMMIT}
    r = S.job(gross("timelimit"), schedule=(((0,), 10.0),), prior=prior)
    assert r["d_from"].startswith("DistQLDPC, kept")
    assert S.assess(r, gross("timelimit")) == "settled"
