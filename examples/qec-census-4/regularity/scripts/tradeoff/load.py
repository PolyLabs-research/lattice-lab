import json, math, collections
import numpy as np
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
D=json.load(open(SP+'/census-data.json'))
E=D['entries']
def gkey(l,m):
    g=math.gcd(l,m); return (g, l*m//g)
for e in E:
    e['g']=gkey(e['l'],e['m'])
# dedup: group key + k -> keep max d (check consistency)
dd={}
incons=[]
for e in E:
    key=(e['g'],e['k'])
    if key in dd:
        if dd[key]['d']!=e['d']: incons.append((dd[key],e))
        if e['d']>dd[key]['d']: dd[key]=e
    else: dd[key]=e
U=list(dd.values())
