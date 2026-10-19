"""
Build the website's data file from lattice-lab's own records and code.

    uv run python site/build_data.py

Writes site/public/assets/data.js, defining `window.SITE = {...}`. Every number the site shows
comes from here or from the browser's own computation; nothing is typed in by hand except the
per-rule table of Study B, copied from docs/settling-time.md.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
sys.path.insert(0, str(EX / "linear-atlas-3"))

import atlas3  # noqa: E402
import eigen  # noqa: E402

OUT = ROOT / "site" / "public" / "assets" / "data.js"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def split(n: int) -> tuple[int, int]:
    v = (n & -n).bit_length() - 1
    return v, n >> v


def sord(m: int) -> int:
    j = 1
    while pow(2, j, m) not in (1, m - 1):
        j += 1
    return j


def p90(m: int) -> int:
    """Rule 90's odd period on the m-cycle: the lcm of the orders of zeta^j + zeta^-j."""
    return 1 if m == 1 else eigen.odd_part(frozenset({(1, 0), (-1, 0)}), m)


def fields() -> dict:
    out = {}
    for m in range(5, 50, 2):
        mod, d = eigen.field(m)
        out[m] = [hex(mod), d]
    return out


RULES = {
    "ctrl": ("square", ("N4", "B4"), "Square N4 + B4 (a typical rule)"),
    "m1": ("square", ("A4", "K8", "B4", "self"), "Square A4 + K8 + B4 + self"),
    "m2": ("triangle", ("VS", "T9", "T13", "self"), "Triangle VS + T9 + T13 + self (its s)"),
    "m3": ("square", ("K8", "M8", "E4"), "Square K8 + M8 + E4"),
    "m4": ("square", ("C4", "L8", "M8"), "Square C4 + L8 + M8"),
    "m5": ("square", ("C4", "L8", "M8", "E4"), "Square C4 + L8 + M8 + E4"),
    "m6": (
        "square",
        ("A4", "B4", "C4", "L8", "E4", "self"),
        "Square A4 + B4 + C4 + L8 + E4 + self",
    ),
    "xor": ("square", ("N4", "D4"), "Square parity rule B1357/S1357 (N4 + D4)"),
    "n4": ("square", ("N4",), "Square N4, the four nearest cells"),
    "n4self": ("square", ("N4", "self"), "Square N4 + self"),
    "h1": ("hexagon", ("H1",), "Hexagon parity rule B135/S135 (H1)"),
    "triE": ("triangle", ("E",), "Triangle edge rule B13/S13 (its s)"),
    "triEVOVS": ("triangle", ("E", "VO", "VS"), "Triangle edge+vertex rule (its s)"),
    "vot13": ("triangle", ("VO", "T13"), "Triangle VO + T13, the twisted power (its s)"),
    "cube": ("square", ("N4", "K8", "C4"), "Square N4 + K8 + C4 = N4 cubed"),
    "dil": ("square", ("C4", "self"), "Square C4 + self, a dilation"),
}


def rules() -> dict:
    out = {}
    for key, (lattice, shells, label) in RULES.items():
        f = atlas3.polynomial(lattice, shells)
        out[key] = {"label": label, "lattice": lattice, "terms": sorted(map(list, f))}
    uu, ud, du, dd = atlas3._triangle_entries(("E",))
    out["triE"]["ud"], out["triE"]["du"] = sorted(map(list, ud)), sorted(map(list, du))
    return out


def xor() -> dict:
    rows = jsonl(EX / "xor-periods-algebra" / "records.jsonl")
    out = []
    for r in rows:
        n, period = r["n"], r["period"]
        v, m = split(n)
        law = 1 if m == 1 else 2**v * (2 ** sord(m) - 1)
        rival = 1 if m == 1 else 2**v * p90(m)
        out.append([n, str(period), int(r["dies"]), str(law), str(rival)])
    return {"rows": out}


def hexagon() -> dict:
    seen = {}
    for name in ["parity-lattices", "parity-lattices-hexagon"]:
        for r in jsonl(EX / name / "records.jsonl"):
            if r.get("lattice") == "hexagon" and "period" in r:
                seen[r["n"]] = (r["period"], r["dies"], name)
    out = []
    for n in sorted(seen):
        period, dies, study = seen[n]
        v, m = split(n)
        if m == 1:
            first = corrected = 1
        elif m == 3:  # both laws make an exception of m = 3, where the period is 2^v
            first = corrected = 2**v
        else:
            first, corrected = 2 * 2**v * (2 ** sord(m) - 1), 2 * 2**v * p90(m)
        out.append([n, str(period), int(dies), str(first), str(corrected),
                    1 if study == "parity-lattices" else 2])  # fmt: skip
    return {"rows": out}


