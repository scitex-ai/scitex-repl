---
name: scitex-repl
description: Interactive-REPL helpers from the SciTeX ecosystem — system-clipboard read/write, an IPython %paste replacement that works on WSL / headless Linux, plus thin embed / less / paste wrappers.
tags: [scitex-repl]
primary_interface: python
package: scitex-repl
import: scitex_repl
---

# scitex-repl

`scitex-repl` is the ecosystem home for interactive-REPL ergonomics.

The flagship piece is reliable clipboard access on the platforms where
IPython's bundled `%paste` magic typically breaks: WSL and headless
Linux, where the stock backend tries to fall back to `tkinter` (a
system apt package, not pip-installable). `scitex-repl` routes
everything through `pyperclip`, which speaks the platform-native
tools — `xsel` / `xclip` on Linux, `clip.exe` on WSL, and the native
clipboards on macOS / Windows.

## Leaves

- `01_installation.md` — pip install + clipboard backend setup.
- `02_quick-start.md` — read/write round-trip and the IPython `%paste`
  installer in 30 seconds.
- `03_python-api.md` — function signatures and exact behaviour.

## Public surface (at a glance)

```python
import scitex_repl

scitex_repl.read_clipboard()         -> str
scitex_repl.write_clipboard(text)    -> None
scitex_repl.install_ipython_paste()  -> None
scitex_repl.ClipboardError           # raised on backend failure
```

The three legacy v0.1 entry points (`embed`, `less`, `paste`) also
remain on the public surface for back-compat.
