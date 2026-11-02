import os
os.environ['OMP_NUM_THREADS']='1'; os.environ['OPENBLAS_NUM_THREADS']='1'; os.environ['MKL_NUM_THREADS']='1'
import pickle, json, collections, random, math, sys
from multiprocessing import Pool
C=pickle.load(open('classes.pkl','rb'))
E=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))['entries']
maxd=collections.defaultdict(int)
for e in E: maxd[e['n']]=max(maxd[e['n']],e['d'])
def grp(l,m): g=math.gcd(l,m); return (g,l*m//g)
tasks=[]
# job 1: certain achievers of max d at n
for c in C:
    if c['conn'] and c['k']>0 and c['d'] is not None and c['d']==maxd.get(c['n']):
        tasks.append(('ach',c['l'],c['m'],c['n'],c['k'],c['d'],c['A'],c['B']))
# job 2: population sample, one torus per group, connected k>0
random.seed(2026)
byng=collections.defaultdict(list); reptor={}
for c in C:
    if not (c['conn'] and c['k']>0): continue
    g=grp(c['l'],c['m'])
    key=(c['n'],g)
    if key not in reptor: reptor[key]=(c['l'],c['m'])
    if reptor[key]==(c['l'],c['m']): byng[c['n']].append(c)
for n in sorted(byng):
    if n not in maxd: continue
    pop=byng[n]; s=random.sample(pop,min(40,len(pop)))
    for c in s: tasks.append(('pop',c['l'],c['m'],c['n'],c['k'],c['d'] if c['d'] is not None else -(c['upper'] or 0),c['A'],c['B']))
print(collections.Counter(t[0] for t in tasks),flush=True)
def work(t):
    from stencil import min_diam
    D,_=min_diam(t[1],t[2],[tuple(p) for p in t[6]],[tuple(p) for p in t[7]])
    return list(t)+[D]
if __name__=='__main__':
    random.shuffle(tasks)
    with Pool(3) as p, open('jobs_out.jsonl','w') as f:
        for i,r in enumerate(p.imap_unordered(work,tasks,chunksize=4)):
            f.write(json.dumps(r)+'\n')
            if i%200==0: f.flush(); print(i,len(tasks),flush=True)
    print('done')
