"""Reports: a question's story in Markdown, rebuilt from the ledger alone.

Every number in a report is read from ledger entries, and every prediction is shown with the
entry that recorded it, so a reader can check that it was written before the run that tested it
(`lattice-lab verify` does that mechanically).
"""

from __future__ import annotations

import math

import numpy as np
from kepler import LAWS

from lattice_lab.ledger import Ledger


def _fmt(value, digits: int = 3) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if not math.isfinite(value):
            return "-"
        if abs(value) < 1e-12:
            return "0"
        if abs(value) >= 1e6 or abs(value) < 1e-3:
            return f"{value:.{digits}g}"
        return np.format_float_positional(
            value, precision=digits, unique=False, fractional=False, trim="-"
        )
    return str(value)


def _short(digest: str | None) -> str:
    return f"`{digest[:12]}`" if digest else "-"


def _formula(law: str) -> str:
    formula = LAWS[law].formula if law in LAWS else law
    return "T(L) = " + formula.replace("x", "L").replace("exp", "exp")


def _constants(fit: dict | None) -> str:
    if not fit or not fit.get("params"):
        return "-"
    parts = []
    for name, value in fit["params"].items():
        error = (fit.get("stderr") or {}).get(name)
        parts.append(f"{name} = {_fmt(value, 4)} ± {_fmt(error, 2)}")
    return ", ".join(parts)


def _code(prov: dict, name: str) -> str:
    state = prov.get(name) or {}
    commit = state.get("commit")
    text = f"{state.get('version') or '?'}"
    if commit:
        text += f" @ `{commit[:10]}`" + (" (uncommitted changes)" if state.get("dirty") else "")
    return text


def render(ledger: Ledger, question_hash: str) -> str:
    entries = ledger.for_question(question_hash)
    question = entries[0]
    spec = question["body"]["spec"]
    prov = question["body"].get("provenance") or {}
    verdicts = [e for e in entries if e["kind"] == "verdict"]
    final = verdicts[-1] if verdicts else None
    asked = len(ledger.questions())
    number = question["body"].get("questions_asked_before", 0) + 1

    lines = [f"# {question['body']['title']}", ""]
    if final is None:
        lines += ["**No verdict yet**: the question was interrupted before its first verdict.", ""]
    else:
        body = final["body"]
        law = body.get("law")
        headline = f"**Verdict: {body['verdict']}**"
        if law:
            headline += f": {law}, `{_formula(law)}`"
        elif body.get("leading"):
            headline += f" (leading: {body['leading']})"
        lines += [headline, "", body["note"] + ".", ""]
        if law:
            lines += _answer(body, law)

    lines += [
        "| | |",
        "| --- | --- |",
        f"| Question | `{spec['id']}`, ledger entry {question['seq']} {_short(question_hash)} |",
        f"| Asked | {question['time']} |",
        f"| Experiment | {spec['rule']} on {spec['shape']} tori, density {spec['density']:g}, "
        f"{spec['seeds']} seeds per size, caps {spec['cap']:,} to {spec['max_cap']:,} |",
        f"| Laws considered | {', '.join(spec['laws'])} |",
        f"| Code | lattice-lab {_code(prov, 'lattice_lab')}; "
        f"LatticeLife {_code(prov, 'latticelife')}; Kepler {_code(prov, 'kepler')}; "
        f"Python {prov.get('python', '?')} |",
        f"| Records | `{question['body'].get('records_file') or '-'}` |",
        f"| Questions in this ledger | {asked} (this was number {number}); every one asked is "
        "counted, since scanning many rules turns up chance fits |",
    ]
    if final is not None:
        lines.append(f"| Compute | {_fmt(final['body'].get('spent_cell_steps'))} cell updates |")
    lines.append("")

    for observation in (e for e in entries if e["kind"] == "observations"):
        if observation["body"]["role"] == "fit" and observation["body"]["round"] == 0:
            lines += ["## Fit sizes", ""]
            lines += _data_table(observation["body"])
    for verdict in verdicts:
        lines += _round(ledger, entries, verdict)

    lines += [
        "## Checking this report",
        "",
        "`lattice-lab verify --lab <lab>` checks that no ledger entry was edited, that every "
        "prediction was written before the run that tested it and that every held-out record was "
        "appended after it, and reruns records to confirm they reproduce byte for byte.",
        "",
    ]
    return "\n".join(lines)


def _answer(body: dict, law: str) -> list[str]:
    fit = (body.get("fits") or {}).get(law)
    combined = (body.get("combined_fits") or {}).get(law)
    test = next((t for t in body.get("tests", []) if t["law"] == law), None)
    lines = []
    if fit:
        lines.append(f"- Fitted to the fit sizes (what was pre-registered): {_constants(fit)}.")
    if combined:
        lines.append(f"- Refitted to every measured size: {_constants(combined)}.")
    if test and test.get("m"):
        lines.append(
            f"- Held out: {test['inside']} of {test['m']} sizes inside the 95% band; joint "
            f"chi-square test p = {_fmt(test['p'], 2)}."
        )
    robust = body.get("robustness") or []
    if robust:
        agree = sum(v["agrees"] for v in robust)
        lines.append(
            f"- Robustness: {agree} of {len(robust)} reduced fits (smallest sizes dropped, "
            "each size left out) lead with the same law."
        )
    return [*lines, ""]


