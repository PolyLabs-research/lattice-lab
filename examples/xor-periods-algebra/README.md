# Round 2 of the XOR period test: exact periods by algebra

The law from [round 1](../xor-periods) predicts the longest period of B1357/S1357 on the n x n
torus. Simulation cannot reach sizes whose periods run to millions of generations or more;
`algebra.py` computes the period exactly, as the order of the rule's polynomial in
GF(2)[x,y]/(x^n - 1, y^n - 1), from the prime factors of the candidate period rather than by
stepping through it. Before registration it reproduced every simulated period.

`ledger.jsonl` holds the predictions for every n from 3 to 200 (the law, and rule 90's period as
the rival), written and pushed before the computation ran on any new size.

```bash
uv run python examples/xor-periods-algebra/study.py run     # refuses until the registration is committed
uv run lattice-lab verify --lab examples/xor-periods-algebra
```
