# A pre-registered test: the XOR rule's period on n x n tori

The law under test, found by Kepler's exact-law search from LatticeLife runs on n = 3..30 and
committed in `8d7bc58` (2026-10-16):

    period(n) = 2^v(n) * (2^sord(n) - 1)

for B1357/S1357 on an n x n square torus (n not a power of 2). The rival: the torus's period
equals that of the 1D rule 90 on an n-cycle. They part where rule 90 falls short of its bound.

`ledger.jsonl` holds the question and the three sets of predictions (the law, the rival, and a
control), written and pushed before any of the registered runs existed. `study.py run` refuses to
start until they are committed. Check the chain and the order with

```bash
uv run lattice-lab verify --lab examples/xor-periods
git log --format='%h %ad %s' --date=iso -- examples/xor-periods/ledger.jsonl
```

The write-up is in [docs/xor-periods.md](../../docs/xor-periods.md) once the run is judged.
