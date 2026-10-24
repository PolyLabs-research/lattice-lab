"""examples/qec-census-3 (stage 3a): the k > 0 rule by common zeros against bb.k_linalg on every
raw code of small tori, the classes against the group's action, and the distances against
enumeration. Small stage-1 tori only (the census guard refuses the rest)."""

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


C = _load("qec_census_stage3", ROOT / "examples" / "qec-census-3" / "census3.py")


@pytest.mark.parametrize("ell,m", [(3, 3), (3, 4), (3, 6)])
def test_common_zero_rule_is_k_positive(ell, m):
    pairs, cand = C.candidates(ell, m)
    cand = set(cand)
    for i in range(len(pairs)):
        for j in range(i, len(pairs)):
            A, B = C.polynomial(pairs[i], m), C.polynomial(pairs[j], m)
            assert (C.bb.k_linalg(A, B, ell, m) > 0) == ((i, j) in cand)


def _as_list(key):
    return [[list(t) for t in P] for P in key]


def _translate(P, g, ell, m):
    return [((p + g[0]) % ell, (q + g[1]) % m) for p, q in P]


def test_classes_are_invariant_under_the_group():
    ell, m = 3, 6
    out = C.classes(ell, m)
    keys = {tuple(tuple(tuple(t) for t in P) for P in c["key"]) for c in out["classes"]}
    assert sum(c["size"] for c in out["classes"]) == out["raw_k_positive"]
    auts = C.census.automorphisms(ell, m)
    rng = random.Random(3)
    for c in rng.sample(out["classes"], 10):
        A, B = [tuple(t) for t in c["A"]], [tuple(t) for t in c["B"]]
        (g0, g1), (h0, h1) = rng.choice(auts)
        f = lambda P: [((p * g0 + q * h0) % ell, (p * g1 + q * h1) % m) for p, q in P]  # noqa: E731
        A2 = _translate(f(A), (rng.randrange(ell), rng.randrange(m)), ell, m)
        B2 = _translate(f(B), (rng.randrange(ell), rng.randrange(m)), ell, m)
        if rng.random() < 0.5:
            A2, B2 = B2, A2
        ((key, _, _),) = C.census.canonical([(A2, B2)], ell, m)
        assert key in keys and _as_list(key) == c["key"]
        assert C.bb.k_linalg(A2, B2, ell, m) == c["k"]


def test_distances_match_enumeration():
    ell, m = 3, 4
    for c in C.classes(ell, m)["classes"]:
        A, B = [tuple(t) for t in c["A"]], [tuple(t) for t in c["B"]]
        r = C.deep_distance(A, B, ell, m, 60)
        assert r["status"] == "complete"
        assert r["d"] == C.distance.distance_brute(A, B, ell, m, "Z")["d"]


def test_published_form_is_a_subfamily():
    # Bravyi et al.'s [[72,12,6]] on 6 x 6 is of the published form: its class must appear
    ell, m = 6, 6
    out = C.classes(ell, m)
    A, B = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]
    ((key, _, _),) = C.census.canonical([(A, B)], ell, m)
    match = [c for c in out["classes"] if c["key"] == _as_list(key)]
    assert len(match) == 1 and match[0]["k"] == 12


def test_guard_refuses_held_out():
    held = sorted(C.census.held_out_tori())[0]
    with pytest.raises(C.census.HeldOut):
        C.zero_masks(*held)
