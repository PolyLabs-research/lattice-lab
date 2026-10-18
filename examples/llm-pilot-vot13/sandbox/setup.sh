#!/usr/bin/env bash
# One-time setup of this sandbox in a fresh container (CARD.md):
#   ./setup.sh > setup.log 2>&1
# 1. a Python environment with numpy and sympy, run as ./python;
# 2. elan and the Lean toolchain. release.lean-lang.org is blocked here, so the toolchain comes
#    from the GitHub release and is linked as v4.35.0-local;
# 3. mathlib and the library, built from source with the pinned lake-manifest.json (about an
#    hour). Safe to rerun: each step is skipped when it is already done.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$PWD

echo "== python"
if [ ! -x .venv/bin/python ]; then
  if command -v uv >/dev/null; then
    uv venv -q --python 3.12 .venv || uv venv -q .venv
    uv pip install -q --python .venv/bin/python numpy sympy
  else
    python3 -m venv .venv
    .venv/bin/pip install -q numpy sympy
  fi
fi
./python -c "import numpy, sympy; print('numpy', numpy.__version__, 'sympy', sympy.__version__)"

echo "== elan"
export PATH=$HOME/.elan/bin:$PATH
if ! command -v elan >/dev/null; then
  mkdir -p .setup
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o .setup/elan-init.sh
  sh .setup/elan-init.sh -y --default-toolchain none
fi

echo "== lean"
if ! elan toolchain list | grep -q '^v4.35.0-local'; then
  mkdir -p "$HOME/lean-toolchains"
  cd "$HOME/lean-toolchains"
  curl -sSfL -o lean.zip https://github.com/leanprover/lean4/releases/download/v4.35.0/lean-4.35.0-linux.zip
  unzip -q -o lean.zip
  rm lean.zip
  elan toolchain link v4.35.0-local "$HOME/lean-toolchains/lean-4.35.0-linux"
  cd "$ROOT"
fi
export ELAN_TOOLCHAIN=v4.35.0-local
lean --version

echo "== mathlib and the library"
cd proofs
lake build
echo "== done"
