"""
Step 4i: the simplest form of the relatives' identities.

In R1's frame (R1 = 10491524, r = diag(1, 27)): is
    R_target = (r^i R1) * t(x)^e1 * t(y)^e2 * B,   B F(2^9)-valued, off the axis lines,
for some i in {0, 1, 2} and e1, e2 mod 513?  (t(x) = x + 1/x: rule 90 along x.)  Solved on the
f18 line logs (mod 27 and mod 19, brute force), then verified exactly in the group ring and checked
for the D4 images.  Also: the phi-eigencomponents of R1's mu_19 vector against those of t(x), t(y).
Writes twist_unit.json.
"""
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
import f18  # noqa: E402

M = 37
LINES = [(1, k) for k in range(M)] + [(0, 1)]
OFF = [i for i, jk in enumerate(LINES) if jk not in ((1, 0), (0, 1))]
D = ((1, 0), (0, 27))


def logs(f):
    return np.array([f18.log(gr.eig(f, *jk)) if gr.eig(f, *jk) else -1 for jk in LINES], dtype=np.int64)


def inv(f):
    return gr.power(f, 2**18 - 2) ^ gr.ONE ^ gr.support_idempotent(f)


def main():
    f18.full_log_table()
    out = {}
    R1 = gr.rule_array(10491524)
    tx = gr.from_points([(1, 0), (-1, 0)])
    ty = gr.from_points([(0, 1), (0, -1)])
    Lx, Ly = logs(tx), logs(ty)
    tw = [R1, gr.act(R1, D), gr.act(gr.act(R1, D), D)]
    Ltw = [logs(t) for t in tw]
    for target in (20982139, 178279803, 10491524):
        Rt = gr.rule_array(target)
        b = logs(Rt)
        res = []
        for i in range(3):
            diff = (b - Ltw[i])
            for mod in (19, 27):
                pass
            sol = {}
            for mod in (19, 27):
                hits = []
                for e1, e2 in itertools.product(range(mod), repeat=2):
                    if all((diff[j] - e1 * Lx[j] - e2 * Ly[j]) % mod == 0 for j in OFF):
                        hits.append((e1, e2))
                sol[mod] = hits
            if sol[19] and sol[27]:
                res.append({"i": i, "mod19": sol[19][:4], "mod27": sol[27][:4]})
        out[str(target)] = res
        print(target, "= r^i R1 * t(x)^e1 t(y)^e2 * F(2^9) off-axis:", res if res else "no")
    # exact group-ring verification of the solutions found
    Ex = np.zeros((M, M), dtype=np.uint8); Ex[:, 0] = 1
    Ey = np.zeros((M, M), dtype=np.uint8); Ey[0, :] = 1
    Eax = Ex ^ Ey ^ gr.JJ
    for target, res in out.items():
        for s in res:
            e19 = s["mod19"][0]
            for e27 in s["mod27"]:
                # CRT to mod 513
                e = tuple(next(x for x in range(513) if x % 19 == e19[k] and x % 27 == e27[k]) for k in range(2))
                den = gr.mul(tw[s["i"]], gr.mul(gr.power(tx, e[0]), gr.power(ty, e[1])))
                # den vanishes on the axis lines (t(x) at j = 0, t(y) at k = 0): invert off-axis only
                Q = gr.mul(gr.rule_array(int(target)), inv(den))
                Q511 = gr.power(Q, 511)
                ok = bool(np.array_equal(gr.mul(Q511 ^ gr.ONE, gr.ONE ^ Eax), np.zeros_like(Q)))
                s.setdefault("verified", []).append({"e_mod513": e, "group_ring_offaxis": ok})
                print("   verified", target, "i =", s["i"], "e =", e, ":", ok)
                break
    with open(os.path.join(gr.HERE, "twist_unit.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
