"""
Round 3 of the linear-rule atlas: the refined statement, registered on new rules.

    uv run python examples/linear-atlas-3/validate.py
    uv run python examples/linear-atlas-3/study.py register
    uv run python examples/linear-atlas-3/study.py run --workers 4
    uv run lattice-lab verify --lab examples/linear-atlas-3

Round 2 (docs/linear-atlas.md) refuted the factorisation pattern. Its failures were perfect cubes,
a dilation, and four single-size accidents. The refined statement, written as the procedure
atlas3.predict, predicts the odd part of a rule's period from its polynomial alone. Here it is
registered on rules never computed:
- **square:** 120 rules using the new shells L8, M8 or E4. These are all 20 whose call is not
  the full bound, and a seeded sample of 100 of the 876 that are.
- **hexagon:** all 112 using H4, H5 or H13.
- **triangle:** all 112 using T7, T9 or T13.

Each is tested at 34 odd parts: every m from 9 to 61, and the 7 from 63 to 141 where rule 90's or
rule 150's period differs from the full bound. That is n = m on the square, and n = 2m on the
hexagon and triangle. Pairs computed during validation are excluded. Each predicted odd part is
checked exactly (atlas3.OddExact). Rules the procedure makes no prediction for are computed and
reported. Two hypotheses are judged:

- **strict:** every prediction holds;
- **accidents:** every failure is at m <= 61, and failures are at most 1% of the predictions.
  This allows round 2's kind of exception, which was at small sizes, but not at the decisive
  sizes, where the mechanisms matter.
"""

from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import atlas3

from lattice_lab.study import Study, append_records, main

HERE = Path(__file__).resolve().parent
atlas2, engine = atlas3.atlas2, atlas3.engine


def seen() -> set[tuple[str, int]]:
    """(rule, m) pairs whose period was computed in validate.py, before registration."""
    data = json.loads((HERE / "validation.json").read_text())
    out = set()
    for row in data["shells"] + data["odd parts"]:
        out.add((row["rule"], engine.odd_part(row["n"])))
    return out


def question() -> dict:
    return {
        "id": "linear-atlas-3",
        "title": "Does the refined statement predict the periods of linear rules nobody has "
        "computed?",
        "statement": "atlas3.predict: the odd part of the period at odd part m is, in order: "
        "1 if f = 0; the order of (a, b) mod m if f is a monomial; no prediction if f wraps mod "
        "m; for a dilation f = h(x^p, y^p), predict(h, m/p) if p | m, else predict(h, m); for an "
        "odd prime power f = g^k, q / gcd(q, k) with q = predict(g, m); for a complete split "
        "into one kind of 1D factor g, the symmetric 1D rule's period on m cells; no prediction "
        "for a split into mixed factors; otherwise the full bound 2^sord(m) - 1 (2^ord(m) - 1 "
        "if f is not symmetric). On the triangle f is s, where M^2 = s I.",
        "rules": "square: rules using L8, M8 or E4 (with N4, D4, A4, K8, B4, C4): every one whose "
        "call at m = 9 is not the full bound, and a sample of 100 of the rest (random.Random(3)); "
        "hexagon: all 112 using H4, H5 or H13 (with H1, H2, H3); triangle: all 112 using T7, T9 "
        "or T13 (with E, VO, VS)",
        "sizes": "odd m from 9 to 61, and from 63 to 141 where rule 90's or rule 150's period "
        "differs from the full bound; n = m (square), 2m (hexagon, triangle)",
        "validation": "validate.py, before registration: the new shells against direct "
        "simulation (60 of 60 pairs agree); OddExact against the odd part of atlas2.Exact's "
        "period (72 of 72); predict against every record of rounds 1 and 2 and round 1's "
        "discovery data at odd parts >= 9: 7,746 agree, 78 have no prediction, and the 4 that "
        "disagree are round 2's four accidents",
        "seen before registration": "the (rule, m) pairs computed in validate.py are excluded",
        "hypotheses": {
            "strict": "every registered prediction holds",
            "accidents": "every failure is at m <= 61, and failures are at most 1% of the "
            "registered predictions",
        },
        "data from earlier rounds": "the procedure was written after round 2's verdict and "
        "checked against all earlier data; nothing here was computed before registration "
        "except the excluded pairs",
    }


