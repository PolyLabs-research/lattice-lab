"""Stage 2 of the code census (examples/qec-census-2): its rules against stage-1 data, the
registration (made from l, m and stage-1 results only), the permit that alone opens a held-out
torus, the jobs and scheduler, the procedures on small stage-1 tori, and decide on synthetic
records. Nothing here computes a code, k, a class or a distance on a held-out torus: where a test
needs a held-out name, the computing primitives are stubbed to raise."""

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "examples" / "qec-census-2"
DATA = ROOT / "examples" / "qec-census" / "data"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("qec_census_stage2", HERE / "study.py")
R = S.rules
C = S.census


def _rows(name: str) -> list[dict]:
    return [json.loads(x) for x in (DATA / f"{name}.jsonl").read_text().splitlines()][1:]


def _all_rows() -> list[dict]:
    out = []
    for path in sorted(DATA.glob("*x*.jsonl")):
        out += [json.loads(x) for x in path.read_text().splitlines()][1:]
    return out


ROWS = _all_rows()


# ---------------------------------------------------------------- the rules against stage 1


def test_criterion_on_the_116_stage1_tori_gives_the_35_with_codes():
    ks = R.stage1_ksets()
    assert len(ks) == 116 and sum(1 for v in ks.values() if v) == 35
    assert {t for t in ks if R.criterion(*t)} == {t for t, v in ks.items() if v}
    # docs/code-census.md's cases: odd part 5 needs 15 | N; 11, 13, 17, 19, 23 rule out 3 x q
    for t in [
        (5, 5),
        (5, 10),
        (10, 10),
        (5, 7),
        (5, 11),
        (5, 13),
        (5, 17),
        (3, 11),
        (7, 11),
        (9, 11),
        (3, 13),
        (7, 13),
        (3, 17),
        (3, 19),
        (3, 23),
    ]:
        assert not R.criterion(*t)


def test_passes_is_the_root_test_it_states():
    # gcd(x^q + 1, (x + 1)^N + 1) nontrivial <=> some q-th root of unity z != 1 has
    # (1 + z)^N = 1, checked in GF(2^d) with bb's field
    bb = S.bb
    for q in (3, 5, 7, 9, 11, 13, 15, 21, 25):
        field = bb.Field(q)
        roots = [field.pow(field.zeta, e) for e in range(1, q)]
        for n in (3, 5, 7, 9, 15, 21, 35, 45, 63, 75, 341):
            want = any(field.pow(1 ^ z, n) == 1 for z in roots)
            assert R.passes(q, n) == want, (q, n)
    # docs/code-census.md's table: for ζ of order 5, 1 + ζ has order 15; μ_q holds the roots of
    # every order dividing q, so a side with 3 in its odd part passes (1 + ω = ω^2)
    assert R.passes(5, 15) and not R.passes(5, 5) and R.passes(9, 9) and R.passes(15, 15)
    assert R.passes(7, 7) and R.passes(31, 31)  # all of GF(8)*, GF(32)*
    assert not R.passes(11, 33) and R.passes(11, 341) and not R.passes(13, 39)


def test_the_k_formulas_reproduce_stage_1():
    ks = R.stage1_ksets()
    for t, v in ks.items():
        mk = R.max_k(*t)
        assert mk["value"] == (max(v) if v else 0), t
        assert mk["bound"] >= mk["value"]
        if v:
            assert R.min_k(*t) == min(v), t
            assert "lookup" in mk["rule"]
            if t[0] % 3 == 0 and t[1] % 3 == 0:  # both rules apply and agree (15 tori)
                assert mk["rule"] == "8lm/9, lookup" and mk["value"] == 8 * t[0] * t[1] // 9
        else:
            assert R.min_k(*t) is None and mk["rule"] == "criterion 1 fails"
    assert sum(1 for t in ks if R.max_k(*t)["rule"] == "8lm/9, lookup") == 15


def test_the_kset_rule_reproduces_the_18_one_sided_stage1_tori():
    ks = R.stage1_ksets()
    one = {t: R.kset_rule(*t) for t in ks if R.kset_rule(*t)}
    assert len(one) == 18
    for t, rule in one.items():
        assert rule["source"] == "stage 1" and rule["kset"] == ks[t], t
    assert R.lifted_kset([4, 8], 3, 12) == [4, 8, 16, 32]  # j = 0, 1, 2


def test_the_instance_lister_gives_the_17_stage1_instances():
    found = [
        (f"{a}x{b}", tuple(f["type"]), f["value"])
        for a, b in sorted(R.stage1_ksets())
        for f in R.forced_types(a, b)
    ]
    assert sorted(found) == sorted(
        [
            ("3x5", (3, 5), 2),
            ("3x10", (3, 5), 4),
            ("3x15", (3, 5), 6),
            ("3x20", (3, 5), 8),
            ("3x25", (3, 5), 10),
            ("3x30", (3, 5), 12),
            ("3x7", (3, 7), 2),
            ("3x14", (3, 7), 4),
            ("3x28", (3, 7), 8),
            ("3x25", (3, 25), 2),
            ("5x6", (5, 3), 4),
            ("5x9", (5, 3), 6),
            ("5x12", (5, 3), 8),
            ("5x15", (5, 3), 10),
            ("5x18", (5, 3), 12),
            ("7x9", (7, 3), 6),
            ("7x12", (7, 3), 8),
        ]
    )


