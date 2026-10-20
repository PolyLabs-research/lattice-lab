"""Rule 4850's ninth powers at m = 37 (examples/rule-4850): the fast census agrees with the
group-ring counts, and the five unexplained ninth-power rules, rechecked by eigen.py."""

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "rule-4850"))
sys.path.insert(0, str(ROOT / "examples" / "linear-atlas-3"))

import census  # noqa: E402
import eigen  # noqa: E402

NINTH_RADIUS_4 = [1, 7, 13, 41, 82, 233, 577, 644, 800, 873, 1023, 1057, 3394, 4850, 5665,
                  17409, 18436, 23615, 27268, 28359, 32767]  # fmt: skip
UNEXPLAINED = [4850, 482758, 699738, 985232, 1431278, 1968276]


def test_the_census_reproduces_the_radius_4_counts():
    logs = census.class_logs(4)
    assert {q: int(census.confined(logs, q)[1:].sum()) for q in (3, 9, 27)} == {
        3: 110, 9: 21, 27: 4
    }  # fmt: skip
    nine = census.confined(logs, 9)
    assert [n for n in range(1, len(nine)) if nine[n]] == NINTH_RADIUS_4


def test_the_six_are_ninth_powers_at_37_and_482758_is_4850_times_rule_7():
    for n in UNEXPLAINED:
        assert eigen.odd_part(census.rule(n), 37) == (2**18 - 1) // 9, n
    product = Counter((p + r, q + s) for p, q in census.rule(4850) for r, s in census.rule(7))
    assert frozenset(k for k, v in product.items() if v % 2) == census.rule(482758)
