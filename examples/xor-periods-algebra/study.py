"""
Round 2 of the XOR period test: exact periods by algebra, at every n from 3 to 200.

    uv run python examples/xor-periods-algebra/study.py preregister
    uv run python examples/xor-periods-algebra/study.py run
    uv run lattice-lab verify --lab examples/xor-periods-algebra

The law (lattice-lab 8d7bc58, confirmed by simulation at 45 registered sizes in
examples/xor-periods) predicts the longest period of B1357/S1357 on the n x n torus; the rival is
rule 90's period on the n-cycle. Simulation could not reach sizes whose periods run to millions
of generations or more (47, 49, 53, 61, ..., and rule 90's next shortfalls at 95, 111, ...);
`algebra.torus_period` computes them exactly (see algebra.py). The predictions are written and
pushed before it runs on any size it has not already reproduced from the simulations.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import algebra  # noqa: E402

from lattice_lab.ledger import Ledger, canonical, record_lines  # noqa: E402
from lattice_lab.provenance import provenance  # noqa: E402

LEDGER = HERE / "ledger.jsonl"
RECORDS = "records.jsonl"
SIZES = list(range(3, 201))
SIMULATED = HERE.parent / "xor-periods" / "records.jsonl"


def simulated_sizes() -> list[int]:
    """Sizes whose period was measured by simulation before this round (n = 3..30, 31, 33, 34,
    35, 37, and the 45 of round 1)."""
    measured = set(range(3, 31)) | {31, 33, 34, 35, 37}
    for line in SIMULATED.read_text().splitlines():
        measured.add(json.loads(line)["grid"])
    return sorted(measured)


def two_adic(n: int) -> int:
    return n // algebra.odd_part(n)


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
    measured = simulated_sizes()
    question = ledger.append(
        "question",
        {
            "id": "xor-periods-algebra",
            "title": "Exact periods of B1357/S1357 on n x n square tori, n = 3..200",
            "rule": "B1357/S1357",
            "shape": "square",
            "method": "algebra.torus_period: tau^t in GF(2)[x,y]/(x^n - 1, y^n - 1) from a single "
            "cell, which has the torus's longest period and transient; the period as the "
            "order of tau past the transient, from the prime factors of the candidate",
            "validation": "before registration the method reproduced the simulated period at all "
            f"{len(measured)} simulated sizes and rule 90's published 87381 at n = 37",
            "sizes": SIZES,
            "new_sizes": [n for n in SIZES if n not in measured],
            "simulated_sizes": measured,
            "law": {
                "expression": "2^v(n)*(2^sord(n) - 1); 1 for a power of 2",
                "committed_in": "lattice-lab 8d7bc58 (2026-10-16)",
                "round_1": "examples/xor-periods: confirmed at 45 of 45 sizes, rival refuted at 74",
            },
            "provenance": provenance(),
        },
    )
    q = question["hash"]
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "2^v(n)*(2^sord(n) - 1)",
            "predictions": {str(n): algebra.law(n) for n in SIZES},
            "transient": {
                "odd n": "at most 1 (proved: tau^(2^sord) = tau)",
                "even n": "at most 2^v(n) (seen in round 1, not proved)",
            },
            "decision": "confirmed at n when the exact longest period equals the prediction, "
            "refuted otherwise",
        },
    )
    rival = {str(n): algebra.rule90_period(n) for n in SIZES}
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "rival: the period of rule 90 on an n-cycle",
            "predictions": rival,
            "differs_from_law_at": [n for n in SIZES if rival[str(n)] != algebra.law(n)],
            "decision": "refuted at n when the exact period differs from the prediction",
        },
    )
    print(
        json.dumps(
            {
                "registered": len(ledger),
                "new_sizes": question["body"]["new_sizes"],
                "rival_differs_at": ledger.entries[-1]["body"]["differs_from_law_at"],
            }
        )
    )


def run() -> None:
    ledger = Ledger(LEDGER)
    kinds = [e["kind"] for e in ledger.entries]
    if kinds != ["question", "prediction", "prediction"]:
        sys.exit(f"expected exactly the registration (entries 0-2), found {kinds}")
    if not committed(LEDGER):
        sys.exit("commit (and push) the registered predictions before running")
    question = ledger.entries[0]
    records_path = HERE / RECORDS
    started = ledger.append(
        "run_started",
        {
            "question": question["hash"],
            "records_file": RECORDS,
            "records_offset": records_path.stat().st_size if records_path.exists() else 0,
            "sizes": SIZES,
            "provenance": provenance(),
        },
    )
    with records_path.open("a") as out:
        for n in SIZES:
            began = time.time()
            result = algebra.torus_period(n)
            out.write(
                canonical({"n": n, "rule": "B1357/S1357", "shape": "square", **result}) + "\n"
            )
            out.flush()
            print(
                f"n={n}: period {result['period']} transient {result['transient']} "
                f"({time.time() - began:.1f}s)",
                flush=True,
            )
    refs, rows = [], []
    for offset, digest, line in record_lines(records_path):
        if offset >= started["body"]["records_offset"]:
            refs.append({"offset": offset, "sha256": digest})
            rows.append(json.loads(line))
    observed = ledger.append(
        "observations", {"question": question["hash"], "records": refs, "rows": rows}
    )
    law_p, rival_p = (e["body"]["predictions"] for e in ledger.entries[1:3])
    new = set(question["body"]["new_sizes"])
    outcomes = {}
    for row in rows:
        n, key = row["n"], str(row["n"])
        bound = 1 if n % 2 else two_adic(n)
        outcomes[key] = {
            "period": row["period"],
            "transient": row["transient"],
            "new": n in new,
            "law": "confirmed" if row["period"] == law_p[key] else "refuted",
            "rival": "refuted" if row["period"] != rival_p[key] else "agrees",
            "transient_ok": row["transient"] <= bound,
        }
    refuted = [int(k) for k, o in outcomes.items() if o["law"] == "refuted"]
    ledger.append(
        "verdict",
        {
            "question": question["hash"],
            "cites": {
                "predictions": [e["hash"] for e in ledger.entries[1:3]],
                "run_started": started["hash"],
                "heldout_observations": observed["hash"],
            },
            "outcomes": outcomes,
            "law": {
                "confirmed": len(outcomes) - len(refuted),
                "refuted": len(refuted),
                "refuted_at": refuted,
                "confirmed_new": sum(
                    o["law"] == "confirmed" and o["new"] for o in outcomes.values()
                ),
            },
            "rival_refuted_at": [int(k) for k, o in outcomes.items() if o["rival"] == "refuted"],
            "transients_within_bounds": all(o["transient_ok"] for o in outcomes.values()),
            "transient_exceptions": [int(k) for k, o in outcomes.items() if not o["transient_ok"]],
        },
    )
    print(
        json.dumps(
            {
                k: ledger.entries[-1]["body"][k]
                for k in ("law", "rival_refuted_at", "transients_within_bounds")
            }
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="round 2: exact periods by algebra")
    parser.add_argument("step", choices=("preregister", "run"))
    args = parser.parse_args()
    preregister() if args.step == "preregister" else run()


if __name__ == "__main__":
    main()
