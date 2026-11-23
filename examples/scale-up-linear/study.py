"""
A registered calibration of the scale-up instrument, on linear rules.

    uv run --no-sync python examples/scale-up-linear/study.py register
    uv run --no-sync python examples/scale-up-linear/study.py run --workers 1
    uv run --no-sync lattice-lab verify --lab examples/scale-up-linear

**The idea.** To follow a rule to larger scales, zoom out: replace each block of fine cells by
one supercell and ask whether some rule on the supercells predicts the zoomed-out fine run
(docs/scale-up-plan.md). The instrument that asks it is a closure test (scaleup.py): run the fine
world and then zoom out, or zoom out and then run the coarse world, and count the supercells
where the two differ. Before that count is trusted on rules whose answer nobody knows, it is
tried here where the answer is a theorem.

For a rule that is linear over GF(2), the library proves both halves (proofs/LatticeProofs/
GroupRing.lean): 2^k generations are one generation of the same rule with every neighbour 2^k
cells away (`gstep_iterate_two_pow`, Frobenius), and each coset of the sublattice 2^k Z^2 then
runs as a copy of the rule on the torus 2^k times smaller (`restrict_iterate`). So zooming out by
2^k, with the clock slowed by 2^k, is exact, and the coarse rule is the fine rule itself.

**The worlds.** LatticeLife's four parity rules on its own wrapped grids: B1357/S1357 and
B1357/S02468 on the square, B135/S135 and B135/S0246 on the hexagon. The triangle is left out:
its rule is a 2 x 2 matrix M with M^2 = s I, and it is s that scales, not M.

**Predictions**, one ledger entry per case:

- *H0, the mechanism.* On the fine grid itself, 2^k generations equal one generation of the same
  rule on the adjacency with neighbours 2^k apart: no cell differs, for 2^k from 2 to 128.
- *H1, the known zero.* With a block of b = 2^k and a clock of b, no supercell differs after any
  number of coarse generations, for three ways of reading a supercell: the fine cell at the
  block's corner, the fine cell at another fixed place in the block, and the parity of the whole
  block. b runs from 2 to 128.
- *H2, the known half.* Where the scales do not match, the two routes differ by a non-zero
  linear functional of the start, so from a uniformly random start every supercell is a fair
  coin. mismatch.py works out, from the group ring alone, how many of those coins are
  independent. A control is registered where the answer is all of them or all but one, since the
  total is then a binomial count, exactly, or to within the number of starts: a block of 3 (the
  scale-up is exact at powers of two only), a clock one generation early, a clock at half
  speed, a clock one generation late, and the wrong coarse rule. Its total over the starts must
  lie in the interval registered with it, which a correct instrument leaves with probability
  at most ALPHA.

The verdict is `calibrated` when every case holds, `not calibrated` when any fails, and
`incomplete` otherwise (a missing record, or a zero case in which both routes were dead
throughout, which tests nothing).

**What the registration had seen** is in the question's `excluded_seen`.

**Added after the verdict** (2026-11-23, the plan's step 1): `rerun`, which computes one stored
record again so that `lattice-lab verify` can check it, and the import it needs. Nothing that
ran was changed, but this file's sha256 is no longer the one in the question.
"""

from __future__ import annotations

import functools
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import mismatch  # noqa: E402
import scaleup  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

RULES = {"square": ("B1357/S1357", "B1357/S02468"), "hexagon": ("B135/S135", "B135/S0246")}
OTHER = {
    "B1357/S1357": "B1357/S02468",
    "B1357/S02468": "B1357/S1357",
    "B135/S135": "B135/S0246",
    "B135/S0246": "B135/S135",
}

ZERO_SEEDS = (1, 2, 3)
CONTROL_SEEDS = tuple(range(1, 65))
ALPHA = 1e-6
# Fine sides the instrument was written and tested on. No registered case uses one.
SEEN_SIDES = (12, 16, 18, 24)

# H0: (fine side, dilation). 48 with 32 wraps more than half-way round the torus.
MECHANISM = {
    "square": ((96, 2), (96, 4), (100, 8), (150, 16), (257, 32), (48, 32), (192, 64), (320, 128)),
    "hexagon": ((96, 2), (96, 4), (100, 8), (150, 16), (258, 32), (48, 32), (192, 64), (320, 128)),
}
# H1: coarse sides, each at blocks 2, 4, 8 and 16; then (coarse side, block) at larger blocks.
COARSE = {"square": (5, 14, 20, 37), "hexagon": (10, 14, 22, 38)}
BLOCKS = (2, 4, 8, 16)
LARGE = {"square": ((14, 32), (5, 64), (5, 128)), "hexagon": ((14, 32), (6, 64), (6, 128))}
# H2: (kind, block, clock, coarse rule is the other parity rule), each at these coarse sides.
CONTROLS = (
    ("a block of 3", 3, 3, False),
    ("one generation early", 4, 3, False),
    ("half speed", 4, 2, False),
    ("one generation late", 4, 5, False),
    ("the wrong coarse rule", 4, 4, True),
)
CONTROL_COARSE = (20, 32)


