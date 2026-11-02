"""Independent check of the column claim against the raw census records and census-data.json."""
import json, math, glob, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SP = Path("/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad")
EX = Path("/home/user/lattice-lab/examples")
Q = {int(e): v["qualifies"] for e, v in json.load(open(HERE / "qual.json")).items()}


def odd(x):
    while x % 2 == 0:
        x //= 2
    return x


def critE(l, m):
    E = odd(math.lcm(l, m))
    return any(Q[e] for e in range(3, E + 1, 2) if E % e == 0)


def isprime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** .5) + 1))


def group(l, m):
    g = math.gcd(l, m)
    # invariant factors of Z_l x Z_m are (g, lm/g); canonical as sorted elementary divisors
    def pp(n):
        out = []
        p = 2
        while n > 1:
            if n % p == 0:
                q = 1
                while n % p == 0:
                    n //= p; q *= p
                out.append(q)
            p += 1
        return out
    return tuple(sorted(pp(g) + pp(l * m // g)))


universe = [(l, m) for l in range(2, 201) for m in range(l, 201) if l * m <= 200]
print("universe tori (2<=l<=m, lm<=200):", len(universe))
Ns = sorted({l * m for l, m in universe})
print("distinct lm:", len(Ns), " composite 4..200:", sum(1 for N in range(4, 201) if not isprime(N)),
      " equal:", Ns == [N for N in range(4, 201) if not isprime(N)])

byN = defaultdict(set)
for l, m in universe:
    byN[l * m].add(critE(l, m))
assert all(len(s) == 1 for s in byN.values())
withE = sorted(N for N in Ns if critE(*next((l, m) for l, m in universe if l * m == N)))
simple = sorted(N for N in Ns if any(N % c == 0 for c in (3, 7, 31, 73, 85)))
print("lm with criterion E:", len(withE), " == divisible by 3,7,31,73,85:", withE == simple)
m6 = [2 * N for N in withE if N % 3 == 0]
m14 = [2 * N for N in withE if N % 3 and N % 7 == 0]
rest = [2 * N for N in withE if N % 3 and N % 7]
print("n multiple of 6:", len(m6), m6[0], m6[-1], " multiples of 14 (not 6):", len(m14), m14, " rest:", rest)
print("multiples of 6 from 12..396 all present:", m6 == list(range(12, 397, 6)))

# ---- records -------------------------------------------------------------------------------
rec = {}
for p in sorted(glob.glob(str(EX / "qec-census-3" / "data" / "*.jsonl"))):
    lines = [json.loads(x) for x in open(p) if x.strip()]
    h = lines[0]
    rows = lines[1:]
    rec[(h["l"], h["m"])] = dict(stage="3a", crit=None, classes=h["classes"], nrows=len(rows),
                                 kpos=sum(r["k"] > 0 for r in rows),
                                 conn=sum(bool(r["connected"]) and r["k"] > 0 for r in rows),
                                 raw_kpos=h.get("raw_k_positive"))
for folder, st in (("qec-census-3b", "3b"), ("qec-census-3c", "3c"), ("qec-census-4", "4")):
    for x in open(EX / folder / "records.jsonl"):
        if not x.strip():
            continue
        r = json.loads(x)
        if r.get("job") != "torus":
            print("non-torus record in", folder, r.get("job")); continue
        if "error" in r:
            print("error record", folder, r["l"], r["m"]); continue
        key = (r["l"], r["m"])
        if key in rec:
            print("duplicate torus record", key, rec[key]["stage"], st)
        rec[key] = dict(stage=st, crit=r.get("criterion_e"), classes=r["classes"], nrows=len(r["rows"]),
                        kpos=sum(y["k"] > 0 for y in r["rows"]),
                        conn=sum(bool(y["connected"]) and y["k"] > 0 for y in r["rows"]), raw_kpos=None)
print("computed tori:", len(rec), " by stage:", {s: sum(v["stage"] == s for v in rec.values()) for s in ("3a", "3b", "3c", "4")})
print("computed tori outside universe:", [t for t in rec if t not in universe])
mm_field, mm_classes, mm_rows = [], [], []
for t, v in rec.items():
    c = critE(*t)
    if v["crit"] is not None and v["crit"] != c:
        mm_field.append((t, v["crit"], c))
    if (v["classes"] > 0) != c:
        mm_classes.append((t, v["classes"], c))
    if v["nrows"] != v["classes"]:
        mm_rows.append((t, v["nrows"], v["classes"]))
print("mismatch record criterion_e field vs mine:", mm_field, " (records carrying the field:",
      sum(v["crit"] is not None for v in rec.values()), ")")
print("mismatch classes>0 vs mine:", mm_classes)
print("rows != classes:", mm_rows[:10], len(mm_rows))
noconn = [t for t, v in rec.items() if critE(*t) and v["conn"] == 0]
print("tori with criterion E but no connected k>0 class:", noconn)
print("tori with E:", sum(critE(*t) for t in rec), " without:", sum(not critE(*t) for t in rec))

uncomputed = [t for t in universe if t not in rec]
print("uncomputed tori:", len(uncomputed))
s4 = [t for t in universe if 150 < t[0] * t[1] <= 200]
print("stage-4 universe:", len(s4), " computed:", sum(t in rec for t in s4))
unc_old = [t for t in uncomputed if t[0] * t[1] <= 150]
print("uncomputed with lm<=150:", unc_old, " each isomorphic to a computed torus:",
      all(any(group(*t) == group(*u) for u in rec) for t in unc_old))

# ---- census-data.json columns ---------------------------------------------------------------
D = json.load(open(SP / "census-data.json"))
E = D["entries"]
obs_n = sorted({e["n"] for e in E})
print("observed columns:", len(obs_n))
pred_n = [2 * N for N in withE]
print("observed not predicted:", [n for n in obs_n if n not in pred_n])
miss = [n for n in pred_n if n not in obs_n]
print("predicted not observed:", miss)
for n in miss:
    ts = [t for t in universe if 2 * t[0] * t[1] == n]
    print("   n=%d tori %s computed %s groups %s" % (n, ts, [t for t in ts if t in rec], sorted({group(*t) for t in ts})))
# do the entries' tori match records?
ent_tori = {(e["l"], e["m"]) for e in E}
print("entry tori not in records:", [t for t in ent_tori if t not in rec])
# per-column: tori with E computed vs tori contributing entries
cols_partial = []
for N in withE:
    ts = [t for t in universe if t[0] * t[1] == N]
    done = [t for t in ts if t in rec]
    if done and len(done) < len(ts):
        cols_partial.append((2 * N, [t for t in ts if t not in rec]))
print("columns observed but with some tori not yet computed:", cols_partial)
# stage-4 uncomputed with E, deduplicated by group
s4u = [t for t in s4 if t not in rec and critE(*t)]
grp_new = sorted({group(*t) for t in s4u if not any(group(*t) == group(*u) for u in rec)})
print("stage-4 uncomputed tori with E:", len(s4u), s4u)
print("  of which groups with no computed isomorphic torus:", len(grp_new), grp_new)
s4nE = [t for t in s4 if t not in rec and not critE(*t)]
print("stage-4 uncomputed tori without E:", s4nE)

# dedupe columns by group: how many distinct groups carry codes
grpsE = {group(*t) for t in universe if critE(*t)}
print("distinct groups (lm<=200, l,m>=2) with E:", len(grpsE), " of", len({group(*t) for t in universe}))
