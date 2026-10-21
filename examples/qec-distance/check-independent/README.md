# The independent checker's development records

Scratch from the independent check of `distance.py`, made before registration and kept because
`study.py`'s `excluded_seen` refers to it. The checker wrote its own enumeration, an LP-free
check-driven search (`dfs.c`, since rewritten as `../search.c`), and one integer program per
logical in HiGHS and SCIP. It then compared them with `distance_ilp`, `distance_brute` and
d_X = d_Z on development codes only: no published entry and no code at a published torus type.

- `devcodes.json` and `devcodes2.json` are the development codes.
- `mine.jsonl`, `cmpA.jsonl`, `cmpB.jsonl` and `large.jsonl` are the comparisons.
- The `t_*.py` files are its spot checks.

It found no disagreement. The scripts are not part of the study and are excluded from lint.
