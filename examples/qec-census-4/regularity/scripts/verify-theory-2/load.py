import json, glob, collections, math, os
D='/home/user/lattice-lab/examples/qec-census-3/data'
def load(K=4, connected=True):
    tori={}
    for f in glob.glob(D+'/*.jsonl'):
        lines=open(f).read().splitlines()
        h=json.loads(lines[0])
        rows=[json.loads(L) for L in lines[1:]]
        sel=[r for r in rows if r['status']=='complete' and (r['connected'] if connected is not None else True) and r['k']==K]
        tori[(h['l'],h['m'])]=dict(n=h['n'], rows=sel, nclasses=h['classes'])
    return tori
def grp(l,m):
    g=math.gcd(l,m); return (g, l*m//g)