def predictions() -> list[dict]:
    skip = seen()
    out = []
    for lattice in ("square", "hexagon", "triangle"):
        for shells in atlas3.new_rules(lattice):
            rule = atlas3.name(lattice, shells)
            f = atlas3.polynomial(lattice, shells)
            predicted, computed, why = {}, [], {}
            for m in atlas3.SIZES:
                if (rule, m) in skip:
                    continue
                value, reason = atlas3.predict(f, m)
                why[str(m)] = reason
                if value is None:
                    computed.append(m)
                else:
                    predicted[str(m)] = str(value)
            out.append(
                {
                    "rule": rule,
                    "lattice": lattice,
                    "shells": list(shells),
                    "predictions": predicted,
                    "computed at": computed,
                    "why": why,
                }
            )
    return out


def _job(task):
    lattice, shells, m, value = task
    n = atlas3.size(lattice, m)
    exact = atlas3.OddExact(lattice, tuple(shells), n)
    record = {"lattice": lattice, "shells": list(shells), "m": m, "n": n}
    if value is None:
        record["odd part"] = exact.odd_part()
        return record
    record["predicted"] = value
    record["check"] = exact.check(int(value))
    if not record["check"]["is_odd_part"]:
        record["odd part"] = exact.odd_part()
    return record


def _cost(task) -> float:
    lattice, _, m, _ = task
    n = atlas3.size(lattice, m)
    return n**2 * (8 if lattice == "triangle" else 1) * atlas2.sord(m)


def execute(path: Path, workers: int) -> None:
    tasks = []
    for p in predictions():
        tasks += [(p["lattice"], p["shells"], int(m), v) for m, v in p["predictions"].items()]
        tasks += [(p["lattice"], p["shells"], m, None) for m in p["computed at"]]
    if path.exists():  # a resumed run skips what is already recorded
        done = {
            (r["lattice"], tuple(r["shells"]), r["m"])
            for r in map(json.loads, path.read_text().splitlines())
        }
        tasks = [t for t in tasks if (t[0], tuple(t[1]), t[2]) not in done]
    tasks.sort(key=_cost, reverse=True)  # the slowest first
    with Pool(workers) as pool:
        for record in pool.imap_unordered(_job, tasks):
            append_records(path, [record])
            print(
                f"{record['lattice']} {'+'.join(record['shells'])} m={record['m']}",
                file=sys.stderr,
                flush=True,
            )


def decide(rows: list[dict], registered: list[dict]) -> dict:
    checked = {(r["lattice"], tuple(r["shells"]), r["m"]): r for r in rows}
    rules, summary, failures = {}, {}, []
    total = 0
    for p in registered:
        key = (p["lattice"], tuple(p["shells"]))
        fails = []
        for m, value in p["predictions"].items():
            total += 1
            record = checked[(*key, int(m))]
            if not record["check"]["is_odd_part"]:
                fails.append(
                    {
                        "m": int(m),
                        "predicted": value,
                        "odd part": record["odd part"],
                        "why": p["why"][m],
                    }
                )
        computed = {str(m): checked[(*key, m)]["odd part"] for m in p["computed at"]}
        rules[p["rule"]] = {
            "status": "failed" if fails else "held",
            "predictions": len(p["predictions"]),
            "failures": fails,
            "computed": computed,
        }
        failures += [{"rule": p["rule"], **f} for f in fails]
        for m in p["predictions"]:
            step = p["why"][m].split(";")[0].split(" (")[0]
            outcome = "failed" if any(f["m"] == int(m) for f in fails) else "held"
            group = summary.setdefault(p["lattice"], {}).setdefault(step, {"held": 0, "failed": 0})
            group[outcome] += 1
    large = [f for f in failures if f["m"] > 61]
    return {
        "strict": "held" if not failures else "refuted",
        "accidents": "held" if not large and len(failures) <= 0.01 * total else "refuted",
        "predictions": total,
        "failed": len(failures),
        "failures": failures,
        "summary": summary,
        "rules": rules,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
