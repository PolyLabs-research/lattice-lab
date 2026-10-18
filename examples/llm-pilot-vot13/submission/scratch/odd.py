import sys, csv; sys.path.insert(0,'tools')
from tori import *
rows=list(csv.DictReader(open('data/vot13_periods.csv')))
P={}
for r in rows:
    n,v,m,p=int(r['n']),int(r['v']),int(r['m']),int(r['period'])
    if m not in P: P[m]=period(square(m),S_VOT13)
    q=p//P[m]; assert q*P[m]==p
    a=q.bit_length()-1; assert 2**a==q
    print(n,v,m,P[m],p,'exp',a, 'v-exp',v-a)
