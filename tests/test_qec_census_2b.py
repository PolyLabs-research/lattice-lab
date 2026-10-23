"""The continuation of stage 2 of the code census (examples/qec-census-2b) and census.c's capacity.

census.c: the old file (stage 1's and stage 2's registered one) is the new one with
code_change.json's patch reversed; the two give the same ranks on every raw code of several
stage-1 tori (with bb.k_linalg on samples and stage 1's k counts), and the new one gives the right
k on 3x51 (lm = 153, outside every hold-out list) and refuses lm = 161 loudly. The continuation:
its jobs are stage 2's failed jobs, its predictions stage 2's registered ones for them verbatim,
its permit and job, its scheduler, and decide on stage 2's real records and synthetic ones.
Nothing here computes on a held-out torus: where a test needs a held-out name, every computing
primitive is stubbed to raise."""

import hashlib
import importlib.util
import json
import math
import random
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "examples" / "qec-census-2b"
STAGE2 = ROOT / "examples" / "qec-census-2"
DATA = ROOT / "examples" / "qec-census" / "data"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("qec_census_stage2b", HERE / "study.py")
S2, C, R = S.stage2, S.census, S.rules
bb = C.bb


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _header(name: str) -> dict:
    return json.loads((DATA / f"{name}.jsonl").read_text().splitlines()[0])


def _error_rows() -> list[dict]:
    rows = [json.loads(x) for x in (STAGE2 / "records.jsonl").read_text().splitlines()]
    return [r for r in rows if "error" in r]


def _forbid_computing(monkeypatch):
    """Every primitive that computes on a torus's codes raises instead."""

    def forbidden(*args, **kwargs):
        raise AssertionError("computed on a torus")

    monkeypatch.setattr(C, "_census_binary", forbidden)
    for module, names in (
        (C.bb, ["local_terms", "k_linalg", "k_characters"]),
        (C.distance, ["distance_search", "distance_ilp", "verify_witness", "distance_brute"]),
        (C.retest, ["_isomorphisms", "equivalence_key", "_carried_key"]),
    ):
        for name in names:
            monkeypatch.setattr(module, name, forbidden)
    for name in ("ranks", "k_all", "classes", "canonical", "census_torus"):
        monkeypatch.setattr(C, name, forbidden)


# ---------------------------------------------------------------- census.c's capacity


def test_the_patch_reverses_to_the_registered_files():
    change = S.code_change()
    registered = S.stage2_ledger()["question"]["body"]["sha256"]
    for name, key in (("census.c", "census_c"), ("census.py", "census_py")):
        old = S.old_source(name)
        assert _sha(old) == change[name]["old_sha256"] == registered[key]
        assert S._sha256_file(S.CENSUS_FILES[name]) == change[name]["new_sha256"] != registered[key]
    # stage 1 ran the old census.c: every file header records it
    assert change["census.c"]["old_sha256"] == S.STAGE1_CENSUS_C
    assert all(
        json.loads(p.read_text().splitlines()[0])["census_c_sha256"] == S.STAGE1_CENSUS_C
        for p in DATA.glob("*x*.jsonl")
    )
    # census.c's patch is the capacity and the refusal's message, nothing else
    old, new = S.old_source("census.c"), C.CENSUS_C.read_text()
    assert (
        "#define MAXLM 128\n#define WORDS 4" in old and "#define MAXLM 160\n#define WORDS 5" in new
    )
    removed = [x for x in old.splitlines() if x not in new.splitlines()]
    added = [x for x in new.splitlines() if x not in old.splitlines()]
    assert len(removed) == 4 and all(
        "MAXLM" in x or "WORDS" in x or "256 bits" in x for x in removed
    )
    assert all(
        re.search(r"MAXLM|WORDS|320 bits|size out of range|L, M, LM|lm <=|^\s+return fprintf", x)
        for x in added
    ), added
    # the only stage-2 pinned files that differ from its registration are the documented ones
    now = S2.code_hashes()
    assert sorted(k for k in registered if registered[k] != now[k]) == sorted(S.CHANGED)
    summary = S.change_summary()
    assert summary["census.c"]["hunks"] == 3 and "+#define MAXLM 160" in summary["census.c"]["diff"]


