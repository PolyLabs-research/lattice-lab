"""Claim 1 & 2: column tops by group; cyclic vs non-cyclic of the same order (independent)."""
import json, math
from collections import defaultdict, Counter

SP = "/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad"
D = json.load(open(f"{SP}/census-data.json"))
E = D["entries"]


def gkey(l, m):
    g = math.gcd(l, m)
    return (g, l * m // g)


def gname(G):
    return f"Z{G[1]}" if G[0] == 1 else f"Z{G[0]}xZ{G[1]}"


# per group: {k: (d, settled)}; check isomorphic tori agree
grp = defaultdict(dict)
tori_of = defaultdict(set)
conflicts = []
for e in E:
    G = gkey(e["l"], e["m"])
    tori_of[G].add((e["l"], e["m"]))
    prev = grp[G].get(e["k"])
    if prev is not None and prev[0] != e["d"]:
        conflicts.append((G, e["k"], prev, e["d"], (e["l"], e["m"])))
    if prev is None or e["d"] > prev[0]:
        grp[G][e["k"]] = (e["d"], e["settled"])
print("entries", len(E), "groups", len(grp), "tori", sum(len(v) for v in tori_of.values()))
print("isomorphic-torus conflicts:", conflicts)
print("unsettled entries:", [(e["l"], e["m"], e["k"], e["d"], e["stage"]) for e in E if not e["settled"]])

by_order = defaultdict(list)
for G in grp:
    by_order[G[0] * G[1]].append(G)

# ---- claim 1: every group's top within one step (2) of its column top
print("\n== claim 1: group top vs column top (dedup by group)")
short = Counter()
big = []
for N, Gs in sorted(by_order.items()):
    col = max(max(d for d, _ in grp[G].values()) for G in Gs)
    for G in Gs:
        top = max(d for d, _ in grp[G].values())
        short[col - top] += 1
        if col - top > 2:
            big.append((2 * N, gname(G), top, col))
print("shortfall distribution (in d):", dict(sorted(short.items())))
print("groups more than one step below their column top:", big)

# per (n,k): spread across groups of the same order
print("\n== same (n,k), different groups: spread of d")
spread = Counter(); ex = []
for N, Gs in sorted(by_order.items()):
    ks = set().union(*[grp[G].keys() for G in Gs])
    for k in ks:
        ds = [(grp[G][k][0], gname(G)) for G in Gs if k in grp[G]]
        if len(ds) > 1:
            s = max(ds)[0] - min(ds)[0]
            spread[s] += 1
            if s > 2:
                ex.append((2 * N, k, sorted(ds)))
print("spread distribution:", dict(sorted(spread.items())))
for x in ex:
    print("  ", x)

# ---- claim 2: cyclic vs best non-cyclic of same order (column top)
print("\n== claim 2: cyclic top vs best non-cyclic top, same order")
res = Counter(); rows = []
for N, Gs in sorted(by_order.items()):
    cyc = [G for G in Gs if G[0] == 1]
    nc = [G for G in Gs if G[0] > 1]
    if not cyc or not nc:
        if nc:
            rows.append((2 * N, "no cyclic computed", [gname(G) for G in nc]))
        continue
    ct = max(d for d, _ in grp[cyc[0]].values())
    nt = max(max(d for d, _ in grp[G].values()) for G in nc)
    r = "tie" if ct == nt else ("cyclic higher" if ct > nt else "non-cyclic higher")
    res[r] += 1
    rows.append((2 * N, r, ct, nt, [gname(G) for G in nc]))
print(dict(res), "total", sum(res.values()))
for r in rows:
    print("  ", r)

# per-k version: at the same (n,k), cyclic vs best non-cyclic
print("\n== claim 2 at matched k: cyclic vs best non-cyclic at the same (n,k)")
res2 = Counter(); lst = []
for N, Gs in sorted(by_order.items()):
    cyc = [G for G in Gs if G[0] == 1]
    nc = [G for G in Gs if G[0] > 1]
    if not cyc or not nc:
        continue
    for k, (dc, _) in grp[cyc[0]].items():
        dn = [grp[G][k][0] for G in nc if k in grp[G]]
        if not dn:
            continue
        r = "tie" if dc == max(dn) else ("cyclic higher" if dc > max(dn) else "non-cyclic higher")
        res2[r] += 1
        if r == "non-cyclic higher":
            lst.append((2 * N, k, dc, max(dn)))
print(dict(res2))
print("non-cyclic higher at matched k:", lst)

# k_min per group and where each group's top sits
print("\n== k at which each group's top sits; k_min cyclic vs non-cyclic")
kk = Counter()
for N, Gs in sorted(by_order.items()):
    cyc = [G for G in Gs if G[0] == 1]
    for G in Gs:
        kmin = min(grp[G])
        top = max(d for d, _ in grp[G].values())
        ktop = min(k for k, (d, _) in grp[G].items() if d == top)
        kk[("cyc" if G[0] == 1 else "nc", "top at kmin" if ktop == kmin else "top above kmin")] += 1
print(dict(kk))
diffk = []
for N, Gs in sorted(by_order.items()):
    cyc = [G for G in Gs if G[0] == 1]
    if not cyc:
        continue
    kc = min(grp[cyc[0]])
    for G in Gs:
        if G[0] > 1 and min(grp[G]) != kc:
            diffk.append((2 * N, gname(G), min(grp[G]), kc))
print("non-cyclic groups whose k_min differs from the cyclic's:", len(diffk), diffk)
json.dump({gname(G): {str(k): v[0] for k, v in grp[G].items()} for G in grp}, open(
    f"{SP}/regularity/verify-structure-3/groups_kd.json", "w"))
