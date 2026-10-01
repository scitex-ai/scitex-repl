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
    export LC_ALL=C.UTF-8 LANG=C.UTF-8
    mkdir -p "$TMPDIR" "$SCITEX_DIR" "$IPYTHONDIR" "$PIP_CACHE_DIR" \
        "$UV_CACHE_DIR" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME"
    unset VIRTUAL_ENV PYTHONPATH PYTHONHOME
    "$base_python" -I -m venv "$CI_SCRATCH/venv"
    CI_PY="$CI_SCRATCH/venv/bin/python"
    export PATH="$CI_SCRATCH/venv/bin:$PATH"
    echo "repl-ci: job=$kind python=$version scratch=$CI_SCRATCH"
}
