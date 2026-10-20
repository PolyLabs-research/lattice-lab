r"""Twisted stabilizers of the 3-adic class function of a rule at m = 37.
v(c) = v27(lambda(c)) in Z/27 (or -1 for a zero eigenvalue), c in (Z/37)^2 \ 0.
Gamma_f = {(g, k) in GL2(F37) x Z/18 : v(g c) = 2^k v(c) for all c}  (g acts on characters, c column).
Always contains (D4, 0) and (2 I, 1)."""
import numpy as np
import nf

m = 37
PTS = [(j, k) for j in range(m) for k in range(m)]
IDX = {p: i for i, p in enumerate(PTS)}
J, K = nf.grid()
NZ = ~((J == 0) & (K == 0))
POW2 = [pow(2, k, 27) for k in range(18)]


def vfun(vals):
    return nf.V27()[vals]


def apply(g, j=J, k=K):
    (p, q), (r, s) = g
    return ((p * j + q * k) % m) * m + (r * j + s * k) % m


def multiplier(v, g):
    """k in 0..17 with v(g c) = 2^k v(c) for all c, or None."""
    img = v[apply(g)]
    base = v
    ok = []
    for kk in range(18):
        w = np.where(base[NZ] >= 0, (POW2[kk] * base[NZ]) % 27, -1)
        if np.array_equal(img[NZ], w):
            ok.append(kk)
    return ok


def stabilizer(v, dets=None):
    """all (g, ks) in GL2(F37) with a multiplier; search via images of e1, e2."""
    out = []
    ve1, ve2 = v[IDX[(1, 0)]], v[IDX[(0, 1)]]
    for kk in range(18):
        c1s = [p for p in PTS if p != (0, 0) and v[IDX[p]] == (POW2[kk] * ve1 % 27 if ve1 >= 0 else -1)]
        c2s = [p for p in PTS if p != (0, 0) and v[IDX[p]] == (POW2[kk] * ve2 % 27 if ve2 >= 0 else -1)]
        w = np.where(v[NZ] >= 0, (POW2[kk] * v[NZ]) % 27, -1)
        for c1 in c1s:
            for c2 in c2s:
                g = ((c1[0], c2[0]), (c1[1], c2[1]))  # columns are images of e1, e2
                det = (c1[0] * c2[1] - c2[0] * c1[1]) % m
                if det == 0:
                    continue
                if dets is not None and det not in dets:
                    continue
                if np.array_equal(v[apply(g)][NZ], w):
                    out.append((g, kk))
    return out


def matmul(g, h):
    return tuple(tuple(sum(g[i][t] * h[t][jj] for t in range(2)) % m for jj in range(2)) for i in range(2))