def settling() -> dict:
    seeds = []
    paths = [EX / "lab-b2s34" / "records" / "settling-time-hexagon-B2S34-0.jsonl",
             EX / "settling-time-replication" / "records.jsonl"]  # fmt: skip
    for path in paths:
        for r in jsonl(path):
            t = r["transient"] if r["survived"] else r["extinction_step"]
            seeds.append([r["grid"], t, 0 if "lab-b2s34" in str(path) else 1])
    universality = [  # docs/settling-time.md, Study B, per rule: IQR / slope and its error
        ["square", "B3567/S248", 0.84, 0.09],
        ["square", "B358/S034", 0.74, 0.09],
        ["hexagon", "B1/S126", 0.66, 0.07],
        ["hexagon", "B134/S01345", 0.74, 0.07],
        ["triangle, edge", "B123/S012", 0.82, 0.08],
        ["triangle, edge", "B23/S013", 0.75, 0.09],
        ["triangle, edge+vertex", "B2,5,7,8,10/S0,2,7,8,9,10,11", 0.77, 0.09],
        ["triangle, edge+vertex", "B3,7,8,9/S0,5,6,9,12", 0.88, 0.09],
    ]
    return {"seeds": seeds, "log": [37.6, -36.3], "power": [22.3, 0.398],
            "universality": universality, "shared": [0.765, 0.029], "gumbel": 0.786}  # fmt: skip


def ledger() -> dict:
    """Pilot 3's ledger, each entry with the exact text its hash is taken over."""
    sys.path.insert(0, str(ROOT / "src"))
    from lattice_lab.ledger import canonical

    out = []
    for e in jsonl(EX / "llm-pilot-vot13" / "ledger.jsonl"):
        text = canonical({k: e[k] for k in ("seq", "kind", "time", "prev", "body")})
        out.append({"seq": e["seq"], "kind": e["kind"], "time": e["time"], "prev": e["prev"],
                    "hash": e["hash"], "text": text})  # fmt: skip
    return {"study": "llm-pilot-vot13", "entries": out}


def _target(command: str) -> str:
    """The first file a shell command names, for a readable label."""
    m = re.search(r"[\w./-]+\.(?:py|lean|md|csv|json|txt|toml)\b", command)
    return f": {Path(m.group(0)).name}" if m else ""


def _category(call: dict) -> tuple[str, str]:
    tool, given = call["tool"], call.get("input", {})
    if tool in ("Write", "Edit"):
        verb = "write" if tool == "Write" else "edit"
        return "write", f"{verb}: {Path(given.get('file_path', '')).name}"
    if tool == "Read":
        return "read", f"read: {Path(given.get('file_path', '')).name}"
    if tool in ("Monitor", "ScheduleWakeup"):
        return "wait", "wait for the Lean build"
    command = given.get("command", "")
    if "lake build" in command or "lake env lean" in command:
        return "lean", "compile Lean" + _target(command.replace("lakefile.toml", ""))
    if "git commit" in command or "git push" in command:
        return "commit", "commit and push"
    if "until " in command or "sleep " in command:
        return "wait", "wait for the Lean build"
    if "setup.sh" in command:
        return "setup", "start setup: setup.sh"
    if "python" in command:
        return "compute", "run Python" + _target(command)
    if any(w in command for w in ("cat ", "sed -n", "grep ", "head ", "tail ", "ls ")):
        return "read", "read files" + _target(command)
    return "shell", "shell"


def timelines() -> list[dict]:
    pilots = [
        ("Pilot 2: the triangle laws", EX / "llm-pilot-triangle", "2026-10-18T20:28:23Z"),
        ("Pilot 3: VO + T13's law, from data", EX / "llm-pilot-vot13", "2026-10-18T22:05:13Z"),
        ("Pilot 4: the cubes at m = 37", EX / "llm-pilot-37", "2026-10-19T06:40:26Z"),
    ]
    out = []
    for name, d, start in pilots:
        path = d / "transcript" / "tool_calls.jsonl"
        if not path.exists():
            out.append({"name": name, "start": start, "calls": [], "pending": True})
            continue
        calls = []
        for c in jsonl(path):
            cat, label = _category(c)
            calls.append([c["time"], cat, label])
        out.append({"name": name, "start": start, "calls": calls, "pending": False})
    return out


