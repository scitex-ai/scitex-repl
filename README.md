# scitex-repl

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

Interactive-REPL helpers (`embed`, `less`, `paste`) — standalone module
from the [SciTeX](https://github.com/ywatanabe1989) ecosystem.

Ported out of `scitex_gen._ipython` as part of the scitex-gen full
retirement wave.

## Install

```bash
pip install scitex-repl
```

`scitex-repl` reaches the system clipboard through
[`pyperclip`](https://pypi.org/project/pyperclip/), which talks directly
to the platform-native clipboard tools:

- **Linux** — needs `xsel` (or `xclip`) on `PATH`: `sudo apt install xsel`.
- **WSL** — uses `clip.exe` / `powershell.exe`; both ship with Windows
  and should already be on `PATH`.
- **macOS / Windows** — uses the built-in clipboard; no extra install.

## Public API

```python
import scitex_repl

# Read / write the system clipboard explicitly.
text = scitex_repl.read_clipboard()
scitex_repl.write_clipboard("hello")

# Replace IPython's tkinter-based %paste with a pyperclip-backed one
# that works on WSL / headless Linux. Call from inside IPython, or
# from an ipython_config.py startup file.
scitex_repl.install_ipython_paste()

# Drop into an IPython shell, optionally pre-executing the clipboard.
scitex_repl.embed()

# Pipe a string through the system `less` pager.
scitex_repl.less("a very long string ...")

# Exec the current clipboard contents in the calling scope.
scitex_repl.paste()
```

## Why this exists

On WSL and headless Linux, IPython's bundled `%paste` magic falls back
to a clipboard backend that requires `tkinter` — a system package
that's not pip-installable and is typically absent from container / CI
environments. `scitex_repl.install_ipython_paste()` swaps `%paste` for a
`pyperclip`-backed implementation so paste works out of the box on the
platforms where users hit this most.

If no clipboard backend is reachable, `read_clipboard` /
`write_clipboard` raise a loud `ClipboardError` whose message names the
exact tool to install — they never silently return an empty string.

## Status

- `read_clipboard` / `write_clipboard` / `install_ipython_paste` are
  the recommended entry points for new code.
- `less` and `paste` are functional thin wrappers over IPython /
  pyperclip and remain as the original v0.1 surface.
- `embed` is preserved from the upstream — the upstream file was mostly
  commented-out scaffolding around a single small helper. A richer REPL
  bootstrapper can be layered on later if there's demand.

## License

AGPL-3.0-only.
