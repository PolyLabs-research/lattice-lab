"""
What else the scale-up test's runs show. Exploratory: nothing here was registered.

    uv run --no-sync python examples/scale-up-sizes/extras.py

Reads the step-2 runs (sides 32 to 256, examples/scale-up-compete) together with the runs of
whichever registered parts have a verdict (sides 512 and 1024; 2048 and 4096 once the large
part has run), and writes extras.json:

- **the power of the side each spread follows**, refitted over every side there is. Step 2 gave
  these with errors of 0.07 to 0.10; the test held the power at -1 and asked whether the
  amplitude carried over. With a longer run of sides the power itself is known better.
- **each mean at every side**, the constant refitted over all of them, and how a trend with the
  side ranks against it.
- **the rare species' blocks** at each side: per run, per million cells, and the variance of
  their number over its mean (1 for independent blocks).
- **the claims' scores**: how many of the registered comparisons were beyond 2 and beyond 3
  standard errors, which says whether the errors quoted were the right size.
- **whether the large grids agree with each other.** A registered claim compares a large grid
  with the small grids' constant, whose error is several times the large grid's own. The
  sharper question is whether the means at sides 512 and up agree among themselves: their
  weighted mean, the chi-square against it, and the chance of one that large.
- **the fresh starts of recheck.py**, where there are any, beside the registered sample they
  repeat.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sizes  # noqa: E402
from scipy import stats  # noqa: E402
from sizes import laws  # noqa: E402

from lattice_lab.ledger import Ledger  # noqa: E402

PARTS = (HERE, HERE.parent / "scale-up-sizes-large")
QUANTITIES = ("live", "share", "unlike")
LARGE = 512  # the sides the registered parts ran begin here
RECHECK = HERE / "recheck" / "records.jsonl"


def runs_by_world_and_side() -> tuple[dict, dict]:
    """Every run, by (world, side): step 2's, and those of the parts that have a verdict. Also
    the verdicts, by part."""
    runs: dict[tuple[str, int], list[dict]] = {}
    for line in (laws.OUT / "records.jsonl").read_text().splitlines():
        record = json.loads(line)
        runs.setdefault((laws.world_of(record), int(record["cells"] ** 0.5)), []).append(record)
    verdicts = {}
    for part in PARTS:
        path = part / "ledger.jsonl"
        if not path.exists():
            continue
        entries = Ledger(path).entries
        if entries[-1]["kind"] != "verdict":
            continue
        verdicts[part.name] = entries[-1]["body"]
        for row in entries[-2]["body"]["rows"]:
            runs.setdefault((row["world"], row["side"]), []).append(row)
    return runs, verdicts


def blocks(runs: list[dict], species: int) -> dict:
    """The blocks of four cells left of species number `species` (from 0), over `runs`."""
    counts = [r["alive"][species][-1] for r in runs]
    units = [c / 4 for c in counts]
    mean = statistics.fmean(units)
    return {
        "starts": len(runs),
        "blocks_per_run": round(mean, 2),
        "per_million_cells": round(mean / runs[0]["cells"] * 1e6, 2),
        "variance_over_mean": round(statistics.variance(units) / mean, 2) if mean else None,
        "starts_with_none": counts.count(0),
        "every_count_a_multiple_of_four": all(c % 4 == 0 for c in counts),
    }


def agreement(by_side: dict[int, list[float]]) -> dict:
    """Whether the means at these sides agree with each other: each mean with its standard
    error, their weighted mean, the chi-square of the means against it and the chance of a
    chi-square that large if one constant lay behind them all."""
    sides = sorted(by_side)
    means = [statistics.fmean(by_side[s]) for s in sides]
    errors = [statistics.stdev(by_side[s]) / math.sqrt(len(by_side[s])) for s in sides]
    weights = [1.0 / e**2 for e in errors]
    centre = sum(w * m for w, m in zip(weights, means, strict=True)) / sum(weights)
    chi2 = sum(w * (m - centre) ** 2 for w, m in zip(weights, means, strict=True))
    gaps = [
        (abs(means[i] - means[j]) / math.hypot(errors[i], errors[j]), sides[i], sides[j])
        for i in range(len(sides))
        for j in range(i + 1, len(sides))
    ]
    widest = max(gaps) if gaps else (0.0, None, None)
    return {
        "sides": sides,
        "mean": [laws.signif(m) for m in means],
        "se": [laws.signif(e) for e in errors],
        "weighted_mean": [laws.signif(centre), laws.signif(math.sqrt(1.0 / sum(weights)))],
        "chi2": round(chi2, 2),
        "dof": len(sides) - 1,
        "chance": laws.signif(float(stats.chi2.sf(chi2, len(sides) - 1)), 3),
        "widest_gap": {"standard_errors": round(widest[0], 2), "sides": [widest[1], widest[2]]},
    }


def mean_and_error(values: list[float]) -> tuple[float, float]:
    return statistics.fmean(values), statistics.stdev(values) / math.sqrt(len(values))


def rechecks(runs: dict) -> list[dict]:
    """The fresh starts of recheck.py, by world and side, beside the registered sample."""
    if not RECHECK.exists():
        return []
    fresh: dict[tuple[str, int], list[dict]] = {}
    for line in RECHECK.read_text().splitlines():
        record = json.loads(line)
        fresh.setdefault((laws.world_of(record), int(record["cells"] ** 0.5)), []).append(record)
    out = []
    for (world, side), found in sorted(fresh.items()):
        seeds = [r["seed"] for r in found]
        row: dict = {"world": world, "side": side, "starts": len(found)}
        row["seeds"] = [min(seeds), max(seeds)]
        for quantity in QUANTITIES:
            new = [laws.measure(r, quantity, -1) for r in found]
            old = [laws.measure(r, quantity, -1) for r in runs.get((world, side), [])]
            entry = {"fresh": [laws.signif(v) for v in mean_and_error(new)]}
            if len(old) > 1:
                (mean, error), (was, its) = mean_and_error(new), mean_and_error(old)
                entry["registered"] = [laws.signif(was), laws.signif(its)]
                scale = math.hypot(error, its)
                entry["gap_in_standard_errors"] = round((mean - was) / scale, 2) if scale else None
                entry["together"] = [laws.signif(v) for v in mean_and_error(new + old)]
            row[quantity] = entry
        out.append(row)
    return out


def scores(verdict: dict) -> dict:
    found = [abs(d["score"]) for d in verdict["details"].values() if "score" in d]
    return {
        "comparisons": len(found),
        "beyond_2": sum(s > 2 for s in found),
        "beyond_3": sum(s > 3 for s in found),
        "largest": max(found),
        "expected_beyond_2": round(len(found) * 0.0455, 1),
        "root_mean_square": round(math.sqrt(statistics.fmean(s * s for s in found)), 2),
    }


def analyse() -> dict:
    runs, verdicts = runs_by_world_and_side()
    fitted = sizes.load_results()["worlds"]
    out: dict = {"sides": sorted({side for _, side in runs}), "worlds": {}, "scores": {}}
    for world in laws.WORLDS:
        sides = sorted(side for w, side in runs if w == world)
        row: dict = {"starts": {str(s): len(runs[world, s]) for s in sides}}
        for quantity in QUANTITIES:
            by_side = {s: [laws.measure(r, quantity, -1) for r in runs[world, s]] for s in sides}
            mean, spread = laws.size_law(by_side), laws.spread_law(by_side)
            row[quantity] = {
                "mean": mean["mean"],
                "se": mean["se"],
                "law": mean["law"],
                "constant": mean.get("constants") if mean["law"] == "constant" else None,
                "ranking": mean.get("ranking"),
                "spread": spread["spread"],
                "power_of_the_side": spread["constants"]["b"],
                "power_at_sides_32_to_256": fitted[world]["against_size"][quantity]["spread"][
                    "constants"
                ]["b"],
                "amplitude": [spread["inverse"]["a"], spread["inverse"]["se_log"]],
                "amplitude_chi2_per_dof": spread["inverse"]["chi2_per_dof"],
            }
            large = {s: v for s, v in by_side.items() if s >= LARGE}
            if len(large) > 1:
                row[quantity]["large_grids_agree"] = agreement(large)
        rare = fitted[world].get("blocks")
        if rare:
            row["blocks"] = {str(s): blocks(runs[world, s], rare["species"] - 1) for s in sides}
        row["all_species_alive"] = {
            str(s): sum(all(e is None for e in r["extinct_at"]) for r in runs[world, s])
            for s in sides
        }
        out["worlds"][world] = row
    for name, verdict in verdicts.items():
        out["scores"][name] = scores(verdict)
    out["recheck"] = rechecks(runs)
    return out


def main() -> None:
    results = analyse()
    (HERE / "extras.json").write_text(json.dumps(results, indent=1) + "\n")
    print("sides:", results["sides"])
    for world, row in results["worlds"].items():
        for quantity in QUANTITIES:
            q = row[quantity]
            print(
                f"{world}: {quantity}: spread falls as side^{q['power_of_the_side'][0]:.3f} "
                f"± {q['power_of_the_side'][1]:.3f} (was {q['power_at_sides_32_to_256'][0]:.3f} "
                f"± {q['power_at_sides_32_to_256'][1]:.3f}); mean {q['law']} {q['constant']}"
            )
            agree = q.get("large_grids_agree")
            if agree:
                print(
                    f"   sides {agree['sides']}: chi2 {agree['chi2']} on {agree['dof']}, chance "
                    f"{agree['chance']}; widest gap {agree['widest_gap']}"
                )
        for side, found in row.get("blocks", {}).items():
            print(f"{world}: side {side}: blocks {found}")
    for name, found in results["scores"].items():
        print(f"{name}: scores {found}")
    for row in results["recheck"]:
        print(f"recheck: {row}")


if __name__ == "__main__":
    main()
