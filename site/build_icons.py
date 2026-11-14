"""
Draw the site's mark as the picture files a page's head names, for the places an SVG does not reach.

    uv run --with pillow python site/build_icons.py

Writes public/favicon.ico (16, 32 and 48 pixels), public/apple-touch-icon.png (180) and
public/assets/mark-512.png, the logo the home page's structured data gives. The mark is the one in
public/assets/mark.svg and build_pages.py: a 3 x 3 grid of cells with a gold centre. Run it again
only if the mark changes.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "public"
CELL, SOFT, GOLD, PAPER = "#155f78", "#b9d3dc", "#a1660d", "#f2f4f1"
GRID = [[CELL, SOFT, CELL], [SOFT, GOLD, SOFT], [CELL, SOFT, CELL]]


def mark(size: int, background: str | None, margin: float) -> Image.Image:
    """The mark at `size` pixels, drawn four times larger and reduced so its edges are smooth."""
    big = size * 4
    image = Image.new("RGBA", (big, big), background or (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    unit = big * (1 - 2 * margin) / 26  # the SVG's viewBox is 26 units across
    for row, colours in enumerate(GRID):
        for col, colour in enumerate(colours):
            x = big * margin + (1 + 8.5 * col) * unit
            y = big * margin + (1 + 8.5 * row) * unit
            draw.rounded_rectangle([x, y, x + 7 * unit, y + 7 * unit], radius=unit, fill=colour)
    return image.resize((size, size), Image.LANCZOS)


def main() -> None:
    mark(48, None, 0).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    mark(180, PAPER, 0.16).convert("RGB").save(OUT / "apple-touch-icon.png", optimize=True)
    mark(512, PAPER, 0.16).convert("RGB").save(OUT / "assets" / "mark-512.png", optimize=True)
    print("wrote favicon.ico, apple-touch-icon.png and assets/mark-512.png")


if __name__ == "__main__":
    main()
