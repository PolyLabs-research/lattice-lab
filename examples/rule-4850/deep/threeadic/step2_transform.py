"""Step 2: the Legendre transform of the 27th-power obstruction digit.

A[w, L] = chi(w . c_L) for w, L over the 38 projective points of (Z/37)^2 (fixed representatives).
Claim (checked here): A A^T = 37 I over Z, so A is invertible mod 3 (37 = 1 mod 3) and
d = A^T e has the unique solution e = A d mod 3.  So "d is a Z/3-combination of chi(w.c)" holds
for EVERY scaling-odd function d; with all 38 directions the system is vacuous and the content is
the support of the unique e.

Units realising chi(w.c) at the right level, nonzero everywhere:
  level 1 (log/3 mod 3): t_n has digit1 = eps1 chi(n)  [but t vanishes on w-perp]
  level 2 (log/9 mod 3): (1 + t_n) is a ninth power with digit2 = eps2 chi(n), value 1 at n = 0.
So f * prod_w (1 + t_w)^(-eps2 e_w) is a 27th power at every character, for every ninth-power rule.
Verified for each rule below directly in F(2^18) (tlib) and independently in F(2^36) (census37):
lambda^9709 = 1 at all 1368 characters.  Writes step2_transform.json.
"""
import json
import sys

import numpy as np

import tlib
from tlib import M, N, chi, LINES

sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
import census37 as C  # noqa: E402

RULES = {4850: 4, 482758: 5, 10491524: 6, 8438150: 6, 43250486: 6, 20982139: 6, 178279803: 6}


def short_rep(w):
    """a shortest integer vector (sup norm) on the projective line of w mod 37."""
    best = None
    for a in range(-6, 7):
        for b in range(-6, 7):
            if (a, b) == (0, 0):
                continue
            if (a * w[1] - b * w[0]) % M == 0:
                key = (max(abs(a), abs(b)), abs(a) + abs(b), -a, -b)
                if best is None or key < best[0]:
                    best = (key, (a, b))
    return best[1]


def chi_matrix():
    A = np.zeros((38, 38), dtype=np.int64)
    for wi, w in enumerate(LINES):
        for li, c in enumerate(LINES):
            A[wi, li] = chi[(w[0] * c[0] + w[1] * c[1]) % M]
    return A


def d4_orbits_of_directions():
    """D4 orbits of projective directions (g acts on w by signed permutations)."""
    seen, orbs = set(), []
    for wi, w in enumerate(LINES):
        if wi in seen:
            continue
        orb = set()
        for p, q in ((w[0], w[1]), (w[1], w[0])):
            for sp in (1, -1):
                for sq in (1, -1):
                    li, _ = tlib.line_of(sp * p, sq * q)
                    orb.add(li)
        seen |= orb
        orbs.append(sorted(orb))
    return orbs


def unit_digits():
    """digit1 of t_n and digit2 of (1 + t_n), n = 1..36, as multiples of chi(n)."""
    lt = tlib.LOG[tlib.T[1:]]
    assert np.all(lt % 3 == 0)
    d1 = (lt // 3) % 3
    eps1 = set(int(d1[n - 1] * chi[n] % 3) for n in range(1, M))
    l1t = tlib.LOG[1 ^ tlib.T[1:]]
    assert np.all(l1t % 9 == 0)
    d2 = (l1t // 9) % 3
    eps2 = set(int(d2[n - 1] * chi[n] % 3) for n in range(1, M))
    # also t^3: digit2 = digit1(t)
    l3 = (3 * lt) % N
    d2t3 = (l3 // 9) % 3
    eps3 = set(int(d2t3[n - 1] * chi[n] % 3) for n in range(1, M))
    return eps1, eps2, eps3


def unit_product_values(e, sign):
    """values of prod_w (1 + t_{w.c})^(sign * e_w) at all characters (tlib field)."""
    out = np.ones((M, M), dtype=np.int64)
    for wi, w in enumerate(LINES):
        if e[wi] % 3 == 0:
            continue
        ex = (sign * e[wi]) % 3
        u = 1 ^ tlib.T[(w[0] * tlib.JJ + w[1] * tlib.KK) % M]
        out = tlib.vmul(out, tlib.vpow(u, ex))
    return out


def independent_27th_check(f_terms, e, sign):
    """in census37's F(2^36): (f * prod (1+t_w)^(sign e_w))(c)^9709 == 1 at every nonzero c."""
    F = C.F
    z = [F.pow(F.zeta, i) for i in range(M)]
    bad = 0
    for j in range(M):
        for k in range(M):
            if (j, k) == (0, 0):
                continue
            v = C._value(f_terms, j, k)
            for wi, w in enumerate(LINES):
                ex = (sign * e[wi]) % 3
                if ex == 0:
                    continue
                n = (w[0] * j + w[1] * k) % M
                u = 1 ^ z[n] ^ z[-n % M]
                for _ in range(ex):
                    v = F.mul(v, u)
            if F.pow(v, 9709) != 1:
                bad += 1
    return bad


if __name__ == "__main__":
    A = chi_matrix()
    AAT = A @ A.T
    assert np.array_equal(AAT, 37 * np.eye(38, dtype=np.int64)), "not a conference matrix"
    print("A A^T = 37 I over Z: ok (A invertible mod 3, mod 9, mod 27)")
    eps1, eps2, eps3 = unit_digits()
    print("digit1(t_n) = eps1 chi(n), eps1 =", eps1, "; digit2(1+t_n) = eps2 chi(n), eps2 =", eps2,
          "; digit2(t_n^3) = eps3 chi(n), eps3 =", eps3)
    assert len(eps1) == 1 and len(eps2) == 1
    eps2 = eps2.pop()
    orbs = d4_orbits_of_directions()
    out = {"conference": True, "eps1": list(eps1), "eps2": eps2, "eps3": list(eps3),
           "direction_orbits": [[LINES[i] for i in o] for o in orbs],
           "direction_orbit_short": [[short_rep(LINES[i]) for i in o] for o in orbs]}
    print("D4 orbits of directions:", [[short_rep(LINES[i]) for i in o] for o in orbs])
    st1 = json.load(open("step1_digits.json"))
    for n, r in RULES.items():
        d = np.array(st1[str(n)]["line_digit2"], dtype=np.int64)
        e = (A @ d) % 3
        assert np.array_equal((A.T @ e) % 3, d % 3)
        supp = [i for i in range(38) if e[i]]
        by_orbit = []
        for o in orbs:
            vals = [int(e[i]) for i in o]
            by_orbit.append(vals)
        # realise: f * prod (1+t_w)^(-e_w/eps2) is a 27th power everywhere
        sign = (-pow(eps2, -1, 3)) % 3
        U = unit_product_values(e, sign)
        fv = tlib.rule_values(n, r)
        prod = tlib.vmul(fv, U)
        Lp = tlib.logs(prod)
        nz = [(j, k) for j in range(M) for k in range(M) if (j, k) != (0, 0)]
        ok = all(Lp[j, k] >= 0 and Lp[j, k] % 27 == 0 for j, k in nz)
        bad = independent_27th_check(C.rule(n, r), e, sign)
        out[n] = {"e": [int(x) for x in e], "support_size": len(supp),
                  "support": [short_rep(LINES[i]) for i in supp], "by_orbit": by_orbit,
                  "f_times_units_27th_power_everywhere": bool(ok), "independent_bad_characters": bad}
        print(n, "support of e:", len(supp), "of 38; per D4 orbit:", by_orbit,
              "| f*N 27th power everywhere:", ok, "independent check bad:", bad)
    json.dump(out, open("step2_transform.json", "w"), indent=1, default=int)
