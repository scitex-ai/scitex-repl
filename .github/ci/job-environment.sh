#!/usr/bin/env bash
# REPL-specific inner runtime. The outer wrapper binds job-owned scratch here.
set -euo pipefail

repl_ci_environment() {
    local kind="${1:?job kind required}" version="${2:?Python version required}"
    case "$version" in
        3.11|3.12|3.13) ;;
        *) echo "::error::unsupported CI Python version: $version"; return 1 ;;
    esac
    local base_python="/opt/venv-$version/bin/python"
    [ -x "$base_python" ] || {
        echo "::error::baked Python missing: $base_python — rebuild the verified SIF"
        return 1
    }
    local parent="${SCITEX_REPL_CI_JOB_TMP:?outer wrapper must supply bind-backed job scratch}"
    case "$parent" in
        /*) ;;
        *) echo "::error::CI job scratch must be absolute"; return 1 ;;
    esac
    [ -d "$parent" ] && [ -w "$parent" ] || {
        echo "::error::CI job scratch is not writable: $parent"
        return 1
    }
    CI_SCRATCH="$(mktemp -d "$parent/repl-$kind-$version.XXXXXXXX")"
    export TMPDIR="$CI_SCRATCH/tmp"
    export SCITEX_DIR="$CI_SCRATCH/scitex"
    export IPYTHONDIR="$CI_SCRATCH/ipython"
    export XDG_CACHE_HOME="$CI_SCRATCH/cache"
    export XDG_CONFIG_HOME="$CI_SCRATCH/config"
    export XDG_DATA_HOME="$CI_SCRATCH/data"
    export PIP_CACHE_DIR="$XDG_CACHE_HOME/pip"
    export UV_CACHE_DIR="$XDG_CACHE_HOME/uv"
    export COVERAGE_FILE="$CI_SCRATCH/.coverage"
    export PIP_CONFIG_FILE=/dev/null
    export NETRC=/dev/null
    export PIP_KEYRING_PROVIDER=disabled
    export PIP_DISABLE_PIP_VERSION_CHECK=1
    export PYTHONDONTWRITEBYTECODE=1
    export SCITEX_LOGGING_FORMAT=default
    export SCITEX_STORE_DSN='postgresql://repl-refused@127.0.0.1:1/repl-refused?connect_timeout=1'
    export LC_ALL=C.UTF-8 LANG=C.UTF-8
    mkdir -p "$TMPDIR" "$SCITEX_DIR" "$IPYTHONDIR" "$PIP_CACHE_DIR" \
        "$UV_CACHE_DIR" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME"
    unset VIRTUAL_ENV PYTHONPATH PYTHONHOME
    "$base_python" -I -m venv "$CI_SCRATCH/venv"
    CI_PY="$CI_SCRATCH/venv/bin/python"
    export PATH="$CI_SCRATCH/venv/bin:$PATH"
    echo "repl-ci: job=$kind python=$version scratch=$CI_SCRATCH"
}

# Each application receives only its owned state and declared command operands.
# OIDC credentials remain in the publisher shell and are passed only to curl
# and Twine at their corresponding calls.
repl_ci_run() {
    test -n "${CI_PY:-}" && test -d "${CI_SCRATCH:-}" || {
        echo "::error::REPL job context is not initialized" >&2
        return 1
    }
    env -i \
        "PATH=$CI_SCRATCH/venv/bin:/usr/local/bin:/usr/bin:/bin" \
        LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        "TMPDIR=$TMPDIR" "SCITEX_DIR=$SCITEX_DIR" "IPYTHONDIR=$IPYTHONDIR" \
        "XDG_CACHE_HOME=$XDG_CACHE_HOME" "XDG_CONFIG_HOME=$XDG_CONFIG_HOME" \
        "XDG_DATA_HOME=$XDG_DATA_HOME" "COVERAGE_FILE=$COVERAGE_FILE" \
        "PIP_CACHE_DIR=$PIP_CACHE_DIR" "UV_CACHE_DIR=$UV_CACHE_DIR" \
        PIP_CONFIG_FILE=/dev/null UV_NO_CONFIG=1 NETRC=/dev/null \
        PIP_KEYRING_PROVIDER=disabled PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 RUN_E2E=1 \
        SCITEX_LOGGING_FORMAT=default "SCITEX_STORE_DSN=$SCITEX_STORE_DSN" \
        "SCITEX_REPL_RELEASE_TAG=${SCITEX_REPL_RELEASE_TAG:-}" \
        "PGHOST=$CI_SCRATCH/refused-socket" PGPORT=1 PGUSER=repl-refused \
        PGDATABASE=repl-refused "PGPASSFILE=$CI_SCRATCH/refused-pgpass" \
        "PGSERVICEFILE=$CI_SCRATCH/refused-pgservice" \
        GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 "$@"
}
