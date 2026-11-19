"""Planar parents (examples/qec-parents): the shortest-form search against an independent
enumeration, the keys, the quotient tool against linear algebra, and the study's verdict logic.
Development data only: small tori and stage 3a. The registered populations of stages 3b, 3c and
4 are kept out of the tests."""

import itertools
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))
sys.path.insert(0, str(ROOT / "examples" / "qec-parents"))

import bb  # noqa: E402
import parents  # noqa: E402
import planar  # noqa: E402
import study  # noqa: E402

GROSS = ([(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)])


def _span(tri) -> int:
    return max(max(p[i] for p in tri) - min(p[i] for p in tri) for i in (0, 1))


def _preimages(box, g1, g2, ell, m, A, B):
    """The box points that (g1, g2) sends to each monomial difference of A and of B."""
    out = []
    for P in (A, B):
        for i in (1, 2):
            t = ((P[i][0] - P[0][0]) % ell, (P[i][1] - P[0][1]) % m)
            image = {
                p: ((p[0] * g1[0] + p[1] * g2[0]) % ell, (p[0] * g1[1] + p[1] * g2[1]) % m)
                for p in box
            }
            out.append([p for p in box if image[p] == t])
    return out


def brute_forms(ell, m, A, B, radius=3):
    """Every form within the box, by plain enumeration: {key: [(g1, g2), ...]} at the least
    range, and that range."""
    box = list(itertools.product(range(-radius, radius + 1), repeat=2))
    best, found = None, {}
    for g1 in itertools.product(range(ell), range(m)):
        for g2 in itertools.product(range(ell), range(m)):
            pre = _preimages(box, g1, g2, ell, m, A, B)
            for p, q, s, t in itertools.product(*pre):
                r = max(_span([(0, 0), p, q]), _span([(0, 0), s, t]))
                if best is None or r < best:
                    best, found = r, {}
                if r == best:
                    k = parents.key(((0, 0), p, q), ((0, 0), s, t))
                    found.setdefault(k, []).append((g1, g2))
    return best, found


def _random_code(rng, ell, m):
    mons = list(itertools.product(range(ell), range(m)))
    return tuple(rng.sample(mons, 3)), tuple(rng.sample(mons, 3))


def test_the_search_agrees_with_plain_enumeration_and_every_form_wraps_to_the_same_k():
    rng = random.Random(3)
    checked = 0
    for ell, m in ((2, 3), (3, 3), (2, 4), (3, 4), (2, 6)):
        codes = [_random_code(rng, ell, m) for _ in range(5)]
        got = parents.shortest_forms([(ell, m, A, B) for A, B in codes])
        for (A, B), (rng_c, keys) in zip(codes, got, strict=True):
            best, found = brute_forms(ell, m, A, B)
            assert rng_c == best
            assert keys == sorted(parents.key_text(k) for k in found)
            k_code = bb.k_linalg(A, B, ell, m)
            for key, maps in found.items():
                # the key is the form up to a symmetry, so wrap the form itself: rebuild it
                # from one of its maps by the same enumeration
                g1, g2 = maps[0]
                wrapped = _wrap_some_form(key, g1, g2, ell, m, A, B)
                assert bb.k_linalg(*wrapped, ell, m) == k_code
            checked += 1
    assert checked >= 20


def _wrap_some_form(key, g1, g2, ell, m, A, B):
    """A form of (A, B) under (g1, g2) with the given key, wrapped back onto the torus."""
    box = list(itertools.product(range(-3, 4), repeat=2))
    pre = _preimages(box, g1, g2, ell, m, A, B)
    for p, q, s, t in itertools.product(*pre):
        form = (((0, 0), p, q), ((0, 0), s, t))
        if parents.key(*form) == key:
            return parents.reduce_form(form, g1, g2, ell, m)
    raise AssertionError("no form with that key under that map")


def test_connected_means_the_monomial_differences_generate_the_group():
    A = ((0, 0), (0, 2), (0, 4))
    assert not parents.connected(2, 6, A, A)
    assert parents.connected(2, 6, A, ((0, 0), (1, 1), (0, 1)))
    assert parents.connected(6, 12, *GROSS)
    # a code that is not connected still has forms, of one component: range 1 here
    assert parents.shortest_forms([(2, 6, A, A)])[0][0] == 1


