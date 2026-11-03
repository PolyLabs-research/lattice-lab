"""Census stage 4's study (examples/qec-census-4/study.py): the tori, the cap, the fits as
registered, and the judging rules on synthetic records."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "examples" / "qec-census-4" / "study.py"
spec = importlib.util.spec_from_file_location("qec_census_stage4_study", STUDY)
S = importlib.util.module_from_spec(spec)
sys.modules["qec_census_stage4_study"] = S
spec.loader.exec_module(S)


def test_tori():
    t = S.tori()
    assert len(t["fresh"]) == 104 and sorted(t["exposed"]) == sorted(S.EXPOSED)
    every = t["fresh"] + t["exposed"]
    assert all(2 <= a <= b and 150 < a * b <= 200 for a, b in every)
    assert len(set(every)) == 110
    held = S.census.held_out_tori() | set(S.census.stage1_tori())
    assert not held & set(every)


def test_cap_and_fits():
    assert [S.cap(n) for n in (302, 350, 400)] == [24, 28, 30]
    f = S.fits.fit()
    assert (f["b"], f["c"]) == (S.B, S.C_ENV)
    assert abs(f["record_d_over_sqrt_n"] - S.G_RECORD) < 1e-4
    assert abs(f["record_score"] - S.S_RECORD) < 1e-4
    assert f["score_line"]["at_400"] + 1 <= S.S_CEILING + 0.05


def rec(n, best, settled=True, classes=10, e=True, bad=0):
    return {"job": "torus", "l": 2, "m": n // 4, "n": n, "classes": classes, "criterion_e": e,
            "k_sample": {"disagree": bad},
            "best": {"connected": {str(k): {"d": d, "settled": settled, "unresolved": 0}
                                   for k, d in best.items()}}}  # fmt: skip


def test_judge_torus():
    j = S.judge_torus(rec(400, {4: 30, 10: 24}))  # 1.5 sqrt(n); 10 * 576 / 400 = 14.4
    assert j["E"] == "pass" and j["S2"] == "pass" and j["G"] == "yes" and j["S1"] == "yes"
    j = S.judge_torus(rec(400, {4: 32}))
    assert j["E"] == "fail"
    j = S.judge_torus(rec(400, {4: 26}, settled=False))
    assert j["E"] == "incomplete" and j["G"] == "open" and j["S1"] == "open"
    j = S.judge_torus(rec(400, {4: 32}, settled=False))
    assert j["E"] == "fail" and j["G"] == "yes"  # a lower bound can prove these
    assert S.judge_torus(rec(400, {}, classes=0, e=False))["P0"] == "pass"
    assert S.judge_torus(rec(400, {}, classes=0, e=True))["P0"] == "fail"
    assert S.judge_torus(rec(400, {4: 20}, bad=1))["P0"] == "fail"
    j = S.judge_torus(rec(320, {16: 18}))  # 16 * 324 / 320 = 16.2: S1 yes, S2 pass
    assert j["S1"] == "yes" and j["S2"] == "pass"
    assert S.judge_torus(rec(320, {16: 20}))["S2"] == "fail"  # 20.0
    assert S.judge_torus({"error": "x"})["P0"] == "fail"


def test_decide_h_passes_on_json_round_tripped_records(monkeypatch):
    import json

    r = rec(400, {4: 30, 10: 24}) | {"settings": S.SETTINGS, "sha256": {}, "group": "fresh"}
    r = json.loads(json.dumps(r))
    v = S.decide([r], [])
    assert v["H"] == "pass" and not v["problems"]


def test_checkpoint_round_trip(tmp_path, monkeypatch):
    import json

    monkeypatch.setattr(S, "CHECKPOINT", tmp_path / "cp.jsonl")
    A, B = [[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]]
    row = {"A": A, "B": B}
    good = {"status": "complete", "d": 6, "witness": [0, 5, 4, 1, 21, 23]}
    save = S._saver(6, 6, "run-1")
    save("k1", good, row)
    save("k2", {"status": "timelimit", "error": "boom"}, row)  # not remembered
    S.CHECKPOINT.write_text(S.CHECKPOINT.read_text() + '{"cut sh')  # a stop mid-write
    save("k3", good, row)  # starts its own line
    got = S._checkpoint(6, 6, "run-1")
    assert set(got) == {"k1", "k3"} and got["k1"]["d"] == 6
    assert S._checkpoint(6, 6, "another run") == {}
    assert S._checkpoint(6, 6, None) == {}
    bad = json.loads(S.CHECKPOINT.read_text().splitlines()[0])
    bad["exact"]["witness"] = [0, 1]
    S.CHECKPOINT.write_text(json.dumps(bad) + "\n")
    import pytest

    with pytest.raises(RuntimeError):
        S._checkpoint(6, 6, "run-1")


def test_p0_counts_class_errors():
    r = rec(400, {4: 20}) | {"class_errors": 1}
    assert S.judge_torus(r)["P0"] == "fail"
