"""The code census, stage 1 (examples/qec-census/census.py): the fast k against bb, the canonical
form against examples/qec-distance-2's equivalence_key, the classes against the orbits of the
equivalence group, the hold-out refusal, and the summary on synthetic data. Everything here runs
on small stage-1 tori; nothing touches a held-out torus."""

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "examples" / "qec-census"
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))

import bb  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up there
    spec.loader.exec_module(module)
    return module


C = _load("qec_census", HERE / "census.py")
ODD = [(3, 3), (3, 5), (3, 7), (7, 7), (5, 9)]
EVEN = [(2, 9), (3, 6), (4, 6), (6, 6), (6, 9)]


# ---------------------------------------------------------------- k


def test_raw_parameters_are_the_family_once_each():
    for ell, m in [(2, 3), (3, 4), (4, 6)]:
        P = C.raw_parameters(ell, m)
        assert len(P) == C.raw_count(ell, m) == ell * math.comb(m, 2) * m * math.comb(ell, 2)
        a, b, c, d, e, f = P.T
        assert (b < c).all() and (e < f).all() and (a < ell).all() and (d < m).all()
        pairs = set()
        for t in P:
            A, B = C.polynomials(t)
            pairs.add(tuple(tuple(map(tuple, C.retest._reduce(X, ell, m))) for X in (A, B)))
        assert len(pairs) == len(P)  # distinct choices, distinct pairs (module docstring)


def test_rank_hz_equals_rank_hx_on_every_raw_code():
    for ell, m in [(3, 3), (3, 6), (6, 6), (7, 7), (4, 9)]:
        r = C.ranks(ell, m, check=True)
        assert len(r) == C.raw_count(ell, m)
        assert (r[:, 0] == r[:, 1]).all()


def test_fast_k_matches_bb_on_random_raw_codes():
    rng = random.Random("test qec-census k")
    for ell, m in ODD + EVEN:
        P, k = C.raw_parameters(ell, m), C.k_all(ell, m)
        positive = np.flatnonzero(k > 0).tolist()
        zero = np.flatnonzero(k == 0).tolist()
        sample = rng.sample(positive, min(40, len(positive))) + rng.sample(zero, min(40, len(zero)))
        for i in sample:
            A, B = C.polynomials(P[i])
            assert bb.k_linalg(A, B, ell, m) == k[i], (ell, m, P[i])
            assert bb.k_characters(A, B, ell, m) == k[i], (ell, m, P[i])
    # both kinds occur: the test sees codes with k > 0 at odd and even sizes
    assert (C.k_all(3, 7) > 0).any() and (C.k_all(6, 6) > 0).any()


def test_a_code_with_k_above_zero_has_weights_three_and_three():
    for ell, m in [(3, 3), (3, 6), (6, 6)]:
        P, k = C.raw_parameters(ell, m), C.k_all(ell, m)
        for i in np.flatnonzero(k > 0):
            A, B = C.polynomials(P[i])
            assert [len(C.retest._reduce(X, ell, m)) for X in (A, B)] == [3, 3]
        # the cancelling choices (a = 0 and 0 in {b, c}) are units: k = 0
        unit = (P[:, 0] == 0) & (P[:, 1] == 0)
        assert unit.any() and (k[unit] == 0).all()


def test_k_is_zero_where_l_or_m_is_a_power_of_two():
    # the lemma in census.py's docstring: B (or A) is a unit at every character
    for ell, m in [(2, 3), (2, 9), (2, 15), (4, 6), (4, 9), (3, 8), (6, 8), (8, 9)]:
        assert (C.k_all(ell, m) == 0).all(), (ell, m)
    # and it is a lemma about the size only: tori without a power of 2 do have codes with k > 0
    assert (C.k_all(3, 6) > 0).any() and (C.k_all(3, 3) > 0).any()


# ---------------------------------------------------------------- classes


def _random_trinomial(rng, ell, m):
    return [list(t) for t in rng.sample([(p, q) for p in range(ell) for q in range(m)], 3)]


def test_the_canonical_form_is_equivalence_key():
    rng = random.Random("test qec-census canonical")
    for ell, m in [(3, 3), (4, 6), (6, 6), (3, 7), (2, 9)]:
        codes = [(_random_trinomial(rng, ell, m), _random_trinomial(rng, ell, m))
                 for _ in range(60)]  # fmt: skip
        got = C.canonical(codes, ell, m)
        assert [g[0] for g in got] == [C.retest.equivalence_key(A, B, ell, m) for A, B in codes]
    for ell, m in [(3, 6), (3, 9)]:  # every code of the family with k > 0
        P, k = C.raw_parameters(ell, m), C.k_all(ell, m)
        codes = [C.polynomials(P[i]) for i in np.flatnonzero(k > 0)]
        got = C.canonical(codes, ell, m)
        assert [g[0] for g in got] == [C.retest.equivalence_key(A, B, ell, m) for A, B in codes]


