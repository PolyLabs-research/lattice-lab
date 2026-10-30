"""
Census stage 4b's probabilistic distances: information-set decoding (isd.c, Lee-Brickell p = 2)
with a fixed number of iterations, and the model that turns "no light codeword found in N
iterations" into a miss probability.

**The method.** Each iteration of isd.c takes a uniformly random order of the qubits and the
information set I it gives: the pivots of a Gauss-Jordan basis of ker H_X, taken in that order
(|I| = K = dim ker H_X). Every codeword c of ker H_X is the sum of the basis rows at the pivots in
its support, so c is seen (as a row, or a sum of two rows) exactly when |supp(c) ∩ I| is 1 or 2.
isd.c weighs every row and every sum of two rows whose logical label is nonzero (a nontrivial
codeword: a Z-logical).

**The model.** If I were a uniformly random K-subset of the n qubits, a fixed codeword of weight w
would be seen in one iteration with probability

    p(n, K, w) = [w C(n-w, K-1) + C(w, 2) C(n-w, K-2)] / C(n, K),

and missed in N independent iterations with probability (1 - p)^N <= exp(-N p). `budget` gives the
N for a miss probability eps at every weight up to `target`: p is smallest at w = target.
- Only one codeword of each weight is assumed (the conservative case), and translates, which
  are logicals of the same weight, are not counted.
- **The assumption is the uniform information set.** isd.c's I is the greedy basis of a uniformly
  random order, not a uniform K-subset. `calibrate` measures, on codes of known d, how often a
  known minimum-weight logical meets I in 1 or 2 positions, against p. The model is used only
  where that calibration shows the measured rate at least p (study.py).

**What a result means.** "No nontrivial codeword of weight <= target in N iterations" says: under
the model, a logical of weight <= target exists with probability at most eps. That is a
probabilistic statement, and is reported as its own tier, never as an exact d. A codeword found
is a checked upper bound, as before.

A fixed iteration budget, rather than wall-clock time, makes a run's outcome the same on any
machine for the same seed.
"""

from __future__ import annotations

import importlib.util
import math
import sys
import time
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ISD_C = HERE / "isd.c"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


parts = _load("qec_open_parts", HERE.parent / "qec-open-distance" / "parts.py")
distance, bb = parts.distance, parts.bb


def p_seen(n: int, K: int, w: int) -> float:
    """The model's probability that one iteration sees a fixed codeword of weight w."""
    total = comb(n, K)
    return (w * comb(n - w, K - 1) + comb(w, 2) * comb(n - w, K - 2)) / total


def budget(n: int, K: int, target: int, eps: float) -> int:
    """Iterations N with exp(-N p) <= eps for every weight 2 <= w <= target."""
    p = min(p_seen(n, K, w) for w in range(2, target + 1))
    return math.ceil(math.log(1 / eps) / p)


def run(A, B, ell: int, m: int, iterations: int, target: int, seed: int = 0,
        watch=None, limit: float = 7 * 86400) -> dict:  # fmt: skip
    """isd.c on the code's Z side: the lightest nontrivial codeword seen (checked), the number of
    iterations with one of weight <= target, and with a watch, its meetings with I."""
    n, r, k, rows, marks = parts._code(A, B, ell, m, "Z")
    exe, compiler = parts.binary(str(ISD_C))
    lines = [f"{n} {r} {k} {int(seed)} {int(iterations)} {int(target)}", *rows, *marks]
    if watch is not None:
        lines.append(f"watch {len(watch)} " + " ".join(map(str, watch)))
    t0 = time.time()
    stdout, done = parts._run([exe], "\n".join(lines) + "\n", limit)
    if not done:
        raise RuntimeError("isd.c did not finish within its wall-clock guard")
    out = {"n": n, "k": k, "iterations": None, "hits": None, "dim": None}
    for words in map(str.split, stdout.splitlines()):
        if words[:1] == ["dim"]:
            out["dim"] = int(words[1])
        elif words[:1] == ["done"]:
            out["iterations"], out["hits"] = int(words[1]), int(words[2])
        elif words[:1] == ["watch"]:
            out["meet1"], out["meet2"] = int(words[1]), int(words[2])
    finds = parts._finds(stdout)
    witness = finds[-1] if finds else None
    if witness is not None:
        check = distance.verify_witness(A, B, ell, m, "Z", witness)
        if not check["logical"]:
            raise RuntimeError("isd.c gave a bad witness")
    if out["dim"] != ell * m + k // 2 or out["iterations"] != iterations:
        raise RuntimeError(f"isd.c: dim {out['dim']}, iterations {out['iterations']}")
    return out | {"upper": len(witness) if witness else None, "witness": witness, "seed": seed,
                  "target": target, "seconds": round(time.time() - t0, 2),
                  "compiler": compiler, "isd_c_sha256": parts.sha256(ISD_C)}  # fmt: skip


def certify(A, B, ell: int, m: int, d: int, eps: float, seed: int = 0) -> dict:
    """The probabilistic claim "no logical of weight < d" (d even, so target d - 2): run the
    budget for eps. 'probable' when nothing of weight <= target is seen; 'lighter' (a checked
    logical below d) otherwise."""
    n = 2 * ell * m
    K = ell * m + bb.k_linalg(A, B, ell, m) // 2
    target = d - 2
    N = budget(n, K, target, eps)
    r = run(A, B, ell, m, N, target, seed)
    status = "lighter" if r["upper"] is not None and r["upper"] <= target else "probable"
    return r | {"status": status, "d": d, "eps": eps, "K": K, "budget": N}


def calibrate(A, B, ell: int, m: int, witness, iterations: int, seed: int = 0) -> dict:
    """The measured rate at which a known minimum-weight logical meets I in 1 or 2 positions,
    against the model's p for its weight."""
    n = 2 * ell * m
    K = ell * m + bb.k_linalg(A, B, ell, m) // 2
    w = len(witness)
    r = run(A, B, ell, m, iterations, w, seed, watch=witness)
    measured = (r["meet1"] + r["meet2"]) / iterations
    return {"n": n, "K": K, "w": w, "iterations": iterations, "meet1": r["meet1"],
            "meet2": r["meet2"], "measured": measured, "model": p_seen(n, K, w),
            "ratio": measured / p_seen(n, K, w), "hits": r["hits"], "upper": r["upper"],
            "seconds": r["seconds"]}  # fmt: skip
