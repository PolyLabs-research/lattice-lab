"""
Every registered study in the lab (the 33 ledgers), for the dashboards' Predictions page: one row
per study and one per registered prediction, with the outcome its verdict gives it.

Each study records its verdict in its own shape, so each has a reader below that maps the
verdict back onto its predictions. The words used:

- **role:** "claim" (what the study predicted), "candidate" (one of several rival laws or
  mechanisms registered to be tested against each other: a rejected candidate is the test
  working, not a failed claim) or "control".
- **outcome:** "held", "failed", "not tested", "incomplete", "not applicable", "reported"
  (registered to be reported, not judged), "pending" (the run has no verdict yet) or
  "no verdict" (the ledger has none).
- **interim:** true for stage 4, whose verdict is recorded when its run ends: its outcomes are
  what the records say so far.
"""

from __future__ import annotations

import json
from pathlib import Path

AREAS = {
    "Code census": ["qec-census-2", "qec-census-2b", "qec-census-3b", "qec-census-3c",
                    "qec-census-3d", "qec-census-4"],
    "Code distances": ["qec-bb", "qec-distance", "qec-distance-2", "qec-open-distance",
                       "qec-open-distance-2"],
    "Periods and laws": ["xor-periods", "xor-periods-algebra", "parity-lattices",
                         "parity-lattices-hexagon", "linear-atlas", "linear-atlas-2",
                         "linear-atlas-3", "kepler-rediscovery", "hexagon-family", "fable-units",
                         "rule-4850"],
    "LLM pilots": ["llm-pilot", "llm-pilot-triangle", "llm-pilot-vot13", "llm-pilot-25",
                   "llm-pilot-37", "llm-pilot-37b", "llm-pilot-37c"],
    "Settling times": ["lab-b2s34", "settling-time-replication", "settling-universality",
                       "settling-time-local"],
}  # fmt: skip
CODE_AREAS = ("Code census", "Code distances")
WORDS = {"pass": "held", "hold": "held", "holds": "held", "supported": "held",
         "confirmed": "held", "consistent": "held", "yes": "held", "fail": "failed",
         "fails": "failed", "refuted": "failed", "rejected": "failed", "no": "failed",
         "incomplete": "incomplete", "inconclusive": "incomplete", "open": "incomplete",
         "not applicable": "not applicable", "not tested": "not tested"}  # fmt: skip


def word(w) -> str:
    return WORDS.get(w, str(w))


def row(label, text, outcome, role="claim", note=""):
    return {"label": str(label), "text": str(text or "")[:240], "outcome": outcome, "role": role,
            "note": note}  # fmt: skip


def _text(b: dict) -> str:
    for k in ("predict", "claim", "predicted", "law", "test", "decision"):
        if isinstance(b.get(k), str):
            return b[k]
    return ""


# -------------------------------------------------------------------------------- readers
# each takes (the predictions' bodies, the verdict's body or None, context) -> rows, summary


def fable_units(P, v, ctx):
    bad = bool(v["wrong"] or v["missing"])
    out = [row(f"unit, p = {b['p']}" if b["test"] == "unit" else f"{b['test']}, {b['i']}",
               _text(b) or f"predicted {b['predicted']}",
               "incomplete" if bad else "held",
               note="" if not bad else "the verdict lists wrong or missing items")
           for b in P]  # fmt: skip
    return out, f"criterion {v['criterion']}, pyramids {v['pyramids']}; {v['unit']['agree']} of " \
                f"{v['unit']['primes']} primes agree"  # fmt: skip


def hexagon_family(P, v, ctx):
    nt, wrong = set(v["not_tested"]), set(map(str, v["wrong"]))
    out = []
    for b in P:
        key = f"{b['test']}@{b['m']}"
        o = "failed" if key in wrong else "not tested" if key in nt else "held"
        out.append(row(f"{b['test']} at m = {b['m']}", f"odd part {b['predicted']}", o))
    return out, f"{v['classification']}: {v['agree']} of {v['tested']} tested agree"


