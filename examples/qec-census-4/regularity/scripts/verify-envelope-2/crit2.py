import math, json
from crit import odd, pgcd, xp1pow
def critE(l,m):
    E=math.lcm(odd(l),odd(m))
    if E==1: return False
    return pgcd((1<<E)|1, xp1pow(E)^1).bit_length()>1
R=[json.loads(x) for x in open('/home/user/lattice-lab/examples/qec-census-4/records.jsonl')]
print('stage4 mismatch:',[(r['l'],r['m']) for r in R if r['criterion_e']!=critE(r['l'],r['m'])])
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
print('data tori failing:',[t for t in {(e['l'],e['m']) for e in D['entries']} if not critE(*t)])
for t in [(11,14),(12,13),(13,13),(6,30),(13,14),(4,48),(6,32),(8,24),(12,16)]:
    print(t,2*t[0]*t[1],critE(*t), 'group', (math.gcd(*t), t[0]*t[1]//math.gcd(*t)))
