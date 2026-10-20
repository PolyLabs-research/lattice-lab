"""The budget benchmark's machine grader (examples/consult-budget): true identities hold, false
ones fail, the nine known finds are found, and the model's text cannot run code."""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "consult-budget"))

import bench  # noqa: E402

AB = {"a": "x + x^-1", "b": "y + y^-1"}
UNITS = {"a+b": "a + b", "ab": "a*b", "(a+1)(b+1)": "(a + 1)*(b + 1)"}
CUBED = {"N4+self": "1 + a + b", "D4+self": "1 + a*b", "N4+D4": "a + b + a*b"}
NINE = {
    ("a+b", "N4+self"): 1112, ("a+b", "D4+self"): 10498, ("a+b", "N4+D4"): 13584,
    ("ab", "N4+self"): 2436, ("ab", "D4+self"): 17056, ("ab", "N4+D4"): 28944,
    ("(a+1)(b+1)", "N4+self"): 3461, ("(a+1)(b+1)", "D4+self"): 26883,
    ("(a+1)(b+1)", "N4+D4"): 18246,
}  # fmt: skip


def answer(block: dict) -> str:
    return "Some prose.\n\n```json\n" + json.dumps(block) + "\n```\n"


def test_the_nine_are_found_and_a_wrong_one_is_false():
    facts = [{"rule": n, "factors": [[UNITS[u], 1], [CUBED[g], 3]]} for (u, g), n in NINE.items()]
    wrong = {"rule": 4850, "factors": [["a + b", 1], ["1 + a + b", 3]]}
    out = bench.check(answer({"definitions": AB, "factorisations": facts + [wrong]}))
    assert out["found"] == sorted(NINE.values())
    assert (out["true"], out["false"], out["unreadable"]) == (9, 1, 0)
    # a true factorisation with no cube in it is not a find
    split = [["a + b", 1], ["1 + a + b", 1], ["1 + a + b", 2]]
    out = bench.check(answer({"definitions": AB,
                              "factorisations": [{"rule": 1112, "factors": split}]}))  # fmt: skip
    assert out["true"] == 1 and out["found"] == []


def test_q1_identities():
    dilated = " + ".join(f"x^{6 * p}*y^{6 * q}" for p, q in bench.points([(7, 5)]))
    block = {"definitions": AB, "congruences": [
        {"lhs": "f2(x, y)", "rhs": "a*b*f1(x, y)"},
        {"lhs": "f3(x, y)", "rhs": "(a + b)*f1(x, y)"},
        {"lhs": "f5(x, y)", "rhs": "(a + 1)*(b + 1)*f1(x, y)"},
        {"lhs": "f1(x^2, y^2)*t(x)*t(y)*t(x*y)*t(x/y)", "rhs": "O(7, 5)"},
        # the eight points of O(7, 5), dilated by 6: the set is invariant mod 37
        {"lhs": "O(7, 5)", "rhs": dilated},
        {"lhs": "f4(x, y)*O(19, 19)", "rhs": "O(15, 15) + O(16, 16)"},
        {"lhs": "f2(x, y)", "rhs": "f1(x, y)"},
    ]}  # fmt: skip
    out = bench.check(answer(block))
    assert [c["holds"] for c in out["congruences"]] == [True] * 6 + [False]
    assert (out["true"], out["false"]) == (6, 1)


def test_rule_90_is_confined_by_a_big_power():
    # the certificate form: f^87381 is idempotent, here for t(x) = x + 1/x at 37
    block = {"congruences": [{"lhs": "t(x)^(2*87381)", "rhs": "t(x)^87381"}]}
    assert bench.check(answer(block))["true"] == 1


def test_untrusted_text_is_not_run(tmp_path):
    marker = tmp_path / "ran"
    evil = [f"__import__('os').system('touch {marker}')", "x.__class__", "open('x')",
            "[x for x in y]", "lambda: 1", "eval('1')"]  # fmt: skip
    out = bench.check(answer({"congruences": [{"lhs": e, "rhs": "x"} for e in evil],
                              "definitions": {"__x": "x"}}))  # fmt: skip
    assert out["unreadable"] == len(evil) and out["true"] == out["false"] == 0
    assert not marker.exists()
    assert bench.check("no JSON here")["json"] is False


def _rule(n):
    a = np.zeros((37, 37), dtype=np.uint8)
    for p, q in bench.points(bench.family_orbits(n)):
        a[p % 37, q % 37] ^= 1
    return a


def test_two_findings_of_the_benchmark():
    """Rule 4850 (one of the seven the sixth pilot left to chance) has every nonzero eigenvalue a
    ninth power at 37, and 17056 is 1112 under the exponent map (a, b) -> (a + b, a - b)."""

    def qth_powers(n, q):  # f^((2^18 - 1)/q) idempotent: every nonzero value a q-th power
        e = bench.power(_rule(n), (2**18 - 1) // q)
        return bool((bench.mul(e, e) == e).all())

    assert qth_powers(4850, 3) and qth_powers(4850, 9) and not qth_powers(4850, 27)
    assert not qth_powers(1112, 9) and qth_powers(1112, 3)
    image = {(a + b, a - b) for a, b in bench.points(bench.family_orbits(1112))}
    assert image == bench.points(bench.family_orbits(17056))
