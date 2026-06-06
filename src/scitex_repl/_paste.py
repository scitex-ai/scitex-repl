#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paste — exec the system clipboard contents.

Ported from scitex-gen ``_ipython/_paste.py``. The clipboard contents
are passed through :func:`textwrap.dedent` before ``exec`` so that
indented multi-line copy/paste payloads from editors don't trigger
``IndentationError``.

.. warning::
    ``paste()`` evaluates whatever sits on your clipboard in the
    current scope. Do not point it at untrusted data.
"""
from __future__ import annotations


def paste() -> None:
    """Run the system clipboard contents through ``exec``.

    Prints any exception raised by the ``exec`` call instead of
    propagating it — matching the legacy scitex-gen behavior. Requires
    ``pyperclip``.
    """
    import textwrap

    import pyperclip

    try:
        clipboard_content = pyperclip.paste()
        clipboard_content = textwrap.dedent(clipboard_content)
        exec(clipboard_content)  # noqa: S102 - by design
    except Exception as exc:  # pragma: no cover - depends on clipboard
        print(f"Could not execute clipboard content: {exc}")
