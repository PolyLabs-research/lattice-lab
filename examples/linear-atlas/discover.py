"""
Discovery for the linear-rule atlas: exact periods on small tori, and Kepler's laws for them.

    uv run python examples/linear-atlas/discover.py --workers 4

For each of the 42 shell rules (engine.rules()), the exact longest period on every n x n torus
from 8 to 60 (even n on the hexagon and triangle). Smaller tori are left out: there a shell at
distance 2 folds onto itself. Kepler's find_integer_laws (with the 1D linear rules' periods in its
vocabulary) is then asked for laws on three subsets, in this order: all n, n not a power of 2,
odd part at least 5. Kepler's proposal for a rule is the first subset giving a law confirmed by at
least MIN_CONFIRMED points, with every law it lists there that is confirmed as often. These rules
were fixed before any law was seen. Writes discovery.jsonl and proposals.json.
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import engine
from kepler import find_integer_laws

HERE = Path(__file__).resolve().parent
MIN_CONFIRMED = 10


def odd_part(n: int) -> int:
    return engine.odd_part(n)


SUBSETS = {
    "all n": lambda n: True,
    "n not a power of 2": lambda n: n & (n - 1) != 0,
    "odd part at least 5": lambda n: odd_part(n) >= 5,
}


def sizes(lattice: str) -> list[int]:
    return [n for n in range(8, 61) if engine.valid_size(lattice, n)]


def _job(task):
    lattice, shells, n = task
    return {
        "lattice": lattice,
        "shells": list(shells),
        "n": n,
        "period": engine.period(lattice, shells, n),
    }


def propose(points: list[tuple[int, int]]) -> dict:
    for subset, keep in SUBSETS.items():
        chosen = [(n, p) for n, p in points if keep(n)]
        laws = find_integer_laws([n for n, _ in chosen], [p for _, p in chosen])
        strong = [law for law in laws if law.confirmed_by >= MIN_CONFIRMED]
        if strong:
            return {
                "subset": subset,
                "points": len(chosen),
                "laws": [law.to_dict() for law in strong],
            }
    return {"subset": None, "laws": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    tasks = [(lat, shells, n) for lat, shells in engine.rules() for n in sizes(lat)]
    with Pool(args.workers) as pool:
        rows = list(pool.imap(_job, tasks, chunksize=4))
    (HERE / "discovery.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    proposals = {}
    for lattice, shells in engine.rules():
        key = engine.name(lattice, shells)
        points = [
            (r["n"], r["period"])
            for r in rows
            if r["lattice"] == lattice and tuple(r["shells"]) == shells
        ]
        proposals[key] = {"lattice": lattice, "shells": list(shells), **propose(points)}
        best = proposals[key]["laws"][0]["expression"] if proposals[key]["laws"] else None
        print(f"{key:28s} {str(proposals[key]['subset']):22s} {best}", flush=True)
    (HERE / "proposals.json").write_text(json.dumps(proposals, indent=1) + "\n")


if __name__ == "__main__":
    main()
