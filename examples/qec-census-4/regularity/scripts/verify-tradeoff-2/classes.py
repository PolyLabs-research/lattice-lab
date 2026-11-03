import json, glob, math, collections
EX='/home/user/lattice-lab/examples'
def inv(l,m):
    g=math.gcd(l,m); return (g,l*m//g)
def load():
    out={}
    for p in sorted(glob.glob(EX+'/qec-census-3/data/*.jsonl')):
        L=[json.loads(x) for x in open(p) if x.strip()]
        h=L[0]
        rows=[dict(k=r['k'],d=r.get('d') if r.get('status')=='complete' else r.get('d'),conn=r.get('connected'),complete=r.get('status')=='complete',upper=r.get('upper')) for r in L[1:]]
        out[(h['l'],h['m'])]=dict(stage='3a',rows=rows)
    for folder,st in (('qec-census-3b','3b/3c'),('qec-census-3c','3b/3c'),('qec-census-4','4')):
        for x in open(f'{EX}/{folder}/records.jsonl'):
            r=json.loads(x)
            if r.get('job')!='torus' or 'error' in r: continue
            rows=[]
            for y in r['rows']:
                ex=y.get('exact') or {}
                rows.append(dict(k=y['k'],d=ex.get('d') if ex.get('status')=='complete' else None,conn=y['connected'],complete=ex.get('status')=='complete',upper=y.get('upper')))
            out[(r['l'],r['m'])]=dict(stage=st,rows=rows)
    return out
if __name__=='__main__':
    T=load()
    print('tori',len(T))
    c=collections.Counter()
    for t,v in T.items():
        for r in v['rows']:
            c[(v['stage'],r['complete'],r['upper'] is not None)]+=1
    print(c)
    # sample of a 3a row raw
    p=sorted(glob.glob(EX+'/qec-census-3/data/*.jsonl'))[5]
    print(open(p).readlines()[:3])
    x=open(EX+'/qec-census-4/records.jsonl').readline(); print(x[:800])
