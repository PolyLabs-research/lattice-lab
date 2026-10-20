"""Step 4: unrestricted half-Frobenius is vacuous at 37 -- an explicit exact certificate for 4850.

Facts checked here:
 (a) u_n = 1 + t_n (rule 150 in a direction) is nonzero for every n, a ninth power, with
       digit2(u_n) = eps2 chi(n)          (eps2 != 0, mod 3)
       log(u_n) mod 19 = c19 psi(n)        (c19 != 0), psi(n) = 2^(ind_2 n) mod 19, psi(-1) = 1.
 (b) The 38 x 38 matrices X[w, L] = chi(w.c_L) and Y[w, L] = psi(w.c_L) satisfy
       X X^T = 37 I (over Z),  Y Ybar^T = 37 I (mod 19)   (Ybar: psi^-1),
     so both are invertible (mod 3, mod 19).
 (c) Hence for every zero-free symmetric ninth-power-confined rule f there are unique n_w mod 57
     (w over the 38 directions) with f * prod_w u_w^(n_w) F(2^9)-valued at every character; as
     group-ring elements mod (x^37 - 1, y^37 - 1):
       B := f * prod_w (1 + X_w + 1/X_w)^(n_w)   satisfies   B(x^(2^9), y^(2^9)) = B   EXACTLY,
     which is the half-Frobenius form of mechanism 5 (B invariant under the dilation by 2^9 = -6).
     Conversely any such B certifies f's ninth powers (B is a 27th power, the u_w are ninth powers).
 (d) For 4850 (and relatives) the certificate is computed and the identity checked exactly in the
     group ring F2[Z/37 x Z/37]; also lambda_B(c)^(2^9) = lambda_B(c) at every c (tlib field).
 (e) The weights: number of D4 direction-orbits used by the 3-part (n_w mod 3) and by the
     19-part (n_w mod 19).
Writes step4_vacuity.json.
"""
import json

import numpy as np

import tlib
from tlib import M, N, chi, LINES
import sbasis

IND = {pow(2, i, M): i for i in range(36)}


def psi(n):
    n %= M
    return 0 if n == 0 else pow(2, IND[n], 19)


def psibar(n):
    n %= M
    return 0 if n == 0 else pow(pow(2, IND[n], 19), -1, 19)


def matrices():
    X = np.zeros((38, 38), dtype=np.int64)
    Y = np.zeros((38, 38), dtype=np.int64)
    Yb = np.zeros((38, 38), dtype=np.int64)
    for wi, w in enumerate(LINES):
        for li, c in enumerate(LINES):
            n = (w[0] * c[0] + w[1] * c[1]) % M
            X[wi, li] = chi[n]
            Y[wi, li] = psi(n)
            Yb[wi, li] = psibar(n)
    return X, Y, Yb


