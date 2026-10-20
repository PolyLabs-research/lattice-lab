"""
The seventh pilot's registered held-out test: the ninth-power census at m = 37 at radius 6.

    uv run --no-sync python examples/llm-pilot-37c/study.py register
    uv run --no-sync python examples/llm-pilot-37c/study.py run
    uv run --no-sync lattice-lab verify --lab examples/llm-pilot-37c

The rule-4850 study (examples/rule-4850) refuted chance at radius 5: five new ninth-power rules
at 37 that the atlas procedure does not explain (four independent of 4850), against 0.0066
expected. This census takes the 28 orbits with 0 <= b <= a <= 6 and every rule that uses an
orbit of radius 6 (2^28 - 2^21 = 266,338,304), none of which the agent sees, and records every
one whose nonzero eigenvalues at 37 are all ninth powers, with

- what the atlas procedure (mechanisms 1 to 4) says, and whether that explains it (the same
  rule as the rule-4850 study: a predicted odd part dividing 29,127, or a split);
- whether it is an image of one of the five targets under a map in GL2(Z/37), or a target times
  a rule whose eigenvalues at 37 are all ninth powers (then it says nothing new);
- its 11 class logs mod 27.

The expectation, registered: a mechanism is at work, so the unexplained rules that are not images
or multiples of the targets exceed what chance gives, expected + 3 sd + 1, with the expected count
from each class's ninth-power rate measured on the same rules, independently (sd its square
root). The census is also the held-out set on which the judge measures the agent's condition.

Rules are enumerated in 127 chunks, one per nonempty set of radius-6 orbits, each over all 2^21
sets of smaller orbits; values at the 11 classes are xors of the orbits' (census.py).
"""

from __future__ import annotations

import itertools
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EX = HERE.parent
sys.path[:0] = [str(EX / "rule-4850"), str(EX / "linear-atlas-3")]

import atlas3  # noqa: E402
import census  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

RADIUS = 6
NINTH = (2**18 - 1) // 9
TARGETS = [4850, 699738, 985232, 1431278, 1968276]


def question() -> dict:
    return {
        "id": "pilot7-radius-6",
        "title": "Ninth-power rules at m = 37 among the radius-6 square rules (held out)",
        "statement": "Among the rules of the radius-6 square family that use an orbit of radius "
        "6, count those whose nonzero eigenvalues at m = 37 are all ninth powers, that the atlas "
        "procedure does not explain, and that are neither images under GL2(Z/37) nor ninth-power "
        "multiples of the five targets (4850, 699738, 985232, 1431278, 1968276). Expectation: more "
        "than chance, expected + 3 sd + 1 from the per-class null.",
        "source": "the rule-4850 study's refutation of chance at radius 5",
        "sizes": [37],
        "excluded_seen": ["the rules of radius at most 5 (the agent's data)"],
        "checker": "rule-4850/census.py (class values, discrete logs mod 27); atlas3.predict",
        "hypotheses": {"mechanism": "unexplained new rules > expected + 3 sd + 1"},
    }


def predictions() -> list[dict]:
    return [{"test": "unexplained ninth-power rules at 37 among new radius-6 rules",
             "predicted": "more than expected + 3 sd + 1 (a mechanism)"}]  # fmt: skip


def _ocoords(orbit) -> np.ndarray:
    zeta = [census.power(2, e) for e in range(census.M)]
    out = []
    for j, k in census.characters():
        v = 0
        for p, q in census.points(orbit):
            v ^= zeta[(p * j + q * k) % census.M]
        out.append(census.coord(v))
    return np.array(out, dtype=np.uint32)


def sweep(radius: int) -> dict:
    """The new rules of the radius family (those using an orbit of that radius): counts per q,
    per-class ninth-power counts, and the ids of the ninth-power rules."""
    orbs = census.orbits(radius)
    low = len(census.orbits(radius - 1))
    base = np.zeros((11, 1 << low), dtype=np.uint32)
    for i, o in enumerate(orbs[:low]):
        base[:, 1 << i : 2 << i] = base[:, : 1 << i] ^ _ocoords(o)[:, None]
    high = [_ocoords(o) for o in orbs[low:]]
    table = census.log_table()
    counts = Counter()
    class_ok = np.zeros(11, dtype=np.int64)
    nine = []
    for c in range(1, 1 << len(high)):
        off = np.zeros(11, dtype=np.uint32)
        for i, v in enumerate(high):
            if c >> i & 1:
                off ^= v
        logs = table[base ^ off[:, None]]
        zero = logs == census.ZERO
        ok9 = zero | (logs % 9 == 0)
        class_ok += ok9.sum(axis=1)
        for q in (3, 9, 27):
            counts[q] += int(np.all(zero | (logs % q == 0), axis=0).sum())
        idx = np.flatnonzero(np.all(ok9, axis=0))
        nine += [(c << low) | int(i) for i in idx]
    n = ((1 << len(high)) - 1) << low
    return {"rules": n, "counts": counts, "rates": class_ok / n, "nine": nine}


