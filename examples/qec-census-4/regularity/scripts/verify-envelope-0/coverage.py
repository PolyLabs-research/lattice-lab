"""Which stage-4 tori (150<lm<=200) are done, which can have codes (criterion E), per n and per group."""
import json, math, sys, importlib.util
from pathlib import Path
from collections import defaultdict
ROOT=Path('/home/user/lattice-lab')
spec=importlib.util.spec_from_file_location('bbmod', ROOT/'examples/qec-bb/bb.py')
bb=importlib.util.module_from_spec(spec); spec.loader.exec_module(bb)
def crit_e(l,m):
    lo, mo = bb.two_part(l)[1], bb.two_part(m)[1]
    E=math.lcm(lo,mo)
    if (l,m) in recs: return recs[(l,m)]['criterion_e']
    if E%3==0 or E%7==0: return True
    for e in range(3,E+1,2):
        if E%e: continue
        F=bb._field(e)
        mu={F.pow(F.zeta,i) for i in range(e)}
        if any((1^a) in mu for a in mu if a!=1): return True
    return False
def group(l,m):
    g=math.gcd(l,m); return (g, l*m//g)
recs={}
for line in open(ROOT/'examples/qec-census-4/records.jsonl'):
    r=json.loads(line)
    if r.get('job')=='torus': recs[(r['l'],r['m'])]=r
tori=[(l,m) for l in range(2,200) for m in range(l,201) if 150<l*m<=200]
print('tori',len(tori),'records',len(recs))
D=json.load(open(sys.argv[1]))
s4={(e['l'],e['m']) for e in D['entries'] if e['stage']=='4'}
byn=defaultdict(list)
for (l,m) in tori:
    ce=crit_e(l,m)
    done=(l,m) in recs
    if done: assert recs[(l,m)]['criterion_e']==ce,(l,m)
    byn[2*l*m].append(((l,m),ce,done,group(l,m),(l,m) in s4))
grpdone=defaultdict(bool)
for n in byn:
    for t,ce,done,g,ins in byn[n]:
        if done: grpdone[g]=True
for n in sorted(byn):
    items=byn[n]
    withcodes=[x for x in items if x[1]]
    if not withcodes: continue
    pend=[x for x in withcodes if not x[2]]
    pend_newgroup=[x for x in pend if not grpdone[x[3]]]
    print(n, 'codes-tori:',[f"{t[0]}x{t[1]}{'' if d else '*'}" for t,ce,d,g,i in withcodes],
          'PENDING groups not covered:' if pend_newgroup else '', [f"{x[0][0]}x{x[0][1]} {x[3]}" for x in pend_newgroup])
