#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke tests for scitex_repl top-level imports."""
from __future__ import annotations


def test_top_level_import():
    import scitex_repl

    assert hasattr(scitex_repl, "__version__")


def test_public_surface():
    import scitex_repl

    for name in ("embed", "less", "paste"):
        assert hasattr(scitex_repl, name), name
        assert callable(getattr(scitex_repl, name))


def test_all_listed():
    import scitex_repl

    assert set(scitex_repl.__all__) >= {"embed", "less", "paste", "__version__"}
