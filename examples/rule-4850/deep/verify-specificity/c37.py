"""37-specific class bookkeeping, built from scratch (closure of <D4, 2I> on nonzero characters)."""
import numpy as np
M = 37
D4 = [((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)),
      ((0, 1), (1, 0)), ((0, -1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (-1, 0))]
def act(g, c, m=M):
    return ((g[0][0] * c[0] + g[0][1] * c[1]) % m, (g[1][0] * c[0] + g[1][1] * c[1]) % m)
def mm(A, B, m=M):
    return tuple(tuple(sum(A[i][t] * B[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
NZ = [(j, k) for j in range(M) for k in range(M) if (j, k) != (0, 0)]
POS = {c: i for i, c in enumerate(NZ)}
# classes: orbits of <D4, doubling>; record for each character an exponent i with c = 2^i g rep
REPS = []
CLS = {}
for c in [(0, 1)] + [(1, k) for k in range(M)] + NZ:
    if c in CLS:
        continue
    ci = len(REPS); REPS.append(c)
    fr = [(c, 0)]; CLS[c] = (ci, 0)
    while fr:
        nf = []
        for x, i in fr:
            for g in D4:
                y = act(g, x)
                if y not in CLS:
                    CLS[y] = (ci, i); nf.append((y, i))
            y = (2 * x[0] % M, 2 * x[1] % M)
            if y not in CLS:
                CLS[y] = (ci, (i + 1) % 36); nf.append((y, (i + 1) % 36))
        fr = nf
assert len(CLS) == 1368
NCL = len(REPS)
# Frobenius exponents that fix a class rep (with D4): forced levels
def stab_exponents(rep):
    ks = set()
    for g in D4:
        for i in range(36):
            u = pow(2, i, M)
            if act(g, (u * rep[0] % M, u * rep[1] % M)) == rep:
                ks.add(i)
    return sorted(ks)
STAB = [stab_exponents(r) for r in REPS]
CI = np.array([CLS[c][0] for c in NZ]); EI = np.array([CLS[c][1] for c in NZ])
def expand(class_vals, mod):
    """class values (NCL, n) of a Frobenius-equivariant function (v(2c) = 2 v(c) mod `mod`) -> (1368, n)."""
    cv = np.asarray(class_vals) % mod
    mult = np.array([pow(2, int(i), mod) for i in EI])
    return (cv[CI] * mult[:, None]) % mod
def perm(A):
    return np.array([POS[act(A, c)] for c in NZ])
inv2 = pow(2, -1, M)
ROT = ((1, 1), (1, M - 1)); ROTI = ((inv2, inv2), (inv2, M - inv2))
def partial(g, frame):
    D = ((1, 0), (0, pow(2, g, M)))
    return D if frame == 'A' else mm(ROTI, mm(D, ROT))
