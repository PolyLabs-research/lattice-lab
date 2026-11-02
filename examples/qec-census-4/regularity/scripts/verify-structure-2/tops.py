import json, math, collections
D=json.load(open('../../census-data.json'))
E=D['entries']
ns=sorted(set(e['n'] for e in E))
print('distinct n:',len(ns))
print('n not mult of 6:',[n for n in ns if n%6])
# tops per n
top=collections.defaultdict(lambda:None)
for e in E:
    if top[e['n']] is None or e['d']>top[e['n']]['d']: top[e['n']]=e
def f(n,c=0.6175): return 2*math.floor(c*math.sqrt(n*math.log(n))/2)
tops6=[n for n in ns if (n//2)%3==0]
print('tops along mult of 6:',len(tops6))
miss=[]
for n in tops6:
    t=top[n]
    allk=[ (e['k'],e['d'],e['stage'],e['settled']) for e in E if e['n']==n and e['d']==t['d']]
    pr=f(n)
    flag='' if pr==t['d'] else ' <-- MISS'
    if pr!=t['d']: miss.append(n)
    print(n, 'd=',t['d'],'pred=',pr, 'raw=%.3f'%(0.6175*math.sqrt(n*math.log(n))), 'kd:',allk, flag)
print('misses',miss, 'hits', len(tops6)-len(miss))
