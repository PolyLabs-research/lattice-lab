import json, glob, collections, pickle
EX='/home/user/lattice-lab/examples/'
C=[]  # dicts: l,m,n,k,d (exact or None),upper,conn,A,B,stage
for f in sorted(glob.glob(EX+'qec-census-3/data/*.jsonl')):
    L=open(f).readlines(); h=json.loads(L[0])
    for line in L[1:]:
        r=json.loads(line)
        C.append(dict(l=h['l'],m=h['m'],n=h['n'],k=r['k'],d=r.get('d') if r.get('status')=='complete' else None,upper=r.get('d'),conn=r['connected'],A=r['A'],B=r['B'],stage='3a',status=r.get('status')))
for st,f in [('3b',EX+'qec-census-3b/records.jsonl'),('3c',EX+'qec-census-3c/records.jsonl'),('4',EX+'qec-census-4/records.jsonl')]:
    for line in open(f):
        h=json.loads(line)
        if h.get('job')!='torus': continue
        for r in h['rows']:
            ex=r.get('exact')
            d=ex['d'] if (ex and ex.get('status')=='complete') else None
            C.append(dict(l=h['l'],m=h['m'],n=h['n'],k=r['k'],d=d,upper=r.get('upper'),conn=r['connected'],A=r['A'],B=r['B'],stage=st,status=(ex or {}).get('status')))
# 3d reruns
for line in open(EX+'qec-census-3d/records.jsonl'):
    r=json.loads(line); c=r['class']; dq=r.get('distqldpc',{})
    C.append(dict(l=c['torus'][0],m=c['torus'][1],n=c['n'],k=c['k'],d=dq.get('d') if dq.get('lower')==dq.get('d') else None,upper=dq.get('d'),conn=True,A=c['A'],B=c['B'],stage='3d',status='rerun'))
print(len(C), collections.Counter(x['stage'] for x in C), collections.Counter((x['stage'],x['conn']) for x in C))
print('statuses',collections.Counter((x['stage'],x['status']) for x in C).most_common(20))
pickle.dump(C,open('classes.pkl','wb'))
