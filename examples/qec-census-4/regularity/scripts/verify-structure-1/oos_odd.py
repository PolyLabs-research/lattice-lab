# Out-of-sample: for every odd G' = Z_n1 x Z_n2 (n1|n2) with |G'| <= MAX, compute the exact connected k-set
# and test (b) kmin == 2 ord_t(2) (t smallest admissible | exp) and (c) single <=> one admissible t with rank-1 primes.
import json,sys,time
from kset import kset_odd
from gf import primes, ordmod
MAX=int(sys.argv[1])
A=json.load(open('admissible.json')); exact=A['exact']
assert max(exact)>=MAX  # exact list complete up to 401
out=[]; t0=time.time()
for n1 in range(1,MAX+1,2):
    for n2 in range(n1,MAX//n1+1,2):
        if n2%n1 or n2==1: continue
        adm=[t for t in exact if n2%t==0]
        if not adm: continue
        ks=kset_odd(n1,n2)
        tmin=min(adm)
        predb=2*ordmod(tmin)
        predc= len(adm)==1 and all(n1%p for p in primes(adm[0]))
        rec=dict(G=(n1,n2),adm=adm,ks=ks,b_ok=(ks and ks[0]==predb),c_ok=((len(ks)==1)==predc),predb=predb,predc=predc)
        out.append(rec)
        if not rec['b_ok'] or not rec['c_ok']: print('FAIL',rec,flush=True)
print('odd groups with admissible t, |G\'|<=%d:'%MAX,len(out),' b ok',sum(r['b_ok'] for r in out),' c ok',sum(r['c_ok'] for r in out),' time',round(time.time()-t0))
json.dump(out,open('oos_odd_%d.json'%MAX,'w'))
import collections
print('kmin dist',collections.Counter(r['ks'][0] for r in out))
print('single groups', [(r['G'],r['adm'],r['ks']) for r in out if len(r['ks'])==1][:80])
