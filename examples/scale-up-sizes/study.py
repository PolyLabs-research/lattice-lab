"""
The registered scale-up test, part 1 of 2: sides 512 and 1024, run on the lab's own machine.

    uv run --no-sync python examples/scale-up-sizes/study.py register
    uv run --no-sync python examples/scale-up-sizes/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-sizes

What is asked, what is predicted and how a claim is judged are in sizes.py, which this part
shares with examples/scale-up-sizes-large (sides 2048 and 4096). Both parts were registered
before either was run. The study carries `rerun`, so verify can compute sample records again.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sizes  # noqa: E402

from lattice_lab.study import main  # noqa: E402

SIDES = (512, 1024)
SEEDS = tuple(range(3001, 3033))  # 32 starts

STUDY = sizes.build(HERE, SIDES, SEEDS, "1 of 2: sides 512 and 1024, on the lab's own machine")

if __name__ == "__main__":
    main(STUDY)
