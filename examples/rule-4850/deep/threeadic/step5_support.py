"""Step 5: the minimal unit support, with vanishing units allowed on line-explained classes.

General fact (used here, proved in the report): any symmetric one-variable unit U(X_w) has, at a
character c with n = w.c != 0, the value U(t_n); if it is a cube, log_t U(t_n) = ell * phi(n)
(mod 171) with phi(n) = 2^(ind_2 n) (mod 9 and mod 19) and ell = log_t U(t_1) arbitrary; at n = 0 its
value is U(0) in {0, 1}, and U(0) can be switched by adding Q37 (Q37(t_n) = 0 for n != 0).  So a
D4-symmetric product N of one-variable units is described by (ell_O mod 171) per direction orbit O
and the set V of orbits whose units vanish on their perpendicular lines (orbit O's perpendicular
lines form the class O itself).  f * N is F(2^9)-valued (27th-power valued) at every character not
on a vanishing line iff
      sum_O ell_O Phi_O(c) = -log_t f(c)   (mod 171, resp. mod 9)  for the classes c not in V,
Phi_O(c) = sum_{w in D4 w_O / +-} phi(w.c).  The classes in V must then be explained separately (the
pilot's condition 3: the line restriction is a monomial times full cyclotomic polynomials).
For each rule: the classes whose line restriction is such a product (computed by trial division),
and for every V among them and every T (V subset of T), solvability mod 9, mod 19, mod 171; the
minimal |T| (orbits and directions).  Controls: explained ninth-power rules and random cube-confined
rules.  Writes step5_support.json.
"""
import itertools
import json
import sys

import numpy as np
import sympy

import tlib
from tlib import M, LINES
import sbasis
import zsolve

sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
import census37 as C  # noqa: E402

IND = {pow(2, i, M): i for i in range(36)}
LT1 = int(tlib.LOG[tlib.T[1]])
X = sympy.symbols("x")


def phi(n, mod):
    n %= M
    return 0 if n == 0 else pow(2, IND[n], mod)


def orbit_vectors(w0):
    vs = set()
    for g in sbasis.D4:
        a, b = g(*w0)
        if (a, b) < (-a, -b):
            a, b = -a, -b
        vs.add((a, b))
    return sorted(vs)


def short(w):
    best = None
    for a in range(-6, 7):
        for b in range(-6, 7):
            if (a, b) != (0, 0) and (a * w[1] - b * w[0]) % M == 0:
                key = (max(abs(a), abs(b)), abs(a) + abs(b))
                if best is None or key < best[0]:
                    best = (key, (a, b))
    return best[1]


ORB_VECS = [orbit_vectors(short(w)) for w in sbasis.ORBIT_REP]


def Phi_matrix(mod):
    """rows: orbits, cols: classes."""
    P = np.zeros((11, 11), dtype=np.int64)
    for oi, vs in enumerate(ORB_VECS):
        for ci, (j, k) in enumerate(tlib.CENSUS_REPS):
            P[oi, ci] = sum(phi(w[0] * j + w[1] * k, mod) for w in vs) % mod
    return P


