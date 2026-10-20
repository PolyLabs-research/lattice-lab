"""
Step 4h: non-vacuity of the partial-twist identity X = R1^a (rR1)^b (r^2R1)^c * (F(2^9)-valued) off
the axis lines (R1 = 10491524, r = diag(1,27)).  For random radius-6 rules X and for every
recorded ninth-confined rule X: does some (a, b, c) mod 513 work?  (mod 19 and mod 27 separately,
then CRT; solved by brute force over (a, b, c).)  Also the analogous span of the partial twists of
other confined rules Y (is R2 in Y's span?), to see whether the span phenomenon is specific.
Writes vacuity_twist.json.
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
r = ((1, 0), (0, 27))


def logs(f):
    v = [f18.log(gr.eig(f, *jk)) for jk in LINES]
    return None if any(x is None for x in v) else np.array(v, dtype=np.int64)


def twists(f):
    return [f, gr.act(f, r), gr.act(gr.act(f, r), r)]


def coeff_grid(mod):
    return np.array(list(itertools.product(range(mod), repeat=3)), dtype=np.int64)


G19, G27 = coeff_grid(19), coeff_grid(27)


def in_span(cols, b):
    A = np.stack([c[OFF] for c in cols], axis=0)  # (3, 36)
    ok = {}
    for mod, G in ((19, G19), (27, G27)):
        S = (G @ (A % mod) - b[OFF] % mod) % mod
        hits = np.flatnonzero((S == 0).all(axis=1))
        ok[mod] = G[hits[:3]].tolist()
    return ok


def main():
    f18.full_log_table()
    out = {}
    R1 = gr.rule_array(10491524)
    cols = [logs(t) for t in twists(R1)]
    # random rules
    rng = np.random.default_rng(13)
    n19 = n27 = nboth = tried = 0
    while tried < 1000:
        x = int(rng.integers(1, 1 << 28))
        b = logs(gr.rule_array(x))
        if b is None:
            continue
        tried += 1
        s = in_span(cols, b)
        n19 += bool(s[19]); n27 += bool(s[27]); nboth += bool(s[19]) and bool(s[27])
    out["random"] = {"tried": tried, "in_span_mod19": n19, "in_span_mod27": n27, "both": nboth}
    print("random radius-6 rules in span{R1, rR1, r^2R1} off-axis:", out["random"])
    # recorded ninth-confined rules
    rec = json.load(open(os.path.join(gr.HERE, "baselines.json")))["recorded"]
    hits = []
    for rr in rec:
        if not rr["ninth_confined"]:
            continue
        b = logs(gr.rule_array(rr["rule"]))
        if b is None:
            continue
        s = in_span(cols, b)
        if s[19] and s[27]:
            hits.append((rr["rule"], s[19][0]))
    out["recorded_confined_in_span"] = hits
    print("recorded ninth-confined rules in the span (mod 19 and 27):", hits)
    # specificity: spans of other confined unit rules' partial twists (in the same frame) that
    # contain some other recorded confined rule nontrivially
    others = [rr["rule"] for rr in rec if rr["ninth_confined"] and rr["rule"] not in (10491524, 20982139, 178279803)]
    cnt = 0
    found = []
    for y in others[:60]:
        fy = gr.rule_array(y)
        cy = [logs(t) for t in twists(fy)]
        if any(c is None for c in cy):
            continue
        # is the span 3-dimensional mod 19 (nondegenerate)?
        cnt += 1
        for z in others[:60]:
            if z == y:
                continue
            b = logs(gr.rule_array(z))
            if b is None:
                continue
            s = in_span(cy, b)
            if s[19] and s[27] and any(sum(1 for v in c if v % 19) > 1 for c in s[19]):
                found.append((y, z))
    out["other_spans_checked"] = cnt
    out["other_span_hits"] = found[:30]
    print("other confined rules Y (", cnt, "): pairs (Y, Z) with Z in span of Y's twists (nontrivially):", found[:30])
    with open(os.path.join(gr.HERE, "vacuity_twist.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
