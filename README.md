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

## Public API

```python
import scitex_repl

# Drop into an IPython shell, optionally pre-executing the clipboard.
scitex_repl.embed()

# Pipe a string through the system `less` pager.
scitex_repl.less("a very long string ...")

# Exec the current clipboard contents.
scitex_repl.paste()
```

## Status

- `less` and `paste` are functional thin wrappers over IPython /
  pyperclip.
- `embed` is preserved from the upstream — the upstream file was mostly
  commented-out scaffolding around a single small helper. A richer REPL
  bootstrapper can be layered on later if there's demand.

## License

AGPL-3.0-only.