def test_the_linear_law_table_from_stage1_data():
    # docs/code-census.md's table: classes of each instance's type and their largest d; 16 of
    # 17 equal, 3x15 below. _law_outcome on the stage-1 d's gives the same.
    counts, outcomes = {}, {}
    for a, b in sorted(R.stage1_ksets()):
        rows = [r for r in ROWS if (r["l"], r["m"]) == (a, b)]
        for f in R.forced_types(a, b):
            typed = [r for r in rows if R.has_type(r["characters"], *f["type"], a, b)]
            counts[(f"{a}x{b}", tuple(f["type"]))] = len(typed)
            state = {
                r["class"]: {"k": r["k"], "runs": [_exact_run(r["search"]["d"])]} for r in typed
            }
            outcomes[f"{a}x{b} {f['type']}"] = S._law_outcome(state, list(state), f["value"])
    assert [counts[(t, (3, 5))] for t in ("3x5", "3x10", "3x15", "3x20", "3x25", "3x30")] == [
        1,
        6,
        1,
        24,
        13,
        10,
    ]
    assert [counts[(t, (5, 3))] for t in ("5x6", "5x9", "5x12", "5x15", "5x18")] == [
        4,
        3,
        14,
        11,
        24,
    ]
    assert [counts[(t, (3, 7))] for t in ("3x7", "3x14", "3x28")] == [1, 4, 14]
    assert counts[("7x9", (7, 3))] == 2 and counts[("7x12", (7, 3))] == 13
    assert counts[("3x25", (3, 25))] == 1
    assert sum(v == "equal" for v in outcomes.values()) == 16
    assert outcomes["3x15 [3, 5]"] == "below"
    assert S._law_verdict(outcomes) == "holds"  # 16 of 17 >= 80%


def test_result_7_conditions_reproduce_stage_1():
    ii = only_i = 0
    agree = 0
    for r in ROWS:
        a = R.condition_i(r["A"], r["B"], r["l"], r["m"])
        b = R.condition_ii(r["A"], r["B"], r["characters"], r["l"], r["m"])
        ii += b
        only_i += a and not b
        agree += (a or b) == (r["search"]["d"] == 2)
    assert (ii, only_i, agree, len(ROWS)) == (263, 51, 3330, 3330)


def test_result_8_quotient_bound_reproduces_stage_1():
    bounded = attained = 0
    for r in ROWS:
        q = R.quotient_bound(r["A"], r["B"], r["characters"], r["l"], r["m"])
        if q is None:
            continue
        bounded += 1
        attained += q["bound"] == r["search"]["d"]
        assert r["search"]["d"] <= q["bound"]
        assert len(q["support"]) == q["bound"] == 2 * q["order"]
    assert (bounded, attained) == (2482, 873)


def test_the_explicit_logicals_pass_verify_witness_on_stage1_classes():
    distance = S.distance
    proved = unproved = proved_ok = unproved_ok = 0
    for r in ROWS:
        for f in R.forced_bounds(r["A"], r["B"], r["characters"], r["l"], r["m"]):
            ok = distance.verify_witness(r["A"], r["B"], r["l"], r["m"], "Z", f["support"])
            assert ok["weight"] == f["value"]
            if f["proved"]:
                proved, proved_ok = proved + 1, proved_ok + ok["logical"]
                assert r["search"]["d"] <= f["value"]
            else:
                unproved, unproved_ok = unproved + 1, unproved_ok + ok["logical"]
    assert (proved_ok, proved, unproved_ok, unproved) == (33, 33, 82, 113)
    rng = random.Random("test qec-census-2 quotient witnesses")
    for r in rng.sample(ROWS, 150):
        q = R.quotient_bound(r["A"], r["B"], r["characters"], r["l"], r["m"])
        if q is not None:
            v = distance.verify_witness(r["A"], r["B"], r["l"], r["m"], "Z", q["support"])
            assert v["logical"] and v["weight"] == q["bound"]


def test_the_base_reduction_reproduces_stage_1():
    tori = sorted(t for t in R.stage1_ksets() if R.frontier_torus(*t) and R.stage1_ksets()[t])
    assert len(tori) == 13
    bests = reduce = 0
    for t in tori:
        rows = [r for r in ROWS if (r["l"], r["m"]) == t]
        top = max(r["k"] * r["search"]["d"] ** 2 for r in rows)
        at = [r for r in rows if r["k"] * r["search"]["d"] ** 2 == top]
        bests += len(at)
        reduce += sum(R.reduces_to_base(r["A"], r["B"], *t) for r in at)
        assert all(r["k"] >= 8 for r in rows if R.reduces_to_base(r["A"], r["B"], *t))
    assert bests == reduce == 20
    rows = [r for r in ROWS if (r["l"], r["m"]) == (6, 15)]
    assert sum(R.reduces_to_base(r["A"], r["B"], 6, 15) for r in rows) == 60
    assert R.reduces_to_base([[0, 0], [0, 1], [0, 2]], [[0, 0], [1, 0], [2, 0]], 3, 3)
    assert not R.reduces_to_base([[0, 0], [0, 1], [0, 2]], [[0, 0], [0, 1], [0, 2]], 3, 3)
    with pytest.raises(ValueError):
        R.reduces_to_base([[0, 0], [0, 1], [0, 2]], [[0, 0], [1, 0], [2, 0]], 3, 5)