def kepler_rediscovery(P, v, ctx):
    out = []
    for b in P:
        key = f"{b['dataset']} | {b['stage']}"
        o = "failed" if key in v["refuted"] else "held" if key in v["outcomes"] else "not tested"
        out.append(row(key, b["decision"], o))
    return out, f"{v['confirmed']} confirmed, {len(v['refuted'])} refuted"


def rival_laws(P, v, ctx):
    """lab-b2s34: candidate laws, each surviving its held-out test or not."""
    out = [row(b["law"], b["formula"], "held" if b["law"] in v["survivors"] else "failed",
               role="candidate") for b in P]  # fmt: skip
    return out, f"leading law {v['leading']}; survivors {', '.join(v['survivors'])}"


def linear_atlas(P, v, ctx):
    out = []
    for b in P:
        st = v["rules"][b["rule"]]["status"]
        o = "held" if st == "first law confirmed" else "failed"
        out.append(row(b["rule"], f"the first of its laws, {b['subset']}", o, note=st))
    s = v["summary"]
    return out, "; ".join(
        f"{k}: " + ", ".join(f"{n} {w}" for w, n in d.items()) for k, d in s.items()
    )


def linear_atlas_2(P, v, ctx):
    out = []
    for b in P:
        st = v["rules"][b["rule"]]["status"]
        o = {"held": "held", "failed": "failed"}.get(st, "not tested")
        out.append(row(f"{b['rule']} (part {b['part']})", b.get("law") or b.get("family") or "",
                       o, note="" if o != "not tested" else st))  # fmt: skip
    return out, f"pattern {v['pattern']}; failed: {', '.join(v['failed']) or 'none'}"


def linear_atlas_3(P, v, ctx):
    out = [row(b["rule"], "periods at the sizes it was not computed at",
               word(v["rules"][b["rule"]]["status"])) for b in P]  # fmt: skip
    return out, f"strict statement {v['strict']}; accidents {v['accidents']}; {v['failed']} of " \
                f"{v['predictions']} period predictions failed"  # fmt: skip


def by_size(key_fail):
    def read(P, v, ctx):
        bad = set(v[key_fail])
        out = [row(f"m = {b['m']}", _text(b) or f"{b.get('predicted_unexplained')} unexplained",
                   "failed" if b["m"] in bad else "held") for b in P]  # fmt: skip
        return out, f"{key_fail.replace('_', ' ')}: {', '.join(map(str, v[key_fail])) or 'none'}"

    return read


def llm_pilot_37c(P, v, ctx):
    summary = f"mechanism {v['mechanism']}: {v['unexplained']} unexplained, bar {v['bar']:.1f}"
    return [row(P[0]["test"], P[0]["predicted"], word(v["mechanism"]))], summary


def held_lists(keyf):
    def read(P, v, ctx):
        held = {json.dumps(x) for x in v["held"]}
        failed = {json.dumps(x) for x in v["failed"]}
        missing = {json.dumps(x) for x in v["missing"]}
        out = []
        for b in P:
            k = json.dumps(keyf(b))
            o = "failed" if k in failed else "not tested" if k in missing else \
                "held" if k in held else "incomplete"  # fmt: skip
            out.append(row(f"n = {b['n']}" + (f", rule {b['rule']}" if "rule" in b else ""),
                           f"period {b['predicted']}", o))  # fmt: skip
        return out, f"law {v['law']}; {len(v['held'])} held, {len(v['failed'])} failed"

    return read


def parity_lattices_hexagon(P, v, ctx):
    out = []
    for b in P:
        law = b["law"]
        if law.startswith("rival"):
            out.append(row("rival law", law, "failed" if v["rival_refuted_at"] else "held",
                           role="candidate"))  # fmt: skip
        elif law.startswith("triangles"):
            out.append(
                row("triangle law", law, "failed" if v["triangle_law"]["refuted"] else "held")
            )
        elif law.startswith("hexagon transient"):
            out.append(row("hexagon transient", law,
                           "failed" if v["hexagon_transient_refuted_at"] else "held"))  # fmt: skip
        else:
            out.append(row("hexagon law", law, "failed" if v["hexagon_law"]["refuted"] else "held"))
    h = v["hexagon_law"]
    return out, f"hexagon law confirmed at {h['confirmed']}, refuted at {h['refuted']}; " \
                f"rival refuted at {len(v['rival_refuted_at'])} sizes"  # fmt: skip


