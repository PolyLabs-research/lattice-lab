"""Step 11: what the partial-Frobenius symmetry would explain, if it were explained.

Setting: a symmetric rule f at 37 whose 27-adic residue R_f is invariant under P = Rot^-1 diag(1, 27) Rot
(frame B of 4850; for 10491524 itself P = diag(1, 27)).  Then
  (i)  [lemma] R_f^63 = 1: every eigenvalue is a cube;
  (ii) the digit1 function (log/3 mod 3) of f is a P-invariant, D4-symmetric, scaling-odd function;
       here we compute the space of such functions on the 11 classes (linear algebra mod 3), and its
       subspace vanishing on the line-explained classes of 4850 (axis, diagonal, (1,2) in frame A:
       restrictions t^3, t^2 Psi_5^2, t^4 Psi_13, all ninth powers).
If that subspace has dimension 1, then [symmetry] + [the three exact line factorisations] force
cube confinement and leave ninth-power confinement to ONE trit; 4850's value of that trit is 0.
Same computation for 10491524 in its own frame (line-explained classes (0,1), (1,1), (1,3)).
Writes step11_reduction.json.
"""
import json

import numpy as np
import sympy

import tlib
from tlib import M, chi
from step9_partialfrob import CLS, EX, NZ, NZJ, NZK, perm_index, partial

REPS = tlib.CENSUS_REPS


def class_to_char_matrix():
    """E (len(NZ) x 11) over Z/3: digit at character = chi(u) * digit at its class representative."""
    E = np.zeros((len(NZ), 11), dtype=np.int64)
    sign = np.where(EX[NZJ, NZK] % 2 == 0, 1, 2)  # chi(u) = (-1)^ind u, as 1 or 2 mod 3
    E[np.arange(len(NZ)), CLS[NZJ, NZK]] = sign
    return E


def nullspace_mod3(A):
    A = sympy.Matrix(A.tolist())
    # row reduce over GF(3)
    from sympy.polys.matrices import DomainMatrix
    from sympy import GF
    dm = DomainMatrix.from_Matrix(A).convert_to(GF(3))
    ns = dm.nullspace()
    return [[int(x) % 3 for x in row] for row in ns.to_Matrix().tolist()] if ns.shape[0] else []


def analyse(P, fixed_zero_classes):
    E = class_to_char_matrix()
    p = perm_index(P)
    C = (E[p] - E) % 3                      # invariance: C x = 0
    rows = [C]
    # class (1,6) is forced 0
    e6 = np.zeros((1, 11), dtype=np.int64); e6[0, 6] = 1
    rows.append(e6)
    A = np.concatenate(rows) % 3
    sym = nullspace_mod3(A)
    rows2 = rows + [np.eye(11, dtype=np.int64)[[c]] for c in fixed_zero_classes]
    A2 = np.concatenate(rows2) % 3
    free = nullspace_mod3(A2)
    # the base space without the symmetry
    base = nullspace_mod3(e6)
    return dict(dim_symmetric_odd=len(base), dim_P_invariant=len(sym), P_invariant_basis=sym,
                dim_after_line_classes=len(free), remaining_basis=free,
                remaining_classes=[[REPS[i] for i in range(11) if v[i]] for v in free])


if __name__ == "__main__":
    out = {}
    st1 = json.load(open("step1_digits.json"))
    for name, P, fixed in (("4850 (frame A; P in frame B)", partial(6, "B"), [0, 1, 2]),
                           ("10491524 (own frame; P = diag(1,27))", partial(6, "A"), [0, 1, 3])):
        res = analyse(P, fixed)
        out[name] = res
        print(name)
        print("   dim of symmetric odd digit functions:", res["dim_symmetric_odd"],
              "| P-invariant:", res["dim_P_invariant"],
              "| P-invariant and zero on the line-explained classes", [REPS[c] for c in fixed], ":",
              res["dim_after_line_classes"], "spanned by", res["remaining_basis"], "on classes", res["remaining_classes"])
    # 4850's and 10491524's actual digit vectors in these spaces
    for n, key in ((4850, "4850 (frame A; P in frame B)"), (10491524, "10491524 (own frame; P = diag(1,27))")):
        d2 = np.array(st1[str(n)]["class_digit2"])
        basis = out[key]["P_invariant_basis"]
        A = sympy.Matrix(basis).T
        # solve A y = d2 mod 3 by brute force (dim small)
        import itertools
        sol = [y for y in itertools.product(range(3), repeat=len(basis))
               if np.array_equal((np.array(basis).T @ np.array(y)) % 3, d2 % 3)]
        out[key]["digit2_coordinates"] = sol
        rem = out[key]["remaining_basis"][0] if out[key]["remaining_basis"] else None
        print(n, "digit2 =", d2.tolist(), "coordinates in the P-invariant basis:", sol)
        if rem is not None:
            idx = [i for i in range(11) if rem[i]]
            print("   digit2 on the free orbit", [REPS[i] for i in idx], ":", [int(d2[i]) for i in idx],
                  "(digit1 there is 0: the ninth-power trit)")
    json.dump(out, open("step11_reduction.json", "w"), indent=1, default=str)