def test_orbits_and_subgroups():
    # every stage-1 class's Frobenius orbits have the size orbit_size gives their type
    for r in ROWS[::7]:
        for o in r["frobenius_orbits"]:
            t = R.character_order(*o["first"], r["l"], r["m"])
            assert o["size"] == R.orbit_size(*t)
    # odd_subgroups against a brute-force closure on small tori
    for ell, m in [(3, 3), (3, 9), (6, 9), (9, 9), (5, 15), (12, 6)]:
        lo, mo = R.odd(ell), R.odd(m)
        (s2, _), (t2, _) = R.two_part(ell), R.two_part(m)
        odd = [((s2 * u) % ell, (t2 * v) % m) for u in range(lo) for v in range(mo)]
        n, found = math.lcm(lo, mo), set()
        for g in odd:
            for h in odd:
                sub = {
                    ((i * g[0] + j * h[0]) % ell, (i * g[1] + j * h[1]) % m)
                    for i in range(n)
                    for j in range(n)
                }
                found.add(tuple(sorted(sub)))
        assert set(R.odd_subgroups(ell, m)) == found, (ell, m)
        assert R.odd_subgroups(ell, m)[0] == ((0, 0),)


# ---------------------------------------------------------------- the registration


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


def test_the_registration_computes_nothing_on_any_torus(monkeypatch):
    _forbid_computing(monkeypatch)
    q = S.question()
    preds = S.predictions()
    assert q["id"] == C.STAGE2_ID == S.ID
    assert [tuple(t) for t in q["tori"]] == R.held_out() and len(q["tori"]) == 122
    assert set(q["sha256"]) == {
        "census_py",
        "census_c",
        "distance_py",
        "search_c",
        "bb_py",
        "retest_py",
        "holdout_json",
        "summary_json",
        "rules_py",
    }
    parts = [p["part"] for p in preds]
    assert parts == ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9"]
    by = {p["part"]: p for p in preds}
    assert len(by["H1"]["predicted"]) == 122
    assert sum(by["H1"]["predicted"].values()) == 29 == len(by["H2"]["predicted"])
    assert len(by["H7"]["instances"]) == 19
    json.dumps(q), json.dumps(preds)  # plain JSON


def test_the_held_out_predictions():
    # values follow from l and m (and stage-1 look-ups); a few by hand
    assert not R.criterion(3, 29) and not R.criterion(2, 48) and R.criterion(3, 31)
    assert R.max_k(3, 21) == {
        "bound": 56,
        "multiple": 1,
        "odd_torus": [3, 21],
        "value": 56,
        "rule": "8lm/9",
    }
    assert R.max_k(3, 40)["value"] == 8 * 8 and R.max_k(3, 40)["rule"] == "lookup"  # 3x5: 8
    assert R.max_k(3, 31)["value"] is None and R.max_k(3, 31)["bound"] == 82
    assert R.min_k(3, 31) == 2 * R.order_of_two(93) == 20
    assert R.kset_rule(3, 42)["source"] == "this run" and R.kset_rule(3, 42)["odd_torus"] == [3, 21]
    assert R.kset_rule(3, 36)["kset"] == R.lifted_kset([4, 8, 12, 24], 3, 36)
    laws = {x["key"]: x["value"] for x in S.law_instances()}
    assert laws["law 3x50 (3,5)"] == 20 and laws["law 3x31 (3,31)"] == 2
    assert laws["law 7x15 (7,3)"] == 10
    plan = S.frontier_plan()
    assert plan["h8"] == ["3x21", "3x36", "3x39", "3x42", "6x18", "6x21", "9x12"]
    assert {x["torus"] for x in plan["excluded"]} == {"3x45", "3x48", "6x24", "9x15", "12x12"}
    assert plan["h9"]["252"] == {"three": ["3x42", "6x21"], "other": ["7x18", "9x14"]}
    assert plan["h9"]["216"] == {"three": ["3x36", "6x18", "9x12"], "other": []}


def test_exposure():
    exposed = R.exposure()
    held = set(R.held_out())
    assert set(exposed) <= held and len(exposed) == 23
    assert {(12, 12), (8, 18), (6, 24), (9, 16), (2, 48), (3, 29)} <= set(exposed)
    assert set(map(tuple, R.holdout()["exposed_extrapolation"])) <= set(exposed)
    iso = R.isomorphic_to_exposed()
    assert not set(iso) & set(exposed)
    for t, twins in iso.items():
        assert all(R.torus_type(*t) == R.torus_type(*e) for e in twins)
    assert iso[(3, 36)] == [(9, 12)] and iso[(3, 42)] == [(6, 21)]
    assert S.exposure_status(12, 12) == "exposed" and S.exposure_status(3, 36) == "isomorphic"
    assert S.exposure_status(3, 21) == "clean"
    for t in R.held_out():
        assert R.torus_type(*t) == tuple(sorted(S.distance.torus_type(*t)))


# ---------------------------------------------------------------- the hold-out and the permit


def _held_out_both():
    return [t for a, b in R.held_out() for t in ((a, b), (b, a))]


def test_the_study_refuses_held_out_tori_outside_the_permit(monkeypatch):
    _forbid_computing(monkeypatch)
    A, B = [[0, 0], [0, 1], [1, 0]], [[0, 0], [0, 2], [1, 1]]
    c = {"A": A, "B": B, "class": 0, "rep": 0, "k": 4}
    entries = [
        lambda a, b: S.torus_record(a, b),
        lambda a, b: S.scan_record(a, b, 0),
        lambda a, b: S.frontier_round(a, b, 1, []),
        lambda a, b: S.crosscheck_record(a, b, []),
        lambda a, b: S.law_record(a, b, 3, 5),
        lambda a, b: S.structure(c, a, b),
        lambda a, b: S.search(A, B, a, b, "d2", 3, 1),
        lambda a, b: S.program(A, B, a, b, 1),
        lambda a, b: S._verify(A, B, a, b, [0, 1]),
        lambda a, b: S._classes(a, b),
    ]
    for a, b in _held_out_both() + [(6, 11), (2, 36), (3, 26), (12, 13), (3, 2)]:
        for entry in entries:
            with pytest.raises(C.HeldOut):
                entry(a, b)


