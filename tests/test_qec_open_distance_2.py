"""examples/qec-open-distance-2: the packing search against enumeration and the unpacked search at
development sizes, the study's fresh codes, and its rules on synthetic records. Nothing here
computes a distance of a registered A1 or A2 code, or of [[756,16]]."""

import importlib.util
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("qec_open_study_2", ROOT / "examples" / "qec-open-distance-2" / "study.py")
pack, bb, D = S.pack, S.bb, S.distance
DEVELOPMENT = [(3, 4), (3, 7), (4, 6), (2, 9), (3, 6), (3, 8)]


def _dev_codes(count, seed):
    rng, out = random.Random(seed), []
    while len(out) < count:
        ell, m = rng.choice(DEVELOPMENT)
        A = sorted({(rng.randrange(ell), rng.randrange(m)) for _ in range(3)})
        B = sorted({(rng.randrange(ell), rng.randrange(m)) for _ in range(3)})
        if len(A) < 3 or len(B) < 3:
            continue
        k = bb.k_linalg(A, B, ell, m)
        if k and ell * m + k // 2 <= D.BRUTE_CAP:
            out.append((A, B, ell, m))
    return out


@pytest.mark.parametrize("A,B,ell,m", _dev_codes(8, 99))
def test_packing_search_matches_enumeration(A, B, ell, m):
    want = pack.brute(A, B, ell, m)
    for anchors in ((0, ell * m), None):
        r = pack.search(A, B, ell, m, "Z", anchors=anchors, parts=3, depth=3, workers=2,
                        time_limit=120)  # fmt: skip
        assert r["status"] == "complete" and r["d"] == want
        assert r["search_c"] == "search_pack.c"


def test_packing_search_on_the_gross_code_and_its_cut():
    A, B = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]
    p = pack.search(A, B, 12, 6, "Z", anchors=(0, 72), parts=4, depth=5, workers=2,
                    time_limit=300)  # fmt: skip
    q = pack.reference(A, B, 12, 6, "Z", anchors=(0, 72), parts=4, depth=5, workers=2,
                       time_limit=300)  # fmt: skip
    assert p["d"] == q["d"] == 12 and q["search_c"] == "search_parts.c"
    nodes = [sum(x["nodes"] for x in r["passes"][-2]["parts"]) for r in (p, q)]
    assert nodes[0] < nodes[1]  # the cut prunes


def test_reference_is_study_1s_search():
    assert pack.plain.SEARCH_C.name == "search_parts.c"
    assert pack.packed.SEARCH_C.name == "search_pack.c"
    assert pack.packed is not pack.plain


def test_fresh_codes():
    a1, a2 = S.a1_codes(), S.a2_codes()
    assert len(a1) == len(S.A1_SIZES) * S.A1_PER_SIZE
    assert len(a2) == len(S.A2_SIZES) * S.A2_PER_SIZE
    assert a1 == S.a1_codes() and a2 == S.a2_codes()  # repeatable
    for c in a1:
        assert c["k"] == bb.k_linalg(S._poly(c["A"]), S._poly(c["B"]), c["l"], c["m"]) > 0
        assert c["l"] * c["m"] + c["k"] // 2 <= D.BRUTE_CAP
    for c in a2:
        assert c["k"] > 0 and c["A"][0][1] == 0 and c["B"][0][0] == 0
        assert all(x != 0 for x in (c["A"][0][0], c["A"][1][1], c["A"][2][1], c["B"][0][1],
                                    c["B"][1][0], c["B"][2][0]))  # fmt: skip
        assert S.generates(S._poly(c["A"]), S._poly(c["B"]), c["l"], c["m"])
    assert not S.generates([(7, 0), (0, 10), (0, 0)], [(0, 0), (7, 0), (2, 0)], 9, 12)
    dev = {D.torus_type(*t) for t in DEVELOPMENT + [(6, 3), (6, 9), (5, 12), (4, 15)]}
    for ell, m in S.A1_SIZES + S.A2_SIZES:
        assert D.torus_type(ell, m) not in dev


def _run(d=None, status="complete", lower=None, upper=None, c="search_pack.c"):
    sha = S.code_hashes()["search_pack_c" if c == "search_pack.c" else "search_parts_c"]
    return {"status": status, "d": d, "lower": d if lower is None else lower,
            "upper": d if upper is None else upper, "seconds": 1.0, "search_c": c,
            "search_c_sha256": sha}  # fmt: skip


def _cpass(b, found=False, least=None, witness=None):
    return {"job": "C_pass", "bound": b, "found": found, "least": least, "witness": witness,
            "seconds": 1.0, "settings": S.SETTINGS,
            "search_c_sha256": S.code_hashes()["search_pack_c"]}  # fmt: skip


