#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real round-trip tests for scitex_repl._clipboard.

These tests do NOT mock pyperclip. They drive the actual system
clipboard. On headless / sandboxed runners (no xsel / xclip / clip.exe)
they skip CLEANLY via ``pytest.skip`` so CI stays green without lying
about coverage.
"""

from __future__ import annotations

import pytest


def _require_clipboard_backend() -> None:
    """Skip the calling test if no clipboard backend is available.

    Uses the production :func:`scitex_repl.read_clipboard` /
    :func:`write_clipboard` so the probe goes through the same
    ``ClipboardError`` translation layer the user-facing API does. This
    catches both pyperclip's own ``PyperclipException`` and the
    ``FileNotFoundError`` that gets raised on hosts that look like WSL
    but don't actually have ``powershell.exe`` on PATH (containers,
    sandboxed runners).
    """
    from scitex_repl import ClipboardError, read_clipboard, write_clipboard

    try:
        # A no-op probe: write the current clipboard back to itself.
        write_clipboard(read_clipboard())
    except ClipboardError as exc:
        pytest.skip(reason=f"no clipboard backend available on this host: {exc}")


def test_read_clipboard_round_trip_returns_payload():
    # Arrange
    _require_clipboard_backend()
    import pyperclip

    from scitex_repl import read_clipboard

    payload = "scitex-repl clipboard round trip 12345"
    pyperclip.copy(payload)

    # Act
    result = read_clipboard()

    # Assert
    assert result == payload


def test_write_clipboard_places_text_on_clipboard():
    # Arrange
    _require_clipboard_backend()
    import pyperclip

    from scitex_repl import write_clipboard

    payload = "scitex-repl write helper 67890"

    # Act
    write_clipboard(payload)

    # Assert
    assert pyperclip.paste() == payload


def test_round_trip_preserves_multiline_text():
    # Arrange
    _require_clipboard_backend()
    from scitex_repl import read_clipboard, write_clipboard

    payload = "line one\nline two\n  indented line three\n"

    # Act
    write_clipboard(payload)
    result = read_clipboard()

    # Assert
    assert result == payload


def test_public_api_exposes_clipboard_helpers():
    # Arrange
    import scitex_repl

    expected = {
        "read_clipboard",
        "write_clipboard",
        "install_ipython_paste",
        "ClipboardError",
    }

    # Act
    surface = set(scitex_repl.__all__)

    # Assert
    assert expected <= surface
