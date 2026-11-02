"""Torus shapes at the column tops vs base rate (shape is irrelevant up to isomorphism)."""
from common import *
E = ENTRIES
top = defaultdict(int)
for e in E:
    top[e["n"]] = max(top[e["n"]], e["d"])
at = [e for e in E if e["d"] == top[e["n"]]]
print("entries at column top:", len(at), "of", len(E))
print("l among top entries:", sorted(Counter(e["l"] for e in at).items()))
print("l among all entries:", sorted(Counter(e["l"] for e in E).items()))
print("top entries on cyclic groups (gcd(l,m)=1):", sum(math.gcd(e["l"], e["m"]) == 1 for e in at), "of", len(at))
print("all entries on cyclic groups:", sum(math.gcd(e["l"], e["m"]) == 1 for e in E), "of", len(E))
# columns where the top is attained only on non-cyclic groups
cols = defaultdict(list)
for e in at:
    cols[e["n"]].append((e["l"], e["m"], group_name(e["l"], e["m"]), e["k"]))
print("columns whose top has no cyclic-group entry:", {n: v for n, v in cols.items() if all(math.gcd(l, m) > 1 for l, m, g, k in v)})
