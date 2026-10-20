"""Step 4. Other numerators with the same 60-degree symmetry.  In eigen-coordinates (A, B) = (e1+e2, e1-e2) of an
exponent e, the D4 x <M> orbit of e has eigenvalue
   W_lam(A alpha, A beta),   W_lam(al, be) = W(al, lam be) + W(lam al, be),   lam = B/A,
(24 points) unless lam is in mu6, where it collapses to the hexagon (12 points, eigenvalue W).  The rule is
f = (orbit)/s, eigenvalue W_lam(A c)/(t_al t_be) off the diagonals.  lam matters modulo mu6 and lam -> 1/lam.
Here: the 3-adic level of every (lam, A) at every size of step 3 with agen >= 1."""
import json, sys
import numpy as np
import famlib as L
from sizes_engine import Size, v3arr


def lam_classes(m, u):
    mu6 = {pow(u, i, m) for i in range(6)}
    seen, reps = set(), []
    for lam in range(1, m):
        if lam in seen or np.gcd(lam, m) != 1:
            continue
        cls = {lam * v % m for v in mu6} | {pow(lam, -1, m) * v % m for v in mu6}
        seen |= cls
        reps.append(lam)
    return reps, mu6


def W_values(S, r):
    """field values of W on the grid (dict-free numpy object array)."""
    m, F = S.m, S.F
    h = pow(2, -1, m)
    u = (1 + r) * h % m
    mu3 = [1, u * u % m, pow(u, 4, m)]
    mu3i = [pow(x, -1, m) for x in mu3]
    Wv = np.zeros((m, m), dtype=object)
    done = np.zeros((m, m), dtype=bool)
    t = F.t
    for al in range(1, m):
        for be in range(1, m):
            if done[al, be]:
                continue
            w = 0
            for x, xi in zip(mu3, mu3i):
                w ^= F.mul(t[x * al % m], t[be * xi % m])
            stack = [((al, be), w)]
            while stack:
                (x, y), ww = stack.pop()
                if done[x, y]:
                    continue
                done[x, y] = True
                Wv[x, y] = ww
                stack.append(((2 * x % m, 2 * y % m), F.sqr(ww)))
                for c2 in ((u * x % m, y * pow(u, -1, m) % m), (y, x), (-x % m, y), (x, -y % m)):
                    if not done[c2]:
                        stack.append((c2, ww))
    return Wv, u


def run(m):
    S = Size(m)
    if not S.A or not S.agen:
        return None
    A3, Q = S.A, 3 ** S.A
    out = dict(m=m, agen=S.agen, roots=[])
    idx = np.arange(m)
    al = idx[:, None] * np.ones((1, m), dtype=np.int64)
    be = np.ones((m, 1), dtype=np.int64) * idx[None, :]
    off = (al > 0) & (be > 0)
    for r in S.roots:
        Wv, u = W_values(S, r)
        reps, mu6 = lam_classes(m, u)
        rr = dict(r=r, u=u, lam=[])
        for lam in reps:
            if lam in mu6:
                vWl = None  # hexagon: handled by step 3
                W_l = Wv
            else:
                W_l = np.zeros((m, m), dtype=object)
                for x in range(1, m):
                    for y in range(1, m):
                        W_l[x, y] = Wv[x, lam * y % m] ^ Wv[lam * x % m, y]
            # logs of W_l on the grid (cheap: by Frobenius orbits of the scalar doubling)
            vW = np.full((m, m), -2, dtype=np.int64)
            for x in range(1, m):
                for y in range(1, m):
                    if vW[x, y] != -2:
                        continue
                    v = S.F.log3(W_l[x, y])
                    cx, cy = x, y
                    while vW[cx, cy] == -2:
                        vW[cx, cy] = -1 if v is None else v
                        if v is not None:
                            v = 2 * v % Q
                        cx, cy = 2 * cx % m, 2 * cy % m
            best = []
            seenA = set()
            for Aa in S.units:
                if Aa in seenA:
                    continue
                seenA |= {Aa, m - Aa}
                Wp = vW[(Aa * al) % m, (Aa * be) % m]
                nz = off & (Wp >= 0)
                Lv = (Wp - S.vt[al] - S.vt[be]) % Q
                E = int((A3 - v3arr(Lv[nz], A3)).max()) if nz.any() else 0
                best.append((Aa, S.agen - E, int((off & (Wp < 0)).sum())))
            lev = max(b[1] for b in best)
            rr['lam'].append(dict(lam=lam, hexagon=lam in mu6, best_level=lev,
                                  confined=[b for b in best if b[1] >= 1][:40], zero_chars_min=min(b[2] for b in best)))
        out['roots'].append(rr)
    return out


if __name__ == '__main__':
    ms = [int(x) for x in sys.argv[1:]] or [13, 37]
    res = []
    for m in ms:
        o = run(m)
        if o is None:
            print(m, 'skip'); continue
        res.append(o)
        for rr in o['roots']:
            for d in rr['lam']:
                print('m=%d r=%d lam=%d hexagon=%s best level %d; confined (A, level, zero chars): %s' % (
                    m, rr['r'], d['lam'], d['hexagon'], d['best_level'], d['confined'][:20]), flush=True)
    json.dump(res, open('step4_lambda_%s.json' % '_'.join(map(str, ms)), 'w'), indent=1)
