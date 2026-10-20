"""Mechanisms 1-8 (atlas3.predict, pilot 7's condition) on the members of every cube-level
(cube, not ninth) cluster of rules sharing a full mod-27 pattern with a coprime partner
(cube_cluster_ids.json, from gcd_clusters.json). Writes condition_clusters.jsonl."""
import json, signal, sys
sys.path[:0] = ["/home/user/pilot-37c-round2", "/home/user/lattice-lab/examples/rule-4850",
                "/home/user/lattice-lab/examples/linear-atlas-3"]
import atlas3, census, mechanism
HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
N18 = 2**18 - 1
signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))


def level(logs):
    nz = [v for v in logs if v != 27]
    if all(v % 9 == 0 for v in nz):
        return "ninth"
    return "cube" if all(v % 3 == 0 for v in nz) else "other"


G = json.load(open(f"{HERE}/gcd_clusters.json"))
need = sorted({i for fam in G for cl in G[fam]["clusters"]
               if level(cl["logs"]) == "cube" and any(d == 0 for _, _, d in cl["gcd_degrees"])
               for i in cl["ids"]})
json.dump(need, open(f"{HERE}/cube_cluster_ids.json", "w"))
out = open(f"{HERE}/condition_clusters.jsonl", "w")
for rid in need:
    f = census.rule(rid, 6)
    row = {"id": rid}
    try:
        signal.alarm(60)
        odd, why = atlas3.predict(f, 37)
        row["atlas_explains"] = bool("splits" in why or (odd is not None and (N18 // 3) % odd == 0))
    except TimeoutError:
        row["atlas_explains"] = False
    signal.alarm(0)
    try:
        signal.alarm(60)
        q = mechanism.condition(f, 37)
        row["q"], row["cond_explains"] = int(q), q % 3 == 0
    except TimeoutError:
        row["q"], row["cond_explains"] = None, False
    signal.alarm(0)
    row["explained"] = row["atlas_explains"] or row["cond_explains"]
    out.write(json.dumps(row) + "\n"); out.flush()
