"""Exact distances of bivariate bicycle codes (examples/qec-distance/distance.py). Random codes
are drawn only at development sizes: of no published torus type, and none of the sizes
registered for examples/qec-distance/study.py or examples/qec-distance-2/study.py
(tests/test_qec_distance_2.py checks the second). The toric code, whose distance min(l, m) is a
classical theorem, is used at any size, and the codes of examples/qec-distance-2/fault_cases.json
and the two codes the registered search stalled on are known answers."""

import importlib.util
import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))
sys.path.insert(0, str(ROOT / "examples" / "qec-distance"))

import bb  # noqa: E402
import distance as D  # noqa: E402

SIZES = [(2, 2), (2, 3), (2, 4), (3, 3), (2, 5), (2, 6), (4, 4)]
TORIC = [[(0, 0), (1, 0)], [(0, 0), (0, 1)]]
CASES = ROOT / "examples" / "qec-distance-2" / "fault_cases.json"
FAULT = [(1, 2), (3, 2)], [(2, 3), (3, 3)], 4, 5  # the registered test's failing code, d_X = 2
# the codes on which the registered search stalled (study.py, part 1 (c), 6x18 #1 and #2):
# A, B, k and d
STALLED = [
    ([(2, 0), (0, 15), (0, 8)], [(0, 0), (4, 0), (5, 0)], 4, 4),
    ([(1, 0), (0, 14), (0, 15)], [(0, 6), (4, 0), (2, 0)], 8, 6),
]
needs_cc = pytest.mark.skipif(shutil.which("cc") is None, reason="the search needs cc")


def codes(seed, count=12):
    """Random codes with k > 0 at the test sizes: two to four terms per polynomial."""
    rng = random.Random(seed)
    for ell, m in SIZES:
        found = 0
        while found < count:
            A = [(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.randint(2, 4))]
            B = [(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.randint(2, 4))]
            k = bb.k_linalg(A, B, ell, m)
            if k and ell * m + k // 2 <= D.BRUTE_CAP:
                found += 1
                yield A, B, ell, m, k


def bits(row) -> int:
    return sum(1 << int(i) for i in np.flatnonzero(row))


