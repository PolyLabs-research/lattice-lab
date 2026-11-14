"""
Build the website's pages: each body in site/src/ wrapped in the shared head, header and footer.

    uv run python site/build_pages.py

Writes site/public/<page>.html. The bodies' interactive parts are in site/public/assets/js/.
lattice-lab's pages compute from site/public/assets/data.js (site/build_data.py); the other
programmes' pages carry their few numbers in their own bodies and scripts, each with its source.
"""

from __future__ import annotations

from pathlib import Path

SITE = Path(__file__).resolve().parent
SRC, OUT = SITE / "src", SITE / "public"

# page: (title, description, section). A section is a programme, and its key is the page that
# introduces it; the header marks it, and the lattice-lab section has a second row of its own.
PAGES = {
    "index": (
        "PolyLabs Research",
        "What small systems can actually do: cellular automata and quantum codes, a small chess "
        "network, a model that learns algebra by search, an evolved cell, a company of AI agents "
        "and a document-investigation agent, each judged by a check it cannot change.",
        "home",
    ),
    "lattice": (
        "lattice-lab · PolyLabs Research",
        "Laws of cellular automata on finite lattices, found by experiment, tested by registered "
        "prediction and proved in Lean, with AI agents proposing and proving.",
        "lattice",
    ),
    "model": (
        "The research model · PolyLabs Research",
        "How a claim becomes a result: experiment, law, registered test, Lean proof, and AI agents "
        "whose work is judged by machines. With the real ledger to check in your browser.",
        "lattice",
    ),
    "parity": (
        "Parity laws · PolyLabs Research",
        "Exact period laws of the parity rules on square, hexagonal and triangular tori: run them, "
        "and see where a registered law failed and was corrected.",
        "lattice",
    ),
    "atlas": (
        "Linear atlas · PolyLabs Research",
        "Periods of 502 linear cellular automata, three registered rounds, the eigenvalues that "
        "decide them, and the cubes and ninth powers at m = 37.",
        "lattice",
    ),
    "settling": (
        "Settling time · PolyLabs Research",
        "How long a random soup takes to settle: a logarithmic law replicated to tori of side "
        "1024, and fluctuations with one shape across lattices.",
        "lattice",
    ),
    "proofs": (
        "Proofs · PolyLabs Research",
        "The Lean 4 library behind the results: what is proved, by whom, and on which axioms.",
        "lattice",
    ),
    "codes": (
        "Quantum codes · PolyLabs Research",
        "How the ring of these rules carries over to bivariate bicycle quantum codes: logical "
        "qubits read off the torus's characters, checked by a registered test and in your browser.",
        "lattice",
    ),
    "census": (
        "Code census · PolyLabs Research",
        "Every weight-6 bivariate bicycle code up to 400 qubits: the best distance and the best "
        "k d²/n at each size, and what was registered before each stage ran.",
        "lattice",
    ),
    "tiny-alphazero": (
        "Tiny AlphaZero · PolyLabs Research",
        "A 6.5-million-parameter chess network trained by self-play on one small computer: how "
        "improvement is measured, 25 registered rounds, the plateau, and a public rating that "
        "comes out as a spread.",
        "tiny-alphazero",
    ),
    "reckoner": (
        "Reckoner · PolyLabs Research",
        "A five-million-parameter model learning algebra by search against a checker, one readable "
        "rewrite at a time: the par game, the first campaign and its errata, and a sweep whose "
        "predictions failed.",
        "reckoner",
    ),
    "protocell": (
        "Protocell · PolyLabs Research",
        "A single simulated cell whose wall and brain are one neural network, evolved to manage "
        "light: the hypothesis, the worlds, and the first cell to beat every simple rule tried.",
        "protocell",
    ),
    "organisation": (
        "the_organisation · PolyLabs Research",
        "An open-source company of AI agents, with gates between phases and a person who pays and "
        "signs: what it is, the checks agents cannot talk past, and its one run on a real model.",
        "organisation",
    ),
    "corpus-lens": (
        "Corpus Lens · PolyLabs Research",
        "A document-investigation tool whose agent may record a finding only with a quote the "
        "server finds on a real page: the pipeline, the citation gate to try, and what is checked.",
        "corpus-lens",
    ),
    "contact": (
        "Contact · PolyLabs Research",
        "Write to PolyLabs Research: questions about any of the programmes, their results or "
        "their methods.",
        "contact",
    ),
    "404": ("Not found · PolyLabs Research", "This page does not exist.", ""),
}

