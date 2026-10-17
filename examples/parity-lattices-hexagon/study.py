"""
Round 2 of the parity-lattice test: the hexagon's period is rule 90's.

    uv run python examples/parity-lattices-hexagon/study.py preregister
    uv run python examples/parity-lattices-hexagon/study.py run
    uv run lattice-lab verify --lab examples/parity-lattices-hexagon

Round 1 (examples/parity-lattices) registered P(n) = 2 * 2^v(n) * (2^sord(n) - 1) for all three
parity rules at n = 62..200. It held at all 140 triangular sizes and 67 of 70 hexagonal ones. On
the hexagon it was refuted at n = 74, 148 and 190, each time by a factor of exactly 3. Those
odd parts, 37 and 95, are sizes where rule 90 on an m-cycle falls short of 2^sord(m) - 1 by a
factor of 3. That suggested, and the identity

    sigma(x, y)^2 = (x + 1/x) (y + 1/y) (x/y + y/x)      in F2[x^+-1, y^+-1]

(sigma = the hexagon's six steps) proves, that the odd part of the hexagon's period is rule 90's
period on the odd-part cycle (docs/parity-lattices.md). The factor 2 * 2^v(n) is still only
observed. This round registers the revised law at every even n from 202 to 400, with round 1's
law as the rival (they differ at seven sizes), and the triangular lattices at those seven sizes,
where round 1's law predicts no shortfall.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "parity-lattices"))
sys.path.insert(0, str(HERE.parent / "xor-periods-algebra"))

import algebra  # noqa: E402
import lattices  # noqa: E402

from lattice_lab.ledger import Ledger, canonical, record_lines  # noqa: E402
from lattice_lab.provenance import provenance  # noqa: E402

LEDGER = HERE / "ledger.jsonl"
RECORDS = "records.jsonl"
SIZES = list(range(202, 401, 2))
TRIANGLES = ("triangle-edge", "triangle-edge+vertex")


def revised(n: int) -> int:
    """2 * 2^v(n) * R(m), R(m) = rule 90's period on the m-cycle (m = odd part of n); round 1's
    small families: m = 1 dies, m = 3 has period 2^v(n)."""
    m = lattices.odd_part(n)
    two_v = n // m
    if m == 1:
        return 1
    if m == 3:
        return two_v
    return 2 * two_v * algebra.rule90_period(m)


def rival(n: int) -> int:
    return lattices.law("hexagon", n)


def shortfall_sizes() -> list[int]:
    return [n for n in SIZES if revised(n) != rival(n)]


def hexagon_transient(n: int) -> int:
    m = lattices.odd_part(n)
    return n // 2 if m == 1 else 2 * (n // m)


def committed(path: Path) -> bool:
    status = subprocess.run(
        ["git", "-C", str(HERE), "status", "--porcelain", "--", str(path)],
        capture_output=True,
        text=True,
    )
    tracked = subprocess.run(
        ["git", "-C", str(HERE), "ls-files", "--error-unmatch", str(path)],
        capture_output=True,
        text=True,
    )
    return status.returncode == 0 and not status.stdout.strip() and tracked.returncode == 0


def preregister() -> None:
    ledger = Ledger(LEDGER)
    if len(ledger):
        sys.exit("already registered: the ledger has entries")
    short = shortfall_sizes()
    question = ledger.append(
        "question",
        {
            "id": "parity-lattices-hexagon",
            "title": "Is the hexagonal parity rule's period 2 * 2^v(n) times rule 90's period on "
            "the odd-part cycle? n = 202..400",
            "rules": {
                "hexagon": "B135/S135",
                "triangle-edge": "B13/S13",
                "triangle-edge+vertex": "B1,3,5,7,9,11/S1,3,5,7,9,11",
            },
            "sizes": {"hexagon": SIZES, **{lat: short for lat in TRIANGLES}},
            "prompted_by": "examples/parity-lattices verdict: round 1's law refuted on the "
            "hexagon at n = 74, 148, 190, by a factor of 3 each time, and nowhere else",
            "derivation": "sigma(x,y)^2 = (x + 1/x)(y + 1/y)(x/y + y/x) over F2; so every "
            "eigenvalue of the hexagon on the odd part of the torus is, up to squaring, a "
            "product of three rule-90 eigenvalues, and taking y = 1/x gives each rule-90 "
            "eigenvalue squared back. The odd part of the period is rule 90's period on the "
            "odd-part cycle (proved); the 2-part 2 * 2^v(n) is observed, not proved",
            "method": "lattices.period (examples/parity-lattices) with round 1's law as the "
            "candidate multiple, which both laws divide; rule 90's period from "
            "algebra.rule90_period (examples/xor-periods-algebra)",
            "provenance": provenance(),
        },
    )
    q = question["hash"]
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "hexagon: 2 * 2^v(n) * R(m), R(m) = rule 90's period on the m-cycle, "
            "m = odd part of n; m = 1 dies, m = 3: 2^v(n)",
            "predictions": {"hexagon": {str(n): revised(n) for n in SIZES}},
            "decision": "confirmed at n when the exact longest period equals the prediction",
        },
    )
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "rival (round 1's law): hexagon 2 * 2^v(n) * (2^sord(n) - 1)",
            "predictions": {"hexagon": {str(n): rival(n) for n in SIZES}},
            "differs_from_law_at": short,
            "decision": "refuted at n when the exact period differs from the prediction",
        },
    )
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "triangles, at the sizes where rule 90 falls short: round 1's law, "
            "2 * 2^v(n) * (2^sord(n) - 1), with no shortfall",
            "predictions": {
                lat: {str(n): lattices.law(lat, n) for n in short} for lat in TRIANGLES
            },
            "rival": {
                lat: {
                    str(n): 2
                    * (n // lattices.odd_part(n))
                    * algebra.rule90_period(lattices.odd_part(n))
                    for n in short
                }
                for lat in TRIANGLES
            },
            "decision": "confirmed at (lattice, n) when the exact longest period equals the "
            "prediction",
        },
    )
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "hexagon transient: 2 * 2^v(n), or n/2 when n is a power of 2",
            "predictions": {"hexagon": {str(n): hexagon_transient(n) for n in SIZES}},
            "decision": "confirmed at n when the exact transient equals the prediction",
        },
    )
    print(json.dumps({"registered": len(ledger), "sizes": len(SIZES), "shortfall_sizes": short}))


def _job(args):
    lattice, n = args
    began = time.time()
    try:
        result = lattices.period(lattice, n)
    except Exception as exc:  # reported, never hidden
        result = {"error": repr(exc)}
    return {"lattice": lattice, "n": n, **result}, time.time() - began


REGISTRATION = ["question", "prediction", "prediction", "prediction", "prediction"]


def run(workers: int) -> None:
    ledger = Ledger(LEDGER)
    kinds = [e["kind"] for e in ledger.entries]
    if kinds != REGISTRATION:
        sys.exit(f"expected exactly the registration (entries 0-4), found {kinds}")
    if not committed(LEDGER):
        sys.exit("commit (and push) the registered predictions before running")
    question = ledger.entries[0]
    path = HERE / RECORDS
    started = ledger.append(
        "run_started",
        {
            "question": question["hash"],
            "records_file": RECORDS,
            "records_offset": path.stat().st_size if path.exists() else 0,
            "provenance": provenance(),
        },
    )
    jobs = [(lat, n) for lat, sizes in question["body"]["sizes"].items() for n in sizes]
    jobs.sort(key=lambda j: (j[0] == "hexagon", -j[1]))  # the slow triangles first
    with Pool(workers) as pool, path.open("a") as out:
        for record, seconds in pool.imap_unordered(_job, jobs):
            out.write(canonical(record) + "\n")
            out.flush()
            print(
                f"{record['lattice']} n={record['n']}: {record.get('period')} "
                f"(transient {record.get('transient')}, {seconds:.0f}s)",
                flush=True,
            )
    refs, rows = [], []
    for offset, digest, line in record_lines(path):
        if offset >= started["body"]["records_offset"]:
            refs.append({"offset": offset, "sha256": digest})
            rows.append(json.loads(line))
    observed = ledger.append(
        "observations", {"question": question["hash"], "records": refs, "rows": rows}
    )
    law_p = ledger.entries[1]["body"]["predictions"]["hexagon"]
    rival_p = ledger.entries[2]["body"]["predictions"]["hexagon"]
    triangle_p = ledger.entries[3]["body"]["predictions"]
    transient_p = ledger.entries[4]["body"]["predictions"]["hexagon"]
    outcomes, errors = {}, []
    for row in rows:
        lat, key = row["lattice"], str(row["n"])
        name = f"{lat} {key}"
        if "error" in row:
            errors.append(name)
            continue
        outcome = {"period": row["period"], "transient": row["transient"]}
        if lat == "hexagon":
            outcome["law"] = "confirmed" if row["period"] == law_p[key] else "refuted"
            outcome["rival"] = "agrees" if row["period"] == rival_p[key] else "refuted"
            outcome["transient_law"] = (
                "confirmed" if row["transient"] == transient_p[key] else "refuted"
            )
        else:
            outcome["law"] = "confirmed" if row["period"] == triangle_p[lat][key] else "refuted"
        outcomes[name] = outcome

    def tally(lats):
        mine = {k: o for k, o in outcomes.items() if k.split()[0] in lats}
        refuted = sorted(k for k, o in mine.items() if o["law"] == "refuted")
        return {
            "confirmed": len(mine) - len(refuted),
            "refuted": len(refuted),
            "refuted_at": refuted,
        }

    ledger.append(
        "verdict",
        {
            "question": question["hash"],
            "cites": {
                "predictions": [e["hash"] for e in ledger.entries[1:5]],
                "run_started": started["hash"],
                "heldout_observations": observed["hash"],
            },
            "outcomes": outcomes,
            "hexagon_law": tally(("hexagon",)),
            "rival_refuted_at": sorted(
                (k for k, o in outcomes.items() if o.get("rival") == "refuted"),
                key=lambda k: int(k.split()[1]),
            ),
            "triangle_law": tally(TRIANGLES),
            "hexagon_transient_refuted_at": sorted(
                k for k, o in outcomes.items() if o.get("transient_law") == "refuted"
            ),
            "errors": errors,
        },
    )
    body = ledger.entries[-1]["body"]
    print(json.dumps({k: body[k] for k in ("hexagon_law", "rival_refuted_at", "triangle_law")}))


def main() -> None:
    parser = argparse.ArgumentParser(description="round 2: the hexagon's period is rule 90's")
    parser.add_argument("step", choices=("preregister", "run"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    preregister() if args.step == "preregister" else run(args.workers)


if __name__ == "__main__":
    main()
