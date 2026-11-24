"""
Before registering: does a rule's verdict hang on the start? Exploratory.

    uv run --no-sync python examples/scale-up-territories/sizing.py [--workers 2]

The wider screen (examples/scale-up-search/rivals.py) ran all its 4,784 contests from one
start, 11001: every rule met its copy on the same two starting grids, the full one and the
half-full one. A registered test on fresh rules means to say something about rules, so before
its bands are drawn this asks how much of a rule's verdict is the rule and how much is the
grid it happened to start from.

The first 200 rules of the screen's draw are run again exactly as the screen ran them, alone
and against their copies, from another start, 11002. Reported (`sizing.json`): every number
the registered test's claims are about, from each start, and how many rules keep their
verdict from one start to the other.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import territories  # noqa: E402
from territories import contests, rivals, search  # noqa: E402

RULES, START = 200, 11002
OUT = HERE / "sizing"


def seen() -> list[dict]:
    """The same rules as the screen ran them, from its own start: their records cut down to
    what `territories.run_one` keeps."""
    wanted = {r["rule"] for r in rivals.rules()[:RULES]}
    out = []
    for line in (rivals.OUT / "records.jsonl").read_text().splitlines():
        record = json.loads(line)
        if record["rules"][0] in wanted:
            told = contests.describe(record)
            out.append({"kind": "contest", "index": record["index"], "rule": record["rules"][0],
                        "start": record["seed"], "density": record["density"],
                        "tie_break": record["tie_break"], "verdict": told["verdict"],
                        "territories": told["territories"]})  # fmt: skip
    for line in (search.OUT / "records.jsonl").read_text().splitlines():
        record = json.loads(line)
        if record["family"] == "rule" and record["rules"][0] in wanted:
            told = search.describe(record)
            if not any(r["kind"] == "alone" and r["rule"] == record["rules"][0] for r in out):
                out.append({"kind": "alone", "index": record["index"],
                            "rule": record["rules"][0], "start": record["seed"],
                            "called": told["called"]})  # fmt: skip
    return out


def compare(first: list[dict], second: list[dict]) -> dict:
    """How many rules keep their verdict between two sets of records of the same rules."""
    one = {e["rule"]: e for e in territories.entries(first)}
    two = {e["rule"]: e for e in territories.entries(second)}
    rules = sorted(set(one) & set(two))
    same = sum(territories.holds(one[r]) == territories.holds(two[r]) for r in rules)
    gained = [r for r in rules if not territories.holds(one[r]) and territories.holds(two[r])]
    lost = [r for r in rules if territories.holds(one[r]) and not territories.holds(two[r])]
    contests_same = sum(one[r]["verdicts"][where] == two[r]["verdicts"][where]
                        for r in rules for where in one[r]["verdicts"])  # fmt: skip
    alone_same = sum(one[r]["alone"] == two[r]["alone"] for r in rules)
    return {
        "rules": len(rules),
        "hold or not, the same from both starts": same,
        "hold from the second start only": gained,
        "hold from the first start only": lost,
        "the same of both, neither, the standoff only, the draw only": sum(
            one[r]["holds"] == two[r]["holds"] for r in rules),
        "contests": 4 * len(rules),
        "contests with the same verdict": contests_same,
        "called the same alone": alone_same,
    }  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    path = OUT / "records.jsonl"
    done = set()
    if path.exists():
        done = {territories.key(json.loads(line)) for line in path.read_text().splitlines()}
    todo = [job for job in territories.jobs(rivals.rules()[:RULES], START) if job not in done]
    with ProcessPoolExecutor(args.workers) as pool, path.open("a") as sink:
        for record in pool.map(territories.run_one, todo, chunksize=4):
            sink.write(json.dumps(record) + "\n")
            sink.flush()
    second = [json.loads(line) for line in path.read_text().splitlines()]
    first = seen()
    summary = {"rules": RULES, "starts": [search.SEED, START],
               "from the screen's start": territories.measure(first),
               "from the second start": territories.measure(second),
               "between the starts": compare(first, second)}  # fmt: skip
    (HERE / "sizing.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
