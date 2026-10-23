"""The instruments of examples/qec-open-distance (parts.py): the split search against
distance_brute and the unsplit search on small codes, its parts' coverage, and the window's
witnesses. Nothing here touches the study's two codes beyond their k."""

import importlib.util
import random
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


P = _load("qec_open_parts", ROOT / "examples" / "qec-open-distance" / "parts.py")


def _codes(sizes, count, seed):
    rng = random.Random(seed)
    out = []
    for ell, m in sizes:
        found = 0
        while found < count:
            A = [(rng.randrange(ell), rng.randrange(m)) for _ in range(3)]
            B = [(rng.randrange(ell), rng.randrange(m)) for _ in range(3)]
            if len(set(A)) < 3 or len(set(B)) < 3 or bb.k_linalg(A, B, ell, m) == 0:
                continue
            if ell * m + bb.k_linalg(A, B, ell, m) // 2 > D.BRUTE_CAP:
                continue
            out.append((A, B, ell, m))
            found += 1
    return out


@pytest.mark.parametrize("A,B,ell,m", _codes([(3, 4), (3, 7), (4, 6), (2, 9)], 3, 2026))
def test_split_search_matches_enumeration(A, B, ell, m):
    want = D.distance_brute(A, B, ell, m, "Z")["d"]
    for parts, depth in ((1, 2), (3, 2), (5, 3), (7, 4)):
        r = P.search(A, B, ell, m, "Z", anchors=(0, ell * m), parts=parts, depth=depth,
                     workers=2, time_limit=120)  # fmt: skip
        assert r["status"] == "complete" and r["d"] == want
        r = P.search(A, B, ell, m, "Z", anchors=None, parts=parts, depth=depth, workers=2,
                     time_limit=120)  # fmt: skip
        assert r["status"] == "complete" and r["d"] == want


def test_parts_cover_the_pass_exactly():
    # the gross code's pass at bound 10 finds nothing (d = 12): the parts' nodes at and below the
    # split depth add up to the unsplit pass's, and the nodes above it are counted by every part
    A, B = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]
    whole = D.distance_search(A, B, 12, 6, "Z", bound=10, anchors=(0, 72), deepen=False)
    assert whole["status"] == "complete" and whole["d"] is None
    above = {}
    for depth in (2, 4, 6):
        one = P.search(A, B, 12, 6, "Z", anchors=(0, 72), first=10, last=10, parts=1,
                       depth=depth, workers=1, time_limit=120)["passes"][0]  # fmt: skip
        assert one["parts"][0]["nodes"] == whole["nodes"]
        split = P.search(A, B, 12, 6, "Z", anchors=(0, 72), first=10, last=10, parts=5,
                         depth=depth, workers=3, time_limit=120)["passes"][0]  # fmt: skip
        assert not split["found"]
        total = sum(x["nodes"] for x in split["parts"])
        above[depth] = (total - whole["nodes"]) / 4  # 4 extra copies of the nodes above
        assert total >= whole["nodes"] and above[depth] == int(above[depth])
    assert above[2] < above[4] < above[6]


def test_split_search_on_the_gross_code():
    A, B = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]
    r = P.search(A, B, 12, 6, "Z", anchors=(0, 72), parts=6, depth=5, workers=3,
                 time_limit=300)  # fmt: skip
    assert r["status"] == "complete" and r["d"] == 12 and r["lower"] == 12
    assert [p["bound"] for p in r["passes"]] == list(range(2, 14))
    assert [p["found"] for p in r["passes"]] == [False] * 11 + [True]
    assert D.verify_witness(A, B, 12, 6, "Z", r["witness"])["logical"]
    # stopping at `last`: no find below 12 shows d >= 12 only
    r = P.search(A, B, 12, 6, "Z", anchors=(0, 72), first=11, last=12, parts=4, depth=5,
                 workers=2, time_limit=300)  # fmt: skip
    assert r["status"] == "bound" and r["lower"] == 12 and r["d"] is None


def test_split_search_time_limit():
    A, B = [(3, 0), (0, 2), (0, 7)], [(0, 3), (1, 0), (2, 0)]
    r = P.search(A, B, 12, 12, "Z", anchors=(0, 144), first=17, parts=4, depth=5, workers=2,
                 time_limit=0.5)  # fmt: skip
    assert r["status"] == "timelimit" and r["lower"] is None and r["passes"] == []


def test_window_gives_checked_upper_bounds():
    for A, B, ell, m in _codes([(3, 6), (3, 8)], 2, 7):
        want = D.distance_brute(A, B, ell, m, "Z")["d"]
        w = P.window(A, B, ell, m, "Z", seeds=(0, 1), seconds=0.5, workers=2)
        assert w["upper"] == want  # small codes: found at once
        assert D.verify_witness(A, B, ell, m, "Z", w["witness"])["weight"] == want
        assert all(x["weights"] == sorted(x["weights"], reverse=True) for x in w["runs"])


def test_window_is_repeatable_by_seed():
    A, B = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]
    one = P.window(A, B, 12, 6, "Z", seeds=(5,), seconds=0.3, workers=1)["runs"][0]
    two = P.window(A, B, 12, 6, "Z", seeds=(5,), seconds=0.3, workers=1)["runs"][0]
    n = min(len(one["weights"]), len(two["weights"]))
    assert one["weights"][:n] == two["weights"][:n] and n >= 1