# The header's first row: one link per programme, then contact.
NAV = [
    ("lattice", "lattice-lab"),
    ("tiny-alphazero", "Tiny AlphaZero"),
    ("reckoner", "Reckoner"),
    ("protocell", "Protocell"),
    ("organisation", "the_organisation"),
    ("corpus-lens", "Corpus Lens"),
    ("contact", "Contact"),
]

# A programme's own pages, shown as a second row on each of them.
SUBNAV = {
    "lattice": [
        ("lattice", "Overview"),
        ("model", "The model"),
        ("parity", "Parity laws"),
        ("atlas", "Linear atlas"),
        ("settling", "Settling time"),
        ("proofs", "Proofs"),
        ("codes", "Quantum codes"),
        ("census", "Code census"),
    ],
}

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
    <nav class="nav" aria-label="Programmes">
{nav}
    </nav>
  </div>
{subnav}</header>
"""

SUBNAV_ROW = """  <div class="bar sub">
    <nav class="nav subnav" aria-label="{label}">
{links}
    </nav>
  </div>
"""

# What every page's footer says, then what the page's own programme adds.
FOOT_ALL = """<p>Every number on this site comes from a programme's own records (its registered
      predictions, preregistrations, run logs and rulings) or is computed in your browser. Where a
      test failed, the page says so, and a result counts because a check outside the work passed
      it, not because the work says so.</p>"""

FOOT_SECTION = {
    "lattice": """<p>Experiments run on
      <a href="https://github.com/PolyLabs-research/gameoflife_advanced">LatticeLife</a>; laws are
      fitted by <a href="https://github.com/PolyLabs-research/kepler">Kepler</a>; both are open
      source. The studies, with their ledgers and records, and the Lean library are in
      <a href="https://github.com/PolyLabs-research/lattice-lab">lattice-lab</a>, which is open
      source too.</p>
    <p>The agents in the pilots are Claude Code sessions, each started fresh with no context but a
      problem card; the seventh pilot's second round ran over the API. Their proofs count because
      Lean accepts them, not because they say so.</p>""",
}

FOOT = """<footer class="site-foot gutter">
  <div class="bar">
    {notes}
    <div class="links">
      <a href="https://github.com/PolyLabs-research">github.com/PolyLabs-research</a>
      <a href="index.html#method">How we work</a>
      <a href="contact.html">Contact</a>
      <a href="mailto:contact@polylabs-research.net">contact@polylabs-research.net</a>
    </div>
  </div>
</footer>
{scripts}
</body>
</html>
"""


def nav_links(items: list[tuple[str, str]], page: str, section: str, indent: str) -> str:
    """The links of one navigation row, the current page marked, and its programme too."""
    out = []
    for key, label in items:
        mark = ""
        if key == page:
            mark = ' aria-current="page"'
        elif key == section:
            mark = ' aria-current="true"'
        out.append(f'{indent}<a href="{key}.html"{mark}>{label}</a>')
    return "\n".join(out)


def build(page: str) -> str:
    title, description, section = PAGES[page]
    nav = nav_links(NAV, page, section, "      ")
    subnav = ""
    if section in SUBNAV:
        label = dict(NAV)[section]
        links = nav_links(SUBNAV[section], page, "", "      ")
        subnav = SUBNAV_ROW.format(label=f"{label} pages", links=links)
    body = (SRC / f"{page}.html").read_text()
    # The 404 page is served at whatever path was missed, such as /proofs/nope, so its relative
    # links must resolve from the root.
    base = '<base href="/">\n' if page == "404" else ""
    head = HEAD.format(
        title=title, description=description, base=base, mark=MARK, nav=nav, subnav=subnav
    )
    # data.js holds lattice-lab's records, which only its own pages compute from.
    scripts = ['<script src="assets/data.js"></script>'] if section == "lattice" else []
    scripts.append('<script src="assets/lib.js"></script>')
    if (OUT / "assets" / "js" / f"{page}.js").exists():
        scripts.append(f'<script src="assets/js/{page}.js"></script>')
    notes = "\n    ".join(n for n in (FOOT_ALL, FOOT_SECTION.get(section, "")) if n)
    return head + body.rstrip() + "\n" + FOOT.format(notes=notes, scripts="\n".join(scripts))


def main() -> None:
    for page in PAGES:
        (OUT / f"{page}.html").write_text(build(page))
        print(f"wrote {OUT / page}.html")


if __name__ == "__main__":
    main()