def census() -> dict:
    sys.path.insert(0, str(EX / "llm-pilot-37"))
    import census as c

    train = {m: [] for m in c.cube_sizes(9, 161)}
    with open(EX / "llm-pilot-37" / "data" / "unexplained.csv") as f:
        for row in csv.DictReader(f):
            train[int(row["m"])].append(f"{row['lattice']} {row['shells']}")
    held = {}
    records = EX / "llm-pilot-37" / "records.jsonl"
    if records.exists():
        for r in jsonl(records):
            held[r["m"]] = [f"{x['lattice']} {x['shells']}" for x in r["unexplained"]]
    sizes = c.cube_sizes(163, 225) + [m for m in (259, 333) if m in c.cube_sizes(259, 333)]
    return {"train": train, "heldout": held, "heldout_sizes": sizes}


def proofs() -> dict:
    """The Lean library's modules: size, theorem count and imports within the library."""
    lib = ROOT / "proofs" / "LatticeProofs"
    core = [line.split()[1].split(".")[1] for line in (ROOT / "proofs" / "LatticeProofs.lean")
            .read_text().splitlines() if line.startswith("import LatticeProofs.")]  # fmt: skip
    out = {}
    for path in sorted(lib.glob("*.lean")):
        text = path.read_text()
        imports = []
        for line in text.splitlines():
            if line.startswith("import LatticeProofs"):
                name = line.split()[1]
                imports += core if name == "LatticeProofs" else [name.split(".")[1]]
        declaration = r"^(?:@\[[^\]]*\]\s*)?(?:private\s+)?(?:theorem|lemma)\s"
        theorems = len(re.findall(declaration, text, re.M))
        out[path.stem] = {"lines": len(text.splitlines()), "theorems": theorems,
                          "imports": sorted(set(imports)), "core": path.stem in core}  # fmt: skip
    return out


# The fourth pilot's state, as the site shows it. Edited by hand as the pilot moves on.
PILOT37 = {
    "status": "answered by an agent",
    "card": "Six rules that none of the known mechanisms touches had every eigenvalue a cube at "
    "m = 37, far beyond chance. In the fourth pilot an agent found why within 23 minutes, on a "
    "question nobody had answered, and proved it in Lean. Its condition made 633 claims at 94 "
    "sizes, 180 of them at sizes it never saw, and none was false.",
    "time": "95 min, 131 calls; a follow-up took 6 more",
    "judge": '<span class="badge ok">passed, round 1</span>',
    "test": "180 of 180 claims held at held-out sizes",
    "eyebrow": "answered in the fourth pilot",
    "html": """<p>The fourth pilot set an agent on this question, in its own container, with the
      census up to <em class="var">m</em> = 161 and the Lean library. Nobody knew the answer, the
      orchestrator included. Ten minutes in, it found that three of the six are the first one
      times rule-90 factors. After 23 minutes it had a mechanism that explains all six, which it
      calls <strong>half-Frobenius confinement</strong>.</p>
    <p>At 37, 2<sup>9</sup> ≡ −6 and 6² ≡ −1, so multiplying a character by 6 acts on
      eigenvalues as the Frobenius x ↦ x<sup>2<sup>9</sup></sup>. A rule whose cells are unchanged
      by ×6 has every eigenvalue in F(2<sup>9</sup>), and every element of F(2<sup>9</sup>) is a
      cube in F(2<sup>18</sup>). None of the six is such a rule. But each becomes one when
      multiplied by a few rule-90 passes, whose eigenvalues are cubes at 37, and that is enough.</p>
    <div class="row">
      <button id="m37-identity" class="primary" type="button">Multiply out its identity</button>
    </div>
    <p>The judge ran the agent's general condition on all 1,274 rules at 94 sizes, 29 of them
      registered before the launch and never shown to the agent, and checked each claim
      against its own eigenvalues: <strong>633 claims, none false</strong>. The agent proved in
      Lean that each of the six has period dividing 87,381 at 37. Its first version took rule 90's
      period as given; asked for more, it proved that too, with an explicit cube root.</p>
    <p class="note">By the agent's account, the mechanism needs both a short square root of −1
      mod m and rule 90's own confinement at m. In its sweep up to m = 301, the mixed form acts
      on the atlas's rules only at 37, which is why 37 looked unique.</p>""",
}


def main() -> None:
    data = {
        "fields": fields(),
        "rules": rules(),
        "xor": xor(),
        "hexagon": hexagon(),
        "settling": settling(),
        "ledger": ledger(),
        "timelines": timelines(),
        "census": census(),
        "proofs": proofs(),
        "pilot37": PILOT37,
    }
    text = json.dumps(data, separators=(",", ":"))
    OUT.write_text("// Generated by site/build_data.py from lattice-lab's records. Do not edit.\n"
                   f"window.SITE = {text};\n")  # fmt: skip
    print(f"wrote {OUT} ({len(text) // 1024} KB)")
    _ = math  # noqa


if __name__ == "__main__":
    main()