def logs_of(f) -> list[int]:
    zeta = [census.power(2, e) for e in range(census.M)]
    out = []
    for j, k in census.characters():
        v = 0
        for p, q in f:
            v ^= zeta[(p * j + q * k) % census.M]
        out.append(int(census.log_table()[census.coord(v)]))
    return out


def _support(f) -> frozenset:
    return frozenset((p % 37, q % 37) for p, q in f)


def image_of(f, g) -> list | None:
    """A map in GL2(Z/37) sending g's support onto f's, or None."""
    A, B = _support(g), _support(f)
    if len(A) != len(B):
        return None
    pts = sorted(A)
    p1 = pts[0]
    p2 = next(p for p in pts if (p1[0] * p[1] - p1[1] * p[0]) % 37)
    inv = pow((p1[0] * p2[1] - p1[1] * p2[0]) % 37, -1, 37)
    P = [[p2[1] * inv, -p2[0] * inv], [-p1[1] * inv, p1[0] * inv]]  # [p1 p2]^-1
    for i1, i2 in itertools.product(B, B):
        m = [[(i1[r] * P[0][c] + i2[r] * P[1][c]) % 37 for c in range(2)] for r in range(2)]
        if (m[0][0] * m[1][1] - m[0][1] * m[1][0]) % 37 == 0:
            continue
        image = frozenset(((m[0][0] * x + m[0][1] * y) % 37, (m[1][0] * x + m[1][1] * y) % 37)
                          for x, y in A)  # fmt: skip
        if image == B:
            return m
    return None


def quotient(f, g):
    """f / g exactly as Laurent polynomials over GF(2), or None."""
    import sympy

    x, y = sympy.symbols("x y")
    lo = 12  # shifts every exponent of these rules into [0, 24]
    F = sympy.Poly(sum(x ** (p + lo) * y ** (q + lo) for p, q in f), x, y, modulus=2)
    G = sympy.Poly(sum(x ** (p + 8) * y ** (q + 8) for p, q in g), x, y, modulus=2)
    q, r = sympy.div(F, G)
    if not r.is_zero:
        return None
    return frozenset((int(e[0]) - lo + 8, int(e[1]) - lo + 8)
                     for e, c in q.terms() if int(c) % 2)  # fmt: skip


def classify(rid: int, radius: int) -> dict:
    f = census.rule(rid, radius)
    odd, why = atlas3.predict(f, 37)
    explained = "splits" in why or (odd is not None and NINTH % odd == 0)
    out = {"test": "hit", "id": rid, "logs": logs_of(f), "procedure": why, "predicted_odd": odd,
           "explained": explained, "image_of": None, "multiple_of": None}  # fmt: skip
    if not explained:
        for t in TARGETS:
            g = census.rule(t, 5)
            if image_of(f, g) is not None:
                out["image_of"] = t
                break
            q = quotient(f, g)
            if q is not None and all(v == census.ZERO or v % 9 == 0 for v in logs_of(q)):
                out["multiple_of"] = t
                break
    return out


def execute(path: Path, workers: int) -> None:
    if path.exists() and path.read_text().strip():
        return
    start = time.time()
    s = sweep(RADIUS)
    rows = [classify(rid, RADIUS) for rid in s["nine"]]
    expected = float(s["rules"] * np.prod(s["rates"]))
    append_records(path, rows + [{
        "test": "summary", "new_rules": s["rules"],
        "confined": {str(q): s["counts"][q] for q in (3, 9, 27)},
        "class_ninth_rates": [round(float(r), 5) for r in s["rates"]],
        "expected_by_chance": expected, "sd": math.sqrt(expected),
        "seconds": round(time.time() - start, 1),
    }])  # fmt: skip


def decide(rows: list[dict], registered: list[dict]) -> dict:
    hits = [r for r in rows if r["test"] == "hit"]
    summary = next((r for r in rows if r["test"] == "summary"), None)
    new = [r for r in hits if not r["explained"] and not r["image_of"] and not r["multiple_of"]]
    bar = summary and summary["expected_by_chance"] + 3 * summary["sd"] + 1
    return {
        "missing": [] if summary else ["summary"],
        "ninth_power_new": len(hits),
        "explained": sum(r["explained"] for r in hits),
        "images": [r["id"] for r in hits if r["image_of"]],
        "multiples": [r["id"] for r in hits if r["multiple_of"]],
        "unexplained": len(new),
        "bar": bar,
        "mechanism": "supported" if summary and len(new) > bar else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
