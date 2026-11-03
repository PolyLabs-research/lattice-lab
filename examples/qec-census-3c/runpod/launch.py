"""
Create, inspect and stop the census and spot-check pods through RunPod's REST API
(docs/runpod-setup.md).

    python examples/qec-census-3c/runpod/launch.py create [--job JOB] [--vcpu N] [--dry-run]
    python examples/qec-census-3c/runpod/launch.py list
    python examples/qec-census-3c/runpod/launch.py status POD_ID
    python examples/qec-census-3c/runpod/launch.py stop POD_ID
    python examples/qec-census-3c/runpod/launch.py delete POD_ID

The API key comes from the environment (RUNPOD_API_KEY) when it is set; otherwise the request is
sent without one, for a proxy that adds it. It only acts on pods named in JOBS: `list` shows only
those, and `status`, `stop` and `delete` refuse any other pod, so a pod of yours running something
else is never touched.

The jobs: `census-3c` (stage 3c, pod-run.sh here), `census-3d` (stage 3d,
examples/qec-census-3d/pod-run.sh) and `spotcheck` (the stage 3b/3c spot-check,
examples/qec-census-3b/spotcheck/pod-run.sh, with a large container disk for the DRAT proofs).

The pod: a CPU pod, compute-optimized (cpu5c, then cpu3c), on-demand in Secure Cloud. RunPod
gives CPU pods no pod volume (volumeInGb comes back 0), so /workspace is on the container disk and
a restart clones afresh; the records survive because they are pushed within 2 minutes.
Its start command installs git, clones the branch (or rebases an existing clone onto it), and runs
pod-run.sh, at every start. The GitHub token reaches the pod as the
RunPod secret `lattice_lab_github_token`, which RunPod substitutes when the pod boots; this script
never sees it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://rest.runpod.io/v1"
JOBS = {
    "census-3c": {"name": "lattice-lab-census-3c", "vcpu": 8, "disk": 20, "volume": 20,
                  "script": "examples/qec-census-3c/runpod/pod-run.sh"},
    "check-310": {"name": "lattice-lab-check-310", "vcpu": 8, "disk": 80, "volume": None,
                  "script": "examples/qec-census-4/check-310/pod-run.sh"},
    "census-4": {"name": "lattice-lab-census-4", "vcpu": 32, "disk": 60, "volume": None,
                 "script": "examples/qec-census-4/pod-run.sh"},
    "census-4-recheck": {"name": "lattice-lab-census-4-validate", "vcpu": 32, "disk": 40,
                         "volume": None, "script": "examples/qec-census-4/pod-validate.sh recheck"},
    "census-4-validate": {"name": "lattice-lab-census-4-validate", "vcpu": 32, "disk": 40,
                          "volume": None, "script": "examples/qec-census-4/pod-validate.sh"},
    "census-3d": {"name": "lattice-lab-census-3d", "vcpu": 32, "disk": 40, "volume": None,
                  "script": "examples/qec-census-3d/pod-run.sh"},
    "census-4d": {"name": "lattice-lab-census-4d", "vcpu": 32, "disk": 40, "volume": None,
                  "script": "examples/qec-census-4d/pod-run.sh"},
    # cpu5c allows 15 GB of disk per vCPU, cpu3c 10: 300 GB fits both at 32 vCPU
    "spotcheck": {"name": "lattice-lab-spotcheck", "vcpu": 32, "disk": 300, "volume": None,
                  "script": "examples/qec-census-3b/spotcheck/pod-run.sh"},
}  # fmt: skip
NAMES = {j["name"] for j in JOBS.values()}
BRANCH = "ccr-ab9f0bb1-qb20sx"
REPO = "github.com/PolyLabs-research/lattice-lab.git"
SECRET = "lattice_lab_github_token"

START = """export DEBIAN_FRONTEND=noninteractive
fail() {{
  echo "POD START FAILED: $*"; echo "(the pod waits here; stop or delete it with launch.py)"
  sleep infinity
}}
apt-get update -q && apt-get install -yq git ca-certificates || fail "apt-get could not install git"
GH_TOKEN=$(printf %s "$GH_TOKEN" | tr -d '[:space:]')
case "$GH_TOKEN" in
  "{{{{"*|"") fail "GH_TOKEN is not set: create the RunPod secret {SECRET}";;
esac
URL="https://x-access-token:$GH_TOKEN@{REPO}"
if ! out=$(git ls-remote --heads "$URL" {BRANCH} 2>&1); then
  fail "the token cannot read {REPO}: $(echo "$out" | sed "s/$GH_TOKEN/***/g" | tail -3)"
