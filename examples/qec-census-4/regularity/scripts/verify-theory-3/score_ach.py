import os
os.environ['OMP_NUM_THREADS']='1'
import pickle, json, collections, random
from multiprocessing import Pool
C=pickle.load(open('classes.pkl','rb'))
E=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))['entries']
best=collections.defaultdict(lambda:(0,0,0))
for e in E:
    if e['score']>best[e['n']][0]: best[e['n']]=(e['score'],e['k'],e['d'])
random.seed(5)
tasks=[]
for n,(s,k,d) in best.items():
    if n<=200: continue
    a=[c for c in C if c['n']==n and c['conn'] and c['k']==k and c['d']==d]
    for c in random.sample(a,min(60,len(a))): tasks.append((n,k,d,c['l'],c['m'],c['A'],c['B'],len(a)))
def work(t):
    from stencil import min_diam
    return list(t)+[min_diam(t[3],t[4],[tuple(p) for p in t[5]],[tuple(p) for p in t[6]])[0]]
if __name__=='__main__':
    with Pool(4) as p: res=p.map(work,tasks,chunksize=2)
    by=collections.defaultdict(list)
    for r in res: by[r[0]].append(r)
    for n in sorted(by):
        Ds=[r[-1] for r in by[n]]
        print(n,'k',by[n][0][1],'d',by[n][0][2],'score',round(best[n][0],2),'achievers',by[n][0][7],'checked',len(Ds),'minD',min(Ds),dict(sorted(collections.Counter(Ds).items())))
