"""
Serve site/public/ on this machine the way Firebase Hosting serves it, to check pages before
a deploy.

    python3 site/preview.py          # then open http://localhost:8000
    python3 site/preview.py 8123     # on another port

Like firebase.json's cleanUrls and trailingSlash settings: /census serves census.html,
/census.html and /census/ redirect to /census, and a missing page gets 404.html with status 404.
Plain `python3 -m http.server` does none of that, so the links between pages would not resolve.
"""

from __future__ import annotations

import sys
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent / "public"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        path, _, query = self.path.partition("?")
        clean = None
        if path.endswith("/index.html"):
            clean = path[: -len("index.html")]
        elif path.endswith(".html"):
            clean = path[: -len(".html")]
        elif path.endswith("/") and path != "/":
            clean = path.rstrip("/")
        if clean is not None:
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", clean + ("?" + query if query else ""))
            self.end_headers()
            return
        target = PUBLIC / path.lstrip("/")
        if path == "/":
            self.path = "/index.html"
        elif not target.exists() and target.with_name(target.name + ".html").is_file():
            self.path = path + ".html"
        elif not target.is_file():
            body = (PUBLIC / "404.html").read_bytes()
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(PUBLIC)))
    print(f"serving {PUBLIC} at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
