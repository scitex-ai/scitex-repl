# Installation

```bash
pip install scitex-repl
```

`scitex-repl` reaches the system clipboard through
[`pyperclip`](https://pypi.org/project/pyperclip/), which talks to the
platform-native clipboard tool. On most platforms that tool is already
present; on Linux it is not.

## Clipboard backend

| Platform | Backend pyperclip uses | Install step |
| --- | --- | --- |
| Linux  | `xsel` (or `xclip`)            | `sudo apt install xsel` |
| WSL    | `clip.exe` / `powershell.exe`  | already on Windows PATH; add `/mnt/c/Windows/System32` if not |
| macOS  | `pbcopy` / `pbpaste`           | built-in — no install |
| Windows| WinAPI clipboard                | built-in — no install |

If no backend is available, `scitex_repl.read_clipboard()` /
`write_clipboard()` raise `ClipboardError` with a message naming the
exact tool to install. They never silently return an empty string.

## Development install

```bash
git clone https://github.com/ywatanabe1989/scitex-repl
cd scitex-repl
uv pip install -e ".[dev]"
pytest tests/ -q
```
