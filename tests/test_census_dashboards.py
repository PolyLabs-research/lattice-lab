"""The census dashboards' data layer (examples/qec-census-4/dashboards/build.py) against the
records: counts reconcile, isomorphic tori agree, the known codes and checks are where the
write-ups put them, and the frontier is the census explorer's."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "examples" / "qec-census-4" / "dashboards" / "build.py"
EXPLORER = ROOT / "examples" / "qec-census-4" / "explorer" / "build_data.py"

pytestmark = pytest.mark.skipif(not (ROOT / "examples" / "qec-census-4" / "records.jsonl").exists(),
                                reason="census records not present")  # fmt: skip


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def data():
    return _load("census_dashboards_build", BUILD).build()


def test_reconciles(data):
    b = _load("census_dashboards_build", BUILD)
    assert b.check(data) == []


def test_frontier_is_the_explorers(data):
    ex = _load("census_explorer_build", EXPLORER).entries()
    mine = {(e["l"], e["m"], e["k"]): (e["d"], e["settled"]) for e in data["frontier"]}
    theirs = {(e["l"], e["m"], e["k"]): (e["d"], e["settled"]) for e in ex}
    assert mine == theirs


def test_every_torus_once(data):
    tori = data["tori"]
    assert len(tori) == len({t["torus"] for t in tori}) == 116 + 122 + 110
    by_stage = {s: sum(t["stage"] == s for t in tori) for s in ("3a", "3b/3c", "4")}
    assert by_stage == {"3a": 116, "3b/3c": 122, "4": 110}


def test_stage4_tori_are_the_studys():
    b = _load("census_dashboards_build", BUILD)
    src = (ROOT / "examples" / "qec-census-4" / "study.py").read_text()
    # study.tori() and EXPOSED, restated in build.py: compare the source lines that define them
    assert "if 150 < ell * m <= 200" in src and "range(2, 15)" in src and "range(ell, 101)" in src
    exposed = "EXPOSED = [(6, 30), (11, 14), (12, 13), (13, 13), (13, 14), (14, 14)]"
    assert exposed in src
    assert b.S4_EXPOSED == {(6, 30), (11, 14), (12, 13), (13, 13), (13, 14), (14, 14)}
    assert len(b.S4_TORI) == 110


def test_known_codes(data):
    fr = {e["id"]: e for e in data["frontier"]}
    assert (fr["5x31-k10"]["d"], fr["5x31-k10"]["tier"]) == (22, "second method")
    assert (fr["5x21-k10"]["d"], fr["5x21-k10"]["tier"]) == (16, "certified")
    for t in ("3x45", "5x27", "2x69", "3x46", "6x23", "3x47", "2x72", "4x36", "3x49"):
        e = fr[f"{t}-k4"]
        assert (e["d"], e["settled"], e["settled_by"]) == (24, True, "stage 3d (DistQLDPC)")
    # 9x15 (exposed, not rerun by stage 3d) stays unsettled; its isomorphic twin 3x45 is settled
    assert (fr["9x15-k4"]["settled"], fr["9x15-k4"]["iso_settled_torus"]) == (False, "3x45")


def test_spotcheck_tiers(data):
    from collections import Counter

    b = _load("census_dashboards_build", BUILD)
    judge = json.loads(b.SPOT_JUDGE.read_text())["tiers"]
    assert Counter(judge.values()) == {"certified": 9, "second method": 9,
                                       "second implementation": 10}  # fmt: skip
    tiers = Counter(e["tier"] for e in data["frontier"] if e["tier"] != "not checked")
    # 3x47 and 3x49 were checked at d = 22, before stage 3d raised them to 24
    assert tiers == {"certified": 9, "second method": 10, "second implementation": 8}


def test_witnesses_are_logicals(data):
    """A sample of the frontier's witnesses, each checked as a logical of weight d."""
    dist = _load("qec_distance_distance", ROOT / "examples" / "qec-distance" / "distance.py")
    for e in data["frontier"][::40]:
        if not e["witness"]:
            continue
        A = [tuple(t) for t in json.loads(e["A"])]
        B = [tuple(t) for t in json.loads(e["B"])]
        w = dist.verify_witness(A, B, e["l"], e["m"], "Z", json.loads(e["witness"]))
        assert w["logical"] and w["weight"] == e["d"], e["id"]


def test_summary_counts(data):
    s = {r["metric"]: r for r in data["summary"]}
    assert s["tori_total"]["value"] == 348
    assert s["frontier_entries"]["value"] == len(data["frontier"])
    assert s["classes"]["value"] == sum(t["classes"] or 0 for t in data["tori"])
