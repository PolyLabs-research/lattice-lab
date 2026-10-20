"""Step 17b: joint statistics of the d = 1 and d = 2 trinomial conditions over the 72 Frobenius orbits of
primitive 1387th roots a = g1387^k, and their dependence on the mu19 and mu73 components of a
(k mod 19, k mod 73).  Also locate a = t_1^63."""
import json, collections
import nf
from step17_trinomial import X_Y, g1387, a0, V, NK
def ninth(a, d):
    X, Y = X_Y(a, d)
    return V[1 ^ X ^ Y] % 9 == 0
k0 = next(k for k in range(1387) if nf.kpow(g1387, k) == a0)
rows = []
seen = set()
for k in range(1, 1387):
    if k % 19 == 0 or k % 73 == 0:
        continue
    rep = min(k * pow(2, i, 1387) % 1387 for i in range(18))
    if rep in seen:
        continue
    seen.add(rep)
    a = nf.kpow(g1387, rep)
    rows.append(dict(k=rep, k19=rep % 19, k73=rep % 73, d1=bool(ninth(a, 1)), d2=bool(ninth(a, 2))))
both = [r for r in rows if r['d1'] and r['d2']]
print('orbits:', len(rows), ' d1:', sum(r['d1'] for r in rows), ' d2:', sum(r['d2'] for r in rows), ' both:', len(both))
rep0 = min(k0 * pow(2, i, 1387) % 1387 for i in range(18))
print('a = t_1^63 is g1387^%d, orbit rep %d, in "both":' % (k0, rep0), any(r['k'] == rep0 for r in both))
# dependence on components: for d1, group by (k mod 19) up to the Frobenius action on Z/19 (2 has order 18 mod 19)
by19 = collections.defaultdict(list)
for r in rows:
    by19[r['k19'] != 0].append(r['d1'])
d1_by_19orbit = collections.Counter((r['k19'] == 0, r['d1']) for r in rows)
print('d1 vs (k mod 19 == 0):', dict(d1_by_19orbit))
# Within an orbit the 19-part runs over a full Frobenius orbit of (Z/19)*: there is one such orbit, so no 19-dependence is visible; use the joint (k19, k73) after normalising k19 = 1
norm = []
for r in rows:
    # normalise by Frobenius so that k mod 19 == 1
    for i in range(18):
        kk = r['k'] * pow(2, i, 1387) % 1387
        if kk % 19 == 1:
            norm.append((kk % 73, r['d1'], r['d2'])); break
print('after normalising k = 1 mod 19, the mu73 exponents with d1 ninth:', sorted(x for x, a, b in norm if a))
print('                                    with d2 ninth:', sorted(x for x, a, b in norm if b))
print('   t_1^63 has mu73 exponent', [kk % 73 for kk in [k0 * pow(2, i, 1387) % 1387 for i in range(18)] if kk % 19 == 1])
json.dump(dict(rows=rows, both=both, rep_t1=rep0), open('step17b_joint.json', 'w'), indent=1)
