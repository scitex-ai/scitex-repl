#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""embed — drop into an IPython shell with clipboard content preloaded.

Confirmed clipboard code runs in the embedded IPython namespace before the
interactive session starts. Clipboard access stays optional on headless hosts.
"""

from __future__ import annotations

import sys

import scitex_logging as slogging

log = slogging.getLogger(__name__)


def embed() -> None:
    """Start an IPython shell, optionally executing clipboard content.

    Prompts the user once for whether the clipboard contents should be
    executed inside the new shell. Requires ``IPython`` and
    ``pyperclip`` — both are declared as ``scitex-repl`` runtime deps.

    Notes
    -----
    - If ``pyperclip`` cannot reach the clipboard (e.g. no display on
      Linux), the prompt still runs but the clipboard content is empty.
    - The shell uses ``InteractiveShellEmbed`` with an explicit local namespace.
    """
    import pyperclip
    from IPython.terminal.embed import InteractiveShellEmbed

    try:
        clipboard_content = pyperclip.paste()
    except pyperclip.PyperclipException as exc:  # pragma: no cover - env dep
        clipboard_content = ""
        log.error(f"Could not access the clipboard: {exc}")

    # NOTE (PS-220): this stays on stdout via sys.stdout.write, NOT log.info.
    # It is an interactive prompt consumed by the input() below — log.info is
    # level-gated (silent at the default WARN level), which would leave the
    # user staring at a blocked stdin with no visible question. The auditor
    # recognizes sys.stdout.write as an explicit caller-owned stream.
    sys.stdout.write("Clipboard content loaded. Do you want to execute it? [y/n]\n")
    sys.stdout.flush()
    execute_clipboard = input().strip().lower() == "y"

    namespace = {}
    ipython_shell = InteractiveShellEmbed(user_ns=namespace)
    if clipboard_content and execute_clipboard:
        ipython_shell.run_cell(clipboard_content)
    # IPython.embed() returns None. Execute the confirmed cell before entering
    # the real shell, and retain its namespace throughout the interactive call.
    ipython_shell(
        header="IPython is now running. Clipboard content was executed if confirmed.",
        local_ns=namespace,
    )
