"""Search: for a rule f (eigenvalues lambda on (Z/37)^2), a multiplier m (a simple symmetric rule) and
M in SL2(Z/37), does   G(Mc)/G(c) in F(2^9)*   hold at every c with G(c), G(Mc) != 0, G = f*m ?
(the 'twisted half-Frobenius invariance').  Exhaustive over SL2(Z/37) (50616 matrices)."""
import sys, json, random, time
import numpy as np
import ff18 as F
import vec

P = 37
J, K = np.meshgrid(np.arange(P), np.arange(P), indexing='ij')
C = np.stack([J.ravel(), K.ravel()])
NZC = (C[0] != 0) | (C[1] != 0)

MULT_ORBITS = {'1': [(0, 0)], 's=a+b': [(1, 0)], 'P=ab': [(1, 1)], '1+s': [(0, 0), (1, 0)],
               'e=(1+a)(1+b)': [(0, 0), (1, 0), (1, 1)], 'a^2+b^2': [(2, 0)]}


def grid_vals(orbs_or_rule, radius=None):
    """values on the full 37x37 grid; orbs_or_rule = rule number (with radius) or list of orbits."""
    if radius is not None:
        V = vec.values([orbs_or_rule], radius)[0]
    else:
        V = np.zeros((19, 19), dtype=np.int64)
        for o in orbs_or_rule:
            for j in range(19):
                for k in range(19):
                    V[j, k] ^= F.orbit_value(o, j, k)
    full = np.zeros((P, P), dtype=np.int64)
    for j in range(P):
        for k in range(P):
            full[j, k] = V[vec.red(j), vec.red(k)]
    return full.ravel()


def log513(vals):
    L = vec.logs(vals)
    return np.where(L < 0, -1, L % 513)


def sl2():
    out = []
    for a in range(P):
        for b in range(P):
            for c in range(P):
                for d in range(P):
                    if (a * d - b * c) % P == 1:
                        out.append((a, b, c, d))
    return np.array(out, dtype=np.int64)


def search(G513, mats, chunk=4000):
    hits = []
    for s in range(0, len(mats), chunk):
        Ms = mats[s:s + chunk]
        j2 = (Ms[:, 0:1] * C[0][None, :] + Ms[:, 1:2] * C[1][None, :]) % P
        k2 = (Ms[:, 2:3] * C[0][None, :] + Ms[:, 3:4] * C[1][None, :]) % P
        g2 = G513[j2 * P + k2]
        g1 = G513[None, :]
        ok = (g2 == g1) | (g2 < 0) | (g1 < 0) | (~NZC[None, :])
        good = np.all(ok, axis=1)
        hits.extend([tuple(int(x) for x in m) for m in Ms[good]])
    return hits


if __name__ == '__main__':
    t0 = time.time()
    mats = sl2()
    print('SL2 size', len(mats), time.time() - t0)
    mults = {name: grid_vals(orbs) for name, orbs in MULT_ORBITS.items()}
    out = {}
    targets = [(4850, 4), (10491524, 6), (20982139, 6), (178279803, 6), (482758, 5), (8438150, 6), (43250486, 6)]
    random.seed(11)
    controls = [(random.randrange(1, 1 << 15), 4) for _ in range(6)] + [(7, 4), (41, 4), (13, 4), (233, 4), (3394, 4), (5665, 4)]
    for n, r in targets + controls:
        fv = grid_vals(n, r)
        res = {}
        for name, mv in mults.items():
            G = np.array([F.mul(int(x), int(y)) for x, y in zip(fv, mv)], dtype=np.int64)
            hits = search(log513(G), mats)
            res[name] = hits
        out[str(n)] = {k: v for k, v in res.items()}
        print(n, {k: len(v) for k, v in res.items()}, ' e.g.', {k: v[:3] for k, v in res.items() if 4 < len(v) < 200}, round(time.time() - t0, 1))
    json.dump(out, open('sl2search.json', 'w'))
