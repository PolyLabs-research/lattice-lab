"""
The census remainder, entry by entry, and size by size.

    uv run --no-sync python examples/census-remainder/findings.py

For each of the 45 census entries pilot 4's condition left (llm-pilot-37: data/unexplained.csv,
less judgements/round-2.json's covered rows): the rule's symmetries mod m (the lattice's, and
all of GL2(Z/m)), its free classes and their distinct values with the full symmetries, and the
chance model's probability. Then, per size, the atlas's expected and observed counts
(expected.jsonl) and the full square family's (family-<m>.json). Writes findings.json.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import remainder
from remainder import census

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent / "llm-pilot-37"


def remaining() -> list[tuple[int, str, str]]:
    judged = json.loads((PILOT / "judgements" / "round-2.json").read_text())
    covered = {tuple(r) for r in judged["mechanism"]["census_covered_rows"]["train"]}
    with open(PILOT / "data" / "unexplained.csv") as f:
        rows = [(int(r["m"]), r["lattice"], r["shells"]) for r in csv.DictReader(f)]
    return [r for r in rows if r not in covered]


def main() -> None:
    polys = {(lattice, "+".join(shells)): f for lattice, shells, f in census.rules()}
    entries = []
    for m, lattice, shells in remaining():
        f = polys[(lattice, shells)]
        lattice_sym = remainder.symmetries(f, m)
        full = remainder.full_symmetries(f, m) if m <= 69 else lattice_sym
        free, distinct, chance = remainder.distinct_free(f, m, tuple(full))
        entry = {"m": m, "lattice": lattice, "shells": shells}
        entry |= {"lattice_symmetries": len(lattice_sym), "symmetries_mod_m": len(full)}
        entry |= {"free": free, "distinct_free_values": distinct, "chance": chance}
        entries.append(entry)
    sizes = [json.loads(line) for line in (HERE / "expected.jsonl").read_text().splitlines()]
    family = {}
    for path in sorted(HERE.glob("family-*.json")):
        d = json.loads(path.read_text())
        family[d["m"]] = {k: d[k] for k in ("population", "forced", "expected", "sd", "observed")}
    keys = ("m", "population", "expected", "sd", "observed")
    rows = [
        {k: s[k] for k in keys} | {"forced": len(s["forced"])} for s in sizes if s["population"]
    ]
    out = {"entries": entries, "sizes": rows, "family": family}
    (HERE / "findings.json").write_text(json.dumps(out, indent=1) + "\n")
    print("| m | rule | symmetries (lattice / mod m) | free | distinct | chance |")
    for e in entries:
        print(f"| {e['m']} | {e['lattice']} {e['shells']} | {e['lattice_symmetries']} / "
              f"{e['symmetries_mod_m']} | {e['free']} | {e['distinct_free_values']} | "
              f"{e['chance']:.2g} |")  # fmt: skip
    print("\n| m | rules | forced | expected | observed |")
    for s in out["sizes"]:
        if s["expected"] > 0.05 or s["observed"] or s["forced"]:
            expected = f"{s['expected']} ± {s['sd']}"
            print(
                f"| {s['m']} | {s['population']} | {s['forced']} | {expected} | {s['observed']} |"
            )
    for m, d in family.items():
        print(f"family m = {m}: {d}")


if __name__ == "__main__":
    main()
