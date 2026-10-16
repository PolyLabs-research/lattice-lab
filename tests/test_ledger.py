"""The ledger: append-only, hash-chained, and the order check."""

import json

import numpy as np
import pytest

from lattice_lab.ledger import (
    GENESIS,
    Ledger,
    LedgerError,
    canonical,
    check_order,
    clean,
    record_lines,
    sha256_text,
)


def clock():
    return "2026-10-16T00:00:00+00:00"


def test_entries_chain_and_reload(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path, clock=clock)
    a = ledger.append("question", {"id": "q", "x": 1.5})
    b = ledger.append("plan", {"question": a["hash"], "values": [1, 2]})
    assert a["prev"] == GENESIS and b["prev"] == a["hash"] and b["seq"] == 1
    again = Ledger(path)
    assert again.entries == ledger.entries and again.verify() == []
    assert again.get(b["hash"])["body"]["values"] == [1, 2]
    assert [e["seq"] for e in again.for_question(a["hash"])] == [0, 1]


def test_clean_makes_plain_json():
    data = clean(
        {
            "a": np.float64(1.5),
            "b": np.array([1, 2]),
            "c": float("nan"),
            "d": (1, "x"),
            "e": np.bool_(True),
            "f": float("inf"),
        }
    )
    assert data == {"a": 1.5, "b": [1, 2], "c": None, "d": [1, "x"], "e": True, "f": None}
    assert canonical({"b": 1, "a": 2}) == '{"a":2,"b":1}'


@pytest.mark.parametrize("tamper", ["edit", "delete", "swap"])
def test_any_change_breaks_the_chain(tmp_path, tamper):
    path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path, clock=clock)
    for i in range(4):
        ledger.append("prediction", {"law": "power", "y": [float(i)]})
    lines = path.read_text().splitlines()
    if tamper == "edit":
        entry = json.loads(lines[1])
        entry["body"]["y"] = [99.0]  # a prediction quietly changed after the fact
        lines[1] = json.dumps(entry)
    elif tamper == "delete":
        del lines[2]
    else:
        lines[1], lines[2] = lines[2], lines[1]
    path.write_text("\n".join(lines) + "\n")
    assert Ledger(path).verify()


def test_a_partial_last_line_is_reported_and_blocks_appending(tmp_path):
    path = tmp_path / "ledger.jsonl"
    Ledger(path, clock=clock).append("question", {"id": "q"})
    with path.open("a") as f:
        f.write('{"seq": 1, "kind": "pl')
    ledger = Ledger(path)
    assert ledger.truncated and "partial line" in ledger.verify()[0]
    with pytest.raises(LedgerError):
        ledger.append("plan", {})


def test_unknown_kind_and_missing_hash():
    ledger = Ledger(None)
    with pytest.raises(ValueError):
        ledger.append("gossip", {})
    with pytest.raises(LedgerError):
        ledger.get("0" * 64)


def test_record_lines_offsets(tmp_path):
    path = tmp_path / "r.jsonl"
    path.write_bytes(b'{"a": 1}\n{"b": 2}\n{"c": 3')  # the last write was cut short
    lines = record_lines(path)
    assert [(o, line) for o, _, line in lines] == [(0, b'{"a": 1}'), (9, b'{"b": 2}')]
    assert lines[0][1] == sha256_text(b'{"a": 1}')


def _tested_round(tmp_path, *, predict_after_start=False, early_record=False, change=False):
    records = tmp_path / "records.jsonl"
    records.write_text('{"fit": 1}\n')
    ledger = Ledger(tmp_path / "ledger.jsonl", clock=clock)
    q = ledger.append("question", {"id": "q"})["hash"]
    if not predict_after_start:
        prediction = ledger.append("prediction", {"question": q, "law": "power"})
    run = ledger.append(
        "run_started",
        {"question": q, "records_file": "records.jsonl", "records_offset": records.stat().st_size},
    )
    if predict_after_start:
        prediction = ledger.append("prediction", {"question": q, "law": "power"})
    with records.open("a") as f:
        f.write('{"heldout": 1}\n')
    lines = record_lines(records)
    used = lines[0] if early_record else lines[1]
    observed = ledger.append(
        "observations", {"question": q, "records": [{"offset": used[0], "sha256": used[1]}]}
    )
    ledger.append(
        "verdict",
        {
            "question": q,
            "cites": {
                "predictions": [prediction["hash"]],
                "run_started": run["hash"],
                "heldout_observations": observed["hash"],
            },
        },
    )
    if change:
        records.write_text('{"fit": 1}\n{"heldout": 2}\n')
    return ledger


def test_order_check_passes_a_proper_round(tmp_path):
    assert check_order(_tested_round(tmp_path), tmp_path) == []


def test_order_check_catches_a_prediction_made_after_the_run_started(tmp_path):
    problems = check_order(_tested_round(tmp_path, predict_after_start=True), tmp_path)
    assert any("written after the run" in p for p in problems)


def test_order_check_catches_a_held_out_record_that_predates_the_run(tmp_path):
    problems = check_order(_tested_round(tmp_path, early_record=True), tmp_path)
    assert any("predates the run" in p for p in problems)


def test_order_check_catches_a_changed_record(tmp_path):
    problems = check_order(_tested_round(tmp_path, change=True), tmp_path)
    assert any("missing or changed" in p for p in problems)
