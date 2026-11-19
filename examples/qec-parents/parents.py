"""
Planar parents of the census's codes: the cells, each class's shortest planar forms, and the
keys that say when two classes share one.

**Forms.** A bivariate bicycle code (A, B) lives on a group G = Z_l x Z_m. A planar form of it is
a homomorphism phi: Z^2 -> G with two integer triangles that phi carries onto A and B, each up to
a translation (multiplying A or B by a monomial is an equivalence). The planar pair is the same
code on the infinite plane, and the torus code is that pair wrapped by phi's kernel. The forms
run over every phi, not only the torus's own coordinates, because 2 x 93, 3 x 62 and 6 x 31 are
one group and their codes are the same codes. A form's range is the larger bounding-box side of
its two triangles; forms.c finds the least range and every form attaining it (`shortest_forms`).

**Keys.** `key` puts a planar pair in a normal form under translation of each triangle, the 8
signed permutations of the two coordinates (applied to both triangles) and the swap of A and B.
Two classes share a parent when their sets of shortest-form keys meet.

**Cells.** `cells` reads the census (stages 3a, 3b, 3c and 4): a cell is a torus and a k, its d
the best exact distance of a connected class, and its frontier classes the connected classes
with a completed exact run at that d.
"""

from __future__ import annotations

import glob
import json
import subprocess
import tempfile
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
EX = HERE.parent
FORMS_C = HERE / "forms.c"
_TMP = []


@cache
def _binary() -> str:
    tmp = tempfile.TemporaryDirectory(prefix="qec-parents-")
    _TMP.append(tmp)  # removed when the process exits
    binary = Path(tmp.name) / "forms"
    subprocess.run(["cc", "-O2", "-o", str(binary), str(FORMS_C)], check=True)
    return str(binary)


def _normal(tri) -> tuple:
    """A triangle's points translated so the least x and the least y are 0, sorted."""
    x0, y0 = min(p[0] for p in tri), min(p[1] for p in tri)
    return tuple(sorted((p[0] - x0, p[1] - y0) for p in tri))


SIGNED = [(a, b, c, d) for a, b, c, d in
          [(1, 0, 0, 1), (-1, 0, 0, 1), (1, 0, 0, -1), (-1, 0, 0, -1),
           (0, 1, 1, 0), (0, -1, 1, 0), (0, 1, -1, 0), (0, -1, -1, 0)]]  # fmt: skip


def key(ta, tb) -> tuple:
    """The normal form of the planar pair (ta, tb), each a triangle of three points."""
    best = None
    for a, b, c, d in SIGNED:
        na = _normal([(a * x + b * y, c * x + d * y) for x, y in ta])
        nb = _normal([(a * x + b * y, c * x + d * y) for x, y in tb])
        for cand in ((na, nb), (nb, na)):
            if best is None or cand < best:
                best = cand
    return best


def key_text(k) -> str:
    """A key as text: the two triangles' points, 'x,y x,y x,y|x,y x,y x,y'."""
    return "|".join(" ".join(f"{x},{y}" for x, y in tri) for tri in k)


def key_parse(text: str) -> tuple:
    return tuple(tuple(tuple(int(v) for v in p.split(",")) for p in tri.split(" "))
                 for tri in text.split("|"))  # fmt: skip


def shortest_forms(codes) -> list[tuple[int, list[str]]]:
    """For each (l, m, A, B): (least range, the sorted key texts of every shortest form). For a
    connected code every form's phi is onto; a code that is not connected gets the forms of one
    component, which are not parents of the whole code (see `connected`)."""
    lines = []
    for ell, m, A, B in codes:
        flat = [v for P in (A, B) for mon in P for v in mon]
        lines.append(" ".join(str(v) for v in (ell, m, *flat)))
    proc = subprocess.run([_binary()], input="\n".join(lines) + "\n", capture_output=True,
                          text=True, check=True)  # fmt: skip
    rows = proc.stdout.split("\n")
    out, i = [], 0
    for _ in codes:
        tag, rng, count = rows[i].split()
        assert tag == "R"
        raw = set(rows[i + 1 : i + 1 + int(count)])
        i += 1 + int(count)
        keys = set()
        for line in raw:
            v = [int(t) for t in line.split()]
            keys.add(
                key(((0, 0), (v[0], v[1]), (v[2], v[3])), ((0, 0), (v[4], v[5]), (v[6], v[7])))
            )
        out.append((int(rng), sorted(key_text(k) for k in keys)))
    return out


