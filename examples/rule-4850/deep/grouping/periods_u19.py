"""
Step 1b: in the rotated frame, u^19(10491524) = f^9709 (the 27th-power residue symbol of 4850 rotated,
equal to those of 20982139 and 178279803) as a bilinear form in sextic Gauss-period elements:
    u^19 = sum_{A,B} c_AB P_A(x) P_B(y),   P_A = sum_{i in A} x^i,
A, B running over {0} and the six cosets 2^c H of H = <27> = <2^6> (order 6) in (Z/37)*.
Checks that the coefficients are constant on the blocks A x B, prints c, and checks the same
decomposition fails for 4850's own frame and for a random confined rule.  Writes periods_u19.json.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

M = 37
H = sorted({pow(27, e, M) for e in range(6)})
orbits = [[0]] + [sorted({pow(2, c, M) * h % M for h in H}) for c in range(6)]
assert sorted(sum(orbits, [])) == list(range(M))


def block_form(a):
    c = np.zeros((7, 7), dtype=int)
    for A, oa in enumerate(orbits):
        for B, ob in enumerate(orbits):
            blk = a[np.ix_(oa, ob)]
            if blk.min() != blk.max():
                return None
            c[A, B] = int(blk[0, 0])
    return c


out = {"H": H, "orbits": orbits}
for n in (10491524, 20982139, 178279803, 4850, 1431278):
    u19 = gr.power(gr.u_of(gr.rule_array(n)), 19)
    c = block_form(u19)
    out[str(n)] = None if c is None else c.tolist()
    print(n, "block-constant on sextic-period blocks:", c is not None)
    if c is not None:
        print(c)
json.dump(out, open(os.path.join(gr.HERE, "periods_u19.json"), "w"), indent=1)
