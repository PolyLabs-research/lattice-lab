"""
The orchestrator's side of the m = 25 pilot: the square family's census, the judge's target
rules and evaluation sets.

The family is every symmetric square rule within distance 4 (tools/family.py: 32,767 unions of
D4 orbits). census(m) lists the family rules confined to the cubes at m that no known mechanism
of the atlas procedure accounts for, with the chance model's expectation, using the census of
the m = 37 pilot (llm-pilot-37/census.py) and the remainder's model
(census-remainder/remainder.py). The procedure's slow steps (atlas3's 1D split search and root
test) do not depend on m, so they are cached across sizes.
"""

from __future__ import annotations

import csv
import functools
import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EX = HERE.parent
sys.path.insert(0, str(EX / "census-remainder"))

import atlas3  # noqa: E402
import remainder  # noqa: E402
from remainder import census  # noqa: E402


def _tool(name: str):
    """A sandbox tool, loaded under its own name so it cannot shadow the atlas's modules."""
    spec = importlib.util.spec_from_file_location(f"pilot25_{name}", HERE / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


family = _tool("family")

_split = atlas3.factor.split
atlas3.factor.split = functools.lru_cache(maxsize=None)(lambda f: _split(set(f)))
atlas3.factor.split = (lambda cached: lambda f: cached(frozenset(f)))(atlas3.factor.split)
atlas3.root = functools.lru_cache(maxsize=None)(atlas3.root)

# The open question: the rules confined at m = 25 beyond chance (docs/census-remainder.md).
ATLAS25 = [("triangle", "E+T7+self"), ("hexagon", "H1+H3+H13"), ("hexagon", "H3+H4+H5")]


def family_hits(m: int) -> list[int]:
    """The family's unexplained confinements at m, from a saved census (family-<m>.json here or in
    census-remainder), as rule ids."""
    for path in (HERE / "data" / f"family{m}.json", EX / "census-remainder" / f"family-{m}.json"):
        if path.exists():
            hits = json.loads(path.read_text())["hits"]
            return sorted(h["id"] if "id" in h else family.bits_of(h["orbits"]) for h in hits)
    raise FileNotFoundError(f"no family census at m = {m}")


def census_at(m: int) -> dict:
    """The family's census at m: every unexplained confinement, and the chance model's count."""
    N = 2 ** census.eigen.field(m)[1] - 1
    mean = var = 0.0
    population, forced, hits = 0, 0, []
    for bits, f in family.rules():
        predicted, _ = atlas3.predict(f, m)
        if predicted is None or (N // 3) % predicted == 0:
            continue
        a = remainder.analyse(f, m)
        population += 1
        if a["forced"]:
            forced += 1
            continue
        mean += a["chance"]
        var += a["chance"] * (1 - a["chance"])
        if a["cubes"]:
            hits.append({"id": bits, "orbits": [list(o) for o in family.orbits_of(bits)],
                         "free": a["free"], "chance": a["chance"]})  # fmt: skip
    return {"m": m, "population": population, "forced": forced, "expected": mean,
            "sd": var**0.5, "observed": len(hits), "hits": hits}  # fmt: skip


SAMPLE_SEED, SAMPLE_SIZE = 25, 2000


@functools.cache
def sample() -> tuple[int, ...]:
    """A fixed random sample of family rules, for the judge's soundness checks."""
    rng = random.Random(SAMPLE_SEED)
    return tuple(sorted(rng.sample(range(1, 2 ** len(family.ORBITS)), SAMPLE_SIZE)))


def remainder_rows() -> list[dict]:
    with open(EX / "census-remainder" / "findings.json") as f:
        return json.load(f)["entries"]


def atlas_rules() -> list[dict]:
    return json.loads((EX / "llm-pilot-37" / "data" / "rules.json").read_text())


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
