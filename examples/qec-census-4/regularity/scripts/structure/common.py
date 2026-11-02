"""Shared helpers: load census entries, per-torus records, group invariants, criterion E."""
import json, math, glob, functools
from pathlib import Path
from collections import defaultdict, Counter

SP = Path("/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad")
EX = Path("/home/user/lattice-lab/examples")
D = json.load(open(SP / "census-data.json"))
ENTRIES = D["entries"]
PUBLISHED = D["published"]


def two_part(x):
    s = 0
    while x % 2 == 0:
        x //= 2; s += 1
    return s, x


def factor(n):
    f, p = {}, 2
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1; n //= p
        p += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def group_key(l, m):
    """Z_l x Z_m ~ Z_g x Z_(lm/g), g = gcd: invariant factors (g, lcm)."""
    g = math.gcd(l, m)
    return (g, l * m // g)


def group_name(l, m):
    g, L = group_key(l, m)
    return f"Z{L}" if g == 1 else f"Z{g}xZ{L}"


def pparts(l, m):
    """p -> (a, b) exponents of p in the two invariant factors (rank-2 abelian group)."""
    g, L = group_key(l, m)
    out = {}
    for p in set(factor(g)) | set(factor(L)):
        out[p] = (factor(g).get(p, 0), factor(L).get(p, 0))
    return out


# ---- criterion E via GF(2)[x] gcd ------------------------------------------------------------
def _pmod(a, b):
    db = b.bit_length()
    while a.bit_length() >= db:
        a ^= b << (a.bit_length() - db)
    return a


def _pgcd(a, b):
    while b:
        a, b = b, _pmod(a, b)
    return a


def _pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1; b >>= 1
    return r


def _ppow(a, e):
    r = 1
    while e:
        if e & 1:
            r = _pmul(r, a)
        a = _pmul(a, a); e >>= 1
    return r


def ord2(e):
    r, x = 1, 2 % e
    while x != 1:
        x = x * 2 % e; r += 1
    return r


@functools.lru_cache(None)
def qualifies(e):
    """e odd > 1: mu_e holds a != 1 with 1 + a in mu_e  <=>  gcd(x^e + 1, (x+1)^e + 1) != 1 over GF(2)
    (x = 1 is not a root of the second, x = 0 not of the first)."""
    f = (1 << e) | 1
    g = _ppow(0b11, e) ^ 1
    return _pgcd(f, g).bit_length() > 1


def odd_exponent(l, m):
    return math.lcm(two_part(l)[1], two_part(m)[1])


def criterion_e(l, m):
    E = odd_exponent(l, m)
    return any(qualifies(e) for e in range(3, E + 1, 2) if E % e == 0)


def minimal_qualifying(E):
    return [e for e in range(3, E + 1, 2) if E % e == 0 and qualifies(e)
            and not any(qualifies(f) for f in range(3, e, 2) if e % f == 0)]


# ---- per-torus records (all stages) -----------------------------------------------------------
def torus_records():
    """(l, m) -> dict(stage, criterion_e, classes, rows=[{k,d,connected}]) for every computed torus."""
    out = {}
    for p in sorted(glob.glob(str(EX / "qec-census-3" / "data" / "*.jsonl"))):
        lines = [json.loads(x) for x in open(p) if x.strip()]
        head = lines[0]
        rows = [{"k": r["k"], "d": r.get("d"), "connected": r.get("connected"),
                 "complete": r.get("status") == "complete", "A": r.get("A"), "B": r.get("B")}
                for r in lines[1:]]
        out[(head["l"], head["m"])] = {"stage": "3a", "rows": rows, "classes": len(rows),
                                       "criterion_e": None}
    for folder, stage in (("qec-census-3b", "3b/3c"), ("qec-census-3c", "3b/3c"),
                          ("qec-census-4", "4")):
        for x in open(EX / folder / "records.jsonl"):
            r = json.loads(x)
            if r.get("job") != "torus" or "error" in r:
                continue
            rows = []
            for y in r["rows"]:
                ex = y.get("exact") or {}
                rows.append({"k": y["k"], "d": ex.get("d") if ex.get("status") == "complete" else None,
                             "connected": y["connected"], "complete": ex.get("status") == "complete",
                             "upper": y.get("upper"), "A": y.get("A"), "B": y.get("B")})
            out[(r["l"], r["m"])] = {"stage": stage, "rows": rows, "classes": r["classes"],
                                     "criterion_e": r.get("criterion_e"),
                                     "best": r["best"]}
    return out
