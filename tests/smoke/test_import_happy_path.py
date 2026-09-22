"""Smoke: installed package exposes its public surface (PS-211).

Subprocess-driven (``sys.executable <tmp script>``) so this proves the
installed distribution resolves — an in-process import would not.
Hermetic: no network, no credentials, no writes outside tmp dirs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke

_PROBE = "import scitex_repl\nprint(sorted(scitex_repl.__all__))\n"


def test_subprocess_import_exposes_public_surface(tmp_path: Path) -> None:
    # Arrange
    probe = tmp_path / "probe_repl.py"
    probe.write_text(_PROBE)
    argv = [sys.executable, str(probe)]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert (completed.returncode, completed.stdout.splitlines()) == (
        0,
        ["['__version__', 'embed', 'less', 'paste']"],
    )
