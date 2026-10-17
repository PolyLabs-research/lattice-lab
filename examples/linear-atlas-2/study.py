"""
Round 2 of the linear-rule atlas: the factorisation pattern, registered.

    uv run python examples/linear-atlas-2/study.py register
    uv run python examples/linear-atlas-2/study.py run --workers 4
    uv run lattice-lab verify --lab examples/linear-atlas-2

After round 1 (examples/linear-atlas, docs/linear-atlas.md) the laws that held fell into two
families, and the rules' polynomials sorted them into those families with no exception: a rule
that splits into one-dimensional passes has a 1D rule's period, and one that does not reaches the
full bound. That was noticed afterwards, on the same data. Here it predicts (atlas2.py):

- **A.** For each of the 34 atlas rules with a law, the law its factorisation picks from those
  Kepler proposed, at new sizes where rule 90's or rule 150's period differs from the full bound:
  on the square, every such n from 141 to 303; on the hexagon and triangle, every such even n up
  to 400 for rule 90 and up to 300 for rule 150, within the subset the law was found on.
- **B.** For 112 square rules never computed here, and the four atlas square rules without a law,
  the period at odd n from the factorisation alone: every odd n from 13 to 61 (new rules only),
  and every odd n from 63 to 203 where rule 90's or rule 150's period differs from the full bound.

Each predicted value is checked exactly (atlas2.Exact.check). A prediction holds when the value is
the period at every size, and fails at the first size where it is not. The pattern is refuted by
any failure. Rules the pattern makes no prediction for are computed and reported.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import atlas2
import engine
import factor
from kepler import find_integer_laws

from lattice_lab.study import Study, append_records, main

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("atlas_discover", atlas2.ATLAS / "discover.py")
discover = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(discover)

# Computed while timing the engine, before registration: excluded, whatever they show.
SEEN = {("hexagon", ("H1", "self"), 394), ("triangle", ("E", "VO", "VS"), 394)}
SEEN_NOTE = (
    "Three (rule, size) pairs were computed exactly while timing the engine, before this "
    "registration, and their outcome was seen: square N4+D4 at 389, hexagon H1+self at 394 and "
    "triangle E+VO+VS at 394; each had the full-bound period. 389 is not a test size; the two at "
    "394 are excluded."
)


def a_sizes(lattice: str) -> list[int]:
    if lattice == "square":
        return [n for n in range(141, 304) if atlas2.decisive(n)]
    return [
        n
        for n in range(162, 401, 2)
        if n & (n - 1)
        and (
            atlas2.p90(n) != atlas2.full_bound(n)
            or (n <= 300 and atlas2.p150(n) != atlas2.full_bound(n))
        )
    ]


def b_sizes(new: bool) -> list[int]:
    small = list(range(13, 62, 2)) if new else []
    return small + [n for n in range(63, 204, 2) if atlas2.decisive(n)]


def _atlas(name: str):
    return json.loads((atlas2.ATLAS / name).read_text())


def _discovery_points(lattice: str, shells: tuple[str, ...]) -> list[tuple[int, int]]:
    rows = [
        json.loads(line) for line in (atlas2.ATLAS / "discovery.jsonl").read_text().splitlines()
    ]
    return [
        (r["n"], r["period"])
        for r in rows
        if r["lattice"] == lattice and tuple(r["shells"]) == shells
    ]


def family(lattice: str, shells: tuple[str, ...]) -> dict:
    """The pattern's family for an atlas rule, from its polynomial (on the triangle, from s with
    M^2 = s I)."""
    if lattice == "triangle":
        s = factor.triangle_square(shells)
        if not s:
            return {"family": "constant", "law": "1", "why": "M^2 = 0: the torus dies"}
        if len(s) == 1:
            return {"family": "constant", "law": "2", "why": "M^2 is a translation"}
        result = factor.split(s)
    else:
        result = factor.split(factor.polynomial(lattice, shells))
    types = sorted({f["factor"] for f in result["factors"]})
    if not result["splits"]:
        return {"family": "full bound", "factor types": types}
    one_d = {("1+u",): "P90", ("1+u+u^2",): "P150"}[tuple(types)]
    return {"family": "1D", "1D rule": one_d, "factor types": types}


def _law(fam: dict, laws: list[str]) -> str:
    if fam["family"] == "constant":
        return fam["law"]
    if fam["family"] == "1D":
        return next(e for e in laws if fam["1D rule"] in e)
    return next(e for e in laws if "sord" in e and "P" not in e)


def question() -> dict:
    return {
        "id": "linear-atlas-2",
        "title": "Does a linear rule's factorisation into 1D passes decide its period?",
        "pattern": "found after round 1's verdict (examples/linear-atlas, factor.py): a rule that "
        "splits completely into one-dimensional factors (on the triangle, whose matrix's square "
        "does) has a 1D rule's period; one that does not reaches the full bound",
        "part A": "the 34 atlas rules with a law; the law its factorisation picks from Kepler's "
        "round-1 proposals, at sizes where rule 90's or rule 150's period differs from the full "
        "bound (square 141 to 303; hexagon and triangle even n to 400 for rule 90, to 300 for "
        "rule 150), within the law's subset",
        "part B": "112 new square rules (shells K8, B4, C4 with N4, D4, A4) and the four atlas "
        "square rules without a law; at odd n the period from the factorisation alone: the full "
        "bound 2^sord(n) - 1 unless the rule splits completely; P90(n) for factors 1 + u only; "
        "P150(n) for 1 + u + u^2 only; the symmetric 1D rule's period for another single factor; "
        "no prediction for mixed factors. Sizes: odd 13 to 61 (new rules), and odd 63 to 203 "
        "where rule 90's or rule 150's period differs from the full bound",
        "checked before registration": "on round 1's discovery data, the 14 atlas square rules at "
        "every odd n from 9 to 59 fit part B's rule",
        "seen before registration": SEEN_NOTE,
        "engine": "atlas2.Exact: engine.Torus's check with a product tree for the proper-divisor "
        "tests; before registration it agreed with engine.Torus.check, reason for reason, on 121 "
        "values from 120 random round-1 records with n <= 100 and on all 104 values in the 52 "
        "round-1 records with a failed check",
        "decision": "a prediction holds when its value is the exact period at every size; the "
        "pattern is refuted by any failure",
    }


def predictions() -> list[dict]:
    out = []
    proposals = _atlas("proposals.json")
    for key, prop in proposals.items():
        if not prop["laws"]:
            continue
        lattice, shells = prop["lattice"], tuple(prop["shells"])
        keep = discover.SUBSETS[prop["subset"]]
        points = [(n, p) for n, p in _discovery_points(lattice, shells) if keep(n)]
        found = {law.expression: law for law in find_integer_laws(*zip(*points, strict=True))}
        fam = family(lattice, shells)
        expression = _law(fam, [law["expression"] for law in prop["laws"]])
        law = found[expression]
        sizes = [n for n in a_sizes(lattice) if keep(n) and (lattice, shells, n) not in SEEN]
        out.append(
            {
                "part": "A",
                "rule": key,
                "lattice": lattice,
                "shells": list(shells),
                **{k: v for k, v in fam.items() if k != "law"},
                "law": expression,
                "subset": prop["subset"],
                "predictions": {str(n): str(law(n)) for n in sizes},
            }
        )
    no_law = [
        tuple(p["shells"]) for p in proposals.values() if p["lattice"] == "square" and not p["laws"]
    ]
    for shells, new in [(s, False) for s in no_law] + [(s, True) for s in atlas2.new_rules()]:
        call = atlas2.classify(shells)
        sizes = b_sizes(new)
        body = {
            "part": "B",
            "rule": engine.name("square", shells),
            "lattice": "square",
            "shells": list(shells),
            "new": new,
            **call,
        }
        if call["call"] == "no prediction":
            out.append({**body, "computed at": sizes, "predictions": {}})
        else:
            out.append(
                {**body, "predictions": {str(n): str(atlas2.predict(call, n)) for n in sizes}}
            )
    return out


def _job(task):
    lattice, shells, n, value = task
    exact = (
        atlas2.Exact.square(tuple(shells), n)
        if lattice == "square" and any(s in atlas2.EXTRA for s in shells)
        else atlas2.Exact.atlas(lattice, tuple(shells), n)
    )
    record = {"lattice": lattice, "shells": list(shells), "n": n}
    if value is None:
        record["period"] = exact.period()
        return record
    record["predicted"] = value
    record["check"] = exact.check(int(value))
    if not record["check"]["is_period"]:
        record["period"] = exact.period()
    return record


def _cost(task) -> float:
    lattice, _, n, _ = task
    return n**2 * (8 if lattice == "triangle" else 1) * atlas2.sord(engine.odd_part(n))


def execute(path: Path, workers: int) -> None:
    tasks = []
    for p in predictions():
        if p["predictions"]:
            tasks += [(p["lattice"], p["shells"], int(n), v) for n, v in p["predictions"].items()]
        else:
            tasks += [(p["lattice"], p["shells"], n, None) for n in p["computed at"]]
    tasks.sort(key=_cost, reverse=True)  # the slowest first
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
    rules, summary = {}, {"A": {}, "B": {}}
    for p in registered:
        key = (p["lattice"], tuple(p["shells"]))
        if not p["predictions"]:
            rules[p["rule"]] = {
                "part": p["part"],
                "status": "no prediction",
                "periods": {str(n): checked[(*key, n)]["period"] for n in p["computed at"]},
            }
            group = "no prediction"
        else:
            failures = []
            for n, value in p["predictions"].items():
                record = checked[(*key, int(n))]
                if not record["check"]["is_period"]:
                    failures.append({"n": int(n), "predicted": value, "period": record["period"]})
            status = "held" if not failures else "failed"
            rules[p["rule"]] = {
                "part": p["part"],
                "status": status,
                "sizes": len(p["predictions"]),
                "failures": failures,
            }
            group = f"{p.get('family') or p['call']}: {status}"
        summary[p["part"]][group] = summary[p["part"]].get(group, 0) + 1
    failed = [k for k, r in rules.items() if r["status"] == "failed"]
    return {
        "pattern": "refuted" if failed else "held at every registered prediction",
        "failed": failed,
        "summary": summary,
        "rules": rules,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
