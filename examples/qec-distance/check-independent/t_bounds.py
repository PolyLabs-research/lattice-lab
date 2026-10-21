"""Builder's bounds when SCIP stops at a limit: lower <= d <= upper, witness valid (toric, d known)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
T = [(0, 0), (1, 0)], [(0, 0), (0, 1)]
for ell, m in [(13, 13), (11, 14), (15, 15)]:
    d = min(ell, m)
    for lim in (1, 3, 8, 20):
        r = D.distance_ilp(*T, ell, m, "Z", time_limit=lim)
        w = D.verify_witness(*T, ell, m, "Z", r["witness"])["logical"] if r["witness"] else None
        ok = (r["lower"] is None or r["lower"] <= d) and (r["upper"] is None or r["upper"] >= d)
        print(ell, m, "lim", lim, r["status"], "lower", r["lower"], "dual", round(r["dual_bound"], 6), "upper", r["upper"], "wit", w, "OK" if ok else "BAD", flush=True)
