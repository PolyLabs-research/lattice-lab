"""Step 9: partial-Frobenius symmetry of the 27-adic residue, in the Legendre/sextic language.

R_f(c) = log lambda_f(c) mod 27 (the mu_27 part).  For a symmetric rule it is determined by the 11
class logs: lambda(u g c0) = lambda(c0)^(2^ind u).  Partial Frobenius in a frame:
    frame A: P_g = diag(1, 2^g)          frame B (45 degrees): P_g^B = Rot^-1 diag(1, 2^g) Rot, Rot = [[1,1],[1,-1]]
Lemma (proved in the report): if R_f(P c) = R_f(c) for all c, for P = P_g in a frame where f is
D4-symmetric, then R_f^(2^g - 1) = 1, i.e. log = 0 mod 27/gcd(2^g - 1, 27): g = 6 -> cubes,
g = 2, 4 -> ninth powers, g odd -> 27th powers.
Computed here:
 (1) the character formula: in frame B the digit2 of 10491524 (= 4850's in frame A composed with
     Rot) equals chi(j) D(ind(k/j) mod 6) for jk != 0 -- D read off and checked at all characters;
 (2) census: for every zero-free rule of radius <= 4 (32767) and the zero-free cube-confined rules of
     radius <= 5: which P_g (g in 1..17, frames A and B) fix R_f; the lemma is checked on every hit;
     how many cube-confined rules have r = P_6-symmetric R, explained vs unexplained;
 (3) the same at the digit level only (digit1 of cube-confined rules mod 3; digit2 of ninth-power).
Writes step9_partialfrob.json.
"""
import json
from collections import Counter, defaultdict

import numpy as np

import tlib
from tlib import M, chi

IND = {pow(2, i, M): i for i in range(36)}
REPS = tlib.CENSUS_REPS


def char_map():
    """for each character (j, k) != 0: (class index, i) with lambda(j,k) = lambda(rep)^(2^i)."""
    cls = np.full((M, M), -1, dtype=np.int64)
    ex = np.zeros((M, M), dtype=np.int64)
    import sbasis
    for ci, (rj, rk) in enumerate(REPS):
        for g in sbasis.D4:
            a, b = g(rj, rk)
            for u in range(1, M):
                j, k = (u * a) % M, (u * b) % M
                if cls[j, k] < 0:
                    cls[j, k] = ci
                    ex[j, k] = IND[u]
    assert (cls[1:, :] >= 0).all() and (cls[0, 1:] >= 0).all()
    return cls, ex


CLS, EX = char_map()
P27 = np.array([pow(2, int(i), 27) for i in range(36)])  # 2^i mod 27
NZ = [(j, k) for j in range(M) for k in range(M) if (j, k) != (0, 0)]
NZJ = np.array([j for j, k in NZ])
NZK = np.array([k for j, k in NZ])


def residue_all(class_logs27):
    """(len(NZ), nrules) array: log mod 27 at every nonzero character, from (11, nrules) class logs."""
    cl = np.asarray(class_logs27) % 27
    return (cl[CLS[NZJ, NZK]] * P27[EX[NZJ, NZK]][:, None]) % 27


def perm_index(Mx):
    """index array p with NZ[p[i]] = Mx * NZ[i]."""
    pos = {c: i for i, c in enumerate(NZ)}
    out = []
    for j, k in NZ:
        a = (Mx[0][0] * j + Mx[0][1] * k) % M
        b = (Mx[1][0] * j + Mx[1][1] * k) % M
        out.append(pos[(a, b)])
    return np.array(out)


ROT = ((1, 1), (1, M - 1))
ROTI = tuple(tuple(int(x) for x in row) for row in (np.array([[1, 1], [1, -1]]) * pow(2, -1, M)) % M)


def matmul(A, B):
    return tuple(tuple(sum(A[i][t] * B[t][j] for t in range(2)) % M for j in range(2)) for i in range(2))


def partial(g, frame):
    D = ((1, 0), (0, pow(2, g, M)))
    if frame == "A":
        return D
    return matmul(ROTI, matmul(D, ROT))


PERMS = {(g, fr): perm_index(partial(g, fr)) for g in range(1, 18) for fr in ("A", "B")}


def symmetries(Rall, mod=27):
    """for each (g, frame): boolean array over rules, R(Pc) == R(c) mod `mod` at every c."""
    out = {}
    for key, p in PERMS.items():
        out[key] = np.all((Rall[p] - Rall) % mod == 0, axis=0)
    return out


