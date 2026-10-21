"""SCIP's own memory accounting vs the process's peak RSS, on a toric run stopped by a time limit."""
import resource, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
T = [(0, 0), (1, 0)], [(0, 0), (0, 1)]
held = []
r = D.distance_ilp(*T, int(sys.argv[2]), int(sys.argv[2]), "Z", time_limit=float(sys.argv[1]), configure=held.append)
mdl = held[0]
print(r["status"], r["lower"], r["upper"], "nodes", r["nodes"])
print("SCIP getMemUsed MB", mdl.getMemUsed() / 2**20, "getMemTotal MB", mdl.getMemTotal() / 2**20,
      "extern MB", mdl.getMemExternEstim() / 2**20, "peak RSS MB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
