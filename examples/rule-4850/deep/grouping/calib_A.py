"""
Step 5c: the null rate of the (A)-symmetry on a mu_3-valued class function.

For every rule of the radius-5 family (2,097,151 rules) take its cubic residue symbol
lambda^87381 (log mod 3, from census.py's class logs mod 27) -- a mu_3-valued symmetric class
function, i.e. the same kind of object as the residue symbol R27 of a ninth-confined rule -- and
test whether it is fixed by g1 (4850's frame) or by D = diag(1, 27) (rotated frame), with the
bookkeeping of census_A.py.  Restricted to the rules with no zero eigenvalue and that are NOT
cube-confined (so the symbol is a genuinely nontrivial random-looking function), this estimates
P(A | mu_3-valued), the factor by which (A) multiplies the null probability of 4850's
ninth-confinement.  Writes calib_A.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402
import census_A as CA  # noqa: E402

C = gr.census


def main():
    logs = C.class_logs(5)
    unit = ~(logs == 255).any(axis=0)
    cube = C.confined(logs, 3)
    sym = np.where(logs == 255, 255, (logs % 3) * 9).astype(np.uint8)  # mu_3-valued symbol, as logs
    sel = unit & ~cube
    sel[0] = False
    out = {"rules_used": int(sel.sum())}
    for name, G in (("g1", ((14, 24), (24, 14))), ("D", ((1, 0), (0, 27)))):
        CA.G1 = G
        A = CA.A_from_logs(sym)
        k = int((A & sel).sum())
        out[name] = {"count": k, "rate": k / int(sel.sum())}
        print(name, k, "of", int(sel.sum()), "rate %.3e (3^-6 = %.3e)" % (k / int(sel.sum()), 3.0**-6))
    with open(os.path.join(gr.HERE, "calib_A.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