def _rows(c_last=29):
    rows = []
    for c in S.a1_codes():
        rows.append({"job": "A1", "key": c["key"], "runs": {"brute": 4, "pack_lm": _run(4),
                                                             "pack_all": _run(4)}})  # fmt: skip
    for c in S.a2_codes():
        rows.append(
            {
                "job": "A2",
                "key": c["key"],
                "runs": {"pack": _run(8), "plain": _run(8, c="search_parts.c")},
            }
        )
    for name, code in S.KNOWN.items():
        r = _run(None, "bound", 24, None) if name == "360" else _run(code["d"])
        rows.append({"job": "B", "key": f"B:{name}", "code": name, **r})
    rows += [_cpass(b) for b in range(2, c_last + 1)]
    rows.append(
        {
            "job": "C_end",
            "status": "timelimit",
            "budget": S.C_BUDGET,
            "settings": S.SETTINGS,
            "search_c_sha256": S.code_hashes()["search_pack_c"],
        }
    )
    return rows


def test_decide_hold_and_failures():
    out = S.decide(_rows(), [])
    assert out["verdict"] == "hold", out
    assert out["C"]["d_at_least"] == 30
    short = _rows(27)
    assert S.decide(short, [])["C2"] == "fail" and S.decide(short, [])["verdict"] == "fail"
    rows = _rows()
    rows[0]["runs"]["pack_all"] = _run(6)
    assert S.decide(rows, [])["A1"] == "fail"
    rows = _rows()
    rows[len(S.a1_codes())]["runs"]["plain"] = _run(None, "timelimit", 9, None, "search_parts.c")
    assert S.decide(rows, [])["A2"] == "fail"  # pack's d = 8 lies below plain's lower 9
    rows = _rows()
    rows[len(S.a1_codes())]["runs"]["plain"] = _run(None, "timelimit", 6, None, "search_parts.c")
    out = S.decide(rows, [])
    assert out["A2"] == "pass" and out["A2_report"]["both_complete"] == len(S.a2_codes()) - 1
    rows = _rows()
    rows[-2]["search_c_sha256"] = "0" * 64
    assert S.decide(rows, [])["H"] == "fail"
    rows = _rows()
    rows[-1]["budget"] = 1.0
    assert S.decide(rows, [])["H"] == "fail"


def test_decide_on_a_find():
    A, B = S._poly(S.TARGET["A"]), S._poly(S.TARGET["B"])
    # no real witness: a forged one fails verify_witness, and a find below 30 fails C1
    rows = [r for r in _rows() if r["job"] not in ("C_pass", "C_end")]
    rows += [_cpass(b) for b in range(2, 26)] + [_cpass(26, True, 25, list(range(25)))]
    rows.append(_rows()[-1])
    out = S.decide(rows, [])
    assert out["C1"] == "fail" and out["H"] == "fail" and out["verdict"] == "fail"
    assert not D.verify_witness(A, B, 21, 18, "Z", list(range(25)))["logical"]


def test_execute_smoke(tmp_path, monkeypatch):
    gross = {"l": 12, "m": 6, "A": [[3, 0], [0, 1], [0, 2]], "B": [[0, 3], [1, 0], [2, 0]],
             "k": 12, "last": 12}  # fmt: skip
    small = [S.a1_codes()[0] | {"l": 3, "m": 4, "A": [[0, 0], [1, 1], [2, 3]],
                                "B": [[0, 0], [1, 0], [0, 1]]}]  # fmt: skip
    small[0]["k"] = bb.k_linalg(S._poly(small[0]["A"]), S._poly(small[0]["B"]), 3, 4)
    monkeypatch.setattr(S, "a1_codes", lambda: small if small[0]["k"] else [])
    monkeypatch.setattr(S, "a2_codes", lambda: [])
    monkeypatch.setattr(S, "KNOWN", {"144": S.KNOWN["144"]})
    monkeypatch.setattr(S, "TARGET", gross)
    path = tmp_path / "records.jsonl"
    S.execute(path, 2, budget=600.0)
    rows = S._rows(path)
    jobs = [r["job"] for r in rows]
    assert jobs.count("B") == 1 and jobs[-1] == "C_end"
    assert [r["bound"] for r in rows if r["job"] == "C_pass"] == list(range(2, 13))
    assert not any(r["found"] for r in rows if r["job"] == "C_pass")  # d = 12: nothing below
    assert rows[-1]["status"] == "bound"
    before = path.read_text()
    S.execute(path, 2, budget=600.0)
    assert path.read_text() == before
