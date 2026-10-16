"""The discovery loop: propose, fit, rank, pre-register, choose the next experiment, run, judge,
record.

    ask(question, experimenter, ledger)

1. Record the question, with the code that answers it (`question` entry).
2. Measure the fit sizes (`run_started`, `observations`). Sizes whose seeds never all settle,
   even at `max_cap`, are kept in the record and left out of every fit.
3. Each round:
   a. Propose and fit: every law in the question's library, fitted to the complete sizes.
   b. Rank by BIC with an Occam window. No eligible law: the verdict is "none fits".
   c. Choose the held-out sizes where the laws still in play disagree most, within the budget
      (`plan`).
   d. Pre-register: every eligible law's predictions at those sizes, with bands and their
      covariance, one `prediction` entry each, before anything runs there.
   e. Run the held-out sizes (`run_started`, `observations`).
   f. Judge the recorded predictions against the measurements; for a law found, check it is
      not fragile (`verdict`, citing every prediction, the run and the observations).
   g. A law found, or every law rejected, ends the question. Otherwise the held-out sizes join
      the fit and, if rounds and budget remain, another round starts.

`Outcome` is the last verdict, with what is needed to report it. Every number in it is also in
the ledger, so a report can be rebuilt from the ledger alone (`report.render`).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from kepler import rank

from lattice_lab.analysis import choose_space, decide, fit_laws, fragility, prediction_body
from lattice_lab.experiment import Experimenter, Observation
from lattice_lab.ledger import Ledger
from lattice_lab.planner import plan_heldout
from lattice_lab.question import Question, cells_of

FINAL = ("found", "none fits")


@dataclass
class Outcome:
    question: Question
    question_hash: str
    verdict: str
    law: str | None
    note: str
    rounds: int
    spent_cell_steps: int
    verdict_hash: str
    entries: list[str] = field(default_factory=list)


def _estimated_cost(question: Question, labels) -> float:
    return sum(cells_of(label) * question.cap * question.seeds for label in labels)


def ask(
    question: Question,
    experimenter: Experimenter,
    ledger: Ledger,
    *,
    provenance: dict | None = None,
    records_file: str | None = None,
    log: Callable[[str], None] | None = None,
) -> Outcome:
    log = log or (lambda message: None)
    asked_before = len(ledger.questions())
    q_entry = ledger.append(
        "question",
        {
            "id": question.id,
            "title": question.title(),
            "spec": question.to_dict(),
            "provenance": provenance or {},
            "records_file": records_file,
            "questions_asked_before": asked_before,
        },
    )
    qh = q_entry["hash"]
    written = [qh]

    def record(kind: str, body: dict) -> dict:
        entry = ledger.append(kind, {"question": qh, **body})
        written.append(entry["hash"])
        return entry

    budget = question.budget_cell_steps
    spent = 0

    def finish(round_no: int, verdict: str, note: str, **body) -> Outcome:
        body.setdefault("final", True)
        entry = record(
            "verdict",
            {
                "round": round_no,
                "verdict": verdict,
                "note": note,
                "law": body.pop("law", None),
                "spent_cell_steps": spent,
                **body,
            },
        )
        log(f"verdict: {verdict}" + (f" ({entry['body']['law']})" if entry["body"]["law"] else ""))
        return Outcome(
            question,
            qh,
            verdict,
            entry["body"]["law"],
            note,
            round_no,
            spent,
            entry["hash"],
            written,
        )

    if _estimated_cost(question, question.fit_sizes) > budget:
        return finish(0, "inconclusive", "the budget does not cover one run of the fit sizes")

    # Fit sizes.
    log(f"measuring the fit sizes {list(question.fit_sizes)}")
    run = record(
        "run_started",
        {
            "round": 0,
            "role": "fit",
            "labels": list(question.fit_sizes),
            "records_file": records_file,
            "records_offset": experimenter.offset(),
        },
    )
    measured = experimenter.measure(list(question.fit_sizes), budget)
    spent += measured.spent_cell_steps
    fit_entry = record(
        "observations",
        {
            "round": 0,
            "role": "fit",
            "run": run["hash"],
            "rows": [o.to_json() for o in measured.observations],
            "records": measured.records,
            "spent_cell_steps": measured.spent_cell_steps,
            "notes": measured.notes,
        },
    )
    fit_obs: list[Observation] = [o for o in measured.observations if o.complete]
    fit_entries = [fit_entry["hash"]]
    pool = list(question.heldout_pool)
    space = choose_space(question, fit_obs)

    for round_no in range(1, question.max_rounds + 1):
        if len(fit_obs) < question.min_points:
            return finish(
                round_no,
                "inconclusive",
                f"only {len(fit_obs)} sizes settled completely; {question.min_points} "
                "are needed to fit",
                cites={"fit_observations": fit_entries},
            )

        # Propose, fit, rank.
        fits = fit_laws(question.laws, fit_obs, space)
        ranking = rank(fits)
        fits_json = {f.name: f.to_dict() for f in fits}
        if ranking.best is None:
            return finish(
                round_no,
                "none fits",
                ranking.note,
                ranking=ranking.to_dict(),
                fits=fits_json,
                cites={"fit_observations": fit_entries},
            )

        # Choose the next experiment.
        plan = plan_heldout(question, ranking, fit_obs, pool, space, budget - spent)
        plan_entry = record(
            "plan",
            {
                "round": round_no,
                "space": space,
                "fit_labels": [o.label for o in fit_obs],
                "ranking": ranking.to_dict(),
                "fits": fits_json,
                **plan,
            },
        )
        labels = plan["chosen"]
        log(f"round {round_no}: {ranking.note}; held-out sizes {labels}")
        if not labels:
            return finish(
                round_no,
                "inconclusive",
                "no held-out size is left in the pool, or none fits the budget",
                ranking=ranking.to_dict(),
                cites={"fit_observations": fit_entries, "plan": plan_entry["hash"]},
            )

        # Pre-register.
        predictions: dict[str, dict] = {}
        prediction_hashes: list[str] = []
        for entry in ranking.entries:
            if not entry.eligible:
                continue
            body = prediction_body(entry.fit, labels)
            predicted = record(
                "prediction", {"round": round_no, "plan": plan_entry["hash"], **body}
            )
            predictions[entry.name] = predicted["body"]
            prediction_hashes.append(predicted["hash"])

        # Run.
        run = record(
            "run_started",
            {
                "round": round_no,
                "role": "heldout",
                "labels": labels,
                "records_file": records_file,
                "records_offset": experimenter.offset(),
            },
        )
        measured = experimenter.measure(labels, budget - spent)
        spent += measured.spent_cell_steps
        held_entry = record(
            "observations",
            {
                "round": round_no,
                "role": "heldout",
                "run": run["hash"],
                "rows": [o.to_json() for o in measured.observations],
                "records": measured.records,
                "spent_cell_steps": measured.spent_cell_steps,
                "notes": measured.notes,
            },
        )
        heldout = measured.observations

        # Judge.
        decision = decide(question, fit_obs, heldout, predictions, space)
        verdict, note = decision["verdict"], decision["note"]
        # For readers only: every law, rejected or not, refitted to every size. It shows whether
        # a rejection rests on the law's shape or only on its extrapolation from the fit sizes.
        context_fits = fit_laws(question.laws, [*fit_obs, *heldout], space)
        context = rank(context_fits)
        variants = []
        if verdict == "found":
            variants = fragility(question, fit_obs, heldout, decision, space)
            flips = [v for v in variants if not v["agrees"]]
            if flips:
                verdict = "fragile"
                note = (
                    f"{decision['law']} passed, but the verdict flips "
                    f"{'; '.join(v['variant'] + ' (' + str(v['leading']) + ')' for v in flips)}"
                )
        cites = {
            "predictions": prediction_hashes,
            "run_started": run["hash"],
            "heldout_observations": held_entry["hash"],
            "fit_observations": fit_entries,
            "plan": plan_entry["hash"],
        }
        law = decision["law"] if verdict == "found" else None
        last_round = round_no == question.max_rounds or verdict in FINAL
        outcome = finish(
            round_no,
            verdict,
            note,
            law=law,
            leading=decision["leading"],
            tests=decision["tests"],
            survivors=decision["survivors"],
            rivals=decision["rivals"],
            combined_ranking=decision["combined_ranking"],
            combined_fits=decision["combined_fits"],
            all_data_ranking=context.to_dict(),
            all_data_fits={f.name: f.to_dict() for f in context_fits},
            fit_ranking=ranking.to_dict(),
            fits=fits_json,
            robustness=variants,
            space=space,
            final=last_round,
            cites=cites,
        )
        if last_round:
            return outcome
        # Not settled: the held-out sizes join the fit, and the next round looks further.
        fit_obs = fit_obs + [o for o in heldout if o.complete]
        fit_entries.append(held_entry["hash"])
        pool = [label for label in pool if label not in labels]
    return outcome  # pragma: no cover - the loop always returns inside
