"""examples/qec-census-3c: the fast irreducibility test against bb's trial division, the tori it
continues on, the copied predictions, and the combined judging on synthetic records. Nothing here
computes on a held-out torus."""

import importlib.util
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


C = _load("qec_census_stage3c_study", ROOT / "examples" / "qec-census-3c" / "study.py")
S, bb = C.s3b, C.bb


@pytest.mark.parametrize("d", range(2, 27))
def test_fast_is_trial_division(d):
    assert C.irreducible_fast(d) == bb._irreducible(d)


def _has_factor(p: int, d: int) -> bool:
    return any(bb._pmod(p, f) == 0 for f in range(2, 1 << (d // 2 + 1)))


@pytest.mark.parametrize("d", [27, 30, 33, 36, 40])
def test_fast_output_is_irreducible_and_smallest(d):
    p = C.irreducible_fast(d)
    assert p.bit_length() - 1 == d and not _has_factor(p, d)
    # every earlier candidate has a factor (spot-checked on the last few before p)
    for q in range(max((1 << d) | 1, p - 40), p, 2):
        assert _has_factor(q, d)


def test_fast_fields_restores_bb():
    original = bb._irreducible
    with C.fast_fields():
        assert bb._irreducible is C.irreducible_fast
        f = bb._field(2**20 - 1)
        assert f.poly == original(20)
    assert bb._irreducible is original


def test_fields_are_unchanged_on_stage_1_tori():
    # the Field objects stage 3b's instruments use, with and without the patch
    for N in (3, 7, 9, 15, 21, 31, 33, 45, 63, 93):
        bb._field.cache_clear()
        plain = bb._field(N)
        with C.fast_fields():
            fast = bb._field(N)
        assert (plain.d, plain.poly) == (fast.d, fast.poly)
        assert vars(plain).keys() == vars(fast).keys()
        assert all(vars(plain)[k] == vars(fast)[k] for k in vars(plain)
                   if isinstance(vars(plain)[k], (int, tuple, list, dict)))  # fmt: skip
    bb._field.cache_clear()


def test_tori_continue_stage_3b():
    done = {(r["l"], r["m"]) for _, _, r in C._s3b_rows()}
    t = C.tori()
    every = [x for g in ("random", "extrapolation", "exposed") for x in S.tori()[g]]
    assert set(t) | done == set(every) and not set(t) & done
    assert len(set(t)) == len(t) == len(every) - len(done)
    assert t == [x for x in every if x not in done]  # stage 3b's order


def test_predictions_are_stage_3bs():
    s3b = [e for e in C._s3b_ledger() if e["kind"] == "prediction"]
    mine = C.predictions()
    assert [p["copied_from"] for p in mine] == [e["hash"] for e in s3b]
    assert [C._unlinked(p) for p in mine] == [C._unlinked(e["body"]) for e in s3b]
    assert all("question" not in p for p in mine)


def test_decide_combines_both_studies():
    s3b_rows = [r for _, _, r in C._s3b_rows()]
    regs = [{"question": "x", **p} for p in C.predictions()]
    out = C.decide([], regs)
    assert out["records"] == {"stage3b": len(s3b_rows), "stage3c": 0}
    assert out == C.decide([], regs) and "the predictions differ" not in str(out["problems"])
    # the tori not yet run leave stage 3b's extrapolation parts incomplete or failed, never pass
    assert out["P1"] != "pass" or not [x for x in C.tori() if x in S.tori()["extrapolation"]]
    tampered = [dict(p) for p in regs]
    tampered[2] = tampered[2] | {"constant": 9.9}
    bad = C.decide([], tampered)
    assert bad["verdict"] == "fail" and bad["H"] == "fail"
