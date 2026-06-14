# Python API

All names are importable from the top-level `scitex_repl` package.

## `read_clipboard() -> str`

Return the current system-clipboard contents as text.

- Raises `scitex_repl.ClipboardError` if pyperclip cannot reach a
  backend. The exception message names the platform-specific tool
  (`xsel` / `clip.exe` / …) so the caller knows what to install.
- No silent fallback: never returns an empty string for a broken
  backend.

## `write_clipboard(text: str) -> None`

Copy `text` to the system clipboard. Same `ClipboardError` contract as
`read_clipboard`.

## `install_ipython_paste(shell=None) -> None`

Register a `%paste` line magic on the active IPython shell that:

1. Reads the clipboard via `read_clipboard()`.
2. Runs the result through `textwrap.dedent` so indented editor
   payloads execute without `IndentationError`.
3. Executes the result in the user's namespace via `shell.run_cell`.

- If `shell` is `None`, uses `IPython.get_ipython()`.
- Raises `RuntimeError` if no IPython shell is active and `shell` was
  not supplied.

## `ClipboardError`

A `RuntimeError` subclass raised by the read/write helpers when no
clipboard backend is available.

## Legacy v0.1 surface (still supported)

- `embed() -> None` — drop into an IPython shell, optionally
  pre-executing the clipboard contents (interactive prompt).
- `less(output: str) -> None` — pipe `output` through the system
  `less` pager from inside IPython.
- `paste() -> None` — `exec` the dedented clipboard contents in the
  caller's scope.
