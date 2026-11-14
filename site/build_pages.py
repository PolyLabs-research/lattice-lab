"""
Build the website's pages: each body in site/src/ wrapped in the shared head, header and footer.

    uv run python site/build_pages.py                # for Firebase Hosting, which is in use
    uv run python site/build_pages.py --html-links   # for a host without clean URLs

Writes site/public/<page>.html, sitemap.xml and robots.txt. The bodies' interactive parts are in
site/public/assets/js/. lattice-lab's pages compute from site/public/assets/data.js
(site/build_data.py); the other programmes' pages carry their few numbers in their own bodies and
scripts, each with its source.

Firebase serves /census.html at /census and redirects the longer address to it, so links between
pages are written without ".html" unless --html-links is given. Bodies in src/ name pages as
"census.html" either way; the builder rewrites them.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
SRC, OUT = SITE / "src", SITE / "public"

ORIGIN = "https://polylabs-research.net"
SITE_NAME = "PolyLabs Research"
# The picture a shared link shows (site/og-card.html, rendered at 1200 x 630).
CARD = f"{ORIGIN}/assets/og.png"
CARD_ALT = "PolyLabs Research: small systems, judged by checks they cannot change"

# page: (title, description, section). The title is what a search result shows first, so it
# names the subject in the words someone would search for; the site's name is added after it. A
# description over about 160 characters is cut off in a search result. A section is a programme,
# and its key is the page that introduces it; the header marks it, and the lattice-lab section has
# a second row of its own.
PAGES = {
    "index": (
        "PolyLabs Research: small systems, judged by machines",
        "What small systems can actually do: cellular automata and quantum codes, a 6.5M-parameter "
        "chess network, algebra by search, an evolved cell and AI agents.",
        "home",
    ),
    "lattice": (
        "lattice-lab: cellular automaton laws, proved in Lean",
        "Laws of cellular automata on finite lattices, found by experiment, tested by registered "
        "prediction and proved in Lean, with AI agents proposing and proving.",
        "lattice",
    ),
    "model": (
        "How a claim becomes a result: the research model",
        "How a claim becomes a result: experiment, law, registered test, Lean proof, and AI agents "
        "judged by machines. With a real ledger to check in your browser.",
        "lattice",
    ),
    "parity": (
        "Period laws of parity cellular automata",
        "Exact period laws of the parity rules on square, hexagonal and triangular tori: run them, "
        "and see where a registered law failed and was corrected.",
        "lattice",
    ),
    "atlas": (
        "An atlas of linear cellular automata periods",
        "Periods of 502 linear cellular automata, three registered rounds, the eigenvalues that "
        "decide them, and the cubes and ninth powers at m = 37.",
        "lattice",
    ),
    "settling": (
        "Settling time of Life-like cellular automata",
        "How long a random soup takes to settle: a logarithmic law replicated to tori of side "
        "1024, and fluctuations with one shape across lattices.",
        "lattice",
    ),
    "proofs": (
        "Lean 4 proofs of cellular automaton laws",
        "The Lean 4 library behind lattice-lab's results on cellular automata: what is proved, by "
        "whom (AI agents included), and on which axioms.",
        "lattice",
    ),
    "codes": (
        "Bivariate bicycle quantum codes: k and d, reproduced",
        "Bivariate bicycle quantum codes in the ring of linear cellular automata: logical qubits "
        "read off the torus's characters, and published distances reproduced.",
        "lattice",
    ),
    "census": (
        "Census of bivariate bicycle codes up to 400 qubits",
        "Every weight-6 bivariate bicycle code up to 400 qubits: the best distance and the best "
        "k d²/n at each size, and what was registered before each stage ran.",
        "lattice",
    ),
    "tiny-alphazero": (
        "Tiny AlphaZero: a 6.5M-parameter chess network",
        "A 6.5M-parameter chess network trained by self-play on one small computer: 25 registered "
        "rounds, a plateau, and a public rating that comes out as a spread.",
        "tiny-alphazero",
    ),
    "reckoner": (
        "Reckoner: a small model learning algebra by search",
        "A 5M-parameter model learning algebra by search against a checker, one readable rewrite "
        "at a time: the par game, the first campaign and its errata.",
        "reckoner",
    ),
    "protocell": (
        "Protocell: an evolved cell that manages light",
        "A simulated cell whose wall and brain are one neural network, evolved to manage light: "
        "the hypothesis, the worlds, and the first cell to beat every simple rule.",
        "protocell",
    ),
    "organisation": (
        "the_organisation: a company of AI agents",
        "An open-source company of AI agents with gates between phases and a person who pays and "
        "signs: the checks agents cannot talk past, and its one real run.",
        "organisation",
    ),
    "corpus-lens": (
        "Corpus Lens: an agent that must quote its page",
        "Document investigation where an AI agent may record a finding only with a quote the "
        "server finds on a real page. Try the citation gate in your browser.",
        "corpus-lens",
    ),
    "contact": (
        "Contact",
        "Write to PolyLabs Research: questions about any of the programmes, their results or "
        "their methods.",
        "contact",
    ),
    "404": ("Not found", "This page does not exist.", ""),
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
<html lang="en-GB">
<head>
<meta charset="utf-8">
{base}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
{indexing}
<meta property="og:site_name" content="PolyLabs Research">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{card}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{card_alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f2f4f1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1416" media="(prefers-color-scheme: dark)">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="assets/mark.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
{preloads}
<link rel="stylesheet" href="assets/fonts/fonts.css">
<link rel="stylesheet" href="assets/site.css">
{structured}
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
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

# The two fonts every page's first screen is set in, fetched before the stylesheet asks for them.
PRELOADS = "\n".join(
    f'<link rel="preload" href="assets/fonts/{font}.woff2" as="font" type="font/woff2" crossorigin>'
    for font in ("stix-two-text-normal-400-600-latin", "ibm-plex-mono-normal-400-latin")
)

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


def url(page: str) -> str:
    """A page's one address, as Firebase serves it."""
    return f"{ORIGIN}/" if page == "index" else f"{ORIGIN}/{page}"


