"""
Step 1: the dilation ratio u = f(x^6, y^6)/f(x, y) of rule 4850 at 37, exactly, in the group ring.

Checks (all exact):
  * mul agrees with a direct cyclic convolution on random elements;
  * f^29127 = 1 + JJ (the dossier's identity) and f^9709 != 1 + JJ;
  * u := f^511 + JJ equals sigma_6(f) * f^{-1} (f^{-1} = f^(2^18 - 2) on the nontrivial part);
  * u^57 = 1 exactly (ninth-power confinement), u^19 != 1, u^3 != 1;
  * eigenvalues: u(zeta^c) = lambda(c)^511 = lambda(6c)/lambda(c) at a sample of characters,
    computed independently in F(2^36) (census37's field), and every nonzero lambda has order | 29127
    (eigen.odd_part on 4850 gives 29127).
Then: weights, supports, the GL2(Z/37) stabilisers, invariance under scalar subgroups.
Writes u4850.json.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/lattice-lab/examples/linear-atlas-3")
import eigen as atlas_eigen  # noqa: E402

rng = np.random.default_rng(1)
M = gr.M


def direct_mul(a, b):
    out = np.zeros((M, M), dtype=np.int64)
    for i, j in zip(*np.nonzero(a)):
        out += np.roll(np.roll(b, i, axis=0), j, axis=1)
    return (out & 1).astype(np.uint8)


def summary(name, a, out, stab=True):
    rec = {"weight": gr.weight(a)}
    rec["trivial_component"] = int(a.sum()) & 1
    for n in (2, 3, 4, 6, 8, 10, 16, 36):  # scalar invariance
        rec[f"dilation_{n}_invariant"] = gr.invariant_under(a, n)
    if stab:
        t0 = time.time()
        S = gr.stabiliser(a)
        rec["stabiliser_order"] = int(len(S))
        rec["stabiliser"] = [list(map(int, g)) for g in S][:64]
        rec["stab_time"] = round(time.time() - t0, 2)
    out[name] = rec
    print(name, {k: v for k, v in rec.items() if k != "stabiliser"})
    return rec


def main():
    out = {}
    for _ in range(5):
        a = (rng.random((M, M)) < 0.3).astype(np.uint8)
        b = (rng.random((M, M)) < 0.3).astype(np.uint8)
        assert np.array_equal(gr.mul(a, b), direct_mul(a, b))
    print("mul agrees with direct convolution")

    f = gr.rule_array(4850)
    assert gr.weight(f) == 40
    assert np.array_equal(gr.power(f, 29127), gr.ONE ^ gr.JJ)
    assert not np.array_equal(gr.power(f, 9709), gr.ONE ^ gr.JJ)
    print("f^29127 = 1 + JJ, f^9709 != 1 + JJ")

    u = gr.u_of(f)
    finv = gr.inverse_nontrivial(f)
    assert np.array_equal(gr.mul(f, finv), gr.ONE ^ gr.JJ)  # f*finv = 1 on nontrivial, 0 at trivial
    u2 = gr.mul(gr.dilate(f, 6), finv)
    # sigma6(f)*finv has trivial component 0*1 = 0 -> add JJ
    u2 = u2 ^ gr.JJ if (int(u2.sum()) & 1) == 0 else u2
    assert np.array_equal(u, u2), "u != sigma6(f)/f"
    print("u = f^511 + JJ = sigma_6(f) f^-1 (trivial component 1)")

    for e, should_be_one in ((57, True), (19, False), (3, False), (171, True), (513, True)):
        is_one = np.array_equal(gr.power(u, e), gr.ONE)
        assert is_one == should_be_one, e
    print("u^57 = 1, u^19 != 1, u^3 != 1")

    # independent eigenvalue check
    F = gr._field()
    for (j, k) in [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13), (3, 17), (5, 29)]:
        lam = gr.eig(f, j, k)
        lam6 = gr.eig(f, 6 * j, 6 * k)
        mu = gr.eig(u, j, k)
        assert mu == F.pow(lam, 511), (j, k)
        assert F.mul(mu, lam) == lam6, (j, k)
        assert F.pow(mu, 57) == 1
    print("eigenvalues of u = lambda^511 = lambda(6c)/lambda(c) in F(2^36), and in mu_57 (sample)")
    op = atlas_eigen.odd_part(frozenset(gr.census.rule(4850, 4)), 37)
    print("eigen.odd_part(4850, 37) =", op)
    out["odd_part_4850"] = op
    assert op == 29127

    u3, u19 = gr.power(u, 3), gr.power(u, 19)
    u9 = gr.power(u, 9)
    for name, a in (("f", f), ("u", u), ("u^3", u3), ("u^9", u9), ("u^19", u19)):
        summary(name, a, out)
    np.save(os.path.join(gr.HERE, "u4850.npy"), np.stack([f, u, u3, u19]))
    out["u_support"] = gr.pts(u)
    out["u19_support"] = gr.pts(u19)
    out["u3_support"] = gr.pts(u3)
    with open(os.path.join(gr.HERE, "u4850.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
