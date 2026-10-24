"""
Spot-check C5 (docs/census-stage3b-spotcheck-plan.md): a code (A, B on l x m) run through
DistQLDPC (github.com/guluchen/DistQLDPC), an implementation written apart from this project.

`export` writes the four files DistQLDPC reads (its README):
- Hx: the X checks (rows of H_X);
- Hz: the Z checks (rows of H_Z);
- Gx: the Z-type logicals, a basis of ker(Hx) / row(Hz);
- Gz: the X-type logicals, a basis of ker(Hz) / row(Hx).
The bases come from distance._logicals_bits, and their sizes must both be bb.k_linalg.

`run` calls its binary with an engine (maxsat, its default, or cc) and a wall-clock limit. It
reads back the last lower bound ("c d_lb:"), the exact distance ("c d  :") when it finishes, and
the final line "o N", which is the distance or the best upper bound found before the limit.
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


def run(A, B, ell: int, m: int, engine: str = "maxsat", limit: int = 7200) -> dict:
    with tempfile.TemporaryDirectory(prefix="spotcheck-distq-") as d:
        k = export(A, B, ell, m, Path(d))
        t0 = time.time()
        proc = subprocess.run([str(BINARY), f"-engine={engine}", f"-cpu-lim={int(limit)}",
                               f"{d}/CODE"], capture_output=True, text=True,
                              timeout=limit + 600, cwd=str(DISTQ))  # fmt: skip
        out = proc.stdout + proc.stderr
    lbs = [int(x) for x in re.findall(r"c d_lb:\s*(\d+)", out)]
    exact = re.findall(r"c d  :\s*(\d+)", out)
    final = re.findall(r"^o (\d+)", out, re.M)
    return {"engine": engine, "k": k, "lower": max(lbs) if lbs else None,
            "d": int(exact[-1]) if exact else None,
            "upper": int(final[-1]) if final else None,
            "seconds": round(time.time() - t0, 1), "returncode": proc.returncode,
            "tail": out[-600:]}  # fmt: skip