def _data_table(body: dict) -> list[str]:
    lines = [
        "| Size | L | Seeds | Median settling time | 95% interval | Unsettled | Note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in body["rows"]:
        interval = f"{_fmt(row['low'])} to {_fmt(row['high'])}" if row["complete"] else "-"
        lines.append(
            f"| {row['label']} | {_fmt(row['x'])} | {row['seeds']} | {_fmt(row['y'])} | "
            f"{interval} | {row['unsettled']} | {row['note'] or ''} |"
        )
    for note in body.get("notes") or []:
        lines.append(f"\n{note}")
    return [*lines, ""]


def _round(ledger: Ledger, entries: list[dict], verdict: dict) -> list[str]:
    body = verdict["body"]
    round_no = body["round"]
    cites = body.get("cites") or {}
    lines = [f"## Round {round_no}: {body['verdict']}", ""]
    plan = ledger.get(cites["plan"]) if cites.get("plan") else None
    ranking = (plan["body"]["ranking"] if plan else body.get("ranking")) or {}
    fits = (plan["body"]["fits"] if plan else body.get("fits")) or {}
    if ranking:
        space = plan["body"]["space"] if plan else body.get("space", "?")
        fit_labels = plan["body"]["fit_labels"] if plan else []
        lines += [
            f"### Fits to {len(fit_labels) or '?'} sizes ({space} space)",
            "",
            f"{ranking.get('note', '')}.",
            "",
            "| Law | ΔBIC | Constants | R² | Eligible |",
            "| --- | --- | --- | --- | --- |",
        ]
        for entry in ranking.get("entries", []):
            fit = fits.get(entry["name"])
            eligible = "yes" if entry["eligible"] else f"no: {entry['reason']}"
            lines.append(
                f"| {entry['name']} | {_fmt(entry['delta_bic'], 2)} | {_constants(fit)} | "
                f"{_fmt(entry['r2'], 4)} | {eligible} |"
            )
        lines.append("")
    if plan and plan["body"].get("chosen"):
        chosen = plan["body"]["chosen"]
        lines += [
            f"Held-out sizes chosen: {', '.join(str(c) for c in chosen)}, where "
            f"{', '.join(plan['body']['contenders'])} disagree most for the budget.",
            "",
        ]
    predictions = [ledger.get(h) for h in cites.get("predictions", [])]
    run = ledger.get(cites["run_started"]) if cites.get("run_started") else None
    if predictions and run:
        lines += [
            f"### Predictions, recorded before the run (entry {run['seq']}) started",
            "",
            "| Law | Size | Predicted | 95% band | Entry |",
            "| --- | --- | --- | --- | --- |",
        ]
        for p in predictions:
            pb = p["body"]
            for i, label in enumerate(pb["labels"]):
                lines.append(
                    f"| {pb['law']} | {label} | {_fmt(pb['y'][i])} | {_fmt(pb['low'][i])} "
                    f"to {_fmt(pb['high'][i])} | {p['seq']} {_short(p['hash'])} |"
                )
        lines.append("")
    held = ledger.get(cites["heldout_observations"]) if cites.get("heldout_observations") else None
    if held:
        lines += ["### Held-out measurements", ""]
        lines += _data_table(held["body"])
    tests = body.get("tests") or []
    if tests:
        lines += [
            "### Held-out tests",
            "",
            "| Law | Result | p (joint chi-square) | Inside 95% band |",
            "| --- | --- | --- | --- |",
        ]
        for t in tests:
            inside = f"{t['inside']} of {t['m']}" if t["m"] else "-"
            lines.append(f"| {t['law']} | {t['status']} | {_fmt(t['p'], 2)} | {inside} |")
        skipped = sorted({str(s) for t in tests for s in t.get("skipped", [])})
        if skipped:
            lines.append(
                f"\nNot tested (seeds unsettled at every cap): sizes {', '.join(skipped)}."
            )
        lines.append("")
    combined = body.get("combined_ranking")
    if combined:
        lines += [
            "### Laws that passed, refitted to every size",
            "",
            "| Law | ΔBIC | Constants |",
            "| --- | --- | --- |",
        ]
        for entry in combined.get("entries", []):
            fit = (body.get("combined_fits") or {}).get(entry["name"])
            lines.append(f"| {entry['name']} | {_fmt(entry['delta_bic'], 2)} | {_constants(fit)} |")
        lines.append("")
    context = body.get("all_data_ranking")
    if context:
        lines += [
            "### Context: every law refitted to every size",
            "",
            "Not part of the verdict, which rests on the pre-registered predictions. It shows "
            "whether a rejected law fails in shape or only in its extrapolation from the fit "
            "sizes.",
            "",
            "| Law | ΔBIC | Constants | Eligible |",
            "| --- | --- | --- | --- |",
        ]
        for entry in context.get("entries", []):
            fit = (body.get("all_data_fits") or {}).get(entry["name"])
            eligible = "yes" if entry["eligible"] else f"no: {entry['reason']}"
            lines.append(
                f"| {entry['name']} | {_fmt(entry['delta_bic'], 2)} | {_constants(fit)} | "
                f"{eligible} |"
            )
        lines.append("")
    robust = body.get("robustness") or []
    if robust:
        lines += [
            "### Robustness",
            "",
            "| Variant | Leading law | Verdict | Same law |",
            "| --- | --- | --- | --- |",
        ]
        for v in robust:
            lines.append(
                f"| {v['variant']} | {v['leading'] or '-'} | {v['verdict']} | "
                f"{'yes' if v['agrees'] else 'NO'} |"
            )
        lines.append("")
    lines += [f"Verdict entry {verdict['seq']} {_short(verdict['hash'])}.", ""]
    return lines
