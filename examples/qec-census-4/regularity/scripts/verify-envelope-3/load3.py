"""Independent loader (verify-envelope-3). Per torus: connected k>0 classes with
exact d (if computed & complete) and window upper bound (stages 3b-4)."""
import json, glob, math, collections
from pathlib import Path
EX = Path('/home/user/lattice-lab/examples')

def grp(l, m):
    g = math.gcd(l, m); return (g, l*m//g)

def evdown(u):
    return None if u is None else u - (u % 2)

def load():
    T = {}   # (l,m) -> dict(n, src, classes=[(k, d_exact or None, upper or None)])
    for p in sorted(glob.glob(str(EX/'qec-census-3'/'data'/'*.jsonl'))):
        L = [json.loads(x) for x in open(p) if x.strip()]
        h = L[0]
        cl = []
        bad = 0
        for r in L[1:]:
            if not r.get('connected') or r['k'] <= 0: continue
            if r['status'] != 'complete': bad += 1; cl.append((r['k'], None, r.get('d'))); continue
            cl.append((r['k'], r['d'], r['d']))
        T[(h['l'], h['m'])] = dict(n=h['n'], src='3a', cl=cl, bad=bad, hdr_classes=h['classes'])
    for st, tag in (('qec-census-3b', '3b'), ('qec-census-3c', '3c'), ('qec-census-4', '4')):
        for x in open(EX/st/'records.jsonl'):
            r = json.loads(x)
            if r.get('job') != 'torus' or not r.get('rows'): continue
            cl = []
            for y in r['rows']:
                if not y.get('connected') or y['k'] <= 0: continue
                e = y.get('exact')
                d = e['d'] if (e and e.get('status') == 'complete') else None
                cl.append((y['k'], d, y.get('upper')))
            key = (r['l'], r['m'])
            if key in T: T[key].setdefault('dups', []).append(tag)
            T[key] = dict(n=r['n'], src=tag, cl=cl, best=r['best']['connected'])
    # stage 3d: DistQLDPC exact d for classes of 9 tori
    d3 = collections.defaultdict(list)
    for x in open(EX/'qec-census-3d'/'records.jsonl'):
        r = json.loads(x)
        if 'class' in r:
            d3[tuple(r['class']['torus'])].append(r)
    return T, d3
