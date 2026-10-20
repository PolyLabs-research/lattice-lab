"""Step 1: the 3-adic digits of the eigenvalues at every nonzero character, for 4850 and relatives.

For a rule f, L(c) = log lambda_f(c) (generator G of tlib), at all 1368 nonzero characters.
digit_i(c) = floor(L / 3^i) mod 3, read only when L = 0 mod 3^i.
Checks: lambda(2c) = lambda(c)^2, lambda(-c) = lambda(c); L = 0 mod 9 at every c;
d(c) = L/9 mod 3 satisfies d(uc) = chi(u) d(c) (so d is one value per line, times chi).
Cross-checks: (i) the class pattern mod 27 against the dossier's (up to one global unit s mod 27);
(ii) full logs against relations/logtab.npy (census37 coordinates, f18 generator) up to one
global unit s mod 2^18-1; (iii) eigen.odd_part divides 29127.
Writes step1_digits.json."""
import json
import sys

import numpy as np

import tlib
from tlib import M, N, chi, LINES, LINE_CLASS

RULES = {4850: 4, 482758: 5, 10491524: 6, 8438150: 6, 43250486: 6, 20982139: 6, 178279803: 6}
DOSSIER27 = {4850: [18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18], 482758: [0, 0, 9, 9, 18, 9, 0, 0, 9, 0, 18],
             10491524: [9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9], 8438150: [9, 0, 0, 18, 0, 9, 0, 18, 0, 0, 18],
             43250486: [9, 18, 9, 0, 9, 9, 0, 18, 9, 18, 18], 20982139: [9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9],
             178279803: [9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9]}
DOSSIER513_4850 = [18, 198, 9, 234, 162, 63, 0, 495, 9, 387, 180]


def full_logs(n, r):
    v = tlib.rule_values(n, r)
    return tlib.logs(v)


def check_structure(L):
    nz = [(j, k) for j in range(M) for k in range(M) if (j, k) != (0, 0)]
    for j, k in nz:
        a = L[j, k]
        b = L[2 * j % M, 2 * k % M]
        if a < 0:
            assert b < 0
            continue
        assert b == 2 * a % N
        assert L[-j % M, -k % M] == a
    return True


def digit_line_rep(L, level):
    """the digit floor(L/3^level) mod 3 at each line representative, after checking lower digits vanish."""
    out = []
    for j, k in LINES:
        a = L[j, k]
        if a < 0:
            out.append(None)
            continue
        assert a % 3 ** level == 0
        out.append(int((a // 3 ** level) % 3))
    return out


def check_chi_scaling(L, level):
    """digit(u c) = chi(u) digit(c) for every nonzero c, u."""
    for j in range(M):
        for k in range(M):
            if (j, k) == (0, 0) or L[j, k] < 0:
                continue
            li, u = tlib.line_of(j, k)
            cj, ck = LINES[li]
            d0 = (L[cj, ck] // 3 ** level) % 3
            d = (L[j, k] // 3 ** level) % 3
            assert d == (chi[u] * d0) % 3, (j, k)
    return True


if __name__ == "__main__":
    out = {}
    # census class representatives
    reps = tlib.CENSUS_REPS
    sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
    sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
    import census37 as C
    logtab = np.load("/home/user/lattice-lab/examples/rule-4850/deep/relations/logtab.npy")
    s27 = None
    sN = None
    for n, r in RULES.items():
        L = full_logs(n, r)
        pass  # the trivial character may be 0
        check_structure(L)
        nzero = int(sum(1 for j in range(M) for k in range(M) if (j, k) != (0, 0) and L[j, k] < 0))
        assert nzero == 0
        allnine = all(L[j, k] % 9 == 0 for j in range(M) for k in range(M) if (j, k) != (0, 0))
        d = digit_line_rep(L, 2)
        check_chi_scaling(L, 2)
        cls27 = [int(L[j, k] % 27) for j, k in reps]
        # global unit s mod 27 relating my logs to the dossier's
        if s27 is None:
            cand = [s for s in range(27) if s % 3 and all(s * a % 27 == b for a, b in zip(cls27, DOSSIER27[n]))]
            assert len(cand) >= 1, cand
            s27 = cand
        else:
            s27 = [s for s in s27 if all(s * a % 27 == b for a, b in zip(cls27, DOSSIER27[n]))]
        # independent implementation: census37 values in F(2^36) and the f18 full log table
        f = C.rule(n, r)
        th = [int(logtab[C.coord(C._value(f, j, k))]) for j, k in reps]
        mine = [int(L[j, k]) for j, k in reps]
        if sN is None:
            # s with th = s * mine mod N, solved from a value with a unit log (if any) else by search
            s_c = None
            for a, b in zip(mine, th):
                if np.gcd(a, N) == 9:
                    pass
            # brute force over s mod N would be 262143 tries x 11: fine
            S = np.arange(N, dtype=np.int64)
            ok = np.ones(N, dtype=bool)
            for a, b in zip(mine, th):
                ok &= (S * a) % N == b
            sN = S[ok]
        else:
            sN = np.array([s for s in sN if all(s * a % N == b for a, b in zip(mine, th))])
        out[n] = dict(radius=r, all_ninth=bool(allnine), class_logs27=cls27,
                      line_digit2=d, line_class=LINE_CLASS,
                      class_digit2=[int((L[j, k] // 9) % 3) for j, k in reps])
        print(n, "ninth everywhere:", allnine, "class logs mod 27:", cls27,
              "digit2 per class:", out[n]["class_digit2"], "#s candidates:", len(sN))
    out["s27_candidates"] = [int(s) for s in s27]
    out["sN_candidates"] = [int(s) for s in sN[:20]]
    out["sN_count"] = int(len(sN))
    print("global unit mod 27 relating to the dossier:", s27)
    print("global units mod N relating to f18 full logs:", len(sN), sN[:5])
    # odd part check for 4850
    sys.path.insert(0, "/home/user/lattice-lab/examples/linear-atlas-3")
    import eigen
    sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850")
    import census
    op = eigen.odd_part(census.rule(4850, 4), 37)
    print("eigen.odd_part(4850, 37) =", op, "divides 29127:", 29127 % op == 0)
    out["odd_part_4850"] = int(op)
    json.dump(out, open("step1_digits.json", "w"), indent=1)