def unit_facts():
    u = 1 ^ tlib.T
    assert np.all(u != 0)
    lu = tlib.LOG[u]
    assert np.all(lu % 9 == 0)
    d2 = (lu // 9) % 3
    eps2 = {int(d2[n] * chi[n] % 3) for n in range(1, M)}
    c19 = {int(lu[n] * pow(psi(n), -1, 19) % 19) for n in range(1, M)}
    assert len(eps2) == 1 and len(c19) == 1
    return eps2.pop(), c19.pop()


def group_ring_power_unit(w, n, A):
    """A * (1 + X_w + X_w^-1)^n in F2[Z/37^2] (A a 37 x 37 0/1 array, axis 0 = x exponent)."""
    for _ in range(n):
        A = A ^ np.roll(A, (w[0], w[1]), axis=(0, 1)) ^ np.roll(A, (-w[0], -w[1]), axis=(0, 1))
    return A


def rule_array(n, r):
    import census37 as C
    A = np.zeros((M, M), dtype=np.uint8)
    for p, q in C.rule(n, r):
        A[p % M, q % M] ^= 1
    return A


def dilate(A, s):
    """B(x^s, y^s): coefficient of (s p, s q) is A[p, q]."""
    out = np.zeros_like(A)
    idx = (s * np.arange(M)) % M
    out[np.ix_(idx, idx)] = A
    return out


def ga_values(A):
    """eigenvalues of a group-ring element at all characters, in the tlib field (via orbits of
    single monomials: lambda = sum_{p,q} A[p,q] zeta^(pj+qk)); computed through symmetric pairs."""
    # zeta itself is not in F(2^18); evaluate the symmetric element only: pair (p,q) with (-p,-q)
    # zeta^n + zeta^-n = t_n, and A symmetric under (p,q) -> (-p,-q) is required.
    assert np.array_equal(A, A[(-np.arange(M)) % M][:, (-np.arange(M)) % M])
    J, K = tlib.JJ, tlib.KK
    v = np.zeros((M, M), dtype=np.int64)
    if A[0, 0]:
        v ^= 1
    seen = set()
    for p in range(M):
        for q in range(M):
            if (p, q) == (0, 0) or not A[p, q] or (p, q) in seen:
                continue
            seen.add((p, q))
            seen.add(((-p) % M, (-q) % M))
            v ^= tlib.T[(p * J + q * K) % M]
    return v


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
    X, Y, Yb = matrices()
    assert np.array_equal(X @ X.T, 37 * np.eye(38, dtype=np.int64))
    assert np.array_equal((Y @ Yb.T) % 19, (37 * np.eye(38, dtype=np.int64)) % 19)
    print("X X^T = 37 I over Z; Y Ybar^T = 37 I mod 19: ok")
    eps2, c19 = unit_facts()
    print("1 + t_n: nonzero, ninth power, digit2 = %d chi(n), log mod 19 = %d psi(n)" % (eps2, c19))
    inv37_19 = pow(37, -1, 19)
    RULES = {4850: 4, 482758: 5, 10491524: 6, 8438150: 6, 43250486: 6, 20982139: 6, 178279803: 6}
    out = {"eps2": eps2, "c19": c19}
    orbit_of = {}
    for oi, o in enumerate(sbasis.ORBITS):
        for li in o:
            orbit_of[li] = oi
    for n, r in RULES.items():
        L = tlib.logs(tlib.rule_values(n, r))
        lv = np.array([L[j, k] for j, k in LINES])
        assert np.all(lv >= 0) and np.all(lv % 9 == 0)
        d = (lv // 9) % 3
        g = lv % 19
        # 3-part: sum_w n_w eps2 chi(w.c_L) = -d_L (mod 3)  ->  n = -(X d) / eps2   (X^-1 = X^T, 37 = 1)
        n3 = (-(X @ d) * pow(eps2, -1, 3)) % 3
        assert np.array_equal((eps2 * (X.T @ n3) + d) % 3, np.zeros(38))
        # 19-part: sum_w n_w c19 psi(w.c_L) = -g_L (mod 19)  ->  n = -37^-1 c19^-1 Ybar g
        n19 = (-(Yb @ g) * inv37_19 * pow(c19, -1, 19)) % 19
        assert np.array_equal((c19 * (Y.T @ n19) + g) % 19, np.zeros(38))
        nw = [int((a * 19 * pow(19, -1, 3) + b * 3 * pow(3, -1, 19)) % 57) for a, b in zip(n3, n19)]
        assert all(x % 3 == a and x % 19 == b for x, a, b in zip(nw, n3, n19))
        # exact group-ring certificate
        A = rule_array(n, r)
        B = A.copy()
        for wi, w in enumerate(LINES):
            B = group_ring_power_unit(w, nw[wi], B)
        inv = np.array_equal(dilate(B, pow(2, 9, M)), B)
        # field check: B's eigenvalues lie in F(2^9)
        vb = ga_values(B)
        fin9 = bool(np.all(tlib.vpow(np.where(vb == 0, 1, vb), 512) == np.where(vb == 0, 1, vb)))
        # also: only the 3-part (n_w in {0,19,38}): f * N3 is a 27th power, 19-part = f's own
        n3only = [int(a * 19 * pow(19, -1, 3) % 57) for a in n3]
        orbs3 = sorted({orbit_of[i] for i in range(38) if n3[i]})
        orbs19 = sorted({orbit_of[i] for i in range(38) if n19[i]})
        out[n] = dict(n_w_mod57=nw, n_w_mod3=[int(x) for x in n3], n_w_mod19=[int(x) for x in n19],
                      dirs3=int(np.count_nonzero(n3)), dirs19=int(np.count_nonzero(n19)),
                      orbits3=[sbasis.ORBIT_REP[i] for i in orbs3], orbits19=[sbasis.ORBIT_REP[i] for i in orbs19],
                      B_weight=int(B.sum()), B_dilation_invariant=bool(inv), B_values_in_F512=fin9,
                      total_unit_degree=int(sum(nw)))
        print(n, "| 3-part: %d directions, orbits %s | 19-part: %d directions, %d orbits | B = f*N: "
              "dilation(2^9)-invariant %s, F(2^9)-valued %s, weight %d of 1369, total exponent %d"
              % (out[n]["dirs3"], out[n]["orbits3"], out[n]["dirs19"], len(orbs19), inv, fin9, B.sum(), sum(nw)))
    # a random control: the same construction for random zero-free ninth-power-confined rules exists by
    # (b); for a cube-confined but not ninth-power rule the 3-part system has the same unique solution
    # but the units (1+t) cannot change digit1, so f * N is never a 27th power: check one.
    json.dump(out, open("step4_vacuity.json", "w"), indent=0)