def _compile_old(tmp_path: Path) -> str:
    source = tmp_path / "census_old.c"
    source.write_text(S.old_source("census.c"))
    assert S._sha256_file(source) == S.STAGE1_CENSUS_C
    binary = tmp_path / "census_old"
    subprocess.run(["cc", "-O2", "-o", str(binary), str(source)], check=True, capture_output=True)
    return str(binary)


def _params(ell: int, m: int, i: int) -> tuple:
    """Raw code i in census.c's order, without raw_parameters (which guards the torus)."""
    bc = [(b, c) for b in range(m) for c in range(b + 1, m)]
    ef = [(e, f) for e in range(ell) for f in range(e + 1, ell)]
    i, j4 = divmod(i, len(ef))
    i, d = divmod(i, m)
    a, j2 = divmod(i, len(bc))
    return (a, *bc[j2], d, *ef[j4])


def _sample(k: np.ndarray, rng, size: int) -> list[int]:
    pos, zero = np.flatnonzero(k > 0).tolist(), np.flatnonzero(k == 0).tolist()
    return rng.sample(pos, min(size, len(pos))) + rng.sample(zero, min(size, len(zero)))


def test_the_old_and_new_census_c_agree_on_every_raw_code_of_stage1_tori(tmp_path):
    old = _compile_old(tmp_path)
    rng = random.Random("test qec-census-2b capacity")
    for ell, m in [(3, 7), (6, 6), (6, 15), (3, 33), (7, 14)]:
        C.guard(ell, m)
        before = subprocess.run([old, "k", str(ell), str(m)], check=True, capture_output=True)
        before = np.frombuffer(before.stdout, dtype=np.uint8).astype(np.int64)
        after = C.ranks(ell, m)
        assert len(after) == C.raw_count(ell, m) and (before == after).all(), (ell, m)
        k = 2 * ell * m - 2 * after
        counts = {str(a): int((k == a).sum()) for a in sorted(set(k.tolist()))}
        assert counts == _header(f"{ell}x{m}")["raw_by_k"]
        P = C.raw_parameters(ell, m)
        for i in _sample(k, rng, 15):
            assert tuple(P[i]) == _params(ell, m, i)
            A, B = C.polynomials(P[i])
            assert bb.k_linalg(A, B, ell, m) == k[i], (ell, m, P[i])
        assert (k > 0).any()
    # check mode (rank H_X, rank H_Z per code) too, byte for byte, on two of them
    new = C._census_binary()
    for ell, m in [(3, 7), (6, 6)]:
        C.guard(ell, m)
        args = ["k", str(ell), str(m), "check"]
        before = subprocess.run([old, *args], check=True, capture_output=True).stdout
        after = subprocess.run([new, *args], check=True, capture_output=True).stdout
        assert before == after and len(after) == 2 * C.raw_count(ell, m), (ell, m)


