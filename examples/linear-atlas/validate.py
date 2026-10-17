"""
The engine against LatticeLife, before it is trusted.

    uv run python examples/linear-atlas/validate.py

Two checks. For the eight shell rules LatticeLife can run (its parity rules, with and without the
cell itself), the longest period from LatticeLife's own simulation (the lcm of a single cell's, one
up and one down cell on the triangle) must equal the engine's exact period at every small size.
For all 42 rules, a direct simulation from the shells' offsets in LatticeLife's (row, column)
grid, independent of the group rings, must agree with the engine too. Writes validation.json.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import engine
import numpy as np
from latticelife.config import DEFAULT_CONFIG_PATH, load_config
from latticelife.core.rules import Rule
from latticelife.experiments.harness import single_species_session
from latticelife.experiments.periodicity import CycleDetector

HERE = Path(__file__).resolve().parent
SIZES = {"square": range(4, 15), "hexagon": range(6, 17, 2), "triangle": range(6, 17, 2)}
MODE = {("triangle", True): "edge+vertex", ("triangle", False): "edge"}


def simulate(lattice: str, rule: str, n: int, cell: int, mode: str | None) -> int:
    base = load_config(DEFAULT_CONFIG_PATH)
    config = base if mode is None else replace(base, grid=replace(base.grid, triangle_mode=mode))
    session = single_species_session(config, Rule.from_bs_string(rule), lattice, n, 0.0, 1)
    session.grid.occupancy[:] = 0
    session.grid.occupancy[cell] = 1
    detector = CycleDetector()
    detector.observe(session.grid.occupancy, 0)
    step = 0
    while True:
        session.step()
        step += 1
        found = detector.observe(session.grid.occupancy, step)
        if found is not None:
            return found[0]


def _neighbours(lattice: str, shells: tuple[str, ...], n: int) -> list[np.ndarray]:
    """For each shell term, the flat index of that neighbour of every cell (self included)."""
    r, c = np.divmod(np.arange(n * n), n)
    out = []
    for shell in shells:
        if shell == "self":
            out.append(np.arange(n * n))
        elif lattice == "square":
            for dr, dc in engine.SQUARE_SHELLS[shell]:
                out.append(((r + dr) % n) * n + (c + dc) % n)
        elif lattice == "hexagon":
            q, a = c, r - c // 2  # axial coordinates of each cell
            for dq, da in engine.HEXAGON_SHELLS[shell]:
                q2, a2 = q + dq, a + da
                out.append(((a2 + np.floor_divide(q2, 2)) % n) * n + q2 % n)
        else:
            up = (r + c) % 2 == 0
            offsets = engine.TRIANGLE_SHELLS[shell]
            for (ur, uc), (dr, dc) in zip(offsets["up"], offsets["down"], strict=True):
                rr = np.where(up, r + ur, r + dr)
                cc = np.where(up, c + uc, c + dc)
                out.append((rr % n) * n + cc % n)
    return out


def direct(lattice: str, shells: tuple[str, ...], n: int) -> int:
    """The longest period by brute force: lcm over a single cell (an up and a down cell)."""
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


def main() -> None:
    results = []
    for (lattice, shells), rule in engine.LATTICELIFE.items():
        mode = MODE.get((lattice, "VS" in shells)) if lattice == "triangle" else None
        cells = (0, 1) if lattice == "triangle" else (0,)
        for n in SIZES[lattice]:
            simulated = math.lcm(*(simulate(lattice, rule, n, c, mode) for c in cells))
            exact = engine.period(lattice, shells, n)
            results.append(
                {
                    "rule": engine.name(lattice, shells),
                    "latticelife": rule,
                    "n": n,
                    "simulated": simulated,
                    "exact": exact,
                    "agree": simulated == exact,
                }
            )
            print(json.dumps(results[-1]), flush=True)
    direct_checks = []
    for lattice, shells in engine.rules():
        for n in {"square": (5, 6, 7, 9, 10), "hexagon": (6, 8, 10), "triangle": (6, 8, 10)}[
            lattice
        ]:
            brute, exact = direct(lattice, shells, n), engine.period(lattice, shells, n)
            direct_checks.append(
                {
                    "rule": engine.name(lattice, shells),
                    "n": n,
                    "direct": brute,
                    "exact": exact,
                    "agree": brute == exact,
                }
            )
    (HERE / "validation.json").write_text(
        json.dumps({"latticelife": results, "direct": direct_checks}, indent=1) + "\n"
    )
    print(
        json.dumps(
            {
                "latticelife": len(results),
                "latticelife_disagree": [r for r in results if not r["agree"]],
                "direct": len(direct_checks),
                "direct_disagree": [r for r in direct_checks if not r["agree"]],
            }
        )
    )


if __name__ == "__main__":
    main()