def steps_for(block: int) -> int:
    """Coarse generations a zero case is followed for: fewer at large blocks, where each one is
    `block` fine generations."""
    return 8 if block <= 16 else 4 if block == 32 else 2


def mechanism_case(shape: str, rule: str, side: int, dilation: int) -> dict:
    """H0: `dilation` generations of the rule against one generation of the same rule with
    neighbours `dilation` apart, cell for cell on one grid."""
    return {
        "hypothesis": "H0",
        "kind": "neighbours 2^k apart",
        "shape": shape,
        "rule": rule,
        "side": side,
        "block": 1,
        "clock": dilation,
        "projection": "identity",
        "offset": [0, 0],
        "coarse_rule": rule,
        "coarse_side": side,
        "coarse_dilation": dilation,
        "seeds": list(ZERO_SEEDS),
        "coarse_steps": 3 if dilation <= 32 else 2,
    }


def zoom_case(shape, rule, coarse, block, clock, projection, offset, coarse_rule, matched) -> dict:
    """H1 (`matched`) and H2: the rule on the grid of side block * coarse, zoomed out by `block`
    and compared with `coarse_rule` on LatticeLife's own grid of side `coarse`."""
    return {
        "hypothesis": "H1" if matched else "H2",
        "kind": "matched scales",
        "shape": shape,
        "rule": rule,
        "side": block * coarse,
        "block": block,
        "clock": clock,
        "projection": projection,
        "offset": list(offset),
        "coarse_rule": coarse_rule,
        "coarse_side": coarse,
        "coarse_dilation": 1,
        "seeds": list(ZERO_SEEDS if matched else CONTROL_SEEDS),
        "coarse_steps": steps_for(block) if matched else 1,
    }


def control_candidates() -> list[dict]:
    """Every control considered, with what the group ring says of it (mismatch.law)."""
    out = []
    for shape in scaleup.SHAPES:
        for rule in RULES[shape]:
            for kind, block, clock, swap in CONTROLS:
                for coarse in CONTROL_COARSE:
                    coarse_rule = OTHER[rule] if swap else rule
                    case = zoom_case(
                        shape, rule, coarse, block, clock, "decimate", (0, 0), coarse_rule, False
                    )
                    law = mismatch.law(shape, rule, case["side"], block, clock, coarse_rule)
                    out.append({**case, "kind": kind, **law})
    return out


