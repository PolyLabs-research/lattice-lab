"""
Is every world on the clock the still world at another block and tick? A look at the worlds
of step 4j. Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-family/look.py still
    uv run --no-sync python examples/scale-up-family/look.py

Step 4j (examples/scale-up-class-memory) read 29 worlds and the still world each on a clock
set by its walls, through blocks of 8, and tried one rule in all of them: the still world's
rule for blocks of 8 at its matched tick of 16 generations. It serves the worlds step 4f's
rule served or nearly served. In the others a block changes hands more often than that rule
would have it. Read after the verdict, two numbers fitted to a world (a pace within the tick,
and a chance of taking a neighbour's leader) brought the rule most of the way, and decision
D15 of docs/scale-up-plan.md asked what those numbers are.

**The family tried here needs no fitted number.** The ladder of steps 4e to 4i already holds
the still world read through other blocks, and the rule was seen to change from rung to rung
in one way: the smaller the block, the more often a block beside a wall changes hands. So
the still world's own rule is taken at every block and tick the kept runs give (`still`):

- blocks of 4, 8, 16 and 32, from the leaders step 4g kept of its eight runs on side 2,048,
  each over the block's matched age, at every tick those leaders allow (a tick is so many
  readings; the matched tick is a quarter of the block's size squared);
- and blocks of 2, which no step had read: the first 64 generations of four of those same
  runs made again, read through blocks of 2 at every generation. These are the only runs
  this look makes: four runs of 64 generations.

Each such reading is a rule. A world's two numbers are then a block and a tick: the reading
of the still world whose rule has least surprise on the starts the world learns from. No
table is fitted and nothing is interpolated.

**What is asked of each of the 30 worlds**, from the leaders step 4j's registered run kept
of it (every block of 8, every two generations, four starts: two to learn from and two to
try on, as registered), over the window step 4j gave it:

1. *At its walls' tick, as step 4j read it:* which reading of the still world is the world
   nearest, and how near: that rule's surprise on the starts the world is tried on, beside
   the world's own rule, as it is and with how long in view.
2. *Does the likeness move with the tick?* The world is read again at half its walls' tick
   and at twice it. If it is the still world at a block and a tick, its nearest reading
   should keep the block and halve or double the tick.
3. *Is it then a rung of the ladder at a tick of its own?* The still world's rungs are its
   readings at their matched ticks: blocks of 2 at 1 generation, 4 at 4, 8 at 16, 16 at 64,
   32 at 256. If a world at its walls' tick is nearest a reading of pace k (a tick of k
   matched ticks), it is read once more at its walls' tick over k, and the rung of the same
   block is tried there. So a world's two numbers are a block and a tick, and nothing else
   is fitted.
4. *Does a noise then add anything?* With a chance e, fitted on the starts the world learns
   from, a block takes the leader of one of its eight neighbours whatever its past.
5. *Run on by itself over the world's window,* which rule ends nearest the world: the look's
   rule of step 4j, the nearest reading's, the rung's at the world's own tick, or the
   world's own?
6. *Could the block and the tick be had without scoring a rule?* Three things read off
   leaders alone (how often blocks change hands in a tick, how often a change is undone at
   the next, how often a lead eight ticks old beside a flat wall changes hands) are set
   beside the same three in every reading of the still world.

The readings of the still world go to still.json and the summary to look/summary.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CLASS = HERE.parent / "scale-up-class-memory"


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold several study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


study = _module("scale_up_class_memory_study", CLASS / "study.py")
extras = _module("scale_up_class_memory_extras", CLASS / "extras.py")
clock, look, ladder = study.clock, study.look, study.ladder
zoom, rung = look.zoom, look.study  # the instrument, and step 4g's study

STILL_READINGS = HERE / "still.json"
OUT = HERE / "look" / "summary.json"
Q = ladder.Q
PLAIN, HOW = study.PLAIN, study.HOW
SEES = study.READINGS  # as it is; with how long in view, up to 8 ticks
AGE = SEES[HOW]  # every tally here is kept by how long, up to 8 ticks
STILL = study.STILL
SIDE = rung.SIDE  # the still world's readings are step 4g's grid, side 2,048
SMALL = 2  # the block no step had read
SMALL_STARTS = (18001, 18002, 18003, 18004)  # four of step 4g's starts of the still world
BLOCKS = (SMALL, *rung.BLOCKS)
FASTEST = 4.0  # a reading's tick is at most this many matched ticks
SLOWEST = 0.25  # a world is read again at no less than this share of its walls' tick
SEEN = 7  # ticks of a block's past that a tally by how long needs before it
LOOKS = (8, 16)  # the reading step 4j tried: blocks of 8 at their matched tick
CHANCES = np.round(np.arange(0.0, 0.801, 0.005), 3)  # the values tried for a noise
PAIRS = 4  # run-ons of a rule from one start: this many pairs, eight runs
DRAWS = 20261128  # the run-ons here name their draws by this
THINGS = ("blocks that change hands in a tick", "changes undone at the next tick",
          "a lead 8 ticks old beside a flat wall changes hands")  # fmt: skip


# --- the still world at every block and tick -----------------------------------------------------


def small(seed: int) -> np.ndarray:
    """The still world on step 4g's grid from one of its starts, for the 64 generations that
    are the matched age of blocks of 2: the leader of every block of 2 at every generation.
    Kept on disk, and read from there if it is."""
    last = 16 * SMALL * SMALL
    path = ladder.CACHE / f"family-still-{SIDE}-{last}-{seed}.npz"
    if path.exists():
        with np.load(path) as kept:
            return kept["leaders"]
    grid = zoom.lattice((STILL, STILL), "standoff", SIDE)
    start = zoom.mixed_start(SIDE, seed, 2, density=1.0)
    grid.occupancy = start.astype(np.int8).copy()
    grid.lifespans[start > 0] = 1
    rng = np.random.default_rng([20261123, 2, int(seed)])  # the standoff draws nothing
    frames = [zoom.leaders(zoom.read(grid.occupancy, SIDE, SMALL, 2))]
    for _ in range(last):
        grid.step(rng)
        frames.append(zoom.leaders(zoom.read(grid.occupancy, SIDE, SMALL, 2)))
    leaders = np.stack(frames)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, leaders=leaders)
    return leaders


def readings(block: int, every: int) -> list[int]:
    """The ticks a block is read at: so many of its kept readings, up to FASTEST matched
    ticks, and leaving at least eight ticks to read inside the block's matched age."""
    matched = block * block / 4
    last = 16 * block * block
    out = []
    for tick in range(every, int(FASTEST * matched) + 1, every):
        if last - max(4 * block * block, SEEN * tick) >= 8 * tick:
            out.append(tick)
    return out


