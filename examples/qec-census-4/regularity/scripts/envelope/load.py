"""Shared loader for the envelope analysis (read-only on the repo).

Envelope definitions
--------------------
E(n)   : per n, the max settled best-connected d over all tori (all k) with that n.
         Unsettled entries (2, both 'exposed', both at d=22 where other tori settle at 24)
         are lower bounds and are kept apart.
R(n)   : running max of E over n' <= n (the "staircase" upper hull, monotone).
first(d): smallest n with E(n) >= d  (first appearance of each even d).
Group  : Z_l x Z_m ~ Z_gcd x Z_lcm; isomorphic tori are duplicate points.
"""
import json, math, glob, collections
from pathlib import Path

SCR = Path('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad')
REPO = Path('/home/user/lattice-lab/examples')
D = json.load(open(SCR / 'census-data.json'))
ENTRIES = D['entries']


def group(l, m):
    g = math.gcd(l, m)
    return (g, l * m // g)


def per_n():
    """n -> dict(dmax settled, dlb (incl. unsettled), stage, argmax tori/k, groups)."""
    out = {}
    for e in ENTRIES:
        n = e['n']
        r = out.setdefault(n, {'n': n, 'd': 0, 'dlb': 0, 'stage': e['stage'], 'arg': [],
                                'groups': set(), 'tori': set(), 'k_at_max': set()})
        r['groups'].add(group(e['l'], e['m']))
        r['tori'].add((e['l'], e['m']))
        r['dlb'] = max(r['dlb'], e['d'])
        if e['settled']:
            if e['d'] > r['d']:
                r['d'] = e['d']; r['arg'] = []; r['k_at_max'] = set()
            if e['d'] == r['d']:
                r['arg'].append((e['l'], e['m'], e['k'])); r['k_at_max'].add(e['k'])
        if e['stage'] != r['stage']:
            r['stage'] = r['stage'] + '+' + e['stage'] if e['stage'] not in r['stage'] else r['stage']
    rows = [out[n] for n in sorted(out)]
    run = 0
    for r in rows:
        run = max(run, r['d'])
        r['R'] = run
        r['groups_n'] = len(r['groups'])
    return rows


def class_counts():
    """(l,m) -> number of classes with k>0 (all stages), for an extreme-value covariate."""
    cc = {}
    for p in glob.glob(str(REPO / 'qec-census-3' / 'data' / '*.jsonl')):
        with open(p) as f:
            h = json.loads(f.readline())
        cc[(h['l'], h['m'])] = h['classes']
    for st in ('qec-census-3b', 'qec-census-3c', 'qec-census-4'):
        for x in open(REPO / st / 'records.jsonl'):
            r = json.loads(x)
            if r.get('job') == 'torus' and 'classes' in r:
                cc[(r['l'], r['m'])] = r['classes']
    return cc


def stage_of(n):
    return 'train' if n <= 300 else 'test'