def test_census_c_holds_lm_up_to_160_and_refuses_above_loudly(tmp_path, monkeypatch):
    source = C.CENSUS_C.read_text()
    maxlm = int(re.search(r"#define MAXLM (\d+)", source).group(1))
    words = int(re.search(r"#define WORDS (\d+)", source).group(1))
    assert maxlm == 160 and 64 * words >= 2 * maxlm and 64 * (words - 1) < 2 * maxlm
    held = C.held_out_tori()
    assert max(a * b for a, b in held) == 150 <= maxlm
    # 3x51 (lm = 153): no hold-out list has it, and its order exceeds every held-out torus's,
    # so it is isomorphic to none; guard refuses it only as not a stage-1 torus
    ell, m = 3, 51
    assert (ell, m) not in held and ell * m > max(a * b for a, b in held)
    assert R.criterion(ell, m)
    with pytest.raises(C.HeldOut, match="not a stage-1 torus"):
        C.guard(ell, m)
    out = subprocess.run([C._census_binary(), "k", str(ell), str(m)], check=True,
                         capture_output=True).stdout  # fmt: skip
    k = 2 * ell * m - 2 * np.frombuffer(out, dtype=np.uint8).astype(np.int64)
    assert len(k) == ell * math.comb(m, 2) * m * math.comb(ell, 2)
    assert k.max() == 8 * ell * m // 9 and (k > 0).sum() > 0
    rng = random.Random("test qec-census-2b 3x51")
    for i in _sample(k, rng, 12):
        A, B = C.polynomials(_params(ell, m, i))
        assert bb.k_linalg(A, B, ell, m) == k[i], _params(ell, m, i)
    # a class with k > 128 is beyond search.c: stage 2's search records it as an error run
    # (guard stubbed only so that search reaches distance_search on this non-held-out torus)
    i = int(np.flatnonzero(k == k.max())[0])
    A, B = C.polynomials(_params(ell, m, i))
    with monkeypatch.context() as patch:
        patch.setattr(C, "guard", lambda *args, **kwargs: None)
        run = S2.search(A, B, ell, m, "d2", 64, 5.0)
    assert run["status"] == "error" and "beyond search.c's limits" in run["error"]
    assert run["d"] is None and run["lower"] is None and run["witness"] is None
    # the old census.c refused it, as it refused stage 2's tori with lm >= 129
    old = subprocess.run([_compile_old(tmp_path), "k", "3", "51"], capture_output=True, text=True)
    assert old.returncode == 1 and "size out of range" in old.stderr and not old.stdout
    # lm = 161: refused, saying why, and ranks raises with that message (7x23 is held out of
    # nothing either; guard is stubbed only so that ranks reaches census.c)
    big = subprocess.run([C._census_binary(), "k", "7", "23"], capture_output=True, text=True)
    assert big.returncode == 1 and not big.stdout
    assert "lm = 161" in big.stderr and "MAXLM = 160" in big.stderr
    monkeypatch.setattr(C, "guard", lambda *args, **kwargs: None)
    with pytest.raises(RuntimeError, match="census.c refused 7x23.*MAXLM = 160"):
        C.ranks(7, 23)


# ---------------------------------------------------------------- the registration


def test_the_registration_computes_nothing_and_copies_stage2_verbatim(monkeypatch):
    _forbid_computing(monkeypatch)
    q, preds = S.question(), S.predictions()
    ledger = S.stage2_ledger()
    errors = _error_rows()
    failed = [r["key"] for r in errors]
    assert len(failed) == 54
    assert sum(r["test"] == "torus" for r in errors) == 46
    assert sum(r["test"] == "law" for r in errors) == 8
    order = [j["key"] for j in ledger["predictions"]["protocol"]["body"]["jobs"]]
    assert q["id"] == C.STAGE2B_ID == S.ID and sorted(q["jobs"]) == sorted(failed)
    assert q["jobs"] == [key for key in order if key in failed]  # stage 2's order
    assert q["waiting_on_failed"] == [] and q["fed"] == {"H2": [], "H4": []}
    assert [f["key"] for f in q["failed_jobs"]] == failed  # the records file's order
    assert all(f["lm"] >= 129 and "exit status 1" in f["error"] for f in q["failed_jobs"])
    tori = {tuple(t) for t in q["tori"]}
    assert len(tori) == 46 and tori <= set(R.held_out())
    assert all(129 <= a * b <= 150 for a, b in tori)
    assert {(a, b) for a, b in R.held_out() if a * b >= 129} == tori
    assert q["continues"]["verdict_value"] == "incomplete"
    assert q["continues"]["verdict"] == ledger["verdict"]["hash"]
    assert q["sha256"] == S.code_hashes() and set(S2.HASHED) < set(q["sha256"])
    by = {p["part"]: p for p in preds}
    assert list(by) == [*S.PARTS, "protocol"]
    names = {f"{a}x{b}" for a, b in tori}
    for part in S.PARTS:
        source = ledger["predictions"][part]
        assert by[part]["source_entry"]["hash"] == source["hash"]
        assert by[part]["source_question"] == ledger["question"]["hash"]
        field = S._items(part, source["body"])
        mine, theirs = by[part][field], source["body"][field]
        for key, value in source["body"].items():  # every other field verbatim
            if key not in (field, "question", "excluded"):
                assert by[part][key] == value, (part, key)
        if part == "H7":
            assert sorted(x["key"] for x in mine) == sorted(k for k in failed if "law" in k)
            assert all(x in theirs for x in mine)
        elif isinstance(theirs, dict):
            assert set(mine) == set(theirs) & names
            assert all(mine[k] == theirs[k] for k in mine)
        else:
            assert mine == [t for t in theirs if t in names]
    assert by["H8"]["tori"] == [] and by["H9"]["sizes"] == {}
    assert len(by["H1"]["predicted"]) == 46 and len(by["H6"]["tori"]) == 12
    protocol = by["protocol"]
    stage2_jobs = {j["key"]: j for j in ledger["predictions"]["protocol"]["body"]["jobs"]}
    assert protocol["jobs"] == [stage2_jobs[k] for k in q["jobs"]]
    assert protocol["sha256"] == S.code_hashes()
    assert protocol["per_part_verdict_rule"] == S2.VERDICT_RULE
    json.dumps(q), json.dumps(preds)


