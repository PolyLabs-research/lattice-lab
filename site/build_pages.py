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
import itertools
import json
import re
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent
SRC, OUT = SITE / "src", SITE / "public"

ORIGIN = "https://polylabs-research.net"
SITE_NAME = "PolyLabs Research"
# The picture a shared link shows (site/og-card.html, rendered at 1200 x 630).
CARD = f"{ORIGIN}/assets/og.png"
CARD_ALT = "PolyLabs Research: small systems, judged by checks they cannot change"
# Where each page's source, and so its history, is kept.
HISTORY = "https://github.com/PolyLabs-research/lattice-lab/commits/main/site/src"

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
<meta name="theme-color" content="#0b1113">
<script>try{{if(localStorage.getItem("theme")==="light")document.documentElement.dataset.theme="light"}}catch(e){{}}</script>
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
{toggle}
  </div>
{subnav}</header>
"""

# The header's switch between the dark theme, which is the site's own, and a light one.
ICON = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"'
TOGGLE = f"""    <button class="theme-toggle" type="button" aria-label="Switch to the light theme">
      <svg class="moon" {ICON} stroke-linejoin="round">
        <path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>
      </svg>
      <svg class="sun" {ICON} stroke-linecap="round">
        <circle cx="12" cy="12" r="4"/>
        <path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2"/>
        <path d="M5.3 5.3l1.5 1.5M17.2 17.2l1.5 1.5M5.3 18.7l1.5-1.5M17.2 6.8l1.5-1.5"/>
      </svg>
    </button>"""

# The fonts every page's first screen is set in, fetched before the stylesheet asks for them.
PRELOADS = "\n".join(
    f'<link rel="preload" href="assets/fonts/{font}.woff2" as="font" type="font/woff2" crossorigin>'
    for font in (
        "ibm-plex-sans-normal-400-latin",
        "ibm-plex-sans-normal-600-latin",
        "ibm-plex-mono-normal-400-latin",
    )
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
    <p class="colophon">No trackers, and no requests to anyone else: the fonts are served from
      here.{history}</p>
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


# The programmes whose pages hold a table of results, in the order the home page shows them. The
# home page draws one cell for each row of each table, so it cannot say more than the pages do.
RECORD_PAGES = ["lattice", "tiny-alphazero", "reckoner", "protocell", "organisation", "corpus-lens"]
# A row's first badge says how it came out: held, did not hold, held with a caveat, or open.
VERDICTS = {"ok": "h", "bad": "m", "gold": "q", "muted": "o"}
# The words for a count of each kind, where a page's table is not one of claims that held or not.
RECORD_WORDS = {
    "noun": "results",
    "h": "held",
    "m": "did not hold",
    "q": "with a caveat",
    "o": "open or null",
}
RECORD_WORDS_FOR = {
    "organisation": {
        "noun": "ways of running it",
        "h": "complete",
        "q": "run in part",
        "o": "not yet run for real",
    },
    "corpus-lens": {"noun": "checks", "o": "not yet run"},
}


class ResultRows(HTMLParser):
    """The rows of a page's table of results: its headings, each cell's text, each row's badges."""

    def __init__(self) -> None:
        super().__init__()
        self.heads: list[str] = []
        self.rows: list[dict] = []
        self.inside = self.in_body = False
        self.text: list[str] | None = None
        self.badge: list[str] | None = None
        self.row: dict | None = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        classes = (dict(attrs).get("class") or "").split()
        if tag == "table":
            self.inside = "stack" in classes and not self.rows
        if not self.inside:
            return
        if tag == "tbody":
            self.in_body = True
        elif tag == "tr" and self.in_body:
            self.row = {"cells": [], "badges": []}
        elif tag in ("td", "th"):
            self.text = []
        elif tag == "span" and "badge" in classes and self.row is not None:
            kind = next((c for c in classes if c in VERDICTS), "muted")
            self.badge = [kind, ""]

    def handle_endtag(self, tag: str) -> None:
        if not self.inside:
            return
        if tag == "table":
            self.inside = self.in_body = False
        elif tag == "span" and self.badge is not None and self.row is not None:
            self.row["badges"].append((self.badge[0], " ".join(self.badge[1].split())))
            self.badge = None
        elif tag in ("td", "th") and self.text is not None:
            text = " ".join("".join(self.text).split())
            if self.row is not None:
                self.row["cells"].append(text)
            elif tag == "th":
                self.heads.append(text)
            self.text = None
        elif tag == "tr" and self.row is not None:
            if self.row["badges"]:
                self.rows.append(self.row)
            self.row = None

    def handle_data(self, data: str) -> None:
        if self.text is not None:
            self.text.append(data)
        if self.badge is not None:
            self.badge[1] += data


