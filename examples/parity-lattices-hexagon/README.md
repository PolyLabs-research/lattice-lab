# Round 2 of the parity-lattice test: the hexagon's period is rule 90's

[Round 1](../parity-lattices) refuted Kepler's law on the hexagon at n = 74, 148 and 190, each time
by a factor of 3, at odd parts where the 1D rule 90 falls short of 2^sord - 1. Over GF(2),
sigma(x, y)^2 = (x + 1/x)(y + 1/y)(x/y + y/x): two hexagon generations are three passes of rule
90. So the odd part of the hexagon's period is rule 90's period on the odd-part cycle
([docs/parity-lattices.md](../../docs/parity-lattices.md) has the proof).

`ledger.jsonl` holds the corrected law, 2 * 2^v(n) * R(m), at every even n from 202 to 400. It
also holds round 1's law as the rival, the triangles at the seven sizes where the two differ, and
the hexagon transients. All of it was committed and pushed (`f99dafc`) before any of these sizes
was computed.

```bash
uv run python examples/parity-lattices-hexagon/study.py run     # refuses until the registration is committed
uv run lattice-lab verify --lab examples/parity-lattices-hexagon
```

Result: the corrected law was confirmed at all 100 sizes, and the rival refuted at all seven
where it differs (202, 222, 282, 296, 380, 394, 398). Both triangular rules attained the full
bound at those seven sizes, as predicted, and the hexagon transients were confirmed at all 100.