def structured(page: str) -> str:
    """What the page is, for search engines (schema.org, as JSON-LD)."""
    title, description, section = PAGES[page]
    org, site = f"{ORIGIN}/#organisation", f"{ORIGIN}/#website"
    if page == "index":
        graph = [
            {
                "@type": "Organization",
                "@id": org,
                "name": SITE_NAME,
                "url": f"{ORIGIN}/",
                "logo": f"{ORIGIN}/assets/mark-512.png",
                "email": "contact@polylabs-research.net",
                "sameAs": ["https://github.com/PolyLabs-research"],
            },
            {
                "@type": "WebSite",
                "@id": site,
                "name": SITE_NAME,
                "url": f"{ORIGIN}/",
                "description": description,
                "inLanguage": "en-GB",
                "publisher": {"@id": org},
            },
        ]
    else:
        # Home, then the programme, then the programme's own page.
        crumbs = [(SITE_NAME, "index")]
        if section in dict(NAV):
            crumbs.append((dict(NAV)[section], section))
        if page != section:
            crumbs.append((dict(SUBNAV.get(section, [])).get(page, title), page))
        graph = [
            {
                "@type": "WebPage",
                "@id": url(page),
                "url": url(page),
                "name": title,
                "description": description,
                "inLanguage": "en-GB",
                "isPartOf": {"@id": site},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": i, "name": name, "item": url(key)}
                    for i, (name, key) in enumerate(crumbs, 1)
                ],
            },
        ]
    data = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def clean_links(document: str) -> str:
    """Links between pages without ".html", the form Firebase serves and does not redirect."""
    pages = "|".join(re.escape(page) for page in PAGES)

    def clean(match: re.Match) -> str:
        page, rest = match.group(1), match.group(2) or ""
        return f'href="{"./" if page == "index" else page}{rest}"'

    return re.sub(rf'href="({pages})\.html(#[^"]*)?"', clean, document)


def build(page: str, html_links: bool = False) -> str:
    title, description, section = PAGES[page]
    nav = nav_links(NAV, page, section, "      ")
    subnav = ""
    if section in SUBNAV:
        label = dict(NAV)[section]
        links = nav_links(SUBNAV[section], page, "", "      ")
        subnav = SUBNAV_ROW.format(label=f"{label} pages", links=links)
    body = (SRC / f"{page}.html").read_text().replace("<main class=", '<main id="main" class=', 1)
    # The 404 page is served at whatever path was missed, such as /proofs/nope, so its relative
    # links must resolve from the root. It has no address of its own to index.
    missing = page == "404"
    base = '<base href="/">\n' if missing else ""
    if missing:
        indexing = '<meta name="robots" content="noindex">'
    else:
        indexing = (
            f'<link rel="canonical" href="{url(page)}">\n'
            f'<meta property="og:url" content="{url(page)}">'
        )
    head = HEAD.format(
        title=html.escape(title if page == "index" else f"{title} · {SITE_NAME}"),
        og_title=html.escape(title),
        description=html.escape(description),
        indexing=indexing,
        card=CARD,
        card_alt=html.escape(CARD_ALT),
        preloads=PRELOADS,
        structured=""
        if missing
        else f'<script type="application/ld+json">{structured(page)}</script>',
        base=base,
        mark=MARK,
        nav=nav,
        subnav=subnav,
    )
    # data.js holds lattice-lab's records, which only its own pages compute from.
    scripts = ['<script src="assets/data.js"></script>'] if section == "lattice" else []
    scripts.append('<script src="assets/lib.js"></script>')
    if (OUT / "assets" / "js" / f"{page}.js").exists():
        scripts.append(f'<script src="assets/js/{page}.js"></script>')
    notes = "\n    ".join(n for n in (FOOT_ALL, FOOT_SECTION.get(section, "")) if n)
    document = head + body.rstrip() + "\n" + FOOT.format(notes=notes, scripts="\n".join(scripts))
    return document if html_links else clean_links(document)


def sitemap() -> str:
    """Every page a search engine should list, at its one address."""
    locs = "\n".join(f"  <url><loc>{url(page)}</loc></url>" for page in PAGES if page != "404")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{locs}\n</urlset>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--html-links",
        action="store_true",
        help='link pages as "census.html", for a host that does not serve clean URLs',
    )
    args = parser.parse_args()
    for page, (_, description, _) in PAGES.items():
        (OUT / f"{page}.html").write_text(build(page, args.html_links))
        print(f"wrote {OUT / page}.html")
        if len(description) > 160 and page != "404":
            print(f"  note: its description is {len(description)} characters; 160 are shown")
    (OUT / "sitemap.xml").write_text(sitemap())
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n")
    print(f"wrote {OUT}/sitemap.xml and robots.txt")


if __name__ == "__main__":
    main()
