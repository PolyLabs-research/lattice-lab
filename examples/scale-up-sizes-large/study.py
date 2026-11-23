"""
The registered scale-up test, part 2 of 2: sides 2048 and 4096, for a rented machine.

    uv run --no-sync python examples/scale-up-sizes-large/study.py register
    uv run --no-sync python examples/scale-up-sizes-large/study.py run --workers 8
    uv run --no-sync lattice-lab verify --lab examples/scale-up-sizes-large

What is asked, what is predicted and how a claim is judged are in
examples/scale-up-sizes/sizes.py, which this part shares with part 1 (sides 512 and 1024). Both
parts were registered before either was run. A run at side 4096 takes about 3 GB of memory and
20 to 25 minutes on one core. The study carries `rerun`, so verify can compute sample records
again.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scale-up-sizes"))

import sizes  # noqa: E402

from lattice_lab.study import main  # noqa: E402

SIDES = (2048, 4096)
SEEDS = tuple(range(4001, 4017))  # 16 starts

STUDY = sizes.build(HERE, SIDES, SEEDS, "2 of 2: sides 2048 and 4096, on a rented machine")

if __name__ == "__main__":
    main(STUDY)
