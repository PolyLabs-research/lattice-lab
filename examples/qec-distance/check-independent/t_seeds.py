import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
codes = json.load(open("devcodes2.json"))
for i in [12, 18, 20, 27]:
    c = codes[i]
    res = []
    for seed in (0, 1, 2, 3):
        for kind in "ZX":
            r = D.distance_ilp(c["A"], c["B"], c["l"], c["m"], kind, time_limit=300, seed=seed)
            res.append((seed, kind, r["status"], r["d"], r["nodes"]))
    print(i, c["l"], c["m"], res, flush=True)