def _ledger(path: Path, kinds=("question", "prediction", "run_started"), tori=None, qid=None):
    from lattice_lab.ledger import Ledger

    ledger = Ledger(path)
    for kind in kinds:
        body = {"id": qid or C.STAGE2_ID, "tori": tori or [list(t) for t in R.held_out()]}
        ledger.append(kind, body if kind == "question" else {"x": 1})
    return path


def _as_job(source: str, filename: Path, name: str = "job"):
    """The function `name` of `source`, whose code says it is defined in `filename`."""
    namespace = {"C": C}
    exec(compile(source, str(filename), "exec"), namespace)
    return namespace[name]


JOB = """
def job(tori, probe):
    with C.Stage2Permit(tori):
        return [probe(*t) for t in tori]
"""


def test_the_permit_opens_only_in_the_registered_job_during_the_run(tmp_path, monkeypatch):
    _forbid_computing(monkeypatch)
    monkeypatch.setattr(C, "STAGE2_LEDGER", tmp_path / "ledger.jsonl")
    job = _as_job(JOB, C.STAGE2_STUDY)

    def opened(a, b):
        C.guard(a, b)
        return True

    # no ledger: refused, and nothing opened
    with pytest.raises(C.HeldOut, match="not registered"):
        job([(3, 21)], opened)
    # registered but not started, or already judged: refused
    _ledger(tmp_path / "ledger.jsonl", ("question", "prediction"))
    with pytest.raises(C.HeldOut, match="has not started"):
        job([(3, 21)], opened)
    (tmp_path / "ledger.jsonl").unlink()
    _ledger(tmp_path / "ledger.jsonl", ("question", "prediction", "run_started", "observations"))
    with pytest.raises(C.HeldOut, match="in progress"):
        job([(3, 21)], opened)
    (tmp_path / "ledger.jsonl").unlink()
    _ledger(tmp_path / "ledger.jsonl", qid="another study")
    with pytest.raises(C.HeldOut, match="question is not"):
        job([(3, 21)], opened)
    (tmp_path / "ledger.jsonl").unlink()
    # a started run of the registered study: the job's torus opens, for the block only
    _ledger(tmp_path / "ledger.jsonl", tori=[[3, 21], [3, 31]])
    assert job([(3, 21)], opened) == [True]
    with pytest.raises(C.HeldOut):
        C.guard(3, 21)
    with pytest.raises(C.HeldOut):  # the other orientation stays refused
        job([(3, 21)], lambda a, b: C.guard(b, a))
    with pytest.raises(C.HeldOut, match="not among the registered"):
        job([(3, 22)], opened)
    with pytest.raises(C.HeldOut, match="not a held-out torus"):
        job([(6, 11)], opened)
    with pytest.raises(C.HeldOut):  # a refused torus stays refused inside a permit
        job([(3, 21)], lambda a, b: C.guard(6, 11))
    assert C._STAGE2_OPEN == frozenset()
    # the same code anywhere else, or under another name, is refused
    with pytest.raises(C.HeldOut, match="job only"):
        _as_job(JOB, tmp_path / "study.py")([(3, 21)], opened)
    with pytest.raises(C.HeldOut, match="job only"):
        _as_job(JOB.replace("def job", "def jobs"), C.STAGE2_STUDY, "jobs")([(3, 21)], opened)
    with pytest.raises(C.HeldOut, match="job only"):
        with C.Stage2Permit([(3, 21)]):
            pass
    # a tampered ledger is refused
    lines = (tmp_path / "ledger.jsonl").read_text().splitlines()
    lines[0] = lines[0].replace("3,21", "3,22")
    (tmp_path / "ledger.jsonl").write_text("\n".join(lines) + "\n")
    with pytest.raises(C.HeldOut, match="does not verify"):
        job([(3, 21)], opened)


def test_job_needs_the_permit(tmp_path, monkeypatch):
    _forbid_computing(monkeypatch)
    monkeypatch.setattr(C, "STAGE2_LEDGER", tmp_path / "ledger.jsonl")
    calls = []

    def dispatch(spec, path):
        C.guard(spec["l"], spec["m"])
        calls.append(spec["key"])
        return {"classes": []}

    monkeypatch.setattr(S, "_dispatch", dispatch)
    monkeypatch.setattr(S.distance, "scip_version", lambda: "SCIP (test)")
    spec = {"test": "torus", "key": "torus 3x21", "l": 3, "m": 21}
    with pytest.raises(C.HeldOut):
        S.job(spec, str(tmp_path / "records.jsonl"))
    assert calls == []
    _ledger(tmp_path / "ledger.jsonl")
    record = S.job(spec, str(tmp_path / "records.jsonl"))
    assert calls == ["torus 3x21"] and record["key"] == "torus 3x21"
    with pytest.raises(C.HeldOut):
        C.guard(3, 21)


# ---------------------------------------------------------------- jobs and the scheduler