def cases() -> list[dict]:
    """Every registered case, in order, each with what it predicts."""
    out = [
        mechanism_case(shape, rule, side, dilation)
        for shape in scaleup.SHAPES
        for rule in RULES[shape]
        for side, dilation in MECHANISM[shape]
    ]
    for shape in scaleup.SHAPES:
        pairs = [(coarse, block) for coarse in COARSE[shape] for block in BLOCKS]
        for rule in RULES[shape]:
            for coarse, block in pairs + list(LARGE[shape]):
                for projection, offset in (
                    ("decimate", (0, 0)),
                    ("decimate", (block - 1, block // 2)),
                    ("parity", (0, 0)),
                ):
                    out.append(
                        zoom_case(shape, rule, coarse, block, block, projection, offset, rule, True)
                    )
    for case in out:
        case["predicted"] = "zero"
        case["law"] = "no supercell differs, at any coarse generation, from any start"
    for candidate in control_candidates():
        if candidate["zero"]:
            raise AssertionError(f"a control that should differ does not: {candidate}")
        deficiency = candidate["supercells"] - candidate["rank"]
        if deficiency > 1:
            continue  # listed in the question's controls_left_out
        if deficiency == 1 and not candidate["even"]:
            raise AssertionError(f"rank N - 1 without the even-weight constraint: {candidate}")
        low, high = mismatch.pooled_acceptance(
            candidate["supercells"], deficiency, len(CONTROL_SEEDS), ALPHA
        )
        case = {k: v for k, v in candidate.items() if k not in ("zero", "even")}
        out.append(
            {
                **case,
                "predicted": "half",
                "law": "the supercells that differ after one coarse generation, added over the "
                "starts, are a binomial count of fair coins"
                + ("" if deficiency == 0 else ", each start's count being even"),
                "trials": len(CONTROL_SEEDS) * candidate["supercells"],
                "alpha": ALPHA,
                "accept": [low, high],
            }
        )
    for number, case in enumerate(out):
        case["case"] = number
        if case["side"] in SEEN_SIDES:
            raise AssertionError(f"case {number} uses a fine side the instrument was tested on")
        _diagram(case)  # raises here, before registration, if the geometry does not exist
    return out


def _diagram(case: dict) -> scaleup.Diagram:
    fine = scaleup.World(case["shape"], case["rule"], case["side"])
    coarse = scaleup.World(
        case["shape"], case["coarse_rule"], case["coarse_side"], case["coarse_dilation"]
    )
    projection = scaleup.Projection(case["projection"], case["block"], tuple(case["offset"]))
    return scaleup.Diagram(fine, coarse, projection, case["clock"])


def bundles(registered: list[dict]) -> list[list[dict]]:
    """The cases grouped so that each group shares one fine run: the same fine world, clock,
    starts and number of coarse generations."""
    groups: dict[tuple, list[dict]] = {}
    for case in registered:
        key = (case["shape"], case["rule"], case["side"], case["clock"], case["coarse_steps"],
               tuple(case["seeds"]))  # fmt: skip
        groups.setdefault(key, []).append(case)
    return list(groups.values())


def run_bundle(job: tuple[list[dict], int]) -> list[dict]:
    """One fine run from one start, and every case of the bundle read off it."""
    group, seed = job
    first = group[0]
    start = scaleup.random_start(first["shape"], first["side"], seed)
    results, last = scaleup.closure([_diagram(c) for c in group], start, first["coarse_steps"])
    return [
        {
            "case": case["case"],
            "seed": seed,
            "supercells": result.supercells,
            "mismatches": list(result.mismatches),
            "live": list(result.live),
            "start_sha256": scaleup.digest(start),
            "fine_sha256": last,
        }
        for case, result in zip(group, results, strict=True)
    ]


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {(r["case"], r["seed"]) for r in map(json.loads, path.read_text().splitlines())}
    jobs = []
    for group in bundles(cases()):
        for seed in group[0]["seeds"]:
            todo = [case for case in group if (case["case"], seed) not in done]
            if todo:
                jobs.append((todo, seed))
    jobs.sort(key=lambda job: -(job[0][0]["side"] ** 2) * job[0][0]["clock"])  # slowest first
    if workers <= 1:
        for job in jobs:
            append_records(path, run_bundle(job))
        return
    with ProcessPoolExecutor(workers) as pool:
        for rows in pool.map(run_bundle, jobs):
            append_records(path, rows)


def judge(case: dict, rows: list[dict]) -> dict:
    """One case against its records: `holds`, `fails`, `missing` or `untested`."""
    seeds = {r["seed"] for r in rows}
    if seeds != set(case["seeds"]) or len(rows) != len(seeds):
        return {"outcome": "missing", "seeds": len(seeds)}
    if any(len(r["mismatches"]) != case["coarse_steps"] for r in rows):
        return {"outcome": "missing", "seeds": len(seeds)}
    if case["predicted"] == "zero":
        worst = max(max(r["mismatches"]) for r in rows)
        if worst:
            bad = next(r for r in sorted(rows, key=lambda r: r["seed"]) if max(r["mismatches"]))
            return {"outcome": "fails", "seed": bad["seed"], "mismatches": bad["mismatches"],
                    "supercells": bad["supercells"]}  # fmt: skip
        if not any(v for r in rows for v in r["live"]):
            return {"outcome": "untested", "why": "both routes were dead at every generation"}
        return {"outcome": "holds"}
    total = sum(r["mismatches"][0] for r in rows)
    low, high = case["accept"]
    return {
        "outcome": "holds" if low <= total <= high else "fails",
        "total": total,
        "trials": case["trials"],
        "fraction": round(total / case["trials"], 5),
        "accept": [low, high],
    }


def decide(rows: list[dict], registered: list[dict]) -> dict:
    by_case: dict[int, list[dict]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    summary = {
        h: {"cases": 0, "holds": 0, "fails": 0, "missing": 0, "untested": 0}
        for h in ("H0", "H1", "H2")
    }
    failures, controls = [], []
    for case in registered:
        result = judge(case, by_case.get(case["case"], []))
        counts = summary[case["hypothesis"]]
        counts["cases"] += 1
        counts[result["outcome"]] += 1
        label = {k: case[k] for k in ("case", "hypothesis", "kind", "shape", "rule", "side",
                                      "block", "clock", "projection", "offset")}  # fmt: skip
        if result["outcome"] != "holds":
            failures.append({**label, **result})
        if case["predicted"] == "half" and "total" in result:
            controls.append({**label, **result})
    outcomes = {o for h in summary.values() for o in ("fails", "missing", "untested") if h[o]}
    verdict = (
        "not calibrated" if "fails" in outcomes else "incomplete" if outcomes else "calibrated"
    )
    return {
        "verdict": verdict,
        "hypotheses": summary,
        "not_holding": failures,
        "controls": controls,
        "largest_block": max(c["block"] * c["coarse_dilation"] for c in registered),
        "largest_fine_side": max(c["side"] for c in registered),
    }


def question() -> dict:
    registered = cases()
    left_out = [
        {k: c[k] for k in ("kind", "shape", "rule", "side", "block", "clock", "supercells", "rank")}
        for c in control_candidates()
        if c["supercells"] - c["rank"] > 1
    ]
    return {
        "id": "scale-up-linear",
        "title": "Does the scale-up instrument recover the two known answers for linear rules?",
        "statement": "A closure test (scaleup.py) runs a fine world for s * clock generations and "
        "then zooms out, or zooms out and then runs a coarse world for s generations, and counts "
        "the supercells where the two differ. For LatticeLife's four parity rules on the square "
        "and the hexagon it must count none where the scales match (H0, H1), and a fair coin per "
        "supercell where they do not (H2).",
        "source": "a conversation on 2026-11-23 about a measurable scale-up process for the "
        "lab's rules; docs/scale-up-plan.md",
        "theorems": {
            "H0": "gstep_iterate_two_pow (proofs/LatticeProofs/GroupRing.lean): 2^k steps of D "
            "are one step of 2^k D, on every torus",
            "H1": "restrict_iterate (the same file), with H0: read along a coset of the "
            "sublattice, the rule 2^k D on G is the rule D on the sub-torus",
            "H2": "from the group ring by machine (mismatch.py), not formalised: the two routes "
            "differ by the functional f^T + g(x^b, y^b), and the rank of its translates by the "
            "sublattice says how many supercells are independent fair coins",
        },
        "rules": RULES,
        "cases": {h: sum(c["hypothesis"] == h for c in registered) for h in ("H0", "H1", "H2")},
        "starts": "scaleup.random_start: every cell 0 or 1 with probability 1/2, from "
        "numpy.random.default_rng([20261123, shape, side, seed]); seeds 1 to 3 for H0 and H1, "
        "1 to 64 for H2. Cases with the same fine grid share their starts.",
        "alpha": ALPHA,
        "controls_left_out": {
            "why": "their mismatch functionals have rank below supercells - 1, so the total is "
            "not a binomial count and no exact interval is known for it",
            "controls": left_out,
        },
        "verdict_rule": "calibrated: every case holds. not calibrated: any case fails. "
        "incomplete: otherwise. A zero case holds when no supercell differs at any coarse "
        "generation from any start, and the fine route was not dead throughout. A control holds "
        "when its total over the starts, after one coarse generation, lies in its interval.",
        "sha256": {
            f: hashlib.sha256((HERE / f).read_bytes()).hexdigest()
            for f in ("scaleup.py", "mismatch.py", "study.py")
        },
        "excluded_seen": [
            "The instrument was written and tested on fine sides 12, 16, 18 and 24 only, with "
            "seeds from 9001 (tests/test_scale_up_linear.py and the session that wrote it): H0 "
            "at dilations 2 to 16, H1 at blocks 2 and 4, and controls at blocks 2, 3 and 4 with "
            "clocks 1 to 5. All the zero cases counted zero and every rank matched the engine's "
            "own. No registered case uses those sides.",
            "For the controls, f^T was computed in the group ring at the registered sizes, and "
            "at coarse sides 28 and 36, to get each rank (mismatch.law). That is the prediction's "
            "derivation and it runs no cellular automaton.",
            "For timing, Conway's Life (B3/S23), which is not in this study, was stepped 10 "
            "generations on the 256 and 512 square tori and the 512 hexagon torus, and with two "
            "and three species on the 512 square torus.",
            "For the plan (docs/scale-up-plan.md), the second-order form of the four rules and "
            "of Conway's Life, next = F(now) + before, was run on sides 12 and 24.",
            "LatticeLife's engine has not been run on any registered case.",
        ],
    }


def predictions() -> list[dict]:
    return cases()


@functools.lru_cache(maxsize=1)
def _registered() -> tuple[dict, ...]:
    return tuple(cases())


def rerun(record: dict) -> dict:
    """One stored record, computed again from its case and seed (for `lattice-lab verify`)."""
    return run_bundle(([_registered()[record["case"]]], record["seed"]))[0]


STUDY = Study(
    directory=HERE,
    question=question,
    predictions=predictions,
    execute=execute,
    decide=decide,
    rerun=rerun,
)

if __name__ == "__main__":
    main(STUDY)
