import json, collections, math
import numpy as np
from scipy import stats
rows=[json.loads(l) for l in open('jobs_out.jsonl')]
ach=collections.defaultdict(list); pop=collections.defaultdict(list)
for r in rows:
    kind,l,m,n,k,d,A,B,D=r
    (ach if kind=='ach' else pop)[n].append((k,d,D,l,m))
W={(r['n']):None for r in json.load(open('all_D.json'))}
allD=json.load(open('all_D.json'))
wit={}
for n in sorted({r['n'] for r in allD}):
    es=[r for r in allD if r['n']==n]; mx=max(es,key=lambda e:(e['d'],-e['k'])); wit[n]=mx['D']
print('n maxd | witnessD | achievers: count, minD, Ddist | pop: count, Ddist, median | P(pop D < minAchD), P(pop D > minAchD)')
cmp=[]
for n in sorted(ach):
    a=[x[2] for x in ach[n]]; p=[x[2] for x in pop[n]]
    mn=min(a)
    lt=np.mean([x<mn for x in p]) if p else float('nan'); gt=np.mean([x>mn for x in p]) if p else float('nan')
    cmp.append((n,mn,np.median(p) if p else None,lt,gt,np.mean(p) if p else None, np.mean(a)))
    print(n, ach[n][0][1],'|',wit.get(n),'|',len(a),mn,dict(sorted(collections.Counter(a).items())),'|',len(p),dict(sorted(collections.Counter(p).items())),np.median(p) if p else None,'|',round(lt,2),round(gt,2))
print('\nBand summary: minD of max-d achievers vs census population (connected k>0 classes) D')
for lo in range(0,400,50):
    sel=[c for c in cmp if lo<c[0]<=lo+50]
    if not sel: continue
    print(f'{lo+1}-{lo+50}: minD_ach {dict(collections.Counter(c[1] for c in sel))}  mean pop D {np.mean([c[5] for c in sel if c[5] is not None]):.2f}  mean ach D {np.mean([c[6] for c in sel]):.2f}  mean minD_ach {np.mean([c[1] for c in sel]):.2f}')
cmp2=[c for c in cmp if c[5] is not None]
x=np.array([c[0]/2 for c in cmp2]); y=np.array([c[1] for c in cmp2]); pm=np.array([c[5] for c in cmp2])
print('spearman minD_ach vs N',stats.spearmanr(x,y))
print('mean(minD_ach - mean pop D) =',np.mean(y-pm), ' n>200:',np.mean((y-pm)[x>100]),' n<=200:',np.mean((y-pm)[x<=100]))
# within-pop correlation between exact d and D (n<=200, all exact)
rs=[]
for n in sorted(pop):
    p=[(d,D) for k,d,D,l,m in pop[n] if d>0]
    if len(p)>=15 and len(set(q[0] for q in p))>1 and len(set(q[1] for q in p))>1:
        rs.append((n,stats.spearmanr([q[0] for q in p],[q[1] for q in p])[0]))
print('within-n spearman(d, D) on population (exact d only):',len(rs),'mean',np.mean([r[1] for r in rs]),'pos',sum(r[1]>0 for r in rs),'neg',sum(r[1]<0 for r in rs))
json.dump(cmp,open('cmp.json','w'))
