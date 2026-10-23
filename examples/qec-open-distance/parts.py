"""
Two instruments for codes too large for examples/qec-distance's search on one core: that search
with each pass shared among processes (`search`, search_parts.c), and an upper bound by random
information sets (`window`, window.c). Both build their input from examples/qec-distance's
distance.py (bb's bitmask rows and `_logicals_bits`), in the format of its search.c, and every
witness either reports is checked by distance.verify_witness.

**The split search.** search_parts.c is search.c with a split: given (depth, parts, part), a
node whose set S has `depth` qubits is searched only by the part chosen by a hash of S's qubits
in the order they were added, and every part searches every node above that depth. A node's
place in the tree, and so its set and order, does not depend on the traversal: the children of
a node are the candidates of its check of fewest candidates, which depends on S, the exclusions
and the anchor, not on the best so far. Pruning does depend on the best so far, but only removes
subtrees, so a node at the split depth that one part reaches is the same node, with the same
subtree below it, in any part that reaches it. The parts' subtrees at that depth are therefore
disjoint, and every node at that depth that the unsplit pass would search (with the best it would
have) is searched by its own part. `search` runs passes b = first, first + 1, ... in turn, each
as `parts` processes of one pass with bound b (search.c's single pass: first = bound = b, which
lowers its bound to each find), at most `workers` at once, and stops after the first pass in
which some part finds a logical, or when the time is up.

- A pass in which no part finds a logical shows that no logical of the kind has weight below b:
  the unsplit pass with bound b keeps no leaf (search.c's argument), since each of its nodes at
  the split depth was searched by its own part with the same best (b, no part having lowered
  it), and its nodes above that depth by every part.
- A pass in which some part finds one gives the least weight below b exactly: each part ends
  with the least weight of a logical in its subtrees (or b), since a part lowers its bound only
  to weights it has found, and so prunes only subtrees with nothing lighter than its best; the
  least over parts is the least below b.
So d >= b after a pass at b with no find, and d = the least weight found in the first pass that
finds one, whatever the earlier passes did; earlier passes only bound the work. A pass stopped
by the time limit shows nothing; the lower bound is the largest b of a finished pass without a
find. Anchors: (0, lm) by distance_ilp's translation argument (distance.py), or every qubit.

**The window.** window.c draws a random order of the qubits and reduces a basis of ker H_X (kind
Z) to the reduced echelon form whose pivots come first in that order; each row is a codeword, and
each row with a nonzero logical label is a logical. A logical whose support meets the pivots in
one position is a row of that iteration. It gives upper bounds only: the lightest logical found
in its time, with its witness, which `window` checks. Seeds are given, so a run is repeatable up
to the number of iterations the time allows.
"""

from __future__ import annotations

import atexit
import functools
import hashlib
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qec-bb"))
sys.path.insert(0, str(HERE.parent / "qec-distance"))

import bb  # noqa: E402
import distance  # noqa: E402

SEARCH_C = HERE / "search_parts.c"
WINDOW_C = HERE / "window.c"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@functools.cache
def binary(source: str) -> tuple[str, str]:
    """`source` compiled with the system's cc into a temporary directory (removed when the
    process exits), once per process; and the compiler's version line."""
    directory = Path(tempfile.mkdtemp(prefix="qec-parts-"))
    atexit.register(shutil.rmtree, directory, True)
    out = directory / Path(source).stem
    subprocess.run(["cc", "-O2", "-o", str(out), source], check=True, capture_output=True)
    version = subprocess.run(["cc", "--version"], capture_output=True, text=True).stdout
    return str(out), version.splitlines()[0] if version else "cc"


def _code(A, B, ell: int, m: int, kind: str):
    """The checks (as bitmask rows) and the logical labels of each qubit, as search.c reads them,
    checked against bb.k_linalg."""
    if kind not in distance.KINDS:
        raise ValueError(kind)
    n = 2 * ell * m
    hx, hz = distance._bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    labels = distance._logicals_bits(stabilizers, checks, n)
    k = bb.k_linalg(A, B, ell, m)
    if len(labels) != k:
        raise RuntimeError(f"{len(labels)} logicals found, but k = {k}")
    if not labels or len(labels) > 128 or n > 2048 or len(checks) > 1024:
        raise ValueError("no logicals, or beyond the C programs' limits")
    rows = []
    for row in checks:
        support = [t for t in range(n) if row >> t & 1]
        rows.append(" ".join(map(str, [len(support), *support])))
    marks = []
    for t in range(n):
        x = sum((v >> t & 1) << j for j, v in enumerate(labels))
        marks.append(f"{x & (2**64 - 1):x} {x >> 64:x}")
    return n, len(checks), k, rows, marks


def _run(argv: list[str], text: str, limit: float):
    """Run a C program with `text` on stdin for at most `limit` seconds: (stdout, finished)."""
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)  # fmt: skip
    try:
        stdout, stderr = proc.communicate(text, timeout=max(limit, 0.001))
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, _ = proc.communicate()
        return stdout, False
    if proc.returncode:
        raise RuntimeError(f"{argv[0]} failed: {stderr.strip()}")
    return stdout, True


def _finds(stdout: str) -> list[list[int]]:
    out = []
    for words in map(str.split, stdout.splitlines()):
        if words[:1] == ["best"] and len(words) >= 2 and len(words) == int(words[1]) + 2:
            out.append([int(q) for q in words[2:]])
    return out