def parity_lattices(P, v, ctx):
    out = []
    for b in P:
        if b["law"].startswith("hexagon transient"):
            out.append(row("hexagon transient", b["law"],
                           "failed" if v["hexagon_transient_refuted_at"] else "held"))  # fmt: skip
        else:
            L = v["law"]
            note = f"refuted at {', '.join(L['refuted_at'])}" if L["refuted"] else ""
            out.append(row("period law", b["law"], "failed" if L["refuted"] else "held", note=note))
    L = v["law"]
    return out, f"law confirmed at {L['confirmed']}, refuted at {L['refuted']}"


def xor_periods(P, v, ctx):
    out = []
    for b in P:
        law = b["law"]
        if law.startswith("rival"):
            out.append(row("rival law", law, "failed" if v["rival_refuted_at"] else "held",
                           role="candidate"))  # fmt: skip
        elif law.startswith("control"):
            out.append(row("control", law, "held" if v.get("controls_pass") else "failed",
                           role="control"))  # fmt: skip
        else:
            L = v["law"]
            o = "failed" if L.get("refuted") else "held"
            out.append(row("period law", law, o))
    L = v["law"]
    return out, f"law confirmed at {L['confirmed']} sizes, refuted at {L['refuted']}; rival " \
                f"refuted at {len(v['rival_refuted_at'])}"  # fmt: skip


def rule_4850(P, v, ctx):
    return [row(P[0]["test"], P[0]["predicted"], word(v["coincidence"]))], \
        f"coincidence {v['coincidence']}: {len(v['unexplained'])} unexplained"  # fmt: skip


def settling_local(P, v, ctx):
    out = [row(b["claim"], b["decision"], word(v["statuses"][b["claim"]])) for b in P]
    return out, "; ".join(f"{k}: {s}" for k, s in v["statuses"].items())


def settling_replication(P, v, ctx):
    out = []
    for b in P:
        if b.get("role") == "law":
            out.append(row(b["law"], b.get("formula", ""), word(v["laws"][b["law"]]["status"]),
                           role="candidate"))  # fmt: skip
        else:
            m = b["mechanism"]
            out.append(row(m, b.get("decision", ""), word(v["mechanisms"][m]["status"]),
                           role="candidate"))  # fmt: skip
    return out, f"survivors: {', '.join(v['survivors'])}"


def settling_universality(P, v, ctx):
    out = []
    for b in P:
        if b.get("role") == "universality":
            out.append(row(b["claim"], b["decision"], word(v[b["claim"]]["status"])))
            continue
        rule = v["rules"][f"{b['lattice']} {b['rule']}"]
        if b.get("role") == "law":
            val = rule["laws"][b["law"]]
            st = val["status"] if isinstance(val, dict) else val
            out.append(row(f"{b['lattice']} {b['rule']}: {b['law']}", b.get("formula", ""),
                           word(st), role="candidate"))  # fmt: skip
        else:
            m = b["mechanism"]
            out.append(row(f"{b['lattice']} {b['rule']}: {m}", b.get("decision", ""),
                           word(rule["mechanisms"][m]["status"]), role="candidate"))  # fmt: skip
    return out, f"U1 shape {v['U1 shape']['status']}; U2 amplitude ratio " \
                f"{v['U2 amplitude ratio']['status']}"  # fmt: skip


def qec_bb(P, v, ctx):
    out = []
    for b in P:
        if b["test"] == "method":
            out.append(row("method", b["predicted"], word(v["method"])))
        else:
            ok = v["rediscovery"] == f"{len(v['reproduced'])} of {len(v['reproduced'])}" and \
                not v["source_discrepancies"]  # fmt: skip
            out.append(row("rediscovery", b["predicted"], "held" if ok else "failed"))
    return out, f"method {v['method']}; rediscovery {v['rediscovery']}"


