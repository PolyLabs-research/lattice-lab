import json, math, sys
exec(open('check_bounds.py').read().split('# ---- 3. structure ----')[1].split('rows = []')[0])
E = json.load(open(sys.argv[1]))['entries']
rows=[]
for e in E:
    if not e.get('A') or not e.get('B'): continue
    l,m=e['l'],e['m']
    ga=len(subgroup(norm_gens(e['A'],l,m),l,m)); gb=len(subgroup(norm_gens(e['B'],l,m),l,m))
    rows.append((e['n'],e['k'],e['d'],l,m,ga,gb,min(ga,gb)))
tight=[r for r in rows if r[2]==r[7]]
print('entries where d == min(|Ga|,|Gb|):',len(tight),'of',len(rows))
print('entries where min(|Ga|,|Gb|) <= 1.5 sqrt(n):',sum(1 for r in rows if r[7]<=1.5*math.sqrt(r[0])))
# top ratio codes
top=sorted(rows,key=lambda r:-r[2]/math.sqrt(r[0]))[:15]
for r in top: print('n=%d k=%d d=%d %dx%d |Ga|=%d |Gb|=%d |G|=%d d/sqrt n=%.3f'%(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[3]*r[4],r[2]/math.sqrt(r[0])))
# among entries with d/sqrt(n) >= 1.3, how many have a proper Ga or Gb
hi=[r for r in rows if r[2]/math.sqrt(r[0])>=1.3]
print('d/sqrt n >= 1.3:',len(hi),' with proper Ga or Gb:',sum(1 for r in hi if r[7]<r[3]*r[4]))