def tally(frames: np.ndarray, every: int, tick: int, first: int, last: int) -> np.ndarray:
    """One run's transitions of `tick` generations, read every `tick` from generation `first`
    while they end by `last`, counted by [how long a block has had its leader, in these
    ticks and up to 8][leader][neighbours species 1 leads][neighbours species 2 leads]
    [leader one tick on]. `frames` holds the run's leaders every `every` generations."""
    at = np.arange(first, last - tick + 1, tick, dtype=np.int64)
    size = AGE.size * Q * 81 * Q
    counts = np.zeros(size, dtype=np.int64)
    for a in range(0, at.size, 8):
        g = at[a : a + 8]
        own = frames[g // every]
        view = zoom.codes("total", own, zoom.ring(own), Q)
        past = AGE.code(frames, every, tick, g)
        after = frames[(g + tick) // every]
        counts += np.bincount(((past * (Q * 81) + view) * Q + after).ravel(), minlength=size)
    return counts.reshape(AGE.size, Q, 9, 9, Q)


def undone(frames: np.ndarray, every: int, tick: int, first: int, last: int) -> np.ndarray:
    """Over the same readings: the blocks with another leader one tick on, and those of them
    that have their old leader again one tick after that."""
    changed = back = 0
    for g in range(first, last - 2 * tick + 1, tick):
        now, after, then = (frames[(g + k * tick) // every] for k in range(3))
        moved = after != now
        changed += int(moved.sum())
        back += int((moved & (then == now)).sum())
    return np.array([changed, back], dtype=np.int64)


def still() -> dict:
    """Every reading of the still world, as {(block, tick): its tally by how long and the
    two counts of `undone`}: blocks of 4 to 32 from step 4g's kept leaders, blocks of 2 from
    the short runs made here. A reading starts at the start of its block's matched age, or
    as soon after as seven ticks of a block's past can be seen."""
    out: dict = {}

    def add(frames: np.ndarray, block: int, every: int) -> None:
        for tick in readings(block, every):
            first = max(4 * block * block, SEEN * tick)
            first += (-first) % every
            last = 16 * block * block
            found = out.setdefault((block, tick), [0, 0])
            found[0] = found[0] + tally(frames, every, tick, first, last)
            found[1] = found[1] + undone(frames, every, tick, first, last)

    plan = rung.design()["still"]
    for seed in plan["learn"] + plan["try"]:
        run = rung.fine("still", seed)
        for block in rung.BLOCKS:
            add(run[block], block, block)
    for seed in SMALL_STARTS:
        add(small(seed), SMALL, 1)
    return out


def write_still() -> None:
    found = still()
    STILL_READINGS.write_text(json.dumps({
        "what": "the still world's own rule at every block and tick its kept runs give "
                "(look.py): for each reading the tally of its transitions over the block's "
                "matched age on side 2,048, counted by [how long a block has had its leader, "
                "up to 8 ticks][leader][neighbours species 1 leads][neighbours species 2 "
                "leads][leader one tick on] as study.sparse writes a tally, and how many "
                "changes of hands were read with the next tick in view and how many of them "
                "were undone at it. Blocks of 4 to 32 are step 4g's eight runs (starts 18001 "
                "to 18008); blocks of 2 are the first 64 generations of four of them made "
                "again",
        "readings": [{"block": block, "tick": tick, "tally": study.sparse(counts),
                      "changes": int(back[0]), "undone": int(back[1])}
                     for (block, tick), (counts, back) in sorted(found.items())],
    }) + "\n")  # fmt: skip


def family() -> dict:
    """The readings of the still world, from still.json."""
    kept = json.loads(STILL_READINGS.read_text())["readings"]
    return {(r["block"], r["tick"]): {"tally": study.dense(r["tally"], AGE.size),
                                      "changes": r["changes"], "undone": r["undone"]}
            for r in kept}  # fmt: skip


def pace(block: int, tick: int) -> float:
    """A reading's tick in matched ticks of its block."""
    return tick / (block * block / 4)


# --- rules, scored one tick ahead ----------------------------------------------------------------


def rule(sees, counts: np.ndarray) -> np.ndarray:
    """The chances a reading's rule gives, from a tally by how long."""
    return sees.chances(sees.of(counts))


def bits(sees, chances: np.ndarray, trial: np.ndarray) -> float:
    """The bits a transition of a tally costs a table of chances, on average, both read as
    `sees` reads (`look.surprise`, for a rule given as its chances)."""
    trial = sees.of(trial)
    seen = trial > 0
    return float(-(trial[seen] * np.log2(chances[seen])).sum() / max(trial.sum(), 1))


def mixed(chances: np.ndarray, e: float) -> np.ndarray:
    """A rule with a noise: with chance e a block takes the leader of one of its eight
    neighbours, whatever its past, and otherwise does as the rule says."""
    return (1 - e) * chances + e * NOISE[None]


NOISE = extras.neighbours()


def beside(sees, chances: np.ndarray, halves: list, trial: np.ndarray) -> dict:
    """A rule on the starts a world is tried on, beside the world's own rule: more surprise
    than the own rule learned from both of the starts it learns from (as step 4j registered
    it), and than the own rule as it would be with endless data (as step 4j's extras)."""
    learned = bits(sees, rule(sees, sum(halves)), trial)
    from_one = float(np.mean([bits(sees, rule(sees, half), trial) for half in halves]))
    mine = bits(sees, chances, trial)
    endless = 2 * learned - from_one
    return {"more surprise": round(mine / learned - 1, 4),
            "beside its own with endless data": round(mine / endless - 1, 4)}  # fmt: skip


# --- things read off leaders alone ---------------------------------------------------------------


def things(counts: np.ndarray, changes: float, back: float) -> dict:
    """Three things that need no rule: the share of blocks with another leader, or none, one
    tick on; the share of such changes undone at the next tick; and the chance that a block
    which has had its leader eight ticks or more, with three of its eight neighbours under
    the rival, changes hands."""
    plain = counts.sum(axis=0)
    same = sum(plain[leader, :, :, leader].sum() for leader in range(Q))
    old = look.hands(counts)[AGE.size - 1, 3]
    return dict(zip(THINGS, (
        float(1 - same / max(plain.sum(), 1)),
        float(back / max(changes, 1)),
        float(old[1] / old[0]) if old[0] >= look.ENOUGH else None), strict=True))  # fmt: skip


def through_nobody(counts: np.ndarray) -> float:
    """Of the changes of hands in a tally, the share that leave a block with no leader or
    take one that had none: the two species level in it, before or after."""
    plain = counts.sum(axis=0)
    changes = plain.sum() - sum(plain[leader, :, :, leader].sum() for leader in range(Q))
    nobody = plain[0].sum() - plain[0, :, :, 0].sum() + plain[1:, :, :, 0].sum()
    return float(nobody / max(changes, 1))


def apart(mine: dict, theirs: dict) -> float | None:
    """How far two sets of the three things are from each other: the root of the mean square
    of the differences of their logarithms."""
    pairs = [(mine[name], theirs[name]) for name in THINGS]
    if any(a is None or b is None or a <= 0 or b <= 0 for a, b in pairs):
        return None
    return float(np.sqrt(np.mean([np.log(a / b) ** 2 for a, b in pairs])))


# --- run on --------------------------------------------------------------------------------------


def run_on(sees, leaders: np.ndarray, chances: np.ndarray, tick: int, first: int, last: int,
           draws: tuple[int, ...]) -> dict:  # fmt: skip
    """A rule, given as its chances, run on by itself from generation `first` of one of step
    4j's runs, a tick at a time to `last`, PAIRS times two runs. At the end: its blocks whose
    leader is not the real world's, the blocks that changed leader meanwhile, and its walls
    and the real world's."""
    steps = (last - first) // tick
    start = leaders[first // clock.EVERY]
    there = leaders[(first + steps * tick) // clock.EVERY]
    code = sees.code(leaders, clock.EVERY, tick, np.array([first], dtype=np.int64))[0]
    amiss, walls = [], []
    for pair in range(PAIRS):
        for twin in (0, 1):
            rng = np.random.default_rng([DRAWS, *draws, twin, pair])
            grid, past = start, code
            for _ in range(steps):
                new = look.step(chances, past, grid, rng)
                past = sees.moved(past, grid, new)
                grid = new
            amiss.append(float((grid != there).mean()))
            walls.append(ladder.walls(grid))
    return {"amiss": float(np.mean(amiss)), "changed": float((start != there).mean()),
            "walls": float(np.mean(walls)), "walls_world": ladder.walls(there)}  # fmt: skip


def ran(sees, runs: dict, chances: np.ndarray, tick: int, window: tuple[int, int],
        which: int) -> dict:  # fmt: skip
    """A rule run on over a world's window, a tick at a time, from each start the world is
    tried on: blocks amiss over blocks changed, and the walls it keeps."""
    found = [run_on(sees, leaders, chances, tick, *window, (seed, tick, which))
             for seed, leaders in runs.items()]  # fmt: skip
    return {
        "amiss over changed": round(float(np.mean([f["amiss"] for f in found])
                                          / np.mean([f["changed"] for f in found])), 4),
        "walls kept": round(float(np.mean([f["walls"] for f in found])
                                  / np.mean([f["walls_world"] for f in found])), 4),
    }  # fmt: skip


# --- one world -----------------------------------------------------------------------------------


def nearest(rules: dict, learn: np.ndarray, blocks=BLOCKS) -> tuple[int, int]:
    """The reading of the still world whose plain rule has least surprise on a tally."""
    return min((key for key in rules if key[0] in blocks),
               key=lambda key: bits(SEES[PLAIN], rules[key][PLAIN], learn))  # fmt: skip


def tick_at(walls_tick: int, factor: float) -> int:
    """So many of a world's walls' ticks, to the nearest reading of its kept leaders."""
    return max(clock.EVERY, clock.EVERY * round(walls_tick * factor / clock.EVERY))


def read_at(runs: dict, plan: dict, tick: int, window: tuple[int, int]) -> dict:
    """A world read at one tick over its window: the tally of each start it learns from, of
    the starts it is tried on together, and of all of them; and what its leaders alone say."""
    first = max(window[0], SEEN * tick)
    first += (-first) % clock.EVERY
    tallies = {seed: tally(leaders, clock.EVERY, tick, first, window[1])
               for seed, leaders in runs.items()}  # fmt: skip
    back = sum(undone(leaders, clock.EVERY, tick, first, window[1]) for leaders in runs.values())
    everything = sum(tallies.values())
    return {"halves": [tallies[seed] for seed in plan["learn"]],
            "trial": sum(tallies[seed] for seed in plan["try"]),
            "things": things(everything, back[0], back[1]),
            "through nobody": through_nobody(everything)}  # fmt: skip


def scored(rules: dict, key: tuple[int, int], at: dict, noise: bool = True) -> dict:
    """One reading of the still world tried in a world read at one tick: its block, tick and
    pace, and its rule beside the world's own, as it is and with how long in view; and the
    same with a noise fitted on the starts the world learns from."""
    learn = sum(at["halves"])
    out: dict = {"block": key[0], "tick": key[1], "pace": round(pace(*key), 3)}
    for reading, sees in SEES.items():
        chances = rules[key][reading]
        out[reading] = beside(sees, chances, at["halves"], at["trial"])
        if noise:
            e = float(min(CHANCES, key=lambda e, c=chances, s=sees: bits(s, mixed(c, e), learn)))
            out[reading]["with a noise"] = {
                "e": e, **beside(sees, mixed(chances, e), at["halves"], at["trial"])}  # fmt: skip
    return out


def read(world_plan: dict, walls_tick: int, runs: dict, rules: dict, seen: dict,
         run_ons: bool = True) -> dict:  # fmt: skip
    """One world of step 4j, from the leaders its registered run kept."""
    window = clock.window(walls_tick)
    here = read_at(runs, world_plan, walls_tick, window)
    learn = sum(here["halves"])
    out: dict = {"walls' tick": walls_tick,
                 **{name: study.number(v, 5) for name, v in here["things"].items()}}  # fmt: skip
    out["changes of hands to or from no leader"] = round(here["through nobody"], 4)
    # 1. at its walls' tick: the look's reading, and the nearest
    near = nearest(rules, learn)
    out["the look's reading"] = scored(rules, LOOKS, here)
    out["the nearest reading"] = scored(rules, near, here)
    out["the nearest of the blocks step 4g read"] = scored(
        rules, nearest(rules, learn, rung.BLOCKS), here, noise=False)  # fmt: skip
    # 2. does the likeness move with the tick?
    for name, factor in (("at half its walls' tick", 0.5), ("at twice its walls' tick", 2.0)):
        tick = tick_at(walls_tick, factor)
        there = read_at(runs, world_plan, tick, window)
        moved = nearest(rules, sum(there["halves"]))
        out[name] = {"read at": tick, **scored(rules, moved, there, noise=False)}
    # 3. is it a rung of the ladder at a tick of its own?
    key = (near[0], near[0] * near[0] // 4)
    own_tick = tick_at(walls_tick, max(1 / pace(*near), SLOWEST))
    at_own = read_at(runs, world_plan, own_tick, window)
    out["the rung at its own tick"] = {"read at": own_tick, **scored(rules, key, at_own)}
    # 6. the reading nearest by what its leaders alone say
    far = {k: apart(here["things"], found) for k, found in seen.items()}
    by_things = min((k for k in far if far[k] is not None), key=lambda k: far[k])
    out["the reading nearest by what its leaders alone say"] = {
        "apart": round(far[by_things], 4),
        **scored(rules, by_things, here, noise=False)}  # fmt: skip
    # 5. run on
    if run_ons:
        tried = {seed: runs[seed] for seed in world_plan["try"]}
        ran_on: dict = {}
        for reading, sees in SEES.items():
            each = {
                "the look's reading": (rules[LOOKS][reading], walls_tick),
                "the nearest reading": (rules[near][reading], walls_tick),
                "its own rule": (rule(sees, learn), walls_tick),
                "the rung, at its own tick": (rules[key][reading], own_tick),
                "its own rule, at its own tick": (
                    rule(sees, sum(at_own["halves"])), own_tick),
            }  # fmt: skip
            for i, (name, (chances, tick)) in enumerate(each.items()):
                ran_on[f"{name}, {reading}"] = ran(sees, tried, chances, tick, window, i)
        out["run on"] = ran_on
    return out


# --- every world ---------------------------------------------------------------------------------


BARS = (0.025, 0.04)  # step 4j's bar for a rule that serves, and a looser one
TRIED = {  # the rules a world is counted against the bars for, by where the look tells them
    "the look's reading, at its walls' tick": ("the look's reading", False),
    "the nearest reading, at its walls' tick": ("the nearest reading", False),
    "the nearest reading with a noise": ("the nearest reading", True),
    "the rung at its own tick": ("the rung at its own tick", False),
    "the rung at its own tick with a noise": ("the rung at its own tick", True),
}


def counted(worlds: dict) -> dict:
    """Over the worlds but the still one, by group: how many each rule tried is within each
    bar of, on the starts they are tried on, as it is and with how long in view."""
    out: dict = {}
    for name, (where, noise) in TRIED.items():
        for reading in SEES:
            for bar in BARS:
                cell = out.setdefault(f"{name}, {reading}", {}).setdefault(f"within {bar:.1%}", {})
                for world, found in worlds.items():
                    if world == STILL:
                        continue
                    told = found[where][reading]
                    more = (told["with a noise"] if noise else told)["more surprise"]
                    group = cell.setdefault(found["group"], [0, 0])
                    group[0] += int(more <= bar)
                    group[1] += 1
    return out


def moved(worlds: dict) -> dict:
    """Does a world's nearest reading move with the tick it is read at? Over all the worlds,
    by group: how many keep the block of their nearest reading when read at half their
    walls' tick and at twice it, and how many of those take a shorter tick at half and a
    longer one at twice."""
    out: dict = {}
    for name, shorter in (("at half its walls' tick", True), ("at twice its walls' tick", False)):
        for found in worlds.values():
            near, there = found["the nearest reading"], found[name]
            cell = out.setdefault(name, {}).setdefault(found["group"], [0, 0, 0])
            kept = near["block"] == there["block"]
            right = there["tick"] < near["tick"] if shorter else there["tick"] > near["tick"]
            cell[0] += int(kept)
            cell[1] += int(kept and right)
            cell[2] += 1
    return out


def placed(worlds: dict) -> dict:
    """How often three things read off leaders alone find a world's nearest reading: over
    the worlds but the still one, by group, how many get the same reading, the same block,
    and how many there are."""
    out: dict = {}
    for world, found in worlds.items():
        if world == STILL:
            continue
        near = found["the nearest reading"]
        by = found["the reading nearest by what its leaders alone say"]
        cell = out.setdefault(found["group"], [0, 0, 0])
        cell[0] += int((near["block"], near["tick"]) == (by["block"], by["tick"]))
        cell[1] += int(near["block"] == by["block"])
        cell[2] += 1
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("step", nargs="?", choices=["still"],
                        help="read the still world at every block and tick, and stop")  # fmt: skip
    parser.add_argument("--worlds", nargs="*", help="only these worlds, and nothing written")
    parser.add_argument("--fast", action="store_true", help="no run-ons")
    args = parser.parse_args()
    if args.step == "still":
        write_still()
        return
    kin = family()
    rules = {key: {reading: rule(sees, found["tally"]) for reading, sees in SEES.items()}
             for key, found in kin.items()}  # fmt: skip
    seen = {key: things(found["tally"], found["changes"], found["undone"])
            for key, found in kin.items()}  # fmt: skip
    rows = [json.loads(line) for line in study.RECORDS.read_text().splitlines()]
    plan, chosen = study.design(), study.worlds()
    worlds: dict = {}
    for world in plan:
        if args.worlds and world not in args.worlds:
            continue
        walls_tick = study.tick_of(rows, plan, world)
        runs = {seed: clock.fine(world, seed)["leaders"]
                for seed in plan[world]["learn"] + plan[world]["try"]}  # fmt: skip
        found = read(plan[world], walls_tick, runs, rules, seen, not args.fast)
        worlds[world] = {"group": chosen[world]["group"], **found}
        print(world, json.dumps(worlds[world]), flush=True)
    if args.worlds:
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "what": "the worlds of step 4j beside the still world at every block and tick "
                "(look.py, exploratory): for each world the reading of the still world whose "
                "rule is nearest it at its walls' tick, at half that and at twice it; the "
                "rung of that block at the world's own tick (its walls' tick over the nearest "
                "reading's pace); whether a noise adds to either; the rules run on; and the "
                "reading nearest by three things read off "
                "leaders alone. `more surprise` is on the starts a world is tried on, beside "
                "the world's own rule at the same tick",
        "the still world's readings": {
            f"{block} at {tick}": {"pace": round(pace(block, tick), 3),
                                   "transitions": int(kin[block, tick]["tally"].sum()),
                                   **{name: study.number(v, 5) for name, v in found.items()},
                                   "changes of hands to or from no leader": round(
                                       through_nobody(kin[block, tick]["tally"]), 4)}
            for (block, tick), found in sorted(seen.items())},
        "worlds within a bar, by group as [within, of]": counted(worlds),
        "does the nearest reading move with the tick, by group as [block kept, and the tick "
        "the right way, of]": moved(worlds),
        "placed by its leaders alone, by group as [same reading, same block, of]": placed(worlds),
        "worlds": worlds,
    }, indent=1) + "\n")  # fmt: skip


if __name__ == "__main__":
    main()
