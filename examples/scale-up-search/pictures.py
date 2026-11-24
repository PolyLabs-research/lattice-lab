"""
Pictures of the worlds the search sorts, to see what its numbers mean. Exploratory.

    uv run --no-sync python examples/scale-up-search/pictures.py [--out DIR]

Each world is run once on a 256 x 256 grid from start 13001 and drawn at generations 16,
128, 1,024 and 4,096, a cell to a pixel: empty cells dark, each species its own colour. The
frames go into one page, `index.html` in `~/lattice-lab-runs/search/pictures` unless told
otherwise, which needs nothing but a browser. Nothing is written into the repository.
"""

from __future__ import annotations

import argparse
import base64
import html
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import organised  # noqa: E402

SIDE, SEED, TIMES = 256, 13001, (16, 128, 1024, 4096)
OUT = Path.home() / "lattice-lab-runs" / "search" / "pictures"
# The page's surface for an empty cell, then species 1 to 3: a blue, an orange and a green
# checked to stay apart, every pair of them, on this surface and for the common kinds of
# colour-blindness. A fourth colour would not pass that check, so no world of more than three
# species is drawn.
COLOURS = ((26, 26, 25), (57, 135, 229), (217, 89, 38), (25, 158, 112))
# title, rules, tie-break, share of cells live at the start, what to look for
WORLDS: list[tuple[str, tuple[str, ...], str, float, str]] = [
    ("Life against HighLife", ("B3/S23", "B36/S23"), "standoff", 0.5,
     "The world of steps 2 to 4: patches a few cells across, at every age."),
    ("Vote, alone", ("B5678/S45678",), "standoff", 0.5,
     "Domains form in a few generations and then stop for good."),
    ("Anneal, alone", ("B4678/S35678",), "standoff", 0.5,
     "Domains that keep growing: the walls between them straighten and small domains go, "
     "until the grid runs out."),
    ("Anneal against a copy of itself", ("B4678/S35678",) * 2, "standoff", 1.0,
     "Each species needs a majority of its own kind around a cell, and its rival is in the "
     "way: both die."),
    ("B2378/S25678, alone", ("B2378/S25678",), "standoff", 0.5,
     "A rule from the even draw (number 1107). Alone, its dense ground takes the whole grid "
     "within about a thousand generations, and that is the end of it."),
    ("B2378/S25678 against a copy of itself", ("B2378/S25678",) * 2, "standoff", 1.0,
     "Two species with that one rule. Neither can take the grid: they sort into territories, "
     "each fills in its own, and the territories go on growing."),
    ("B2378/S25678, three copies", ("B2378/S25678",) * 3, "standoff", 1.0,
     "Three species with the one rule share the grid out the same way."),
    ("B015/S1 against a copy of itself, ties left empty", ("B015/S1",) * 2, "standoff", 1.0,
     "Under the standoff the two species sort themselves into territories that stay busy "
     "inside and grow slowly."),
    ("B015/S1 against a copy of itself, ties drawn", ("B015/S1",) * 2, "random", 1.0,
     "The same world with every tie settled by a draw: the species stay mixed."),
]  # fmt: skip


def png(pixels: np.ndarray) -> bytes:
    """An image file from a height x width x 3 array of bytes."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    height, width, _ = pixels.shape
    rows = b"".join(b"\x00" + pixels[y].tobytes() for y in range(height))
    head = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) + chunk(b"IDAT", zlib.compress(rows, 9))
            + chunk(b"IEND", b""))  # fmt: skip


def frame(grid: np.ndarray) -> bytes:
    """One grid of 0 for empty and species' numbers, as an image."""
    return png(np.asarray(COLOURS, dtype=np.uint8)[grid])


def page(worlds: list[tuple], side: int = SIDE, seed: int = SEED, times=TIMES) -> str:
    parts = []
    for title, rules, kind, density, note in worlds:
        if len(rules) >= len(COLOURS):
            raise ValueError(f"{title}: no more than {len(COLOURS) - 1} species can be drawn")
        shots = organised.snapshots(rules, kind, side, seed, times, density)
        frames = "".join(
            f'<figure><img alt="{html.escape(title)}, generation {t}" width="{side}" '
            f'height="{side}" src="data:image/png;base64,'
            f'{base64.b64encode(frame(shots[t])).decode()}"><figcaption>generation {t:,}'
            f"</figcaption></figure>"
            for t in times
        )
        several = len(rules) > 1
        key = " ".join(
            f'<span class="key" style="background: rgb{COLOURS[i + 1]}"></span>'
            f"{f'species {i + 1}, ' * several}{html.escape(rule)}"
            for i, rule in enumerate(rules)
        )
        start = "every cell live" if density == 1 else f"{density:.0%} of cells live"
        tie = f", ties by the {'random draw' if kind == 'random' else kind}" * (len(rules) > 1)
        parts.append(
            f"<section><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p>"
            f'<p class="how">{key} &nbsp; start: {start}{tie}</p>'
            f'<div class="frames">{frames}</div></section>'
        )
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Worlds that organise themselves, and worlds that do not</title><style>"
        ":root{color-scheme:dark}"
        "body{background:#1a1a19;color:#f0efec;font:16px/1.5 system-ui,sans-serif;"
        "margin:2rem auto;max-width:1120px;padding:0 1rem}h1{font-size:1.5rem}"
        "h2{font-size:1.15rem;margin:2rem 0 .2rem}p{margin:.2rem 0;max-width:70ch}"
        ".how{color:#c3c2b7;font-size:.9rem;max-width:none}.frames{display:flex;flex-wrap:wrap;"
        "gap:12px;margin-top:.6rem}figure{margin:0}img{display:block;image-rendering:pixelated;"
        "border:1px solid #383835}figcaption{color:#c3c2b7;font-size:.85rem;margin-top:.2rem}"
        ".key{display:inline-block;width:.8em;height:.8em;margin:0 .35em 0 .9em;"
        "vertical-align:baseline}"
        "</style><h1>Worlds that organise themselves, and worlds that do not</h1>"
        f"<p>Each world on a {side} &times; {side} grid that wraps round, a cell to a pixel, "
        f"from one mixed start. Empty cells are dark.</p>{''.join(parts)}</html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--side", type=int, default=SIDE)
    parser.add_argument("--times", type=int, nargs="+", default=list(TIMES))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(page(WORLDS, args.side, SEED, tuple(args.times)))
    print(args.out / "index.html")


if __name__ == "__main__":
    main()