def test_the_jobs():
    jobs = S.jobs()
    keys = [j["key"] for j in jobs]
    assert len(keys) == len(set(keys))
    tori = {(j["l"], j["m"]) for j in jobs}
    assert tori <= set(R.held_out())
    assert {(j["l"], j["m"]) for j in jobs if j["test"] == "torus"} == set(R.held_out())
    assert sorted(j["key"] for j in jobs if j["test"] == "law") == sorted(
        x["key"] for x in S.law_instances()
    )
    plan = S.frontier_plan()
    for name in plan["tori"]:
        assert f"crosscheck {name}" in keys
        assert all(f"frontier {name} round {r}" in keys for r in range(1, S.ROUNDS + 1))
    position = {key: i for i, key in enumerate(keys)}
    for j in jobs:
        assert all(a in position for a in j.get("after", []))
        assert S.TIMEOUTS[j["test"]] < 2 * 3600  # a cloud session's command stops at 2 hours
    assert set(plan["tori"]) == {
        "3x21",
        "3x36",
        "3x39",
        "3x42",
        "6x18",
        "6x21",
        "9x12",
        "7x18",
        "9x14",
    }


def test_execute_respects_dependencies_and_resumes(tmp_path, monkeypatch):
    jobs = [
        {"test": "torus", "key": "a", "l": 3, "m": 21},
        {"test": "frontier", "key": "c", "l": 3, "m": 21, "after": ["a", "b"]},
        {"test": "scan", "key": "b", "l": 3, "m": 21},
        {"test": "torus", "key": "d", "l": 3, "m": 31},
    ]
    monkeypatch.setattr(S, "jobs", lambda: jobs)
    order = []

    def run(spec, path):
        order.append(spec["key"])
        if spec["key"] == "b":
            return {**spec, "error": "boom"}
        return {**spec, "seen": [r["key"] for r in S.prior_records(spec, path)]}

    path = tmp_path / "records.jsonl"
    S.execute(path, 1, run=run)
    assert order == ["a", "b", "c", "d"]  # c waits for a and b, then goes before d
    records = [json.loads(x) for x in path.read_text().splitlines()]
    assert next(r for r in records if r["key"] == "c")["seen"] == ["a", "b"]
    S.execute(path, 1, run=run)  # resume: nothing to do
    assert order == ["a", "b", "c", "d"]
    path.write_text(path.read_text() + '{"key": "e", "rows": [1')
    with pytest.raises(S.StudyError, match="incomplete line"):
        S.execute(path, 1, run=run)
    monkeypatch.setattr(
        S, "jobs", lambda: [{"test": "torus", "key": "x", "l": 3, "m": 21, "after": ["nothing"]}]
    )
    with pytest.raises(S.StudyError, match="no job will write"):
        S.execute(tmp_path / "other.jsonl", 2, run=run)


# ---------------------------------------------------------------- the procedures, on stage 1


def _exact_run(d, instrument="scan"):
    return {
        "instrument": instrument,
        "status": "complete",
        "d": d,
        "lower": d,
        "upper": d,
        "witness": list(range(d)),
        "verified": True,
        "k": None,
    }


def _keyed(test, name, body):
    return {"key": f"{test} {name}", "test": test, **body}


def test_the_torus_record_reproduces_stage_1():
    rec = S.torus_record(3, 9)
    rows = _rows("3x9")
    assert rec["raw_k_positive"] == 476 and rec["kset"] == [4, 8, 12, 24]
    assert [c["rep"] for c in rec["classes"]] == [r["rep"] for r in rows]
    for c, r in zip(rec["classes"], rows, strict=True):
        assert (c["runs"][0]["d"] == 2) == (r["search"]["d"] == 2)
        assert S.interval(c["runs"])[0] <= r["search"]["d"] <= S.interval(c["runs"])[1]
        assert c["structure"]["k_characters"] == c["k"]
        assert c["structure"]["base"] == R.reduces_to_base(r["A"], r["B"], 3, 9)


def test_the_frontier_pipeline_on_a_small_stage1_torus():
    name, rows = "3x12", _rows("3x12")
    recs = [_keyed("torus", name, S.torus_record(3, 12))]
    recs += [_keyed("scan", f"{name} part {i}", S.scan_record(3, 12, i)) for i in range(4)]
    rnd = S.frontier_round(3, 12, 1, recs)
    assert rnd["stopped"] == "resolved" and not rnd["conflicts"] and not rnd["missing"]
    state = S.merge(recs + [_keyed("frontier", name, rnd)], 3, 12)
    truth = {r["class"]: r["search"]["d"] for r in rows}
    assert all(S.exact(s["runs"]) == truth[i] for i, s in state.items())
    out = S._frontier_outcome(state)
    top = max(r["k"] * r["search"]["d"] ** 2 for r in rows)
    assert out["outcome"] == "holds"
    assert out["best"] == [r["class"] for r in rows if r["k"] * r["search"]["d"] ** 2 == top]


