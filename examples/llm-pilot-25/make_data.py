"""
The data the m = 25 pilot's agent is given.

    uv run python examples/llm-pilot-25/make_data.py

- rules.json, shells.json: the atlas's 1,274 shell rules and their shells (as in the m = 37 pilot).
- remainder.csv: the 45 census entries the m = 37 pilot's mechanism left (odd m from 9 to 161),
  with their symmetries, free classes, distinct free values, the chance model's probability and
  the orchestrator's verdict (docs/census-remainder.md).
- family21.json, family25.json: the square family's unexplained confinements at m = 21 and 25,
  with the census's totals and the chance model's expectation.
- expected.csv: per census size, the atlas's unexplained confinements and the chance model's count.
- pilot4.md: the m = 37 pilot's proposal, which tools/halffrob.py implements.
"""

from __future__ import annotations

import json
import shutil

import cubes25

DATA = cubes25.HERE / "data"


def verdict(e: dict) -> str:
    if e["m"] in (13, 29):
        return "chance"
    if e["m"] == 115:
        return "a split the procedure mispredicts (four correlated rule-90 passes)"
    if e["symmetries_mod_m"] > e["lattice_symmetries"] and e["m"] in (21, 69):
        return "hidden symmetries mod m"
    if e["m"] == 21:
        return "coinciding eigenvalues; mild excess"
    return "open"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    for name in ("rules.json", "shells.json"):
        shutil.copy(cubes25.EX / "llm-pilot-37" / "data" / name, DATA / name)
    rows = [e | {"verdict": verdict(e)} for e in cubes25.remainder_rows()]
    cubes25.write_csv(DATA / "remainder.csv", rows)
    for m in (21, 25):
        saved = json.loads((cubes25.EX / "census-remainder" / f"family-{m}.json").read_text())
        hits = []
        for h in saved["hits"]:
            bits = cubes25.family.bits_of(h["orbits"])
            terms = sorted(map(list, cubes25.family.rule(bits)))
            hits.append({"id": bits, "orbits": h["orbits"], "terms": terms, "free": h["free"],
                         "chance": h["chance"]})  # fmt: skip
        out = {k: saved[k] for k in ("m", "population", "forced", "expected", "sd", "observed")}
        (DATA / f"family{m}.json").write_text(json.dumps(out | {"hits": hits}, indent=1) + "\n")
    sizes = [json.loads(line) for line in (cubes25.EX / "census-remainder" / "expected.jsonl")
             .read_text().splitlines()]  # fmt: skip
    cubes25.write_csv(DATA / "expected.csv", [
        {"m": s["m"], "rules": s["population"], "forced": len(s["forced"]),
         "expected": s["expected"], "sd": s["sd"], "observed": s["observed"]}
        for s in sizes if s["population"]])  # fmt: skip
    shutil.copy(cubes25.EX / "llm-pilot-37" / "submission" / "proposal.md", DATA / "pilot4.md")
    print(sorted(p.name for p in DATA.iterdir()))


if __name__ == "__main__":
    main()