def test_fixes_and_swaps_count_the_automorphisms():
    rng = random.Random("test qec-census fixes")
    ell, m = 6, 6
    P, k = C.raw_parameters(ell, m), C.k_all(ell, m)
    picks = rng.sample(np.flatnonzero(k > 0).tolist(), 12)
    codes = [C.polynomials(P[i]) for i in picks]
    norm = C.retest._translates
    for (A, B), (_, fixes, swaps) in zip(codes, C.canonical(codes, ell, m), strict=True):
        ta, tb = (norm(C.retest._reduce(X, ell, m), ell, m) for X in (A, B))
        f = s = 0
        for aut in C.automorphisms(ell, m):
            ua, ub = (norm(C.retest._mapped(C.retest._reduce(X, ell, m), aut, ell, m), ell, m)
                      for X in (A, B))  # fmt: skip
            f += (ua, ub) == (ta, tb)
            s += (ua, ub) == (tb, ta)
        assert (fixes, swaps) == (f, s) and fixes >= 1


def test_the_classes_are_the_orbits_and_k_is_constant_on_each():
    for ell, m in [(3, 3), (3, 6), (3, 9)]:
        found = C.classes(ell, m)
        P, k = C.raw_parameters(ell, m), C.k_all(ell, m)
        positive = [tuple(P[i].tolist()) for i in np.flatnonzero(k > 0)]
        orbits = {frozenset(o) for o in C.orbit_partition(ell, m, positive)}
        key_classes = {}
        for i in np.flatnonzero(k > 0):
            A, B = C.polynomials(P[i])
            key = C.retest.equivalence_key(A, B, ell, m)
            key_classes.setdefault(key, set()).add(tuple(P[i].tolist()))
        # no two classes equivalent and no class split: the partitions are equal
        assert {frozenset(s) for s in key_classes.values()} == orbits
        assert len(found["classes"]) == len(orbits)
        assert sum(c["size"] for c in found["classes"]) == len(positive)
        for c in found["classes"]:
            members = key_classes[tuple(tuple(map(tuple, X)) for X in c["key"])]
            assert c["size"] == len(members) and c["k_constant"]
            assert {bb.k_linalg(*C.polynomials(t), ell, m) for t in members} == {c["k"]}
            assert tuple(c["params"]) == min(members, key=lambda t: _raw_index(t, ell, m))


def _raw_index(t, ell, m):
    P = C.raw_parameters(ell, m)
    return int(np.flatnonzero((P == np.array(t)).all(axis=1))[0])


def test_the_orbit_check_can_see_a_split():
    # two codes in one orbit (a diagonal automorphism (x, y) -> (x^-1, y^-1) maps one to the
    # other, up to monomials) and one code alone: the partition must join the first two
    ell, m = 3, 3
    P, k = C.raw_parameters(ell, m), C.k_all(ell, m)
    found = C.classes(ell, m)
    big = max(found["classes"], key=lambda c: c["size"])
    key = tuple(tuple(map(tuple, X)) for X in big["key"])
    members = [tuple(P[i].tolist()) for i in np.flatnonzero(k > 0)
               if C.retest.equivalence_key(*C.polynomials(P[i]), ell, m) == key]  # fmt: skip
    assert len(members) >= 2
    orbits = C.orbit_partition(ell, m, members[:2])
    assert len(orbits) == 1


# ---------------------------------------------------------------- the hold-out


def _held_out():
    h = json.loads((HERE / "holdout.json").read_text())
    return [tuple(t) for key in ("held_out_random", "held_out_extrapolation") for t in h[key]]


def _forbid_computing(monkeypatch):
    """Every primitive that computes on codes raises instead (guard needs none of them)."""

    def forbidden(*args, **kwargs):
        raise AssertionError("computed on a refused torus")

    monkeypatch.setattr(C, "_census_binary", forbidden)
    for module, names in ((C.bb, ["local_terms", "k_linalg", "k_characters", "two_part"]),
                          (C.distance, ["distance_search", "distance_ilp", "verify_witness"]),
                          (C.retest, ["_isomorphisms", "_reduce", "_mapped", "_translates",
                                      "equivalence_key", "_carried_key"])):  # fmt: skip
        for name in names:
            monkeypatch.setattr(module, name, forbidden)


