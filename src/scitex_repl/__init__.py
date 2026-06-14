#!/usr/bin/env python3
"""scitex-repl — interactive-REPL helpers (embed / less / paste).

A small standalone module for interactive workflows: drop into an
IPython shell pre-loaded with clipboard content (``embed``), pipe a
string into ``less`` from IPython (``less``), or exec the clipboard's
text right where you are (``paste``).

Ported out of ``scitex-gen._ipython`` as part of the scitex-gen full
retirement wave (Phase B).
"""

from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _v

    try:
        __version__ = _v("scitex-repl")
    except PackageNotFoundError:
        __version__ = "0.0.0+local"
    del _v, PackageNotFoundError
except ImportError:  # pragma: no cover - only on ancient Pythons
    __version__ = "0.0.0+local"

from ._clipboard import (
    ClipboardError,
    install_ipython_paste,
    read_clipboard,
    write_clipboard,
)
from ._embed import embed
from ._less import less
from ._paste import paste

__all__ = [
    "ClipboardError",
    "__version__",
    "embed",
    "install_ipython_paste",
    "less",
    "paste",
    "read_clipboard",
    "write_clipboard",
]
