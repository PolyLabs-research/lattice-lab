"""examples/qec-census-3b: the fast instruments against stage 3a on stage-1 tori, criterion E on
every stage-1 torus, the guard, and the judging rules on synthetic records. Nothing here computes
on a held-out torus."""

import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA3A = ROOT / "examples" / "qec-census-3" / "data"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("qec_census_stage3b_study", ROOT / "examples" / "qec-census-3b" / "study.py")
F = S.fast


def _stage3a(ell, m):
    lines = [json.loads(x) for x in (DATA3A / f"{ell}x{m}.jsonl").read_text().splitlines()]
    return lines[0], lines[1:]


@pytest.mark.parametrize("ell,m", [(3, 6), (3, 9), (6, 9), (3, 15), (7, 9)])
def test_fast_classes_are_stage_3as(ell, m):
    _, rows = _stage3a(ell, m)
    old = {json.dumps(r["key"]): r for r in rows}
    new = {json.dumps(r["key"]): r for r in F.classes(ell, m)["classes"]}
    assert set(old) == set(new)
    assert all(old[k]["k"] == new[k]["k"] and old[k]["connected"] == new[k]["connected"]
               for k in new)  # fmt: skip


@pytest.mark.parametrize("ell,m", [(3, 6), (6, 9)])
def test_frontier_is_stage_3as_best(ell, m):
    _, rows = _stage3a(ell, m)
    want = defaultdict(int)
    for r in rows:
        if r["connected"]:
            want[r["k"]] = max(want[r["k"]], r["d"])
    f = F.frontier(ell, m, workers=2, limit=120, log=lambda s: None)
    got = {k: v for k, v in f["best"]["connected"].items()}
    assert {k: v["d"] for k, v in got.items()} == dict(want)
    assert all(v["settled"] for v in got.values())
    d = {json.dumps(r["key"]): r["d"] for r in rows}
    assert all(r["upper"] is None or r["upper"] >= d[json.dumps(r["key"])] for r in f["classes"])


def test_criterion_e_on_every_stage_1_torus():
    for path in DATA3A.glob("*.jsonl"):
        head, rows = _stage3a(*map(int, path.stem.split("x")))
        assert S.criterion_e(head["l"], head["m"]) == bool(rows)


def test_the_guard_opens_only_inside_a_run():
    held = S.tori()["random"][0]
    with pytest.raises(S.census.HeldOut):
        S.c3.zero_masks(*held)
    with S.opened():
        S.census.guard(*held)  # admitted
        with pytest.raises(S.census.HeldOut):
            S.census.guard(2, 48 + 1000)  # not a registered torus: still refused
    with pytest.raises(S.census.HeldOut):
        S.c3.zero_masks(*held)
    assert S.census.guard is S._ORIGINAL_GUARD


def test_tori():
    t = S.tori()
    assert (len(t["random"]), len(t["extrapolation"]), len(t["exposed"])) == (22, 79, 21)
    assert S.P4_TORUS in t["random"] and (12, 12) in t["exposed"]


def _rec(best, n=200, group="random", classes=5, crit=True, lm=(4, 25)):
    return {"l": lm[0], "m": lm[1], "n": n, "group": group, "classes": classes,
            "criterion_e": crit, "k_sample": {"sampled": 50, "disagree": 0},
            "best": {"connected": {str(k): {"d": d, "settled": s} for k, (d, s) in best.items()}}}  # fmt: skip


def test_judging_rules():
    ok = S.judge_torus(_rec({4: (18, True), 8: (12, True)}))
    assert ok["P0"] == ok["P1"] == ok["P2"] == ok["P3"] == "pass"
    assert S.judge_torus(_rec({4: (12, True), 8: (14, True)}))["P1"] == "fail"
    cap = 2 * math.floor(1.40 * math.sqrt(200) / 2)
    assert S.judge_torus(_rec({4: (cap + 2, True)}))["P2"] == "fail"
    assert S.judge_torus(_rec({4: (cap, True)}))["P2"] == "pass"
    assert S.judge_torus(_rec({16: (14, True)}))["P3"] == "fail"  # 16 * 196 / 200 > 12
    assert S.judge_torus(_rec({16: (14, True)}, n=300, group="extrapolation"))["P3"] == "pass"
    assert S.judge_torus(_rec({4: (18, False)}))["P2"] == "incomplete"
    assert S.judge_torus(_rec({}, classes=0, crit=True))["P0"] == "fail"
    p4 = S.judge_torus(_rec({8: (16, True)}, n=192, lm=S.P4_TORUS))
    assert p4["P4"] == "pass"
    assert S.judge_torus(_rec({8: (14, True)}, n=192, lm=S.P4_TORUS))["P4"] == "fail"
