"""How rare are the partial-norm properties of 10491524 & co?
  P0: v27(lambda(27 j, k)) = v27(lambda(j, k))           (3-part invariant under the x-partial dilation)
  P1: v27(N_x(lambda)) = 0, N_x(j,k) = prod_{h=1,27,26} lambda(h j, k)   (partial norm a 27th power)
  P2: s19(N_x(lambda))(j, k) independent of j               (19-part of the partial norm depends on k only)
all for j, k != 0.  Tested on random rules of radius 4, 5, 6, on the ninth-power records, and on the relatives."""
import json, random
import numpy as np
import ff18 as F
import vec

J = np.arange(1, 19)


def props(ns, radius):
    V = vec.values(ns, radius)
    v = vec.v27(V)
    L = vec.logs(V)
    nz = np.all(V[:, 1:, 1:] != 0, axis=(1, 2))
    vv = v[:, 1:, 1:]
    v27p = v[:, vec.IDX27, :][:, 1:, 1:]
    P0 = np.all(vv == v27p, axis=(1, 2)) & nz
    # partial norm logs
    Ln = L[:, J, :] + L[:, [vec.IDX27[j] for j in J], :] + L[:, [vec.IDX26[j] for j in J], :]
    Ln = Ln[:, :, 1:] % F.N
    i27, i19 = vec._consts()
    vn = (Ln % 27) * i27 % 27
    sn = (Ln % 19) * i19 % 19
    P1 = np.all(vn == 0, axis=(1, 2)) & nz
    P2 = np.all(sn == sn[:, :1, :], axis=(1, 2)) & nz
    ninth = np.all(v[:, :, :][:, 1:, :] % 9 == 0, axis=(1, 2))  # (axis column included via j>=1,k=0)
    ninth &= np.all((v[:, 0, 1:] % 9 == 0) | (v[:, 0, 1:] < 0), axis=1)
    return dict(nz=nz, P0=P0, P1=P1, P2=P2, ninth=ninth)


out = {}
random.seed(7)
for radius, cnt in ((4, 32767), (5, 30000), (6, 30000)):
    if radius == 4:
        ns = np.arange(1, 1 << 15)
    else:
        nb = len(F.orbits(radius))
        ns = np.array([random.randrange(1, 1 << nb) for _ in range(cnt)], dtype=np.int64)
    res = {}
    for start in range(0, len(ns), 4000):
        p = props(ns[start:start + 4000], radius)
        for key, val in p.items():
            res.setdefault(key, []).append(val)
    res = {k: np.concatenate(v) for k, v in res.items()}
    nzc = int(res['nz'].sum())
    rec = dict(rules=int(len(ns)), nonzero_offaxis=nzc,
               P0=int(res['P0'].sum()), P1=int(res['P1'].sum()), P2=int(res['P2'].sum()),
               P0P1P2=int((res['P0'] & res['P1'] & res['P2']).sum()), P1P2=int((res['P1'] & res['P2']).sum()),
               ninth=int((res['ninth'] & res['nz']).sum()),
               ninth_and_P1=int((res['ninth'] & res['P1']).sum()), ninth_and_P2=int((res['ninth'] & res['P2']).sum()),
               P1P2_rules=[int(n) for n in ns[res['P1'] & res['P2']]][:40],
               P2_rules=[int(n) for n in ns[res['P2']]][:40])
    out['random_r%d' % radius] = rec
    print('radius', radius, {k: v for k, v in rec.items()})
# ninth-power records at radius 6 (and the relatives)
rs = [json.loads(l) for l in open('/home/user/lattice-lab/examples/llm-pilot-37c/records.jsonl')]
rs = [r for r in rs if 'id' in r]
ids = np.array([r['id'] for r in rs], dtype=np.int64)
p = props(ids, 6)
tab = []
for r, nz, a, b, c in zip(rs, p['nz'], p['P0'], p['P1'], p['P2']):
    tab.append(dict(id=r['id'], explained=r['explained'], procedure=r['procedure'][:50], nonzero=bool(nz), P0=bool(a), P1=bool(b), P2=bool(c)))
out['records_r6'] = tab
print('records r6 with nonzero off-axis values:', sum(t['nonzero'] for t in tab))
for t in tab:
    if t['nonzero'] and (t['P1'] or t['P2'] or t['P0']):
        print('  ', t)
print('  P0/P1/P2 counts among nonzero records:', sum(t['P0'] for t in tab), sum(t['P1'] for t in tab), sum(t['P2'] for t in tab))
d = json.load(open('/home/user/lattice-lab/examples/llm-pilot-37c/data/ninth37.json'))
for fam in d['families']:
    ids = np.array([r['id'] for r in fam['ninth_power_rules']], dtype=np.int64)
    p = props(ids, fam['radius'])
    print('ninth37 radius', fam['radius'], 'rules', len(ids), 'nonzero', int(p['nz'].sum()), 'P0', [int(i) for i in ids[p['P0']]], 'P1', [int(i) for i in ids[p['P1']]], 'P2', [int(i) for i in ids[p['P2']]])
    out['ninth37_r%d' % fam['radius']] = dict(ids=[int(i) for i in ids], nonzero=[int(i) for i in ids[p['nz']]], P0=[int(i) for i in ids[p['P0']]], P1=[int(i) for i in ids[p['P1']]], P2=[int(i) for i in ids[p['P2']]])
json.dump(out, open('baseline_pn.json', 'w'), indent=1)
