"""
Spot-check C5 (docs/census-stage3b-spotcheck-plan.md): a code (A, B on l x m) run through
DistQLDPC (github.com/guluchen/DistQLDPC), an implementation written apart from this project.

`export` writes the four files DistQLDPC reads (its README):
- Hx: the X checks (rows of H_X);
- Hz: the Z checks (rows of H_Z);
- Gx: the Z-type logicals, a basis of ker(Hx) / row(Hz);
- Gz: the X-type logicals, a basis of ker(Hz) / row(Hx).
The bases come from distance._logicals_bits, and their sizes must both be bb.k_linalg.

`run` calls its binary with an engine (maxsat, its default, or cc) and a limit (-cpu-lim). It
reads back the last lower and upper bounds ("c d_lb: N", "c d_ub: N"; "-" means none), and the
exact distance ("c d  : N", or UNKNOWN when it stops first, with exit code 1). When the cc engine
stops without an answer it withdraws its earlier bound lines ("withdrawn" in its status line),
and then both bounds are None. Any other exit, or output without the "c d  :" line, raises.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))
sys.path.insert(0, str(ROOT / "examples" / "qec-distance"))

import bb  # noqa: E402
import distance  # noqa: E402

DISTQ = Path(os.environ.get("DISTQLDPC",
                            "/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/"
                            "scratchpad/lit/dq"))  # fmt: skip
BINARY = DISTQ / "bin" / "distqldpc"


def _rows(bits: list[int], n: int) -> str:
    return "\n".join(" ".join("1" if b >> q & 1 else "0" for q in range(n)) for b in bits) + "\n"


def export(A, B, ell: int, m: int, directory: Path, name: str = "CODE") -> int:
    n = 2 * ell * m
    hx, hz = distance._bit_rows(A, B, ell, m)
    gx = distance._logicals_bits(hx, hz, n)  # Z-type: ker(Hx) / row(Hz)
    gz = distance._logicals_bits(hz, hx, n)  # X-type: ker(Hz) / row(Hx)
    k = bb.k_linalg(A, B, ell, m)
    if len(gx) != k or len(gz) != k:
        raise RuntimeError(f"logical bases of sizes {len(gx)}, {len(gz)}, but k = {k}")
    directory = Path(directory)
    for tag, bits in (("Hx", hx), ("Hz", hz), ("Gx", gx), ("Gz", gz)):
        (directory / f"{name}_{tag}.txt").write_text(_rows(bits, n))
    return k


def _last(pattern: str, out: str) -> int | None:
    found = re.findall(pattern, out)
    return int(found[-1]) if found and found[-1] != "-" else None


def run(A, B, ell: int, m: int, engine: str = "maxsat", limit: int = 7200) -> dict:
    with tempfile.TemporaryDirectory(prefix="spotcheck-distq-") as d:
        k = export(A, B, ell, m, Path(d))
        t0 = time.time()
        try:
            proc = subprocess.run([str(BINARY), f"-engine={engine}", f"-cpu-lim={int(limit)}",
                                   f"{d}/CODE"], capture_output=True, text=True,
                                  timeout=limit + 600, cwd=str(DISTQ))  # fmt: skip
        except subprocess.TimeoutExpired:
            return {"engine": engine, "k": k, "lower": None, "d": None, "upper": None,
                    "seconds": round(time.time() - t0, 1), "returncode": None,
                    "tail": "killed: no answer within the limit + 600 s"}  # fmt: skip
        out = proc.stdout + proc.stderr
    exact = re.findall(r"^c d  :\s*(\S+)", out, re.M)
    if proc.returncode not in (0, 1) or not exact:
        raise RuntimeError(f"distqldpc exited {proc.returncode}: {out[-600:]}")
    withdrawn = "withdrawn" in out
    d_exact = int(exact[-1]) if exact[-1].isdigit() else None
    if proc.returncode == 0 and d_exact is None:
        raise RuntimeError(f"distqldpc exited 0 without a distance: {out[-600:]}")
    return {"engine": engine, "k": k,
            "lower": None if withdrawn else _last(r"c d_lb:\s*(\S+)", out),
            "d": d_exact,
            "upper": None if withdrawn else _last(r"c d_ub:\s*(\S+)", out),
            "withdrawn": withdrawn, "seconds": round(time.time() - t0, 1),
            "returncode": proc.returncode, "tail": out[-600:]}  # fmt: skip
