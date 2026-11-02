"""Quantisation-aware comparison: how many admissible n does each form get wrong when the
frontier is modelled as the even staircase R(n) = 2*floor(f(n)/2) (running max of F(n))?
Also: isomorphic-torus consistency check."""
import json, math, collections
import numpy as np

D = json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E = D['entries']
F = collections.defaultdict(int)
for e in E:
    F[e['n']] = max(F[e['n']], e['d'])
ns = np.array(sorted(F)); Fd = np.array([F[n] for n in ns])
R = np.maximum.accumulate(Fd)
sel = ns >= 48
n = ns[sel].astype(float); Rn = R[sel]; Fn = Fd[sel]

def count(f):
    pred = 2 * np.floor(f / 2)
    return int((pred != Rn).sum()), int(np.abs(pred - Rn).max())

# sqrt(n ln n): one param c
best = {}
cs = np.linspace(0.5, 0.7, 4001)
res = [(count(c * np.sqrt(n * np.log(n)))[0], c) for c in cs]
m = min(r[0] for r in res); best['c sqrt(n ln n)'] = (m, [round(r[1], 4) for r in res if r[0] == m][::200][:5])
res = [(count(c * np.sqrt(n))[0], c) for c in np.linspace(1.2, 1.6, 4001)]
m = min(r[0] for r in res); best['c sqrt(n)'] = (m, [round(r[1], 4) for r in res if r[0] == m][:3])
res = [(count(c * n ** 0.75)[0], c) for c in np.linspace(0.3, 0.45, 4001)]
m = min(r[0] for r in res); best['c n^(3/4)'] = (m, [round(r[1], 4) for r in res if r[0] == m][:3])
res = [(count(c * n ** (2 / 3))[0], c) for c in np.linspace(0.5, 0.65, 4001)]
m = min(r[0] for r in res); best['c n^(2/3)'] = (m, [round(r[1], 4) for r in res if r[0] == m][:3])
# n^b: two params
bestnb = (999, None)
allnb = []
for b in np.linspace(0.55, 0.70, 301):
    for c in np.exp(np.linspace(np.log(0.4), np.log(1.2), 801)):
        k = count(c * n ** b)[0]
        allnb.append((k, b, c))
        if k < bestnb[0]:
            bestnb = (k, b, c)
best['c n^b'] = (bestnb[0], (round(bestnb[1], 4), round(bestnb[2], 4)))
bset = sorted(set(round(b, 3) for k, b, c in allnb if k == bestnb[0]))
print("admissible n in [48,400]:", len(n))
for k, v in best.items():
    print("%-16s min #mismatches vs even staircase R(n): %s" % (k, v))
print("b values achieving the n^b minimum:", bset[0], "...", bset[-1], "(%d values)" % len(bset))
for tol in [1, 2]:
    bs = sorted(set(round(b, 3) for k, b, c in allnb if k <= bestnb[0] + tol))
    print("b values within +%d mismatches: %.3f..%.3f" % (tol, bs[0], bs[-1]))

# isomorphic consistency
tor = collections.defaultdict(lambda: collections.defaultdict(int))
for e in E:
    g = math.gcd(e['l'], e['m'])
    tor[(g, e['l'] * e['m'] // g)][(e['l'], e['m'])] = max(tor[(g, e['l'] * e['m'] // g)][(e['l'], e['m'])], e['d'])
print("\nisomorphism classes with >1 torus:", sum(1 for v in tor.values() if len(v) > 1))
for grp, v in sorted(tor.items()):
    if len(set(v.values())) > 1:
        print("  INCONSISTENT best d within group Z_%d x Z_%d:" % grp, dict(v))
# per-k inconsistency
tk = collections.defaultdict(dict)
for e in E:
    g = math.gcd(e['l'], e['m'])
    tk[((g, e['l'] * e['m'] // g), e['k'])][(e['l'], e['m'])] = (e['d'], e['settled'], e['stage'])
for key, v in sorted(tk.items()):
    if len(set(x[0] for x in v.values())) > 1:
        print("  per-k mismatch", key, v)
print("unsettled:", [(e['l'], e['m'], e['k'], e['d']) for e in E if not e['settled']])
print("distinct groups (dedup) per 50-band:",
      collections.Counter((2 * g * mm) // 50 * 50 for g, mm in tor))
