"""
Create, inspect and stop the stage 3c census pod through RunPod's REST API (docs/runpod-setup.md).

    python examples/qec-census-3c/runpod/launch.py create [--vcpu 8] [--dry-run]
    python examples/qec-census-3c/runpod/launch.py list
    python examples/qec-census-3c/runpod/launch.py status POD_ID
    python examples/qec-census-3c/runpod/launch.py stop POD_ID
    python examples/qec-census-3c/runpod/launch.py delete POD_ID

The API key comes from the environment (RUNPOD_API_KEY) when it is set; otherwise the request is
sent without one, for a proxy that adds it. It only acts on pods named NAME: `list` shows only
those, and `status`, `stop` and `delete` refuse any other pod, so a pod of yours running something
else is never touched.

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
NAME = "lattice-lab-census-3c"
BRANCH = "ccr-ab9f0bb1-qb20sx"
REPO = "github.com/PolyLabs-research/lattice-lab.git"
SECRET = "lattice_lab_github_token"

START = f"""set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -q && apt-get install -yq git ca-certificates
case "$GH_TOKEN" in
  "{{{{"*|"") echo "GH_TOKEN is not set: create the RunPod secret {SECRET}"; sleep infinity;;
esac
mkdir -p /workspace && cd /workspace
if [ -d lattice-lab/.git ]; then
  git -C lattice-lab pull -q --rebase --autostash origin {BRANCH} \\
    || {{ echo "UPDATE FAILED: running the pod-run.sh already on the volume"; \\
         git -C lattice-lab rebase --abort 2>/dev/null; true; }}
else
  git clone -q --branch {BRANCH} "https://x-access-token:$GH_TOKEN@{REPO}" lattice-lab
fi
exec bash lattice-lab/examples/qec-census-3c/runpod/pod-run.sh
"""


def body(vcpu: int) -> dict:
    return {
        "name": NAME,
        "computeType": "CPU",
        "cpuFlavorIds": ["cpu5c", "cpu3c"],
        "cpuFlavorPriority": "custom",
        "vcpuCount": vcpu,
        "cloudType": "SECURE",
        "interruptible": False,
        "imageName": "ubuntu:24.04",
        "containerDiskInGb": 20,
        "volumeInGb": 20,
        "volumeMountPath": "/workspace",
        "ports": [],
        "env": {"GH_TOKEN": f"{{{{ RUNPOD_SECRET_{SECRET} }}}}"},
        "dockerStartCmd": ["bash", "-c", START],
    }


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
    if pod.get("name") != NAME:
        sys.exit(f"pod {pod_id} is named {pod.get('name')!r}, not {NAME!r}: not touching it")
    return pod


def brief(pod: dict) -> dict:
    keys = ("id", "name", "desiredStatus", "cpuFlavorId", "vcpuCount", "memoryInGb", "costPerHr",
            "lastStartedAt", "lastStatusChange", "interruptible")  # fmt: skip
    return {k: pod.get(k) for k in keys}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    p.add_argument("action", choices=("create", "list", "status", "stop", "delete"))
    p.add_argument("pod_id", nargs="?")
    p.add_argument("--vcpu", type=int, default=8)
    p.add_argument("--dry-run", action="store_true", help="print the create request, send nothing")
    a = p.parse_args()
    if a.action == "create":
        if a.dry_run:
            print(json.dumps(body(a.vcpu), indent=2))
            return
        if any(x.get("name") == NAME for x in call("GET", "/pods")):
            sys.exit(f"a pod named {NAME} exists already (see `list`)")
        print(json.dumps(brief(call("POST", "/pods", body(a.vcpu))), indent=2))
    elif a.action == "list":
        pods = [brief(x) for x in call("GET", "/pods") if x.get("name") == NAME]
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
