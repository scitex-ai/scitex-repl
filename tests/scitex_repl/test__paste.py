#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_repl.paste.

A stub pyperclip is swapped into ``sys.modules`` so the tests never touch
the real clipboard (CI on headless Linux runners typically has none).
No monkeypatch (PA-306): explicit save/restore with try/finally.
"""
from __future__ import annotations

import sys
import types
from collections.abc import Iterator
from typing import Any

import pytest

from scitex_repl import paste


@pytest.fixture
def fake_pyperclip() -> Iterator[types.ModuleType]:
    previous = sys.modules.get("pyperclip")
    fake = types.ModuleType("pyperclip")
    setattr(fake, "paste", lambda: "x = 1 + 1\n")
    setattr(fake, "PyperclipException", Exception)
    sys.modules["pyperclip"] = fake
    try:
        yield fake
    finally:
        if previous is None:
            sys.modules.pop("pyperclip", None)
        else:
            sys.modules["pyperclip"] = previous


def test_paste_executes_clipboard_assignment_silently(
    fake_pyperclip: types.ModuleType, capfd: Any
) -> None:
    # Arrange
    clipboard_is_noop_assignment = True

    # Act
    paste()
    captured = capfd.readouterr()

    # Assert
    assert (clipboard_is_noop_assignment, captured.out, captured.err) == (True, "", "")


def test_paste_error_diagnostic_reports_clipboard_failure(
    fake_pyperclip: types.ModuleType, capfd: Any
) -> None:
    # Arrange
    setattr(fake_pyperclip, "paste", lambda: "raise RuntimeError('boom')")

    # Act
    paste()
    err = capfd.readouterr().err

    # Assert
    assert "Could not execute clipboard content" in err


def test_paste_error_diagnostic_includes_original_message(
    fake_pyperclip: types.ModuleType, capfd: Any
) -> None:
    # Arrange
    setattr(fake_pyperclip, "paste", lambda: "raise RuntimeError('boom')")

    # Act
    paste()
    err = capfd.readouterr().err

    # Assert
    assert "boom" in err
