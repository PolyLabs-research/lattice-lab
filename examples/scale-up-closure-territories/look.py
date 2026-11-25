"""
A first look at worlds of territories, zoomed out. Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-closure-territories/look.py [--workers 2]

Step 4 zoomed out two worlds of patches and found maps of where things still move, with no
rule that is the same from one block size to the next. Steps 4b and 4c found worlds of another
kind: two species with one rule between them, each counting only its own kind, which sort into
territories that go on growing. Two of them are looked at here with step 4's instrument
(examples/scale-up-closure/zoom.py), each under the standoff from a full start:

    still   B245678/S3678: two grounds that fill in and stop, and the walls between them
    busy    B23467/S4568: two grounds that stay busy inside, their shares of the grid level

Each is run on a wrapped grid of side 1,024 for 4,096 generations from eight fresh starts
(15001 to 15008) and read through blocks of 4, 8, 16 and 32. Coarse rules are learned from
four of the starts and tried on the other four.

**What a block is read as** (an alphabet):

    leader             the species with more cells in the block (0: none, or a tie)
    leader+contested   the leader, and whether its rival holds a tenth or more of the block's
                       live cells

**Two clocks.** Step 4 slowed the clock by the block: one coarse generation was b fine ones,
because nothing travels faster than a cell a generation. Step 4b's areas said these worlds
keep another time: seen through blocks twice the size they are the same picture four times
later, not twice. So every block is read on two clocks:

    block    one coarse generation is b fine ones: 4, 8, 16, 32
    square   one coarse generation is b x b / 4 fine ones: 4, 16, 64, 256

They are the same clock at blocks of 4. The square clock runs four times slower for each
doubling of the block, the block clock twice.

**What is measured**, from generation 64 on (the first generations are the sorting-out):

- **one generation ahead.** On the starts a rule did not learn from, how often each view of a
  block (nothing, the block, its neighbour counts, its neighbours in place) calls the next
  symbol, and its surprise in bits.
- **changing hands.** The chance that a block has a new leader one coarse generation on, by
  how many of its eight neighbours its rival leads.
- **one rule at every time.** A rule learned before generation 1,024 tried after it, against
  the rule learned after it.
- **one rule at every rung.** The rule learned at blocks of b tried at blocks of 2b, against
  the rule learned there. A rule that serves at the next rung as well as that rung's own is
  what this ladder calls a fixed point, and step 4 found none. A grid read through blocks
  twice the size has a quarter of the blocks, and on the square clock a quarter of the
  coarse generations as well, so the rule from the rung below has learned from far more and
  would win on that alone: it is tried a second time having learned from as many transitions
  as the rung's own rule (`as much data`).
- **the same at matched ages.** If the world through blocks twice the size is the same
  picture four times later, the rungs should be compared at ages that match: blocks of 4
  over generations 64 to 256, blocks of 8 over 256 to 1,024, blocks of 16 over 1,024 to
  4,096, each on the square clock. Changing hands and the rule from the rung below are
  measured again that way.
- **many generations ahead.** From the zoomed-out world at generation 1,024 the coarse rule
  is run on by itself, drawing every block's next symbol from its table of neighbour counts,
  with no fine cells under it. Two things are read off it. The walls it keeps (the share of
  neighbouring blocks under different leaders), beside the fine world's: whether its world
  is the same kind of world. And the plan's closure error, the share of blocks whose leader
  is not the fine world's at the same generation: whether it is the same world. That is set
  beside two others: the start itself, had nothing moved, and a second run of the rule from
  the same start with other draws, which says how much of the error is the rule's own dice.
- **one rule for both worlds** (`between`). The rule learned in one world tried in the
  other, against the rule learned there, at every block on both clocks. The two worlds have
  nothing in common cell by cell: if their rules meet as the block grows, the ladder has
  found something that is not in either rule.

The fine runs are kept in ~/lattice-lab-runs/closure-territories/cache, so the analysis can
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
sys.path.insert(0, str(HERE.parent / "scale-up-closure"))

import zoom  # noqa: E402

OUT = HERE / "look"
CACHE = Path.home() / "lattice-lab-runs" / "closure-territories" / "cache"
WORLDS = {
    "still": {"rules": ("B245678/S3678",) * 2, "kind": "standoff"},
    "busy": {"rules": ("B23467/S4568",) * 2, "kind": "standoff"},
}
SIDE, GENERATIONS = 1024, 4096
BLOCKS = (4, 8, 16, 32)
LEARN = tuple(range(15001, 15005))
TRY = tuple(range(15005, 15009))
ALPHABETS = ("leader", "leader+contested")
CLOCKS = ("block", "square")
CONTESTED = 0.1  # the rival's share of a block's live cells that makes the block contested
FROM = 64  # the generation the reading starts at
SPLIT = 1024  # the generation that parts the early period from the late one
EVERY = 16  # a transition is read every so many generations at least
VIEWS = ("total", "full")  # the views a rule is tried with across times and rungs
LEADER = np.array([0, 1, 2, 1, 2], dtype=np.int8)  # the leader of each of the five symbols


def clock(name: str, block: int) -> int:
    """The fine generations in one coarse generation at blocks of `block`."""
    return block if name == "block" else block * block // 4


def age(block: int) -> tuple[int, int]:
    """The generations over which blocks of `block` are read at matched ages: FROM to four
    times FROM at blocks of 4, and four times later for each doubling of the block."""
    scale = (block // 4) ** 2
    return FROM * scale, 4 * FROM * scale


# --- the fine runs -------------------------------------------------------------------------------


def symbols(counts: np.ndarray) -> np.ndarray:
    """Every block as one of five symbols, from the two species' counts in it: 0 where neither
    leads; 1 and 2 where a species leads and its rival holds under a tenth of the block's live
    cells; 3 and 4 where species 1 or 2 leads a contested block."""
    first, second = counts[0].astype(np.int64), counts[1].astype(np.int64)
    leader = np.where(first > second, 1, np.where(second > first, 2, 0))
    contested = np.minimum(first, second) >= CONTESTED * (first + second)
    return np.where(leader == 0, 0, leader + 2 * contested).astype(np.int8)


def cache_path(name: str, seed: int, side: int, generations: int) -> Path:
    return CACHE / f"{name}-{side}-{generations}-{seed}.npz"


def run_fine(job: tuple[str, int, int, int]) -> str:
    """One world from one start, read through every block every `block` generations and kept
    on disk: for each block the symbols of every reading, and every 64 generations each
    species' share of the grid."""
    name, seed, side, generations = job
    path = cache_path(name, seed, side, generations)
    if path.exists():
        return str(path)
    world = WORLDS[name]
    grid = zoom.lattice(world["rules"], world["kind"], side)
    start = zoom.mixed_start(side, seed, 2, density=1.0)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])
    frames = {b: [symbols(zoom.read(grid.occupancy, side, b, 2))] for b in BLOCKS}
    shares = []
    for generation in range(1, generations + 1):
        grid.step(rng)
        for b in BLOCKS:
            if generation % b == 0:
                frames[b].append(symbols(zoom.read(grid.occupancy, side, b, 2)))
        if generation % 64 == 0:
            shares.append([float((grid.occupancy == s).mean()) for s in (1, 2)])
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, shares=np.array(shares),
                        **{f"symbols_{b}": np.stack(frames[b]) for b in BLOCKS})  # fmt: skip
    return str(path)


