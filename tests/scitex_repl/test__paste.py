#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_repl.paste.

We monkey-patch pyperclip so we don't depend on the test runner having
clipboard access (CI on headless Linux runners typically does not).
"""
from __future__ import annotations

import sys
import types

import pytest


@pytest.fixture
def fake_pyperclip(monkeypatch):
    fake = types.SimpleNamespace(
        paste=lambda: "x = 1 + 1\n",
        PyperclipException=Exception,
    )
    monkeypatch.setitem(sys.modules, "pyperclip", fake)
    return fake


def test_paste_runs_clipboard(fake_pyperclip):
    from scitex_repl import paste

    # Should not raise — clipboard content is a no-op assignment.
    paste()


def test_paste_swallows_exec_errors(fake_pyperclip, capsys):
    fake_pyperclip.paste = lambda: "raise RuntimeError('boom')"

    from scitex_repl import paste

    paste()
    captured = capsys.readouterr()
    assert "Could not execute clipboard content" in captured.out
    assert "boom" in captured.out
