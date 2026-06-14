# Quick start

## Read / write round-trip

```python
import scitex_repl

scitex_repl.write_clipboard("hello from scitex-repl")
assert scitex_repl.read_clipboard() == "hello from scitex-repl"
```

If pyperclip cannot reach the system clipboard, both helpers raise
`scitex_repl.ClipboardError` with a message naming the missing backend
tool (`xsel`, `clip.exe`, …). There is no silent empty-string fallback.

## IPython `%paste` that works on WSL / headless Linux

IPython's stock `%paste` magic falls back to a `tkinter`-backed clipboard
on Linux and breaks where users hit it most. Swap it for a
`pyperclip`-backed one:

```ipython
In [1]: import scitex_repl

In [2]: scitex_repl.install_ipython_paste()

In [3]: %paste
# executes whatever is on your clipboard, with leading indentation
# stripped via textwrap.dedent so editor copy/paste payloads run cleanly
```

Drop the same two lines into your `~/.ipython/profile_default/startup/`
to make this the default in every IPython session.
