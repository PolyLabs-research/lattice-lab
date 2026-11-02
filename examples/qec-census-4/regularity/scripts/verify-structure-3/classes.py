"""Claim 3: connected smallest-k class counts, cyclic vs non-cyclic, and an extreme-value test.

For each group (deduplicated over isomorphic tori), take the connected classes at the group's
smallest k.  Count them, and record for each class an interval [lo, hi] for d:
  exact d known -> [d, d];  otherwise -> [2, upper] (window upper bound; pruned classes).
Extreme-value test: draw N_nc classes (without replacement) from the cyclic group's k_min
classes; the hypergeometric probability that the draw contains a class at the cyclic top,
bounded below using only classes proven at the top and above using classes whose upper bound
reaches the top.  If class count alone explains 'cyclic higher', then at the non-cyclic count
the cyclic population should usually NOT reach its top.
"""
import json, math, pickle
from collections import defaultdict, Counter
from math import comb

HERE = "/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/regularity/verify-structure-3"
T = pickle.load(open(f"{HERE}/tori.pkl", "rb"))
KD = json.load(open(f"{HERE}/groups_kd.json"))


def gkey(l, m):
    g = math.gcd(l, m)
    return (g, l * m // g)


def gname(G):
    return f"Z{G[1]}" if G[0] == 1 else f"Z{G[0]}xZ{G[1]}"


groups = defaultdict(list)
for (l, m), v in T.items():
    groups[gkey(l, m)].append(((l, m), v))

info = {}
mism = []
for G, lst in groups.items():
    per = []
    for (l, m), v in lst:
        conn = [r for r in v["rows"] if r["conn"]]
        if not conn:
            per.append(((l, m), None, 0, [], v["stage"]))
            continue
        kmin = min(r["k"] for r in conn)
        cls = [r for r in conn if r["k"] == kmin]
        per.append(((l, m), kmin, len(cls), cls, v["stage"]))
    sig = {(p[1], p[2]) for p in per}
    if len(sig) > 1:
        mism.append((gname(G), [(p[0], p[1], p[2], p[4]) for p in per]))
    # use the torus with most exact info: prefer stage 3a, else first
    per.sort(key=lambda p: (p[4] != "3a", p[0]))
    info[G] = per[0]
print("isomorphic tori with different (k_min, #classes):", mism)

by_order = defaultdict(list)
for G, p in info.items():
    if p[1] is not None:
        by_order[G[0] * G[1]].append(G)

cnt = Counter(); rows = []
for N, Gs in sorted(by_order.items()):
    cyc = [G for G in Gs if G[0] == 1]
    if not cyc:
        continue
    c = cyc[0]
    for G in Gs:
        if G[0] == 1:
            continue
        pc, pn = info[c], info[G]
        same_k = pc[1] == pn[1]
        r = "cyclic more" if pc[2] > pn[2] else ("equal" if pc[2] == pn[2] else "non-cyclic more")
        cnt[(r, same_k)] += 1
        rows.append((2 * N, gname(G), pn[1], pn[2], pc[2]))
print("class-count comparisons (result, same k_min):", dict(cnt), "total", sum(cnt.values()))
for r in rows:
    print("  ", r)

# ---- extreme-value test
print("\n== extreme-value test: draw N_nc classes from the cyclic k_min population")
print("(n, nc group, N_nc, N_cyc, cyclic top, nc top, #cyc classes proven at top, #cyc classes with upper>=top,"
      " P_lo(draw reaches cyc top), P_hi, verdict)")
summary = Counter()
for N, Gs in sorted(by_order.items()):
    cyc = [G for G in Gs if G[0] == 1]
    if not cyc:
        continue
    c = cyc[0]
    _, kmin, Nc, cls_c, _ = info[c]
    top_c = KD[gname(c)][str(kmin)]
    exact_top = sum(1 for r in cls_c if r["d"] is not None and r["d"] >= top_c)
    maybe_top = sum(1 for r in cls_c if (r["d"] is not None and r["d"] >= top_c) or (r["d"] is None and (r["upper"] or 0) >= top_c))
    for G in Gs:
        if G[0] == 1:
            continue
        _, kn, Nn, cls_n, _ = info[G]
        top_n = KD[gname(G)][str(kn)]
        # P(sample of size Nn from Nc contains >=1 of the K top classes)
        def p_hit(K):
            if Nn >= Nc:
                return 1.0 if K > 0 else 0.0
            return 1 - comb(Nc - K, Nn) / comb(Nc, Nn)
        plo, phi = p_hit(exact_top), p_hit(maybe_top)
        if top_c > top_n:
            v = "cyc higher: count explains" if phi < 0.5 else ("cyc higher: count does NOT explain" if plo > 0.95 else "cyc higher: ambiguous")
        elif top_c == top_n:
            v = "tie"
        else:
            v = "nc higher"
        summary[v] += 1
        print("  ", (2 * N, gname(G), Nn, Nc, top_c, top_n, exact_top, maybe_top, round(plo, 3), round(phi, 3), v))
print(dict(summary))