def test_held_out_tori_are_refused_before_anything_is_computed(monkeypatch):
    _forbid_computing(monkeypatch)
    A, B = [[0, 0], [0, 1], [1, 0]], [[0, 0], [0, 2], [1, 1]]
    c = {"A": A, "B": B, "fixes": 1, "swaps": 0}
    entries = [
        lambda a, b: C.raw_parameters(a, b),
        lambda a, b: C.ranks(a, b, check=True),
        lambda a, b: C.k_all(a, b),
        lambda a, b: C.automorphisms(a, b),
        lambda a, b: C.canonical([(A, B)], a, b),
        lambda a, b: C.classes(a, b),
        lambda a, b: C.orbit_partition(a, b, [(0, 1, 2, 0, 0, 1)]),
        lambda a, b: C.census_torus(a, b),
        lambda a, b: C.structure(c, a, b, 1),
        lambda a, b: C._translation_stabilizer(A, a, b),
        lambda a, b: C.frobenius_orbits([((0, 0), 1)], a, b),
        lambda a, b: C.dilations(A, B, a, b),
        lambda a, b: C._verified(A, B, a, b, [0, 1]),
        lambda a, b: C.class_distance(A, B, a, b, 1),
        lambda a, b: C.recheck(A, B, a, b, 1),
        lambda a, b: C.program_distance(A, B, a, b, 1),
    ]
    held = _held_out()
    assert len(held) == 122
    for ell, m in held:
        for a, b in ((ell, m), (m, ell)):
            for entry in entries:
                with pytest.raises(C.HeldOut):
                    entry(a, b)
                with pytest.raises(C.HeldOut):  # allow_isomorphic does not open a held-out one
                    C.guard(a, b, allow_isomorphic=True)
    for a, b in [(1, 7), (3, 2), (12, 13), (11, 14)]:  # not stage-1 tori (or not l <= m)
        for entry in entries:
            with pytest.raises(C.HeldOut):
                entry(a, b)
    for a, b in [(6, 11), (2, 36)]:  # isomorphic to a held-out torus: refused by default
        for entry in entries:
            with pytest.raises(C.HeldOut, match="isomorphic"):
                entry(a, b)


def test_the_summary_refuses_a_file_of_a_held_out_torus(tmp_path, monkeypatch):
    _forbid_computing(monkeypatch)
    for ell, m in [(2, 33), (33, 2), (12, 12)]:
        data = tmp_path / f"{ell}x{m}"
        C.write_torus(data, [_header(ell, m, 1), _class(ell, m, 0, 4, 6, [])])
        with pytest.raises(C.HeldOut):
            C.summarize(data)
        with pytest.raises(C.HeldOut):
            C.cross_torus([_header(ell, m, 1), _header(3, 10, 1)], [])
    # a stage-1 file whose rows claim another torus is refused too
    data = tmp_path / "mixed"
    C.write_torus(data, [_header(3, 9, 1), _class(3, 22, 0, 4, 6, [])])
    with pytest.raises(ValueError, match="another torus"):
        C.summarize(data)


def test_isomorphic_tori_are_refused_by_default():
    iso = [t for t in C.stage1_tori() if C.isomorphic_held_out(*t)]
    assert sorted(iso) == [(2, 36), (3, 26), (4, 14), (5, 14), (6, 11), (6, 13), (6, 16),
                           (7, 10)]  # fmt: skip
    assert C.isomorphic_held_out(6, 11) == [(2, 33), (3, 22)]
    for t in iso:
        with pytest.raises(C.HeldOut, match="isomorphic"):
            C.guard(*t)
        C.guard(*t, allow_isomorphic=True)
    assert not set(C.census_tori()) & set(iso)
    assert len(C.census_tori()) == 116 and len(C.census_tori(allow_isomorphic=True)) == 124
    held = set(_held_out())
    for tori in (C.census_tori(), C.census_tori(allow_isomorphic=True)):
        assert not {t for t in tori} & (held | {(b, a) for a, b in held})
        sizes = [a * b for a, b in tori]
        assert sizes == sorted(sizes, reverse=True)  # the largest first


