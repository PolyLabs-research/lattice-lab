"""Per-group (deduplicated) frontier: which groups sit on the envelope; does structure predict d, k?"""
from common import *
import numpy as np

E = ENTRIES
G = defaultdict(dict)      # group -> k -> best d (max over isomorphic tori; settled preferred)
tor = defaultdict(set)
for e in E:
    g = group_key(e["l"], e["m"])
    tor[g].add((e["l"], e["m"]))
    if e["k"] not in G[g] or e["d"] > G[g][e["k"]]:
        G[g][e["k"]] = e["d"]


def inv(g):
    a, b = g
    N = a * b
    pp = pparts(*g)
    r2 = sum(1 for x in pp.get(2, (0, 0)) if x > 0)
    r3 = sum(1 for x in pp.get(3, (0, 0)) if x > 0)
    sq = any(min(v) > 0 for p, v in pp.items())  # non-cyclic
    return dict(N=N, n=2 * N, cyclic=(a == 1), r2=r2, r3=r3, v2=two_part(N)[0],
                three=(N % 3 == 0), seven=(N % 7 == 0), odd=two_part(N)[1],
                Eodd=odd_exponent(*g))


rows = []
for g, kd in G.items():
    I = inv(g)
    kmin = min(kd)
    best = max(kd.values())
    rows.append(dict(g=g, **I, kmin=kmin, dbest=best, d_at_kmin=kd[kmin],
                     kset=sorted(kd), smax=max(k * d * d / I["n"] for k, d in kd.items()),
                     kd=kd, tori=sorted(tor[g])))
rows.sort(key=lambda r: (r["n"], r["g"]))

# 1. column maxima: which k, which group type
print("== column maxima (dedup by group)")
byn = defaultdict(list)
for r in rows:
    byn[r["n"]].append(r)
col = []
for n, rs in sorted(byn.items()):
    top = max(r["dbest"] for r in rs)
    winners = [r for r in rs if r["dbest"] == top]
    ks_at_top = sorted(set(k for r in winners for k, d in r["kd"].items() if d == top))
    col.append((n, top, ks_at_top, [r["g"] for r in winners], [r["g"] for r in rs]))
cls = Counter()
for n, top, ks, win, allg in col:
    N = n // 2
    c = "3|N" if N % 3 == 0 else ("7|N" if N % 7 == 0 else "other")
    cls[(c, tuple(ks))] += 1
print("column-max k by column class:", dict(cls))
print("is best d always at the torus's smallest k?",
      sum(r["dbest"] == r["d_at_kmin"] for r in rows), "of", len(rows), "groups")
bad = [(r["g"], r["kd"]) for r in rows if r["dbest"] != r["d_at_kmin"]]
print("   exceptions:", bad)
# monotone in k per group?
nonmono = []
for r in rows:
    ks = sorted(r["kd"])
    ds = [r["kd"][k] for k in ks]
    if any(ds[i + 1] > ds[i] for i in range(len(ds) - 1)):
        nonmono.append((r["g"], list(zip(ks, ds))))
print("groups where best d is NOT non-increasing in k:", len(nonmono), nonmono[:10])

# 2. ratio d/sqrt(n) by column class
print("\n== column max d/sqrt(n) by class")
for c in ("3|N", "7|N", "other"):
    v = [(n, top / math.sqrt(n)) for n, top, ks, w, a in col
         if (("3|N" if (n // 2) % 3 == 0 else ("7|N" if (n // 2) % 7 == 0 else "other")) == c)]
    print(c, len(v), "mean ratio %.3f" % np.mean([x for _, x in v]), [(n, round(x, 3)) for n, x in v][:60])

# 3. within-column comparisons between groups (same N), at k = kmin
print("\n== same-order comparisons (best d at the group's min k; best d at k=4 if any)")
for n, rs in sorted(byn.items()):
    if len(rs) < 2:
        continue
    desc = []
    for r in rs:
        desc.append(f"{'Z%d' % r['g'][1] if r['g'][0]==1 else 'Z%dxZ%d' % r['g']}"
                    f"[r2={r['r2']},r3={r['r3']}] kmin={r['kmin']} d={r['d_at_kmin']} "
                    f"smax={r['smax']:.2f} kset={r['kset']}")
    print(n, " | ".join(desc))
json.dump([{k: (v if k != "kd" else {str(a): b for a, b in v.items()}) for k, v in r.items()} for r in rows],
          open("groups.json", "w"), default=str, indent=0)
