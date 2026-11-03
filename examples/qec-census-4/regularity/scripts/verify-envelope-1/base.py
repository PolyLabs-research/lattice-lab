"""Independent rebuild of the frontier staircase from census-data.json (no reuse of envelope/ code)."""
import json, math
import numpy as np
P = '/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'
D = json.load(open(P))
ent = D['entries']

def grp(l, m):
    g = math.gcd(l, m); return (g, l*m//g)

ns = sorted({e['n'] for e in ent})
E = {}      # settled max d per n
Elb = {}    # incl. unsettled lower bounds
groups = {}
for e in ent:
    n = e['n']
    Elb[n] = max(Elb.get(n, 0), e['d'])
    if e['settled']:
        E[n] = max(E.get(n, 0), e['d'])
    groups.setdefault(n, set()).add(grp(e['l'], e['m']))
# staircase
R = {}; run = 0
for n in ns:
    run = max(run, E.get(n, 0)); R[n] = run
thr = []   # (d, n_prev, n_first)
for d in range(2, 40, 2):
    nf = [n for n in ns if E.get(n, 0) >= d]
    if not nf: break
    nf = nf[0]
    i = ns.index(nf)
    npv = ns[i-1] if i > 0 else nf
    thr.append((d, npv, nf))
