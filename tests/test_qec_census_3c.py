"""examples/qec-census-3c: the fast irreducibility test against bb's trial division, the tori it
continues on, the copied predictions, and the combined judging on synthetic records. Nothing here
computes on a held-out torus."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
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


def test_patched_restores_bb_and_census3():
    original, masks = bb._irreducible, C.c3.zero_masks
    with C.patched():
        assert bb._irreducible is C.irreducible_fast and C.c3.zero_masks is C.zero_masks_wide
        assert S.fast.c3.zero_masks is C.zero_masks_wide  # the module fast.py and study.py use
        f = bb._field(2**20 - 1)
        assert f.poly == original(20)
    assert bb._irreducible is original and C.c3.zero_masks is masks


@pytest.mark.parametrize("ell,m", [(3, 6), (3, 9), (6, 9), (3, 15), (7, 9), (2, 31), (4, 25)])
def test_wide_masks_are_census3s_on_stage_1_tori(ell, m):
    pairs, masks = C.c3.zero_masks(ell, m)
    with C.patched():
        wide_pairs, wide = C.zero_masks_wide(ell, m)
    assert np.array_equal(pairs, wide_pairs) and np.array_equal(masks, wide)
    assert masks.dtype == wide.dtype


def test_wide_zeros_on_66_bit_values():
    import random

    rng = random.Random(3)
    value = [[rng.getrandbits(66) for _ in range(9)] for _ in range(12)]
    value[5] = [
        a ^ b for a, b in zip(value[0], value[7], strict=True)
    ]  # 1 + u5 + u7 = 0 everywhere
    value[3][2] = value[0][2] ^ value[4][2]  # and 1 + u3 + u4 = 0 at one character
    pairs = np.array([(a, b) for a in range(1, 12) for b in range(a + 1, 12)], dtype=np.int64)
    zero = C._zeros(value, pairs)
    for i, (a, b) in enumerate(pairs):
        for c in range(9):
            assert zero[i, c] == (value[0][c] ^ value[a][c] ^ value[b][c] == 0)
    assert zero.sum() == 9 + 1
    with pytest.raises(ValueError):
        C._zeros([[1 << 130]], pairs[:0])


def test_fields_are_unchanged_on_stage_1_tori():
    # the Field objects stage 3b's instruments use, with and without the patch
    for N in (3, 7, 9, 15, 21, 31, 33, 45, 63, 93):
        bb._field.cache_clear()
        plain = bb._field(N)
        with C.patched():
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
    assert "the predictions differ from stage 3b's" not in out["problems"]
    # disclosed in the question: stage 3b's records alone fail P1 and P2
    assert out["P1"] == out["P2"] == out["verdict"] == "fail"
    assert "P1 = fail (3x35, 5x21)" in C.question()["known_at_registration"]
    tampered = [dict(p) for p in regs]
    tampered[2] = tampered[2] | {"constant": 9.9}
    bad = C.decide([], tampered)
    assert "the predictions differ from stage 3b's" in bad["problems"] and bad["H"] == "fail"


def test_decide_folds_in_stage_3c_rows():
    regs = [{"question": "x", **p} for p in C.predictions()]
    ell, m = C.tori()[0]
    stamp = {k: v for k, v in C.code_hashes().items() if k in ("study_py", "tests_py")}
    row = {"job": "torus", "l": ell, "m": m, "n": 2 * ell * m, "group": S.group_of(ell, m),
           "classes": 0, "criterion_e": False, "k_sample": {"sampled": 50, "disagree": 0},
           "best": {"connected": {}}, "settings": S.SETTINGS, "s3c_sha256": stamp}  # fmt: skip
    out = C.decide([row], regs)
    assert out["records"]["stage3c"] == 1 and f"{ell}x{m}" in out["per_torus"]
    assert not any("another stage 3c code" in p for p in out["problems"])
    other = C.decide([row | {"s3c_sha256": {}}], regs)
    assert any("another stage 3c code" in p for p in other["problems"])
    twice = C.decide([row, row], regs)
    assert "a torus has two records" in twice["problems"]
