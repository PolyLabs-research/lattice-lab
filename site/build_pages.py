"""
Build the website's pages: each body in site/src/ wrapped in the shared head, header and footer.

    uv run python site/build_pages.py

Writes site/public/<page>.html. The bodies' interactive parts are in site/public/assets/js/, and
their data in site/public/assets/data.js (site/build_data.py).
"""

from __future__ import annotations

from pathlib import Path

SITE = Path(__file__).resolve().parent
SRC, OUT = SITE / "src", SITE / "public"

# page: (title, description)
PAGES = {
    "index": (
        "PolyLabs Research",
        "Laws of cellular automata on finite lattices, found by experiment, tested by registered "
        "prediction and proved in Lean, with AI agents proposing and proving.",
    ),
    "model": (
        "The research model · PolyLabs Research",
        "How a claim becomes a result: experiment, law, registered test, Lean proof, and AI agents "
        "whose work is judged by machines. With the real ledger to check in your browser.",
    ),
    "parity": (
        "Parity laws · PolyLabs Research",
        "Exact period laws of the parity rules on square, hexagonal and triangular tori: run them, "
        "and see where a registered law failed and was corrected.",
    ),
    "atlas": (
        "Linear atlas · PolyLabs Research",
        "Periods of 502 linear cellular automata, three registered rounds, the eigenvalues that "
        "decide them, and the open question at m = 37.",
    ),
    "settling": (
        "Settling time · PolyLabs Research",
        "How long a random soup takes to settle: a logarithmic law replicated to tori of side "
        "1024, and fluctuations with one shape across lattices.",
    ),
    "proofs": (
        "Proofs · PolyLabs Research",
        "The Lean 4 library behind the results: what is proved, by whom, and on which axioms.",
    ),
    "404": ("Not found · PolyLabs Research", "This page does not exist."),
}

NAV = [
    ("model", "The model"),
    ("parity", "Parity laws"),
    ("atlas", "Linear atlas"),
    ("settling", "Settling time"),
    ("proofs", "Proofs"),
]

MARK = """<svg class="brand-mark" viewBox="0 0 26 26" aria-hidden="true">
        <rect x="1" y="1" width="7" height="7" rx="1" style="fill: var(--cell)"/>
        <rect x="9.5" y="1" width="7" height="7" rx="1" style="fill: var(--cell-soft)"/>
        <rect x="18" y="1" width="7" height="7" rx="1" style="fill: var(--cell)"/>
        <rect x="1" y="9.5" width="7" height="7" rx="1" style="fill: var(--cell-soft)"/>
        <rect x="9.5" y="9.5" width="7" height="7" rx="1" style="fill: var(--gold)"/>
        <rect x="18" y="9.5" width="7" height="7" rx="1" style="fill: var(--cell-soft)"/>
        <rect x="1" y="18" width="7" height="7" rx="1" style="fill: var(--cell)"/>
        <rect x="9.5" y="18" width="7" height="7" rx="1" style="fill: var(--cell-soft)"/>
        <rect x="18" y="18" width="7" height="7" rx="1" style="fill: var(--cell)"/>
      </svg>"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{base}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/fonts/fonts.css">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<header class="site-head gutter">
  <div class="bar">
    <a class="brand" href="index.html">
      {mark}
      <span class="brand-name">PolyLabs Research</span>
    </a>
    <nav class="nav" aria-label="Site">
{nav}
    </nav>
  </div>
</header>
"""

FOOT = """<footer class="site-foot gutter">
  <div class="bar">
    <p>Every number on this site comes from the project's registered records or is computed in
      your browser from the rules themselves. Experiments run on
      <a href="https://github.com/PolyLabs-research/gameoflife_advanced">LatticeLife</a>; laws are
      fitted by <a href="https://github.com/PolyLabs-research/kepler">Kepler</a>; both are open
      source. The studies, ledgers and Lean library are in lattice-lab, which is private for
      now.</p>
    <p>The agents in the pilots are Claude Code sessions, each started fresh with no context but a
      problem card. Their proofs count because Lean accepts them, not because they say so.</p>
    <div class="links">
      <a href="https://github.com/PolyLabs-research">github.com/PolyLabs-research</a>
      <a href="model.html">How we work</a>
      <a href="proofs.html">What is proved</a>
    </div>
  </div>
</footer>
<script src="assets/data.js"></script>
<script src="assets/lib.js"></script>
{script}
</body>
</html>
"""


def build(page: str) -> str:
    title, description = PAGES[page]
    nav = "\n".join(f'      <a href="{p}.html">{label}</a>' for p, label in NAV)
    body = (SRC / f"{page}.html").read_text()
    # The 404 page is served at whatever path was missed, such as /proofs/nope, so its relative
    # links must resolve from the root.
    base = '<base href="/">\n' if page == "404" else ""
    head = HEAD.format(title=title, description=description, base=base, mark=MARK, nav=nav)
    js = OUT / "assets" / "js" / f"{page}.js"
    script = f'<script src="assets/js/{page}.js"></script>' if js.exists() else ""
    return head + body.rstrip() + "\n" + FOOT.format(script=script)


def main() -> None:
    for page in PAGES:
        (OUT / f"{page}.html").write_text(build(page))
        print(f"wrote {OUT / page}.html")


if __name__ == "__main__":
    main()
