"""
Check the built website for what can be checked mechanically, before a pull request or a deploy.

    python3 site/build_pages.py && python3 site/check_site.py

Exits 0 when every check passes and 1 otherwise, listing each failure. It checks that:

- every page in build_pages.PAGES is built, and the sitemap lists each of them but the 404 page;
- every link between pages, and to an asset, leads to a file, and every #anchor to an id there;
- each programme page has its table of results, and each row's first badge says how it came out;
- the review's record (review-state.json) names every programme the home page draws;
- nothing links into a private repository, and no page holds an email address but the site's own
  or a path on someone's machine;
- the home page's "Latest on the record" holds at most eight entries, each with its date, its
  verdict and its record.

It reads only site/public/ and site/review-state.json, and needs nothing but Python.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import build_pages

SITE = Path(__file__).resolve().parent
PUBLIC = SITE / "public"
OWN_EMAIL = "contact@polylabs-research.net"
LEDGER_MAX = 8


class Page(HTMLParser):
    """The links, ids and ledger entries of one built page."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.ledger: list[dict] = []
        self._in_ledger = False
        self._entry: dict | None = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        classes = (a.get("class") or "").split()
        if tag == "ol" and "ledger" in classes:
            self._in_ledger = True
        elif self._in_ledger and tag == "li":
            self._entry = {"when": False, "badge": False, "receipt": False}
        elif self._entry is not None:
            if "when" in classes:
                self._entry["when"] = True
            if "badge" in classes:
                self._entry["badge"] = True
            if "receipt" in classes:
                self._entry["receipt"] = True

    def handle_endtag(self, tag: str) -> None:
        if self._entry is not None and tag == "li":
            self.ledger.append(self._entry)
            self._entry = None
        elif self._in_ledger and tag == "ol":
            self._in_ledger = False


def target(link: str, here: str) -> tuple[Path, str] | None:
    """The file and anchor a link on page `here` leads to, or None for a link off the site."""
    if re.match(r"^[a-z]+:", link) or link.startswith("//"):
        return None
    path, _, anchor = link.partition("#")
    if not path:
        return PUBLIC / f"{here}.html", anchor
    path = path.split("?")[0].lstrip("/")
    if path in ("", "./"):
        return PUBLIC / "index.html", anchor
    file = PUBLIC / path
    if not file.suffix and file.with_name(file.name + ".html").exists():
        file = file.with_name(file.name + ".html")
    return file, anchor


def main() -> int:
    failures: list[str] = []
    pages: dict[str, Page] = {}
    state = json.loads((SITE / "review-state.json").read_text())["repos"]
    private = [entry["repo"] for entry in state.values() if not entry["public"]]
    for name in build_pages.PAGES:
        file = PUBLIC / f"{name}.html"
        if not file.exists():
            failures.append(f"{name}: not built")
            continue
        page = Page()
        text = file.read_text()
        page.feed(text)
        pages[name] = page
        # privacy: no link into a private repository, no address but the site's own, no paths
        for repo in private:
            if f"github.com/{repo}".lower() in text.lower():
                failures.append(f"{name}: links into the private repository {repo}")
        for email in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)):
            if email != OWN_EMAIL:
                failures.append(f"{name}: holds the email address {email}")
        for path in set(re.findall(r"(?:/home/|/media/|/Users/)[\w.-]+", text)):
            failures.append(f"{name}: holds the local path {path}")

    # links and anchors
    for name, page in pages.items():
        for link in page.links:
            if name == "404" or link.startswith("mailto:"):
                continue
            hit = target(link, name)
            if hit is None:
                continue
            file, anchor = hit
            if not file.exists():
                failures.append(f"{name}: {link} leads to no file")
            elif anchor and file.suffix == ".html":
                ids = pages.get(file.stem, Page()).ids
                if anchor not in ids:
                    failures.append(f"{name}: {link} names an anchor that is not there")

    # the sitemap
    sitemap = (PUBLIC / "sitemap.xml").read_text() if (PUBLIC / "sitemap.xml").exists() else ""
    for name in build_pages.PAGES:
        if name != "404" and build_pages.url(name) not in sitemap:
            failures.append(f"sitemap.xml: does not list {name}")

    # each programme's results, and the review's record of them
    covered = {page for entry in state.values() for page in entry["pages"]}
    for name in build_pages.RECORD_PAGES:
        rows = build_pages.record(name)
        if not rows:
            failures.append(f"{name}: has no table of results with a badge in each row")
        if name not in covered:
            failures.append(f"review-state.json: no repository is reviewed for the {name} page")

    # the home page's latest entries
    ledger = pages.get("index", Page()).ledger
    if not ledger:
        failures.append("index: has no Latest on the record list")
    if len(ledger) > LEDGER_MAX:
        failures.append(f"index: Latest on the record has {len(ledger)} entries, over {LEDGER_MAX}")
    for i, entry in enumerate(ledger, 1):
        missing = [part for part, there in entry.items() if not there]
        if missing:
            failures.append(f"index: entry {i} of Latest on the record has no {', '.join(missing)}")

    for line in failures:
        print(line)
    verdict = "all checks pass" if not failures else f"{len(failures)} failures"
    print(f"{len(pages)} pages checked: {verdict}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
