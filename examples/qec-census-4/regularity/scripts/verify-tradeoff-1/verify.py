import json, math, collections
import numpy as np
from scipy import optimize
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
E=json.load(open(SP+'/census-data.json'))['entries']
INC={int(k):v for k,v in json.load(open('incomplete_n.json')).items()}
grp=lambda e:(math.gcd(e['l'],e['m']),e['l']*e['m']//math.gcd(e['l'],e['m']))
chk=collections.defaultdict(set)
for e in E: chk[(grp(e),e['k'])].add(e['d'])
print('iso-duplicate inconsistencies:',[x for x in chk.items() if len(x[1])>1])
print('distinct groups',len({grp(e) for e in E}),'distinct tori',len({(e['l'],e['m']) for e in E}),'entries',len(E))
# frontier per (n,k): max over all tori at n (isomorphic tori share n, so duplicates collapse)
F={}
for e in E: F[(e['n'],e['k'])]=max(F.get((e['n'],e['k']),0),e['d'])
P=np.array(sorted((n,k,d) for (n,k),d in F.items()),float); N,K,D=P.T
print('frontier (n,k) points:',len(P))
# --- c
tr=(K<=16)&(N<=300)
c=np.sum((D[tr]+K[tr])*np.sqrt(N[tr]))/np.sum(N[tr])
print(f'c (LS d+k=c sqrt n, k<=16, n<=300, N={tr.sum()}): {c:.4f}')
C=1.692
# --- envelope
ns=sorted(set(N.astype(int)))
env={n:max(F[(n,k)] for k in K[N==n].astype(int)) for n in ns}
kmin={n:int(K[N==n].min()) for n in ns}
kenv={n:[int(k) for k in K[N==n] if F[(n,int(k))]==env[n]] for n in ns}
print('envelope n count',len(ns),' kmin counter',collections.Counter(kmin.values()))
print('envelope carried by kmin at all n:',all(kmin[n] in kenv[n] for n in ns))
r=np.array([env[n]-(C*math.sqrt(n)-kmin[n]) for n in ns]); nsA=np.array(ns)
ins=nsA<=300
for lab,s in (('all',np.ones_like(ins)),('n<=300 (in-sample)',ins),('n>300',~ins)):
    print(f'  envelope resid {lab}: N={s.sum()} within+-2 {np.mean(np.abs(r[s])<=2):.3f} ({(np.abs(r[s])<=2).sum()}) rms {np.sqrt(np.mean(r[s]**2)):.2f} mean {r[s].mean():+.2f}')
print('  envelope points outside +-2:',[(n,kmin[n],env[n],round(C*math.sqrt(n)-kmin[n],2)) for n,x in zip(ns,r) if abs(x)>2])
# --- band maxima
print('\nBand maxima of env/sqrt(n): observed vs model (recipe: model at the observed argmax n) and model band max')
rows=[]
for a in range(0,400,50):
    v=[(env[n]/math.sqrt(n),n) for n in ns if a<n<=a+50]
    if not v: continue
    ob,nb=max(v)
    mod_at=C-kmin[nb]/math.sqrt(nb)
    mv=max((C-kmin[n]/math.sqrt(n),n) for n in ns if a<n<=a+50)
    rows.append((a,ob,nb,kmin[nb],mod_at,ob-mod_at,mv[0],mv[1],ob-mv[0]))
    print(f'  ({a:3d},{a+50:3d}] obs {ob:.3f} @n={nb} (kmin {kmin[nb]}, d={env[nb]}) | model@that n {mod_at:.3f} diff {ob-mod_at:+.3f} | model band max {mv[0]:.3f} @n={mv[1]} diff {ob-mv[0]:+.3f} | even-step 2/sqrt(n)={2/math.sqrt(nb):.3f}')
print('  max |diff| recipe:',max(abs(x[5]) for x in rows),' max |diff| band-max vs band-max:',max(abs(x[8]) for x in rows))
# --- stage-4 test
te=(K<=16)&(N>300)
pr=C*np.sqrt(N)-K; e=D-pr
print(f'\nStage-4 test k<=16 n>300: N={te.sum()} rms {np.sqrt(np.mean(e[te]**2)):.3f} bias {e[te].mean():+.3f} within2(cont) {np.mean(np.abs(e[te])<=2):.2f}')
pe=2*np.maximum(1,np.round(pr/2))
print(f'   even-rounded pred: within2 {np.mean(np.abs(pe[te]-D[te])<=2):.2f} exact {np.mean(pe[te]==D[te]):.2f}')
inc=np.isin(N,list(INC))
print(f'   test points at n with unfinished non-isomorphic tori {sorted(set(N[te&inc].astype(int)))}: {(te&inc).sum()} points:',[(int(n),int(k),int(d),round(p,1)) for n,k,d,p in zip(N[te&inc],K[te&inc],D[te&inc],pr[te&inc])])
s=te&~inc
print(f'   complete-n subset: N={s.sum()} rms {np.sqrt(np.mean(e[s]**2)):.3f} bias {e[s].mean():+.3f}')
print('   n values present in test:',sorted(set(N[te].astype(int))))
# what if the known [[360,12,24]] (6x30, unfinished) were in the census
D2=D.copy(); i=np.where((N==360)&(K==12))[0]
print('   census (360,12) =',D[i], 'model',pr[i])
D2[i]=np.maximum(D2[i],24); e2=D2-pr
print(f'   with [[360,12,24]] inserted: rms {np.sqrt(np.mean(e2[te]**2)):.3f} bias {e2[te].mean():+.3f}')
# --- sensitivity of c to training cut and its effect
print('\nsensitivity of the 1-param c to training cut (k<=16):')
for cut in (150,200,250,300):
    t=(K<=16)&(N<=cut); cc=np.sum((D[t]+K[t])*np.sqrt(N[t]))/np.sum(N[t])
    for lo in (cut,300):
        tt=(K<=16)&(N>lo); ee=D[tt]-(cc*np.sqrt(N[tt])-K[tt])
        print(f'  fit n<={cut}: c={cc:.4f} | test n>{lo}: N={tt.sum()} rms {np.sqrt(np.mean(ee**2)):.2f} bias {ee.mean():+.2f}')
# --- is the -k coefficient identified? free slope on k
for cut in (200,300):
    t=(K<=16)&(N<=cut)
    X=np.c_[np.sqrt(N[t]),-K[t]]; b,*_=np.linalg.lstsq(X,D[t],rcond=None)
    X2=np.c_[np.sqrt(N[t]),-K[t],np.ones(t.sum())]; b2,*_=np.linalg.lstsq(X2,D[t],rcond=None)
    print(f'  fit n<={cut}: d=c sqrt n - a k -> c={b[0]:.3f} a={b[1]:.3f} | d=c sqrt n - a k + e -> c={b2[0]:.3f} a={b2[1]:.3f} e={b2[2]:+.2f}')
np.save('frontier.npy',P)
json.dump({'env':env,'kmin':kmin},open('env.json','w'))
