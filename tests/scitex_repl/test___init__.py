"""Smoke tests for scitex_repl top-level imports."""

from __future__ import annotations

import pytest


def test_top_level_import_exposes_version_attribute():
    # Arrange
    import scitex_repl

    # Act
    version = getattr(scitex_repl, "__version__", None)

    # Assert
    assert isinstance(version, str)


@pytest.mark.parametrize("helper_name", ["embed", "less", "paste"])
def test_public_helper_is_exposed_and_callable(helper_name):
    # Arrange
    import scitex_repl

    # Act
    helper = getattr(scitex_repl, helper_name, None)

    # Assert
    assert callable(helper) is True


def test_dunder_all_lists_public_helpers():
    # Arrange
    import scitex_repl

    # Act
    exported = set(scitex_repl.__all__)

    # Assert
    assert exported >= {"embed", "less", "paste", "__version__"}