def test_the_frontier_round_probes_searches_and_keeps_its_budget(monkeypatch):
    # the loop's logic with a stand-in for the search: class 0 (k 8) hides d = 10, class 1
    # (k 4) d = 12, class 2 (k 4) d = 14; after a scan that bounds nothing
    classes = [
        {"class": i, "rep": i, "k": k, "A": None, "B": None} for i, k in enumerate((8, 4, 4))
    ]
    truth = {0: 10, 1: 12, 2: 14}
    monkeypatch.setattr(S, "_classes", lambda ell, m: classes)
    calls = []

    def search(A, B, ell, m, instrument, bound, limit):
        i = current[0]
        d = truth[i]
        calls.append((i, instrument, bound))
        if instrument == "probe":  # one pass: finds d if d < bound, within its time
            if d < bound:
                return {
                    "instrument": "probe",
                    "status": "complete",
                    "d": d,
                    "lower": d,
                    "upper": d,
                    "witness": [0] * d,
                    "verified": True,
                    "bound": bound,
                }
            return {
                "instrument": "probe",
                "status": "complete",
                "d": None,
                "lower": bound,
                "upper": None,
                "witness": None,
                "verified": None,
                "bound": bound,
            }
        return {**_exact_run(d, "deep"), "bound": bound}

    current = [None]

    def pick(state, cands, skip):
        i = real_pick(state, cands, skip)
        current[0] = i
        return i

    real_pick = S._pick
    monkeypatch.setattr(S, "_pick", pick)
    monkeypatch.setattr(S, "search", search)
    scan = [
        {
            "class": i,
            "rep": i,
            "k": c["k"],
            "runs": [
                {
                    "instrument": "scan",
                    "status": "timelimit",
                    "d": None,
                    "lower": 9,
                    "upper": None,
                    "witness": None,
                    "verified": None,
                }
            ],
        }
        for i, c in enumerate(classes)
    ]
    prior = [{"key": "scan 3x9 part 0", "l": 3, "m": 9, "classes": scan}]
    rec = S.frontier_round(3, 9, 1, prior)
    # class 0 first (largest k at equal lower bound): no threshold to probe below, so searched;
    # then L = 800, and classes 1 and 2 are probed at their thresholds (15): found below, out
    assert calls == [(0, "deep", 64), (1, "probe", 15), (2, "probe", 15)]
    assert rec["stopped"] == "resolved" and rec["best"] == [0] and rec["L"] == 800
    # a budget too small for a deep search stops the round before it
    calls.clear()
    clock = iter(range(0, 10**6, 1000))
    rec = S.frontier_round(3, 9, 1, prior, budget=S.DEEP_LIMIT - 1, clock=lambda: next(clock))
    assert rec["stopped"] == "budget" and calls == [] and rec["candidates"] == [0, 1, 2]


def test_the_law_procedure_on_stage1_instances():
    for name, typ, outcome in (
        ("3x10", (3, 5), "equal"),
        ("5x6", (5, 3), "equal"),
        ("3x15", (3, 5), "below"),
    ):
        ell, m = map(int, name.split("x"))
        rec = S.law_record(ell, m, *typ)
        state = S.merge([_keyed("law", name, rec)], ell, m)
        truth = {r["class"]: r["search"]["d"] for r in _rows(name)}
        assert S._law_outcome(state, [c["class"] for c in rec["classes"]], rec["value"]) == outcome
        for i, s in state.items():
            assert S.interval(s["runs"])[0] <= truth[i] <= S.interval(s["runs"])[1]
        assert rec["stopped"] == "done"


# ---------------------------------------------------------------- decide, on synthetic records


def _search_run(d, instrument="d2", lower=None, status="complete", bound=3, lm=63, upper=None):
    found = d if d is not None and d < bound else None
    lower = lower if lower is not None else (found if found else bound)
    up = upper if upper is not None else found
    return {
        "instrument": instrument,
        "status": status,
        "d": found if status == "complete" else None,
        "lower": lower,
        "upper": up,
        "witness": list(range(up)) if up else None,
        "verified": True if up else None,
        "k": None,
        "bound": bound,
        "deepen": instrument not in ("probe", "law probe"),
        "anchors": [0, lm],
        "limit": S.INSTRUMENTS[instrument]["limit"],
    }


