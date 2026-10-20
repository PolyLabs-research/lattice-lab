"""Step 15: is W(al, be) = sum_{u in mu3} t_{u al} t_{be/u} a short product of t's (rule 90 values) at each
class?  At (1, 4): the six t's of W cancel to four, t_5 + t_17 + t_8 + t_14 = t_11 (t_6 + t_3) = t_11 t_14 t_17.
Search, at every class representative (al, be) = (1, k), for W = t_{j1} ... t_{jr} (r <= 5), and more generally
W = prod t_j^{n_j} * (1 + t_i) * ... with the t's of the same Legendre-class data; report the 3-adic
bookkeeping v9(W) = 3 c sum chi(j_i) and compare with the requirement v9(W) = -2 v9(pi)."""
import itertools, json
import numpy as np
import nf

m = 37
T = nf.tvec()
EXP, LOG = nf.tables()
mu3 = [1, 10, 26]
def W(al, be):
    v = 0
    for u in mu3:
        v ^= nf.kmul(T[u * al % m], T[be * pow(u, -1, m) % m])
    return v
def six(al, be):
    idx = []
    for u in mu3:
        a, b = u * al % m, be * pow(u, -1, m) % m
        for s in ((a + b) % m, (a - b) % m):
            idx.append(min(s, m - s))
    # cancel pairs
    out = []
    for i in sorted(set(idx)):
        if idx.count(i) % 2:
            out.append(i)
    return out
logt = {j: int(LOG[T[j]]) for j in range(1, 19)}
NK = nf.NK
res = []
for (j, k) in nf.CLASSES[1:]:
    al, be = j, k
    w = W(al, be)
    terms = six(al, be)
    lw = int(LOG[w])
    found = None
    for r in range(1, 6):
        for combo in itertools.combinations_with_replacement(range(1, 19), r):
            if sum(logt[c] for c in combo) % NK == lw:
                found = combo; break
        if found:
            break
    chi = [nf.legendre(c) for c in found] if found else None
    res.append(dict(cls=(j, k), surviving_t_terms=terms, product=found, chi=chi))
    print((j, k), 'W = sum of t over', terms, '  = product of t over', found, ' chi:', chi)
json.dump(res, open('step15_tproducts.json', 'w'), indent=1)