def qec_distance(P, v, ctx):
    out = []
    for b in P:
        t = b["test"]
        if t in ("method-enumeration", "method-dx-dz", "method-toric"):
            out.append(row(t, _text(b), word(v["method"]),
                           note="judged together as 'method': fails at "
                                + ", ".join(v["method_failures"])))  # fmt: skip
        elif t == "method-search":
            c = v["search_counts"]
            out.append(row(t, _text(b), "failed" if c["disagree"] or c["method error"] else "held"))
        else:
            out.append(row(f"rediscovery {b['name']}", f"d = {b['predicted_d']}",
                           word(v["rediscovery"].get(b["name"], "not tested").replace(
                               "reproduced", "pass"))))  # fmt: skip
    return out, f"method {v['method']} (at {', '.join(v['method_failures'])}); " \
                f"{v['counts']['reproduced']} of 12 known distances reproduced"  # fmt: skip


def qec_distance_2(P, v, ctx):
    clean = not any(v["failures"].values()) and not v["missing"]
    out = [row(f"part {b['part']}", _text(b) or "a known code's distance",
               "held" if clean else "incomplete") for b in P]  # fmt: skip
    return out, f"instruments {v['instruments']}; no failures recorded" if clean else \
        f"instruments {v['instruments']}"  # fmt: skip


def parts(P, v, ctx, key="part"):
    out = []
    pv = v.get("parts", v)
    for b in P:
        p = b.get(key) or b.get("id")
        val = pv.get(p)
        if p == "protocol":
            o = "held" if not v.get("protocol_failures") else "failed"
        elif isinstance(val, dict):
            o = "reported"
        else:
            o = word(val) if val is not None else "not tested"
        out.append(row(p, _text(b), o))
    return out, f"verdict {v.get('verdict', '')}"


def stage3b(P, v, ctx):
    v3c = ctx["verdict"]("qec-census-3c")
    out, _ = parts(P, v3c, ctx)
    for r in out:
        r["note"] = "judged with stage 3c's verdict, which covers stage 3b's records"
    return out, f"judged with stage 3c: verdict {v3c['verdict']}"


def stage4(P, v, ctx):
    i4 = ctx["interim4"]
    out = []
    for b in P:
        p = b["part"]
        if p in ("E", "S2"):
            o, note = ("failed", i4[p][0]) if i4[p] else ("pending", "no torus fails it so far")
        elif p in ("G", "S1"):
            o, note = ("held", i4[p][0]) if i4[p] else ("pending", "no torus achieves it so far")
        elif p == "P0":
            o, note = ("failed", i4[p][0]) if i4[p] else ("pending", "no torus fails it so far")
        else:
            o, note = "pending", "judged when the run ends"
        out.append(row(p, _text(b), o, note=note))
    return out, "running: the verdict is recorded when the run ends"


READERS = {
    "fable-units": fable_units, "hexagon-family": hexagon_family,
    "kepler-rediscovery": kepler_rediscovery, "lab-b2s34": rival_laws,
    "linear-atlas": linear_atlas, "linear-atlas-2": linear_atlas_2,
    "linear-atlas-3": linear_atlas_3, "llm-pilot-25": by_size("sizes_beyond_chance"),
    "llm-pilot-37": by_size("sizes_with_exceptions"),
    "llm-pilot-37b": by_size("sizes_beyond_chance"), "llm-pilot-37c": llm_pilot_37c,
    "llm-pilot-triangle": held_lists(lambda b: [b["rule"], b["n"]]),
    "llm-pilot-vot13": held_lists(lambda b: b["n"]), "llm-pilot": held_lists(lambda b: b["n"]),
    "parity-lattices-hexagon": parity_lattices_hexagon, "parity-lattices": parity_lattices,
    "xor-periods": xor_periods, "xor-periods-algebra": xor_periods, "rule-4850": rule_4850,
    "settling-time-local": settling_local, "settling-time-replication": settling_replication,
    "settling-universality": settling_universality, "qec-bb": qec_bb,
    "qec-distance": qec_distance, "qec-distance-2": qec_distance_2,
    "qec-open-distance": parts, "qec-census-2": parts, "qec-census-2b": parts,
    "qec-census-3c": parts, "qec-census-3d": lambda P, v, c: parts(P, v, c, key="id"),
    "qec-census-3b": stage3b, "qec-census-4": stage4,
}  # fmt: skip


