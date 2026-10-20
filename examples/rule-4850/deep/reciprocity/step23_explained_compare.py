"""Step 23: what the line/reciprocity reformulation looks like for rules the known mechanisms
explain, against 4850.  For each radius-4 ninth-power rule (examples/llm-pilot-37c/data/ninth37.json)
and each class (1, k), is G_k(T) = F(T, D_k(T)) 'cyclotomically complete', i.e. T^a times full
Psi_e's (every GF(2)-factor of each Psi_e that occurs, with one multiplicity)?  Then its class is
pure exponent bookkeeping in <1 + zeta>.  Reported: the classes where it is not."""
import json
from rlib import *

def complete(Q):
    cyc = cyclo_table(600)
    facs = dict(factor2(Q))
    rest = dict(facs)
    rest.pop(0b10, None)
    used = set()
    for p in list(rest):
        if p in used:
            continue
        if p not in cyc:
            return False
        e = cyc[p]
        parts = [q for q, _ in factor2(psi(e))] if e > 1 else [p]
        mult = rest[p]
        for q in parts:
            if rest.get(q) != mult:
                return False
            used.add(q)
    return True

d = json.load(open('/home/user/lattice-lab/examples/llm-pilot-37c/data/ninth37.json'))
KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
rows = []
for fam in d['families']:
    for r in fam['ninth_power_rules']:
        n, rad = r['id'], fam['radius']
        F = rule_F(n, rad)
        bad = []
        for k in KS:
            G = Q_dickson(F, k)
            if G == 0:
                continue
            if not complete(G):
                bad.append(k)
        rows.append((n, rad, r['procedure'], bad))
        print(f'{n:8d} r{rad} {r["procedure"][:45]:45s} non-cyclotomic classes (1,k): {bad}')
