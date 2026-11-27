"""
A picture for the look at a coarse rule that remembers. Exploratory.

    uv run --no-sync python examples/scale-up-memory/pictures.py [--out DIR]

One page of small charts, drawn from look/summary.json (so look.py has to have been run): for
each of the two worlds, and for blocks with three, four and five of their eight neighbours
under the rival, the chance that a block has another leader one tick on, against how long it
has had its leader, with one line for each rung. Where the four lines lie on one another the
table is the same at every rung once a block's past is in view; where they stand apart it is
not. The chances run over three tenfolds, so they are drawn on a scale of tenfolds.

The page goes to `index.html` in `~/lattice-lab-runs/memory/pictures` unless told otherwise,
and needs nothing but a browser. Nothing is written into the repository.
"""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / "look" / "summary.json"
OUT = Path.home() / "lattice-lab-runs" / "memory" / "pictures"

BLOCKS = ("4", "8", "16", "32")
NEAR = (3, 4, 5)  # rival neighbours, one chart each
SPANS = ("1", "2", "3 or 4", "5 to 8", "9 to 15", "16 and more")
SHORT = ("1", "2", "3–4", "5–8", "9–15", "16+")
WORLDS = {"still": "The still world", "busy": "The busy world"}
LOW, HIGH = 0.0002, 1.0  # the chances drawn, on a scale of tenfolds
TICKS = (0.001, 0.01, 0.1, 1.0)
WIDTH, HEIGHT = 330, 264
LEFT, RIGHT, TOP, BOTTOM = 46, 34, 26, 40

# one hue, a step for each rung: checked as an ordinal ramp against each surface
STYLE = """
.viz-root{color-scheme:light;--surface-1:#fcfcfb;--page:#f9f9f7;--text-primary:#0b0b0b;
--text-secondary:#52514e;--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;
--border:rgba(11,11,11,0.10);--s1:#86b6ef;--s2:#3987e5;--s3:#1c5cab;--s4:#0d366b}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{
color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;--text-primary:#f0efec;
--text-secondary:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
--border:rgba(255,255,255,0.10);--s1:#184f95;--s2:#2a78d6;--s3:#6da7ec;--s4:#b7d3f6}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;
--text-primary:#f0efec;--text-secondary:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
--border:rgba(255,255,255,0.10);--s1:#184f95;--s2:#2a78d6;--s3:#6da7ec;--s4:#b7d3f6}
body{margin:0;background:var(--page);color:var(--text-primary);
font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:1.5rem 1rem 3rem}
h1{font-size:1.4rem;margin:0 0 .4rem}h2{font-size:1.05rem;margin:1.6rem 0 .3rem}
p{max-width:46rem;color:var(--text-secondary);margin:.4rem 0}
.legend{display:flex;flex-wrap:wrap;gap:.3rem 1.2rem;margin:1rem 0 .2rem;
color:var(--text-secondary);font-size:.9rem}
.legend span{display:inline-flex;align-items:center;gap:.4rem}
.key{display:inline-block;width:18px;height:0;border-top:2px solid}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:.8rem}
figure{margin:0;background:var(--surface-1);border:1px solid var(--border);border-radius:8px;
padding:.6rem .6rem .3rem;position:relative}
figcaption{font-size:.9rem;color:var(--text-secondary);margin:0 0 .2rem .2rem}
svg{display:block;width:100%;height:auto;outline:none}
svg:focus-visible{outline:2px solid var(--s2);outline-offset:2px;border-radius:4px}
.grid{stroke:var(--grid);stroke-width:1}.axis{stroke:var(--axis);stroke-width:1}
.tick{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.name{fill:var(--text-secondary);font-size:11px}
.line{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.dot{stroke:var(--surface-1);stroke-width:2}
.cross{stroke:var(--axis);stroke-width:1;visibility:hidden}
.tip{position:absolute;pointer-events:none;background:var(--surface-1);
border:1px solid var(--border);border-radius:6px;padding:.4rem .6rem;font-size:.85rem;
box-shadow:0 2px 8px rgba(0,0,0,.12);visibility:hidden;white-space:nowrap;z-index:2}
.tip .head{color:var(--text-secondary);margin-bottom:.2rem}
.tip .line-row{display:flex;align-items:center;gap:.45rem}
.tip b{font-weight:600;font-variant-numeric:tabular-nums;min-width:3.6em}
.tip i{font-style:normal;color:var(--text-secondary)}
details{margin-top:1.4rem}summary{cursor:pointer;color:var(--text-secondary)}
table{border-collapse:collapse;margin-top:.6rem;font-size:.9rem}
th,td{padding:.2rem .7rem;text-align:right;font-variant-numeric:tabular-nums;
border-bottom:1px solid var(--grid)}th:first-child,td:first-child,th:nth-child(2),
td:nth-child(2){text-align:left}th{color:var(--text-secondary);font-weight:500}
.foot{font-size:.85rem;margin-top:1.2rem}
"""

