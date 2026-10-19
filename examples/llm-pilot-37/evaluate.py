"""
Evaluate the agent's `condition` at one m, in a process of its own, for the judge.

    python evaluate.py <tree> <rules.json> <m> <out.json>

It imports mechanism.py from the agent's tree (with the tree and its tools/ on the path), calls
condition(f, m) for every rule, and writes {"m", "seconds", "claims": {rule id: q > 1}, "errors"}.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path


def main() -> None:
    tree, rules_path, m, out = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    sys.path[:0] = [str(tree), str(tree / "tools")]
    import mechanism

    rules = json.loads(rules_path.read_text())
    claims, errors = {}, {}
    start = time.time()
    for rule in rules:
        f = frozenset(map(tuple, rule["terms"]))
        try:
            q = int(mechanism.condition(f, m))
        except Exception:
            errors[rule["id"]] = traceback.format_exc(limit=2)[-500:]
            continue
        if q > 1:
            claims[rule["id"]] = q
    result = {"m": m, "seconds": round(time.time() - start, 1), "claims": claims, "errors": errors}
    Path(out).write_text(json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