S = _load("qec_open_study", ROOT / "examples" / "qec-open-distance" / "study.py")


def test_codes_are_the_sources():
    for key, c in S.CODES.items():
        assert 2 * c["l"] * c["m"] == int(key)
        assert bb.k_linalg(*S._code(key)) == c["k"]


def test_execute_and_decide_on_the_gross_code(tmp_path, monkeypatch):
    gross = {"name": "gross", "l": 12, "m": 6, "A": [[3, 0], [0, 1], [0, 2]],
             "B": [[0, 3], [1, 0], [2, 0]], "k": 12, "published_upper": 12}  # fmt: skip
    monkeypatch.setitem(S.CODES, "360", gross)
    monkeypatch.setitem(S.CODES, "756", gross)
    monkeypatch.setattr(S, "WINDOW_SECONDS", 2.0)
    monkeypatch.setattr(S, "SEARCH_BUDGET", {"360": 300.0, "756": 0.001})
    path = tmp_path / "records.jsonl"
    S.execute(path, 4, budget={"360": 300.0, "756": 0.001}, seconds=2.0)
    rows = S._rows(path)
    assert [r["job"] for r in rows if r["job"] != "pass"] == ["window", "window", "search_end",
                                                              "search_end"]  # fmt: skip
    a = S.summarise(rows, "360")
    assert a["window_upper"] == 12 and a["d"] == 12 and a["lower"] == 12 and not a["problems"]
    assert [r["bound"] for r in rows if r["job"] == "pass"] == list(range(2, 13))
    b = S.summarise(rows, "756")
    assert b["search_status"] == "timelimit" and b["lower"] is None and b["d"] is None
    out = S.decide(rows, [])
    assert out["H4"] == "pass" and out["H1"] == "fail"  # 12 < 24: a lighter logical
    # resume skips everything recorded
    before = path.read_text()
    S.execute(path, 4, budget={"360": 300.0, "756": 0.001}, seconds=2.0)
    assert path.read_text() == before


def _pass(code, b, found=False, least=None):
    return {"job": "pass", "code": code, "bound": b, "found": found, "least": least,
            "witness": None, "seconds": 1.0, "parts": [{}] * S.PARTS,
            "settings": S.SEARCH_SETTINGS,
            "search_parts_c_sha256": S.code_hashes()["search_parts_c"]}  # fmt: skip


def _window(code, upper):
    return {"job": "window", "code": code, "upper": upper, "witness": None,
            "k": S.CODES[code]["k"], "seconds": S.WINDOW_SECONDS,
            "runs": [{"seed": s} for s in S.WINDOW_SEEDS],
            "window_c_sha256": S.code_hashes()["window_c"]}  # fmt: skip


def _end(code):
    return {"job": "search_end", "code": code, "status": "bound", "budget": S.SEARCH_BUDGET[code],
            "settings": S.SEARCH_SETTINGS}  # fmt: skip


def test_decide_rules():
    rows = [_window("360", 24), _window("756", 34),
            *[_pass("360", b) for b in range(2, 25)], _end("360"),
            *[_pass("756", b) for b in range(2, 22)], _end("756")]  # fmt: skip
    out = S.decide(rows, [])
    assert out["verdict"] == "hold" and out["H1"] == "pass" and out["H2"] == "pass"
    assert out["codes"]["360"]["d"] == 24 and out["H3"]["lower"] == 21 and out["H3"]["in_range"]
    # the budget ends before the pass at 24
    short = [r for r in rows if not (r["job"] == "pass" and r["code"] == "360" and r["bound"] > 22)]
    assert S.decide(short, [])["verdict"] == "incomplete"
    # a lighter logical found by the search
    light = [r for r in short] + [_pass("360", 23, True, 22)]
    out = S.decide(light, [])
    assert out["H1"] == "fail" and out["verdict"] == "fail" and out["codes"]["360"]["d"] == 22
    # the window lighter than 34 on 756
    rows2 = [_window("756", 32) if r["job"] == "window" and r["code"] == "756" else r for r in rows]
    assert S.decide(rows2, [])["H2"] == "fail"
    # a gap in the passes
    gap = [r for r in rows if not (r["job"] == "pass" and r["code"] == "756" and r["bound"] == 5)]
    assert S.decide(gap, [])["H4"] == "fail"
    # a search find on 756 below 34 fails H2, whatever the window found
    find = [r for r in rows if r["job"] != "search_end" or r["code"] != "756"]
    find += [_pass("756", 22, True, 21), _end("756")]
    out = S.decide(find, [])
    assert out["H2"] == "fail" and out["verdict"] == "fail" and out["H3"]["found_below_34"]
    # records from other code or settings fail H4
    other = [dict(r, search_parts_c_sha256="0" * 64) if r["job"] == "pass" else r for r in rows]
    assert S.decide(other, [])["H4"] == "fail"
    other = [dict(r, budget=1.0) if r["job"] == "search_end" else r for r in rows]
    assert S.decide(other, [])["H4"] == "fail"
    other = [dict(r, settings={**S.SEARCH_SETTINGS, "depth": 3}) if r["job"] == "pass" else r
             for r in rows]  # fmt: skip
    assert S.decide(other, [])["H4"] == "fail"
