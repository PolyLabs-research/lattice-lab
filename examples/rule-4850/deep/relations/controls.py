"""Locate the known certificates among the stored control hits (results_small_off.json)
and confirm the exact factorisations they rest on.   python controls.py"""
import json
import sys
sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
import shells  # noqa: E402
import run_targets as RT  # noqa: E402
import tables  # noqa: E402

C = tables.C


def number(S):
    rem, num = set(S), 0
    for i, o in enumerate(C.orbits(6)):
        pts = C.points(o)
        if pts <= rem:
            num |= 1 << i
            rem -= pts
    assert not rem
    return num


P5x = frozenset({(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)})  # Psi5(a) = 1 + a + a^2
P5y = frozenset((q, p) for p, q in P5x)
U2 = shells.lmul(P5x, P5y)
U3 = shells.lmul(U2, RT.expset(2))
n2, n3 = number(U2), number(U3)
print("Psi5(a)Psi5(b) = rule", n2, "; Psi5(a)Psi5(b)(a+b) = rule", n3)
print("699738 == Psi5Psi5(a+b) * W exactly:", shells.lmul(U3, RT.expset(57)) == RT.expset(699738))
print("1431278 == Psi5Psi5 * V exactly:", shells.lmul(U2, RT.expset(960)) == RT.expset(1431278))
r = {x["rule"]: x for x in json.load(open("results_small_off.json"))}
want = {57: [(10, None, 1, 128)], 960: [(10, None, 1, 4)], 699738: [(0, 8, 128, n3)],
        1431278: [(0, 8, 4, n2)]}
for n, ws in want.items():
    if n not in r:
        print(n, "not in results")
        continue
    hits = r[n].get("genuine", []) + r[n].get("all", [])
    for gp, dp, m1, m2 in ws:
        f = [h for h in hits if h["gp"] == gp and (dp is None or h["dp"] == dp)
             and h["M1"] == m1 and h["M2"] == m2]
        print(n, "certificate (gp, dp, M1, M2) =", (gp, dp, m1, m2), "found:", len(f) > 0, f[:1])