def test_the_summary_does_not_place_a_code_on_a_held_out_torus(tmp_path, monkeypatch):
    calls = []
    real = C.retest.equivalence_key

    def spy(A, B, ell, m):
        calls.append((ell, m))
        return real(A, B, ell, m)

    monkeypatch.setattr(C.retest, "equivalence_key", spy)
    C.summarize(tmp_path)  # no data: nothing placed, nothing computed
    assert calls == []
    _synthetic(tmp_path)
    s = C.summarize(tmp_path)
    assert (12, 12) not in calls and set(calls) <= set(C.stage1_tori())
    gross = next(p for p in s["published"] if p["name"].startswith("[[288"))
    assert gross["status"].startswith("not placed") and "held out" in gross["status"]


# ---------------------------------------------------------------- distances and selection


def test_interval_and_compare():
    exact = {"status": "complete", "d": 6, "lower": 6, "upper": 6, "verified": True}
    optimal = {"status": "optimal", "d": 6, "lower": 6, "upper": 6, "verified": True}
    stopped = {"status": "timelimit", "d": None, "lower": 4, "upper": 8, "verified": True}
    assert C.compare(exact, optimal) == "agree"
    assert C.compare(exact, stopped) == "consistent"
    assert C.compare(exact, {**optimal, "d": 7, "lower": 7, "upper": 7}) == "disagree"
    # an unchecked witness bounds nothing
    assert C.interval({**stopped, "verified": False}) == (4, math.inf)
    assert C.interval({"status": "timelimit", "lower": None, "upper": None}) == (1, math.inf)
    # a failed witness leaves only the lower bound (census_torus reports the failure itself)
    assert C.compare({**exact, "verified": False, "upper": 3, "d": 3, "lower": 3},
                     {**stopped, "lower": 4}) == "consistent"  # fmt: skip
    assert C.compare({**exact, "upper": 3, "d": 3, "lower": 3}, {**stopped, "lower": 4}) == (
        "disagree"
    )
    # "agree" needs both witnesses to pass verify_witness
    assert C.compare({**exact, "verified": False}, optimal) == "consistent"
    assert C.compare(exact, {**optimal, "verified": False}) == "consistent"
    assert C.compare(exact, {**optimal, "verified": None}) == "consistent"
    # two searches compare the same way (the second search)
    assert C.compare(exact, {**exact, "kind": "X"}) == "agree"


def _row(i, k, d, status="complete"):
    return {"class": i, "k": k, "search": {"status": status, "d": d if status == "complete"
                                           else None}}  # fmt: skip


def test_ilp_selection():
    rows = [_row(0, 12, 6), _row(1, 8, 7), _row(2, 4, 6), _row(3, 8, None, "timelimit")]
    rows += [_row(i, 2, 4) for i in range(4, 50)]
    rows.append({"class": 50, "k": 2, "search": None})  # not searched (distance_kmin)
    chosen = C.ilp_selection(rows, 6, 6, 0.05)
    # 12 * 36 = 432 > 8 * 49 = 392: class 0 alone is best
    assert chosen[0] == "best" and chosen[3] == "timelimit"
    samples = [i for i, why in chosen.items() if why == "sample"]
    assert len(samples) == math.ceil(0.05 * 47) and 50 not in chosen
    assert chosen == C.ilp_selection(rows, 6, 6, 0.05)  # deterministic
    ties = [_row(0, 4, 6), _row(1, 4, 6), _row(2, 4, 4)]
    chosen = C.ilp_selection(ties, 3, 3, 0.05)
    assert chosen == {0: "best", 1: "best", 2: "sample"}  # at least one sample


def test_census_of_a_small_torus_end_to_end(tmp_path):
    lines = C.census_torus(3, 3, C.Options(search_limit=60, ilp_limit=60))
    header, rows = lines[0], lines[1:]
    assert header["type"] == "header" and header["classes"] == len(rows) == 4
    assert header["raw_codes"] == 81 and header["scip_fix"] == C.distance.SCIP_FIX
    assert header["search_c_sha256"] and header["census_c_sha256"] and header["solver"]
    assert header["problems"] == 0 and header["isomorphic_held_out"] == []
    for r in rows:
        assert r["search"]["status"] == "complete" and r["search"]["verified"]
        assert r["k_characters"] == r["k"] and r["weights"] == [3, 3]
        assert r["orbit_size"] * r["stabilizer"] == header["group_order"]
        assert 2 * sum(o["size"] * o["term"] for o in r["frobenius_orbits"]) == r["k"]
    checked = [r for r in rows if r["program"]]
    assert checked and all(r["crosscheck"] == "agree" for r in checked)
    assert all(r["recheck"] is None for r in rows) and header["rechecks"] == {}  # all agree
    path = C.write_torus(tmp_path, lines)
    assert path.name == "3x3.jsonl" and C.read_torus(path) == (header, rows)
    assert not list(tmp_path.glob(".*.tmp"))