def _study():
    path = ROOT / "examples" / "qec-distance" / "study.py"
    spec = importlib.util.spec_from_file_location("qec_distance_study", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_test_sizes_are_neither_published_nor_registered():
    study = _study()
    registered = study.PUBLISHED_SIZES + study.METHOD_SIZES + study.SEARCH_SIZES
    held_out = {D.torus_type(ell, m) for ell, m in registered}
    assert not held_out & {D.torus_type(ell, m) for ell, m in SIZES}
    # part 1 (c): no published order (so no published n) and no method type
    orders = {ell * m for ell, m in study.PUBLISHED_SIZES}
    method = {D.torus_type(ell, m) for ell, m in study.METHOD_SIZES}
    assert all(ell * m not in orders for ell, m in study.SEARCH_SIZES)
    assert not method & {D.torus_type(ell, m) for ell, m in study.SEARCH_SIZES}
    assert D.torus_type(3, 5) == D.torus_type(1, 15) == D.torus_type(5, 3) == (3, 5)
    assert D.torus_type(9, 6) == D.torus_type(18, 3) != D.torus_type(6, 6)


def test_the_check_matrices_are_bbs():
    for A, B, ell, m, k in codes(1, count=4):
        hx, hz = D.check_matrices(A, B, ell, m)
        bx, bz = D._bit_rows(A, B, ell, m)
        assert [bits(r) for r in hx] == bx and [bits(r) for r in hz] == bz
        assert hx.dtype == np.uint8 and hx.shape == hz.shape == (ell * m, 2 * ell * m)
        assert 2 * ell * m - D.rank(hx) - D.rank(hz) == k
        assert not ((hx.astype(int) @ hz.T.astype(int)) % 2).any()


def test_inversion_and_swap_carry_h_x_to_h_z():
    # H_Z = P H_X Phi, the identity behind d_X = d_Z, checked entry by entry
    for A, B, ell, m, _ in codes(2, count=4):
        hx, hz = D.check_matrices(A, B, ell, m)
        P, Phi = D.inversion_swap(ell, m)
        assert np.array_equal((P.astype(int) @ hx @ Phi) % 2, hz)
        assert np.array_equal(Phi @ Phi, np.eye(2 * ell * m, dtype=np.uint8))


def test_the_logical_bases_have_k_independent_logicals():
    for A, B, ell, m, k in codes(3, count=4):
        bx, bz = D._bit_rows(A, B, ell, m)
        LX = [bits(r) for r in D.logical_basis(A, B, ell, m, "X")]
        LZ = [bits(r) for r in D.logical_basis(A, B, ell, m, "Z")]
        assert len(LX) == len(LZ) == k
        assert all((r & v).bit_count() % 2 == 0 for v in LX for r in bz)
        assert all((r & v).bit_count() % 2 == 0 for v in LZ for r in bx)
        assert bb.rank_gf2(bx + LX) == bb.rank_gf2(bx) + k
        assert bb.rank_gf2(bz + LZ) == bb.rank_gf2(bz) + k
        # the pairing between the two kinds is nondegenerate
        pairing = [sum(((x & z).bit_count() & 1) << j for j, z in enumerate(LZ)) for x in LX]
        assert bb.rank_gf2(pairing) == k


def test_toric_codes_have_distance_min_l_m():
    pytest.importorskip("pyscipopt")
    for ell, m in [(2, 5), (3, 3), (4, 4), (3, 6), (4, 6), (5, 6), (6, 8)]:
        r = D.distance_ilp(*TORIC, ell, m, "Z", time_limit=60)
        assert r["k"] == 2 and r["status"] == "optimal" and r["d"] == min(ell, m), (ell, m)
        assert D.verify_witness(*TORIC, ell, m, "Z", r["witness"])["logical"]
        if ell * m + 1 <= D.BRUTE_CAP:
            assert D.distance_brute(*TORIC, ell, m, "Z")["d"] == min(ell, m)


def test_the_program_agrees_with_enumeration_and_d_x_equals_d_z():
    pytest.importorskip("pyscipopt")
    seen = set()
    for A, B, ell, m, k in codes(4):
        z = D.distance_ilp(A, B, ell, m, "Z", time_limit=60)
        x = D.distance_ilp(A, B, ell, m, "X", time_limit=60)
        bz, bx = D.distance_brute(A, B, ell, m, "Z"), D.distance_brute(A, B, ell, m, "X")
        assert z["status"] == x["status"] == "optimal" and z["k"] == x["k"] == k
        assert z["d"] == bz["d"] == x["d"] == bx["d"], (A, B, ell, m)
        assert z["lower"] == z["upper"] == z["d"] == len(z["witness"])
        assert D.verify_witness(A, B, ell, m, "Z", z["witness"])["logical"]
        assert D.verify_witness(A, B, ell, m, "X", x["witness"])["logical"]
        assert D.verify_witness(A, B, ell, m, "Z", bz["witness"])["logical"]
        assert len(bz["witness"]) == bz["d"]
        seen.add(z["d"])
    assert len(seen) >= 3  # the codes are not all alike


def test_the_translation_row_keeps_the_optimum():
    pytest.importorskip("pyscipopt")
    for A, B, ell, m, _ in codes(5, count=3):
        with_row = D.distance_ilp(A, B, ell, m, "Z", time_limit=60)
        without = D.distance_ilp(A, B, ell, m, "Z", time_limit=60, translation=False)
        assert with_row["d"] == without["d"]


def test_witness_check_rejects_stabilizers_and_non_kernel_vectors():
    A, B, ell, m = [(0, 0), (1, 0), (0, 1)], [(0, 0), (0, 2), (1, 1)], 2, 4
    hx, hz = D.check_matrices(A, B, ell, m)
    stabilizer = np.flatnonzero(hz[0]).tolist()
    r = D.verify_witness(A, B, ell, m, "Z", stabilizer)
    assert r["in_kernel"] and not r["nontrivial"] and not r["logical"]
    r = D.verify_witness(A, B, ell, m, "Z", [0])
    assert not r["in_kernel"] and not r["logical"]
    assert not D.verify_witness(A, B, ell, m, "Z", [0, 0])["valid_support"]


def test_a_code_with_no_logicals_is_reported_cleanly():
    A, B, ell, m = [(0, 0)], [(1, 0), (0, 1)], 3, 3  # A = 1 is a unit: k = 0
    assert bb.k_linalg(A, B, ell, m) == 0
    assert D.logical_basis(A, B, ell, m, "X").shape == (0, 18)
    assert D.distance_brute(A, B, ell, m, "Z")["d"] is None
    pytest.importorskip("pyscipopt")
    r = D.distance_ilp(A, B, ell, m, "Z", time_limit=60)
    assert r["status"] == "no_logicals" and r["k"] == 0 and r["d"] is None
    assert r["witness"] is None


@needs_cc
def test_the_search_agrees_with_enumeration():
    for A, B, ell, m, k in codes(4, count=6):
        lm = ell * m
        for kind in D.KINDS:
            brute = D.distance_brute(A, B, ell, m, kind)["d"]
            every = D.distance_search(A, B, ell, m, kind)
            anchored = D.distance_search(A, B, ell, m, kind, anchors=(0, lm))
            single = D.distance_search(A, B, ell, m, kind, anchors=(0, lm), deepen=False)
            for r in (every, anchored, single):
                assert r["status"] == "complete" and r["k"] == k
                assert r["d"] == r["lower"] == brute == len(r["witness"]), (A, B, ell, m)
                assert D.verify_witness(A, B, ell, m, kind, r["witness"])["logical"]
            # the passes below d ended without a logical, and the next found one of weight d
            assert [p["bound"] for p in every["passes"]] == list(range(2, brute + 1))
            assert [p["bound"] for p in anchored["passes"]] == list(range(2, brute + 1))
            assert single["passes"] == [] and single["deepen"] is False
            # with the bound at d, it proves that nothing lighter exists
            for deepen in (True, False):
                below = D.distance_search(A, B, ell, m, kind, bound=brute, deepen=deepen)
                assert below["status"] == "complete" and below["d"] is None
                assert below["lower"] == brute and below["witness"] is None
                assert below["passes"][-1]["bound"] == brute


@needs_cc
def test_the_search_on_toric_codes():
    for ell, m in [(2, 5), (3, 6), (5, 6), (6, 8), (10, 10)]:
        for deepen in (True, False):
            r = D.distance_search(*TORIC, ell, m, "Z", deepen=deepen)
            assert r["status"] == "complete" and r["k"] == 2 and r["d"] == min(ell, m), (ell, m)
            assert D.verify_witness(*TORIC, ell, m, "Z", r["witness"])["logical"]
    A, B = [(0, 0)], [(1, 0), (0, 1)]  # k = 0
    assert D.distance_search(A, B, 3, 3)["status"] == "no_logicals"


@needs_cc
def test_the_search_finds_the_distances_it_stalled_on():
    # part 1 (c) of study.py, 6x18 #1 and #2: the single pass from bound 64 found no logical in
    # 30 minutes, from every qubit or from (0, lm); the program found d = 4 and 6 at once
    for A, B, k, d in STALLED:
        for kind in D.KINDS:
            for anchors in (None, (0, 6 * 18)):
                r = D.distance_search(A, B, 6, 18, kind, anchors=anchors, time_limit=60)
                assert r["status"] == "complete" and r["k"] == k and r["d"] == d
                assert [p["bound"] for p in r["passes"]] == list(range(2, d + 1))
                assert D.verify_witness(A, B, 6, 18, kind, r["witness"])["logical"]


def test_the_program_on_the_codes_the_search_stalled_on():
    pytest.importorskip("pyscipopt")
    for A, B, k, d in STALLED:
        r = D.distance_ilp(A, B, 6, 18, "Z", time_limit=60)
        assert r["status"] == "optimal" and r["k"] == k and r["d"] == d
        assert D.verify_witness(A, B, 6, 18, "Z", r["witness"])["logical"]


def test_the_program_is_right_where_scips_defaults_were_wrong():
    # with SCIP_FIX (the default) the program gives the right d on the programs where SCIP
    # 10.0's defaults gave a wrong optimum (distance_ilp's docstring): the registered test's 4x5
    # code at seeds 0 to 7, and each program of fault_cases.json at up to 3 of its failing seeds
    pytest.importorskip("pyscipopt")
    for seed in range(8):
        r = D.distance_ilp(*FAULT, "X", time_limit=60, seed=seed)
        assert r["status"] == "optimal" and r["d"] == r["lower"] == 2, seed
        assert D.verify_witness(*FAULT, "X", r["witness"])["logical"]
    cases = json.loads(CASES.read_text())["codes"]
    assert len(cases) == 38 and sum(bool(s) for c in cases for s in c["wrong"].values()) == 49
    for c in cases:
        for kind, seeds in c["wrong"].items():
            for seed in seeds[:3]:
                r = D.distance_ilp(c["A"], c["B"], c["l"], c["m"], kind, time_limit=60, seed=seed)
                assert r["status"] == "optimal" and r["d"] == c["d"], (c["id"], kind, seed)
                assert r["k"] == c["k"]


def test_scips_defaults_were_wrong_on_the_4x5_code():
    # the test above can see the fault: without SCIP_FIX, the SCIP that the fault was found in
    # gives d_X = 3 at some seeds
    pytest.importorskip("pyscipopt")
    if D.scip_version() != "SCIP 10.0 (pyscipopt 6.3.0)":
        pytest.skip("the fault was found in SCIP 10.0 through pyscipopt 6.3.0")
    found = [D.distance_ilp(*FAULT, "X", 60, seed=s, scip_fix=False)["d"] for s in range(8)]
    assert 3 in found and set(found) == {2, 3}


@needs_cc
def test_the_search_reports_a_lower_bound_at_its_time_limit():
    # the toric code at 20x20 (d = 20) takes the search far more than a second: the passes that
    # ended before the limit give d >= the last one's bound
    r = D.distance_search(*TORIC, 20, 20, "Z", time_limit=1)
    assert r["status"] == "timelimit" and r["d"] is None and r["witness"] is None
    assert 2 <= r["lower"] < 20 and r["nodes"] is None
    assert [p["bound"] for p in r["passes"]] == list(range(2, r["lower"] + 1))
    # the single pass, stopped, has no lower bound
    single = D.distance_search(*TORIC, 20, 20, "Z", time_limit=1, deepen=False)
    assert single["status"] == "timelimit" and single["d"] is None and single["lower"] is None


def test_the_search_logical_basis_is_independent_and_complete():
    for A, B, ell, m, k in codes(3, count=4):
        bx, bz = D._bit_rows(A, B, ell, m)
        LX = D._logicals_bits(bz, bx, 2 * ell * m)
        assert len(LX) == k
        assert all((r & v).bit_count() % 2 == 0 for v in LX for r in bz)
        assert bb.rank_gf2(bx + LX) == bb.rank_gf2(bx) + k


def test_enumeration_refuses_beyond_its_cap():
    with pytest.raises(ValueError):
        D.distance_brute(*TORIC, 5, 6, "Z")  # dim ker H_X = 31


def test_the_program_records_its_solver_and_settings():
    pytest.importorskip("pyscipopt")
    r = D.distance_ilp(*TORIC, 3, 4, "X", time_limit=30, seed=3)
    assert r["solver"].startswith("SCIP ") and r["seed"] == 3
    assert r["parameters"]["limits/time"] == 30
    assert r["parameters"]["limits/memory"] == D.MEMORY_MB
    assert r["parameters"]["randomization/randomseedshift"] == 3
    assert r["nodes"] >= 1 and r["seconds"] >= 0
    # the settings against SCIP's fault are on by default, and recorded
    assert r["scip_fix"] is True
    assert D.SCIP_FIX == {"constraints/xor/maxprerounds": 0, "separating/rapidlearning/freq": -1}
    for name, value in D.SCIP_FIX.items():
        assert r["settings"][name] == r["parameters"][name] == value
    off = D.distance_ilp(*TORIC, 3, 4, "X", time_limit=30, scip_fix=False)
    assert off["scip_fix"] is False and off["d"] == r["d"] == 3
    assert not set(D.SCIP_FIX) & (set(off["settings"]) | set(off["parameters"]))


def _row(status, lower, upper, logical=True, k=4, k_linalg=4):
    check = {"logical": logical} if upper is not None else None
    return {"status": status, "published_d": 12, "lower": lower, "upper": upper,
            "witness_check": check, "k": k, "k_linalg": k_linalg}  # fmt: skip


def _search_row(status, d, lower, upper, logical=True, k=4, k_linalg=4):
    check = {"logical": logical} if upper is not None else None
    return {"status": status, "d": d, "published_d": 12, "lower": lower, "upper": upper,
            "witness_check": check, "k": k, "k_linalg": k_linalg}  # fmt: skip


def test_the_registered_classification():
    # synthetic records (no computation): the rule in study.py, case by case, against the
    # registered d (12); first the program alone
    def classify(row, d):
        return _study().classify(row, None, d)

    assert classify(_row("optimal", 12, 12), 12) == "reproduced"
    assert classify(_row("optimal", 10, 10), 12) == "contradicted"
    assert classify(_row("optimal", 14, 14), 12) == "contradicted"
    assert classify(_row("timelimit", 9, 14), 12) == "consistent but unresolved"
    # a lower bound that meets a checked witness settles d, at a limit too
    assert classify(_row("timelimit", 12, 12), 12) == "reproduced"
    assert classify(_row("timelimit", 9, None), 12) == "consistent but unresolved"
    assert classify(_row("memlimit", 9, 11), 12) == "contradicted"
    assert classify(_row("timelimit", 13, 20), 12) == "contradicted"
    # the registered d, not the record's published_d, is what an entry is judged against
    assert classify(_row("optimal", 12, 12), 10) == "contradicted"
    # a broken run says nothing about d: a failed witness, a status other than optimal or a
    # limit, too few logicals, or an optimal end without a witness
    assert classify(_row("timelimit", 9, 11, logical=False), 12) == "method error"
    assert classify(_row("optimal", 12, 12, logical=False), 12) == "method error"
    assert classify(_row("optimal", 10, 10, logical=False), 12) == "method error"
    for status in ("infeasible", "no_logicals", "userinterrupt", "nodelimit", "unknown"):
        assert classify(_row(status, None, None), 12) == "method error", status
    assert classify(_row("optimal", 12, 12, k=2), 12) == "method error"
    assert classify(_row("optimal", None, None), 12) == "method error"
    assert classify({"test": "published", "key": "x", "error": "killed"}, 12) == "not tested"


def test_the_registered_classification_with_both_instruments():
    # synthetic records (no computation): the program and the search together
    classify = _study().classify
    found = _search_row("complete", 12, 12, 12)
    assert classify(None, found, 12) == "reproduced"
    assert classify(None, _search_row("complete", 10, 10, 10), 12) == "contradicted"
    # the search at its limit has no lower bound; its witness is an upper bound
    stopped = _search_row("timelimit", None, None, 12)
    assert classify(None, stopped, 12) == "consistent but unresolved"
    assert classify(None, _search_row("timelimit", None, None, 11), 12) == "contradicted"
    # the program's lower bound and the search's witness together settle d
    assert classify(_row("timelimit", 12, 20), stopped, 12) == "reproduced"
    assert classify(_row("timelimit", 9, 20), stopped, 12) == "consistent but unresolved"
    assert classify(_row("timelimit", 9, 20), found, 12) == "reproduced"
    assert classify(_row("optimal", 12, 12), found, 12) == "reproduced"
    # intervals that do not meet are a method error, whatever the registered d
    assert classify(_row("optimal", 12, 12), _search_row("complete", 10, 10, 10), 12) == (
        "method error"
    )
    assert classify(_row("timelimit", 13, 20), stopped, 12) == "method error"
    # a broken instrument is a method error even when the other is sound
    assert classify(_row("optimal", 12, 12), _search_row("complete", 12, 12, 12, k=2), 12) == (
        "method error"
    )
    bad = _search_row("complete", 12, 12, 12, logical=False)
    assert classify(_row("optimal", 12, 12), bad, 12) == "method error"
    assert classify(None, _search_row("complete", 12, 12, None), 12) == "method error"
    # a search that completes with nothing below its bound says d >= the bound
    assert classify(None, _search_row("complete", None, 64, None), 12) == "contradicted"
    # one instrument failed: the other decides
    failed = {"test": "published-search", "key": "x (search)", "name": "x", "error": "killed"}
    assert classify(_row("optimal", 12, 12), failed, 12) == "reproduced"
    assert classify(None, failed, 12) == "not tested"


def _synthetic_rows(study, preds):
    """A full, passing set of records (no computation), one per job."""
    hashes = {}
    for p in preds[:4]:
        hashes.update(p.get("codes_sha256", {}))
    registered = {p["name"]: p for p in preds[4:]}
    rows = []
    for j in study.jobs():
        key = j["key"]
        if j["test"] == "published":
            p = registered[key]
            rows.append({**_row("optimal", p["predicted_d"], p["predicted_d"], k=p["k"],
                                k_linalg=p["k"]), "test": "published", "key": key, "name": key,
                         "published_k": p["k"], "published_d": p["predicted_d"],
                         "codes_sha256": p["codes_sha256"]})  # fmt: skip
        elif j["test"] == "published-search":
            p = registered[j["name"]]
            d = p["predicted_d"]
            rows.append({**_search_row("complete", d, d, d, k=p["k"], k_linalg=p["k"]),
                         "test": "published-search", "key": key, "name": j["name"],
                         "published_k": p["k"], "published_d": d,
                         "codes_sha256": p["codes_sha256"]})  # fmt: skip
        elif j["test"] == "toric":
            d = min(j["l"], j["m"])
            rows.append({**_row("optimal", d, d, k=2, k_linalg=2), "test": "toric", "key": key,
                         "expected_d": d, "d": d})  # fmt: skip
        elif j["test"] == "random":
            rows.append({"test": "random", "key": key, "codes": study.PER_SIZE,
                         "agree": study.PER_SIZE, "codes_sha256": hashes[key]})  # fmt: skip
        else:
            exact = {"status": "optimal", "d": 12, "lower": 12, "upper": 12, "k": 4,
                     "witness_check": {"logical": True}}  # fmt: skip
            rows.append({"test": "search", "key": key, "k_linalg": 4, "codes_sha256": hashes[key],
                         "program": exact, "search": {**exact, "status": "complete"},
                         "search_anchored": {**exact, "status": "complete"}})  # fmt: skip
    return rows


def test_decide_reports_failed_jobs_as_not_tested():
    # synthetic records (no computation): a failed job is a row with only its spec and an error
    study = _study()
    preds = study.predictions()
    rows = _synthetic_rows(study, preds)
    verdict = study.decide(rows, preds)
    assert verdict["method"] == "holds" and not verdict["missing"]
    assert verdict["counts"]["reproduced"] == 12 and not verdict["registration_mismatches"]
    failed = {"[[288,12,18]]", "[[288,12,18]] (search)", "[[144,12,12]] (the gross code)",
              "toric 16x17", "random 3x4", "search 6x18 #1"}  # fmt: skip
    rows = [{**j, "error": "Killed"} if j["key"] in failed else r
            for j, r in zip(study.jobs(), rows, strict=True)]  # fmt: skip
    verdict = study.decide(rows, preds)
    assert verdict["rediscovery"]["[[288,12,18]]"] == "not tested"
    # the gross code's program failed, and its search alone reproduces d
    assert verdict["rediscovery"]["[[144,12,12]] (the gross code)"] == "reproduced"
    assert verdict["rediscovery_by_instrument"]["[[144,12,12]] (the gross code)"] == {
        "program": "not tested",
        "search": "reproduced",
    }
    assert verdict["counts"]["not tested"] == 1 and verdict["counts"]["reproduced"] == 11
    assert verdict["method"] == "fails" and set(verdict["method_failures"]) == failed - {
        "[[288,12,18]]",
        "[[288,12,18]] (search)",
        "[[144,12,12]] (the gross code)",
    }
    assert verdict["search"]["search 6x18 #1"] == "not tested" and not verdict["missing"]


def test_decide_judges_against_the_registration():
    # synthetic records (no computation): a record whose codes.json or d changed after
    # registration is judged against the registered d, and reported
    study = _study()
    preds = study.predictions()
    rows = _synthetic_rows(study, preds)
    i = next(i for i, r in enumerate(rows) if r["key"] == "[[144,12,12]] (the gross code)")
    rows[i] = {**rows[i], "codes_sha256": "0" * 64, "published_d": 14, "upper": 14, "lower": 14}
    j = next(j for j, r in enumerate(rows) if r["key"] == "[[144,12,12]] (the gross code) (search)")
    rows[j] = {**rows[j], "codes_sha256": "0" * 64, "published_d": 14, "d": 14, "upper": 14,
               "lower": 14}  # fmt: skip
    verdict = study.decide(rows, preds)
    assert verdict["rediscovery"]["[[144,12,12]] (the gross code)"] == "contradicted"
    assert verdict["registration_mismatches"] == [
        "[[144,12,12]] (the gross code)",
        "[[144,12,12]] (the gross code) (search)",
    ]
    # a published entry whose program found too few logicals is a method error, and fails
    rows = _synthetic_rows(study, preds)
    rows[0] = {**rows[0], "k": rows[0]["k"] - 2}
    verdict = study.decide(rows, preds)
    assert verdict["method_errors"] == [rows[0]["key"]] and verdict["method"] == "fails"


def test_the_registered_search_comparison():
    # synthetic records (no computation): part 1 (c)'s rule, case by case
    outcome = _study().search_outcome

    def result(status, d, lower, upper, logical=True, k=4):
        check = {"logical": logical} if upper is not None else None
        return {"status": status, "d": d, "lower": lower, "upper": upper, "k": k,
                "witness_check": check}  # fmt: skip

    def row(program, search, anchored=None):
        anchored = search if anchored is None else anchored
        return {"k_linalg": 4, "program": program, "search": search, "search_anchored": anchored}

    exact = result("optimal", 14, 14, 14)
    found = result("complete", 14, 14, 14)
    assert outcome(row(exact, found)) == "agree"
    assert outcome(row(result("timelimit", None, 12, 16), found)) == "consistent"
    assert outcome(row(exact, result("timelimit", None, None, 16))) == "consistent"
    both = row(result("timelimit", None, 12, 20), result("timelimit", None, None, 18))
    assert outcome(both) == "consistent"
    assert outcome(row(result("optimal", 12, 12, 12), found)) == "disagree"
    assert outcome(row(result("timelimit", None, 15, 20), found)) == "disagree"
    assert outcome(row(exact, result("complete", None, 64, None))) == "disagree"
    assert outcome(row(result("infeasible", None, None, None), found)) == "method error"
    assert outcome(row(exact, result("complete", 14, 14, 14, logical=False))) == "method error"
    assert outcome(row(result("optimal", 14, 14, 14, k=2), found)) == "method error"
    assert outcome({"test": "search", "key": "x", "error": "killed"}) == "not tested"
    # the search from (0, lm) must agree as well
    assert outcome(row(exact, found, result("complete", 12, 12, 12))) == "disagree"
    assert outcome(row(exact, found, result("timelimit", None, None, 16))) == "agree"
    assert outcome(row(exact, found, result("complete", 14, 14, 14, k=2))) == "method error"


def test_the_study_runs_the_largest_entries_first_and_registers_one_prediction_each():
    study = _study()
    jobs = study.jobs()
    published = [j for j in jobs if j["test"] in ("published", "published-search")]
    assert jobs[: len(published)] == published and len(published) == 24
    n = {c["name"]: c["n"] for c in study.codes()}
    assert [n[j["key"]] for j in published[::2]] == sorted(n.values(), reverse=True)
    assert [j["name"] for j in published[1::2]] == [j["key"] for j in published[::2]]
    assert len({j["key"] for j in jobs}) == len(jobs)
    preds = study.predictions()
    assert len(preds) == 4 + 12
    assert [p["predicted_d"] for p in preds[4:]] == [c["d"] for c in study.codes()]
    assert len([j for j in jobs if j["test"] == "search"]) == 9
    verdict = study.decide([], preds)
    assert verdict["method"] == "incomplete" and len(verdict["missing"]) == len(jobs)
