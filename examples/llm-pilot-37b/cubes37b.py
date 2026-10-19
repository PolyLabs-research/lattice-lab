"""
The orchestrator's side of the sixth pilot (the square family at m = 37): its targets, the known
mechanisms, the family's census at the held-out sizes, and the judge's evaluation sets.

The fifth pilot's registered census (llm-pilot-25/records.jsonl) found 16 rules of the square
family (all 32,767 symmetric square rules within distance 4) confined to the cubes at m = 37 that
no known mechanism explains, against 0.6 expected by chance; three of them are also confined at
61. The census itself is the fifth pilot's (llm-pilot-25/cubes25.census_at), and so are the family
and the sandbox tools, which this pilot copies.

The known mechanisms are now three: the atlas procedure's (splitting, powers, dilations, twisted
powers, forced subfields), the fourth pilot's half-Frobenius condition (tools/halffrob.py) and the
fifth pilot's cube certificates and twisted pairs (tools/certificate.py). known_q(f, m) is the lcm
of the two pilots' conditions.
"""

from __future__ import annotations

import functools
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EX = HERE.parent
sys.path.insert(0, str(EX / "llm-pilot-25"))

import cubes25  # noqa: E402

census = cubes25.census
family = cubes25.family
remainder = cubes25.remainder
write_csv = cubes25.write_csv
atlas_rules = cubes25.atlas_rules

PILOT25 = EX / "llm-pilot-25"


def _tool(name: str):
    """A sandbox tool, loaded under its own name so it cannot shadow the atlas's modules. Its
    imports of the other tools resolve within tools/."""
    tools = str(HERE / "tools")
    sys.path.insert(0, tools)
    try:
        path = HERE / "tools" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"pilot37b_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(tools)
    return module


@functools.cache
def conditions():
    """The fourth and fifth pilots' conditions, as the sandbox carries them."""
    return _tool("halffrob"), _tool("certificate")


def known_q(f: frozenset, m: int) -> int:
    """The lcm of what the fourth and fifth pilots' conditions prove for f at m (1 if nothing)."""
    halffrob, certificate = conditions()
    return math.lcm(int(halffrob.condition(f, m)), int(certificate.condition(f, m)))


def records() -> dict[int, dict]:
    """The fifth pilot's registered census, by m."""
    out = {}
    for line in (PILOT25 / "records.jsonl").read_text().splitlines():
        r = json.loads(line)
        out[r["m"]] = r
    return out


@functools.cache
def targets() -> tuple[tuple[int, int], ...]:
    """(m, rule id): the confinements at 37 and 61 that neither pilot's condition explains."""
    out = []
    for m in (37, 61):
        for h in records()[m]["hits"]:
            if known_q(family.rule(h["id"]), m) % 3:
                out.append((m, h["id"]))
    return tuple(out)


SAMPLE_SEED, SAMPLE_SIZE = 37, 2000


@functools.cache
def sample() -> tuple[int, ...]:
    """A fixed random sample of family rules, for the judge's soundness checks."""
    rng = random.Random(SAMPLE_SEED)
    return tuple(sorted(rng.sample(range(1, 2 ** len(family.ORBITS)), SAMPLE_SIZE)))
