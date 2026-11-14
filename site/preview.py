"""
Serve site/public/ on this machine the way Firebase Hosting serves it, to check pages before
a deploy.

    python3 site/preview.py                     # then open the address it prints
    python3 site/preview.py 8123                # on another port
    python3 site/preview.py --bind 127.0.0.1    # reachable from this machine only

Like firebase.json's cleanUrls and trailingSlash settings: /census serves census.html,
/census.html and /census/ redirect to /census, and a missing page gets 404.html with status 404.
Plain `python3 -m http.server` does none of that, so the links between pages would not resolve.

Like `python3 -m http.server`, it listens on every address of this machine, IPv6 and IPv4, so
the pages can be opened from another machine on the network: "localhost" in a browser means the
machine the browser is on, which over SSH is not this one.
"""

from __future__ import annotations

import argparse
import contextlib
import socket
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent / "public"


class Handler(SimpleHTTPRequestHandler):
    def route(self) -> bool:
        """Apply Firebase's rules to the path asked for; True when the answer has been sent."""
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
            return True
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
            if self.command != "HEAD":
                self.wfile.write(body)
            return True
        return False

    def do_GET(self) -> None:
        if not self.route():
            super().do_GET()

    def do_HEAD(self) -> None:
        if not self.route():
            super().do_HEAD()

    def log_message(self, format: str, *args: object) -> None:
        pass


class DualStackServer(ThreadingHTTPServer):
    """Listens for IPv6 and IPv4 on one socket, as `python3 -m http.server` does."""

    address_family = socket.AF_INET6

    def server_bind(self) -> None:
        with contextlib.suppress(OSError):
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


def network_address() -> str | None:
    """This machine's address on its network, for opening the pages from another machine."""
    with contextlib.suppress(OSError), socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.connect(("192.0.2.1", 9))  # sends nothing: it only asks which address would be used
        address = probe.getsockname()[0]
        return None if address.startswith("127.") else address
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    parser.add_argument("port", nargs="?", type=int, default=8000)
    parser.add_argument(
        "--bind",
        metavar="ADDRESS",
        help="listen on this address only, such as 127.0.0.1 (default: every address)",
    )
    args = parser.parse_args()
    handler = partial(Handler, directory=str(PUBLIC))
    if args.bind:
        kind = DualStackServer if ":" in args.bind else ThreadingHTTPServer
        server = kind((args.bind, args.port), handler)
    else:
        try:
            server = DualStackServer(("::", args.port), handler)
        except OSError:  # a machine with IPv6 switched off
            server = ThreadingHTTPServer(("0.0.0.0", args.port), handler)
    print(f"serving {PUBLIC}")
    if args.bind:
        host = f"[{args.bind}]" if ":" in args.bind else args.bind
        print(f"  at http://{host}:{args.port}")
    else:
        print(f"  on this machine:      http://localhost:{args.port}")
        address = network_address()
        if address:
            print(f"  from another machine: http://{address}:{args.port}")
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()


if __name__ == "__main__":
    main()