def test_stage2s_ledger_and_records_are_as_registered():
    ledger = S.stage2_ledger()
    assert ledger["verdict"]["body"]["verdict"] == "incomplete"
    assert sorted(ledger["verdict"]["body"]["failed_jobs"]) == sorted(
        r["key"] for r in _error_rows()
    )
    rows = S.failed_rows(ledger=ledger)
    assert [r["row"] for r in rows] == _error_rows()
    # every error row is census.c's refusal, at a torus with lm > 128
    assert all("census', 'k'" in r["row"]["error"] for r in rows)
    assert all(r["row"]["l"] * r["row"]["m"] > 128 for r in rows)


# ---------------------------------------------------------------- the permit and the job


def _ledger(path: Path, kinds=("question", "prediction", "run_started"), tori=None, qid=None,
            sha256=None, specs=None):  # fmt: skip
    from lattice_lab.ledger import Ledger

    ledger = Ledger(path)
    for kind in kinds:
        if kind == "question":
            body = {
                "id": qid or C.STAGE2B_ID,
                "tori": tori or [[3, 50], [5, 30]],
                "sha256": sha256 or S.code_hashes(),
            }
        elif kind == "prediction":
            body = {"part": "protocol", "jobs": specs or []}
        else:
            body = {"x": 1}
        ledger.append(kind, body)
    return path


def _as_job(source: str, filename: Path, name: str = "job"):
    namespace = {"C": C}
    exec(compile(source, str(filename), "exec"), namespace)
    return namespace[name]


JOB = """
def job(tori, probe):
    with C.Stage2Permit(tori):
        return [probe(*t) for t in tori]
"""


def test_the_permit_opens_for_the_continuations_job_on_its_own_ledger(tmp_path, monkeypatch):
    _forbid_computing(monkeypatch)
    monkeypatch.setattr(C, "STAGE2B_LEDGER", tmp_path / "ledger.jsonl")
    job = _as_job(JOB, C.STAGE2B_STUDY)

    def opened(a, b):
        C.guard(a, b)
        return True

    with pytest.raises(C.HeldOut, match="not registered"):
        job([(3, 50)], opened)
    _ledger(tmp_path / "ledger.jsonl", ("question", "prediction"))
    with pytest.raises(C.HeldOut, match="has not started"):
        job([(3, 50)], opened)
    (tmp_path / "ledger.jsonl").unlink()
    _ledger(tmp_path / "ledger.jsonl", qid=C.STAGE2_ID)  # stage 2's id is not this study's
    with pytest.raises(C.HeldOut, match="question is not qec-census-stage2b"):
        job([(3, 50)], opened)
    (tmp_path / "ledger.jsonl").unlink()
    _ledger(tmp_path / "ledger.jsonl")
    assert job([(3, 50)], opened) == [True]
    with pytest.raises(C.HeldOut):
        C.guard(3, 50)
    with pytest.raises(C.HeldOut, match="not among the registered"):
        job([(3, 21)], opened)
    with pytest.raises(C.HeldOut):
        job([(3, 50)], lambda a, b: C.guard(b, a))
    assert C._STAGE2_OPEN == frozenset()
    # stage 2's job reads stage 2's ledger, whose run has finished: refused, whatever this
    # study's ledger holds
    stage2_job = _as_job(JOB, C.STAGE2_STUDY)
    with pytest.raises(C.HeldOut, match="in progress"):
        stage2_job([(3, 50)], opened)
    with pytest.raises(C.HeldOut, match="job only"):
        _as_job(JOB, tmp_path / "study.py")([(3, 50)], opened)


