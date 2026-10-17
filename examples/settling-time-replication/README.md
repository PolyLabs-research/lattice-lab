# A registered replication: B2/S34 settling times on hexagon tori up to 1024

The example lab ([../lab-b2s34](../lab-b2s34)) found the median settling time of B2/S34 soups on
hexagon tori of 8 to 128 to be logarithmic in the size, with a power law 8.4 BIC points behind.
`study.py` registers both laws' predictions at L = 192 to 1024 (100 seeds each), with two
mechanisms that predict the seed-to-seed fluctuations from each law's constants
(extreme values with light tails, Gumbel; with heavy tails, Frechet). It was committed and pushed
(`d9a7823`) before any run at these sizes.

```bash
uv run python examples/settling-time-replication/study.py run      # refuses until registered and pushed
uv run lattice-lab verify --lab examples/settling-time-replication --rerun 3
```

Result: the log law replicated (p = 0.15, 6 of 6 inside their bands), and the power law was
rejected (p = 10^-9). The heavy-tailed mechanism was rejected outright. The Gumbel mechanism got
the shape and the constancy of the fluctuations right but their size wrong (an interquartile
range of 20 against 29.6 predicted). See [docs/settling-time.md](../../docs/settling-time.md).
