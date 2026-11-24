"""
A first look at worlds of several species, zoomed out. Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-closure/look.py [--workers 2] [--quick]

Three worlds, the ones the scale-up test followed to large grids: Life against HighLife under
the standoff (side 1024, 1,024 generations), and soup 19 under the standoff and under the
random draw (side 512, 512 generations). Each is run from sixteen fresh starts and read through
blocks of 4, 8, 16 and 32 with the clock at the block (zoom.py). Coarse rules are learned from
eight of the starts (7001 to 7008) and tried on the other eight (7009 to 7016).

What is measured, in the alphabets `leader`, `moved` and `leader+moved`:

- **one generation ahead.** On the starts a rule did not learn from, how often each view of a
  supercell (nothing, the supercell, its neighbour counts, its neighbours in place) calls the
  next symbol, and its surprise in bits. For a rule learned from the whole run, and for one
  learned in one period (up to generation 256, or after it) tried in the other: a coarse rule
  worth the name is the same rule at every time.
- **the rule for movement.** The chance that a block moves next, by whether it just moved and
  by how many of its eight neighbours did.
- **stillness.** The blocks that moved although nothing around them had. Under the standoff
  there can be none (zoom.py's first known answer).
- **many generations ahead.** From the zoomed-out world at generation 128 the coarse rule is
  run on by itself, by its likeliest symbol and by draws. The share of blocks moving is set
  beside the fine world's own at each later generation, and so are the supercells where the
  likeliest-symbol run and the fine world differ, beside how many differ from where they
  started.

The fine runs are kept in ~/lattice-lab-runs/closure/cache (about 300 MB), so the analysis can
be run again without them. The summary goes to look/summary.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scale-up-compete"))

import zoom  # noqa: E402
from first_look import HIGHLIFE, LIFE, soup_rules  # noqa: E402

OUT = HERE / "look"
CACHE = Path.home() / "lattice-lab-runs" / "closure" / "cache"
WORLDS = {
    "pair standoff": {"rules": (LIFE, HIGHLIFE), "kind": "standoff", "side": 1024,
                      "generations": 1024},
    "soup standoff": {"rules": soup_rules(19), "kind": "standoff", "side": 512,
                      "generations": 512},
    "soup random": {"rules": soup_rules(19), "kind": "random", "side": 512, "generations": 512},
}  # fmt: skip
QUICK = {"side": 256, "generations": 256}
BLOCKS = (4, 8, 16, 32)
LEARN = tuple(range(7001, 7009))
TRY = tuple(range(7009, 7017))
ALPHABETS = ("leader", "moved", "leader+moved")
SPLIT = 256  # the generation that parts the early period from the late one
FROM = 128  # the generation the coarse rule is run on from
DRAWS = 2


def world(name: str, quick: bool) -> dict:
    return {**WORLDS[name], **(QUICK if quick else {})}


# --- the fine runs -------------------------------------------------------------------------------


def cache_path(name: str, seed: int, quick: bool) -> Path:
    w = world(name, quick)
    return CACHE / f"{name.replace(' ', '-')}-{w['side']}-{w['generations']}-{seed}.npz"


def run_fine(job: tuple[str, int, bool]) -> str:
    """One world from one start, read through every block and kept on disk."""
    name, seed, quick = job
    path = cache_path(name, seed, quick)
    if not path.exists():
        w = world(name, quick)
        start = zoom.mixed_start(w["side"], seed, len(w["rules"]))
        found = zoom.histories(
            w["rules"], w["kind"], w["side"], start, w["generations"], BLOCKS, seed=seed
        )
        arrays = {}
        for block, history in found.items():
            arrays[f"counts_{block}"] = history.counts
            arrays[f"moved_{block}"] = history.moved
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, **arrays)
    return str(path)


def load(name: str, seed: int, block: int, quick: bool) -> zoom.History:
    with np.load(cache_path(name, seed, quick)) as kept:
        return zoom.History(block, block, kept[f"counts_{block}"], kept[f"moved_{block}"])


# --- one world at one block ----------------------------------------------------------------------


def periods(first: int, block: int, generations: int) -> dict[str, tuple[int, int]]:
    """The coarse generations of each period: early up to SPLIT, late after it."""
    cut = min(SPLIT, generations // 2) // block
    return {"early": (first, cut), "late": (cut, generations // block)}


def tidy(score: dict) -> dict:
    seen = max(score["transitions"], 1)
    return {
        "transitions": score["transitions"],
        "wrong_per_thousand": round(1000 * (1 - score["right"] / seen), 3),
        "bits_each": round(score["bits"] / seen, 5),
    }


def removed(scores: dict, by: str, over: str = "own") -> dict:
    """The share of the `over` view's errors, and of its surprise, that the `by` view removes."""
    wrong = lambda kind: scores[kind]["transitions"] - scores[kind]["right"]  # noqa: E731
    return {
        "errors": round(1 - wrong(by) / max(wrong(over), 1), 4),
        "bits": round(1 - scores[by]["bits"] / max(scores[over]["bits"], 1e-12), 4),
    }


