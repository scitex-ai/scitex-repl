"""E2E: paste() diagnoses an exec failure in a fresh interpreter (PS-212).

The full story — a stub clipboard holding a raising payload is swapped
in, ``paste()`` execs it, swallows the error, and reports the diagnostic
on stderr with a zero exit status. The real clipboard is never touched
(headless-safe), real interpreter, real filesystem, no network. Gated on
``RUN_E2E=1`` (skipped by default).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        os.environ.get("RUN_E2E") != "1",
        reason="e2e: set RUN_E2E=1 to run end-to-end workflows",
    ),
]

_PROBE = (
    "import sys, types\n"
    "stub = types.ModuleType('pyperclip')\n"
    "setattr(stub, 'paste', lambda: \"raise RuntimeError('boom')\")\n"
    "setattr(stub, 'PyperclipException', Exception)\n"
    "sys.modules['pyperclip'] = stub\n"
    "from scitex_repl import paste\n"
    "paste()\n"
)


def test_paste_failure_is_diagnosed_on_stderr(tmp_path: Path) -> None:
    # Arrange
    probe = tmp_path / "probe_e2e.py"
    probe.write_text(_PROBE)
    argv = [sys.executable, str(probe)]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=60)

    # Assert
    assert (completed.returncode, "Could not execute clipboard content" in completed.stderr) == (
        0,
        True,
    )
