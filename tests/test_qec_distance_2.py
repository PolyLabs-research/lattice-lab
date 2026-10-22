"""The registered re-test of the distance instruments (examples/qec-distance-2/study.py): its
sizes, codes and equivalence keys, and its rules on synthetic records. Nothing here computes a
distance of a code of the re-test; the equivalence checks use development sizes only."""

import importlib.util
import random
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))
sys.path.insert(0, str(ROOT / "examples" / "qec-distance"))

import bb  # noqa: E402
import distance as D  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STUDY = _load("qec_distance_retest", ROOT / "examples" / "qec-distance-2" / "study.py")
TESTS = _load("test_qec_distance_sizes", ROOT / "tests" / "test_qec_distance.py")
# the sizes at which development drew random codes after the registered run: the SCIP fault
# hunt and the fault scan, the deepening search's codes, the timing codes, the verification's
# hunts (H1, H2 and the power check of part (a)) and part (f)'s smoke test
DEVELOPMENT_SIZES = [(2, 2), (2, 3), (2, 4), (3, 3), (2, 5), (2, 6), (3, 4), (2, 7), (4, 4),
                     (2, 8), (3, 6), (2, 9), (6, 3), (2, 12), (4, 5), (5, 4), (2, 10), (2, 11),
                     (4, 6), (6, 4), (3, 8), (8, 3), (5, 5), (1, 16), (1, 25), (7, 7), (6, 10),
                     (9, 9), (7, 14), (12, 9), (6, 24), (1, 13), (1, 17), (1, 18), (1, 19),
                     (1, 20), (1, 23), (1, 24), (3, 11), (2, 17), (2, 19), (3, 13), (6, 7),
                     (3, 14), (4, 11), (2, 22), (2, 23), (5, 10), (3, 17), (4, 13), (5, 11),
                     (7, 8), (4, 14), (8, 8), (4, 16), (6, 11), (4, 17), (6, 13)]  # fmt: skip


def test_the_sizes_are_reserved_and_of_no_other_type():
    first = STUDY.first
    reserved = STUDY.RESERVED_SMALL + STUDY.RESERVED_PAIR
    assert set(STUDY.METHOD_SIZES) <= set(STUDY.RESERVED_SMALL)
    assert set(STUDY.TRINOMIAL_SIZES) <= set(STUDY.RESERVED_PAIR)
    # only 2x13 and 3x9 can hold a code within the enumeration's cap; part (f) takes the rest
    assert STUDY.METHOD_SIZES == [(2, 13), (3, 9)]
    assert STUDY.POWER_SIZES == [(3, 10), (4, 7), (5, 6), (2, 14), (4, 8), (5, 8)]
    assert D.torus_type(3, 10) == D.torus_type(5, 6)  # the isomorphic pair
    assert all(
        ell * m + 1 > D.BRUTE_CAP for ell, m in set(STUDY.RESERVED_SMALL) - {(2, 13), (3, 9)}
    )
    assert set(STUDY.RESERVED_PAIR) - set(STUDY.TRINOMIAL_SIZES) == {(5, 13)}
    # no reserved size has a published entry's order, or the type of a size that development,
    # the tests or the registered test drew random codes at
    orders = {ell * m for ell, m in first.PUBLISHED_SIZES}
    assert not orders & {ell * m for ell, m in reserved}
    used = first.PUBLISHED_SIZES + first.METHOD_SIZES + first.SEARCH_SIZES + TESTS.SIZES
    used += DEVELOPMENT_SIZES
    assert not {D.torus_type(*s) for s in used} & {D.torus_type(*s) for s in reserved}


def _mentions(text: str, ell: int, m: int) -> bool:
    return any(re.search(rf"(?<![\dx]){a}x{b}(?![\d])", text) for a, b in ((ell, m), (m, ell)))


def test_the_toric_sizes_are_new():
    first = STUDY.first
    text = " ".join(first.EXCLUDED_SEEN + STUDY.EXCLUDED_SEEN)
    earlier = set(first.TORIC_SIZES) | {(2, 5), (3, 3), (4, 4), (3, 6), (4, 6), (5, 6), (6, 8),
                                        (3, 4), (10, 10), (20, 20)}  # fmt: skip
    for ell, m in STUDY.TORIC_SIZES:
        assert not _mentions(text, ell, m), (ell, m)
        assert (ell, m) not in earlier and (m, ell) not in earlier
    assert _mentions(text, 16, 17) and _mentions(text, 13, 13)  # the check can see a size
    ns = [2 * ell * m for ell, m in STUDY.TORIC_SIZES]
    assert len(set(STUDY.TORIC_SIZES)) == 6 and max(ns) == 510


