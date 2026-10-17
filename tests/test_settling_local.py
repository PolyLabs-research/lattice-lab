"""Round 2 of the B2/S34 settling-time study (examples/settling-time-local): the ledger is intact
and ordered, the verdict is what docs/settling-time.md reports, and pooling every global
measurement gives the ratio of spread to slope it states."""

import math
from pathlib import Path

import numpy as np
from latticelife.experiments.observables import median_transient

from lattice_lab import extremes
from lattice_lab.ledger import Ledger, check_order

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
LAB = EXAMPLES / "settling-time-local"


def test_the_ledger_is_intact_and_the_verdict_holds():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds == ["question"] + ["prediction"] * 6 + ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["statuses"] == {
        "k, plain extreme values": "consistent",
        "k, fading correction": "rejected",
        "the local tail accounts for the spread": "consistent",
        "the local tail accounts for the slope": "consistent",
        "stationarity": "consistent",
        "independence": "rejected",
    }
    assert verdict["t_min"] == 144.0 and verdict["blocks_1024"] == 60 * 16384
    assert verdict["late_block_neighbours"]["share_with_a_late_neighbour"] > 0.95
    rows = ledger.entries[-2]["body"]["rows"]
    assert all(max(r["local"]["8"]) == r["transient"] for r in rows)


def test_pooled_global_data_give_the_gumbel_ratio():
    study_a = Ledger(EXAMPLES / "settling-time-replication" / "ledger.jsonl").entries[-2]["body"]
    times = {
        int(r.grid): list(r.settling_times) for r in median_transient(study_a["rows"]) if r.complete
    }
    for r in Ledger(LAB / "ledger.jsonl").entries[-2]["body"]["rows"]:
        times[r["grid"]].append(r["transient"])
    f = extremes.fluctuations(times)
    sizes = sorted(f)
    slope, slope_se = extremes.weighted_slope(
        np.log(sizes), [f[n]["median"] for n in sizes], [f[n]["median_error"] for n in sizes]
    )
    iqr, iqr_se = extremes.weighted_mean(
        [f[n]["iqr"] for n in sizes], [f[n]["iqr_error"] for n in sizes]
    )
    ratio = iqr / slope
    error = ratio * math.hypot(iqr_se / iqr, slope_se / slope)
    assert abs(ratio - 0.765) < 0.005 and abs(error - 0.042) < 0.005
    assert abs(ratio - extremes.gumbel_iqr_per_slope(2)) < 2 * error
