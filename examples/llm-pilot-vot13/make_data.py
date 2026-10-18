"""
The data the agent is given: VO + T13's exact period on the atlas's triangular torus at every
even side from 4 to 64, all sizes computed before this pilot was planned.

    uv run python examples/llm-pilot-vot13/make_data.py
"""

from __future__ import annotations

from pathlib import Path

import exact

HERE = Path(__file__).resolve().parent


def main() -> None:
    lines = ["n,v,m,period"]
    for n in range(4, 65, 2):
        v = (n & -n).bit_length() - 1
        lines.append(f"{n},{v},{n >> v},{exact.period(('VO', 'T13'), n)}")
    (HERE / "data").mkdir(exist_ok=True)
    (HERE / "data" / "vot13_periods.csv").write_text("\n".join(lines) + "\n")
    print(f"wrote {len(lines) - 1} rows")


if __name__ == "__main__":
    main()
