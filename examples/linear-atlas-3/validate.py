"""
Before round 3 is registered: the new shells, the odd-part check, and the procedure on old data.

    uv run python examples/linear-atlas-3/validate.py

1. **The new shells.** For rules using each new shell, on all three lattices, the engine's exact
   period (atlas3.build, atlas2.Exact) must equal a direct simulation from the offsets in
   LatticeLife's (row, column) grid, the method of examples/linear-atlas/validate.py.
2. **The odd-part check.** atlas3.OddExact's odd part must equal the odd part of
   atlas2.Exact's period, and its check must accept that value.
3. **The procedure on data it was not built from.** predict is applied to every record of rounds
   1 and 2 and to round 1's discovery data. On the square, it predicts the period at odd n. On
   the hexagon and triangle, it predicts the odd part of each period, at the odd part of n.
   Agreements and disagreements are counted and listed, not judged.

Writes validation.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import atlas3
import numpy as np

HERE = Path(__file__).resolve().parent
atlas2, engine = atlas3.atlas2, atlas3.engine
ATLAS = atlas3.ROOT / "linear-atlas"


def _neighbours(lattice: str, shells: tuple[str, ...], n: int) -> list[np.ndarray]:
    r, c = np.divmod(np.arange(n * n), n)
    out = []
    for shell in shells:
        if shell == "self":
            out.append(np.arange(n * n))
        elif lattice == "square":
            for dr, dc in atlas3.SQUARE[shell]:
                out.append(((r + dr) % n) * n + (c + dc) % n)
        elif lattice == "hexagon":
            q, a = c, r - c // 2
            for dq, da in atlas3.HEXAGON[shell]:
                q2, a2 = q + dq, a + da
                out.append(((a2 + np.floor_divide(q2, 2)) % n) * n + q2 % n)
        else:
            up = (r + c) % 2 == 0
            offsets = atlas3.TRIANGLE[shell]
            for (ur, uc), (dr, dc) in zip(offsets["up"], offsets["down"], strict=True):
                rr = np.where(up, r + ur, r + dr)
                cc = np.where(up, c + uc, c + dc)
                out.append((rr % n) * n + cc % n)
    return out


def direct(lattice: str, shells: tuple[str, ...], n: int) -> int:
    terms = _neighbours(lattice, shells, n)
    periods = []
    for cell in (0, 1) if lattice == "triangle" else (0,):
        state = np.zeros(n * n, dtype=np.uint8)
        state[cell] = 1
        seen, t = {}, 0
        while state.tobytes() not in seen:
            seen[state.tobytes()] = t
            new = np.zeros_like(state)
            for index in terms:
                new ^= state[index]
            state, t = new, t + 1
        periods.append(t - seen[state.tobytes()])
    return math.lcm(*periods)


def exact_period(lattice: str, shells: tuple[str, ...], n: int) -> int:
    return atlas2.Exact(lattice, *atlas3.build(lattice, shells, n), n).period()


def odd(p: int) -> int:
    return p // (p & -p)


def shells_check() -> list[dict]:
    sizes = {"square": (7, 8, 9, 10), "hexagon": (8, 10, 12), "triangle": (8, 10, 12)}
    rules = {
        "square": [("L8",), ("M8",), ("E4",), ("L8", "self"), ("N4", "M8"), ("D4", "E4", "self")],
        "hexagon": [
            ("H4",),
            ("H5",),
            ("H13",),
            ("H4", "self"),
            ("H1", "H13"),
            ("H2", "H5", "self"),
        ],
        "triangle": [
            ("T7",),
            ("T9",),
            ("T13",),
            ("T7", "self"),
            ("E", "T13"),
            ("VS", "T9", "self"),
        ],
    }
    out = []
    for lattice, chosen in rules.items():
        for shells in chosen:
            for n in sizes[lattice]:
                a, b = direct(lattice, shells, n), exact_period(lattice, shells, n)
                out.append(
                    {
                        "rule": atlas3.name(lattice, shells),
                        "n": n,
                        "direct": a,
                        "exact": b,
                        "agree": a == b,
                    }
                )
    return out


def odd_check() -> list[dict]:
    out = []
    for lattice in ("square", "hexagon", "triangle"):
        for shells in atlas3.new_rules(lattice)[::15]:
            for n in (12, 18, 20) if lattice != "square" else (11, 12, 15):
                p = exact_period(lattice, shells, n)
                e = atlas3.OddExact(lattice, shells, n)
                o = e.odd_part()
                out.append(
                    {
                        "rule": atlas3.name(lattice, shells),
                        "n": n,
                        "period": p,
                        "odd part": o,
                        "agree": o == odd(p) and e.check(o)["is_odd_part"],
                    }
                )
    return out


def old_data() -> dict:
    """predict against rounds 1 and 2 (records and discovery), at odd parts."""
    rows = []
    for line in (ATLAS / "discovery.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows.append((r["lattice"], tuple(r["shells"]), r["n"], r["period"], "round 1 discovery"))
    verdict1 = json.loads((ATLAS / "ledger.jsonl").read_text().splitlines()[-1])["body"]["rules"]
    for line in (ATLAS / "records.jsonl").read_text().splitlines():
        r = json.loads(line)
        good = [int(v) for v, c in r["checks"].items() if c["is_period"]]
        period = good[0] if good else r["period"]
        rows.append((r["lattice"], tuple(r["shells"]), r["n"], period, "round 1 test"))
    assert verdict1
    for line in (atlas3.ROOT / "linear-atlas-2" / "records.jsonl").read_text().splitlines():
        r = json.loads(line)
        if "check" not in r:
            period = r["period"]
        else:
            period = int(r["predicted"]) if r["check"]["is_period"] else r["period"]
        rows.append((r["lattice"], tuple(r["shells"]), r["n"], period, "round 2"))
    agree, disagree, none = 0, [], 0
    for lattice, shells, n, period, source in rows:
        m = engine.odd_part(n)
        if m < 9:
            continue
        f = atlas3.polynomial(lattice, shells)
        value, why = atlas3.predict(f, m)
        if value is None:
            none += 1
        elif value == odd(period):
            agree += 1
        else:
            disagree.append(
                {
                    "rule": atlas3.name(lattice, shells),
                    "n": n,
                    "m": m,
                    "predicted": value,
                    "odd part": odd(period),
                    "why": why,
                    "source": source,
                }
            )
    return {"agree": agree, "disagree": disagree, "no prediction": none}


def main() -> None:
    shells = shells_check()
    print("shells:", sum(r["agree"] for r in shells), "of", len(shells), flush=True)
    odd_parts = odd_check()
    print("odd parts:", sum(r["agree"] for r in odd_parts), "of", len(odd_parts), flush=True)
    old = old_data()
    print("old data: agree", old["agree"], "no prediction", old["no prediction"], flush=True)
    for d in old["disagree"]:
        print("  disagree", d)
    (HERE / "validation.json").write_text(
        json.dumps({"shells": shells, "odd parts": odd_parts, "old data": old}, indent=1) + "\n"
    )


if __name__ == "__main__":
    main()