def _klass(i, k, d, cond=None, base=True, quotient=None, zeros=None, lm=63):
    """A torus record's class row: d is the class's true d (the d2 run and a scan know it)."""
    cond = (d == 2) if cond is None else cond
    st = {
        "zeros": zeros or [[1, 1, 1]] * (k // 2),
        "k_characters": k,
        "cond_i": cond,
        "cond_ii": False,
        "quotient": quotient,
        "forced": [],
        "base": base,
    }
    runs = [_search_run(d, "d2", lm=lm)]
    if d > 2:
        runs.append(_search_run(d, "scan", bound=64, lm=lm, upper=d, lower=d))
        runs[-1].update({"d": d})
    return {
        "class": i,
        "rep": 100 + i,
        "params": [0] * 6,
        "k": k,
        "size": 1,
        "k_constant": True,
        "structure": st,
        "runs": runs,
    }


def _torus_rec(name, classes):
    ell, m = map(int, name.split("x"))
    ks = sorted({c["k"] for c in classes})
    return {
        "key": f"torus {name}",
        "test": "torus",
        "l": ell,
        "m": m,
        "n": 2 * ell * m,
        "raw_k_positive": sum(c["size"] for c in classes),
        "kset": ks,
        "max_k": max(ks, default=0),
        "min_k": min(ks, default=None),
        "classes": classes,
    }


def _synthetic(monkeypatch):
    """A small study: 3x21 (clean, codes), 3x29 (exposed, none), 3x42 (isomorphic to 6x21,
    codes), 6x21 (exposed, codes), 7x18 (other torus at n = 252), 2x28 (clean, none); one H7
    instance on each of 3x21 and 3x42; H8 on 3x21, 3x42 and 6x21; H9 at 126 and 252."""
    preds = {
        "H1": {
            "part": "H1",
            "predicted": {
                "3x21": True,
                "3x29": False,
                "3x42": True,
                "6x21": True,
                "7x18": True,
                "2x28": False,
            },
        },
        "H2": {
            "part": "H2",
            "predicted": {
                "3x21": {"value": 56, "bound": 56, "multiple": 1, "odd_torus": [3, 21]},
                "3x42": {"value": 112, "bound": 112, "multiple": 2, "odd_torus": [3, 21]},
                "6x21": {"value": 112, "bound": 112, "multiple": 2, "odd_torus": [3, 21]},
                "7x18": {"value": None, "bound": 112, "multiple": 2, "odd_torus": [7, 9]},
            },
        },
        "H3": {"part": "H3", "predicted": {"3x21": 4, "3x42": 4, "6x21": 4, "7x18": 12}},
        "H4": {
            "part": "H4",
            "predicted": {
                "3x42": {"source": "this run", "odd_torus": [3, 21], "kset": None},
                "6x21": {"source": "this run", "odd_torus": [3, 21], "kset": None},
                "7x18": {"source": "stage 1", "odd_torus": [7, 9], "kset": [12, 24]},
            },
        },
        "H5": {"part": "H5", "tori": ["3x21", "3x42", "6x21", "7x18"], "protocol": S.PROTOCOL},
        "H6": {"part": "H6"},
        "H7": {
            "part": "H7",
            "instances": [
                {
                    "key": "law 3x21 (3,7)",
                    "torus": "3x21",
                    "l": 3,
                    "m": 21,
                    "type": [3, 7],
                    "value": 6,
                },
                {
                    "key": "law 3x42 (3,7)",
                    "torus": "3x42",
                    "l": 3,
                    "m": 42,
                    "type": [3, 7],
                    "value": 12,
                },
            ],
            "threshold": {},
        },
        "H8": {"part": "H8", "tori": ["3x21", "3x42", "6x21"]},
        "H9": {
            "part": "H9",
            "sizes": {
                "126": {"three": ["3x21"], "other": []},
                "252": {"three": ["3x42", "6x21"], "other": ["7x18"]},
            },
        },
    }
    records = [
        _torus_rec(
            "3x21",
            [_klass(0, 56, 2), _klass(1, 8, 6, zeros=[[1, 3, 1]] * 4), _klass(2, 4, 4, base=False)],
        ),
        _torus_rec("3x29", []),
        _torus_rec("2x28", []),
        _torus_rec(
            "3x42",
            [
                _klass(0, 112, 2, lm=126),
                _klass(1, 8, 12, lm=126, zeros=[[1, 6, 1]] * 4),
                _klass(2, 4, 14, base=False, lm=126),
            ],
        ),
        _torus_rec("6x21", [_klass(0, 112, 2, lm=126), _klass(1, 4, 16, base=False, lm=126)]),
        _torus_rec(
            "7x18", [_klass(0, 12, 8, base=False, lm=126), _klass(1, 24, 4, base=False, lm=126)]
        ),
    ]
    records[3]["kset"] = [4, 8, 112]  # synthetic: lifted 3x21 k-set is [4, 8, 16, 56, 112]
    for name, rec in (("3x21", records[0]), ("3x42", records[3])):
        law = {
            "key": f"law {name} (3,7)",
            "test": "law",
            "l": rec["l"],
            "m": rec["m"],
            "type": [3, 7],
            "value": 2 * rec["m"] // 7,
            "classes": [{"class": 1, "rep": 101, "k": 8, "runs": []}],
        }
        records.append(law)
    jobs = [{"key": r["key"], "test": r["test"], "l": r["l"], "m": r["m"]} for r in records]
    monkeypatch.setattr(S, "jobs", lambda: jobs)
    return records, list(preds.values())


def test_decide_on_a_passing_synthetic_run(monkeypatch):
    records, preds = _synthetic(monkeypatch)
    records[3]["kset"] = R.lifted_kset([4, 8, 56], 3, 42)
    records[3]["kset"] = sorted(set(records[3]["kset"]))
    v = S.decide(records, preds)
    assert v["parts"]["H1"] == "holds" and v["detail"]["H1"]["exposed"] == "holds"
    assert v["parts"]["H2"] == "holds" and v["detail"]["H2"]["found"]["7x18"] == 24
    assert v["parts"]["H3"] == "holds" and v["parts"]["H5"] == "holds"
    assert v["parts"]["H7"] == "holds" and v["detail"]["H7"]["items"] == {
        "law 3x21 (3,7)": "equal",
        "law 3x42 (3,7)": "equal",
    }
    assert v["detail"]["H8"]["items"] == {"3x21": "holds", "3x42": "holds", "6x21": "fails"}
    assert v["parts"]["H8"] == "holds"  # 6x21 is exposed: reported apart
    assert v["detail"]["H8"]["exposed"] == "fails"
    assert v["detail"]["H9"]["items"]["126"] == "holds"
    assert v["detail"]["H9"]["detail"]["126"]["judged"]["uncontested"]
    assert v["detail"]["H9"]["items"]["252"] == "holds"
    assert v["instruments"] == "hold" and v["verdict"] == "hold", v["parts"]


def test_decide_fails_and_reports_what_failed(monkeypatch):
    records, preds = _synthetic(monkeypatch)
    records[3]["kset"] = sorted(set(R.lifted_kset([4, 8, 56], 3, 42)))
    # H1 on a clean torus: codes where none were predicted
    records[2]["raw_k_positive"] = 3
    # H5: a class with d = 2 that neither condition predicts
    records[0]["classes"][1]["structure"]["cond_i"] = True
    v = S.decide(records, preds)
    assert v["detail"]["H1"]["items"]["2x28"] == "fails" and v["parts"]["H1"] == "fails"
    assert v["detail"]["H5"]["items"]["3x21"] == "fails"
    assert v["detail"]["H5"]["detail"]["3x21"]["mismatch"] == [1]
    assert v["verdict"] == "fail"
    # H4 against this run's odd torus
    records, preds = _synthetic(monkeypatch)
    v = S.decide(records, preds)
    assert v["detail"]["H4"]["items"]["3x42"] == "fails"
    assert v["detail"]["H4"]["sets"]["3x42"]["expected"] == [4, 8, 16, 56, 112]


def test_decide_on_instruments_and_bounds(monkeypatch):
    records, preds = _synthetic(monkeypatch)
    records[3]["kset"] = sorted(set(R.lifted_kset([4, 8, 56], 3, 42)))
    # a program whose interval misses the search's d: a disagreement fails the instruments
    program = {
        "instrument": "program",
        "status": "optimal",
        "d": 8,
        "lower": 8,
        "upper": 8,
        "witness": list(range(8)),
        "verified": True,
        "k": 8,
        "scip_fix": True,
        "settings": S.distance.SCIP_FIX,
        "seed": 0,
        "limit": S.PROGRAM_LIMIT,
    }
    records.append(
        {
            "key": "crosscheck 3x42",
            "test": "crosscheck",
            "l": 3,
            "m": 42,
            "classes": [{"class": 1, "rep": 101, "k": 8, "runs": [program]}],
        }
    )
    # an odd d and a lower bound above the quotient bound on 3x21
    records[0]["classes"][2]["structure"]["quotient"] = {
        "bound": 2,
        "order": 1,
        "form": "B",
        "g": [1, 0],
        "weight": 2,
        "verified": True,
    }
    v = S.decide(records, preds)
    problems = v["detail"]["H6"]["problems"]
    assert any("DISAGREEMENT" in p for p in problems["3x42"][1])
    assert any("quotient bound" in p for p in problems["3x21"][2])
    assert v["instruments"] == "fail" and v["verdict"] == "fail"
    # a run made otherwise than registered
    records, preds = _synthetic(monkeypatch)
    records[0]["classes"][0]["runs"][0]["anchors"] = "all"
    v = S.decide(records, preds)
    assert v["protocol_failures"]["torus 3x21"] and v["instruments"] == "fail"


def test_decide_unresolved_and_missing(monkeypatch):
    records, preds = _synthetic(monkeypatch)
    records[3]["kset"] = sorted(set(R.lifted_kset([4, 8, 56], 3, 42)))
    # 3x42: the best's d only bracketed: [11, inf] on a k = 8 class, so H8 and H7 unresolved
    c = records[3]["classes"][1]
    c["runs"] = [
        _search_run(12, "d2", lm=126),
        _search_run(None, "scan", status="timelimit", lower=9, bound=64, lm=126),
    ]
    records = [r for r in records if r["key"] != "torus 7x18"]
    v = S.decide(records, preds)
    assert v["detail"]["H8"]["items"]["3x42"] == "unresolved"
    assert v["detail"]["H7"]["items"]["law 3x42 (3,7)"] == "unresolved"
    assert v["detail"]["H9"]["items"]["252"] == "not tested"
    assert v["missing"] == ["torus 7x18"] and v["verdict"] == "incomplete"
    assert v["detail"]["H7"]["outcome"] == "inconclusive"  # 1 of 2 resolved < 75%


def test_the_law_threshold_and_the_frontier_rule():
    eq = {f"i{j}": "equal" for j in range(8)}
    assert S._law_verdict(eq) == "holds"
    assert S._law_verdict({**eq, "a": "below", "b": "below"}) == "holds"  # 8 of 10
    assert S._law_verdict({**eq, "a": "below", "b": "below", "c": "below"}) == "fails"
    assert S._law_verdict({**eq, "a": "above"}) == "fails"
    assert S._law_verdict({**eq, **{f"u{j}": "unresolved" for j in range(3)}}) == "inconclusive"
    assert S._law_verdict({}) == "not applicable"

    def st(runs_by_class, base):
        return {
            i: {"k": k, "runs": runs, "base": base[i]} for i, (k, runs) in runs_by_class.items()
        }

    best = {0: (8, [_exact_run(10)]), 1: (4, [_exact_run(12)])}  # 800 against 576
    assert S._frontier_outcome(st(best, {0: True, 1: False}))["outcome"] == "holds"
    assert S._frontier_outcome(st(best, {0: False, 1: True}))["outcome"] == "fails"
    loose = {
        0: (8, [_exact_run(10)]),
        1: (
            4,
            [{"instrument": "scan", "status": "timelimit", "d": None, "lower": 9, "upper": None}],
        ),
    }
    out = S._frontier_outcome(st(loose, {0: True, 1: False}))
    assert out["outcome"] == "unresolved" and out["not_reducing"] == [1]
    assert S._frontier_outcome(st(loose, {0: True, 1: True}))["outcome"] == "holds"


def test_crosscheck_choice_and_threshold():
    state = {i: {"k": 4, "runs": [_exact_run(d)]} for i, d in enumerate([2, 4, 6, 8, 8, 6])}
    choice = S.crosscheck_choice(state, "3x9")
    assert [i for i, why in choice.items() if why == "best"] == [3, 4]
    assert sum(why == "sample" for why in choice.values()) == 1
    assert all(S.exact(state[i]["runs"]) >= 4 for i in choice)
    assert S._threshold(4, 800) == 15 and S._threshold(8, 800) == 10
    assert S._threshold(8, math.inf) == S.BOUND


def test_the_worker_process_refuses_without_a_started_run(tmp_path):
    # the real worker path (a subprocess loading study.py and calling job) on a stage-1 torus's
    # name: the permit refuses before anything is computed, whatever state stage 2's ledger is in
    # (absent, registered, or a run in progress, which would not list 3x9)
    spec = {"test": "torus", "key": "torus 3x9", "l": 3, "m": 9}
    record = S._run(spec, tmp_path / "records.jsonl")
    assert record["key"] == "torus 3x9" and "HeldOut" in record["error"]
    assert "Stage2Permit" in record["error"]