def test_job_runs_stage2s_code_only_inside_the_permit(tmp_path, monkeypatch):
    _forbid_computing(monkeypatch)
    monkeypatch.setattr(C, "STAGE2B_LEDGER", tmp_path / "ledger.jsonl")
    calls = []

    def dispatch(spec, path):
        C.guard(spec["l"], spec["m"])
        calls.append(spec["key"])
        return {"classes": []}

    monkeypatch.setattr(S2, "_dispatch", dispatch)
    monkeypatch.setattr(S.distance, "scip_version", lambda: "SCIP (test)")
    spec = {"test": "torus", "key": "torus 3x50", "l": 3, "m": 50}
    with pytest.raises(C.HeldOut):
        S.job(spec, str(tmp_path / "records.jsonl"))
    _ledger(tmp_path / "ledger.jsonl", specs=[spec])
    record = S.job(spec, str(tmp_path / "records.jsonl"))
    assert calls == ["torus 3x50"] and record["key"] == "torus 3x50"
    # a spec that is not a registered job of the continuation
    with pytest.raises(S.StudyError, match="not a registered job"):
        S.job({**spec, "key": "torus 3x50 again"}, str(tmp_path / "records.jsonl"))
    # a pinned file that differs from the registration: refused before computing
    (tmp_path / "ledger.jsonl").unlink()
    _ledger(
        tmp_path / "ledger.jsonl",
        specs=[spec],
        sha256={**S.code_hashes(), "census_c": "0" * 64},
    )
    with pytest.raises(S.StudyError, match="changed since the registration.*census_c"):
        S.job(spec, str(tmp_path / "records.jsonl"))
    assert calls == ["torus 3x50"]
    with pytest.raises(S.StudyError, match="census_c"):
        S.execute(tmp_path / "records.jsonl", 1)


def test_the_worker_process_refuses_without_a_started_run(tmp_path):
    # the real worker path on a stage-1 torus's name: the permit refuses before computing
    spec = {"test": "torus", "key": "torus 3x9", "l": 3, "m": 9}
    record = S._run(spec, tmp_path / "records.jsonl")
    assert record["key"] == "torus 3x9" and "HeldOut" in record["error"]
    assert "Stage2Permit" in record["error"]


def test_execute_runs_each_job_once_and_resumes(tmp_path, monkeypatch):
    _forbid_computing(monkeypatch)
    specs = [
        {"test": "torus", "key": "torus 3x50", "l": 3, "m": 50},
        {"test": "law", "key": "law 3x50 (3,5)", "l": 3, "m": 50, "type": [3, 5], "value": 20},
        {"test": "torus", "key": "torus 5x30", "l": 5, "m": 30},
    ]
    monkeypatch.setattr(S, "jobs", lambda: specs)
    ran = []

    def run(spec, path):
        ran.append(spec["key"])
        return {**spec, "classes": []}

    path = tmp_path / "records.jsonl"
    S.execute(path, 2, run=run, window=0)
    assert sorted(ran) == sorted(s["key"] for s in specs)
    S.execute(path, 2, run=run, window=0)  # resume: nothing left
    assert len(ran) == 3
    path.write_text(path.read_text()[:-5])
    with pytest.raises(S.StudyError, match="incomplete line"):
        S.execute(path, 1, run=run, window=0)
    # a window too short for any job's timeout stops before running anything
    with pytest.raises(S.StudyError, match="the window ends"):
        S.execute(tmp_path / "other.jsonl", 1, run=run, window=60)
    assert len(ran) == 3


def test_the_continuations_jobs_are_stage2s_failed_jobs():
    ledger = S.stage2_ledger()
    specs = S.jobs(ledger)
    assert sorted(j["key"] for j in specs) == sorted(r["key"] for r in _error_rows())
    assert all("after" not in j for j in specs)
    # a registered job waiting on a failed one would join them
    fake = {
        **ledger,
        "predictions": {
            **ledger["predictions"],
            "protocol": {
                "body": {
                    "jobs": ledger["predictions"]["protocol"]["body"]["jobs"]
                    + [
                        {
                            "key": "later",
                            "test": "frontier",
                            "l": 3,
                            "m": 50,
                            "after": ["torus 3x50"],
                        }
                    ]  # fmt: skip
                }
            },
        },
    }
    assert [j["key"] for j in S.jobs(fake)][-1] == "later"


# ---------------------------------------------------------------- decide