def test_run_resumes_and_refuses_mixed_options(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(C, "census_tori", lambda allow_isomorphic=False: [(3, 5), (2, 3)])
    options = C.Options(search_limit=30, ilp_limit=30)
    C.run(tmp_path, 2, options)
    assert sorted(p.name for p in tmp_path.glob("*.jsonl")) == ["2x3.jsonl", "3x5.jsonl"]
    before = {p.name: p.read_text() for p in tmp_path.glob("*.jsonl")}
    C.run(tmp_path, 2, options)  # resume: nothing to do
    assert "0 tori to run" in capsys.readouterr().out
    assert {p.name: p.read_text() for p in tmp_path.glob("*.jsonl")} == before
    with pytest.raises(SystemExit, match="options"):
        C.run(tmp_path, 2, C.Options(search_limit=31, ilp_limit=30))
    header, rows = C.read_torus(tmp_path / "2x3.jsonl")
    assert header["classes"] == 0 and rows == []
    # allow_isomorphic says which tori run, not how: a later run with it resumes
    C.run(tmp_path, 2, C.Options(search_limit=30, ilp_limit=30, allow_isomorphic=True))
    assert "0 tori to run" in capsys.readouterr().out


def test_run_takes_a_relative_data_path_from_the_working_directory(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(C, "census_tori", lambda allow_isomorphic=False: [(2, 3)])
    monkeypatch.chdir(tmp_path)
    C.run(Path("relative"), 1, C.Options(search_limit=30, ilp_limit=30))
    assert "2x3 done" in capsys.readouterr().out
    assert [p.name for p in (tmp_path / "relative").glob("*.jsonl")] == ["2x3.jsonl"]
    assert not (HERE / "relative").exists()


def test_the_run_order_starts_with_the_costly_tori(monkeypatch):
    order = C.run_order(C.census_tori())
    assert order[: len(C.COSTLY)] == list(C.COSTLY)
    assert sorted(order) == sorted(C.census_tori())
    rest = order[len(C.COSTLY) :]
    assert [a * b for a, b in rest] == sorted((a * b for a, b in rest), reverse=True)
    seen = {}  # the run's default is 2 workers, one core each
    monkeypatch.setattr(C, "run", lambda data, workers, options: seen.update(workers=workers))
    C.main(["run"])
    assert seen == {"workers": 2}


# ---------------------------------------------------------------- structure


def test_the_gross_family_code_at_6x6():
    # [[72,12,6]]: A = x^3 + y + y^2, B = y^3 + x + x^2, of the family's form on 6 x 6
    found = C.classes(6, 6)
    key = C.retest.equivalence_key([[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]], 6, 6)
    c = next(c for c in found["classes"] if tuple(tuple(map(tuple, X)) for X in c["key"]) == key)
    assert c["k"] == 12
    group = len(C.automorphisms(6, 6)) * 36**2 * 2
    s = C.structure(c, 6, 6, group)
    # the same four characters of the 3 x 3 odd part, two with multiplicity 2 (examples/qec-bb)
    assert len(s["characters"]) == 4 and sorted(t for _, _, t in s["characters"]) == [1, 1, 2, 2]
    assert s["k_characters"] == 12 and s["weights"] == [3, 3]
    assert s["orbit_size"] * s["stabilizer"] == group
    assert s["aut_swapping"] >= 1  # x <-> y swaps A and B (l = m)


def test_frobenius_orbits_and_dilations():
    terms = [((1, 2), 1), ((2, 1), 1), ((1, 1), 2), ((2, 2), 2)]
    orbits = C.frobenius_orbits(terms, 6, 6)
    assert [(o["size"], o["term"]) for o in orbits] == [(2, 2), (2, 1)]
    # A = 1 + x + x^3 and B = 1 + y + y^3 on 7 x 7: the dilation by 2 sends the exponents
    # {0, 1, 3} to {0, 2, 6} = {0, 1, 3} - 1 (mod 7), a translate, in each variable; by 3, to
    # {0, 3, 2}, which is not
    d = C.dilations([[0, 0], [1, 0], [3, 0]], [[0, 0], [0, 1], [0, 3]], 7, 7)
    assert d["fixing"] == [2, 4] and d["swapping"] == []


# ---------------------------------------------------------------- the summary


def _header(ell, m, classes, **extra):
    return {"type": "header", "l": ell, "m": m, "n": 2 * ell * m, "raw_codes": 1,
            "raw_k_positive": classes, "classes": classes, "classes_by_k": {}, "crosschecks": {},
            "problems": 0, "seconds": 1.0, "options": C.Options().as_dict(),
            "isomorphic_held_out": [], **extra}  # fmt: skip


def _class(ell, m, i, k, d, key, status="complete", lower=None, upper=None, program=None,
           crosscheck=None, problems=()):  # fmt: skip
    search = {"status": status, "d": d if status == "complete" else None,
              "lower": d if status == "complete" else lower,
              "upper": d if status == "complete" else upper, "verified": True}  # fmt: skip
    return {"type": "class", "l": ell, "m": m, "n": 2 * ell * m, "class": i, "k": k, "size": 1,
            "A": [], "B": [], "key": key, "search": search, "program": program,
            "crosscheck": crosscheck, "problems": list(problems)}  # fmt: skip


def _synthetic(path):
    gross = C.retest.equivalence_key([[3, 0], [0, 1], [0, 2]], [[0, 3], [1, 0], [2, 0]], 6, 6)
    gross = [list(map(list, X)) for X in gross]
    other = [[[0, 0], [0, 1], [0, 2]], [[0, 0], [1, 0], [2, 0]]]
    best = {"program": {"reason": "best"}, "crosscheck": "agree"}
    stopped = {"status": "timelimit", "lower": 5, "upper": 9, "program": {"reason": "timelimit"},
               "crosscheck": "consistent"}  # fmt: skip
    wrong = {"program": {"reason": "sample"}, "crosscheck": "disagree",
             "problems": ["DISAGREEMENT: search (6, 6), program (7, 7)"]}  # fmt: skip
    six = [_class(6, 6, 0, 12, 6, gross, **best), _class(6, 6, 1, 4, 8, other),
           _class(6, 6, 2, 8, None, other, **stopped)]  # fmt: skip
    C.write_torus(path, [_header(6, 6, 3), *six])
    three = [_class(3, 12, 0, 16, 4, other), _class(3, 12, 1, 4, 6, other, **wrong)]
    C.write_torus(path, [_header(3, 12, 2), *three])
    C.write_torus(path, [_header(5, 7, 1), _class(5, 7, 0, 4, 4, other)])


def test_the_summary_on_synthetic_data(tmp_path):
    _synthetic(tmp_path)
    s = C.summarize(tmp_path)
    assert s["tori_done"] == 3 and s["classes"] == 6
    assert len(s["disagreements"]) == 1 and s["disagreements"][0]["l"] == 3
    assert s["crosschecks"] == {"agree": 1, "consistent": 1, "disagree": 1}
    f72 = next(f for f in s["frontier"] if f["n"] == 72)
    # scores at n = 72: 12*36/72 = 6, 4*64/72 = 3.6, 16*16/72 = 3.6, 4*36/72 = 2
    assert [(b["l"], b["m"], b["k"], b["d"]) for b in f72["best"]] == [(6, 6, 12, 6)]
    assert f72["best_d_by_k"]["4"]["d"] == 8 and f72["best_d_by_k"]["16"]["d"] == 4
    # the stopped class could still beat the best (8 * 81 / 72 = 9 > 6)
    assert [(o["l"], o["class"]) for o in f72["open"]] == [(6, 2)]
    published = {p["name"]: p for p in s["published"]}
    p72 = published["[[72,12,6]]"]
    assert p72["status"] == "in the census" and p72["rank_at_n"] == 1 and p72["d"] == 6
    assert p72["rank_in_torus"] == 1 and p72["classes_at_n"] == 5
    assert published["[[70,6,8]]"]["status"].startswith("not in the census")
    assert published["[[90,8,10]]"]["status"] == "torus not in the data"
    from io import StringIO

    out = StringIO()
    C.print_summary(s, out)
    text = out.getvalue()
    assert text.startswith("!!! DISAGREEMENTS") and "[[72,12,6]]" in text


def test_the_frontier_says_what_each_d_rests_on(tmp_path):
    other = [[[0, 0], [0, 1], [0, 2]], [[0, 0], [1, 0], [2, 0]]]

    def program(status, lower, upper, verified=True):
        return {"reason": "best", "status": status, "d": upper if status == "optimal" else None,
                "lower": lower, "upper": upper, "verified": verified}  # fmt: skip

    stopped = {"status": "timelimit", "crosscheck": "consistent"}
    wrong = {"crosscheck": "disagree", "problems": ["DISAGREEMENT: search (6, 6), program (7, 7)"]}
    rows = [
        _class(6, 6, 0, 12, 6, other, program=program("optimal", 6, 6), crosscheck="agree"),
        _class(6, 6, 1, 8, 8, other, program=program("timelimit", 5, 8), crosscheck="consistent"),
        # the search stopped and the program closed it
        _class(6, 6, 2, 4, None, other, lower=4, program=program("optimal", 7, 7), **stopped),
        # neither closed it alone; together they do
        _class(6, 6, 3, 4, None, other, lower=9, program=program("timelimit", 5, 9), **stopped),
        # the best score at n = 72 (16 * 36 / 72 = 8), but with a disagreement: left out
        _class(6, 6, 4, 16, 6, other, program=program("optimal", 7, 7), **wrong),
        # stopped with no logical found and no program: open
        _class(6, 6, 5, 4, None, other, status="timelimit", lower=3),
    ]
    rows[1]["recheck"] = {"outcome": "agree"}
    for r in rows[2:4] + rows[5:]:
        r["search"]["verified"] = None  # a stopped search with no witness
    C.write_torus(tmp_path, [_header(6, 6, len(rows)), *rows])
    s = C.summarize(tmp_path)
    (f,) = s["frontier"]
    assert f["excluded"] == [[6, 6, 4]] and f["exact"] == 4
    (best,) = f["best"]  # 8 * 64 / 72 = 7.1 > 12 * 36 / 72 = 6
    assert (best["class"], best["d"], best["d_by"]) == (1, 8, "search")
    assert best["crosscheck"] == "consistent"
    assert best["program"] == [5, 8] and best["recheck"] == "agree" and best["search_verified"]
    four = f["best_d_by_k"]["4"]
    assert four["d"] == 9 and [(c["class"], c["d_by"]) for c in four["codes"]] == [(3, "bounds")]
    assert C.established(rows[0]) == (6, "search, program")
    assert C.established(rows[2]) == (7, "program")
    assert C.established(rows[4]) == (None, None)
    assert [(o["class"], o["lower"], o["upper"]) for o in f["open"]] == [(5, 3, None)]
    from io import StringIO

    out = StringIO()
    C.print_summary(s, out)
    assert "[[72,8,8]]* 6x6#1" in out.getvalue() and "excluded 1" in out.getvalue()


def test_codes_equivalent_across_isomorphic_tori_are_matched(tmp_path, monkeypatch):
    # 3 x 10 and 5 x 6 are both Z_30: a 3 x 10 code carried by an isomorphism onto 5 x 6 is the
    # same code up to equivalence, and the summary must say so and count it once
    a, b = C.classes(3, 10)["classes"][:2]
    f = C.retest._isomorphisms((3, 10), (5, 6))[0]
    image = [C.retest._mapped(C.retest._reduce(P, 3, 10), f, 5, 6) for P in (a["A"], a["B"])]
    image = [[list(u) for u in P] for P in image]
    key = [list(map(list, X)) for X in C.retest.equivalence_key(*image, 5, 6)]

    def row(ell, m, i, c, A, B, key):
        r = _class(ell, m, i, c["k"], 6, key)
        return {**r, "A": A, "B": B}

    C.write_torus(tmp_path, [_header(3, 10, 2), row(3, 10, 0, a, a["A"], a["B"], a["key"]),
                             row(3, 10, 1, b, b["A"], b["B"], b["key"])])  # fmt: skip
    C.write_torus(tmp_path, [_header(5, 6, 1), row(5, 6, 0, a, *image, key)])
    s = C.summarize(tmp_path)
    (group,) = s["isomorphic_tori"]
    assert group["tori"] == [[3, 10], [5, 6]] and group["distinct"] == 2 and group["shared"] == 1
    f60 = next(f for f in s["frontier"] if f["n"] == 60)
    assert f60["classes"] == 3 and f60["distinct"] == 2
    best = {(x["l"], x["m"], x["class"]): x["same_as"] for x in f60["best"]}
    assert best.get((5, 6, 0)) == [[3, 10, 0]] or best.get((3, 10, 0)) == [[5, 6, 0]]
    # a code placed at n = 60 is ranked among the 2 distinct classes, not the 3 rows
    code = {"name": "test", "l": 5, "m": 6, "A": image[0], "B": image[1], "n": 60, "k": a["k"],
            "d": 6}  # fmt: skip
    monkeypatch.setattr(C, "published_codes", lambda: [code])
    (placed,) = C.summarize(tmp_path)["published"]
    assert placed["status"] == "in the census" and placed["classes_at_n"] == 2
    rank = 1 + (b["k"] > a["k"])
    assert placed["rank_at_n"] == rank and placed["d_by"] == "search"


def test_the_stabilizer_by_brute_force():
    # every element (φ, g, h, swap) of the equivalence group that fixes the pair (A, B)
    for ell, m in [(3, 3), (3, 6)]:
        found = C.classes(ell, m)
        auts = C.automorphisms(ell, m)
        group = len(auts) * (ell * m) ** 2 * 2
        shifts = [(g0, g1) for g0 in range(ell) for g1 in range(m)]

        def shifted(P, g, ell=ell, m=m):
            return frozenset(((p + g[0]) % ell, (q + g[1]) % m) for p, q in P)

        for c in found["classes"][:6]:
            A, B = (frozenset(map(tuple, C.retest._reduce(X, ell, m))) for X in (c["A"], c["B"]))
            count = 0
            for f in auts:
                fa, fb = (frozenset(C.retest._mapped(X, f, ell, m)) for X in (A, B))
                ga = [g for g in shifts if shifted(fa, g) in (A, B)]
                hb = [h for h in shifts if shifted(fb, h) in (A, B)]
                for g in ga:
                    for h in hb:
                        image = (shifted(fa, g), shifted(fb, h))
                        count += (image == (A, B)) + (image[::-1] == (A, B))
            s = C.structure(c, ell, m, group)
            assert s["stabilizer"] == count, (ell, m, c["class"])


def test_the_second_search_runs_where_the_program_does_not_agree(monkeypatch):
    # the program stopped with only a lower bound of 1: the best classes get the second search,
    # kind X from every qubit, which must agree with the first; the others get none
    def stopped(A, B, ell, m, limit, allow_isomorphic=False):
        return {"status": "timelimit", "d": None, "lower": 1, "upper": None, "witness": None,
                "verified": None, "k": bb.k_linalg(A, B, ell, m), "seconds": 0.0}  # fmt: skip

    monkeypatch.setattr(C, "program_distance", stopped)
    header, *rows = C.census_torus(3, 3, C.Options(search_limit=60, ilp_limit=60))
    best = [r for r in rows if r["program"] and r["program"]["reason"] == "best"]
    assert best and all(r["crosscheck"] == "consistent" for r in rows if r["program"])
    for r in rows:
        if r in best:
            assert r["recheck"]["kind"] == "X" and r["recheck"]["anchors"] == "all"
            assert r["recheck"]["outcome"] == "agree" and r["recheck"]["d"] == r["search"]["d"]
        else:
            assert r["recheck"] is None
    assert header["rechecks"] == {"agree": len(best)} and header["problems"] == 0


def test_a_failing_instrument_is_recorded_not_fatal(monkeypatch):
    real = C.class_distance

    def flaky(A, B, ell, m, *args, **kwargs):
        if A == C.classes(ell, m)["classes"][1]["A"] and B == C.classes(ell, m)["classes"][1]["B"]:
            raise RuntimeError("simulated failure")
        return real(A, B, ell, m, *args, **kwargs)

    monkeypatch.setattr(C, "class_distance", flaky)
    header, *rows = C.census_torus(3, 3, C.Options(search_limit=60, ilp_limit=60))
    bad = rows[1]
    assert bad["search"]["status"] == "error" and header["problems"] == 1
    assert any("simulated failure" in p for p in bad["problems"])
    # it goes to the program, which still bounds it, and nothing else is affected
    assert bad["program"]["reason"] == "search error" and bad["crosscheck"] == "consistent"
    assert all(r["search"]["status"] == "complete" for r in rows if r is not bad)
    # the program's optimum establishes its d, and the failure does not exclude it
    assert C.established(bad) == (bad["program"]["d"], "program") and not C._doubtful(bad)


def test_a_failing_program_is_recorded_not_fatal(monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("simulated program failure")

    monkeypatch.setattr(C, "program_distance", broken)
    header, *rows = C.census_torus(3, 3, C.Options(search_limit=60, ilp_limit=60))
    failed = [r for r in rows if r["program"]]
    assert failed and all(r["program"]["status"] == "error" for r in failed)
    assert header["problems"] == len(failed)
    assert all(r["problems"] == ["program failed: RuntimeError: simulated program failure"]
               for r in failed)  # fmt: skip
    assert all(C.established(r)[1] == "search" for r in rows)
