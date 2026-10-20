"""
Step 2b: GF(2)-rank of the 37x37 coefficient matrix of u (and u^19) -- a separable element
A(x) B(y) has rank 1; a product of k one-variable-direction factors along the axes stays low rank.
Baselines: the four rules pilot 7 explained (u = N / N(x^6, y^6), N a product of rule-90 units),
4850 and its family, and random rules.  Writes rank_u.json.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402


def rank2(A):
    A = A.copy().astype(np.uint8)
    r = 0
    for c in range(A.shape[1]):
        piv = next((i for i in range(r, A.shape[0]) if A[i, c]), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(A.shape[0]):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
    return r


out = {}
rules = [4850, 10491524, 20982139, 178279803, 699738, 985232, 1431278, 1968276, 57, 960]
rng = np.random.default_rng(2)
rules += [int(n) for n in rng.integers(1, 1 << 28, 20)]
for n in rules:
    f = gr.rule_array(n)
    u = gr.u_of(f)
    u19 = gr.power(u, 19)
    out[n] = {"rank_u": rank2(u), "rank_u19": rank2(u19), "w_u": gr.weight(u)}
    print(n, out[n])
json.dump(out, open(os.path.join(gr.HERE, "rank_u.json"), "w"), indent=1)