def logt_classes(n, r, mod):
    L = tlib.logs(tlib.rule_values(n, r))
    out = []
    for j, k in tlib.CENSUS_REPS:
        a = int(L[j, k])
        assert a >= 0 and a % 3 == 0
        if mod == 9:
            out.append((a // 3) * pow(LT1 // 3, -1, 9) % 9)
        else:
            out.append(a * pow(LT1, -1, 19) % 19)
    return out


def cyclotomic_lines(n, r):
    """classes whose line restriction g_k(x) = f(x, x^k) is a monomial times full cyclotomic Phi_e's."""
    f = C.rule(n, r)
    out = []
    phis = {e: sympy.Poly(sympy.cyclotomic_poly(e, X), X, modulus=2) for e in range(1, 400) if sympy.totient(e) <= 200}
    for ci, (j, k) in enumerate(tlib.CENSUS_REPS):
        if (j, k) == (0, 1):
            j, k = 1, 0  # the axis line g(x) = f(x, 1)
        exps = [p * j + q * k for p, q in f]
        lo = min(exps)
        coeffs = {}
        for e in exps:
            coeffs[e - lo] = coeffs.get(e - lo, 0) ^ 1
        g = sympy.Poly(sum(X**e for e, c in coeffs.items() if c), X, modulus=2)
        if g.is_zero:
            out.append(None)
            continue
        # strip x
        while g.eval(0) == 0:
            g = sympy.Poly(sympy.quo(g.as_expr(), X), X, modulus=2)
        for e, P in phis.items():
            if P.degree() > g.degree():
                continue
            while g.degree() >= P.degree() and g.rem(P).is_zero:
                g = g.quo(P)
        out.append(g.degree() == 0)
    return out


def min_support(target9, target19, explained, P9, P19):
    """for every V subset of explained classes (excluding (1,6), always F(2^9)), minimal T (V subset T)."""
    free = [ci for ci in range(11) if explained[ci] and ci != 6]
    res = {}
    for mod, label in ((9, "mod9"), (19, "mod19"), (171, "mod171")):
        best = None
        for vsize in range(len(free) + 1):
            for V in itertools.combinations(free, vsize):
                cls = [c for c in range(11) if c not in V and c != 6]
                rest = [o for o in range(11) if o not in V]
                for tsize in range(0, 12 - vsize):
                    if best is not None and vsize + tsize > best[0]:
                        break
                    for Textra in itertools.combinations(rest, tsize):
                        T = list(V) + list(Textra)
                        ok = True
                        if mod in (9, 171):
                            A = P9[np.ix_(T, cls)].T if T else np.zeros((len(cls), 0), dtype=np.int64)
                            ok &= zsolve.solvable(A, [-target9[c] for c in cls], 3, 2)
                        if ok and mod in (19, 171):
                            A = P19[np.ix_(T, cls)].T if T else np.zeros((len(cls), 0), dtype=np.int64)
                            ok &= zsolve.solvable(A, [-target19[c] for c in cls], 19, 1)
                        if ok:
                            ndir = sum(len(ORB_VECS[o]) for o in T)
                            cand = (len(T), ndir, list(V), sorted(T))
                            if best is None or cand[:2] < best[:2]:
                                best = cand
                            break
        res[label] = None if best is None else dict(orbits=best[0], directions=best[1],
                                                    vanishing_classes=[tlib.CENSUS_REPS[c] for c in best[2]],
                                                    T=[sbasis.ORBIT_REP[o] for o in best[3]])
    return res


if __name__ == "__main__":
    P9, P19 = Phi_matrix(9), Phi_matrix(19)
    out = {"orbit_vectors": ORB_VECS}
    rules = {4850: 4, 482758: 5, 10491524: 6, 8438150: 6, 43250486: 6, 20982139: 6, 178279803: 6,
             # explained ninth-power controls (pilot 7 targets and atlas-explained)
             699738: 5, 985232: 5, 1431278: 5, 1968276: 5, 233: 4, 13: 4, 7: 4}
    # random zero-free cube-confined controls from step3 (unexplained)
    st3 = json.load(open("step3_census.json"))
    rng = np.random.default_rng(5)
    unex = [x for x in st3["cube"] if not x["cube_explained"] and x["w1"] > 0]
    for x in rng.choice(len(unex), 8, replace=False):
        rules[unex[x]["id"]] = unex[x]["radius"]
    for n, r in rules.items():
        try:
            t9 = logt_classes(n, r, 9)
        except AssertionError:
            print(n, "not cube-valued / has zeros; skipped")
            continue
        t19 = logt_classes(n, r, 19)
        expl = cyclotomic_lines(n, r)
        ms = min_support(t9, t19, [bool(e) for e in expl], P9, P19)
        out[n] = dict(radius=r, logt9=t9, logt19=t19, cyclotomic_classes=[tlib.CENSUS_REPS[c] for c in range(11) if expl[c]],
                      min_support=ms)
        print(n, "cyclotomic line classes:", out[n]["cyclotomic_classes"])
        for k, v in ms.items():
            print("    ", k, v)
        sys.stdout.flush()
    json.dump(out, open("step5_support.json", "w"), indent=1, default=int)
