"""How common is the 4850 structure 'f * u is very sparse' (u = s = x+1/x+y+1/y or u = ab)?
Laurent products (no reduction), all radius-4 rules + the radius-6 ninth-power records; lists every rule
with |f*u| <= 12 and its confinement level at 37 (census logs mod 27)."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census

def grid(points, R):
    a = np.zeros((2 * R + 1, 2 * R + 1), dtype=np.int64)
    for p, q in points:
        a[p + R, q + R] ^= 1
    return a

def conv(a, b):
    # 2D binary convolution via integer FFT-free method (small arrays)
    out = np.zeros((a.shape[0] + b.shape[0] - 1, a.shape[1] + b.shape[1] - 1), dtype=np.int64)
    for i, j in zip(*np.nonzero(b)):
        out[i:i + a.shape[0], j:j + a.shape[1]] ^= a
    return out

S = grid({(1, 0), (-1, 0), (0, 1), (0, -1)}, 1)
AB = grid({(1, 1), (1, -1), (-1, 1), (-1, -1)}, 1)
logs4 = census.class_logs(4)
res = {}
hist = {'s': {}, 'ab': {}}
hits = []
for n in range(1, 1 << 15):
    f = grid(census.rule(n, 4), 4)
    for name, u in (('s', S), ('ab', AB)):
        w = int(conv(f, u).sum())
        hist[name][w] = hist[name].get(w, 0) + 1
        if w <= 12:
            L = logs4[:, n]
            nz = L[L != 255]
            hits.append(dict(rule=n, u=name, weight=w, f_terms=int(f.sum()), cube=bool(np.all(nz % 3 == 0)), ninth=bool(np.all(nz % 9 == 0))))
res['radius4_hist'] = {k: dict(sorted(v.items())) for k, v in hist.items()}
res['radius4_sparse'] = hits
print('radius-4: rules with |f*u| <= 12:')
for h in hits:
    print('  ', h)
rs = [json.loads(l) for l in open('/home/user/lattice-lab/examples/llm-pilot-37c/records.jsonl')]
rs = [r for r in rs if 'id' in r]
rec_hits = []
for r in rs:
    f = grid(census.rule(r['id'], 6), 6)
    for name, u in (('s', S), ('ab', AB)):
        w = int(conv(f, u).sum())
        if w <= 16:
            rec_hits.append(dict(rule=r['id'], u=name, weight=w, explained=r['explained'], procedure=r['procedure'][:40]))
res['radius6_records_sparse'] = rec_hits
print('radius-6 ninth-power records with |f*u| <= 16:')
for h in rec_hits:
    print('  ', h)
json.dump(res, open('sparsequot.json', 'w'), indent=1)
