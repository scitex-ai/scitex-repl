#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""clipboard — explicit read / write helpers plus IPython ``%paste`` install.

This module exists because, on WSL and headless Linux, IPython's bundled
``%paste`` magic falls back to ``tkinter`` for clipboard access. ``tkinter``
is a system package (apt ``python3-tk``), is NOT pip-installable, and is
generally unavailable in container / CI environments — so ``%paste``
errors out where users most need it.

The fix is to route clipboard reads through `pyperclip`, which speaks
the platform-native clipboard tools (``xsel`` / ``xclip`` on Linux,
``clip.exe`` / ``powershell.exe`` on WSL, the native AppKit clipboard on
macOS, and the WinAPI clipboard on Windows). No ``tkinter`` involved.

Public API
----------
* :func:`read_clipboard` — return the clipboard text or raise loudly.
* :func:`write_clipboard` — copy text to the clipboard.
* :func:`install_ipython_paste` — register a ``%paste`` line magic on the
  active IPython shell that uses :func:`read_clipboard` instead of
  IPython's tkinter-based default.
"""

from __future__ import annotations


class ClipboardError(RuntimeError):
    """Raised when the system clipboard cannot be reached.

    The message names the platform-specific backend tool (``xsel`` /
    ``xclip`` on Linux, ``clip.exe`` on WSL/Windows) so the user knows
    what to install. We never silently fall back to an empty string —
    that would mask a broken environment.
    """


def _backend_hint() -> str:
    """Return a one-line install hint for the host's clipboard backend."""
    import sys

    if sys.platform.startswith("linux"):
        # WSL is reported as 'linux' by sys.platform; distinguish via
        # /proc/version so we can name clip.exe instead of xsel.
        try:
            with open("/proc/version", encoding="utf-8") as f:
                proc_version = f.read().lower()
        except OSError:
            proc_version = ""
        if "microsoft" in proc_version or "wsl" in proc_version:
            return (
                "On WSL, pyperclip uses clip.exe / powershell.exe — they "
                "ship with Windows and should already be on PATH. If they "
                "are not, add /mnt/c/Windows/System32 to PATH."
            )
        return (
            "On Linux, install a clipboard backend: "
            "`sudo apt install xsel` (or xclip). "
            "pyperclip will pick it up automatically."
        )
    if sys.platform == "darwin":
        return (
            "On macOS, pyperclip uses the built-in pbcopy/pbpaste — no install needed."
        )
    if sys.platform.startswith("win"):
        return "On Windows, pyperclip uses the native clipboard — no install needed."
    return (
        "pyperclip could not locate a clipboard backend on this platform. "
        "See https://pyperclip.readthedocs.io for supported backends."
    )


def _backend_exceptions():
    """Return the tuple of exception types that mean 'no backend reachable'.

    pyperclip raises ``PyperclipException`` when it knows a backend is
    missing — but on some hosts (e.g. WSL distros where ``powershell.exe``
    isn't on PATH) the underlying ``subprocess.Popen`` call raises a bare
    ``FileNotFoundError`` that pyperclip does NOT wrap. We treat both as
    'no backend reachable' so the user sees a clean :class:`ClipboardError`
    naming the missing tool, not a 200-line Popen traceback.
    """
    import pyperclip

    return (pyperclip.PyperclipException, FileNotFoundError, OSError)


def read_clipboard() -> str:
    """Return the current clipboard contents as text.

    Returns
    -------
    str
        The clipboard contents.

    Raises
    ------
    ClipboardError
        If pyperclip cannot reach a clipboard backend. The message
        names the platform-specific tool (xsel / clip.exe / etc.) so
        the caller knows what to install.
    """
    import pyperclip

    try:
        return pyperclip.paste()
    except _backend_exceptions() as exc:
        raise ClipboardError(
            f"Cannot read system clipboard: {exc}. {_backend_hint()}"
        ) from exc


def write_clipboard(text: str) -> None:
    """Copy ``text`` to the system clipboard.

    Parameters
    ----------
    text : str
        Text to place on the clipboard.

    Raises
    ------
    ClipboardError
        If pyperclip cannot reach a clipboard backend. The message
        names the platform-specific tool so the caller knows what to
        install.
    """
    import pyperclip

    try:
        pyperclip.copy(text)
    except _backend_exceptions() as exc:
        raise ClipboardError(
            f"Cannot write system clipboard: {exc}. {_backend_hint()}"
        ) from exc


def install_ipython_paste(shell=None) -> None:
    """Register a ``%paste`` line magic backed by :func:`read_clipboard`.

    IPython's stock ``%paste`` falls back to ``tkinter`` on WSL / headless
    Linux and errors out. Calling this function from an IPython session
    (or an ``ipython_config.py`` startup file) replaces ``%paste`` with
    one that reads the clipboard through pyperclip, executes it in the
    user's namespace via ``shell.run_cell``, and surfaces a clean
    :class:`ClipboardError` if no backend is available.

    Parameters
    ----------
    shell : IPython.core.interactiveshell.InteractiveShell, optional
        The IPython shell to attach the magic to. If ``None``, uses
        ``IPython.get_ipython()`` — the standard way of grabbing the
        currently-running shell.

    Raises
    ------
    RuntimeError
        If no IPython shell is active and ``shell`` was not supplied.
    """
    import textwrap

    if shell is None:
        from IPython import get_ipython

        shell = get_ipython()
        if shell is None:
            raise RuntimeError(
                "install_ipython_paste() called outside an IPython shell "
                "and no `shell` argument was provided. Either run it from "
                "inside IPython or pass an InteractiveShell instance."
            )

    def _paste_magic(_line: str) -> None:
        clipboard_text = read_clipboard()
        shell.run_cell(textwrap.dedent(clipboard_text))

    shell.register_magic_function(_paste_magic, magic_kind="line", magic_name="paste")
