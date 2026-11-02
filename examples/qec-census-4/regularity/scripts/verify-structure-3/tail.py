"""Per-class tail rates at k_min, n <= 200 (every class has an exact d): cyclic vs non-cyclic."""
import pickle, math, json
from collections import defaultdict
T = pickle.load(open("tori.pkl", "rb"))
def gkey(l, m):
    g = math.gcd(l, m); return (g, l * m // g)
pop = {}
for (l, m), v in sorted(T.items(), key=lambda t: (t[1]["stage"] != "3a", t[0])):
    G = gkey(l, m)
    if G in pop: continue
    conn = [r for r in v["rows"] if r["conn"]]
    if not conn: continue
    kmin = min(r["k"] for r in conn)
    ds = [r["d"] for r in conn if r["k"] == kmin]
    pop[G] = (kmin, ds, v["stage"])
byN = defaultdict(list)
for G in pop: byN[G[0] * G[1]].append(G)
tot = {"cyc": [0, 0, 0], "nc": [0, 0, 0]}
print("(n, group, #classes, missing d, frac at cyc top, frac at cyc top-2)")
for N, Gs in sorted(byN.items()):
    if 2 * N > 200: continue
    cyc = [G for G in Gs if G[0] == 1]
    if not cyc or len(Gs) == 1: continue
    top = max(d for d in pop[cyc[0]][1] if d is not None)
    for G in sorted(Gs):
        ds = pop[G][1]; miss = sum(d is None for d in ds); dd = [d for d in ds if d is not None]
        a = sum(d >= top for d in dd); b = sum(d >= top - 2 for d in dd)
        lab = "cyc" if G[0] == 1 else "nc"
        tot[lab][0] += len(dd); tot[lab][1] += a; tot[lab][2] += b
        print((2 * N, ("Z%d" % G[1]) if G[0] == 1 else "Z%dxZ%d" % G, len(ds), miss, round(a / len(dd), 4), round(b / len(dd), 4)))
for lab, (n_, a, b) in tot.items():
    print(lab, "pooled classes", n_, "at cyclic top: %d (%.2f%%)" % (a, 100 * a / n_), "at top-2 or more: %d (%.1f%%)" % (b, 100 * b / n_))