def test_the_codes_are_fresh_distinct_and_as_registered():
    for ell, m in STUDY.METHOD_SIZES:
        codes = STUDY.method_codes(ell, m)
        assert len(codes) == STUDY.PER_SIZE
        keys = [STUDY.equivalence_key(c["A"], c["B"], ell, m) for c in codes]
        assert len(set(keys)) == len(keys) and not set(keys) & STUDY.seen_keys(ell, m)
        assert all(c["k"] == bb.k_linalg(c["A"], c["B"], ell, m) > 0 for c in codes)
        assert all(ell * m + c["k"] // 2 <= D.BRUTE_CAP for c in codes)
    for ell, m in STUDY.TRINOMIAL_SIZES:
        codes = STUDY.trinomial_codes(ell, m)
        assert len(codes) == STUDY.TRINOMIAL_PER_SIZE
        keys = [STUDY.equivalence_key(c["A"], c["B"], ell, m) for c in codes]
        assert len(set(keys)) == len(keys) and not set(keys) & STUDY.seen_keys(ell, m)
        for c in codes:
            assert 4 <= c["k"] <= 12 and c["form"] == STUDY.TRINOMIAL_FORMS[(ell, m)]
            assert len(c["A"]) == len(c["B"]) == 3
            A, B = c["A"], c["B"]
            if c["form"] == "published":  # A = x^a + y^b + y^c, B = y^d + x^e + x^f
                assert A[0][1] == A[1][0] == A[2][0] == B[0][0] == B[1][1] == B[2][1] == 0
            else:
                assert len({tuple(t) for t in A}) == len({tuple(t) for t in B}) == 3
    # part (f): 8 codes of each family at each size (6 one-axis at 4x7), as the docstring says,
    # distinct within each size, from the draws, development codes and toric code, and between
    # the isomorphic tori 3x10 and 5x6
    counts, ks = {}, []
    for ell, m in STUDY.POWER_SIZES:
        codes = STUDY.power_codes(ell, m)
        keys = [STUDY.equivalence_key(c["A"], c["B"], ell, m) for c in codes]
        assert len(set(keys)) == len(keys) and not set(keys) & STUDY.seen_keys(ell, m)
        for c in codes:
            assert c["k"] == bb.k_linalg(c["A"], c["B"], ell, m) >= STUDY.POWER_KMIN
            counts[c["family"]] = counts.get(c["family"], 0) + 1
            ks.append(c["k"])
        assert [c["family"] for c in codes] == sorted(
            (c["family"] for c in codes), key=STUDY.POWER_FAMILIES.index
        )
    assert counts == {"oneaxis": 46, "hp": 48, "factor1": 48} and (min(ks), max(ks)) == (4, 40)
    assert sum(c["family"] == "oneaxis" for c in STUDY.power_codes(4, 7)) == 6
    carried = {
        STUDY._carried_key(c["A"], c["B"], (3, 10), (5, 6)) for c in STUDY.power_codes(3, 10)
    }
    assert not carried & {
        STUDY.equivalence_key(c["A"], c["B"], 5, 6) for c in STUDY.power_codes(5, 6)
    }
    for c in STUDY.power_codes(4, 8):  # the families' shapes
        A, B = c["A"], c["B"]
        if c["family"] == "hp":
            assert len({q for _, q in A}) == 1 and len({p for p, _ in B}) == 1
        if c["family"] == "oneaxis":
            assert len({q for _, q in A}) == len({q for _, q in B}) == 1 or (
                len({p for p, _ in A}) == len({p for p, _ in B}) == 1
            )
    # the checker's codes at 3x9 and 9x11, and at 7x12 (the type of 3x28), are among the keys
    # that the draws avoid, with the toric code's
    assert len(STUDY.seen_keys(3, 9)) > 1 and len(STUDY.seen_keys(3, 28)) > 1
    assert STUDY.equivalence_key(*STUDY.TORIC, 9, 11) in STUDY.seen_keys(9, 11)
    # a checker's edge case at 4x7 has A = 0 (it cancels): its key is still a key
    assert STUDY.equivalence_key([[-4, 4], [0, 4]], [[0, -6]], 4, 7) in STUDY.seen_keys(4, 7)


def test_equivalence_keys_name_equivalent_codes():
    # on development sizes only: monomial factors, swapping A and B and automorphisms of the
    # torus keep the key, and k and d with it
    rng = random.Random("test qec-distance-2 equivalence")
    ell, m = 3, 4
    group = [(p, q) for p in range(ell) for q in range(m)]
    maps = STUDY._isomorphisms((ell, m), (ell, m))
    assert len(maps) == 4  # Z_12 has 4 automorphisms
    assert len(STUDY._isomorphisms((2, 13), (2, 13))) == 12
    assert len(STUDY._isomorphisms((9, 11), (9, 11))) == 60
    assert not STUDY._isomorphisms((6, 8), (3, 16)) and STUDY._isomorphisms((5, 12), (4, 15))
    tested = 0
    while tested < 6:
        A, B = rng.sample(group, 3), rng.sample(group, 2)
        k = bb.k_linalg(A, B, ell, m)
        if not k:
            continue
        tested += 1
        key, d = STUDY.equivalence_key(A, B, ell, m), D.distance_brute(A, B, ell, m)["d"]
        g, h, f = rng.choice(group), rng.choice(group), rng.choice(maps)
        A2 = STUDY._mapped([(p + g[0], q + g[1]) for p, q in B], f, ell, m)
        B2 = STUDY._mapped([(p + h[0], q + h[1]) for p, q in A], f, ell, m)
        assert STUDY.equivalence_key(A2, B2, ell, m) == key
        assert bb.k_linalg(A2, B2, ell, m) == k and D.distance_brute(A2, B2, ell, m)["d"] == d
        # carried onto the transposed torus 4 x 3, the key is that of the transposed code
        swap = STUDY._isomorphisms((ell, m), (m, ell))[0]
        At, Bt = ([(q, p) for p, q in P] for P in (A, B))
        carried = [STUDY._mapped(P, swap, m, ell) for P in (A, B)]
        assert STUDY.equivalence_key(*carried, m, ell) == STUDY.equivalence_key(At, Bt, m, ell)
    # codes with different k are not equivalent, and their keys differ
    A, B = [(0, 0), (1, 0)], [(0, 0), (0, 2)]
    assert bb.k_linalg(A, B, 3, 4) != bb.k_linalg(*STUDY.TORIC, 3, 4)
    assert STUDY.equivalence_key(A, B, 3, 4) != STUDY.equivalence_key(*STUDY.TORIC, 3, 4)


def test_the_jobs_run_the_largest_first_and_the_predictions_are_registered():
    jobs = STUDY.jobs()
    assert len(jobs) == len({j["key"] for j in jobs}) == 130 + 142
    known = [j for j in jobs if j["test"] == "known"]
    published = known[:24]
    n = {c["name"]: c["n"] for c in STUDY.known_codes()}
    assert jobs[:24] == published and [n[j["code"]] for j in published[::2]] == sorted(
        (c["n"] for c in STUDY.first.codes()), reverse=True
    )
    assert [j["instrument"] for j in published[:2]] == [STUDY.PROGRAM, STUDY.ANCHORED]
    assert [j["code"] for j in known[24:]] == ["stalled 6x18 #1"] * 3 + ["stalled 6x18 #2"] * 3
    counts = {
        t: sum(j["test"] == t for j in jobs) for t in ("toric", "trinomial", "fault", "power")
    }
    assert counts == {"toric": 18, "trinomial": 42, "fault": 38, "power": 142}
    assert all(j["test"] == "power" for j in jobs[-142:])
    preds = STUDY.predictions()
    tests = [p["test"] for p in preds]
    assert tests[:8] == ["enumeration", "faults", "program-search", "search-completes",
                         "search-completes", "toric", "power", "power-control"]  # fmt: skip
    assert tests[8:] == ["known"] * 14 and all(p["blind"] is False for p in preds[8:])
    assert preds[1]["blind"] is False and "not a prediction" in preds[1]["note"]
    assert [p["known_d"] for p in preds[8:20]] == [c["d"] for c in STUDY.first.codes()]
    assert [p["known_d"] for p in preds[20:]] == [4, 6]
    # the decisive parts carry the protocol that decide checks the records against
    assert [i for i, p in enumerate(preds) if "protocol" in p] == [0, 1, 2, 5, 6]
    assert preds[0]["protocol"] == STUDY.PROTOCOL and STUDY.PROTOCOL["scip_fix"] == D.SCIP_FIX
    assert len(preds[6]["codes_sha256"]) == 142
    q = STUDY.question()
    assert q["id"] == "qec-distance-retest" and q["scip_fix"] == D.SCIP_FIX
    assert len(q["excluded_seen"]) == len(STUDY.EXCLUDED_SEEN)
    assert q["power_sizes"] == [list(s) for s in STUDY.POWER_SIZES]


# ---------------------------------------------------------------- synthetic records


def _result(status, d, lower, upper, k=4, logical=True, **more):
    check = {"logical": logical} if upper is not None else None
    return {"status": status, "d": d, "lower": lower, "upper": upper, "k": k,
            "witness_check": check, **more}  # fmt: skip


def _protocol(instrument, lm=None, fixed=True):
    """A result's fields that decide checks against the registered protocol."""
    if instrument == STUDY.PROGRAM:
        return {"scip_fix": fixed, "settings": dict(D.SCIP_FIX) if fixed else {}}
    return {"deepen": True, "anchors": "all" if instrument == STUDY.SEARCH else [0, lm]}


def _exact(instrument, d, k, lm=None):
    return _result(STUDY.EXACT[instrument], d, d, d, k=k, **_protocol(instrument, lm))


def _runs(d, k, seeds, fixed=True):
    """Programs of both kinds, optimal with d at each seed, under SCIP_FIX or (not `fixed`)
    SCIP's defaults."""
    fields = _protocol(STUDY.PROGRAM, fixed=fixed)
    return {kind: [_result("optimal", d, d, d, k=k, seed=s, **fields) for s in seeds]
            for kind in D.KINDS}  # fmt: skip


def _enumeration_code(lm, d=3, k=2):
    exact = {"witness_check": {"logical": True}, "d": d}
    return {"k": k, "brute": {"Z": dict(exact), "X": dict(exact)},
            "program": _runs(d, k, STUDY.METHOD_SEEDS),
            "search": {STUDY.SEARCH: _exact(STUDY.SEARCH, d, k),
                       STUDY.ANCHORED: _exact(STUDY.ANCHORED, d, k, lm)}}  # fmt: skip


def _power_code(d=3, k=4):
    return {"k": k, "k_linalg": k,
            "search": {kind: _exact(STUDY.SEARCH, d, k) for kind in D.KINDS},
            "program": _runs(d, k, STUDY.POWER_SEEDS),
            "control": _runs(d, k, STUDY.POWER_SEEDS, fixed=False)}  # fmt: skip


def _rows(preds):
    """A full, passing set of records (no computation), one per job, made by the protocol."""
    hashes, known = {}, {}
    for p in preds:
        if p["test"] == "known":
            known[p["name"]] = p
        else:
            hashes.update(p.get("codes_sha256", {}))
    rows = []
    for j in STUDY.jobs():
        if j["test"] == "enumeration":
            lm = j["l"] * j["m"]
            codes = [_enumeration_code(lm) for _ in range(STUDY.PER_SIZE)]
            rows.append({**j, "codes_sha256": hashes[j["key"]], "codes": STUDY.PER_SIZE,
                         "agree": STUDY.PER_SIZE, "rows": codes})  # fmt: skip
        elif j["test"] == "fault":
            exact = {"witness_check": {"logical": True}, "d": 2}
            rows.append({**j, "codes_sha256": hashes[j["key"]], "k": 8, "known_d": 2,
                         "k_linalg": 8, "brute": {"Z": dict(exact), "X": dict(exact)},
                         "program": _runs(2, 8, STUDY.FAULT_SEEDS)})  # fmt: skip
        elif j["test"] == "power":
            rows.append({**j, "codes_sha256": hashes[j["key"]], **_power_code()})
        elif j["test"] == "trinomial":
            rows.append({**j, "codes_sha256": hashes[j["code"]], "k_linalg": 4,
                         "result": _exact(j["instrument"], 8, 4, j["l"] * j["m"])})  # fmt: skip
        elif j["test"] == "toric":
            d = min(j["l"], j["m"])
            rows.append({**j, "A": STUDY.TORIC[0], "B": STUDY.TORIC[1], "k_linalg": 2,
                         "expected_d": d,
                         "result": _exact(j["instrument"], d, 2, j["l"] * j["m"])})  # fmt: skip
        else:
            p = known[j["code"]]
            rows.append({**j, "l": p["l"], "m": p["m"], "codes_sha256": p["codes_sha256"],
                         "k_linalg": p["k"], "known_d": p["known_d"],
                         "result": _exact(j["instrument"], p["known_d"], p["k"],
                                          p["l"] * p["m"])})  # fmt: skip
    return rows


def _replace(records, key, **fields):
    return [{**r, **fields} if r["key"] == key else r for r in records]


def _with_result(rows, key, result):
    """The rows with that job's result replaced, made by the protocol (its fields are set)."""
    row = next(r for r in rows if r["key"] == key)
    fields = _protocol(row["instrument"], row["l"] * row["m"])
    return _replace(rows, key, result={**result, **fields})


def _fail(rows, key):
    """The rows with that job's record replaced by a failed job's: its spec and an error."""
    spec = next(j for j in STUDY.jobs() if j["key"] == key)
    return [{**spec, "error": "Killed"} if r["key"] == key else r for r in rows]


PREDS = None


def _preds():
    global PREDS
    if PREDS is None:
        PREDS = STUDY.predictions()
    return PREDS


def test_decide_holds_on_a_full_passing_run_and_reports_missing_jobs():
    preds = _preds()
    rows = _rows(preds)
    verdict = STUDY.decide(rows, preds)
    assert verdict["instruments"] == "hold" and not verdict["missing"]
    assert not any(verdict["failures"].values()) and not verdict["protocol_failures"]
    assert verdict["enumeration"] == {"sizes": 2, "codes": 50, "agree": 50}
    assert verdict["faults"]["codes"] == verdict["faults"]["right"] == 38
    assert verdict["program_search"]["counts"]["agree"] == 14
    assert {v["verdict"] for v in verdict["search_completes"].values()} == {"holds"}
    assert all(verdict["toric"].values()) and len(verdict["toric"]) == 6
    assert verdict["power"]["codes"] == verdict["power"]["right"] == 142
    assert verdict["power"]["control"]["runs"] == 142 * 2 * 20
    assert verdict["known"]["counts"]["reproduced"] == 14
    assert verdict["known"]["intervals"]["[[288,12,18]]"] == [18, 18]
    # a run with jobs still to do is incomplete, not failed
    verdict = STUDY.decide(rows[5:], preds)
    assert verdict["instruments"] == "incomplete" and len(verdict["missing"]) == 5
    assert STUDY.decide([], preds)["instruments"] == "incomplete"


def test_decide_fails_on_a_wrong_value_in_the_decisive_parts():
    preds = _preds()
    rows = _rows(preds)
    fixed = _protocol(STUDY.PROGRAM)
    # (a): one program, at one seed, one too high (the fault's signature)
    bad = [_enumeration_code(26) for _ in range(STUDY.PER_SIZE)]
    bad[3]["program"]["X"][2] = _result("optimal", 4, 4, 4, k=2, seed=2, **fixed)
    verdict = STUDY.decide(_replace(rows, "enumeration 2x13", rows=bad), preds)
    assert verdict["instruments"] == "fail" and not verdict["failures"]["protocol"]
    assert verdict["failures"]["enumeration"] == {
        "enumeration 2x13": {"#4": ["program X 2: d = 4, expected 3"]}
    }
    # (a): a search that stopped at its limit is not exact, and fails
    bad = [_enumeration_code(27) for _ in range(STUDY.PER_SIZE)]
    bad[0]["search"][STUDY.SEARCH] = _result("timelimit", None, 2, None, k=2,
                                             **_protocol(STUDY.SEARCH))  # fmt: skip
    verdict = STUDY.decide(_replace(rows, "enumeration 3x9", rows=bad), preds)
    assert "enumeration 3x9" in verdict["failures"]["enumeration"]
    # (b): a fault code wrong at one seed
    key = "fault registered 4x5"
    row = next(r for r in rows if r["key"] == key)
    program = {**row["program"], "X": list(row["program"]["X"])}
    program["X"][0] = _result("optimal", 3, 3, 3, k=8, seed=0, **fixed)
    verdict = STUDY.decide(_replace(rows, key, program=program), preds)
    assert verdict["instruments"] == "fail" and list(verdict["failures"]["faults"]) == [key]
    # (e): the toric code with the wrong d, or too few logicals
    for result in (_exact(STUDY.PROGRAM, 4, 2), _exact(STUDY.PROGRAM, 5, 1)):
        verdict = STUDY.decide(_with_result(rows, "toric 5x9: program", result), preds)
        assert verdict["instruments"] == "fail" and not verdict["toric"]["toric 5x9"]
    # a failed job in a decisive part fails it
    verdict = STUDY.decide(_fail(rows, "toric 15x17: search"), preds)
    assert verdict["failures"]["toric"] == {"toric 15x17": {"search": ["not tested"]}}


def test_part_f_judges_the_fixed_program_and_reports_the_control_apart():
    preds = _preds()
    rows = _rows(preds)
    key = "power 4x7 #1"
    row = next(r for r in rows if r["key"] == key)

    def changed(arm, kind, i, **fields):
        runs = {k: list(v) for k, v in row[arm].items()}
        runs[kind][i] = {**runs[kind][i], **fields}
        return _replace(rows, key, **{arm: runs})

    # no control run wrong: the power prediction fails, beside a verdict that holds
    verdict = STUDY.decide(rows, preds)
    assert verdict["power"]["control"]["verdict"] == "fails" and verdict["instruments"] == "hold"
    # SCIP's defaults too high at one seed (the fault's signature): reported, and it holds
    verdict = STUDY.decide(changed("control", "X", 3, d=4, lower=4, upper=4), preds)
    assert verdict["instruments"] == "hold"
    control = verdict["power"]["control"]
    assert control["verdict"] == "holds" and control["wrong"] == {key: [["X", 3, "optimal", 4, 4]]}
    assert control["wrong_runs"] == control["wrong_programs"] == 1
    # a lower bound above d at a limit, and a status such as infeasible, are wrong; a limit
    # whose bounds hold d is not
    for fields, wrong in (({"status": "timelimit", "d": None, "lower": 4}, True),
                          ({"status": "infeasible", "d": None, "lower": None}, True),
                          ({"status": "timelimit", "d": None, "lower": 2}, False)):  # fmt: skip
        found = STUDY.decide(changed("control", "Z", 0, **fields), preds)["power"]["control"]
        assert (found["verdict"] == "holds") is wrong, fields
    # a missing record leaves it incomplete
    verdict = STUDY.decide([r for r in rows if r["key"] != key], preds)
    assert verdict["power"]["control"]["verdict"] == "incomplete"
    assert verdict["power"]["control"]["not_tested"] == [key]
    # the program under SCIP_FIX wrong at one seed fails the instruments
    verdict = STUDY.decide(changed("program", "Z", 7, d=4, lower=4, upper=4), preds)
    assert verdict["instruments"] == "fail"
    assert verdict["failures"]["power"] == {key: ["program Z 7: d = 4, expected 3"]}
    # the searches unequal (d_X != d_Z), or one stopped at its limit, fail it
    search = {**row["search"], "X": {**row["search"]["X"], "d": 4, "lower": 4, "upper": 4}}
    verdict = STUDY.decide(_replace(rows, key, search=search), preds)
    assert "search: d_X != d_Z" in verdict["failures"]["power"][key]
    stopped = {**row["search"]["Z"], "status": "timelimit", "d": None, "upper": None,
               "witness_check": None, "lower": 2}  # fmt: skip
    verdict = STUDY.decide(_replace(rows, key, search={**row["search"], "Z": stopped}), preds)
    assert "search Z: status timelimit" in verdict["failures"]["power"][key]
    # a failed job fails it
    verdict = STUDY.decide(_fail(rows, key), preds)
    assert verdict["failures"]["power"] == {key: ["not tested"]}
    assert verdict["power"]["control"]["verdict"] == "incomplete"


def test_decide_checks_the_registered_protocol():
    # records that were not made as registered fail, whatever their values
    preds = _preds()
    rows = _rows(preds)

    def off(records):
        verdict = STUDY.decide(records, preds)
        assert verdict["instruments"] == "fail"
        return verdict["failures"]["protocol"]

    # a toric record of another size than its job's (its own d then passes part (e))
    key = "toric 5x9: program"
    toric = next(r for r in rows if r["key"] == key)
    small = {**toric["result"], "d": 3, "lower": 3, "upper": 3}
    verdict = STUDY.decide(_replace(rows, key, l=3, m=3, result=small), preds)
    assert verdict["toric"]["toric 5x9"] is True and verdict["instruments"] == "fail"
    assert verdict["failures"]["protocol"] == {key: ["l x m = 3x3, registered 5x9"]}
    assert off(_replace(rows, key, A=[[0, 0], [2, 0]])) == {key: ["not the toric code"]}
    # part (a) at one seed instead of five
    key = "enumeration 2x13"
    row = next(r for r in rows if r["key"] == key)
    one = [{**c, "program": {kind: runs[:1] for kind, runs in c["program"].items()}}
           for c in row["rows"]]  # fmt: skip
    assert "#1 program Z: seeds [0]" in off(_replace(rows, key, rows=one))[key]
    # part (b) with no program runs
    key = "fault registered 4x5"
    found = off(_replace(rows, key, program={"Z": [], "X": []}))[key]
    assert found == ["program Z: seeds []", "program X: seeds []"]
    # a program without SCIP_FIX in its settings, as a record, or among part (b)'s runs
    key = "[[30,4,6]]: program"
    entry = next(r for r in rows if r["key"] == key)
    for result in ({**entry["result"], "scip_fix": False, "settings": {}},
                   {**entry["result"], "settings": {}}):  # fmt: skip
        assert off(_replace(rows, key, result=result)) == {key: ["program: not under SCIP_FIX"]}
    key = "fault registered 4x5"
    row = next(r for r in rows if r["key"] == key)
    program = {kind: [{**r, "scip_fix": {}} for r in runs] for kind, runs in row["program"].items()}
    assert len(off(_replace(rows, key, program=program))[key]) == 40
    # a search that did not deepen, or ran from other anchors than its instrument's
    key = f"[[30,4,6]]: {STUDY.ANCHORED}"
    entry = next(r for r in rows if r["key"] == key)
    for result in ({**entry["result"], "deepen": False}, {**entry["result"], "anchors": "all"}):
        assert list(off(_replace(rows, key, result=result))) == [key]
    # part (f)'s control run with SCIP_FIX
    key = "power 5x8 #3"
    row = next(r for r in rows if r["key"] == key)
    control = {kind: [{**r, **_protocol(STUDY.PROGRAM)} for r in runs]
               for kind, runs in row["control"].items()}  # fmt: skip
    found = off(_replace(rows, key, control=control))[key]
    assert len(found) == 40 and found[0] == "control Z 0: not under SCIP's defaults"


def test_part_c_compares_intervals_and_reports_completion_apart():
    preds = _preds()
    rows = _rows(preds)
    code = "trinomial 3x28 #1"
    # the program at its limit with bounds holding the search's d: consistent, and it holds
    stopped = _result("timelimit", None, 6, 9)
    verdict = STUDY.decide(_with_result(rows, f"{code}: program", stopped), preds)
    assert verdict["instruments"] == "hold"
    assert verdict["program_search"]["outcomes"][code] == "consistent"
    assert verdict["program_search"]["completed"][code][STUDY.PROGRAM] is False
    # a search that stalls is consistent too, and fails its completion prediction only
    stall = _result("timelimit", None, 7, None)
    verdict = STUDY.decide(_with_result(rows, f"{code}: {STUDY.ANCHORED}", stall), preds)
    assert verdict["instruments"] == "hold"
    assert verdict["search_completes"][STUDY.ANCHORED] == {
        "verdict": "fails", "stalled": [code], "not_tested": []
    }  # fmt: skip
    assert verdict["search_completes"][STUDY.SEARCH]["verdict"] == "holds"
    # what the docstring states: (c) sees a program fault only where a search completes; an
    # optimum too high passes when both searches stop below it
    high = _with_result(rows, f"{code}: program", _result("optimal", 9, 9, 9))
    for name in (STUDY.SEARCH, STUDY.ANCHORED):
        high = _with_result(high, f"{code}: {name}", _result("timelimit", None, 7, None))
    verdict = STUDY.decide(high, preds)
    assert verdict["program_search"]["outcomes"][code] == "consistent"
    assert verdict["instruments"] == "hold"
    assert {v["verdict"] for v in verdict["search_completes"].values()} == {"fails"}
    # a search that ends with nothing below its bound has not found d: a stall, and its
    # lower bound (64) contradicts the program's 8
    nothing = _result("complete", None, 64, None)
    verdict = STUDY.decide(_with_result(rows, f"{code}: {STUDY.SEARCH}", nothing), preds)
    assert verdict["program_search"]["outcomes"][code] == "disagree"
    assert verdict["search_completes"][STUDY.SEARCH]["verdict"] == "fails"
    # a lower bound at a time-out above another instrument's witness: they disagree
    above = _result("timelimit", None, 9, None)
    verdict = STUDY.decide(_with_result(rows, f"{code}: {STUDY.SEARCH}", above), preds)
    assert verdict["instruments"] == "fail" and verdict["failures"]["program-search"] == {
        code: "disagree"
    }
    # a witness that fails the check, or too few logicals: a method error
    for result in (_result("optimal", 8, 8, 8, logical=False), _result("optimal", 8, 8, 8, k=2)):
        verdict = STUDY.decide(_with_result(rows, f"{code}: program", result), preds)
        assert verdict["failures"]["program-search"] == {code: "method error"}
    # a failed job fails the part; the completion prediction is then incomplete, not failed
    verdict = STUDY.decide(_fail(rows, f"{code}: {STUDY.SEARCH}"), preds)
    assert verdict["failures"]["program-search"] == {code: "not tested"}
    assert verdict["search_completes"][STUDY.SEARCH]["verdict"] == "incomplete"


def test_compare_case_by_case():
    def row(instrument, result, k_linalg=4):
        return {"instrument": instrument, "k_linalg": k_linalg, "result": result}

    exact = [row(STUDY.PROGRAM, _exact(STUDY.PROGRAM, 8, 4)),
             row(STUDY.SEARCH, _exact(STUDY.SEARCH, 8, 4)),
             row(STUDY.ANCHORED, _exact(STUDY.ANCHORED, 8, 4))]  # fmt: skip
    assert STUDY.compare(exact) == "agree"
    assert STUDY.compare(exact[:2]) == "not tested"
    assert STUDY.compare([]) == "not tested"
    assert STUDY.compare(exact[:2] + [{"instrument": STUDY.ANCHORED, "error": "x"}]) == "not tested"
    lower = [exact[0], exact[1], row(STUDY.ANCHORED, _result("complete", 6, 6, 6))]
    assert STUDY.compare(lower) == "disagree"
    # disagreement shows even when an instrument is missing
    assert STUDY.compare(lower[1:]) == "disagree"
    bad = [exact[0], exact[1], row(STUDY.ANCHORED, _result("infeasible", None, None, None))]
    assert STUDY.compare(bad) == "method error"


def test_the_known_answers_are_classified_by_the_registered_rule():
    preds = _preds()
    rows = _rows(preds)
    # a contradiction fails the instruments, the known d having been reproduced before
    entry = "[[72,12,6]]"
    wrong = _exact(STUDY.PROGRAM, 8, 12)
    alone = [r for r in rows if r["key"] != f"{entry}: {STUDY.ANCHORED}"]
    verdict = STUDY.decide(_with_result(alone, f"{entry}: program", wrong), preds)
    assert verdict["known"]["classes"][entry] == "contradicted"
    assert verdict["known"]["contradicted"] == [entry] and verdict["instruments"] == "fail"
    assert verdict["failures"]["known"] == [entry]
    verdict = STUDY.decide(_with_result(rows, f"{entry}: program", wrong), preds)
    assert verdict["known"]["classes"][entry] == "method error"  # the intervals do not meet
    assert verdict["known"]["by_instrument"][entry] == {
        STUDY.PROGRAM: "contradicted", STUDY.ANCHORED: "reproduced"
    }  # fmt: skip
    assert verdict["instruments"] == "fail" and verdict["failures"]["known"] == [entry]
    # the program's optimum too high on [[288,12,18]] with the search stopped below it; and
    # both instruments wrong alike on the gross code: contradicted, and both fail
    big, gross = "[[288,12,18]]", "[[144,12,12]] (the gross code)"
    attack = _with_result(rows, f"{big}: program", _result("optimal", 19, 19, 19, k=12))
    attack = _with_result(
        attack, f"{big}: {STUDY.ANCHORED}", _result("timelimit", None, 16, None, k=12)
    )
    verdict = STUDY.decide(attack, preds)
    assert verdict["known"]["classes"][big] == "contradicted"
    assert verdict["failures"]["known"] == [big] and verdict["instruments"] == "fail"
    alike = _with_result(rows, f"{gross}: program", _result("optimal", 13, 13, 13, k=12))
    alike = _with_result(alike, f"{gross}: {STUDY.ANCHORED}", _result("complete", 13, 13, 13, k=12))
    verdict = STUDY.decide(alike, preds)
    assert verdict["known"]["classes"][gross] == "contradicted"
    assert verdict["instruments"] == "fail"
    # the stalled codes are judged against the program's d of the first run, with three
    # instruments; a search at its limit with a lower bound, and the program exact, reproduce
    name = "stalled 6x18 #2"
    verdict = STUDY.decide(
        _with_result(rows, f"{name}: {STUDY.SEARCH}", _result("timelimit", None, 5, None, k=8)),
        preds,
    )
    assert verdict["known"]["classes"][name] == "reproduced" and verdict["instruments"] == "hold"
    # a record whose code differs from the registration fails, and is reported
    verdict = STUDY.decide(_replace(rows, f"{name}: program", codes_sha256="0" * 64), preds)
    assert verdict["registration_mismatches"] == [f"{name}: program"]
    assert verdict["instruments"] == "fail"
    # a failed job here leaves the entry to the other instruments
    verdict = STUDY.decide(_fail(rows, "[[30,4,6]]: program"), preds)
    assert verdict["known"]["classes"]["[[30,4,6]]"] == "reproduced"
    assert verdict["known"]["by_instrument"]["[[30,4,6]]"][STUDY.PROGRAM] == "not tested"


def test_execute_refuses_a_cut_off_last_record(tmp_path, monkeypatch):
    # a study process killed while appending a record leaves an incomplete last line, which no
    # observation can cite; execute names it rather than append the next record to it
    path = tmp_path / "records.jsonl"
    monkeypatch.setattr(STUDY, "jobs", lambda: [{"key": "a"}])
    path.write_text('{"key": "a"}\n')
    STUDY.execute(path, 1)  # every job has a record: nothing runs
    assert path.read_text() == '{"key": "a"}\n'
    path.write_text('{"key": "a"}\n{"key": "b", "rows": [1, 2')
    with pytest.raises(STUDY.StudyError, match="incomplete line at byte 13 "):
        STUDY.execute(path, 1)
    assert path.read_text().endswith("[1, 2")


def test_classify_is_the_registered_rule_for_two_instruments():
    # the general rule gives examples/qec-distance's classify on every pair of records that
    # its own tests use
    first = STUDY.first

    def program(status, lower, upper, logical=True, k=4):
        r = _result(status, upper if status == "optimal" else None, lower, upper, k=k,
                    logical=logical)  # fmt: skip
        return {**r, "k_linalg": 4}

    def search(status, d, lower, upper, logical=True, k=4):
        return {**_result(status, d, lower, upper, k=k, logical=logical), "k_linalg": 4}

    programs = [None, program("optimal", 12, 12), program("optimal", 10, 10),
                program("timelimit", 9, 14), program("timelimit", 12, 12),
                program("timelimit", 9, None), program("memlimit", 9, 11),
                program("timelimit", 13, 20), program("timelimit", 9, 11, logical=False),
                program("optimal", 12, 12, k=2), program("infeasible", None, None),
                {"error": "killed"}]  # fmt: skip
    searches = [None, search("complete", 12, 12, 12), search("complete", 10, 10, 10),
                search("timelimit", None, None, 12), search("timelimit", None, 11, 13),
                search("timelimit", None, 13, None), search("complete", None, 64, None),
                search("complete", 12, 12, 12, logical=False), {"error": "killed"}]  # fmt: skip
    for p in programs:
        for s in searches:
            rows = []
            for instrument, r in ((STUDY.PROGRAM, p), (STUDY.ANCHORED, s)):
                if r is not None and "error" not in r:
                    rows.append({"instrument": instrument, "k_linalg": 4, "result": r})
            for d in (10, 12, 14):
                assert STUDY.classify(rows, d) == first.classify(p, s, d), (p, s, d)
