#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""embed — drop into an IPython shell with clipboard content preloaded.

Ported from scitex-gen ``_ipython/_embed.py``. The upstream file was
largely commented-out scaffolding around a single working ``embed()``
helper; that helper is preserved here as a thin wrapper over
:func:`IPython.embed` with optional pyperclip integration.

TODO
----
The legacy upstream module included extensive commented-out variants
(``embed_with_clipboard_exec`` etc.) plus a CLI ``__main__`` block that
boots ``scitex.session.start`` / ``scitex.session.close``. Those
fragments were not actually wired up upstream and are NOT ported here.
A richer REPL bootstrapper can be layered on later if needed.
"""
from __future__ import annotations


def embed() -> None:
    """Start an IPython shell, optionally executing clipboard content.

    Prompts the user once for whether the clipboard contents should be
    executed inside the new shell. Requires ``IPython`` and
    ``pyperclip`` — both are declared as ``scitex-repl`` runtime deps.

    Notes
    -----
    - If ``pyperclip`` cannot reach the clipboard (e.g. no display on
      Linux), the prompt still runs but the clipboard content is empty.
    - The shell uses ``IPython.embed`` with no preconfigured magic.
    """
    import pyperclip
    from IPython import embed as _embed

    try:
        clipboard_content = pyperclip.paste()
    except pyperclip.PyperclipException as exc:  # pragma: no cover - env dep
        clipboard_content = ""
        print("Could not access the clipboard:", exc)

    print("Clipboard content loaded. Do you want to execute it? [y/n]")
    execute_clipboard = input().strip().lower() == "y"

    ipython_shell = _embed(
        header=(
            "IPython is now running. Clipboard content will be executed "
            "if confirmed."
        )
    )

    if clipboard_content and execute_clipboard:
        ipython_shell.run_cell(clipboard_content)
