# Round 2: what B2/S34's local settling times say

Study A ([../settling-time-replication](../settling-time-replication)) left a post-hoc idea: a tail
prefactor fading with L, to explain a falling slope and a narrow spread. `study.py` tests the
assumptions behind it on local settling times. These come from LatticeLife's
`experiments.local`: when each 8 x 8 or 16 x 16 block of a torus enters the soup's final cycle.
The study runs 60 fresh soups on tori of 1024 and 320 on 256. Every prediction was fixed from
Study A's data and pushed (`525b0f5`) before any local transient of B2/S34 was computed.

```bash
uv run python examples/settling-time-local/study.py run --workers 4
uv run lattice-lab verify --lab examples/settling-time-local
```

Result: the local tail is the same at 256 and 1024 (stationary), but late blocks cluster (97%
have a late neighbour, against 4% if independent), so independence is rejected. The tail's
prefactor is undetermined (k = 4.2 +- 3.1). After the verdict, the same runs' global settling
times show Study A's narrow spread was a low draw. Pooled, B2/S34's ratio of spread to slope is
0.765 +- 0.042, Gumbel's. See [docs/settling-time.md](../../docs/settling-time.md#round-2-what-the-local-settling-times-say).