def load(name: str, seed: int, side: int, generations: int) -> dict:
    with np.load(cache_path(name, seed, side, generations)) as kept:
        return {"shares": kept["shares"], **{b: kept[f"symbols_{b}"] for b in BLOCKS}}


# --- transitions ---------------------------------------------------------------------------------


def instants(block: int, tick: int, first: int, last: int) -> list[int]:
    """The generations at which a transition of `tick` generations is read between `first`
    and `last`: one after another, but no more often than every EVERY generations."""
    start = -(-first // block) * block
    return list(range(start, last - tick + 1, max(tick, EVERY)))


def pairs(frames: np.ndarray, block: int, tick: int, first: int, last: int, alphabet: str):
    """A run's transitions at one block and clock: the blocks at each instant, and the same
    blocks one coarse generation later, in `alphabet`."""
    at = np.array(instants(block, tick, first, last), dtype=np.int64)
    own, after = frames[at // block], frames[(at + tick) // block]
    if alphabet == "leader":
        own, after = LEADER[own], LEADER[after]
    return own, after


def tally(
    rule: zoom.CoarseRule,
    own: np.ndarray,
    after: np.ndarray,
    keep: float = 1.0,
    rng: np.random.Generator | None = None,
) -> zoom.CoarseRule:
    """`rule` with these transitions tallied in, under every view. With `keep` under 1, only
    that share of them, drawn by `rng`: a rule learned from as few transitions as another."""
    tables = dict(rule.tables)
    for a in range(0, own.shape[0], 8):
        before, later = own[a : a + 8], after[a : a + 8]
        around = zoom.ring(before)
        kept = None if keep >= 1 else rng.random(later.shape) < keep
        for kind in zoom.KINDS:
            view = zoom.codes(kind, before, around, rule.q)
            if kept is not None:
                tables[kind] = tables[kind].add(view[kept], later[kept])
            else:
                tables[kind] = tables[kind].add(view, later)
    return zoom.CoarseRule(rule.q, tables)


def score(rule: zoom.CoarseRule, kind: str, own: np.ndarray, after: np.ndarray) -> dict:
    """How well the table of `kind` foretells these transitions: how many there are, how many
    it called right, and its surprise in bits in all."""
    seen = right = 0
    bits = 0.0
    for a in range(0, own.shape[0], 8):
        before, later = own[a : a + 8], after[a : a + 8]
        chance = rule.chances(kind, before, zoom.ring(before))
        seen += later.size
        right += int((chance.argmax(axis=-1) == later).sum())
        given = np.take_along_axis(chance, later[..., None].astype(np.int64), axis=-1)
        bits += float(-np.log2(given).sum())
    return {"transitions": seen, "right": right, "bits": bits}


def add(first: dict, second: dict) -> dict:
    return {k: first[k] + second[k] for k in first}


def tidy(found: dict) -> dict:
    seen = max(found["transitions"], 1)
    return {
        "transitions": found["transitions"],
        "wrong_per_thousand": round(1000 * (1 - found["right"] / seen), 3),
        "bits_each": round(found["bits"] / seen, 6),
    }


def hands(own: np.ndarray, after: np.ndarray) -> np.ndarray:
    """Changing hands, from transitions in the leader alphabet: for each number of a block's
    eight neighbours that its rival leads, how many blocks with a leader there were, and how
    many had another leader, or none, one coarse generation on. A (9, 2) array."""
    led = own > 0
    rival = np.where(own == 1, 2, 1)
    near = (zoom.ring(own) == rival).sum(axis=0)
    out = np.zeros((9, 2), dtype=np.int64)
    np.add.at(out[:, 0], near[led], 1)
    np.add.at(out[:, 1], near[led & (after != own)], 1)
    return out


def walls(grid: np.ndarray) -> float:
    """The share of neighbouring pairs of blocks, across and down the wrapped grid, whose
    leaders differ."""
    led = LEADER[grid]
    across = led != np.roll(led, -1, axis=-1)
    down = led != np.roll(led, -1, axis=-2)
    return float((across.mean() + down.mean()) / 2)


# --- one world -----------------------------------------------------------------------------------


def excess(rule: zoom.CoarseRule, own_rule: zoom.CoarseRule, tried: list[tuple]) -> dict:
    """The surprise of `rule` on transitions it did not learn from, over that of the rule
    learned where they come from, less one: 0 for a rule that serves as well."""
    out = {}
    for kind in VIEWS:
        theirs = ours = 0.0
        for own, after in tried:
            theirs += score(rule, kind, own, after)["bits"]
            ours += score(own_rule, kind, own, after)["bits"]
        out[kind] = round(theirs / ours - 1, 4) if ours else None
    return out


def analyse(job: tuple[str, int, int, tuple[int, ...]]) -> tuple[str, dict]:
    """Everything measured of one world, from its cached runs."""
    name, side, generations, blocks = job
    runs = {seed: load(name, seed, side, generations) for seed in (*LEARN, *TRY)}
    split = min(SPLIT, generations // 4)
    out: dict = {"side": side, "generations": generations, "blocks": list(blocks),
                 "learn": list(LEARN), "try": list(TRY), "split": split}  # fmt: skip
    shares = np.stack([runs[seed]["shares"] for seed in runs])
    out["shares"] = {"generation": [64 * (i + 1) for i in range(shares.shape[1])],
                     "live": [round(float(v), 4) for v in shares.sum(axis=2).mean(axis=0)],
                     "larger species": [round(float(v), 4)
                                        for v in shares.max(axis=2).mean(axis=0)]}  # fmt: skip
    for alphabet in ALPHABETS:
        q = 3 if alphabet == "leader" else 5
        found: dict = {}
        rules: dict = {}
        for name_of_clock in CLOCKS:
            for block in blocks:
                tick = clock(name_of_clock, block)
                if generations - FROM < 2 * tick:
                    continue

                def of(seed, first=FROM, last=generations, block=block, tick=tick, a=alphabet):
                    return pairs(runs[seed][block], block, tick, first, last, a)

                whole = early = late = zoom.CoarseRule.empty(q)
                for seed in LEARN:
                    whole = tally(whole, *of(seed))
                    early = tally(early, *of(seed, FROM, split))
                    late = tally(late, *of(seed, split, generations))
                rules[(name_of_clock, block)] = whole
                tried = [of(seed) for seed in TRY]
                row: dict = {"clock": tick, "ahead": {}}
                for kind in zoom.KINDS:
                    total = {"transitions": 0, "right": 0, "bits": 0.0}
                    for own, after in tried:
                        total = add(total, score(whole, kind, own, after))
                    row["ahead"][kind] = tidy(total)
                changed = sum(int((own != after).sum()) for own, after in tried)
                row["changed_per_thousand"] = round(
                    1000 * changed / row["ahead"]["nothing"]["transitions"], 3)  # fmt: skip
                tried_late = [of(seed, split, generations) for seed in TRY]
                if all(own.shape[0] >= 2 for own, _ in tried_late):
                    row["early rule late"] = excess(early, late, tried_late)
                if alphabet == "leader":
                    counted = sum(hands(own, after) for own, after in tried)
                    row["hands"] = {"blocks": counted[:, 0].tolist(),
                                    "changed": counted[:, 1].tolist()}  # fmt: skip
                found[f"{name_of_clock} {block}"] = row
        thin = np.random.default_rng([20261125, 5, LEARN[0]])

        def thinned(name_of_clock, below, block, a=alphabet, q=q, thin=thin):
            """The rule of the rung below, learned from as many transitions as this rung's."""
            lower = [pairs(runs[seed][below], below, clock(name_of_clock, below), FROM,
                           generations, a) for seed in LEARN]  # fmt: skip
            upper = sum(pairs(runs[seed][block], block, clock(name_of_clock, block), FROM,
                              generations, a)[0].size for seed in LEARN)  # fmt: skip
            keep = upper / sum(own.size for own, _ in lower)
            rule = zoom.CoarseRule.empty(q)
            for own, after in lower:
                rule = tally(rule, own, after, keep, thin)
            return rule

        # one rule at every rung: the rule from the rung below, tried at this one
        for name_of_clock in CLOCKS:
            for below, block in zip(blocks, blocks[1:], strict=False):
                if (name_of_clock, block) not in rules or (name_of_clock, below) not in rules:
                    continue
                tick = clock(name_of_clock, block)
                tried = [pairs(runs[seed][block], block, tick, FROM, generations, alphabet)
                         for seed in TRY]  # fmt: skip
                lower, here = rules[(name_of_clock, below)], rules[(name_of_clock, block)]
                row = found[f"{name_of_clock} {block}"]
                row["rule from the rung below"] = excess(lower, here, tried)
                row["rule from the rung below, as much data"] = excess(
                    thinned(name_of_clock, below, block), here, tried)  # fmt: skip
        # the same at matched ages, on the square clock
        aged: dict = {}
        for block in blocks:
            first, last = age(block)
            tick = clock("square", block)
            if last > generations or last - first < 2 * tick:
                continue
            rule = quarter = zoom.CoarseRule.empty(q)
            for seed in LEARN:
                learnt = pairs(runs[seed][block], block, tick, first, last, alphabet)
                rule = tally(rule, *learnt)
                quarter = tally(quarter, *learnt, 0.25, thin)  # as much as the rung above has
            tried = [pairs(runs[seed][block], block, tick, first, last, alphabet)
                     for seed in TRY]  # fmt: skip
            seen = sum(own.size for own, _ in tried)
            changed = sum(int((own != after).sum()) for own, after in tried)
            row = {"generations": [first, last], "transitions": seen,
                   "changed_per_thousand": round(1000 * changed / seen, 3)}  # fmt: skip
            if alphabet == "leader":
                counted = sum(hands(own, after) for own, after in tried)
                row["hands"] = {"blocks": counted[:, 0].tolist(),
                                "changed": counted[:, 1].tolist()}  # fmt: skip
            aged[block] = (rule, tried, row, quarter)
        for block, (rule, tried, row, _) in aged.items():
            if block // 2 in aged:
                row["rule from the rung below"] = excess(aged[block // 2][0], rule, tried)
                row["rule from the rung below, as much data"] = excess(
                    aged[block // 2][3], rule, tried)  # fmt: skip
            found[f"square {block}"]["at matched ages"] = row
        # many generations ahead: the rule with neighbour counts, run on by itself
        rng = np.random.default_rng([20261125, 4, LEARN[0]])
        again = np.random.default_rng([20261125, 7, LEARN[0]])
        for name_of_clock in CLOCKS:
            for block in blocks:
                if (name_of_clock, block) not in rules:
                    continue
                rule = rules[(name_of_clock, block)]
                tick = clock(name_of_clock, block)
                steps = (generations - split) // tick
                if steps < 2:
                    continue
                marks = zoom.horizons(steps)
                fine = {h: [] for h in marks}
                run_on = {h: [] for h in marks}
                differ = {h: [] for h in marks}
                frozen = {h: [] for h in marks}
                twins = {h: [] for h in marks}
                at_start = []
                for seed in TRY:
                    frames = runs[seed][block]
                    grid = frames[split // block]
                    if alphabet == "leader":
                        grid = LEADER[grid]
                    first, twin = LEADER[grid], grid
                    at_start.append(walls(grid))
                    for h in range(1, steps + 1):
                        grid = rule.step("total", grid, rng)
                        twin = rule.step("total", twin, again)
                        if h in fine:
                            there = LEADER[frames[(split + h * tick) // block]]
                            fine[h].append(walls(there))
                            run_on[h].append(walls(grid))
                            differ[h].append(float((LEADER[grid] != there).mean()))
                            frozen[h].append(float((first != there).mean()))
                            twins[h].append(float((LEADER[grid] != LEADER[twin]).mean()))

                def mean(kept, marks=marks):
                    return [round(float(np.mean(kept[h])), 5) for h in marks]

                found[f"{name_of_clock} {block}"]["walls"] = {
                    "from generation": split,
                    "at the start": round(float(np.mean(at_start)), 5),
                    "generations on": [h * tick for h in marks],
                    "fine": mean(fine),
                    "run on": mean(run_on),
                }
                # the closure error: blocks whose leader is not the fine world's
                found[f"{name_of_clock} {block}"]["apart"] = {
                    "from generation": split,
                    "generations on": [h * tick for h in marks],
                    "run on": mean(differ),
                    "the start, frozen": mean(frozen),
                    "two runs of the rule": mean(twins),
                }
        out[alphabet] = found
    return name, out


def between(job: tuple[int, int, tuple[int, ...]]) -> dict:
    """One rule for both worlds: at every block and clock, the surprise of each world's rule
    on the other world's unseen starts, over that of the rule learned there, less one."""
    side, generations, blocks = job
    first, second = WORLDS
    runs = {name: {seed: load(name, seed, side, generations) for seed in (*LEARN, *TRY)}
            for name in WORLDS}  # fmt: skip
    out: dict = {}
    for alphabet in ALPHABETS:
        q = 3 if alphabet == "leader" else 5
        found = {}
        for name_of_clock in CLOCKS:
            for block in blocks:
                tick = clock(name_of_clock, block)
                if generations - FROM < 2 * tick:
                    continue
                rules, tried = {}, {}
                for name in WORLDS:
                    rule = zoom.CoarseRule.empty(q)
                    for seed in LEARN:
                        rule = tally(rule, *pairs(runs[name][seed][block], block, tick, FROM,
                                                  generations, alphabet))  # fmt: skip
                    rules[name] = rule
                    tried[name] = [pairs(runs[name][seed][block], block, tick, FROM,
                                         generations, alphabet) for seed in TRY]  # fmt: skip
                found[f"{name_of_clock} {block}"] = {
                    f"the {first} world's rule in the {second} world": excess(
                        rules[first], rules[second], tried[second]),
                    f"the {second} world's rule in the {first} world": excess(
                        rules[second], rules[first], tried[first]),
                }  # fmt: skip
        out[alphabet] = found
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--part", choices=("all", "between"), default="all",
                        help="between: only the two worlds' rules tried on each other")  # fmt: skip
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    fine = [(name, seed, SIDE, GENERATIONS) for seed in (*LEARN, *TRY) for name in WORLDS]
    with ProcessPoolExecutor(args.workers) as pool:
        list(pool.map(run_fine, fine))
        if args.part == "all":
            jobs = [(name, SIDE, GENERATIONS, BLOCKS) for name in WORLDS]
            found = dict(pool.map(analyse, jobs))
        else:
            found = json.loads((OUT / "summary.json").read_text())
    found["between the worlds"] = between((SIDE, GENERATIONS, BLOCKS))
    (OUT / "summary.json").write_text(json.dumps(found, indent=1) + "\n")
    for where, row in found["between the worlds"]["leader"].items():
        print(f"between the worlds, leader, {where}: {row}")
    for name, world in found.items():
        if name not in WORLDS:
            continue
        for alphabet in ALPHABETS:
            for where, row in world[alphabet].items():
                ahead = row["ahead"]
                print(f"{name}, {alphabet}, {where} (clock {row['clock']}): changed "
                      f"{row['changed_per_thousand']} per thousand; bits each: nothing "
                      f"{ahead['nothing']['bits_each']}, own {ahead['own']['bits_each']}, "
                      f"total {ahead['total']['bits_each']}, full {ahead['full']['bits_each']}; "
                      f"early rule late {row.get('early rule late')}; rule from the rung below "
                      f"{row.get('rule from the rung below')}")  # fmt: skip


if __name__ == "__main__":
    main()
