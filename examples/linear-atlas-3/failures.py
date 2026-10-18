"""
After round 3's verdict: what the 43 failures are. (Not registered.)

    uv run python examples/linear-atlas-3/failures.py

1. **VO+T13.** The three expectations in expectation.json, each against all 34 sizes.
2. **Every failure.** Computed directly from the eigenvalues (eigen.py's method):
   - how f factors over GF(2), by Kronecker substitution and recombination of up to three
     univariate pieces at a time (20 seconds at most; "None" where it did not finish);
   - how many distinct eigenvalues it has, up to Frobenius;
   - whether they all lie in a proper subfield F(2^e), or only in a subgroup of F(2^sord)*.
3. **The failure rate at each m**, VO+T13 apart. Is it a small-size effect?

Writes analysis.json.
"""

from __future__ import annotations

import collections
import itertools
import json
import signal
from pathlib import Path

import atlas3
import eigen
import sympy

HERE = Path(__file__).resolve().parent
_x = sympy.Symbol("x")
_X, _Y = sympy.symbols("X Y")


def _poly2(s):
    i0, j0 = min(i for i, _ in s), min(j for _, j in s)
    return sympy.Poly(sum(_X ** (i - i0) * _Y ** (j - j0) for i, j in s), _X, _Y, modulus=2)


def factor2d(f: frozenset) -> list[frozenset]:
    """The irreducible factors of f over GF(2), up to monomials. f(x, x^B) is factored, and
    products of its factors are tried as 2D divisors, smallest first."""
    f = set(f)
    i0, j0 = min(i for i, _ in f), min(j for _, j in f)
    base = 2 * (max(i for i, _ in f) - i0) + 1
    F = sympy.Poly(sum(_x ** ((i - i0) + base * (j - j0)) for i, j in f), _x, modulus=2)
    pieces = [p for p, e in F.factor_list()[1] for _ in range(e)]
    out, rest, free = [], _poly2(f), list(range(len(pieces)))
    for r in range(1, min(3, len(pieces)) + 1):  # products of up to three pieces
        for idx in itertools.combinations(free, r):
            if any(i not in free for i in idx):
                continue
            G = sympy.Poly(1, _x, modulus=2)
            for i in idx:
                G *= pieces[i]
            g = set()
            for (power,), c in G.terms():
                if int(c) % 2:
                    j, i = divmod(power, base)
                    g.add((i, j))
            if len(g) < 2:
                continue
            q, remainder = sympy.div(rest, _poly2(g), _X, _Y, modulus=2)
            if remainder.is_zero:
                out.append(frozenset(g))
                rest = q
                free = [i for i in free if i not in idx]
    if free:  # what is left: one factor, perhaps reducible
        out.append(frozenset((i, j) for (i, j), c in rest.terms() if int(c) % 2))
    return out


class _Slow(Exception):
    pass


def _alarm(signum, frame):
    raise _Slow


def factor2d_capped(f: frozenset, seconds: int = 20) -> list[frozenset] | None:
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(seconds)
    try:
        return factor2d(f)
    except _Slow:
        return None
    finally:
        signal.alarm(0)


def _normal(g: frozenset) -> frozenset:
    i0, j0 = min(i for i, _ in g), min(j for _, j in g)
    return frozenset((i - i0, j - j0) for i, j in g)


def dilation_pairs(factors: list[frozenset]) -> list[tuple[int, int, int]]:
    """(a, b, d): factor b is factor a in x^d, y^d, up to a monomial."""
    pairs = []
    for (a, ga), (b, gb) in itertools.permutations(enumerate(factors), 2):
        for d in (2, 3, 5, 7):
            if _normal(frozenset((d * i, d * j) for i, j in ga)) == _normal(gb):
                pairs.append((a, b, d))
    return pairs