def _no_code_record(spec: dict) -> dict:
    ell, m = spec["l"], spec["m"]
    return {
        **spec,
        "n": 2 * ell * m,
        "raw_k_positive": 0,
        "kset": [],
        "max_k": 0,
        "min_k": None,
        "classes": [],
    }


def test_decide_with_nothing_run(monkeypatch):
    _forbid_computing(monkeypatch)
    preds = S.predictions()
    v = S.decide([], preds)
    assert v["verdict"] == "incomplete" and len(v["missing"]) == 54
    assert v["parts"]["H8"] == v["parts"]["H9"] == "not applicable"
    assert v["not_applicable"] == ["H8", "H9"] and v["code_changed"] == []
    c = v["combined"]
    assert c["outcome"] == "incomplete" and c["original"]["verdict"] == "incomplete"
    assert "stays so" in c["statement"] and "registered before either run" in c["statement"]
    assert c["code_changed_since_stage2_registration"] == ["census_c", "census_py"]
    assert c["unexplained_change"] == []
    assert len(c["failed_jobs"]) == 54 and c["records"]["replaced_error_rows"] == []
    # an empty part is 'not applicable' only when stage 2's rules do not judge it failing
    real = S2.decide

    def failing_h9(*args, **kwargs):
        out = real(*args, **kwargs)
        return {**out, "parts": {**out["parts"], "H9": "fails"}}

    monkeypatch.setattr(S2, "decide", failing_h9)
    own = S.own_verdict([], preds)
    assert own["parts"]["H9"] == "fails" and own["parts"]["H8"] == "not applicable"
    assert own["verdict"] == "fail"
    # with nothing new, the combined parts are stage 2's own outcomes
    assert c["parts"] == c["original"]["parts"]


def test_decide_replaces_error_rows_and_judges_by_stage2s_rules(monkeypatch):
    _forbid_computing(monkeypatch)
    preds = S.predictions()
    by = {p["part"]: p for p in preds}
    specs = by["protocol"]["jobs"]
    without = [j for j in specs if j["test"] == "torus" and not by["H1"]["predicted"][
        f"{j['l']}x{j['m']}"]]  # fmt: skip
    assert len(without) == 34
    rows = [_no_code_record(j) for j in without]
    v = S.decide(rows, preds)
    h1 = v["detail"]["H1"]["items"]
    assert all(h1[f"{j['l']}x{j['m']}"] == "holds" for j in without)
    assert v["verdict"] == "incomplete" and len(v["missing"]) == 54 - 34
    c = v["combined"]
    assert len(c["records"]["replaced_error_rows"]) == 34
    assert len(c["failed_jobs"]) == 54 - 34 and c["missing"] == []
    combined_h1 = c["detail"]["H1"]["items"]
    assert all(combined_h1[f"{j['l']}x{j['m']}"] == "holds" for j in without)
    assert c["outcome"] == "incomplete"
    # a coded torus recorded with no code fails H1, in both judgements
    coded = next(j for j in specs if j["key"] == "torus 3x50")
    v = S.decide(rows + [_no_code_record(coded)], preds)
    assert v["detail"]["H1"]["items"]["3x50"] == "fails" and v["verdict"] == "fail"
    assert v["combined"]["outcome"] == "fail"
    # a record of a job stage 2 did not fail is not the continuation's: off protocol here, and
    # a duplicate in the combined report
    extra = {"test": "torus", "key": "torus 2x28", "l": 2, "m": 28}
    v = S.decide(rows + [_no_code_record(extra)], preds)
    assert "torus 2x28" in v["protocol_failures"] and v["verdict"] == "fail"
    assert v["combined"]["duplicates"] == ["torus 2x28"]
    assert v["combined"]["instruments"] == "fail"


def test_decide_reports_files_changed_beyond_the_documented_change(monkeypatch):
    _forbid_computing(monkeypatch)
    preds = S.predictions()
    real = S.code_hashes()
    monkeypatch.setattr(S, "code_hashes", lambda: {**real, "rules_py": "0" * 64})
    stage2_now = S2.code_hashes()
    monkeypatch.setattr(S2, "code_hashes", lambda: {**stage2_now, "rules_py": "0" * 64})
    v = S.decide([], preds)
    assert "rules_py" in v["code_changed"]
    assert v["combined"]["unexplained_change"] == ["rules_py"]
