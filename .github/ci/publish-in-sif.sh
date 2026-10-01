#!/usr/bin/env bash
# Runs INSIDE the reused scitex-ci SIF (apptainer exec — invoked via
# exec-in-sif.sh). Publishes ./dist/* to PyPI via MANUAL OIDC Trusted
# Publishing, then twine upload.
#
# WHY manual OIDC (not pypa/gh-action-pypi-publish): that action is a Docker
# container action. Self-hosted Spartan compute nodes have NO Docker, so the
# action cannot run there. PyPI Trusted Publishing is just an OIDC token
# exchange over plain HTTPS, so we do it by hand:
#
#   1. Ask the GitHub Actions OIDC provider for a JWT with audience=pypi,
#      using the per-job ACTIONS_ID_TOKEN_REQUEST_{TOKEN,URL} env vars (present
#      because the publish job declares `permissions: id-token: write`).
#      apptainer exec (no --cleanenv) passes those host env vars into the SIF.
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
"$PY" -I .github/ci/validate-dist.py dist

# --- step 1: request the OIDC JWT (audience=pypi) from GitHub ---
: "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:?ACTIONS_ID_TOKEN_REQUEST_TOKEN not set — the publish job needs 'permissions: id-token: write'}"
: "${ACTIONS_ID_TOKEN_REQUEST_URL:?ACTIONS_ID_TOKEN_REQUEST_URL not set — the publish job needs 'permissions: id-token: write'}"

echo "=== minting OIDC JWT (audience=pypi) ==="
JWT="$(curl -fsS \
    -H "Authorization: bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" \
    "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=pypi" |
    "$PY" -c 'import sys,json; print(json.load(sys.stdin)["value"])')"
test -n "$JWT" || {
    echo "::error::OIDC JWT request returned an empty token"
    exit 1
}
echo "OIDC JWT obtained (length=${#JWT})"

# --- step 2: exchange the JWT for a short-lived PyPI API token ---
echo "=== exchanging JWT at PyPI mint-token endpoint ==="
MINT_RESP="$(curl -sS -X POST https://pypi.org/_/oidc/mint-token \
    -d "{\"token\":\"${JWT}\"}")"
MINTED="$(printf '%s' "$MINT_RESP" |
    "$PY" -c 'import sys,json; d=json.load(sys.stdin); print(d.get("token",""))')"
if [ -z "$MINTED" ]; then
    # Surface PyPI's error body VERBATIM (the JWT is NOT echoed) so a trust
    # misconfiguration is diagnosable — this is the decisive failure mode for
    # the fleet. Print the raw response unconditionally (most reliable on an
    # error path); pretty-print is best-effort on top.
    echo "::error::PyPI mint-token returned no token."
    echo "--- PyPI mint-token response body (raw) ---"
    printf '%s\n' "$MINT_RESP"
    echo "--- (pretty, best-effort) ---"
    printf '%s' "$MINT_RESP" |
        "$PY" -c 'import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))' \
            2>/dev/null || true
    exit 1
fi
echo "PyPI token minted (length=${#MINTED})"

# --- step 3: validate with job-owned twine, then upload ---
echo "=== installing twine (job-owned venv) ==="
"$PY" -I -m pip --isolated install --index-url https://pypi.org/simple twine
"$PY" -I -m pip --isolated check
"$PY" -I -m twine check --strict dist/*

echo "=== twine upload dist/* ==="
TWINE_USERNAME="__token__" TWINE_PASSWORD="$MINTED" \
    "$PY" -m twine upload --non-interactive --disable-progress-bar dist/*

echo "PUBLISH-OK: scitex-repl dist/* uploaded to PyPI via manual OIDC trusted publishing"
