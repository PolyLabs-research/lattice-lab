"""Step 5: how often is the hidden symmetry present, and how often does it come with ninth powers?
For each rule of the radius-4 and radius-5 families (census.class_logs, logs mod 27), expand the class
logs to all 1368 characters (v(2^k g rep) = 2^k v(rep), g in D4), and test whether v is invariant
under M, for
   M0 = [[18, 29], [29, 18]]  (the order-3 symmetry of 4850's frame: R diag(10, 26) R^-1, R = [[1,1],[1,-1]])
   T  = diag(10, 26)          (the same symmetry in the rotated frame, as for 10491524)
Then: ninth-confinement rate among the M-symmetric rules, per-class ninth-power rates, forced classes."""
import sys, json, time
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census

m = 37
ZERO = 255
reps = census.characters()
D4 = [((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)),
      ((0, 1), (1, 0)), ((0, -1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (-1, 0))]
def act(g, c):
    return ((g[0][0] * c[0] + g[0][1] * c[1]) % m, (g[1][0] * c[0] + g[1][1] * c[1]) % m)
where = {}
for ci, r in enumerate(reps):
    for g in D4:
        for k in range(36):
            c = act(g, r)
            c = (pow(2, k, m) * c[0] % m, pow(2, k, m) * c[1] % m)
            where.setdefault(c, (ci, k))
assert len(where) == 1368
def expand_pairs(M):
    """list of (class_i, k_i, class_j, k_j) for c and M c over all g rep (enough: c = g rep)."""
    out = set()
    for ci, r in enumerate(reps):
        for g in D4:
            c = act(g, r)
            d = act(M, c)
            out.add((where[c], where[d]))
    return sorted(out)
def sym_mask(logs, M):
    ok = np.ones(logs.shape[1], dtype=bool)
    for (ci, ki), (cj, kj) in expand_pairs(M):
        a, b = logs[ci].astype(np.int64), logs[cj].astype(np.int64)
        va = np.where(a == ZERO, -1, (pow(2, ki, 27) * a) % 27)
        vb = np.where(b == ZERO, -1, (pow(2, kj, 27) * b) % 27)
        ok &= va == vb
    return ok
M0 = ((18, 29), (29, 18))
T = ((10, 0), (0, 26))
out = {}
for radius in (4, 5):
    t0 = time.time()
    logs = census.class_logs(radius)
    n = logs.shape[1]
    nine = census.confined(logs, 9); nine[0] = False
    cube = census.confined(logs, 3); cube[0] = False
    res = {'rules': n - 1, 'ninth': int(nine.sum()), 'cube': int(cube.sum())}
    for name, M in (('M0', M0), ('T', T)):
        s = sym_mask(logs, M); s[0] = False
        idx = np.flatnonzero(s)
        nz = np.all(logs[:, idx] != ZERO, axis=0)
        sub = logs[:, idx]
        per_class = [float(np.mean((sub[i] != ZERO) & (sub[i] % 9 == 0))) for i in range(11)]
        res[name] = {'symmetric': int(s.sum()), 'symmetric_no_zero': int(nz.sum()),
                     'symmetric_and_ninth': int((s & nine).sum()),
                     'symmetric_and_ninth_rules': [int(x) for x in np.flatnonzero(s & nine)][:200],
                     'symmetric_and_cube': int((s & cube).sum()),
                     'per_class_ninth_rate': per_class}
        print(radius, name, {k: v for k, v in res[name].items() if k != 'symmetric_and_ninth_rules'}, flush=True)
        print('    symmetric & ninth rules (first 40):', res[name]['symmetric_and_ninth_rules'][:40], flush=True)
    out[radius] = res
    print('radius', radius, 'rules', n - 1, 'ninth', res['ninth'], 'time', round(time.time() - t0, 1), flush=True)
    del logs
json.dump(out, open('step5_calib.json', 'w'), indent=1)
