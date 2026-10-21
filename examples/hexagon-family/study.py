"""
A registered held-out test of the hexagon-family classification (the rule-4850 deep dive).

    uv run --no-sync python examples/hexagon-family/study.py register
    uv run --no-sync python examples/hexagon-family/study.py run

The deep dive (examples/rule-4850/deep/REPORT.md) found that rule 4850 is the member f_{2,5} of
the family

    f_{p,q} = (Hex_{p,q} + Hex_{p,q}^T) / (x + 1/x + y + 1/y),   Hex_{p,q} = {±(2p,0), ±(p,±q)},

and that, where q^2 + 3p^2 ≡ 0 (mod m), its members have eigenvalues W(2p α, 2p β)/(t_α t_β)
(a reduction theorem). The family investigator (deep/family, step13_predictions.py) then wrote 47
predictions of period odd parts. It computed 6, all as predicted; the other 41 are this test.
They span four tiers:

- the classification at 37 (non-residue p: 29127, residue p: 87381);
- two-orbit rules at 37 (`even_sum`);
- the cube-level analogue at 13;
- the reading at other sizes (61, 97, 109, 111, 181, 193, 481, 703 and the 2-primitive primes up
  to 1861).

`predictions.json` is the investigator's file, copied here unchanged and hashed into the question.

Each prediction is computed in its own process, by the family's builders and
examples/linear-atlas-3/eigen.py odd_part, with a time limit of 45 minutes. A prediction that
runs out of time is recorded as not tested; it neither supports nor refutes. Any computed odd
part that differs from the prediction refutes the classification as stated.

Change after registration (2026-10-21, before the run was resumed). The first run was killed by
a container restart after 37 of the 41 records: 35 agreed and 2 timed out (the T4 entries at 709
and 757). The four entries left (T4, at m = 829, 877, 1213 and 1861) are not run.
- Their registered predictions are expressions, such as "2^930 - 1 (3-part 3^2)", not integers.
  The registered comparison cannot match them, so a completed computation would have counted as a
  false mismatch.
- The two smaller T4 entries already exceeded the time limit.

They are recorded as not run, which counts like a time-out: not tested. Nothing else changes.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent / "rule-4850" / "deep" / "family"
sys.path.insert(0, str(HERE.parent.parent / "src"))

from lattice_lab.study import Study, append_records, main  # noqa: E402

LIMIT = 45 * 60
PYTHON = HERE.parent.parent / ".venv" / "bin" / "python"


def held_out() -> list[dict]:
    return [p for p in json.loads((HERE / "predictions.json").read_text()) if not p["computed"]]


def question() -> dict:
    return {
        "id": "hexagon-family-classification",
        "title": "Period odd parts of the hexagon family f_{p,q}, held out from the 4850 deep dive",
        "statement": "For each of the 41 held-out entries of predictions.json (rule construction, "
        "size m, predicted odd part), the odd part of the period computed by eigen.odd_part "
        "equals the prediction.",
        "source": "examples/rule-4850/deep/family/step13_predictions.py",
        "predictions_file": "predictions.json",
        "predictions_sha256": hashlib.sha256((HERE / "predictions.json").read_bytes()).hexdigest(),
        "checker": "examples/linear-atlas-3/eigen.py odd_part, on the exponent sets built by "
        "famlib / step12",
        "time_limit_seconds": LIMIT,
    }


def predictions() -> list[dict]:
    return [{"test": p["rule"], "m": p["m"], "predicted": p["predicted_odd_part"],
             "tier": p["tier"][:80], "construct": p["construct"]}
            for p in held_out()]  # fmt: skip


WORKER = """
import json, sys
sys.path.insert(0, {family!r})
import famlib as L
from step12_evenreps import build
p = json.loads(sys.argv[1])
c = p["construct"]
if c["kind"] == "hex":
    f = L.hex_rule(c["p"], c["q"])
else:
    f = build([tuple(t) for t in c["parts"]], p["m"], {{37: 16}}[p["m"]])
print(json.dumps({{"odd_part": int(L.odd_part(f, p["m"])), "terms": len(f)}}))
"""


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {json.loads(line)["rule"] for line in path.read_text().splitlines() if line.strip()}
    code = WORKER.format(family=str(FAMILY))
    for p in sorted(held_out(), key=lambda p: p["m"]):
        if p["rule"] + "@" + str(p["m"]) in done:
            continue
        if not isinstance(p["predicted_odd_part"], int):  # see the change note above
            append_records(
                path,
                [
                    {
                        "test": "prediction",
                        "rule": p["rule"] + "@" + str(p["m"]),
                        "m": p["m"],
                        "predicted": p["predicted_odd_part"],
                        "not_run": "the prediction is an expression, not an integer",
                    }
                ],
            )
            continue
        try:
            out = subprocess.run([str(PYTHON), "-c", code, json.dumps(p)], cwd=FAMILY,
                                 capture_output=True, text=True, timeout=LIMIT)  # fmt: skip
            res = (
                json.loads(out.stdout.strip().splitlines()[-1])
                if out.returncode == 0
                else {"error": out.stderr[-500:]}
            )
        except subprocess.TimeoutExpired:
            res = {"timeout": LIMIT}
        row = {"test": "prediction", "rule": p["rule"] + "@" + str(p["m"]), "m": p["m"],
               "predicted": p["predicted_odd_part"], **res}  # fmt: skip
        if "odd_part" in res:
            row["agrees"] = res["odd_part"] == p["predicted_odd_part"]
        append_records(path, [row])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    preds = [r for r in rows if r["test"] == "prediction"]
    tested = [r for r in preds if "odd_part" in r]
    wrong = [r["rule"] for r in tested if not r["agrees"]]
    return {
        "missing": [] if len(preds) == len(registered) else ["records"],
        "tested": len(tested),
        "not_tested": [r["rule"] for r in preds if "odd_part" not in r],
        "agree": len(tested) - len(wrong),
        "wrong": wrong,
        "classification": "holds" if tested and not wrong else ("refuted" if wrong else "untested"),
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