def follow(rule: zoom.CoarseRule, kind: str, symbols: np.ndarray, first: int, seed: int) -> dict:
    """zoom.follow with the draws named by the start's seed."""
    return zoom.follow(rule, kind, symbols, first, np.random.default_rng([20261124, seed]), DRAWS)


def average(found: list[dict]) -> dict:
    """The mean over the starts at each horizon, and for the drawn run its share of the fine
    world's movement start by start: the mean of that ratio and its spread over the starts."""
    out = {"horizon": found[0]["horizon"]}
    for key in ("fine", "likely", "drawn", "differ", "drifted"):
        out[key] = [round(float(v), 6) for v in np.mean([f[key] for f in found], axis=0)]
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = np.array([f["drawn"] for f in found]) / np.array([f["fine"] for f in found])
    out["drawn_over_fine"] = [round(float(v), 4) for v in ratio.mean(axis=0)]
    if len(found) > 1:
        out["drawn_over_fine_spread"] = [round(float(v), 4) for v in ratio.std(axis=0, ddof=1)]
    return out


def study(job: tuple[str, int, bool]) -> tuple[str, int, dict]:
    """Everything measured of one world at one block."""
    name, block, quick = job
    w = world(name, quick)
    generations, species = w["generations"], len(w["rules"])
    out: dict = {"supercells": (w["side"] // block) ** 2, "steps": generations // block}
    rules: dict[str, dict[str, zoom.CoarseRule]] = {}
    shape = {}
    blank = zoom.History(block, block, np.zeros((2, species, 1, 1)), np.zeros((2, 1, 1), bool))
    for alphabet in ALPHABETS:
        _, q, first = zoom.states(blank, alphabet)
        shape[alphabet] = (q, first)
        rules[alphabet] = {p: zoom.CoarseRule.empty(q) for p in ("early", "late")}
    unstable = 0
    for seed in LEARN:
        history = load(name, seed, block, quick)
        unstable += zoom.unstable(history)
        for alphabet in ALPHABETS:
            symbols, q, first = zoom.states(history, alphabet)
            for period, (a, b) in periods(first, block, generations).items():
                rules[alphabet][period] = rules[alphabet][period].learn(symbols, a, b)
    for alphabet in ALPHABETS:
        rules[alphabet]["whole"] = rules[alphabet]["early"].plus(rules[alphabet]["late"])

    scores = {
        alphabet: {
            rule: {period: {kind: {"transitions": 0, "right": 0, "bits": 0.0}
                            for kind in zoom.KINDS} for period in ("early", "late")}
            for rule in ("whole", "early", "late")
        }
        for alphabet in ALPHABETS
    }  # fmt: skip
    shares = {alphabet: [] for alphabet in ALPHABETS}
    ahead: dict[str, dict[str, list]] = {}
    marks = [g for g in (FROM, SPLIT, generations // 2, generations) if g <= generations]
    for seed in TRY:
        history = load(name, seed, block, quick)
        unstable += zoom.unstable(history)
        for alphabet in ALPHABETS:
            symbols, q, first = zoom.states(history, alphabet)
            shares[alphabet].append(
                [np.bincount(symbols[g // block].ravel(), minlength=q) / symbols[0].size
                 for g in marks]
            )  # fmt: skip
            for rule in ("whole", "early", "late"):
                for period, (a, b) in periods(first, block, generations).items():
                    for kind in zoom.KINDS:
                        got = rules[alphabet][rule].score(kind, symbols, a, b)
                        for key, value in got.items():
                            scores[alphabet][rule][period][kind][key] += value
            if "moved" in alphabet and FROM // block >= first and FROM < generations:
                kinds = ("own", "total", "full") if alphabet == "moved" else ("own", "total")
                for kind in kinds:
                    found = follow(rules[alphabet]["whole"], kind, symbols, FROM // block, seed)
                    ahead.setdefault(alphabet, {}).setdefault(kind, []).append(found)
    out["moved_from_stillness"] = unstable
    for alphabet in ALPHABETS:
        q, first = shape[alphabet]
        table = {
            "symbols": q,
            "views_met": {k: int(rules[alphabet]["whole"].tables[k].rows.size) for k in zoom.KINDS},
            "share_of_each_symbol": {
                str(g): [round(float(v), 5) for v in np.mean(shares[alphabet], axis=0)[i]]
                for i, g in enumerate(marks)
            },
            "one_generation": {},
        }
        for rule in ("whole", "early", "late"):
            for period in ("early", "late"):
                got = scores[alphabet][rule][period]
                table["one_generation"][f"{rule} rule, {period} period"] = {
                    **{kind: tidy(got[kind]) for kind in zoom.KINDS},
                    "neighbour_counts_remove": removed(got, "total"),
                    "neighbours_in_place_remove": removed(got, "full"),
                    "the_supercell_removes": removed(got, "own", "nothing"),
                }
        if alphabet in ahead:
            table["many_generations"] = {
                "from_generation": FROM,
                "clock": block,
                **{kind: average(found) for kind, found in ahead[alphabet].items()},
            }
        if alphabet == "moved":
            table["rule_for_movement"] = {}
            for period in ("whole", "early", "late"):
                seen = rules[alphabet][period].tables["total"]
                grid = np.zeros((2, 9, 2), dtype=np.int64)
                grid[seen.rows // 9, seen.rows % 9] = seen.counts
                with np.errstate(invalid="ignore", divide="ignore"):
                    chance = grid[..., 1] / grid.sum(axis=-1)
                table["rule_for_movement"][period] = {
                    "after_still": [None if np.isnan(v) else round(float(v), 5) for v in chance[0]],
                    "after_moved": [None if np.isnan(v) else round(float(v), 5) for v in chance[1]],
                    "seen_still": grid[0].sum(axis=-1).tolist(),
                    "seen_moved": grid[1].sum(axis=-1).tolist(),
                    # the tallies themselves, [was it moving][moving neighbours][does it move]
                    "tally": grid.tolist(),
                }
        out[alphabet] = table
    return name, block, out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--quick", action="store_true", help="side 256, 256 generations")
    parser.add_argument("--worlds", nargs="+", default=list(WORLDS), choices=list(WORLDS))
    args = parser.parse_args()
    fine = [(name, seed, args.quick) for name in args.worlds for seed in LEARN + TRY]
    jobs = [(name, block, args.quick) for name in args.worlds for block in BLOCKS]
    summary: dict = {"worlds": {}}
    out = OUT.with_name("look-quick") if args.quick else OUT
    out.mkdir(exist_ok=True)
    if (out / "summary.json").exists():
        summary = json.loads((out / "summary.json").read_text())
    with ProcessPoolExecutor(args.workers) as pool:
        list(pool.map(run_fine, fine))
        for name, block, found in pool.map(study, jobs):
            w = world(name, args.quick)
            entry = summary["worlds"].setdefault(name, {})
            entry.update(
                rules=list(w["rules"]), tie_break=w["kind"], side=w["side"],
                generations=w["generations"], learned_from=[LEARN[0], LEARN[-1]],
                tried_on=[TRY[0], TRY[-1]],
            )  # fmt: skip
            entry.setdefault("blocks", {})[str(block)] = found
            print(f"{name}, block {block}: moved from stillness {found['moved_from_stillness']}")
            for alphabet in ALPHABETS:
                got = found[alphabet]["one_generation"]["whole rule, late period"]
                print(
                    f"   {alphabet}: wrong per thousand "
                    + ", ".join(f"{kind} {got[kind]['wrong_per_thousand']}" for kind in zoom.KINDS)
                    + f"; neighbour counts remove {got['neighbour_counts_remove']}"
                )
            (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")


if __name__ == "__main__":
    main()
