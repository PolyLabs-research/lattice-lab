"""
Can Kepler find the hexagon's period law itself? A registered replay with a wider vocabulary.

    uv run python examples/kepler-rediscovery/study.py register
    uv run python examples/kepler-rediscovery/study.py run
    uv run lattice-lab verify --lab examples/kepler-rediscovery

In the parity-lattice study (docs/parity-lattices.md), Kepler's find_integer_laws found
P(n) = 2 * 2^v(n) * (2^sord(n) - 1) for all three parity rules from simulations up to n = 60. The
law was refuted on the hexagon at n = 74, 148 and 190, and the corrected law,
2 * 2^v(n) * R(m) with R(m) rule 90's period on the odd part, came from reasoning: Kepler had no
feature for another automaton's period, so it could not have proposed it.

Kepler 0af9b28 adds one: the periods of the one-dimensional linear rules (60, 90 and 150) on a
ring of n cells and of odd(n) cells. They are all the elementary rules linear over GF(2), not
rule 90 alone. This study replays the history with that vocabulary, on the same data subsets
discover.py used, and registers before running it what a search that had the vocabulary should
have done:

- On the discovery data (n <= 60), list both the formula and a rule-90 law, since they agree
  there, and name the first size beyond the data where they part. That is the size that
  decides, and the experiment the study should have run first.
- On the data up to 200: on the hexagon, put a rule-90 law first, drop the formula, and predict
  every hexagon period measured at 202 to 400. On the square (B1357/S1357) and both triangular
  rules, where the formula is right, keep it first and drop every rule-90 law.

No new simulation: the data are the committed records of the earlier studies. The new thing
tested is the search.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from kepler import find_integer_laws

from lattice_lab.study import Study, append_records, main

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent
sys.path.insert(0, str(EXAMPLES / "xor-periods-algebra"))

import algebra  # noqa: E402  (rule 90's period, computed independently of Kepler)

CHECK_UP_TO = {"square": 200}  # odd n beyond 200 would need 2^k - 1 factored for k > 200
CHECK_DEFAULT = 400


def limit(lattice: str) -> int:
    return CHECK_UP_TO.get(lattice, CHECK_DEFAULT)


def odd_part(n: int) -> int:
    while n % 2 == 0:
        n //= 2
    return n


def suborder(m: int) -> int:
    if m <= 3:
        return 1
    k, v = 1, 2 % m
    while v not in (1, m - 1):
        v, k = v * 2 % m, k + 1
    return k


def formula(n: int, factor: int) -> int:
    return factor * (n // odd_part(n)) * (2 ** suborder(odd_part(n)) - 1)


def rule90(n: int, factor: int) -> int:
    return factor * algebra.rule90_period(n)


def _rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (EXAMPLES / name).read_text().splitlines()]


def lattice_data() -> dict:
    """period by n, per lattice, and the stage each n first appeared in."""
    out: dict = {}
    for stage, name in (
        ("discovery", "parity-lattices/discovery.jsonl"),
        ("round 1", "parity-lattices/records.jsonl"),
        ("round 2", "parity-lattices-hexagon/records.jsonl"),
    ):
        for r in _rows(name):
            out.setdefault(r["lattice"], {})[r["n"]] = (r["period"], stage)
    for r in _rows("xor-periods-algebra/records.jsonl"):
        out.setdefault("square", {})[r["n"]] = (
            r["period"],
            "discovery" if r["n"] <= 30 else "round 1",
        )
    return out


SUBSETS = {
    "all n": lambda n: True,
    "n not a power of 2": lambda n: n & (n - 1) != 0,
    "odd part at least 5": lambda n: odd_part(n) >= 5,
}
# (lattice, subset): the subsets discover.py searched; on the square, the one the XOR law is for
DATASETS = [
    ("hexagon", "odd part at least 5", 2),
    ("triangle-edge", "n not a power of 2", 2),
    ("triangle-edge+vertex", "n not a power of 2", 2),
    ("square", "n not a power of 2", 1),
]
STAGES = {"discovery": ("discovery",), "up to 200": ("discovery", "round 1")}


def valid(lattice: str, subset: str, n: int) -> bool:
    return (lattice == "square" or n % 2 == 0) and n >= 3 and SUBSETS[subset](n)


def question() -> dict:
    return {
        "id": "kepler-rediscovery",
        "title": "With the periods of the 1D linear rules in its vocabulary, does Kepler find the "
        "hexagon's law, name the experiment that decides it, and keep the others?",
        "search": "kepler.find_integer_laws (Kepler 0af9b28), default settings",
        "data": [
            "examples/parity-lattices/discovery.jsonl (n = 6..60)",
            "examples/parity-lattices/records.jsonl (n = 62..200)",
            "examples/parity-lattices-hexagon/records.jsonl (hexagon n = 202..400, triangles at 7)",
            "examples/xor-periods-algebra/records.jsonl (square, n = 3..200; discovery: n <= 30)",
        ],
        "datasets": [{"lattice": a, "subset": b, "factor": c} for a, b, c in DATASETS],
        "equivalence": "a law is 'the formula' or 'a rule-90 law' when its values equal "
        "factor * 2^v(n) * (2^sord(n) - 1), or factor * rule 90's period on n cells (computed "
        "by examples/xor-periods-algebra, not Kepler), at every valid n up to 400 (200 on the "
        "square, where the data end)",
    }


def predictions() -> list[dict]:
    out = []
    for lattice, subset, _ in DATASETS:
        first = 37 if lattice == "square" else 74
        out.append(
            {
                "dataset": f"{lattice}, {subset}",
                "stage": "discovery",
                "expect": {"formula listed": True, "rule-90 law listed": True, "decides at": first},
                "decision": "confirmed when both are among the laws returned and the first valid "
                "n beyond the data where they differ is the one given",
            }
        )
        hexagon = lattice == "hexagon"
        out.append(
            {
                "dataset": f"{lattice}, {subset}",
                "stage": "up to 200",
                "expect": {
                    "first law": "a rule-90 law" if hexagon else "the formula",
                    "formula listed": not hexagon,
                    "rule-90 law listed": hexagon,
                    **({"predicts round 2": True} if hexagon else {}),
                },
                "decision": "confirmed when the first law is the one given, the other is not "
                "among the laws returned"
                + (
                    ", and the first law equals every hexagon period measured at 202 to 400"
                    if hexagon
                    else ""
                ),
            }
        )
    return out


def execute(path: Path, workers: int) -> None:
    data = lattice_data()
    records = []
    for lattice, subset, factor in DATASETS:
        for stage, included in STAGES.items():
            points = sorted(
                (n, p)
                for n, (p, s) in data[lattice].items()
                if s in included and valid(lattice, subset, n)
            )
            laws = find_integer_laws([n for n, _ in points], [p for _, p in points])
            top = limit(lattice)
            beyond = [n for n in range(points[-1][0] + 1, top + 1) if valid(lattice, subset, n)]
            check = [n for n in range(3, top + 1) if valid(lattice, subset, n)]
            records.append(
                {
                    "dataset": f"{lattice}, {subset}",
                    "lattice": lattice,
                    "subset": subset,
                    "factor": factor,
                    "stage": stage,
                    "points": len(points),
                    "largest_n": points[-1][0],
                    "laws": [
                        {
                            **law.to_dict(),
                            "values": {str(n): str(law(n)) for n in check},
                        }
                        for law in laws
                    ],
                    "beyond": beyond,
                }
            )
    append_records(path, records)


def _kind(law: dict, lattice: str, subset: str, factor: int) -> str | None:
    checks = [int(n) for n in law["values"]]
    values = {int(n): v for n, v in law["values"].items()}
    if all(values[n] == str(formula(n, factor)) for n in checks):
        return "the formula"
    if all(values[n] == str(rule90(n, factor)) for n in checks):
        return "a rule-90 law"
    return None


def decide(rows: list[dict], registered: list[dict]) -> dict:
    data = lattice_data()
    by_key = {(r["dataset"], r["stage"]): r for r in rows}
    outcomes = {}
    for p in registered:
        row = by_key[(p["dataset"], p["stage"])]
        kinds = [_kind(law, row["lattice"], row["subset"], row["factor"]) for law in row["laws"]]
        found = {
            "first law": kinds[0] if kinds else None,
            "formula listed": "the formula" in kinds,
            "rule-90 law listed": "a rule-90 law" in kinds,
            "laws": [law["expression"] for law in row["laws"]],
            "kinds": kinds,
        }
        if "decides at" in p["expect"]:
            pair = [
                row["laws"][kinds.index("the formula")] if "the formula" in kinds else None,
                row["laws"][kinds.index("a rule-90 law")] if "a rule-90 law" in kinds else None,
            ]
            found["decides at"] = (
                next(
                    (
                        n
                        for n in row["beyond"]
                        if pair[0]["values"][str(n)] != pair[1]["values"][str(n)]
                    ),
                    None,
                )
                if all(pair)
                else None
            )
        if "predicts round 2" in p["expect"] and row["laws"]:
            measured = {
                n: period
                for n, (period, stage) in data[row["lattice"]].items()
                if stage == "round 2" and valid(row["lattice"], row["subset"], n)
            }
            top = row["laws"][0]["values"]
            found["round 2 sizes"] = len(measured)
            found["predicts round 2"] = all(top[str(n)] == str(v) for n, v in measured.items())
        confirmed = all(found.get(k) == v for k, v in p["expect"].items())
        outcomes[f"{p['dataset']} | {p['stage']}"] = {
            "expected": p["expect"],
            "found": found,
            "status": "confirmed" if confirmed else "refuted",
        }
    return {
        "outcomes": outcomes,
        "confirmed": sum(o["status"] == "confirmed" for o in outcomes.values()),
        "refuted": sorted(k for k, o in outcomes.items() if o["status"] == "refuted"),
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
