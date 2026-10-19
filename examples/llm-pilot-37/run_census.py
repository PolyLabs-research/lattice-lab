"""
Run census.unexplained over a range of odd m, appending one line per m to a JSONL file, so a long
run can be watched and resumed.

    uv run python examples/llm-pilot-37/run_census.py <lo> <hi> <out.jsonl>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import census


def main() -> None:
    lo, hi, path = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
    done = set()
    if path.exists():
        done = {json.loads(line)["m"] for line in path.read_text().splitlines() if line}
    for m in census.cube_sizes(lo, hi):
        if m in done:
            continue
        start = time.time()
        rows = census.unexplained(m)
        with open(path, "a") as f:
            f.write(json.dumps({"m": m, "seconds": round(time.time() - start, 1),
                                "unexplained": rows}) + "\n")  # fmt: skip


if __name__ == "__main__":
    main()
