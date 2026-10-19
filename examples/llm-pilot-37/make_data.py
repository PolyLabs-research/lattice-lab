"""
The data the m = 37 pilot's agent is given.

    uv run python examples/llm-pilot-37/make_data.py

- data/rules.json: all 1,274 shell rules of the atlas (atlas3.all_rules on the three lattices):
  lattice, shells, and the rule's Laurent polynomial as exponent pairs. On the triangle it is s,
  with M^2 = s I. Square and hexagon polynomials are in the atlas's own coordinates (axial on the
  hexagon), so all three live on the torus (Z/m)^2 the same way.
- data/shells.json: each shell's translations, as the atlas defines them.
- data/census37.csv: every rule at m = 37: the odd part of its period, whether every nonzero
  eigenvalue is a cube, and the atlas procedure's prediction and the step that decided it.
- data/unexplained.csv: every (rule, m) with m odd in TRAIN at which every nonzero eigenvalue is a
  cube and the procedure does not account for it (census.unexplained).
"""

from __future__ import annotations

import csv
import json

import census
from census import atlas3, eigen

TRAIN = (9, 161)


def main() -> None:
    out = census.HERE / "data"
    out.mkdir(exist_ok=True)
    rules = [
        {"id": i, "lattice": lattice, "shells": list(shells), "terms": sorted(map(list, f))}
        for i, (lattice, shells, f) in enumerate(census.rules())
    ]
    (out / "rules.json").write_text(json.dumps(rules) + "\n")
    shells = {lattice: {name: [list(t) for t in sh] if not isinstance(sh, dict)
                        else {k: [list(t) for t in v] for k, v in sh.items()}
                        for name, sh in atlas3.SHELLS[lattice].items()}
              for lattice in census.LATTICES}  # fmt: skip
    (out / "shells.json").write_text(json.dumps(shells, indent=1) + "\n")

    m = 37
    _, _, N, _, _ = census.setup(m)
    with open(out / "census37.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "lattice", "shells", "odd_part", "all_cubes", "predicted", "step"])
        for i, (lattice, shells, poly) in enumerate(census.rules()):
            predicted, step = atlas3.predict(poly, m)
            w.writerow([i, lattice, "+".join(shells), eigen.odd_part(poly, m),
                        int(census.confined(poly, m, 3)), predicted, step])  # fmt: skip
    # census-train.jsonl is run_census.py's output over TRAIN. Its run predates the twisted-power
    # check in census.explained, so each row is checked again here.
    runs = {}
    for line in (census.HERE / "census-train.jsonl").read_text().splitlines():
        r = json.loads(line)
        runs[r["m"]] = r["unexplained"]
    missing = [m for m in census.cube_sizes(*TRAIN) if m not in runs]
    if missing:
        raise SystemExit(f"census-train.jsonl lacks m = {missing}")
    polys = {(lat, "+".join(sh)): (sh, f) for lat, sh, f in census.rules()}
    rows = []
    for m in sorted(runs):
        for row in runs[m]:
            shells, f = polys[(row["lattice"], row["shells"])]
            if not census.explained(f, m, row["q"], (row["lattice"], shells)):
                rows.append(row)
    with open(out / "unexplained.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["m", "q", "lattice", "shells", "call"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rules)} rules; {len(rows)} unexplained cube confinements at odd m in {TRAIN}")


if __name__ == "__main__":
    main()