if __name__ == "__main__":
    res = {}
    # (1) the character formula for 10491524 (frame B of 4850) and 4850 itself
    L = tlib.logs(tlib.rule_values(10491524, 6))
    d = np.where(L >= 0, (L // 9) % 3, -1)
    D = {}
    ok = True
    for j in range(1, M):
        for k in range(1, M):
            b = (IND[k] - IND[j]) % 6
            # d(j,k) = chi(j) D(b)
            dv = int(d[j, k] * chi[j] % 3)
            if b in D and D[b] != dv:
                ok = False
            D.setdefault(b, dv)
    axis = int(d[0, 1])
    res["formula_10491524"] = dict(holds=ok, D=D, axis_value=axis)
    print("10491524 digit2: d(j,k) = chi(j) D(ind(k/j) mod 6) for jk != 0:", ok, "D =", dict(sorted(D.items())), "axis", axis)
    # for 4850 in its own frame: with u = j + k, v = j - k
    L4 = tlib.logs(tlib.rule_values(4850, 4))
    d4 = (L4 // 9) % 3
    D4f = {}
    ok4 = True
    for j in range(M):
        for k in range(M):
            u, v = (j + k) % M, (j - k) % M
            if u == 0 or v == 0:
                continue
            b = (IND[v] - IND[u]) % 6
            dv = int(d4[j, k] * chi[u] % 3)
            if b in D4f and D4f[b] != dv:
                ok4 = False
            D4f.setdefault(b, dv)
    res["formula_4850"] = dict(holds=ok4, D=D4f)
    print("4850 digit2: d(j,k) = chi(j+k) D(ind((j-k)/(j+k)) mod 6) off the diagonals:", ok4, "D =", dict(sorted(D4f.items())))
    # (2) census of residue symmetries
    Lc = np.asarray(np.load("/home/user/lattice-lab/examples/rule-4850/deep/relations/L5.npy"))
    zf = (Lc >= 0).all(axis=0)
    # radius 4 all zero-free rules
    ids4 = np.flatnonzero(zf[: 1 << 15])
    ids4 = ids4[ids4 > 0]
    R4 = residue_all(Lc[:, ids4].astype(np.int64))
    sy4 = symmetries(R4)
    conf = np.all(Lc[:, ids4] % 27 == 0, axis=0)
    hits = {}
    lemma_ok = True
    for (g, fr), arr in sy4.items():
        n = int(arr.sum())
        if n:
            # lemma: R^(2^g-1) = 1, i.e. (2^g - 1) log = 0 mod 27 at every character
            vals = np.all(R4[:, arr] * (2**g - 1) % 27 == 0)
            lemma_ok &= bool(vals)
            hits[f"g={g},{fr}"] = n
    res["radius4_all_zero_free"] = dict(n=int(len(ids4)), symmetric_counts=hits, lemma_holds=lemma_ok)
    print("radius-4 zero-free rules:", len(ids4), "| residue fixed by partial Frobenius P_g:", hits, "| lemma holds on all:", lemma_ok)
    # cube-confined radius <= 5 with status
    st3 = json.load(open("step3_census.json"))
    cube = st3["cube"]
    ids = np.array([x["id"] for x in cube])
    Rc = residue_all(Lc[:, ids].astype(np.int64))
    syc = symmetries(Rc)
    # digit-level (mod 3 of the digit): digit1 for cube rules -> compare (R/3) mod 3
    rows = defaultdict(list)
    for (g, fr), arr in syc.items():
        for i in np.flatnonzero(arr):
            rows[f"g={g},{fr}"].append((int(ids[i]), bool(cube[i]["cube_explained"]), bool(cube[i]["nine_explained"]),
                                        "w2" in cube[i]))
    summ = {k: dict(n=len(v), explained=sum(1 for x in v if x[1]), unexplained=[x[0] for x in v if not x[1]][:20],
                    n_unexplained=sum(1 for x in v if not x[1]), ninth=sum(1 for x in v if x[3])) for k, v in rows.items()}
    res["cube_r5_residue_symmetry"] = summ
    print("zero-free cube-confined, radius <= 5 (%d): residue fixed by P_g:" % len(cube))
    for k in sorted(summ, key=lambda s: (int(s.split(',')[0][2:]), s)):
        print("   ", k, summ[k])
    # digit-level symmetry for cube rules: digit1 pattern (R/3 mod 3 when R = 0 mod 3)
    dsy = {}
    for (g, fr), p in PERMS.items():
        R3 = (Rc // 3) % 3
        arr = np.all((R3[p] - R3) % 3 == 0, axis=0)
        dsy[f"g={g},{fr}"] = (int(arr.sum()), [int(ids[i]) for i in np.flatnonzero(arr) if not cube[i]["cube_explained"]][:12],
                              int(sum(1 for i in np.flatnonzero(arr) if not cube[i]["cube_explained"])))
    res["cube_r5_digit1_symmetry"] = dsy
    print("digit1-level symmetry (n, unexplained ids, n unexplained):")
    for k in ("g=6,A", "g=6,B", "g=12,A", "g=12,B", "g=2,A", "g=2,B", "g=4,A", "g=4,B"):
        print("   ", k, dsy[k])
    # ninth-power radius-6 records (logs mod 27)
    r6 = []
    for line in open("/home/user/lattice-lab/examples/llm-pilot-37c/records.jsonl"):
        rr = json.loads(line)
        if "logs" not in rr or any(x is None or x == 255 for x in rr["logs"]):
            continue
        r6.append(rr)
    R6 = residue_all(np.array([rr["logs"] for rr in r6]).T)
    sy6 = symmetries(R6)
    s6 = {f"g={g},{fr}": [r6[i]["id"] for i in np.flatnonzero(a)] for (g, fr), a in sy6.items() if a.any()}
    res["ninth_r6_residue_symmetry"] = {k: dict(n=len(v), ids=v[:30]) for k, v in s6.items()}
    print("radius-6 zero-free ninth-power hits (%d): residue fixed by P_g:" % len(r6))
    for k, v in s6.items():
        print("   ", k, len(v), v[:12])
    json.dump(res, open("step9_partialfrob.json", "w"), indent=1, default=int)