SCRIPT = """
const DATA = JSON.parse(document.getElementById('data').textContent);
const fmt = v => v == null ? 'too few blocks' : (v < 0.01 ? v.toFixed(4) : v.toFixed(3));
for (const fig of document.querySelectorAll('figure[data-chart]')) {
  const panel = DATA.panels[+fig.dataset.chart];
  const svg = fig.querySelector('svg'), cross = fig.querySelector('.cross');
  const tip = fig.querySelector('.tip');
  let at = panel.xs.length - 1;
  const show = (i, px, py) => {
    at = i;
    cross.setAttribute('x1', panel.xs[i]); cross.setAttribute('x2', panel.xs[i]);
    cross.style.visibility = 'visible';
    tip.replaceChildren();
    const head = document.createElement('div'); head.className = 'head';
    head.textContent = 'has had its leader for ' + DATA.spans[i] + (i ? ' ticks' : ' tick');
    tip.append(head);
    panel.series.forEach((values, s) => {
      const row = document.createElement('div'); row.className = 'line-row';
      const key = document.createElement('span'); key.className = 'key';
      key.style.borderTopColor = 'var(--s' + (s + 1) + ')';
      const value = document.createElement('b'); value.textContent = fmt(values[i]);
      const name = document.createElement('i'); name.textContent = 'blocks of ' + DATA.blocks[s];
      row.append(key, value, name); tip.append(row);
    });
    tip.style.visibility = 'visible';
    const box = fig.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    let left = px + 14, top = py - h - 10;
    if (left + w > box.width - 4) left = px - w - 14;
    if (top < 4) top = py + 14;
    tip.style.left = Math.max(4, left) + 'px'; tip.style.top = top + 'px';
  };
  const hide = () => { cross.style.visibility = 'hidden'; tip.style.visibility = 'hidden'; };
  const nearest = event => {
    const box = svg.getBoundingClientRect();
    const x = (event.clientX - box.left) * DATA.width / box.width;
    let best = 0;
    panel.xs.forEach((px, i) => { if (Math.abs(px - x) < Math.abs(panel.xs[best] - x)) best = i; });
    const fb = fig.getBoundingClientRect();
    show(best, event.clientX - fb.left, event.clientY - fb.top);
  };
  svg.addEventListener('pointermove', nearest);
  svg.addEventListener('pointerleave', hide);
  const place = () => {
    const box = svg.getBoundingClientRect(), fb = fig.getBoundingClientRect();
    show(at, panel.xs[at] * box.width / DATA.width + box.left - fb.left, box.top - fb.top + 60);
  };
  svg.addEventListener('focus', place);
  svg.addEventListener('blur', hide);
  svg.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      at = Math.max(0, Math.min(panel.xs.length - 1, at + (event.key === 'ArrowLeft' ? -1 : 1)));
      place(); event.preventDefault();
    }
  });
}
"""


def chances(summary: dict, world: str, near: int) -> list[list[float | None]]:
    """For one world and one number of rival neighbours: for each rung, the chance of
    changing hands by how long the block has had its leader (None where too few blocks)."""
    found = summary["worlds"][world]["changing hands, by a block's past"]
    return [[found[block]["chance"][f"has had its leader for {span} ticks"][near]
             for span in SPANS] for block in BLOCKS]  # fmt: skip


def x_at(i: int) -> float:
    return LEFT + (WIDTH - LEFT - RIGHT) * i / (len(SPANS) - 1)


def y_at(chance: float) -> float:
    share = (math.log10(max(chance, LOW)) - math.log10(LOW)) / (math.log10(HIGH) - math.log10(LOW))
    return HEIGHT - BOTTOM - (HEIGHT - TOP - BOTTOM) * share


