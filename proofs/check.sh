#!/usr/bin/env bash
# Build the proofs and print the axioms the main results rest on.
#   proofs/check.sh            (from the repository root)
# Needs the Lean toolchain in lean-toolchain. Where release.lean-lang.org is blocked, download
# lean-<version>-linux.zip from the GitHub release, unzip it, link it with
#   elan toolchain link v4.35.0-local <dir>
# and run with ELAN_TOOLCHAIN=v4.35.0-local. Where mathlib's cache is reachable, `lake exe cache
# get` saves the build; without it, the imported part of mathlib builds in about 15 minutes on 4
# cores.
set -euo pipefail
cd "$(dirname "$0")"
lake build
lake env lean Axioms.lean
