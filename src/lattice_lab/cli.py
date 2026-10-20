"""The `lattice-lab` command.

    lattice-lab ask QUESTION.toml [--lab DIR] [--workers N]   answer a question, write a report
    lattice-lab report [--lab DIR] [--question ID]              rebuild a report from the ledger
    lattice-lab verify [--lab DIR] [--rerun N]                  check the ledger and rerun records
    lattice-lab selfcheck [--thresholds FILE] [--replicates N]  recover known laws, vs pass marks
    lattice-lab laws                                            the law library
    lattice-lab consult ask|review NAME ...                     ask other models (consult.py)

A lab directory holds `ledger.jsonl`, `records/` (LatticeLife's JSONL, one file per question
asked) and `reports/`. Progress goes to stderr; a JSON summary to stdout. Exit status: 0 when
the command did its job (any verdict is an answer), 1 when `verify` or `selfcheck` failed, 2
for a bad question file or arguments.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from kepler import LAWS

from lattice_lab import consult
from lattice_lab.experiment import LatticeExperimenter, question_config, rerun_record
from lattice_lab.ledger import Ledger, LedgerError, check_order, record_lines
from lattice_lab.loop import ask
from lattice_lab.provenance import provenance
from lattice_lab.question import Question, QuestionError
from lattice_lab.report import render
from lattice_lab.selfcheck import load_thresholds, render_selfcheck, run_selfcheck


def _stderr(message: str) -> None:
    print(f"lattice-lab: {message}", file=sys.stderr, flush=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lattice-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ask", help="Answer a question and write its report.")
    p.add_argument("question", type=Path)
    p.add_argument("--lab", type=Path, default=Path("lab"))
    p.add_argument("--workers", type=int, default=1)

    p = sub.add_parser("report", help="Rebuild a question's report from the ledger.")
    p.add_argument("--lab", type=Path, default=Path("lab"))
    p.add_argument("--question", default=None, help="question id, entry number or hash prefix")

    p = sub.add_parser("verify", help="Check the ledger's chain and order, and rerun records.")
    p.add_argument("--lab", type=Path, default=Path("lab"))
    p.add_argument("--rerun", type=int, default=3, help="records to rerun per question (0: none)")

    p = sub.add_parser("selfcheck", help="Recover known laws from synthetic data.")
    p.add_argument("--thresholds", type=Path, default=Path("thresholds.toml"))
    p.add_argument("--replicates", type=int, default=None, help="fewer, for a quick look")
    p.add_argument("--out", type=Path, default=None, help="write the Markdown result here")

    sub.add_parser("laws", help="List the law library.")
    consult.add_parser(sub)
    return parser


def _write_report(lab: Path, ledger: Ledger, question_entry: dict) -> Path:
    path = lab / "reports" / f"{question_entry['body']['id']}-{question_entry['seq']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(ledger, question_entry["hash"]))
    return path


def cmd_ask(args) -> int:
    question = Question.from_toml(args.question)
    lab = args.lab
    lab.mkdir(parents=True, exist_ok=True)
    ledger = Ledger(lab / "ledger.jsonl")
    records_file = f"records/{question.id}-{len(ledger)}.jsonl"
    experimenter = LatticeExperimenter(
        question, lab / records_file, workers=args.workers, progress=_stderr
    )
    outcome = ask(
        question,
        experimenter,
        ledger,
        provenance=provenance(),
        records_file=records_file,
        log=_stderr,
    )
    report = _write_report(lab, ledger, ledger.get(outcome.question_hash))
    print(
        json.dumps(
            {
                "question": question.id,
                "verdict": outcome.verdict,
                "law": outcome.law,
                "note": outcome.note,
                "rounds": outcome.rounds,
                "spent_cell_steps": outcome.spent_cell_steps,
                "report": str(report),
                "ledger_entry": outcome.question_hash,
            }
        )
    )
    return 0


def _find_question(ledger: Ledger, key: str | None) -> dict:
    questions = ledger.questions()
    if not questions:
        raise QuestionError("the ledger holds no questions")
    if key is None:
        return questions[-1]
    matches = [
        q
        for q in questions
        if q["body"]["id"] == key or str(q["seq"]) == key or q["hash"].startswith(key)
    ]
    if not matches:
        raise QuestionError(f"no question {key!r} in the ledger")
    return matches[-1]


def cmd_report(args) -> int:
    ledger = Ledger(args.lab / "ledger.jsonl")
    entry = _find_question(ledger, args.question)
    path = _write_report(args.lab, ledger, entry)
    print(json.dumps({"report": str(path)}))
    return 0


def cmd_verify(args) -> int:
    path = args.lab / "ledger.jsonl"
    if not path.is_file():
        raise QuestionError(f"no ledger at {path}")
    ledger = Ledger(path)
    problems = ledger.verify() + check_order(ledger, args.lab)
    installed = provenance()
    reruns = {"checked": 0, "identical": 0, "different": []}
    warnings = []
    for q in ledger.questions():
        recorded = (q["body"].get("provenance") or {}).get("latticelife", {}).get("commit")
        if recorded and recorded != installed["latticelife"].get("commit"):
            warnings.append(
                f"question {q['seq']} was run with LatticeLife {recorded[:10]}, "
                f"installed is {str(installed['latticelife'].get('commit'))[:10]}"
            )
        if not args.rerun or not q["body"].get("records_file"):
            continue
        if "spec" not in q["body"]:  # a study's records may come from several rules
            warnings.append(f"question {q['seq']}: no loop spec, so its records were not rerun")
            continue
        lines = record_lines(args.lab / q["body"]["records_file"])
        if not lines:
            continue
        spec = Question.from_dict(q["body"]["spec"])
        config = question_config(spec)
        sample = random.Random(q["hash"]).sample(lines, min(args.rerun, len(lines)))
        for offset, _, line in sample:
            reruns["checked"] += 1
            if rerun_record(json.loads(line), config).encode() == line:
                reruns["identical"] += 1
            else:
                reruns["different"].append({"question": q["seq"], "offset": offset})
    if reruns["different"]:
        problems.append(f"{len(reruns['different'])} rerun record(s) differ from the stored ones")
    print(
        json.dumps(
            {
                "entries": len(ledger),
                "questions": len(ledger.questions()),
                "problems": problems,
                "warnings": warnings,
                "reruns": reruns,
            }
        )
    )
    return 1 if problems else 0


def cmd_selfcheck(args) -> int:
    thresholds = load_thresholds(args.thresholds)
    result = run_selfcheck(thresholds, args.replicates, progress=_stderr)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_selfcheck(result))
    print(json.dumps(result))
    return 0 if result["passed"] else 1


def cmd_laws(args) -> int:
    for law in LAWS.values():
        variables = "" if law.variables == ("x",) else f" [in {', '.join(law.variables)}]"
        print(f"{law.name:22s} {law.formula:28s} {law.description}{variables}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    commands = {
        "ask": cmd_ask,
        "report": cmd_report,
        "verify": cmd_verify,
        "selfcheck": cmd_selfcheck,
        "laws": cmd_laws,
        "consult": lambda a: consult.main(a, _stderr),
    }
    try:
        return commands[args.command](args)
    except (QuestionError, LedgerError, consult.ConsultError, OSError) as exc:
        _stderr(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
