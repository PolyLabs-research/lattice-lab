"""
Parity rules on LatticeLife's hexagonal and triangular lattices: simulate, then ask Kepler.

    uv run python examples/parity-lattices/discover.py

A cell's next state is the parity of its live neighbours:

    hexagon                 B135/S135                       6 neighbours
    triangle, edge          B13/S13                         3 neighbours
    triangle, edge+vertex   B1,3,5,7,9,11/S1,3,5,7,9,11     12 neighbours

On an n x n torus (n even: both lattices alternate across columns), from a single live cell (on
the triangular lattice, one up and one down cell: the two kinds of cell), every rule is linear,
so the torus's longest period is the lcm of those single cells' periods. Writes discovery.jsonl
(one record per lattice and size) and laws.json (Kepler's find_integer_laws on the periods).
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

from kepler import find_integer_laws
from latticelife.config import DEFAULT_CONFIG_PATH, load_config
from latticelife.core.rules import Rule
from latticelife.experiments.harness import single_species_session
from latticelife.experiments.periodicity import CycleDetector

HERE = Path(__file__).resolve().parent
LATTICES = {
    "hexagon": ("hexagon", None, "B135/S135"),
    "triangle-edge": ("triangle", "edge", "B13/S13"),
    "triangle-edge+vertex": ("triangle", "edge+vertex", "B1,3,5,7,9,11/S1,3,5,7,9,11"),
}
SIZES = list(range(6, 61, 2))
CAP = 300_000


def single_cell(lattice: str, n: int, cell: int, cap: int = CAP):
    shape, mode, rule = LATTICES[lattice]
    base = load_config(DEFAULT_CONFIG_PATH)
    config = base if mode is None else replace(base, grid=replace(base.grid, triangle_mode=mode))
    session = single_species_session(config, Rule.from_bs_string(rule), shape, n, 0.0, 1)
    session.grid.occupancy[:] = 0
    session.grid.occupancy[cell] = 1
    detector = CycleDetector()
    detector.observe(session.grid.occupancy, 0)
    for step in range(1, cap):
        session.step()
        found = detector.observe(session.grid.occupancy, step)
        if found is not None:
            return {"period": found[0], "transient": found[1]}
    return None


def main() -> None:
    records = []
    for lattice in LATTICES:
        for n in SIZES:
            cells = (
                {"cell": 0} if lattice == "hexagon" else {"up": 0, "down": 1}
            )  # (0,0) up, (0,1) down
            starts = {kind: single_cell(lattice, n, index) for kind, index in cells.items()}
            period = math.lcm(*(s["period"] for s in starts.values()))
            transient = max(s["transient"] for s in starts.values())
            records.append(
                {
                    "lattice": lattice,
                    "n": n,
                    "starts": starts,
                    "period": period,
                    "transient": transient,
                }
            )
    (HERE / "discovery.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    laws = {}
    for lattice in LATTICES:
        data = [(r["n"], r["period"]) for r in records if r["lattice"] == lattice]
        laws[lattice] = {}
        for label, keep in (
            ("all even n", lambda n: True),
            ("n not a power of 2", lambda n: n & (n - 1)),
            ("odd part at least 5", lambda n: n // (n & -n) >= 5),
        ):
            subset = [(n, p) for n, p in data if keep(n)]
            found = find_integer_laws([n for n, _ in subset], [p for _, p in subset])
            laws[lattice][label] = [law.to_dict() for law in found[:3]]
    (HERE / "laws.json").write_text(json.dumps(laws, indent=1) + "\n")
    for lattice, by_set in laws.items():
        for label, found in by_set.items():
            best = found[0] if found else None
            print(
                f"{lattice:22s} {label:20s}",
                (best["expression"], best["determined_by"], best["confirmed_by"])
                if best
                else "no law",
            )


if __name__ == "__main__":
    main()
