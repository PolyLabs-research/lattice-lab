"""
Pictures for the first look at worlds of territories, zoomed out. Exploratory.

    uv run --no-sync python examples/scale-up-closure-territories/pictures.py [--out DIR]

The look's numbers say a coarse rule, run on by itself, keeps about as many walls as the world
it was learned from. These pictures are the check a number cannot make: whether its world
looks like that world.

For each of the two worlds, through blocks of 4, 8 and 16 on the square clock, a block to a
square coloured by who leads it:

    the world at generation 1,024
    the same world at generation 4,096
    the coarse rule's own world at generation 4,096: run on from the first picture by drawing
    from its table of neighbour counts, with no fine cells under it

The start (15005) is one the rule did not learn from. Nothing obliges the third picture to
agree with the second block for block: the coarse rule draws its own chances. At the least
they should be the same kind of picture, with territories as large and walls as smooth. Where
they are also the same picture, the coarse rule has foretold where the territories would be,
and the captions say in how many blocks it has not.

The fine runs are read from look.py's cache, so look.py has to have been run. The page goes to
`index.html` in `~/lattice-lab-runs/closure-territories/pictures` unless told otherwise, and
needs nothing but a browser. Nothing is written into the repository.
"""

from __future__ import annotations

import argparse
import base64
import html
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold more than one
    look.py and more than one pictures.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


look = _module("scale_up_closure_territories_look", HERE / "look.py")
# the search's pictures, for their colours and their image writer
drawn = _module("scale_up_search_pictures", HERE.parent / "scale-up-search" / "pictures.py")
zoom = look.zoom

OUT = Path.home() / "lattice-lab-runs" / "closure-territories" / "pictures"
SEED = look.TRY[0]
BLOCKS = (4, 8, 16)
WIDTH = 512  # the side of every picture on the page, in pixels
NOTES = {
    "still": "Two grounds that fill in and stop: nothing moves but the walls between them.",
    "busy": "Two grounds that stay busy inside, their shares of the grid level.",
}


