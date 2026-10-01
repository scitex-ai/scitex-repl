#!/usr/bin/env bash
# Build and validate the actual artifacts, not an ambient source installation.
set -euo pipefail
source .github/ci/job-environment.sh
repl_ci_environment build "${1:-3.12}"
repl_ci_run "$CI_PY" -I -m pip --isolated install --index-url https://pypi.org/simple build twine

rm -rf "${PWD:?checkout path required}/dist"
repl_ci_run "$CI_PY" -I -m build --outdir dist
repl_ci_run "$CI_PY" -I .github/ci/validate-dist.py dist
repl_ci_run "$CI_PY" -I -m twine check --strict dist/*

WHEELS=("$PWD"/dist/*.whl)
[ "${#WHEELS[@]}" -eq 1 ] && [ -f "${WHEELS[0]}" ] || {
    echo "::error::expected exactly one newly built wheel"
    exit 1
}
repl_ci_run "$CI_PY" -I -m pip --isolated install --index-url https://pypi.org/simple "${WHEELS[0]}[all,dev]"
repl_ci_run "$CI_PY" -I -m pip --isolated check
repl_ci_run "$CI_PY" -I - <<'PY'
import importlib.metadata
from pathlib import Path

import scitex_repl

assert scitex_repl.__version__ == importlib.metadata.version("scitex-repl")
assert all(callable(getattr(scitex_repl, name)) for name in ("embed", "less", "paste"))
assert not Path(scitex_repl.__file__).resolve().is_relative_to(Path.cwd() / "src")
print("Installed-wheel import:", scitex_repl.__version__, scitex_repl.__file__)
PY
export RUN_E2E=1
repl_ci_run "$CI_PY" -m pytest tests/ \
    --basetemp="$TMPDIR/wheel-pytest" -o "cache_dir=$XDG_CACHE_HOME/pytest" \
    --junitxml="$CI_SCRATCH/wheel-pytest.xml"
