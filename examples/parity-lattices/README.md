# Parity rules on the hexagonal and triangular lattices: discovery and round 1

`discover.py` runs the parity rule on LatticeLife's hexagonal lattice (B135/S135) and on its
triangular lattice, in both neighbourhoods (edge: B13/S13; edge+vertex:
B1,3,5,7,9,11/S1,3,5,7,9,11). Each run starts from a single live cell, on every even n x n
torus from 6 to 60. Kepler's `find_integer_laws` then searches the periods and finds one law for
all three (`discovery.jsonl`, `laws.json`):

    P(n) = 2 * 2^v(n) * (2^sord(n) - 1)

`lattices.py` computes periods exactly, as orders in the torus's group ring. Before registration
it reproduced all 84 simulated periods and transients. `ledger.jsonl` holds the predictions at
every even n from 62 to 200 on all three lattices, committed and pushed (`bc47043`) before the
engine ran on any of those sizes.

```bash
uv run python examples/parity-lattices/discover.py
uv run python examples/parity-lattices/study.py run       # refuses until the registration is committed
uv run lattice-lab verify --lab examples/parity-lattices
```

Result: 207 of 210 confirmed. The law held on both triangular lattices at all 70 sizes. On the
hexagon it failed at n = 74, 148 and 190, each time by exactly a factor of 3. The explanation and
a proof (the hexagon's odd period is rule 90's) are in
[docs/parity-lattices.md](../../docs/parity-lattices.md). Round 2, the corrected law, is in
[../parity-lattices-hexagon](../parity-lattices-hexagon).
