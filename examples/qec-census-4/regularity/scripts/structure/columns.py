"""Rows (even d) and columns (which n carry codes; duplicates from isomorphic tori)."""
from common import *

E = ENTRIES
R = torus_records()
print("entries", len(E), "settled", sum(e["settled"] for e in E))
# ---------------- rows
print("\n== ROWS")
print("odd d among entries:", sum(e["d"] % 2 for e in E))
dl = Counter(e["d"] for e in E)
print("distinct d levels:", len(dl), sorted(dl.items()))
pts = Counter((e["n"], e["d"]) for e in E)
print("distinct (n,d) points:", len(pts), " entries per point mean %.2f" % (len(E) / len(pts)))
# all classes (not just frontier) parity
allrows = [(t, r) for t, v in R.items() for r in v["rows"] if r["d"] is not None]
print("all classes with exact d:", len(allrows), "odd:", sum(r["d"] % 2 for t, r in allrows))

# ---------------- columns
print("\n== COLUMNS")
universe = [(l, m) for l in range(2, 201) for m in range(l, 201) if l * m <= 200]
print("tori 2<=l<=m, lm<=200:", len(universe))
Ns = sorted(set(l * m for l, m in universe))
print("possible N=lm (composite, 4..200):", len(Ns), " possible n=2N:", len(Ns))
withE = sorted(set(l * m for l, m in universe if criterion_e(l, m)))
print("N with criterion E on some torus:", len(withE))
# criterion depends only on N?
byN = defaultdict(set)
for l, m in universe:
    byN[l * m].add(criterion_e(l, m))
print("orders N where tori disagree on criterion E:", [N for N, s in byN.items() if len(s) > 1])
# characterise: primitive qualifying e
def why(N):
    odd = two_part(N)[1]
    return [e for e in (3, 7, 31, 73, 85, 127) if odd % e == 0]
print("N with codes by reason: 3|N:", sum(1 for N in withE if N % 3 == 0),
      " 7|N not 3:", sum(1 for N in withE if N % 3 and N % 7 == 0),
      " other:", [(N, why(N)) for N in withE if N % 3 and N % 7])
print("all even n in [2,400]:", 200, "| n=2N with N composite:", len(Ns), "| with codes:", len(withE))
for lo, hi in [(1, 100), (101, 150), (151, 200)]:
    a = [N for N in Ns if lo <= N <= hi]; b = [N for N in withE if lo <= N <= hi]
    print(f"  N in [{lo},{hi}]: possible {len(a)}, with codes {len(b)} ({len(b)/len(a):.0%})")
# compare with N divisible by 3 or 7 only
print("N<=200 composite with 3|N or 7|N:", sum(1 for N in Ns if N % 3 == 0 or N % 7 == 0))
obsN = sorted(set(e["n"] // 2 for e in E))
print("observed columns:", len(obsN))
missing = [N for N in withE if N not in obsN]
computed = set(R)
for N in missing:
    tori = [(l, m) for l, m in universe if l * m == N]
    print("  predicted column without entries: n=%d tori %s computed %s" % (
        2 * N, tori, [t for t in tori if t in computed]))
print("columns observed but not predicted:", [N for N in obsN if N not in withE])
# stage-4 progress
s4 = [(l, m) for l, m in universe if 150 < l * m <= 200]
print("stage 4 tori:", len(s4), "computed:", sum(t in computed for t in s4),
      " with criterion E:", sum(criterion_e(*t) for t in s4),
      " computed with E:", sum(criterion_e(*t) and t in computed for t in s4))
notdone = [t for t in s4 if t not in computed and criterion_e(*t)]
print("stage-4 tori with codes not yet computed:", notdone)
print("other uncomputed tori in universe (lm<=150):", [t for t in universe if t not in computed and t[0] * t[1] <= 150])

# ---------------- per-column multiplicity, isomorphic duplicates
print("\n== MULTIPLICITY")
byn = defaultdict(list)
for e in E:
    byn[e["n"]].append(e)
tor_per_n = {n: sorted(set((e["l"], e["m"]) for e in es)) for n, es in byn.items()}
grp_per_n = {n: sorted(set(group_key(*t) for t in ts)) for n, ts in tor_per_n.items()}
print("entries per column: mean %.2f, median %s, max %d" % (
    len(E) / len(byn), sorted(len(v) for v in byn.values())[len(byn) // 2], max(len(v) for v in byn.values())))
print("tori per column: mean %.2f, groups per column: mean %.2f" % (
    sum(map(len, tor_per_n.values())) / len(byn), sum(map(len, grp_per_n.values())) / len(byn)))
# dedupe: entries keyed by (group, k)
bygk = defaultdict(list)
for e in E:
    bygk[(group_key(e["l"], e["m"]), e["k"])].append(e)
incons = [(g, [(x["l"], x["m"], x["d"], x["settled"]) for x in es]) for g, es in bygk.items()
          if len(set(x["d"] for x in es)) > 1]
print("(group,k) cells:", len(bygk), " entries:", len(E), " duplicate entries:", len(E) - len(bygk),
      f"({(len(E)-len(bygk))/len(E):.0%})")
print("isomorphic tori disagreeing on best d at same k:", incons)
# k-sets identical across isomorphic tori?
gt = defaultdict(set)
for e in E:
    gt[group_key(e["l"], e["m"])].add((e["l"], e["m"]))
ksets = {t: frozenset((e["k"], e["d"]) for e in E if (e["l"], e["m"]) == t) for g in gt for t in gt[g]}
print("groups:", len(gt), " with >1 torus:", sum(len(v) > 1 for v in gt.values()),
      " groups whose tori have different (k,d) sets:",
      [(g, sorted(gt[g])) for g in gt if len(set(ksets[t] for t in gt[g])) > 1])
dpts = Counter((2 * g[0] * g[1], e) for (g, k), es in bygk.items() for e in [es[0]["d"]])
print("distinct (n,d) points after dedupe:", len(set((2*g[0]*g[1], es[0]["d"]) for (g,k), es in bygk.items())))
print("\ncolumn table: n | tori | groups | entries | dedup entries | k values | d values")
for n in sorted(byn):
    es = byn[n]
    cells = {(group_key(e["l"], e["m"]), e["k"]) for e in es}
    print(f"{n:4d} | {len(tor_per_n[n]):2d} | {len(grp_per_n[n]):2d} | {len(es):3d} | {len(cells):3d} | "
          f"{sorted(set(e['k'] for e in es))} | {sorted(set(e['d'] for e in es))}")
