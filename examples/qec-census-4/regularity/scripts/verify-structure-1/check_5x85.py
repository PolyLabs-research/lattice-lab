# Independent re-check of the out-of-sample counterexample G = Z_5 x Z_85 (torus 5 x 85, n = 850):
# (1) every pair of zero sets sharing more than one Frobenius orbit: is ANY representative pair connected (explicit BFS)?
# (2) exact GF(2) rank on random connected codes with a common zero: k values seen.
import numpy as np, itertools, random, collections, time
from gf import partner_table, ordmod
from botheven import k_of, connected
n1,n2=5,85; N=85
part=np.array(partner_table(N))
els=[(a,b) for a in range(n1) for b in range(n2)]
ci=np.array([i for i in range(n1) for j in range(n2)]); cj=np.array([j for i in range(n1) for j in range(n2)])
E={u:(ci*u[0]*(N//n1)+cj*u[1])%N for u in els}
reps=collections.defaultdict(list)
nz=[u for u in els if u!=(0,0)]
t0=time.time()
for u,v in itertools.combinations(nz,2):
    z=(part[E[u]]==E[v])
    if z.any(): reps[z.tobytes()].append((u,v))
masks=list(reps); marr=[np.frombuffer(m,dtype=bool) for m in masks]
print('distinct nonempty zero sets',len(masks),'sizes',collections.Counter(int(m.sum()) for m in marr),'t',round(time.time()-t0,1))
inter=collections.Counter()
big=[]
for i in range(len(masks)):
    for j in range(i,len(masks)):
        s=int((marr[i]&marr[j]).sum())
        if s: inter[s]+=1
        if s>8: big.append((i,j,s))
print('intersection sizes over zero-set pairs',dict(inter))
print('pairs sharing >1 orbit:',len(big))
def gen_bfs(gens):
    seen={(0,0)}; st=[(0,0)]
    while st:
        x=st.pop()
        for g in gens:
            y=((x[0]+g[0])%n1,(x[1]+g[1])%n2)
            if y not in seen: seen.add(y); st.append(y)
    return len(seen)
conn_big=0; maxsub=0
for i,j,s in big:
    for (u,v) in reps[masks[i]]:
        for (w,z) in reps[masks[j]]:
            sz=gen_bfs([u,v,w,z]); maxsub=max(maxsub,sz)
            if sz==n1*n2: conn_big+=1
print('connected representative pairs among them:',conn_big,' largest generated subgroup:',maxsub,'of',n1*n2)
# (2) rank check
rng=random.Random(7); ks=collections.Counter(); tried=0
allpairs=[p for m in masks for p in reps[m]]
while sum(ks.values())<60:
    (u,v)=rng.choice(allpairs); (w,z)=rng.choice(allpairs)
    A=[(0,0),u,v]; B=[(0,0),w,z]
    zA=part[E[u]]==E[v]; zB=part[E[w]]==E[z]
    if not (zA&zB).any() or not connected(A,B,n1,n2): continue
    k=k_of(A,B,n1,n2); ks[(k,2*int((zA&zB).sum()))]+=1
print('(rank k, character k) counts:',dict(ks))
