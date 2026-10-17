"""
A registered blind test of Kepler on 42 linear rules nobody had worked out.

    uv run python examples/linear-atlas/validate.py      # the engine against LatticeLife
    uv run python examples/linear-atlas/discover.py      # periods at n <= 60, Kepler's laws
    uv run python examples/linear-atlas/study.py register
    uv run python examples/linear-atlas/study.py run --workers 4
    uv run lattice-lab verify --lab examples/linear-atlas

Every rule built from symmetric neighbour shells on the square, hexagonal and triangular lattices
(engine.py: 14 per lattice), a cell's next state being the parity of its live neighbours in those
shells, with or without itself. Only four had been studied before: the square's eight-neighbour
XOR rule (N4 + D4), the hexagon's parity rule (H1), and the triangle's (E, E + VO + VS). Their
periods are known (docs/xor-periods.md, docs/parity-lattices.md). The other 38 are blind.

discover.py computed every rule's exact period on tori of 8 to 60 and asked Kepler for laws, by a
rule fixed before any law was seen. Here, every law it proposed (the first and every rival
confirmed as often) is registered with its value at each test size before any test size is
computed. Test sizes: 61 to 140 on the square, even n from 62 to 160 on the hexagon and
triangle, within the subset the law was found on. Each value is then checked exactly
(engine.Torus.check): it is the period when the rule's matrix repeats after it and after none of
its proper divisors.
"""

from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import discover
import engine
from kepler import find_integer_laws

from lattice_lab.study import Study, append_records, main

HERE = Path(__file__).resolve().parent
STUDIED = {
    ("square", ("N4", "D4")),
    ("hexagon", ("H1",)),
    ("triangle", ("E",)),
    ("triangle", ("E", "VO", "VS")),
}


def test_sizes(lattice: str, subset: str) -> list[int]:
    span = range(61, 141) if lattice == "square" else range(62, 161)
    keep = discover.SUBSETS[subset]
    return [n for n in span if engine.valid_size(lattice, n) and keep(n)]


def _discovery_points(lattice: str, shells: tuple[str, ...]) -> list[tuple[int, int]]:
    rows = [json.loads(line) for line in (HERE / "discovery.jsonl").read_text().splitlines()]
    return [
        (r["n"], r["period"])
        for r in rows
        if r["lattice"] == lattice and tuple(r["shells"]) == shells
    ]


def proposals() -> dict:
    return json.loads((HERE / "proposals.json").read_text())


def question() -> dict:
    return {
        "id": "linear-atlas",
        "title": "Do Kepler's period laws for 42 shell-built linear rules hold at new sizes?",
        "rules": [engine.name(lat, sh) for lat, sh in engine.rules()],
        "studied_before": sorted(engine.name(lat, sh) for lat, sh in STUDIED),
        "discovery": {
            "sizes": "8 to 60 (even on the hexagon and triangle)",
            "periods": "discovery.jsonl",
            "proposal_rule": "discover.py: subsets all n, n not a power of 2, odd part at least 5, "
            f"in that order; the first with a law confirmed by >= {discover.MIN_CONFIRMED} points; "
            "every law confirmed as often is registered",
            "proposals": "proposals.json",
        },
        "validation": "validation.json: 58 (rule, size) pairs against LatticeLife's simulation, "
        "154 against a direct simulation of all 42 rules; all agree",
        "search": "kepler.find_integer_laws, Kepler 0af9b28",
        "test_sizes": "61 to 140 on the square; even 62 to 160 on the hexagon and triangle; within "
        "the law's subset",
    }


def predictions() -> list[dict]:
    out = []
    for key, prop in proposals().items():
        lattice, shells = prop["lattice"], tuple(prop["shells"])
        body = {
            "rule": key,
            "lattice": lattice,
            "shells": list(shells),
            "studied_before": (lattice, shells) in STUDIED,
            "subset": prop["subset"],
        }
        if not prop["laws"]:
            out.append({**body, "laws": [], "decision": "no law proposed: nothing to test"})
            continue
        keep = discover.SUBSETS[prop["subset"]]
        points = [(n, p) for n, p in _discovery_points(lattice, shells) if keep(n)]
        found = {law.expression: law for law in find_integer_laws(*zip(*points, strict=True))}
        sizes = test_sizes(lattice, prop["subset"])
        laws = []
        for registered in prop["laws"]:
            law = found[registered["expression"]]
            laws.append(
                {
                    "expression": law.expression,
                    "confirmed_by": law.confirmed_by,
                    "predictions": {str(n): str(law(n)) for n in sizes},
                }
            )
        out.append(
            {
                **body,
                "laws": laws,
                "decision": "a law is confirmed when its value is the exact period at every test "
                "size; refuted at the first size where it is not",
            }
        )
    return out


def _job(task):
    lattice, shells, n, values = task
    torus = engine.Torus(lattice, tuple(shells), n)
    checks = {}
    for value in values:
        number = int(value) if value.lstrip("-").isdigit() else None
        checks[value] = (
            torus.check(number) if number else {"is_period": False, "reason": "not a whole number"}
        )
    record = {"lattice": lattice, "shells": list(shells), "n": n, "checks": checks}
    if not any(c["is_period"] for c in checks.values()):
        record["period"] = torus.period()
    return record


def execute(path: Path, workers: int) -> None:
    tasks = []
    for p in predictions():
        if not p["laws"]:
            continue
        for n in test_sizes(p["lattice"], p["subset"]):
            values = sorted({law["predictions"][str(n)] for law in p["laws"]})
            tasks.append((p["lattice"], p["shells"], n, values))
    tasks.sort(key=lambda t: (t[0] != "triangle", -t[2]))  # the slowest first
    with Pool(workers) as pool:
        for record in pool.imap_unordered(_job, tasks):
            append_records(path, [record])
            print(
                f"{record['lattice']} {'+'.join(record['shells'])} n={record['n']}",
                file=sys.stderr,
                flush=True,
            )


def decide(rows: list[dict], registered: list[dict]) -> dict:
    checked = {(r["lattice"], tuple(r["shells"]), r["n"]): r for r in rows}
    per_rule, summary = {}, {"blind": {}, "studied": {}}
    for p in registered:
        group = "studied" if p["studied_before"] else "blind"
        if not p["laws"]:
            per_rule[p["rule"]] = {"status": "no law"}
            summary[group]["no law"] = summary[group].get("no law", 0) + 1
            continue
        laws = {}
        for law in p["laws"]:
            failures = []
            for n, value in law["predictions"].items():
                record = checked[(p["lattice"], tuple(p["shells"]), int(n))]
                if not record["checks"][value]["is_period"]:
                    failures.append(
                        {"n": int(n), "predicted": value, "period": record.get("period")}
                    )
            laws[law["expression"]] = {
                "status": "confirmed" if not failures else "refuted",
                "sizes": len(law["predictions"]),
                "first_failure": min(failures, key=lambda f: f["n"]) if failures else None,
                "failures": len(failures),
            }
        first = p["laws"][0]["expression"]
        survivors = [e for e, s in laws.items() if s["status"] == "confirmed"]
        outcome = (
            "first law confirmed"
            if laws[first]["status"] == "confirmed"
            else ("a rival confirmed" if survivors else "every law refuted")
        )
        per_rule[p["rule"]] = {
            "subset": p["subset"],
            "laws": laws,
            "survivors": survivors,
            "status": outcome,
        }
        summary[group][outcome] = summary[group].get(outcome, 0) + 1
    return {"rules": per_rule, "summary": summary}


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