def test_the_gross_code_has_a_form_of_range_two():
    ((rng_c, keys),) = parents.shortest_forms([(6, 12, *GROSS)])
    assert rng_c == 2 and keys


def test_the_key_ignores_translation_signed_permutation_and_the_swap():
    rng = random.Random(5)
    for _ in range(50):
        ta = [(rng.randrange(-4, 5), rng.randrange(-4, 5)) for _ in range(3)]
        tb = [(rng.randrange(-4, 5), rng.randrange(-4, 5)) for _ in range(3)]
        k = parents.key(ta, tb)
        a, b, c, d = rng.choice(parents.SIGNED)
        sa, sb = (
            (rng.randrange(-9, 9), rng.randrange(-9, 9)),
            (rng.randrange(-9, 9), rng.randrange(-9, 9)),
        )
        ua = [(a * x + b * y + sa[0], c * x + d * y + sa[1]) for x, y in ta]
        ub = [(a * x + b * y + sb[0], c * x + d * y + sb[1]) for x, y in tb]
        assert parents.key(ub, ua) == k == parents.key(ua, ub)
        assert parents.key_parse(parents.key_text(k)) == k
    # and it tells apart pairs that are not related
    assert parents.key([(0, 0), (1, 0), (0, 1)], [(0, 0), (1, 0), (0, 2)]) != parents.key(
        [(0, 0), (1, 0), (0, 1)], [(0, 0), (2, 0), (1, 2)])  # fmt: skip


def test_the_gross_pair_has_eight_excitations_and_periods_twelve():
    assert planar.signature(*GROSS) == {"Q": 8, "mixed_area": 8, "period_x": 12, "period_y": 12}
    assert planar.k_on_torus(*GROSS, 6, 12) == 12
    assert planar.k_on_torus(*GROSS, 12, 12) == 16


def test_the_quotient_gives_k_on_every_torus_and_respects_both_bounds():
    rng = random.Random(11)
    done = 0
    while done < 25:
        A = [(rng.randrange(4), rng.randrange(4)) for _ in range(3)]
        B = [(rng.randrange(4), rng.randrange(4)) for _ in range(3)]
        if len(set(A)) < 3 or len(set(B)) < 3:
            continue
        Q = planar.dimension(A, B)
        ell, m = rng.randint(2, 9), rng.randint(2, 9)
        k = bb.k_linalg(A, B, ell, m)
        assert planar.k_on_torus(A, B, ell, m) == k
        if Q is not None:
            assert k <= 2 * Q <= 2 * planar.mixed_area(A, B)
        done += 1


def test_a_pair_with_a_common_factor_has_an_infinite_quotient():
    A = [(0, 0), (1, 0), (0, 1)]
    assert planar.dimension(A, A) is None
    assert planar.signature(A, A)["Q"] is None
    assert planar.dimension([(0, 0)], A) == 0


def test_mixed_area_of_two_unit_triangles_and_of_a_segment():
    tri = [(0, 0), (1, 0), (0, 1)]
    assert planar.mixed_area(tri, tri) == 1
    assert planar.mixed_area([(0, 0), (2, 0), (1, 0)], [(0, 0), (0, 3), (0, 1)]) == 6


@pytest.fixture(scope="module")
def stage_3a():
    return parents.cells(stages=("3a",))


def test_a_cells_frontier_is_its_connected_classes_at_the_best_distance(stage_3a):
    cell = stage_3a[("3a", 6, 12, 12)]
    assert (cell["n"], cell["d"]) == (144, 12)  # the gross code's cell
    assert cell["frontier"] and cell["others"]
    assert all(c[0] == "3a" for c in stage_3a)
    forms = parents.shortest_forms([(6, 12, A, B) for A, B in cell["frontier"]])
    assert all(r > 0 and keys for r, keys in forms)


def test_record_cells_are_the_best_scores_at_each_n(stage_3a):
    rec = parents.record_cells(stage_3a, "3a")
    assert ("3a", 6, 12, 12) in rec
    by_n = {}
    for c, v in stage_3a.items():
        by_n[v["n"]] = max(by_n.get(v["n"], 0), parents.score(c, v))
    assert {stage_3a[c]["n"] for c in rec} == set(by_n)
    assert all(parents.score(c, stage_3a[c]) == by_n[stage_3a[c]["n"]] for c in rec)
    assert parents.record_cells(stage_3a, "4") == []


