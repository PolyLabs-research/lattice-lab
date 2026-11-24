"""
The worlds with territories, followed eight times longer. Exploratory: nothing here is
registered.

    uv run --no-sync python examples/scale-up-search/long.py [--workers 2]

confirm.py stops at generation 2,048. In the contests that hold territories there, two things
are still going on at once: the territories grow, and inside its own territory each species
goes on filling in the ground it holds (as the same rule does over the whole grid when it is
alone). The correlation area counts both, so 2,048 generations cannot say what is left once
the filling-in is over: territories that keep growing, or a map that has set.

So the same worlds are run here to generation 16,384, on a grid of side 512 so that a run
costs twice a confirm run and not eight times, from start 12001, read at generations 128 to
16,384 through blocks of 4 to 64.

**Which worlds** (`picks`): Anneal, whose domains are known to grow until the grid is used
up, as the anchor; and of confirm's contests, pairs and copies, those whose first start showed
territories of 16 cells or more at generation 2,048: the four with the largest, and the world
of five copies.

They are read as confirm.py reads a world. On this grid a block of 64 is an eighth of the
side, so an area near 64 x 64 = 4,096 means the grid is running out, not the world.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import confirm  # noqa: E402
import organised  # noqa: E402
import search  # noqa: E402

OUT = HERE / "long"
SIDE, SEED = 512, confirm.STARTS[0]
TIMES = (128, 256, 512, 1024, 2048, 4096, 8192, 16384)
BLOCKS = (4, 8, 16, 32, 64)
MOST = 4


def picks(found: list[dict]) -> list[dict]:
    """The worlds to follow. `found` is confirm's worlds as its summary describes them."""

    def territory(f: dict) -> float:
        return max((t["area"][-1] or 0.0 for t in f["territories"]), default=0.0)

    def world(f: dict) -> dict:
        return {k: f[k] for k in ("family", "index", "name", "rules", "tie_break", "density")}

    out = [world(f) for f in found if f["family"] == "known" and f["name"] == "Anneal"]
    held = [f for f in found if f["family"] in ("contest", "pair", "copies")
            and territory(f) >= search.LARGE]  # fmt: skip
    two = sorted((f for f in held if f["family"] != "copies"), key=lambda f: -territory(f))
    out += [world(f) for f in two[:MOST]]
    out += [world(f) for f in held if f["family"] == "copies"]
    return out


def run(world: dict) -> dict:
    found = organised.profile(
        world["rules"], world["tie_break"], SIDE, SEED, TIMES, BLOCKS, world["density"]
    )
    return {**world, "why": "followed for longer", "side": SIDE, "seed": SEED, **found}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    picked = OUT / "picks.json"
    if not picked.exists():  # picked once, from the first start of each of confirm's worlds
        first = {confirm.key(r): r
                 for r in map(json.loads, (confirm.OUT / "records.jsonl").read_text().splitlines())
                 if r["seed"] == SEED}  # fmt: skip
        candidates = json.loads((confirm.OUT / "candidates.json").read_text())
        found = [confirm.describe([first[confirm.key(w)]]) for w in candidates
                 if confirm.key(w) in first]  # fmt: skip
        picked.write_text(json.dumps(picks(found), indent=1) + "\n")
    worlds = json.loads(picked.read_text())
    path = OUT / "records.jsonl"
    done = set()
    if path.exists():
        done = {confirm.key(json.loads(line)) for line in path.read_text().splitlines()}
    todo = [w for w in worlds if confirm.key(w) not in done]
    with ProcessPoolExecutor(args.workers) as pool, path.open("a") as sink:
        for record in pool.map(run, todo):
            sink.write(json.dumps(record) + "\n")
            sink.flush()
    by_world = {confirm.key(r): r for r in map(json.loads, path.read_text().splitlines())}
    found = [confirm.describe([by_world[confirm.key(w)]]) for w in worlds]
    summary = {"side": SIDE, "times": list(TIMES), "blocks": list(BLOCKS), "start": SEED,
               "worlds": found}  # fmt: skip
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    for f in found:
        print(f"{f['called']}: {f['name']} ({f['tie_break']}): {f['field']}, live {f['live']}, "
              f"area {f['area']}, growth late {f.get('growth_late')}")  # fmt: skip
        for t in f["territories"]:
            print(f"    {t['field']}: {t['called']}, share {t['share']}, area {t.get('area')}, "
                  f"growth late {t.get('growth_late')}")  # fmt: skip


if __name__ == "__main__":
    main()