def ahead(
    name: str,
    seed: int,
    block: int,
    side: int = look.SIDE,
    generations: int = look.GENERATIONS,
) -> dict:
    """One world through blocks of `block` on the square clock, by who leads each block: at
    the generation the coarse rule is started from, at the last generation its clock reaches,
    and in the coarse rule's own world at that generation. The rule is the one with neighbour
    counts, learned from look.LEARN; `seed` should be a start it did not learn from."""
    tick = look.clock("square", block)
    split = min(look.SPLIT, generations // 4)
    rule = zoom.CoarseRule.empty(3)
    for learnt in look.LEARN:
        frames = look.load(name, learnt, side, generations)[block]
        learnt_from = look.pairs(frames, block, tick, look.FROM, generations, "leader")
        rule = look.tally(rule, *learnt_from)
    frames = look.load(name, seed, side, generations)[block]
    steps = (generations - split) // tick
    rng = np.random.default_rng([20261125, 6, int(seed), block])
    start = look.LEADER[frames[split // block]]
    grid = start
    for _ in range(steps):
        grid = rule.step("total", grid, rng)
    last = split + steps * tick
    fine = look.LEADER[frames[last // block]]
    return {"from": split, "to": last, "coarse generations": steps, "start": start,
            "fine": fine, "run on": grid,
            "walls": {"start": look.walls(start), "fine": look.walls(fine),
                      "run on": look.walls(grid)},
            "apart": {"start": float((start != fine).mean()),
                      "run on": float((grid != fine).mean())}}  # fmt: skip


def page(shown: list[tuple[str, int, dict]], seed: int = SEED, width: int = WIDTH) -> str:
    """The page, from (world, block, what `ahead` gave) for every row of pictures."""
    parts, last = [], None
    for name, block, found in shown:
        if name != last:
            rule = look.WORLDS[name]["rules"][0]
            key = " ".join(
                f'<span class="key" style="background: rgb{drawn.COLOURS[s]}"></span>'
                f"blocks species {s} leads"
                for s in (1, 2)
            )
            parts.append(
                f"<h2>{html.escape(rule)} against a copy of itself (the {name} world)</h2>"
                f"<p>{html.escape(NOTES.get(name, ''))}</p><p class='how'>{key}</p>"
            )
            last = name
        walls, apart = found["walls"], found["apart"]
        told = {
            "start": f"{apart['start']:.1%} of its blocks have another leader by generation "
            f"{found['to']:,}",
            "fine": "",
            "run on": f"{apart['run on']:.1%} of its blocks have another leader than the world's",
        }
        frames = "".join(
            f'<figure><img alt="{html.escape(name)} world, blocks of {block}, {html.escape(what)}"'
            f' width="{width}" height="{width}" src="data:image/png;base64,'
            f'{base64.b64encode(drawn.frame(found[which])).decode()}"><figcaption>'
            f"{html.escape(what)}<br>walls: {walls[which]:.3f} of neighbouring pairs"
            f"{'<br>' * bool(told[which])}{html.escape(told[which])}</figcaption></figure>"
            for which, what in (
                ("start", f"the world at generation {found['from']:,}"),
                ("fine", f"the world at generation {found['to']:,}"),
                ("run on", f"the coarse rule's own world at generation {found['to']:,}"),
            )
        )
        tick = look.clock("square", block)
        parts.append(
            f"<h3>Through blocks of {block}: one coarse generation is {tick} fine ones, and the "
            f"coarse rule runs for {found['coarse generations']:,}</h3>"
            f'<div class="frames">{frames}</div>'
        )
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Worlds of territories, zoomed out: the world and its coarse rule</title><style>"
        ":root{color-scheme:dark}"
        "body{background:#1a1a19;color:#f0efec;font:16px/1.5 system-ui,sans-serif;"
        "margin:2rem auto;max-width:1620px;padding:0 1rem}h1{font-size:1.5rem}"
        "h2{font-size:1.15rem;margin:2.2rem 0 .2rem}h3{font-size:1rem;font-weight:600;"
        "margin:1.2rem 0 0}p{margin:.2rem 0;max-width:80ch}"
        ".how{color:#c3c2b7;font-size:.9rem;max-width:none}.frames{display:flex;flex-wrap:wrap;"
        "gap:12px;margin-top:.5rem}figure{margin:0}img{display:block;image-rendering:pixelated;"
        "border:1px solid #383835}figcaption{color:#c3c2b7;font-size:.85rem;margin-top:.2rem}"
        ".key{display:inline-block;width:.8em;height:.8em;margin:0 .35em 0 .9em;"
        "vertical-align:baseline}.key:first-child{margin-left:0}"
        "</style><h1>Worlds of territories, zoomed out: the world and its coarse rule</h1>"
        f"<p>Each picture is a {look.SIDE:,} &times; {look.SIDE:,} grid that wraps round, read "
        f"through blocks: one square is one block, coloured by the species with more cells in "
        f"it. In every row the first two pictures are the world itself, from start {seed}. The "
        f"third is the coarse rule's own world: started from the first picture and run on by "
        f"drawing each block's next leader from a table of what blocks with as many "
        f"neighbours under each leader did, in four other runs. Nothing obliges it to match "
        f"the second picture block for block, since it draws its own chances: at the least it "
        f"should be the same kind of picture. Under the pictures is how far it does match: in "
        f"how many blocks the leader is not the one the world has at the last generation, for "
        f"the coarse rule's world and for the first picture, had nothing moved.</p>"
        f"{''.join(parts)}</html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    shown = [(name, block, ahead(name, SEED, block)) for name in look.WORLDS for block in BLOCKS]
    for name, block, found in shown:
        walls = {which: round(share, 4) for which, share in found["walls"].items()}
        apart = {which: round(share, 4) for which, share in found["apart"].items()}
        print(f"{name}, blocks of {block}: generation {found['from']} to {found['to']}, "
              f"walls {walls}, apart from the world {apart}")  # fmt: skip
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(page(shown))
    print(args.out / "index.html")


if __name__ == "__main__":
    main()