def record(page: str) -> list[dict]:
    """A programme's results, as its page lists them: the claim, how it came out, and the rest."""
    parser = ResultRows()
    parser.feed((SRC / f"{page}.html").read_text())
    # A table that begins with the round or the stage names its claim in the second column.
    labelled = parser.heads[:1] in (["Round"], ["Stage"])
    results = []
    for row in parser.rows:
        cells, (kind, label) = row["cells"], row["badges"][0]
        claim = f"{cells[0]}: {cells[1]}" if labelled else cells[0]
        results.append(
            {
                "verdict": VERDICTS[kind],
                "kind": kind,
                "label": label,
                "claim": claim,
                "outcome": cells[-1].removeprefix(label).strip(),
            }
        )
    return results


def number_rows(body: str) -> str:
    """Give each row of a page's table of results an id, for the home page's cells to link to."""
    start = body.find('<table class="stack">')
    if start < 0:
        return body
    first, end = body.index("<tbody>", start), body.index("</table>", start)
    count = itertools.count(1)
    rows = re.sub(r"<tr>", lambda _: f'<tr id="result-{next(count)}">', body[first:end])
    return body[:first] + rows + body[end:]


def tally(page: str, results: list[dict]) -> str:
    """A programme's results counted by how they came out, in that page's words."""
    words = RECORD_WORDS | RECORD_WORDS_FOR.get(page, {})
    counts = {v: sum(r["verdict"] == v for r in results) for v in "hmqo"}
    parts = ", ".join(f"{counts[v]} {words[v]}" for v in "hmqo" if counts[v])
    return f"{len(results)} {words['noun']}: {parts}"


def fill_record(body: str) -> str:
    """The home page's cells and counts, written from the programme pages' own tables."""
    totals = dict.fromkeys("hmqo", 0)
    for page in RECORD_PAGES:
        results = record(page)
        cells = []
        for i, r in enumerate(results, 1):
            totals[r["verdict"]] += 1
            cells.append(
                f'<a class="c {r["verdict"]}" href="{page}.html#result-{i}" tabindex="-1"'
                f' data-kind="{r["kind"]}" data-label="{html.escape(r["label"])}"'
                f' data-claim="{html.escape(r["claim"])}"'
                f' data-outcome="{html.escape(r["outcome"])}"></a>'
            )
        counted = tally(page, results)
        head, _, rest = counted.partition(":")
        body = body.replace(f"<!--strip:{page}-->", "".join(cells))
        body = body.replace(f"<!--tally:{page}-->", f"<b>{head}</b>:{rest}")
        body = body.replace(f"<!--label:{page}-->", html.escape(counted))
    for verdict, count in totals.items():
        body = body.replace(f"<!--total:{verdict}-->", str(count))
    body = body.replace("<!--total:all-->", str(sum(totals.values())))
    if "<!--" in body:
        raise ValueError("the home page has a marker the builder did not fill")
    return body


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
    if page in RECORD_PAGES:
        body = number_rows(body)
    if page == "index":
        body = fill_record(body)
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
        toggle=TOGGLE,
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
    # The site is a folder of a public repository, so each page's history can be read there.
    history = (
        "" if missing else f' <a href="{HISTORY}/{page}.html">This page\'s history</a> is public.'
    )
    foot = FOOT.format(notes=notes, scripts="\n".join(scripts), history=history)
    document = head + body.rstrip() + "\n" + foot
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
