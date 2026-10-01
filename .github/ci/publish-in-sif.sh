#!/usr/bin/env bash
# Runs INSIDE the reused scitex-ci SIF (apptainer exec — invoked via
# exec-in-sif.sh). Publishes ./dist/* to PyPI via MANUAL OIDC Trusted
# Publishing, then twine upload.
#
# The selected CPU runner publishes inside its digest-verified SIF using
# short-lived PyPI Trusted Publishing credentials. Docker service jobs use a
# separate runner pool. Only these publish-job credentials enter this SIF:
#
#   1. Ask the GitHub Actions OIDC provider for a JWT with audience=pypi,
#      using the per-job ACTIONS_ID_TOKEN_REQUEST_{TOKEN,URL} env vars (present
#      because the publish job declares `permissions: id-token: write`).
#      the clean outer wrapper forwards these two explicit operands.
#   2. Exchange that JWT at PyPI's mint-token endpoint for a short-lived,
#      scope-limited PyPI API token.
#   3. twine upload dist/* with TWINE_USERNAME=__token__ and that minted token.
#
# This requires a Trusted Publisher to be configured on PyPI for
# (project=scitex-repl, owner=scitex-ai, repo=scitex-repl,
#  workflow=pypi-publish-and-github-release-on-tag.yml, environment=pypi).
# The release owner must verify the live Trusted Publisher before tagging;
# this script neither reads nor changes PyPI's trust configuration.
#
# curl, python and job-owned-venv twine all live in the SIF.
#
# Fail-loud (operator directive): every step asserts non-empty output and
# `set -euo pipefail`; any failure is a HARD error with the exact cause, never
# a silent skip.
set -euo pipefail

source .github/ci/job-environment.sh
repl_ci_environment publish "${1:-3.12}"
PY="$CI_PY"
repl_ci_run "$PY" -I .github/ci/validate-dist.py dist

# --- step 1: request the OIDC JWT (audience=pypi) from GitHub ---
: "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:?ACTIONS_ID_TOKEN_REQUEST_TOKEN not set — the publish job needs 'permissions: id-token: write'}"
: "${ACTIONS_ID_TOKEN_REQUEST_URL:?ACTIONS_ID_TOKEN_REQUEST_URL not set — the publish job needs 'permissions: id-token: write'}"

echo "=== minting OIDC JWT (audience=pypi) ==="
JWT="$(repl_ci_run curl -fsS \
    -H "Authorization: bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" \
    "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=pypi" |
    repl_ci_run "$PY" -c 'import sys,json; print(json.load(sys.stdin)["value"])')"
test -n "$JWT" || {
    echo "::error::OIDC JWT request returned an empty token"
    exit 1
}
echo "OIDC JWT obtained (length=${#JWT})"

# --- step 2: exchange the JWT for a short-lived PyPI API token ---
echo "=== exchanging JWT at PyPI mint-token endpoint ==="
MINT_RESP="$(repl_ci_run curl -sS -X POST https://pypi.org/_/oidc/mint-token \
    -d "{\"token\":\"${JWT}\"}")"
MINTED="$(printf '%s' "$MINT_RESP" |
    repl_ci_run "$PY" -c 'import sys,json; d=json.load(sys.stdin); print(d.get("token",""))')"
if [ -z "$MINTED" ]; then
    echo "::error::PyPI mint-token returned no token."
    printf '%s' "$MINT_RESP" |
        repl_ci_run "$PY" -c 'import sys,json,re
d=json.load(sys.stdin)
codes={e.get("code", "unknown") for e in d.get("errors", []) if isinstance(e, dict)}
safe=sorted(c for c in codes if isinstance(c, str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", c))
print("PyPI mint-token error codes: " + (", ".join(safe) or "unknown"))' \
            2>/dev/null || echo "PyPI mint-token error codes: unreadable"
    exit 1
fi
echo "PyPI token minted (length=${#MINTED})"

# --- step 3: validate with job-owned twine, then upload ---
echo "=== installing twine (job-owned venv) ==="
repl_ci_run "$PY" -I -m pip --isolated install --index-url https://pypi.org/simple twine
repl_ci_run "$PY" -I -m pip --isolated check
repl_ci_run "$PY" -I -m twine check --strict dist/*

echo "=== twine upload dist/* ==="
repl_ci_run env TWINE_USERNAME="__token__" TWINE_PASSWORD="$MINTED" \
    "$PY" -m twine upload --config-file /dev/null --non-interactive --disable-progress-bar dist/*

echo "PUBLISH-OK: scitex-repl dist/* uploaded to PyPI via manual OIDC trusted publishing"
