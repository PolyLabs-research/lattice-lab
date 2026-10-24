"""
The split search of examples/qec-open-distance/parts.py with the packing cut (search_pack.c).

parts.py is loaded here as a module of its own (`qec_open_parts_pack`), and that copy's SEARCH_C
is set to search_pack.c, so `search` below is parts.search, unchanged, running the new C program;
examples/qec-open-distance and its registered files are not touched. `reference` is the same
search with study 1's search_parts.c (no packing cut), and `brute` is distance_brute: the two
instruments the packing search is checked against.

search_pack.c's docstring gives the packing cut and its argument. In short: the unsatisfied
checks whose candidate sets are pairwise disjoint each need a qubit of their own from the logical,
so a branch with |S| + packing >= best holds no lighter logical. Every claim of parts.search (a
pass without a find shows d >= its bound; the least find of a pass is the least weight below it)
holds as before.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPEN = HERE.parent / "qec-open-distance"
SEARCH_C = HERE / "search_pack.c"


def _load(name: str, path: Path):
    """A module from its file, registered under `name` (once per process)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


packed = _load("qec_open_parts_pack", OPEN / "parts.py")
packed.SEARCH_C = SEARCH_C
plain = _load("qec_open_parts", OPEN / "parts.py")
bb, distance = packed.bb, packed.distance
sha256 = packed.sha256


def search(*args, **kwargs) -> dict:
    """parts.search with search_pack.c; the result names the C file and its sha256."""
    out = packed.search(*args, **kwargs)
    out.pop("search_parts_c_sha256", None)
    return {**out, "search_c": "search_pack.c", "search_c_sha256": sha256(SEARCH_C)}


def reference(*args, **kwargs) -> dict:
    """parts.search with study 1's search_parts.c (no packing cut)."""
    out = plain.search(*args, **kwargs)
    out.pop("search_parts_c_sha256", None)
    return {**out, "search_c": "search_parts.c", "search_c_sha256": sha256(plain.SEARCH_C)}


def brute(A, B, ell: int, m: int, kind: str = "Z") -> int | None:
    return distance.distance_brute(A, B, ell, m, kind)["d"]
