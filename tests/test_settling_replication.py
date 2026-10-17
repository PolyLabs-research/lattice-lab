"""The B2/S34 settling-time replication (examples/settling-time-replication): its ledger is intact
and ordered, its verdict is what the write-up reports, and its decision code tells the two
mechanisms apart on synthetic data drawn from each."""

import importlib.util
import json
import math
from pathlib import Path

import numpy as np

from lattice_lab.ledger import Ledger, check_order

LAB = Path(__file__).resolve().parent.parent / "examples" / "settling-time-replication"


def _study():
    spec = importlib.util.spec_from_file_location("settling_replication", LAB / "study.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_ledger_is_intact_and_the_verdict_holds():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == ["question"] + ["prediction"] * 8 + ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["survivors"] == ["logarithmic"] and verdict["unsettled"] == []
    assert verdict["laws"]["power"]["status"] == "rejected"
    assert verdict["laws"]["logarithmic"]["inside"] == 6
    gumbel = verdict["mechanisms"]["extreme value, light tails (Gumbel)"]
    assert gumbel["status"] == "rejected"
    assert [k for k, t in gumbel["tests"].items() if not t["passes"]] == ["iqr"]
    assert verdict["mechanisms"]["extreme value, heavy tails (Frechet)"]["status"] == "rejected"


def test_the_decision_tells_the_mechanisms_apart():
    study = _study()
    registered = [e["body"] for e in Ledger(LAB / "ledger.jsonl").entries[1:9]]
    template = json.loads((LAB / "records.jsonl").read_text().splitlines()[0])
    rng = np.random.default_rng(1)

    def records(kind):
        out = []
        for size in study.SIZES:
            for seed in range(1, 101):
                if kind == "gumbel":
                    t = 37.6 * math.log(size) - 36.3 - 18.8 * 0.3665 + rng.gumbel(0, 18.8)
                else:
                    scale = 22.3 * size**0.398 / math.log(2) ** (-1 / 5.03)
                    t = scale * (-math.log(rng.random())) ** (-1 / 5.03)
                t = int(round(t))
                out.append(dict(template, grid=size, seed=seed, transient=t, stopped_at=t + 2))
        return out

    for kind, law, mechanism in (
        ("gumbel", "logarithmic", "extreme value, light tails (Gumbel)"),
        ("frechet", "power", "extreme value, heavy tails (Frechet)"),
    ):
        verdict = study.decide(records(kind), registered)
        assert verdict["survivors"] == [law]
        statuses = {m: r["status"] for m, r in verdict["mechanisms"].items()}
        assert statuses[mechanism] == "consistent"
        assert list(statuses.values()).count("consistent") == 1