def connected(ell: int, m: int, A, B) -> bool:
    """True when the differences of A's monomials and of B's generate Z_l x Z_m: the code's
    Tanner graph is connected, and every phi that carries a form onto it is onto."""
    gens = [((P[i][0] - P[0][0]) % ell, (P[i][1] - P[0][1]) % m) for P in (A, B) for i in (1, 2)]
    seen, todo = {(0, 0)}, [(0, 0)]
    while todo:
        u = todo.pop()
        for g in gens:
            v = ((u[0] + g[0]) % ell, (u[1] + g[1]) % m)
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == ell * m


def reduce_form(k, g1, g2, ell: int, m: int):
    """The torus code a planar pair gives under phi(x) = g1, phi(y) = g2."""
    return tuple([((x * g1[0] + y * g2[0]) % ell, (x * g1[1] + y * g2[1]) % m) for x, y in tri]
                 for tri in k)  # fmt: skip


# ------------------------------------------------------------------------------ the census


def _poly(P) -> tuple:
    return tuple(tuple(t) for t in P)


def census_rows():
    """Every class row of the census with what this study needs: (stage, l, m, n, k, connected,
    d or None, A, B, best), d the class's exact distance when its run completed and best the
    cell's best d as the census reports it (stage 3a: computed here)."""
    for p in sorted(glob.glob(str(EX / "qec-census-3" / "data" / "*.jsonl"))):
        lines = [json.loads(x) for x in open(p) if x.strip()]
        head, best = lines[0], {}
        for r in lines[1:]:
            if r.get("connected") and r["status"] == "complete":
                best[r["k"]] = max(best.get(r["k"], 0), r["d"])
        for r in lines[1:]:
            d = r["d"] if r["status"] == "complete" else None
            yield ("3a", head["l"], head["m"], head["n"], r["k"], bool(r.get("connected")), d,
                   _poly(r["A"]), _poly(r["B"]), best.get(r["k"]))  # fmt: skip
    for folder, stage in (("qec-census-3b", "3b"), ("qec-census-3c", "3c"), ("qec-census-4", "4")):
        for x in open(EX / folder / "records.jsonl"):
            r = json.loads(x)
            if r.get("job") != "torus" or "error" in r or not r.get("classes"):
                continue
            best = {int(ks): v["d"] for ks, v in r["best"]["connected"].items()}
            for y in r["rows"]:
                exact = y.get("exact") or {}
                d = exact["d"] if exact.get("status") == "complete" else None
                yield (stage, r["l"], r["m"], r["n"], y["k"], bool(y["connected"]), d,
                       _poly(y["A"]), _poly(y["B"]), best.get(y["k"]))  # fmt: skip


def cells(stages=("3a", "3b", "3c", "4")) -> dict:
    """{(stage, l, m, k): {"n", "d", "frontier": [(A, B)], "others": [(A, B)]}}: the frontier
    classes are the connected ones with a completed exact run at the cell's best d, the others
    the cell's remaining connected classes. A cell with no frontier class is left out."""
    out: dict = {}
    for stage, ell, m, n, k, connected, d, A, B, best in census_rows():
        if stage not in stages or not connected or best is None:
            continue
        cell = out.setdefault((stage, ell, m, k), {"n": n, "d": best, "frontier": [], "others": []})
        cell["frontier" if d == best else "others"].append((A, B))
    return {c: v for c, v in out.items() if v["frontier"]}


def score(cell_key, cell) -> float:
    return cell_key[3] * cell["d"] ** 2 / cell["n"]


def record_cells(cs: dict, stage: str) -> list:
    """For each n of the stage, the cells with the highest k d^2 / n at that n."""
    by_n: dict = {}
    for c, v in cs.items():
        if c[0] == stage:
            by_n.setdefault(v["n"], []).append((score(c, v), c))
    out = []
    for n in sorted(by_n):
        top = max(s for s, _ in by_n[n])
        out += sorted(c for s, c in by_n[n] if s == top)
    return out