def search(A, B, ell: int, m: int, kind: str = "Z", anchors=None, first: int = 2,
           last: int = distance.SEARCH_BOUND, parts: int = 4, depth: int = 6, workers: int = 4,
           time_limit: float = 3600.0, on_pass=None) -> dict:  # fmt: skip
    """The least weight of a logical of the given kind, by passes b = first, ..., last of the
    split search (module docstring), each pass as `parts` processes, at most `workers` at once.
    `on_pass(entry)` is called after each finished pass with its record (bound, found, the
    least weight found or None, its witness, its wall-clock seconds, and each part's nodes
    and seconds).

    Returns status ("complete": a pass found a logical, and d is exact; "bound": the passes ran
    to `last` without a find, so d >= last; "timelimit"); d; lower (d, or the largest bound of a
    finished pass without a find, or None); upper and witness (verified, or an error is raised);
    passes; and the settings."""
    if anchors is None:
        starts = list(range(2 * ell * m))
    else:
        starts = [int(a) for a in anchors]
    n, r, k, rows, marks = _code(A, B, ell, m, kind)
    exe, compiler = binary(str(SEARCH_C))
    start = time.time()
    out = {"kind": kind, "l": ell, "m": m, "n": n, "k": k, "first": first, "last": last,
           "parts": parts, "depth": depth, "workers": workers,
           "anchors": "all" if anchors is None else starts, "time_limit": time_limit,
           "compiler": compiler, "search_parts_c_sha256": sha256(SEARCH_C)}  # fmt: skip
    passes, lower, status, witness = [], None, "bound", None
    for b in range(first, last + 1):
        text = "\n".join([f"{n} {r} {k} {b} {b} {len(starts)}", " ".join(map(str, starts)),
                          *rows, *marks]) + "\n"  # fmt: skip

        t_pass = time.time()

        def part(p, b=b, text=text):
            t0 = time.time()
            stdout, done = _run([exe, str(depth), str(parts), str(p)], text,
                                time_limit - (time.time() - start))  # fmt: skip
            nodes = None
            for words in map(str.split, stdout.splitlines()):
                if words[:1] == ["done"] and len(words) == 2:
                    nodes = int(words[1])
            if done and nodes is None:
                raise RuntimeError("search_parts.c ended without finishing")
            finds = _finds(stdout)
            return {"part": p, "finished": done, "nodes": nodes,
                    "seconds": round(time.time() - t0, 3),
                    "least": len(finds[-1]) if finds else None,
                    "witness": finds[-1] if finds else None}  # fmt: skip

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(part, range(parts)))
        if not all(x["finished"] for x in results):
            status = "timelimit"
            break
        found = [x for x in results if x["witness"]]
        best = min(found, key=lambda x: x["least"]) if found else None
        if best:
            check = distance.verify_witness(A, B, ell, m, kind, best["witness"])
            if not check["logical"] or check["weight"] != best["least"] or best["least"] >= b:
                raise RuntimeError(f"part {best['part']} of pass {b} gave a bad witness")
            witness = best["witness"]
        entry = {"bound": b, "found": bool(best), "least": best["least"] if best else None,
                 "witness": witness if best else None, "seconds": round(time.time() - t_pass, 3),
                 "parts": [{key: x[key] for key in ("part", "nodes", "seconds", "least")}
                           for x in results]}  # fmt: skip
        passes.append(entry)
        if on_pass:
            on_pass(entry)
        if best:
            status = "complete"
            break
        lower = b
    d = len(witness) if status == "complete" else None
    return {**out, "status": status, "d": d, "lower": d if d is not None else lower,
            "upper": d, "witness": witness, "passes": passes,
            "seconds": round(time.time() - start, 3)}  # fmt: skip


def window(A, B, ell: int, m: int, kind: str = "Z", seeds=(0,), seconds: float = 60.0,
           workers: int = 4) -> dict:  # fmt: skip
    """The lightest logical of the given kind found by window.c in `seconds` of wall clock for
    each seed (in parallel, at most `workers` at once): an upper bound, with its witness checked
    by distance.verify_witness. Returns upper, witness, and for each seed its least weight,
    iterations and the weights it found in turn."""
    n, r, k, rows, marks = _code(A, B, ell, m, kind)
    exe, compiler = binary(str(WINDOW_C))
    lm = ell * m

    def one(seed):
        text = "\n".join([f"{n} {r} {k} {int(seed)} {float(seconds)}", *rows, *marks]) + "\n"
        stdout, done = _run([exe], text, seconds + 600)
        if not done:
            raise RuntimeError("window.c did not stop")
        dim = iterations = None
        for words in map(str.split, stdout.splitlines()):
            if words[:1] == ["dim"]:
                dim = int(words[1])
            elif words[:1] == ["done"]:
                iterations = int(words[1])
        if dim != lm + k // 2 or iterations is None:
            raise RuntimeError(f"window.c: kernel dimension {dim}, expected {lm + k // 2}")
        finds = _finds(stdout)
        for f in finds:
            check = distance.verify_witness(A, B, ell, m, kind, f)
            if not check["logical"]:
                raise RuntimeError(f"window.c seed {seed} gave a bad witness")
        return {"seed": int(seed), "iterations": iterations,
                "weights": [len(f) for f in finds],
                "least": len(finds[-1]) if finds else None,
                "witness": finds[-1] if finds else None}  # fmt: skip

    with ThreadPoolExecutor(max_workers=workers) as pool:
        runs = list(pool.map(one, seeds))
    best = min((x for x in runs if x["witness"]), key=lambda x: x["least"], default=None)
    return {"kind": kind, "l": ell, "m": m, "n": n, "k": k, "seconds": seconds,
            "upper": best["least"] if best else None, "witness": best["witness"] if best else None,
            "runs": [{key: x[key] for key in ("seed", "iterations", "weights", "least")}
                     for x in runs],
            "compiler": compiler, "window_c_sha256": sha256(WINDOW_C)}  # fmt: skip