def panel(series: list[list[float | None]], title: str, index: int) -> str:
    """One chart: a line for each rung over how long a block has had its leader."""
    parts = [f'<line class="grid" x1="{LEFT}" x2="{WIDTH - RIGHT}" y1="{y_at(t):.1f}" '
             f'y2="{y_at(t):.1f}"/><text class="tick" x="{LEFT - 6}" y="{y_at(t) + 4:.1f}" '
             f'text-anchor="end">{t:g}</text>' for t in TICKS]  # fmt: skip
    base = HEIGHT - BOTTOM
    parts.append(f'<line class="axis" x1="{LEFT}" x2="{WIDTH - RIGHT}" y1="{base}" y2="{base}"/>')
    parts += [f'<text class="tick" x="{x_at(i):.1f}" y="{base + 15}" text-anchor="middle">'
              f"{html.escape(label)}</text>" for i, label in enumerate(SHORT)]  # fmt: skip
    parts.append(f'<text class="name" x="{(LEFT + WIDTH - RIGHT) / 2:.1f}" y="{HEIGHT - 6}" '
                 'text-anchor="middle">ticks the block has had its leader</text>')  # fmt: skip
    parts.append('<text class="name" x="4" y="11">chance of another leader one tick on</text>')
    parts.append(f'<line class="cross" x1="0" x2="0" y1="{TOP}" y2="{base}"/>')
    ends = []
    for s, values in enumerate(series, start=1):
        points, run = [], []
        for i, value in enumerate(values):
            if value is None or value <= 0:
                points.append(run)
                run = []
            else:
                run.append((x_at(i), y_at(value)))
        points.append(run)
        for run in points:
            if len(run) > 1:
                path = " ".join(f"{x:.1f},{y:.1f}" for x, y in run)
                parts.append(f'<polyline class="line" stroke="var(--s{s})" points="{path}"/>')
        for run in points:
            parts += [f'<circle class="dot" fill="var(--s{s})" cx="{x:.1f}" cy="{y:.1f}" r="4"/>'
                      for x, y in run]  # fmt: skip
        if values[-1] is not None and values[-1] > 0:
            ends.append((y_at(values[-1]), BLOCKS[s - 1]))
    # a label at the end of a line only where the lines have come apart
    ends.sort()
    apart = all(b[0] - a[0] >= 12 for a, b in zip(ends, ends[1:], strict=False))
    if apart and len(ends) == len(series):
        parts += [f'<text class="name" x="{WIDTH - RIGHT + 8}" y="{y + 4:.1f}">{label}</text>'
                  for y, label in ends]  # fmt: skip
    label = html.escape(f"{title}: the chance of changing hands, by how long the block has "
                        "had its leader, a line for each block size. The values are in the table "
                        "below.")  # fmt: skip
    return (f'<figure data-chart="{index}"><figcaption>{html.escape(title)}</figcaption>'
            f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" role="img" tabindex="0" aria-label="{label}">'
            f'{"".join(parts)}</svg><div class="tip" role="status"></div></figure>')  # fmt: skip


def table(summary: dict) -> str:
    """Every value drawn, and the rule as it is beside them."""
    rows = []
    for world, name in WORLDS.items():
        found = summary["worlds"][world]["changing hands, by a block's past"]
        for near in NEAR:
            for span in ("as it is", *SPANS):
                key = span if span == "as it is" else f"has had its leader for {span} ticks"
                cells = []
                for block in BLOCKS:
                    value = found[block]["chance"][key][near]
                    cells.append("<td>–</td>" if value is None else f"<td>{value:.4f}</td>")
                how = "whatever its past (the rule as it is)" if span == "as it is" else span
                rows.append(f"<tr><td>{html.escape(name)}, {near} rival neighbours</td>"
                            f"<td>{html.escape(how)}</td>{''.join(cells)}</tr>")  # fmt: skip
    head = "".join(f"<th>blocks of {b}</th>" for b in BLOCKS)
    return ("<details><summary>The values as a table</summary><table><thead><tr><th>World and "
            f"neighbours</th><th>Ticks it has had its leader</th>{head}</tr></thead><tbody>"
            f"{''.join(rows)}</tbody></table></details>")  # fmt: skip


def page(summary: dict) -> str:
    panels, data = [], []
    for world, name in WORLDS.items():
        row = []
        for near in NEAR:
            series = chances(summary, world, near)
            row.append(panel(series, f"{near} rival neighbours", len(data)))
            data.append({"xs": [round(x_at(i), 1) for i in range(len(SPANS))], "series": series})
        panels.append(f'<h2>{html.escape(name)}</h2><div class="row">{"".join(row)}</div>')
    legend = "".join(f'<span><span class="key" style="border-top-color:var(--s{s})"></span>'
                     f"blocks of {b}</span>" for s, b in enumerate(BLOCKS, start=1))  # fmt: skip
    embedded = json.dumps({"panels": data, "spans": list(SPANS), "blocks": list(BLOCKS),
                           "width": WIDTH}).replace("</", "<\\/")  # fmt: skip
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>How long a block has had its leader</title><style>{STYLE}</style></head>
<body class="viz-root"><main>
<h1>How often a block changes hands, by how long it has had its leader</h1>
<p>Each chart is for blocks with so many of their eight neighbours under the rival. Along the
bottom: for how many ticks running the block has had its present leader. Up the side: the
chance it has another leader one tick on, on a scale of tenfolds. One line for each block
size, each read at the age that matches it.</p>
<p>Where the four lines lie on one another, the table is the same at every block size once a
block's past is in view: that is so at five rival neighbours. Where they stand apart, it is
not: at three, a block twice the size changes hands about half as often, whatever its
past.</p>
<div class="legend" aria-label="Block sizes">{legend}</div>
{"".join(panels)}
{table(summary)}
<p class="foot">From examples/scale-up-memory/look/summary.json: step 4g's sixteen runs (side
2,048 to generation 16,384) read again with a block's past in view. Exploratory: nothing here
is registered. A chance is drawn where at least 200 blocks stand behind it.</p>
</main><script id="data" type="application/json">{embedded}</script>
<script>{SCRIPT}</script></body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, default=OUT, help="the folder the page goes to")
    args = parser.parse_args()
    summary = json.loads(SUMMARY.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(page(summary))
    print(f"written {args.out / 'index.html'}")


if __name__ == "__main__":
    main()
