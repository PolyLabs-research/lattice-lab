import ast
import numpy as np
rows=[]
for line in open('classes.out'):
    line=line.strip()
    if line.startswith("(") and line.count(",")==10 and "'" in line:
        rows.append(ast.literal_eval(line))
print(len(rows))
def cdf(ps,k):
    dist=np.zeros(len(ps)+1); dist[0]=1
    for p in ps:
        new=np.zeros_like(dist); new[:-1]+=dist[:-1]*(1-p); new[1:]+=dist[:-1]*p; dist=new
    return dist[:k+1].sum()
def summ(sel, label):
    obs=sum(1 for t in sel if t[5]>=t[4])
    lo=sum(t[8] for t in sel); hi=sum(t[9] for t in sel)
    print(label, "| pairs",len(sel),"| non-cyclic reaches cyclic top:",obs,
          "| expected if non-cyclic classes were draws from the cyclic population: [%.1f, %.1f]"%(lo,hi),
          "| P(<= observed): %.3f (p_lo) / %.3f (p_hi)"%(cdf([t[8] for t in sel],obs), cdf([t[9] for t in sel],obs)))
summ(rows,"all")
summ([t for t in rows if t[0]<=200],"n<=200")
summ([t for t in rows if t[0]>200],"n>200")