def eigen_profile(f: frozenset, m: int) -> dict:
    mod, degree = eigen.field(m)
    top = degree
    zeta = [eigen._pow(2, e, mod, top) for e in range(m)]
    seen, values = set(), set()
    for j in range(m):
        for k in range(m):
            if (j, k) in seen:
                continue
            a, b = j, k
            while (a, b) not in seen:
                seen.add((a, b))
                a, b = 2 * a % m, 2 * b % m
            v = 0
            for x, y in f:
                v ^= zeta[(x * j + y * k) % m]
            values.add(v)
    orbits = set()
    for v in values:  # distinct eigenvalues up to Frobenius
        w, orbit = v, set()
        while w not in orbit:
            orbit.add(w)
            w = eigen._mul(w, w, mod, top)
        orbits.add(min(orbit))
    s = atlas3.atlas2.sord(m)
    p = eigen.odd_part(f, m)
    fields = [e for e in sympy.divisors(s) if e < s and (2**e - 1) % p == 0]
    return {
        "distinct eigenvalues up to Frobenius": len(orbits),
        "odd part": p,
        "full bound / odd part": (2**s - 1) // p,
        "all in a proper subfield": f"F(2^{min(fields)})" if fields else None,
    }


def main() -> None:
    ledger = [json.loads(line) for line in (HERE / "ledger.jsonl").read_text().splitlines()]
    verdict = ledger[-1]["body"]
    records = {
        (r["lattice"], tuple(r["shells"]), r["m"]): r
        for r in map(json.loads, (HERE / "records.jsonl").read_text().splitlines())
    }

    def actual(lattice, shells, m):
        r = records[(lattice, shells, m)]
        return int(r["predicted"]) if r.get("check", {}).get("is_odd_part") else r["odd part"]

    # 1. VO+T13's expectations
    expectation = json.loads((HERE / "expectation.json").read_text())
    vo = {}
    for version in ("version 1", "version 2", "version 3"):
        e = expectation[version]
        hits = [
            int(m)
            for m, v in e["expected odd part"].items()
            if int(v) == actual("triangle", ("VO", "T13"), int(m))
        ]
        computed = set(e["already computed when written"])
        later = [int(m) for m in e["expected odd part"] if int(m) not in computed]
        vo[version] = {
            "written": e["written"],
            "sizes": len(e["expected odd part"]),
            "match": len(hits),
            "sizes computed after it was written": len(later),
            "of those, match": len([m for m in later if m in hits]),
            "mismatches": sorted(int(m) for m in e["expected odd part"] if int(m) not in hits),
        }

    # 2. every failure
    rules = {p["body"]["rule"]: p["body"] for p in ledger if p["kind"] == "prediction"}
    failures = []
    for f in verdict["failures"]:
        body = rules[f["rule"]]
        poly = atlas3.polynomial(body["lattice"], tuple(body["shells"]))
        factors = factor2d_capped(poly)
        failures.append(
            {
                "rule": f["rule"],
                "m": f["m"],
                "predicted / odd part": int(f["predicted"]) // int(f["odd part"]),
                "terms": len(poly),
                "factors (terms each)": None
                if factors is None
                else sorted(len(g) for g in factors),
                "dilation pairs": None if factors is None else dilation_pairs(factors),
                **eigen_profile(poly, f["m"]),
            }
        )

    # 3. the rate at each m
    totals, fails = collections.Counter(), collections.Counter()
    for body in rules.values():
        for m in body["predictions"]:
            totals[int(m)] += 1
    for f in verdict["failures"]:
        if f["rule"] != "triangle VO+T13":
            fails[f["m"]] += 1
    rate = {
        str(m): {"failed": fails[m], "predictions": totals[m], "sord": atlas3.atlas2.sord(m)}
        for m in sorted(totals)
    }

    sE = atlas3.polynomial("triangle", ("E",))
    identity = atlas3.factor._times(set(sE), {(3 * i, 3 * j) for i, j in sE})
    vo["s(VO+T13) = s_E(x, y) s_E(x^3, y^3)"] = frozenset(identity) == atlas3.polynomial(
        "triangle", ("VO", "T13")
    )
    out = {
        "VO+T13 expectations": vo,
        "failures": failures,
        "failure rate by m (VO+T13 apart)": rate,
    }
    (HERE / "analysis.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(vo, indent=1))
    print("rate:", {m: (r["failed"], r["sord"]) for m, r in rate.items() if r["failed"]})
    for f in failures:
        print(f)


if __name__ == "__main__":
    main()
