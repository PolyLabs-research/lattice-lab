"""P0 in every frame.  For an order-3 'partial dilation' M of (Z/37)^2 -- eigenvalue mu in {27, 10}
on a line U, eigenvalue 1 on a line W != U -- test
    P0_M:  v27(lambda(M c)) = v27(lambda(c))   for every c != 0 with lambda(c), lambda(Mc) != 0.
(The standard frame is U = x-axis, W = y-axis.)  Rules: 4850 and relatives, the radius-4 ninth-power
rules, and random radius-4 rules (baseline)."""
import json, random, sys
import numpy as np
import ff18 as F
import vec

P = 37
lines = [(1, m) for m in range(P)] + [(0, 1)]


def full_v(n, r):
    V = vec.values([n], r)[0]
    v = vec.v27(V)
    full = np.zeros((P, P), dtype=np.int64)
    for j in range(P):
        for k in range(P):
            full[j, k] = v[vec.red(j), vec.red(k)]
    return full


def matrices():
    out = []
    for iu, u in enumerate(lines):
        for iw, w in enumerate(lines):
            if iu == iw:
                continue
            Pm = np.array([[u[0], w[0]], [u[1], w[1]]]) % P
            det = int(round(Pm[0, 0] * Pm[1, 1] - Pm[0, 1] * Pm[1, 0])) % P
            dinv = pow(det, -1, P)
            Pinv = (np.array([[Pm[1, 1], -Pm[0, 1]], [-Pm[1, 0], Pm[0, 0]]]) * dinv) % P
            for mu in (27, 10):
                M = (Pm @ np.diag([mu, 1]) @ Pinv) % P
                out.append(((u, w, mu), M))
    return out


MATS = matrices()
J, K = np.meshgrid(np.arange(P), np.arange(P), indexing='ij')
C = np.stack([J.ravel(), K.ravel()])  # 2 x 1369
NZ = (C[0] != 0) | (C[1] != 0)
PERM = np.array([((M @ C) % P)[0] * P + ((M @ C) % P)[1] for _, M in MATS])  # (n_mats, 1369)


def p0_frames(n, r):
    v = full_v(n, r).ravel()
    vm = v[PERM]
    ok = (vm == v[None, :]) | (vm < 0) | (v[None, :] < 0) | (~NZ[None, :])
    good = np.all(ok, axis=1)
    return [MATS[i][0] for i in np.nonzero(good)[0]]


if __name__ == '__main__':
    out = {}
    rels = [(4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6)]
    d = json.load(open('/home/user/lattice-lab/examples/llm-pilot-37c/data/ninth37.json'))
    r4 = [(rr['id'], 4, rr['procedure']) for rr in d['families'][0]['ninth_power_rules']]
    for n, r in rels:
        fr = p0_frames(n, r)
        out[str(n)] = [list(map(list, f[:2])) + [f[2]] for f in fr]
        print(n, 'frames with P0:', len(fr), fr[:8])
    print('radius-4 ninth-power rules:')
    for n, r, proc in r4:
        fr = p0_frames(n, r)
        out['r4_%d' % n] = [list(map(list, f[:2])) + [f[2]] for f in fr]
        print('  ', n, proc[:40], 'frames:', len(fr), fr[:4])
    random.seed(3)
    cnts = []
    for t in range(300):
        n = random.randrange(1, 1 << 15)
        cnts.append(len(p0_frames(n, 4)))
    out['random_r4_frame_counts'] = np.bincount(cnts).tolist()
    print('random radius-4 rules: histogram of #frames with P0:', np.bincount(cnts).tolist())
    json.dump(out, open('frames.json', 'w'), indent=1)