def test_the_control_sample_is_bounded_and_repeatable():
    others = [(((0, 0), (0, 1), (0, i)), ((0, 0), (1, 0), (2, 0))) for i in range(2, 500)]
    c = ("4", 9, 60, 8)
    s = study.control_sample(c, others)
    assert len(s) == study.CONTROL and set(s) <= set(others)
    assert s == study.control_sample(c, list(reversed(others)))
    assert s != study.control_sample(("4", 9, 60, 10), others)
    assert study.control_sample(c, others[:5]) == sorted(others[:5])


def _row(group, cell, parents_, record=True, n=310, d=10, rng=2, connected=True):
    ell, m, k = cell
    return {"test": "class", "group": group, "record": record, "l": ell, "m": m, "k": k, "n": n,
            "d": d, "range": rng, "parents": parents_, "stage": "x", "A": [], "B": [],
            "connected": connected}  # fmt: skip


def _decide(rows, monkeypatch):
    monkeypatch.setattr(study, "population", lambda: [r for r in rows if r["test"] == "class"])
    return study.decide(rows, [])


def test_the_verdict_counts_descent_and_compares_it_with_the_control(monkeypatch):
    def par(p, q=4, ma=4):
        return {"test": "parent", "parent": p, "Q": q, "mixed_area": ma, "period_x": 3,
                "period_y": 3}  # fmt: skip

    rows = [
        _row("early", (3, 5, 4), ["P", "E"], n=30),
        _row("late", (5, 31, 8), ["P"]),          # descends
        _row("late", (5, 31, 8), ["X"]),          # same cell, does not
        _row("late", (2, 80, 8), ["Y"], n=320),   # a record cell that does not descend
        _row("late", (2, 81, 4), ["P"], record=False, n=324),
        _row("control", (5, 31, 8), ["P"]),
        _row("control", (5, 31, 8), ["Z"]),
        _row("control", (5, 31, 8), ["W"]),
        _row("control", (2, 80, 8), ["V"], n=320),
        par("P"), par("X"), par("Y"),
    ]  # fmt: skip
    v = _decide(rows, monkeypatch)
    assert v["missing"] == [] and v["method"] == "holds"
    assert (v["late_record_cells"], v["late_record_cells_descending"]) == (2, 1)
    assert v["descent"] == "holds"
    assert (v["frontier_fraction"], v["control_fraction"]) == (0.3333, 0.25)
    assert v["specific"] == "fails"
    assert v["not_descending"] == [[2, 80, 8]]
    assert v["cover"] == [{"early_cell": [30, 3, 5, 4, 10], "late_record_cells": 1}]
    assert (v["all_late_cells"], v["all_late_cells_descending"]) == (3, 2)
    assert [s["parent"] for s in v["shared_parents"]] == ["P"]

    # fewer control hits: the frontier is now at least twice the control
    v = _decide(
        [r for r in rows if r.get("parents") != ["P"] or r["group"] != "control"], monkeypatch
    )
    assert v["control_fraction"] == 0.0 and v["specific"] == "holds"

    # a parent that breaks a bound, an infinite quotient, and a missing signature all fail
    for broken in (par("X", q=3), par("X", q=5, ma=4), par("X", q=None)):
        v = _decide([broken if r.get("parent") == "X" else r for r in rows], monkeypatch)
        assert v["method"] == "fails" and v["method_failures"][0]["parent"] == "X"
    v = _decide([r for r in rows if r.get("parent") != "Y"], monkeypatch)
    assert v["method"] == "fails"

    # no cell descends: both tests fail
    v = _decide([r for r in rows if r["test"] == "parent" or r["group"] != "early"], monkeypatch)
    assert (v["descent"], v["specific"], v["cover_size"]) == ("fails", "fails", 0)


def test_a_class_without_a_form_or_not_connected_fails_the_method_check(monkeypatch):
    rows = [_row("early", (3, 5, 4), ["P"], n=30), _row("late", (5, 31, 8), [], rng=-1)]
    v = _decide(rows, monkeypatch)
    assert v["method"] == "fails" and v["unconnected"] == [[5, 31, 8, "late"]]
    rows = [_row("early", (3, 5, 4), ["P"], n=30, connected=False)]
    assert _decide(rows, monkeypatch)["unconnected"] == [[3, 5, 4, "early"]]