fi
[ -n "$out" ] || fail "branch {BRANCH} not found on {REPO}"
mkdir -p /workspace && cd /workspace || fail "no /workspace"
if [ -d lattice-lab/.git ]; then
  git -C lattice-lab pull -q --rebase --autostash origin {BRANCH} \\
    || {{ echo "UPDATE FAILED: running the pod-run.sh already on the volume"; \\
         git -C lattice-lab rebase --abort 2>/dev/null; }}
else
  git clone -q --branch {BRANCH} "$URL" lattice-lab 2>&1 | sed "s/$GH_TOKEN/***/g"
  [ -d lattice-lab/.git ] || fail "git clone failed"
fi
echo "pod start: cloned, running pod-run.sh"
exec bash lattice-lab/{SCRIPT}
"""


def start(job: str) -> str:
    return START.format(SECRET=SECRET, REPO=REPO, BRANCH=BRANCH, SCRIPT=JOBS[job]["script"])


def body(job: str, vcpu: int | None = None) -> dict:
    j = JOBS[job]
    return {
        "name": j["name"],
        "computeType": "CPU",
        "cpuFlavorIds": ["cpu5c", "cpu3c"],
        "cpuFlavorPriority": "custom",
        "vcpuCount": vcpu or j["vcpu"],
        "cloudType": "SECURE",
        "interruptible": False,
        "imageName": "ubuntu:24.04",
        "containerDiskInGb": j["disk"],
        "ports": [],
        "env": {"GH_TOKEN": f"{{{{ RUNPOD_SECRET_{SECRET} }}}}"},
        "dockerStartCmd": ["bash", "-c", start(job)],
    } | ({"volumeInGb": j["volume"], "volumeMountPath": "/workspace"} if j["volume"] else {})


def call(method: str, path: str, data: dict | None = None):
    # urllib's default User-Agent is refused by RunPod's CDN (Cloudflare error 1010)
    headers = {"Content-Type": "application/json", "User-Agent": "lattice-lab-census/1.0"}
    if os.environ.get("RUNPOD_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['RUNPOD_API_KEY']}"
    payload = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(API + path, method=method, headers=headers, data=payload)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path}: HTTP {e.code}: {e.read().decode()[:500]}")


def ours(pod_id: str) -> dict:
    pod = call("GET", f"/pods/{pod_id}")
    if pod.get("name") not in NAMES:
        sys.exit(f"pod {pod_id} is named {pod.get('name')!r}, not one of {sorted(NAMES)}: "
                 "not touching it")  # fmt: skip
    return pod


def brief(pod: dict) -> dict:
    keys = ("id", "name", "desiredStatus", "cpuFlavorId", "vcpuCount", "memoryInGb", "costPerHr",
            "lastStartedAt", "lastStatusChange", "interruptible")  # fmt: skip
    return {k: pod.get(k) for k in keys}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    p.add_argument("action", choices=("create", "list", "status", "stop", "delete"))
    p.add_argument("pod_id", nargs="?")
    p.add_argument("--job", choices=sorted(JOBS), default="census-3c")
    p.add_argument("--vcpu", type=int, help="default: the job's (census-3c 8, spotcheck 32)")
    p.add_argument("--dry-run", action="store_true", help="print the create request, send nothing")
    a = p.parse_args()
    if a.action == "create":
        if a.dry_run:
            print(json.dumps(body(a.job, a.vcpu), indent=2))
            return
        name = JOBS[a.job]["name"]
        if any(x.get("name") == name for x in call("GET", "/pods")):
            sys.exit(f"a pod named {name} exists already (see `list`)")
        print(json.dumps(brief(call("POST", "/pods", body(a.job, a.vcpu))), indent=2))
    elif a.action == "list":
        pods = [brief(x) for x in call("GET", "/pods") if x.get("name") in NAMES]
        print(json.dumps(pods, indent=2))
    else:
        if not a.pod_id:
            sys.exit("give the pod id")
        ours(a.pod_id)
        if a.action == "status":
            print(json.dumps(brief(call("GET", f"/pods/{a.pod_id}")), indent=2))
        elif a.action == "stop":
            print(json.dumps(brief(call("POST", f"/pods/{a.pod_id}/stop")), indent=2))
        else:
            call("DELETE", f"/pods/{a.pod_id}")
            print(f"deleted {a.pod_id}")


if __name__ == "__main__":
    main()
