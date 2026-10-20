"""
Steps 1-2 (baselines): the group-ring objects of many rules, to see whether 4850's are special.

For a rule f (symmetric, any zero eigenvalues handled by the support idempotent e_f = f^(2^18-1)):
    u    = f^511 (unitised)             eigenvalues lambda^511 = lambda(6c)/lambda(c), in mu_513
    u3   = u^3                           (mu_171; mu_19 when f is ninth-confined)
    u19  = u^19 = f^9709                 the 27th-power residue symbol of f (mu_27; mu_3 iff confined)
    B    = f^14820 (14820 = 1 mod 511, 0 mod 57)   the F(2^9)-part when f is ninth-confined
    conf = (u^57 == 1)                   ninth-power confinement, decided in the group ring
For each: weight, and the order of its stabiliser in GL2(Z/37) (exact).

Rules: every ninth-confined rule recorded at radius 4, 5 (data/ninth37.json) and 6
(records.jsonl), the 4850 relatives, the cores W = (0,0)+(2,0)+(2,1)+(2,2) (rule 57) and
V = (3,0)+(3,1)+(3,2)+(3,3) (rule 960), and random rules of radius 4 and 6.
Writes baselines.json.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

LAB = "/home/user/lattice-lab/examples"
A_F29 = 14820
assert A_F29 % 511 == 1 and A_F29 % 57 == 0


def objects(f):
    e = gr.support_idempotent(f)
    fix = gr.ONE ^ e
    u = gr.power(f, 511) ^ fix
    u3 = gr.power(u, 3)
    u19 = gr.power(u, 19)
    B = gr.power(f, A_F29) ^ fix
    conf = bool(np.array_equal(gr.power(u, 57), gr.ONE))
    q27 = bool(np.array_equal(u19, gr.ONE))  # lambda^9709 = 1: 27th powers
    return {"u": u, "u3": u3, "u19": u19, "B": B, "conf": conf, "q27": q27, "e": e}


def describe(n, stab=True):
    f = gr.rule_array(n)
    ob = objects(f)
    rec = {"rule": n, "weight_f": gr.weight(f), "ninth_confined": ob["conf"], "q27": ob["q27"],
           "nonunit": not np.array_equal(ob["e"], gr.ONE ^ gr.JJ)}
    for k in ("u", "u3", "u19", "B"):
        rec[f"w_{k}"] = gr.weight(ob[k])
        if stab:
            rec[f"stab_{k}"] = int(len(gr.stabiliser(ob[k])))
    rec["B_sigma6_invariant"] = gr.invariant_under(ob["B"], 6)
    return rec, ob


def recorded_rules():
    out = {}
    d = json.load(open(f"{LAB}/llm-pilot-37c/data/ninth37.json"))
    for fam in d["families"]:
        for r in fam["ninth_power_rules"]:
            out[r["id"]] = {"radius": fam["radius"], "explained": r["explained"], "procedure": r["procedure"],
                            "logs": r["logs"]}
    for line in open(f"{LAB}/llm-pilot-37c/records.jsonl"):
        r = json.loads(line)
        if "id" not in r:
            continue
        out.setdefault(r["id"], {"radius": 6, "explained": r["explained"], "procedure": r["procedure"],
                                 "logs": r["logs"]})
    return out


def main():
    t0 = time.time()
    rec = recorded_rules()
    special = {4850: "target", 482758: "4850*(1+a)(1+b)", 10491524: "4850 rotated", 8438150: "4850*Phi3(xy)Phi3(x/y)",
               43250486: "4850*Phi3(x)^2Phi3(y)^2", 20982139: "unexplained r6", 178279803: "unexplained r6",
               57: "W core", 960: "V core", 699738: "pilot7", 985232: "pilot7", 1431278: "pilot7", 1968276: "pilot7"}
    rows = []
    for n in sorted(set(rec) | set(special)):
        r, _ = describe(n)
        r.update(rec.get(n, {}))
        r["tag"] = special.get(n, "")
        rows.append(r)
        print(n, r["tag"], {k: r[k] for k in r if k.startswith(("w_", "stab_", "ninth", "nonunit"))}, flush=True)
    print("recorded rules done", round(time.time() - t0, 1), "s")

    rng = np.random.default_rng(20261020)
    rand = []
    for radius, nbits, count, stab_count in ((4, 15, 400, 60), (6, 28, 400, 60)):
        for i in range(count):
            n = int(rng.integers(1, 1 << nbits))
            r, _ = describe(n, stab=i < stab_count)
            r["radius"] = radius
            rand.append(r)
    print("random done", round(time.time() - t0, 1), "s")

    def stats(vals):
        vals = np.array(vals)
        return {"n": int(len(vals)), "min": int(vals.min()), "median": float(np.median(vals)), "max": int(vals.max())}

    summary = {}
    for k in ("w_u", "w_u3", "w_u19", "w_B"):
        summary[k] = {"random": stats([r[k] for r in rand]),
                      "confined_recorded": stats([r[k] for r in rows if r["ninth_confined"]])}
    for k in ("stab_u", "stab_u3", "stab_u19", "stab_B"):
        vals = [r[k] for r in rows if r["ninth_confined"] and k in r]
        summary[k + "_confined_hist"] = {str(v): vals.count(v) for v in sorted(set(vals))}
        vals = [r[k] for r in rand if k in r]
        summary[k + "_random_hist"] = {str(v): vals.count(v) for v in sorted(set(vals))}
    summary["random_ninth_confined"] = sum(r["ninth_confined"] for r in rand)
    print(json.dumps(summary, indent=1))
    with open(os.path.join(gr.HERE, "baselines.json"), "w") as fh:
        json.dump({"summary": summary, "recorded": rows, "random": rand}, fh, indent=1)


if __name__ == "__main__":
    main()
