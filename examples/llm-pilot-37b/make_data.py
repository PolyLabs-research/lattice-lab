"""
The data the sixth pilot's agent is given.

    uv run python examples/llm-pilot-37b/make_data.py

- rules.json, shells.json: the atlas's 1,274 shell rules and their shells (as in the m = 37 pilot).
- family.json: the square family's census at every size computed so far (m = 21, 25, and the
  fifth pilot's registered sizes 29 to 75): per size, the chance model's expectation and every
  confined rule the atlas procedure and forced subfields do not account for, each with what the
  fourth pilot's condition (tools/halffrob.py) and the fifth pilot's (tools/certificate.py) prove
  for it, and whether it is a target (unexplained at 37 or 61).
- targets.json: the 19 targets, with their polynomials, symmetries, free classes, distinct free
  values and chance (the 16 rules at 37, three of them also at 61).
- pilot4.md, pilot5.md: the two previous proposals, which tools/halffrob.py and
  tools/certificate.py implement.
"""

from __future__ import annotations

import json
import shutil

import cubes37b

DATA = cubes37b.HERE / "data"
P25 = cubes37b.PILOT25


def hit_row(h: dict, m: int, targets: set) -> dict:
    halffrob, certificate = cubes37b.conditions()
    f = cubes37b.family.rule(h["id"])
    return {
        "id": h["id"],
        "orbits": h["orbits"],
        "terms": sorted(map(list, f)),
        "free": h["free"],
        "chance": h["chance"],
        "pilot4_q": int(halffrob.condition(f, m)),
        "pilot5_q": int(certificate.condition(f, m)),
        "target": (m, h["id"]) in targets,
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    for name in ("rules.json", "shells.json", "pilot4.md"):
        shutil.copy(P25 / "data" / name, DATA / name)
    shutil.copy(P25 / "submission" / "proposal.md", DATA / "pilot5.md")
    targets = set(cubes37b.targets())
    sizes = []
    for m in (21, 25):
        saved = json.loads((P25 / "data" / f"family{m}.json").read_text())
        sizes.append({k: saved[k] for k in ("m", "population", "forced", "expected", "sd")}
                     | {"hits": [hit_row(h, m, targets) for h in saved["hits"]]})  # fmt: skip
    for m, r in sorted(cubes37b.records().items()):
        sizes.append({k: r[k] for k in ("m", "population", "forced", "expected", "sd")}
                     | {"hits": [hit_row(h, m, targets) for h in r["hits"]]})  # fmt: skip
    for s in sizes:
        s["observed"] = len(s["hits"])
        s["unexplained"] = sum(1 for h in s["hits"] if (h["pilot4_q"] * h["pilot5_q"]) % 3)
    (DATA / "family.json").write_text(json.dumps({"sizes": sizes}, indent=1) + "\n")

    rows = []
    for m, rid in sorted(targets):
        f = cubes37b.family.rule(rid)
        full = cubes37b.remainder.full_symmetries(f, m)
        free, distinct, chance = cubes37b.remainder.distinct_free(f, m, tuple(full))
        rows.append({"m": m, "id": rid, "orbits": [list(o) for o in cubes37b.family.orbits_of(rid)],
                     "terms": sorted(map(list, f)), "symmetries_mod_m": len(full),
                     "free_classes": free, "distinct_free_values": distinct,
                     "chance": chance})  # fmt: skip
    (DATA / "targets.json").write_text(json.dumps(rows, indent=1) + "\n")
    print(sorted(p.name for p in DATA.iterdir()), len(rows), "targets")


if __name__ == "__main__":
    main()