def build(examples: Path, interim4: dict) -> tuple[list[dict], list[dict]]:
    ledgers = {}
    for folder in sorted(p.parent.name for p in examples.glob("*/ledger.jsonl")):
        entries = [json.loads(x) for x in (examples / folder / "ledger.jsonl").read_text()
                   .splitlines() if x.strip()]  # fmt: skip
        ledgers[folder] = entries

    def verdict(folder):
        v = [e for e in ledgers[folder] if e["kind"] == "verdict"]
        return v[-1]["body"] if v else None

    ctx = {"verdict": verdict, "interim4": interim4}
    area_of = {f: a for a, fs in AREAS.items() for f in fs}
    studies, preds = [], []
    for folder, entries in ledgers.items():
        q = next(e for e in entries if e["kind"] == "question")
        P = [e for e in entries if e["kind"] == "prediction"]
        v = verdict(folder)
        times = {}
        for e in entries:
            times.setdefault(e["kind"], e["time"])
        if v is None and folder not in ("qec-census-3b", "qec-census-4"):
            rows = [row(b["body"].get("part") or b["body"].get("test") or b["seq"],
                        _text(b["body"]), "no verdict") for b in P]  # fmt: skip
            summary = "no verdict in the ledger"
        else:
            rows, summary = READERS[folder]([b["body"] for b in P], v, ctx)
        interim = folder == "qec-census-4"
        for e, r in zip(P, rows, strict=True):
            preds.append({"key": f"{folder}#{e['seq']}", "study": folder, "seq": e["seq"],
                          "area": area_of[folder], **r, "interim": interim,
                          "registered": e["time"][:16].replace("T", " ")})  # fmt: skip
        claims = [r for r in rows if r["role"] == "claim"]
        cands = [r for r in rows if r["role"] == "candidate"]
        n_claim = len(claims)
        held = sum(r["outcome"] == "held" for r in claims)
        failed = sum(r["outcome"] == "failed" for r in claims)
        # neutral outcomes (not applicable, reported, not tested) leave a study held; blocking
        # ones (incomplete, pending) make it incomplete. A study of candidates alone holds when
        # some candidate survives.
        blocking = sum(r["outcome"] in ("incomplete", "pending") for r in claims)
        if not rows or all(r["outcome"] == "no verdict" for r in rows):
            outcome = "no verdict"
        elif interim:
            outcome = "pending"
        elif not claims:
            outcome = "held" if any(r["outcome"] == "held" for r in cands) else "failed"
        elif failed:
            outcome = "mixed" if held else "failed"
        elif blocking:
            outcome = "incomplete"
        else:
            outcome = "held"
        studies.append({
            "study": folder, "title": q["body"].get("title") or q["body"].get("id") or folder,
            "area": area_of[folder], "codes": area_of[folder] in CODE_AREAS,
            "registered": q["time"][:16].replace("T", " "),
            "run_started": (times.get("run_started") or "")[:16].replace("T", " ") or None,
            "verdict_time": (times.get("verdict") or "")[:16].replace("T", " ") or None,
            "predictions": len(rows), "claims": n_claim, "claims_held": held,
            "claims_failed": failed, "claims_other": n_claim - held - failed,
            "candidates": len(cands),
            "candidates_survived": sum(r["outcome"] == "held" for r in cands),
            "candidates_rejected": sum(r["outcome"] == "failed" for r in cands),
            "controls": sum(r["role"] == "control" for r in rows),
            "outcome": outcome, "interim": interim, "summary": summary,
        })  # fmt: skip
    return studies, preds
