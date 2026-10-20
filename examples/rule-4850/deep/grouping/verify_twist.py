"""
Step 4g: exact group-ring verification of the partial-twist relations, and their meaning.

R1 = 10491524 (= 4850 rotated by 45 degrees), R2 = 20982139, R3 = 178279803, r = diag(1, 27),
r^i R1 = R1(x, y^(27^i)).  Exponents lifted from partial_twist.py (mod 19) by CRT so that the
mu_27 parts also cancel (a + b + c = 1 mod 3; all mu_27 parts are equal):
    Q2 = R2 / (R1^3  (rR1)^14 (r^2R1)^41)
    Q3 = R3 / (R1^17 (rR1)^17 (r^2R1)^62)       (17 + 17 + 62 = 96 = 0 mod 3? -> chosen below)
Claim: Q^511 = 1 on every character off the two axis lines (Q is F(2^9)-valued there), i.e.
    (Q^511 + 1) (1 + E_ax) = 0,  E_ax = Ex + Ey + JJ the idempotent of the axis lines.
Checked exactly in the group ring and at all 38 line representatives in F(2^36).
Also: the decomposition of the mu_19 log vectors under phi = r (an order-3 operator on the
off-axis lines) into eigencomponents 1, 7, 11 (the cube roots of 1 mod 19).
Writes verify_twist.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
import f18  # noqa: E402

M = 37
LINES = [(1, k) for k in range(M)] + [(0, 1)]


def lift(c19, need_sum_mod3=1):
    """lift a mod-19 exponent vector to mod 513 with sum = need (mod 3)."""
    a, b, c = c19
    for t in range(3):
        cc = c + 19 * t
        if (a + b + cc) % 3 == need_sum_mod3:
            return (a, b, cc)
    raise ValueError


def inv(f):
    v = gr.power(f, 2**18 - 2)
    return v ^ gr.ONE ^ gr.support_idempotent(f)


def main():
    out = {}
    R1, R2, R3 = (gr.rule_array(n) for n in (10491524, 20982139, 178279803))
    r = ((1, 0), (0, 27))
    T = [R1, gr.act(R1, r), gr.act(gr.act(R1, r), r)]
    Ex = np.zeros((M, M), dtype=np.uint8); Ex[:, 0] = 1  # sum_i x^i
    Ey = np.zeros((M, M), dtype=np.uint8); Ey[0, :] = 1
    Eax = Ex ^ Ey ^ gr.JJ
    # sanity of E_ax: eigenvalue 1 exactly on the axis lines
    for jk in LINES:
        assert gr.eig(Eax, *jk) == (1 if jk in ((1, 0), (0, 1)) else 0)
    for name, target, c19 in (("R2", R2, (3, 14, 3)), ("R3", R3, (17, 17, 5))):
        e = lift(c19)
        den = gr.ONE.copy()
        for Ti, ei in zip(T, e):
            den = gr.mul(den, gr.power(Ti, ei))
        Q = gr.mul(target, inv(den))
        Q511 = gr.power(Q, 511)
        ok = bool(np.array_equal(gr.mul(Q511 ^ gr.ONE, gr.ONE ^ Eax), np.zeros_like(Q)))
        # eigenvalue check at all line reps
        F = gr._field()
        eig_ok = all((F.pow(gr.eig(Q, *jk), 511) == 1) == (jk not in ((1, 0), (0, 1))) for jk in LINES)
        # on the axes: the residual
        ax = {str(jk): [f18.log(gr.eig(Q, *jk)) % 27, f18.log(gr.eig(Q, *jk)) % 19] for jk in ((1, 0), (0, 1))}
        out[name] = {"exponents_mod513": e, "group_ring_identity_offaxis": ok, "eigen_check": eig_ok,
                     "Q_weight": gr.weight(Q), "axis_residual_mod27_mod19": ax}
        print(name, "= R1^%d (rR1)^%d (r^2R1)^%d * B, B F(2^9)-valued off the axes:" % e, ok,
              "(eigenvalues:", eig_ok, ") Q weight", gr.weight(Q), "axis residual (log mod 27, mod 19):", ax)

    # eigencomponents of the mu_19 vectors under phi
    f18.full_log_table()
    off = [i for i, jk in enumerate(LINES) if jk not in ((1, 0), (0, 1))]
    V = {}
    for name, f in (("R1", R1), ("rR1", T[1]), ("r2R1", T[2]), ("R2", R2), ("R3", R3)):
        V[name] = np.array([f18.log(gr.eig(f, *jk)) % 19 for jk in LINES])
    # projectors onto eigenvalue w of phi on span{R1, rR1, r2R1}: P_w = (1/3) sum_i w^-i phi^i
    inv3 = pow(3, -1, 19)
    comps = {}
    for w in (1, 7, 11):
        comps[w] = (inv3 * (V["R1"] + pow(w, -1, 19) * V["rR1"] + pow(w, -2, 19) * V["r2R1"])) % 19
    recon = (comps[1] + comps[7] + comps[11]) % 19
    assert np.array_equal(recon[off], V["R1"][off])
    for name in ("R2", "R3"):
        for scal in ((1, 1, 7), (1, 1, 11), (1, 7, 1), (1, 11, 1), (7, 1, 1), (11, 1, 1)):
            pred = (scal[0] * comps[1] + scal[1] * comps[7] + scal[2] * comps[11]) % 19
            if np.array_equal(pred[off], V[name][off]):
                out[f"{name}_components"] = {"scalars_on_(1,7,11)_components": scal}
                print(name, "= R1 with its phi-eigencomponents (1, 7, 11) multiplied by", scal, "(off the axes)")
    out["component_supports"] = {str(w): int((comps[w][off] != 0).sum()) for w in comps}
    print("nonzero off-axis entries of the 1-, 7-, 11-components of R1's mu_19 vector:", out["component_supports"])
    with open(os.path.join(gr.HERE, "verify_twist.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
