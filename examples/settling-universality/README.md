# A registered universality test: settling times on every lattice

`select.py` draws rules at random on the square, hexagon and triangular (edge, edge+vertex)
lattices, and keeps the first two per lattice that settle. That makes eight rules, chosen by
criteria that never look at the growth law or the fluctuations. `study.py fit` measures them on
tori of 8 to 64, and `study.py register` writes each rule's predictions at 128, 256 and 512:
six laws and two extreme-value mechanisms per rule. It also writes two claims about all eight
at once: one shared shape of the fluctuations (Kelly skewness 0.2215), and one shared ratio of
spread to growth (0.786), the Gumbel values for the largest of about L^2 independent times. It
was committed and pushed (`48176fd`) before any run at the test sizes, and before the B2/S34
replication's verdict.

```bash
uv run python examples/settling-universality/study.py run --workers 4
uv run lattice-lab verify --lab examples/settling-universality
```

Result: the log law held and the power law failed for all eight rules. Both shared claims were
confirmed: shape 0.177 +- 0.023, and ratio 0.765 +- 0.029 (the eight agree, p = 0.64). Per rule,
the Gumbel mechanism passed for seven of the eight. See
[docs/settling-time.md](../../docs/settling-time.md).
