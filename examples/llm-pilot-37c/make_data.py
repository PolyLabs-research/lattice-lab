"""
The seventh pilot's data (data/), from the earlier pilots' files and two censuses at m = 37.

    uv run --no-sync python examples/llm-pilot-37c/make_data.py

- rules.json, shells.json, family.json, pilot4.md, pilot5.md: the sixth pilot's data, as it had
  them (the atlas's rules and shells; the square family's cube census at m = 21, 25 and 29 to 75;
  the fourth and fifth pilots' proposals);
- family_77_125.json: the sixth pilot's registered cube census at the 17 odd m from 77 to 125;
- pilot6.md: the sixth pilot's proposal (unit times a power), whose condition is
  tools/unitpower.py;
- ninth37.json: the ninth-power census at 37 of the square family at radius 4 (32,767 rules) and
  of the new rules at radius 5 (2,064,384, those using an orbit of radius 5): counts, the class
  characters, each class's rate of ninth powers, and every ninth-power rule with its 11 class
  logs mod 27, what the atlas procedure says, and whether it is explained;
- targets.json: the five targets (4850, 699738, 985232, 1431278, 1968276) and 482758, which is
  4850 times rule 7 and so not a target;
- consultation-1.md, consultation-2.md: two consultations of Claude Fable on rule 4850
  (consultations/2026-10-20-rule-4850), verbatim.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EX = HERE.parent
REPO = EX.parent
sys.path[:0] = [str(HERE / "tools"), str(EX / "linear-atlas-3")]

import atlas3  # noqa: E402
import census37  # noqa: E402

TARGETS = [4850, 699738, 985232, 1431278, 1968276]
DERIVED = {482758: "4850 times rule 7 = (1 + a)(1 + b), whose values are ninth powers at 37"}
NINTH = (2**18 - 1) // 9


def explain(f: frozenset) -> tuple[str, bool]:
    odd, why = atlas3.predict(f, 37)
    return why, "splits" in why or (odd is not None and NINTH % odd == 0)


def ninth_census() -> dict:
    out = {"m": 37, "characters": census37.characters(), "families": []}
    for radius, lo in ((4, 1), (5, 1 << 15)):
        logs = census37.class_logs(radius)
        ids = np.arange(logs.shape[1])
        new = ids >= lo
        masks = {q: census37.confined(logs, q) & new for q in (3, 9, 27)}
        ok9 = (logs == census37.ZERO) | (logs % 9 == 0)
        hits = []
        for rid in map(int, np.flatnonzero(masks[9])):
            f = census37.rule(rid, radius)
            why, explained = explain(f)
            role = ("target" if rid in TARGETS else "derived" if rid in DERIVED
                    else "explained" if explained else "unexplained")  # fmt: skip
            hits.append({
                "id": rid, "orbits": [list(o) for i, o in enumerate(census37.orbits(radius))
                                      if rid >> i & 1],
                "logs": [None if v == census37.ZERO else int(v) for v in logs[:, rid]],
                "q27": bool(masks[27][rid]), "procedure": why, "explained": explained,
                "role": role,
            })  # fmt: skip
        out["families"].append({
            "radius": radius, "rules": int(new.sum()),
            "note": "all rules" if radius == 4 else "new rules only: those using a radius-5 orbit",
            "confined": {str(q): int(masks[q].sum()) for q in (3, 9, 27)},
            "class_ninth_rates": [round(float(r), 4) for r in ok9[:, new].mean(axis=1)],
            "ninth_power_rules": hits,
        })  # fmt: skip
    return out


def main() -> None:
    data = HERE / "data"
    data.mkdir(exist_ok=True)
    old = EX / "llm-pilot-37b" / "data"
    for name in ["rules.json", "shells.json", "family.json", "pilot4.md", "pilot5.md"]:
        shutil.copy(old / name, data / name)
    shutil.copy(EX / "llm-pilot-37b" / "submission" / "proposal.md", data / "pilot6.md")
    rows = [json.loads(line) for line in
            (EX / "llm-pilot-37b" / "records.jsonl").read_text().splitlines()]  # fmt: skip
    (data / "family_77_125.json").write_text(json.dumps({"sizes": rows}, indent=1) + "\n")
    ninth = ninth_census()
    (data / "ninth37.json").write_text(json.dumps(ninth, indent=1) + "\n")
    by_id = {h["id"]: h for fam in ninth["families"] for h in fam["ninth_power_rules"]}
    targets = []
    for rid in TARGETS + list(DERIVED):
        h = by_id[rid]
        radius = 4 if rid < 1 << 15 else 5
        targets.append({
            "m": 37, "id": rid, "radius": radius, "orbits": h["orbits"],
            "terms": sorted(map(list, census37.rule(rid, radius))), "logs": h["logs"],
            "target": rid in TARGETS, "note": DERIVED.get(rid, ""),
        })  # fmt: skip
    (data / "targets.json").write_text(json.dumps(targets, indent=1) + "\n")
    consult = REPO / "consultations" / "2026-10-20-rule-4850" / "round-1"
    for k in (1, 2):
        record = json.loads((consult / f"fable-r{k}.json").read_text())
        head = (f"# Consultation {k}: Claude Fable on rule 4850 ({record['finished'][:10]})\n\n"
                "Asked through the API, with code execution, at effort xhigh, independently of "
                "the other consultation. Its JSON block of identities was checked by machine: "
                "every one holds. Verbatim below.\n\n---\n\n")  # fmt: skip
        (data / f"consultation-{k}.md").write_text(head + record["text"].rstrip() + "\n")
    print({fam["radius"]: fam["confined"] for fam in ninth["families"]},
          {h["id"]: h["role"] for fam in ninth["families"] for h in fam["ninth_power_rules"]
           if h["role"] != "explained"})  # fmt: skip


if __name__ == "__main__":
    main()
