#!/usr/bin/env bash
# Native REPL tests in a fresh environment inside the digest-verified CI SIF.
set -euo pipefail
source .github/ci/job-environment.sh
repl_ci_environment test "${1:?Python version required}"

# Full declared dependencies are a gate; never retry with reduced extras.
"$CI_PY" -I -m pip --isolated install --index-url https://pypi.org/simple ".[all,dev]"
"$CI_PY" -I -m pip --isolated check
export RUN_E2E=1
exec "$CI_PY" -m pytest tests/ \
    --basetemp="$TMPDIR/pytest" -o "cache_dir=$XDG_CACHE_HOME/pytest" \
    --cov=scitex_repl --cov-report="xml:$CI_SCRATCH/coverage.xml" --cov-report=term \
    --junitxml="$CI_SCRATCH/pytest.xml"
