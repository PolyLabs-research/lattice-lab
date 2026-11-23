#!/usr/bin/env python3
"""Rent the CPU pod for the large part of the scale-up test (sides 2048 and 4096).

    cd examples/scale-up-sizes-large/pod
    python cpu_pod.py --hours 6 --max-rate 1.12          # the plan: nothing is created
    python cpu_pod.py --hours 6 --max-rate 1.12 --yes    # creates the pod

This belongs to the lab's own machine, not to the study. It uses the lifecycle that machine
already runs for its other projects (`tinyalphazero.cloud`, in ~/Documents/dev/chess): the pod
carries a deadline in its name and deletes itself at it, a timer on the machine deletes any pod
past its deadline, a budget check refuses a launch the account cannot cover, and the API key is
read from a file, never from the command line or the environment. launch.sh, next to this
file, does everything after the launch. The owner confirms the flavour, the hours, the rate
ceiling and the worst cost before every `--yes`.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

CHESS_SRC = Path("~/Documents/dev/chess/src").expanduser()
sys.path.insert(0, str(CHESS_SRC))
try:
    from tinyalphazero import cloud
except ImportError as error:  # only on a machine without that lifecycle library
    raise SystemExit(f"the RunPod lifecycle library is not at {CHESS_SRC}: {error}") from None

TAG = "latticelab-sizes"
IMAGE = "runpod/base:1.4.1-ubuntu2404"  # RunPod's CPU base image; its CMD is /start.sh
FLAVORS = ("cpu3c", "cpu3g", "cpu5c", "cpu5g")


def flavours(rp: cloud.RunPod) -> dict[str, dict]:
    query = (
        "query { cpuFlavors { id displayName minVcpu maxVcpu ramMultiplier "
        "specifics { securePrice stockStatus } } }"
    )
    return {f["id"]: f for f in rp._gql(query)["cpuFlavors"]}  # noqa: SLF001


def body(deadline: int, flavor: str, vcpu: int, disk_gb: int) -> dict:
    """RunPod's REST v2 request for a CPU pod, as the protocell project's launcher sends it."""
    if vcpu < 2 or vcpu & (vcpu - 1):
        raise cloud.CloudError("the vCPU count must be a power of two, 2 or more")
    return {
        "name": cloud.pod_name(TAG, deadline),
        "image": IMAGE,
        "cloud": "SECURE",
        "cpu": {"id": flavor, "vcpuCount": vcpu},
        "disk": disk_gb,
        "ports": ["22/tcp"],
        "startSsh": True,
        "cmd": cloud.watchdog_start_cmd(True),
        "env": {"TAZ_DEADLINE": str(deadline)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--flavor", default="cpu5c", choices=FLAVORS)
    parser.add_argument("--vcpu", type=int, default=32)
    parser.add_argument("--hours", type=float, required=True, help="the hard deadline, from now")
    parser.add_argument("--max-rate", type=float, required=True, help="the confirmed $/h ceiling")
    parser.add_argument("--disk", type=int, default=20, help="container disk, GB")
    parser.add_argument("--yes", action="store_true", help="actually create the pod")
    args = parser.parse_args(argv)
    try:
        rp = cloud.RunPod()
        limits = cloud.Limits.load()
        flavour = flavours(rp)[args.flavor]
        if not flavour["minVcpu"] <= args.vcpu <= flavour["maxVcpu"]:
            raise cloud.CloudError(
                f"{args.flavor} takes {flavour['minVcpu']}-{flavour['maxVcpu']} vCPUs"
            )
        # RunPod lists one price per flavour: it is per two vCPUs an hour (cpu5c at 0.07, 32
        # vCPUs, billed $1.12/h on 2026-11-01). The pod's own rate, read after creation, binds.
        rate = float(flavour["specifics"]["securePrice"]) * args.vcpu / 2.0
        if rate > args.max_rate:
            raise cloud.CloudError(
                f"the planned ${rate:.3f}/h is over the ceiling ${args.max_rate:.3f}/h"
            )
        balance = rp.balance()["balance"]
        worst = cloud.plan(rate, args.hours, balance, limits)
        deadline = int(time.time() + args.hours * 3600)
        request = body(deadline, args.flavor, args.vcpu, args.disk)
        print(
            f"plan: {args.flavor} ({flavour['displayName']}), {args.vcpu} vCPU, "
            f"{args.vcpu * flavour['ramMultiplier']} GB, SECURE, ${rate:.3f}/h, {args.hours} h cap "
            f"-> worst case ${worst:.2f}; balance ${balance:.2f}; name {request['name']}; "
            f"stock {flavour['specifics']['stockStatus']}"
        )
        if not args.yes:
            print("dry run: nothing created (pass --yes to launch)")
            return 0
        pod = rp.create_pod(request)
        cloud.ledger(
            "launch", pod_id=pod["id"], name=request["name"], deadline=deadline,
            spec={"project": "lattice-lab", "flavor": args.flavor, "vcpu": args.vcpu,
                  "hours": args.hours, "image": IMAGE},
        )  # fmt: skip
        actual = float(pod.get("cost") or rate)
        refusal = None
        if actual > args.max_rate:
            refusal = f"the pod's rate ${actual:.3f}/h is over the ceiling ${args.max_rate:.3f}/h"
        else:
            try:
                cloud.plan(actual, args.hours, balance, limits)
            except cloud.BudgetError as error:
                refusal = str(error)
        if refusal:
            rp.terminate_pod(pod["id"])
            cloud.ledger("terminate", pod_id=pod["id"], reason=f"actual rate refused: {refusal}")
            print(f"terminated {pod['id']} at once: {refusal}")
            return 2
        print(
            f"launched {pod['id']} {request['name']} at ${actual:.3f}/h; "
            f"worst case ${actual * args.hours:.2f} by the deadline"
        )
        return 0
    except cloud.CloudError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
